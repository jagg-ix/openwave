# M9 CAT/EPT canonical specification

This document separates exact identities, numerical results, physical
identifications, and open model choices.

## 1. Formal CAT/EPT interface

The pinned contract supplies

```text
psi = sqrt(rho) exp(i Phi)
|psi|^2 = rho
tau_ent = gamma C
S_I = hbar tau_ent
|W| = exp(-tau_ent)
omega_C = mc^2/hbar
omega_Z(0) = 2 omega_C.
```

These identities do not select a particle equation, interaction, carrier, gauge
action, unit map, or nonlinear coupling.

## 2. Shared density and information interface

Accepted carriers map to normalized probability through a positive density:

```text
scalar: rho = |psi|^2
spinor: rho = Psi^dagger Psi
cell/shell probability: p_i proportional to rho_i Delta V_i.
```

M9.3 distinguishes remaining KL disequilibrium, accumulated discarded
information, and one-step total correlation. Channel depth is a data-processing
order, not physical time.

## 3. Scalar and 1+1D spinor records

The scalar branch uses

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi.
```

For norm `N`:

```text
eta = gN/2
psi = eta/sqrt(g) sech(eta x) exp(i eta^2 t/2)
mu = -eta^2/2
omega_phase = eta^2/2
E = -eta^3/(3g)
R_rms = pi/(2 sqrt(3) eta).
```

M9.4--M9.5 validate localization, finite perturbation survival, scaling, and

```text
omega_phase R_rms^2 = pi^2/24
E/(mu N) = 1/3.
```

M9.6 records that the scalar carrier has global `U(1)` norm but does not itself
supply local gauge charge, spin-1/2, or protected topology.

M9.7a uses the bounded 1+1D nonlinear Dirac/Soler equation

```text
i d_t Psi = -i alpha d_x Psi
            + beta (m - lambda bar(Psi)Psi) Psi
alpha = -sigma_2
beta = sigma_3
m = lambda = 1
omega = 0.8.
```

Its exact two-component solitary wave passes stationary-residual, second-order
convergence, conservation, window, finite perturbation, free-control,
background-pure-gauge, and entropic-clock gates.

## 4. Three-dimensional electrostatic program

### 4.1 M9.7b1 electrostatic qualification

M9.7b1 validates the spherical Maxwell constraint

```text
Q(r) = 4 pi integral_0^r s^2 q rho(s) ds
E(r) = Q(r)/(4 pi epsilon0 r^2)
phi(infinity) = 0.
```

The field energy includes the exterior Coulomb tail:

```text
U_E = epsilon0/2 integral_0^R 4 pi r^2 E^2 dr
      + Q(R)^2/(8 pi epsilon0 R).
```

This stage closes Gauss law, signed flux, field/source energy, resolution,
window, source-response, and radial information ledgers for a regular spherical
spinor-density source.

### 4.2 M9.7b2 stationary coupled branch

The spherical stationary four-spinor is

```text
Psi(r,t) = exp(-i omega t)
           (v(r) chi, i u(r) sigma.rhat chi)^T.
```

Its density and Lorentz scalar are

```text
rho = v^2 + u^2
S = v^2 - u^2.
```

The selected coupled equations are

```text
v' = -(omega - q phi + M) u
u' + 2u/r = (omega - q phi - M) v
M = m - lambda S
Q' = 4 pi r^2 q rho
phi' = -Q/(4 pi epsilon0 r^2).
```

The scored dimensionless inputs are

```text
m = epsilon0 = q = N = 1
lambda = 64.
```

Unit norm excludes the zero solution. Electrostatic charge continuation produces

```text
omega = 0.9914633829359464
v(0) = 0.07365091100207258
phi(0) = 0.024408951727442642
R_rms = 5.879232363303192.
```

The branch passes near-fourth-order profile/frequency convergence, independent
Dirac and Maxwell residuals, field/source energy closure, window convergence,
signed source sectors, and the radial CAT/EPT information ledger.

The exploratory phase selected `lambda=64`; it is not a CAT/EPT derivation or a
physical prediction.

## 5. M9.7b3 constrained time-dependent spherical dynamics

### 5.1 Evolution equations

The stationary branch is evolved by

```text
i V_t = (d_r + 2/r) U + (q phi + M) V
i U_t = -d_r V + (q phi - M) U
M = m - lambda(|V|^2-|U|^2)

rho = |V|^2 + |U|^2
Q(r,t) = 4 pi integral_0^r s^2 q rho(s,t) ds
E(r,t) = Q(r,t)/(4 pi epsilon0 r^2).
```

The longitudinal electrostatic potential is reconstructed with
`phi(infinity,t)=0` after every local half-step.

### 5.2 Discrete Hamiltonian structure

Shell volumes define the physical norm weight `W`. A second-order radial
derivative `D` is paired with

```text
D_plus = -W^-1 D^T W.
```

The radial kinetic Dirac block is therefore Hermitian in the weighted norm. The
kinetic Crank--Nicolson substep is unitary. The nonlinear effective mass and
longitudinal potential are real local phase rotations. Strang composition gives
a second-order time integrator.

No step renormalizes the spinor after the initial perturbation.

### 5.3 Frozen perturbation

```text
V -> (1 + 0.02 cos(pi r/R)) exp(+i chi) V
U -> (1 - 0.02 cos(pi r/R)) exp(-i chi) U
chi = 0.02 sin(pi r/R).
```

The perturbation combines a component-opposite shape change and radial phase
current while preserving the target norm at the initial time.

### 5.4 Dynamic refinement and conservation

For `R=40`, `t=5`, and cells `{256,512,1024}`:

```text
spinor self-convergence order = 1.92688667
density self-convergence order = 2.09471979
max norm drift = 6.22e-15
max total-energy relative drift = 3.26e-7
max projected Gauss residual = 3.90e-14
max matter boundary-current magnitude = 4.62e-7.
```

At the finest dynamic level:

```text
fidelity = 0.9999328646
density volume-L1 difference = 0.0039748121.
```

### 5.5 Long-time finite perturbation result

For 512 cells through `t=20`:

```text
fidelity = 0.9998920265
phase-aligned spinor volume-L2 = 0.0103914847
density volume-L1 = 0.0087558063
R_rms = 5.8887647996
core fraction r<=16 = 0.9897530407
outer-20% fraction = 7.22475e-5
max norm drift = 9.99e-15
max total-energy relative drift = 8.15e-8
max projected Gauss residual = 1.96e-14.
```

This is finite-time stability evidence for the selected spherical constrained
model. It is not a nonlinear orbital-stability theorem.

### 5.6 Dynamic window and information ledgers

Independently converged branches on `R={30,40,50}` are evolved through `t=10` at
fixed radial spacing. Relative spreads are

```text
RMS radius = 0.00524638
central potential = 0.00142295
core fraction = 0.000429055.
```

The final perturbed shell probability gives

```text
initial remaining KL = 1.3226178112
terminal remaining KL = 1.2965294256
accumulated gain = 0.0260883856
terminal one-step correlation = 3.9028548024
ledger closure error = 0.
```

### 5.7 Radiation boundary

The M9.7b3 symmetry reduction is spherical and electrostatic:

```text
B = 0
S_Poynting = E x B = 0.
```

Electromagnetic Poynting flux is exactly zero because the model contains no
transverse Maxwell degree. This is a symmetry-enforced negative radiation result,
not evidence for full Maxwell-wave stability. The matter boundary-current
diagnostic remains below `5.5e-7`.

## 6. Real and imaginary action sectors

- scalar and Soler interactions are explicit real-Hamiltonian model choices;
- M9.7b2--M9.7b3 include self-consistent longitudinal electrostatic back-reaction;
- `lambda=64`, `q=1`, normalization, perturbation, and boundaries are selected
  dimensionless inputs;
- none is derived from the pinned CAT/EPT imaginary-action layer;
- `S_I` and `|W|` remain weighting observables;
- no local imaginary potential or irreversible back-reaction is inferred.

## 7. Evidential status

Established:

- source-pinned CAT/EPT algebraic interfaces;
- convergent scalar and spinor solvers;
- Cartesian and radial information-clock interfaces;
- localized 1+1D scalar and spinor mathematical candidates;
- a 3D electrostatic Maxwell constraint;
- a normalized localized stationary 3D radial spinor branch;
- finite-time constrained spherical spinor--electrostatic evolution;
- roundoff-level dynamic norm conservation;
- bounded dynamic total-energy drift;
- dynamic Gauss closure, refinement, window, perturbation, and information ledgers.

Not established:

- transverse Maxwell waves, magnetic self-fields, or radiation;
- non-spherical orbital stability;
- calibrated electric charge or electron/positron identity;
- fermionic quantization and statistics;
- physical mass or absolute units;
- necessity of `lambda=64` or any selected nonlinear interaction;
- irreversible physical-time evolution from the imaginary action.

The next canonical gate is M9.7c: non-spherical/transverse Maxwell--spinor
evolution with electric, magnetic, Poynting, absorbing-boundary, and emitted-energy
ledgers.
