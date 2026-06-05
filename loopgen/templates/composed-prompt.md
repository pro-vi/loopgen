# Composed Prompt — assembly skeleton

This file is **not** an emittable prompt. It is the recipe `/loopgen` Phase 3
follows to assemble `loop/PROMPT.md` after the `SKILL.md` Derivation read
contract has been satisfied. It assembles from three inputs:

1. the nearest archetype's **body template** — `templates/bodies/<archetype>-body.md`,
2. the shared **primitive blocks** — `primitives/*.md`,
3. the classified **primitive bundle + divergences** from Phase 2.

The body templates are legacy-derived emittable prompts (frontier / goal /
story from the retired loop skills; greenfield reconstructed). This skeleton
defines the union section order, the provenance/frontload contract, and the
patch/degrade/strip logic that turns a body template into a composed prompt.

## Section order (union of all archetype bodies)

1. **Header line** — archetype-specific ("You are running …").
2. **Provenance preamble** — ALWAYS via `{{PROVENANCE}}` (format below). NEW;
   the one section the legacy skills never emitted.
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
   `frontier` / `story` / `greenfield` bodies; **not** `goal` (which relies on
   oracle principles + the acceptance inventory as its evidence surface). Do
   not add a standalone Signal-hierarchy section to a `goal` prompt — the legacy
   goal prompt never had one, and adding it breaks U11.
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
assembler never adds a section the archetype's legacy body lacked except for
the explicit U11 compatibility deltas: provenance, frontload, canonical
artifact/state references, and the shared frontier pressure-accounting block.

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

0. **Verify read set.** Confirm `loop/STATE.md` will record the base reads,
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
7a. **Apply pressure surface** (`primitives/pressure.md`):
   - If `count(pressure_objects) ≥ 1` at compose (the frontload latent-pressure
     mining step or a human seed produced ≥1 row), replace `{{PRESSURE_SURFACE}}`
     with the block below the `---` in `primitives/pressure.md`, resolving any
     include markers it carries.
   - Otherwise strip `{{PRESSURE_SURFACE}}` entirely (step 8 removes it). A pure
     archetype with no seeded or mined pressure stays byte-identical — gated
     exactly like `{{BENCHMARK_FRONTIER_MODE}}`.
   - The active rows live in `loop/PRESSURE.md` (re-read each pass), not inlined
     into the prompt; the emitted block carries the re-read contract, the mode
     law, and the backpressure instruction.
8. **Strip dead sections.** Remove any section whose `{{placeholder}}` was not
   substituted. If any `{{…}}` survives, WARN in the emit summary — the emitted
   prompt must contain no dead sections.
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

## Backward-compatibility invariant (U11 gate)

For a **pure** archetype (no divergences; no conditional overlay active beyond
detected consult degradation), the assembly procedure reproduces the legacy
skill's body except for the accepted compatibility deltas. The U11 probe diffs
composed output against the legacy reference and accepts only: (a) the
provenance preamble, (b) the frontload preamble, (c) canonical artifact/state
contract references, (d) the shared pressure-accounting block for pure frontier
only, and (e) cosmetic whitespace/ordering. Any other load-bearing structural
difference on a pure case fails the probe.

The `{{PRESSURE_SURFACE}}` block is gated on ≥1 compose-time pressure object: a
pure case with no seeded or mined pressure has it stripped, so it is **absent**
(not a delta) and byte-identity holds. A case that intentionally seeds pressure
is not a pure case and is tested separately.
