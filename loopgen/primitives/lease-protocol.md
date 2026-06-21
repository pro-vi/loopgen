# lease-protocol (shared primitive, gated)

## Purpose

The one honest failure a loopgen prompt cannot currently survive: the loop
**dying unobserved** — session death, a hang, a context overflow. It is silent
*and* expensive (an unattended run burns the night doing nothing). An agent
**cannot self-report its own death**: a timestamp it writes and then hangs on
looks healthy forever. Detecting it needs an *external* observer reading a file
the dead loop is no longer updating. This primitive emits that file's spec.

**Scope.** Two layers, and only the first ships here:

- **Liveness detection (shipped, normative).** The loop maintains a small
  heartbeat/deadline file; an external observer reads it and tells *alive* from
  *hung* from *cleanly stopped*. This needs **no ownership, no identity, no
  locking** — just a file the loop keeps fresh and stops touching when it dies.
- **Safe automated restart (deferred — the watchdog).** *Acting* on a hung
  loop — relaunching it without double-launching over a still-alive one — needs
  mutual exclusion, and that is where ownership / a CAS lock / identity live.
  That is the watchdog's job and is **deferred**; the open problems it must solve
  are named below, not half-built into the running loop.

Recovery of *iteration state* is not this primitive's job — loopgen already
commits per accepted iteration, so `git status` + `loop/STATE.md`
(`last_action` / `next_action`) is the resume truth. The lease covers only the
gap git can't: *is the process still alive.*

## Include when

**Gated.** Emit `loop/LEASE.md` + the `{{LEASE_MAINTENANCE}}` prompt-section only
for the unattended cadences — `cadence-shape ∈ {deferred-fire-and-forget,
checkpoint-gated}` — **or** when the frontload **`unattended`** flag is set (the
override for an operator leaving a `sync` / `chapter` loop running overnight;
`frontload-audit.md` records it under `frontload.unattended` + provenance *only
when set*). Interactive `sync` / `chapter` loops without the flag emit neither —
stripped, **byte-identical** (the empty-gate stripping `pressure.md` /
`subagent-patterns.md` use, including no provenance token when off).

## Liveness = an advancing deadline (no heartbeat field, no identity)

A live loop proves it is moving by **advancing its own deadline**: each iteration
it rewrites `expected_deadline = now + ttl` in `loop/LEASE.md`. A dead loop stops
advancing it, so eventually `now > expected_deadline` and it reads as **hung**.
The moving deadline *is* the heartbeat — no separate heartbeat field (stamped
once per iteration it would equal `iteration_started_at` and add nothing). So
`ttl` must exceed the longest *legitimate* iteration (default conservative, e.g.
2h; detection latency is therefore ≈ `ttl`). Whether the *work* advances is the
separate, existing `signal-starvation` / quiet-signal stall concern — the lease
does not track it.

The loop writes this file from **file-persisted state only** — it never needs to
remember anything across `/goal` re-invocations, so it is safe under the runner
contract (durable progress lives in files, not memory).

## The liveness surface

**`loop/LEASE.md` — UNTRACKED** (gitignored by `/loopgen` at emit, composition
step 7a; the loop also re-ensures it before its first stamp). Rewritten in full
**atomically** (write a temp file, then rename over it) every iteration start, so
it is never torn and never a tracked diff. `ttl` is read-only config in the
frontload preamble.

```yaml
iteration: <int>
iteration_started_at: <ts>
expected_deadline: <ts>      # iteration_started_at + ttl — advancing this is the liveness signal
status: running              # running | checkpointed | paused-external
```

## Liveness computation (the observer — reviewable without the watchdog)

Read `loop/LEASE.md` (atomic writes ⇒ never torn; all fields rewritten together,
so a parseable render is never internally inconsistent) and classify (first match
wins):

- **hung** — `status == running` AND `now > expected_deadline`. The loop blew its
  iteration budget and only an external actor can move it. A genuinely dead
  runner is caught here: its last atomic render persists with an elapsed deadline.
- **idle / done** — `status ∈ {checkpointed, paused-external}`. Stopped on
  purpose; not a failure.
- **alive** — otherwise (`now ≤ expected_deadline`). Working normally.

That is the whole shipped contract. No ref, no owner record, no generation — an
observer needs none of them to tell a live loop from a dead one.

## Deferred — safe automated restart (the watchdog)

Detecting *hung* is shipped; safely *restarting* a hung loop is not. A restarter
must not relaunch over a loop that is merely slow-but-alive, and two restarters
must not both relaunch — that needs **mutual exclusion**, which is the hard part
and the reason ownership is **not** in the running loop. The open problems a
watchdog implementation must solve (named, not faked):

- **Mutual exclusion / ownership.** A single-owner record claimed atomically —
  e.g. a `git update-ref refs/loopgen/lease <new> <expected-old>` CAS on a blob,
  or an `O_EXCL` lockfile — so only one restarter wins and a stale claim fails
  atomically. A monotonic generation fences a superseded runner's late writes.
- **Identity across re-invocations.** A `/goal` loop session has **no stable
  self-id** between iterations (only files persist), so ownership cannot be the
  loop checking "is this record mine?" The watchdog must **assign** each session
  it launches a durable credential (e.g. a frontload-provided run token or a
  launcher-injected env id) and write that into the owner record, so the
  relaunched session can prove ownership and a stale one cannot.
- **Record lifecycle across runs.** A persistent owner record must be **reset or
  rotated** when a fresh run begins (`loop/STATE.md` back at `iteration: 0`),
  or a stale record from a finished run blocks the next one. Tie its lifetime to
  the run, not the repo.
- **Restart policy.** Crash-loop backoff (a takeover counter + `acquired_at`
  bound on how long a just-acquired-but-unstamped owner may look pending) and a
  cap before abandoning. The liveness surface above gives the watchdog the signal
  it polls; this policy sits on top.

The running loop participates in none of this. It only keeps `loop/LEASE.md`
fresh; an external watchdog, if and when built, owns restart.

## Recovery stays git (iteration-state only)

On resume, `git status` + `loop/STATE.md` (`last_action` / `next_action`) is the
truth. **No `pending_op`, no precondition-sha, no ACID journal for iteration
state.** **Carve-out:** the metered-**spend** write-ahead ledger
(`primitives/frontload-audit.md` Budget-policy property *d*) **stays** — paid
tokens are not git-revertable; the "no write-ahead" claim is scoped to
iteration-state recovery only.

---

## loop/LEASE.md (rendered artifact — UNTRACKED liveness surface)

> `/loopgen` adds `loop/LEASE.md` to the target repo's `.gitignore` at file
> emission (composition step 7a). A pure projection of liveness; never
> hand-edited. Rewritten in full and atomically (temp file + rename) every
> iteration start.

```yaml
iteration: <i>
iteration_started_at: <ts>
expected_deadline: <ts>     # iteration_started_at + ttl — advancing this is the liveness signal
status: running             # running | checkpointed | paused-external
```

---

## {{LEASE_MAINTENANCE}} (prompt-section — injected into the iteration protocol)

> Fills `{{LEASE_MAINTENANCE}}` so the lease instruction reaches `loop/PROMPT.md`
> (the file the runner re-reads each iteration). Without it the lease would be
> inert — declared but never stamped. Gated and stripped like
> `{{PRESSURE_SURFACE}}`.

## Liveness lease (stamp at the start of every iteration)

At the start of each iteration, before the numbered protocol, keep the liveness
file fresh so an external observer can tell a live loop from a dead one. This is
purely file work — no ownership, no identity, nothing to remember between
iterations:

1. **Stamp liveness** into `loop/LEASE.md`, written **atomically** (write a temp
   file, then rename over it), rewriting all fields: `iteration`,
   `iteration_started_at`, `expected_deadline` (= `iteration_started_at + ttl`),
   `status: running`. `loop/LEASE.md` is untracked, so this never dirties tracked
   state. (Defensively ensure it is gitignored first:
   `git check-ignore -q loop/LEASE.md || printf 'loop/LEASE.md\n' >> .gitignore`.)
2. **On a clean stop**, set `status: checkpointed` (checkpoint boundary) or
   `paused-external` (explicit external pause) so an observer reads idle/done, not
   hung.

Advancing `expected_deadline` each iteration is the liveness signal; whether the
*work* advances is the separate, existing `signal-starvation` / quiet-signal
stall concern. Detecting a hung loop and restarting it is an external watchdog's
job (out of scope for the running loop).
