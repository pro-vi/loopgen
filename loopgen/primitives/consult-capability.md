# consult-capability (axis primitive)

## Purpose

The frontier-model consult channel available in the host, so the composed
prompt schedules consults only when they exist and degrades gracefully
otherwise (the bodytxt learning). **Environment-detected, not
archetype-varying** — it is a composition *overlay* that changes which sections
Phase 3 emits, and does **not** contribute to the classifier's weighted-Hamming
distance.

## Values

- `tier-0` — no consult channel. Drop scheduled-consult sections; substitute a
  periodic human-look gate; surface the limitation in provenance.
- `tier-1` — human-bridge: the loop emits a consult request as an async handoff
  for the human to relay.
- `tier-2` — single programmatic consult (one MCP tool, one sub-agent, or
  `/second-opinion`).
- `tier-3` — rich consult fabric (Agentify Desktop MCP, PAL, multiple `mcp__*`
  tools, `/agentify`): blind adversarial consults + multi-modal research.

## Detection heuristics

At frontload time, probe the host:

| Found | Tier |
|---|---|
| `mcp__agentify-desktop__*` tools, PAL, or multiple `mcp__*` + `/agentify` | `tier-3` |
| one `mcp__*` tool or sub-agent channel, or `/second-opinion` | `tier-2` |
| only a way to ask the human to relay | `tier-1` |
| nothing | `tier-0` |

This probe reads the **composing host** — the environment `/loopgen` runs in
right now. The README allows pasting the emitted prompt into a different
runner (Claude Code, Codex, …), so the detected tier is **compose-host-bound**,
not a promise about wherever the prompt is finally pasted. Re-running
`/loopgen` after a runner change is the clean path — see Run-host
verification below for the in-loop safety net that catches the gap when it
isn't.

## Archetype defaults

| Archetype | Default |
|---|---|
| frontier | detect; `tier-0` if undetected |
| goal | detect; `tier-0` if undetected |
| story | detect; `tier-0` if undetected |
| greenfield | detect; `tier-0` if undetected |

All archetypes default `tier-0` and degrade gracefully — never silently assume
a consult channel exists.

## Composition rules

- `tier-0` **forces** removal of consult-dependent sections (blind comprehension
  reads, scheduled creative consults, adversarial refute panels) and inserts the
  emittable periodic human-look gate (`{{HUMAN_LOOK_GATE}}` —
  `primitives/human-look-gate.md`); record the degradation in provenance.
- `tier-1` replaces programmatic consults with an async human-bridge handoff.
- `tier ≥ 2` enables the greenfield invariant-8 blind adversarial consult and
  the story Surface-Taste blind read; consult cadence aligns with
  `cadence-shape` boundaries.
- Every consult remains subject to `external-trust-boundary.md`: channel
  detection proves availability, never disclosure authority. Unauthorized or
  unsanitized packets stay local and degrade to the Human-look gate.

## Run-host verification

Because the detected tier is compose-host-bound (see Detection heuristics),
any composed prompt carrying `tier ≥ 1` consult sections (the
`{{SUBAGENT_PATTERNS}}` block, and any archetype's own consult-dependent
sections) must carry an **iteration-0 channel check**: self-gated on durable
state exactly like other bootstrap work (`primitives/runner-contract.md`'s
idempotency corollary — run once, then skipped), verify that each named
consult channel the detected tier promised actually exists on the **run
host**. A missing channel degrades — *that channel only* — to its next-lower
tier's substitute (a missing tier ≥ 2 channel degrades to the tier-1 async
human-bridge handoff if that still exists, else to the tier-0 periodic
human-look gate); the loop never silently proceeds against a phantom tool,
and never spends this check on an interactive prompt
(`runner-contract.md`'s unattended corollary forbids that). Record
`consult_tier_effective` and the per-channel degradation in
`.loop/<loop-id>/STATE.md`, and surface it in that iteration's summary. This
check is the **safety net**, not the primary mechanism — the primary fix for
a runner change is re-deriving with `/loopgen` on the actual run host; a
`tier-0` prompt carries no consult sections, so the check never fires there.

`consult_tier_effective` is a **canonical common STATE key**
(`primitives/context-stack.md`), value + per-channel basis, `n/a` at tier-0.
The self-gate is on the key being **fresh for this host**, not merely present:
the Operational core's health line re-tests it every pass, and the loop
**re-verifies (overwrite-in-place, never trusting the cached value)** whenever
a resume lands on a different runner or a promised channel fails at use time —
a cached effective tier must not outlive its host.

## Placeholders

`{{RUN_HOST_VERIFICATION}}` — substituted with the block below the `---` when
`consult-tier ≥ 1`, **inside the Operational core** (right after the
context-health check, before the halt-cause quick list); stripped
byte-identical at `tier-0`, where the prompt carries no consult sections to
gate (same strip rule as `{{SUBAGENT_PATTERNS}}`, composed-prompt step 8).

`{{CONSULT_TIER}}` — a nested fill inside the emitted block (the detected tier
label, e.g. `tier-2`), present only when the block emits — exactly as in
`subagent-patterns.md`.

---

**Run-host channel check** (`{{CONSULT_TIER}}` was detected on the *composing*
host; this runner may differ): at iteration 0, and again whenever the co-emitted
Context-health check finds `consult_tier_effective` (`STATE.md`) absent or stale
here, verify non-interactively that each promised channel exists. A missing
channel degrades — that channel only — to the next-lower substitute (tier ≥ 2 →
tier-1 human-bridge → tier-0 human-look gate); record value + per-channel basis
in `STATE.md` and surface it in that iteration's summary.
