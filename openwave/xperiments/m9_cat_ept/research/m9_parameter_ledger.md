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
| Probability map | `p_i proportional to dx rho_i` | Shared M9.3 input |
| Coarse-graining channel | periodic `(1/4,1/2,1/4)` | M9.3 input |
| Scalar localization survey | `kappa in {0,+2,-2}` | M9.4 bounded choice |
| Accepted scalar branch | focusing `g=2`, norm `N=1` | Selected model input |
| Spinor equation | cubic 1+1D Soler / massive Gross-Neveu form | M9.7a selected model input |
| Dirac representation | `alpha=-sigma_2`, `beta=sigma_3` | Convention |
| Spinor parameters | `m=1`, `lambda=1`, `omega=0.8` | Frozen dimensionless inputs |
| Gauge-interface parameter | `q=1` | Dimensionless covariance-test input, not electric calibration |
| Spinor boundary approximation | wide periodic box, exponentially small tails | Numerical input |

## Exact scalar-family identities

For arbitrary positive scalar `g,N`:

```text
eta = gN/2,
omega_phase = eta^2/2,
E = -g^2 N^3/24,
R_rms = pi/(2 sqrt(3) eta).
```

These are deductions from the selected scalar equation, not independent physical
predictions.

## M9.7a spinor result classification

| Result | Evidential classification |
| --- | --- |
| Exact Soler profile at `m=1,lambda=1,omega=0.8` | Selected-model identity |
| Approximately second-order numerical return | Solver validation |
| Norm and model-energy conservation | Numerical conservation result |
| Fixed finite-time perturbation survival | Stability evidence, not a proof |
| Free-Dirac control dispersal | Discriminating numerical control |
| Pure-gauge covariance | Background-connection interface check |
| `rho=Psi^dagger Psi` clock compatibility | Interface preservation |
| `q=1` | Arbitrary dimensionless normalization; not measured electric charge |

## Open structural choices

| Choice | Status |
| --- | --- |
| Derivation of scalar or Soler interaction from CAT/EPT | Open |
| Three-dimensional spinor carrier and localization mechanism | Open |
| Dynamical Maxwell/gauge action and self-field | Open |
| Physical units for length, time, energy, and mass | Open |
| Electric charge normalization and sign sectors | Open |
| 3D spin observable and fermionic statistics | Open |
| Choice of physical phase-clock interpretation | Open |
| Irreversible back-reaction from `S_I` | Open |

## Calibration targets

No experimental particle value has been used. The electron mass, electric charge,
magnetic moment, Compton frequency, and radius are neither inputs nor outputs.

A later physical unit map must state which measured quantity fixes each scale.
Reusing the same value as an output will count as calibration, not prediction.

## Current prediction status

There is still no particle-physics prediction. The strongest completed statements
are conditional model results:

> Given the selected dimensionless scalar equation, its exact bright-soliton
> family has the verified M9.5 scaling.

> Given the selected dimensionless Soler equation and frozen frequency, the exact
> two-component 1+1D profile passes the M9.7a localization, convergence,
> perturbation, background-gauge, and density-clock gates.

Neither statement assigns a Standard Model identity.

## Parameter-count audit

The scalar output depends on selecting a focusing interaction and coupling. The
spinor output additionally fixes a nonlinear Dirac interaction, mass parameter,
frequency, representation convention, and gauge-interface normalization. Physical
interpretation still requires unit, charge, and clock maps. The current freedom is
not smaller than the number of physical observables that could be claimed. M9 is
not a zero-parameter particle model.
