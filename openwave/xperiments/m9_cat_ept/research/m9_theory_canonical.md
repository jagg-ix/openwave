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
action, or unit map.

## 2. Shared density and clock interface

Accepted carriers map to normalized probability through a positive density:

```text
scalar: rho = |psi|^2
spinor: rho = Psi^dagger Psi
cell/shell probability: p_i proportional to rho_i Delta V_i.
```

M9.3 distinguishes remaining KL disequilibrium, accumulated discarded
information, and one-step total correlation. Channel depth is a data-processing
order, not physical time.

## 3. Scalar carrier record

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

## 4. M9.7a nonlinear spinor carrier

The bounded 1+1D prerequisite is

```text
i d_t Psi = -i alpha d_x Psi
            + beta (m - lambda bar(Psi)Psi) Psi
alpha = -sigma_2
beta = sigma_3
m = lambda = 1
omega = 0.8.
```

Its exact two-component Soler wave passes stationary-residual, second-order
convergence, conservation, window, finite perturbation, free-control,
background-pure-gauge, and entropic-clock gates.

The background transformation

```text
Psi' = exp(i q chi) Psi
A_x' = A_x + d_x chi
```

closes the covariant-energy interface. M9.7a does not contain a dynamical Maxwell
field.

## 5. M9.7b1 electrostatic Maxwell qualification

M9.7b1 freezes a regular spherical spinor-density source

```text
F(r) = A exp(-r/a)
G(r) = A eta (r/a) exp(-r/a)
rho = F^2 + G^2
a = 1
eta = 1/2.
```

It solves

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

This stage validates Gauss law, flux, field/source energy, signed source sectors,
resolution, window, source response, and the radial information map. Its spinor
density is an ansatz rather than a Dirac solution.

## 6. M9.7b2 coupled stationary radial system

### 6.1 Spinor convention

The spherical stationary four-spinor is

```text
Psi(r,t) = exp(-i omega t)
           (v(r) chi, i u(r) sigma.rhat chi)^T.
```

Its positive density and Lorentz scalar are

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

### 6.2 Frozen branch

The scored dimensionless inputs are

```text
m = epsilon0 = q = N = 1
lambda = 64.
```

The branch is continued through electrostatic charge fractions
`{0,1/4,1/2,3/4,1}`. Unit norm excludes the trivial zero field. The frequency is
parameterized by `omega=m tanh(s)`, enforcing the mass-gap condition.

A non-scoring exploratory solve selected `lambda=64` and the solver tolerances.
The result is therefore not blind preregistration and the coupling is not a
prediction.

### 6.3 Boundary conditions

At the center:

```text
u(0)=0
Q(0)=0
N(0)=0.
```

At finite radius `R`:

```text
N(R)=1
phi(R)=Q(R)/(4 pi epsilon0 R)
u(R)/v(R)=(kappa+1/R)/(m+omega-q phi(R))
kappa^2=m^2-(omega-q phi(R))^2.
```

### 6.4 Stationary solution

At the finest scored level:

```text
omega = 0.9914633829359464
v(0) = 0.07365091100207258
phi(0) = 0.024408951727442642
R_rms = 5.879232363303192
N = 1.0000000000740235
Q_total = 1.
```

Successive spinor, density, and frequency differences have observed orders

```text
3.95999936
3.95865476
3.96436926.
```

The independent stationary residual is `2.8273e-7`.

### 6.5 Maxwell and energy ledgers

```text
relative Gauss residual = 3.0123e-6
potential residual = 3.6943e-9
boundary-flux error = 2.9851e-8.
```

The field and source-potential energies are

```text
E_field = 0.007752284287965573
E_source = 0.007752284291468033
relative mismatch = 4.5180e-10.
```

The selected-model matter and total energies are

```text
E_matter = 1.0115160502925487
E_total = 1.0192683345805142.
```

The stationary eigenvalue identity closes to `5.7230e-8` relative.

### 6.6 Localization and robustness

At `R=40`, the fraction inside `r<=16` is `0.98942404`; the outer-20% fraction is
`7.9131e-5`.

At fixed radial spacing, the `R={30,40,50}` relative spreads are

```text
frequency = 7.3787e-6
central potential = 3.5742e-5
RMS radius = 2.3186e-3.
```

A fixed 5% opposite modulation of the initial upper/lower numerical guess returns
to the same BVP branch. This is an initial-guess basin check, not time-dependent
or orbital stability.

### 6.7 Signed sectors and clock interface

Under

```text
q -> -q
Q -> -Q
phi -> -phi,
```

`q phi`, the stationary spinor, and field energy are unchanged while signed
charge and boundary flux reverse. This is a dimensionless opposite source sector,
not an electron/positron calibration.

Shell probabilities

```text
p_i proportional to (v_i^2+u_i^2) Delta V_i
```

preserve the reflecting radial information ledger. Remaining KL contracts,
accumulated gain grows, one-step correlation remains nonnegative, and closure
error is zero.

## 7. Real and imaginary action sectors

- scalar and Soler interactions are explicit real-Hamiltonian model choices;
- M9.7b2 includes self-consistent electrostatic back-reaction;
- `lambda=64`, `q=1`, and the unit normalization are selected dimensionless inputs;
- none is derived from the pinned CAT/EPT imaginary-action layer;
- `S_I` and `|W|` remain weighting observables;
- no local imaginary potential or irreversible back-reaction is inferred.

## 8. Evidential status

Established:

- source-pinned CAT/EPT algebraic interfaces;
- convergent scalar and spinor solvers;
- Cartesian and radial information-clock interfaces;
- localized 1+1D scalar and spinor mathematical candidates;
- a background local-`U(1)` interface;
- a 3D electrostatic Maxwell constraint;
- a normalized localized stationary 3D radial spinor with electrostatic
  back-reaction;
- signed dimensionless charge, Gauss-law, boundary-flux, field-energy,
  convergence, window, and stationary eigenvalue ledgers.

Not established:

- time-dependent or orbital stability of the 3D branch;
- transverse Maxwell waves or magnetic self-fields;
- calibrated electric charge or electron/positron identity;
- fermionic quantization and statistics;
- physical mass or absolute units;
- necessity of `lambda=64` or any selected nonlinear interaction;
- irreversible physical-time evolution from the imaginary action.

The next canonical gate is M9.7b3: time-dependent spinor and gauge evolution
starting from the converged M9.7b2 branch.
