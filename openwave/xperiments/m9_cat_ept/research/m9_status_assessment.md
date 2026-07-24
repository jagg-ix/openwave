# CAT/EPT status after M9.74

## OpenWave platform validation

| Status | Count |
| --- | ---: |
| Fully validated in-platform | 0 |
| Partial / bounded controls | 20 |
| Honest negative | 1 |
| Not yet addressed | 0 |
| Total explicit criteria | 21 |

The sole criterion-level negative remains the lepton-mass hierarchy. Particle stability is stronger but still partial. M9.69 constructs a localized stationary non-Gaussian solution of the full normalized cubic--quintic equation. The deep PhysLib audit shows that complete-continuum `H¹(ℝ³)` weak compactness, a direct-method engine, negative-level exclusion of vanishing, and positive-binding-gap exclusion of dichotomy already exist. PR #16 adds constrained attainment and composes the concentration branches. The remaining analytic gaps are normalized-mass weak closure, weak lower semicontinuity of the promoted target energy, translation tightness, construction of the conservative spatial flow and its invariants, and nonzero-branch coercivity modulo symmetries.

## Formal interface changes

The live PhysLib base is `0a04328a01b7911078c4f9d01cc0c8c963519dc2`; updated PR #16 has head `5d0cdf07c891b1dbe7381b93c2d794b593fae09d`.

- `EuclideanHOneThree` is a complete continuum `H¹(ℝ³)` Bessel-energy carrier, not a finite-mode surrogate.
- Every Sobolev-bounded sequence has an `H¹`-weakly convergent subsequence.
- The existing complete-carrier direct method attains a level from boundedness and sequential weak lower semicontinuity.
- PR #16 adds sequential weak closure of constraints to derive constrained attainment.
- `normalizedCoreGroundEnergy_neg` excludes concentration--compactness vanishing.
- strict subadditivity and `compactCoreBindingGap_pos` exclude dichotomy.
- PR #16 proves that an explicit trichotomy therefore leaves compactness modulo translations.
- Exact cubic--quintic density coercivity and conditional uniform orbital control remain included.

This corrects the earlier shallow boundary: generic H¹ compactness and the direct-method engine are not missing.

## Latest decisions

- **M9.72:** scoped constrained direct-method closure is complete on the live continuum carrier. Mass-constraint weak closure and target-energy weak lower semicontinuity remain to be instantiated.
- **M9.73:** vanishing and dichotomy are formally eliminated using current branch results. Derivation of the concentration trichotomy and translation tightness remains open.
- **M9.74:** the frozen M9.71 ratio `1.074356835825` survives a different radial-amplitude perturbation and a Hann-windowed periodogram. Three-grid relative discrepancies are `2.61%`, `0.21%`, and `1.60%`, all inside the immutable 5% gate. No external experiment was performed.

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

CAT/EPT remains a substantial cross-repository formal-and-computational program and an incomplete physical theory. The deeper audit substantially improves the mathematical status of the variational program, while narrowing the unresolved work to specific analytic interfaces. Internal numerical robustness of the replacement mode does not establish an observed particle, experimental calibration, or physical validation.
