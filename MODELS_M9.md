# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation, formal theorem status, and subprediction status are separate. A scoped theorem or internally successful mode test changes the evidence attached to a row without automatically making that criterion physically validated.

## Platform summary after M9.74

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
| Electron rest energy | ⚠️ A dimensionless scale minimum and localized stationary branch exist. The rest-mass unit remains calibration-required. |
| de Broglie clock | ⚠️ PhysLib proves a scoped entropic/physical proper-time equality. The M9.65 Gaussian breathing ratio failed M9.68. M9.71 freezes `omega_radial / omega_Compton = 1.074356835825` from the non-Gaussian stationary branch. It passes held-out grids and M9.74 independently reproduces it with a radial-amplitude perturbation and periodogram on `20³/24³/28³`. No external experiment or physical Zitterbewegung identification is established. |
| Particle stability | ⚠️ The original action/profile families disperse. M9.69 constructs a localized non-Gaussian stationary branch. The live PhysLib branch already proves a complete continuum `H¹(ℝ³)` carrier, weak compactness with norm-bound retention, weak-plus-norm strong closure, tight-measure compactness consequences, a direct-method engine, local existence/uniqueness for supplied `C¹` generators, vanishing/dichotomy exclusion, and compact-sublevel orbital stability. PR #16 adds predicate-carrier bridges, constrained attainment, and concentration composition. Target-generator regularity, constraint closure, energy lower semicontinuity, derivation of tightness, global conserved flow, compact target sublevels, and physical-particle identification remain open. |
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
| Gravity | ⚠️ OpenWave has weak-field and equivalence-principle controls. PhysLib provides scoped Einstein--Maxwell--entropic actions/PDEs, ADM, maximal-development, cubic-semiflow, continuum `H¹` variational/dynamics, and clock interfaces. A calibrated coupled physical evolution remains open. |

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
| Metric-built Einstein--Maxwell--entropic field equations and global actions | proved with explicit scope | certified action derivatives, stationarity, carriers, and analytic hypotheses |
| Intrinsic curved Maxwell equation | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and maximal development | conditional | concrete vector field, tangency, fixed-Cauchy, and quotient data |
| Fixed-spatial-energy cubic continuum sector | jointly continuous contractive nonlinear semiflow; zero global attractor | dissipative pointwise cubic flow, not the conservative particle PDE |
| Complete continuum `H¹(ℝ³)` carrier and weak compactness | directly proved | weak subsequence and norm-bound retention; target mass closure remains separate |
| Weak-plus-norm strong H¹ closure | directly proved | requires target norm convergence |
| Tight probability and joint field/density subsequences | directly proved as consequences of tightness | recentered target tightness remains to derive |
| Local H¹ existence/uniqueness | directly proved for supplied `C¹` generators | concrete target generator regularity remains open |
| Complete-carrier and constrained direct method | directly proved; constrained bridge in PR #16 | weak closure and target-energy lower semicontinuity remain target-specific |
| Negative level, strict subadditivity, and positive binding gap | directly proved | exclude vanishing and dichotomy under explicit hypotheses |
| Compact branch from explicit concentration trichotomy | directly proved in PR #16 | target trichotomy/tightness remain open |
| Compact-sublevel Cazenave--Lions orbital stability | directly proved | requires compact target sublevel and conserved admissible flow |
| Cubic--quintic density coercivity | directly proved | exact pointwise factorization and lower bound |
| Entropic versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.69 stationary branch | qualified by three seeds and three nested grids | numerical full-equation branch, conditional on M9.63 coefficients |
| M9.65 breathing prediction | internally tested and falsified | Gaussian collective-coordinate approximation |
| M9.71 replacement radial mode | internally held-out and independently method-tested | no external experimental test or physical validation |

## Prediction ledger

| Record | State |
| --- | --- |
| M9.65 Gaussian breathing ratio `2.634371114527` | frozen, internally tested, falsified |
| M9.71 stationary-branch radial ratio `1.074356835825` | frozen, held-out-grid passed, M9.74 independent perturbation/estimator passed |

Current methodological counts:

- 2 frozen/preregistered subpredictions;
- 2 internally tested subpredictions;
- 1 internally passed and 1 falsified;
- 1 passed by an independent perturbation and estimator;
- 0 externally tested predictions;
- 0 validated physical predictions.

All 21 platform criteria have evidence. None is fully validated. The sole criterion-level negative remains the predictive lepton-mass hierarchy.
