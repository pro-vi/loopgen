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
4. **Runner contract** — ALWAYS (`primitives/runner-contract.md`).
5. **Judgment default** — ALWAYS (`primitives/judgment-default.md`); in
   `greenfield` it is carried by invariant 7 instead, so it is not emitted twice.
6. **Frontload preamble** — ALWAYS via `{{FRONTLOAD_PREAMBLE}}`
   (`primitives/frontload-audit.md` output).
6a. **Pressure surface** — CONDITIONAL via `{{PRESSURE_SURFACE}}`
   (`primitives/pressure.md`). Emitted right after the frontload preamble — the
   weather is read before the body — but **only when ≥1 pressure object exists**
   at compose time; otherwise stripped, leaving the prompt byte-identical.
6b. **Subagent patterns** — CONDITIONAL via `{{SUBAGENT_PATTERNS}}`
   (`primitives/subagent-patterns.md`). Emitted after the pressure surface — an
   available *capability* read before the body — but **only when
   `consult-tier ≥ 1`**, filtered to the patterns that tier meets; at `tier-0` it
   is stripped, leaving the prompt byte-identical. Carried by all four bodies.
7. **Archetype body** — the nearest archetype's body, placeholders filled.
   Conditional sub-sections by archetype:
   - `frontier`: Frontier vector · Core law · Homeostasis (5 axes) · Evaluator
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
    (`primitives/halt-cause-classifier.md`, including the archetype's terminal
    cause).
12. **Artifacts to maintain** — the canonical files required by the active
    artifact contracts (`artifact-shape`, divergent primitive add-ons, overlays).
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

0. **Verify read set.** Confirm `.loop/<loop-id>/STATE.md` will record the base reads,
   nearest archetype/body reads, divergent primitive/source reads, and active
   overlay reads required by `SKILL.md` Derivation read contract. Missing reads
   are derivation gaps, not silent defaults.
1. **Load** `templates/bodies/<nearest>-body.md`.
2. **Resolve includes.** For each `{{INCLUDE primitives/X.md}}` marker, inline
   the block that follows the `---` spec separator in that primitive file.
3. **Fill placeholders** from the frontload audit + primitive bundle, including
   `{{PROVENANCE}}` and `{{FRONTLOAD_PREAMBLE}}`.
4. **Do not prepend extra sections.** Provenance and frontload live only at the
   explicit body placeholders, so every archetype has one stable section order.
5. **Apply divergence patches.** For every axis where the bundle diverges from
   the archetype default, replace the archetype's default section with the
   diverging value's section and name it in provenance:
   - `target-shape` → swap the target/framing block and apply any target-level
     file/state add-ons from `SKILL.md` Artifact + state contracts (notably
     metric/trace add-ons for `frontier-expanding`).
   - `cadence-shape` → swap the checkpoint/cadence block (e.g. chapter cadence
     into a frontier body).
   - `convergence-shape` → swap the stop-signal block (e.g. capstone-plus-closer).
   - `halt-shape` → swap the reopen-policy block (e.g. checkpoint-with-reopen).
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
     `.loop/<loop-id>/STATE.md` `pressure_objects`, so `{{PRESSURE_SURFACE}}` fires via its own
     ≥1-object gate (step 7a). The two gates **nest**: oracle-integrity rows are a
     strict subset of overlay-active-and-oracle-trusted cases, so they never appear
     without the overlay block that explains them, and a pure archetype — or a
     benchmark overlay over a deterministic non-LLM, non-minted oracle — seeds none
     and stays byte-identical. The frontload Evaluator-integrity audit
     (`primitives/frontload-audit.md`) names any unmet integrity property as a
     `derivation-gap` before emit.
7a. **Apply pressure surface** (`primitives/pressure.md`):
   - If `count(pressure_objects) ≥ 1` at compose (the frontload latent-pressure
     mining step or a human seed produced ≥1 row), replace `{{PRESSURE_SURFACE}}`
     with the block below the `---` in `primitives/pressure.md`, resolving any
     include markers it carries.
   - Otherwise strip `{{PRESSURE_SURFACE}}` entirely (step 8 removes it). A pure
     archetype with no seeded or mined pressure stays byte-identical — gated
     exactly like `{{BENCHMARK_FRONTIER_MODE}}`.
   - The active rows live in `.loop/<loop-id>/PRESSURE.md` (re-read each pass), not inlined
     into the prompt; the emitted block carries the re-read contract, the mode
     law, and the backpressure instruction.
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
   - Otherwise (`tier-0`) strip `{{SUBAGENT_PATTERNS}}` entirely (step 8 removes
     it). The loop runs single-agent via pattern A — byte-identical, gated
     exactly like `{{PRESSURE_SURFACE}}`.
   - Pattern A (single-agent iteration) is the existing protocol; it is never
     part of this block, and nothing here is a required gate to accept an
     iteration.
8. **Strip dead sections.** Remove any section whose `{{placeholder}}` was not
   substituted. If any `{{…}}` survives, WARN in the emit summary — the emitted
   prompt must contain no dead sections. When a stripped placeholder sat on its
   own line between blank lines, **collapse the surrounding blanks to a single
   newline**, so the stacked gated placeholders (`{{PRESSURE_SURFACE}}` /
   `{{SUBAGENT_PATTERNS}}`) leave byte-identical output
   in every on/off combination (no double blank line when an inner one is
   stripped).
9. **Verify halt semantics.** The emitted prompt must distinguish invocation
   halt from archetype completion. Shared halt causes (`genuine-escalate`,
   `derivation-gap`, `signal-starvation`, `wrong-loop`) never mean the
   frontier, goal, story, or greenfield artifact is complete by themselves.
   Frontier's `homeostatic-checkpoint` also does not mean completion; frontier
   loops checkpoint and reopen on fresh signal. Only non-frontier
   archetype-terminal success causes may claim completion. If this distinction
   is absent, patch the prompt before emitting.
   Also verify that any non-terminal shared halt requires a full search-surface
   scan first, so a single blocked row cannot stop the loop while another
   reversible in-scope intervention remains.
10. **Emit** (see `SKILL.md` Artifact + state contracts and Phase 4): common
   files + nearest archetype files + divergent primitive add-ons + active
   overlay files.

## Pressure-surface gating

The `{{PRESSURE_SURFACE}}` block is gated on ≥1 compose-time pressure object: a
pure case with no seeded or mined pressure has it stripped (step 8), so a
zero-pressure compose carries no pressure section. A case that intentionally
seeds pressure is not a pure case.
