"""
g1 face-state audit

python run_audit.py
"""

from __future__ import annotations

import sys

from face_lattice import FaceLattice


def main() -> int:
    print("=== g1 first-class faces ===")

    lat = FaceLattice()
    cubes = lat.add_chain_x(3, start=(0, 0, 0))
    c0, c1, c2 = [c.coord for c in cubes]

    # Bulk charge
    lat.do_set_phase(c0, 1.0, label="charge")

    # Activate contact interfaces along the chain
    de1 = lat.do_activate_contact(c0, c1, sigma=1.0, label="contact_01")
    de2 = lat.do_activate_contact(c1, c2, sigma=0.5, label="contact_12")
    print(f"activate contact 0-1 ΔE={de1:+.6e}")
    print(f"activate contact 1-2 ΔE={de2:+.6e}")

    # Transfer along faces
    lat.do_transfer(c0, c1, 0.4, label="hop_01")
    lat.do_transfer(c1, c2, 0.2, label="hop_12")

    # Face-only intervention
    lat.do_set_face_sigma(c2, "+x", 0.3, label="boundary_face")

    # Illegal: non-adjacent transfer
    rejected = False
    try:
        lat.do_transfer(c0, c2, 0.1, label="skip")
    except ValueError:
        rejected = True

    # Illegal: non-adjacent contact
    contact_rejected = False
    try:
        lat.do_activate_contact(c0, c2, sigma=1.0, label="skip_contact")
    except ValueError:
        contact_rejected = True

    r = lat.audit_full_history()
    print(f"E_config     = {r['total_config_e']:.6e}")
    print(f"E_interface  = {r['total_interface_e']:.6e}")
    print(f"E_obs(t1)    = {r['e_obs_t1']:.6e}")
    print(f"Σ ΔE         = {r['sum_delta_e']:.6e}")
    print(f"residual     = {r['residual']:.6e}")
    print(f"audit ok     = {r['ok']}")
    print(f"transfer skip rejected  = {rejected}")
    print(f"contact skip rejected   = {contact_rejected}")

    e_a = lat.system_energy()
    _ = [lat.cubes[c].phi for c in (c0, c1, c2)]
    e_b = lat.system_energy()
    pure = e_a == e_b
    print(f"observation pure = {pure}")

    if not (r["ok"] and rejected and contact_rejected and pure):
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
