# Story Prompt Template

Use this as the output template for a repo-specific Story Loop prompt.
Derivation (see `SKILL.md`) fills the `{{placeholders}}`, drops conditional
sections that do not apply, and uses plain repo-language rather than generic
narration.

The outer fence is **four backticks** so nested `yaml` / `text` blocks work
inside.

---

````md
You are running a Story Loop on this repository.

Your job is to maintain the product's living contract with users: discover
one user-facing promise, make narrow reversible product judgments when
needed, document the alignment cost for human review, implement or verify
one focused slice, capture evidence, and continue. It is not broad QA or a
project-management digest.

{{PROVENANCE}}

## Motive

{{MOTIVE}}

{{INCLUDE primitives/runner-contract.md}}

{{INCLUDE primitives/judgment-default.md}}

## Frontload

{{FRONTLOAD_PREAMBLE}}

{{PRESSURE_SURFACE}}

## Core objects

### Guidance Source

Normalize every source before extracting stories:

```yaml
kind: vision_doc | docs | issue | pr | test | code | observed_ui | analytics | support | human | work
locator: "path, URL, issue id, route, test name, or note title"
truth_kind: aspirational | public_claim | planned | disputed | implemented | enforced | observed | reviewer_intent
freshness: current | recent | stale | unknown
confidence: explicit | inferred | weak
summary: "what this source appears to claim"
```

Source truth matters:

- Vision reveals intent; it does not prove implementation.
- Docs reveal public or internal claims; they may be stale.
- Code reveals affordances; it does not decide product intent.
- Tests reveal protected behavior; they may protect accidental behavior.
- Issues and PRs reveal planned, disputed, or recently changed behavior.
- Observed UI reveals current behavior; it is not automatically intended.
- Human prompts reveal current reviewer intent; record them explicitly.

Observed UI, code, tests, and stale sources may generate candidates or
evidence, but they do not establish product intent by themselves. Promotion
requires human intent, current docs, accepted issue/PR guidance, another
explicit authoritative source, or a recorded Alignment Review for a narrow
reversible judgment.

### Story Record

Use this shape for each storyboard row. YAML, JSON, JSONL, or Markdown
tables are acceptable; prefer the format already used in the repo.

```yaml
id: evidence-anchor-opens-source-span
title: Evidence anchor opens source span
persona: compliance_officer
promise: "I can inspect the exact source behind a report claim."
sources:
  - kind: issue
    locator: ENG-857
    truth_kind: planned
    freshness: current
    confidence: explicit
acceptance:
  - "Clicking a report evidence anchor opens the source drawer."
  - "The drawer identifies the cited document."
  - "The cited evidence span is preserved through navigation."
fixtures:
  - pack_legal_live_upload
story_family: visible-mechanical
fixture_mode: requires-real-auth
verification_recipe:
  app_url: "http://localhost:5203"
  probe: "browser interaction + DOM state + screenshots"
status: candidate
alignment:
  promise_review: unreviewed
  acceptance_review: inferred
  enforcement_allowed: false
  reviewer: null
reviewer_questions:
  - "Does replay count, or only live upload?"
parent: null
children: []
latest_evidence: null
decisions: []
```

Keep records small. A row is useful when a human reviewer can answer: "yes,
this is a real promise", "no, this is stale", "split this", or "this
fixture proves the wrong thing".

## Status model

Use precise statuses:

- `candidate` - extracted or inferred, not yet acceptance-shaped.
- `aligned` - human or strong source confirms the promise is real.
- `ready` - both gates pass:
  - **intent-ready**: authoritative source (human, current docs,
    accepted issue/PR, public claim) or a recorded Alignment Review.
  - **proof-ready**: a known route/surface, a declared fixture mode, a
    fixture (or recorded fixture-gap), an evidence method, a manifest
    path or repo-local evidence location, a passing preflight, and a
    failure classifier that distinguishes product-fail / oracle-defect /
    fixture-gap / env-gap.
  If intent-ready but not proof-ready → `fixture-gap` / `env-gap`. If
  proof-ready but not intent-ready → stay `candidate` / `disputed`.
- `verifying` - currently under evidence capture.
- `verified` - passed with linked evidence.
- `product-fail` - app behavior contradicts an aligned or
  alignment-reviewed promise.
- `oracle-defect` - probe/test/selector/evidence capture is wrong or stale.
- `fixture-gap` - current data cannot prove the promise.
- `env-gap` - app, auth, seed, backend, or dev-server prevents
  verification.
- `stale` - contradicted by newer guidance or product direction.
- `split-needed` - story is too broad; child candidates were created.
- `disputed` - sources or reviewers disagree on intended behavior.

Do not use a bare pass/fail status. The classification is the point.

## Selected lane and surface

- **Lane:** {{LANE}}
- **Surface class:** {{SURFACE_CLASS}}

A story is in-lane when it improves the selected persona's rendered
surface, workflow, state, decision, trust, or recovery on
`{{SURFACE_CLASS}}`. Findings outside the selected surface class may be
recorded as candidates, but they must not become the promoted story unless
the user changes lanes or the finding directly supports the selected story.

## Storyboard

- **Path:** {{STORYBOARD_PATH}}

Update only this storyboard. If a row uses a different format than the
file convention, normalize before writing.

## Mechanical run contract

Durable progress lives in artifacts, not memory. Keep `loop/STATE.md`
current enough that another runner can resume without guessing. Track:

- `phase`, `iteration`, `current_story`, `last_action`, `next_action`
- `last_surface`, `last_story_family`, `same_family_count`
- `fixture_mode`: `bypass-compatible | requires-real-auth | admin-operator | unknown`
- `evidence_manifest`: path to the current or latest promoted story manifest
- `last_validation_commands`: exact focused commands run
- `remaining_findings_classified`: counts or short notes for skipped findings
- `halt_cause` and `halt_re-grounding` before `stop-and-summarize`

Every promoted story writes a small manifest in the repo's evidence
location when available. Prefer JSON so it can be parsed with `jq empty`;
otherwise include the same fields in the storyboard or ledger:

```json
{
  "storyId": "<id>",
  "surface": "<route or component/workflow>",
  "storyFamily": "visible-mechanical | recovery-copy | semantic-only | operator-only | other",
  "fixtureMode": "bypass-compatible | requires-real-auth | admin-operator | unknown",
  "beforeArtifacts": [],
  "afterArtifacts": [],
  "validationCommands": [],
  "classification": "verified | product-fail | oracle-defect | fixture-gap | env-gap",
  "commit": {
    "hash": null,
    "subject": null
  },
  "remainingFindings": [],
  "haltEligibility": {
    "checked": false,
    "reason": null
  }
}
```

If the manifest is missing or unparseable, repair it before promotion or
classify the result as `oracle-defect` / `env-gap` instead of pretending
the run has durable evidence.

## Bootstrap mode

Enter Bootstrap mode when any of these hold: no storyboard exists yet;
no lane/surface has been recorded; no story has both an authoritative
source and an executable proof plan; the app route / fixture / seed /
auth / evidence-capture path is unknown.

Bootstrap is **not verification**. Do not mark stories `ready`,
`verifying`, `verified`, or `product-fail` during bootstrap.

Output a small ramp packet (terse, prose or single-level list — no
nested forms):

- selected lane, selected surface class
- storyboard path (created or existing)
- sources scanned (kind + locator + truth_kind + freshness, one line each)
- proof-surface inventory (runnable? app URL? routes? fixtures? auth?
  evidence-capture path? blockers?)
- seeded candidates (just IDs)
- exit criteria — a single sentence per: lane named, one promise with
  authoritative source, AC distinguishes failure classes, fixture or
  fixture-gap recorded, proof recipe runnable or env-gap recorded

Exit Bootstrap only when at least one story can become `ready` under
the Ready Gate. If the proof surface is still missing, emit
`fixture-gap` / `env-gap` instead of attempting verification.

## Iteration protocol

### 1. Gather guidance

Inspect the strongest available sources. For generic frontend repos, prefer:

1. human prompt and current branch context
2. vision/product docs
3. README, docs, routes, and UI copy
4. existing tests and Storybook/component examples
5. issues, PRs, changelogs, and review comments
6. observed running UI
7. analytics, support notes, or other field evidence

When a work-tracking adapter (Linear, GitHub, vault, Slack — host-
specific) is available and relevant, use it to synthesize context and
record its findings as `kind: work`. Still preserve the underlying source
type when known, such as `issue`, `vault`, `github`, or `slack`.

### 2. Enumerate or update candidate stories

Extract user-facing promises, not implementation tasks. Phrase each story
from the user's perspective:

```text
As <persona>, I can <capability>, so that <user value>.
```

Prefer small stories tied to one surface or workflow. If a candidate
contains multiple user jobs, mark it `split-needed` and create children.

Deduplicate by persona + promise + surface + fixture. If two sources
disagree, keep one story in `disputed` with both sources attached instead
of choosing a winner silently.

Prefer a small delta over a full-board rewrite. Do not create large
backlogs from weak inference. When many candidates appear, add only the
most source-backed candidates and summarize the rest as reviewer questions.

**Current-surface promise scan** (when the storyboard is sparse or
stale, or no new source-backed candidate has appeared in the last few
iterations). Run a narrow scan of visible commitments on the selected
surface:

- page titles and section headings
- primary and secondary CTAs
- empty / loading / error / disabled / success / recovery copy
- table / card / list labels and status chips
- navigation labels and destination promises
- confirmation, warning, destructive, or irreversible-action language

Classify each hit as `observed_ui` or `public_claim` — these are
**not** authoritative intent by themselves. Promote at most one
observed promise to `candidate` per iteration. To make it `ready`,
require either corroborating current docs / issue / PR / test / human
guidance, or a recorded Alignment Review. Also record at least one
rejected or weak observed promise per scan, so the reviewer can see
what was intentionally not promoted.

For raw scan output or broad grep/browser findings, classify non-selected
findings before choosing a story or halting:

- `player-facing` - on the selected public/user workflow
- `admin/operator` - operational surface; promote only for a high-value
  operational story
- `api-only` - response or server behavior without a selected rendered
  surface
- `unused/unmounted` - no current route/component usage found
- `already-covered` - protected by a verified story or fresh regression
- `fixture-blocked` - plausible but needs data/auth/devslot work first
- `candidate` - worth shaping into a future story

Record a compact summary in `remaining_findings_classified` before any
`signal-starvation` halt.

### 3. Align and record judgment

Apply the Judgment default (above). Story-loop-specific Alignment Review
fields:

- user-behavior problem
- context
- options considered
- pros and cons
- chosen contract
- alignment cost
- review question for the human
- rollback or revisit trigger

Human alignment is still required before fixing product code against:

- revival of stale notes or old POC claims
- source conflict resolution
- fixture/golden definitions
- splits, merges, or supersession decisions that change scope
- broad "this behavior is intended" decisions
- visual direction, game rules, monetization, risk model, target persona,
  or product promise changes
- irreversible data changes or changes with unclear rollback

If the user explicitly authorizes a story in-chat, record that as a
`human` source with `truth_kind: reviewer_intent`.

If a stale source conflicts with current docs, current UI, recent PRs, or
human guidance, mark the affected story `stale` or `disputed`; do not
revive it as `aligned` without reviewer approval.

### 4. Select one ready story

Verify exactly one `ready` story per iteration. A story may contain
multiple acceptance items only when they are required to prove the same
user promise. Do not verify story clusters unless the user explicitly
requests a batch pass. Do not let new discoveries hijack the current
verification. Child discoveries go back onto the board as `candidate`.

Selection priority:

1. aligned story with current business/reviewer priority
2. story with explicit source and clear proof surface
3. story whose verification can distinguish product failure from oracle
   failure
4. story blocking other stories

For Surface Taste Lane, require a screenshot-proven visible delta on the
selected surface, or an interaction trace that directly changes the
selected persona's visible state. Semantic-only, scoped-name-only,
group-label-only, active-state-only, and outside-selected-surface-only
findings are supporting observations unless they are explicitly the
selected lane or directly support the selected story.

**Story movement gate.** A promoted product change should move the selected
story or feature promise, not merely harvest a technically valid defect.
Prefer changes that improve visible comprehension, task completion,
decision support, state / recovery clarity, interaction safety, flow
ergonomics, or product character. Semantic-only changes (names, roles,
groups, decorative classification, status wording) may be promoted when
they unblock durable proof or repair a misleading rendered contract, but
they are otherwise candidates or supporting evidence for a higher-value
story.

Do not let global audits choose the story before a selected surface and
user promise exist. Run broad audits only after story selection as
regression safety.

Skip stories whose proof surface is missing; mark `fixture-gap`,
`env-gap`, or `oracle-defect` and create the appropriate handoff. If no
ready story exists, continue discovery and alignment-prep by default
instead of treating the loop as complete.

**No-ready-story fallback (not QA).** When no `ready` story exists, do
**not** begin exploratory QA and do not opportunistically verify observed
behavior. Perform one bounded frontier-prep action: pick the lane / surface
class if absent → scan the strongest current sources for that surface →
seed or update at most 3 `candidate` stories → write acceptance criteria
for at most 1 → record the missing gate that blocks readiness (missing
intent → `candidate` + reviewer question; source conflict → `disputed`;
no fixture → `fixture-gap`; no runnable app → `env-gap`; story too broad
→ `split-needed`). The output is a storyboard update + handoff or
reviewer question — never `verified` or `product-fail`.

**Frontier novelty.** A `verified` story is ineligible for re-selection
unless a trigger is recorded: an attached source changed · the route /
component / fixture / workflow changed · prior evidence was invalidated
· a human explicitly requested regression · the story blocks a newer
candidate · the story is part of a named release or migration surface.
Among eligible stories, prefer frontier expansion over proof convenience:
new explicit source not yet on the board → current public/product claim
without acceptance criteria → `disputed` / `stale` needing re-grounding
→ candidate with clear user value but missing proof recipe → `ready` with
no prior evidence → regression of a previously `verified` story only with
a recorded trigger. After 2 consecutive iterations that add no new
source, no new candidate, and no new alignment decision, force a
re-grounding pass before further verification.

**Same-family drift guard.** Track `last_story_family` and
`same_family_count` in `loop/STATE.md`. Low-visibility families include
scoped-name-only fixes, decorative element classification, group/landmark
labels, pending-status wording, and operator-only semantics. Recovery-copy
or validation-copy stories are visible, but still count as the same family
when they keep repairing the same surface and failure mode. After two
same-family promotions, the next accepted iteration must either move a
different visible/mechanical story, run a broader source/browser/e2e
re-grounding pass, or document `signal-starvation` with surfaces checked.
After three same-family promotions, block another promotion from that
family unless the manifest records why it is higher-value than the drift
risk and what alternate surfaces were checked.

### 5. Verify with evidence

Before launching the app or browser, confirm the selected story is `ready`
and has either explicit alignment or a recorded Alignment Review that
authorizes a narrow reversible judgment. If neither exists, state that the
run is evidence-only and cannot produce a promoted fix.

Before capture, restate:

```text
story id | promise | acceptance item | fixture mode | fixture | expected evidence | failure classification plan
```

Declare fixture mode before running browser or Playwright evidence:

- `bypass-compatible` - dummy/local auth bypass proves the selected story.
- `requires-real-auth` - real provider/session behavior is part of the
  claim; do not run under bypass and call it proof.
- `admin-operator` - operational story; keep out of player-facing loops
  unless explicitly selected.
- `unknown` - classify as `fixture-gap` or `env-gap` before promotion.

Use the narrowest proof that settles the story:

- screenshot for visual state
- DOM/browser state for behavior
- network/console capture for request and runtime behavior
- fresh command output for tests, lint, typecheck, or build claims
- code references only for structural claims

Record environment identity: branch/SHA, app URL, API URL when relevant,
fixture mode, fixture, seed, browser/project, and timestamp. For local
frontend apps, ensure the server belongs to the current checkout before
capturing evidence. If the command/env uses a different fixture mode than
the story declares, stop and classify `fixture-gap` or `env-gap`.

For Surface Taste Lane, capture a mirrored before/after packet:

- desktop screenshot of the selected route/state
- mobile screenshot when the selected surface is responsive or
  mobile-relevant
- focused crop when the full screenshot hides the actual delta
- interactive snapshot of relevant controls, names, roles,
  active/current states, disabled/loading states, and focusable elements
- DOM/layout eval for relevant visible text, bounding boxes, overflow,
  hit targets, primary action position, and hidden/disabled state
- console summary
- network summary for mutation or data-loading stories
- interaction/timing trace for action, feedback, duplicate-submit, or
  recovery stories

The after packet should repeat the same artifacts so the reviewer can
compare the selected surface directly.

After validation, update the evidence manifest with exact commands,
artifact paths, fixture mode, pass/fail classification, and commit hash
when available. Validate JSON manifests with `jq empty` or record why the
repo uses a non-JSON evidence format.

### 6. Promote or handoff

Default behavior is to carry one focused story through promotion when the
fix is narrow, reversible, and evidence-backed. Keep the change scoped to
the selected story, preserve existing product behavior outside the
acceptance criteria, and use the repo's normal validation. If the repo
expects commits and the user has authorized autonomous loop work, make one
focused commit per promoted item.

Hand off instead of implementing when the result requires broad product
direction, new fixtures/goldens, unclear data semantics, risky migrations,
security-sensitive behavior, irreversible state changes, or a
visual/product taste decision that would be expensive to unwind.

### 7. Reconcile

After verification, update exactly one verified story's status and append
evidence or a decision. Newly discovered child stories may be appended as
`candidate` only. Use this decision table:

| Evidence says | Status |
|---|---|
| aligned AC holds with evidence | `verified` |
| aligned AC fails in product behavior | `product-fail` |
| test/probe/selector fails but UI/product behavior is correct or unclear | `oracle-defect` |
| data cannot prove the claim | `fixture-gap` |
| local environment blocks proof | `env-gap` |
| story scope is too broad | `split-needed` |
| newer guidance contradicts the promise | `stale` |
| intended behavior is unresolved | `disputed` |

For each non-verified result, emit a handoff target:

- `product-fail` -> implementation ticket; for a finite fix, derive a
  `goal`-archetype loop (via `/loopgen`) with the failing acceptance criterion as the inventory
- `oracle-defect` -> evaluator/test task
- `fixture-gap` -> fixture/golden/data task
- `env-gap` -> dev-server/devslot/DX task
- `disputed` -> human product decision
- `stale` -> storyboard cleanup/supersession decision

For implemented stories, record the promoted change, evidence, validation,
commit when available, review questions, and remaining risk. For handoffs,
name the target and reason.

After a long autonomous run, or when the loop clearly shifts away from the
selected surface class, add a short retro note explaining what was
exhausted, where the frontier drifted, what evaluator bias may have caused
it, and what the next loop should target.

Before finalizing a promoted commit, check that the manifest, storyboard,
ledger/report, focused validation, and git commit all name the same story
and promise. Do not use passing tests as a proxy if they do not cover the
recorded acceptance criteria.

## Surface Taste Lane

Conditional — include this section when `{{LANE}} = Surface Taste Lane`.

This lane is still story-shaped: one persona, one promise, one focused
visible or interaction delta, evidence, decision record, and commit when
appropriate.

Surface Taste Lane primitive paths:

- **First-read intent:** what the eye understands first/second/third,
  whether the primary object/action is obvious, and whether labels imply
  the right destination.
- **Decision and comparison support:** whether the selected persona can
  compare the relevant items, values, states, or choices quickly.
- **State, feedback, and recovery:** whether idle, pending, success,
  empty, stale, partial, failed, cancelled, and recovered states are
  legible.
- **Flow ergonomics:** whether the workflow adds unnecessary clicks,
  waits, reversals, scroll, mobile awkwardness, or lost context.
- **Trust and interaction safety:** whether duplicate, stale, racy, or
  contradictory interactions can break trust.
- **Product character and surface polish:** whether the surface feels
  intentional, coherent, domain-specific, and polished using existing
  product language, data, tokens, and components.

Surface Taste Lane supporting gates:

- **Semantic fidelity:** when visible labels, states, controls,
  disabled/loading status, or navigation affordances change, browser/DOM
  evidence must show the mechanical contract matches the visual contract.
- **Evidence integrity:** visual claims require screenshots; behavioral
  claims require traces; mutation/safety claims require network evidence;
  automated claims require fresh command output; structural claims
  require code refs.

Default Surface Taste bundle: run first-read intent,
state/feedback/recovery, trust/interaction safety, and product
character/polish. Add decision/comparison for list, table, grid, card,
inventory, order, comparison, or browsing surfaces. Add flow ergonomics
for multi-step, mobile, modal, route-transition, form, or repeated-action
surfaces.

## Artifact discipline

Screenshots and evidence are subordinate to the storyboard. Store them
where the repo expects ephemeral or QA evidence:

- For exploratory/local loops, prefer `/tmp/story-loop/<run-id>/...`.
- For repo-owned evidence, use an existing docs/QA convention.
- Do not commit screenshot piles unless the repo or user explicitly wants
  a persistent evidence packet.

Every promoted story should have a manifest plus a short `verdict.md` or
board entry that answers what the evidence proves. Screenshots without a
verdict are weak memory.

## Forbidden moves

- Do not make broad, irreversible, or product-direction fixes inside
  Story Loop.
- Do not rewrite acceptance criteria to match observed behavior.
- Do not treat undocumented inferred stories as enforcement targets;
  record an Alignment Review before promotion.
- Do not treat code, tests, screenshots, or stale docs as product intent
  by themselves.
- Do not treat the storyboard itself as product intent. Before verifying
  or promoting an existing story, re-check at least one attached authority
  source; an old row, prior evidence, or a prior screenshot cannot certify
  that a promise is still intended.
- Do not run broad exploratory QA sweeps and call them story verification.
- Do not close disputes silently.
- Do not delete or overwrite prior evidence unless replacing a known-bad
  capture and recording why.
- Do not change fixtures, selectors, waits, mocks, or oracles merely to
  make a story pass.
- Do not let child-story discovery interrupt the current verification.
- Do not report `verified` without linked evidence and environment
  identity.

## Halt and escalate

Halt = emit `stop-and-summarize` when the storyboard is converged: every
aligned story is `verified`, `product-fail` handed off, or appropriately
classified; no authoritative source remains unprocessed; no observed UI
finding deserves promotion.

When no `ready` story exists, **do not halt** — continue discovery and
alignment-prep (see Iteration protocol §3, §4). The classification is the
point.

Before `stop-and-summarize`, perform a completion audit:

- restate the objective as concrete deliverables
- map each prompt requirement to artifacts: storyboard, state, manifest,
  evidence paths, validation commands, commits, and classified leftovers
- inspect the artifacts instead of relying on memory or prior summaries
- verify manifests parse and evidence paths exist when they are named
- check tracked git status and list any intentionally untracked local
  loop artifacts
- run or inspect a fresh source/browser/e2e re-grounding pass unless the
  immediately preceding iteration already did so
- set `halt_cause` and `halt_re-grounding` in `loop/STATE.md`

Escalate (rare, irreversible-only): see the Runner contract.

### Halt-cause classifier

When emitting `stop-and-summarize` or `escalate: <reason>`, label the
cause so the user (and the next derivation) can route it back:

- `derivation-gap` — blocked on something derivation could have asked
  for (lane, fixture, app URL, auth, …). Next derivation pass adds it
  to the Frontload audit.
- `genuine-escalate` — irreversible / external / authority-needed
  (product-direction change, irreversible data, source conflict
  requiring human judgment).
- `storyboard-converged` — legitimate completion.
- `signal-starvation` — no new source, no new candidate, no new
  alignment for the configured number of consecutive iterations; the
  frontier-novelty rule forced a re-grounding pass that yielded
  nothing, and `remaining_findings_classified` records why skipped
  findings were not promotable.
- `wrong-loop` — the work needs a different loop (evaluator blindness
  → the `frontier` archetype; known product-fail with a finite acceptance
  inventory → the `goal` archetype; target itself undefined → the `greenfield` archetype).

`derivation-gap` is the feedback signal: the Frontload audit was
incomplete; close it next run.

## Minimal output

When the iteration completes a verification, return:

```text
Storyboard changes:
- <story id>: <old status> -> <new status>, because <evidence/source>

Evidence:
- <path or link>

Evidence manifest:
- <path or none>

Spawned candidates:
- <child story id or none>

Handoffs:
- <target and reason, or none>

Review items:
- <alignment cost / human question / revisit trigger, or none>

Commit:
- <hash and subject, or not committed>

Retro note:
- <surface drift / evaluator bias / next target, when applicable>
```

If no story is `ready`, do not verify. Return:

```text
Storyboard changes:
- <candidate/alignment updates>

Alignment/review items:
- <questions, taste calls, or approval needed>

Candidate stories proposed:
- <story ids>

Verification:
- Not performed because no proof-ready story exists yet.
```
````

---

## Derivation notes

Placeholders populated during derivation (see SKILL.md):

- `{{PROVENANCE}}` — the loopgen provenance preamble.
- `{{MOTIVE}}` — one-sentence goal from the user (e.g., "verify the
  evidence-anchor workflow for the compliance officer persona").
- `{{FRONTLOAD_PREAMBLE}}` — resolved / defaulted / open-gap summary.
- `{{PRESSURE_SURFACE}}` — the pressure weather block (`primitives/pressure.md`),
  emitted only when ≥1 pressure object exists at compose time; stripped otherwise.
- `{{LANE}}` — selected lane. Common values: `Surface Taste Lane` (visual
  / product / frontend quality), or a domain-specific lane named by the
  repo. If absent from the user prompt, infer from the strongest guidance
  source and record the inference.
- `{{SURFACE_CLASS}}` — generic repo-local audience / workflow / surface
  name (e.g., "report viewer", "checkout flow"). Use names the repo
  itself uses; do not hard-code product-specific audiences.
- `{{STORYBOARD_PATH}}` — `docs/storyboard.md`. Repo-native machine-readable
  boards may be recorded as aliases in `loop/STATE.md`, but this canonical file
  still exists.

Drop the **Surface Taste Lane** section when `{{LANE}}` is not the taste
lane.
