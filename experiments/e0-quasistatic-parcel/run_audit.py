"""
Run e0 conservation audit demo.

Usage:
    python run_audit.py

Exits non-zero if audit fails.
"""

from __future__ import annotations

import sys

from parcel import Parcel


def main() -> int:
    p = Parcel(phi=0.0)  # start liquid-like

    e0 = p.get_total_energy()
    print("=== e0 quasi-static parcel audit ===")
    print(f"initial φ={p.get_phase():.3f}  ρ={p.get_density():.1f}  E={e0:.6e} J")

    # Sequence of interventions
    steps = [0.25, 0.5, 1.0, 0.0, 0.8]
    for i, phi in enumerate(steps):
        de = p.do_set_phase_fraction(phi, label=f"step_{i}")
        print(
            f"  do(φ={phi:.3f})  ΔE={de:+.6e} J  "
            f"ρ={p.get_density():.1f}  E={p.get_total_energy():.6e} J"
        )

    result = p.audit_full_history()
    print("---")
    print(f"E_obs(t0)     = {result['e_obs_t0']:.6e}")
    print(f"Σ ΔE_interv   = {result['sum_delta_e']:.6e}")
    print(f"E_obs(t1)     = {result['e_obs_t1']:.6e}")
    print(f"residual      = {result['residual']:.6e}")
    print(f"n_interv      = {result['n_interventions']}")
    print(f"audit ok      = {result['ok']}")

    # Observation purity check: repeated reads must not change E
    e_a = p.get_total_energy()
    _ = p.get_phase()
    _ = p.get_density()
    _ = p.get_config_energy()
    e_b = p.get_total_energy()
    pure = e_a == e_b
    print(f"observation pure = {pure}")

    if not result["ok"] or not pure:
        print("FAIL")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
