# evidence-tier (shared primitive)

## Purpose

The signal hierarchy: how the loop ranks memory surfaces when deciding what to
trust as evidence for the next intervention. Constant across all archetypes;
the classifier never overrides this ranking.

## Include when

Every composed prompt, as its "Signal hierarchy" section.

## Composition notes

- Every archetype's queue artifact (`artifact-shape.md`,
  `queue-as-second-artifact.md`) is a tier-1/2 surface — the loop's primary
  defense against drift.
- This ranking is the substrate the `frontier` same-family admissibility rule
  and quiet-signal checkpoint key on (`archetypes/frontier.md`,
  `references/same-family-drift.md`).

---

## Signal hierarchy

1. **Externally reviewed findings** — human or external-review output the loop
   did not author. Highest authority; independent of the loop's own narrative.
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
