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

These identities do not select the later scalar, spinor, gauge, transport, or
nonlinear-coupling models.

## Accumulated selected inputs

| Stage | Selected inputs | Classification |
| --- | --- | --- |
| Scalar | Focusing cubic family | Bounded model choice |
| 1+1D spinor | Cubic Soler equation | Selected carrier |
| Spherical branch | `m=epsilon0=q=N=1`, `lambda=64` | Dimensionless inputs |
| M9.7c transverse | `m=1`, `q=0.35`, local opposite-charge pair | Bounded reduction |
| M9.9 transport | `m=1`, `q=0.25`, centers `-8,+8`, momenta `+0.9,-0.9` | Frozen 1D collision |
| M9.10 transport | `m=1`, `q=0.20`, width `2.2` | Frozen 2D transport |
| M9.10 centers | `(-5,-2)`, `(5,2)` | Frozen non-axis-aligned collision |
| M9.10 momenta | `(0.95,0.35)`, `(-0.95,-0.2275)` | Frozen transport input |
| M9.10 gauge seed | amplitude `0.006`, width `4` | Frozen magnetic perturbation |
| M9.10 numerics | spectral derivatives, RK4, conductivity absorber | Numerical/boundary choice |

## M9.11 selected inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Nonlinear family | `lambda in {0,2,4,8}` | Bounded survey |
| Effective mass | `M_s=m-lambda psi_s^dagger sigma_z psi_s` | Selected Soler interaction |
| Survey grid | `48x48`, `t=8` | Scored finite-time gate |
| Strongest member | `lambda=8` | Selected by minimum RMS spreading |
| Perturbation width | factor `1.05` | Frozen perturbation |
| Perturbation y momentum | factor `1.05` | Frozen perturbation |
| Perturbation gauge seed | factor `1.10` | Frozen perturbation |
| Perturbation grid | `64x64`, `t=8` | Scored robustness gate |
| Long-time grid | `64x64`, `t=12` | Scored rejection gate |

The survey family and thresholds were frozen for the scored decision. `lambda=8`
is not a CAT/EPT derivation or a measured coupling.

## M9.11 result classification

| Result | Evidential classification |
| --- | --- |
| Spreading improvement `0.12690276` | Finite-time nonlinear-family result |
| `lambda=8` RMS ratio `1.40072364` at `t=8` | Reduced-spreading candidate |
| Perturbed RMS ratio `1.34175227` | Finite-time perturbation survival |
| Long-time RMS ratio `1.73615505` | Long-horizon dispersal/rejection result |
| Long-time peak ratio `0.67364906` | Particle-gate rejection evidence |
| Maximum norm drift `1.835e-7` | Coarse-survey conservation result |
| Maximum energy drift `2.091e-7` | Coarse-survey energy result |
| Maximum final Gauss residual `0.003406` | Coarse-survey constraint result |
| `accepted_particle_candidate=false` | Explicit negative model decision |

## Current conditional statement

> Given the selected 2+1D Maxwell--Dirac reduction, bounded
> `lambda={0,2,4,8}` survey, fixed perturbation, numerical scheme, and time windows,
> `lambda=8` reduces spreading and survives through `t=8`, but disperses beyond the
> frozen particle gate at `t=12`. No stable two-dimensional particle candidate is
> accepted.

## Open structural choices

| Choice | Status |
| --- | --- |
| Three-dimensional transported Maxwell--Dirac program | Open M9.12 |
| Stable localized charged solution | Not established |
| Physical units and charge calibration | Open |
| Fermionic quantization and statistics | Open |
| Derivation of selected interactions from CAT/EPT | Open |
| Irreversible back-reaction from `S_I` | Open |

## Parameter-count audit

M9.11 adds a four-member coupling family, localization metrics, perturbation
factors, two resolutions, and two time horizons. It is a selected decision study,
not a zero-parameter particle prediction.
