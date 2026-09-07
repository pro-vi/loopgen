# subagent-patterns (shared primitive, gated)

## Purpose

Let a composed prompt reach for **parallel / separate subagents** when the
host actually has a consult channel — a *capability*, not a leash. The honest
failures it covers: a loop that can't fan an investigation out in parallel,
can't poll a long-running job without blocking, and has no cheap *separate*
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
| **D** cheap separate second look | a quick *second look* at a result through a separate channel | tier ≥ 1 (tier-1 = async human-bridge handoff; tier ≥ 2 = programmatic) |
| **B** parallel fan-out | split an investigation across separate agents (investigate / refute / cross-domain) and reconcile | tier 3 (blind-adversarial + multi-modal fabric) |
| **C** long-experiment polling | submit a long job, wait on it through the runner's non-blocking wait primitive (never a foreground call that sleeps), auto-diagnose and resubmit on failure — under a durable job id + capped retry/backoff | tier 3, or tier ≥ 1 with a pollable job channel |

**D is a second look, not a tribunal.** It exists to catch the loop's own
*honest* mistakes (drift, a missed case), not to "prove" the loop didn't cheat —
the threat model here is honest failure, not deception. It is never a required
gate: an iteration is accepted on the archetype's own contract, with or without D.

This complements, and does not replace, the existing
Consult → Architect → Build bridge a `frontier` body already carries
(`templates/bodies/frontier-body.md`); the consult cadence still aligns with
`cadence-shape` boundaries (`primitives/consult-capability.md`).

## Placeholders

`{{SUBAGENT_PATTERNS}}` — substituted with the block below the `---`, **filtered
bullet-by-bullet** to the B/C/D patterns the detected consult-tier meets (D at
tier ≥ 1; B at tier 3; C at tier 3 or tier ≥ 1 with a pollable channel) — the
composer emits only the applicable bullets as it fills the placeholder (step 7b),
so a tier-1/2 host never sees a tier-3 pattern inlined; the whole block is
stripped at `tier-0`. It sits immediately after `{{PRESSURE_SURFACE}}` in every
body (section 6b — same gated placement + strip rule as the pressure surface).

`{{CONSULT_TIER}}` — a **nested** fill inside the emitted block (the tier
detected on the *composing* host, e.g. `tier-2` — the Run-host channel check
resolves what is effective), present only when the block emits; filled by
step 7b, never left dangling (at `tier-0` the whole block is gone).

## Authoring guidance (not emitted)

- **Gate.** Fill `{{SUBAGENT_PATTERNS}}` iff `consult-tier ≥ 1`; keep only the
  rows whose tier-gate the detected tier meets; otherwise strip (byte-identical).
- **Capability, not obligation.** Nothing in this block forces a pattern. If the
  emitted language ever reads as "you must run an independent check to accept,"
  it has drifted from capability into a leash — cut it back.
- **No new detection vocabulary.** Map onto `consult-capability` tier-0..3; do
  not invent capability flags.
- **Separation is not independence.** The emitted text says *separate*, never
  *independent*: sibling channels share the host and the conversation cone, and
  role separation alone is not attested isolation. An *independent* claim is
  earned only by runner-attested isolation, which no current host provides —
  until one does, the strongest honest claim is a separate second look.
- **Compose-time detects; the run host governs.** `{{CONSULT_TIER}}` is the
  composing host's detection, and emitted wording must never present it as
  what *this* runner has live. Every consult-dependent instruction defers to
  `consult_tier_effective` (+ per-channel basis) in `STATE.md`, written and
  kept fresh by the Run-host channel check
  (`primitives/consult-capability.md`).

---

## Subagent patterns (available capability — not required)

Pattern **A — single-agent iteration** is the protocol you already run; it is
not listed here and is always sufficient on its own. The patterns below are
*optional* parallel / separate moves emitted for the consult tier detected on
the composing host (`{{CONSULT_TIER}}`) — capabilities to reach for **when
they help**, never gates you must pass to accept an iteration.

- **D — cheap separate second look** *(consult tier ≥ 1)*: take a quick second
  look at a result through a separate channel before trusting it. At tier-1
  this is an async human-bridge handoff; at tier ≥ 2 it is programmatic. A *second
  look* to catch your own honest mistakes (drift, a missed case) — **not** an
  accountability tribunal, and never a required gate. A separate channel is not
  attested isolation; its verdict is advisory, never acceptance authority.
- **B — parallel fan-out** *(consult tier 3)*: split an investigation across
  separate agents — investigate / refute / cross-domain — and reconcile their
  findings. Blind-adversarial + multi-modal; use when one search angle won't
  surface everything.
- **C — long-experiment polling** *(consult tier 3, or tier ≥ 1 when frontload
  binds a pollable job channel — never at tier-0, where this block is stripped)*:
  submit a long-running job, wait on it, and auto-diagnose and resubmit on
  failure instead of blocking the loop on it. Resubmit only under a **durable job
  identity** (persisted job id / idempotency key) and a **capped retry with
  backoff** — never an unbounded resubmit loop. **The wait itself must cost no
  turns.** A foreground call that sleeps and re-checks is charged the whole
  conversation context on every call, and late in a loop that context is
  hundreds of thousands of tokens per check (measured 2026-09-06: eight bot
  review rounds waited from the foreground cost more than the review itself).
  Wait through the runner's non-blocking primitive — in Claude Code, `Monitor`
  (one event per new comment / job status, `persistent: true` for a
  session-length watch) or Bash `run_in_background` with an `until` loop that
  exits when the condition holds — and do other loop work, or end the
  iteration, until the event arrives. The same rule covers every external wait
  the frontload names (a deploy, a bot review round, a one-off job, a timed
  hold), not only tier-3 experiments.

Only the patterns at or below the compose-detected tier were emitted; the rest
were dropped at compose. Emitted is not verified: a pattern is usable only
while `consult_tier_effective` in `STATE.md` (value + per-channel basis, from
the iteration-0 Run-host channel check) meets its gate — where the effective
tier or a channel's basis falls short, treat that pattern as absent on this
runner. None is required to accept an iteration — the single-agent protocol
remains sufficient.
