# greenfield (archetype)

## Loop shape

A green-field discovery loop. Evaluator scaffolding precedes the artifact: a
score-locked ramp builds `loop/RUBRIC.md` before the first production render.
The loop then discovers *what* to build, the target phase-shifts as intent
reveals itself (≥3 live `loop/INTENT.md` hypotheses), and sequenced plans give
way to imbalance-seeking. The user curates intent, names failure modes, and
raises ceilings; the loop proposes, the user disposes.

## Default primitive values

| Axis | Default |
|---|---|
| `target-shape` | `discovery-reframing` |
| `halt-shape` | `manual-gated` |
| `artifact-shape` | `rubric+intent` |
| `convergence-shape` | `stone-reframe` |
| `cadence-shape` | `checkpoint-gated` |
| `consult-capability` | detect (`tier-0` default) |

## Forbidden divergences

- `target-shape: finite-criteria` — a fixed target is not green-field; route to
  `goal`.
- Any existing benchmark / oracle / CI signal / pre-built thing to improve —
  that is `frontier`, not green-field.

## Failure modes

- **Rubric inflation (agent grades own homework)** — the dominant early failure.
  Mitigation: pixel/artifact citation mandatory for any score above 2; a blind
  comprehension read for audience-facing scores above 3.
- **Escalate-polling** — pausing for input that should be a judgment call.
  Mitigation: judgment-default + bounded escalate triggers + saturation rule.
- **Ceiling capture** — a numerical milestone becomes a ceiling once hit.
  Mitigation: raise the ceiling as a **new** rubric version with score
  quarantine, not a stricter restatement of stale criteria.
- **Capability stagnation** — the loop won't grow new tools. Mitigation:
  CAPABILITY mode at priority 0/1 (must advance the stone, not pad the toolbelt).
- **Self-congratulation on a wrong target** — Mitigation: frontier-model
  creative consults (when `consult-capability ≥ tier-2`); INTENT.md re-review.

## Extras

- Includes the 11 invariants (`references/greenfield-invariants.md`).
- Emits `loop/RUBRIC.md`, `loop/INTENT.md`, and `loop/README.md` as required
  artifacts.
- Uses research → preloop → bootstrap → iter phase gates, each with
  `owner: loop | user | external`; user-owned gates cannot be flipped by the
  loop.
- Body template: `templates/bodies/greenfield-body.md`.
