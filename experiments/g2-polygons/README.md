# g2 — Polygons beyond cubes

Same discipline as g0/g1. Different Euclidean units.

---

## Units

| Kind | Sides | Edge-adjacency |
|------|-------|----------------|
| triangle | 3 | share full edge |
| square | 4 | share full edge (2D analogue of cube face) |
| hexagon | 6 | share full edge |

v0 is **2D**: polygons in the plane. Contact = shared edge (not vertex-only).

Each polygon carries bulk `φ` and per-edge interface order `σ`.

```
E_obs = Σ E_config(poly) + Σ E_interface(edge)
```

---

## Rules

- `do_set_phase(id, φ)`
- `do_set_edge_sigma(id, edge_i, σ)`
- `do_activate_contact(a, b)` — requires a shared edge pair
- `do_transfer(a, b, amount)` — requires contact
- Vertex-only touch → rejected

---

## Scope

Not 3D polyhedra yet. Not harness. Not terrestrial claim.
Same audit spine as the cube line.
