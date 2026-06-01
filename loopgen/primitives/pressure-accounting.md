# pressure-accounting (shared frontier primitive)

## Purpose

Frontier loops do not finish; they account for pressure. This primitive gives
generic frontier prompts a small checkpoint contract without requiring a
benchmark artifact system.

## Include when

Every prompt whose nearest archetype is `frontier`. It is universal for
frontier, independent of any benchmark-frontier overlay.

---

## Pressure record

Record these fields in the findings ledger or `loop/STATE.md`:

```yaml
pressure_status: open | paid | blocked | exhausted
pressure_debt: none | low | medium | high | explicitly_deferred
checkpoint_reason:
  plateau_after_active_pressure
  budget_exhausted
  evaluator_invalid
  risk_limit_hit
  target_gap_unresolved
  negative_result_saved
next_pressure: <trace/artifact/dimension/intervention to try next>
```

`pressure_status` names whether useful pressure remains. `pressure_debt`
names whether the current evidence is strong enough to support the claim.
`next_pressure` names the next evidence-producing move unless pressure has
been paid or explicitly deferred. `checkpoint_reason` is required for every
frontier checkpoint.

## Generic checkpoint rule

A generic frontier loop may checkpoint only after it has applied active
pressure or recorded why active pressure is blocked. A quiet ledger, green
cheap channel, or balanced homeostasis scan is not enough by itself.

Valid checkpoint states:

- `pressure_status: paid` with `pressure_debt: none`
- `pressure_status: exhausted` with a concrete `checkpoint_reason`
- `pressure_status: blocked` with `pressure_debt: explicitly_deferred` and the
  budget, scope, or authority that blocks the next pressure

Invalid checkpoint states:

- no pressure scan
- `pressure_status: open`
- `checkpoint_reason` omitted
- a claimed improvement whose evidence did not get stronger

## Storage rule

Do not invent a new artifact for generic frontier pressure. Use the existing
findings ledger, trace index, or `loop/STATE.md`. Heavier artifact roles belong
only to the benchmark-frontier overlay.
