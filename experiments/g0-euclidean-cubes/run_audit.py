"""
g0 conservation + geometry audit.

python run_audit.py
"""

from __future__ import annotations

import sys

from lattice import CubeLattice


def main() -> int:
    print("=== g0 Euclidean cube lattice audit ===")

    lat = CubeLattice()

    # --- 1D chain of 5 cubes along +x ---
    chain = lat.add_chain_x(5, start=(0, 0, 0), phi=0.0)
    coords = [c.coord for c in chain]

    # Charge the first cube (intervention)
    de = lat.do_set_phase(coords[0], 1.0, label="charge_head")
    print(f"charge head φ=1.0  ΔE={de:+.6e} J  system_E={lat.system_energy():.6e}")

    # Wave the state down the chain face by face
    print("wave along chain:")
    for i in range(len(coords) - 1):
        de = lat.do_transfer(coords[i], coords[i + 1], amount=1.0, label=f"hop_{i}")
        phases = [f"{lat.get_cube(c).phi:.2f}" for c in coords]
        print(f"  hop {coords[i]} → {coords[i+1]}  ΔE={de:+.6e}  φ={phases}")

    # --- small 2x2 grid, cross transfer ---
    grid = CubeLattice()
    grid.add_grid_xy(2, 2, start=(0, 0, 0), phi=0.0)
    grid.do_set_phase((0, 0, 0), 0.8, label="seed")
    grid.do_transfer((0, 0, 0), (1, 0, 0), 0.3, label="+x")
    grid.do_transfer((1, 0, 0), (1, 1, 0), 0.2, label="+y")
    grid.do_transfer((1, 1, 0), (0, 1, 0), 0.1, label="-x")

    # Illegal transfer must fail
    illegal_ok = False
    try:
        grid.do_transfer((0, 0, 0), (1, 1, 0), 0.1, label="diagonal_forbidden")
    except ValueError:
        illegal_ok = True

    r_chain = lat.audit_full_history()
    r_grid = grid.audit_full_history()

    print("--- chain audit ---")
    print(f"E_obs(t0)   = {r_chain['e_obs_t0']:.6e}")
    print(f"Σ ΔE        = {r_chain['sum_delta_e']:.6e}")
    print(f"E_obs(t1)   = {r_chain['e_obs_t1']:.6e}")
    print(f"residual    = {r_chain['residual']:.6e}")
    print(f"n_interv    = {r_chain['n_interventions']}")
    print(f"audit ok    = {r_chain['ok']}")

    print("--- grid audit ---")
    print(f"residual    = {r_grid['residual']:.6e}")
    print(f"audit ok    = {r_grid['ok']}")
    print(f"diagonal rejected = {illegal_ok}")

    # Observation purity on chain
    e_a = lat.system_energy()
    _ = lat.snapshot_phases()
    _ = lat.system_energy()
    e_b = lat.system_energy()
    pure = e_a == e_b
    print(f"observation pure = {pure}")

    if not (r_chain["ok"] and r_grid["ok"] and illegal_ok and pure):
        print("FAIL")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
