# g3 — Spheres and cones

Same spine as g0–g2. Different Euclidean carriers.

---

## Units

| Kind | Geometry (v0) | Contact law |
|------|---------------|-------------|
| **Sphere** | center + radius | touch when \(\lvert c_i - c_j\rvert \approx r_i + r_j\) (within tol) |
| **Cone** | apex + base center + base radius + height axis | (1) base-disk touch (coplanar bases, edge contact), or (2) apex-in-base special case rejected for v0 — only **base-circle touch** and **lateral simplified**: distance between axes + radii |

v0 keeps contact **conservative and explicit**:

- Sphere–sphere: point contact at separation \(r_i+r_j\)
- Cone–cone: shared base-circle edge in a plane (two bases coplanar, centers separated by \(r_a+r_b\) in-plane), or stacked base-to-base (centers along axis, separation ~0 for glued bases — treated as contact)
- Sphere–cone: sphere touches cone **base circle plane** at distance matching base radius ring, or touches apex region — v0 only implements **sphere center in base plane, distance to base center = R_base ± r_sphere** (ring touch) and **sphere–apex** distance ≈ r_sphere (apex touch)

Vertex-only / glancing without satisfying a rule → **rejected**.

---

## State and energy

- Bulk `φ` per body
- Optional contact order `σ` on an active contact pair (interface energy)
- `E_obs = Σ E_config + Σ E_interface(contact)`

Interventions: `do_set_phase`, `do_activate_contact`, `do_transfer` — all logged.

---

## Scope

Idealized rigid Euclidean bodies. Not continuum deformation. Not harness. Not terrestrial ice. Audit spine unchanged.
