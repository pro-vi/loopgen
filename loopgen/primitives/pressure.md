# pressure (shared primitive)

## Purpose

Pressure is the universal force every loop runs inside: contextual **salience
with consequence** that bends the next move *before* the gate. A constraint is a
wall (a move is illegal); pressure is a slope (a move is allowed but uphill,
costlier, or now owes an explanation). The four archetype queue artifacts —
acceptance inventory (`goal`), storyboard (`story`), rubric+intent
(`greenfield`), findings ledger (`frontier`) — are all pressure surfaces; this
primitive names the contract they share. `primitives/pressure-accounting.md` is
the `frontier` projection of this object, not a separate concept.

## Include when

Emitted into a composed prompt as the `{{PRESSURE_SURFACE}}` block **only when
≥1 pressure object exists at compose time** (authored or mined). With zero
pressure objects the placeholder is left unsubstituted and stripped by the
`composed-prompt.md` dead-section rule — a pure archetype with no seeded
pressure stays byte-identical. Otherwise this file is a derivation-time
contract, not emitted. No seed, no slope.

## The pressure object

A pressure is a structured row in `loop/STATE.md` `pressure_objects` (rendered to
`loop/PRESSURE.md`), never prose. Prose pressure is decision-inert.

| field | values | role |
|---|---|---|
| `id` | stable string | anchor for ledger + read-back |
| `source` | `authored` · `mined` · `backpressure` | who put it in the field (human seed · latent-mined · fed back from an outcome) |
| `scope` | path / surface / criterion / dimension | what it covers |
| `mode` | `salience` · `preference` · `burden` · `constraint` | how it bends a move (authority on the surface) |
| `strength` | `low` · `medium` · `high` | how hard it tilts |
| `satisfied_by` | an `evidence-tier.md` tier-1/2 signal | what cashes it out — never the loop's own prose |
| `on_violation` | `owes_proof` · `owes_explanation` · `blocks` | the consequence half |
| `expires` | iteration / condition | mandatory decay; no row without one |
| `status` | `active` → `paid` · `hardened` · `stale` · `retired` | lifecycle |

**Modes**, weakest to strongest: `salience` (stay in attention) · `preference`
(favor unless reason not to) · `burden` (allowed but now owes proof) ·
`constraint` (hardened wall). When modes conflict on the same scope the stronger
wins: **`constraint` > `burden` > `preference` > `salience`**. Only `constraint`
is a wall; the other three are slopes.

## Placeholders

`{{PRESSURE_SURFACE}}` — substituted verbatim with the block below the `---`
when the gate holds; else stripped. The active rows themselves live in
`loop/PRESSURE.md` (re-read each pass), not inlined into the prompt.

## Authoring guidance (not emitted)

- **Gate.** Populate `{{PRESSURE_SURFACE}}` iff `count(pressure_objects) ≥ 1` at
  compose. This keeps zero-pressure pure archetypes byte-identical (U11).
- **Compaction survival.** The *pointer* ("re-read `loop/PRESSURE.md` each
  pass") must sit in the durable prompt — it rides the runner's user-role
  continuation, which survives Codex compaction verbatim while the assistant
  summary is lossy. The *content* lives on disk. File-backed beats
  context-trusted.
- **Salience without consequence is bloat; consequence without salience is
  review after the whistle.** Every row carries both halves or it is cut.

---

## Pressure weather

Before you select a queue row or score a criterion this iteration, re-read
`loop/PRESSURE.md`. It holds the active pressure field — the weather the
acceptance criteria get read in. Let each active row tilt the plan **while you
are still planning, before any gate**:

- `salience` — keep it in attention; name it in the plan.
- `preference` — favor the move it points to unless you have a reason not to.
- `burden` — the move it covers is allowed but now owes proof; cite tier-1/2
  evidence or do not claim it.
- `constraint` — a wall; the move is refused.

When modes conflict on one scope, the stronger wins (`constraint` > `burden` >
`preference` > `salience`). A pressure is real only if a later iteration can
point at where it bent a plan; a row whose `satisfied_by` cannot cite tier-1/2
evidence (`evidence-tier.md`) is cut, not rendered.

## Backpressure

When an attempt resolves against the world — a failed verify, eval, probe, or
review — capture the result as pressure for the next pass: append a
`source: backpressure` object to `loop/STATE.md` `pressure_objects` (it renders
into `loop/PRESSURE.md`), scoped to what failed, in the mode the failure implies
(a failed safety check is a `burden`; a corrupted oracle is a `constraint`), and
record its creation in `pressure_ledger`. This is how late consequence becomes
early pressure:
the next iteration starts already bent away from the failure instead of
re-discovering it. The loop improves not because the model got smarter but
because failure stops being wasted.

## Lifecycle

Each pass, retire what no longer earns its place. A `paid` pressure (its
consequence cashed out) drops from the weather; a `stale` pressure (past
`expires`, or its cause gone) retires; a soft pressure that kept costing the
same move may `harden` into a `constraint`. Record every transition in
`loop/STATE.md` `pressure_ledger`. Pressure without a lifecycle is bureaucracy
with better branding.
