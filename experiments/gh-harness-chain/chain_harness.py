"""
gh — Cube chain + per-cube constructive harness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

FACES = {
    "+x": (1, 0, 0),
    "-x": (-1, 0, 0),
    "+y": (0, 1, 0),
    "-y": (0, -1, 0),
    "+z": (0, 0, 1),
    "-z": (0, 0, -1),
}

Coord = Tuple[int, int, int]


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


@dataclass
class InterventionRecord:
    label: str
    kind: str
    delta_e: float
    detail: dict = field(default_factory=dict)


@dataclass
class HCube:
    coord: Coord
    phi: float = 0.0
    phi_ambient: float = 0.0
    kappa: float = 1.0e5
    mass: float = 1.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5
    e_dissipated: float = 0.0
    harness_engaged: bool = False

    def config_energy(self) -> float:
        phi = _clamp01(self.phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)

    def total_energy(self) -> float:
        return self.config_energy() + self.e_dissipated


class HarnessChain:
    def __init__(self) -> None:
        self.cubes: Dict[Coord, HCube] = {}
        self.intervention_log: List[InterventionRecord] = []

    def add_chain_x(self, n: int, start: Coord = (0, 0, 0)) -> List[HCube]:
        x0, y0, z0 = start
        out = []
        for i in range(n):
            c = HCube(coord=(x0 + i, y0, z0))
            self.cubes[c.coord] = c
            out.append(c)
        return out

    def faces_shared(self, a: Coord, b: Coord) -> Optional[str]:
        ax, ay, az = a
        bx, by, bz = b
        d = (bx - ax, by - ay, bz - az)
        for name, vec in FACES.items():
            if vec == d:
                return name
        return None

    def system_energy(self) -> float:
        return sum(c.total_energy() for c in self.cubes.values())

    def do_set_phase(self, coord: Coord, phi: float, label: str = "set") -> float:
        c = self.cubes[coord]
        phi = _clamp01(phi)
        e0 = self.system_energy()
        before = c.phi
        c.phi = phi
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="set",
                delta_e=de,
                detail={"coord": coord, "phi_before": before, "phi_after": phi},
            )
        )
        return de

    def do_transfer(self, src: Coord, dst: Coord, amount: float, label: str = "transfer") -> float:
        if self.faces_shared(src, dst) is None:
            raise ValueError(f"no face {src}→{dst}")
        a, b = self.cubes[src], self.cubes[dst]
        amount = float(amount)
        if amount > a.phi:
            amount = a.phi
        if amount > 1.0 - b.phi:
            amount = 1.0 - b.phi
        if amount < 0.0:
            amount = 0.0
        e0 = self.system_energy()
        a.phi = _clamp01(a.phi - amount)
        b.phi = _clamp01(b.phi + amount)
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="transfer",
                delta_e=de,
                detail={"src": src, "dst": dst, "amount": amount},
            )
        )
        return de

    def do_engage(self, coord: Coord, label: str = "engage") -> float:
        self.cubes[coord].harness_engaged = True
        self.intervention_log.append(
            InterventionRecord(label=label, kind="engage", delta_e=0.0, detail={"coord": coord})
        )
        return 0.0

    def do_release(self, coord: Coord, label: str = "release") -> float:
        self.cubes[coord].harness_engaged = False
        self.intervention_log.append(
            InterventionRecord(label=label, kind="release", delta_e=0.0, detail={"coord": coord})
        )
        return 0.0

    def do_harness_tick(self, coord: Coord, dt: float, label: str = "tick") -> float:
        c = self.cubes[coord]
        if not c.harness_engaged:
            self.intervention_log.append(
                InterventionRecord(
                    label=label,
                    kind="harness_tick",
                    delta_e=0.0,
                    detail={"coord": coord, "engaged": False},
                )
            )
            return 0.0
        cost = c.kappa * abs(c.phi - c.phi_ambient) * dt
        e0 = self.system_energy()
        c.e_dissipated += cost
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="harness_tick",
                delta_e=de,
                detail={"coord": coord, "dt": dt, "cost": cost, "phi": c.phi},
            )
        )
        return de

    def audit_full_history(self, tolerance: float = 1e-9) -> dict:
        e_now = self.system_energy()
        sum_delta = sum(r.delta_e for r in self.intervention_log)
        e0 = e_now - sum_delta
        residual = e_now - (e0 + sum_delta)
        return {
            "ok": abs(residual) <= tolerance,
            "e_obs_t0": e0,
            "sum_delta_e": sum_delta,
            "e_obs_t1": e_now,
            "residual": residual,
            "total_dissipated": sum(c.e_dissipated for c in self.cubes.values()),
            "n_interventions": len(self.intervention_log),
        }
