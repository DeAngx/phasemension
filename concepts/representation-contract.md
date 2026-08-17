# Representation Contract (Phase D — Locked)

Code represents relations; it is not the thing.

This contract can be revised later based on experiment data, failures, and breakthroughs. Until then it is the default rule for any computational work in this project.

---

## What the code is allowed to claim

A computational representation may claim only that it:

1. **Tracks** the primary quantities defined for its transition class (for quasi-static H₂O boundaries: phase/density state + configurational energy), sampled at the audit control volume.
2. **Obeys** the Phase A energy audit: kinetic (or explicit zero) + configurational + full intervention log; conservation holds within declared tolerance.
3. **Separates** observation from intervention: pure reads have no side effects; every `do(...)` logs ΔE.
4. **Declares** its scope — which real process or idealized relation it is modeling, and which locked terms it is *not* claiming to instantiate (especially harness, unless introduced as explicit continuous intervention).

It may **not** claim:

- That it *is* the material, the planet, or the phase.
- That a non-default density is “held” unless an intervention ledger shows the ongoing cost.
- That harness exists in the model unless harness is an explicit, energy-accounted term.
- Completeness beyond the declared scope.

---

## What counts as evidence the claim has failed

| Failure signature | Meaning |
|-------------------|--------|
| Energy non-conservation under pure observation | Numerical or structural bug; audit broken |
| State change with no logged ΔE | Silent intervention; decree without cost |
| Phase/density undefined at audit time | Phase C tracking requirement violated |
| Harness language used with no intervention cost | Constructive term smuggled in as if natural |
| Scope creep: claims beyond the declared toy | Overclaim; retreat violated |

---

## Deliberately left unrepresented (for now)

- Full planetary interior
- Topology/information ledgers as independent accounts
- Natural harness (not forced by Phase B)
- Use, application, or fabrication outcomes

These may be added later only under revised or additional contracts.

---

## One-line contract

**Code tracks declared relations under an energy audit; it does not become the thing, and failure is any silent energy change, undefined primary quantity, or claim beyond declared scope.**
