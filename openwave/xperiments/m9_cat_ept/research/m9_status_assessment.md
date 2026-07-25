# CAT/EPT status after M9.89

## OpenWave platform validation

| Status | Count |
| --- | ---: |
| Fully validated in-platform | 4 |
| Partial / bounded controls | 16 |
| Honest negative | 1 |
| Not yet addressed | 0 |
| Total explicit criteria | 21 |

The validated rows are `particle_stability`, `spin_half_statistics`, `em_waves`, and `thermal_field`. The sole criterion-level negative remains the lepton-mass hierarchy.

## Re-evaluation of formerly unavailable infrastructure

The live PhysLib base at `829abc1c3a6c947de8aa1cab61194c3d83aa5c4e` already contains the complete H1 carrier, free unitary Schrödinger group, nonlinear continuum semiflows, Rellich/Hartree/no-loss chain, global conservative target certificate, compact minimizing orbit, uniform stability theorem, and identified-branch structure.

The adapter branch adds named constructors rather than new foundations:

- exact free H1 unitary-group certificate;
- construction of an identified branch from any actual minimizer;
- existence of an identified branch inside the compact uniformly stable minimizing orbit of every global conservative certificate.

## M9.87--M9.89 decisions

- **M9.87:** exact free/local group laws, reversibility, mass preservation, and split-flow composition close at roundoff. The previous `flow unavailable` classification is rejected.
- **M9.88:** all four perturbation families preserve mass below `9.1e-13`; energy drift is second order; localization and the H1 tube remain bounded; no Derrick-type escape is observed.
- **M9.89:** M9.69 remains within phase-aligned H1 distance `0.00161` of its computed standing-wave orbit on three grids while mass and energy remain closed.

## Boundary

Particle stability is validated only inside the platform rubric. The result does not establish physical particle identity, calibrated mass or charge, abundance, external agreement, or universal global well-posedness for arbitrary nonlinear continuum models.
