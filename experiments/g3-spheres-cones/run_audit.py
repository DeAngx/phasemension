"""g3 spheres/cones audit — python run_audit.py"""

from __future__ import annotations

import sys

from bodies import BodyWorld, Cone, Sphere


def main() -> int:
    print("=== g3 spheres and cones ===")

    w = BodyWorld(tol=1e-6)

    # Two spheres touching along x
    w.add_sphere(Sphere(bid="S0", center=(0.0, 0.0, 0.0), radius=1.0))
    w.add_sphere(Sphere(bid="S1", center=(2.0, 0.0, 0.0), radius=1.0))

    # Cone with base in z=0 plane, apex above; sphere S2 touches base outer ring
    # base center origin-ish: apex at (5,0,2), axis (0,0,-1), height 2 → base at (5,0,0), R=1
    w.add_cone(
        Cone(
            bid="C0",
            apex=(5.0, 0.0, 2.0),
            axis=(0.0, 0.0, -1.0),
            height=2.0,
            base_radius=1.0,
        )
    )
    # sphere touch outer ring: center in base plane z=0, dist from (5,0,0) = 1+0.5 = 1.5
    w.add_sphere(Sphere(bid="S2", center=(6.5, 0.0, 0.0), radius=0.5))

    # sphere on apex: apex (5,0,2), r=0.5 → center (5,0,2.5)
    w.add_sphere(Sphere(bid="S3", center=(5.0, 0.0, 2.5), radius=0.5))

    w.do_set_phase("S0", 1.0, label="charge_S0")
    de_ss = w.do_activate_contact("S0", "S1", sigma=1.0, label="ss")
    print(f"sphere-sphere contact ΔE={de_ss:+.6e}")
    w.do_transfer("S0", "S1", 0.4, label="ss_hop")

    de_sc = w.do_activate_contact("S2", "C0", sigma=0.7, label="sc_ring")
    print(f"sphere-cone base ring ΔE={de_sc:+.6e}")
    print(f"  kind={w.contacts[('C0','S2')].kind if ('C0','S2') in w.contacts else w.contacts[('S2','C0')].kind}")

    de_ap = w.do_activate_contact("S3", "C0", sigma=0.5, label="sc_apex")
    print(f"sphere-cone apex ΔE={de_ap:+.6e}")

    # non-contact: S0 and S2 far apart
    rejected = False
    try:
        w.do_transfer("S0", "S2", 0.1, label="far")
    except ValueError:
        rejected = True

    r = w.audit_full_history()
    print(f"residual={r['residual']:.6e} ok={r['ok']} contacts={r['n_contacts']}")
    print(f"far transfer rejected={rejected}")

    if not (r["ok"] and rejected and r["n_contacts"] >= 3):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
