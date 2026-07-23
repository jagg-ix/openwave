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

These identities do not select a carrier, interaction, gauge action, unit map, or
particle identity.

## 2. Density and information interface

Accepted scalar and spinor carriers map to normalized probability through

```text
scalar: rho = |psi|^2
spinor: rho = Psi^dagger Psi
p_i proportional to rho_i Delta V_i.
```

The information channel records remaining KL disequilibrium, accumulated discarded
information, and one-step total correlation. Channel depth is not physical time.

## 3. Validated lower-dimensional records

M9.4--M9.6 validate an exact neutral 1+1D scalar soliton and establish its charge,
spin, and topology boundary. M9.7a validates an exact two-component 1+1D Soler
solitary wave.

M9.7b1--M9.7b3 add a spherical electrostatic Maxwell constraint, a normalized
stationary radial spinor branch, and finite-time constrained dynamics. The selected
radial branch uses

```text
m = epsilon0 = q = N = 1
lambda = 64
omega = 0.9914633829359464
R_rms = 5.879232363303192.
```

M9.7c adds bounded transverse radiation with nonzero Poynting flux and absorber
energy accounting. M9.8 provides shared claim-aware instrumentation.

## 4. M9.9 transported planar reduction

```text
i psi_s,t = [sigma_x(-i d_x-s q A_x)
             + m sigma_z-s q A_y sigma_y] psi_s

A_x,t = -E_x
E_x,t = -J_x
A_y,t = -E_y
E_y,t = -A_y,xx-J_y-sigma E_y.
```

The selected packets propagate and cross while norm, corrected energy, net charge,
final Gauss, magnetic, and emitted-energy ledgers remain within their frozen gates.
This is not a localized-particle result.

## 5. M9.10 two-dimensional transported reduction

### 5.1 Matter equation

For `s in {+1,-1}`:

```text
i psi_s,t = [sigma_x(-i d_x-s q A_x)
             + sigma_y(-i d_y-s q A_y)
             + m sigma_z] psi_s.
```

Charge and current are

```text
rho = q(|psi_+|^2-|psi_-|^2)
J_i = q psi_+^dagger sigma_i psi_+
      - q psi_-^dagger sigma_i psi_-.
```

### 5.2 Maxwell equation

```text
A_x,t = -E_x
A_y,t = -E_y
E_x,t = d_y B_z-J_x-sigma E_x
E_y,t = -d_x B_z-J_y-sigma E_y
B_z = d_x A_y-d_y A_x.
```

The absorber-induced charge obeys

```text
rho_abs,t = -div(sigma E),
```

and the Gauss ledger audits `div(E)=rho+rho_abs`.

### 5.3 Frozen inputs and result

```text
m = 1
q = 0.20
packet width = 2.2
centers = (-5,-2), (5,2)
momenta = (0.95,0.35), (-0.95,-0.2275)
gauge seed amplitude = 0.006.
```

```text
transported-spinor order = 8.18686
long-run norm drift = 5.73621e-9
corrected-energy drift = 6.53843e-9
final Gauss residual = 1.49202e-8 absolute, 1.71900e-5 relative
max net charge = 5.51630e-11
packet separation = 10.77033 -> 1.03495
transport angle = 0.38051 -> 1.34895
emitted energy = 1.12278e-5
max magnetic field = 0.00770611.
```

All nine M9.10 gates pass. The high smooth-benchmark refinement order is not
claimed as universal accuracy.

## 6. M9.11 localization and radiative-stability decision

The selected nonlinear family modifies each species' effective mass:

```text
M_s = m-lambda psi_s^dagger sigma_z psi_s
lambda in {0,2,4,8}.
```

At `t=8`, the strongest member reduces spreading:

```text
free maximum RMS ratio = 1.52762639
lambda=8 maximum RMS ratio = 1.40072364
spreading improvement = 0.12690276
lambda=8 minimum peak ratio = 0.85486943
lambda=8 minimum core fraction = 0.95543175.
```

The fixed perturbation survives the finite-time gate:

```text
maximum RMS ratio = 1.34175227
minimum peak ratio = 0.88188286
minimum core fraction = 0.95992433.
```

At `t=12`, the same member fails:

```text
maximum RMS ratio = 1.73615505
minimum peak ratio = 0.67364906
minimum core fraction = 0.92050318.
```

Canonical decision:

> `lambda=8` is a finite-time reduced-spreading candidate, but it fails the
> long-time localization gate. No stable two-dimensional particle candidate is
> accepted.

All nine decision-procedure gates pass, including the explicit negative particle
decision and the norm, energy, Gauss, perturbation, and radiation ledgers.

## 7. Evidential status

Established for selected dimensionless models:

- source-pinned CAT/EPT algebraic, density, and information interfaces;
- scalar and spinor controls and lower-dimensional localization candidates;
- spherical stationary and finite-time electrostatic dynamics;
- bounded transverse radiation and absorber accounting;
- one- and two-dimensional spatial Dirac transport;
- two-dimensional magnetic curl, Gauss continuity, non-axis-aligned transport,
  refinement, and domain-shape robustness;
- a completed nonlinear localization decision with finite-time improvement and
  long-time rejection.

Not established:

- a stable localized charged particle;
- orbital or asymptotic stability;
- full three-dimensional Maxwell--Dirac dynamics;
- physical mass, charge, length, or energy calibration;
- electron, positron, photon, or Standard Model identity;
- fermionic quantization and statistics;
- unique CAT/EPT selection of `lambda=8` or the other selected interactions;
- irreversible physical-time evolution derived from the imaginary action.

The next canonical target is a separately bounded three-dimensional transport
program.
