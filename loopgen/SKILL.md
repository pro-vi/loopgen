---
name: loopgen
description: "Compose a repo-specific, /goal-ready loop prompt from a primitive vocabulary — loopgen writes the weather, not just the target. Classifies a task to its nearest archetype (frontier / goal / story / greenfield), composes the prompt from primitive values — defaulting to the archetype, diverging where the task demands — and emits with provenance. Also diagnoses a drifting loop. Triggers: '/loopgen', 'derive a loop for X', 'make me an overnight loop', 'close the findings in X', 'fix the bugs by morning', 'push a benchmark with a loop', 'walk the storyboard', 'build out an idea from zero'."
---

# Loopgen

`/loopgen` derives a repo-specific, **runner-agnostic** loop prompt with a
canonical `/goal` kick-off. The emitted `loop/PROMPT.md` carries the complete
iteration contract; the operator-facing invocation is always a stable pointer
to that file. It is a **hybrid dispatcher + compositional generator**: it runs a
shared pre-flight audit, classifies the task to its nearest *archetype* by
extracting primitive values, composes the prompt by combining those values
(defaulting to the nearest archetype's presets and diverging where the task
demands), and emits with a provenance preamble.

It replaces the four legacy loop skills, whose irreducible cores now live as
archetype reference documents (`archetypes/*.md`) and whose shared
infrastructure is the primitive vocabulary (`primitives/*.md`). Output is
backward-compatible under the U11 probe: a pure archetype reproduces the legacy
skill's prompt plus the accepted contract deltas (provenance, frontload,
canonical artifact/state references, and frontier pressure accounting where
applicable).

Invoke **once per run** to author or revise a prompt; the loop's per-iteration
playbook lives in the composed `loop/PROMPT.md`, not here. Invoke in
**Diagnostic mode** to retrofit a drifting loop.

## When to invoke

- "derive a loop / write me a loop for X"
- "make this an overnight / autonomous loop"
- any per-archetype loop intent: closing a finite checklist, pushing a
  benchmark, walking a storyboard, or building an idea from zero
- a task that mixes archetypes (e.g. frontier evidence discipline + story
  chapter cadence) — loopgen is the only skill that composes hybrids

## Do NOT invoke when

- the user wants a one-off plan, not an iterative loop → `/architect`
- the user wants to *run* a loop now → that is the runner's job (`/goal`);
  loopgen only generates the prompt
- pure debugging → a debugging tool, not a loop

## The primitive vocabulary (single source of truth)

Phase 2 classifies against this matrix. It is locked; extend it only when ≥2
archetypes meaningfully differ on a new axis (the vocabulary-axis test).

**Axes that vary by archetype** (the five the classifier weights):

| Axis | Values | frontier | goal | story | greenfield | wt |
|---|---|---|---|---|---|---|
| `target-shape` | finite-criteria · frontier-expanding · promise-discovery · discovery-reframing | frontier-expanding | finite-criteria | promise-discovery | discovery-reframing | 3 |
| `halt-shape` | terminal · equilibrium · checkpoint-with-reopen · manual-gated | equilibrium | terminal | checkpoint-with-reopen | manual-gated | 3 |
| `artifact-shape` | prompt-only · acceptance-inventory · storyboard · rubric+intent · findings-ledger | findings-ledger | acceptance-inventory | storyboard | rubric+intent | 3 |
| `convergence-shape` | criteria-completion · homeostatic-checkpoint · capstone-plus-closer · stone-reframe · iteration-cap | homeostatic-checkpoint | criteria-completion | capstone-plus-closer | stone-reframe | 2 |
| `cadence-shape` | sync · checkpoint-gated · chapter · deferred-fire-and-forget | checkpoint-gated | sync | chapter | checkpoint-gated | 1 |

Max weighted-Hamming distance is **12** (3+3+3+2+1). `consult-capability`
(tier-0..3) and `benchmark-frontier` are **environment/frontload-detected, not
archetype-varying** — they are composition *overlays* that change which
sections Phase 3 emits, and do **not** participate in classification distance.
Consult tiers are defined below; benchmark-frontier is defined in
`primitives/benchmark-frontier.md`.

**Shared primitives** (constant across archetypes; in every composed prompt):
`runner-contract`, `judgment-default`, `evidence-tier`, `frontload-audit`,
`halt-cause-classifier`, `diagnostic-pattern`, `evaluator-maturity` (T0–T6),
`queue-as-second-artifact`, `pressure`.
`pressure` is universal, but its `{{PRESSURE_SURFACE}}` block emits only when ≥1
pressure object exists at compose time (gated; byte-identical when empty).
`pressure-accounting` is the `frontier` projection of `pressure`, not a separate
archetype-varying axis.

**Forbidden divergences** (identity-breaking; never compose — route away):

- `goal` cannot take `target-shape` `frontier-expanding`/`discovery-reframing`,
  nor `halt-shape` `manual-gated`.
- `frontier`/`greenfield` cannot take `target-shape` `finite-criteria`.

**Contradictions** (classification error → AskUserQuestion, never silent
default): `target: finite-criteria` with `halt: equilibrium`/`manual-gated`, or
with `convergence: homeostatic-checkpoint`.

**`consult-capability` tiers** (detected at frontload time — probe for
`mcp__agentify-desktop__*`, other `mcp__*` tools, `/second-opinion`,
`/agentify`, PAL): `tier-0` none → drop scheduled-consult sections + substitute
a human-look gate; `tier-1` human-bridge handoff; `tier-2` single programmatic
consult; `tier-3` rich fabric (blind adversarial + multi-modal). All archetypes
default `tier-0` if undetected — never assume a channel exists.

## Derivation read contract

Do not compose from memory. Every authoring run reads a bounded, provenance-
relevant set of files and records that list in `loop/STATE.md`
`derivation_read_set`.

**Always read before classification and composition:**

- `templates/composed-prompt.md`
- `primitives/target-shape.md`
- `primitives/halt-shape.md`
- `primitives/artifact-shape.md`
- `primitives/convergence-shape.md`
- `primitives/cadence-shape.md`
- `primitives/consult-capability.md`
- `primitives/frontload-audit.md`
- `primitives/runner-contract.md`
- `primitives/judgment-default.md`
- `primitives/evidence-tier.md`
- `primitives/halt-cause-classifier.md`
- `primitives/queue-as-second-artifact.md`
- `primitives/pressure.md`

`primitives/pressure.md` is read every run because the frontload latent-pressure
mining step is universal and needs its modes + object schema. It shapes the
emitted prompt (and appears in the provenance `Primitive sources:` line) only
when mining or a seed produces ≥1 pressure object, so a zero-pressure pure case
stays byte-identical even though the file is in the read set.

**After classification, also read:**

- `archetypes/<nearest>.md`
- `templates/bodies/<nearest>-body.md`
- every `primitives/<axis>.md` whose value diverged from the nearest archetype
  default
- every `archetypes/<source>.md` that supplied a divergent value by archetype
  default
- every reference named by the nearest archetype's `## Extras`
- every primitive/reference named by active overlays

For frontier-shaped tasks, read `primitives/evaluator-maturity.md` and
`primitives/pressure-accounting.md`. When benchmark language appears or the
benchmark-frontier overlay activates, read `primitives/benchmark-frontier.md`,
`primitives/eval-ladder.md`, `references/benchmark-frontier-artifacts.md`, and
`references/benchmark-frontier-example.md`.

The provenance preamble's `Primitive sources:` line is the human-readable slice
of this read set: it names the files whose values shaped or diverged from the
nearest archetype. A required read that cannot be completed is a derivation gap,
not a reason to guess.

## Phase 1 — Frontload audit

Run the universal pre-flight from `primitives/frontload-audit.md`, plus the
nearest archetype's extra items (named in each `archetypes/*.md`). For every
item: **resolve** (AskUserQuestion if the host has it, else print prominently),
**default + Alignment Review**, or **escalate-mark** (irreversible only).

Always assess `consult-capability` here (the bodytxt-learned move): detect the
tier and record it; it changes which sections Phase 3 emits.

For frontier-shaped tasks, also assess `benchmark-frontier`: it activates only
when frontload binds a concrete benchmark, evaluation, or harness object with an
evaluation unit and evidence location. Benchmark/eval/harness language without
a bound object is a derivation gap, not a silent generic frontier default.

Record results under `loop/STATE.md` `frontload:` and produce the frontload
preamble (resolved / defaulted / open gaps). Anything unresolved, undefaulted,
and unmarked is a **derivation gap** — name it explicitly; the emitted prompt's
halt-cause classifier flags `derivation-gap` halts so the next pass closes it.

## Phase 2 — Primitive extraction + archetype classification

1. **Extract** a value for each varying axis from the task description, using
   the detection heuristics in each `primitives/<axis>.md`.
2. **Check contradictions** first. If the bundle hits a contradiction pair,
   HALT classification and fire AskUserQuestion with the conflicting axes — no
   silent default.
3. **Classify.** Compute weighted-Hamming distance from the bundle to each
   archetype's defaults (weights above). The nearest archetype is the shorthand
   reference. **Be decisive — pick one archetype; do not present a menu.**
4. **Name divergences.** Every axis whose value differs from the nearest
   archetype's default is a divergence; record `axis → value (source-archetype
   or "task")`.
5. **Ties = genuine hybrid.** A genuine hybrid is *equidistant* (or near-equal,
   margin ≤1) between two archetypes — e.g. distance 5 to one and 5–6 to another.
   There, pick the higher-weight-match archetype as the shorthand and name the
   other's contributions as divergences; if still ambiguous, fire AskUserQuestion
   with the two candidates. Do **not** treat a low-distance task as a hybrid: a
   task at distance 3 from story and 9 from everything else (e.g. bodytxt — a
   story loop with a `frontier-expanding` target) is **story with one
   divergence**, not a frontier+story tie. No equidistant hybrid has yet been
   observed in a real run; until one is, a large margin means snap decisively to
   the nearest. (These distances are exact arithmetic over the matrix above —
   the eyeball that once called bodytxt a "hybrid" is the failure mode computing
   them guards against.)

Emit a structured classification: `{archetype, runnable, target-status,
divergences[], overlays[], consult-tier, evaluator-tier}`, where `target-status`
is `defined` or `UNDEFINED → derivation-gap`, and `runnable` is `false` whenever
a slot the loop needs to fire (dimension, stop rule, scope, evidence signal) is
unbound. A
clean archetype match — even an exact one — is a *candidate*, not a launchable
loop: the *preintent* read is that "improve the codebase" classifies as `frontier`
yet binds no dimension or stop rule, so it emits `{archetype: frontier, runnable:
false}` with those as derivation gaps (see `primitives/target-shape.md`). No
silent defaults — every divergence, every unbound slot, and an undefined target
is visible.

## Phase 3 — Compose

Follow `templates/composed-prompt.md`. In short: load the nearest archetype's
body (`templates/bodies/<archetype>-body.md`), resolve `{{INCLUDE}}` markers
from `primitives/*.md`, fill placeholders from Phase 1 including the
`{{PROVENANCE}}` and `{{FRONTLOAD_PREAMBLE}}` slots, apply divergence patches,
apply consult degradation, strip any section with an unsubstituted placeholder
(warn if any survive), verify halt semantics, and emit.

The provenance preamble MUST enumerate the archetype, every divergence + its
source, overlays, the consult tier, and the frontload gaps. If a section says "the
archetype" without provenance naming the composing values, the composition is
invisible — fix it.

The emitted prompt MUST also distinguish invocation halt from archetype
completion. Shared halt causes (`genuine-escalate`, `derivation-gap`,
`signal-starvation`, `wrong-loop`) are not completion claims by themselves.
Frontier's `homeostatic-checkpoint` also does not mean completion; frontier
loops checkpoint and reopen on fresh signal. Only non-frontier archetype
success causes may say the loop is complete. If a prompt can halt on a shared
cause, it must tell the runner to report the frontier/queue/story as open or
checkpointed and list the unresolved artifact rows or halt scan.
It must also require a full search-surface scan before any non-terminal halt,
so one blocked row cannot stop a frontier/story/greenfield/goal loop while
another in-scope evaluator, observability, specification, verifier, or queue
repair move remains.

## Artifact + state contracts

Every file-backed emission writes the same canonical anchors. Repo-native paths
may be recorded as aliases inside `loop/STATE.md`, but they do **not** replace
the canonical files.

**Common files, every archetype:**

- `loop/PROMPT.md` — the complete re-entrant iteration prompt.
- `loop/STATE.md` — the durable resume state.
- `loop/PRESSURE.md` — the active pressure field, rendered from `loop/STATE.md`
  `pressure_objects` (the source of truth) and re-read each iteration to shape
  how criteria are interpreted; seeded empty until a pressure exists. It is the
  canonical pressure surface for `goal` / `story` / `greenfield`. `frontier`
  already renders its pressure through the findings ledger + `pressure_status`
  (the projection, `primitives/pressure-accounting.md`), so for `frontier`
  `loop/PRESSURE.md` aliases that surface rather than inventing a second one —
  consistent with the frontier Storage rule (findings ledger / `loop/STATE.md`).

**Archetype files:**

| Archetype | Required files |
|---|---|
| `goal` | `loop/ACCEPTANCE.md`, `loop/VERIFY.md` |
| `story` | `docs/storyboard.md` |
| `frontier` | `loop/FINDINGS.md`, `loop/TRACES.md`, `loop/METRICS.md` |
| `greenfield` | `loop/RUBRIC.md`, `loop/INTENT.md`, `loop/README.md` |

`loop/VERIFY.md` may start as an empty "not yet run" final-verify transcript;
it still exists so every goal loop has the same resume surface. `loop/TRACES.md`
and `loop/METRICS.md` are indexes: they may point to repo-native trace
directories, performance reports, benchmark outputs, or generated artifacts.

**Required `loop/STATE.md` keys, every archetype:**

- `archetype`, `identity`, `primitive_bundle`, `divergences`, `overlays`
- `consult_tier`, `evaluator_tier`
- `derivation_read_set`
- `frontload: {resolved, defaulted, open_gaps}`
- `artifacts: {canonical, repo_aliases}`
- `iteration`, `phase`, `current_artifact`, `last_action`, `next_action`
- `halt_cause`, `halt_scan`
- `pressure_objects`, `pressure_ledger`

**Archetype-specific `loop/STATE.md` keys:**

- `goal` — `goal_version`, `current_criterion`, `stuck_counters`,
  `final_verify`, `oracle_change_notes`.
- `story` — `storyboard_path`, `lane`, `surface_class`, `current_story`,
  `last_surface`, `last_story_family`, `same_family_count`, `fixture_mode`,
  `evidence_manifest`, `remaining_findings_classified`.
- `frontier` — `frontier_vector`, `current_anchor`, `reward_channels`,
  `pressure_status`, `pressure_debt`, `checkpoint_reason`, `next_pressure`,
  `trace_locations`, `metric_locations`, `guardrails`.
- `greenfield` — `score_lock`, `phase_gates`, `rubric_version`,
  `score_comparable_with`, `target_hypotheses`, `current_stone_axis`,
  `capability_list`, `user_halt_owner`.

`frontier`'s `pressure_status` / `pressure_debt` / `checkpoint_reason` /
`next_pressure` are the frontier projection of the common `pressure_objects` /
`pressure_ledger` — the same field, rendered as a checkpoint contract.

**Hybrid merge rule.** A hybrid is a union over **active contracts**, not a
blind union over all contributing archetypes:

1. Emit the nearest archetype's complete file + state contract.
2. Add every file and state key required by each divergent primitive value.
3. Add every file and state key required by each active overlay.
4. Never drop the nearest archetype's state obligations unless the divergence is
   forbidden and the task is routed away instead of composed.

Important add-ons:

- `target-shape: frontier-expanding` adds `loop/TRACES.md`,
  `loop/METRICS.md`, `frontier_vector`, `trace_locations`,
  `metric_locations`, and `guardrails` when those are not already present.
- `artifact-shape: findings-ledger` adds the full frontier artifact set:
  `loop/FINDINGS.md`, `loop/TRACES.md`, and `loop/METRICS.md`.
- `artifact-shape: acceptance-inventory` adds `loop/ACCEPTANCE.md` and
  `loop/VERIFY.md`.
- `artifact-shape: storyboard` adds `docs/storyboard.md`.
- `artifact-shape: rubric+intent` adds `loop/RUBRIC.md`, `loop/INTENT.md`, and
  `loop/README.md`.
- `overlay: benchmark-frontier` adds `loop/DOMAIN_SPEC.md`,
  `loop/BENCHMARK.md`, `loop/CANDIDATES.jsonl`, `loop/FRONTIER.json`, and
  `loop/traces/`.

## Phase 4 — Emit + surface decision

**Default surface: file.** Write the full Artifact + state contract: common
files, nearest archetype files, divergent primitive add-ons, and active overlay
files. Seed canonical artifacts even when they only point at repo-native aliases.

For `frontier` with `overlay: benchmark-frontier`, emit or resolve the semantic
artifact roles from `primitives/benchmark-frontier.md`: `DOMAIN_SPEC`,
`BENCHMARK`, `CANDIDATES`, `FRONTIER`, and `traces`. These roles are conditional
on the overlay and are not required for pure frontier.

Emit chat-only only when the user explicitly asks for a dry run, sketch, or
chat-only derivation. Otherwise write the canonical files above; deterministic
artifact emission is the default.

### The kick-off (runner invocation)

After emitting, give the operator the **pointer kick-off** — the line they paste
into `/goal` to start the loop. It is a **bare pointer**: the fixed runner verb,
the path to the prompt, and a one-phrase identity. Nothing else.

> `/goal read loop/PROMPT.md and execute as <one-phrase loop identity>.`
>
> e.g. `/goal read loop/PROMPT.md and execute as the hybrid-pareto benchmarking loop.`

`/goal` re-sends the *same* prompt every iteration (see
`primitives/runner-contract.md`), so the kick-off must be **iteration-agnostic**
and carry **no instruction content** — every rule (which file is the goal, where
`STATE.md` is, the iteration protocol, the bootstrap gate) lives in
`loop/PROMPT.md`, the single source. If you are tempted to add a clause to the
kick-off ("…and start with…", "…loop/STATE.md tells you where you are"), put it
in `PROMPT.md` instead. NEVER bake first-iteration language into the kick-off
("begin with the bootstrap", "first, instantiate…") — on iteration 2 it
mis-fires, re-running one-time setup.

This only works if `PROMPT.md` is **re-entrant**: all bootstrap /
inventory-instantiation / one-time work must be **self-gated on durable state** in
`loop/STATE.md` (`iteration: 0`, "no inventory / storyboard / ledger yet"), run
once then skipped. The canonical self-gate shape is story-body's `## Bootstrap
mode` (enter when the artifact doesn't exist; exit when the first unit can
advance); every archetype with iteration-0 setup (goal-inventory,
greenfield-preloop, frontier-ledger-seed) needs the same gate — verify the
composed `PROMPT.md` has it before emitting, or the pointer kick-off is unsafe.

Then present the menu:

- **Approve** — keep the emitted files.
- **Modify** — the user overrides one or more primitive values; rerun Phase 2
  classification and Phase 3 composition with the overrides, then re-emit.
- **Abort** — discard.

Return a one-paragraph rationale: archetype + divergences, consult tier,
evaluator tier (if applicable), and any open frontload gaps.

## Diagnostic mode

Invoked to retrofit a drifting loop, not author a new one. Follow
`primitives/diagnostic-pattern.md`: read the current `loop/PROMPT.md` +
`loop/STATE.md` + the queue artifact + ledger; **classify which archetype the
loop currently is** (it may have drifted from its declared archetype — flag the
drift first); score against that archetype's failure modes (`archetypes/*.md`);
emit a **minimal** `loop/PROMPT.md` mutation (inline edit, never a rewrite);
write a ⚠️ block to `loop/STATE.md`.

## Anti-patterns

- **Forcing a hybrid into one archetype.** When the task is genuinely mixed,
  do not snap to the nearest and drop the rest — name the divergences.
- **Pretending consult capability exists at tier-0.** Degrade gracefully;
  substitute a human-look gate; record it in provenance.
- **Silent defaults on a contradiction.** Contradictory primitives are a
  classification error → ask the user.
- **Primitive-vocabulary inflation.** Add an axis only when ≥2 archetypes
  meaningfully differ on it.
- **Invisible composition.** Every divergence axis must appear in the
  provenance preamble with its source.
- **Dead sections.** Strip any section whose placeholder was not substituted.

## Composability

| Direction | Skill | Relationship |
|---|---|---|
| upstream | `/architect` | conceptual parent; an architect blueprint is a first-class `goal` criteria source |
| upstream | `/oracle-design` | complementary for the `goal` archetype's verifier matrix |
| downstream | `/goal` | canonical runner that executes the emitted `loop/PROMPT.md`; `/goal` is the runner, not the `goal` archetype |
| downstream | `/provision`, `/route` | may still name the removed loop commands; repoint to `/loopgen` |
| sibling | `frontier-loop`, `goal-loop`, `story-loop`, `greenfield-loop` | retired and removed; their archetype cores live in `archetypes/*.md` |

## References

- `primitives/` — the vocabulary. Axes (`target-shape`, `halt-shape`,
  `artifact-shape`, `convergence-shape`, `cadence-shape`, `consult-capability`)
  + shared blocks (`runner-contract`, `judgment-default`, `evidence-tier`,
  `frontload-audit`, `halt-cause-classifier`, `diagnostic-pattern`,
  `evaluator-maturity`, `queue-as-second-artifact`, `pressure-accounting`) and
  the conditional `benchmark-frontier` / `eval-ladder` overlay.
- `archetypes/` — `frontier`, `goal`, `story`, `greenfield`: irreducible loop
  shape + default primitive values + forbidden divergences + failure modes.
- `templates/composed-prompt.md` — the assembly skeleton; `templates/bodies/`
  — the four emittable archetype bodies.
- `references/oracle-principles.md` (goal), `references/review-closure-overlay.md`
  + `references/same-family-drift.md` (frontier),
  `references/greenfield-invariants.md` (greenfield),
  `references/backward-compat-tests.md` (the U11 probe).
