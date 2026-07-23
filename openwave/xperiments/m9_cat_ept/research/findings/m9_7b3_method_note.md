# M9.7b3 method note: time-dependent spherical spinor--electrostatic gate

## Decision

The selected M9.7b2 stationary branch survives the frozen finite perturbation
through `t=20` under a norm-unitary time-dependent nonlinear Dirac evolution with
a self-consistent longitudinal electrostatic field.

Every scored acceptance condition passes.

## Numerical structure

The physical shell-volume norm is

```text
N = sum_i Delta V_i (|V_i|^2 + |U_i|^2).
```

A second-order derivative `D` is paired with

```text
D_plus = -W^-1 D^T W,
```

where `W=diag(Delta V_i)`. Therefore the kinetic radial Dirac block is Hermitian
in the weighted norm. Its Crank--Nicolson step is unitary. The nonlinear mass and
electrostatic potential are real local phase rotations and preserve component
magnitudes during each local substep.

The longitudinal gauge field is projected from the current density after every
local half-step. This makes Gauss law a dynamical constraint rather than an
independently propagating transverse Maxwell mode.

## Dynamic refinement

The frozen `256/512/1024`-cell perturbation refinement through `t=5` gives

| Observable | Observed order |
| --- | ---: |
| Phase-aligned spinor volume-L2 | `1.92688667` |
| Density volume-L1 | `2.09471979` |

Across the three levels:

- maximum norm drift: `6.22e-15`;
- maximum total-energy relative drift: `3.26e-7`;
- maximum projected Gauss residual: `3.90e-14`;
- maximum matter boundary-current diagnostic: `4.62e-7`.

The finest perturbed run at `t=5` has

```text
fidelity = 0.9999328646
density volume-L1 difference = 0.0039748121.
```

## Long-time perturbation

For `R=40`, 512 cells, and `t=20`:

```text
fidelity = 0.9998920265
phase-aligned spinor volume-L2 = 0.0103914847
density volume-L1 = 0.0087558063
R_rms = 5.8887647996
core fraction r<=16 = 0.9897530407
outer-20% fraction = 7.22475e-5.
```

Conservation and constraint diagnostics are

```text
max norm drift = 9.99e-15
max total-energy relative drift = 8.15e-8
max projected Gauss residual = 1.96e-14
max matter boundary-current magnitude = 5.44e-7.
```

The final field and total charge are

```text
phi(0,t=20) = 0.0242629893
Q(t=20) = 0.9999999999999898.
```

This is finite-time stability evidence only. No spectral or nonlinear orbital
stability theorem is inferred.

## Window study

Independently converged stationary branches on `R={30,40,50}` are evolved through
`t=10` at fixed radial spacing. Relative spreads are

```text
RMS radius = 0.00524638
central potential = 0.00142295
core fraction = 0.000429055.
```

All frozen window thresholds pass.

## Radiation and boundary flux

In the spherical electrostatic truncation

```text
B = 0
S_Poynting = E x B = 0.
```

The electromagnetic radiation-flux ledger is therefore exactly zero. This is a
symmetry-enforced negative result: the model has no transverse radiative degree.
It must not be reported as a successful Maxwell-radiation simulation.

The matter current at the numerical boundary remains below `5.5e-7` in the long
run, showing that the finite window does not control the reported localization.
The weighted kinetic closure is reflecting, so this current is a contamination
diagnostic rather than an absorbing-boundary balance.

## Radial information clock

The final perturbed shell probability gives

```text
initial remaining KL = 1.3226178112
terminal remaining KL = 1.2965294256
accumulated gain = 0.0260883856
terminal one-step correlation = 3.9028548024
ledger closure error = 0.
```

Remaining disequilibrium contracts, accumulated discarded information grows, and
the one-step correlation remains nonnegative.

## Evidential classification

M9.7b3 establishes:

- time-dependent spherical nonlinear Dirac evolution;
- longitudinal electrostatic response at every substep;
- roundoff-level norm conservation;
- bounded total-energy drift;
- dynamic Gauss closure;
- second-order refinement and window convergence;
- finite-time localization under the frozen perturbation;
- preservation of the radial CAT/EPT density-clock interface.

It does not establish:

- transverse Maxwell waves, magnetic fields, or radiation;
- non-spherical orbital stability;
- calibrated electric charge or electron/positron identity;
- fermionic quantization or statistics;
- unique CAT/EPT selection of the Soler coupling;
- irreversible imaginary-action back-reaction.
