# Benchmark-Frontier Example: Weave Quality Loop

This is the dogfood case that earns the benchmark-frontier overlay.

## Task

Push the Weave quality loop until it stops confusing green traces with a
finished frontier. The benchmark object is the Weave quality harness and its
trace set. The eval unit is a project/case run. The durable evidence is the
trace output plus candidate/frontier artifacts.

## Classification

```yaml
archetype: frontier
divergences: none
overlays:
  - benchmark-frontier
weighted_hamming_distance: unchanged
```

This remains the `frontier` archetype. The overlay activates because frontload
binds a benchmark/eval/harness object. A pure "improve this repo" frontier
prompt would get pressure accounting only.

## Bound Roles

| Role | Weave binding |
|---|---|
| `DOMAIN_SPEC` | prompt/runtime/code quality surface for Weave |
| `BENCHMARK` | braid-self, empty-greenfield, sibling repo, and held-back repo cases |
| `CANDIDATES` | prompt, runtime, code, and evaluator candidates with lineage |
| `FRONTIER` | current best/Pareto candidate set plus pressure debt |
| `traces` | per-candidate/per-case quality traces |

Candidate axes:

- prompt candidate: changes to extraction, intention-boundary, or review prompt
- runtime candidate: changes to loop scheduling, state update, or trace capture
- code candidate: changes to parser, fixture, or benchmark harness
- evaluator candidate: changes that make expected-red or held-back failures
  visible

## Rejected Old Checkpoint Shape

Old result:

```yaml
green_traces: 16
open_findings: 0
changed_files: 0
candidate_expansion: none
case_expansion: none
control_expansion: none
pressure_debt: unrecorded
```

Benchmark-frontier rejects this as a checkpoint. Green search traces and zero
OPEN generic rows do not pay pressure debt. The next move must expand one of:
candidate, case, control, metric, project category, evaluator dimension, or
artifact audit.

If live-agent budget or external authority blocks that expansion, the loop must
halt as:

```yaml
status: PAUSED_EXTERNAL
pressure_status: blocked
pressure_debt: explicitly_deferred
checkpoint_reason: budget_exhausted
next_pressure: add a held-back repo case or expected-red evaluator control
```

It must not report the frontier as complete.

## Why Generic Pressure Is Not Enough

Generic frontier pressure accounting catches the first bug: "no OPEN findings"
is not enough to checkpoint. Weave needs the heavier overlay because the next
useful pressure is not just another finding. It is candidate economy: propose
an alternate prompt/runtime/code candidate, run it on search cases, preserve the
negative rows, then apply held-back/adversarial pressure before promoting it.
