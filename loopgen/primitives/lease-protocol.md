# lease-protocol (shared primitive, gated)

## Purpose

The one honest failure a loopgen prompt cannot currently survive: the loop
**dying unobserved** — session death, a hang, a context overflow. It is silent
*and* expensive (an unattended run burns the night doing nothing). An agent
**cannot self-report its own death**: a timestamp it writes and then hangs on
looks healthy forever. Detecting it needs an *external* observer reading a file
the dead loop is no longer updating. This primitive emits the **lease spec** that
observer reads.

**Scope (matches the plan's "watchdog deferred").** Two things are **normative
and shipped here**: (1) the *liveness surface* the running loop maintains, and
(2) the *owner record* that makes a future restart split-brain-safe. The
*restarter / watchdog itself* — the process that detects a hung loop and
relaunches it — is **deferred**; this spec gives it the on-disk state it needs
and a recommended takeover mechanism, but the running loop never restarts itself.

Recovery of *iteration state* is not this primitive's job — loopgen already
commits per accepted iteration, so `git status` + `loop/STATE.md`
(`last_action` / `next_action`) is the resume truth. The lease covers only the
gap git can't: *is the process still alive, and who owns it.*

## Include when

**Gated.** Emit `loop/LEASE.md` + the `{{LEASE_MAINTENANCE}}` prompt-section only
for the unattended cadences — `cadence-shape ∈ {deferred-fire-and-forget,
checkpoint-gated}` — **or** when the frontload **`unattended`** flag is set (the
override for an operator leaving a `sync` / `chapter` loop running overnight;
`frontload-audit.md` records it under `frontload.unattended` + provenance *only
when set*). Interactive `sync` / `chapter` loops without the flag emit neither —
stripped, **byte-identical** (the empty-gate stripping `pressure.md` /
`subagent-patterns.md` use, including no provenance token when off).

## Liveness = an advancing deadline (no separate heartbeat)

A live loop proves it is moving by **advancing its own deadline**: each iteration
start it rewrites `expected_deadline = now + ttl` in `loop/LEASE.md`. A dead loop
stops advancing it, so eventually `now > expected_deadline` and it reads as
**hung**. There is no separate heartbeat field — stamped once per iteration it
would always equal `iteration_started_at` and add nothing; the moving deadline
*is* the heartbeat. So `ttl` must exceed the longest *legitimate* iteration
(default conservative, e.g. 2h; detection latency is therefore ≈ `ttl`). Whether
the *work* advances is the separate, existing `signal-starvation` / quiet-signal
stall concern — the lease does not track it.

## Two surfaces

- **`refs/loopgen/lease` — the owner record** (a git blob the ref points to). The
  single durable, **rollback-immune** source of truth for *who owns the loop* and
  the crash-loop count. Read with `git cat-file -p $(git rev-parse
  refs/loopgen/lease)`; written with `git hash-object -w` + a CAS
  `git update-ref`. Survives a working-tree-only `git checkout` (refs are not in
  the worktree), so identity never desyncs from a STATE rollback.
- **`loop/LEASE.md` — the volatile liveness surface, UNTRACKED** (gitignored by
  `/loopgen` at emit, composition step 7c). Rewritten in full **atomically** (temp
  file + rename) every iteration start, so it is never torn and never a tracked
  diff.

Config (`ttl`, `restart_cap`) is read-only, set at frontload in `loop/PROMPT.md`;
it is not a mutable store. There is no `lease:` block in `loop/STATE.md` — folding
the count and identity into the rollback-immune owner blob is what closes the
STATE-rollback desync.

### Schema

**Owner record** (the blob `refs/loopgen/lease` points to):

```yaml
generation:   <int>   # monotonic; the orderable CAS / fencing value
owner_id:     <id>    # current owner/session; changes on takeover
run_id:       <id>    # stable loop-instance id (survives takeovers)
restart_count: <int>  # 0 at bootstrap; +1 atomically with each takeover CAS — a monotonic counter the watchdog reads for backoff
acquired_at:  <ts>    # when this owner claimed the ref — bounds alive-pending
```

**`loop/LEASE.md`** (volatile, untracked, atomic, rewritten every iteration
start; echoes `generation` so the observer can discard a superseded render):

```yaml
generation: <int>            # echo of the OWNED generation (re-written every iteration)
owner_id: <id>               # echo, for diagnostics
iteration: <int>
iteration_started_at: <ts>
expected_deadline: <ts>      # iteration_started_at + ttl — advancing this IS the liveness signal
status: running              # running | checkpointed | paused-external
```

## Liveness computation (the observer — reviewable without the watchdog)

1. **Read the owner record.** `git cat-file -p $(git rev-parse refs/loopgen/lease)`
   → `(generation_ref, owner_ref, acquired_at, …)`.
2. **Read `loop/LEASE.md`** (atomic writes ⇒ never torn, and all fields are
   rewritten together each iteration, so a parseable render is never internally
   inconsistent):
   - `LEASE.generation == generation_ref` → a current render; classify in step 3.
   - missing, or `LEASE.generation < generation_ref` → the owner has not produced
     a current render yet. **Bound it with `acquired_at`:** if
     `now > acquired_at + ttl`, the owner died before its first stamp →
     **stale-owner** (restart-eligible); otherwise **alive-pending** (recently
     acquired — wait until `acquired_at + ttl`). This bound is what stops a death
     in the just-acquired / pre-first-stamp window from hiding forever.
3. **Classify the current render (first match wins):**
   - **hung** — `status == running` AND `now > expected_deadline` (wins regardless
     of recency; only an external actor can move it).
   - **idle / done** — `status ∈ {checkpointed, paused-external}`.
   - **alive** — otherwise (`now ≤ expected_deadline`).

## What the running loop does (normative — see {{LEASE_MAINTENANCE}})

The running loop never restarts itself. Each iteration it **bootstraps or
confirms** ownership, **stamps** liveness, and **re-checks** ownership before
committing. The full procedure is the emitted `{{LEASE_MAINTENANCE}}` block below.
Confirm is the key safety step: if the owner record's `owner_id` is no longer this
session's id, a restarter has taken over → the loop **stops without writing**.

## Ownership & restart — recommended mechanism (the restarter is deferred)

Mutual exclusion is an **atomic compare-and-swap on the `refs/loopgen/lease`
object id**: `git update-ref refs/loopgen/lease <new-blob> <expected-old-blob>`
swaps atomically only if the ref still holds `<expected-old-blob>` (the id last
read via `git rev-parse`). git refs do native CAS on object ids, so a stale claim
fails atomically (non-zero exit) and there is no lock to leak. `generation` (read
from the blob *content*) is the orderable fencing tag — the **observer** uses it
to discard a stale `loop/LEASE.md` render, and it doubles as the monotonic
takeover counter. A **session's** own ownership check is simpler: its session id
== the record's `owner_id` (so a watchdog-relaunched session, whose id the
watchdog wrote in, resumes, while a stale or bootstrap-race-losing session stops).

- **Bootstrap** — self-gated on `loop/STATE.md` `iteration: 0` (the canonical
  re-entrant gate, SKILL.md Phase 4), **not** ref existence. Write the owner blob
  `{generation: 0, owner_id: self, run_id, restart_count: 0, acquired_at: now}`
  and create the ref with an all-zero expected-old
  (`git update-ref … 0000…0`), which succeeds **iff the ref is absent**. If the
  create CAS loses (a racer won, or the ref survived a STATE rollback), re-read
  and *confirm* / defer to the restarter — do not re-bootstrap.
- **Takeover (the restarter's action — deferred watchdog).** Only when the loop
  reads **hung** or **stale-owner**. Write a *single* new blob
  `{generation: gen_ref + 1, owner_id: <relaunched session's id>, run_id,
  restart_count: <old> + 1, acquired_at: now}` and CAS it in. **The incremented
  `restart_count` rides the same blob as the new `generation`**, so they advance
  atomically — a crash right after the CAS leaves both advanced (no counter
  freeze, no desync). `owner_id` must be the **relaunched session's** id, so that
  session's Confirm matches and resumes; a stale superseded session has a
  different `owner_id` and a lower `generation`, so it reads superseded and stops.
  A successful `update-ref` *is* the acquisition; an optional re-read is a
  fast-fail, not a correctness requirement.

**Deferred to the watchdog implementation** (named, not falsely closed): *who*
polls the lease and decides hung; the relaunch trigger; and the **crash-loop
backoff** — `restart_count` is a monotonic takeover counter the watchdog reads
(with `acquired_at`) to decide when to stop relaunching (e.g. against a
frontload-set `restart_cap`, with whatever reset-on-progress heuristic it
chooses); recovery when a bootstrap create-CAS is lost. The lease exposes the
state these need; the restart *policy* is out of scope here — the running loop
never enforces a cap or resets the counter.

## Recovery stays git (iteration-state only)

On resume, `git status` + `loop/STATE.md` (`last_action` / `next_action`) is the
truth. **No `pending_op`, no precondition-sha, no ACID journal for iteration
state.** **Carve-out:** the metered-**spend** write-ahead ledger
(`primitives/frontload-audit.md` Budget-policy property *d*) **stays** — paid
tokens are not git-revertable; the "no write-ahead" claim is scoped to
iteration-state recovery only.

---

## loop/LEASE.md (rendered artifact — UNTRACKED volatile liveness surface)

> `/loopgen` adds `loop/LEASE.md` to the target repo's `.gitignore` at file
> emission (composition step 7c). A pure projection of liveness; never
> hand-edited. Rewritten in full and atomically (temp file + rename) every
> iteration start. Identity is authoritative in the owner record
> (`refs/loopgen/lease`).

```yaml
generation: <n>             # echo of the OWNED generation, re-written every iteration start
owner_id: "<owner-id>"      # echo, for diagnostics
iteration: <i>
iteration_started_at: <ts>
expected_deadline: <ts>     # iteration_started_at + ttl — advancing this is the liveness signal
status: running             # running | checkpointed | paused-external
```

---

## {{LEASE_MAINTENANCE}} (prompt-section — injected FIRST in the iteration protocol)

> Fills `{{LEASE_MAINTENANCE}}` so the lease instructions reach `loop/PROMPT.md`.
> Emitted **before `{{PRESSURE_SURFACE}}`** so the ownership check runs before any
> other start-of-iteration work writes state. Gated and stripped like
> `{{PRESSURE_SURFACE}}`.

## Liveness lease (do this first, before anything else this iteration)

Before the pressure weather and the numbered protocol — the very first thing each
iteration — maintain the liveness lease. The **owner record** is the git ref
`refs/loopgen/lease`, which points at a small blob; read it with
`git cat-file -p $(git rev-parse refs/loopgen/lease)`. Your `owner_id` is the id
this session runs under (bootstrap mints a fresh one; if a watchdog relaunched
you, it wrote your id into the record when it took over).

1. **Establish / confirm ownership before doing any work.**
   - *Bootstrap* — only when `loop/STATE.md` shows `iteration: 0` (the canonical
     re-entrant gate) **and** `refs/loopgen/lease` does not exist: build the owner
     record `{generation: 0, owner_id: self, run_id, restart_count: 0,
     acquired_at: now}`, write it as a blob and capture the id, then create the ref
     with an all-zero expected-old (creation succeeds only if the ref is absent):

     ```sh
     new=$(printf '%s' "$owner_record_yaml" | git hash-object -w --stdin)
     git update-ref refs/loopgen/lease "$new" 0000000000000000000000000000000000000000
     git check-ignore -q loop/LEASE.md || printf 'loop/LEASE.md\n' >> .gitignore
     ```

     If the create loses (a racer won the ref), re-read and treat as *Confirm*.
   - *Confirm* — read your own session id; if it equals the record's `owner_id`,
     you are the current owner — adopt the record's `generation` for your stamps
     and continue. (Checking your session id against `owner_id`, not the existing
     `loop/LEASE.md` stamp, is what lets a watchdog-relaunched session resume: the
     watchdog wrote *your* id into the record on takeover.)
   - *Superseded* — if your session id ≠ the record's `owner_id` (a restarter
     replaced you, or you lost the bootstrap race), **stop now — write nothing,
     commit nothing.** Do not re-render pressure, do not touch `loop/STATE.md`.
2. **Stamp liveness** into `loop/LEASE.md`, **atomically** (write a temp file then
   rename over it), rewriting all fields: `generation` + `owner_id` (from the
   owner record), `iteration`, `iteration_started_at`, `expected_deadline`
   (= `iteration_started_at + ttl`), `status: running`. `loop/LEASE.md` is
   untracked, so this never dirties tracked state.
3. **Re-check before committing.** Before the end-of-iteration commit, re-read the
   owner record and abort the commit if its `owner_id` is no longer your session
   id (a takeover landed mid-iteration).
4. **On a clean stop**, set `status: checkpointed` / `paused-external` in
   `loop/LEASE.md` so an observer reads idle/done, not hung.

This loop only ever **creates** the owner record (once, at bootstrap) and
otherwise only **reads** it — it never mutates it and never restarts itself.
Detecting a hung loop and taking it over is the external watchdog's job (deferred).
