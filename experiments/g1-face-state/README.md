# g1 — First-class faces (Euclidean deepening)

Cubes are volumes. **Faces are the interaction machinery.**

Phase G made adjacency law. g1 makes the face itself a tracked object with state and energy.

---

## What is tracked

| Object | State | Energy |
|--------|--------|--------|
| Cube (volume) | bulk `φ` | config (same family as e0/g0) |
| Face (oriented side of a cube) | interface order `σ ∈ [0, 1]` | interface energy `∝ σ` |

System energy:

```
E_obs = Σ E_config(cube) + Σ E_interface(face)
```

Only **boundary faces that participate in a contact** (paired with a neighbor face) can carry non-zero interface cost in the audit demo; unpaired faces stay σ = 0 unless explicitly set (still logged).

---

## Euclidean rules

- 6 faces per cube: `±x ±y ±z`
- Contact iff two cubes share a face pair (outward normal of A = inward of B)
- `do_transfer` still requires contact
- `do_set_face_sigma(cube, face, σ)` — intervention on interface order
- `do_set_phase(cube, φ)` — bulk intervention
- No diagonal. No silent face activation.

---

## Declared scope

- Discrete Euclidean interface model
- Not ice, not fabricator, not harness (H stays separate unless later combined)
- Parallel to water line; same audit spine

## Exit

Runnable; multi-step bulk + face interventions; conservation PASS; non-contact transfer rejected.
