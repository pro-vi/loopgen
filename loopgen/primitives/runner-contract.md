# Runner Contract (shared primitive)

**Purpose.** Declares that the emitted prompt is runner-agnostic internally
while the operator-facing kick-off always uses `/goal`. Establishes the four
things the prompt assumes about its host and the boundary between a runner
ceiling and a repository failure.

**Include when.** Every composed prompt, every archetype, unconditionally.
This block is universal.

**Placeholders.** None — substituted verbatim.

**Idempotency corollary (authoring guidance — not part of the inlined block).**
Because the runner re-invokes the loop from the same bare-pointer kick-off every
iteration — without re-sending the prompt's contents — the emitted prompt must
be safe to re-run from any state: all first-iteration / bootstrap /
one-time setup must be **self-gated on durable state** (`.loop/<loop-id>/STATE.md`
`iteration: 0`, "no `<artifact>` yet"), run once, then skipped — never assumed to
run "first". The **kick-off** invocation the operator pastes into the runner must
likewise be iteration-agnostic (a pointer to the prompt, no "begin with…" step) —
it is re-sent unchanged each iteration. Canonical self-gate shape: story-body's
`## Bootstrap mode`. See SKILL.md Phase 4 → "The kick-off (runner invocation)".

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
runner-contract level.

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
`/goal`, which re-invokes the loop iteratively from the same bare-pointer
kick-off; it never re-sends this prompt's contents. The prompt assumes only:

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

Waiting on something external (a deploy, a review bot's round, a
submitted job, a timed hold) must not spend turns: never wait through a
foreground call that sleeps and re-checks, because every such call is
charged the whole conversation context. Arm the runner's non-blocking
wait (in Claude Code: `Monitor`, or Bash `run_in_background` with an
`until` loop that exits when the condition holds), then do other loop
work or end the iteration; act when the event arrives.

Accepted-iteration commits are authorized by default. Every accepted iteration
that changes tracked files must end with one focused Conventional Commit after
the evidence and canonical artifacts are updated, validators run, and
`git status --short` is inspected. Do not push unless the prompt or human
explicitly authorizes publishing. Do not commit rejected, undecided, or
runner-ceiling crash-recovery diffs.
