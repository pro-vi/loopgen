---
name: loopgen
description: "Compose a repo-specific, /goal-ready loop prompt from a primitive vocabulary — loopgen writes the weather, not just the target. Classifies a task to its nearest archetype (frontier / goal / story / greenfield), composes the prompt from primitive values — defaulting to the archetype, diverging where the task demands — and emits with provenance. Also diagnoses a drifting loop. Triggers: '/loopgen', 'derive a loop for X', 'make me an overnight loop', 'close the findings in X', 'fix the bugs by morning', 'push a benchmark with a loop', 'walk the storyboard', 'build out an idea from zero'."
---

# Loopgen

`/loopgen` derives a repo-specific, **runner-agnostic** loop prompt with a
canonical `/goal` kick-off. The emitted `.loop/<loop-id>/PROMPT.md` carries the complete
iteration contract; the operator-facing invocation is always a stable pointer
to that file. It is a **hybrid dispatcher + compositional generator**: it runs a
shared pre-flight audit, classifies the task to its nearest *archetype* by
extracting primitive values, composes the prompt by combining those values
(defaulting to the nearest archetype's presets and diverging where the task
demands), and emits with a provenance preamble.

Each archetype's irreducible core lives in `archetypes/*.md`; its shared
infrastructure is the primitive vocabulary in `primitives/*.md`.

Invoke **once per run** to author or revise a prompt; the loop's per-iteration
playbook lives in the composed `.loop/<loop-id>/PROMPT.md`, not here. Invoke in
**Diagnostic mode** to retrofit a drifting loop.

## When to invoke

- "derive a loop / write me a loop for X"
- "make this an overnight / autonomous loop"
- any per-archetype loop intent: closing a finite checklist, pushing a
  benchmark, walking a storyboard, or building an idea from zero
- a task that mixes archetypes (e.g. frontier evidence discipline + story
  chapter cadence) — loopgen is the only skill that composes hybrids

## Do NOT invoke when

- the user wants a one-off plan or one-shot build, not an iterative loop → a
  planning / build path, not loopgen
- a known-path transform gated by a terminal verifier — even one with finite
  acceptance criteria — is a one-shot build, not a loop (the Phase 2 loop-necessity
  gate catches it if it slips through to classification)
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

**Shared primitives** (the non-archetype-varying vocabulary layer; each one
surfaces differently — not all are constant, and not all are emitted):

- **Emitted in every composed prompt:** `runner-contract`, `judgment-default`,
  the frontload-audit output (`primitives/frontload-audit.md`, filling
  `{{FRONTLOAD_PREAMBLE}}`), `halt-cause-classifier`, `context-stack` (the memory
  model + STATE/JOURNAL/DERIVATION schema + context budget, INCLUDEd by every
  body's Artifacts section), and `pressure` (the always-on pinned HUD via
  `{{PRESSURE_SURFACE}}` — no compose gate; ADR 0004).
- **Archetype-scoped:** `evidence-tier` — every archetype except `goal`, which
  relies on oracle principles + the acceptance inventory as its evidence
  surface instead (`templates/composed-prompt.md` §8, Signal hierarchy).
  `evaluator-maturity` (T0–T6) and `frontier-vector-adequacy` (the earned
  outcome-dimension lifecycle) — `frontier` only, named in its `## Extras`.
- **Wired, artifact-shape-scoped:** `queue-as-second-artifact` — the queue-growth
  block INCLUDEd by every body's Artifacts section whenever `artifact-shape` is
  not `prompt-only` (i.e. almost every composed prompt); it carries the
  `closed-retain-N` bound and the INDEX/FULL row split. `pressure-accounting` is
  the `frontier` projection of `pressure`, not a separate archetype-varying axis.
- **Gated** (universal in the vocabulary, conditional in the composed output):
  `subagent-patterns` — the one remaining compose-gated block. Its
  `{{SUBAGENT_PATTERNS}}` block (catalog B/C/D — pattern A is the existing
  single-agent protocol, never part of the block) emits only at
  `consult-tier ≥ 1`, filtered to that tier; at `tier-0` it is stripped
  byte-identical (`primitives/subagent-patterns.md`).
- **Read every run, never emitted:** `diagnostic-pattern` — read on every
  Diagnostic-mode invocation to drive the retrofit procedure; per
  `primitives/diagnostic-pattern.md` it is "not part of an emitted prompt"
  (Diagnostic mode only, never Phase 1–4 authoring).

**Forbidden divergences** (identity-breaking; never compose — route away):

- `goal` cannot take `target-shape` `frontier-expanding`/`discovery-reframing`,
  nor `halt-shape` `manual-gated`.
- `frontier`/`greenfield` cannot take `target-shape` `finite-criteria`.

**Contradictions** (classification error → AskUserQuestion, never silent
default): `target: finite-criteria` with `halt: equilibrium`/`manual-gated`, or
with `convergence: homeostatic-checkpoint`.

Not a contradiction: `frontier` + `reopen_contract: none` resolving to
`halt-shape: requested=equilibrium → effective=terminal` is a
**frontload-resolved divergence** (the guarded closed-corpus resolution,
`primitives/halt-shape.md`) — the target stays `frontier-expanding`, and both
requested and effective values are recorded in provenance.

**`consult-capability` tiers** (detected at frontload time — probe for
`mcp__agentify-desktop__*`, other `mcp__*` tools, `/second-opinion`,
`/agentify`, PAL): `tier-0` none → drop scheduled-consult sections + substitute
the emittable human-look gate (`primitives/human-look-gate.md`); `tier-1`
human-bridge handoff; `tier-2` single programmatic
consult; `tier-3` rich fabric (blind adversarial + multi-modal). All archetypes
default `tier-0` if undetected — never assume a channel exists.

## Derivation read contract

Do not compose from memory. Every authoring run reads a bounded, provenance-
relevant set of files. Persisting that list is scoped to successful
composition: only a run that composes and emits writes it as
`derivation_read_set` in the write-once `.loop/<loop-id>/DERIVATION.md`;
declines and Diagnostic mode read but never write it (below).

**Tier 1 — read for classification + frontload (every run, including runs
that decline):**

- `primitives/target-shape.md`
- `primitives/halt-shape.md`
- `primitives/artifact-shape.md`
- `primitives/convergence-shape.md`
- `primitives/cadence-shape.md`
- `primitives/consult-capability.md`
- `primitives/frontload-audit.md`
- `primitives/pressure.md`

`primitives/pressure.md` is read every run because the frontload latent-pressure
mining step is universal and needs its modes + object schema. Its
`{{PRESSURE_SURFACE}}` block is now emitted in **every** composed prompt
(always-on; ADR 0004 reversed the former ≥1-object gate), so it always appears in
the provenance `Primitive sources:` line; seeded or mined rows only pre-populate
the in-force set.

**Tier 2 — read for composition (only after the loop-necessity gate passes
and composition proceeds):**

- `templates/composed-prompt.md`
- `primitives/runner-contract.md`
- `primitives/judgment-default.md`
- `primitives/evidence-tier.md`
- `primitives/halt-cause-classifier.md`
- `primitives/queue-as-second-artifact.md`
- `primitives/context-stack.md`
- `primitives/human-look-gate.md`

A `{loop_warranted: false}` decline stops after Tier 1 — the loop-necessity
gate halts Phase 2 before Tier 2's composition reads ever start. A decline
emits no loop artifacts and mints no loop id, so it has no `DERIVATION.md` to
write: it names its Tier-1 read list in the decline response instead. A
Diagnostic-mode invocation likewise never reaches Tier 2; it reads per
`primitives/diagnostic-pattern.md` instead of the Tier 1 list, and never
writes the target loop's write-once `DERIVATION.md` — its reads are named in
its diagnostic output. `derivation_read_set` in `.loop/<loop-id>/DERIVATION.md`
records whichever tiers the successful composition actually read. This does not
change the derivation-gap rule below: a required read that cannot be completed
is still a derivation gap, not a reason to guess.

**After classification, also read:**

- `archetypes/<nearest>.md`
- `templates/bodies/<nearest>-body.md`
- every `primitives/<axis>.md` whose value diverged from the nearest archetype
  default
- every `archetypes/<source>.md` that supplied a divergent value by archetype
  default
- every reference named by the nearest archetype's `## Extras`
- every primitive/reference named by active overlays

For frontier-shaped tasks, read `primitives/evaluator-maturity.md`,
`primitives/pressure-accounting.md`, and
`primitives/frontier-vector-adequacy.md`. When benchmark language appears or the
benchmark-frontier overlay activates, read `primitives/benchmark-frontier.md`,
`primitives/eval-ladder.md`, `references/benchmark-frontier-artifacts.md`, and
`references/benchmark-frontier-example.md`. When `consult-tier ≥ 1`,
read `primitives/subagent-patterns.md`.

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

Also record the runner-lifecycle declaration `context_mode_requested`
(`fresh-episode` / `rolling-lossy` / `unknown`) with its
`context_mode_compose_basis` — an operator statement or a declared runner
profile only, defaulting to `unknown`, never inferred from what the
composing window shows (`primitives/context-stack.md`: model-visible history
proves neither mode).

For frontier-shaped tasks, also assess `benchmark-frontier`: it activates only
when frontload binds a concrete benchmark, evaluation, or harness object with an
evaluation unit and evidence location. Benchmark/eval/harness language without
a bound object is a derivation gap, not a silent generic frontier default.

Record results under `.loop/<loop-id>/DERIVATION.md` `frontload:` (the write-once
derivation record — `primitives/context-stack.md`) and produce the frontload
preamble (resolved / defaulted / open gaps). Anything unresolved, undefaulted,
and unmarked is a **derivation gap** — name it explicitly; the emitted prompt's
halt-cause classifier flags `derivation-gap` halts so the next pass closes it.

## Phase 2 — Primitive extraction + archetype classification

**Loop-necessity gate (run FIRST, before classifying).** Answer the iteration
test: *does this task REQUIRE re-entry, or converge in one pass?* A loop earns its
scaffolding ONLY when convergence is uncertain and the path is discovered through
iteration — the runner attempts, the oracle REJECTS, it revises, and re-enters,
repeatedly. All three must lean "loop":

1. **Re-entry expected** — you do NOT expect iteration-1 success; attempt → reject
   → revise cycles are the norm, not the exception.
2. **Path discovered, not known** — the work isn't a known `read → transform →
   verify`; the route is found by trial.
3. **Oracle as gradient, not gate** — the oracle shapes successive attempts, vs.
   gating one terminal completion.

If instead the path is known, the oracle gates one completion, and iteration-1
success is the expected case → **it is a one-shot build, not a loop.** Emit
`{loop_warranted: false}` and STOP — do not classify, compose, or emit loop
artifacts. The task wants direct one-shot implementation (planned first or not),
not loop scaffolding; hand it to whatever build/implementation path the consumer
uses.

**The trap this exists to catch (named from a real miss):** a task that classifies
as `goal` at **distance 0** — `{finite-criteria, terminal, criteria-completion}` —
with a strong deterministic oracle and a *known* path. Distance 0 to `goal` is
**necessary but not sufficient** for a loop: the `goal` *shape* (hit a fixed
target, stop) is also the *build* shape. A goal whose criteria are each satisfiable
in a single known pass is a build wearing loop clothes — its STATE reads
`iteration: 1 → criteria-met`, the re-entry machinery never firing. Only emit a
`goal` loop when at least one criterion genuinely needs iterate-to-converge
(flaky-fix, "until the suite passes" over many tries, search with no fixed pass
line). `frontier`/`story`/`greenfield` are the genuinely-iterative archetypes;
`goal` is the one most easily mistaken for a loop.

If genuinely mixed (some criteria one-shot, some iterate-to-converge), or you
cannot tell → AskUserQuestion: loop vs build.

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

Emit a structured classification: `{archetype, loop_warranted, runnable,
target-status, divergences[], overlays[], consult-tier, evaluator-tier}`, where
`loop_warranted` is `true` only after the loop-necessity gate passes (a `false`
gate already stopped the skill — the task is a one-shot build, not a loop),
`target-status`
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
Frontier's `homeostatic-checkpoint` also does not mean completion: a frontier
objective never completes by being good enough. It fires only after the full
frontier scan reaches checkpointable quiescence — known homeostasis axes are
balanced, pressure discovery found no admissible pressure, and vector adequacy
has no candidate awaiting a probe or confirmation and no newly admitted
dimension requiring continuation. The episode
then either checkpoints and reopens on fresh signal (effective `equilibrium`)
or terminates on declared-workset exhaustion (effective `terminal`) — ending
the execution, not the objective. Only non-frontier archetype
success causes may say the loop is complete. If a prompt can halt on a shared
cause, it must tell the runner to report the frontier/queue/story as open or
checkpointed and list the unresolved artifact rows or halt scan.
It must also require a full search-surface scan before any non-success halt —
including a frontier episode termination —
so one blocked row cannot stop a frontier/story/greenfield/goal loop while
another in-scope evaluator, observability, specification, verifier, or queue
repair move remains.

`genuine-escalate`'s trigger enumeration is canonical across every archetype
and must not be reworded or abbreviated per body: paid API budget,
public-publish, secrets, product direction with unclear rollback, source
conflict between authoritative-current sources — exactly as
`primitives/halt-cause-classifier.md` states it
(`primitives/judgment-default.md` lists the same causes in its escalate
rule). Every body's Halt-cause classifier section cites this list, not a
paraphrase.

Before emit, derive the **mandatory-write set** from the artifact contracts,
one-time bootstrap actions, active overlays, and every acceptance verifier or
output path. Compare each path with the emitted binary allowed/forbidden scope.
A mandatory product write outside the allowed set or inside the forbidden set is
a `derivation-gap`: stop composition and resolve the contradiction instead of
silently widening scope. The host-repository `.gitignore` guard and any required
`git rm -r --cached` of already-tracked `.loop/` paths are the sole
operational-bootstrap exception. The emitted prompt must name that exception
beside its scope manifest and limit it to protecting `.loop/`; it does not
authorize any other `.gitignore` edit. All other mandatory writes must pass the
same scope comparison.

## Artifact + state contracts

Every file-backed emission writes the same canonical anchors. Repo-native paths
may be recorded as aliases inside `.loop/<loop-id>/STATE.md`, but they do **not** replace
the canonical files.

**Loop-record location (uniform).** All loop records live under
`.loop/<loop-id>/` — **gitignored execution state**, uniform with the
frontier-loop scratch already kept there (`.loop/<name>/`). `<loop-id>` is a
**zero-padded sequence prefix + identity slug**: a 3-digit monotonic number
(per repo — `max(existing .loop/NNN-* dirs) + 1`, first loop is `001`) joined by
`-` to the kebab-case of the one-phrase identity used in the kick-off (e.g. the
first loop with identity "weave cross-product OOD loop" → `.loop/001-weave-eval/`).
The prefix orders loops by creation and keeps the dir unique when two loops share
an identity slug; mint it once at bootstrap and reuse it verbatim every iteration.
Records are **local-only by default** (not version-controlled) — they are
execution state, not deliverables; durable conclusions graduate to
`docs/`/`specs/`/code, never the loop dir. The gitignore guard is part of
emit, not optional, and an ignore line alone does not undo prior tracking:
(1) resolve the **host repo root** (`git rev-parse --show-toplevel`) and edit
*that* `.gitignore` — creating it if absent — to ignore `.loop/`; (2) check for
already-tracked `.loop/` paths (`git ls-files .loop/`) and, if any exist,
untrack them with `git rm -r --cached` (kept on disk) before or alongside the
ignore edit; (3) verify with `git check-ignore .loop/<loop-id>/` before writing
any loop record. In a worktree or nested repo, the guard targets the repo root
that owns the working directory (`git rev-parse --show-toplevel` from the
current cwd), not any other worktree's or parent's root. The
kick-off points the runner at `.loop/<loop-id>/PROMPT.md`. Every
`.loop/<loop-id>/<file>` path below is rooted here.

**Common files, every archetype** (tiers per `primitives/context-stack.md`):

- `.loop/<loop-id>/PROMPT.md` — the complete re-entrant iteration prompt; carries
  the always-emitted Operational core near the top for bounded rehydration.
- `.loop/<loop-id>/STATE.md` — **live status only** (PINNED): fixed keys,
  rewrite-in-place, ≤ ~50 lines, no history.
- `.loop/<loop-id>/JOURNAL.jsonl` — the single append-only history (one typed
  record per line, target ≤300 chars — never truncating a required field —
  evidence as write-ahead pointers): `attempt`,
  `oracle_change`, `pressure`, `consult`, `alignment_review`, `checkpoint`,
  `halt`, `score_quarantine`, `bootstrap`, `consolidation`. Read `tail -n 20`
  per pass, `jq` by
  key otherwise. **No separate CHECKPOINTS / monitor file exists** — humans watch
  via the documented journal one-liner. `consolidation` records are written by
  the Consolidation round (`primitives/context-stack.md`): scheduled every ~10
  iterations and **forced early** by contract-layer triggers (a scope surviving
  2+ correct-looking fixes, an unmoved target metric, local proof vs durable
  state disagreeing, an impossible observation) — the round reads the pressure
  set as one field and audits the contract layer beneath the code (ADR 0005).
- `.loop/<loop-id>/DERIVATION.md` — write-once derivation record
  (`primitive_bundle`, `divergences`, `overlays`, `derivation_read_set`,
  `frontload`); read on demand (diagnostic / resume), not per pass.
- `.loop/<loop-id>/PRESSURE.md` — the always-rendered pressure HUD (PINNED),
  rendered from `.loop/<loop-id>/STATE.md` `pressure_objects` (the in-force set,
  the source of truth) and re-read at step 0 each iteration. It is the canonical
  pressure surface for `goal` / `story` / `greenfield`. `frontier` also renders
  its pressure through the findings ledger + `pressure_status` (the projection,
  `primitives/pressure-accounting.md`), so for `frontier`
  `.loop/<loop-id>/PRESSURE.md` aliases that surface rather than inventing a
  second one — consistent with the frontier Storage rule (findings ledger /
  `.loop/<loop-id>/STATE.md`).

**Archetype files:**

| Archetype | Required files |
|---|---|
| `goal` | `.loop/<loop-id>/ACCEPTANCE.md`, `.loop/<loop-id>/VERIFY.md` |
| `story` | `docs/storyboard.md` |
| `frontier` | `.loop/<loop-id>/FINDINGS.md`, `.loop/<loop-id>/TRACES.md`, `.loop/<loop-id>/METRICS.md` |
| `greenfield` | `.loop/<loop-id>/RUBRIC.md`, `.loop/<loop-id>/INTENT.md`, `.loop/<loop-id>/README.md` |

`.loop/<loop-id>/VERIFY.md` may start as an empty "not yet run" final-verify transcript;
it still exists so every goal loop has the same resume surface. `.loop/<loop-id>/TRACES.md`
and `.loop/<loop-id>/METRICS.md` are indexes: they may point to repo-native trace
directories, performance reports, benchmark outputs, or generated artifacts.

**Required `.loop/<loop-id>/STATE.md` keys, every archetype:** live status only,
rewrite-in-place — no history (see the context-stack primitive).

- `archetype`, `identity`
- `consult_tier`, `consult_tier_effective`, `evaluator_tier`
- `context_mode_effective`, `context_mode_resolution_basis`
  (operator-declared / runner-attested / unknown — never observation;
  runner-attested is reserved, no current producer, so absent an operator
  declaration the mode stays unknown),
  `history_visibility_observed` (a visibility fact, never a mode basis)
- `artifacts: {canonical, repo_aliases}`
- `iteration`, `phase`, `current_artifact`, `last_action`, `next_action`
- `halt_cause`, `halt_scan`
- `pressure_objects` (in-force rows only, bounded by pressure-cap)

The write-once derivation keys (primitive_bundle, divergences, overlays,
derivation_read_set, frontload) live in `.loop/<loop-id>/DERIVATION.md`, not
`STATE.md`; the former pressure_ledger / pressure_consulted are pressure /
consult records in `.loop/<loop-id>/JOURNAL.jsonl` (see Common files above).

**Archetype-specific `.loop/<loop-id>/STATE.md` keys:**

- `goal` — `goal_version`, `current_criterion`, `stuck_counters`,
  `final_verify`. (The former `oracle_change_notes` is now an `oracle_change`
  `JOURNAL.jsonl` record, not a STATE key.)
- `story` — `storyboard_path`, `lane`, `surface_class`, `current_story`,
  `last_surface`, `last_story_family`, `same_family_count`, `fixture_mode`,
  `evidence_manifest`, `last_validation_commands`,
  `remaining_findings_classified`. `halt_scan` (common key above) is the
  pre-`stop-and-summarize` full-surface re-grounding record for this
  archetype — story does not carry a second, differently-named halt-scan key.
- `frontier` — `frontier_vector`, `current_anchor`, `reward_channels`,
  `pressure_status`, `pressure_debt`, `checkpoint_reason`, `next_pressure`,
  `trace_locations`, `metric_locations`, `guardrails`.
- `greenfield` — `score_lock`, `phase_gates`, `current_stone_axis`,
  `user_halt_owner`. `rubric_version` and `score_comparable_with` live in
  `.loop/<loop-id>/RUBRIC.md`, `target_hypotheses` lives in
  `.loop/<loop-id>/INTENT.md`, and the `capability_list` capability surface lives
  in `.loop/<loop-id>/README.md` — those files are the canonical source
  (`templates/bodies/greenfield-body.md`, `references/greenfield-invariants.md`),
  not `STATE.md`; `STATE.md` does not duplicate them as a resume pointer, since
  `RUBRIC.md` is itself a required file re-read every iteration.

`frontier`'s `pressure_status` / `pressure_debt` / `checkpoint_reason` /
`next_pressure` are the frontier projection of the common in-force
`pressure_objects` — a checkpoint-level aggregate over those rows (not a
field-for-field rename), rendered as a checkpoint contract; the transition
history they summarize lives in `.loop/<loop-id>/JOURNAL.jsonl` `pressure`
records, not a per-frontier ledger.

**Hybrid merge rule.** A hybrid is a union over **active contracts**, not a
blind union over all contributing archetypes:

1. Emit the nearest archetype's complete file + state contract.
2. Add every file and state key required by each divergent primitive value.
3. Add every file and state key required by each active overlay.
4. Never drop the nearest archetype's state obligations unless the divergence is
   forbidden and the task is routed away instead of composed.

Important add-ons:

- `target-shape: frontier-expanding` adds `.loop/<loop-id>/TRACES.md`,
  `.loop/<loop-id>/METRICS.md`, `frontier_vector`, `trace_locations`,
  `metric_locations`, and `guardrails` when those are not already present.
  `frontier_vector` / `guardrails` are compact one-line live rows seeded once
  from `{{FRONTIER_VECTOR}}` at bootstrap; thereafter runtime admission
  through the earned dimension lifecycle
  (`primitives/frontier-vector-adequacy.md`) is the only mutation path.
- `artifact-shape: findings-ledger` adds the full frontier artifact set:
  `.loop/<loop-id>/FINDINGS.md`, `.loop/<loop-id>/TRACES.md`, and `.loop/<loop-id>/METRICS.md`.
- `artifact-shape: acceptance-inventory` adds `.loop/<loop-id>/ACCEPTANCE.md` and
  `.loop/<loop-id>/VERIFY.md`.
- `artifact-shape: storyboard` adds `docs/storyboard.md`.
- `artifact-shape: rubric+intent` adds `.loop/<loop-id>/RUBRIC.md`, `.loop/<loop-id>/INTENT.md`, and
  `.loop/<loop-id>/README.md`.
- `overlay: benchmark-frontier` adds `.loop/<loop-id>/DOMAIN_SPEC.md`,
  `.loop/<loop-id>/BENCHMARK.md`, `.loop/<loop-id>/CANDIDATES.jsonl`, `.loop/<loop-id>/FRONTIER.json`, and
  `.loop/<loop-id>/traces/`.

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

> `/goal read .loop/<loop-id>/PROMPT.md and execute as <one-phrase loop identity>.`
>
> e.g. `/goal read .loop/<loop-id>/PROMPT.md and execute as the hybrid-pareto benchmarking loop.`

`/goal` re-sends the *same bare-pointer kick-off* every iteration (see
`primitives/runner-contract.md`), never `PROMPT.md`'s contents. The kick-off
must therefore be **iteration-agnostic** and carry **no instruction content** —
every rule (which file is the goal, where `STATE.md` is, the iteration protocol,
the bootstrap gate) lives in
`.loop/<loop-id>/PROMPT.md`, the single source. If you are tempted to add a clause to the
kick-off ("…and start with…", "….loop/<loop-id>/STATE.md tells you where you are"), put it
in `PROMPT.md` instead. NEVER bake first-iteration language into the kick-off
("begin with the bootstrap", "first, instantiate…") — on iteration 2 it
mis-fires, re-running one-time setup.

This only works if `PROMPT.md` is **re-entrant**: all bootstrap /
inventory-instantiation / one-time work must be **self-gated on durable state** in
`.loop/<loop-id>/STATE.md` (`iteration: 0`, "no inventory / storyboard / ledger yet"), run
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
`primitives/diagnostic-pattern.md`: read the current `.loop/<loop-id>/PROMPT.md` +
`.loop/<loop-id>/STATE.md` + the queue artifact + ledger; **classify which archetype the
loop currently is** (it may have drifted from its declared archetype — flag the
drift first); score against that archetype's failure modes (`archetypes/*.md`);
emit a **minimal** `.loop/<loop-id>/PROMPT.md` mutation (inline edit, never a rewrite);
write a ⚠️ block to `.loop/<loop-id>/STATE.md`.

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
- **Composing a loop for a one-shot build.** A `goal` task at distance 0 with a
  known path and a terminal deterministic oracle is a one-shot build, not a loop —
  its STATE would read `iteration: 1 → criteria-met`, the re-entry machinery never
  firing. Run the loop-necessity gate (Phase 2) first; distance 0 to `goal` is
  necessary but not sufficient for a loop.
- **A second history / monitor file.** `JOURNAL.jsonl` is the only history
  surface; a CHECKPOINTS-style monitor file is a second history that drifts from
  the first. Humans watch the loop via the documented journal one-liner, not a
  separate artifact (ADR 0004).
- **Unbounded `STATE.md` keys.** `STATE.md` is live status only,
  rewrite-in-place. Any key that accumulates across iterations (an attempt log, a
  pressure ledger, a consult log, a growing score log) is a history stream in
  disguise — it belongs in `JOURNAL.jsonl`, not `STATE.md`.

## Composability

| Direction | Skill | Relationship |
|---|---|---|
| upstream | a planning / blueprint skill | conceptual parent; a blueprint's units + decisive choice are a first-class `goal` criteria source |
| upstream | an oracle / verifier-design helper | complementary for the `goal` archetype's verifier matrix |
| downstream | `/goal` | canonical runner that executes the emitted `.loop/<loop-id>/PROMPT.md`; `/goal` is the runner, not the `goal` archetype |
| downstream | an upstream orchestrator | may still name the removed loop commands; repoint to `/loopgen` |
| sibling | `frontier-loop`, `goal-loop`, `story-loop`, `greenfield-loop` | retired and removed; their archetype cores live in `archetypes/*.md` |

## References

- `primitives/` — the vocabulary. Axes (`target-shape`, `halt-shape`,
  `artifact-shape`, `convergence-shape`, `cadence-shape`, `consult-capability`)
  + shared blocks (`runner-contract`, `judgment-default`, `evidence-tier`,
  `frontload-audit`, `halt-cause-classifier`, `diagnostic-pattern`,
  `evaluator-maturity`, `queue-as-second-artifact`, `context-stack`, `pressure`,
  `pressure-accounting`, `frontier-vector-adequacy`, `human-look-gate`) and
  the conditional `benchmark-frontier` / `eval-ladder` overlay.
- `archetypes/` — `frontier`, `goal`, `story`, `greenfield`: irreducible loop
  shape + default primitive values + forbidden divergences + failure modes.
- `templates/composed-prompt.md` — the assembly skeleton; `templates/bodies/`
  — the four emittable archetype bodies.
- `references/oracle-principles.md` (goal), `references/review-closure-overlay.md`
  + `references/same-family-drift.md` (frontier),
  `references/greenfield-invariants.md` (greenfield).
