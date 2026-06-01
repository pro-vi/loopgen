# halt-cause-classifier (shared primitive)

## Purpose

When the loop emits `stop-and-summarize` or `escalate: <reason>`, it labels the
cause so the user — and the next derivation pass — can route it back. Unifies
the four legacy classifiers.

## Include when

Every composed prompt, under "Halt conditions." Emit the shared causes plus the
nearest archetype's stop cause (a divergence may add a second archetype's stop
cause). For frontier, the stop cause is a checkpoint, not completion.

## Shared causes (in every prompt)

- `derivation-gap` — blocked on something derivation could have asked for
  (model identity, budget cap, secret, path, fixture, …). **The feedback
  signal**: it tells the user the frontload checklist was incomplete; close it
  next run.
- `genuine-escalate` — irreversible / external / authority-needed (paid API
  budget, public-publish, secrets, product direction with unclear rollback,
  source conflict between authoritative-current sources).
- `signal-starvation` — quiet region: no new strong evidence (no typed trace,
  no reviewed finding, no metric movement, no user reframe) for the configured
  stretch; the quiet-signal checkpoint fired.
- `wrong-loop` — the work belongs in a different archetype (see reroute table).

## Completion semantics

Shared halt causes are **iteration/session halts**, not proof that the loop's
frontier or goal is complete. A prompt MUST make this distinction explicit:

- `genuine-escalate`, `derivation-gap`, `signal-starvation`, and `wrong-loop`
  mean "this invocation halted"; they must report the frontier/queue as still
  OPEN unless the queue is independently empty.
- Frontier loops never self-complete. `homeostatic-checkpoint` means no
  high-yield admissible intervention remains after a full scan; the frontier is
  balanced for now and reopens on fresh signal.
- Only non-frontier archetype-terminal success causes may claim archetype
  completion (`criteria-met`, `storyboard-converged`, or `stone-converged`).
- On any non-terminal shared halt, final output must say the invocation halted
  and report the artifact as OPEN or checkpointed as appropriate, then list the
  unresolved queue rows and the external authorization or derivation change
  needed to resume.
- Runners that expose a generic "goal complete" switch must not use it for a
  non-terminal shared halt. They may mark the *invocation* complete, but the
  loop artifact remains active/paused with OPEN work.

## Non-terminal halt precondition

Before emitting any non-terminal shared halt, the loop MUST scan its full
search surface, not only the currently selected row:

- frontier loops scan all homeostasis axes and all OPEN findings / anchors;
- goal loops scan all acceptance rows and verifier/oracle gaps;
- story loops scan storyboard lanes and unresolved promise rows;
- greenfield loops scan rubric/intent hypotheses and blocked capability
  surfaces.

A single blocked row is not enough to halt. If another reversible, in-scope
intervention can move a different axis or strengthen the evaluator, the loop
continues with that intervention. A non-terminal halt is valid only when every
remaining useful intervention is blocked by the same external authority, would
violate scope/budget, or is low-yield same-family polish with no fresh evidence.

For frontier loops, the halt scan must also emit the pressure accounting fields:
`pressure_status`, `pressure_debt`, `checkpoint_reason`, and `next_pressure`.
Checkpointing with no pressure scan, open pressure, or no checkpoint reason is
invalid; the runner reports the frontier as active or externally paused instead.

The final output for a non-terminal halt must include a compact "halt scan"
naming each searched axis/queue class and why no safe continuation remains.

## Archetype stop causes

| Archetype | Stop cause(s) |
|---|---|
| frontier | `homeostatic-checkpoint` (checkpoint, not completion) |
| goal | `criteria-met` (success) · `partial-deadlock` · `oracle-drift` |
| story | `storyboard-converged` |
| greenfield | `stone-converged` |

## wrong-loop reroute targets

- finite checklist with a pass line → `goal`
- open-ended "make it better" with no pass line → `frontier`
- product-promise discovery / reconciliation → `story`
- target / artifact / evaluator undefined → `greenfield`

## Composition notes

- The stop cause matches the archetype's `convergence-shape`.
- `derivation-gap` is what makes the `frontload-audit` self-improving across
  runs.
