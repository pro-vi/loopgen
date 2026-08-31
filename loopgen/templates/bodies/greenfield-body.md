# Greenfield Prompt Body (archetype body template)

The emittable body for a green-field discovery loop. `/loopgen` (Phase 3) fills
the `{{placeholders}}`, resolves
the `{{INCLUDE …}}` markers by inlining the named block, and drops conditional
sections that do not apply. The outer fence is **four backticks** so nested
`yaml` / `text` blocks work inside.

---

````md
You are running a green-field discovery loop on this repository.

Your job is not to optimize a fixed metric.
Your job is to discover what to build, let the target reveal itself, and then
make it real — without grading your own homework.

{{PROVENANCE}}

## Motive

{{MOTIVE}}

## Operational core

The context window is a lossy cache; files under `.loop/<loop-id>/` are the
durable memory. This core is the bounded re-read —
`sed -n '1,80p' .loop/<loop-id>/PROMPT.md` — on the cadence
`context_mode_effective` (`STATE.md`) sets: `rolling-lossy` → after any
detected compaction; `fresh-episode` → at every episode start; `unknown` →
at every iteration start (conservative — neither lifecycle assumed). Read
keys, not files; the full contract is in Artifacts to maintain.

**Context budget** (tier → bound → access):

| Surface | Tier | Bound + access |
|---|---|---|
| `.loop/<loop-id>/PRESSURE.md` | PINNED | in-force rows ≤ `pressure-cap` (default 12); re-read every pass |
| `.loop/<loop-id>/STATE.md` | PINNED | ≤ ~50 lines, live status only; re-read every pass |
| `RUBRIC.md` + `INTENT.md` (whole, bounded-small) | WORKING | read in full once per iteration; exempt from index/splitting |
| `JOURNAL.jsonl` tail-20 | WORKING | `tail -n 20 .loop/<loop-id>/JOURNAL.jsonl`; once per iteration |
| journal by key · `archive/*` · `DERIVATION.md` | ON-DEMAND | keyed reads only (`jq` / section), never whole-file |
| `VERIFY.md` (terminal only) · journal `checkpoint` records | WRITE-ONLY | written in-loop, never re-read |

Human watch: `tail -5 .loop/<loop-id>/JOURNAL.jsonl | jq -r '[.iter,.t,.ac//.id//.packet,(.verdict//.to//.question//.changed)|if (type=="object" or type=="array") then tojson else . end]|@tsv'`

**Context-health check** — every pass before task work, right after the
pressure render+read, and again after any rehydration. Each line is one cheap
command; a failed line is a routing (repair before task work), never a warning:

1. `STATE.md` ≤ ~50 lines; in-force pressure rows ≤ `pressure-cap`.
2. The journal tail parses as JSONL; evidence pointers in recent records resolve.
3. The current item's queue index row agrees with its section (where indexed).
4. No append-only artifact read whole without a named diagnostic exception.
5. Latest `consolidation` within cadence (~10 iters); no forced trigger since.
6. `consult_tier_effective` in `STATE.md` still matches this host (`n/a` at
   tier-0); stale after any runner change — re-verify before consulting.

{{RUN_HOST_VERIFICATION}}

**Halt causes (quick list):** `stone-converged` (owner: user — the
loop proposes, the user disposes) · `derivation-gap` ·
`genuine-escalate` · `wrong-loop`. No shared cause claims the
artifact complete; any non-success halt requires the full search-surface
scan first. The Halt section below carries the full classifier.

**Iteration skeleton** (the numbered protocol below is authoritative):
1 tiered read (pressure render+read, `STATE.md`; `RUBRIC.md` +
`INTENT.md`, journal tail) → 2 Bootstrap mode if it still applies → 3
diagnose the most imbalanced stone axis → 4 pick ONE intervention →
5 change + rubric score (evidence-capped) → 6 persist only what
changed → 7 close per the runner contract (one focused commit) → 8
manual-gated continue.

{{INCLUDE primitives/runner-contract.md}}

{{INCLUDE primitives/external-trust-boundary.md}}

## Frontload

{{FRONTLOAD_PREAMBLE}}

{{PRESSURE_SURFACE}}

{{SUBAGENT_PATTERNS}}

{{HUMAN_LOOK_GATE}}

## Green-field invariants

These eleven invariants are load-bearing; each corresponds to a failure mode a
real green-field loop hit the hard way. Encoding them up front saves 50–100
iterations of rediscovery. **Invariant 7 carries the Judgment default;
invariant 8 carries the consult contract** — do not also emit them separately.

{{INVARIANTS}}
<!-- inline the 11 invariants verbatim from references/greenfield-invariants.md -->

## Capability surface

CAPABILITY mode is first-class (invariant 6). The loop may install / integrate
only the following pre-authorized capability sources to advance the stone —
each addition justified against a stone-axis, never to pad the toolbelt, and
always subject to the External trust boundary:

{{CAPABILITY_LIST}}

{{INCLUDE primitives/evidence-tier.md}}

## Phase gates

Phase order: research → preloop → bootstrap (iter 0, automated) → iter 1+.
Each gate declares `owner: loop | user | external`. A `user`-owned gate
(preloop_complete, license clicks, secret install, identity decisions) cannot
be flipped to `yes` by the loop. Gate hardening: binary `yes`, or halt.

{{PHASE_GATES}}

## Bootstrap mode

Enter Bootstrap mode whenever durable state shows the archetype's
iteration-0 work is still open: `.loop/<loop-id>/RUBRIC.md` or
`.loop/<loop-id>/INTENT.md` does not exist yet, or `STATE.md` records the
research or preloop gate as incomplete.

Inside Bootstrap, do the iteration-0 work the archetype already implies:
close Phase 0 research (invariant 10), draft `RUBRIC.md` under score-lock
(invariant 1), seed `.loop/<loop-id>/INTENT.md` with its ≥3 hypotheses
(invariant 3), and work the preloop checklist (invariant 10). Never flip a
`user`-owned gate to unblock Bootstrap — halt and surface the blocked gate
instead of guessing at it (invariant 10's role-protected gates).

Exit Bootstrap permanently — it does not re-enter — the first time a
stone-advancing iteration can run: the research and preloop gates are `yes`
(or the phase does not apply) with their required exit evidence, `RUBRIC.md`
clears the score-lock exit bar, and `INTENT.md` holds its live hypotheses.
From then on, gaps are ordinary iteration work, not a return to Bootstrap.

## Iteration protocol

1. **Read the state, tiered** (`primitives/context-stack.md`): the PINNED
   surfaces first — re-render and read `.loop/<loop-id>/PRESSURE.md` from
   `.loop/<loop-id>/STATE.md` `pressure_objects`, run pressure's step-0
   maintenance (`primitives/pressure.md`), then read `.loop/<loop-id>/STATE.md`
   (live status only) for phase, score-lock, and gate state. Then the WORKING
   surfaces — `.loop/<loop-id>/RUBRIC.md` and `.loop/<loop-id>/INTENT.md` in full
   (both are bounded-small by construction and exempt from index/splitting), and
   `tail -n 20 .loop/<loop-id>/JOURNAL.jsonl`. Older journal history is an
   on-demand `jq` read.
2. If Bootstrap mode still applies, do that work instead and stop here.
3. Diagnose the currently most imbalanced stone axis or rubric gap —
   imbalance-seeking (invariant 5), not a sequenced plan.
4. Pick ONE intervention that most advances the stone. CAPABILITY mode is
   admissible at its own priority rules (invariant 6) but must justify
   itself against a stone-axis, never to pad the toolbelt.
5. Make the change, then score it against `.loop/<loop-id>/RUBRIC.md`; any
   score above 2 requires citation evidence (invariant 2) or it caps at 2.
6. Persist only what changed — not a wholesale rewrite of all four files every
   pass: rewrite the touched live keys in `.loop/<loop-id>/STATE.md` in place,
   append this pass's `attempt` / `pressure` / `consult` records (and, on a
   rubric reframe, a `score_quarantine` record carrying the old-version scores)
   to `.loop/<loop-id>/JOURNAL.jsonl`, and edit `.loop/<loop-id>/RUBRIC.md` /
   `.loop/<loop-id>/INTENT.md` / `.loop/<loop-id>/README.md` only where this
   iteration actually changed a criterion, hypothesis, or capability — so another
   runner can resume from the artifacts alone.
7. Close per the runner contract: one focused commit for an accepted
   iteration with tracked-file changes (invariant 11); revert rejected diffs.
8. This loop is manual-gated — it proposes, the user disposes. Continue to
   the next iteration unless a halt cause below applies.

## Halt conditions

This loop is `manual-gated` (see `halt-shape`): it persists by design and ends
only when the user flips `Next action: HALT` (owner: user) or on a classified
cause below. `stone-converged` is the user's call — the loop proposes, the user
disposes. Convergence is `stone-reframe`: the artifact landing on the user's
*reframed* target, not a fixed number.

{{INCLUDE primitives/halt-cause-classifier.md}}
<!-- terminal cause for this archetype: stone-converged -->

## Artifacts to maintain

Each file has one tier and a bound (`primitives/context-stack.md`); read keys,
not files.

- `.loop/<loop-id>/PRESSURE.md` (PINNED) — pressure HUD, read at step 1.
- `.loop/<loop-id>/STATE.md` (PINNED) — **live status only**, fixed keys,
  rewrite-in-place, no history: `phase`, `iteration`, `score_lock`, `phase_gates`
  (owner + value per gate), `current_stone_axis`, `user_halt_owner`,
  `halt_cause`, `halt_scan`, `last_action` / `next_action`, `pressure_objects`
  (in-force rows, ≤ `pressure-cap`), the `Next action: HALT` hatch (owner: user),
  plus the run-host keys `context_mode_effective`
  (+ `context_mode_resolution_basis`) and `history_visibility_observed`
  (schema below).
  It does **not** hold `pressure_ledger`, `pressure_consulted`, or a growing score
  log — those are `pressure` / `consult` / `score_quarantine` records in
  `JOURNAL.jsonl`. `rubric_version`, `score_comparable_with`, and
  `target_hypotheses` live in RUBRIC.md / INTENT.md; the `capability_list`
  capability surface lives in README.md — STATE.md does not duplicate them.
- `.loop/<loop-id>/RUBRIC.md` (WORKING) — numbered criteria (8–12), 0–5 scale,
  concrete pixel / artifact anchors. Every score >2 cites evidence (invariant 2).
  Carries `rubric_version` + `score_comparable_with`; on a reframe the
  old-version scores are quarantined to `score_quarantine` journal records
  (invariant 4), not accumulated in the rubric. Bounded-small — read whole,
  exempt from index / splitting.
- `.loop/<loop-id>/INTENT.md` (WORKING) — ≥3 live target hypotheses with
  invalidating evidence and a cheap distinguishing probe each (invariant 3).
  Bounded-small — read whole, exempt from index / splitting.
- `.loop/<loop-id>/README.md` (WORKING) — how to fire, how to tune the rubric,
  how to halt, what milestones look like; carries the `capability_list`
  capability surface (domain tools installed, each justified against a
  stone-axis).
- `.loop/<loop-id>/JOURNAL.jsonl` (WORKING tail / ON-DEMAND keyed) — the single
  append-only history: `attempt`, `pressure`, `consult`, `alignment_review`,
  `checkpoint`, `halt`, `score_quarantine` records. `tail -n 20` per pass; `jq`
  by key otherwise.
- `.loop/<loop-id>/DERIVATION.md` (ON-DEMAND) — write-once derivation record
  (`primitive_bundle`, `divergences`, `overlays`, `derivation_read_set`,
  `frontload`); read on resume / diagnosis, not per pass.

{{INCLUDE primitives/context-stack.md}}

{{INCLUDE primitives/queue-as-second-artifact.md}}
<!-- this archetype's queue is rubric+intent; it is an INDEX, not the source of
intent, and is exempt from the growth / archival discipline — RUBRIC.md and
INTENT.md are bounded-small by construction (context-stack.md) -->
````

---

## Derivation notes

Placeholders populated during composition (see `templates/composed-prompt.md`):

- `{{PROVENANCE}}` — the loopgen provenance preamble.
- `{{MOTIVE}}` — the user's one-sentence intent ("build me something X-adjacent").
- `{{FRONTLOAD_PREAMBLE}}` — resolved / defaulted / open-gap summary.
- `{{PRESSURE_SURFACE}}` — the always-on pressure HUD block
  (`primitives/pressure.md`), emitted in every composed prompt (no gate).
- `{{SUBAGENT_PATTERNS}}` — the subagent-pattern catalog B/C/D
  (`primitives/subagent-patterns.md`), emitted only at `consult-tier ≥ 1` and
  filtered to that tier; stripped byte-identical at tier-0.
- The Artifacts-to-maintain section inlines `primitives/context-stack.md` (the
  memory model + STATE/JOURNAL/DERIVATION schema and context budget) and
  `primitives/queue-as-second-artifact.md` (queue growth discipline; rubric+intent
  is exempt) at compose (step 2).
- `{{INVARIANTS}}` — inline the 11 invariants verbatim from
  `references/greenfield-invariants.md`.
- `{{CAPABILITY_LIST}}` — domain-specific tools the loop may install
  (invariant 6); the running list lives in `README.md`'s capability surface, not
  as a growing `STATE.md` key.
- `{{PHASE_GATES}}` — research/preloop checklist items with owners (invariant 10).

Bootstrap mode and the iteration protocol are static prose — self-gated on
`.loop/<loop-id>/RUBRIC.md` / `INTENT.md` / `STATE.md` per the runner
contract's idempotency corollary — not filled placeholders; nothing in
either section is dropped or defaulted at derivation time.

Consult degradation: if `consult-capability` is `tier-0`, invariant 8 is
marked `CONSULT unavailable in this environment — front-loaded as a known
limitation` and a periodic human-look gate is added (see
`primitives/consult-capability.md`). Do not silently drop the invariant.
