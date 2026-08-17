# What Is Tracked During the Transition (Phase C — Locked)

Exit statement for the first transition class. Other transition types can be added later as separate runs; this does not freeze all possible T forever.

---

## Statement

**During a quasi-static H₂O phase-boundary crossing (liquid ↔ Ice VI/VII, or solid–solid between high-pressure ices), the primary quantities being tracked are:**

1. **Phase / density state of the parcel** — which phase (or phase fraction) is present, and the associated density \(\rho(P, T, \text{phase})\).
2. **Configurational energy change** — latent heat (enthalpy of transition) plus PV work from \(\Delta V\) at the boundary.

**Sampled at:** the resolution of the parcel (or control volume) used for the energy audit — i.e. whenever the audit evaluates \(E_{\text{obs}}\), both phase identity (or order parameter that distinguishes phases) and the configurational energy terms must be defined for that same volume.

---

## Not primary for this transition class

- Kinetic energy — declare ~0 for quasi-static geologic or lab rates unless the experiment is deliberately dynamic.
- Harness / active constraint set — not supplied by the terrestrial process; only appears if an explicit intervention is added.
- Topology or information accounts — not required for Phase C exit on this T.

---

## Relation to stance

The interval of interest is the interval in which phase fraction and configurational energy are still moving. Once both are fixed again, the object looks ordinary. Attention tracks the change, not the finished noun.

---

## Later runs

Additional transition classes (e.g. anisotropic growth, dynamic interfaces, explicit harness interventions) may define their own primary X and sampling resolution. Each gets its own statement; this one stays for quasi-static H₂O phase-boundary crossings.
