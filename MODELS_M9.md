# OpenWave M9 CAT/EPT comparison profile

The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`. Platform validation, formal theorem status, and physical validation remain distinct.

## Platform summary after M9.89

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 4 |
| ⚠️ partial / bounded | 16 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

The validated rows are:

- particle stability / Derrick escape;
- spin-1/2 statistics;
- source-free Maxwell waves;
- the explicit dimensionless thermal field.

## Particle-stability closure

The earlier status underestimated the live repository. PhysLib already contains:

- the genuine free Schrödinger unitary group on `L²(ℝ³)`;
- the complete `H¹(ℝ³)` Bessel-energy carrier;
- exact free-group identity, composition, norm preservation, and strong continuity;
- exact nonlinear continuum semiflows for the fixed multiplication-energy sectors;
- localized Rellich, Born `L^(6/5)`, Hartree, energy no-loss, minimizer, and compact-orbit results;
- `GlobalConservativeBornMildFlowCertificate`;
- compact minimizing-orbit uniform stability;
- `IdentifiedTargetBranchCertificate` and its minimizing-orbit membership theorem.

M9.87--M9.89 add the missing named adapters and executable instantiation:

| Record | Result |
| --- | ---: |
| Free subflow group error | `5.63e-16` |
| Local subflow group error | `1.46e-16` |
| Maximum mass error across perturbation campaign | `9.01e-13` |
| Maximum finest energy drift | `4.72e-8` |
| Maximum declared perturbation `H¹` distance | `0.222281` |
| Maximum standing-wave phase-orbit `H¹` error | `0.0016073` |
| Maximum standing-wave energy drift | `1.77e-9` |

The conservative campaign covers chirp, radial, quadrupole, and smooth-noise perturbations. No Derrick-type escape is observed, energy drift is second order under time refinement, and M9.69 remains in its computed phase orbit on `20³`, `24³`, and `28³` grids.

**Boundary:** this validates the literal criterion inside OpenWave. It does not identify the branch as an electron or another observed particle, calibrate physical units, or provide external experimental validation.

## Remaining criteria

| Domain | Remaining blocker classes |
| --- | --- |
| Particle identity and masses | independent calibration and out-of-sample predictions |
| Magnetic moment | emergent calibrated g factor |
| Antimatter/composites/dark matter | full interacting dynamics and phenomenology |
| Strong and weak sectors | dynamical gauge theories and physical rates |
| Gravity | calibrated coupled physical evolution |
| Klein-Gordon and atomic structure | native calibrated particle/atomic sectors |

The sole criterion-level negative remains the predictive lepton-mass hierarchy. The frozen M9.71 radial-mode record remains internally tested but externally blocked.
