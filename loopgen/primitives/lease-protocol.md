# lease-protocol (shared primitive, gated)

## Purpose

The one honest failure a loopgen prompt cannot currently survive: the loop
**dying unobserved** — session death, a hang, a context overflow. It is silent
*and* expensive (an unattended run burns the night doing nothing). An agent
**cannot self-report its own death**: a `last_seen` it stamps and then hangs on
looks healthy forever. Detecting it needs an *external* observer reading a
file the dead loop is no longer updating. This primitive emits the **lease
spec** that observer reads — a paper-reviewable contract, **not** a runtime
binding. The watchdog implementation is deferred (Scope Boundaries); what ships
here is the on-disk shape that makes an external restart *possible and safe*.

Recovery of *iteration state* is not this primitive's job — loopgen already
commits per accepted iteration, so `git status` + `loop/STATE.md`
(`last_action` / `next_action`) is the resume truth. The lease covers only the
gap git can't: *is the process still alive, and who owns it.*

## Include when

**Gated.** Emit `loop/LEASE.md` + the `lease:` `loop/STATE.md` block only for
the unattended cadences — `cadence-shape ∈ {deferred-fire-and-forget,
checkpoint-gated}` (both "run while you sleep, look periodically") — **or** when
the frontload **`unattended`** opt-in flag is set (the override for an operator
leaving a `sync` / `chapter` loop running overnight). loopgen has no
attended/unattended axis; `cadence-shape` is the available signal and the
frontload flag is the manual override.

Interactive `sync` / `chapter` loops **without** the flag emit neither file —
the artifact role and the `lease:` STATE block are both stripped, leaving the
composition **byte-identical** (the same empty-gate stripping `pressure.md` and
`benchmark-frontier.md` use). No unattended run, no lease.

## The lease schema

`loop/LEASE.md` is rendered from the `lease:` block in `loop/STATE.md` each
iteration — **STATE is the source of truth**, LEASE is a projection you never
trust independently (a torn write self-heals on the next re-render, exactly as
`PRESSURE.md` does).

```yaml
run_id:               # stable id for this loop instance (set once at bootstrap)
runner_id:            # id of the current runner/session (changes on takeover)
generation:           # monotonic int; the CAS / fencing value (see Acquisition)
iteration:            # current iteration number
iteration_started_at: # ts, set at step 0 of the iteration
heartbeat_at:         # ts, stamped EVERY step 0 (the process is moving) — independent of progress
last_progress_at:     # ts, advances ONLY on verified progress — feeds stall detection, NOT liveness
expected_deadline:    # iteration_started_at + ttl
status:               # running | checkpointed | paused-external
```

`ttl` is the per-iteration budget: default conservative (e.g. 2h), or the
context/horizon budget the frontload horizon-sizing item
(`primitives/frontload-audit.md`) sets when present.

**`heartbeat_at` vs `last_progress_at` are deliberately two fields.**
`heartbeat_at` answers *"is the process moving?"* (stamped every step 0,
unconditionally). `last_progress_at` answers *"is the work advancing?"* (stamped
only on verified progress, an `evidence-tier.md` tier-1/2 signal). Collapsing
them yields a loop that looks **dead while legitimately grinding** on one hard
step, or **alive while hung** mid-rewrite. Liveness reads `heartbeat_at`; stall
detection reads `last_progress_at`; they never cross.

## Acquisition (split-brain safe — fencing alone is not)

Mutual exclusion is an **atomic compare-and-swap on a single owner record**, not
"higher token wins." Higher-token-wins is *not* mutual exclusion: two restarters
can both read `generation` N, both write N+1, and neither ever observes a higher
value — two live owners, split brain.

**Normative mechanism:** the owner record is a git ref, claimed by CAS —

```
git update-ref refs/loopgen/lease <new-owner-blob> <expected-old-blob>
```

git refs do **native compare-and-swap**: the update fails atomically if the ref
no longer holds `<expected-old-blob>`, so a stale owner's claim is rejected and
there is **no lock to leak** (nothing to time out or force-unlock). The owner
record holds `(generation, runner_id)`. A new owner:

1. reads the current ref → `(generation_old, runner_old)`;
2. builds `(generation_old + 1, self)`;
3. CAS-writes it with `<expected-old>` = the blob it just read;
4. **re-reads the ref and aborts if it no longer owns it** — closing the
   read-modify-write race where two racers' CAS both appear to succeed against
   different observed olds.

`generation` is then carried **downstream** as a fencing tag: any LEASE/STATE
write stamped with a generation lower than the current owner's is **ignored** by
a reader (a superseded runner's late write cannot corrupt the live owner's
state). The fencing tag is a *staleness label*, **not** the mutual-exclusion
mechanism — the CAS is.

*(A plain `O_EXCL` lockfile is a future, runner-specific alternative. It would
need its own stale-owner-removal rule and its own late-writer race rule — both
of which the git-ref CAS avoids by construction. Do not adopt it without those
two rules written down.)*

## Liveness computation (worked example — reviewable without the watchdog)

An observer reads `loop/LEASE.md` and classifies it in this **precedence
order** (first match wins):

1. **hung** — `status == running` AND `now > expected_deadline`. *Wins
   regardless of recent progress*: the iteration started, blew its deadline, and
   only an external actor can move it. (Note: a fresh `heartbeat_at` does **not**
   rescue a deadline-blown `running` lease — a process can heartbeat-stamp and
   still be wedged past its budget.)
2. **idle / done** — `status ∈ {checkpointed, paused-external}`. Not a failure;
   the loop stopped on purpose (a checkpoint boundary, or an explicit external
   pause). No restart.
3. **alive** — otherwise: `heartbeat_at` is fresh within `ttl`. Working
   normally; leave it.

`last_progress_at` is **not consulted** for liveness — it feeds stall detection
(`signal-starvation` / quiet-signal), a separate concern. A restarter acts
**only on `hung`**, and only after the restart preconditions below.

## Restart preconditions (an external restarter verifies all before relaunching)

1. `loop/LEASE.md` is present and parseable.
2. `now > expected_deadline`.
3. `status == running`.
4. the worktree is committed-or-recovery-checkpointed — **no silent in-flight
   diff** (loopgen commits per accepted iteration, so a dirty tree means a
   crash mid-iteration; recover or revert it first, never relaunch over it).
5. it **wins the owner-record CAS** — no live owner holds a higher
   `generation` (this is what makes the restart split-brain-safe).
6. the restart count is under a cap (a crash-looping run is a `derivation-gap`
   to surface, not to relaunch forever).

## Recovery stays git (iteration-state only)

On resume, `git status` + `loop/STATE.md` (`last_action` / `next_action`) is the
truth. **No `pending_op`, no precondition-sha, no ACID journal for iteration
state** — a dirty worktree is visible and revertable, and commit-per-iteration
already bounds the loss to one iteration.

**Carve-out:** the metered-**spend** write-ahead ledger
(`primitives/frontload-audit.md` Budget-policy property *d*) **stays.** Paid
tokens are not git-revertable, so spend accounting fails closed via its own
write-ahead row. The "no write-ahead" claim above is scoped to *iteration-state*
recovery only — it does **not** relax the spend ledger.

---

## loop/LEASE.md (rendered artifact — header carries the maintenance rules)

> This block is the rendered `loop/LEASE.md`: a pure projection of the `lease:`
> block in `loop/STATE.md` (the source of truth). Its header carries the
> maintenance rules below so they survive context compaction even when the
> prompt summary is lossy — the same compaction-survival discipline
> `loop/PRESSURE.md` uses. Re-render it from STATE; never edit it as a store.

**Maintenance (every iteration, gated loops only):**

- **Step 0 — stamp `heartbeat_at`** in `loop/STATE.md` `lease:` and re-render
  `loop/LEASE.md`, within the same tool-call sequence, *before* the numbered
  iteration protocol runs. A heartbeat is "the process reached step 0," nothing
  more — never gate it on progress.
- **Set `iteration_started_at` and `expected_deadline`** (`= iteration_started_at
  + ttl`) at the start of each iteration.
- **Advance `last_progress_at` only on verified progress** (a tier-1/2 signal),
  never on a bare commit or a step-0 heartbeat.
- **On takeover** (a new runner resuming a dead/hung loop): run the Acquisition
  CAS, increment `generation`, re-read-and-abort-if-not-owner, then proceed.
- **On a clean stop**, set `status` to `checkpointed` (checkpoint boundary) or
  `paused-external` (explicit external pause) so an observer reads idle/done, not
  hung.

**Full spec** (schema · acquisition CAS · liveness precedence · restart
preconditions): `primitives/lease-protocol.md`. The emitted lease is reviewable
on paper — an observer can compute hung/idle/alive by hand from the fields
above, without the watchdog existing yet.
