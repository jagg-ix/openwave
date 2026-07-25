# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation, formal theorem status, finite-grid qualification, and subprediction status are separate. None of M9.78--M9.80 supplies external physical validation.

## Platform summary after M9.80

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
| Charge quantization | ⚠️ Integer winding is resolved; elementary-charge identity and normalization remain calibration-dependent. |
| Electron rest energy | ⚠️ A dimensionless scale minimum and localized stationary branch exist. The rest-mass unit remains calibration-required. |
| de Broglie clock | ⚠️ PhysLib proves a scoped entropic/physical proper-time equality. M9.65 failed. The frozen M9.71 ratio `1.074356835825` passes internal held-out and independent-method tests. M9.80 preserves the immutable record but blocks external comparison until analytic branch identity, particle identity, independent calibration, and an external dataset exist. |
| Particle stability | ⚠️ M9.69 constructs a localized non-Gaussian stationary branch. The live formal stack proves complete `H¹`/Born compactness, Hartree interaction closure, energy-split no-loss, compact minimizing orbits, and the Cazenave--Lions mechanism. M9.78 constructs a contracting finite-Galerkin Duhamel fixed point whose trajectory converges to Strang under refinement. M9.79 qualifies density-centroid recentering, local-interaction refinement, and finite-grid conservation. M9.80 finds positive constrained curvature and return to one finite-grid `H¹` orbit tube in radial, quadrupole, and shell directions. Continuum Duhamel well-posedness, continuum localization/conservation, analytic branch identity, calibration, and physical-particle identification remain open. |
| Magnetic moment and spin | ⚠️ Pauli-current and spin controls exist; a stable calibrated state and emergent electron g factor remain open. |
| Spin-1/2 statistics | ⚠️ The spinor changes sign after `2π` and returns after `4π`; exchange antisymmetry remains open. |
| Antimatter and annihilation | ⚠️ A reduced capture/annihilation/radiation ledger closes; full-PDE particle annihilation remains open. |
| Lepton mass spectrum | ❌ Tested low-parameter hierarchy laws fail predictive gates. No out-of-sample muon/tau hierarchy is selected. |
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
| Gravity | ⚠️ OpenWave has weak-field and equivalence-principle controls. PhysLib provides scoped Einstein--Maxwell--entropic actions/PDEs, ADM, maximal-development, cubic-semiflow, continuum `H¹` variational, and clock interfaces. A calibrated coupled physical evolution remains open. |

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

## Formal and computational interface summary

| Layer | Status | Boundary |
| --- | --- | --- |
| Complete continuum `H¹(ℝ³)` carrier, Born probability, weak compactness | directly proved | norm/mass no-loss remains interaction-dependent |
| Hartree convergence, energy-split no-loss, minimizer and compact orbit | directly proved | consumes localization and interaction closure |
| Cazenave--Lions minimizing-orbit stability | directly proved | consumes a global admissible conserved flow |
| Cubic--quintic coercivity and corrected weak/mild-flow composition | active PhysLib PR #16 | concrete Duhamel flow and conservation remain inputs |
| Lean/ZIL evidence lifecycle and omission reconciliation | active PhysLib PR #17 | implementation and kernel-verification state remain distinct |
| Bounded `H¹ → H¹` Laplacian premise | rejected | Fourier ratio grows as `k²`; natural weak bound is `H¹ → H⁻¹` |
| M9.78 finite-Galerkin Duhamel fixed point | numerically qualified | not a continuum Strichartz theorem |
| M9.79 dynamically recentered conservation campaign | numerically qualified | not a continuum localization or conservation theorem |
| M9.80 minimizing-orbit identification | numerically qualified | not analytic Lean identification or particle identity |
| M9.71 replacement radial mode | internally robust and externally blocked | no external dataset or physical validation |

## Prediction ledger

| Record | State |
| --- | --- |
| M9.65 Gaussian breathing ratio `2.634371114527` | frozen, internally tested, falsified |
| M9.71 stationary-branch radial ratio `1.074356835825` | frozen, internally passed, external comparison blocked by prerequisites |

Current methodological counts:

- 2 frozen/preregistered subpredictions;
- 2 internally tested subpredictions;
- 1 internally passed and 1 falsified;
- 0 externally tested predictions;
- 0 validated physical predictions.

All 21 platform criteria have evidence. None is fully validated. The sole criterion-level negative remains the predictive lepton-mass hierarchy.
