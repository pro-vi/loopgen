# loopgen

> **Security:** Loopgen composes prompts that may run unattended. External data
> disclosure and software-supply-chain expansion require explicit authorization;
> see [SECURITY.md](SECURITY.md) and the always-emitted External trust boundary.

<p align="center"><strong>Prompt Compiler for creating long-running autonomous loops.</strong></p>

<p align="center"><em>It writes the weather, not just the target — a re-readable pressure field that makes the wrong worlds harder to reach while the loop runs.</em></p>

Your loop died 10 minutes after you went to sleep.

Not because the task was impossible. It blocked on a decision you could have made before it ever fired, or it declared victory on the first green-looking signal.

loopgen writes the part of the prompt that keeps that from happening.

Give it the thing you're trying to do: close a spec, improve the codebase, push a benchmark, walk a frontend, build a vague idea. It classifies the loop, writes the prompt + state + queue files, resolves the decisions that would stall the run, then hands you one `/goal` line. Paste it into Claude Code or Codex and let it run.

The visible output is intentionally boring:

```text
/goal read .loop/<loop-id>/PROMPT.md and execute as <loop identity>.
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
/goal read .loop/001-onboarding-flow/PROMPT.md and execute as onboarding flow loop.
/goal read .loop/002-checkout-benchmark/PROMPT.md and execute as checkout API load benchmark loop.
```

The stable file shape is the point. Product walkthroughs keep the story surface:

```text
.loop/001-onboarding-flow/PROMPT.md
.loop/001-onboarding-flow/STATE.md
.loop/001-onboarding-flow/PRESSURE.md  (seeded empty until a pressure exists)
docs/storyboard.md
```

The backend benchmark track emits the frontier ledger and benchmark overlay:

```text
.loop/002-checkout-benchmark/PROMPT.md
.loop/002-checkout-benchmark/STATE.md
.loop/002-checkout-benchmark/FINDINGS.md
.loop/002-checkout-benchmark/TRACES.md
.loop/002-checkout-benchmark/METRICS.md
.loop/002-checkout-benchmark/DOMAIN_SPEC.md
.loop/002-checkout-benchmark/BENCHMARK.md
.loop/002-checkout-benchmark/FRONTIER.json
.loop/002-checkout-benchmark/CANDIDATES.jsonl
.loop/002-checkout-benchmark/traces/
```

## How it actually works

loopgen is four battle-tested loop-generator skills folded into one compiler. It
picks the shape from your intent, fills the blanks the loop would otherwise hit
mid-run, creates canonical state/prompt/artifact files, then hands you the fixed
`/goal` kickoff prompt.

| Seed | Archetype | Halts on |
|---|---|---|
| A task with a definition of done | `goal` | `criteria-met`: one final-verify proves the frozen acceptance inventory |
| A quality edge to push | `frontier` | `homeostatic-checkpoint`: known axes are balanced, pressure discovery and vector adequacy are resolved, and no high-yield in-scope intervention remains |
| A product surface to walk through | `story` | `storyboard-converged`: the visible product matches the storyboard |
| An idea to build out from zero | `greenfield` | `stone-converged`: the artifact landed on the user's reframed target |

The compiler flow is short:

1. **Frontload audit.** Resolve paths, commands, evaluator, scope, budget, and irreversible decisions before the loop fires.
2. **Classify.** Extract primitive values and pick the nearest archetype. Contradictions ask instead of silently defaulting.
3. **Compose.** Start from the archetype body, apply divergences and overlays, fill provenance and frontload gaps.
4. **Emit.** Write the prompt/state/artifact contract and the same `/goal read .loop/<loop-id>/PROMPT.md...` pointer every time.

Hybrids keep the nearest archetype's contract, then add the active divergent or
overlay pieces. A story-shaped frontend snappiness loop, for example, keeps the
storyboard surface but adds trace/metric evidence because the target needs
before/after pressure.

## Install

It's a skill. Clone it, symlink `loopgen/` into whichever agent's skill directory, then check the contracts.

```bash
git clone git@github.com:pro-vi/loopgen.git
ln -s <clone>/loopgen ~/.claude/skills/loopgen   # Claude Code
ln -s <clone>/loopgen ~/.codex/skills/loopgen    # Codex
ln -s <clone>/loopgen ~/.pi/agent/skills/loopgen # Pi
make check                                       # confirm the skill contracts are coherent
```

## Why This Skill?

Most autonomous prompt workflows behave like one-shot overnight instructions:
the runner gets a large prompt, discovers missing decisions mid-run, then
stalls or invents a stop condition.

loopgen creates a middle layer:

- **Prompt contract** — `.loop/<loop-id>/PROMPT.md` carries the full re-entrant loop playbook
- **Durable state** — `.loop/<loop-id>/STATE.md` holds live status only (iteration, artifacts, pressure, halt scan); the write-once `.loop/<loop-id>/DERIVATION.md` records classification and frontload
- **Queue artifacts** — acceptance inventories, storyboards, ledgers, rubrics, traces, and metrics give the loop somewhere concrete to work
- **Fixed runner pointer** — `/goal read .loop/<loop-id>/PROMPT.md...` stays the only operator-facing kickoff

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
| **Earned dimension discovery** | Lets a frontier loop test whether its current outcome coordinates hide meaningful progress, admitting a new dimension only through independent evidence. |
| **Provenance preamble** | Names the primitive, archetype, body, reference, and overlay files that shaped the prompt. |
| **Runner-stable kickoff** | Always emits one `/goal read .loop/<loop-id>/PROMPT.md...` pointer with no first-iteration instructions baked in. |

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
- On successful composition, record `derivation_read_set`, frontload, divergences, and overlays in the write-once `.loop/<loop-id>/DERIVATION.md` (a decline emits nothing and names its reads in the response); `.loop/<loop-id>/STATE.md` stays live status (artifacts, iteration, pressure)
- Always make hybrids additive: nearest archetype first, then divergent primitive and overlay contracts
- Always emit the bare `/goal read .loop/<loop-id>/PROMPT.md and execute as <identity>.` kickoff
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
| [`loopgen/templates/bodies/`](loopgen/templates/bodies) | Archetype body templates that become `.loop/<loop-id>/PROMPT.md`. |
| [`loopgen/references/`](loopgen/references) | Oracle, benchmark-frontier, greenfield, review closure, and compatibility references. |

---

It's a prompt-writer skill with strong opinions about going to sleep. That's all. YMMV.
