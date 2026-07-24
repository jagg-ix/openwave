# CAT/EPT status after M9.74

## OpenWave platform validation

| Status | Count |
| --- | ---: |
| Fully validated in-platform | 0 |
| Partial / bounded controls | 20 |
| Honest negative | 1 |
| Not yet addressed | 0 |
| Total explicit criteria | 21 |

The sole criterion-level negative remains the lepton-mass hierarchy. Particle stability is stronger but still partial. M9.69 constructs a localized stationary non-Gaussian solution of the full normalized cubic--quintic equation. The deep PhysLib audit shows that the branch already has complete-continuum `H¹(ℝ³)` weak compactness with norm-bound retention, weak-plus-norm strong closure, Prokhorov compactness consequences for tight Born measures, a direct-method engine, local existence/uniqueness for every `C¹` H¹ generator, negative-level exclusion of vanishing, positive-binding-gap exclusion of dichotomy, and a Cazenave--Lions orbital-stability mechanism from compact energy sublevels. PR #16 adds predicate-carrier compactness bridges, constrained attainment, and concentration-branch composition.

## Formal interface changes

The live PhysLib base is `496b275336f30c0f934fe4ddcfa9fbfd99fa567c`; PR #16 has head `9a15bf5023980f6bc401671de7dc7dca164a52d0`.

- Sobolev-bounded sequences admit weakly convergent subsequences whose limits retain the same closed-ball bound.
- Weak convergence plus convergence of the exact H¹ norm gives strong H¹ convergence.
- Tight probability sequences have distributionally convergent subsequences, and H¹ boundedness plus tightness gives one common field/density subsequence.
- Local existence and uniqueness are proved for every `C¹` vector field on the complete H¹ carrier.
- Negative level excludes vanishing; strict subadditivity and positive binding gap exclude dichotomy.
- PR #16 adds constrained attainment and proves that an explicit trichotomy leaves compactness modulo translations.
- Compact-sublevel Cazenave--Lions orbital stability is already proved once the target compact sublevel and conserved flow are supplied.

This corrects the earlier shallow boundary: generic H¹ compactness, local H¹ ODE theory, Prokhorov compactness consequences, and the orbital-stability mechanism are not missing.

## Latest decisions

- **M9.72:** scoped H¹ closure is complete. The concrete target generator's H¹ mapping/`C¹` property and global conserved flow remain open.
- **M9.73:** vanishing and dichotomy are formally eliminated; joint field/density compactness follows once recentered tightness is supplied. Target tightness/trichotomy, mass/norm closure, branch identification, and compact low-energy sublevels remain open.
- **M9.74:** the frozen M9.71 ratio `1.074356835825` survives a radial-amplitude perturbation and Hann-windowed periodogram. Three-grid relative discrepancies are `2.61%`, `0.21%`, and `1.60%`, all inside the immutable 5% gate. No external experiment was performed.

## Prediction ledger

| Prediction state | Count |
| --- | ---: |
| Frozen/preregistered records | 2 |
| Internally tested | 2 |
| Internally passed | 1 |
| Internally falsified | 1 |
| Passed by an independent perturbation/estimator | 1 |
| Externally tested | 0 |
| Physically validated | 0 |

## Current theory classification

CAT/EPT remains a substantial cross-repository formal-and-computational program and an incomplete physical theory. The deeper audit narrows the unresolved work to concrete target-generator regularity, closure/lower-semicontinuity, derivation of tightness, global conserved evolution, and compact-sublevel branch identification. Internal numerical robustness of the replacement mode does not establish an observed particle, experimental calibration, or physical validation.
