# Possible Code Directions

Nothing implemented yet. Just markers so we don't lose the thread.

## Near-term experiments

1. **Anisotropic phase-field toy**  
   2D Cahn-Hilliard or Allen-Cahn with orientation-dependent interfacial energy.  
   Goal: watch a circular interface spontaneously develop facets under strong anisotropy.

2. **Stabilized interface / "harness" term**  
   Add an extra field or potential that penalizes collapse of the interface even when classical surface tension would drive it to disappear.  
   Goal: a bubble-like region that remains coherent under conditions that would normally pop it.

3. **Density as controllable field**  
   Simple continuum model where local density can be driven and held away from equilibrium value by continuous forcing.  
   Couple it to an interface so the two talk to each other.

4. **Memory across transition**  
   After a faceting / solidification step, check whether any signature of the previous soft state survives in the ordered structure (orientation history, residual stress, latent field, etc.).

## Longer horizon

- Discrete exterior calculus on evolving meshes so geometric operators stay clean while topology and density change.
- Constraint language that can express "this configuration is authorized to persist" as a first-class statement.
- Link back to Computational Seal ideas (address, lineage, authority) if the geometry/density layer ever needs provenance of its own.

## Explicit non-goals for now

- Production-grade simulation suite
- Pretty rendering first
- Claims that this is "solved"

Just mess around until something feels load-bearing.
