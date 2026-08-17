# g4 — Shape zoo

More Euclidean carriers under the same discipline as g0–g3.

---

## Bodies (v0)

| Kind | Geometry | Contact law (v0) |
|------|----------|------------------|
| **Regular n-gon** (n≥3) | 2D, center + radius + n | Shared full edge |
| **Oval** | 2D ellipse, center + (rx, ry) | External touch: scaled distance ≈ 1 (ellipse–ellipse approx) |
| **Oblong** | 3D axis-aligned box (lx,ly,lz) | Face coplanar + overlap (AABB face touch) |
| **Tetrahedron** | 4 vertices (regular or given) | Shared full triangular face |
| **Ovoid** | 3D ellipsoid, center + (rx,ry,rz) | External touch via scaled radius sum approx |
| **Cylinder** | axis segment + radius | Side-side (parallel axes, dist≈r1+r2) or base-base stack |

No vertex-only / glancing without a satisfied predicate → **rejected**.

---

## State and energy

- Bulk `φ` per body
- Contact `σ` when activated
- `E_obs = Σ E_config + Σ E_interface`

Interventions: `do_set_phase`, `do_activate_contact`, `do_transfer` — always logged.

---

## Scope

Idealized rigid shapes. Approximations for oval/ovoid contact are explicit, not continuum contact mechanics. Not harness. Not terrestrial claim. Audit spine unchanged.
