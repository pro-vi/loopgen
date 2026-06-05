# loopgen

<p align="center"><strong>Prompt Compiler for creating long-running autonomous loops.</strong></p>

<p align="center"><em>It writes the weather, not just the target — a re-readable pressure field that makes the wrong worlds harder to reach while the loop runs.</em></p>

Your loop died 10 minutes after you went to sleep.

Not because the task was impossible. It blocked on a decision you could have made before it ever fired, or it declared victory on the first green-looking signal.

loopgen writes the part of the prompt that keeps that from happening.

Give it the thing you're trying to do: close a spec, improve the codebase, push a benchmark, walk a frontend, build a vague idea. It classifies the loop, writes the prompt + state + queue files, resolves the decisions that would stall the run, then hands you one `/goal` line. Paste it into Claude Code or Codex and let it run.

The visible output is intentionally boring:

```text
/goal read loop/PROMPT.md and execute as <loop identity>.
```

![loopgen compiled loop contract](assets/loopgen-hero.jpg)

## Quick Start

Ask for the loop you actually want. Same compiler, different track:

| Track | Ask | What loopgen composes |
|---|---|---|
| Product walkthrough | `/loopgen "walk the onboarding flow"` | A story-shaped loop: keep the product surface contract, reconcile the visible flow with the storyboard. |
| Backend benchmark | `/loopgen "optimize the checkout API load benchmark"` | A frontier-shaped benchmark loop: keep pressure accounting, candidate lineage, traces, and metrics. |

Both emit the same kind of fixed kickoff:

```text
/goal read loop/PROMPT.md and execute as onboarding flow loop.
/goal read loop/PROMPT.md and execute as checkout API load benchmark loop.
```

The stable file shape is the point. Product walkthroughs keep the story surface:

```text
loop/PROMPT.md
loop/STATE.md
docs/storyboard.md
```

The backend benchmark track emits the frontier ledger and benchmark overlay:

```text
loop/PROMPT.md
loop/STATE.md
loop/FINDINGS.md
loop/TRACES.md
loop/METRICS.md
loop/DOMAIN_SPEC.md
loop/BENCHMARK.md
loop/FRONTIER.json
loop/CANDIDATES.jsonl
loop/traces/
```

## How it actually works

loopgen is four battle-tested loop-generator skills folded into one compiler. It
picks the shape from your intent, fills the blanks the loop would otherwise hit
mid-run, creates canonical state/prompt/artifact files, then hands you the fixed
`/goal` kickoff prompt.

| Seed | Archetype | Halts on |
|---|---|---|
| A task with a definition of done | `goal` | `criteria-met`: one final-verify proves the frozen acceptance inventory |
| A quality edge to push | `frontier` | `homeostatic-checkpoint`: the loop has no useful in-scope intervention left |
| A product surface to walk through | `story` | `storyboard-converged`: the visible product matches the storyboard |
| An idea to build out from zero | `greenfield` | `stone-converged`: the artifact landed on the user's reframed target |

The compiler flow is short:

1. **Frontload audit.** Resolve paths, commands, evaluator, scope, budget, and irreversible decisions before the loop fires.
2. **Classify.** Extract primitive values and pick the nearest archetype. Contradictions ask instead of silently defaulting.
3. **Compose.** Start from the archetype body, apply divergences and overlays, fill provenance and frontload gaps.
4. **Emit.** Write the prompt/state/artifact contract and the same `/goal read loop/PROMPT.md...` pointer every time.

Hybrids keep the nearest archetype's contract, then add the active divergent or
overlay pieces. A story-shaped frontend snappiness loop, for example, keeps the
storyboard surface but adds trace/metric evidence because the target needs
before/after pressure.

## Install

It's a skill. Send your agent the repo, or clone it and symlink `loopgen/` into the skill directory (`~/.claude/skills/` for Claude Code, `~/.codex/skills/` for Codex).

## Why This Skill?

Most autonomous prompt workflows behave like one-shot overnight instructions:
the runner gets a large prompt, discovers missing decisions mid-run, then
stalls or invents a stop condition.

loopgen creates a middle layer:

- **Prompt contract** — `loop/PROMPT.md` carries the full re-entrant loop playbook
- **Durable state** — `loop/STATE.md` records classification, frontload, artifacts, and halt scan
- **Queue artifacts** — acceptance inventories, storyboards, ledgers, rubrics, traces, and metrics give the loop somewhere concrete to work
- **Fixed runner pointer** — `/goal read loop/PROMPT.md...` stays the only operator-facing kickoff

The result is a loop that can survive handoff, resume from state, and explain
which contract shaped it.

## Capabilities

| Capability | Description |
|---|---|
| **Archetype classification** | Maps the task to `goal`, `frontier`, `story`, or `greenfield` by primitive values, not vibes. |
| **Hybrid composition** | Keeps the nearest archetype contract and adds active divergences or overlays. |
| **Frontload audit** | Resolves commands, paths, evaluator, scope, and irreversible decisions before the loop fires. |
| **Deterministic artifacts** | Emits the same canonical files for the same loop shape every run. |
| **Benchmark frontier overlay** | Adds domain spec, benchmark, candidate lineage, frontier state, and trace roles when a concrete eval is bound. |
| **Provenance preamble** | Names the primitive, archetype, body, reference, and overlay files that shaped the prompt. |
| **Runner-stable kickoff** | Always emits one `/goal read loop/PROMPT.md...` pointer with no first-iteration instructions baked in. |

## Common Asks

| Ask | Shape |
|---|---|
| `/loopgen "close this spec"` | `goal`: finite acceptance inventory + final verify |
| `/loopgen "walk the onboarding flow"` | `story`: storyboard + surface evidence |
| `/loopgen "optimize the checkout API load benchmark"` | `frontier`: findings ledger + traces + metrics + benchmark overlay |
| `/loopgen "build out this artifact idea from zero"` | `greenfield`: rubric + intent + README |
| `/loopgen "improve frontend snappiness"` | `story` with frontier-expanding evidence add-ons |

## Skill Behavior

The bundled `loopgen` skill teaches the model to:

- Never compose from memory; read the required primitives, archetype, body, and overlay references first
- Never silently default on contradictory primitive values
- Always emit canonical artifact files for the active contracts
- Always record `derivation_read_set`, frontload, divergences, overlays, and artifacts in `loop/STATE.md`
- Always make hybrids additive: nearest archetype first, then divergent primitive and overlay contracts
- Always emit the bare `/goal read loop/PROMPT.md and execute as <identity>.` kickoff
- Never put first-iteration setup instructions in the kickoff; bootstrap belongs inside the re-entrant prompt

## Skill Internals

These are not separate user docs. They are the markdown source files the
`loopgen` skill reads, combines, and emits from.

| Source | Role in the compiler |
|---|---|
| [`loopgen/SKILL.md`](loopgen/SKILL.md) | Compiler contract, phases, artifact/state contracts, and runner kickoff rules. |
| [`loopgen/primitives/`](loopgen/primitives) | Primitive vocabulary: target, halt, artifact, convergence, cadence, frontload, runner, evidence, evaluator, pressure, benchmark overlays. |
| [`loopgen/archetypes/`](loopgen/archetypes) | Defaults and failure modes for `goal`, `frontier`, `story`, and `greenfield`. |
| [`loopgen/templates/composed-prompt.md`](loopgen/templates/composed-prompt.md) | Assembly procedure for emitted prompts. |
| [`loopgen/templates/bodies/`](loopgen/templates/bodies) | Archetype body templates that become `loop/PROMPT.md`. |
| [`loopgen/references/`](loopgen/references) | Oracle, benchmark-frontier, greenfield, review closure, and compatibility references. |

---

It's a prompt-writer skill with strong opinions about going to sleep. That's all. YMMV.
