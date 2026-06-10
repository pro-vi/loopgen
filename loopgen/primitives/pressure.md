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
| `source` | `authored` · `mined` · `backpressure` · `overlay` | who put it in the field (human seed · latent-mined · fed back from an outcome · seeded by a composition overlay as a fixed contract, e.g. benchmark-frontier oracle-integrity — provenance is the overlay activation + bound object, exempt from the `mined` low/salience entry rule) |
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

This is iteration **step 0**: before any numbered step of the protocol below,
first **re-render** `loop/PRESSURE.md` from `loop/STATE.md` `pressure_objects`
(the source of truth), then read it and run its maintenance pass (below).
`PRESSURE.md` is a pure projection you never trust independently — re-deriving it
each pass means a torn write (a crash between the STATE mutation and the render)
self-heals instead of stranding the loop on a stale half. It holds the active
pressure field — the weather the acceptance criteria get read in — and its header
carries these maintenance rules, so the discipline survives context compaction
even when this block is summarized away.

**Flush before you continue.** Every pressure mutation — appending a backpressure
row, any lifecycle transition — is written to `loop/STATE.md` `pressure_objects`
and re-rendered to `loop/PRESSURE.md` within the same tool-call sequence that
computed it, before the next decision. Never carry a pending pressure write in
context across a tool call: a compaction boundary can drop it, and the surviving
re-read pointer would then resume against a stale field with no signal a write
was lost. This is the write-ahead discipline the budget spend-ledger already
uses, applied to pressure state. `loop/PRESSURE.md` is the rendered view of
`loop/STATE.md` `pressure_objects` (the source of truth), not a separate store:
where a frontier checkpoint contract says to keep pressure in the findings
ledger / `loop/STATE.md` and not invent a new artifact, this is that same store
rendered — the two agree. Let each active row tilt the plan **while you are
still planning, before any gate**:

- `salience` — keep it in attention; name it in the plan.
- `preference` — favor the move it points to unless you have a reason not to.
- `burden` — the move it covers is allowed but now owes proof; cite tier-1/2
  evidence or do not claim it.
- `constraint` — a wall; the move is refused.

When modes conflict on one scope, the stronger wins (`constraint` > `burden` >
`preference` > `salience`). A pressure is real only if a later iteration can
point at where it bent a plan; a row whose `satisfied_by` cannot cite tier-1/2
evidence (`evidence-tier.md`) is cut, not rendered.

**Record the read-back.** Reading the weather is neither optional nor
self-attested. The numbered iteration protocol in the body does not list
`loop/PRESSURE.md`; step 0 above **extends** it — the pressure read is a
precondition of step 1. Each pass, write a `pressure_consulted` record to
`loop/STATE.md`: every active row id mapped to the plan element it bent, or
`no-effect: <reason>`. That turns "a pressure bent my plan" from prose the loop
can fabricate or silently skip into an artifact the next pass and the case-12
trace can diff against the moves actually made. A pass with no
`pressure_consulted` record has not completed step 0.

**Maintain walls or they fall.** Each pass, re-test every enforced `constraint`
row — `status: active` **or** `hardened`, the two states still in force —
against its reopen / `expires` condition before treating it as a wall. A
`constraint` you did not re-test this pass is read as a `burden` (a slope), not a
wall — a neglected wall un-bricks, it never bricks the loop. This fail-open
default is the guard against self-bricking on a stale or false-negative wall: the
loop self-polices these rules, so the only safe default is the one where neglect
errs toward the slope, never toward the locked door.

Pressure shapes **how** a move is chosen, never **whether** a gate is met. No
mode — not even `constraint` — can deprioritize an `OPEN` acceptance criterion,
suppress a required verify, or let an archetype halt with its terminal contract
unmet. The archetype gate (goal's binary oracle, frontier's pressure checkpoint,
story's ready-gate, greenfield's phase gates) outranks every pressure: pressure
may reorder how you approach the work; it may never erase the work.

**Constraint deadlock escalates.** The priority rule above resolves modes on one
scope; it says nothing about two `constraint` rows on different but overlapping
scopes. When two walls make the set of legal moves toward an `OPEN` gate empty
(every move is refused by one wall or the other), do not spin re-selecting the
criterion or mislabel it `STUCK`: that is a `constraint-deadlock`, which routes to
`genuine-escalate` — a human must relax or re-scope one wall. Name the two
constraints in the halt summary so the next derivation sees the real cause.

## Backpressure

When an attempt resolves against the world — a failed verify, eval, probe, or
review — capture the result as pressure for the next pass: append a
`source: backpressure` object to `loop/STATE.md` `pressure_objects` (it renders
into `loop/PRESSURE.md`), scoped to what failed, in the **softest** mode the
failure justifies — default `burden`, never `constraint` from a single signal. A
backpressure `constraint` (a wall) requires the failure reproduced on a tier-1/2
channel, and even then carries an `expires`/reopen condition: a wall built from
one flaky or transient failure would permanently brick a legitimate fix, and the
loop would self-brick. Record its creation in `pressure_ledger`. This is how late
consequence becomes early pressure:
the next iteration starts already bent away from the failure instead of
re-discovering it. The loop improves not because the model got smarter but
because failure stops being wasted.

**Watch for coupled regression.** Backpressure can ping-pong: fixing scope A
regresses scope B (mints backpressure on B), the next pass fixes B and regresses
A, and the loop runs all night minting alternating rows. Each is a real tier-1/2
failure, so no per-criterion stuck counter ever trips (a *different* scope fails
each pass) and the loop stays alive because some move is always legal — the
oscillation *is* the failure, and nothing per-criterion sees it. When the
`pressure_ledger` shows backpressure alternating between the same two (or N)
scopes over a short window of recent passes (the coupled-window) with no net
criterion-count progress, that is a **coupled-regression** signal, not endless
work: the scopes need joint resolution. Halt with `genuine-escalate` (reason
`coupled-regression`), naming the coupled scopes so a human or the next
derivation can break the coupling — for `goal` this also surfaces as
`partial-deadlock`, for `frontier` it feeds the structural-escalation bridge. Do
not keep ping-ponging.

## Lifecycle

Each pass, retire what no longer earns its place — but a transition is a claim
that owes evidence, exactly like a queue row:

- → `paid` **only** when `satisfied_by` cites fresh tier-1/2 evidence produced
  this run (`evidence-tier.md`). A row may never be flipped to `paid` on the
  loop's own say-so — self-narrated payment is FIXED≠CLOSED laundering that lets
  the loop escape an unmet pressure. The `satisfied_by` channel is
  **pre-registered at creation**: a row pays out only on the channel it declared
  when authored / mined, not a weaker or different one chosen at payment time (a
  green cheap channel that doesn't exercise the pressured scope is a known
  false-green, not payment). A strictly *stronger* channel may be adopted only by
  an explicit re-stamp recorded in `pressure_ledger` (the merge / strengthen
  path), never silently swapped in at payment.
- → `stale` / retired carries the **same** evidence burden as `paid`: cite the
  tier-1/2 signal that proves `expires` met or the cause externally gone — never
  the loop's own say-so. (Retiring is the easiest launder-and-shred exit — drop
  an inconvenient row to `stale`, then collapse it. The required evidence cite,
  kept in the ledger summary, is what blocks it; without it the paid-laundering
  escape just reroutes through `stale`.)
- → `hardened` (soft → `constraint`) only when the same soft pressure kept
  costing the same move across iterations, recorded with that evidence. A
  `hardened` row is still **in force**: it stays in the wall-maintenance set
  above and is re-tested every pass exactly like an `active` `constraint` — it is
  not a terminal state, so it can still be demoted or retired when its reopen
  condition is met.

Record every transition in `loop/STATE.md` `pressure_ledger`, each with its
evidence cite. Bound **both** sets, not just retired rows: a new `source:
backpressure` row scoped to an already-pressured scope **merges into** the
existing row (strengthen / re-stamp), never appends a duplicate; more than
`pressure-cap` in-force rows (`active` or `hardened` — the two states still
re-tested each pass; concrete default 12, frontload-tunable alongside
stuck-attempt-N / quiet-signal-N when pressure is active), or a row that keeps
oscillating its mode (`constraint` ↔ `burden`) or re-stamping without ever
reaching a terminal status (`paid` / `stale` / `retired`), is itself a halt /
checkpoint cause (a `derivation-gap`, or `frontier`'s `checkpoint_reason`), not
silent growth. The `pressure_ledger` itself is capped, not
just the active set: keep at most the last `K` transitions per row (default
`K = 5`) — older in-flight transitions on a non-terminal row collapse to a count +
last state, so an oscillating or repeatedly re-stamped row cannot grow the ledger
without bound. Once a row reaches a terminal status (`paid` / `stale` /
`retired`), collapse its whole history to a one-line summary (id, final status,
evidence); terminal summaries beyond the most recent `M` (default 50) collapse to
an aggregate count. The ledger is therefore bounded by `pressure-cap`·`K` + `M` +
1 — the concrete ceiling case 12 checks: the in-force set (`active` + `hardened`)
is capped at `pressure-cap`, each carrying ≤ `K` transitions, while every
terminal row (`paid` / `stale` / `retired`) is already collapsed to a one-line
summary counted under `M`, so no status escapes both caps. Pressure
without a lifecycle is bureaucracy with better branding; a lifecycle without
evidence is the same laundering wearing a clock.
