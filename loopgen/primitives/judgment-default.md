# Judgment Default (shared primitive)

**Purpose.** Sets the loop's default response to a taste-based or inferred
judgment call: take the narrow reversible action and log an Alignment
Review, rather than pausing to poll the human. Pausing for input is the
polling-shaped failure mode that kills overnight loops; this block is the
structural fix. It also enumerates the *only* conditions that justify
`escalate` instead of proceeding.

**Include when.** Every composed prompt, every archetype, unconditionally.
The escalate triggers compose with `consult-capability` (a tier-0
environment may have to emit a human-bridge handoff where a richer
environment would consult programmatically) and with `halt-cause-classifier`
(`genuine-escalate`).

**Placeholders.** None — substituted verbatim.

---

## Judgment default

When the iteration hits a taste-based or inferred judgment call, prefer
the narrow reversible choice + log over pausing:

1. Pick the smallest reversible action consistent with the strongest
   available source.
2. Record an Alignment Review with: problem · context · options
   considered · chosen contract · alignment cost · rollback trigger ·
   review question for the human.
3. Continue. Human review happens after the fact.

Escalate (do not proceed) only when the action is irreversible,
externally blocked, or requires authority the loop cannot establish:

- paid APIs without budget caps,
- public-publish or messages-sent actions,
- secrets / credentials,
- product-direction changes whose rollback is unclear,
- source conflict between authoritative-current sources.

**Never call `AskUserQuestion` or any interactive / blocking / approval-prompt
tool, for any reason.** The runner may be unattended, so the call is a deadlock,
not a question. Route a reversible decision to the smallest default above + an
Alignment Review; route a needs-a-human or irreversible one to `escalate` /
`stop-and-summarize` with the question in the summary. Async, never interactive.
