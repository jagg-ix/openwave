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

These identities do not select a particle equation, interaction, carrier, or unit
map.

## 2. Shared probability and clock interface

M9 maps any accepted carrier to normalized cell probability through its positive
density:

```text
scalar: rho = |psi|^2
spinor: rho = Psi^dagger Psi
p_i = dx rho_i / sum_j dx rho_j.
```

M9.3 then applies

```text
(Kp)_i = 1/4 p_{i-1} + 1/2 p_i + 1/4 p_{i+1}.
```

Remaining KL disequilibrium contracts and accumulated discarded information grows
along channel depth. This is a data-processing order, not monotonicity of unitary
physical time.

## 3. Scalar carrier record

The scalar branch uses

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi,
g > 0.
```

For norm `N`,

```text
eta = gN/2,
psi(x,t) = eta/sqrt(g) sech(eta x) exp(i eta^2 t/2),
mu = -eta^2/2,
omega_phase = eta^2/2,
E = -eta^3/(3g),
R_rms = pi/(2 sqrt(3) eta).
```

M9.4--M9.5 verify localization, perturbation stability under the declared finite
test, exact scaling, and the identities

```text
omega_phase R_rms^2 = pi^2/24,
E/(mu N) = 1/3.
```

M9.6 establishes the scalar carrier boundary:

- global `U(1)` norm exists;
- no local gauge connection or electric-charge sector exists;
- intrinsic rotations are scalar, not spinorial;
- the profile contracts continuously to the zero vacuum and has no declared
  protected winding sector.

## 4. Spinor replacement carrier

M9.7a selects the bounded prerequisite equation

```text
i d_t Psi = -i alpha d_x Psi
            + beta (m - lambda bar(Psi)Psi) Psi,
alpha = -sigma_2,
beta = sigma_3,
m = 1,
lambda = 1.
```

The accepted solitary wave has frequency

```text
omega = 0.8,
kappa = sqrt(m^2 - omega^2) = 0.6,
Psi(x,t) = Phi_omega(x) exp(-i omega t),
Phi_omega = (v,u)^T,
```

with

```text
D(x) = m + omega cosh(2 kappa x),
v(x) = sqrt(2(m-omega)/lambda)
       (m+omega) cosh(kappa x) / D(x),
u(x) = sqrt(2(m+omega)/lambda)
       (m-omega) sinh(kappa x) / D(x).
```

The upper component is even and the lower component is odd. The analytic
stationary residual closes at `1.96e-16` relative.

### 4.1 Numerical evolution

The implementation uses periodic Fourier differentiation and second-order Strang
splitting:

- exact kinetic Dirac step in Fourier space;
- exact pointwise nonlinear mass step;
- refinement `N = 512, 1024, 2048` on `[-30,30)`;
- `dt = 0.05 dx`, final time `t=2`.

Both spinor and density errors converge at approximately second order. At the
finest level:

```text
phase-aligned spinor L2 = 1.53398e-7,
density relative L1 = 8.72859e-8,
fidelity = 0.9999999999999846,
norm drift = 1.69198e-13,
model-energy drift = 1.03695e-13.
```

### 4.2 Localization decision

The exact nonlinear spinor remains localized and window independent. A fixed 2%
component-opposite modulation evolved to `t=10` retains

```text
core fraction = 0.999789865,
edge fraction = 3.13715e-11,
variance ratio = 1.01115,
fidelity = 0.99994829.
```

The identical initial spinor under the free massive-Dirac equation reaches

```text
variance ratio = 4.27772,
peak ratio = 0.40838.
```

Thus localization is supplied by the selected nonlinear spinor model rather than
the initial profile alone.

### 4.3 Local gauge interface

M9.7a implements the background-covariant transformation

```text
Psi' = exp(i q chi) Psi,
A_x' = A_x + d_x chi,
(-i d_x - q A_x) Psi -> exp(i q chi)(-i d_x - q A_x)Psi.
```

For the frozen periodic pure gauge, density, norm, and covariant model energy are
invariant to binary64 precision. This is an interface test only. `A_mu` is not a
dynamical field, there is no Maxwell energy, and `q=1` is not an electric-charge
calibration.

### 4.4 Spin status

The carrier is a two-component Dirac spinor in 1+1 dimensions. This supplies a
non-scalar representation and component structure. It does not yet establish a
3D spin angular-momentum observable, fermionic anticommutation/statistics, or an
electron identity.

## 5. Real and imaginary action sectors

- the scalar and Soler interactions are explicit real-Hamiltonian model choices;
- neither interaction is derived from the pinned CAT/EPT imaginary-action layer;
- `S_I` and `|W|` remain formal weighting observables;
- no local imaginary potential or irreversible back-reaction is inferred.

## 6. Evidential status

Established:

- source-pinned CAT/EPT algebraic interfaces;
- convergent scalar and spinor control/evolution solvers;
- one explicit coarse-graining information clock;
- localized neutral 1+1D scalar and spinor mathematical candidates;
- a background local-`U(1)` covariant spinor interface;
- preservation of the normalized-density clock under the spinor replacement.

Not established:

- three-dimensional spinor localization;
- a dynamical Maxwell or other gauge field;
- signed, calibrated electric charge or Gauss-law flux;
- fermionic quantization and statistics;
- electron, positron, photon, or other Standard Model identity;
- physical mass or absolute unit calibration;
- necessity of either selected nonlinear interaction;
- irreversible physical-time evolution from the imaginary action.

The next canonical gate is M9.7b: a bounded 3D spinor-plus-dynamical-gauge family
with localization, Gauss-law, convergence, boundary, and perturbation ledgers.
