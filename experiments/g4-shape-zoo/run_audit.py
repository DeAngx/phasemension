"""g4 shape zoo audit — python run_audit.py"""

from __future__ import annotations

import sys

from zoo import (
    Cylinder,
    Oblong,
    Oval,
    Ovoid,
    RegularPolygon,
    ShapeZoo,
    Tetrahedron,
    regular_tetrahedron,
)


def main() -> int:
    print("=== g4 shape zoo ===")
    z = ShapeZoo(tol=1e-5)
    results = []

    # --- pentagons sharing an edge (place second by matching one edge) ---
    # Use two squares via RegularPolygon n=4 for reliable shared edge
    # Square at origin-ish: vertices of unit square via n=4 needs careful placement
    # Simpler: two oblongs face-touching (most reliable)
    z.add(Oblong(bid="O0", origin=(0.0, 0.0, 0.0), size=(2.0, 1.0, 1.0)))
    z.add(Oblong(bid="O1", origin=(2.0, 0.0, 0.0), size=(2.0, 1.0, 1.0)))  # touch on x face
    z.do_set_phase("O0", 1.0, label="charge_oblong")
    de = z.do_activate_contact("O0", "O1", sigma=1.0, label="oblong_face")
    print(f"oblong-oblong face  ΔE={de:+.6e}  kind={z.contacts[('O0','O1')].kind}")
    z.do_transfer("O0", "O1", 0.3, label="oblong_hop")
    results.append("oblong")

    # --- regular pentagon pair: build matching edge manually ---
    # P0 standard; P1 translated so one edge coincides — hard with regular placement.
    # Use n=4 polygons with identical edge by construction:
    # square vertices
    sq0 = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
    sq1 = [(1.0, 0.0), (2.0, 0.0), (2.0, 1.0), (1.0, 1.0)]  # shared edge x=1
    p0 = RegularPolygon(bid="P0", n=4, center=(0.5, 0.5), radius=0.7071)
    p0.vertices = sq0
    p1 = RegularPolygon(bid="P1", n=4, center=(1.5, 0.5), radius=0.7071)
    p1.vertices = sq1
    z.add(p0)
    z.add(p1)
    de = z.do_activate_contact("P0", "P1", sigma=0.8, label="poly_edge")
    print(f"polygon edge       ΔE={de:+.6e}  kind={z.contacts[('P0','P1')].kind}")
    results.append("polygon")

    # --- tetrahedra sharing a face ---
    # T0 standard; T1 mirrors one face by reusing 3 verts + new apex
    v = regular_tetrahedron(scale=1.0, offset=(10.0, 0.0, 0.0))
    z.add(Tetrahedron(bid="T0", vertices=v))
    # share face v[0],v[1],v[2]; new apex on other side
    shared = (v[0], v[1], v[2])
    # reflect v[3] through face plane roughly: use midpoint of face + opposite direction
    mid = (
        (v[0][0] + v[1][0] + v[2][0]) / 3,
        (v[0][1] + v[1][1] + v[2][1]) / 3,
        (v[0][2] + v[1][2] + v[2][2]) / 3,
    )
    # apex' = mid - (v3 - mid) = 2*mid - v3
    v3 = v[3]
    apex2 = (2 * mid[0] - v3[0], 2 * mid[1] - v3[1], 2 * mid[2] - v3[2])
    z.add(Tetrahedron(bid="T1", vertices=(v[0], v[1], v[2], apex2)))
    de = z.do_activate_contact("T0", "T1", sigma=0.6, label="tetra_face")
    print(f"tetra shared face  ΔE={de:+.6e}  kind={z.contacts[('T0','T1')].kind}")
    results.append("tetra")

    # --- ovals approx touch ---
    z.add(Oval(bid="V0", center=(0.0, 10.0), rx=2.0, ry=1.0))
    # mean r = 1.5; place second so d = 3.0
    z.add(Oval(bid="V1", center=(3.0, 10.0), rx=2.0, ry=1.0))
    de = z.do_activate_contact("V0", "V1", sigma=0.5, label="oval")
    print(f"oval approx touch  ΔE={de:+.6e}  kind={z.contacts[('V0','V1')].kind}")
    results.append("oval")

    # --- ovoids approx ---
    z.add(Ovoid(bid="E0", center=(0.0, 20.0, 0.0), radii=(2.0, 1.0, 1.0)))
    # mean r = 4/3 ≈ 1.333; d = 8/3 ≈ 2.667
    ra = (2.0 + 1.0 + 1.0) / 3.0
    z.add(Ovoid(bid="E1", center=(2 * ra, 20.0, 0.0), radii=(2.0, 1.0, 1.0)))
    de = z.do_activate_contact("E0", "E1", sigma=0.4, label="ovoid")
    print(f"ovoid approx touch ΔE={de:+.6e}  kind={z.contacts[('E0','E1')].kind}")
    results.append("ovoid")

    # --- cylinders side touch ---
    z.add(
        Cylinder(
            bid="C0",
            base_center=(0.0, 30.0, 0.0),
            axis=(0.0, 0.0, 1.0),
            height=2.0,
            radius=0.5,
        )
    )
    z.add(
        Cylinder(
            bid="C1",
            base_center=(1.0, 30.0, 0.0),  # dist = 1.0 = 0.5+0.5
            axis=(0.0, 0.0, 1.0),
            height=2.0,
            radius=0.5,
        )
    )
    de = z.do_activate_contact("C0", "C1", sigma=0.9, label="cyl_side")
    print(f"cylinder side      ΔE={de:+.6e}  kind={z.contacts[('C0','C1')].kind}")
    results.append("cylinder")

    # reject non-contact
    rejected = False
    try:
        z.do_transfer("O0", "C0", 0.1, label="far")
    except ValueError:
        rejected = True
    print(f"far transfer rejected = {rejected}")

    r = z.audit_full_history()
    print(
        f"bodies={r['n_bodies']} contacts={r['n_contacts']} "
        f"residual={r['residual']:.6e} ok={r['ok']}"
    )
    print(f"tested: {', '.join(results)}")

    if not (r["ok"] and rejected and len(results) >= 6):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
