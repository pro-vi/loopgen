# Runner Contract (shared primitive)

**Purpose.** Declares that the emitted prompt is runner-agnostic internally
while the operator-facing kick-off always uses `/goal`. Establishes the four
things the prompt assumes about its host and the boundary between a runner
ceiling and a repository failure.

**Include when.** Every composed prompt, every archetype, unconditionally.
This block is universal.

**Placeholders.** None — substituted verbatim.

**Source of truth.** Byte-identical to the `## Runner contract` block in the
retired `frontier-loop` / `goal-loop` / `story-loop` prompt templates
(verified at hoist time). After retirement, this file is canonical.

**Idempotency corollary (authoring guidance — not part of the inlined block).**
Because the runner re-invokes the *same* prompt every iteration, the emitted
prompt must be safe to re-run from any state: all first-iteration / bootstrap /
one-time setup must be **self-gated on durable state** (`loop/STATE.md`
`iteration: 0`, "no `<artifact>` yet"), run once, then skipped — never assumed to
run "first". The **kick-off** invocation the operator pastes into the runner must
likewise be iteration-agnostic (a pointer to the prompt, no "begin with…" step) —
it is re-sent unchanged each iteration. Canonical self-gate shape: story-body's
`## Bootstrap mode`. See SKILL.md Phase 4 → "The kick-off (runner invocation)".
Dogfooding citation: mdtools hybrid-pareto goal loop (2026-05-29) — a kick-off
that said "begin with its First-iteration bootstrap" would have re-run inventory
instantiation on iteration 2; fix was to gate the bootstrap on `iteration: 0`
inside `PROMPT.md` and reduce the kick-off to a stable pointer.

**Unattended corollary (authoring guidance).** When the loop runs UNATTENDED (the
default for `/goal`, cron-style runs, `cadence-shape: deferred-fire-and-forget`),
the emitted prompt MUST **globally forbid interactive / blocking / approval-prompt
tools (`AskUserQuestion` and the like), for ANY reason** — no human is there to
answer, so any such call is an overnight deadlock. Route every decision instead:
reversible → smallest reversible default + Alignment Review; needs-a-human or
irreversible → `stop-and-summarize` with the right halt label and the question in
the summary (async, never interactive). A **context-scoped** ban is not enough —
forbidding interactive prompts only for cost leaves the tool reachable for the
next decision ("which cell?", "ambiguous oracle?"). Make it global, at the
runner-contract level. Dogfooding: mdtools hybrid-pareto loop (2026-05-29) — a
cost-only "don't ask" rule still left `AskUserQuestion` reachable; the loop
blocked on it at the first paid step.

**Commit corollary (authoring guidance).** Loopgen prompts authorize unattended
local commits by default. Every accepted iteration that changes tracked files
must close with exactly one focused Conventional Commit after evidence,
canonical artifacts, validators, and `git status --short` agree. Pushes remain
separately authorized; the default is commit, not publish. A composed prompt may
suppress per-iteration commits only by declaring the suppression in frontload
and giving an alternate durability rule. Rejected, undecided, or runner-ceiling
crash-recovery diffs are not committed: revert them or checkpoint the exact diff
and next command.

---

## Runner contract

This prompt is runner-agnostic internally. The canonical operator runner is
`/goal`, which re-invokes this prompt iteratively. The prompt assumes only:

1. Iterative re-invocation — you are one iteration.
2. File-persisted state — durable progress lives in named files, not memory.
3. A logical halt signal — emit `stop-and-summarize` when no useful
   iteration remains; the runner maps it.
4. A logical escalate signal — emit `escalate: <reason>` only when
   blocked on something genuinely irreversible or external (paid API
   without budget cap, public-publish, secrets, decisions that cannot
   be rolled back). Reversible judgment is not escalation — see the
   judgment default.

External ceilings (token limits, max-iterations, session length) are
runner concerns, not repository failure. Preserve the worktree and
summarize unresolved work for the next run.

Accepted-iteration commits are authorized by default. Every accepted iteration
that changes tracked files must end with one focused Conventional Commit after
the evidence and canonical artifacts are updated, validators run, and
`git status --short` is inspected. Do not push unless the prompt or human
explicitly authorizes publishing. Do not commit rejected, undecided, or
runner-ceiling crash-recovery diffs.
