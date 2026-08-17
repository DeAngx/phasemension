# Energy Audit Rule (Phase A — Locked)

Valid energy audit requires an explicit mechanical + configurational state.

For any computational representation in this project, an energy audit is considered **valid** only if the sampled state vector at each audit time includes at least:

## 1. Kinetic contribution

Enough to compute \(\frac{1}{2}mv^2\) (or the continuum analogue: velocity field / momentum density).

If the model has no kinetic degrees of freedom, this term is declared identically zero and that declaration is part of the audit record.

## 2. Configurational / potential contribution

Enough to compute the energy associated with the current arrangement of density, interface, or order.

Minimum acceptable forms:

- a potential \(V(x)\) or stored-energy density \(W(\text{strain}, \text{order parameters})\), or
- an explicit interface/surface energy term (e.g. phase-field free-energy functional), or
- a declared density-dependent internal energy \(u(\rho)\) when density is a primary field.

## 3. Intervention log

Every `do(...)` between \(t_0\) and \(t_1\) must contribute a recorded \(\Delta E\) (work and/or heat).

No state override is allowed without an accompanying Joule entry.

## Conservation check

```
E_obs(t0) + Σ ΔE_intervention(t0 → t1) = E_obs(t1)
```

within a declared numerical tolerance.

## Deliberately not required for Phase A exit

- Geometry / topology / information accounts as independent ledgers (later open question).
- Full thermodynamic completeness (temperature, entropy production, etc.) — only the energy balance needed to detect phantom Joules or silent interventions.
- A universal continuum formulation — discrete, continuum, or hybrid models are all allowed if they satisfy 1–3.

## Failure conditions (audit invalid)

- State vector lacks kinetic or configurational terms and does not explicitly declare them zero.
- Any intervention alters state without a logged \(\Delta E\).
- Energy drifts under pure observation beyond tolerance.

---

Phase A exit criterion met. Residual open questions ( sufficiency of energy as sole ledger; exact state vector per transition class) remain for later phases if needed.
