# Goal Prompt Template

Use this as the output template for a repo-specific terminal goal loop
prompt. Derivation (see `SKILL.md`) fills the `{{placeholders}}` and drops
conditional sections that do not apply.

The outer fence is **four backticks** so nested `yaml` / `text` blocks
work inside.

---

````md
You are running a terminal goal loop on this repository.

Your job is not to explore the frontier.
Your job is to make a finite acceptance inventory pass without weakening it.

{{PROVENANCE}}

## Motive

{{MOTIVE}}

{{INCLUDE primitives/runner-contract.md}}

{{INCLUDE primitives/judgment-default.md}}

## Frontload

{{FRONTLOAD_PREAMBLE}}

{{PRESSURE_SURFACE}}

## Oracle principles

This loop is honest by construction (full text in
`references/oracle-principles.md`):

1. **Oracle is binary** — pass/fail; never subjective, never self-assessment.
2. **Oracle independence** — a verifier you author must first fail against
   the unmet behavior (mutation, sentinel, known wrong fixture). If it
   cannot fail, it cannot prove.
3. **Consumer-side oracle** — *"if this passes, does the user have a
   working feature?"* If the answer requires inference, the verifier is
   wrong.
4. **Anti-theater** — `FIXED ≠ CLOSED`. A criterion's own verifier passing
   is `PASS_PENDING_FINAL`, not `PASS`. `PASS` requires the **final-verify**
   to prove the whole inventory in one repo state.

## Terminal contract

The run is complete only when **every criterion** in `loop/ACCEPTANCE.md`
for goal version `{{GOAL_VERSION}}` reaches `PASS`.

Completion is a specific halt:

1. emit `criteria-met`
2. then emit `stop-and-summarize`
3. label the halt cause `criteria-met`

Do not emit `criteria-met` for partial completion, local green commands,
manual confidence, or "all easy rows done."

## Goal version

`{{GOAL_VERSION}}` — fingerprint of the frozen inventory + authority
sources + final-verify.

If an authoritative source changes mid-run, do **not** silently absorb it.
Stop, record the source change, and re-derive a new goal version — unless
this prompt explicitly says this is regression mode for the same frozen
version.

{{REGRESSION_MODE}}

## Acceptance inventory

`loop/ACCEPTANCE.md` is the live anchor inventory. Statuses:

- `OPEN` — no criterion-specific proof yet.
- `PASS_PENDING_FINAL` — the criterion's own verifier passed, but the
  final-verify hasn't proved the whole inventory together since.
- `PASS` — the final-verify proved this criterion in the same repo state
  as every other criterion.
- `STUCK` — `{{STUCK_ATTEMPT_N}}` consecutive failed hypotheses with no
  new evidence.
- `BLOCKED_EXTERNAL` — genuine irreversible / external blocker.
- `QUARANTINED` — provenance, criteria, or verifier integrity conflict.

Only `PASS` counts for terminal completion. Every accepted change cites
≥1 criterion ID.

## Verifier discipline

Each criterion has a `verifier` command and `pass_evidence` in
`loop/ACCEPTANCE.md`.

**Valid pass evidence:**

- named test selector passes (with criterion-specific assertion)
- JSON field equals expected value
- CLI output contains exact semantic line
- generated artifact exists and validates
- DOM assertion holds
- migration produces expected schema / row count
- performance threshold met against recorded bound
- error trace includes expected failure legibility

**Invalid pass evidence:**

- "looks good" / manual inspection
- "the suite is green" with no criterion mapping
- snapshot refreshed to current wrong output
- skipped / xfailed criterion
- mocked path replacing integration proof
- assertion-free fixture
- a test you just authored, used as both verifier *and* source of intent

A verifier you author must first **fail** (oracle principle #2). For each
criterion, ask: *if this passes, does the user have a working feature?*
If the answer requires inference, redesign the verifier (principle #3).

## Channels

- **Cheap inner channel:** `{{CHEAP_CHANNEL}}` — run after edits, before
  the criterion-specific verifier.
- **Per-criterion verifier:** the `verifier` field on each criterion.
- **Final-verify:** `{{FINAL_VERIFY}}` — run for terminal completion and
  as a checkpoint after cross-criterion edits.

## Dependency topology

{{TOPOLOGY}}

Criteria are independent unless this topology says otherwise.

- The graph is acyclic; dependencies are *proof* dependencies, not
  implementation preference.
- A child criterion cannot be `PASS` while a prerequisite is failing.
- Passing criteria are regression guards for dependent edits.
- An edit touching multiple criteria cites every affected ID and names
  the primary failing criterion.

Selection order: unmet dependencies first → user-priority when explicit
→ strongest failing evidence → cheapest verifier feedback → highest
regression risk.

## Iteration protocol

1. Read `loop/ACCEPTANCE.md`, `loop/STATE.md`, latest verification
   artifacts, and the source authority files. Confirm the goal version
   still matches the frozen inventory.
2. **Oracle integrity check** before editing:
   - criteria text unchanged except `status` / `last_verification`,
   - verifiers unchanged except via approved Oracle Change Notes,
   - no skipped / xfailed selectors added,
   - no snapshot refreshed without a semantic assertion,
   - no expected evidence weakened.
3. If every criterion is `PASS_PENDING_FINAL` or `PASS`, run the
   **final-verify**. If it proves the whole inventory in the same repo
   state: set all to `PASS`, write `loop/VERIFY.md` with the matrix,
   emit `criteria-met` → `stop-and-summarize`.
4. Otherwise pick one primary failing / `OPEN` criterion by topology +
   priority + cheapest verifier feedback. If every remaining unpassed
   criterion is `STUCK` / `BLOCKED_EXTERNAL` / `QUARANTINED` / wrong-loop-
   shaped, go to halt classification.
5. Before editing, write one line:
   `criterion-id | failing-evidence | hypothesis | edit-surface | rollback`.
6. Make one small reversible change. Run the cheap inner channel; if it
   fails, fix or revert before broader proof.
7. Run the criterion's verifier. Then run impact guards for already-
   passing criteria the edit could disturb.
8. Accept the change only if: the criterion moves toward pass (or gains
   sharper failure evidence), no passing criterion regresses, and the
   oracle was not weakened. Otherwise revert and record the failed
   hypothesis.
9. If the criterion verifier passes, mark `PASS_PENDING_FINAL` — not
   `PASS`. `PASS` waits for the next final-verify.
10. On `{{STUCK_ATTEMPT_N}}` consecutive failures with no new evidence,
    mark the criterion `STUCK` and switch to another unblocked criterion.

## Oracle-drift guard

The headline failure mode. The loop must not:

- delete a criterion
- rewrite a criterion into a weaker form
- merge criteria in a way that drops obligations
- narrow a verifier selector to avoid a failing case
- skip / xfail / invert / remove a failing test
- refresh a snapshot without a semantic assertion proving the new output
- reduce expected evidence specificity
- lower a threshold without an authoritative source change
- replace integration proof with mocked proof
- mark subjective confidence as machine proof
- treat a loop-authored test as source intent

**Verifier changes** require an **Oracle Change Note** appended inline to
`loop/STATE.md`:

```text
oracle_change:
  criterion: AC-XXX
  source_criterion_unchanged: yes
  old_verifier: <cmd>
  new_verifier: <cmd>
  fault: false-positive | false-negative | flake | missing-evidence-hook | non-deterministic
  strictness_proof: <mutation, red/green pair, or sentinel showing new >= old>
  why_not_acceptance_weakening: <one line>
  rollback_trigger: <condition>
```

If strictness-preservation cannot be proved, restore the old verifier or
emit `oracle-drift` and stop.

## Rules

{{SCOPE_MANIFEST}}

### Partial completion is not success

The loop continues while at least one unpassed criterion has a legal
reversible next move inside scope. Halt with `partial-deadlock` only when
every unpassed criterion is `STUCK` / `BLOCKED_EXTERNAL` / `QUARANTINED` /
wrong-loop-shaped.

When halting partial: preserve pass evidence, list every unpassed
criterion with its latest failing evidence, name the next required
authority / verifier / reroute. Do not lower the bar.

### Status-theater prohibition

Do not emit upfront plans or rollout narration. Do not produce completion
summaries mid-run. Traces, diffs, and oracle outputs are truth; notes are
memory.

### Forbidden shortcuts

{{FORBIDDEN_SHORTCUTS}}

No `--no-verify`. No deleting tests. No reducing assertions. No moving a
criterion out of the final-verify. No "temporarily skipped" rows. No
snapshot refresh without semantic proof.

## Halt conditions

Halt = emit `stop-and-summarize`. Terminal success additionally emits
`criteria-met` first. Escalate (rare, irreversible-only) is a separate
signal — see the Runner contract.

Halt when:

- all criteria reach `PASS` in the final-verify → `criteria-met` →
  `stop-and-summarize`
- every remaining unpassed criterion is `STUCK` / `BLOCKED_EXTERNAL` /
  `QUARANTINED` / wrong-loop-shaped → `partial-deadlock`
- oracle drift is detected and cannot be repaired without authority →
  `oracle-drift`
- a genuine irreversible / external blocker prevents proof → `escalate`

### Halt-cause classifier

When emitting `criteria-met`, `stop-and-summarize`, or
`escalate: <reason>`, label:

- `criteria-met` — terminal completion; every criterion in the frozen goal
  version passed in the final-verify.
- `partial-deadlock` — finite goal not met; remaining criteria are stuck /
  blocked / quarantined.
- `oracle-drift` — the criteria / verifier / evidence / final-verify
  cannot be preserved without weakening the acceptance contract.
- `derivation-gap` — blocked on something derivation could have asked for.
  Next derivation pass adds it to the Frontload audit.
- `genuine-escalate` — irreversible / external / authority-needed (paid
  API budget, public-publish, secret, product direction, source conflict).
- `wrong-loop` — the work is not terminal goal-shaped; reroute via `/loopgen` to:
  - the `frontier` archetype if a criterion needs open-ended search, evaluator
    discovery, metric improvement, or "make it better" without a fixed
    pass line;
  - the `greenfield` archetype if the artifact / target / audience / evaluator is
    under-specified and the criteria are placeholders rather than a
    contract;
  - the `story` archetype if the next job is discovering or reconciling product
    promises before a finite implementation target exists.

`derivation-gap` is the feedback signal — the Frontload audit was
incomplete; close it next run.

## Artifacts to maintain

- `loop/ACCEPTANCE.md` — frozen criteria, mutable `status` /
  `last_verification`.
- `loop/STATE.md` — goal version, iteration, current criterion, stuck
  counters, Oracle Change Notes (inline), last action, next action.
- `loop/VERIFY.md` — latest final-verify transcript; written on
  `criteria-met`.
- Evidence artifacts: command output, traces, generated reports,
  screenshots, fixture outputs, metric files.

{{REPO_SPECIFIC_OVERLAY}}
````

---

## Derivation notes

Placeholders populated during derivation (see SKILL.md):

- `{{PROVENANCE}}` — the loopgen provenance preamble.
- `{{MOTIVE}}` — one-sentence terminal goal.
- `{{FRONTLOAD_PREAMBLE}}` — resolved / defaulted / open-gap summary.
- `{{PRESSURE_SURFACE}}` — the pressure weather block (`primitives/pressure.md`),
  emitted only when ≥1 pressure object exists at compose time; stripped otherwise.
- `{{GOAL_VERSION}}` — fingerprint of criteria + provenance + authority +
  final-verify.
- `{{REGRESSION_MODE}}` — omit unless this is a rerun (then: "Regression
  mode for goal version X — same frozen inventory, same final-verify").
- `{{CHEAP_CHANNEL}}` — exact command.
- `{{FINAL_VERIFY}}` — exact terminal command / script.
- `{{TOPOLOGY}}` — dependency graph, or "all criteria independent."
- `{{STUCK_ATTEMPT_N}}` — default 3.
- `{{SCOPE_MANIFEST}}` — allowed / forbidden globs (binary in/out).
- `{{FORBIDDEN_SHORTCUTS}}` — repo-specific shortcut bans.
- `{{ARTIFACT_LOCATIONS}}` — concrete paths.
- `{{REPO_SPECIFIC_OVERLAY}}` — command notes, fixture notes, CI caveats,
  known false-green zones.

## Acceptance row format

YAML list in `loop/ACCEPTANCE.md`. Minimum fields per criterion: `id` ·
`statement` · `source` · `authority` · `verifier` · `pass_evidence` ·
`fail_evidence` · `status` · `depends_on` · `reopen_condition` ·
`last_verification`.

A design blueprint's unit IDs lift in as `id`; its test scenarios lift in
as `pass_evidence` + `fail_evidence`; its decisive choice becomes the
`authority`. The only new work goal-loop does on top of an upstream
blueprint is wire the `verifier` command per criterion and define the
`final-verify`.

A criterion may be split into subcriteria only when proof requires it;
the parent remains, and completion requires every child *and* the
parent-level verifier to pass. Splitting is illegal if it drops any
obligation.
