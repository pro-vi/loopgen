# Benchmark Frontier Artifacts

Benchmark-frontier artifacts are semantic roles first and filenames second. The
runner may use repo-native files, but the fields must be mechanically auditable.

## Roles

| Role | Default file | Required fields |
|---|---|---|
| `DOMAIN_SPEC` | `DOMAIN_SPEC.md` | fixed surface, mutable surface, eval unit, budget, leakage risks |
| `BENCHMARK` | `BENCHMARK.md` | search set, holdout set, expected-green controls, expected-red controls, metrics, timeouts |
| `CANDIDATES` | `CANDIDATES.jsonl` | candidate rows, lineage, hypothesis, status, trace paths |
| `FRONTIER` | `FRONTIER.json` | current best/Pareto members, evaluator health, pressure debt, checkpoint reason |
| `traces` | `traces/<candidate>/<case>/evaluation.json` | raw per-candidate/per-case evidence |

## Candidate Row

Required fields:

```yaml
candidate_id: string
parent_candidate_id: string | null
operator: draft | debug | improve | ablate | stress | falsify | transfer | compress
hypothesis: string
dimension: string
metric_vector: object
status: proposed | compliance_checked | smoke_checked | search_scored | frontier_member | rejected | holdout_confirmed | holdout_regressed | pressure_paid | pressure_deferred
artifacts:
  compliance_trace: path
  smoke_trace: path
  search_trace: path
  holdout_trace: path | null
  adversarial_trace: path | null
  meta_eval_trace: path | null
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

## FRONTIER Role

`FRONTIER` references only scored candidates. It compares by metric vector,
cost, and latency, not recency.

Minimum fields:

```yaml
members: [candidate_id]
pareto_dimensions: [dimension]
eval_health: calibrated | flaky | underpowered | contaminated | gamed | stale | judge_uncalibrated
pressure_debt: none | low | medium | high | explicitly_deferred
checkpoint_reason: string | null
next_pressure: string | null
```

When `eval_health != calibrated`, the loop may claim harness progress only.
Product progress waits for calibrated or explicitly bounded evaluator pressure.
