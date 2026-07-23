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
| Radial parameters | `m=epsilon0=q=N=1`, `lambda=64` | Dimensionless inputs |
| Spherical gauge dynamics | Poisson projection | Constrained model |
| M9.7c transverse geometry | Planar `A_y,E_y,B_z` | Bounded reduction |
| M9.7c coupling | `m=1`, `q=0.35` | Dimensionless inputs |
| M9.7c absorber | Edge conductivity | Boundary model |

## M9.9 selected inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Geometry | One transported coordinate with `A_x,E_x,A_y,E_y,B_z` | Bounded planar reduction |
| Matter | Opposite-charge spatial packets | Net-neutral transported pair |
| Parameters | `m=1`, `q=0.25`, width `2.5` | Dimensionless inputs |
| Centers and momenta | `-8,+8`; `+0.9,-0.9` | Frozen collision input |
| Spatial derivative | Periodic centered second order | Numerical method |
| Time integrator | RK4 with `dt=0.08 dx` | Numerical method |

M9.9 produces order `1.89918`, norm drift `6.02e-10`, corrected-energy drift
`1.073e-6`, final relative Gauss residual `0.02264`, and packet crossing. It is a
transport result, not a localized-particle result.

## M9.10 selected inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Geometry | Two transported coordinates with `A_x,A_y,E_x,E_y,B_z` | Bounded 2+1D reduction |
| Spinor Hamiltonian | `sigma_x(-i d_x-sqA_x)+sigma_y(-i d_y-sqA_y)+m sigma_z` | Selected Dirac coupling |
| Matter sector | Opposite-charge 2D Gaussian packets | Net-neutral pair |
| Mass and charge | `m=1`, `q=0.20` | Dimensionless inputs |
| Packet width | `2.2` | Frozen localization input |
| Packet centers | `(-5,-2)`, `(5,2)` | Frozen transport input |
| Packet momenta | `(0.95,0.35)`, `(-0.95,-0.2275)` | Frozen non-axis-aligned collision |
| Gauge seed | amplitude `0.006`, width `4` | Frozen magnetic perturbation |
| Spatial derivative | Periodic spectral differentiation | Numerical method |
| Time integrator | RK4 with `dt=0.055 min(dx,dy)` | Numerical method |
| Absorber | Conductivity plus evolved induced charge | Boundary/Gauss model |

## M9.10 scored studies

| Study | Frozen values |
| --- | --- |
| Refinement | square grids `{32,64,128}`, `t=2` |
| Long run | `96x96`, half-width `18`, `t=8` |
| Domain shapes | `72x60`, `72x72`, `72x84` at fixed spacing |
| Gauss gate | final absolute `<=2e-4`, relative `<=0.05` |
| Domain gate | separation spread `<=0.08`, emitted-energy spread `<=0.30` |

## M9.10 result classification

| Result | Evidential classification |
| --- | --- |
| Smooth-benchmark order `8.18686` | Spectral/RK4 solver validation for frozen case |
| Norm drift `5.73621e-9` | Finite-time norm conservation |
| Corrected-energy drift `6.53843e-9` | Matter/field/absorber balance |
| Final Gauss residual `1.719e-5` relative | 2D dynamic constraint result |
| Net charge `<=5.5163e-11` | Neutrality including absorber charge |
| Separation `10.77033 -> 1.03495` | Two-dimensional packet transport |
| Angle `0.38051 -> 1.34895` | Non-axis-aligned transport result |
| Emitted energy `1.12278e-5` | Bounded Poynting result |
| `q=0.20` | Arbitrary dimensionless coupling |

## Current conditional statement

> Given the selected 2+1D temporal-gauge equations, opposite-charge packets,
> dimensionless parameters, spectral/RK4 solver, gauge seed, conductivity absorber,
> and frozen studies, the packets transport non-axis-aligned while norm, corrected
> energy, net charge, Gauss, magnetic, emitted-energy, refinement, and domain-shape
> ledgers remain within their declared gates.

This does not establish a stable charged particle, physical calibration, fermionic
quantization, or Standard Model identity.

## Open structural choices

| Choice | Status |
| --- | --- |
| Two-dimensional localization/radiative stability | Open M9.11 |
| Full three-dimensional Maxwell--Dirac transport | Open |
| Physical units and charge calibration | Open |
| Fermionic quantization and statistics | Open |
| Derivation of selected interactions from CAT/EPT | Open |

## Parameter-count audit

M9.10 adds a second spatial coordinate, non-axis-aligned packet data, spectral
differentiation, an absorber-charge field, domain shapes, and time windows. It is
a selected multi-parameter field-model qualification, not a zero-parameter
particle prediction.
