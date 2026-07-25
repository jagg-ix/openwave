# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 OpenWave comparison criteria and combines a stationary non-Gaussian branch, theorem-guided finite-grid dynamics, explicit claim boundaries, a reusable uncalibrated particle-model API, and a branch-wide imported inventory of the CAT/EPT Lean/ZIL formalization corpus.

## Platform status after M9.95

- Seven criteria are validated in-platform.
- Thirteen criteria remain partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- The reusable particle kernel wraps coefficient selection, stationary branch construction, exact subflows, perturbations, periodic-covariant observables, serialization fingerprints, and a fail-closed physical-identity gate.
- The formalization importer pins `entropic-physlib-linear-full` by exact tree `239a663a3192a3144fb998e7bb200e09689a3bb9`, current `Physlib.lean` blob `182a06e0f50314ec54436da602b4ac86eba4ee08`, 11 ZIL graphs, 422 graph entities, 12 open/external boundaries, and 24 Lean sources.
- The latest tree includes `EddingtonAffineFirstIntegral.lean`, adding affine connection residual, first-integral Einstein-Λ recovery, torsion-vacuum, and Lovelock field-equation bridges.
- M9.94 binds the canonical three-dimensional particle envelope to Pauli spin/current and closes the tree-level `g=2` relation.
- M9.95 binds one canonical declared-winding particle pair to electric and magnetic kernels under one shared dimensionless ledger.

Validated criteria:

1. charge quantization;
2. particle stability / Derrick escape;
3. spin-1/2 statistics;
4. source-free Maxwell waves;
5. free massive Klein-Gordon evolution;
6. dimensionless Coulomb orbital quantization;
7. the explicit dimensionless thermal field.

## Canonical implementation surfaces

| Surface | Path | Role |
| --- | --- | --- |
| 21-criterion profile | `model_conformance.py` and `MODELS_M9.md` | executable comparison status |
| Model registration | `model_registration.py` | canonical M9 component, formal revision, and imported-surface map |
| Particle kernel | `particle_model.py` | reusable state construction, perturbation, flow, periodic observables, and identity gate |
| Selected PhysLib contract | `formal/physlib_contract.v2.json` and `physlib_contract.py` | historical selected theorem contract and drift validation |
| Operational ZIL inventory | `formalization_inventory.py` and `formalization_inventory_additional.py` | electrogravity and open-systems graphs |
| Corpus ZIL inventory | `formalization_inventory_corpus.py` | Rivers, Lovelock–Rund, Veliev, latest tree/source data, and Eddington gravity imports |
| Import validator | `formalization_import.py` | 11-graph declaration coverage, exact tree/blob checks, status preservation, and adapter resolution |
| Canonical spin bridge | `canonical_spin_magnetic_bridge.py` | Pauli embedding, current, moment, angular momentum, tree `g=2` |
| Canonical force bridge | `canonical_force_formal_bridge.py` | declared winding pair, shared electric/magnetic ledger, formal potential/superoperator boundary |

## Imported ZIL corpus

Operational/status graphs:

1. electrogravitic action closure;
2. Lindblad-driven leads;
3. Liouville second quantization;
4. Cauchy weak limit;
5. Lindblad trace preservation.

Merged formalization-family graphs:

6. Rivers scalar Green functions;
7. Rivers scalar Green functions — continuum extension;
8. Lovelock–Rund continuum variational structure;
9. Lovelock–Rund pointwise operators;
10. Lovelock–Rund invariant geometry;
11. Veliev periodic Schrödinger perturbation theory.

Lean declarations remain proof authority. ZIL records components, claims, assumptions, sources, proof tokens, dependencies, status vocabulary, rules, queries, and explicit boundaries. OpenWave does not reinterpret pending, conditional, open, constructive-QFT, or external-analytic items as proved.

## Particle, force, and gravity boundaries

The neutral stationary branch is available. Nonzero winding may be declared, but a charged stationary branch is not claimed until winding is embedded into the same solved state and passes localization and dynamical-stability gates.

The M9.94 Pauli embedding closes spin `1/2` and the tree-level `g=2` ratio. It does not derive the Schwinger anomaly from the CAT/EPT particle. The M9.95 pair closes dimensionless electric and magnetic force ledgers, but the two nonzero winding sectors are declared rather than dynamically embedded, and no physical force-unit calibration is inherited.

The Eddington affine first integral derives an Einstein equation with cosmological constant algebraically after assuming the affine connection field equation. It does not supply a full variational derivation, global nonlinear Cauchy development, or calibrated CAT/EPT gravity.

A physical assignment still requires one certificate covering localization, normalization, embedded winding, calibration, rest energy, clock identity, spin/exchange, magnetic moment, far-field force, and an out-of-sample prediction.

## Boundary

The M9 stack establishes a reproducible mathematical particle kernel, a branch-wide imported formalization inventory, and seven criterion-scoped OpenWave validations. It does not establish an observed-particle identity, charged stationary particles, calibrated physical units, a CAT/EPT derivation of the anomalous magnetic moment, global calibrated gravity, or external experimental agreement.

## Next critical targets

1. M9.96: construct a charged stationary branch whose field-derived winding, localization, and dynamical stability close simultaneously.
2. M9.97: use that charged branch in full-PDE annihilation and composite-sector campaigns.
3. M9.98: register independent calibration and out-of-sample physical prediction gates.
