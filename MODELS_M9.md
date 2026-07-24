# OpenWave M9 CAT/EPT comparison profile

This file is the canonical **M9 extension column** for the shared OpenWave comparison rubric. The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`.

Platform validation, formal theorem status, and prediction status are deliberately separated. A scoped Lean theorem or a frozen prediction improves the evidence attached to a row, but neither becomes an in-platform physical validation without the corresponding independent result.

## Platform summary after M9.65

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
| Electron rest energy | ⚠️ A dimensionless scale minimum and localized branch exist. The rest-mass unit remains calibration-required; M9.65 does not predict the mass itself. |
| de Broglie clock | ⚠️ OpenWave separates reversible phase, entropic monotone, and geometry-clock channels. PhysLib proves an operational entropic/physical proper-time equality in the positive imaginary-Einstein sector under an explicit action-rate calibration. M9.65 freezes `omega_breath / omega_Compton = 2.634371114527`, but this breathing mode is untested and is not yet a physical Zitterbewegung identification. |
| Particle stability | ⚠️ The original M9.49/M9.52 action and profiles disperse. M9.63 selects `alpha = 74.6630446265`, `beta = 415.7483217224` under two declared Gaussian self-consistency conditions and retains the branch on three grids. M9.64 proves an exact coercive energy bound, preserves mass/energy on nested spatial grids, and keeps the preregistered small scale orbit bounded. Kernel-formalized arbitrary-`H¹` orbital stability and a physical particle remain open. |
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
| Gravity | ⚠️ OpenWave has weak-field and equivalence-principle controls. PhysLib adds scoped metric-built Einstein--Maxwell--entropic action/PDE interfaces, global action, ADM constraint propagation, conditional maximal-development infrastructure, and calibrated clock theorems. A concrete calibrated coupled physical evolution remains open. |

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
| Cubic continuum `C(X,ℂ)` sector | local existence/uniqueness and exact global positive-time irreversible flow | pointwise cubic generator, not the selected spatial differential cubic--quintic PDE |
| Fixed multiplication-energy plus cubic damping | explicit global positive-time flow and norm contraction | fixed spatial energy field, not state-dependent or differential Hamiltonian |
| Mode-diagonal unbounded Caticha generator | self-adjoint/closable with explicit scope | measurable real diagonal symbols |
| Homogeneous damping and phase-plus-damping | maximally dissipative with explicit contraction `C₀` semigroups | homogeneous bounded sectors |
| Free kinetic Kolmogorov model | positive smooth kernel, bracket certificate, and explicit PDE derivative identities | constant-coefficient free model |
| Entropic versus physical proper time | proved with explicit physical sector | positive imaginary-Einstein energy and action-rate calibration; not every entropy arrow |
| M9.63 coefficient pair | unique under two declared self-consistency conditions | those conditions are not yet derived from the full action |
| M9.64 spatial cubic--quintic flow | exact coercive bound and converged numerical bridge | arbitrary-`H¹` kernel theorem remains open |
| M9.65 breathing prediction | prediction-ready and frozen | not independently tested or validated |

## Calibration, falsification, and prediction status

M9.62 defined a preregistered failure rule for all 21 rows and, at that snapshot, contained zero prediction-ready claims. M9.65 adds one separate immutable prediction record:

```text
prediction: omega_breath = 2.634371114527 * m c^2 / hbar
tolerance:  5% relative error
status:     prediction-ready, untested, unvalidated
```

The current methodological ledger is therefore:

- 3 dimensionless-testable gates;
- 2 formal-conditional identities;
- 15 calibration-required gates;
- 1 retained negative;
- 1 prediction-ready physical claim;
- 0 tested physical predictions;
- 0 validated physical predictions.

Four independent mass/length/time/charge anchors can consume all four unit directions. Fitting those anchors defines units; it does not itself validate the breathing prediction or the theory.

All 21 platform criteria have evidence. None is fully validated. The remaining negative is the predictive lepton-mass hierarchy. CAT/EPT remains incomplete until the M9.63 conditions are derived or replaced, the full spatial particle theorem is closed, and the frozen M9.65 prediction survives an independent comparison without refitting.
