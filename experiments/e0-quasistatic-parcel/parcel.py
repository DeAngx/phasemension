"""
e0 — Quasi-static two-phase H₂O-like parcel

Tracks phase fraction and configurational energy under an explicit
observation / intervention boundary and a conservation audit.

Scope (Phase D): idealized single parcel. Not ice, not Earth, not
programmable matter. No harness. No spatial field.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InterventionRecord:
    """One logged do(...) step."""

    label: str
    phi_before: float
    phi_after: float
    delta_e: float  # Joules (model units)


@dataclass
class Parcel:
    """
    Single control volume with phase fraction φ ∈ [0, 1].

    φ = 0 → liquid-like
    φ = 1 → high-pressure-ice-like
    """

    # Material stand-ins (model units; not real EOS)
    rho_l: float = 1000.0  # kg/m³ liquid-like
    rho_s: float = 1650.0  # kg/m³ ice-VII-like order of magnitude
    latent_per_mass: float = 3.0e5  # J/kg stand-in for latent heat
    # PV stand-in: reference pressure * specific volume change scale
    pv_scale: float = 1.0e5  # J/kg stand-in for P·Δv contribution

    mass: float = 1.0  # kg — parcel mass (fixed)
    phi: float = 0.0  # current phase fraction

    intervention_log: list[InterventionRecord] = field(default_factory=list)

    # --- Observation (pure: no side effects) ---

    def get_phase(self) -> float:
        return self.phi

    def get_density(self) -> float:
        """Linear mix between liquid-like and solid-like density."""
        return (1.0 - self.phi) * self.rho_l + self.phi * self.rho_s

    def config_energy_at(self, phi: float) -> float:
        """
        Configurational energy for a given phase fraction.

        E_config(φ) = m * [ φ * L + φ * pv_scale ]
        Simple stand-in: latent + PV contribution both scale with φ.
        Kinetic declared 0 (quasi-static).
        """
        phi = _clamp01(phi)
        return self.mass * (phi * self.latent_per_mass + phi * self.pv_scale)

    def get_config_energy(self) -> float:
        return self.config_energy_at(self.phi)

    def get_kinetic_energy(self) -> float:
        return 0.0  # quasi-static: declared zero

    def get_total_energy(self) -> float:
        return self.get_kinetic_energy() + self.get_config_energy()

    # --- Intervention ---

    def do_set_phase_fraction(self, phi_new: float, label: str = "set_phi") -> float:
        """
        Force phase fraction to phi_new. Logs ΔE. Returns ΔE.

        This is do(φ = phi_new). Silent overrides are forbidden by construction.
        """
        phi_new = _clamp01(phi_new)
        e_before = self.get_total_energy()
        phi_before = self.phi

        self.phi = phi_new

        e_after = self.get_total_energy()
        delta_e = e_after - e_before

        self.intervention_log.append(
            InterventionRecord(
                label=label,
                phi_before=phi_before,
                phi_after=phi_new,
                delta_e=delta_e,
            )
        )
        return delta_e

    # --- Audit ---

    def audit_from(self, e_obs_t0: float, tolerance: float = 1e-9) -> dict:
        """
        Conservation check:

            E_obs(t0) + Σ ΔE_intervention = E_obs(t1)

        Call with e_obs_t0 captured *before* the interventions you want to
        account for (or use total log from start if t0 was the initial state).
        """
        sum_delta = sum(r.delta_e for r in self.intervention_log)
        e_obs_t1 = self.get_total_energy()
        predicted = e_obs_t0 + sum_delta
        residual = e_obs_t1 - predicted
        ok = abs(residual) <= tolerance

        return {
            "ok": ok,
            "e_obs_t0": e_obs_t0,
            "sum_delta_e": sum_delta,
            "e_obs_t1": e_obs_t1,
            "residual": residual,
            "tolerance": tolerance,
            "n_interventions": len(self.intervention_log),
        }

    def audit_full_history(self, tolerance: float = 1e-9) -> dict:
        """
        Audit assuming t0 was the initial state before any interventions
        (E at φ that existed before the first log entry, or current if empty).
        """
        if not self.intervention_log:
            e0 = self.get_total_energy()
            return self.audit_from(e0, tolerance=tolerance)

        # Reconstruct E at true start: current E minus all logged deltas
        e_now = self.get_total_energy()
        sum_delta = sum(r.delta_e for r in self.intervention_log)
        e0 = e_now - sum_delta
        return self.audit_from(e0, tolerance=tolerance)


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return float(x)
