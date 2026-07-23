# M9 CAT/EPT canonical specification

This document separates formal identities, selected equations, numerical results,
and physical identifications.

## 1. Formal CAT/EPT interface

The pinned formal source supplies

```text
psi = sqrt(rho) exp(i Phi)
|psi|^2 = rho
tau_ent = gamma C
S_I = hbar tau_ent
|W| = exp(-tau_ent)
omega_C = mc^2/hbar
omega_Z(0) = 2 omega_C.
```

These identities do not select a carrier, nonlinear interaction, gauge action,
unit map, or particle identity.

## 2. Shared density and information interface

For every accepted carrier, positive density defines normalized cell or shell
probability:

```text
scalar: rho = |psi|^2
spinor: rho = Psi^dagger Psi
p_i proportional to rho_i Delta V_i.
```

The M9 information channel measures remaining KL disequilibrium, accumulated
discarded information, and one-step total correlation. Channel depth is a data
processing order, not physical time.

## 3. Scalar and 1+1D spinor records

The scalar bright-soliton family uses

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi
eta = gN/2
psi = eta/sqrt(g) sech(eta x) exp(i eta^2 t/2).
```

Its exact energy, radius, frequency, norm scaling, and invariant ledgers pass.
The scalar carrier does not itself supply electric charge, spin-1/2, or protected
topology.

M9.7a uses

```text
i Psi_t = -i alpha Psi_x + beta(m-lambda bar(Psi)Psi)Psi
alpha = -sigma_2
beta = sigma_3
m = lambda = 1
omega = 0.8.
```

The exact two-component Soler wave passes stationary, convergence, conservation,
window, perturbation, free-control, background-gauge, and information gates.

## 4. Spherical electrostatic program

The radial gauge constraint is

```text
Q' = 4 pi r^2 q rho
phi' = -Q/(4 pi epsilon0 r^2).
```

The coupled stationary spinor branch solves

```text
v' = -(omega-q phi+M)u
u' + 2u/r = (omega-q phi-M)v
M = m-lambda(v^2-u^2).
```

For

```text
m = epsilon0 = q = N = 1
lambda = 64
```

the selected normalized branch has

```text
omega = 0.9914633829359464
R_rms = 5.879232363303192.
```

The stationary and time-dependent radial programs pass residual, norm, energy,
Gauss, flux, convergence, window, perturbation, localization, and information
ledgers. Spherical electrostatics has no transverse magnetic radiation mode.

## 5. Bounded transverse radiation

M9.7c evolves

```text
A_t = -E
E_t = -A_xx - J - sigma(x) E
B = A_x.
```

A neutral opposite-charge local spinor pair supplies `J`. The bounded reduction
passes vacuum and coupled convergence, dynamic zero-charge Gauss closure, nonzero
Poynting emission, corrected energy balance, and absorber/window robustness.

## 6. Shared instrumentation

M9.8 defines deterministic preset-to-ledger and preset-to-runner links, common
metric and acceptance panels, explicit claim boundaries, headless JSON/PNG export,
an interactive dashboard, and OpenWave launcher discovery.

Instrumentation consumes scientific ledgers; it does not alter equations or add
physical claims.

## 7. M9.9 transported planar Maxwell--Dirac reduction

### 7.1 Matter equations

Two opposite-charge packets evolve by

```text
i psi_s,t = [sigma_x(-i d_x-s q A_x)
             + m sigma_z-s q A_y sigma_y] psi_s
s in {+1,-1}.
```

Charge and currents are

```text
rho = q(|psi_+|^2-|psi_-|^2)
J_i = q psi_+^dagger sigma_i psi_+
      - q psi_-^dagger sigma_i psi_-.
```

### 7.2 Gauge equations

```text
A_x,t = -E_x
E_x,t = -J_x
A_y,t = -E_y
E_y,t = -A_y,xx - J_y - sigma(x) E_y
B_z = A_y,x.
```

The initial longitudinal field inverts the centered-derivative Fourier symbol, so
the initial discrete Gauss equation uses the same operator as the evolution and
diagnostic.

### 7.3 Frozen inputs

```text
m = 1
q = 0.25
packet width = 2.5
packet centers = -8,+8
packet momenta = +0.9,-0.9
transverse seed amplitude = 0.008
transverse seed width = 4.
```

The total norm is one and the net charge is zero.

### 7.4 Numerical result

The 128/256/512 refinement gives

```text
transported-spinor order = 1.8991759529.
```

At 512 points through `t=14`:

```text
max norm drift = 6.0176e-10
max corrected-energy relative drift = 1.07295e-6
final Gauss residual = 2.75441e-4 absolute
final Gauss residual = 0.0226400 relative
max net charge = 1.04083e-16
packet separation = 16 -> -2.21328
emitted energy = 2.84143e-5
max transverse field = 0.0100947.
```

The wave-packet centers cross. The result demonstrates spatial Dirac transport and
gauge back-reaction. It does not demonstrate a stable localized charged particle.

## 8. Evidential status

Established for selected dimensionless models:

- source-pinned CAT/EPT algebraic and density interfaces;
- scalar and spinor control/localization results;
- spherical electrostatic stationary and finite-time dynamics;
- bounded transverse Maxwell radiation and absorber accounting;
- shared research instrumentation with claim boundaries;
- transported opposite-charge Dirac packets with longitudinal and transverse gauge
  response;
- bounded convergence, norm, corrected-energy, charge, Gauss, transport, and
  emitted-energy ledgers.

Not established:

- a stable localized charged particle;
- full two- or three-dimensional Maxwell--Dirac dynamics;
- physical mass, charge, length, or energy calibration;
- electron, positron, photon, or Standard Model identity;
- fermionic quantization and statistics;
- necessity of the selected nonlinear and gauge couplings;
- irreversible physical-time dynamics derived from the imaginary action.

The next canonical gate is M9.10: two-dimensional transported Maxwell--Dirac
qualification with two-dimensional Gauss, magnetic curl, energy, absorber,
refinement, domain-shape, and transport ledgers.
