# M9 CAT/EPT roadmap

M9 is complete through a bounded two-dimensional localization and radiative
stability decision. The decision gate passes, but no stable two-dimensional
particle candidate is accepted.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1--M9.8 | Formal, scalar, spinor, gauge, radiation, and instrumentation program | DONE |
| M9.9 | Spatially transported planar Maxwell--Dirac qualification | DONE |
| M9.10 | Two-dimensional transported Maxwell--Dirac qualification | DONE |
| M9.11 | Two-dimensional localization/radiative-stability decision | DONE; negative particle decision |
| M9.12 | Three-dimensional transported Maxwell--Dirac program | NEXT |

## Accumulated transport program

M9.9 establishes one-dimensional spatial Dirac transport with longitudinal and
transverse gauge fields. M9.10 extends the reduction to two transported spatial
coordinates with `E_x`, `E_y`, magnetic curl, non-axis-aligned motion, Poynting
transport, conductivity absorption, induced absorber charge, refinement, and
domain-shape studies.

M9.10 key result:

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

## M9.11 localization decision

The bounded nonlinear family is

```text
lambda in {0,2,4,8}
M_s = m - lambda psi_s^dagger sigma_z psi_s.
```

At `t=8`, increasing the selected coupling reduces spreading:

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

The same strongest member fails the `t=12` long-time gate:

```text
maximum RMS ratio = 1.73615505
minimum peak ratio = 0.67364906
minimum core fraction = 0.92050318.
```

Decision:

> `lambda=8` is a finite-time reduced-spreading candidate, but it fails the
> long-time localization gate; no stable two-dimensional particle candidate is
> accepted.

All nine decision-procedure gates pass, including norm, corrected energy, final
Gauss, radiation, perturbation, and explicit particle-rejection checks.

## Next gate: M9.12

M9.12 must treat three-dimensional transport as a new research program rather than
an automatic particle promotion. It must define a bounded 3D representation,
Maxwell constraints, magnetic curl, boundary/energy ledgers, refinement controls,
and an honest localization or dispersal decision before any physical calibration.
