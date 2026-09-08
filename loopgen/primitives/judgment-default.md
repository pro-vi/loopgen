# Judgment Default (shared primitive)

**Purpose.** Sets the loop's default response to a taste-based or inferred
judgment call: take the narrow reversible action and log an Alignment
Review, rather than pausing to poll the human. Pausing for input is the
polling-shaped failure mode that kills overnight loops; this block is the
structural fix. It also enumerates the *only* conditions that justify
`escalate` instead of proceeding.

**Include when.** Every composed prompt, every archetype, unconditionally.
The escalate triggers compose with `consult-capability` (a tier-0
environment routes consult-shaped needs to the Human-look gate's review
packet — `primitives/human-look-gate.md`; tier-1 emits an async human-bridge
handoff; richer environments consult programmatically) and with
`halt-cause-classifier` (`genuine-escalate`).

**Placeholders.** None — substituted verbatim.

---

## Judgment default

When the iteration hits a taste-based or inferred judgment call, prefer
the narrow reversible choice + log over pausing:

1. Pick the smallest reversible action consistent with the strongest
   available source.
2. Record an Alignment Review as an `alignment_review` record in
   `.loop/<loop-id>/JOURNAL.jsonl` with: problem · context · options
   considered · chosen contract · alignment cost · rollback trigger ·
   review question for the human. Heavy detail is a pointer, not an inlined
   blob, per the journal's ≤300-char target (`primitives/context-stack.md`).
3. Continue. Human review happens after the fact.

Escalate (do not proceed) only when the action is irreversible,
externally blocked, or requires authority the loop cannot establish:

- paid APIs without budget caps,
- public-publish or messages-sent actions,
- secrets / credentials,
- external disclosure of repository, connector, personal, customer, or other
  restricted data without destination-specific authorization,
- installation or execution of a new dependency, package, plugin, extension,
  MCP server, downloaded binary, or remote installer without source-specific
  authorization,
- product-direction changes whose rollback is unclear,
- source conflict between authoritative-current sources.

**Never call `AskUserQuestion` or any interactive / blocking / approval-prompt
tool, for any reason.** The runner may be unattended, so the call is a deadlock,
not a question. Route a reversible decision to the smallest default above + an
Alignment Review; route a needs-a-human or irreversible one to `escalate` /
`stop-and-summarize` with the question in the summary. Async, never interactive.
