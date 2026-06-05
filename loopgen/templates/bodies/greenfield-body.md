# Greenfield Prompt Body (archetype body template)

The emittable body for a green-field discovery loop — the one archetype with no
legacy prompt template, reconstructed from `greenfield-loop`'s emit procedure +
the 11 invariants. `/loopgen` (Phase 3) fills the `{{placeholders}}`, resolves
the `{{INCLUDE …}}` markers by inlining the named block, and drops conditional
sections that do not apply. The outer fence is **four backticks** so nested
`yaml` / `text` blocks work inside.

---

````md
You are running a green-field discovery loop on this repository.

Your job is not to optimize a fixed metric.
Your job is to discover what to build, let the target reveal itself, and then
make it real — without grading your own homework.

{{PROVENANCE}}

## Motive

{{MOTIVE}}

{{INCLUDE primitives/runner-contract.md}}

## Frontload

{{FRONTLOAD_PREAMBLE}}

{{PRESSURE_SURFACE}}

## Green-field invariants

These eleven invariants are load-bearing; each corresponds to a failure mode a
real green-field loop hit the hard way. Encoding them up front saves 50–100
iterations of rediscovery. **Invariant 7 carries the Judgment default;
invariant 8 carries the consult contract** — do not also emit them separately.

{{INVARIANTS}}
<!-- inline the 11 invariants verbatim from references/greenfield-invariants.md -->

## Capability surface

CAPABILITY mode is first-class (invariant 6). The loop may install / integrate
the following to advance the stone — each addition justified against a
stone-axis, never to pad the toolbelt:

{{CAPABILITY_LIST}}

{{INCLUDE primitives/evidence-tier.md}}

## Phase gates

Phase order: research → preloop → bootstrap (iter 0, automated) → iter 1+.
Each gate declares `owner: loop | user | external`. A `user`-owned gate
(preloop_complete, license clicks, secret install, identity decisions) cannot
be flipped to `yes` by the loop. Gate hardening: binary `yes`, or halt.

{{PHASE_GATES}}

## Halt conditions

This loop is `manual-gated` (see `halt-shape`): it persists by design and ends
only when the user flips `Next action: HALT` (owner: user) or on a classified
cause below. `stone-converged` is the user's call — the loop proposes, the user
disposes. Convergence is `stone-reframe`: the artifact landing on the user's
*reframed* target, not a fixed number.

{{INCLUDE primitives/halt-cause-classifier.md}}
<!-- terminal cause for this archetype: stone-converged -->

## Artifacts to maintain

- `loop/RUBRIC.md` — numbered criteria (8–12), 0–5 scale, concrete pixel/
  artifact anchors. Every score >2 cites evidence (invariant 2). Carries
  `rubric_version` + `score_comparable_with`; score quarantine on reframe
  (invariant 4).
- `loop/INTENT.md` — ≥3 live target hypotheses with invalidating evidence and
  a cheap distinguishing probe each (invariant 3).
- `loop/STATE.md` — phase, iteration, `score_lock`, gate owners/values, current
  open seams, last/next action, `Next action: HALT` hatch (owner: user).
- `loop/README.md` — how to fire, how to tune the rubric, how to halt, what
  milestones look like.

{{INCLUDE primitives/queue-as-second-artifact.md}}
<!-- this archetype's queue is rubric+intent; it is an INDEX, not the source of intent -->
````

---

## Derivation notes

Placeholders populated during composition (see `templates/composed-prompt.md`):

- `{{PROVENANCE}}` — the loopgen provenance preamble.
- `{{MOTIVE}}` — the user's one-sentence intent ("build me something X-adjacent").
- `{{FRONTLOAD_PREAMBLE}}` — resolved / defaulted / open-gap summary.
- `{{PRESSURE_SURFACE}}` — the pressure weather block (`primitives/pressure.md`),
  emitted only when ≥1 pressure object exists at compose time; stripped otherwise.
- `{{INVARIANTS}}` — inline the 11 invariants verbatim from
  `references/greenfield-invariants.md`.
- `{{CAPABILITY_LIST}}` — domain-specific tools the loop may install (invariant 6).
- `{{PHASE_GATES}}` — research/preloop checklist items with owners (invariant 10).
- `{{ARTIFACT_LOCATIONS}}` — concrete paths.

Consult degradation: if `consult-capability` is `tier-0`, invariant 8 is
marked `CONSULT unavailable in this environment — front-loaded as a known
limitation` and a periodic human-look gate is added (see
`primitives/consult-capability.md`). Do not silently drop the invariant.
