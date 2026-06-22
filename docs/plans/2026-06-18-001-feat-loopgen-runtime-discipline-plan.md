---
title: Evolving loopgen with AutoResearch's runtime discipline (v3.3 — U1 dropped; ships U2/U3/U4)
type: feat
status: completed
date: 2026-06-18
origin: standalone — loopgen × Deli AutoResearch comparison (this session)
supersedes: v3.2 (lease deflation); v3.1 (readiness-hardened); v3 (deflation); v2 (fire-once); v1 (accepted-delta U11 versioning)
---

## Revision lineage

- **v1** — graft-by-mechanism + "accepted-delta U11 versioning." Killed by review: making a backward-compat probe's reference extensible is tautological.
- **v2** — fire-once reframe. loopgen is fire-once-and-consumed → no consumers pinned to old output → backward compatibility is not a real obligation. Dropped versioning/compat entirely; kept the correctness fixes. *(The U11 sigil + backward-compat framing are now fully retired from the repo — PR #4.)*
- **v3** — deflation. Threat model = **honest failure, not deception.** A prompted agent doesn't *go out of its way to cheat* — it drifts under context pressure, pattern-completes "looks done," confabulates, takes the locally-easy path. So don't *over-build* (or duplicate) accountability machinery; keep the anti-*honest-failure* defenses (most of which loopgen already has) and foreground the few genuine nuggets.
- **v3.1 (this) — readiness-hardened.** A 3-checker readiness pass against the post-cleanup repo. Corrected one thesis error (the integrity wall is anti-*optimism* for self-graded oracles, not "trained-RL theater"); carved out the spend ledger from the no-write-ahead claim; deflated U3 (its rule already ships); gave U1 a real design (it was the named centerpiece but undesigned); deflated U2's gate to the existing tier ladder; demoted U5 to backlog.
- **v3.2 (PR-review deflation — this PR's commits) — U1 lease reduced to liveness-detection-only.** PR review (Codex) showed the owner-record / `owner_id` / CAS **ownership** layer is incompatible with `/goal`'s file-only re-invocation (a session can't recall a self-minted id across iterations → it self-supersedes) and that a durable owner ref blocks future runs. Resolved by removing ownership from the running loop entirely: the shipped lease is just an untracked `loop/LEASE.md` heartbeat (`{iteration, iteration_started_at, expected_deadline, status}`, advancing-deadline) that an external observer reads; mutual exclusion / ownership / identity / ref-lifecycle / safe restart moved wholly to the **deferred watchdog**, with its open problems named.
- **v3.3 (this PR, final) — U1 DROPPED entirely.** Even deflated, the lease only *produces* a liveness file; its value needs a *consumer* — a watchdog that detects the blown deadline and acts. That watchdog must be launched **outside the loop's failure domain**, which requires runtime ownership loopgen structurally lacks: it emits a *prompt* for a runner it doesn't control. A self-spawned watchdog dies with the session that spawned it, and some runners (e.g. Codex) can't spawn one at all. The *nugget* (an agent can't self-report its death) is real, but the *mechanism* (a watchdog) doesn't port from AutoResearch's **owns-its-runtime** context to loopgen's **emits-a-prompt** context — a mis-graft. loopgen already keeps the portable half: crash **recovery** via git + STATE. Dropped U1 entirely (the `lease-protocol` primitive, the `{{LEASE_MAINTENANCE}}` wiring across the four bodies + `composed-prompt.md`, and the `SKILL.md` / `frontload-audit.md` hooks). The PR ships **U2 + U3 + U4** — all runtime-independent. **The durable boundary this established is recorded in `docs/adr/0001-loopgen-does-not-own-its-runtime.md`.**

---

## The gold nuggets — what's actually worth taking from AutoResearch

The headline: **loopgen has independently reinvented most of the honest-failure defenses already.** The genuine adds are narrow.

| Nugget | Honest failure it addresses | loopgen today | Action |
|---|---|---|---|
| **External liveness observer** (lease + tiny watchdog) | the loop **dies silently** — session death, hang, context overflow. Silent *and* expensive. | **absent** (crash *recovery* via git + STATE *is* present) | ~~ADD~~ → explored as U1, **DROPPED in review (v3.3)** — no consumer is buildable where loopgen runs (watchdog needs runtime ownership loopgen lacks) |
| **Subagent patterns A–D** | can't parallelize, can't poll a long job, no cheap independent second look | partial (consult-tiers, no catalog) | **ADD** (capability) |
| Goal: provenance ≠ progress/closure | optimism: *"I committed code → progress"* with no acceptance pass | **mostly already has** (`evidence-tier` tier-4 + goal-body Invalid-pass-evidence) | thin reinforcement + the one new bit |
| "Restructure, don't retune" on stall | cognitive-loop — trying harder at the same dead end | partial (`same-family` admissibility) | reinforce, 1 line |
| Frontload / persist-to-files / no-blocking | honest *blocking* + *context loss* | **already has** | leave + tiny horizon/context add |
| Stall detection (no-new-signal → act) | honest *drift* | **already has** (`signal-starvation`, quiet-signal) | leave — no reducer cathedral |
| Commit-per-iteration recovery | crash mid-run | **already has** (end-of-iteration transaction) | leave — git is recovery |
| Oracle-integrity wall (no candidate authors **+** verifies **+** promotes its own evidence) | optimism: the loop over-trusts a *self-graded oracle* | **has it for eval loops** (benchmark-frontier evaluator-integrity audit, when a benchmark/eval/harness object is trusted or mutated) | leave — present where eval-loops self-grade; extending to other archetypes is a deliberate non-goal, **don't hoist/duplicate** |

So the real grafts came down to: **the subagent-pattern catalog** — plus a **thin goal reinforcement** for the one closure check that's slightly under-stated for `goal`, and a light frontload touch-up. (The external liveness observer was explored as U1 and **dropped in review** — its watchdog consumer can't be built where loopgen runs; see lineage v3.3.)

---

## Architecture Decision (deflated)

**Threat model = honest failure (drift / forgetting / optimism), not deception.** Consequence:

- **One paranoid gate: closure.** A false *"done"* is the only failure that's silent *and* expensive. Spend the paranoia there — *run the actual check before claiming done; the agent's opinion is not evidence* — and let everything else ride (honest mistakes are loud and cheap to redo).
- **Graft only the genuine nuggets, in their lightest form.**
- **Explicitly NOT building** (over-built or already-present): the oracle-integrity *hoist*, write-ahead/ACID *iteration-state* recovery, the typed-observation-interface + single-reducer + priority-lattice.
- **Rationale (Simplicity):** the plan should be *smaller* than what loopgen already is.

**Corrected boundary (the v3 thesis error).** v3 framed the integrity wall as "trained-RL theater, 99% prompted = theater." That's wrong. The wall is about a **self-graded oracle** — *the candidate authors, verifies, and promotes its own evidence* — which is **anti-optimism (an honest failure), not anti-cheat**, and is common in *prompted* research/eval loops, not just trained-RL ones. loopgen already runs it **for benchmark-frontier / self-graded *eval* loops** (frontload requires the evaluator-integrity audit when a benchmark/eval/harness object is trusted or mutated — `frontload-audit.md`) — **not universally.** We don't HOIST it to every self-graded archetype: that extension is a deliberate non-goal (anti-optimism here is a judgment call, and duplicating the apparatus is the over-build) — **not** a claim that coverage is already universal. The thing to avoid is *duplicating* it into a parallel apparatus.

---

## Implementation Units

> **Build order** (post-readiness): **U4 + U3 are ready now** (small, low-risk) → **U1** (now designed → buildable, the high-value graft) → **U2** (deflated → buildable). **U1 and U2 both edit the same `SKILL.md` regions** (shared-primitive list, STATE-key contract, artifact tables, read contract) — sequence them or do one consolidated `SKILL.md` pass; no logical cycles.

### U1. External liveness observer (lease spec) + git-backed recovery  *(the centerpiece — now designed)*

> **❌ U1 was DROPPED — nothing below ships (PR review; see lineage v3.3).** The lease delivers value only through a *consumer* (a watchdog that detects the blown deadline and acts), and that watchdog must run **outside the loop's failure domain** — which requires runtime ownership loopgen lacks (it emits a *prompt* for a runner it doesn't control; a self-spawned watchdog dies with the session, and runners like Codex can't spawn one). The *nugget* (an agent can't self-report its death) is real; the *mechanism* (a watchdog) doesn't port from AutoResearch's owns-its-runtime context. loopgen keeps the portable half — crash *recovery* via git + STATE. **The entire U1 design below is kept only as the decision record of what was explored and why it was cut; none of it is in the shipped skill.**

- **Goal:** Cover the one honest failure loopgen can't currently survive — the loop **dying** unobserved — without binding loopgen to a runtime and without ACID machinery.
- **Why it's the nugget:** an agent cannot self-report its own death; a `last_seen` it writes then hangs on looks healthy forever. This needs an *external* observer.
- **Emission gate (concrete):** emit `loop/LEASE.md` for the **overnight/unattended cadences** — `cadence-shape ∈ {deferred-fire-and-forget, checkpoint-gated}` (both "run while you sleep, check periodically") — **plus** a frontload opt-in flag so an operator leaving a `sync`/`chapter` loop running unattended can force it on. loopgen has no attended/unattended axis; cadence-shape is the available signal and the frontload flag is the override. Interactive `sync`/`chapter` loops without the flag omit the lease (empty-gate stripping, byte-stable when off).
- **Lease schema** (`loop/LEASE.md`, rendered from `loop/STATE.md` each iteration — STATE is source of truth):
  ```yaml
  run_id:               # stable id for this loop instance (set once at bootstrap)
  runner_id:            # id of the current runner/session (changes on takeover)
  generation:           # monotonic int; the CAS / fencing value (see Acquisition)
  iteration:            # current iteration number
  iteration_started_at: # ts, set at step 0
  heartbeat_at:         # ts, stamped EVERY step 0 (process is moving) — independent of progress
  last_progress_at:     # ts, advances ONLY on verified progress — feeds stall detection, NOT liveness
  expected_deadline:    # iteration_started_at + ttl
  status:               # running | checkpointed | paused-external
  ```
  `ttl` = the per-iteration budget; default conservative (e.g. 2h) or the context/horizon budget U4 sets at frontload.
- **Acquisition (split-brain safe — fencing alone is not):** mutual exclusion is an **atomic compare-and-swap on a single owner record**, *not* "higher token wins" (two restarters can both read generation N and both write N+1, and neither sees a higher value). **Normative mechanism:** `git update-ref refs/loopgen/lease <new> <expected-old>` — git refs do native CAS, so a stale owner's update fails atomically and there is no lock to leak. The owner record holds `(generation, runner_id)`; a new owner increments `generation`; after writing, the runner **re-reads and aborts if it no longer owns the ref** (closes the read-modify-write race). `generation` is the monotonic fencing value carried *downstream* so a superseded runner's late writes are ignored — a staleness tag, not the mutual-exclusion mechanism. (A plain `O_EXCL` lockfile is a *future, runner-specific* alternative — it would need its own stale-owner removal + late-writer race rules, which CAS avoids.)
- **Liveness computation (worked example — makes the spec reviewable *without* the watchdog).** An observer reads LEASE in this **precedence order**:
  - **hung** — `status == running` AND `now > expected_deadline` — *wins regardless of recent progress* (started, blew its deadline).
  - **idle/done** — `status ∈ {checkpointed, paused-external}` (not a failure).
  - **alive** — otherwise, `heartbeat_at` fresh within ttl.
  `last_progress_at` is a **separate** concern (verified progress → stall detection) and is **not** used for liveness — conflating them yields a loop that looks dead while working, or alive while hung. A restarter acts **only on `hung`**, after the preconditions below.
- **Restart preconditions** (checklist an external restarter verifies before relaunching): (1) LEASE present + parseable; (2) `now > expected_deadline`; (3) `status == running`; (4) worktree is committed-or-recovery-checkpointed (no silent in-flight diff); (5) it wins the owner-record CAS — no live owner with a higher `generation`; (6) restart count under a cap.
- **Recovery stays git (iteration-state only):** loopgen already commits per accepted iteration; on resume `git status` + STATE (`last_action`/`next_action`) is the truth. **No `pending_op`/precondition-sha/ACID for iteration state.** **Carve-out:** the metered-**spend** write-ahead ledger (`frontload-audit` budget property *d*) **stays** — paid tokens aren't git-revertable; the no-write-ahead claim is scoped to iteration-state recovery, not spend accounting.
- **Files:** Create `loopgen/primitives/lease-protocol.md`; Modify `loopgen/SKILL.md` (declare the gated `loop/LEASE.md` artifact role + the new STATE keys: `run_id`, `runner_id`, `generation`, `iteration_started_at`, `heartbeat_at`, `last_progress_at`, `expected_deadline`, `status`).
- **Patterns to follow (by section name, not line number — runner-contract.md line numbers drift):** `runner-contract.md` **"Unattended corollary"** + **"External ceilings… Preserve the worktree"** paragraph (crash-recovery language — keep, don't grow); `benchmark-frontier.md` (gated artifact emission); `pressure.md` empty-gate stripping (the gate mechanism).
- **Acceptance (buildable now — no watchdog required):** (a) compose a `deferred-fire-and-forget` (or `checkpoint-gated`) loop → `LEASE.md` emitted with all fields; a `sync`/`chapter` loop without the unattended flag → omitted (byte-stable). (b) STATE carries the `runner_id`/`generation` + heartbeat/progress fields. (c) `lease-protocol.md` contains the worked liveness-computation example AND the acquisition CAS sequence a reviewer can trace by hand (spec sufficiency is paper-reviewable). This replaces the unfalsifiable "external observer can act."
- **Verification:** lease emitted on the right gate; fields sufficient for the worked liveness computation; recovery needs only git + STATE.

### U2. Subagent-pattern catalog A–D (gated on the existing tier ladder)
- **Goal:** Let a composed prompt use parallel/independent subagents when the channel exists — a capability, not a leash.
- **Approach (deflated gate):** B parallel fan-out (investigate / refute / cross-domain), C long-experiment polling (auto-diagnose-resubmit), D an independent cheap re-check. **Gate on the existing `consult-capability` tier-0..3** — *not* a new per-capability detection vocabulary (which doesn't exist; inventing it is the over-build this plan avoids):
  - **A** (single-agent iteration) is **not** a catalog addition — it is the existing iteration protocol every body already emits. The `{{SUBAGENT_PATTERNS}}` block adds only **B/C/D**.
  - **D** (cheap second look) — tier-1 as a human-look gate; tier-2+ programmatic.
  - **B** (parallel fan-out) — tier-3 (rich fabric: blind adversarial + multi-modal).
  - **C** (long-experiment polling) — tier-3, or where frontload binds a pollable job channel.
  Accept that consult-tier ≈ *channel richness*, not exact capability — a deliberate simplification. At **tier-0 the `{{SUBAGENT_PATTERNS}}` block is fully stripped → byte-stable** (the loop runs single-agent via the existing protocol). D is framed as "a cheap second look," not an anti-cheat tribunal.
- **Placement:** add `{{SUBAGENT_PATTERNS}}` to the section-order union in `composed-prompt.md` adjacent to the action/consult machinery, carried by all four bodies, gate-stripped exactly like `{{PRESSURE_SURFACE}}` (mirror the pressure surface's gated placement + strip rule; as shipped the order is lease 6a / pressure 6b / subagent 6c).
- **Files:** Create `loopgen/primitives/subagent-patterns.md`; Modify the four bodies (gated `{{SUBAGENT_PATTERNS}}`), `loopgen/templates/composed-prompt.md` (section order + gate step), `loopgen/SKILL.md`.
- **Patterns to follow:** `pressure.md:14-21,46-61` (empty-gate stripping + placement); `consult-capability.md` (the tier-0..3 ladder); `frontier-body.md:196-220` (the existing Consult→Architect→Build bridge it complements).
- **Test scenarios:** *Happy:* tier-3 → B/C/D present. *Edge:* tier-0 → `{{SUBAGENT_PATTERNS}}` fully stripped, byte-stable (loop runs single-agent via the existing protocol). *Integration:* D used as a quick independent re-read, not a required gate.
- **Verification:** patterns emit only at/above their tier; tier-0 byte-stable; nothing forces them.

### U3. Goal: provenance ≠ progress/closure + item-scoped replan  *(deflated — no new primitive)*
- **Goal:** Close the narrow remaining gap for `goal`: provenance (commit/diff/command-success) is *neither closure nor progress*. The repo **already** gates closure (`oracle-principles` FIXED≠CLOSED; goal-body's Invalid-pass-evidence) and already ranks commit-log as negative-only (`evidence-tier` tier-4) — so do **not** create a duplicate `goal-evidence.md` four-tier primitive.
- **Approach:** two thin goal-body edits, layered on the existing **Verifier-discipline** section (don't restate pass/fail evidence):
  1. **copy the exact `evidence-tier` tier-4 rule text** into goal-body as a *local* progress rule — `goal` does **not** emit the standalone signal-hierarchy (`composed-prompt.md` excludes it), so a bare *citation* would dangle; the emitted goal prompt must carry the rule itself (provenance / commit-log isn't *progress*, so the stall counter can't reset on a bare commit);
  2. the one genuinely-new bit: **item-scoped replan/decompose** inserted into the iteration protocol *ahead of* the `wrong-loop` reroute (an item that resists the same approach twice gets replanned/decomposed before the whole loop is declared the wrong archetype).
- **Files:** Modify `loopgen/templates/bodies/goal-body.md` only. (No new primitive; no `SKILL.md` change.)
- **Patterns to follow:** `evidence-tier.md` tier-4; `goal-body.md` "Verifier discipline" / Invalid-pass-evidence + the iteration protocol's STUCK→switch and `wrong-loop` reroute (insert replan just before it).
- **Test scenarios:** *Conformance:* substantial commit, acceptance oracle still fails → not progress, item OPEN, closure forbidden. *Edge:* one item resists the same approach twice → item-scoped replan, *then* (if still stuck) wrong-loop.
- **Verification:** the emitted `goal` prompt *contains* the progress rule (self-contained, no dangling cite); treats provenance as neither progress nor closure; replan precedes reroute; no duplicate evidence section.

### U4. Light frontload extensions + a one-line "restructure-don't-retune"
- **Goal:** Two cheap honest-failure adds at compose time; no new machinery.
- **Files:** Modify `loopgen/primitives/frontload-audit.md` (a **new, distinct** horizon/context-sizing checklist item — *not* folded into the metered-$ `## Budget policy` block, which is the six-property rule for paid+irreversible resources and doesn't fit a context window); and `loopgen/templates/bodies/frontier-body.md` (`same-family` admissibility) for the one-line reinforcement: *when stuck, change the constraint/environment, not the parameters.*
- **Approach:** compose-time only; no emitted-contract change beyond the frontload preamble. Horizon-sizing is **compose-time judgment** (no hard "long" threshold) → the testable acceptance is the byte-identical-when-inapplicable invariant, plus the recommendation surfacing in the frontload preamble. Do **not** build a stall reducer — `signal-starvation` + quiet-signal + `same-family` already cover drift.
- **Patterns to follow:** `frontload-audit.md` checklist items (mirror an existing item's shape, *outside* the Budget policy block); `frontier-body.md:338-356` (same-family admissibility).
- **Test scenarios:** *Edge:* long horizon + weak evaluator → frontload preamble recommends a sub-goal split. *Test expectation:* otherwise no emitted change (byte-stable).
- **Verification:** oversized horizon / context surfaced in the frontload preamble; stall path names restructure-over-retune.

---

## What we explicitly did NOT build (and why that's correct)

| Cut | Why |
|---|---|
| Oracle-integrity **hoist / duplication** to all archetypes | the wall (no self-authored-and-promoted evidence) is a real anti-optimism defense, but it **already lives on benchmark-frontier and fires for benchmark-frontier / self-graded eval loops** — duplicating it into a parallel apparatus is the over-build. |
| Write-ahead / ACID **iteration-state** recovery (`pending_op` + precondition-sha) | git + commit-per-iteration already recovers iteration state; a dirty worktree is visible and revertable. **(The metered-*spend* write-ahead ledger stays — paid tokens can't be reverted.)** |
| Typed-observation interface + single reducer + priority-lattice | loopgen's existing stall detection covers honest drift; the reducer's complexity (and its own double-count/replay bugs) solves a determinism the prompted agent doesn't need. |
| Backward-compat regime / versioning / immutable fixtures | v2 cut it (fire-once); v3.1 confirms it's fully retired from the repo (PR #4). |
| A new per-capability detection vocabulary for U2 | inventing async-polling/isolation/judge-independence detection is the over-build; map A–D onto the existing tier ladder instead. |

## Backlog (not units in this plan)

- **Snapshot linter** (former U0/U5) — a dev-time mechanical renderer + golden diff to catch accidental cross-archetype drift when editing shared primitives. Adopt-if-needed; **not a dependency of anything** (the deflation removed the equivalence-claiming refactors that were its only hard rationale). Prereq before building: an `input.json` fixture schema + a **machine-readable gate declaration** (so the renderer expands `{{INCLUDE}}` + substitutes + strips, and never re-encodes composition policy → "shadow compiler"). Keep it out of the minimal set until shared-primitive churn actually warrants it.

## Scope Boundaries
- No runtime binding (the lease is an emitted spec; the watchdog impl is deferred).
- No new classification axes; no expansion/duplication of the integrity machinery.
- Deferred: S13 domain-pipeline overlay, S14 quality-gate ladder, the watchdog *implementation* (U1 ships the spec + a buildable paper-reviewable acceptance check). If S13 ever lands a trained-reward loop, revisit there.

## Net shape
**Shipped: 1 real graft (U2 subagent catalog) + 1 light touch-up (U4) + 1 thin goal-body reinforcement (U3).** U1 (the liveness lease) was **dropped in PR review** — its watchdog consumer can't be built where loopgen runs (lineage v3.3); the portable failure defense, crash *recovery*, loopgen already had via git + STATE. Snapshot linter → backlog. Far smaller than the surface it edits, because loopgen already holds most of the honest-failure defenses.
