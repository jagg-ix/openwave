# OpenWave M9 CAT/EPT comparison profile

The canonical executable source is `openwave/xperiments/m9_cat_ept/model_conformance_current.py`; it overlays exactly the three M9.96 findings on the historical 21-row profile in `model_conformance.py`. Platform validation, formal theorem status, current-tree evidence, physical identity, calibration, and experimental validation are separate layers.

## Platform summary after M9.96

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 7 |
| ⚠️ partial / bounded | 13 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

Validated rows:

- charge quantization;
- particle stability / Derrick escape;
- spin-1/2 statistics;
- source-free Maxwell waves;
- free massive Klein-Gordon evolution;
- dimensionless Coulomb orbital quantization;
- explicit dimensionless thermal field.

## M9.90--M9.93 retained validated infrastructure

M9.90 closes field-derived winding and exact third-charge arithmetic while preserving elementary-charge and sector-selection boundaries. M9.91 closes free massive Klein-Gordon dispersion, group, reversal, energy, and massless-limit controls. M9.92 closes dimensionless Coulomb radial and cross-angular-momentum orbital quantization. M9.93 adds the selected PhysLib contract, reusable particle-state API, canonical registration, and periodic-covariant translations and observables.

The repository-default particle has no physical name or calibration record. The neutral stationary branch is available. Nonzero winding may be seeded and measured, but it is not a stable charged stationary branch until the same solved state closes winding, localization, residual, and dynamical-stability gates.

## M9.94a — branch-wide formalization import

The import is pinned to:

```text
repository   jagg-ix/entropic-physlib-private
branch       entropic-physlib-linear-full
base commit  e10af9a3b47bf90afc0a88167a5d495b6935f4dc
current tree 239a663a3192a3144fb998e7bb200e09689a3bb9
Physlib.lean 182a06e0f50314ec54436da602b4ac86eba4ee08
```

| Imported surface | Count |
| --- | ---: |
| ZIL graphs | 11 |
| ZIL entity identifiers | 422 |
| Explicit open/external boundaries | 12 |
| Blob-pinned Lean aggregate/source files | 24 |
| Criterion-specific Pauli/Maxwell extension sources | 2 |

Operational/status graphs cover electrogravitic action closure, Lindblad-driven leads, Liouville second quantization, the Cauchy weak limit, and Lindblad trace preservation. Corpus graphs cover Rivers scalar Green functions and their continuum extension, Lovelock–Rund continuum variation, pointwise operators and invariant geometry, and Veliev periodic Schrödinger perturbation theory.

Lean remains proof authority. ZIL preserves components, sources, assumptions, claims, proof tokens, dependencies, pending/conditional/open states, rules, queries, constructive-QFT boundaries, and external analytic requirements.

The current-tree force overlay adds:

- the magnetic-moment/spin-projector relation;
- gauge invariance of the Pauli coupling `sigma^(mu nu) F_(mu nu)`;
- Dirac and anomalous Pauli-interaction splits;
- Maxwell-implies-continuity;
- the conditional conserved-current-to-Maxwell construction;
- gauge invariance of the Maxwell stress source.

Formal availability does not promote a physical criterion.

## M9.94 — canonical spin and magnetic moment

The canonical three-dimensional particle envelope is embedded into a Pauli spinor. Spectral Pauli-current observables close normalization, `J_z = 1/2`, zero orbital control, periodic covariance, opposite-spin reversal, and the tree-level `g = 2` ratio. PhysLib supplies the Pauli tensor, spin-orbit/Foldy-Wouthuysen structure, and the structural Schwinger identity.

**Boundary:** the original M9.94 control is a Gaussian envelope, not the stable neutral M9.69 branch and not a stable charged branch. The Schwinger anomaly is imported as formal structure, not derived from CAT/EPT dynamics. The criterion remains partial.

## M9.95 — canonical electric and magnetic pair bridge

One periodic pair carries declared winding sectors `+3` and `-3`, giving exact dimensionless charges `+1` and `-1`. The same envelopes carry Pauli-current magnetic moments, and one shared dimensionless interaction ledger drives both force kernels.

The bridge closes electric and magnetic energy derivatives, signs, action-reaction, superposition, legacy inverse-square and dipole `r^-4` asymptotes, Yukawa screening, the exact zero-screening Coulomb endpoint, and the Lorentz-EM decomposition/covariance boundary.

**Boundary:** winding is declared rather than embedded in stationary branches; the regularized dipole law is not derived from generated fields; charge, magnetic-moment, and force units remain uncalibrated. Both force criteria remain partial.

## M9.96a — charged stationary feasibility

The validated neutral M9.69 amplitude is multiplied by a regularized winding-three vortex. Four core scales are tested. Every seed is normalized and carries exact measured winding `n = 3`, hence exact arithmetic charge `q = 1`.

Under the full unconstrained selected scalar imaginary-time flow:

- three candidates retain winding three;
- one narrow-core candidate changes sector;
- no candidate simultaneously satisfies the stationary-residual and compact-radius gates;
- the best evolved residual remains approximately `0.512`;
- the best evolved radius is approximately `1.999`.

**Result:** the selected neutral scalar cubic--quintic action does not construct the required charged stationary branch. This is an explicit negative subresult for the current model, not a criterion-level negative and not evidence against a gauge/spinor extension.

## M9.96b — field-derived source and magnetic response

One winding-three candidate supplies its own charge density, convective phase current, Pauli magnetization current, scalar/vector potentials, and periodic electric and magnetic fields.

| Control | Result |
| --- | ---: |
| Integrated charge | `0.9999999999999997` |
| Zero-mode projection loss | `9.56e-3` |
| Projected Gauss residual | `3.67e-16` |
| Static Ampere residual | `5.38e-16` |
| Maximum `div B` | `6.94e-18` |
| Electric self-field energy | `2.026e-2` |
| Magnetic self-field energy | `2.804e-2` |

The magnetic moment is measured independently from the current integral and from the derivative of the weak uniform-field interaction energy:

```text
mu_current  = 1.4150287474588639
mu_response = 1.4150287474588639
```

**Boundary:** Maxwell backreaction is not included in the stationary equation, and the candidate is not a stable charged particle. The magnetic-moment criterion remains partial.

## M9.96c — field-force triangle

Two opposite field-derived candidates generate their own electric and magnetic fields. Force is measured by:

1. the Lorentz volume integral `integral (rho E + j x B) d^3x`;
2. the derivative of the cross interaction energy;
3. the flux of the cross Maxwell stress tensor.

At separation `16/3`:

| Quantity | Result |
| --- | ---: |
| Electric force, axial | `2.07159e-3` |
| Magnetic force, axial | `4.58535e-4` |
| Full Lorentz force, axial | `2.53013e-3` |
| Interaction-energy derivative | `2.47118e-3` |
| Maxwell-stress flux | `2.59376e-3` |
| Energy/Lorentz relative error | `2.33e-2` |
| Stress/Lorentz relative error | `2.52e-2` |
| Action-reaction relative error | `2.72e-9` |

This replaces the earlier direct softened Coulomb/dipole formulas as the candidate-level force evidence. The older kernels remain asymptotic controls.

**Boundary:** center-of-energy acceleration, torque, and spin precession have not been measured in the full coupled PDE. A stable charged pair and physical unit map remain absent. Electric and magnetic force remain partial.

## Current status discipline

| Criterion | Current stronger evidence | Promotion blocker |
| --- | --- | --- |
| Magnetic moment and spin | Field-derived candidate current, moment, weak-field response, Pauli--Maxwell formal link | No stable charged spinorial branch; anomaly and physical calibration open |
| Electric force | Field-derived electric source, projected Gauss closure, Lorentz/energy/stress agreement | No stable charged pair or full-PDE center acceleration |
| Magnetic force | Field-derived magnetization current, static Ampere closure, magnetic force in the triangle | No stable spinorial pair, torque/precession, or calibrated moment/force map |

The current evidence authority and `physical_calibration_ledger_v2.py` preserve all three rows as partial. The historical selected PhysLib contract remains a compatibility subset, not sufficient authority for a new physical identity decision.

## Explicit retained boundaries

- self-consistent gauge/spinorial charged stationary equation;
- full coupled-PDE center acceleration;
- full coupled-PDE torque and spin precession;
- physical charge, magnetic-moment, length, time, and force calibration;
- concrete Maxwell Cauchy construction;
- concrete ADM constraint propagation;
- maximal globally hyperbolic coupled development;
- concrete global nonlinear coupled-action certificate;
- continuum hybridization and LDDL-current convergence;
- genuinely infinite-particle representation;
- continuum Lindblad generator and Fokker-Planck bridge;
- continuum coincident field-product regularization;
- interacting continuum scalar measure;
- arbitrary-order periodic-Schrödinger error estimates;
- out-of-sample physical predictions.

The sole criterion-level negative remains the predictive lepton-mass hierarchy. The next critical target is M9.97: construct a self-consistent gauge/spinorial stationary equation and measure acceleration, torque, and precession with the same field-derived sources.
