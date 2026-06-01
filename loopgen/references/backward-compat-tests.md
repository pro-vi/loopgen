# Backward-Compatibility Tests (U11 probe)

The promotion gate for `/loopgen`. The four **pure** archetype cases must
produce composed `loop/PROMPT.md` output structurally equivalent to the legacy
skill it replaces; the **hybrid** and **tier-0** cases exercise the new
capability and the degradation contract.

## Acceptance criteria

A composed prompt **passes** when its difference from the legacy reference is
limited to exactly three classes:

1. **the provenance preamble** (new, expected — the only addition for a pure
   case), and
2. **frontier pressure accounting** (accepted only for pure frontier), and
3. **cosmetic** whitespace / section-ordering.

Any **load-bearing** structural difference on a pure case (a missing section, a
changed rule, a weakened halt condition, a dropped invariant) is a **failure**
and blocks promotion until the design is revised.

## Cases

### 1. Pure frontier

- **Task:** "Run an evidence-driven improvement loop on this repo; make it
  better and keep the evaluator honest."
- **Expected bundle:** `target=frontier-expanding, halt=equilibrium,
  artifact=findings-ledger, convergence=homeostatic-checkpoint,
  cadence=checkpoint-gated`. Archetype `frontier`, divergences `none`.
- **Reference:** legacy `frontier-loop` output (`templates/bodies/frontier-body.md`
  filled).
- **Must contain:** the 5-axis homeostasis frame, signal hierarchy, same-family
  admissibility, frontier-anchor requirement, quiet-signal checkpoint,
  evaluator-maturity tier, and pressure fields `pressure_status`,
  `pressure_debt`, `checkpoint_reason`, `next_pressure`.
- **Must not contain:** benchmark-frontier artifact roles such as `CANDIDATES`,
  `DOMAIN_SPEC`, `FRONTIER`, candidate row fields, `eval_health`, candidate
  operators, or holdout role fields.

### 2. Pure goal

- **Task:** "Make these acceptance criteria pass without weakening them."
- **Expected bundle:** `target=finite-criteria, halt=terminal,
  artifact=acceptance-inventory, convergence=criteria-completion, cadence=sync`.
  Archetype `goal`, divergences `none`.
- **Reference:** legacy `goal-loop` output.
- **Extra artifact:** `loop/ACCEPTANCE.md` emitted.
- **Must contain:** oracle principles, terminal contract, final-verify, the
  acceptance inventory, oracle-drift guard, partial-deadlock vs criteria-met.

### 3. Pure story

- **Task:** "Maintain a living storyboard; verify one product promise per
  iteration on the report viewer."
- **Expected bundle:** `target=promise-discovery, halt=checkpoint-with-reopen,
  artifact=storyboard, convergence=capstone-plus-closer, cadence=chapter`.
  Archetype `story`, divergences `none`.
- **Reference:** legacy `story-loop` output.
- **Extra artifact:** `docs/storyboard.{md,yaml}` resolved.
- **Must contain:** Guidance Source + Story Record objects, status model,
  ready-gate, same-family drift guard, fixture-mode declaration; Surface Taste
  Lane only if the lane is the taste lane.

### 4. Pure greenfield

- **Task:** "Build me something Kurzgesagt-adjacent; I'll know it when I see it."
- **Expected bundle:** `target=discovery-reframing, halt=manual-gated,
  artifact=rubric+intent, convergence=stone-reframe, cadence=checkpoint-gated`.
  Archetype `greenfield`, divergences `none`.
- **Reference:** legacy `greenfield-loop` output.
- **Extra artifacts:** `loop/RUBRIC.md` + `loop/INTENT.md` (+ `loop/README.md`).
- **Must contain:** all 11 invariants, score-locked ramp, score quarantine,
  CAPABILITY mode, preloop/research phase gates with owners.

### 5. Cross-archetype divergence — bodytxt (story body, frontier-expanding target)

- **Task:** "Build an incremental gallery of pretext demos with overnight
  chapter cadence and frontier-model consults; keep evidence discipline."
- **Expected bundle:** `target=frontier-expanding, halt=checkpoint-with-reopen,
  artifact=storyboard, convergence=capstone-plus-closer, cadence=chapter,
  consult=tier-3`.
- **Classification:** nearest `story`, **distance 3** (margin 6 — frontier is 9,
  goal/greenfield 12). Single divergence: `target-shape: frontier-expanding`
  (only the target axis leaves the story defaults; halt / artifact / convergence
  / cadence are all pure story). Verify by computing the weighted-Hamming
  distances on the bundle (story 3 vs frontier 9 — not a tie).
- **Must contain:** the **story** body (storyboard artifact, chapter cadence,
  capstone-plus-closer convergence, checkpoint-with-reopen halt) with the
  `target-shape` swapped to `frontier-expanding`; the provenance preamble names
  that one divergence + its source. It must **NOT** carry a frontier homeostasis
  frame — nearest is story, so the body is the story body, not a frontier body.
- This case demonstrates the new capability: a story loop with a
  `frontier-expanding` target is a cross-archetype divergence no single legacy
  skill composed (`story-loop`'s target was always `promise-discovery`). It is
  **not** an equidistant hybrid — bodytxt sits firmly in story (distance 3,
  margin 6). A genuine equidistant hybrid (distance ~5–6 to its nearest, margin
  ≤1 to the second) has not yet been observed in a real run; if one appears,
  add it here as the equidistant case.

### 6. Tier-0 consult degradation (any archetype)

- **Task:** any case above, run in an environment with **no** consult channel.
- **Expected:** `consult-capability: tier-0`; every consult-dependent section
  removed (blind comprehension reads, scheduled creative consults, adversarial
  refute panels); a periodic human-look gate inserted; the degradation recorded
  in the provenance preamble. The composed prompt has **no** agentify / mcp
  references and the loop proceeds without consult invocation paths.

### 7. Contradiction (negative case)

- **Task:** "Make these finite criteria pass, but never stop — keep going
  forever." → `target: finite-criteria` + `halt: manual-gated`.
- **Expected:** Phase 2 HALTS classification with `classification error:
  incompatible primitives [target=finite-criteria, halt=manual-gated]` and
  fires AskUserQuestion. No prompt is emitted with a silent default.

### 8. Benchmark-frontier overlay

- **Task:** "Push the Weave quality benchmark overnight against braid-self,
  empty-greenfield, sibling repo, and holdout repo cases."
- **Expected bundle:** same weighted axes as pure frontier. Archetype
  `frontier`, divergences `none`, `overlay: benchmark-frontier`.
- **Must contain:** semantic artifact roles `DOMAIN_SPEC`, `BENCHMARK`,
  `CANDIDATES`, `FRONTIER`, and `traces`; candidate lineage; evaluator health;
  pressure debt; eval ladder; search/holdout/adversarial separation.
- **Must not:** appear as a fifth archetype, change weighted-Hamming distance,
  or make pure frontier emit the candidate artifact bundle.

### 9. Weave premature checkpoint regression

- **Task/result shape:** "16 traces green, 0 OPEN rows, no changed files, no
  candidate/case/control expansion."
- **Expected:** benchmark-frontier rejects checkpoint. It must expand a
  candidate, case, control, metric, project category, evaluator dimension, or
  artifact audit, or pause as `PAUSED_EXTERNAL` with
  `pressure_debt: explicitly_deferred`.

## How to run

The probe is an adversarial workflow: for each pure case, compose via the
Phase 1–3 procedure, diff the result against the legacy body
(`templates/bodies/<archetype>-body.md`), and classify each difference as
provenance / cosmetic / load-bearing. Rows 1–4 must show no load-bearing
difference; row 5 must contain the hybrid sections; row 6 must drop consult
sections; row 7 must halt with an error; row 8 must activate the overlay (emit
the `DOMAIN_SPEC` / `BENCHMARK` / `CANDIDATES` / `FRONTIER` / `traces` roles and
the eval ladder, with classification distance unchanged and the pure-frontier
render free of the candidate bundle); row 9 must reject the green-trace /
zero-OPEN / no-expansion shape as a checkpoint (expand a candidate/case/control,
or halt `PAUSED_EXTERNAL` with `pressure_debt: explicitly_deferred`).

All nine rows are required; a gate run that stops at row 7 does not exercise the
benchmark-frontier overlay this probe is meant to protect.
