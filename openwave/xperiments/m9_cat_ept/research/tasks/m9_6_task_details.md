# M9.6 task: scalar-carrier charge and spin audit

## Question

Which particle attributes are genuinely represented by the current single complex
scalar field, and which require a different carrier?

## Required distinctions

The audit must keep separate:

1. global `U(1)` phase symmetry and conserved norm;
2. local `U(1)` gauge covariance and electric charge;
3. intrinsic spatial rotation representation and spin;
4. model-specific topological charge.

## Frozen checks

- a global phase leaves the scalar norm invariant;
- a local phase leaves the norm invariant but changes the ordinary-gradient
  kinetic energy when no gauge field is present;
- the scalar intrinsic rotation factor is `+1` at both `2pi` and `4pi`;
- a reference spinor factor is `-1` at `2pi` and `+1` at `4pi`;
- the current model has no Maxwell source equation, electric-unit normalization,
  spinor carrier, or declared topological target/boundary class.

## Accepted conclusions

- positive: the current field has a global `U(1)` norm symmetry;
- negative: electric charge is not derived from that fact alone;
- negative: spin-1/2 is not represented by the trivial scalar rotation action;
- negative: no topological charge certificate is implemented for the current
  localized profile.

These are statements about the current carrier, not a theorem that every possible
scalar extension is incapable of charge or topology.

## Replacement routes

The audit must name and distinguish:

- locally gauge-coupled complex scalar: charged spin-0 matter;
- Dirac/Weyl spinor with local gauge coupling: spin-1/2 charge carrier;
- multi-component topological order parameter: possible winding/defect sectors.
