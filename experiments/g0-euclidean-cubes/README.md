# g0 — Discrete Euclidean cubes (Phase G — Locked)

**Phase G is locked.**

Objects are cubes. Man-made. Euclidean. Finite faces. Adjacency is not a metaphor — it is a shared face with a normal and an orientation.

This is not Minecraft. This is not programmable matter claimed. This is the study of **interaction and state transfer** between discrete Euclidean units under the same audit discipline as e0.

---

## Core claim (mechanism only)

A cube is a parcel with geometry.

- Identity: lattice index `(i, j, k)` or an explicit id
- State: phase fraction `φ ∈ [0, 1]` (same family as e0)
- Geometry: 6 faces, axis-aligned, face-adjacent only (no diagonal contact)
- Interaction: only across a shared face
- State transfer across a face is an **intervention** and must log `ΔE`

Observation remains pure. Energy still conserves. The representation is not the material.

---

## What is tracked (Phase C extension for this class)

During a **face-mediated state transfer** between cubes:

1. **Per-cube phase / density state** — `φ` and `ρ(φ)` on each unit
2. **Configurational energy** — per cube, same latent + PV stand-in family as e0
3. **Transfer event** — which face, which direction, how much `φ` (or energy) moved, `ΔE` total for the system

Sampled at: each cube as its own audit volume, plus a system-level sum.

```
Σ E_cube(t0) + Σ ΔE_intervention = Σ E_cube(t1)
```

---

## Interaction rules (v0)

### Adjacency
- Two cubes interact iff they share a full face (6-connected grid).
- No edge-only, no corner-only, no long-range transfer.

### Transfer
- `do_transfer(src, dst, face, amount)`
  - `amount` is a change in phase fraction (clamped so both cubes stay in `[0, 1]`)
  - System configurational energy before/after is computed
  - `ΔE = E_after - E_before` is logged as one intervention on the system log
  - Direction is explicit: state leaves `src`, arrives `dst`

### Local set (still allowed)
- `do_set_phase(cube, φ)` — same as e0, per cube, logged

### Forbidden
- Silent copy of state between cubes
- Transfer without a shared face
- Any change to `φ` that does not hit the intervention log
- Harness language without an explicit costed term (still constructive; not in g0 v0)

---

## Geometry that is load-bearing (not decoration)

- Face normals: `±X, ±Y, ±Z`
- Orientation of a transfer is the outward normal of `src` toward `dst`
- A cube knows its six neighbor slots; empty = boundary
- Lattice can be sparse (missing neighbors are fine)

This is Euclidean structure as **constraint on interaction**, not as rendering candy.

---

## Going further (still inside the frame)

g0 is allowed to get rich without leaving the contract:

| Extension | Status |
|-----------|--------|
| 1D chain of cubes | in scope for first implementation |
| 2D face lattice | in scope |
| 3D block | in scope |
| Multi-step transfer sequences + full system audit | required for exit |
| Face-local state (per-face φ) | later G′ — not required for G exit |
| Oriented / chiral transfer rules | later G′ |
| Polygons other than cubes | later G′ (same discipline) |
| Continuous harness on a cube | only as explicit `do_harness` with power cost — not v0 |
| Spatial continuum field | not G; different experiment |

**Crazy but legal:** treat a whole lattice as one thermodynamic report — every face transfer is a logged transaction; the history is a ledger of geometric events with Joule amounts. Failure is any transaction that does not balance.

**Crazy but illegal:** cubes that “just know” distant state, free reshape of the mesh, ambient density hold with no cost, claiming the lattice *is* matter.

---

## Declared scope (Phase D)

- Idealized discrete Euclidean interaction model
- Does **not** claim to be ice, rock, fabricator, or planetary interior
- Does **not** implement harness in v0
- Does **not** replace the terrestrial water anchor; parallel mechanism line only

---

## Exit criterion

1. Runnable code: at least two face-adjacent cubes (preferably a short chain or small grid)
2. Pure observation APIs per cube and system energy sum
3. `do_transfer` and `do_set_phase` always log `ΔE`
4. System conservation audit passes on a multi-step transfer sequence
5. Describable in locked vocabulary without embarrassment

---

## Relation to e0

e0 = one parcel, no geometry.  
g0 = many parcels, geometry decides who can talk.

Same ledger. Same retreat. More structure.

---

*Phase G locked. Implementation follows.*
