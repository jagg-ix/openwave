# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation and formal theorem status are deliberately separated. A scoped Lean theorem improves the evidence attached to a row, but it does not become an in-platform physical validation without the corresponding calibrated OpenWave result.

## Platform summary after M9.62

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
| Electron rest energy | ⚠️ A dimensionless scale minimum and finite binding candidate exist. M9.62 records mass as calibration-required and promotes no physical mass prediction. |
| de Broglie clock | ⚠️ OpenWave separates reversible phase, entropic monotone, and geometry-clock channels. PhysLib proves an operational entropic/physical proper-time equality in the positive imaginary-Einstein sector under an explicit action-rate calibration; an independently calibrated OpenWave Zitterbewegung clock remains open. |
| Particle stability | ⚠️ The original M9.49/M9.52 action and profile families disperse. M9.59 selects a finite-grid cubic--quintic candidate; M9.60 fixes the cubic law only inside an explicit formal class and identifies quintic saturation as the minimal bounded local polynomial extension; M9.61 finds a normalized-Gaussian variational well and tightness proxy. Arbitrary-`H¹` orbital stability, coefficient selection, and physical calibration remain open. |
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
| Gravity | ⚠️ OpenWave has weak-field and equivalence-principle controls. PhysLib adds scoped metric-built Einstein--Maxwell--entropic action/PDE interfaces, global action, ADM constraint propagation, and conditional maximal-development infrastructure. A concrete calibrated coupled physical evolution remains open. |

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
| Metric-built Einstein--Maxwell--entropic field-equation constructors | proved with explicit scope | certified action derivative, stationarity, and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell equation and atlas independence | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and all-time flow | conditional | explicit globally Lipschitz vector field and tangency data |
| Maximal-development gluing | conditional | fixed-Cauchy extension and smooth quotient data |
| Gauge-covariant cubic Born-density law | directly proved inside an explicit class | locality, cubic homogeneity, gauge covariance, and normalization are premises |
| Cubic continuum `C(X,ℂ)` generator | local existence and uniqueness proved with explicit scope | pointwise cubic generator on a compact continuous-field carrier |
| Mode-diagonal unbounded Caticha generator | self-adjoint/closable with explicit scope | measurable real diagonal symbols |
| Homogeneous damping `-γI` | maximally dissipative with explicit contraction `C₀` semigroup | not the full nonlinear generator |
| Free kinetic Kolmogorov model | positive smooth kernel and bracket certificate directly proved | constant-coefficient free model, not general curved/nonlinear hypoellipticity |
| Entropic versus physical proper time | proved with explicit physical sector | positive imaginary-Einstein energy and action-rate calibration; not every entropy arrow |
| Selected cubic--quintic coefficients | open end-to-end | M9.60 proves structural but not numerical uniqueness |
| Arbitrary-`H¹` orbital stability | open end-to-end | M9.61 is a Gaussian-orbit/tightness bridge |
| Physical calibration | open end-to-end | M9.62 defines failure gates and promotes zero out-of-sample predictions |

## Calibration and falsification status

M9.62 defines a preregistered failure rule for every one of the 21 rows. The calibration ledger contains:

- 3 dimensionless-testable gates;
- 2 formal-conditional identities;
- 15 calibration-required gates;
- 1 retained negative;
- 0 prediction-ready physical claims.

Four independent mass/length/time/charge anchors can consume all four unit directions. Fitting those four anchors defines units; it does not constitute four predictions.

All 21 platform criteria have evidence. None is fully validated. The remaining negative is the predictive lepton-mass hierarchy. CAT/EPT remains an incomplete physical theory until coefficient selection, full continuum particle dynamics, and at least one preregistered out-of-sample prediction are closed.
