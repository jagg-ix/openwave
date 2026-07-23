# M9 CAT/EPT roadmap

Research mode remains headless. No `_launcher.py` is added until the coupled
three-dimensional carrier also passes a time-dependent gauge-evolution gate.

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
| M9.7b2 | Coupled stationary radial Dirac--electrostatic solve | DONE; all stationary gates passed |
| M9.7b3 | Time-dependent Maxwell/spinor perturbation evolution | NEXT |
| M9.8 | Taichi port, shared instrumentation, and launcher | Gated on M9.7b3 |

## Completed scalar and 1+1D program

M9.1--M9.6 establish the source-pinned CAT/EPT interface, free control,
coarse-graining information clock, exact neutral scalar family, scaling ledger,
and the current scalar carrier's charge/spin/topology boundary.

M9.7a replaces the scalar with an exact two-component 1+1D Soler carrier. It
passes stationary-profile, convergence, conservation, window, finite
perturbation, free-control, background-gauge, and clock-interface gates.

## M9.7b1 electrostatic Maxwell qualification

M9.7b1 freezes a regular spherical spinor-density source and validates the
self-consistent electrostatic constraint

```text
Q'(r) = 4 pi r^2 q rho(r)
phi'(r) = -Q(r)/(4 pi epsilon0 r^2).
```

It closes shellwise Gauss law, signed boundary flux, Coulomb-tail field energy,
source/field energy agreement, resolution and window convergence, signed source
sectors, static source response, and the reflecting radial information ledger.
The spinor density in that task is an ansatz rather than a Dirac solution.

## M9.7b2 coupled stationary solution

The completed coupled model is

```text
v' = -(omega - q phi + M) u
u' + 2u/r = (omega - q phi - M) v
M = m - lambda(v^2-u^2)
Q' = 4 pi r^2 q(v^2+u^2)
phi' = -Q/(4 pi epsilon0 r^2).
```

The scored dimensionless inputs are

```text
m = epsilon0 = q = N = 1
lambda = 64.
```

The norm constraint excludes the zero solution. Charge continuation through
`q={0,1/4,1/2,3/4,1}` produces

```text
omega = 0.9914633829359464
v(0) = 0.07365091100207258
phi(0) = 0.024408951727442642
R_rms = 5.879232363303192.
```

The branch passes:

- near-fourth-order spinor, density, and frequency convergence;
- an independent stationary Dirac residual;
- unit norm and signed-charge closure;
- Gauss-law, potential, and boundary-flux residuals;
- field/source energy and stationary eigenvalue identities;
- fixed-spacing `R={30,40,50}` window convergence;
- localized core and tail gates;
- return to the same BVP branch from a fixed 5% initial-guess modulation;
- algebraic `q=+1` and `q=-1` source sectors;
- the reflecting radial CAT/EPT information ledger.

The 5% modulation checks the nonlinear solver basin, not time-dependent
stability. The non-scoring exploratory phase selected `lambda=64` and the solver
tolerances, so the result is not presented as blind preregistration or a coupling
prediction.

See [`findings/m9_7b2_method_note.md`](findings/m9_7b2_method_note.md) and
[`data/m9_7b2_dirac_electrostatic_result.json`](data/m9_7b2_dirac_electrostatic_result.json).

## Next gate: M9.7b3

M9.7b3 must start from the converged M9.7b2 branch and implement time-dependent
spinor plus gauge evolution. Before any renderer or particle identity it must
close:

1. norm and total-energy conservation;
2. the dynamical Gauss constraint;
3. outgoing boundary flux and electromagnetic energy accounting;
4. resolution and window convergence;
5. fixed spinor and gauge perturbations;
6. long-time localization or an honest dispersal/instability result;
7. preservation of the CAT/EPT density and information interfaces.

M9.7b2 does not establish magnetic fields, Maxwell radiation, orbital stability,
fermionic quantization, calibrated charge, or an electron identity.
