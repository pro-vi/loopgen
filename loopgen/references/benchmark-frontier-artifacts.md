# Benchmark Frontier Artifacts

Benchmark-frontier artifacts are semantic roles first and filenames second. The
runner may use repo-native files, but the fields must be mechanically auditable.

## Roles

| Role | Default file | Required fields |
|---|---|---|
| `DOMAIN_SPEC` | `loop/DOMAIN_SPEC.md` | fixed surface, mutable surface, eval unit, budget, leakage risks |
| `BENCHMARK` | `loop/BENCHMARK.md` | search set, holdout set, expected-green controls, expected-red controls, metrics, timeouts |
| `CANDIDATES` | `loop/CANDIDATES.jsonl` | candidate rows, lineage, hypothesis, status, trace paths |
| `FRONTIER` | `loop/FRONTIER.json` | current best/Pareto members, evaluator health, pressure debt, checkpoint reason |
| `traces` | `loop/traces/<candidate>/<case>/evaluation.json` | raw per-candidate/per-case evidence |

## Candidate Row

Required fields:

```yaml
candidate_id: string
parent_candidate_id: string | null
operator: draft | debug | improve | ablate | stress | falsify | transfer | compress
hypothesis: string
dimension: string
metric_vector: object
status: proposed | compliance_checked | smoke_checked | search_scored | frontier_member | rejected | holdout_confirmed | holdout_regressed | pressure_paid
artifacts:
  compliance_trace: path
  smoke_trace: path
  search_trace: path
  holdout_trace: path | null
  adversarial_trace: path | null
  meta_eval_trace: path | null
  oracle_check_trace: path | null      # oracle.ground-truth (P1): independent re-derivation of the key
  negative_control_trace: path | null  # oracle.negative-executed (P3): executed expected-red counter-strategy
  eval_health_trace: path | null       # oracle.expected-red (P5): per-run expected-red / expected-green controls
  receipt: path | null                 # oracle.receipts (P8): oracle/scorer/candidate/model/seed/tool-policy/run-id
```

Rules:

- `candidate_id` is unique. Duplicate hypotheses are allowed only with a
  distinct parent/operator pair.
- `parent_candidate_id` creates a branch; rejected and negative rows remain
  visible.
- Missing or corrupt trace output counts as failure.
- A candidate cannot update `FRONTIER` until compliance, smoke, and search
  evidence exist.
- A search win does not pay pressure debt until holdout, adversarial,
  expected-red, or meta-eval pressure is applied or explicitly deferred.
- A status may not outrun its evidence **or its verdict**: a trace pays for a
  status only when non-null, parseable, candidate/rung-linked, and recording a
  compatible verdict. `holdout_confirmed` needs a passing `holdout_trace`;
  `holdout_regressed` a failing/regressing one; `pressure_paid` a passing
  `holdout_trace`, an `adversarial_trace` recording expected-green/expected-red
  control verdicts, or a `meta_eval_trace` bounding evaluator risk. A non-null
  path alone pays nothing.
- Deferred pressure is **not** a candidate status; it is a `FRONTIER`-level fact
  (`pressure_status: blocked`, `pressure_debt: explicitly_deferred`, with a named
  `blocker`, `next_pressure`, and `claim_scope: search_only`).
- When the overlay trusts-or-mutates the evaluator, the `### Oracle-integrity
  pressure` rows (`primitives/benchmark-frontier.md`) are the **floor** of the trust
  chain: `claim_scope` stays `search_only` until every such row is paid by an
  out-of-cone executed artifact, below holdout / adversarial / meta-eval. The
  `oracle_check_trace` / `negative_control_trace` / `eval_health_trace` / `receipt`
  paths above are how those rows cash out; a non-null path alone pays nothing.

## FRONTIER Role

`FRONTIER` references only scored candidates. It compares by metric vector,
cost, and latency, not recency.

Minimum fields:

```yaml
members: [candidate_id]
pareto_dimensions: [dimension]
claim_scope: search_only | product_progress
eval_health: calibrated | flaky | underpowered | contaminated | gamed | stale | judge_uncalibrated
pressure_status: open | paid | blocked | exhausted
pressure_debt: none | low | medium | high | explicitly_deferred
checkpoint_reason: plateau_after_active_pressure | budget_exhausted | evaluator_invalid | risk_limit_hit | target_gap_unresolved | negative_result_saved | null
next_pressure: string | null   # the deferred rung's next step when blocked
deferred_pressure:             # present only when pressure_status: blocked
  deferred_rung: holdout | adversarial | meta_eval
  blocker: string
```

`claim_scope` is `search_only` until stronger pressure is paid; only then may it
become `product_progress`. A blocked candidate keeps its earned row `status` and
records its unpaid pressure here, in `deferred_pressure`, never as a row status.

When `eval_health != calibrated`, the loop may claim harness progress only.
Product progress waits for calibrated or explicitly bounded evaluator pressure.
When the overlay seeds oracle-integrity rows, an unpaid row holds `eval_health`
below `calibrated` by definition: `product_progress` is unreachable until the
evaluator's own integrity is paid by out-of-cone executed evidence.
