"""
h0 — Harness as explicit costed intervention

Constructive only. Not a natural Earth harness.
Work to hold φ away from φ_ambient is logged every tick and stored
in E_dissipated so the system audit still closes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)


@dataclass
class InterventionRecord:
    label: str
    kind: str  # set | engage | release | harness_tick
    delta_e: float
    detail: dict = field(default_factory=dict)


@dataclass
class HarnessParcel:
    phi: float = 0.0
    phi_ambient: float = 0.0
    kappa: float = 1.0e5  # W per unit |φ - φ_ambient| (model units)
    mass: float = 1.0
    rho_l: float = 1000.0
    rho_s: float = 1650.0
    latent_per_mass: float = 3.0e5
    pv_scale: float = 1.0e5

    e_dissipated: float = 0.0
    harness_engaged: bool = False

    intervention_log: List[InterventionRecord] = field(default_factory=list)

    # --- observation ---

    def get_phase(self) -> float:
        return self.phi

    def get_density(self) -> float:
        return (1.0 - self.phi) * self.rho_l + self.phi * self.rho_s

    def config_energy_at(self, phi: float) -> float:
        phi = _clamp01(phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)

    def get_config_energy(self) -> float:
        return self.config_energy_at(self.phi)

    def get_dissipated_energy(self) -> float:
        return self.e_dissipated

    def get_harness_power(self) -> float:
        """Instantaneous power demand if harness is engaged."""
        if not self.harness_engaged:
            return 0.0
        return self.kappa * abs(self.phi - self.phi_ambient)

    def get_total_energy(self) -> float:
        """E_obs = config + dissipated (bath/controller deposit)."""
        return self.get_config_energy() + self.e_dissipated

    # --- intervention ---

    def do_set_phase(self, phi_new: float, label: str = "set_phi") -> float:
        phi_new = _clamp01(phi_new)
        e_before = self.get_total_energy()
        phi_before = self.phi
        self.phi = phi_new
        e_after = self.get_total_energy()
        delta_e = e_after - e_before
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="set",
                delta_e=delta_e,
                detail={"phi_before": phi_before, "phi_after": phi_new},
            )
        )
        return delta_e

    def do_engage_harness(self, label: str = "engage") -> float:
        self.harness_engaged = True
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="engage",
                delta_e=0.0,
                detail={"phi": self.phi, "phi_ambient": self.phi_ambient},
            )
        )
        return 0.0

    def do_release_harness(self, label: str = "release") -> float:
        self.harness_engaged = False
        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="release",
                delta_e=0.0,
                detail={"phi": self.phi},
            )
        )
        return 0.0

    def do_harness_tick(self, dt: float, label: str = "harness_tick") -> float:
        """
        One hold step. If engaged, charge cost = κ|φ - φ_ambient| dt
        into E_dissipated. φ does not change.
        """
        if dt < 0.0:
            raise ValueError("dt must be non-negative")

        if not self.harness_engaged:
            self.intervention_log.append(
                InterventionRecord(
                    label=label,
                    kind="harness_tick",
                    delta_e=0.0,
                    detail={"dt": dt, "engaged": False, "cost": 0.0},
                )
            )
            return 0.0

        cost = self.kappa * abs(self.phi - self.phi_ambient) * dt
        e_before = self.get_total_energy()
        self.e_dissipated += cost
        e_after = self.get_total_energy()
        delta_e = e_after - e_before  # == cost

        self.intervention_log.append(
            InterventionRecord(
                label=label,
                kind="harness_tick",
                delta_e=delta_e,
                detail={
                    "dt": dt,
                    "engaged": True,
                    "phi": self.phi,
                    "phi_ambient": self.phi_ambient,
                    "power": self.kappa * abs(self.phi - self.phi_ambient),
                    "cost": cost,
                },
            )
        )
        return delta_e

    def audit_full_history(self, tolerance: float = 1e-9) -> dict:
        e_now = self.get_total_energy()
        sum_delta = sum(r.delta_e for r in self.intervention_log)
        e0 = e_now - sum_delta
        residual = e_now - (e0 + sum_delta)
        return {
            "ok": abs(residual) <= tolerance,
            "e_obs_t0": e0,
            "sum_delta_e": sum_delta,
            "e_obs_t1": e_now,
            "residual": residual,
            "e_config": self.get_config_energy(),
            "e_dissipated": self.e_dissipated,
            "n_interventions": len(self.intervention_log),
        }
