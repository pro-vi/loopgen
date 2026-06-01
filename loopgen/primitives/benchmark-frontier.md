# benchmark-frontier (frontier overlay)

## Purpose

Benchmark-frontier is a frontier overlay for optimization work with a concrete
benchmark, eval, or harness object. It adds artifact discipline for search,
promotion, and checkpointing. It is not a fifth archetype and not a weighted
classification axis.

## Activation

Activate only when frontload binds all three:

- a benchmark/eval/harness object with a concrete path, command, or artifact;
- an evaluation unit such as case, repo, prompt, fixture, trace, or scenario;
- an evidence location where results are durable enough to audit.

If the user says "benchmark" or "eval" but no object can be bound, emit a
derivation gap. Do not silently fall back to generic frontier and do not invent
artifact paths.

Record the overlay in provenance:

```yaml
archetype: frontier
overlays:
  - benchmark-frontier
classification_distance: unchanged
```

## Benchmark Frontier Mode

When active, insert this section into the frontier prompt.

### Artifact roles

Roles are invariant; filenames are defaults.

| Role | Default file | Contract |
|---|---|---|
| `DOMAIN_SPEC` | `DOMAIN_SPEC.md` | fixed surface, mutable surface, eval unit, budget, leakage risks |
| `BENCHMARK` | `BENCHMARK.md` | search set, holdout set, expected-green/red controls, metrics, timeouts |
| `CANDIDATES` | `CANDIDATES.jsonl` | rows with candidate lineage, operator, hypothesis, status, eval artifacts |
| `FRONTIER` | `FRONTIER.json` | best/Pareto members, evaluator health, pressure debt, checkpoint reason |
| `traces` | `traces/<candidate>/<case>/evaluation.json` | raw evidence; missing or corrupt output counts as failure |

Repo-native markdown is acceptable only when it preserves the same fields and
can be audited mechanically.

### Candidate row contract

Each row records:

- `candidate_id`
- `parent_candidate_id` or `null`
- `operator`: `draft | debug | improve | ablate | stress | falsify | transfer | compress`
- `hypothesis`
- `dimension`
- `metric_vector`
- `status`
- paths to compliance, smoke, search, holdout, adversarial, and meta-eval traces

A row missing `hypothesis`, `operator`, or a trace path cannot update the
`FRONTIER` role.

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

### Promotion rule

Search improvement earns a local promotion claim, not belief. After a new search
win, pressure debt remains open until holdout, adversarial, expected-red, or
meta-eval pressure is applied, or until the runner explicitly defers it because
budget, scope, or authority blocks stronger pressure.

If evaluator health is anything other than calibrated, the loop may claim
harness progress, not product progress.

Use `primitives/eval-ladder.md` for the candidate promotion ladder:
compliance, smoke, search, holdout, adversarial controls, and meta-eval.

### Green-trace rule

Green search traces, zero OPEN generic findings, and no changed files are not a
checkpoint. The loop must expand one of: candidate, case, control, metric,
project category, evaluator dimension, or artifact audit. If budget or external
authority blocks expansion, halt as `PAUSED_EXTERNAL` with
`pressure_debt: explicitly_deferred`, not as complete.
