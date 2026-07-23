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

## Selected model inputs through M9.7b3

| Choice | Value | Classification |
| --- | --- | --- |
| Scalar localization survey | `kappa in {0,+2,-2}` | Bounded scalar choice |
| 1+1D spinor equation | Cubic Soler form | Selected model |
| 3D radial spinor | `(v chi, i u sigma.rhat chi)^T` | Representation convention |
| Radial effective mass | `M=m-lambda(v^2-u^2)` | Selected Soler interaction |
| Radial parameters | `m=epsilon0=q=N=1`, `lambda=64` | Dimensionless inputs |
| Spherical gauge evolution | Poisson projection after local substeps | Constrained model |
| Radial perturbation | 2% opposite amplitude and phase | Frozen dynamic input |

## M9.7c selected inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Gauge geometry | Planar `A_y(x,t), E_y(x,t), B_z(x,t)` | Bounded transverse reduction |
| Maxwell equation | `A_t=-E`, `E_t=-A_xx-J-sigma E` | Hyperbolic gauge model |
| Matter sector | Opposite-charge local two-spinor pair | Neutral current model |
| Matter Hamiltonian | `H_s=m sigma_z-s q A sigma_y` | Selected local Dirac coupling |
| Mass | `m=1` | Dimensionless input |
| Charge magnitude | `q=0.35` | Dimensionless input |
| Polarization angle | `0.45` | Frozen spinor perturbation |
| Matter envelope width | `2.5` | Frozen localization input |
| Total matter norm | `1` | Normalization input |
| Gauge seed | amplitude `0.01`, width `4` | Frozen gauge perturbation |
| Time integrator | RK4 | Numerical method |
| Spatial operator | Periodic second-order finite difference | Numerical method |
| Absorber | Edge conductivity `sigma(x)` | Boundary model |

## M9.7c scored studies

| Study | Frozen values |
| --- | --- |
| Vacuum refinement | `L=60`, `t=12`, points `{256,512,1024}`, `dt=0.2 dx` |
| Coupled refinement | `L=60`, `t=18`, points `{256,512,1024}`, `dt=0.18 dx` |
| Long run | `L=60`, 1024 points, `t=80` |
| Absorber study | `L={50,60,70}`, `t=75`, fixed spacing |
| Probe radius | `20` |

## Selection transparency

Exploratory runs were used to correct the `sigma_y` sign convention and to select
absorber durations and the central-field fraction threshold. The committed task
file records the final equations, inputs, studies, and gates. M9.7c is therefore
not described as blind preregistration.

## Result classification

| Result | Evidential classification |
| --- | --- |
| Vacuum orders near `2` | Transverse wave-solver validation |
| Coupled orders `1.98383`, `1.95569` | Coupled solver convergence |
| Zero signed charge without projection | Exact neutral-pair symmetry result |
| Corrected-energy drift `5.14e-7` | Finite-time conservation result |
| Nonzero emitted energy | Poynting/radiation result for bounded reduction |
| Long-run absorbed energy `4.90e-4` | Conductivity-boundary accounting result |
| Absorber spread `0.0042613` | Window/absorber robustness result |
| `q=0.35` | Arbitrary dimensionless coupling, not measured charge |

## Current conditional statement

> Given the selected neutral local spinor pair, planar transverse Maxwell reduction,
> dimensionless parameters, finite-difference/RK4 solver, gauge seed, absorber, and
> time windows, the model supports nonzero transverse Poynting emission, preserves
> zero signed charge without Gauss projection, closes matter/field/absorber energy,
> and converges under resolution and absorber-window studies.

This statement does not assign an electron, positron, photon, or Standard Model
identity.

## Open structural choices

| Choice | Status |
| --- | --- |
| Full spatial Maxwell--Dirac transport | Open future extension |
| Charged localized non-spherical solution | Open |
| Non-spherical orbital stability | Open |
| Physical units and charge calibration | Open |
| Fermionic quantization and statistics | Open |
| Derivation of selected interactions from CAT/EPT | Open |
| Irreversible back-reaction from `S_I` | Open |

## Parameter-count audit

M9.7c adds a planar reduction, neutral-pair construction, local spinor Hamiltonian,
polarization angle, envelope, gauge seed, probe position, absorber shape, and time
windows. These are selected modeling inputs. M9 remains a multi-parameter research
model rather than a zero-parameter particle prediction.
