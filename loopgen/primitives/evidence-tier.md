# evidence-tier (shared primitive)

## Purpose

The signal hierarchy: how the loop ranks memory surfaces when deciding what to
trust as evidence for the next intervention. Constant across all archetypes;
the classifier never overrides this ranking.

## Include when

Every archetype except `goal` — the `frontier` body inlines it as its
"Signal hierarchy" section; `story` and `greenfield` pull it via
`{{INCLUDE primitives/evidence-tier.md}}`. `goal` deliberately carries no
standalone Signal hierarchy: its evidence surface is oracle principles + the
acceptance inventory (`templates/composed-prompt.md` §8) — do not add this
block to a `goal` prompt. The always-on pressure surface still speaks this
vocabulary (`satisfied_by` is a tier-1/2 signal — `primitives/pressure.md`),
so the `goal` body carries a compact tier mapping onto its own surfaces
(external review → tier 1; verifier / oracle / acceptance evidence → tier 2)
in place of the hierarchy.

## Composition notes

- Every archetype's queue artifact (`artifact-shape.md`,
  `queue-as-second-artifact.md`) is a tier-1/2 surface — the loop's primary
  defense against drift.
- This ranking is the substrate the `frontier` same-family admissibility rule
  and quiet-signal checkpoint key on (`archetypes/frontier.md`,
  `references/same-family-drift.md`).
- **Tier ranks trust, not read-scope.** These tiers rank a surface's
  *evidentiary authority* — what the loop may trust as proof for the next
  intervention. They are orthogonal to `context-stack.md`'s PINNED / WORKING /
  ON-DEMAND tiers, which rank *when and how much* of a file is re-read. The queue
  is a tier-1/2 *trust* surface **and** a WORKING *read-scope* surface at the same
  time; the two rankings are different axes and must never be conflated.

---

## Signal hierarchy

1. **Externally reviewed findings** — human or external-review output the loop
   did not author. Highest authority; independent of the loop's own narrative.
   Its authority stops at the commit range it read: the commit that fixes its
   findings is code no review has seen, so "every finding fixed" is not "the
   review is closed" — closure needs the same channel run again over the fix.
2. **Typed / machine-derived artifacts** — structured run traces, harness
   state, oracle verdicts, benchmark outputs. Not self-narrated.
3. **Self-authored ledger prose** — the loop's own notes / ledger / findings
   markdown. Useful, but can narrativize drift; weaker than typed artifacts.
4. **Commit-log narrative** — weakest. Use only as a **negative**
   anti-repetition signal, never as positive generative evidence for the next
   intervention; self-narrated recency re-certifies whatever shape dominated
   the window.

## Degraded-coverage rule

If only weak surfaces (tier 3–4) exist, anti-collapse coverage is degraded.
Creating a minimal structured findings surface is itself a valid evaluator-axis
job when the cheap channel is green and no stronger signal is available. Never
emit language that pretends anti-collapse coverage exists when the substrate
for it does not.
