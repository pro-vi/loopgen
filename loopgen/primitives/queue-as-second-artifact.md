# queue-as-second-artifact (shared primitive)

## Purpose

The pattern behind `artifact-shape.md`: every loop maintains `loop/PROMPT.md` +
`loop/STATE.md`, and **most also maintain a third durable artifact** — a
reviewable queue / inventory of discovered-but-not-yet-closed work — because
durable loop mechanics live in artifacts, not memory, and must survive context
compaction.

## Include when

Any composed prompt whose `artifact-shape` is not `prompt-only` (i.e. almost
all of them), as a framing note above the queue section.

## Why it is load-bearing

- **Human-reviewable** after a long autonomous run or a context compaction.
- **Prevents re-discovery** — the loop doesn't re-find the same work each pass.
- **Encodes what repo state can't** — reverted hypotheses, dead directions,
  oscillation history. Current repo state carries landed signal only.

## The queue is an index, not the source of intent

The story-loop learning: the queue is an *index of evidence and intent*, not
intent itself. Before treating an old row as truth, re-check the authority
source (human prompt, current docs, accepted issue/PR, reviewer guidance). An
old row, prior evidence, or a prior screenshot cannot certify that a promise /
criterion is still intended.

## Row contract

Each row records, at minimum: source / provenance · confidence · what would
prove it · status · reopen condition.

For benchmark-frontier, candidate rows are stricter and live in the overlay
artifact roles (`CANDIDATES`, `FRONTIER`, and `traces`) described in
`references/benchmark-frontier-artifacts.md`. That stricter row contract is not
inherited by pure frontier.

## When prompt-only is valid

Only the simplest finite single-criterion runs ("I found one bug, close it")
need no queue.

## Composition notes

- The concrete queue is chosen by `artifact-shape`: `acceptance-inventory`
  (goal) · `storyboard` (story) · `rubric+intent` (greenfield) ·
  `findings-ledger` (frontier).
- The queue is a tier-1/2 surface in `evidence-tier.md`.
