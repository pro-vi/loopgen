# frontload-audit (shared primitive)

## Purpose

The universal pre-flight every archetype runs before composing. Loops fail when
they self-terminate blocked on a decision the user could have made before the
loop fired; the cure is to **frontload every uncertainty** so iteration runs
through the night without blocking.

## Include when

Phase 1, always. Its output — the frontload preamble — fills the
`{{FRONTLOAD_PREAMBLE}}` slot in every composed prompt.

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
- **Latent-pressure mining** — before composing, ask "what does this system
  already care about?" — shared route wrappers, golden tests, a design system
  that punishes one-off components, schema changes that arrive with migration
  notes. Surface these as `source: mined` pressure objects
  (`primitives/pressure.md`) so the loop is bent by them before it acts.
  **Value is not mineable** (delight vs boring, speed vs polish, which
  abstractions to shed) — value is human-seeded `source: authored`. A repo with
  no such conventions mines nothing, and the pressure surface stays empty
  (byte-identical). Every `mined` row carries a provenance pointer to the
  concrete artifact it was mined from (the golden-test glob, the lint rule
  `file:line`, the migration-notes path), grep-confirmed to exist at compose —
  the same "confirm it's observable" discipline the budget rule uses. A mined row
  whose cited convention cannot be pointed at is downgraded to `source: authored`
  (needs human sign-off) or cut: without a provenance trail, a fabricated mined
  row that merely justifies a wanted edit is indistinguishable from a real
  convention. A `mined` row enters at the weakest authority — `strength: low`,
  `mode: salience` (slope-only) — so an over-eager or stale-but-present
  convention nudges attention without bending a gate; promotion to `burden` /
  `constraint` (a wall) needs the same reproduced tier-1/2 evidence a
  backpressure wall does (`primitives/pressure.md`), never the bare fact that
  the convention exists. (The benchmark-frontier overlay's oracle-integrity rows
  are `source: overlay`, a fixed contract — not `mined` — so this low/salience
  entry rule does not apply to them; see `primitives/benchmark-frontier.md`.)
- **Benchmark-frontier overlay** — for frontier-shaped tasks, bind a concrete
  benchmark/eval/harness object, evaluation unit, and durable evidence location,
  or record a derivation gap if benchmark language appears without an object. When
  the bound oracle is **trusted-or-mutated** (an LLM judge, a generated/minted
  answer key, or eval-set evolution), run the **Evaluator-integrity audit** (below).
  A loop with no bound oracle-object, or one over a deterministic non-LLM oracle,
  runs no audit and emits no integrity lines — the preamble is unchanged.
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

## Evaluator-integrity audit (eval / benchmark / frontier loops)

REQUIRED whenever frontload binds a benchmark/eval/harness object the loop
**trusts or mutates** — an LLM-as-judge, a generated/minted answer key, or
eval-set evolution. Such a loop grades its own homework, so the canon's
evaluator-under-test rule becomes an emission gate: **no candidate may author,
verify, and promote the evidence for its own acceptance.** The loop is **not
emittable** unless all eight properties are resolved, defaulted, or
escalate-marked, each against a grep-confirmable on-disk surface (the same
"confirm it's observable" discipline the budget and mined-row rules use). The
properties map 1:1 to the `### Oracle-integrity pressure` rows
(`primitives/benchmark-frontier.md`); this audit is their compile-time half.

Each property binds the same-named row in `benchmark-frontier.md` (P1–P8 in row
order — see the mapping table there):

- **P1 key-independence** (`oracle.ground-truth`) — every answer-key /
  expected-output the scorer reads is re-derived or verified by a channel OTHER
  than its generator (different-family model, deterministic transform, a round-trip
  whose transform is pinned/frozen in `BENCHMARK` and is not the candidate's own
  hypothesis, or recorded human spot-check), the method a field in `BENCHMARK`. A
  generator that writes both the input and the expected output with no independent
  check is non-emittable.
- **P2 judge-independence** (`oracle.judge-diversity`) — each judge role names its
  model family; any role sharing the generator's family does not pay
  `oracle.judge-diversity` (`claim_scope` stays `search_only`). Default-resolve into
  the `consult-capability` tier (tier-0 → human-look gate; tier-2/3 → cross-family).
- **P3 executed-negative-invariant** (`oracle.negative-executed`) — every exclusion
  that gates promotion ("no baseline strategy solves this") names the executable
  that PROVES it by running the proposed counter-strategy as an expected-red,
  against a **declared comparator boundary** (allowed tool class / budget /
  languages). An asserted-not-executed exclusion is non-emittable.
- **P4 repeat-discipline** (`oracle.n-replicate`) — any stochastic gate is computed
  at N≥`oracle-replicate-N` (frontload-tunable, default 3, alongside quiet-signal-N
  / stuck-attempt-N) as a pass-rate; a single seed (N=1) is `provisional` evidence
  that does not pay `oracle.n-replicate`, so `claim_scope` stays `search_only`
  (the candidate keeps its earned lifecycle status). Judge temperature pinned to 0
  or majority-vote. A single-seed binary stamped as a measured gap is non-emittable.
- **P5 expected-red control** (`oracle.expected-red`) — `BENCHMARK` binds ≥1
  expected-red and ≥1 expected-green control that run every iteration; a run whose
  expected-red scores green sets `eval_health: gamed` and checkpoints with
  `checkpoint_reason: evaluator_invalid`. Absent → non-emittable.
- **P6 provenance-not-drift** (`oracle.provenance`) — every field recording WHICH
  model judged rolls up the model that actually ran after fallback, never the
  resolved default.
- **P7 write-ahead ledger** (`oracle.write-ahead`) — every paid / multi-minute eval
  cell write-aheads an attempt/spend row before the call; a pipeline that only
  WARNs-and-continues on crash is non-emittable.
- **P8 measurement-receipts** (`oracle.receipts`) — the claim is bound to a receipt
  (oracle hash, scorer version, candidate hash, actual model, seed, tool policy, run
  id); a frozen scorer is not trusted unless the measurement path is also outside
  the candidate's control.

The trust trigger is itself recorded — `oracle_trust: trusted-or-mutated |
deterministic-frozen` under `frontload` — so the bind is grep-confirmable like the
budget / mined-row binds, not self-asserted. "Out-of-cone" independence
(different-family judge, non-generator key) is **recorded and audited at compose,
enforced at runtime**: the compiler caps the claim until a row cites an out-of-cone
executed artifact, but cannot prove a named sibling model is genuinely independent —
that verification is impl-side (a named residual, not a closed one).

For each unmet property do exactly one of the four frontload actions (resolve /
smallest-reversible-default / escalate-mark / resolve-into-policy). A loop with
**no** bound oracle-object, or one whose oracle is a deterministic non-LLM,
non-minted metric, runs no audit and emits no integrity lines — byte-identical.

## Derivation-gap concept

Anything neither resolved, defaulted, nor escalate-marked is a **derivation
gap** — a future block waiting to happen. The emitted prompt's
`halt-cause-classifier` flags `derivation-gap` halts so the next derivation
pass closes them. An unmet Evaluator-integrity property (above) is a derivation
gap that additionally sets `runnable: false` until closed — an oracle a loop
grades itself against is not emittable on hope.

## Composition notes

- Output: record under `loop/STATE.md` `frontload:` and fill the
  `{{FRONTLOAD_PREAMBLE}}` slot in `loop/PROMPT.md` naming exactly what was
  resolved / defaulted / left open.
- `cadence-shape: deferred-fire-and-forget` raises the completeness bar — no
  human is awake to answer a gap.
