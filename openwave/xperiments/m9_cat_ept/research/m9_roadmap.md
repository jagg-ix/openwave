# M9 CAT/EPT roadmap

M9 is complete through bounded two-dimensional transported Maxwell--Dirac
dynamics. All sectors remain selected dimensionless field models rather than
physical particle identifications.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1--M9.6 | Formal, scalar, clock, scaling, and carrier audit | DONE |
| M9.7a | Bounded 1+1D nonlinear Dirac/Soler qualification | DONE |
| M9.7b1--M9.7b3 | Spherical electrostatic stationary and dynamic program | DONE |
| M9.7c | Bounded transverse Maxwell--spinor radiation | DONE |
| M9.8 | Shared instrumentation, launcher, and renderer | DONE |
| M9.9 | Spatially transported planar Maxwell--Dirac qualification | DONE |
| M9.10 | Two-dimensional transported Maxwell--Dirac qualification | DONE; all gates passed |
| M9.11 | Two-dimensional localization and radiative-stability decision | NEXT |

## Accumulated program

M9.1--M9.8 establish the pinned CAT/EPT density/information interfaces, validated
scalar and spinor controls, a spherical stationary spinor branch, constrained
radial dynamics, bounded transverse radiation, and shared claim-aware
instrumentation.

M9.9 adds one-dimensional spatial Dirac transport with longitudinal and transverse
gauge fields. The opposite-charge packets cross while norm, energy, net charge,
final Gauss, magnetic, and emitted-energy ledgers remain within their frozen gates.

## M9.10 two-dimensional transport

The bounded 2+1D reduction is

```text
i psi_s,t = [sigma_x(-i d_x-s q A_x)
             + sigma_y(-i d_y-s q A_y)
             + m sigma_z] psi_s
s in {+1,-1}

A_x,t = -E_x
A_y,t = -E_y
E_x,t = d_y B_z - J_x - sigma E_x
E_y,t = -d_x B_z - J_y - sigma E_y
B_z = d_x A_y - d_y A_x.
```

The absorber-induced charge obeys `rho_abs,t=-div(sigma E)`, allowing the Gauss
ledger to include matter plus absorber charge without a projection step.

Frozen inputs:

```text
m = 1
q = 0.20
packet width = 2.2
centers = (-5,-2), (5,2)
momenta = (0.95,0.35), (-0.95,-0.2275)
gauge seed amplitude = 0.006.
```

Scored results:

```text
transported-spinor order = 8.18686
long-run norm drift = 5.73621e-9
corrected-energy drift = 6.53843e-9
final Gauss residual = 1.49202e-8 absolute, 1.71900e-5 relative
max net charge = 5.51630e-11
packet separation = 10.77033 -> 1.03495
transport angle = 0.38051 -> 1.34895
emitted energy = 1.12278e-5
absorbed energy = 4.42916e-5
max magnetic field = 0.00770611.
```

The domain-shape study gives relative spreads `2.49e-5` for final separation and
`0.03147` for emitted energy.

The high smooth-benchmark order is not claimed as universal accuracy. M9.10
establishes bounded 2D transport, not stable localization or particle identity.

## Next gate: M9.11

M9.11 must run a bounded two-dimensional nonlinear-coupling survey and decide
whether any member remains localized under fixed perturbation and a longer
radiative horizon. It must return an explicit negative if no member survives.
