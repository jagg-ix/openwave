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
physical unit map, or particle identity.

## 2. Shared density and information interface

Accepted carriers map to normalized probability through positive density:

```text
scalar: rho = |psi|^2
spinor: rho = Psi^dagger Psi
cell/shell probability: p_i proportional to rho_i Delta V_i.
```

The M9 information clock distinguishes remaining KL disequilibrium, accumulated
discarded information, and one-step total correlation. Channel depth is a
data-processing order, not physical time.

## 3. Scalar and 1+1D spinor program

The scalar localization family is

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi
eta = gN/2
psi = eta/sqrt(g) sech(eta x) exp(i eta^2 t/2)
E = -eta^3/(3g)
R_rms = pi/(2 sqrt(3) eta).
```

The exact identities

```text
omega_phase R_rms^2 = pi^2/24
E/(mu N) = 1/3
```

close numerically. The scalar audit records global `U(1)` norm but no local gauge
charge, spin-1/2, or protected topology.

M9.7a then selects

```text
i d_t Psi = -i alpha d_x Psi
            + beta(m-lambda bar(Psi)Psi)Psi
alpha = -sigma_2
beta = sigma_3
m = lambda = 1
omega = 0.8.
```

Its exact solitary wave passes stationary, convergence, conservation, window,
finite perturbation, free-control, background-gauge, and information gates.

## 4. Spherical 3D electrostatic program

### 4.1 Electrostatic qualification

M9.7b1 validates

```text
Q(r) = 4 pi integral_0^r s^2 q rho(s) ds
E(r) = Q(r)/(4 pi epsilon0 r^2)
phi(infinity) = 0.
```

The field-energy ledger includes the exterior Coulomb tail.

### 4.2 Coupled stationary branch

The stationary radial equations are

```text
v' = -(omega - q phi + M) u
u' + 2u/r = (omega - q phi - M) v
M = m - lambda(v^2-u^2)
Q' = 4 pi r^2 q(v^2+u^2)
phi' = -Q/(4 pi epsilon0 r^2).
```

For

```text
m = epsilon0 = q = N = 1
lambda = 64
```

the normalized branch has

```text
omega = 0.9914633829359464
R_rms = 5.879232363303192.
```

It passes independent Dirac and Maxwell residuals, energy closure, convergence,
window, signed-sector, and radial-information gates.

### 4.3 Constrained spherical dynamics

M9.7b3 evolves

```text
i V_t = (d_r + 2/r) U + (q phi + M) V
i U_t = -d_r V + (q phi - M) U
M = m - lambda(|V|^2-|U|^2).
```

The longitudinal field is reconstructed from Gauss law after local substeps. At
`t=20`, the selected branch retains fidelity `0.9998920265`, core fraction
`0.9897530407`, norm drift below `1e-14`, and total-energy drift below `8.2e-8`.

The spherical radiation result is negative by symmetry:

```text
B = 0
E cross B = 0.
```

## 5. M9.7c transverse Maxwell--spinor program

### 5.1 Bounded geometry

M9.7c leaves spherical electrostatics with a planar transverse gauge mode:

```text
A = A_y(x,t)
E = E_y = -A_t
B = B_z = A_x.
```

The hyperbolic field equations are

```text
A_t = -E
E_t = -A_xx - J - sigma(x) E.
```

The field energy and Poynting flux are

```text
E_field = 1/2 integral(E^2+B^2) dx
S_x = E B.
```

### 5.2 Neutral spinor-current pair

Two local two-component spinors carry opposite charge labels:

```text
i psi_s,t = [m sigma_z - s q A sigma_y] psi_s
s in {+1,-1}
J = q psi_+^dagger sigma_y psi_+
    - q psi_-^dagger sigma_y psi_-.
```

Their initial pointwise densities are equal:

```text
rho_q = q(|psi_+|^2-|psi_-|^2) = 0.
```

The symmetric local evolution preserves both species norms exactly in the
continuum and to binary64 equality in the scored runs. Gauss law therefore closes
without a Poisson projection.

This is a local polarization-current model. It does not include spatial transport
of the spinor envelope.

### 5.3 Selected inputs

```text
m = 1
q = 0.35
polarization angle = 0.45
envelope width = 2.5
matter norm = 1
gauge seed amplitude = 0.01
gauge seed width = 4.
```

### 5.4 Numerical structure

- periodic second-order finite differences;
- fourth-order Runge--Kutta time integration;
- edge conductivity absorber;
- symmetric Poynting probes;
- matter, field, absorbed, and emitted-energy ledgers.

The corrected energy is

```text
E_corrected = E_matter + E_field + E_absorbed.
```

### 5.5 M9.7c1 vacuum result

For an exact right-moving pulse:

```text
A orders = 1.99907, 1.99989
E orders = 1.99347, 1.99859.
```

### 5.6 M9.7c2 coupled result

At the finest coupled refinement level:

```text
A self-convergence order = 1.98383
E self-convergence order = 1.95569
max signed charge density = 0
max pair-norm mismatch = 0
corrected-energy relative drift = 5.14e-7
emitted energy = 3.996e-5
central field-energy fraction = 0.09896.
```

### 5.7 M9.7c3 radiation and absorber result

At `t=80`:

```text
emitted energy = 6.15138e-4
absorbed energy = 4.89886e-4
corrected-energy relative drift = 1.77811e-6.
```

Across the three absorber/window cases:

```text
emitted-energy relative spread = 0.0042613
maximum corrected-energy relative drift = 1.443e-6.
```

The Poynting flux is nonzero, unlike the spherical M9.7b3 sector.

## 6. Real and imaginary action sectors

- scalar, Soler, electrostatic, and transverse couplings are selected real-sector
  model choices;
- none is derived from the pinned CAT/EPT imaginary-action layer;
- `S_I` and `|W|` remain formal weighting observables;
- no irreversible local imaginary potential or back-reaction is inferred.

## 7. Evidential status

Established within the selected models:

- source-pinned CAT/EPT algebraic interfaces;
- convergent scalar, spinor, radial, and transverse solvers;
- localized scalar, 1+1D spinor, and stationary radial mathematical candidates;
- constrained spherical finite-time localization;
- transverse electric and magnetic field evolution;
- nonzero Poynting emission;
- dynamic neutral Gauss closure without projection;
- absorber and emitted-energy accounting;
- resolution and absorber-window convergence.

Not established:

- a full spatial non-spherical Maxwell--Dirac solution;
- a localized charged transverse particle;
- non-spherical orbital stability;
- calibrated electric charge or Standard Model identity;
- fermionic quantization and statistics;
- physical mass or absolute units;
- necessity of any selected nonlinear coupling;
- irreversible physical time from the imaginary action.

## 8. Next canonical gate

M9.8 may now add shared instrumentation, deterministic presets, headless export,
and interactive rendering for the validated scalar, radial, and transverse
sectors. The UI must preserve the same claim boundaries and may not default to
an electron or other particle identity.
