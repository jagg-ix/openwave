# M9.7b1 task: 3D electrostatic Maxwell qualification

## Question

Can the M9 spinor-density interface source a self-consistent three-dimensional
electrostatic gauge field with closed Gauss-law, flux, energy, convergence, and
entropic-clock ledgers before attempting the coupled 3D Dirac equation?

This is a bounded subgate of M9.7b. It is not the full 3D Dirac--Maxwell solve.

## Frozen spherical spinor-density ansatz

The regular test carrier has an upper s-wave radial amplitude and a lower p-wave
amplitude that vanishes at the origin:

```text
F(r) = A exp(-r/a)
G(r) = A eta (r/a) exp(-r/a)
rho(r) = F(r)^2 + G(r)^2.
```

Frozen parameters:

```text
a = 1
eta = 1/2
q = +/-1
epsilon0 = 1.
```

`A` is fixed by `4 pi integral r^2 rho dr = 1`. The ansatz is a regular density
carrier and source, not a solution of the 3D Dirac stationary equation.

## Frozen Maxwell sector

The radial finite-volume solver enforces

```text
Q(r) = 4 pi integral_0^r s^2 q rho(s) ds
E(r) = Q(r)/(4 pi epsilon0 r^2)
phi(infinity) = 0.
```

The field energy includes the numerical interior and the exact exterior Coulomb
tail:

```text
U_E = epsilon0/2 integral_0^R 4 pi r^2 E(r)^2 dr
      + Q(R)^2/(8 pi epsilon0 R).
```

The independent source ledger is `1/2 integral rho_q phi d^3x`.

## Exact references

For the frozen ansatz:

```text
raw norm = pi a^3 (1 + 3 eta^2)
phi(0) = q (2 + 3 eta^2)/(8 pi epsilon0 a (1 + 3 eta^2))
U_E = q^2/(8 pi epsilon0 a)
      * (837 eta^4 + 672 eta^2 + 160)
      / (256 (1 + 3 eta^2)^2).
```

## Frozen numerical gates

- refinement: 256, 512, and 1024 shells on `0 <= r <= 16`;
- window study: `R = 12,16,20` at fixed `dr = 1/32`;
- signed sectors: `q=+1` and `q=-1`;
- fixed 2% opposite modulation of upper and lower radial components;
- shell probability `p_i = rho_i Delta V_i`;
- reflecting doubly-stochastic radial channel with 64 depths.

## Acceptance

- Gauss shell residual and boundary-flux error `<= 1e-13`;
- number norm error `<= 1e-13`;
- energy and central-potential convergence order `>= 1.8`;
- finest field-energy relative error `<= 3e-5`;
- finest central-potential relative error `<= 5e-5`;
- source/field energy difference `<= 5e-6` relative to the exact energy;
- core fraction inside `r <= 8a` at least `0.999`;
- outer-20% fraction at most `1e-6`;
- fixed-spacing window spreads at most `1e-5`;
- charge reversal flips `E` and `phi`, preserves density and field energy;
- the 2% source perturbation stays inside the frozen field and localization bands;
- both radial information trajectories contract remaining KL and close the ledger.

## Scope boundary

Passing M9.7b1 establishes a 3D spherical spinor-density source and a
self-consistent electrostatic Maxwell constraint. It does not establish a coupled
3D Dirac stationary solution, Maxwell wave evolution, magnetic fields, dynamical
3D localization, calibrated electric charge, or an electron identity.
