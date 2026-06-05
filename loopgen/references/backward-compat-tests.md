# Backward-Compatibility Tests (U11 probe)

The promotion gate for `/loopgen`. The four **pure** archetype cases must
produce composed `loop/PROMPT.md` output structurally equivalent to the legacy
skill it replaces; the **hybrid** and **tier-0** cases exercise the new
capability and the degradation contract.

## Acceptance criteria

A composed prompt **passes** when its difference from the legacy reference is
limited to these accepted classes:

1. **the provenance preamble** (new, expected — identifies the composed source
   values),
2. **the frontload preamble** (new, expected — every composed prompt records
   resolved / defaulted / open derivation gaps),
3. **frontier pressure accounting** (accepted only for pure frontier),
4. **canonical artifact/state contract references** (`loop/STATE.md`
   `derivation_read_set`, canonical file names, repo aliases), and
5. **cosmetic** whitespace / section-ordering.

The `{{PRESSURE_SURFACE}}` weather block is **gated on ≥1 compose-time pressure
object**. A pure case seeds and mines no pressure, so the block is stripped and
absent — it adds no accepted-delta class (see case 10). A case that intentionally
seeds pressure is, by definition, not a pure case (see case 11).

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
- **Extra artifacts:** `loop/FINDINGS.md`, `loop/TRACES.md`, `loop/METRICS.md`.
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
- **Extra artifacts:** `loop/ACCEPTANCE.md`, `loop/VERIFY.md`.
- **Must contain:** oracle principles, terminal contract, final-verify, the
  acceptance inventory, oracle-drift guard, partial-deadlock vs criteria-met.

### 3. Pure story

- **Task:** "Maintain a living storyboard; verify one product promise per
  iteration on the report viewer."
- **Expected bundle:** `target=promise-discovery, halt=checkpoint-with-reopen,
  artifact=storyboard, convergence=capstone-plus-closer, cadence=chapter`.
  Archetype `story`, divergences `none`.
- **Reference:** legacy `story-loop` output.
- **Extra artifact:** `docs/storyboard.md`.
- **Must contain:** Guidance Source + Story Record objects, status model,
  ready-gate, same-family drift guard, fixture-mode declaration; Surface Taste
  Lane only if the lane is the taste lane.

### 4. Pure greenfield

- **Task:** "Build me something Kurzgesagt-adjacent; I'll know it when I see it."
- **Expected bundle:** `target=discovery-reframing, halt=manual-gated,
  artifact=rubric+intent, convergence=stone-reframe, cadence=checkpoint-gated`.
  Archetype `greenfield`, divergences `none`.
- **Reference:** legacy `greenfield-loop` output.
- **Extra artifacts:** `loop/RUBRIC.md`, `loop/INTENT.md`, `loop/README.md`.
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
  that one divergence + its source. The artifact contract includes
  `docs/storyboard.md` plus `loop/TRACES.md` and `loop/METRICS.md` because the
  `frontier-expanding` target needs measurable before/after evidence. It must
  **NOT** carry a frontier homeostasis frame or `loop/FINDINGS.md` unless
  `artifact-shape: findings-ledger` is also active — nearest is story, so the
  body is the story body, not a frontier body.
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
  `CANDIDATES`, `FRONTIER`, and `traces` with canonical paths
  `loop/DOMAIN_SPEC.md`, `loop/BENCHMARK.md`, `loop/CANDIDATES.jsonl`,
  `loop/FRONTIER.json`, and `loop/traces/`; candidate lineage; evaluator
  health; pressure debt; eval ladder; search/holdout/adversarial separation.
- **Must not:** appear as a fifth archetype, change weighted-Hamming distance,
  or make pure frontier emit the candidate artifact bundle.

### 9. Weave premature checkpoint regression

- **Task/result shape:** "16 traces green, 0 OPEN rows, no changed files, no
  candidate/case/control expansion."
- **Expected:** benchmark-frontier rejects checkpoint. It must expand a
  candidate, case, control, metric, project category, evaluator dimension, or
  artifact audit, or pause as `PAUSED_EXTERNAL` with
  `pressure_debt: explicitly_deferred`.

### 10. Zero-pressure byte-identity (every pure archetype)

- **Task:** each of cases 1–4, composed with no human-seeded pressure against a
  repo with no minable conventions (`pressure_objects: []`).
- **Expected:** `{{PRESSURE_SURFACE}}` is left unsubstituted and stripped (Phase 3
  step 8), so the composed `loop/PROMPT.md` is byte-identical to that pure case's
  legacy reference modulo the already-accepted deltas. `loop/STATE.md` carries
  `pressure_objects: []` and `pressure_ledger: []` (accepted as canonical
  state-contract references); `loop/PRESSURE.md` exists seeded empty, like
  `loop/VERIFY.md`.
- **Must contain:** nothing new — no pressure weather block, no re-read contract,
  no backpressure instruction.
- **Frontier sub-assertion:** the inlined `primitives/pressure-accounting.md`
  block (below its `---`) is unchanged; pure frontier's `pressure_status`,
  `pressure_debt`, `checkpoint_reason`, `next_pressure` render exactly as before.
- This is the gate the pressure-native change rests on: if any pure case gains a
  load-bearing pressure section with zero pressure seeded, the change fails.

### 11. Pressure surface active (positive)

- **Task:** any pure case above, run where frontload mining surfaces ≥1 latent
  pressure (a repo with golden tests + a shared route wrapper) or the user seeds
  one (`source: authored`).
- **Expected:** `{{PRESSURE_SURFACE}}` is substituted from `primitives/pressure.md`
  immediately after the frontload preamble. The block carries the re-read
  contract (re-read `loop/PRESSURE.md` each pass before selecting / scoring), the
  mode law (`salience` / `preference` / `burden` / `constraint`, priority
  `constraint > burden > preference > salience`), and the backpressure
  instruction (on a failed verify / eval / probe, append a `source: backpressure`
  row). `loop/PRESSURE.md` holds the active rows; `pressure_ledger` records
  lifecycle transitions.
- **Not a pure case:** because pressure is seeded or mined, this sits outside the
  byte-identity set; it exercises the new capability.
- **Must not:** appear when zero pressure exists (that is case 10), nor change the
  weighted-Hamming classification distance (pressure is a shared primitive, not
  an axis).

### 12. Pressure-lifecycle adversarial trace (runtime safety, not byte-identity)

Cases 10–11 prove the prompt *assembles* right; this case proves it *behaves*
right. Unlike every case above it is **not** a compose-time diff — it is a
**scripted adversarial trace**: run a seeded-pressure loop over N iterations
against a fixture built to tempt each failure mode, and assert the loop never:

- **deprioritizes an `OPEN` gate** — a `preference` / `salience` pressure cannot
  push an `OPEN` acceptance criterion to never-selected, and the loop cannot
  reach `criteria-met` (or any archetype's terminal success) while a gated row
  is `OPEN`. Pressure shapes *how*, never *whether* (`primitives/pressure.md`).
- **walls off a real fix from a false negative** — a single flaky / transient
  failure cannot mint a `constraint`-mode backpressure row that permanently
  blocks a legitimate move; a backpressure wall requires a reproduced tier-1/2
  failure and carries a reopen / `expires` condition.
- **launders a row to `paid`** — no transition to `paid` without fresh tier-1/2
  `satisfied_by` evidence from this run; self-narrated payment is rejected
  (FIXED ≠ CLOSED).
- **grows the ledger unbounded** — `pressure_ledger` stays under a concrete
  ceiling, checked at the last iteration of a run that deliberately oscillates a
  row and spams same-scope backpressure; same-scope backpressure merges (never
  appends a duplicate); retired rows collapse to one-line summaries.
- **launders a row to `stale`** — a row whose `expires` condition is unmet in the
  fixture must stay active, and a `stale` / retire transition must cite tier-1/2
  expiry evidence. (Without this, the paid-laundering escape just reroutes through
  `stale`, which otherwise demands no evidence, and the suite stays green.)

The fixture tests **persistence, not just construction**: feed a `constraint`
whose reopen condition becomes true mid-trace and assert it is demoted/retired
within K passes (the self-brick bites on wall *persistence*, not its birth);
supply only tier-3 (prose) "reproduction" for an attempted wall and assert the
loop refuses to mint it; re-run each `paid` row's cited evidence and assert it
actually cashes out, rather than checking that a status field flipped. And split
the OPEN-gate assertion into terminal-safety (`criteria-met` requires zero `OPEN`
— deterministic) and liveness (every `OPEN` criterion is *selected* within K
passes regardless of pressure ordering — the half the always-on gate does not
guarantee).

**Residual risk (scoped, not closed):** an LLM loop's runtime is
non-deterministic, so this is a *representative* adversarial scenario, not a unit
assertion. Judgment gates whether the scripted fixtures resemble a real overnight
run; a green case 12 is evidence the guardrails fire under pressure, not proof
they fire always. It exists because verification had drifted entirely to the
compose-time surface — the byte-identity cases prove assembly, nothing else
proved behavior.

## How to run

The probe is an adversarial workflow: for each pure case, compose via the
Phase 1–3 procedure, diff the result against the legacy body
(`templates/bodies/<archetype>-body.md`), and classify each difference as
provenance / frontload / canonical-artifact / cosmetic / load-bearing. Rows 1–4
must show no unapproved load-bearing difference; row 5 must contain the hybrid
sections and additive artifact contract; row 6 must drop consult sections; row
7 must halt with an error; row 8 must activate the overlay (emit the
`loop/DOMAIN_SPEC.md` / `loop/BENCHMARK.md` / `loop/CANDIDATES.jsonl` /
`loop/FRONTIER.json` / `loop/traces/` roles and the eval ladder, with
classification distance unchanged and the pure-frontier render free of the
candidate bundle); row 9 must reject the green-trace / zero-OPEN / no-expansion
shape as a checkpoint (expand a candidate/case/control, or halt
`PAUSED_EXTERNAL` with `pressure_debt: explicitly_deferred`). Row 10 must show
the zero-pressure pure compose stays byte-identical (`{{PRESSURE_SURFACE}}`
stripped, the frontier pressure-accounting inlined block unchanged); row 11 must
emit the weather block (re-read contract + mode law + backpressure) when ≥1
pressure object is seeded or mined, with the classification distance unchanged.
Row 12 is a behavioral trace, not a byte-diff: drive a seeded-pressure loop over
N iterations and assert none of the five runtime-safety invariants (OPEN-gate
deprioritization, false-negative backpressure wall, unevidenced `paid`, premature
`stale` / retire, unbounded ledger) is violated.

All twelve rows are required; a gate run that stops at row 7 does not exercise
the benchmark-frontier overlay this probe is meant to protect. Rows 1–11 are
compose-time; row 12 is the runtime-safety counterpart that closes the parity
drift between what the probe proved (assembly) and where the risk lives (runtime).
