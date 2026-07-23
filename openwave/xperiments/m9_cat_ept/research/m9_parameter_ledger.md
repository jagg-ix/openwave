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

## Selected radial and transverse inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Scalar localization | Focusing cubic family | Bounded model choice |
| 1+1D spinor | Cubic Soler equation | Selected model |
| Radial spinor | `(v chi, i u sigma.rhat chi)^T` | Representation convention |
| Radial parameters | `m=epsilon0=q=N=1`, `lambda=64` | Dimensionless inputs |
| Spherical gauge dynamics | Poisson projection | Constrained model |
| Transverse geometry | Planar `A_y,E_y,B_z` | Bounded reduction |
| M9.7c charge pair | Opposite-charge local spinors | Neutral current model |
| M9.7c coupling | `m=1`, `q=0.35` | Dimensionless inputs |
| M9.7c gauge seed | amplitude `0.01`, width `4` | Frozen perturbation |
| M9.7c absorber | Edge conductivity | Boundary model |

## M9.9 selected inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Geometry | One transported coordinate with `A_x,E_x,A_y,E_y,B_z` | Bounded planar reduction |
| Spinor equation | `sigma_x(-i d_x-sqA_x)+m sigma_z-sqA_y sigma_y` | Selected Dirac coupling |
| Matter sector | Opposite-charge spatial packets | Net-neutral transported pair |
| Mass | `m=1` | Dimensionless input |
| Charge magnitude | `q=0.25` | Dimensionless input, not measured charge |
| Packet width | `2.5` | Frozen localization input |
| Initial centers | `-8,+8` | Frozen transport input |
| Initial momenta | `+0.9,-0.9` | Frozen collision input |
| Transverse seed | amplitude `0.008`, width `4` | Frozen gauge input |
| Longitudinal initial field | Inverse centered-derivative symbol | Discrete Gauss construction |
| Spatial derivative | Periodic centered second order | Numerical method |
| Time integrator | RK4 with `dt=0.08 dx` | Numerical method |
| Transverse absorber | Edge conductivity | Boundary model |

## Scored M9.9 studies

| Study | Frozen values |
| --- | --- |
| Refinement | `L=40`, `t=6`, points `{128,256,512}` |
| Transported interaction | `L=40`, 512 points, `t=14` |
| Total matter norm | `1`, split equally between species |
| Gauss gate | Final absolute `<=4e-4`, relative `<=0.05` |
| Transport gate | Final separation below 75% of initial separation |

## Result classification

| Result | Evidential classification |
| --- | --- |
| Transported-spinor order `1.89918` | Spatial spinor solver validation |
| Norm drift `6.02e-10` | Finite-time norm conservation |
| Corrected-energy drift `1.073e-6` | Matter/field/absorber balance |
| Final Gauss residual `0.02264` relative | Dynamic longitudinal-constraint result |
| Net charge `<=1.04e-16` | Neutral-pair conservation result |
| Packet separation `16 -> -2.21328` | Spatial transport and crossing result |
| Emitted energy `2.84143e-5` | Bounded Poynting-flux result |
| `q=0.25` | Arbitrary dimensionless coupling |

## Current conditional statement

> Given the selected opposite-charge packets, one-dimensional Dirac transport,
> longitudinal and transverse gauge equations, dimensionless inputs, centered
> finite differences, RK4 evolution, and frozen time window, the packets propagate
> and cross while norm, corrected energy, net charge, final Gauss residual,
> transverse back-reaction, and emitted-energy ledgers remain within their gates.

This is not a stable localized-particle result and does not assign an electron,
positron, photon, or Standard Model identity.

## Open structural choices

| Choice | Status |
| --- | --- |
| Full two-dimensional Maxwell--Dirac transport | Open M9.10 |
| Stable localized charged solution | Open |
| Physical units and charge calibration | Open |
| Fermionic quantization and statistics | Open |
| Derivation of selected interactions from CAT/EPT | Open |
| Irreversible back-reaction from `S_I` | Open |

## Parameter-count audit

M9.9 adds packet centers, momenta, width, charge magnitude, gauge seeds, temporal
window, finite-difference scheme, and absorber choices. It is a selected
multi-parameter field-model qualification, not a zero-parameter particle prediction.
