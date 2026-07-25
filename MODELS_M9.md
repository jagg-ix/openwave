# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation, formal theorem status, and subprediction status are separate. Scoped formal closure and finite-grid orbital evidence do not automatically make a criterion physically validated.

## Platform summary after M9.77

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
| de Broglie clock | ⚠️ PhysLib proves a scoped entropic/physical proper-time equality. M9.65 failed. The frozen M9.71 ratio `1.074356835825` passes held-out grids and the independent M9.74 perturbation/periodogram test. No external experiment or physical Zitterbewegung identification is established. |
| Particle stability | ⚠️ M9.69 constructs a localized non-Gaussian stationary branch. The live formal stack proves complete `H¹`/Born compactness, Hartree interaction closure, energy-split no-loss, compact minimizing orbits, and the Cazenave--Lions stability mechanism. M9.75 rejects the false bounded `H¹ → H¹` Laplacian target and unconditional weak closure/lower-semicontinuity claims. M9.76 qualifies the translation quotient and centered tails. M9.77 keeps five perturbations in a small aligned `H¹` tube. The concrete energy-critical Duhamel flow, continuum conservation, analytic branch identification, calibration, and a physical particle remain open. |
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

## Formal interface summary

| Formal layer | Status | Boundary |
| --- | --- | --- |
| Complete continuum `H¹(ℝ³)` carrier and weak compactness | directly proved | norm/mass no-loss remains target-dependent |
| Born probability and first-moment compactness | directly proved | recentered moment bound remains model-specific |
| Hartree interaction convergence and energy-split no-loss | directly proved | local cubic--quintic interaction convergence remains separate |
| Born-law minimizer and compact minimizing orbit | directly proved | consumes localization, weak admissibility, and interaction closure |
| Cazenave--Lions minimizing-orbit stability | directly proved | consumes a global admissible energy-conserving flow |
| Cubic--quintic coercivity and concentration branch composition | proved in active PhysLib PR #16 | localization/trichotomy inputs remain explicit |
| Correct weak `H¹ → H⁻¹` generator and mild-flow certificate | proved in active PhysLib PR #16 | concrete Duhamel/Strichartz construction remains open |
| Strong normalized-mass closure from interaction convergence | proved in active PhysLib PR #16 | no global weak closure of unit sphere is claimed |
| Compact target orbit from Born localization | proved in active PhysLib PR #16 | recentered first moment and local interaction convergence remain inputs |
| Stable minimizing orbit from conservative weak/mild-flow certificate | proved in active PhysLib PR #16 | continuum flow/conservation remain certificate data |
| Bounded `H¹ → H¹` Laplacian premise | rejected | Fourier ratio grows as `k²` |
| Global weak closure of unit mass sphere | rejected | orthonormal modes weakly converge to zero |
| Unconditional weak lower semicontinuity of attractive energy | rejected | translated negative-energy states weakly converge to zero |
| M9.69 stationary branch | OpenWave numerical result | conditional on selected coefficients |
| M9.77 aligned long-time campaign | OpenWave numerical result | finite grid and time |
| M9.71 replacement radial mode | internally robust | no external experiment or physical validation |

## Prediction ledger

| Record | State |
| --- | --- |
| M9.65 Gaussian breathing ratio `2.634371114527` | frozen, internally tested, falsified |
| M9.71 stationary-branch radial ratio `1.074356835825` | frozen, held-out-grid passed, independent perturbation/estimator passed |

Current methodological counts:

- 2 frozen/preregistered subpredictions;
- 2 internally tested subpredictions;
- 1 internally passed and 1 falsified;
- 0 externally tested predictions;
- 0 validated physical predictions.

All 21 platform criteria have evidence. None is fully validated. The sole criterion-level negative remains the predictive lepton-mass hierarchy.