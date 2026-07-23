# M9 input, calibration, and prediction ledger

## Fixed formal inputs

| Input | Status |
| --- | --- |
| Pinned theorem contract | Fixed at `entropic-physlib-linear-full@f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| State reconstruction | `psi = sqrt(rho) exp(i Phi)` |
| Formal clock | `tau_ent = gamma D_KL(p_XY || p_X p_Y)` |
| Imaginary action relation | `S_I = hbar tau_ent` |
| Weight modulus | `|W| = exp(-tau_ent)` |
| Quantum coupling identity | `lambda_Q = hbar^2 / 8` |

## Fixed numerical choices through M9.4

These are declared model inputs, not predictions.

| Choice | Frozen value | Status |
| --- | --- | --- |
| Free control | `i psi_t = -1/2 psi_xx` | Numerically certified |
| Field-to-probability map | `p_i proportional to dx |psi_i|^2` | Fixed by M9.3 |
| Coarse-graining channel | periodic weights `(1/4, 1/2, 1/4)` | Fixed by M9.3 |
| Channel depth and calibration | 64 steps, `gamma = 1` | Dimensionless input |
| Nonlinear survey family | `kappa in {0, +2, -2}` | Fixed by M9.4 |
| Common localization seed | normalized `sech(x)` | Same for all family members |
| Candidate branch | focusing cubic `kappa = -2` | Structural choice, not derived |
| Numerical particle boundary | wide periodic box with exponentially small tails | Approximation to zero-field infinity |

## Results and their evidential weight

| Result | Correct classification |
| --- | --- |
| KL contraction under the declared channel | Data-processing result conditional on the selected channel |
| Accumulated discarded information grows with channel depth | Operational coarse-graining clock, not physical-time monotonicity |
| `kappa = -2` supports a stable bright soliton | Mathematical result for the selected focusing cubic equation |
| Free and defocusing controls disperse | Discriminating numerical control within the bounded family |
| Soliton phase frequency `1/2` | Exact property of the dimensionless selected equation, not a measured particle frequency |

## Open structural choices

| Choice | Current status |
| --- | --- |
| Derivation of the focusing functional from CAT/EPT | Open; currently an explicit model input |
| Three-dimensional carrier and Derrick escape | Open |
| Physical unit map for length, time, energy, and mass | Open |
| Particle identity rule | Open |
| Charge or gauge symmetry | Absent |
| Spinor or double-cover structure | Absent |
| Irreversible back-reaction from `S_I` | Open |
| Alternate coarse-graining channels | Uniqueness not claimed |

## Calibration targets

No experimental particle value has been used. The electron mass, Compton
frequency, charge, and magnetic moment are not calibration inputs and are not
outputs of M9.1--M9.4.

## Predictions

There is no current particle-physics prediction. The accepted statement is
conditional:

> Given the chosen dimensionless focusing cubic equation at `kappa = -2`, the
> normalized bright soliton exists and survives the declared numerical gates.

This statement can validate the numerical particle-search infrastructure. It
does not predict that Nature selects the equation or its coefficient.

## Parameter-count audit

For the headline localization output, at least one decisive structural choice
is present: selecting a focusing rather than free or defocusing nonlinearity,
including its coefficient. Therefore `N_free >= N_obs` for a one-output
localization claim. M9.4 is not advertised as a zero-parameter prediction.

M9.5 must keep the dimensionless scaling family separate from any later physical
calibration. A formal identity or a unit definition cannot be counted as an
independent particle prediction.
