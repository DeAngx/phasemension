# bridge-invariance

Runnable check that the **water line** and **cube line** share one audit spine without collapsing into each other.

```bash
cd experiments/bridge-invariance
python run_bridge.py
```

## What it does

| Regime | Restriction | Operations |
|--------|-------------|------------|
| A | No geometry required | Isolated `Parcel` local `do_set_phase_fraction` |
| B | Shared face required | `CubeLattice` charge + face hops; skip-neighbor rejected |

Both must satisfy \(E(t_0)+\sum\Delta E=E(t_1)\).

## What it is not

- Not a claim that ice is cubes
- Not a merge of terrestrial forcing into discrete geometry
- Not harness

See [`concepts/two-lines-invariance.md`](../../concepts/two-lines-invariance.md).
