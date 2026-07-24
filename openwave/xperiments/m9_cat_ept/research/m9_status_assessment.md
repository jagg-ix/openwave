# CAT/EPT status after M9.68

## OpenWave platform validation

| Status | Count |
| --- | ---: |
| Fully validated in-platform | 0 |
| Partial / bounded controls | 20 |
| Honest negative | 1 |
| Not yet addressed | 0 |
| Total explicit criteria | 21 |

The criterion-level negative remains the lepton-mass hierarchy. Particle stability remains partial: the original action disperses, the M9.63 coefficients retain a finite branch, M9.66 rejects one coefficient-selection premise as a current first-principles derivation, and M9.67 broadens bounded numerical evidence to anisotropic, phase, translation, noise, and scale perturbations. A stationary full-field branch, arbitrary-`H¹` theorem, and physical particle remain open.

## Formal interface changes

The current formal branch head is `e2c06741c3e49deb604082a2e9c2e918eab8d545`.

- The fixed-spatial-energy cubic sector is now packaged as a jointly continuous nonlinear semiflow.
- Positive damping gives strict norm contraction, convergence to zero, and a singleton zero global attractor.
- These results are exact on the compact continuous-field cubic carrier.
- They do not include the conservative spatial Laplacian plus quintic saturation, mass/energy conservation for that PDE, or orbital stability of a nonzero branch.

## Latest decisions

- **M9.66:** reduced Gaussian scale stationarity is action-derived; peak-density matching is not the normalized stationary field equation and is rejected as the current first-principles selection rule.
- **M9.67:** twelve adversarial finite-grid runs qualify stronger numerical orbital evidence, but the requested kernel `H¹` theorem remains open.
- **M9.68:** the frozen M9.65 Gaussian breathing prediction fails its 5% gate by 43%--49% in an independent higher-fidelity OpenWave comparison. No external experiment was performed.

## Prediction ledger

| Prediction state | Count |
| --- | ---: |
| Frozen/preregistered | 1 |
| Independently tested | 1 |
| Passed | 0 |
| Falsified | 1 |
| Externally tested | 0 |

## Current theory classification

CAT/EPT remains a substantial cross-repository formal-and-computational program and an incomplete physical theory. The failed Gaussian condition and breathing subprediction identify specific model/ansatz defects. They do not falsify every CAT/EPT mechanism, but they require replacement rather than parameter refitting.
