# benchmark-frontier (frontier overlay)

## Purpose

Benchmark-frontier is a frontier overlay for optimization work with a concrete
benchmark, eval, or harness object. It adds artifact discipline for search,
promotion, and checkpointing. It is not a fifth archetype and not a weighted
classification axis.

## Activation

Activate only when frontload binds all three:

- a benchmark/eval/harness object with a concrete path, command, or artifact;
- an evaluation unit such as case, repo, prompt, fixture, trace, or scenario;
- an evidence location where results are durable enough to audit.

If the user says "benchmark" or "eval" but no object can be bound, emit a
derivation gap. Do not silently fall back to generic frontier and do not invent
artifact paths.

Record the overlay in provenance:

```yaml
archetype: frontier
overlays:
  - benchmark-frontier
classification_distance: unchanged
```

## Benchmark Frontier Mode

When active, insert this section into the frontier prompt.

### Artifact roles

Roles are invariant; filenames are defaults.

| Role | Default file | Contract |
|---|---|---|
| `DOMAIN_SPEC` | `loop/DOMAIN_SPEC.md` | fixed surface, mutable surface, eval unit, budget, leakage risks |
| `BENCHMARK` | `loop/BENCHMARK.md` | search set, holdout set, expected-green/red controls, metrics, timeouts |
| `CANDIDATES` | `loop/CANDIDATES.jsonl` | rows with candidate lineage, operator, hypothesis, status, eval artifacts |
| `FRONTIER` | `loop/FRONTIER.json` | best/Pareto members, evaluator health, pressure debt, checkpoint reason |
| `traces` | `loop/traces/<candidate>/<case>/evaluation.json` | raw evidence; missing or corrupt output counts as failure |

Repo-native markdown is acceptable only when it preserves the same fields and
can be audited mechanically.

### Candidate row contract

Each row records:

- `candidate_id`
- `parent_candidate_id` or `null`
- `operator`: `draft | debug | improve | ablate | stress | falsify | transfer | compress | consult | architect | build`
- `hypothesis`
- `dimension`
- `metric_vector`
- `status`
- paths to compliance, smoke, and search traces; holdout, adversarial, and
  meta-eval trace paths stay null until that pressure is applied

A row missing `hypothesis`, `operator`, or its compliance/smoke/search trace
paths cannot update the `FRONTIER` role.

Candidate rows are write-through state, not retrospective notes. Once a trace
exists for a candidate, the row must move out of `proposed` in the same
iteration, and the owning `FRONTIER`/`STATE` surfaces must reflect the earned
status before the runner may halt. If a tracked product/prompt/runtime diff was
created for the candidate, the candidate status and git status must close
together: accepted candidates are committed, rejected candidates are reverted,
and undecided candidates keep the loop on the same case instead of
checkpointing.

For repeated structural negatives, the candidate lineage must include the bridge
explicitly: a `consult` row for the trace-backed diagnosis, an `architect` row
for the saved structural plan, and a `build` row for the implemented probe/slice.
The build row cannot become a frontier member until a same-class rerun trace
demonstrates the structural change improved or falsified the candidate.

A status may not outrun its evidence or its verdict. A trace pays for a status
only when it is non-null, parseable, linked to this candidate and rung, and
records a verdict compatible with the claim:

- `holdout_confirmed` requires a `holdout_trace` recording a passing holdout
  verdict; `holdout_regressed` requires one recording a failing/regressing verdict.
- `pressure_paid` requires a stronger-pressure trace whose payload supports the
  claim: a passing `holdout_trace`, an `adversarial_trace` recording the required
  expected-green/expected-red control verdicts, or a `meta_eval_trace` bounding
  evaluator risk. A non-null path alone does not pay pressure debt.

Deferred pressure is not a candidate status; it is a `FRONTIER`-level fact
(`pressure_status: blocked`, `pressure_debt: explicitly_deferred`, with a named
`blocker`, `next_pressure`, and `claim_scope: search_only`).

### Candidate lifecycle

```text
proposed
  -> compliance_checked
  -> smoke_checked
  -> search_scored
  -> frontier_member | rejected
  -> holdout_confirmed | holdout_regressed
  -> pressure_paid
```

Deferred pressure is **not** a candidate status. A search winner whose stronger
pressure is blocked stays at its earned status (e.g. `frontier_member`) with the
unpaid traces `null`; the deferral lives on the owning `FRONTIER` record
(`pressure_status: blocked`, `pressure_debt: explicitly_deferred`, `blocker`,
`next_pressure`, `claim_scope: search_only`). This keeps "I gave up" from
reading as "I advanced a rung."

### Promotion rule

Search improvement earns a local promotion claim, not belief. After a new search
win, pressure debt remains open until holdout, adversarial, expected-red, or
meta-eval pressure is applied, or until the runner explicitly defers it because
budget, scope, or authority blocks stronger pressure.

If evaluator health is anything other than calibrated, the loop may claim
harness progress, not product progress.

### Oracle-integrity pressure

When the mutable surface includes the **evaluator itself** — new tasks, answer
keys, LLM judges, or rubric edits — the loop is editing the thing that grades it.
Karpathy's frozen-metric guarantee is gone, and one rule replaces it: **no
candidate may author, verify, and promote the evidence for its own acceptance.**
A promotion predicate must be computed from evidence *outside the candidate's
mutation closure*, and `claim_scope` may not outrun the weakest trust boundary in
that chain (generator ≠ oracle-author ≠ judge ≠ scorer ≠ promoter).

On overlay activation **when the bound oracle is trusted-or-mutated** (an LLM
judge, a generated/minted answer key, or eval-set evolution — never a
deterministic non-LLM, non-minted metric), seed these rows into `loop/STATE.md`
`pressure_objects` (rendered to `loop/PRESSURE.md`, re-read each pass). Each is
`source: overlay` — a fixed contract installed by the overlay, not a latent-mined
convention, so its provenance is the overlay activation + the bound oracle-object
(grep-confirmable) and it is **exempt from the `mined` low/salience entry rule**
(`primitives/frontload-audit.md`): it enters at `strength: high`, `mode: burden`,
`on_violation: owes_proof`, with a **pre-registered `satisfied_by`** that names a
tier-1/2 (`evidence-tier.md`) **executed** artifact authored **outside the
candidate's authority cone** — never the loop's own prose, never a non-null path alone:

| id | guards against | satisfied_by (pre-registered · executed · out-of-cone) | expires |
|---|---|---|---|
| `oracle.ground-truth` | a self-minted answer key | the key re-derived by a NON-generator route — a different-family model, a deterministic transform oracle, or a structural round-trip whose transform is **pinned/frozen in `BENCHMARK` with a receipt hash, never the candidate's own hypothesis transform** (minting `k = T(input)` then re-running the same `T` to "verify" is author = verifier — it pays nothing) — recorded per candidate | key changes |
| `oracle.judge-diversity` | a same-author judge | a judge family per role distinct from the generator family; a same-family verdict does not pay this row — `claim_scope` stays `search_only`, never `product_progress` | roster changes |
| `oracle.negative-executed` | an asserted exclusion | the proposed counter-strategy RUN as an expected-red and observed to fail the scorer (not a label), against a **declared comparator boundary** (allowed tool class / budget / languages — an undeclared boundary makes the run theater) | per candidate |
| `oracle.n-replicate` | a single-seed number | the gating metric at N≥`oracle-replicate-N` (frontload-tunable, default 3, alongside quiet-signal-N / stuck-attempt-N) as a **pass-rate**, not a 0/100 binary; a single seed (N=1) is `provisional` evidence that does not pay this row — the candidate keeps its earned lifecycle status and `claim_scope` stays `search_only` | per metric run |
| `oracle.expected-red` | a toothless scorer | a known-bad control that scored fail AND a known-good that scored pass THIS run; a green known-bad sets `eval_health: gamed` and checkpoints with `checkpoint_reason: evaluator_invalid` | per run (no carry-over) |
| `oracle.provenance` | a lying manifest | the recorded judge identity equal to the per-step post-fallback model actually used, byte-for-byte | per manifest write |
| `oracle.write-ahead` | a lost paid run | judge calls at temperature 0 (or recorded majority-vote) AND a write-ahead attempt/spend row appended before each paid or multi-minute cell | per paid cell |
| `oracle.receipts` | a driftable measurement | the claim bound to a receipt — oracle hash, scorer version, candidate hash, actual model, seed, tool policy, run id — so the printed number cannot drift or be gamed silently | per measurement |

Each row binds exactly one frontload audit property (`frontload-audit.md`, P1–P8
in this same order) and, where it cashes out per candidate, one trace field
(`references/benchmark-frontier-artifacts.md`). The 1:1 is stated here, never
inferred from a name:

| row | audit property | candidate trace |
|---|---|---|
| `oracle.ground-truth` | P1 key-independence | `oracle_check_trace` |
| `oracle.judge-diversity` | P2 judge-independence | judge roster in `BENCHMARK` |
| `oracle.negative-executed` | P3 executed-negative-invariant | `negative_control_trace` |
| `oracle.n-replicate` | P4 repeat-discipline | gap pass-rate |
| `oracle.expected-red` | P5 expected-red control | `eval_health_trace` |
| `oracle.provenance` | P6 provenance-not-drift | manifest model field |
| `oracle.write-ahead` | P7 write-ahead ledger | `eval_spend_ledger` row |
| `oracle.receipts` | P8 measurement-receipts | `receipt` |

**The coupling (the wall).** While ANY of these rows is `active`/unpaid,
`FRONTIER.claim_scope` MAY NOT be `product_progress`, no candidate may reach
`pressure_paid`, and `eval_health` is treated as not `calibrated` — the loop may
record harness progress only. A green search trace cannot retire an
oracle-integrity row; only its pre-registered executed artifact pays it, and an
unpaid-oracle verdict is read as tier-3 self-narrated prose (`evidence-tier.md`):
it may inform, it pays nothing. These rows are the **floor** of the trust chain,
below holdout / adversarial / meta-eval; they merge into the eval ladder below
(rung 5 adversarial controls pays `oracle.negative-executed` + `oracle.expected-red`;
rung 6 meta-eval pays `oracle.judge-diversity`). Deferral is a `FRONTIER`-level
fact (`pressure_status: blocked`, named `blocker`, `claim_scope: search_only`),
never a candidate status and never silent.

{{INCLUDE primitives/eval-ladder.md}}

### Green-trace rule

Green search traces, zero OPEN generic findings, and no changed files are not a
checkpoint. The loop must expand one of: candidate, case, control, metric,
project category, evaluator dimension, or artifact audit. If budget or external
authority blocks expansion, halt as `PAUSED_EXTERNAL` with
`pressure_debt: explicitly_deferred`, not as complete.
