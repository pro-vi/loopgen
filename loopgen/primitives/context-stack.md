# context-stack (shared primitive)

## Purpose

The memory model every loop runs inside. A loop's runner (`/goal`) re-sends
the *same* bare-pointer kick-off each iteration; in the modeled default
lifecycle (`context_mode_effective: rolling-lossy`) the window is **one
continuous conversation** — a **rolling lossy cache**: user-role text
survives compaction verbatim, assistant turns and tool outputs are
lossy-summarized near the ceiling — while `fresh-episode` restarts it cold
each episode and `unknown` declares neither; under every mode **files are
the durable memory**. A fact
held only in context can vanish at any compaction boundary; a fact held in a file
costs tokens every time it is re-read. This primitive gives every **access
path** exactly one **tier**, a hard **bound**, and a keyed **access
convention** — one file can expose more than one path at different tiers
(`JOURNAL.jsonl`'s tail-20 is WORKING while its `jq`-by-key path is ON-DEMAND) —
so the loop reads keys, not files, and its per-iteration ceremony
stays flat instead of growing with loop age. It is the shared home for the
`STATE.md` register, the `JOURNAL.jsonl` history schema, the `DERIVATION.md`
contract, and the context-budget assertion — collapsing what was four divergent
per-body STATE-key boilerplates into one edit site.

The full motivating measurement (a 33h dota-market run: 51 compactions, a 105 KB
`STATE.md`, a read-set that grew 4.25×, a dead `PRESSURE.md`) and the design
decisions live in ADR 0004.

## Include when

Emitted into **every** composed prompt — all four archetype bodies carry
`{{INCLUDE primitives/context-stack.md}}` in their Artifacts-to-maintain section.
The memory model is universal, so unlike `pressure` / `subagent-patterns` this
block is **never gated**: there is no runtime in which the context window is not
a lossy cache. Read at derivation time by every authoring run (it is a Tier-2
composition read in `SKILL.md`).

## The runtime being modeled

- `/goal` re-sends the same kick-off pointer into one conversation every
  iteration. The kick-off carries no instruction content; every rule lives in
  `.loop/<loop-id>/PROMPT.md`, which the agent must read from the pointer and
  rehydrate on the declared cadence.
- That continuous conversation is the `rolling-lossy` default lifecycle.
  `fresh-episode` and `unknown` (`context_mode_effective`, STATE schema
  below) share every file rule and differ only in the Operational core's
  rehydration cadence — behavior branches on the effective mode alone,
  never on requested mode or observed visibility.
- The window runs pinned near its ceiling (measured mean ~148k of 258k,
  compacting at ~240k). Context-held facts can be summarized away at any
  boundary; file-held facts persist but are re-paid per read.
- Therefore **every fact gets one canonical home and a declared re-read
  cadence.** A file that is re-read whole every pass must be bounded independent
  of loop age, or the read-set grows without limit. A file that only grows must
  never be on the per-pass re-read path.

## The four tiers

Every **access path** is assigned **exactly one** tier. Most artifacts expose a
single path; the split-path cases are deliberate (journal tail vs journal
by-key, queue index/live-rows vs queue archive) and each path carries its own
tier and bound:

- **PINNED** — re-read every pass at step 0; small enough to live in the window
  permanently. Bounded by fixed schemas, not by loop age.
- **WORKING** — read once at iteration start; the read cost is O(1) regardless of
  how long the loop has run, because the surface is an index + the live rows, not
  the whole file.
- **ON-DEMAND** — read only by key, never whole-file: the rare pass that needs
  prior art, plus human review and diagnostics.
- **WRITE-ONLY** — the loop writes it and never re-reads it within the loop; it
  exists for the terminal report or for external watchers.

## Design rationale (not emitted)

- **Live status and history have different lifetimes.** Mixing them in one
  growing `STATE.md` is what produced the 105 KB file and the 4.25× read-set
  growth. The split keeps the PINNED surface small forever while history
  accumulates where it is never read whole.
- **In-force pressure stays PINNED; transitions go to the journal.** The
  `active`/`hardened` rows are legitimately live status and are bounded by
  `pressure-cap`, so they stay in `STATE.md` (the pressure re-render / crash-
  recovery doctrine in `pressure.md` depends on `STATE.md` being the source of
  truth). Only the unbounded transition/consult histories move to the journal —
  the doctrine survives untouched.
- **One history surface, no monitor file.** A CHECKPOINTS-style human-watch file
  is a second history that drifts from the first; it is an anti-pattern. Humans
  watch via the journal one-liner; the loop records delta-only `checkpoint`
  records.
- **A bound the runner cannot see does not exist.** The cap arithmetic and access
  commands are stated in the *emitted* block, not just here, so the O(1) read-set
  is enforced at runtime rather than merely intended.
- **A bound the runner never checks decays.** The prompt text and the
  authoring-time verifier prove the contract *exists*, not that a degraded
  post-compaction agent still *obeys* it at hour 20 — the observed failure shape
  is "I need context" → whole-file read, "temporary" cap widening, a journal
  record whose evidence file was never written, a queue section updated without
  its index row. The context-health check in the emitted block is the cheap
  in-loop detector: a bounded command ritual whose failure routes to repair
  *before* task work, making the compliant path cheaper than the noncompliant
  one. (Hardening from the pre-ship design review, 2026-07-07 — see ADR 0004.)
- **Consolidation is triggered, not only scheduled.** The measured incident
  behind it (dota-market Supabase pooler phantom commits — ADR 0005) burned
  iterations on locally-correct app-layer fixes while the violated contract
  (transaction transport semantics) sat below the code; the decisive shift came
  only when a fresh look attacked the contradiction directly. A cadence-only
  round would let the loop grind until the next multiple of 10; the forced
  triggers (2+ survived fixes, unmoved metric, local/durable disagreement,
  impossible observation, defensive-code accumulation) fire the round the
  moment the signals exist — and the signals are free, because the pressure
  machinery already records them (`no-effect` consults, rows paid without
  target movement). This is also why it is not a separate primitive: the
  trigger data, the field being read, and the merge machinery all live in
  pressure + journal already; a fifth artifact role would be the exact creep
  the storage rules forbid.

---

## Context stack — the memory model

Your runner re-sends only the bare-pointer kick-off each iteration; it never
re-sends this file's contents. Keeping the prompt contract current in the
window is therefore your rehydration responsibility, not the runner's. What
the window does between iterations is `context_mode_effective` in `STATE.md` —
`rolling-lossy` (one continuous conversation; user-role text survives
compaction, assistant/tool output is summarized away near the ceiling),
`fresh-episode` (a cold window every episode), or `unknown` — resolved only from
an operator declaration or runner attestation, never from what the window seems
to show. Runner
attestation is **reserved**: no current runner emits one, so unless an
operator declared the mode it stays `unknown` (rehydrate every iteration) —
do not synthesize an attestation from the window. Under every mode **the
files under `.loop/<loop-id>/` are the durable memory**. Read keys, not
files. Every access path below has exactly one tier and a hard bound (one file
may expose two paths at different tiers — the journal's tail is WORKING, its
keyed history ON-DEMAND); honor each path's access command and never promote an
ON-DEMAND read to a per-pass whole-file read.

### Tier contract

| Tier | When read | Members | Bound |
|---|---|---|---|
| **PINNED** | every pass, step 0 | `PRESSURE.md` (HUD), `STATE.md` (live status) | fixed schemas; `STATE.md` ≤ ~50 lines; in-force pressure set ≤ `pressure-cap` (default 12) |
| **WORKING** | once at iteration start | the queue artifact's **index + OPEN/current sections**; `tail -n 20 .loop/<loop-id>/JOURNAL.jsonl` | index+sections addressing; `closed-retain-N` (default 20); tail-N |
| **ON-DEMAND** | keyed reads only, never whole-file | `JOURNAL.jsonl` history by key (`jq`), `.loop/<loop-id>/archive/*`, `DERIVATION.md`, trace/metric targets | the documented access command below |
| **WRITE-ONLY** | written, never re-read in-loop | `VERIFY.md` (terminal final-verify only), journal `checkpoint` records | delta-only ("unchanged since iter N") |

### `STATE.md` — PINNED live status (fixed keys, rewrite-in-place, **no history, ever**)

`STATE.md` holds **only** current live status: one line per key, overwritten in
place. It is never appended to. Anything that accumulates across iterations
belongs in `JOURNAL.jsonl`, not here. If `STATE.md` grows past ~50 lines the
discipline is broken — a history stream has leaked in; move it to the journal.

Common keys, every archetype:

- `archetype`, `identity`
- `consult_tier`, `evaluator_tier`
- `consult_tier_effective` — the run-host resolution of the consult tier
  (value + per-channel basis), written by the iteration-0 Run-host channel
  check and overwritten on re-verification
  (`primitives/consult-capability.md`); `n/a` at tier-0
- `context_mode_effective` — the run-host resolution of the loop's context
  lifecycle (`fresh-episode` / `rolling-lossy` / `unknown`), with
  `context_mode_resolution_basis` from the closed set `operator-declared` /
  `runner-attested` / `unknown` — never observation: model-visible history
  proves neither mode (a fresh runner may be handed replayed context; a
  rolling window may already be compacted). `runner-attested` is reserved —
  no current runner emits an attestation, so today the basis resolves only
  `operator-declared` or `unknown`; do not synthesize one. Seeded at bootstrap
  from the derivation's `context_mode_requested` when its basis was an operator
  statement; with no declared or attested basis it stays `unknown` — an
  honest value, not a gap to fill
- `history_visibility_observed` — what the window currently shows
  (`prior-context-visible` / `fresh-window` / `unknown`), overwritten when
  checked. A visibility fact only: it is never a
  `context_mode_resolution_basis` and never converts into a mode claim
- `artifacts` (`{canonical, repo_aliases}`)
- `iteration`, `phase`, `current_artifact`, `last_action`, `next_action`
- `halt_cause`, `halt_scan` (overwrite-latest: the most recent full-surface scan
  only; the durable event is the `halt` journal record)
- `pressure_objects` — **in-force rows only** (`active` / `hardened`), bounded
  ≤ `pressure-cap`. The transition history is *not* here; it is the `pressure`
  journal record type.

Per-archetype live keys (your archetype's row applies; the rest are for readers
resuming a hybrid):

| Archetype | Added live keys |
|---|---|
| `goal` | `goal_version`, `current_criterion`, `stuck_counters`, `final_verify` |
| `story` | `storyboard_path`, `lane`, `surface_class`, `current_story`, `last_surface`, `last_story_family`, `same_family_count`, `fixture_mode`, `evidence_manifest`, `last_validation_commands`, `remaining_findings_classified` |
| `frontier` | `frontier_vector`, `current_anchor`, `reward_channels`, `pressure_status`, `pressure_debt`, `checkpoint_reason`, `next_pressure`, `trace_locations`, `metric_locations`, `guardrails` |
| `greenfield` | `score_lock`, `phase_gates`, `current_stone_axis`, `user_halt_owner` |

**Moved out of `STATE.md`** (they were append-only history in disguise): the
former `pressure_ledger` → `pressure` journal records; `pressure_consulted` →
`consult` journal records; goal's `oracle_change_notes` → `oracle_change` journal
records; greenfield's `capability_list` → the `README.md` capability surface. The
write-once derivation record moved to `DERIVATION.md` (below). Frontier's
`pressure_status` / `pressure_debt` / `checkpoint_reason` / `next_pressure` stay
— they are a bounded checkpoint-level aggregate over the in-force rows, not a
transition log.

### `JOURNAL.jsonl` — the single append-only history

One typed JSON record per line, **target ≤300 chars — short by default, but
never truncate a required field**: a longer record that keeps the failure facts
beats a clipped one pointing at nothing. Evidence is carried as **pointers** (a
path, an `AC-id`, a commit — prefer `path#line-range` or path + hash for
load-bearing evidence) never inlined blobs, and evidence is **write-ahead**:
save the trace / command output to its file *first*, then append the record
that points at it — a pointer to a file that does not exist yet is a protocol
violation the context-health check below will catch. `JOURNAL.jsonl`
is the *only* history surface — there is no separate CHECKPOINTS / monitor file.

Record types (`t`), each with `iter` (iteration) plus type-specific fields:

| `t` | Written when | Key fields | Archetypes |
|---|---|---|---|
| `attempt` | each iteration's attempt resolves | `ac`/`anchor`, `action`, `verdict`, `evidence` (pointer); frontier also `disturbed_axis` (the closed axis key — the same-family counter's evidence) | all |
| `oracle_change` | an oracle / criterion is added, edited, or re-scoped | `ac`, `from`, `to`, `why`; goal verifier edits also `fault`, `strictness_proof`, `rollback_trigger` | goal (+ any with an oracle) |
| `pressure` | a pressure row transitions (replaces `pressure_ledger`) | `id`, `from`, `to`, `evidence` | all |
| `consult` | step-0 pressure read-back (replaces `pressure_consulted`) | `consulted` (id→plan-element) or `no-promotion: <reason>` | all |
| `alignment_review` | a defaulted judgment / Alignment Review is recorded | `item`, `decision`, `anchor`; as a Human-look review packet also `packet` (stable id), `question` | all |
| `checkpoint` | a delta-only status change worth a timestamp | `changed` (field→new), else omit | all |
| `halt` | a full halt-scan event fires | `cause`, `scan` (surface→state), `open` | all |
| `score_quarantine` | greenfield reframes the rubric and quarantines old scores | `rubric_from`, `rubric_to`, `quarantined` | greenfield |
| `bootstrap` | one-time setup completes | `what`, `files` | all |
| `consolidation` | on the cadence or any forced trigger — see the Consolidation round below | `lesson` (what recent attempts taught), `covers` (iter range / ids), optional `field` (row-id clusters), `suspected_substrate`, `decision` | all |

`consolidation` is the journal's lessons layer: events record *what happened*;
a consolidation distills *what it taught* — compact enough that the tail-20
read after a compaction naturally resurfaces the latest lessons instead of raw
attempts. It never restates rows that are still live in STATE or the queue.

Access:

- **Per pass (WORKING):** `tail -n 20 .loop/<loop-id>/JOURNAL.jsonl` — recent
  history only; never read the whole file per pass.
- **Keyed (ON-DEMAND):** `jq -c 'select(.ac=="AC-006")' .loop/<loop-id>/JOURNAL.jsonl`
  (swap the selector for `.id`, `.t`, `.anchor`, …) — pull one thread on the rare
  pass that needs prior art. **Fire a keyed read when:** the same criterion /
  anchor has failed twice (pull its thread before the third attempt); a reopen
  condition is being weighed (read only that archived row); or pressure is
  alternating across scopes (pull recent `pressure` records by scope). Needing
  *many* keys at once is the signal to write a `consolidation`, not to read the
  whole file — a full-history read is a named diagnostic exception (halt
  analysis / Diagnostic mode), never a normal move.
- **Human watch (WRITE-ONLY, external):**
  `tail -5 .loop/<loop-id>/JOURNAL.jsonl | jq -r '[.iter,.t,.ac//.id//.packet,(.verdict//.to//.question//.changed)|if (type=="object" or type=="array") then tojson else . end]|@tsv'`.

### Consolidation round — reading the field, auditing the substrate

Consolidation is not just a summary: it is the pass where you stop advancing
the queue and *feel where the pressure is* — the one bounded moment the loop
reads its whole situation instead of the next row. It runs on a **schedule**
(every ~10 iterations, on a criterion/story/anchor closure, or before
final-verify) and is **forced early** by any of these triggers, whichever
comes first:

- the same scope survived **2+ correct-looking fixes** — attempts verified
  locally, yet the pressure row on that scope logs `no-effect` or the target
  does not move;
- the target metric did not move after fixes that should have moved it;
- a proof passes locally while production / durable state disagrees;
- you hold an **impossible observation** — two facts that cannot both be true
  under your current model (e.g. a transaction returned rows that later reads
  cannot find);
- recent fixes are adding defensive code without reducing uncertainty.

The round is one bounded read-and-write, not an open investigation:

1. **Read the field.** Take the whole in-force pressure set as one field, not
   row by row: which rows cluster around a shared suspected cause? Name the
   impossible observation if one exists. (Per-row hygiene cannot see this —
   each row can be individually justified while the field says one thing.)
2. **Audit the contract layer beneath the code.** When a cluster's members are
   each locally correct yet the target does not move, the violated contract
   usually sits one layer below what the loop is modeling. Enumerate the
   guarantees the code relies on — deployed commit, environment/service-identity
   parity, DB transport / pooler mode, driver transaction semantics, queue
   ownership, external API authority — and classify each as **checked at
   runtime**, **inferred from config**, or **unverified**. Any guarantee
   required for correctness but unverified must become a runtime check, a
   launch invariant, or an explicit blocked condition — or the loop's
   confidence in the moves that assumed it is downgraded.
3. **Act on the reading.** Merge clustered rows into one row scoped at the
   shared cause (the merge conserves the debt — `primitives/pressure.md`);
   stamp `suspected_substrate: <layer>` on the merged row and the record when
   the cause sits below the code; promote what the window taught into the
   record's `lesson`.
4. **Decide, and record the decision** in the `consolidation` record's
   `decision`: **continue** the loop as modeled; **fork** — route the named
   contradiction to the consult resolution — the consult channel
   `consult_tier_effective` proves live, else the tier-0 Human-look gate's
   review packet — as a fresh root-cause attack (attack
   the contradiction directly, not the current criterion — a fresh look
   unanchored from the queue is what breaks the frame); or **cleanup** — after
   a substrate cause is confirmed, mint a row to audit symptom-era defensive
   fixes ("does this code encode a permanent invariant, or compensate for the
   old broken world?").

Skipping a triggered consolidation to keep advancing the queue is the measured
failure mode this round exists for: a loop that grinds on downstream symptoms,
each fix locally reasonable, while the real violated contract sits a layer
lower than anything it reads.

### `DERIVATION.md` — write-once derivation record (ON-DEMAND)

Written once at bootstrap, read on demand (diagnostics / resume), **never per
pass**. Records how this loop was composed:

- `primitive_bundle` — the classified axis values.
- `divergences` — each axis whose value differs from the nearest archetype, with
  its source. A compiler-derived resolution (the halt-shape guarded
  closed-corpus rule) records the full triple
  `{requested, effective, resolution_basis}` — the emitted provenance line
  renders from it, and resume / diagnostic readers reconstruct why the emitted
  block was selected without re-deriving.
- `overlays` — active composition overlays.
- `derivation_read_set` — the files `/loopgen` read to compose this loop,
  recorded here in `DERIVATION.md` on successful composition only (a decline
  writes nothing).
- `frontload` — `{resolved, defaulted, open_gaps}`. For frontier this carries
  the reopening-contract fields, and when the reopening contract resolved to
  a closed-world `none`, the four-field `closure_basis` plus
  `declared_workset_version: <loop-id>` —
  the workset version is the loop id the derivation minted; this file is
  write-once, so a running loop can never mint a new version or mutate the
  declared workset's identity. Every archetype's `frontload` also records the
  runner-lifecycle declaration: `context_mode_requested` (`fresh-episode` /
  `rolling-lossy` / `unknown`) with `context_mode_compose_basis` (operator
  statement · declared runner profile · `unknown` default — never inferred
  from visible history). This is the compiler-owned half of the context-mode
  split; the run-host half is `STATE.md` `context_mode_effective` (above).

### Context budget

The Operational core near the top of `PROMPT.md` restates this budget as a table
(file → tier → cap → access command → human watch command) so post-compaction
rehydration is a bounded `sed -n '1,80p' .loop/<loop-id>/PROMPT.md`, not a
whole-file re-read.

**Budget assertion.** A PINNED or WORKING read that exceeds its declared cap
means the file discipline is broken, not that the cap is wrong: a `STATE.md` past
~50 lines, an in-force pressure set past `pressure-cap`, or a queue LIVE window
past `closed-retain-N` is a signal to **archive or collapse first**, before the
next decision — symmetric with the oracle-integrity checks that treat a violated
invariant as a `derivation-gap`, never as a reason to widen the bound. Silent
growth is the failure this whole model exists to prevent.

### Rehydration cadence

The Operational core's bounded re-read
(`sed -n '1,80p' .loop/<loop-id>/PROMPT.md`) fires on the cadence
`context_mode_effective` sets — **after** the mode is resolved, never before:

| `context_mode_effective` | re-read the Operational core |
|---|---|
| `rolling-lossy` | after any detected compaction |
| `fresh-episode` | at every episode start |
| `unknown` | at every iteration start (conservative — neither lifecycle assumed) |

**A trigger is not a basis.** Detecting a compaction, or what the window shows
(`history_visibility_observed`), fires the cadence for an **already-resolved**
mode; neither determines `context_mode_effective` and neither converts into a
mode claim. Resolution stays `operator-declared` / `runner-attested` /
`unknown` — never observation (above). An unresolved mode is `unknown`, which
is exactly why `unknown` re-reads at every iteration start.

### Context-health check

The budget assertion is only real if it is *checked*. At **step 0, right after
the pressure render** — and again after any compaction you can detect (the
conversation summary replacing earlier turns) — run this bounded ritual before
task work. Each line is one cheap command, not an investigation:

1. `STATE.md` line count ≤ ~50.
2. In-force pressure rows ≤ `pressure-cap`.
3. `tail -n 20 JOURNAL.jsonl` parses as JSONL (`jq -e . >/dev/null` per line, or
   `jq -es 'length>=0'` over the tail).
4. The evidence pointers in the most recent ~5 journal records **resolve** —
   the files exist (write-ahead was honored).
5. The queue **index row** for the current item agrees with that item's
   `## <id>` section (status + counters).
6. No whole-file read of an append-only artifact happened since the last check
   unless a diagnostic exception was named.
7. The most recent `consolidation` record is within cadence (~10 iterations:
   `jq -s '[.[]|select(.t=="consolidation")]|last.iter' JOURNAL.jsonl`) **and**
   no forced consolidation trigger has fired since it (Consolidation round,
   above).
8. `consult_tier_effective` in `STATE.md` still describes **this** host: `n/a`
   at tier-0 (there is no consult contract to keep fresh), otherwise the
   recorded value **and** its per-channel basis are still true here. A runner
   change, or any promised channel failing, invalidates the cached value —
   re-verify before consulting.

**A failed line is a routing, not a warning:** past-cap → archive/collapse now;
unparseable tail → repair the malformed record now; dangling evidence → write
the missing file or correct the record now; index/section disagreement →
reconcile from the authoritative surface now (the index owns status/counters —
`primitives/queue-as-second-artifact.md`); stale `consult_tier_effective` →
re-verify the promised channels **non-interactively** now, overwrite the value
and its per-channel basis in `STATE.md`, and degrade **only** the channels that
are actually missing (each to its next-lower substitute: tier ≥ 2 → tier-1
human-bridge → tier-0 human-look gate), never the whole tier; overdue or
triggered consolidation →
run the Consolidation round now, before the next attempt; only then proceed to
the iteration.
A violation that cannot be repaired locally is a `derivation-gap` halt, never
something to work around. The check exists because a post-compaction pass
half-remembers the contract: it makes the contract cheaper to re-honor than to
drift from.
