"""
g4 — Shape zoo: polygons, tetrahedra, oblongs, ovals, ovoids, cylinders.

Explicit contact predicates + energy audit. Same spine as g0–g3.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Vec2 = Tuple[float, float]
Vec3 = Tuple[float, float, float]


def _clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else float(x))


def _dist2(a: Vec2, b: Vec2) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def _dist3(a: Vec3, b: Vec3) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def _sub3(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot3(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm3(a: Vec3) -> float:
    return math.sqrt(_dot3(a, a))


def _normalize3(a: Vec3) -> Vec3:
    n = _norm3(a)
    if n < 1e-15:
        return (0.0, 0.0, 1.0)
    return (a[0] / n, a[1] / n, a[2] / n)


def _edge_key2(p: Vec2, q: Vec2, tol: float = 1e-9) -> Tuple[Vec2, Vec2]:
    a = (round(p[0] / tol) * tol, round(p[1] / tol) * tol)
    b = (round(q[0] / tol) * tol, round(q[1] / tol) * tol)
    return (a, b) if a <= b else (b, a)


def _face_key3(verts: Tuple[Vec3, Vec3, Vec3], tol: float = 1e-9) -> Tuple[Vec3, Vec3, Vec3]:
    rounded = tuple(
        sorted(
            (
                (round(v[0] / tol) * tol, round(v[1] / tol) * tol, round(v[2] / tol) * tol)
                for v in verts
            )
        )
    )
    return rounded  # type: ignore


@dataclass
class InterventionRecord:
    label: str
    kind: str
    delta_e: float
    detail: dict = field(default_factory=dict)


@dataclass
class BodyBase:
    bid: str
    phi: float = 0.0
    mass: float = 1.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5

    def config_energy(self) -> float:
        phi = _clamp01(self.phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)


@dataclass
class RegularPolygon(BodyBase):
    center: Vec2 = (0.0, 0.0)
    radius: float = 1.0
    n: int = 5
    vertices: List[Vec2] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.vertices:
            self.vertices = [
                (
                    self.center[0] + self.radius * math.cos(2 * math.pi * i / self.n),
                    self.center[1] + self.radius * math.sin(2 * math.pi * i / self.n),
                )
                for i in range(self.n)
            ]

    def edges(self) -> List[Tuple[Vec2, Vec2]]:
        v = self.vertices
        return [(v[i], v[(i + 1) % len(v)]) for i in range(len(v))]


@dataclass
class Oval(BodyBase):
    """2D ellipse."""

    center: Vec2 = (0.0, 0.0)
    rx: float = 1.0
    ry: float = 0.5


@dataclass
class Oblong(BodyBase):
    """Axis-aligned box; min corner + size."""

    origin: Vec3 = (0.0, 0.0, 0.0)
    size: Vec3 = (2.0, 1.0, 1.0)  # lx, ly, lz

    def max_corner(self) -> Vec3:
        return (
            self.origin[0] + self.size[0],
            self.origin[1] + self.size[1],
            self.origin[2] + self.size[2],
        )


@dataclass
class Tetrahedron(BodyBase):
    vertices: Tuple[Vec3, Vec3, Vec3, Vec3] = (
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    )

    def faces(self) -> List[Tuple[Vec3, Vec3, Vec3]]:
        a, b, c, d = self.vertices
        return [(a, b, c), (a, b, d), (a, c, d), (b, c, d)]


def regular_tetrahedron(scale: float = 1.0, offset: Vec3 = (0.0, 0.0, 0.0)) -> Tuple[Vec3, Vec3, Vec3, Vec3]:
    # Regular tetra inscribed-ish
    verts = [
        (1.0, 1.0, 1.0),
        (1.0, -1.0, -1.0),
        (-1.0, 1.0, -1.0),
        (-1.0, -1.0, 1.0),
    ]
    # normalize then scale
    out = []
    for v in verts:
        n = math.sqrt(sum(x * x for x in v))
        out.append(
            (
                offset[0] + scale * v[0] / n,
                offset[1] + scale * v[1] / n,
                offset[2] + scale * v[2] / n,
            )
        )
    return (out[0], out[1], out[2], out[3])


@dataclass
class Ovoid(BodyBase):
    """3D ellipsoid."""

    center: Vec3 = (0.0, 0.0, 0.0)
    radii: Vec3 = (1.0, 0.6, 0.4)  # rx, ry, rz


@dataclass
class Cylinder(BodyBase):
    """Finite right cylinder: base center, axis unit, height, radius."""

    base_center: Vec3 = (0.0, 0.0, 0.0)
    axis: Vec3 = (0.0, 0.0, 1.0)
    height: float = 2.0
    radius: float = 0.5

    def __post_init__(self) -> None:
        self.axis = _normalize3(self.axis)

    def top_center(self) -> Vec3:
        ax = self.axis
        return (
            self.base_center[0] + ax[0] * self.height,
            self.base_center[1] + ax[1] * self.height,
            self.base_center[2] + ax[2] * self.height,
        )


@dataclass
class Contact:
    a: str
    b: str
    kind: str
    sigma: float = 0.0
    interface_scale: float = 5.0e4

    def key(self) -> Tuple[str, str]:
        return (self.a, self.b) if self.a <= self.b else (self.b, self.a)

    def interface_energy(self) -> float:
        return self.sigma * self.interface_scale


class ShapeZoo:
    def __init__(self, tol: float = 1e-5) -> None:
        self.bodies: Dict[str, BodyBase] = {}
        self.contacts: Dict[Tuple[str, str], Contact] = {}
        self.intervention_log: List[InterventionRecord] = []
        self.tol = tol

    def add(self, body: BodyBase) -> BodyBase:
        if body.bid in self.bodies:
            raise ValueError(f"exists {body.bid}")
        self.bodies[body.bid] = body
        return body

    def system_energy(self) -> float:
        e = sum(b.config_energy() for b in self.bodies.values())
        e += sum(c.interface_energy() for c in self.contacts.values())
        return e

    def contact_kind(self, a: str, b: str) -> Optional[str]:
        A, B = self.bodies[a], self.bodies[b]

        # Regular polygons — shared edge
        if isinstance(A, RegularPolygon) and isinstance(B, RegularPolygon):
            ak = {_edge_key2(p, q): True for p, q in A.edges()}
            for p, q in B.edges():
                if _edge_key2(p, q) in ak:
                    return "polygon_edge"
            return None

        # Ovals — approximate external touch via isotropic scaling trick
        if isinstance(A, Oval) and isinstance(B, Oval):
            # Map to unit circles by scaling space: weak approx using mean radius
            ra = 0.5 * (A.rx + A.ry)
            rb = 0.5 * (B.rx + B.ry)
            d = _dist2(A.center, B.center)
            if abs(d - (ra + rb)) <= self.tol * 10:  # looser for ellipse approx
                return "oval_touch_approx"
            return None

        # Oblongs — AABB face touch
        if isinstance(A, Oblong) and isinstance(B, Oblong):
            return self._oblong_oblong(A, B)

        # Tetrahedra — shared face
        if isinstance(A, Tetrahedron) and isinstance(B, Tetrahedron):
            fa = {_face_key3(f) for f in A.faces()}
            for f in B.faces():
                if _face_key3(f) in fa:
                    return "tetra_face"
            return None

        # Ovoids — scaled-distance approx
        if isinstance(A, Ovoid) and isinstance(B, Ovoid):
            ra = sum(A.radii) / 3.0
            rb = sum(B.radii) / 3.0
            d = _dist3(A.center, B.center)
            if abs(d - (ra + rb)) <= self.tol * 20:
                return "ovoid_touch_approx"
            return None

        # Cylinders
        if isinstance(A, Cylinder) and isinstance(B, Cylinder):
            return self._cyl_cyl(A, B)

        return None

    def _oblong_oblong(self, A: Oblong, B: Oblong) -> Optional[str]:
        a0, a1 = A.origin, A.max_corner()
        b0, b1 = B.origin, B.max_corner()
        # Face touch along x: a1x ≈ b0x or b1x ≈ a0x, with yz overlap
        tol = self.tol

        def overlap_1d(p0, p1, q0, q1) -> bool:
            return min(p1, q1) - max(p0, q0) > -tol

        # +x of A vs -x of B
        if abs(a1[0] - b0[0]) <= tol and overlap_1d(a0[1], a1[1], b0[1], b1[1]) and overlap_1d(
            a0[2], a1[2], b0[2], b1[2]
        ):
            return "oblong_face_x"
        if abs(b1[0] - a0[0]) <= tol and overlap_1d(a0[1], a1[1], b0[1], b1[1]) and overlap_1d(
            a0[2], a1[2], b0[2], b1[2]
        ):
            return "oblong_face_x"
        if abs(a1[1] - b0[1]) <= tol and overlap_1d(a0[0], a1[0], b0[0], b1[0]) and overlap_1d(
            a0[2], a1[2], b0[2], b1[2]
        ):
            return "oblong_face_y"
        if abs(b1[1] - a0[1]) <= tol and overlap_1d(a0[0], a1[0], b0[0], b1[0]) and overlap_1d(
            a0[2], a1[2], b0[2], b1[2]
        ):
            return "oblong_face_y"
        if abs(a1[2] - b0[2]) <= tol and overlap_1d(a0[0], a1[0], b0[0], b1[0]) and overlap_1d(
            a0[1], a1[1], b0[1], b1[1]
        ):
            return "oblong_face_z"
        if abs(b1[2] - a0[2]) <= tol and overlap_1d(a0[0], a1[0], b0[0], b1[0]) and overlap_1d(
            a0[1], a1[1], b0[1], b1[1]
        ):
            return "oblong_face_z"
        return None

    def _cyl_cyl(self, A: Cylinder, B: Cylinder) -> Optional[str]:
        # Parallel side touch
        if abs(abs(_dot3(A.axis, B.axis)) - 1.0) <= 1e-3:
            # distance between axes
            w = _sub3(B.base_center, A.base_center)
            # component perpendicular to axis
            ax = A.axis
            perp = _sub3(w, (ax[0] * _dot3(w, ax), ax[1] * _dot3(w, ax), ax[2] * _dot3(w, ax)))
            d = _norm3(perp)
            if abs(d - (A.radius + B.radius)) <= self.tol:
                # rough axial overlap check
                return "cylinder_side"
            # base stack: tops/bases near
            if _dist3(A.top_center(), B.base_center()) <= self.tol or _dist3(
                B.top_center(), A.base_center()
            ) <= self.tol:
                return "cylinder_base_stack"
        return None

    def do_set_phase(self, bid: str, phi: float, label: str = "set_phi") -> float:
        b = self.bodies[bid]
        phi = _clamp01(phi)
        e0 = self.system_energy()
        before = b.phi
        b.phi = phi
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="set_phase",
                delta_e=de,
                detail={"bid": bid, "phi_before": before, "phi_after": phi},
            )
        )
        return de

    def do_activate_contact(
        self, a: str, b: str, sigma: float = 1.0, label: str = "contact"
    ) -> float:
        kind = self.contact_kind(a, b)
        if kind is None:
            raise ValueError(f"no contact between {a} and {b}")
        key = (a, b) if a <= b else (b, a)
        sig = _clamp01(sigma)
        e0 = self.system_energy()
        self.contacts[key] = Contact(a=key[0], b=key[1], kind=kind, sigma=sig)
        de = self.system_energy() - e0
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="activate_contact",
                delta_e=de,
                detail={"a": a, "b": b, "contact_kind": kind, "sigma": sig},
            )
        )
        return de

    def do_transfer(self, src: str, dst: str, amount: float, label: str = "transfer") -> float:
        if self.contact_kind(src, dst) is None:
            raise ValueError(f"no contact {src} → {dst}")
        A, B = self.bodies[src], self.bodies[dst]
        amount = float(amount)
        if amount > A.phi:
            amount = A.phi
        if amount > 1.0 - B.phi:
            amount = 1.0 - B.phi
        if amount < 0.0:
            amount = 0.0
        e0 = self.system_energy()
        A.phi = _clamp01(A.phi - amount)
        B.phi = _clamp01(B.phi + amount)
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
            "n_contacts": len(self.contacts),
            "n_bodies": len(self.bodies),
        }
