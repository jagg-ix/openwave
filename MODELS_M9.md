# OpenWave M9 CAT/EPT comparison profile

The executable source is `openwave/xperiments/m9_cat_ept/model_conformance.py`. Platform validation, formal theorem status, physical identity, calibration, and experimental validation are separate layers.

## Platform summary after M9.95

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

The repository-default particle has no physical name or calibration record. The neutral stationary branch is available. Nonzero winding may be declared, but it is not embedded into a stationary branch until a charged solution is actually constructed.

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

Operational/status graphs cover electrogravitic action closure, Lindblad-driven leads, Liouville second quantization, the Cauchy weak limit, and Lindblad trace preservation. Corpus graphs cover Rivers scalar Green functions and their continuum extension, Lovelock–Rund continuum variation, pointwise operators and invariant geometry, and Veliev periodic Schrödinger perturbation theory.

Lean remains proof authority. ZIL preserves components, sources, assumptions, claims, proof tokens, dependencies, pending/conditional/open states, rules, queries, constructive-QFT boundaries, and external analytic requirements.

The latest tree adds `EddingtonAffineFirstIntegral.lean`, including affine connection residual identities, Ricci/scalar first integrals, Einstein-Λ recovery, nonsingular-Λ consequences, torsion-vacuum contorsion elimination, and a Lovelock first-integral field-equation bridge.

**Boundary:** the Eddington result assumes the affine connection field equation and is algebraic on a finite index type. It does not supply the complete variational origin, maximal global Cauchy development, or calibrated CAT/EPT gravity.

## M9.94 — canonical spin and magnetic moment

The canonical three-dimensional particle envelope is embedded into a Pauli spinor. Spectral Pauli-current observables close normalization, `J_z = 1/2`, zero orbital control, periodic covariance, opposite-spin reversal, and the tree-level `g = 2` ratio. PhysLib supplies the Pauli tensor, spin-orbit/Foldy-Wouthuysen structure, and the structural Schwinger identity.

**Boundary:** the Schwinger anomaly is imported as formal structure, not derived from the CAT/EPT particle. A calibrated electron magnetic moment and physical electron identity remain open. The criterion remains partial.

## M9.95 — canonical electric and magnetic pair bridge

One periodic pair carries declared winding sectors `+3` and `-3`, giving exact dimensionless charges `+1` and `-1`. The same envelopes carry Pauli-current magnetic moments, and one shared dimensionless interaction ledger drives both force kernels.

The bridge closes electric and magnetic energy derivatives, signs, action-reaction, superposition, legacy inverse-square and dipole `r^-4` asymptotes, Yukawa screening, the exact zero-screening Coulomb endpoint, and the Lorentz-EM decomposition/covariance boundary.

**Boundary:** winding is declared rather than embedded in stationary branches; the regularized dipole law is not derived from the full CAT/EPT PDE; charge, magnetic-moment, and force units remain uncalibrated. Both force criteria remain partial.

## Explicit retained boundaries

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
- charged stationary CAT/EPT branches;
- physical calibration and out-of-sample predictions.

The sole criterion-level negative remains the predictive lepton-mass hierarchy. The next critical target is M9.96: construct a charged stationary branch with simultaneous winding, localization, and dynamical-stability closure.
