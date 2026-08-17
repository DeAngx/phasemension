"""
g0 — Discrete Euclidean cube lattice

Cubes on a 6-connected grid. State transfer only across shared faces.
Every transfer and every local set is an intervention with logged ΔE.

Not the material. Not harness. Not Minecraft.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

# Face normals: outward from a cube toward a neighbor
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
    kind: str  # "set" | "transfer"
    delta_e: float
    detail: dict = field(default_factory=dict)


@dataclass
class Cube:
    """One Euclidean unit. Geometry is its lattice coordinate."""

    coord: Coord
    phi: float = 0.0
    mass: float = 1.0
    rho_l: float = 1000.0
    rho_s: float = 1650.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5

    def get_phase(self) -> float:
        return self.phi

    def get_density(self) -> float:
        return (1.0 - self.phi) * self.rho_l + self.phi * self.rho_s

    def config_energy_at(self, phi: float) -> float:
        phi = _clamp01(phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)

    def get_config_energy(self) -> float:
        return self.config_energy_at(self.phi)

    def get_kinetic_energy(self) -> float:
        return 0.0

    def get_total_energy(self) -> float:
        return self.get_kinetic_energy() + self.get_config_energy()


class CubeLattice:
    """
    Sparse 6-connected cube lattice.

    System energy = sum of cube energies.
    All state changes go through do_* and hit intervention_log.
    """

    def __init__(self) -> None:
        self.cubes: Dict[Coord, Cube] = {}
        self.intervention_log: List[InterventionRecord] = []

    # --- construction ---

    def add_cube(self, coord: Coord, phi: float = 0.0) -> Cube:
        if coord in self.cubes:
            raise ValueError(f"cube already exists at {coord}")
        c = Cube(coord=coord, phi=_clamp01(phi))
        self.cubes[coord] = c
        return c

    def add_chain_x(self, n: int, start: Coord = (0, 0, 0), phi: float = 0.0) -> List[Cube]:
        """n cubes in a row along +x."""
        out = []
        x0, y0, z0 = start
        for i in range(n):
            out.append(self.add_cube((x0 + i, y0, z0), phi=phi))
        return out

    def add_grid_xy(self, nx: int, ny: int, start: Coord = (0, 0, 0), phi: float = 0.0) -> List[Cube]:
        out = []
        x0, y0, z0 = start
        for i in range(nx):
            for j in range(ny):
                out.append(self.add_cube((x0 + i, y0 + j, z0), phi=phi))
        return out

    # --- observation (pure) ---

    def get_cube(self, coord: Coord) -> Cube:
        return self.cubes[coord]

    def neighbor(self, coord: Coord, face: str) -> Optional[Coord]:
        dx, dy, dz = FACES[face]
        x, y, z = coord
        n = (x + dx, y + dy, z + dz)
        return n if n in self.cubes else None

    def faces_shared(self, a: Coord, b: Coord) -> Optional[str]:
        """Return face name on a that points toward b, or None."""
        ax, ay, az = a
        bx, by, bz = b
        d = (bx - ax, by - ay, bz - az)
        for name, vec in FACES.items():
            if vec == d:
                return name
        return None

    def system_energy(self) -> float:
        return sum(c.get_total_energy() for c in self.cubes.values())

    def snapshot_phases(self) -> Dict[Coord, float]:
        return {coord: c.phi for coord, c in self.cubes.items()}

    # --- intervention ---

    def do_set_phase(self, coord: Coord, phi_new: float, label: str = "set_phi") -> float:
        c = self.cubes[coord]
        phi_new = _clamp01(phi_new)
        e_before = self.system_energy()
        phi_before = c.phi
        c.phi = phi_new
        e_after = self.system_energy()
        delta_e = e_after - e_before
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="set",
                delta_e=delta_e,
                detail={
                    "coord": coord,
                    "phi_before": phi_before,
                    "phi_after": phi_new,
                },
            )
        )
        return delta_e

    def do_transfer(
        self,
        src: Coord,
        dst: Coord,
        amount: float,
        label: str = "transfer",
    ) -> float:
        """
        Move phase-fraction amount from src to dst across a shared face.

        amount > 0 means φ decreases on src and increases on dst (clamped).
        System ΔE is logged. No shared face → hard error (no silent skip).
        """
        if src not in self.cubes or dst not in self.cubes:
            raise KeyError("src and dst must exist")

        face = self.faces_shared(src, dst)
        if face is None:
            raise ValueError(
                f"no face adjacency between {src} and {dst}; "
                "transfer forbidden without shared face"
            )

        a = self.cubes[src]
        b = self.cubes[dst]

        # Clamp so both stay in [0, 1]
        amount = float(amount)
        if amount > a.phi:
            amount = a.phi
        if amount > (1.0 - b.phi):
            amount = 1.0 - b.phi
        if amount <= 0.0:
            # still log a zero transfer? treat as no-op with ΔE=0 record for honesty
            self.intervention_log.append(
                InterventionRecord(
                    label=label,
                    kind="transfer",
                    delta_e=0.0,
                    detail={
                        "src": src,
                        "dst": dst,
                        "face": face,
                        "amount": 0.0,
                        "note": "clamped to zero",
                    },
                )
            )
            return 0.0

        e_before = self.system_energy()
        phi_a0, phi_b0 = a.phi, b.phi
        a.phi = _clamp01(a.phi - amount)
        b.phi = _clamp01(b.phi + amount)
        e_after = self.system_energy()
        delta_e = e_after - e_before

        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="transfer",
                delta_e=delta_e,
                detail={
                    "src": src,
                    "dst": dst,
                    "face": face,
                    "face_opposite": OPPOSITE[face],
                    "amount": amount,
                    "phi_src_before": phi_a0,
                    "phi_src_after": a.phi,
                    "phi_dst_before": phi_b0,
                    "phi_dst_after": b.phi,
                },
            )
        )
        return delta_e

    def do_wave_along_chain(
        self,
        coords: List[Coord],
        amount: float,
        label_prefix: str = "wave",
    ) -> List[float]:
        """
        Push a pulse down a face-connected path: transfer amount along each hop.
        Geometry must form a path of successive face neighbors.
        """
        deltas = []
        for i in range(len(coords) - 1):
            de = self.do_transfer(
                coords[i],
                coords[i + 1],
                amount,
                label=f"{label_prefix}_{i}",
            )
            deltas.append(de)
        return deltas

    # --- audit ---

    def audit_full_history(self, tolerance: float = 1e-9) -> dict:
        e_now = self.system_energy()
        sum_delta = sum(r.delta_e for r in self.intervention_log)
        e0 = e_now - sum_delta
        residual = e_now - (e0 + sum_delta)
        ok = abs(residual) <= tolerance
        return {
            "ok": ok,
            "e_obs_t0": e0,
            "sum_delta_e": sum_delta,
            "e_obs_t1": e_now,
            "residual": residual,
            "tolerance": tolerance,
            "n_interventions": len(self.intervention_log),
            "n_cubes": len(self.cubes),
        }
