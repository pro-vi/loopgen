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
- paths to compliance, smoke, and search traces; holdout, adversarial, and
  meta-eval trace paths stay null until that pressure is applied

A row missing `hypothesis`, `operator`, or its compliance/smoke/search trace
paths cannot update the `FRONTIER` role.

A status may not outrun its evidence or its verdict. A trace pays for a status
only when it is non-null, parseable, linked to this candidate and rung, and
records a verdict compatible with the claim:

- `holdout_confirmed` requires a `holdout_trace` recording a passing holdout
  verdict; `holdout_regressed` requires one recording a failing/regressing verdict.
- `pressure_paid` requires a stronger-pressure trace whose payload supports the
  claim: a passing `holdout_trace`, an `adversarial_trace` recording the required
  expected-green/expected-red control verdicts, or a `meta_eval_trace` bounding
  evaluator risk. A non-null path alone does not pay pressure debt.

Deferred pressure is not a candidate status; it is a `FRONTIER`-level fact
(`pressure_status: blocked`, `pressure_debt: explicitly_deferred`, with a named
`blocker`, `next_pressure`, and `claim_scope: search_only`).

### Candidate lifecycle

```text
proposed
  -> compliance_checked
  -> smoke_checked
  -> search_scored
  -> frontier_member | rejected
  -> holdout_confirmed | holdout_regressed
  -> pressure_paid
```

Deferred pressure is **not** a candidate status. A search winner whose stronger
pressure is blocked stays at its earned status (e.g. `frontier_member`) with the
unpaid traces `null`; the deferral lives on the owning `FRONTIER` record
(`pressure_status: blocked`, `pressure_debt: explicitly_deferred`, `blocker`,
`next_pressure`, `claim_scope: search_only`). This keeps "I gave up" from
reading as "I advanced a rung."

### Promotion rule

Search improvement earns a local promotion claim, not belief. After a new search
win, pressure debt remains open until holdout, adversarial, expected-red, or
meta-eval pressure is applied, or until the runner explicitly defers it because
budget, scope, or authority blocks stronger pressure.

If evaluator health is anything other than calibrated, the loop may claim
harness progress, not product progress.

{{INCLUDE primitives/eval-ladder.md}}

### Green-trace rule

Green search traces, zero OPEN generic findings, and no changed files are not a
checkpoint. The loop must expand one of: candidate, case, control, metric,
project category, evaluator dimension, or artifact audit. If budget or external
authority blocks expansion, halt as `PAUSED_EXTERNAL` with
`pressure_debt: explicitly_deferred`, not as complete.
