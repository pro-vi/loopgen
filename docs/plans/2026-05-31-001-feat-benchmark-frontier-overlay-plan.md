---
title: Benchmark Frontier Overlay
type: feat
status: completed
date: 2026-05-31
origin: braid research + GPT consult + loopgen inbox reply
---

## Architecture Decision

**Approach:** Split the correction into two tiers:

1. Add **pressure accounting** to generic frontier. This is lightweight and applies to every frontier loop: name the frontier dimension, evidence source, pressure status, pressure debt, next pressure, and checkpoint reason.
2. Add **benchmark-frontier** as an opt-in frontier overlay. It activates only when frontload binds a benchmark/eval/harness object. The overlay adds candidate artifacts, eval ladder, search/holdout split, evaluator health, and candidate tree/population semantics.

Do not add a fifth archetype. Do not add a new weighted classification axis. `benchmark-frontier` behaves like `consult-capability`: detected during frontload, recorded in provenance, ignored by weighted-Hamming distance, and used by composition.

**Rationale:** The external pattern from Karpathy `autoresearch`, Stanford `meta-harness`, Harness Bench, OpenAI `mle-bench`, and GPT review is clear: frontier loops need pressure accounting; benchmark-shaped frontier loops need a candidate economy. The general principle should not make every frontier prompt heavy. Generic frontier gets the principle; benchmark-frontier gets the ceremony.

**Trade-offs:** This adds one universal primitive and one overlay primitive. The extra vocabulary is justified because it prevents two distinct failures: generic frontier stopping on passive homeostasis, and benchmark frontier stopping because current traces are green. The cost is more composition logic and a stricter prompt contract.

## Requirements

- **R1:** Generic frontier remains lightweight but cannot checkpoint without explicit pressure accounting.
- **R2:** Benchmark-frontier emits candidate artifacts only when frontload binds a benchmark/eval/harness object.
- **R3:** Benchmark artifacts are defined by semantic roles first, filenames second. JSON/JSONL are defaults; repo-native markdown is acceptable only if mechanically auditable.
- **R4:** Candidate evaluation uses an eval ladder: compliance, smoke, search, holdout, adversarial controls, and meta-eval when needed.
- **R5:** Candidate search is tree-capable: every candidate may name a parent and an operator (`draft`, `debug`, `improve`, `ablate`, `stress`, `falsify`, `transfer`, `compress`).
- **R6:** Evaluator health is explicit. If evaluator health is not calibrated, the loop may claim harness progress, not product progress.
- **R7:** Pure archetype compatibility remains intact.
- **R8:** The re-derived Weave quality prompt rejects the old premature checkpoint shape: green traces, no OPEN rows, no candidate expansion.

## High-Level Technical Design

Directional guidance for review, not implementation specification.

### Generic frontier flow

```text
frontier intent
  -> frontload binds dimension + evidence + scope + stop rule
  -> run or re-evaluate evidence
  -> record delta against frontier vector
  -> assign pressure debt
  -> choose next pressure or intervention
  -> checkpoint only with checkpoint_reason and pressure status
```

Generic frontier does not need `CANDIDATES.jsonl`. Its pressure object can live in the existing findings ledger or `STATE.md`.

### Benchmark-frontier flow

```text
frontier intent + benchmark/eval/harness object
  -> frontload emits overlay: benchmark-frontier
  -> DOMAIN_SPEC role defines fixed surface, mutable surface, eval unit, budget
  -> BENCHMARK role defines search set, holdout, controls, metrics, timeouts
  -> CANDIDATES role records candidate tree/population rows
  -> FRONTIER role records current best/Pareto members and pressure debt
  -> traces role stores per-candidate/per-case evidence
  -> checkpoint only after pressure debt is paid or explicitly deferred
```

### Candidate lifecycle

```text
proposed
  -> compliance_checked
  -> smoke_checked
  -> search_scored
  -> frontier_member | rejected
  -> holdout_confirmed | holdout_regressed
  -> pressure_paid | pressure_deferred
```

### Universal pressure fields

```yaml
pressure_status: open | paid | blocked | exhausted
pressure_debt: none | low | medium | high | explicitly_deferred
checkpoint_reason:
  plateau_after_active_pressure
  budget_exhausted
  holdout_confirmed
  evaluator_invalid
  risk_limit_hit
  target_gap_unresolved
  negative_result_saved
next_pressure: <trace/case/control/project/dimension/operator to try next>
```

### Benchmark artifact roles

Default filenames are recommended, not the actual invariant:

| Role | Default file | Contract |
|---|---|---|
| `DOMAIN_SPEC` | `DOMAIN_SPEC.md` | fixed surface, mutable surface, eval unit, budget, leakage risks |
| `BENCHMARK` | `BENCHMARK.md` | search set, holdout set, expected-green/red controls, metrics, timeouts |
| `CANDIDATES` | `CANDIDATES.jsonl` | candidate rows with parent, operator, hypothesis, status, eval artifacts |
| `FRONTIER` | `FRONTIER.json` | best/Pareto members, evaluator health, pressure debt, checkpoint reason |
| `traces` | `traces/<candidate>/<case>/evaluation.json` | raw evidence; missing/corrupt counts as failure |

Markdown equivalents are acceptable only when they preserve the same fields and can be audited without interpretation.

## Composition Matrix

Old scalar assumptions:

- Frontier "balance" could be treated as the stop signal.
- A findings ledger could stand in for all frontier state.
- A green validator or green trace set could be mistaken for exhausted search.
- "The evaluator" could be rendered as a single thing, even when search, holdout, controls, and judge calibration differ.

New composed model:

- Generic frontier has a pressure object: dimension, evidence, pressure debt, next pressure, checkpoint reason.
- Benchmark-frontier adds candidate artifacts and eval ladder.
- Eval result is a composed surface: compliance, smoke, search, holdout, expected-red controls, evaluator health, and pressure debt.

Consumer surfaces:

- `loop/PROMPT.md` explains the rules.
- `loop/STATE.md` records pressure state and overlay provenance.
- Findings ledger records generic frontier pressure when no benchmark overlay exists.
- Benchmark artifact roles record candidate and frontier state when overlay exists.
- README explains the public shape without introducing a fifth archetype.

Priority lattice:

1. Derivation gaps block launch.
2. Broken compliance/smoke rejects candidate before search score matters.
3. Evaluator health not calibrated downgrades product claims to harness progress.
4. Holdout/adversarial regression blocks promotion even if search score improves.
5. Pressure debt blocks checkpoint unless paid or explicitly deferred by budget/scope/authority.

Ownership boundary:

- Phase 1 frontload detects overlay and binds pressure inputs.
- Phase 3 composition emits the correct prompt/artifact contract.
- The runner maintains the artifacts during execution.
- Loopgen does not implement a runtime benchmark runner.

| Mixed case | Expected visible contract | Typed decision/source | Test |
|---|---|---|---|
| Pure generic frontier, no benchmark object | Existing frontier prompt plus lightweight pressure accounting | `overlay: none`, pressure fields present | `pure_frontier_stays_lightweight` |
| Benchmark object bound | Benchmark artifact roles emitted | `overlay: benchmark-frontier` | `benchmark_frontier_emits_roles` |
| Search improves, holdout regresses | Candidate not promoted; pressure remains open | holdout has priority over search | `holdout_blocks_search_win` |
| Evaluator health underpowered | Harness/evaluator work allowed; product progress not claimed | `eval_health: underpowered` | `uncalibrated_eval_blocks_product_claim` |
| No OPEN findings, green traces | Candidate/case/control expansion required before checkpoint | pressure debt or next pressure required | `green_traces_do_not_checkpoint_without_pressure_scan` |

## Implementation Units

### U1. Universal Pressure Accounting

- **Goal:** Add lightweight pressure accounting to generic frontier without turning every frontier loop into benchmark-frontier.
- **Requirements:** R1, R7
- **Dependencies:** None
- **Files:**
  - Create: `loopgen/primitives/pressure-accounting.md`
  - Modify: `loopgen/templates/bodies/frontier-body.md`
  - Modify: `loopgen/primitives/halt-cause-classifier.md`
  - Modify: `loopgen/SKILL.md`
- **Approach:** Define `pressure_status`, `pressure_debt`, `checkpoint_reason`, and `next_pressure` as generic frontier fields. Use them in homeostasis-before-halt. Keep storage flexible: existing findings ledger or `STATE.md`.
- **Patterns to follow:** `loopgen/templates/bodies/frontier-body.md` homeostasis-before-halt and status taxonomy; `loopgen/primitives/halt-cause-classifier.md` non-terminal halt semantics.
- **Test scenarios:**
  - *Happy path:* generic frontier with a named dimension records next pressure and can checkpoint after active pressure is exhausted.
  - *Edge case:* no OPEN findings and no changed files triggers pressure discovery, not completion.
  - *Error path:* checkpoint without `checkpoint_reason` and pressure scan is invalid.
  - *Integration:* pure frontier remains lighter than benchmark-frontier and emits no candidate artifact roles.
- **Verification:** Generic frontier cannot say `frontier_complete`; it can only checkpoint with pressure status and reason.

### U2. Benchmark-Frontier Overlay Contract

- **Goal:** Add benchmark-frontier as a frontload-detected overlay, not a fifth archetype and not a classification axis.
- **Requirements:** R2, R7
- **Dependencies:** U1
- **Files:**
  - Create: `loopgen/primitives/benchmark-frontier.md`
  - Modify: `loopgen/SKILL.md`
  - Modify: `loopgen/archetypes/frontier.md`
  - Modify: `loopgen/primitives/frontload-audit.md`
- **Approach:** Detect benchmark/eval/harness object during frontload. Emit `overlay: benchmark-frontier` in provenance only when a benchmark object is bound. Weighted-Hamming still sees ordinary `frontier`.
- **Patterns to follow:** `consult-capability` overlay in `loopgen/SKILL.md`; loopgen inbox reply constraint that benchmark-frontier is artifact discipline, not target-shape.
- **Test scenarios:**
  - *Happy path:* "push this benchmark overnight" classifies as `frontier` with `overlay: benchmark-frontier`.
  - *Edge case:* "improve this repo" remains generic frontier unless frontload binds a benchmark/eval/harness object.
  - *Error path:* benchmark/eval language without benchmark object yields derivation gap, not silent generic frontier.
  - *Integration:* pure frontier weighted-Hamming distance and archetype choice remain unchanged.
- **Verification:** Overlay appears in provenance, but not in `dev/classify.py` distance output unless optional metadata is shown outside the distance table.

### U3. Benchmark Artifact Roles And Candidate Topology

- **Goal:** Define the semantic artifact roles and candidate tree/population row contract.
- **Requirements:** R3, R5
- **Dependencies:** U2
- **Files:**
  - Create: `loopgen/references/benchmark-frontier-artifacts.md`
  - Modify: `loopgen/primitives/artifact-shape.md`
  - Modify: `loopgen/primitives/queue-as-second-artifact.md`
  - Modify: `loopgen/SKILL.md`
- **Approach:** Define roles first: `DOMAIN_SPEC`, `BENCHMARK`, `CANDIDATES`, `FRONTIER`, `traces`. Defaults are `DOMAIN_SPEC.md`, `BENCHMARK.md`, `CANDIDATES.jsonl`, `FRONTIER.json`, and `traces/...`, but any repo-native encoding must preserve the same fields. Candidate rows include `candidate_id`, `parent_candidate_id`, `operator`, `hypothesis`, `dimension`, `metric_vector`, `status`, and artifact paths.
- **Patterns to follow:** queue row contract in `loopgen/primitives/queue-as-second-artifact.md`; Phase 4 extra artifact emission in `loopgen/SKILL.md`.
- **Test scenarios:**
  - *Happy path:* benchmark-frontier prompt names all artifact roles and default filenames.
  - *Edge case:* markdown `CANDIDATES` is accepted only if row fields are explicit and auditable.
  - *Error path:* candidate missing `hypothesis`, `operator`, or trace path cannot update `FRONTIER`.
  - *Integration:* candidate with `parent_candidate_id` forms a branch without erasing prior failed/negative candidates.
- **Verification:** Benchmark-frontier has an optimization object; generic frontier does not inherit these files.

### U4. Eval Ladder, Evaluator Health, And Pressure Debt

- **Goal:** Add benchmark-specific evaluation discipline while keeping `evaluator-maturity.md` T0-T6 generic.
- **Requirements:** R4, R6
- **Dependencies:** U2, U3
- **Files:**
  - Create: `loopgen/primitives/eval-ladder.md`
  - Modify: `loopgen/primitives/evaluator-maturity.md`
  - Modify: `loopgen/primitives/benchmark-frontier.md`
- **Approach:** Keep T0-T6 as repo measurement maturity. Add a separate ladder for candidate promotion: compliance, smoke, search, holdout, adversarial, meta-eval. Define `eval_health` values: `calibrated`, `flaky`, `underpowered`, `contaminated`, `gamed`, `stale`, `judge_uncalibrated`. Define how pressure debt increases/decreases.
- **Patterns to follow:** `loopgen/primitives/evaluator-maturity.md` ramp stage separation; GPT critique that local improvement earns promotion, not belief.
- **Test scenarios:**
  - *Happy path:* candidate passes compliance, smoke, search, holdout, and expected-red controls before promotion.
  - *Edge case:* noisy eval marks result inconclusive and preserves pressure debt.
  - *Error path:* missing/corrupt evaluation counts as failure.
  - *Integration:* if `eval_health != calibrated`, the loop records harness progress and cannot claim product progress.
- **Verification:** Candidate score improvements do not reduce pressure debt unless stronger pressure was applied.

### U5. Frontier Prompt Composition

- **Goal:** Compose generic pressure accounting and benchmark-frontier overlay into the frontier body without making generic frontier too heavy.
- **Requirements:** R1, R2, R8
- **Dependencies:** U1, U2, U3, U4
- **Files:**
  - Modify: `loopgen/templates/bodies/frontier-body.md`
  - Modify: `loopgen/templates/composed-prompt.md`
- **Approach:** Generic frontier always gets pressure accounting. Benchmark-frontier conditionally inserts "Benchmark Frontier Mode" with candidate lifecycle, artifact roles, eval ladder, evaluator health, and pressure-debt rules. Homeostasis selects and repairs around the candidate loop; it does not substitute for candidate generation.
- **Patterns to follow:** current primary action spine in `loopgen/templates/bodies/frontier-body.md`; `templates/composed-prompt.md` conditional/degrade logic.
- **Test scenarios:**
  - *Happy path:* generic frontier prompt requires pressure scan but emits no `CANDIDATES` role.
  - *Happy path:* benchmark-frontier prompt emits candidate loop and artifact roles.
  - *Edge case:* all search cases green but holdout absent creates evaluator-axis work before checkpoint.
  - *Error path:* old Weave R18 shape cannot checkpoint until candidate/case/control expansion is attempted or paused with budget/external reason.
- **Verification:** Frontier is not too heavy by default; benchmark-frontier is not too passive when activated.

### U6. Deterministic Contract Checks

- **Goal:** Add lightweight verification for the docs-as-runtime contract.
- **Requirements:** R7, R8
- **Dependencies:** U1, U2, U3, U4, U5
- **Files:**
  - Modify: `dev/classify.py`
  - Create: `dev/verify_loopgen_contracts.py`
  - Modify: `loopgen/references/backward-compat-tests.md`
- **Approach:** `classify.py` may accept optional overlay metadata, but distance ignores it. Because `dev/` may be local/ignored, either keep the verifier explicitly local or promote it into a tracked tools path before calling it a shipped gate. Add contract checks for banned stale closure language, required pressure fields, and benchmark-frontier artifact roles.
- **Patterns to follow:** `dev/classify.py` self-test style; `loopgen/references/backward-compat-tests.md` pure-archetype compatibility probe.
- **Test scenarios:**
  - *Happy path:* pure archetype cases remain structurally equivalent except provenance/accepted pressure additions for frontier.
  - *Edge case:* benchmark-frontier case can use repo-native artifact names if roles/fields are present.
  - *Error path:* stale `frontier_complete`, generic `DEFERRED`, or checkpoint without `checkpoint_reason` fails verifier.
  - *Integration:* old Weave R18 checkpoint shape fails the benchmark-frontier contract.
- **Verification:** Compatibility and new pressure semantics are both checkable without a runtime.

### U7. Docs And Weave Dogfood

- **Goal:** Explain the two-tier model and prove it on the motivating Weave loop.
- **Requirements:** R8
- **Dependencies:** U1, U2, U3, U4, U5, U6
- **Files:**
  - Modify: `README.md`
  - Create: `loopgen/references/benchmark-frontier-example.md`
- **Approach:** README says public story remains four archetypes. Generic frontier has pressure accounting. Benchmark-frontier is "frontier with candidate artifacts." The example re-derives the Weave quality loop with braid-self, empty-greenfield, sibling repo, holdout repo, and prompt/runtime/code candidate axes.
- **Patterns to follow:** README archetype explanation; loopgen inbox reply requirement that U7 close the design.
- **Test scenarios:**
  - *Happy path:* Weave benchmark-frontier prompt creates candidate/case expansion after green traces.
  - *Edge case:* expected-red controls remain intentionally red and do not block all progress.
  - *Error path:* if live agent budget is missing, the loop pauses as `PAUSED_EXTERNAL` with pressure debt explicitly deferred, not checkpointed as complete.
  - *Integration:* dogfood example demonstrates why generic frontier pressure accounting alone would be insufficient for Weave quality.
- **Verification:** The design is not promoted until the Weave prompt rejects "16 traces green, 0 OPEN, no reopen trigger, checkpoint" as a complete result.

## State-Action Contract Matrix

### Generic Pressure Axis

| Action | Caller observation | Durable state change | Side effects | Race / duplicate behavior | Named test |
|---|---|---|---|---|---|
| Bind frontier dimension | Prompt is runnable only after dimension/evidence/scope/stop rule exist | `STATE.md` or frontload preamble records bound slots | None | Re-derivation replaces stale frontload values only when user changes intent | `frontier_requires_bound_pressure_slots` |
| Record pressure | Halt scan names pressure status and next pressure | Findings ledger or `STATE.md` records `pressure_status`, `pressure_debt`, `next_pressure` | None | Duplicate scans append evidence rather than erase prior pressure | `pressure_scan_survives_no_open_findings` |
| Pay pressure debt | Checkpoint becomes allowed only if reason is present | `pressure_debt` becomes `none` or `explicitly_deferred` | Final halt report includes reason | Concurrent runner resumes treat absent reason as open pressure | `checkpoint_requires_pressure_reason` |

Generic invariants:

- `checkpoint_reason != null iff pressure_status in {paid, exhausted, blocked}`
- `pressure_debt = none iff no unresolved improvement claim needs stronger pressure`
- `pressure_debt = explicitly_deferred iff final report names budget/scope/authority reason`

### Benchmark Candidate Axis

| Action | Caller observation | Durable state change | Side effects | Race / duplicate behavior | Named test |
|---|---|---|---|---|---|
| Propose candidate | Candidate row is visible as `proposed` | Append row to `CANDIDATES` role with unique `candidate_id` | None beyond trace/log note | Duplicate `candidate_id` rejected; duplicate hypothesis allowed only with distinct parent/operator | `benchmark_frontier_rejects_duplicate_candidate_id` |
| Compliance check | Row becomes `compliance_checked` or `rejected` | Candidate row records check output path | Trace file written | Re-running compliance updates same candidate/check artifact, not frontier | `candidate_cannot_skip_compliance` |
| Smoke check | Row becomes `smoke_checked` or `rejected` | Smoke trace path recorded | Failing output retained | Re-running smoke replaces same candidate/case smoke result | `candidate_cannot_skip_smoke` |
| Search eval | Search score recorded | Trace role and candidate score fields written | Benchmark metrics emitted | Missing/corrupt evaluation counts as failure | `corrupt_eval_counts_as_failure` |
| Update frontier | `FRONTIER` role shows best/Pareto member | Frontier references scored candidate only | None | Compare by score/cost/latency, not recency | `frontier_references_only_scored_candidates` |
| Holdout/adversarial pressure | Candidate becomes `holdout_confirmed`, `holdout_regressed`, or pressure remains open | Holdout/adversarial trace recorded | None | Holdout never writes search-set scores | `holdout_is_disjoint_from_search` |
| Checkpoint | Runner emits checkpoint/paused report | `FRONTIER` and `STATE.md` record pressure debt/reason | Final scan printed | Blocked candidates remain visible | `benchmark_frontier_checkpoint_requires_pressure_debt_resolution` |

Benchmark invariants:

- `candidate.status in {frontier_member, holdout_confirmed, holdout_regressed} iff candidate.search_score != null`
- `candidate.holdout_result != null iff candidate.search_score != null`
- `frontier.members[] subset CANDIDATES where search_score != null`
- `search_set intersect holdout_set == empty`
- `pressure_debt != none` after a new search win until holdout/adversarial/meta-eval pressure is applied or explicitly deferred`

Transition timing: all artifact writes are synchronous at prompt-contract level. Long evaluations are allowed only if the runner records an in-progress trace path before launch and treats missing/corrupt output as failure on resume.

Omitted-state challenge:

- **Human manually edits benchmark artifacts:** out of scope for runtime enforcement, but contract checks should treat missing required fields as invalid on next iteration.
- **Multiple independent runners use the same artifacts:** out of scope for this prompt-only plan. Race behavior is best-effort append/update discipline, not file locking.

STPA pass:

- Not-provided: no pressure scan -> checkpoint invalid.
- Provided-when-unsafe: candidate promoted while evaluator health uncalibrated -> blocked by eval-health priority.
- Wrong timing: holdout run before search score -> invalid; holdout confirms belief, not discovery.
- Applied too long: pressure debt never payable -> halt as `PAUSED_EXTERNAL` or `budget_exhausted`, not endless loop.
- Stopped too soon: green search traces with open pressure debt -> checkpoint invalid.

## Scope Boundaries

- Loopgen remains a skill/doc generator, not a runtime engine.
- No fifth archetype.
- No new weighted classification axis.
- No requirement that every frontier loop emit benchmark artifacts.
- No changes to braid's Weave code in this plan.
- No real benchmark runner implementation inside loopgen.

### Deferred to Follow-Up Work

- A full prompt assembler/test harness for loopgen output. U6 is lightweight contract checking.
- UI rendering for candidate/frontier artifacts.
- Importing `meta-harness` scripts. This plan borrows the contract, not the code.
- Multi-runner file locking for benchmark artifacts.

## System-Wide Impact

- **Interaction graph:** Phase 1 frontload gains overlay detection and pressure-slot binding; Phase 3 composition gains universal pressure sections plus conditional benchmark-frontier sections; Phase 4 emitted artifact set grows only for benchmark-frontier loops.
- **Error propagation:** derivation gaps remain prompt-time; generic frontier pressure gaps block launch/checkpoint; benchmark candidate failures become artifact rows; budget/external blockers become `PAUSED_EXTERNAL`.
- **State lifecycle risks:** stale candidate/frontier mismatch is handled by invariant checks; generic frontier avoids artifact bloat by keeping pressure in existing state/ledger surfaces.
- **API surface parity:** no CLI/API changes. This is a skill contract and docs change.
- **Integration coverage:** pure archetype compatibility, generic frontier pressure behavior, benchmark-frontier artifact behavior, and Weave dogfood are all required.
- **Unchanged invariants:** four archetypes, weighted-Hamming classification, pointer-only kickoff, consult-capability overlay model, and runner-agnostic markdown prompt contract.

## Risks & Dependencies

| Risk | Mitigation |
|---|---|
| Generic frontier becomes too heavy | U1 uses lightweight pressure fields; benchmark artifacts are conditional on overlay |
| Overlay becomes a stealth fifth archetype | U2 keeps overlay out of distance/classification and records it like consult-capability |
| Benchmark artifact roles become filename cargo cult | U3 defines roles first and filenames second |
| Candidate loop games search metrics | U4 search/holdout/adversarial/meta-eval ladder and expected-red controls |
| Evaluator health turns into vague prose | U4 enumerates states and blocks product claims when not calibrated |
| Pressure debt causes endless loops | Debt may be explicitly deferred by budget/scope/authority with reason |
| Pure frontier compatibility breaks | U6 contract checks and backward-compat reference update |
| Weave loop still stalls at green validators | U7 dogfood requires old R18 shape to fail the new prompt contract |

## Disconfirming Evidence

- If generic frontier now emits full candidate artifacts by default, U1/U5 made frontier too heavy.
- If benchmark-frontier can halt after green search traces with no candidate/case/control expansion and no explicit pressure-debt deferral, U4/U5 failed.
- If pure frontier weighted-Hamming classification changes, U2 failed.
- If candidate scores improve while holdout/adversarial controls silently regress, U4 failed.
- If Weave dogfood still needs the user to say "try another project," U7 failed.

## Bug-Trace / Confidence Cross-Check

| Prior failure / requirement | Contract clause | Expected behavior | Match? |
|---|---|---|---|
| Loop stopped after R18 green traces | U4/U7 pressure-debt + dogfood | Start candidate/case/control expansion or pause with explicit debt deferral | Yes |
| Generic frontier becoming too heavy | U1/U5 tier split | Generic frontier gets pressure fields only, no candidate artifact bundle | Yes |
| No reasoning about new projects | U3/U7 benchmark roles | `BENCHMARK` role defines search/holdout/project categories | Yes |
| `frontier_complete` misuse | U1/U6 checkpoint semantics | Checkpoint only; no completion claim | Yes |
| Benchmark gaming risk | U4 eval ladder | Search improvement is not holdout/adversarial confirmation | Yes |
| Findings-only loop without optimization object | U2/U3 overlay | Benchmark-frontier has candidates and frontier table | Yes |
| Loopgen inbox constraint: roles first, filenames second | U3 artifact roles | Defaults are names, roles are invariant | Yes |
| GPT critique: local improvement earns promotion, not belief | U4 pressure debt | Search win increases debt until stronger pressure pays it | Yes |

Confidence check:

- [x] Decision rationale explicit: principles generalize, ceremony is conditional.
- [x] Data flow traced end-to-end: frontload -> classification -> pressure -> overlay -> candidate/eval -> checkpoint.
- [x] Integration scenarios named: pure frontier, benchmark-frontier, and Weave dogfood.
- [x] Unchanged invariants stated: four archetypes and weighted-Hamming remain.
- [x] Failure modes enumerated for pressure, candidate, eval, and halt boundaries.
- [x] Files-to-touch list grounded in current loopgen files and inbox feedback.
- [x] Disconfirming evidence is wired to contract checks and dogfood behavior.
