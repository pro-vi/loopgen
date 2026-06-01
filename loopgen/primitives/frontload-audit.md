# frontload-audit (shared primitive)

## Purpose

The universal pre-flight every archetype runs before composing. Loops fail when
they self-terminate blocked on a decision the user could have made before the
loop fired; the cure is to **frontload every uncertainty** so iteration runs
through the night without blocking.

## Include when

Phase 1, always. Its output — the frontload preamble — is prepended to every
composed prompt.

## The resolve / default / escalate procedure

For each checklist item, do exactly one of:

1. **Resolve now** — if the host has an AskUserQuestion-style tool, use it;
   otherwise print the uncertainty prominently so the user can answer before
   launching.
2. **Default + Alignment Review** — pick the smallest reversible default and
   record problem · options · chosen contract · rollback trigger. Reversible at
   iteration time.
3. **Escalate-mark** — only for the truly irreversible **one-time** acts
   (public-publish, secrets, product direction with unclear rollback).
4. **Resolve into a budget/quota policy** — REQUIRED for any **metered +
   irreversible** resource the loop consumes **repeatedly while unattended**
   (paid-API $, cloud compute, rate-limited quota). Escalate-marking it is NOT
   enough — at runtime it becomes an interactive block or a silent overspend, the
   exact unattended failure mode. Resolve it into an operative `## Budget policy`
   section in `PROMPT.md` with six properties: **(a)** cap in the unit the harness
   actually **measures** — grep the harness to confirm it's observable; if the
   human wants another unit, pin a conversion table (e.g. tokens are logged but
   USD often has no price table → cap in tokens, not dollars); **(b)** the
   human-authored ceiling on a **read-only** surface (PROMPT.md / env), never in
   loop-rewritten state (lost-update race); **(c)** over-cap work **deferred
   (logged + resumable)**, never AskUserQuestion, never idle; **(d)** a
   **write-ahead spend ledger** so a mid-iteration crash fails closed; **(e)**
   **per-atom re-check** (no mid-flight kill assumption — already-spent tokens
   aren't refunded); **(f)** the one-time **bootstrap/instantiation cost costed
   separately** so a cap is never silently insufficient. A loop that can spend
   unattended without all six is not emittable. For a single *bounded* paid action
   a one-line authorized-or-defer rule suffices; free-only loops emit no budget
   section. (Dogfooding: mdtools hybrid-pareto `/goal` loop, 2026-05-29 — a "soft
   budget" `gaps_flagged` line let the loop block on `AskUserQuestion` at the first
   paid frontier sweep; resolved into its `## Budget policy`.)

## Universal checklist (shared by all archetypes)

- **Motive** — one-sentence goal.
- **Evidence surface** — build / test / run commands; artifact / ledger /
  findings paths.
- **Scope manifest** — allowed / forbidden globs, or `none`.
- **Known false-green zones** — tests / suites that pass without validating.
- **Forbidden shortcuts** — `--no-verify`, mocked integration, assertion-free
  fixtures, snapshot refresh without semantic proof.
- **Artifact locations** — where the queue, traces, and metrics live.
- **Consult availability** — detect the `consult-capability` tier here.
- **Benchmark-frontier overlay** — for frontier-shaped tasks, bind a concrete
  benchmark/eval/harness object, evaluation unit, and durable evidence location,
  or record a derivation gap if benchmark language appears without an object.
- **Parameters / thresholds** — quiet-signal N, stuck-attempt N, cash-out N.
- **Metered/irreversible resources** — any paid tier or quota the loop consumes
  repeatedly while unattended (paid-API $, cloud compute, rate-limited quota). If
  present, resolve into a budget/quota policy (procedure step 4) — never a bare
  escalate-mark, which becomes a runtime block or silent overspend.

Each archetype adds its own items (named in `archetypes/*.md`): frontier —
evaluator tier, ramp stages, two reward channels, frontier vector; goal —
criteria source, authority order, final-verify, dependency topology; story —
lane, surface class, storyboard path, fixtures, app URL; greenfield — target
adjacency, INTENT hypotheses, model identity, paid APIs, preloop checklist.

## Derivation-gap concept

Anything neither resolved, defaulted, nor escalate-marked is a **derivation
gap** — a future block waiting to happen. The emitted prompt's
`halt-cause-classifier` flags `derivation-gap` halts so the next derivation
pass closes them.

## Composition notes

- Output: record under `loop/STATE.md` `frontload:` and prepend a frontload
  preamble to `loop/PROMPT.md` naming exactly what was resolved / defaulted /
  left open.
- `cadence-shape: deferred-fire-and-forget` raises the completeness bar — no
  human is awake to answer a gap.
