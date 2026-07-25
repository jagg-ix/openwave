# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation, formal theorem status, finite-grid qualification, and physical validation are separate. M9.81--M9.83 validate three literal platform criteria while retaining their stronger emergence, identity, and calibration boundaries.

## Platform summary after M9.83

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 3 |
| ⚠️ partial / bounded | 17 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

## Particles

| Criterion | Status |
| --- | --- |
| Charge quantization | ⚠️ Integer winding is resolved; elementary-charge identity and normalization remain calibration-dependent. |
| Electron rest energy | ⚠️ A dimensionless scale minimum and localized stationary branch exist. The rest-mass unit remains calibration-required. |
| de Broglie clock | ⚠️ PhysLib proves a scoped entropic/physical proper-time equality. M9.65 failed. The frozen M9.71 ratio `1.074356835825` passes internal tests, but external comparison remains blocked by analytic identity, calibration, and dataset prerequisites. |
| Particle stability | ⚠️ M9.69--M9.80 provide a stationary branch, finite-Galerkin Duhamel closure, dynamic recentering/conservation, positive constrained curvature, and return to one finite-grid `H¹` orbit tube. Continuum Duhamel well-posedness, continuum localization/conservation, analytic branch identity, calibration, and physical-particle identification remain open. |
| Magnetic moment and spin | ⚠️ Pauli-current and spin controls exist; a stable calibrated state and emergent electron g factor remain open. |
| Spin-1/2 statistics | ✅ Validated in-platform: `2π` sign reversal and `4π` return, fermion exchange phase `-1`, two-state antisymmetry, exchange involution, and identical-state exclusion all close. A specific CAT/EPT particle is not dynamically proven fermionic and is not identified with the electron. |
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
| Gravity | ⚠️ OpenWave has weak-field and equivalence-principle controls. PhysLib provides scoped Einstein--Maxwell--entropic actions/PDEs, ADM, maximal-development, continuum `H¹` variational, and clock interfaces. A calibrated coupled physical evolution remains open. |

## Waves and quantum emergence

| Criterion | Status |
| --- | --- |
| EM waves | ✅ Validated in-platform: exact transverse Maxwell evolution conserves energy, propagates at the declared speed, closes the massless-wave bridge and resolution gates, while PhysLib constructs a smooth source-free harmonic Maxwell plane wave. Photon quantization, full coupled CAT/EPT emergence, and physical calibration remain open. |
| Klein-Gordon | ⚠️ A massive spectral dispersion reduction exists; a native calibrated particle sector remains open. |
| Orbital quantization | ⚠️ A converged radial bound-mode ladder exists; native calibrated atomic structure remains open. |

## Thermal sector

| Criterion | Status |
| --- | --- |
| Heat / thermal-field sector | ✅ Validated in-platform: exact spectral heat flow conserves heat, increases entropy, dissipates variance, obeys exact mode-decay and semigroup laws, freezes at zero diffusivity, and is resolution stable; PhysLib supplies the finite spectral semigroup and zero-mode theorem. Microscopic thermodynamics, material calibration, quantum thermalization, and relativistic heat transport remain open. |

## Reduction audit

The deep repository grep classified all twenty former partials. Only three had their literal criterion closed by both formal and executable evidence. The remaining seventeen are blocked by one or more of:

- physical identity or independent calibration;
- full interacting or gauge dynamics;
- continuum well-posedness/conservation;
- analytic branch identification;
- external datasets and out-of-sample prediction.

## Formal and computational interface summary

| Layer | Status | Boundary |
| --- | --- | --- |
| Fermion exchange and Pauli exclusion | directly proved / executable | no dynamical assignment to a specific CAT/EPT particle |
| Harmonic source-free Maxwell plane wave | directly proved / executable | no photon quantization or empirical calibration |
| Finite spectral heat semigroup and thermal controls | directly proved / executable | no microscopic or material-specific thermodynamics |
| Complete continuum `H¹(ℝ³)` carrier, Born compactness and Hartree closure | directly proved | target localization and continuum flow remain model-specific |
| Cubic--quintic weak/mild-flow composition | active PhysLib PR #16 | concrete continuum Duhamel flow and conservation remain inputs |
| Lean/ZIL evidence lifecycle | active PhysLib PR #17 | implementation and kernel-verification state remain distinct |

## Prediction ledger

| Record | State |
| --- | --- |
| M9.65 Gaussian breathing ratio `2.634371114527` | frozen, internally tested, falsified |
| M9.71 stationary-branch radial ratio `1.074356835825` | frozen, internally passed, external comparison blocked by prerequisites |

The three platform validations are not external physical validations. The sole criterion-level negative remains the predictive lepton-mass hierarchy.
