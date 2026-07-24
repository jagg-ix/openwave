# CAT/EPT status after M9.71

## OpenWave platform validation

| Status | Count |
| --- | ---: |
| Fully validated in-platform | 0 |
| Partial / bounded controls | 20 |
| Honest negative | 1 |
| Not yet addressed | 0 |
| Total explicit criteria | 21 |

The sole criterion-level negative remains the lepton-mass hierarchy. Particle stability is stronger but still partial: M9.69 constructs a localized stationary non-Gaussian solution of the full normalized cubic--quintic equation, and M9.70 formalizes exact density coercivity plus a conditional orbital theorem. The conservative spatial `H¹` flow, its invariants, compactness modulo symmetries, nonzero-branch coercivity, and physical-particle identification remain open.

## Formal interface changes

The M9.70 formal branch head is `51aad63b2541a1377a001df71b85dfe35f26c0af`.

- The cubic--quintic density slack has an exact kernel-proved square factorization.
- Positive `beta` and nonnegative density give the exact lower bound `V(rho) >= -(3 alpha²/(16 beta)) rho`.
- `H1OrbitalCertificate.uniform_orbital_stability` derives uniform orbital control from explicit flow, conservation, compactness, and coercivity fields.
- The theorem is conditional by construction; it does not silently assume the spatial PDE flow has been built.

## Latest decisions

- **M9.69:** one non-Gaussian stationary branch is qualified across three unrelated seeds and three grids. It remains conditional on the M9.63 coefficient pair.
- **M9.70:** the scoped kernel target closes. The end-to-end analytic target does not: PDE flow construction and concentration compactness remain certificate obligations.
- **M9.71:** the frozen replacement ratio `1.074356835825` passes internal held-out grids by margins of `2.34%` and `4.18%`. It has not been externally tested.

## Prediction ledger

| Prediction state | Count |
| --- | ---: |
| Frozen/preregistered records | 2 |
| Internally tested | 2 |
| Internally passed | 1 |
| Internally falsified | 1 |
| Externally tested | 0 |
| Physically validated | 0 |

## Current theory classification

CAT/EPT remains a substantial cross-repository formal-and-computational program and an incomplete physical theory. M9.69 removes dependence on a Gaussian stationary ansatz, M9.70 exposes the exact analytic premises needed for orbital stability, and M9.71 supplies a replacement internally reproducible mode. None of these closes experimental calibration or identifies the branch with an observed particle.
