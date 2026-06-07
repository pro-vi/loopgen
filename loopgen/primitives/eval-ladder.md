# eval-ladder (benchmark-frontier primitive)

## Purpose

Candidate promotion needs a stricter ladder than generic evaluator maturity.
T0-T6 answers "how mature is this repo's measurement?" The eval ladder answers
"may this candidate update the benchmark frontier?"

## Include when

Only inside the benchmark-frontier overlay.

---

## Ladder

1. **Compliance** — candidate satisfies format, API, scope, and forbidden
   shortcut rules.
2. **Smoke** — candidate runs on the cheapest representative path.
3. **Search** — candidate is scored on the search set used to choose work.
4. **Holdout** — candidate is checked against cases not used for search.
5. **Adversarial controls** — expected-green and expected-red controls verify
   the evaluator accepts good output and rejects bad output.
6. **Meta-eval** — when judge calibration is suspect, evaluate the evaluator
   before claiming product progress.

Missing or corrupt output at any rung counts as failure for that rung.

## Evaluator Health

`eval_health` values:

- `calibrated`
- `flaky`
- `underpowered`
- `contaminated`
- `gamed`
- `stale`
- `judge_uncalibrated`

If `eval_health != calibrated`, the loop may record harness progress but cannot
claim product progress.

## Pressure Debt

- Compliance or smoke failure keeps pressure open.
- Search improvement increases pressure debt until stronger pressure is applied.
- Holdout, adversarial controls, or meta-eval can reduce pressure debt when they
  strengthen the evidence behind the claim.
- Noisy, flaky, missing, or corrupt eval output preserves or increases debt.
- Budget, scope, or external authority may set
  `pressure_debt: explicitly_deferred`, but the final report must name the
  blocker and next pressure.

## Oracle-integrity rows (when the overlay seeds them)

When the loop mutates or trusts the evaluator, the `### Oracle-integrity pressure`
rows (`primitives/benchmark-frontier.md`) are the **staged view of this ladder**,
not a parallel checklist:

- Rung 5 (adversarial controls) pays `oracle.negative-executed` and
  `oracle.expected-red`: the executed expected-red counter-strategy and the per-run
  known-bad / known-good controls are the same evidence.
- Rung 6 (meta-eval) pays `oracle.judge-diversity`: evaluating the evaluator's
  independence is the meta-eval rung.
- `oracle.ground-truth`, `oracle.n-replicate`, `oracle.provenance`,
  `oracle.write-ahead`, and `oracle.receipts` gate entry to the ladder at all:
  until each is paid by an out-of-cone executed artifact, no rung verdict may lift
  `claim_scope` to `product_progress`.

While any oracle-integrity row is unpaid, no candidate reaches `pressure_paid`,
`claim_scope` may not be `product_progress`, and `eval_health` is treated as not
`calibrated` — the same three-part wall as `primitives/benchmark-frontier.md`, so
the ladder yields harness progress only.
