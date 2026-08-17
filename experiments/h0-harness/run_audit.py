"""
h0 harness audit

python run_audit.py
"""

from __future__ import annotations

import sys

from harness_parcel import HarnessParcel


def main() -> int:
    print("=== h0 harness as costed intervention ===")

    # --- off-ambient hold ---
    p = HarnessParcel(phi=0.0, phi_ambient=0.0, kappa=1.0e5)
    p.do_set_phase(0.8, label="set_off_ambient")
    p.do_engage_harness()
    for i in range(5):
        de = p.do_harness_tick(0.1, label=f"hold_{i}")
        print(f"  off-ambient tick {i}  power={p.get_harness_power():.4e}  ΔE={de:+.6e}")

    off_spent = p.get_dissipated_energy()
    r_off = p.audit_full_history()
    print(f"off-ambient E_dissipated = {off_spent:.6e}")
    print(f"off-ambient audit ok = {r_off['ok']}  residual = {r_off['residual']:.6e}")

    # --- at-ambient hold (should cost ~0) ---
    q = HarnessParcel(phi=0.0, phi_ambient=0.0, kappa=1.0e5)
    q.do_set_phase(0.0, label="set_ambient")
    q.do_engage_harness()
    for i in range(5):
        q.do_harness_tick(0.1, label=f"ambient_hold_{i}")
    at_spent = q.get_dissipated_energy()
    r_at = q.audit_full_history()
    print(f"at-ambient E_dissipated = {at_spent:.6e}")
    print(f"at-ambient audit ok = {r_at['ok']}")

    # --- release then tick costs nothing ---
    p.do_release_harness()
    de_idle = p.do_harness_tick(1.0, label="idle_tick")
    print(f"released tick ΔE = {de_idle:.6e}")

    # observation purity
    e_a = p.get_total_energy()
    _ = p.get_phase()
    _ = p.get_config_energy()
    _ = p.get_harness_power()
    e_b = p.get_total_energy()
    pure = e_a == e_b
    print(f"observation pure = {pure}")

    ok = (
        r_off["ok"]
        and r_at["ok"]
        and off_spent > 0.0
        and at_spent == 0.0
        and de_idle == 0.0
        and pure
    )
    if not ok:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
