# M9 CAT/EPT canonical specification

This document separates exact identities, numerical results, physical
identifications, and open model choices.

## 1. Formal CAT/EPT interface

The pinned contract supplies

```text
psi = sqrt(rho) exp(i Phi),
|psi|^2 = rho,
tau_ent = gamma C,
S_I = hbar tau_ent,
|W| = exp(-tau_ent),
omega_C = mc^2/hbar,
omega_Z(0) = 2 omega_C.
```

These identities do not select a particle equation, interaction, carrier, gauge
action, or unit map.

## 2. Shared density and clock interface

Accepted carriers map to normalized probability through a positive density:

```text
scalar: rho = |psi|^2
spinor: rho = Psi^dagger Psi
Cartesian cell: p_i proportional to Delta V_i rho_i
radial shell: p_i proportional to Delta V_shell,i rho_i.
```

M9.3 uses a doubly-stochastic channel to distinguish remaining KL
disequilibrium, accumulated discarded information, and one-step total
correlation. Channel depth is a data-processing order, not physical time.

## 3. Scalar carrier record

The scalar branch uses

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi,
g > 0,
```

with norm-`N` family

```text
eta = gN/2,
psi = eta/sqrt(g) sech(eta x) exp(i eta^2 t/2),
mu = -eta^2/2,
omega_phase = eta^2/2,
E = -eta^3/(3g),
R_rms = pi/(2 sqrt(3) eta).
```

M9.4--M9.5 validate localization, finite perturbation survival, scaling, and

```text
omega_phase R_rms^2 = pi^2/24,
E/(mu N) = 1/3.
```

M9.6 records that the scalar carrier has global `U(1)` norm but does not itself
supply local gauge charge, spin-1/2, or a protected topological sector.

## 4. M9.7a nonlinear spinor carrier

The bounded 1+1D prerequisite is

```text
i d_t Psi = -i alpha d_x Psi
            + beta (m - lambda bar(Psi)Psi) Psi,
alpha = -sigma_2,
beta = sigma_3,
m = 1,
lambda = 1,
omega = 0.8.
```

Its exact two-component Soler solitary wave passes stationary-residual,
second-order convergence, conservation, window, finite perturbation, free-control,
background pure-gauge, and entropic-clock gates.

At the finest grid:

```text
spinor L2 error = 1.53398e-7,
density relative L1 = 8.72859e-8,
fidelity = 0.9999999999999846,
norm drift = 1.69198e-13,
model-energy drift = 1.03695e-13.
```

The background transformation

```text
Psi' = exp(i q chi) Psi,
A_x' = A_x + d_x chi
```

closes the covariant-energy interface, but M9.7a has no Maxwell field equation or
field energy.

## 5. M9.7b1 three-dimensional electrostatic gauge sector

### 5.1 Regular spherical source ansatz

M9.7b1 freezes a regular spherical four-spinor density represented by upper
s-wave and lower p-wave radial amplitudes:

```text
F(r) = A exp(-r/a),
G(r) = A eta (r/a) exp(-r/a),
rho(r) = F(r)^2 + G(r)^2,
a = 1,
eta = 1/2.
```

`A` is fixed by

```text
4 pi integral_0^infinity r^2 rho(r) dr = 1.
```

The ansatz is a positive spinor-density carrier and Maxwell source. It is not a
solution of the 3D Dirac stationary equation.

### 5.2 Electrostatic Maxwell constraint

For signed dimensionless source normalization `q`, the solver enforces

```text
Q(r) = 4 pi integral_0^r s^2 q rho(s) ds,
E(r) = Q(r)/(4 pi epsilon0 r^2),
phi(infinity) = 0.
```

The total field energy includes the exterior Coulomb tail:

```text
U_E = epsilon0/2 integral_0^R 4 pi r^2 E(r)^2 dr
      + Q(R)^2/(8 pi epsilon0 R).
```

An independent ledger evaluates

```text
U_source = 1/2 integral rho_q phi d^3x.
```

For the frozen ansatz, exact references are

```text
raw norm = pi a^3 (1 + 3 eta^2),
phi(0) = q(2 + 3 eta^2)/(8 pi epsilon0 a(1 + 3 eta^2)),
U_E = q^2/(8 pi epsilon0 a)
      * (837 eta^4 + 672 eta^2 + 160)
      / (256(1 + 3 eta^2)^2).
```

### 5.3 Numerical result

The 256/512/1024-shell refinement yields observed orders

```text
field energy: 2.00123, 2.00029
central potential: 1.94259, 1.97060.
```

At 1024 shells:

```text
Gauss shell residual = 4.01e-16,
boundary-flux error = 1.11e-16,
field-energy relative error = 2.185e-5,
central-potential relative error = 4.199e-5,
source/field energy relative difference = 3.128e-6.
```

The density has core fraction `0.99981907` inside `r<=8a` and outer-20% fraction
`7.04e-8`.

### 5.4 Signed sectors and perturbation

Changing `q` from `+1` to `-1` reverses `E`, `phi`, and boundary flux while
preserving number density and field energy. This is a dimensionless signed source
sector, not an electron-charge calibration.

A fixed 2% opposite modulation of `F` and `G` gives

```text
field-energy ratio = 1.009983,
central-potential ratio = 1.011529,
core fraction = 0.99981957,
outer-20% fraction = 7.03e-8.
```

This is source-to-field response, not time-dependent spinor stability.

### 5.5 Radial information interface

Radial shell probabilities use `p_i proportional to rho_i Delta V_i`. A
reflecting symmetric nearest-neighbor channel replaces the periodic channel
because the radial interval has an origin and an outer boundary. Base and
perturbed ledgers both show nonincreasing remaining KL, nondecreasing accumulated
gain, nonnegative one-step correlation, and exact ledger closure.

## 6. Real and imaginary action sectors

- scalar and Soler interactions remain explicit real-Hamiltonian model choices;
- the M9.7b1 electrostatic field is a source-responsive Maxwell constraint;
- none of these terms is derived from the pinned CAT/EPT imaginary-action layer;
- `S_I` and `|W|` remain weighting observables;
- no local imaginary potential or irreversible back-reaction is inferred.

## 7. Evidential status

Established:

- source-pinned CAT/EPT algebraic interfaces;
- convergent scalar and 1+1D spinor evolution solvers;
- one Cartesian/periodic and one radial/reflecting information-clock interface;
- localized neutral 1+1D scalar and spinor mathematical candidates;
- a background local-`U(1)` spinor interface;
- a 3D regular spinor-density source with self-consistent electrostatic field;
- signed dimensionless flux, Gauss-law, boundary, and field-energy ledgers.

Not established:

- a coupled 3D Dirac stationary solution;
- dynamical Maxwell waves or magnetic fields;
- dynamical 3D localization and perturbation stability;
- calibrated electric charge or electron/positron identity;
- fermionic quantization and statistics;
- physical mass or absolute unit calibration;
- necessity of the selected scalar, Soler, or radial ansatz;
- irreversible physical-time evolution from the imaginary action.

The next canonical gate is M9.7b2: a bounded self-consistent stationary radial
Dirac--electrostatic system in which the spinor profile and potential determine
one another.
