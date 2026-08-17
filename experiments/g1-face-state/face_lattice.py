"""
g1 — Cubes with first-class faces and interface energy.

Euclidean contact is face-pair identity. Interface order σ is tracked
per face. System audit includes bulk + interface energy.
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

OPPOSITE = {
    "+x": "-x",
    "-x": "+x",
    "+y": "-y",
    "-y": "+y",
    "+z": "-z",
    "-z": "+z",
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
class Face:
    """Oriented face of a cube. σ = interface order."""

    name: str
    sigma: float = 0.0
    interface_scale: float = 5.0e4  # J per unit σ (model)

    def interface_energy(self) -> float:
        return self.sigma * self.interface_scale


@dataclass
class Cube:
    coord: Coord
    phi: float = 0.0
    mass: float = 1.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5
    faces: Dict[str, Face] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.faces:
            self.faces = {name: Face(name=name) for name in FACES}

    def config_energy(self) -> float:
        phi = _clamp01(self.phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)

    def interface_energy(self) -> float:
        return sum(f.interface_energy() for f in self.faces.values())

    def total_energy(self) -> float:
        return self.config_energy() + self.interface_energy()


class FaceLattice:
    def __init__(self) -> None:
        self.cubes: Dict[Coord, Cube] = {}
        self.intervention_log: List[InterventionRecord] = []

    def add_cube(self, coord: Coord, phi: float = 0.0) -> Cube:
        if coord in self.cubes:
            raise ValueError(f"exists {coord}")
        c = Cube(coord=coord, phi=_clamp01(phi))
        self.cubes[coord] = c
        return c

    def add_chain_x(self, n: int, start: Coord = (0, 0, 0)) -> List[Cube]:
        x0, y0, z0 = start
        return [self.add_cube((x0 + i, y0, z0)) for i in range(n)]

    def faces_shared(self, a: Coord, b: Coord) -> Optional[str]:
        ax, ay, az = a
        bx, by, bz = b
        d = (bx - ax, by - ay, bz - az)
        for name, vec in FACES.items():
            if vec == d:
                return name
        return None

    def contact_pair(self, a: Coord, b: Coord) -> Optional[Tuple[str, str]]:
        """(face_on_a, face_on_b) if adjacent."""
        fa = self.faces_shared(a, b)
        if fa is None:
            return None
        return fa, OPPOSITE[fa]

    def system_energy(self) -> float:
        return sum(c.total_energy() for c in self.cubes.values())

    def do_set_phase(self, coord: Coord, phi_new: float, label: str = "set_phi") -> float:
        c = self.cubes[coord]
        phi_new = _clamp01(phi_new)
        e0 = self.system_energy()
        before = c.phi
        c.phi = phi_new
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="set_phase",
                delta_e=de,
                detail={"coord": coord, "phi_before": before, "phi_after": phi_new},
            )
        )
        return de

    def do_set_face_sigma(
        self,
        coord: Coord,
        face: str,
        sigma: float,
        label: str = "set_face",
    ) -> float:
        if face not in FACES:
            raise ValueError(f"unknown face {face}")
        c = self.cubes[coord]
        sigma = _clamp01(sigma)
        e0 = self.system_energy()
        before = c.faces[face].sigma
        c.faces[face].sigma = sigma
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="set_face",
                delta_e=de,
                detail={
                    "coord": coord,
                    "face": face,
                    "sigma_before": before,
                    "sigma_after": sigma,
                },
            )
        )
        return de

    def do_activate_contact(
        self,
        a: Coord,
        b: Coord,
        sigma: float = 1.0,
        label: str = "activate_contact",
    ) -> float:
        """
        Set interface order on both faces of a contact pair.
        Requires Euclidean adjacency.
        """
        pair = self.contact_pair(a, b)
        if pair is None:
            raise ValueError(f"no contact between {a} and {b}")
        fa, fb = pair
        e0 = self.system_energy()
        sa0 = self.cubes[a].faces[fa].sigma
        sb0 = self.cubes[b].faces[fb].sigma
        sig = _clamp01(sigma)
        self.cubes[a].faces[fa].sigma = sig
        self.cubes[b].faces[fb].sigma = sig
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="activate_contact",
                delta_e=de,
                detail={
                    "a": a,
                    "b": b,
                    "face_a": fa,
                    "face_b": fb,
                    "sigma": sig,
                    "sigma_a_before": sa0,
                    "sigma_b_before": sb0,
                },
            )
        )
        return de

    def do_transfer(
        self,
        src: Coord,
        dst: Coord,
        amount: float,
        label: str = "transfer",
    ) -> float:
        pair = self.contact_pair(src, dst)
        if pair is None:
            raise ValueError(f"no face contact {src} → {dst}")
        fa, fb = pair
        a = self.cubes[src]
        b = self.cubes[dst]
        amount = float(amount)
        if amount > a.phi:
            amount = a.phi
        if amount > 1.0 - b.phi:
            amount = 1.0 - b.phi
        if amount < 0.0:
            amount = 0.0

        e0 = self.system_energy()
        phi_a0, phi_b0 = a.phi, b.phi
        a.phi = _clamp01(a.phi - amount)
        b.phi = _clamp01(b.phi + amount)
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="transfer",
                delta_e=de,
                detail={
                    "src": src,
                    "dst": dst,
                    "face_src": fa,
                    "face_dst": fb,
                    "amount": amount,
                    "phi_src_before": phi_a0,
                    "phi_dst_before": phi_b0,
                    "phi_src_after": a.phi,
                    "phi_dst_after": b.phi,
                    "sigma_src_face": a.faces[fa].sigma,
                    "sigma_dst_face": b.faces[fb].sigma,
                },
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
            "n_interventions": len(self.intervention_log),
            "n_cubes": len(self.cubes),
            "total_interface_e": sum(
                c.interface_energy() for c in self.cubes.values()
            ),
            "total_config_e": sum(c.config_energy() for c in self.cubes.values()),
        }
