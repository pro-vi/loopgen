# ADR 0001: loopgen does not own its runtime — no runtime-control grafts

- **Status:** Accepted
- **Date:** 2026-06-22
- **Deciders:** provi, Claude (Opus 4.8), Codex review
- **Supersedes:** the runtime-discipline plan's "external liveness observer" centerpiece (U1)

## Context

loopgen is a **compile-time prompt compiler**: it emits a markdown loop prompt
(`loop/PROMPT.md` + state files) that a *separate* runner (`/goal`, or any host)
executes by re-invoking the prompt each iteration. We grafted Deli AutoResearch's
runtime-discipline ideas into it. Most ported cleanly. One didn't: the **external
liveness observer** — a lease file the loop stamps, plus a watchdog that detects a
silently-dead loop and restarts it. It was the planned centerpiece; it survived
~20 review/verification rounds of hardening before the structural flaw surfaced.

## Decision

loopgen does **not** own its runtime, so it must **not** graft any mechanism that
requires runtime control — watchdogs, background monitors, self-spawned
supervisors, or anything needing a process that lives **outside the loop's own
failure domain**. Such mechanisms belong to whoever owns the runtime (the
runner / host), not to the emitted prompt.

## Rationale

- AutoResearch's heartbeat watchdog works *there* because AutoResearch **owns its
  runtime** (it's a framework orchestrating the whole run) — it can spawn a
  durable, out-of-band monitor.
- loopgen **emits a prompt for a runner it doesn't control.** It can make the loop
  *produce* a liveness file, but the *consumer* (the watchdog) has no portable
  home: a watchdog the loop self-spawns dies with the session it is watching (same
  failure domain), and some runners (e.g. Codex) cannot spawn a durable background
  process at all.
- The *nugget* — "an agent can't self-report its own death" — is real and
  motivated the idea. The *mechanism* — a watchdog — does not survive the move
  from owns-its-runtime to emits-a-prompt. A producer with no buildable consumer
  is dead weight.
- loopgen already holds the **portable** failure defense the runtime gap allows:
  crash **recovery** via commit-per-iteration + `loop/STATE.md`
  (`last_action` / `next_action`). It needs no liveness mechanism to resume after
  a crash.

## Consequences

Positive:

- A clean test for any future graft: *does it need a process outside the loop's
  failure domain?* If yes, it is out of scope for loopgen — push it to the runner.
- The shipped skill stays a pure prompt compiler with no runtime assumptions;
  emitted prompts are byte-portable across runners.
- Removed the single most review-churning surface in the project — the lease
  consumed roughly twenty review/verification rounds before being cut.

Negative:

- loopgen cannot, by itself, detect or recover from a *silently hung* (as opposed
  to crashed) unattended loop. That detection needs a runtime-owning watchdog and
  is explicitly the runner's / host's responsibility.
- An operator running an unattended loop on a non-owning runner has no automated
  liveness alarm; they rely on their own check-ins, or on building a watchdog in
  their own runtime.

## Revisit Triggers

- loopgen gains (or is paired with) a component that **owns the runtime** — e.g. a
  first-party `/goal` runtime that can spawn out-of-band supervisors. A watchdog
  then has a portable home and the lease can be reconsidered *there*, in the
  runtime, not in the compiler.
- A runner-agnostic, failure-domain-external liveness primitive becomes available
  (e.g. the host platform exposes a standard heartbeat/supervisor API the emitted
  prompt can target portably).

## References

- Merged: PR #5, commit `f74eb00` (ships U2 subagent catalog / U3 goal
  provenance+replan / U4 frontload horizon+restructure; U1 dropped).
- Full explored design + decision lineage:
  `docs/plans/2026-06-18-001-feat-loopgen-runtime-discipline-plan.md` (lineage
  v3.3; the U1 section is retained, marked **DROPPED**, as the record of what was
  explored and why it was cut).
- Source idea: Deli AutoResearch runtime harness (heartbeat watchdog / stall
  detection).
