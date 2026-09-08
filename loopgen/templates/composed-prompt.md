# Composed Prompt — assembly skeleton

This file is **not** an emittable prompt. It is the recipe `/loopgen` Phase 3
follows to assemble `.loop/<loop-id>/PROMPT.md` after the `SKILL.md` Derivation read
contract has been satisfied. It assembles from three inputs:

1. the nearest archetype's **body template** — `templates/bodies/<archetype>-body.md`,
2. the shared **primitive blocks** — `primitives/*.md`,
3. the classified **primitive bundle + divergences** from Phase 2.

This skeleton defines the union section order, the provenance/frontload
contract, and the patch/degrade/strip logic that turns a body template into a
composed prompt.

## Section order (union of all archetype bodies)

1. **Header line** — archetype-specific ("You are running …").
2. **Provenance preamble** — ALWAYS via `{{PROVENANCE}}` (format below).
3. **Motive** — ALWAYS.
3a. **Operational core** — ALWAYS. A compact rehydration block right after
   Motive (~50 lines): a one-line runtime reminder (the context window is a
   lossy cache; the files are memory; the rehydration cadence follows
   `context_mode_effective`), the **Context budget** table
   (file → tier → cap → access command → human watch command), the
   **context-health check** (the bounded step-0 audit from
   `primitives/context-stack.md` — caps, tail parse, evidence pointers resolve,
   index/section agreement, consolidation due), the halt-cause
   quick list, and the iteration-protocol skeleton. Its purpose is that a
   post-compaction rehydration read is a bounded `sed -n '1,80p'
   .loop/<loop-id>/PROMPT.md`, not a two-chunk whole-file read — and that the
   pass most likely to violate the read discipline (the half-rehydrated one)
   meets the audit that catches it inside its first 80 lines. Every body
   carries the section inline, authored from its own iteration protocol + the
   context-stack budget (`primitives/context-stack.md`); the shared lines are
   verifier-pinned byte-identical across bodies, and
   `tools/verify_loopgen_contracts.py` asserts exact-once presence and the
   first-80 bound in every render. The composer fills its placeholders —
   including the one gated slot, `{{RUN_HOST_VERIFICATION}}` (consult
   tier ≥ 1, `primitives/consult-capability.md`; stripped byte-identical at
   `tier-0`) — and never gates, drops, or re-synthesizes the section itself.
4. **Runner contract** — ALWAYS (`primitives/runner-contract.md`).
5. **Judgment default** — ALWAYS (`primitives/judgment-default.md`); in
   `greenfield` it is carried by invariant 7 instead, so it is not emitted twice.
5a. **External trust boundary** — ALWAYS
   (`primitives/external-trust-boundary.md`); capability detection never implies
   disclosure, installation, or execution authority.
6. **Frontload preamble** — ALWAYS via `{{FRONTLOAD_PREAMBLE}}`
   (`primitives/frontload-audit.md` output).
6a. **Pressure surface** — ALWAYS via `{{PRESSURE_SURFACE}}`
   (`primitives/pressure.md`). Emitted right after the frontload preamble — the
   pinned pressure HUD is read before the body — in **every** composed prompt
   (the ≥1-object gate is removed; seeded rows are optional). The block carries
   the row schema, the re-read contract, the mode law, and the mandatory
   promotion triggers.
6b. **Subagent patterns** — CONDITIONAL via `{{SUBAGENT_PATTERNS}}`
   (`primitives/subagent-patterns.md`). Emitted after the pressure surface — an
   available *capability* read before the body — but **only when
   `consult-tier ≥ 1`**, filtered to the patterns that tier meets; at `tier-0` it
   is stripped, leaving the prompt byte-identical. Carried by all four bodies.
6c. **Human-look gate** — ALWAYS via `{{HUMAN_LOOK_GATE}}`
   (`primitives/human-look-gate.md`): the consult fallback, emitted at
   **every** tier because a consulted prompt may lawfully downgrade to
   effective tier-0 mid-run (the Run-host channel check degrades per
   channel, ultimately to this gate) — dormant while live channels cover the
   need, live wherever `consult_tier_effective` resolves a need to tier-0.
   Carried by all four bodies, immediately after the subagent slot.
7. **Archetype body** — the nearest archetype's body, placeholders filled.
   Conditional sub-sections by archetype:
   - `frontier`: Frontier vector · Core law · Homeostasis (5 axes) ·
     Frontier-vector adequacy · Evaluator
     maturity · Reward channels · Same-family admissibility · Frontier anchor.
   - `goal`: Oracle principles · Terminal contract · Goal version · Acceptance
     inventory · Verifier discipline · Channels · Dependency topology ·
     Oracle-drift guard.
   - `story`: Core objects · Status model · Lane/surface · Storyboard ·
     Mechanical run contract · Bootstrap · (Surface Taste Lane — conditional).
   - `greenfield`: 11 invariants · Capability surface · Phase gates.
8. **Signal hierarchy** — `primitives/evidence-tier.md`. Carried by the
   `frontier` (inline) / `story` / `greenfield` (via `{{INCLUDE}}`) bodies;
   **not** `goal` (which relies on
   oracle principles + the acceptance inventory as its evidence surface). Do
   not add a standalone Signal-hierarchy section to a `goal` prompt — `goal`
   relies on oracle principles + the acceptance inventory as its evidence
   surface, so the section is wrong for a finite checklist, not part of goal's
   contract.
9. **Iteration protocol** — archetype body.
10. **Rules** — archetype body (scope manifest, closure discipline FIXED≠CLOSED,
    status-theater prohibition, forbidden shortcuts; `frontier` adds same-family
    admissibility + frontier anchor; `goal` adds the oracle-drift guard).
11. **Halt conditions** — archetype body + **Halt-cause classifier** ALWAYS
    (`primitives/halt-cause-classifier.md`, including the archetype's stop
    cause).
12. **Artifacts to maintain** — the canonical files required by the active
    artifact contracts (`artifact-shape`, divergent primitive add-ons, overlays),
    each tagged with its tier, plus the **Context budget** — ALWAYS, carried by
    the `{{INCLUDE primitives/context-stack.md}}` block every body places here
    (tier table, STATE/JOURNAL/DERIVATION schema, and the budget assertion) and
    the `{{INCLUDE primitives/queue-as-second-artifact.md}}` queue-growth block.
13. **Overlays** — benchmark-frontier (`frontier` only when frontload binds a
    benchmark/eval/harness object); review-closure (`frontier` closure mode);
    Surface Taste Lane (`story` taste lane).

**The body template is authoritative for which sections appear.** This union
list is the *superset* across archetypes; a section appears in a composed prompt
only if that archetype's body carries it. A shared block already inlined in a
body is **not** re-emitted from its primitive file (no double-emission), and the
assembler is **additive-minimal**: it never adds a section the archetype's body
lacks except the minimal cross-archetype additions — provenance, frontload,
canonical artifact/state references, and the shared frontier pressure-accounting
block.

## Provenance preamble (ALWAYS — emit with values filled)

```md
> **Loop provenance — composed by `/loopgen`.**
> Archetype: `<nearest>`  ·  Divergences: `<axis: value (source); …>` or `none`.
> Overlays: `<benchmark-frontier; …>` or `none`.
> Consult-capability: `tier-N` (`<channel, or "none — human-look gate substituted">`).
> Evaluator tier: `<T0–T6, or n/a>`.
> Frontload — resolved: [`…`]; defaulted: [`…`]; open gaps: [`…`].
> Primitive sources: `<files whose values diverged from the archetype defaults>`.
> Re-derive (do not hand-edit) when intent, sources, or environment change.
```

Red-flag rule: if any emitted section reads "the archetype" without the
provenance preamble naming which primitive values composed it, the composition
is invisible — the preamble MUST enumerate every divergence axis + its source.

## Assembly procedure (Phase 3 follows this)

0. **Verify read set.** Confirm `derivation_read_set` in the write-once
   `.loop/<loop-id>/DERIVATION.md` will record the base, archetype/body,
   divergent-primitive, and active-overlay reads `SKILL.md`'s Derivation
   read contract requires. Missing reads are derivation gaps, not silent
   defaults.
1. **Load** `templates/bodies/<nearest>-body.md`.
2. **Resolve includes.** For each `{{INCLUDE primitives/X.md}}` marker, inline
   the block that follows the `---` spec separator in that primitive file. Every
   body now carries `{{INCLUDE primitives/context-stack.md}}` (the memory model +
   STATE/JOURNAL/DERIVATION schema + context budget) and
   `{{INCLUDE primitives/queue-as-second-artifact.md}}` (queue growth discipline)
   in its Artifacts-to-maintain section; both resolve here.
   When resolving `context-stack.md`, the composer **may** sharpen the
   Consolidation round's substrate-audit wording with adjacent conceptual
   lenses discovered in the host repo — a meta/reflection, substrate-audit,
   contract/invariant-check, or environment-parity skill or doc — borrowed as
   *concepts only*, never as a required dependency and never by naming a
   private/custom skill in the emitted text: the emitted loop must stand
   alone on any runner.
3. **Fill placeholders** from the frontload audit + primitive bundle, including
   `{{PROVENANCE}}` and `{{FRONTLOAD_PREAMBLE}}`. For frontier,
   `{{FRONTIER_REOPEN_POLICY}}` fills from `effective_halt_shape`
   (`primitives/halt-shape.md` guarded closed-corpus resolution): the
   equilibrium variant by default and in every pass-through case, the terminal
   variant when the guard resolved (or the user requested) terminal. Both
   variants are extracted by heading from
   `templates/bodies/frontier-reopen-policy.md`, never re-authored inline.
4. **Verify the Operational core (ALWAYS); synthesize nothing.** Every body
   carries `## Operational core` right after Motive (union order 3a) — the
   runtime reminder, the Context budget table, the context-health check, the
   halt-cause quick list, and the iteration-protocol skeleton. The composer
   does not author it: verify the section survived composition exactly once
   and sits entirely within the first 80 lines of the emitted prompt, so
   post-compaction rehydration is a bounded `sed -n '1,80p'
   .loop/<loop-id>/PROMPT.md`. Beyond this one ALWAYS section, do not prepend
   extra sections: provenance and frontload live only at their explicit body
   placeholders, so every archetype keeps one stable section order.
5. **Apply divergence patches.** For every axis where the bundle diverges from
   the archetype default, replace the archetype's default section with the
   diverging value's section and name it in provenance:
   - `target-shape` → swap the target/framing block and apply any target-level
     file/state add-ons from `SKILL.md` Artifact + state contracts (notably
     metric/trace add-ons for `frontier-expanding`).
   - `cadence-shape` → swap the checkpoint/cadence block (e.g. chapter cadence
     into a frontier body).
   - `convergence-shape` → swap the stop-signal block (e.g. capstone-plus-closer).
   - `halt-shape` → swap the reopen-policy block. For frontier this is the
     `{{FRONTIER_REOPEN_POLICY}}` selection from `effective_halt_shape` (step
     3; variants in `templates/bodies/frontier-reopen-policy.md`); for other
     archetypes, swap the body's reopen block (e.g. checkpoint-with-reopen).
     A compiler-derived requested→effective divergence is named in provenance
     with both values.
   - `artifact-shape` → add the divergent queue artifact contract to the nearest
     archetype's canonical files; forbidden divergences route away instead.
   Patches are additive/substitutive; they must not perturb untouched sections.
6. **Apply consult degradation** (`primitives/consult-capability.md`):
   - `tier-0` → remove every consult-dependent section (blind comprehension
     reads, scheduled creative consults, adversarial refute panels) and insert
     a periodic human-look gate; record the degradation in provenance.
   - `tier-1` → replace programmatic consults with an async human-bridge handoff.
   - `tier-2`/`tier-3` → keep the consult sections (tier-3 enables blind
     adversarial multi-tool consults).
   - `tier ≥ 1` (any of the three cases above) → also substitute
     `{{RUN_HOST_VERIFICATION}}` (the block below the `---` in
     `primitives/consult-capability.md`) inside the Operational core, so a
     run started on a different runner than the one `/loopgen` composed on
     still gates its consult channels at iteration 0 — and re-verifies on any
     later runner change — instead of scheduling consults against tools that
     don't exist there. At `tier-0` the placeholder strips byte-identical
     (step 8).
7. **Apply benchmark-frontier overlay** (`primitives/benchmark-frontier.md`):
   - Only for nearest archetype `frontier`.
   - Only when frontload resolved a concrete benchmark/eval/harness object,
     evaluation unit, and durable evidence location.
   - Replace `{{BENCHMARK_FRONTIER_MODE}}` with the "Benchmark Frontier Mode"
     block from the primitive, resolving any include markers carried by that
     block before stripping dead sections.
   - Otherwise strip `{{BENCHMARK_FRONTIER_MODE}}` entirely. Pure frontier keeps
     pressure accounting and does not inherit benchmark artifact roles.
   - Record `overlay: benchmark-frontier` in provenance when active. The
     weighted-Hamming distance table remains unchanged.
   - **When the bound evaluator is trusted-or-mutated** (an LLM judge, a
     generated/minted answer key, or eval-set evolution), seed the
     `### Oracle-integrity pressure` rows (`primitives/benchmark-frontier.md`) into
     `.loop/<loop-id>/STATE.md` `pressure_objects`. The pressure surface itself is
     always emitted (step 7a); seeding these rows populates the in-force set so the
     HUD opens with the oracle-integrity slopes already active. They are a strict
     subset of overlay-active-and-oracle-trusted cases, so they never appear
     without the overlay block that explains them; a pure archetype — or a
     benchmark overlay over a deterministic non-LLM, non-minted oracle — seeds none
     and simply starts with an empty in-force set. The frontload
     Evaluator-integrity audit (`primitives/frontload-audit.md`) names any unmet
     integrity property as a `derivation-gap` before emit.
7a. **Apply pressure surface** (`primitives/pressure.md`) — ALWAYS:
   - Replace `{{PRESSURE_SURFACE}}` with the block below the `---` in
     `primitives/pressure.md` in **every** composed prompt (no gate), resolving
     any include markers it carries. Seeded or mined rows are optional — the
     compact HUD block is emitted whether or not `count(pressure_objects) ≥ 1`,
     because its mandatory promotion triggers are what keep the surface from going
     dead (the measured dead-`PRESSURE.md` failure — ADR 0004).
   - The active rows live in `.loop/<loop-id>/PRESSURE.md` (re-read each pass),
     not inlined into the prompt; the emitted block carries the row schema, the
     re-read contract, the mode law, the mandatory promotion triggers, and the
     backpressure instruction.
7b. **Apply subagent patterns** (`primitives/subagent-patterns.md`):
   - If `consult-tier ≥ 1`, replace `{{SUBAGENT_PATTERNS}}` with the block below
     the `---` in `primitives/subagent-patterns.md`, but **emit only the B/C/D
     bullets the detected tier meets — drop the rest at substitution time** (a
     content filter the composer applies as it fills the placeholder, *not* step
     8's whole-placeholder strip): **D** at tier ≥ 1; **B** at tier 3; **C** at
     tier 3, or at tier ≥ 1 when frontload binds a pollable job channel. E.g. a
     tier-1 host with no pollable channel emits the intro + **D only** (B and C
     are omitted, never inlined); tier-3 emits D + B + C. Fill `{{CONSULT_TIER}}`
     with the full tier label (e.g. `tier-2`).
   - Otherwise (`tier-0`) strip `{{SUBAGENT_PATTERNS}}` entirely (step 8
     removes it); the loop runs single-agent via pattern A — byte-identical,
     gated exactly like `{{BENCHMARK_FRONTIER_MODE}}` (the pressure surface,
     by contrast, is always-on — step 7a).
   - `{{HUMAN_LOOK_GATE}}` is always filled with the block below the `---` in
     `primitives/human-look-gate.md`, at **every** tier: the fallback must
     already be in the prompt when a runtime downgrade lands on it. Its
     liveness gate is the runtime condition inside the block, never a compose
     strip.
   - Pattern A (single-agent iteration) is the existing protocol; it is never
     part of this block, and nothing here is a required gate to accept an
     iteration.
8. **Strip dead sections.** Remove any section whose `{{placeholder}}` was not
   substituted. If any `{{…}}` survives, WARN in the emit summary — the emitted
   prompt must contain no dead sections. When a stripped placeholder sat on its
   own line between blank lines, **collapse the surrounding blanks to a single
   newline**, so a gated placeholder (`{{SUBAGENT_PATTERNS}}`,
   `{{RUN_HOST_VERIFICATION}}`, `{{BENCHMARK_FRONTIER_MODE}}`) leaves
   byte-identical output whether on or off
   (no double blank line when it is stripped). `{{PRESSURE_SURFACE}}` is now
   always substituted (step 7a) and never stripped, so it no longer participates
   in this collapse.
9. **Verify halt semantics.** The emitted prompt must distinguish invocation
   halt from archetype completion. Shared halt causes (`genuine-escalate`,
   `derivation-gap`, `signal-starvation`, `wrong-loop`) never mean the
   frontier, goal, story, or greenfield artifact is complete by themselves.
   Frontier's `homeostatic-checkpoint` also does not mean completion: a
   frontier objective has no quality pass-line and never completes by being
   good enough. The checkpoint fires only after the full frontier scan reaches
   quiescence — balanced homeostasis, no admissible pressure, and resolved
   vector adequacy with no candidate awaiting a probe or confirmation and no
   newly admitted dimension requiring continuation. The episode then
   either checkpoints-and-reopens (effective `equilibrium`) or terminates on
   declared-workset exhaustion (effective
   `terminal`, `primitives/halt-shape.md`) — episode termination ends the
   execution, not the objective. Only non-frontier archetype-terminal success
   causes may claim completion. If this distinction is absent, patch the
   prompt before emitting.
   Also verify that any non-success shared halt — including a frontier episode
   termination — requires a full search-surface scan first; for frontier this
   includes pressure discovery and vector adequacy, so a single blocked row or
   provisional balance cannot stop the loop while another reversible in-scope
   intervention remains.
10. **Emit** (see `SKILL.md` Artifact + state contracts and Phase 4): common
   files + nearest archetype files + divergent primitive add-ons + active
   overlay files.

## Pressure-surface: always-on (no gate)

The `{{PRESSURE_SURFACE}}` block is emitted in **every** composed prompt — there
is no compose-time gate (ADR 0004 reversed the former ≥1-object gate, whose
measured failure was a dead `PRESSURE.md`). A zero-pressure compose still carries
the pinned HUD and its mandatory promotion triggers, so the surface is live the
moment the loop mints its first row; seeded rows only pre-populate the in-force
set. The gated placeholders are `{{SUBAGENT_PATTERNS}}` and
`{{RUN_HOST_VERIFICATION}}` (both consult-tier ≥ 1) plus
`{{BENCHMARK_FRONTIER_MODE}}`; `{{HUMAN_LOOK_GATE}}` joins the pressure
surface as always-on — the consult fallback must already be in the prompt
when a runtime downgrade lands on it. `{{SUBAGENT_PATTERNS}}` stays the
reference example of a compose-gated block (stripped byte-identical at
`tier-0`, step 8).
