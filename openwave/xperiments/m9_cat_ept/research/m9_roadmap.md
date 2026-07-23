# M9 CAT/EPT roadmap

The scientific core is complete through a bounded transverse-radiation gate.
Interactive work remains separate from physical-identification claims.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract and conformance suite | DONE |
| M9.2 | Free complex-field solver and exact Gaussian benchmark | DONE |
| M9.3 | Fixed probability map and coarse-graining clocks | DONE |
| M9.4 | Bounded scalar localization decision gate | DONE |
| M9.5 | Exact scalar scaling and observable ledger | DONE |
| M9.6 | Scalar charge/spin/topology audit | DONE |
| M9.7a | Bounded 1+1D nonlinear Dirac/Soler qualification | DONE |
| M9.7b1 | 3D spherical density and electrostatic Maxwell constraint | DONE |
| M9.7b2 | Coupled stationary radial Dirac--electrostatic solve | DONE |
| M9.7b3 | Time-dependent constrained spherical spinor--gauge evolution | DONE |
| M9.7c1 | Vacuum transverse Maxwell propagation benchmark | DONE |
| M9.7c2 | Neutral spinor-current back-reaction and dynamic Gauss | DONE |
| M9.7c3 | Poynting, absorber, and emitted-energy accounting | DONE |
| M9.7c | Bounded transverse Maxwell--spinor qualification | DONE; all gates passed |
| M9.8 | Shared instrumentation, launcher, and renderer | NEXT |

## Accumulated completed program

### M9.1--M9.6

The first six milestones establish:

- a source-pinned CAT/EPT algebraic interface;
- a convergent free complex-field control solver;
- one explicit coarse-graining information clock;
- an exact neutral scalar soliton family;
- exact energy, radius, phase-frequency, and norm scaling;
- an executable boundary showing that the scalar carrier does not supply electric
  charge, spin-1/2, or protected topology.

### M9.7a

The scalar is replaced by an exact two-component 1+1D Soler carrier. It passes
stationary-profile, convergence, conservation, window, finite perturbation,
free-control, background-gauge, and information-interface gates.

### M9.7b1--M9.7b3

The spherical 3D program adds:

```text
Q' = 4 pi r^2 q rho
phi' = -Q/(4 pi epsilon0 r^2)
```

and then solves the coupled stationary radial spinor equations

```text
v' = -(omega - q phi + M) u
u' + 2u/r = (omega - q phi - M) v
M = m - lambda(v^2-u^2).
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

The branch passes stationary residual, energy, Gauss, flux, convergence, window,
signed-sector, and radial-information ledgers.

The time-dependent spherical solver then passes second-order refinement, norm and
energy conservation, dynamical Gauss projection, finite perturbation, window,
and long-time localization gates through `t=20`.

Its radiation result is negative by symmetry:

```text
B = 0
E cross B = 0.
```

### M9.7c1: vacuum transverse Maxwell benchmark

The first transverse milestone evolves

```text
A_t = -E
E_t = -A_xx
B = A_x.
```

A right-moving analytic pulse yields observed orders

```text
A: 1.99907, 1.99989
E: 1.99347, 1.99859.
```

### M9.7c2: neutral spinor-current coupling

The bounded matter sector is

```text
i psi_s,t = [m sigma_z - s q A sigma_y] psi_s
s in {+1,-1}
J = q psi_+^dagger sigma_y psi_+
    - q psi_-^dagger sigma_y psi_-.
```

The pair has equal pointwise density and opposite charge labels, so

```text
rho_q = q(|psi_+|^2-|psi_-|^2) = 0.
```

No Gauss projection is used. Exact charge cancellation and pair norm are
preserved by the symmetric evolution.

At the finest coupled refinement level:

```text
A order = 1.98383
E order = 1.95569
corrected-energy relative drift = 5.14e-7
emitted energy = 3.996e-5
central field-energy fraction = 0.09896.
```

### M9.7c3: absorber and radiation ledger

The transverse equation includes conductivity damping

```text
E_t = -A_xx - J - sigma(x) E.
```

The energy balance is

```text
E_matter + E_field + E_absorbed = constant.
```

At `t=80`:

```text
emitted energy = 6.15138e-4
absorbed energy = 4.89886e-4
corrected-energy relative drift = 1.77811e-6.
```

The three-window absorber study gives

```text
emitted-energy relative spread = 0.0042613
maximum corrected-energy drift = 1.443e-6.
```

## M9.7c decision

M9.7c passes as a bounded transverse Maxwell radiation qualification. It
establishes a nonzero-capable Poynting flux, electric/magnetic field energy,
two-way local spinor-current exchange, dynamic zero-charge Gauss closure,
absorbing boundaries, emitted-energy accounting, and convergence.

It does not establish a full spatial Maxwell--Dirac equation, a charged localized
particle, non-spherical orbital stability, calibrated charge, or particle identity.

## Next gate: M9.8

M9.8 may now add research instrumentation without promoting M9 to a calibrated
particle model. It should provide:

1. a shared launcher for scalar, radial, and transverse studies;
2. deterministic parameter presets matching committed ledgers;
3. common energy, norm, Gauss, Poynting, and information panels;
4. headless export and interactive modes;
5. explicit claim-boundary labels in the UI;
6. no default electron or Standard Model naming;
7. regression checks that rendered metrics match the headless solvers.

A future full spatial Maxwell--Dirac program remains a separate research extension.
