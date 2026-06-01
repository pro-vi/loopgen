# Evaluator Maturity

Two related artifacts for the same decision:

- **Tiers (T0–T6)** name the repository's *current measurement maturity*.
- **Ramp stages (0–9)** name the *artifacts to build* to climb tiers.

For benchmark-frontier candidate promotion, keep this generic maturity scale
separate from `eval-ladder.md`. T0-T6 names repo measurement maturity; the eval
ladder names whether a candidate may update the benchmark frontier.

Use tiers to assess; use ramp stages to plan the climb.

## Tiers

- `T0` install / build / run commands are unknown or unreliable
- `T1` static checks exist: lint, typecheck, compile
- `T2` cheap smoke path exists
- `T3` discriminative unit / integration signal exists
- `T4` representative hard-case, e2e, or search-set signal exists
- `T5` performance, latency, cost, or SLO metrics exist
- `T6` holdout / anti-overfitting checks exist

## Ramp stages

| # | Stage | Produces | Exit condition |
|---|---|---|---|
| 0 | Orientation | Repo map, motive ↔ code correspondence | Agent can describe what the repo does from evidence |
| 1 | Command discovery | Canonical build / test / run commands | All three return 0 on a known-good state |
| 2 | Baseline snapshot | Ledger entry: current green / red / flaky | Something to regress against exists |
| 3 | Smoke validator | `scripts/validate.sh` or equivalent | Runs in seconds; catches obvious breakage |
| 4 | Discriminative signal | Hard-case fixtures distinguishing working from compile-passing | False greens named or eliminated |
| 5 | Trace infrastructure | Structured failure artifacts | Any failure is queryable without re-running |
| 6 | Search set | Curated hard cases covering motive axes | Loop picks work from the set, not from vibes |
| 7 | Search/holdout split | Holdout cases not used for iteration choices | Overfitting is observable |
| 8 | Metric surfacing | Instrumented p50/p95/p99 / token cost / latency | Iterations produce numbers, not anecdote |
| 9 | Golden principles | `docs/golden_principles.md` — testable invariants | Principles are runnable assertions |

## Tier-to-stage cross-reference

| Tier | Stages implied |
|---|---|
| T0 | — (nothing built yet) |
| T1 | 1 (commands work; static checks run) |
| T2 | 1, 2, 3 (baseline + smoke) |
| T3 | 1, 2, 3, 4, 5 (discriminative signal + traces) |
| T4 | T3 + 6 (search set) |
| T5 | T4 + 8 (metric surfacing) |
| T6 | T5 + 7 (holdout) |

Stage 0 (orientation) and stage 9 (golden principles) are orthogonal —
useful at any tier but not required to climb.

## Ramp policy

If below T3, the loop is in **ramp mode**. Prioritize building missing
stages 1–5 before claiming product optimization. Specifically:

1. Discover canonical commands (stage 1).
2. Record baseline (stage 2).
3. Add a cheap smoke validator (stage 3).
4. Create or refine discriminative signal (stage 4).
5. Ensure failures produce traces (stage 5).

Stages 6–9 can be completed inside main-loop mode as `evaluator` or
`observability` work. They do not need to finish before ramp exits.

Ramp may take many iterations. A single stage may span a PR or a branch.
This is not failure; it is the runway the main loop needs.

## Ramp encoded in the motive

Sometimes the user's prompt already contains the ramp as its first
acceptance row ("build a minimal fixture and prove the lifecycle
end-to-end"). When this is the case:

- Recognize the row as ramp, not as an ordinary product slice.
- Do not insert an additional ramp preamble — the row is the preamble.
- Ramp exit aligns with that row's completion. Subsequent rows are
  main-loop, dependent on ramp-complete.

## Decision rule

- weak or ambiguous signal → intervention is `evaluator`
- trustworthy signal and known defect → intervention is `product`
- failures exist but are hard to diagnose → intervention is
  `observability`
- ambiguous instructions blocking measurement → intervention is
  `specification`

## Common failure modes

### Main-loop failure modes

- **Coverage-only loop** — static or unit coverage rises, real risk does
  not. Guard: stage 4 (discriminative signal).
- **Benchmark gaming** — search set improves, holdout silently rots.
  Guard: stage 7 (holdout split).
- **Harness vanity** — loop keeps improving tooling without cashing out
  into product. Guard: once stages 1–5 are done, shift toward product;
  intervention-diversity axis catches same-shape runs.

### Ramp-specific failure modes

- **Over-ramping** — elaborate harness when a smoke test would suffice.
  Guard: ramp stages have explicit exit conditions; do not open a later
  stage until the earlier one closes.
- **Ramp scope creep** — ramp never exits. Guard: ramp exit criterion is
  checkable (five conditions); once met, `ramp-complete` fires and the
  next iteration switches to main-loop.
- **Ramp bypass** — jumping to product work on whatever signal happens
  to exist. Guard: stage 4 exit condition must be met before product
  commits count as valid progress.
- **Ramp theater** — stage artifacts that look like infrastructure but
  do not sharpen signal (e.g. tests asserting tautologies). Guard:
  stage 4 exit requires named false-green elimination, not just the
  presence of additional tests.

Mode discipline: build only enough evaluator quality to keep the signal
honest, then return to product work.
