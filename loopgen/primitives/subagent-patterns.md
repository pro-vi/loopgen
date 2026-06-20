# subagent-patterns (shared primitive, gated)

## Purpose

Let a composed prompt reach for **parallel / independent subagents** when the
host actually has a consult channel — a *capability*, not a leash. The honest
failures it covers: a loop that can't fan an investigation out in parallel,
can't poll a long-running job without blocking, and has no cheap *independent*
second look at its own result. These are advantages to take when they help,
never accountability machinery the loop must satisfy to proceed.

This block adds only patterns **B / C / D**. Pattern **A — single-agent
iteration — is the protocol every body already emits**, not a catalog addition;
it is sufficient on its own and is never gated away.

## Include when

**Gated on the existing `consult-capability` tier** (no new per-capability
detection vocabulary — inventing async-polling / isolation / judge-independence
detection is exactly the over-build this stays clear of). At **`tier-0` the
whole `{{SUBAGENT_PATTERNS}}` block is stripped → byte-identical**: the loop runs
single-agent via pattern A. Above tier-0, only the patterns at or below the
detected tier are emitted; the composer drops the rest at compose time (the same
empty-gate stripping `pressure.md` uses).

The mapping accepts that **consult-tier ≈ channel richness, not exact
capability** — a deliberate simplification, not a precise capability probe.

## The patterns

| Pattern | What it is | Gate |
|---|---|---|
| **A** single-agent iteration | the existing per-iteration protocol every body emits | always — **not** part of this block |
| **D** cheap independent re-check | a quick *second look* at a result through an independent channel | tier ≥ 1 (tier-1 = human-look gate; tier ≥ 2 = programmatic) |
| **B** parallel fan-out | split an investigation across independent agents (investigate / refute / cross-domain) and reconcile | tier 3 (blind-adversarial + multi-modal fabric) |
| **C** long-experiment polling | submit a long job, poll it, auto-diagnose and resubmit on failure instead of blocking | tier 3, or wherever frontload binds a pollable job channel |

**D is a second look, not a tribunal.** It exists to catch the loop's own
*honest* mistakes (drift, a missed case), not to "prove" the loop didn't cheat —
the threat model here is honest failure, not deception. It is never a required
gate: an iteration is accepted on the archetype's own contract, with or without D.

This complements, and does not replace, the existing
Consult → Architect → Build bridge a `frontier` body already carries
(`templates/bodies/frontier-body.md`); the consult cadence still aligns with
`cadence-shape` boundaries (`primitives/consult-capability.md`).

## Placeholders

`{{SUBAGENT_PATTERNS}}` — substituted with the block below the `---`, filtered to
the patterns the detected consult-tier meets; stripped entirely at `tier-0`. It
sits immediately after `{{PRESSURE_SURFACE}}` in every body (section 6b — mirrors
6a's placement and strip rule).

## Authoring guidance (not emitted)

- **Gate.** Fill `{{SUBAGENT_PATTERNS}}` iff `consult-tier ≥ 1`; keep only the
  rows whose tier-gate the detected tier meets; otherwise strip (byte-identical).
- **Capability, not obligation.** Nothing in this block forces a pattern. If the
  emitted language ever reads as "you must run an independent check to accept,"
  it has drifted from capability into a leash — cut it back.
- **No new detection vocabulary.** Map onto `consult-capability` tier-0..3; do
  not invent capability flags.

---

## Subagent patterns (available capability — not required)

Pattern **A — single-agent iteration** is the protocol you already run; it is
not listed here and is always sufficient on its own. The patterns below are
*optional* parallel / independent moves this host's consult channel
(`tier-{{CONSULT_TIER}}`) makes available — capabilities to reach for **when they
help**, never gates you must pass to accept an iteration.

- **D — cheap independent re-check** *(consult tier ≥ 1)*: take a quick second
  look at a result through an independent channel before trusting it. At tier-1
  this is an async human-look handoff; at tier ≥ 2 it is programmatic. A *second
  look* to catch your own honest mistakes (drift, a missed case) — **not** an
  accountability tribunal, and never a required gate.
- **B — parallel fan-out** *(consult tier 3)*: split an investigation across
  independent agents — investigate / refute / cross-domain — and reconcile their
  findings. Blind-adversarial + multi-modal; use when one search angle won't
  surface everything.
- **C — long-experiment polling** *(consult tier 3, or wherever frontload binds a
  pollable job channel)*: submit a long-running job, poll it, and auto-diagnose
  and resubmit on failure instead of blocking the loop on it.

Only the patterns at or below this loop's consult tier are live; the rest were
dropped at compose. None is required to accept an iteration — the single-agent
protocol remains sufficient.
