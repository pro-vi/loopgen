# frontier (archetype)

## Loop shape

Homeostatic frontier-seeking. Each iteration senses the repository's state
across five axes (oracle trustworthiness, product capability, failure
legibility, specification coherence, intervention diversity), diagnoses the
most-disturbed axis, and applies the intervention that most restores balance —
then iterates. The loop alternates between improving the product and improving
the mechanism that judges it: if measurement is weak, improve measurement
first; if measurement is trustworthy, improve the product. The work-type label
(`product` / `evaluator` / `observability` / `specification`) describes the
intervention; it is never picked from a menu.

## Default primitive values

| Axis | Default |
|---|---|
| `target-shape` | `frontier-expanding` |
| `halt-shape` | `equilibrium` |
| `artifact-shape` | `findings-ledger` |
| `convergence-shape` | `homeostatic-checkpoint` |
| `cadence-shape` | `checkpoint-gated` |
| `consult-capability` | detect (`tier-0` default) |

## Forbidden divergences

- `target-shape: finite-criteria` — a fixed finite checklist is goal-shaped;
  route to `goal`.
- Emitting consult sections at `consult-capability: tier-0` — degrade instead.

## Failure modes

- **Goodharting** — the primary metric rises while real capability rots.
  Mitigation: Pareto-frontier metrics, a discriminative search set, and a T6
  anti-overfitting check.
- **Oracle fetishism** — the loop keeps improving tooling without cashing out
  into product. Mitigation: cash-out discipline + the intervention-diversity
  axis catches same-shape runs.
- **Status theater** — summaries / plans in place of committed work. Mitigation:
  the status-theater prohibition; traces are truth, notes are memory.
- **Self-authored closure** — the iteration marks its own change closed and the
  halt fires prematurely. Mitigation: FIXED ≠ CLOSED + external confirmation.
- **Scope drift** — the loop improves adjacent surfaces. Mitigation: a
  scope-manifest halt when a manifest is provided.
- **Mode lock** — the same work shape repeats when another channel is the better
  move. Mitigation: the same-family admissibility rule (cosmetic / rustfmt /
  ledger-only changes do **not** break concentration) + homeostasis diagnosis.
- **Ramp modes** — over-ramping, ramp scope creep, ramp bypass, ramp theater.
  Mitigation: ramp stages carry explicit checkable exit conditions.

## Extras

- Includes `primitives/evaluator-maturity.md` (T0–T6 tiers + ramp stages 0–9).
- Includes `primitives/pressure-accounting.md` so checkpointing is always
  explicit about pressure status, pressure debt, next pressure, and reason.
- Applies `primitives/benchmark-frontier.md` only when frontload binds a
  benchmark/eval/harness object. This is an overlay, not a fifth archetype.
- Applies `references/review-closure-overlay.md` when the branch is in closure
  mode (architecture landed; work comes from reviewed findings / exact probes).
- Carries the lessons of `references/same-family-drift.md` — the greedy
  proof-promotion and observability-echo drift that produced the same-family
  admissibility rule and the quiet-signal checkpoint.
- Body template: `templates/bodies/frontier-body.md`. No extra emitted file
  beyond a findings ledger + traces + benchmark outputs.
