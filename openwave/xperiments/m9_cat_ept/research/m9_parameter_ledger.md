# M9 input, calibration, and prediction ledger

## Fixed formal inputs

| Input | Status |
| --- | --- |
| Pinned theorem contract | `entropic-physlib-linear-full@f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| State reconstruction | `psi = sqrt(rho) exp(i Phi)` |
| Formal clock | `tau_ent = gamma D_KL(...)` |
| Imaginary action | `S_I = hbar tau_ent` |
| Weight modulus | `|W| = exp(-tau_ent)` |

## Fixed numerical model choices

| Choice | Value | Classification |
| --- | --- | --- |
| Free control | `i psi_t = -1/2 psi_xx` | Certified control |
| Probability map | `p_i proportional to dx |psi_i|^2` | M9.3 input |
| Coarse-graining channel | periodic `(1/4,1/2,1/4)` | M9.3 input |
| Localization survey | `kappa in {0,+2,-2}` | M9.4 bounded choice |
| Accepted branch | focusing `g=2`, norm `N=1` | Selected model input |
| Boundary approximation | wide periodic box, exponentially small tails | Numerical input |

## Exact M9.5 family identities

For arbitrary positive `g,N`:

```text
eta = gN/2,
omega_phase = eta^2/2,
E = -g^2 N^3/24,
R_rms = pi/(2 sqrt(3) eta).
```

These are deductions from the selected equation. They are not independent
particle predictions.

| Result | Evidential classification |
| --- | --- |
| `eta ~ N` | Exact scaling identity |
| `omega_phase ~ N^2` | Exact scaling identity |
| `|E| ~ N^3` | Exact scaling identity |
| `R_rms ~ N^-1` | Exact scaling identity |
| `omega_phase R_rms^2 = pi^2/24` | Exact scale invariant |
| `E/(mu N)=1/3` | Exact energy relation |
| Compton radius ratio `pi/sqrt(24)` | Conditional on clock and kinetic unit identifications |
| ZBW radius ratio `pi/sqrt(48)` | Conditional on a different clock identification |

## Open structural choices

| Choice | Status |
| --- | --- |
| Derivation of the focusing interaction from CAT/EPT | Open |
| Three-dimensional carrier and virial/Derrick balance | Open |
| Physical units for length, time, energy, and mass | Open |
| Choice between Compton, ZBW, or another phase-clock interpretation | Open |
| Signed gauge charge and Gauss-law observable | Absent |
| Spinor/double-cover representation | Absent |
| Irreversible back-reaction from `S_I` | Open |

## Calibration targets

No experimental particle value has been used. The electron mass, charge,
magnetic moment, and Compton frequency are neither inputs nor outputs.

A later physical unit map must state which one measured quantity fixes the scale.
Reusing that same value as an output will count as calibration, not prediction.

## Current prediction status

There is still no particle-physics prediction. The strongest result is
conditional:

> Given the selected dimensionless focusing cubic equation, its exact bright
> soliton family has the verified norm, energy, radius, and phase-frequency
> scaling recorded by M9.5.

## Parameter-count audit

The localization output depends on selecting a focusing interaction and its
coupling. The physical interpretation additionally requires a unit scale and
clock identification. Therefore the current information freedom is not smaller
than the number of physical observables claimed. M9 is not a zero-parameter
particle model.
