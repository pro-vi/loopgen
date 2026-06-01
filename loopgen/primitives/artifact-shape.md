# artifact-shape (axis primitive)

## Purpose

Which durable queue artifact the loop maintains beyond `loop/PROMPT.md` and
`loop/STATE.md` — the concrete form of the pattern in
`queue-as-second-artifact.md`. Weight 3. Determines the extra file Phase 4
emits.

## Values

- `prompt-only` — no queue. Valid only for the simplest finite single-criterion
  runs.
- `acceptance-inventory` — `loop/ACCEPTANCE.md`: frozen criteria with stable
  IDs, mutable `status` / `last_verification`.
- `storyboard` — `docs/storyboard.{md,yaml}`: product promises, each row with
  source / confidence / proof / latest evidence.
- `rubric+intent` — `loop/RUBRIC.md` (numbered criteria with 0/2/5 anchors) +
  `loop/INTENT.md` (≥3 live target hypotheses).
- `findings-ledger` — a loop ledger + structured failure traces + metric
  outputs.

## Detection heuristics

| Task phrasing | Value |
|---|---|
| finite criteria / spec | `acceptance-inventory` |
| product promises, frontend behavior | `storyboard` |
| manufactured evaluator + shifting target | `rubric+intent` |
| existing thing to improve, with evidence | `findings-ledger` |
| one-bug single-criterion fix | `prompt-only` |

## Archetype defaults

| Archetype | Default |
|---|---|
| frontier | `findings-ledger` |
| goal | `acceptance-inventory` |
| story | `storyboard` |
| greenfield | `rubric+intent` |

## Composition rules

- Each artifact is a tier-1/2 evidence surface (`evidence-tier.md`) and an
  **index** of evidence/intent, not the source of intent
  (`queue-as-second-artifact.md`).
- Phase 4 emits the chosen artifact as an extra file alongside PROMPT.md +
  STATE.md (`ACCEPTANCE.md` / `storyboard.*` / `RUBRIC.md`+`INTENT.md`); a
  findings-ledger is *suggested*, not silently invented, when the repo lacks a
  convention.
- A pure frontier `findings-ledger` carries generic pressure accounting. The
  benchmark-frontier overlay may additionally emit `DOMAIN_SPEC`, `BENCHMARK`,
  `CANDIDATES`, `FRONTIER`, and `traces` roles, but those roles are conditional
  overlay artifacts and do not change this axis value.
- `acceptance-inventory` pairs with `target-shape: finite-criteria`.
- A divergence on this axis (e.g. `storyboard` into a frontier body) swaps the
  queue section AND the extra emitted file; name it in provenance.
