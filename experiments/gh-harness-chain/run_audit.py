"""gh harness-chain audit — python run_audit.py"""

from __future__ import annotations

import sys

from chain_harness import HarnessChain


def main() -> int:
    print("=== gh harness on cube chain ===")

    h = HarnessChain()
    chain = h.add_chain_x(4)
    coords = [c.coord for c in chain]

    # Charge head and hold off ambient (costs)
    h.do_set_phase(coords[0], 1.0, label="charge")
    h.do_engage(coords[0])
    for i in range(3):
        de = h.do_harness_tick(coords[0], 0.1, label=f"hold_head_{i}")
        print(f"  hold head tick {i} ΔE={de:+.6e}")

    head_spent = h.cubes[coords[0]].e_dissipated

    # Release and hop packet down the chain
    h.do_release(coords[0])
    for i in range(3):
        h.do_transfer(coords[i], coords[i + 1], 1.0, label=f"hop_{i}")

    # Hold tail (still off ambient if φ moved with packet)
    h.do_engage(coords[3])
    for i in range(2):
        h.do_harness_tick(coords[3], 0.1, label=f"hold_tail_{i}")

    tail_spent = h.cubes[coords[3]].e_dissipated

    rejected = False
    try:
        h.do_transfer(coords[0], coords[2], 0.1, label="skip")
    except ValueError:
        rejected = True

    r = h.audit_full_history()
    print(f"head dissipated={head_spent:.6e} tail dissipated={tail_spent:.6e}")
    print(f"total dissipated={r['total_dissipated']:.6e}")
    print(f"residual={r['residual']:.6e} ok={r['ok']}")
    print(f"skip rejected={rejected}")

    ok = r["ok"] and rejected and head_spent > 0.0 and tail_spent > 0.0
    if not ok:
        print("FAIL")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
