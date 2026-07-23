# M9 CAT/EPT roadmap

Research mode remains headless. No `_launcher.py` is added until a coupled
three-dimensional carrier passes its localization and gauge ledgers.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract and conformance suite | DONE |
| M9.2 | Free complex-field solver and exact Gaussian benchmark | DONE |
| M9.3 | Fixed field-to-probability map and coarse-graining clocks | DONE |
| M9.4 | Bounded scalar nonlinear family and localization decision gate | DONE |
| M9.5 | Exact scalar energy, radius, phase-frequency, and scaling ledger | DONE |
| M9.6 | Scalar charge/spin/topology audit and replacement-carrier contract | DONE |
| M9.7a | Bounded 1+1D nonlinear Dirac/Soler spinor qualification | DONE |
| M9.7b1 | 3D spherical spinor-density and electrostatic Maxwell constraint | DONE; all gauge-sector gates passed |
| M9.7b2 | Coupled 3D stationary Dirac--electrostatic solve | NEXT |
| M9.7b3 | Time-dependent Maxwell/spinor perturbation evolution | Gated on M9.7b2 |
| M9.8 | Taichi port, shared instrumentation, and launcher | Gated on M9.7b3 |

## Completed scalar program: M9.1--M9.6

The scalar program establishes a source-pinned CAT/EPT interface, a convergent
free control, one explicit coarse-graining information clock, one exact neutral
1+1D scalar soliton family, and an executable boundary showing that the scalar
carrier does not itself derive electric charge, spin-1/2, or protected topology.

## M9.7a bounded spinor prerequisite

The selected 1+1D Soler carrier passes exact-profile, convergence, conservation,
window, perturbation, free-control, background-gauge, and entropic-clock gates.
It establishes a localized spinor carrier and local-`U(1)` interface, but no
three-dimensional state or dynamical Maxwell field.

See [`findings/m9_7a_method_note.md`](findings/m9_7a_method_note.md).

## M9.7b1 electrostatic Maxwell qualification

The frozen regular spherical spinor-density ansatz is

```text
F(r) = A exp(-r/a)
G(r) = A eta (r/a) exp(-r/a)
a = 1, eta = 1/2.
```

It sources the self-consistent electrostatic constraint

```text
Q(r) = 4 pi integral_0^r s^2 q rho(s) ds
E(r) = Q(r)/(4 pi epsilon0 r^2).
```

The finite-volume implementation passes:

- shellwise Gauss law and signed boundary flux;
- second-order field-energy and central-potential convergence;
- independent field/source energy agreement;
- fixed-spacing window independence;
- dimensionless `q=+1` and `q=-1` sectors;
- a fixed 2% source perturbation response;
- a reflecting radial KL/coarse-graining ledger.

At 1024 shells the Gauss residual is `4.01e-16`, the boundary-flux error is
`1.11e-16`, the field-energy relative error is `2.19e-5`, and the central-potential
relative error is `4.20e-5`.

See [`findings/m9_7b1_method_note.md`](findings/m9_7b1_method_note.md) and
[`data/m9_7b1_electrostatic_gauge_result.json`](data/m9_7b1_electrostatic_gauge_result.json).

## Next gate: M9.7b2

M9.7b2 must freeze and solve a coupled spherical stationary system in which the
spinor profile and electrostatic potential determine one another. It must include:

1. explicit 3D Dirac representation and radial conventions;
2. bounded Soler/Maxwell coupling and frequency range fixed before inspection;
3. stationary residuals for both spinor and electrostatic equations;
4. norm, total energy, Gauss-law, and boundary-flux ledgers;
5. resolution and window convergence;
6. a discriminating uncoupled or no-binding control;
7. finite-time perturbation evolution only after stationary closure;
8. preservation of the CAT/EPT density and radial coarse-graining interfaces;
9. an honest negative if no solution survives the bounded family.

M9.7b1 does not justify a renderer, electron identity, or phenomenology-column
promotion because its spinor density is a frozen source ansatz rather than a
coupled stationary solution.
