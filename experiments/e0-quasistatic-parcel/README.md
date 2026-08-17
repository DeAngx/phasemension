# e0 — Quasi-static two-phase H₂O-like parcel (Phase E — Closed)

First computational experiment. Design and implementation locked for v0. Can be revised or replaced later.

---

## Files

| File | Role |
|------|------|
| `parcel.py` | Parcel state, pure observation, `do_set_phase_fraction`, conservation audit |
| `run_audit.py` | Demo sequence; exits non-zero on audit failure |

```bash
cd experiments/e0-quasistatic-parcel
python run_audit.py
# → PASS
```

---

## What it is

A single control volume (parcel) with phase fraction \(\phi \in [0,1]\).

- \(\phi = 0\) → liquid-like
- \(\phi = 1\) → high-pressure-ice-like

## State vector (Phases A + C)

| Quantity | Role |
|----------|------|
| \(\phi\) | phase fraction |
| \(\rho(\phi)\) | density between \(\rho_L\) and \(\rho_S\) |
| \(E_{\text{config}}(\phi)\) | configurational energy = latent + PV stand-in |
| \(E_{\text{kin}}\) | declared 0 (quasi-static) |
| Intervention log | list of \(\Delta E\) entries |

## Observation (pure, no side effects)

`get_phase()`, `get_density()`, `get_config_energy()`, `get_total_energy()`, `get_kinetic_energy()`

## Intervention

`do_set_phase_fraction(φ_new)` — computes and logs \(\Delta E\). No silent overrides.

## Conservation audit

```
E_obs(t0) + Σ ΔE_intervention = E_obs(t1)
```

Verified: residual 0 on demo sequence; observation purity holds.

## Declared scope (Phase D)

- Idealized quasi-static H₂O-like phase boundary on one parcel
- Does **not** claim to be ice, Earth, or programmable matter
- Does **not** implement harness
- Does **not** resolve spatial interfaces or kinetics

## Non-goals for v0

- Spatial phase-field / faceting
- Continuous harness term
- Temperature dynamics
- Real equation of state

---

*Phase E exit met for e0.*
