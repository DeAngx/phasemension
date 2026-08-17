"""
Bridge invariance demo

Same ledger spine, two restriction regimes:
  A) local phase sets on isolated parcels (water-line style, no geometry required)
  B) face-gated transfers on a cube chain (G-line style, geometry required)

Invariant under test:
  E(t0) + Σ ΔE_intervention = E(t1)
  for both regimes; diagonal/non-adjacent transfer still forbidden in B.

Not a merge of Earth and cubes. A single discipline applied twice.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Import g0 lattice (cube line)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "g0-euclidean-cubes"))
sys.path.insert(0, str(ROOT / "e0-quasistatic-parcel"))

from lattice import CubeLattice  # noqa: E402
from parcel import Parcel  # noqa: E402


def run_water_style() -> dict:
    """Regime A: isolated parcels, local do_set only."""
    parcels = [Parcel(phi=0.0), Parcel(phi=0.0), Parcel(phi=0.0)]
    e0 = sum(p.get_total_energy() for p in parcels)

    parcels[0].do_set_phase_fraction(0.5, label="A_set0")
    parcels[1].do_set_phase_fraction(1.0, label="A_set1")
    parcels[2].do_set_phase_fraction(0.25, label="A_set2")
    parcels[1].do_set_phase_fraction(0.0, label="A_clear1")

    sum_delta = sum(r.delta_e for p in parcels for r in p.intervention_log)
    e1 = sum(p.get_total_energy() for p in parcels)
    residual = e1 - (e0 + sum_delta)
    return {
        "regime": "A_water_style_local_sets",
        "e0": e0,
        "sum_delta": sum_delta,
        "e1": e1,
        "residual": residual,
        "ok": abs(residual) <= 1e-9,
        "n_interventions": sum(len(p.intervention_log) for p in parcels),
    }


def run_cube_style() -> dict:
    """Regime B: chain, face transfers + one charge."""
    lat = CubeLattice()
    chain = lat.add_chain_x(4, start=(0, 0, 0), phi=0.0)
    coords = [c.coord for c in chain]

    lat.do_set_phase(coords[0], 1.0, label="B_charge")
    for i in range(3):
        lat.do_transfer(coords[i], coords[i + 1], 1.0, label=f"B_hop_{i}")

    # geometry law still holds
    rejected = False
    try:
        lat.do_transfer(coords[0], coords[2], 0.1, label="B_skip_forbidden")
    except ValueError:
        rejected = True

    audit = lat.audit_full_history()
    audit["regime"] = "B_cube_style_face_transfer"
    audit["non_adjacent_rejected"] = rejected
    audit["ok"] = audit["ok"] and rejected
    return audit


def main() -> int:
    print("=== bridge invariance ===")
    print("invariant: E(t0) + Σ ΔE = E(t1) under both restriction regimes")
    print()

    a = run_water_style()
    b = run_cube_style()

    print(f"Regime A (local sets, no geometry)")
    print(f"  e0={a['e0']:.6e}  ΣΔE={a['sum_delta']:.6e}  e1={a['e1']:.6e}")
    print(f"  residual={a['residual']:.6e}  ok={a['ok']}")
    print()
    print(f"Regime B (face transfers, geometry required)")
    print(f"  e0={b['e_obs_t0']:.6e}  ΣΔE={b['sum_delta_e']:.6e}  e1={b['e_obs_t1']:.6e}")
    print(f"  residual={b['residual']:.6e}  non_adjacent_rejected={b['non_adjacent_rejected']}  ok={b['ok']}")
    print()

    # Shared spine check
    same_spine = a["ok"] and b["ok"]
    print(f"invariance holds (both audits pass under one discipline) = {same_spine}")

    if not same_spine:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
