# CAT/EPT status after M9.86

## OpenWave platform validation

| Status | Count |
| --- | ---: |
| Fully validated in-platform | 3 |
| Partial / bounded controls | 17 |
| Honest negative | 1 |
| Not yet addressed | 0 |
| Total explicit criteria | 21 |

The validated rows remain `spin_half_statistics`, `em_waves`, and `thermal_field`. The sole criterion-level negative remains the lepton-mass hierarchy.

## New particle-stability closure

The live PhysLib base now proves the missing abstract bridge from local Rellich convergence, recentered uniform tails, and a uniform `L3` density-difference bound to global `L1`, strong `L^(6/5)`, and Hartree convergence.

OpenWave M9.84--M9.86 execute the corresponding finite-grid evidence chain:

- **M9.84:** adjacent-grid `L^(6/5)` error decreases `0.01854 → 0.00621 → 0.00298`; periodic Hartree error decreases `0.00514 → 0.00329 → 0.000644`; the farthest recentered tail is below `6e-6`.
- **M9.85:** target-interaction error decreases `0.04461 → 0.02497 → 0.000727`; nested `H1` distance decreases `0.1865 → 0.1060 → 0.0446`; energy-split error reaches `0.00120` with normalization retained.
- **M9.86:** nested-grid distance to the frozen `32³` reference decreases `0.1316 → 0.1022 → 0.0446`; unrelated seeds remain within `0.01093` in `H1`; the reference feature fingerprint is frozen.

## Retained boundaries

These results do not establish:

- the continuum energy-critical Duhamel/Strichartz flow;
- model-level local Rellich and recentered-tail hypotheses in Lean;
- continuum local cubic--quintic interaction convergence;
- global continuum mass and energy conservation;
- analytic identification of M9.69 with the minimizing orbit;
- physical particle identity, independent calibration, or external agreement.

## Formal dependencies

- Live PhysLib base: `c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3`.
- Criterion bridge PR #18: `19ef639d0ab849f92fb462d5899817ac1a5c4161`.
- Active PR #16: cubic--quintic compactness and corrected weak/mild-flow composition.
- Active PR #17: Lean/ZIL evidence lifecycle and omission reconciliation.

## Current theory classification

CAT/EPT remains an incomplete physical theory. M9.84--M9.86 replace an opaque compactness gap with explicit, measured model premises and a reproducible candidate-branch certificate. They do not change the criterion counts or constitute experimental validation.
