# M9 input, calibration, and prediction ledger

## Fixed formal inputs

| Input | Status |
| --- | --- |
| Pinned theorem contract | Fixed at commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| State reconstruction | `psi = sqrt(rho) exp(i Phi)` |
| Clock definition | `tau_ent = gamma D_KL(p_XY || p_X p_Y)` |
| Imaginary action relation | `S_I = hbar tau_ent` |
| Weight modulus | `|W| = exp(-tau_ent)` |
| Quantum coupling identity | `lambda_Q = hbar^2 / 8` |

## Open structural choices

Every row below counts as freedom until independently fixed before a target value
is inspected.

| Choice | Current status |
| --- | --- |
| Real-action/Hamiltonian functional | Open |
| Nonlinear localization family | Open; must be preregistered |
| Vacuum and boundary condition | Open |
| `p_XY` extraction and `X | Y` partition | Open |
| Entropic calibration `gamma` | Dimensionless input; not yet fixed |
| Unit map for length, time, energy and mass | Open |
| Particle identity rule | Open |
| Search ranges and stopping budget | Open |

## Calibration targets

None are accepted at scaffold stage. In particular, the electron mass and its
Compton/Zitterbewegung frequencies must not be used to choose the localization
functional and then reported as predictions.

## Predictions

None at scaffold stage. The first admissible prediction must be fixed by the
preregistered structure and compared only after the structure and search budget
are frozen.

## Parameter-count rule

For every claimed output, M9 will record `N_obs`, every inequivalent structural
choice in `N_free`, and whether the choice was fixed independently of the output.
A formal identity is not counted as a new physical prediction.
