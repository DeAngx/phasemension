# Observation vs Intervention

Structural boundary for any model or code in this project.

Drawn from the distinction formalized in causal inference (Pearl's do-calculus): observing a state `P(E|X)` is not the same as intervening to force a state `P(E|do(X))`.

When the quantity of interest is energy (Joules), mixing the two produces conservation violations and phantom energy.

---

## Observation (passive tracking)

- Sample existing state. Do not alter trajectory.
- System boundary treated as closed with respect to the measurement.
- Total energy must be constant. Change without intervention = numerical bug or representation error.
- Code: pure functions only (`get_kinetic_energy()`, `sample_temperature()`, etc.). Zero side effects.

## Intervention (active manipulation)

- Inject or extract energy, change constraints, or force a variable to a value.
- Energy or work crosses the boundary. Baseline changes by the exact Joules of the intervention.
- Code: every state-altering operation must return or log ΔJoules (`apply_force()`, `add_heat()`, `clamp_...()`, etc.).
- No silent overrides. `do(v = 0)` requires an explicit work calculation for the velocity change.

## Conservation audit

Required check for any computational representation:

```
Observed Energy(t0) + Σ Intervention Joules (t0 → t1) = Observed Energy(t1)
```

Within floating-point tolerance. Failure means the model is leaking or generating phantom Joules.

## Relation to harness

A harness that sustains a non-default density or topology is continuous intervention. Its energy throughput must remain visible in the ledger. Persistence is not free; the cost is part of the mechanism being studied.

## Relation to retreat

Retreat is not refusal to intervene. It is refusal to intervene without accounting for the Joules, and refusal to treat intervention as if it were observation.
