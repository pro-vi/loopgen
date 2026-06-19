# diagnostic-pattern (shared primitive)

## Purpose

Used by `SKILL.md` Diagnostic mode to retrofit a **drifting** loop — not to
author a new one.

## Include when

Diagnostic mode only. Not part of an emitted prompt.

## Procedure

1. **Read** the current `loop/PROMPT.md`, `loop/STATE.md`, the queue artifact
   (`artifact-shape`), and the ledger / recent diffs.
2. **Classify which archetype the loop currently is** — extract its live
   primitive values. It may have **drifted from its declared archetype** (the
   loopgen addition).
3. **Score** against that archetype's failure modes (`archetypes/*.md`).
4. **Name** the dominant disturbed axis / missing invariant.
5. **Emit a minimal mutation** — an inline `loop/PROMPT.md` edit, never a
   rewrite. The hand-evolved prompt has hard-won lessons; add what is missing
   without losing them.
6. **Write a ⚠️ block** to `loop/STATE.md` telling the next iteration what
   changed and why.

## Drift-from-declared check (loopgen addition)

If the loop's current primitive values no longer match its declared archetype,
**flag the drift in the ⚠️ block before suggesting a mutation**. A loop whose
`target-shape` has changed (e.g. a frontier loop that has discovered a finite
checklist) may need re-derivation via the full Phase 1–4 flow, not a patch.

## Composition notes

- Reuses the `evidence-tier` ranking to decide which surfaces to trust when
  diagnosing.
- The mutation's success criterion is itself a frontier anchor: the next
  iteration should confirm the drift closed.
