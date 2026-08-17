"""g2 polygon audit — python run_audit.py"""

from __future__ import annotations

import sys

from polygons import Polygon, PolygonWorld, square_at, triangle_at


def main() -> int:
    print("=== g2 polygons (edge adjacency) ===")

    w = PolygonWorld()
    # two unit squares sharing a vertical edge at x=1
    w.add(Polygon(pid="S0", kind="square", vertices=square_at(0, 0), phi=0.0))
    w.add(Polygon(pid="S1", kind="square", vertices=square_at(1, 0), phi=0.0))
    # triangle that only touches a corner of S0 — should NOT contact S1 center-style skip
    w.add(Polygon(pid="T0", kind="triangle", vertices=triangle_at(0, 1), phi=0.0))

    w.do_set_phase("S0", 1.0, label="charge")
    de = w.do_activate_contact("S0", "S1", sigma=1.0, label="square_contact")
    print(f"square edge contact ΔE={de:+.6e}")

    w.do_transfer("S0", "S1", 0.5, label="hop")

    # S0 and T0 share edge from (0,1)-(1,1)? triangle_at(0,1)=[(0,1),(1,1),(0,2)]
    # square_at(0,0) top edge (0,1)-(1,1) — yes shared with triangle base
    de_t = w.do_activate_contact("S0", "T0", sigma=0.4, label="square_tri_contact")
    print(f"square-triangle contact ΔE={de_t:+.6e}")

    # S1 and T0: no full shared edge expected
    rejected = False
    try:
        w.do_transfer("S1", "T0", 0.1, label="no_edge")
    except ValueError:
        rejected = True

    r = w.audit_full_history()
    print(f"residual={r['residual']:.6e} ok={r['ok']} n_polys={r['n_polys']}")
    print(f"non-edge transfer rejected={rejected}")

    pure = w.system_energy() == w.system_energy()
    if not (r["ok"] and rejected and pure):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
