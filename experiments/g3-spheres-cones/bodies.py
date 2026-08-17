"""
g3 — Spheres and cones with explicit contact laws and energy audit.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

Vec3 = Tuple[float, float, float]


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


def _dist(a: Vec3, b: Vec3) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a: Vec3) -> float:
    return math.sqrt(_dot(a, a))


def _normalize(a: Vec3) -> Vec3:
    n = _norm(a)
    if n < 1e-15:
        return (0.0, 0.0, 1.0)
    return (a[0] / n, a[1] / n, a[2] / n)


@dataclass
class InterventionRecord:
    label: str
    kind: str
    delta_e: float
    detail: dict = field(default_factory=dict)


@dataclass
class Sphere:
    bid: str
    center: Vec3
    radius: float
    phi: float = 0.0
    mass: float = 1.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5

    def config_energy(self) -> float:
        phi = _clamp01(self.phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)


@dataclass
class Cone:
    """Right circular cone: apex, axis direction (unit), height, base_radius."""

    bid: str
    apex: Vec3
    axis: Vec3  # unit, apex → base
    height: float
    base_radius: float
    phi: float = 0.0
    mass: float = 1.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5

    def __post_init__(self) -> None:
        self.axis = _normalize(self.axis)

    def base_center(self) -> Vec3:
        ax = self.axis
        return (
            self.apex[0] + ax[0] * self.height,
            self.apex[1] + ax[1] * self.height,
            self.apex[2] + ax[2] * self.height,
        )

    def config_energy(self) -> float:
        phi = _clamp01(self.phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)


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


class BodyWorld:
    def __init__(self, tol: float = 1e-6) -> None:
        self.spheres: Dict[str, Sphere] = {}
        self.cones: Dict[str, Cone] = {}
        self.contacts: Dict[Tuple[str, str], Contact] = {}
        self.intervention_log: List[InterventionRecord] = []
        self.tol = tol

    def add_sphere(self, s: Sphere) -> Sphere:
        if s.bid in self.spheres or s.bid in self.cones:
            raise ValueError(f"id exists {s.bid}")
        self.spheres[s.bid] = s
        return s

    def add_cone(self, c: Cone) -> Cone:
        if c.bid in self.spheres or c.bid in self.cones:
            raise ValueError(f"id exists {c.bid}")
        self.cones[c.bid] = c
        return c

    def _phi_of(self, bid: str) -> float:
        if bid in self.spheres:
            return self.spheres[bid].phi
        return self.cones[bid].phi

    def _set_phi(self, bid: str, phi: float) -> None:
        if bid in self.spheres:
            self.spheres[bid].phi = phi
        else:
            self.cones[bid].phi = phi

    def _config_of(self, bid: str) -> float:
        if bid in self.spheres:
            return self.spheres[bid].config_energy()
        return self.cones[bid].config_energy()

    def system_energy(self) -> float:
        e = sum(s.config_energy() for s in self.spheres.values())
        e += sum(c.config_energy() for c in self.cones.values())
        e += sum(ct.interface_energy() for ct in self.contacts.values())
        return e

    # --- contact predicates ---

    def contact_kind(self, a: str, b: str) -> Optional[str]:
        if a in self.spheres and b in self.spheres:
            sa, sb = self.spheres[a], self.spheres[b]
            d = _dist(sa.center, sb.center)
            if abs(d - (sa.radius + sb.radius)) <= self.tol:
                return "sphere_sphere_touch"
            return None

        if a in self.cones and b in self.cones:
            return self._cone_cone(a, b)

        # sphere–cone
        if a in self.spheres and b in self.cones:
            return self._sphere_cone(a, b)
        if a in self.cones and b in self.spheres:
            return self._sphere_cone(b, a)
        return None

    def _cone_cone(self, a: str, b: str) -> Optional[str]:
        ca, cb = self.cones[a], self.cones[b]
        ba, bb = ca.base_center(), cb.base_center()
        # base-to-base stack: opposite axes, bases nearly coincident
        if _dist(ba, bb) <= self.tol:
            if abs(_dot(ca.axis, cb.axis) + 1.0) <= 1e-3 or abs(_dot(ca.axis, cb.axis) - 1.0) <= 1e-3:
                return "cone_cone_base_stack"
        # coplanar base rings: bases in same plane, centers separated by Ra+Rb
        # plane of ca base: normal = axis, through ba
        rel = _sub(bb, ba)
        if abs(_dot(rel, ca.axis)) <= self.tol and abs(_dot(ca.axis, cb.axis) - 1.0) <= 1e-3:
            if abs(_dist(ba, bb) - (ca.base_radius + cb.base_radius)) <= self.tol:
                return "cone_cone_base_ring"
        return None

    def _sphere_cone(self, sid: str, cid: str) -> Optional[str]:
        s, c = self.spheres[sid], self.cones[cid]
        # apex touch
        if abs(_dist(s.center, c.apex) - s.radius) <= self.tol:
            return "sphere_cone_apex"
        # base ring: center in base plane, distance to base center = R ± r
        bc = c.base_center()
        rel = _sub(s.center, bc)
        if abs(_dot(rel, c.axis)) <= self.tol:
            rho = math.sqrt(max(0.0, _dot(rel, rel)))
            if abs(rho - (c.base_radius + s.radius)) <= self.tol:
                return "sphere_cone_base_outer"
            if abs(rho - abs(c.base_radius - s.radius)) <= self.tol and c.base_radius >= s.radius:
                return "sphere_cone_base_inner"
        return None

    # --- interventions ---

    def do_set_phase(self, bid: str, phi: float, label: str = "set_phi") -> float:
        phi = _clamp01(phi)
        e0 = self.system_energy()
        before = self._phi_of(bid)
        self._set_phi(bid, phi)
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
        amount = float(amount)
        sa, sb = self._phi_of(src), self._phi_of(dst)
        if amount > sa:
            amount = sa
        if amount > 1.0 - sb:
            amount = 1.0 - sb
        if amount < 0.0:
            amount = 0.0
        e0 = self.system_energy()
        self._set_phi(src, _clamp01(sa - amount))
        self._set_phi(dst, _clamp01(sb + amount))
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
        }
