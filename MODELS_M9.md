# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation, formal theorem status, and subprediction status are deliberately separated. A scoped theorem, a frozen prediction, or a failed subprediction changes the evidence attached to a row without automatically changing the whole criterion to validated or negative.

## Platform summary after M9.68

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 0 |
| ⚠️ partial / bounded | 20 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

## Particles

| Criterion | Status |
| --- | --- |
| Charge quantization | ⚠️ Integer winding is resolved; the identity and normalization of elementary electric charge remain calibration-dependent. |
| Electron rest energy | ⚠️ A dimensionless scale minimum and localized branch exist. The rest-mass unit remains calibration-required. |
| de Broglie clock | ⚠️ PhysLib proves an operational entropic/physical proper-time equality in a scoped positive-imaginary-Einstein sector. The frozen M9.65 Gaussian breathing prediction was independently tested in M9.68 and fails by `43%`--`49%`. This rejects that collective-coordinate subprediction, not all clock channels or a physical Zitterbewegung model. |
| Particle stability | ⚠️ The original action/profile families disperse. M9.67 keeps scale, anisotropic, phase-chirp, translated, and smooth-noise perturbations bounded on two grids and respects the coercive gradient estimate. M9.66 rejects Gaussian peak-density matching as the current first-principles selection law. A stationary non-Gaussian branch, kernel `H¹` theorem, and physical particle remain open. |
| Magnetic moment and spin | ⚠️ Pauli-current and spin controls exist; a stable calibrated state and emergent electron g factor remain open. |
| Spin-1/2 statistics | ⚠️ The spinor changes sign after `2π` and returns after `4π`; exchange antisymmetry remains open. |
| Antimatter and annihilation | ⚠️ A reduced capture/annihilation/radiation ledger closes; full-PDE particle annihilation remains open. |
| Lepton mass spectrum | ❌ Tested low-parameter hierarchy laws fail predictive gates. No out-of-sample muon/tau hierarchy with residual degrees of freedom is selected. |
| Dark matter candidate | ⚠️ A neutral fixed-charge variational candidate exists; full-PDE stability, abundance, and phenomenology remain open. |
| Quarks | ⚠️ Finite SU(3), singlet, Wilson-loop, fractional-charge, and CKM controls exist; dynamical QCD and physical hadron spectra remain open. |
| Baryons | ⚠️ A charged-triplet graph control exists; physical quark dynamics and baryon spectra remain open. |
| Mesons | ⚠️ A neutral-pair graph control exists; physical meson spectra and decay channels remain open. |

## Forces

| Criterion | Status |
| --- | --- |
| Electric force | ⚠️ A regularized inverse-square asymptote exists; a force between calibrated stable emergent charges remains open. |
| Magnetic force | ⚠️ A regularized dipole `r^-4` asymptote exists; a calibrated particle-level magnetic interaction remains open. |
| Strong force | ⚠️ Cornell/flux-tube and string-breaking controls exist; dynamical QCD and jointly predicted tension/breaking remain open. |
| Weak force | ⚠️ A reduced left-selective transition and decay ledger exists; electroweak gauge dynamics and physical rates remain open. |
| Gravity | ⚠️ OpenWave has weak-field and equivalence-principle controls. PhysLib adds scoped metric-built Einstein--Maxwell--entropic actions/PDEs, ADM, maximal-development, cubic-semiflow, and clock interfaces. A concrete calibrated coupled physical evolution remains open. |

## Waves and quantum emergence

| Criterion | Status |
| --- | --- |
| EM waves | ⚠️ Transverse Maxwell and massless reductions are computationally qualified; PhysLib provides scoped intrinsic/distributional Maxwell interfaces. Common calibrated Cauchy data remain open. |
| Klein-Gordon | ⚠️ A massive spectral dispersion reduction exists; a native calibrated particle sector remains open. |
| Orbital quantization | ⚠️ A converged radial bound-mode ladder exists; native calibrated atomic structure remains open. |

## Thermal sector

| Criterion | Status |
| --- | --- |
| Heat / thermal-field sector | ⚠️ Heat conservation, entropy growth, and diffusion-dissipation controls exist; calibrated microscopic thermodynamics remain open. |

## Formal interface summary

| Formal layer | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic field equations and global actions | proved with explicit scope | certified action derivative, stationarity, carriers, and analytic hypotheses |
| Intrinsic curved Maxwell equation | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and maximal development | conditional | concrete vector field, tangency, fixed-Cauchy, and quotient data |
| Gauge-covariant cubic Born-density law | directly proved inside an explicit class | locality, cubic homogeneity, covariance, and normalization are premises |
| Fixed-spatial-energy cubic continuum sector | jointly continuous contractive nonlinear semiflow; zero global attractor | dissipative pointwise cubic flow, not the conservative particle PDE |
| Mode-diagonal and homogeneous generator sectors | self-adjoint/closable or maximally dissipative with explicit semigroups | declared diagonal or bounded homogeneous realizations |
| Free kinetic Kolmogorov model | positive smooth kernel, bracket certificate, and explicit PDE identities | free constant-coefficient model |
| Entropic versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.63 coefficient rule | scale stationarity derived; peak rule rejected as current first-principles condition | Gaussian stationary-field residual is `0.485819`; alternative selections exist |
| Spatial cubic--quintic Laplacian PDE | exact coercive bound plus nested/adversarial numerics | no kernel `H¹` local/global theorem or orbital stability |
| M9.65 breathing prediction | independently tested and falsified inside OpenWave | no external experiment; not a theory-wide rejection |

## Calibration, falsification, and prediction status

The immutable M9.65 record was:

```text
prediction: omega_breath / omega_Compton = 2.634371114527
tolerance:  5% relative error
```

The M9.68 no-refit comparison gives:

```text
16^3: 1.441044883822
20^3: 1.346755183528
24^3: 1.494924712561
relative discrepancy: 43%--49%
verdict: falsified inside OpenWave
```

The current methodological ledger is:

- 1 frozen/preregistered physical subprediction;
- 1 independently tested subprediction;
- 0 passed predictions;
- 1 falsified subprediction;
- 0 externally tested predictions;
- 0 validated physical predictions.

All 21 platform criteria have evidence. None is fully validated. The sole criterion-level negative remains the predictive lepton-mass hierarchy. The M9.65 failure is retained as a scoped negative result for the Gaussian collective-coordinate approximation.
