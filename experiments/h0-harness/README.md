# h0 — Harness as explicit intervention (Phase H)

**Constructive only.** Phase B showed Earth water phases do not supply a natural harness. This experiment does not claim otherwise.

Harness here means: continuous (or stepped) work by an agent to keep state **away from a declared ambient preference**, with every tick logging ΔE.

---

## Model

- Parcel state: phase fraction `φ ∈ [0, 1]`
- Declared ambient preference: `φ_ambient` (default `0` — liquid-like preference in model units)
- Configurational energy: same family as e0 (`latent + PV` stand-in on `φ`)
- Dissipated account: `E_dissipated` — where harness work goes (heat/bath stand-in inside the control volume)
- Observed energy: `E_obs = E_config + E_dissipated`

### Interventions

| Call | Effect |
|------|--------|
| `do_set_phase(φ)` | Sets φ; logs ΔE from config change |
| `do_engage_harness()` | Arm hold; no energy by itself |
| `do_release_harness()` | Disarm |
| `do_harness_tick(dt)` | If engaged: `cost = κ \|φ - φ_ambient\| dt`; add to `E_dissipated`; log ΔE = cost. φ unchanged |

Holding **at** ambient → cost ≈ 0.  
Holding **off** ambient → cost grows with `|φ - φ_ambient|` and time.

### Audit

```
E_obs(t0) + Σ ΔE_intervention = E_obs(t1)
```

Pure observation does not drift. Silent holds forbidden (no cost without log).

---

## Declared scope (Phase D)

- Idealized controller cost for non-ambient hold
- Does **not** claim natural planetary harness
- Does **not** claim programmable matter
- Does **not** replace terrestrial forcing results

---

## Exit criterion

1. Runnable
2. Off-ambient harness ticks accumulate visible cost and audit passes
3. At-ambient harness ticks cost ~0
4. Observation pure
5. Describable without embarrassment: harness is artificial and costed
