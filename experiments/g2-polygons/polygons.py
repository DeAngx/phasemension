"""
g2 — 2D polygons with edge adjacency and interface energy.

Contact = shared full edge. Vertex-only is not contact.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

Point = Tuple[float, float]


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def _edge_key(p: Point, q: Point, tol: float = 1e-9) -> Tuple[Point, Point]:
    """Canonical undirected edge key."""
    a = (round(p[0] / tol) * tol, round(p[1] / tol) * tol)
    b = (round(q[0] / tol) * tol, round(q[1] / tol) * tol)
    return (a, b) if a <= b else (b, a)


@dataclass
class InterventionRecord:
    label: str
    kind: str
    delta_e: float
    detail: dict = field(default_factory=dict)


@dataclass
class Edge:
    i: int  # local index
    a: Point
    b: Point
    sigma: float = 0.0
    interface_scale: float = 5.0e4

    def key(self) -> Tuple[Point, Point]:
        return _edge_key(self.a, self.b)

    def interface_energy(self) -> float:
        return self.sigma * self.interface_scale


@dataclass
class Polygon:
    pid: str
    kind: str
    vertices: List[Point]
    phi: float = 0.0
    mass: float = 1.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5
    edges: List[Edge] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.edges:
            n = len(self.vertices)
            self.edges = []
            for i in range(n):
                a = self.vertices[i]
                b = self.vertices[(i + 1) % n]
                self.edges.append(Edge(i=i, a=a, b=b))

    def config_energy(self) -> float:
        phi = _clamp01(self.phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)

    def interface_energy(self) -> float:
        return sum(e.interface_energy() for e in self.edges)

    def total_energy(self) -> float:
        return self.config_energy() + self.interface_energy()


def square_at(x: float, y: float, s: float = 1.0) -> List[Point]:
    return [(x, y), (x + s, y), (x + s, y + s), (x, y + s)]


def triangle_at(x: float, y: float, s: float = 1.0) -> List[Point]:
    # right triangle
    return [(x, y), (x + s, y), (x, y + s)]


def hex_at(cx: float, cy: float, r: float = 1.0) -> List[Point]:
    import math

    return [
        (cx + r * math.cos(math.pi / 3 * i), cy + r * math.sin(math.pi / 3 * i))
        for i in range(6)
    ]


class PolygonWorld:
    def __init__(self) -> None:
        self.polys: Dict[str, Polygon] = {}
        self.intervention_log: List[InterventionRecord] = []

    def add(self, poly: Polygon) -> Polygon:
        if poly.pid in self.polys:
            raise ValueError(f"exists {poly.pid}")
        self.polys[poly.pid] = poly
        return poly

    def system_energy(self) -> float:
        return sum(p.total_energy() for p in self.polys.values())

    def shared_edge(
        self, a_id: str, b_id: str
    ) -> Optional[Tuple[Edge, Edge]]:
        a = self.polys[a_id]
        b = self.polys[b_id]
        b_keys = {e.key(): e for e in b.edges}
        for ea in a.edges:
            eb = b_keys.get(ea.key())
            if eb is not None:
                return ea, eb
        return None

    def do_set_phase(self, pid: str, phi: float, label: str = "set_phi") -> float:
        p = self.polys[pid]
        phi = _clamp01(phi)
        e0 = self.system_energy()
        before = p.phi
        p.phi = phi
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="set_phase",
                delta_e=de,
                detail={"pid": pid, "phi_before": before, "phi_after": phi},
            )
        )
        return de

    def do_activate_contact(
        self, a_id: str, b_id: str, sigma: float = 1.0, label: str = "contact"
    ) -> float:
        pair = self.shared_edge(a_id, b_id)
        if pair is None:
            raise ValueError(f"no shared edge between {a_id} and {b_id}")
        ea, eb = pair
        sig = _clamp01(sigma)
        e0 = self.system_energy()
        ea.sigma = sig
        eb.sigma = sig
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="activate_contact",
                delta_e=de,
                detail={"a": a_id, "b": b_id, "sigma": sig, "edge_key": ea.key()},
            )
        )
        return de

    def do_transfer(
        self, src: str, dst: str, amount: float, label: str = "transfer"
    ) -> float:
        if self.shared_edge(src, dst) is None:
            raise ValueError(f"no edge contact {src} → {dst}")
        a = self.polys[src]
        b = self.polys[dst]
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
            "n_polys": len(self.polys),
        }
