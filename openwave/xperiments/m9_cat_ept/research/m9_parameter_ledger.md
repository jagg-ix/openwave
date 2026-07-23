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

## Fixed selected-model inputs

| Choice | Value | Classification |
| --- | --- | --- |
| Scalar localization survey | `kappa in {0,+2,-2}` | M9.4 bounded choice |
| 1+1D spinor equation | Cubic Soler / massive Gross--Neveu form | M9.7a selected input |
| 3D radial spinor | `(v chi, i u sigma.rhat chi)^T` | Representation convention |
| 3D effective mass | `M=m-lambda(v^2-u^2)` | Selected Soler interaction |
| 3D parameters | `m=epsilon0=q=N=1`, `lambda=64` | Dimensionless inputs |
| Stationary branch method | Charge continuation `{0,1/4,1/2,3/4,1}` | Numerical branch construction |
| Radial boundary | Regular origin plus Coulomb/exponential finite-window tail | Boundary convention |
| Dynamic radial grid | Exact shell volumes with second-order weighted-adjoint derivative pair | M9.7b3 discretization |
| Dynamic kinetic step | Weighted-unitary Crank--Nicolson | Numerical method |
| Dynamic local step | Exact nonlinear/electrostatic phase rotation | Numerical method |
| Gauge evolution | Longitudinal Poisson projection after every local half-step | Constrained spherical gauge model |
| Frozen perturbation | 2% opposite amplitude and 2% opposite component phase | M9.7b3 input |
| Dynamic refinement | `R=40`, `t=5`, cells `{256,512,1024}`, `dt=0.1 dr` | Scored gate |
| Long-time run | `R=40`, 512 cells, `t=20` | Scored finite-time gate |
| Dynamic window study | `R={30,40,50}` at fixed radial spacing | Scored gate |
| Radial clock | Reflecting symmetric nearest-neighbor channel, 64 depths | Information input |

## Selection transparency

A non-scoring exploratory BVP continuation selected the normalized `lambda=64`
branch and solver tolerances before M9.7b2. M9.7b3 inherits that selected branch.
The dynamic perturbation, refinement, time horizons, conservation thresholds, and
window study were frozen before the scored dynamic run.

Consequently:

- `lambda=64` is not a CAT/EPT derivation or physical prediction;
- the positive dynamic result applies to the selected dimensionless branch;
- the time-dependent result is finite-time numerical evidence, not an orbital
  stability theorem.

## Result classification

| Result | Evidential classification |
| --- | --- |
| M9.7b2 normalized branch | Coupled stationary BVP result |
| Weighted-unitary norm conservation | Discrete numerical identity |
| Dynamic energy drift below `3.3e-7` across refinement | Numerical conservation result |
| Dynamic Gauss residual below `4e-14` | Poisson-projected longitudinal constraint result |
| Dynamic self-convergence near order 2 | Time-evolution solver validation |
| `t=20` fidelity `0.999892` | Finite-time localization evidence |
| Matter boundary current below `5.5e-7` | Window-contamination diagnostic |
| Electromagnetic Poynting flux `0` | Symmetry-enforced negative in spherical electrostatics |
| Radial KL contraction | Data-processing result for the reflecting channel |
| Magnitude `q=1` | Arbitrary dimensionless normalization, not measured charge |

## Open structural choices

| Choice | Status |
| --- | --- |
| Derivation of scalar or Soler interaction from CAT/EPT | Open |
| Transverse/non-spherical Maxwell degrees | Open M9.7c |
| Magnetic self-field and radiative Poynting flux | Open M9.7c |
| Absorbing boundary and emitted-energy balance | Open M9.7c |
| Non-spherical orbital stability | Open |
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

There is still no particle-physics prediction. The strongest conditional dynamic
statement is:

> Given the selected dimensionless spherical Soler--electrostatic equations,
> `m=epsilon0=q=N=1`, `lambda=64`, the converged M9.7b2 branch, and the frozen
> M9.7b3 numerical method and perturbation, the state remains localized through
> `t=20` while norm, total energy, longitudinal Gauss law, window, refinement, and
> radial-information ledgers remain within their declared gates.

This statement does not assign an electron, positron, or photon identity.

## Parameter-count audit

M9.7b3 removes the prior absence of time evolution in the spherical sector but
retains the selected strong coupling, normalization, representation, electrostatic
projection, reflecting boundary, perturbation, and time-window choices. Physical
interpretation still requires unit, charge, statistics, and clock maps. M9 is not
a zero-parameter particle model.
