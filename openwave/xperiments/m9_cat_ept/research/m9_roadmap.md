# M9 CAT/EPT roadmap

Research mode remains headless. No `_launcher.py` is added until a non-spherical
radiative gauge sector passes its own evolution and boundary-flux gates.

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
| M9.7b3 | Time-dependent constrained spherical spinor--gauge evolution | DONE; all bounded gates passed |
| M9.7c | Non-spherical transverse Maxwell/spinor evolution | NEXT |
| M9.8 | Taichi port, shared instrumentation, and launcher | Gated on M9.7c |

## Completed scalar and 1+1D program

M9.1--M9.6 establish the source-pinned CAT/EPT interface, free control,
coarse-graining information clock, exact neutral scalar family, scaling ledger,
and the scalar carrier's charge/spin/topology boundary.

M9.7a replaces the scalar with an exact two-component 1+1D Soler carrier and
passes stationary-profile, convergence, conservation, window, finite
perturbation, free-control, background-gauge, and clock-interface gates.

## Completed stationary 3D program

M9.7b1 validates the spherical electrostatic Maxwell constraint, signed source
sectors, field/source energy agreement, Coulomb-tail accounting, radial window
convergence, and the reflecting information ledger for a regular spinor-density
source.

M9.7b2 removes the frozen profile by solving

```text
v' = -(omega - q phi + M) u
u' + 2u/r = (omega - q phi - M) v
M = m - lambda(v^2-u^2)
Q' = 4 pi r^2 q(v^2+u^2)
phi' = -Q/(4 pi epsilon0 r^2)
```

with

```text
m = epsilon0 = q = N = 1
lambda = 64.
```

The normalized branch has

```text
omega = 0.9914633829359464
v(0) = 0.07365091100207258
phi(0) = 0.024408951727442642
R_rms = 5.879232363303192.
```

It passes near-fourth-order branch convergence, independent Dirac and Maxwell
residuals, field/source energy closure, window convergence, signed sectors, and
the radial CAT/EPT information ledger. The exploratory phase selected
`lambda=64`; it is not a coupling prediction.

## M9.7b3 constrained spherical dynamics

The completed time-dependent equations are

```text
i V_t = (d_r + 2/r) U + (q phi + M) V
i U_t = -d_r V + (q phi - M) U
M = m - lambda(|V|^2-|U|^2)
Q(r,t) = 4 pi integral_0^r s^2 q rho(s,t) ds
E(r,t) = Q(r,t)/(4 pi epsilon0 r^2).
```

The numerical method uses exact shell-volume weights, a weighted-adjoint radial
Dirac pair, weighted-unitary kinetic Crank--Nicolson, exact local phase steps, and
a Poisson/Gauss projection after each local half-step.

The frozen perturbation is

```text
V -> (1 + 0.02 cos(pi r/R)) exp(+i chi) V
U -> (1 - 0.02 cos(pi r/R)) exp(-i chi) U
chi = 0.02 sin(pi r/R).
```

### Dynamic refinement

At `R=40`, `t=5`, and `cells={256,512,1024}`:

```text
spinor self-convergence order = 1.92688667
density self-convergence order = 2.09471979
max norm drift = 6.22e-15
max total-energy relative drift = 3.26e-7
max projected Gauss residual = 3.90e-14.
```

### Long-time perturbation

At 512 cells through `t=20`:

```text
fidelity = 0.9998920265
R_rms = 5.8887647996
core fraction r<=16 = 0.9897530407
outer-20% fraction = 7.22475e-5
max norm drift = 9.99e-15
max total-energy relative drift = 8.15e-8.
```

The `R={30,40,50}` dynamic window study closes with relative spreads

```text
RMS radius = 0.00524638
central potential = 0.00142295
core fraction = 0.000429055.
```

The final radial clock has accumulated gain `0.0260883856` and exact closure.

## Radiation result

The spherical electrostatic truncation has

```text
B = 0
S_Poynting = E x B = 0.
```

Its electromagnetic radiation-flux ledger is therefore exactly zero. This is a
symmetry-enforced negative result, not a full Maxwell-wave stability result. The
continuum-form matter boundary-current diagnostic remains below `5.5e-7`.

## Next gate: M9.7c

M9.7c must leave spherical electrostatics and include at least one transverse or
non-spherical gauge mode. Before any renderer or particle identity it must close:

1. hyperbolic Maxwell evolution with electric and magnetic energy;
2. dynamical Gauss constraints without an electrostatic projection shortcut;
3. nonzero-capable Poynting and radiation boundary flux;
4. norm and total-energy balance including emitted radiation;
5. resolution, window, and absorbing-boundary convergence;
6. fixed spinor and gauge perturbations;
7. long-time localization or an honest radiative/unstable result;
8. preservation of the CAT/EPT density and information interfaces.

M9.7b3 does not establish transverse radiation, magnetic self-fields,
non-spherical orbital stability, fermionic quantization, calibrated charge, or an
electron identity.
