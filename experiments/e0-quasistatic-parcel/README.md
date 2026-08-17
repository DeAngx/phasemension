# e0 — Quasi-static two-phase H₂O-like parcel (Phase E design — Locked)

First computational experiment. Design is locked; implementation can be revised or replaced later. Other experiments can be added under `experiments/` without reopening this design.

---

## What it is

A single control volume (parcel) that can sit in phase A (liquid-like) or phase B (high-pressure-ice-like), or a mixture defined by a phase fraction \(\phi \in [0,1]\).

## State vector (Phases A + C)

| Quantity | Role |
|----------|------|
| \(\phi\) | phase fraction (0 = liquid-like, 1 = ice-like) |
| \(\rho(\phi)\) | density between \(\rho_L\) and \(\rho_S\) |
| \(E_{\text{config}}(\phi)\) | configurational energy = latent + PV stand-in |
| \(E_{\text{kin}}\) | declared 0 (quasi-static) |
| Intervention log | list of \(\Delta E\) entries |

## Observation (pure, no side effects)

- `get_phase()` / phase fraction
- `get_density()`
- `get_config_energy()`
- `get_total_energy()`

Energy must not drift under pure observation.

## Intervention

- `do_set_phase_fraction(φ_new)` — sole state-changing op for v0
- Computes \(\Delta E = E_{\text{config}}(\phi_{\text{new}}) - E_{\text{config}}(\phi_{\text{old}})\) and appends to intervention log
- No silent overrides

## Conservation audit

```
E_obs(t0) + Σ ΔE_intervention = E_obs(t1)
```

Run after every intervention. Fail if violated beyond declared tolerance.

## Declared scope (Phase D)

- Idealized quasi-static H₂O-like phase boundary on one parcel
- Does **not** claim to be ice, Earth, or programmable matter
- Does **not** implement harness
- Does **not** resolve spatial interfaces or kinetics

## Exit criterion

- Runnable (script or notebook)
- Observation functions pure; every intervention logs ΔE
- Audit passes on a short sequence of phase-fraction changes
- Describable in locked vocabulary without embarrassment

## Non-goals for v0

- Spatial phase-field / faceting
- Continuous harness term
- Temperature dynamics
- Real equation of state

---

*Design locked. Implementation is the remaining work to fully close Phase E.*
