# M9 input, calibration, and prediction ledger

## Fixed formal inputs

| Input | Status |
| --- | --- |
| Pinned theorem contract | `entropic-physlib-linear-full@f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| Scalar reconstruction | `psi = sqrt(rho) exp(i Phi)` |
| Spinor density interface | `rho = Psi^dagger Psi` |
| Formal clock | `tau_ent = gamma D_KL(...)` |
| Imaginary action | `S_I = hbar tau_ent` |
| Weight modulus | `|W| = exp(-tau_ent)` |

## Fixed numerical model choices

| Choice | Value | Classification |
| --- | --- | --- |
| Free scalar control | `i psi_t = -1/2 psi_xx` | Certified control |
| Shared density map | Probability proportional to `rho Delta V` | Interface input |
| Scalar localization survey | `kappa in {0,+2,-2}` | M9.4 bounded choice |
| Accepted scalar branch | Focusing `g=2`, norm `N=1` | Selected model input |
| 1+1D spinor equation | Cubic Soler / massive Gross--Neveu form | M9.7a selected input |
| 1+1D representation | `alpha=-sigma_2`, `beta=sigma_3` | Convention |
| M9.7a parameters | `m=1`, `lambda=1`, `omega=0.8` | Frozen dimensionless inputs |
| M9.7b1 radial source | Exponential upper/lower spherical amplitudes | Frozen source ansatz |
| M9.7b1 electrostatic sector | `a=1`, `eta=1/2`, `epsilon0=1`, `q=+-1` | Gauge-sector inputs |
| M9.7b2 radial spinor | `exp(-i omega t)(v chi, i u sigma.rhat chi)^T` | 3D representation convention |
| M9.7b2 effective mass | `M=m-lambda(v^2-u^2)` | Selected Soler interaction |
| M9.7b2 parameters | `m=epsilon0=q=N=1`, `lambda=64` | Frozen dimensionless inputs |
| Charge continuation | `{0,1/4,1/2,3/4,1}` times final `q` | Numerical branch method |
| Radial boundary | Regular origin plus Coulomb/exponential tail at finite `R` | Boundary convention |
| Radial clock | Reflecting symmetric nearest-neighbor channel, 64 depths | Information input |

## M9.7b2 selection transparency

A non-scoring exploratory BVP continuation was used to locate the normalized
`lambda=64` branch and set the scored solver tolerances. The subsequent refinement,
window, residual, energy, and information checks were frozen around that branch.

Consequently:

- `lambda=64` is not a CAT/EPT derivation or prediction;
- the result is not blind preregistration;
- the positive stationary branch is evidence for the selected model only.

## Result classification

| Result | Evidential classification |
| --- | --- |
| Exact scalar and 1+1D spinor families | Selected-model identities |
| M9.7a convergence/conservation | Solver validation |
| M9.7b1 Gauss law, flux, and field energy | Electrostatic finite-volume validation |
| M9.7b2 nonzero normalized branch | Coupled stationary BVP result |
| `omega=0.9914633829<m` | Selected-model stationary eigenvalue |
| Near-fourth-order branch convergence | Collocation solver validation |
| Independent Dirac/Maxwell residual closure | Numerical equation check |
| Field/source energy agreement | Independent electrostatic ledger |
| Stationary eigenvalue identity | Independent matter/field ledger |
| `q=+1` versus `q=-1` | Dimensionless signed source sectors |
| 5% initial-guess return | Local BVP basin check, not dynamical stability |
| Radial KL contraction | Data-processing result for the reflecting channel |
| Magnitude `q=1` | Arbitrary dimensionless normalization, not measured charge |

## Open structural choices

| Choice | Status |
| --- | --- |
| Derivation of scalar or Soler interaction from CAT/EPT | Open |
| Time-dependent 3D spinor and gauge equations | Open M9.7b3 |
| Magnetic and transverse Maxwell sectors | Open M9.7b3 |
| Dynamical perturbation/orbital stability | Open M9.7b3 |
| Physical units for length, time, energy, mass, and charge | Open |
| Electron-charge normalization and Standard Model identity | Absent |
| Fermionic quantization and statistics | Open |
| Physical phase-clock interpretation | Open |
| Irreversible back-reaction from `S_I` | Open |

## Calibration targets

No experimental particle value has been used. Electron mass, electric charge,
magnetic moment, Compton frequency, and radius are neither inputs nor outputs.

A later physical unit map must state which measured quantity fixes each scale.
Reusing the same value as an output will count as calibration, not prediction.

## Current prediction status

There is still no particle-physics prediction. The strongest new conditional
statement is:

> Given the selected dimensionless spherical Soler--electrostatic equations,
> `m=epsilon0=q=N=1`, and `lambda=64`, a normalized localized stationary branch
> exists and passes the M9.7b2 residual, energy, Gauss, flux, convergence, window,
> signed-sector, and radial-clock gates.

This statement does not assign an electron, positron, or photon identity.

## Parameter-count audit

M9.7b2 removes the arbitrary frozen radial profile of M9.7b1 by solving the spinor
and potential together, but it adds a selected strong nonlinear coupling,
normalization, radial representation, continuation path, and boundary convention.
Physical interpretation still requires unit, charge, statistics, and clock maps.
The current freedom is not smaller than the number of particle observables that
could be claimed; M9 is not a zero-parameter particle model.
