# Greenfield Invariants (archetype reference)

> Hoisted verbatim from the retired `greenfield-loop` SKILL.md. These are the
> 11 patterns every successful green-field loop converges on empirically;
> the `greenfield` archetype includes them in its composed prompt. Encoding
> them up front saves 50–100 iterations of rediscovery.

---

## The 11 green-field invariants (encoded in the emitted prompt)

These are the patterns that *every* successful green-field loop converges on
empirically. Encoding them up-front saves 50–100 iterations of rediscovery.

### 1. Evaluator scaffolding precedes artifact

The first 3–7 iterations are *rubric construction*, not output. The loop
authors `.loop/<loop-id>/RUBRIC.md`, picks initial criteria, writes concrete pixel/
artifact-level anchors, and only then renders the first artifact. If the user
demands output before evaluator, the prompt should warn that early outputs
will inflate.

**Score-locked ramp.** STATE.md starts with `score_lock: yes`. While
locked the loop may not write numeric totals, pass/fail judgments,
milestone claims, or artifact-to-artifact rankings — only rubric drafting,
evidence-rule definitions, the cheap dignity test, audience-comprehension
probes, and explicitly labeled `CALIBRATION — NOT PRODUCT — NOT SCORED`
runs. Exit the lock only when RUBRIC.md v0.1 has 8–12 criteria with
0/2/5 anchors and per-criterion evidence rules, the cheap dignity test
is written, an audience-comprehension probe is defined, and `INTENT.md`
holds live target hypotheses (see #3).

### 2. Pixel/artifact-level evidence is mandatory for any score above 2

The single most reliable failure mode in green-field is *agent-grades-own-
homework*. The fix is structural: every score above 2 requires citation
evidence (extracted frames, AST nodes, test outputs, transcript spans —
whatever the artifact is). No citation = score caps at 2. Run a "would this
pass the cheap dignity test" guard (Keynote-slide-guard equivalent) before
writing the total.

**Blind comprehension for audience-facing scores above 3.** For criteria
involving clarity, narrative, comprehension, audience fit, persuasion, or
memorability: scores above 3 require a blind read — send the artifact to
a fresh isolated session (LLM via the invariant-8 CONSULT channel, or a
human reviewer) **without** the rubric, prompt, internal rationale, or
current scores. Ask: *"what is this trying to do? what did you
understand? what felt missing, confusing, derivative, or hollow?"*
Compare to the artifact's `comprehensionClaim`. Cap the criterion at 2
if no blind read was run; cap at 3 if the blind read substantially
diverges from the claim.

### 3. The intent itself will change. Build for that.

In green-field, the user's "I want X-adjacent" is provisional. They will
look at output and reframe — typically 2–4 times before the actual target
locks in. Encode:
- Schedule explicit **user-look gates** every ~50 iterations (not frequent
  pause-polling — substantive review milestones)
- Treat any user reframe as a first-class iteration that may invalidate
  prior scores; write a `STATE.md` block that explicitly resets stale
  numbers when intent shifts
- Don't let the loop defend old work against new intent
- Maintain `.loop/<loop-id>/INTENT.md` with **≥3 live target hypotheses**: the
  literal interpretation, a more ambitious / more original interpretation,
  and a dangerous-but-plausible wrong interpretation. Each names
  supporting evidence, artifact implications, what good output makes the
  user understand/feel/do, failure smells, invalidating evidence, and one
  cheap probe that distinguishes it. No rubric criterion may be added
  unless it maps to a live hypothesis. Re-review INTENT.md every ~10
  iterations, on every user reframe, and before any major rubric revision.

### 4. Hard-coded numerical targets are scaffolding, not goals

Numerical milestones (45/50, 3 essays × 3 styles, etc.) prevent drift
early. They WILL become ceilings once hit. Encode:
- The rubric is replaceable; the philosopher's stone is not
- When milestone is hit "faster than expected," that's evidence the
  rubric was too easy — *raise the ceiling, don't celebrate*
- Once the user reframes to "no fixed milestone," switch to imbalance-
  seeking (see #5)

**Rubric versions + score quarantine.** `RUBRIC.md` carries
`rubric_version: vN` and `score_comparable_with: [...]`. Any of these
creates a new version and quarantines old scores: user reframe,
target-hypothesis change, major artifact-format change, milestone hit
faster than expected, three consecutive high scores with no substantial
audience/capability change, a frontier-consult flagging stale-target
risk, or a blind-comprehension read that diverges from self-scores.
During quarantine the loop may not claim improvement against the old
total; it must revise the evaluator, run a divergence probe, or
rebaseline under the new version. "Raise the ceiling" must be a new
version, not a stricter restatement of stale criteria.

### 5. Imbalance-seeking replaces sequenced plans eventually

Sequenced plans (N+1, N+2, …) are useful early — they give the loop
something to climb. Eventually the user will say "stop following a script."
At that point switch to imbalance-seeking: every iteration begins with
diagnosis of the *currently most under-developed* dimension of the stone.
Diagnostic categories: output quality (rubric criteria), capability surface,
style/voice emergence, agent experience, creative direction.

### 6. CAPABILITY mode is first-class

Green-field loops *grow capability* — install new tools, integrate new
substrates, wire new modalities — when those advance the stone. This is not
"yak-shaving"; it's the loop's job. Encode CAPABILITY as priority 0 or 1
in the mode menu, with the discipline rule: **must advance the stone, not
pad the toolbelt.** Each addition justified against a stone-axis.

### 7. Judgment default + bounded escalate

Pausing for human input is the polling-shaped failure mode. The default is
**narrow reversible judgment + Alignment Review**: pick the smallest
reversible action consistent with the strongest available source, record
problem · options · chosen contract · alignment cost · rollback trigger ·
review question, and continue. Topic, content, style, scene-direction,
essay-text are all the loop's job — make the call, log it, move on. Human
review happens after the fact.

**Never call `AskUserQuestion` or any interactive / blocking / approval-prompt
tool, for any reason** — unattended, it is a deadlock, not a question. Route
reversible → default + log; needs-a-human or irreversible → `escalate` /
`stop-and-summarize` with the question in the summary.

Emit `escalate: <reason>` only for genuinely irreversible / external
blockers: **paid APIs without budget caps, public-publish actions, and
secrets/credentials** — nothing else.

Saturation rule: 2 consecutive escalates on the same logical question force
a default judgment on the third.

### 8. Frontier-model consults are creative direction, not architecture review

Schedule a CONSULT every ~10 iterations. Frame the question as:
*"what's seductive-but-hollow about recent progress?"* and *"what omission
would look stupid in 6 months?"* — not "review my plan." Disagreement with
the consultant is allowed and sometimes correct. Capture into
`.loop/<loop-id>/creative-consults.md`.

**Blind adversarial protocol.** The consult packet excludes current
scores, the loop's preferred next plan, and self-justifying rationale.
It contains: the user's original intent + later reframes, current
INTENT.md hypotheses, representative artifacts or excerpts, the current
rubric criteria *without scores*, and known constraints. Ask:

1. What current target should be killed or demoted?
2. What's seductive-but-hollow about recent progress?
3. What would look derivative, trivial, or embarrassing in six months?
4. What assumption is the loop over-optimizing?
5. What one experiment would most cheaply invalidate the current rubric?

Within 3 iterations the loop must do one of: run a proposed invalidation
experiment, revise INTENT.md / RUBRIC.md because of the answer, or
explicitly reject the answer with a concrete reason. A consult that
produces no behavioral change and no explicit rejection does **not** count
as completed.

**Consult availability detection (at derivation time).** Inspect the
host environment for a frontier-model consult channel (Agentify Desktop
MCP, PAL, mcp__* tools, or similar). If none is available, mark
invariant 8 in the emitted PROMPT.md as
`CONSULT unavailable in this environment — front-loaded as a known
limitation; the loop proceeds without scheduled creative consults and
surfaces creative-direction blindness as a known risk.` Do not silently
drop the invariant — the user should see at run-start that CONSULT is
off, and consider a periodic human-look gate instead.

### 9. Provenance/re-editability matters from the first generated asset

The moment the loop produces an asset that wasn't deterministically
authored from code (image-gen, video-gen, vendored SVG, generated text),
provenance becomes load-bearing. Encode a slot-manifest contract with at
minimum: `slotId, semanticRole, source, prompt, seed, replaceability,
comprehensionClaim`. The `comprehensionClaim` field — what should this
asset make the viewer/reader/user understand? — is the linchpin of
honest scoring later.

### 10. Human-only work front-loaded into a gated preloop phase

Greenfield projects with hardware, secrets, license clicks, network setup, or
identity decisions (which model? which account? which physical machine?) must
*not* fold those into iter 0. They belong in a **preloop phase** that gates
on a binary completion flag (e.g. `preloop_complete: yes`) the human flips
when the human-only checklist is done. Without this gate, the loop will:

- Spin on escalates for things only the user can do, polling-shape instead of moving
- Wrong-default decisions that should be the user's (which model? which tunnel?)
- Mix human-decision velocity with autonomous-iteration velocity, distorting
  scoring and pacing

When emitting the prompt, identify human-only items in the project's domain
and write them as a numbered preloop checklist with matching fields in
STATE.md. Add a **gate-hardening line**: the gate is binary — `yes` literally,
or halt. No "almost done," no partial fills, no commented-out completions.

**Role-protected gates.** Every phase gate declares its owner:
`owner: loop | user | external`. A `user`-owned gate (preloop_complete,
license clicks, secret install, identity decisions) cannot be flipped
to `yes` by the loop — only an explicit user edit or user message. If
the loop finds a user-owned gate set to `yes` without evidence, treat
it as `no`, restore the block, and continue only with non-gated
preparatory work. A `loop`-owned gate (e.g. `research_complete`) requires
structured `exit_evidence` — decision record, rejected alternatives,
assumptions still at risk, implications for RUBRIC.md and preloop.
Research may run at most 3 consecutive iterations without completing
the gate or naming a specific blocker in STATE.md.

If the project also has *open questions* requiring hands-on research (best
practices, model identity, runtime choice) before the preloop checklist
makes sense, add a **Phase 0: research** that *precedes* preloop, with its
own `research_complete: yes` gate. Phase order: research → preloop → bootstrap
(iter 0 automated) → iter 1+. Gate hardening applies to all phase transitions.

### 11. Per-iteration commit discipline from day one

Loops produce hundreds of durable artifacts (renders, frame-grabs,
transcripts, generated assets). The LEDGER and score files are durable
text; everything else is at risk until committed. Hard rule: every
**accepted** iteration with file changes ends with `git add … && git commit`
before the iteration ends; rejected or undecided diffs are reverted, not
committed (matching `runner-contract.md`). Format: `chore(loop): iter NNN —
<mode> — <focus>`. Use `COMMIT_APPROVED=1` env to bypass interactive hooks.
