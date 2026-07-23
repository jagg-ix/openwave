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
| Shared density map | cell/shell probability proportional to `rho Delta V` | Interface input |
| Scalar localization survey | `kappa in {0,+2,-2}` | M9.4 bounded choice |
| Accepted scalar branch | focusing `g=2`, norm `N=1` | Selected model input |
| 1+1D spinor equation | cubic Soler / massive Gross--Neveu form | M9.7a selected input |
| 1+1D representation | `alpha=-sigma_2`, `beta=sigma_3` | Convention |
| Spinor parameters | `m=1`, `lambda=1`, `omega=0.8` | Frozen dimensionless inputs |
| Background gauge parameter | `q=1` | M9.7a covariance-test input, not electric calibration |
| M9.7b1 radial amplitudes | `F=A exp(-r/a)`, `G=A eta(r/a)exp(-r/a)` | Frozen source ansatz |
| M9.7b1 radial parameters | `a=1`, `eta=1/2`, `epsilon0=1` | Dimensionless inputs |
| Signed electrostatic sectors | `q in {+1,-1}` | Frozen gauge-source labels |
| Radial Maxwell equation | spherical Gauss-law/Poisson constraint | M9.7b1 gauge-sector model |
| Radial boundaries | regular origin, `phi(infinity)=0`, analytic exterior Coulomb tail | Boundary convention |
| Radial clock channel | reflecting symmetric nearest-neighbor, 64 depths | M9.7b1 information input |

## Exact M9.7b1 reference identities

For arbitrary positive `a`, nonnegative `eta`, signed `q`, and positive
`epsilon0`:

```text
N_raw = pi a^3 (1 + 3 eta^2),
phi(0) = q(2 + 3 eta^2)/(8 pi epsilon0 a(1 + 3 eta^2)),
U_E = q^2/(8 pi epsilon0 a)
      * (837 eta^4 + 672 eta^2 + 160)
      / (256(1 + 3 eta^2)^2).
```

These are deductions for the selected radial ansatz. They are not independent
particle predictions.

## Result classification

| Result | Evidential classification |
| --- | --- |
| 1+1D exact Soler profile | Selected-model identity |
| M9.7a convergence/conservation | Solver validation |
| M9.7a finite perturbation survival | Stability evidence, not proof |
| M9.7a pure-gauge covariance | Background-connection interface |
| M9.7b1 shellwise Gauss law and boundary flux | Finite-volume gauge validation |
| M9.7b1 field/source energy agreement | Independent numerical ledger |
| `q=+1` versus `q=-1` field reversal | Dimensionless signed source result |
| M9.7b1 2% source modulation | Static source-response test, not dynamical stability |
| Radial KL contraction | Data-processing result for the reflecting channel |
| `q=1` magnitude | Arbitrary dimensionless normalization; not measured electric charge |

## Open structural choices

| Choice | Status |
| --- | --- |
| Derivation of scalar or Soler interaction from CAT/EPT | Open |
| Coupled 3D radial Dirac equations and representation conventions | Open M9.7b2 |
| Self-consistent spinor response to the electrostatic potential | Open M9.7b2 |
| Bounded frequency/coupling family for the coupled solve | Open; must be frozen before runs |
| Maxwell wave evolution and magnetic sector | Open M9.7b3 |
| Physical units for length, time, energy, mass, and charge | Open |
| Electron-charge normalization and Standard Model identity | Absent |
| 3D angular momentum and fermionic statistics | Open |
| Choice of physical phase-clock interpretation | Open |
| Irreversible back-reaction from `S_I` | Open |

## Calibration targets

No experimental particle value has been used. Electron mass, electric charge,
magnetic moment, Compton frequency, and radius are neither inputs nor outputs.

A later physical unit map must state which measured quantity fixes each scale.
Reusing the same value as an output will count as calibration, not prediction.

## Current prediction status

There is still no particle-physics prediction. The strongest completed statements
are conditional model results:

> Given the selected dimensionless Soler equation and frequency, the exact 1+1D
> spinor profile passes the M9.7a localization and interface gates.

> Given the selected regular spherical spinor-density ansatz, the electrostatic
> Maxwell constraint passes the M9.7b1 Gauss-law, flux, energy, signed-sector,
> convergence, window, perturbation-response, and radial-clock gates.

Neither statement assigns an electron, positron, or photon identity.

## Parameter-count audit

M9.7b1 adds a radial profile shape, lower-component ratio, length scale, gauge
normalization, electrostatic units, and boundary convention. The profile is not
solved from the coupled Dirac equation. Physical interpretation still requires
unit, charge, and clock maps. The current freedom is not smaller than the number
of physical observables that could be claimed; M9 is not a zero-parameter
particle model.
