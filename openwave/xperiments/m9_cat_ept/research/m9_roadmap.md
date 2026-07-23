# M9 CAT/EPT roadmap

Research mode remains headless. No `_launcher.py` is added until a validated
three-dimensional dynamics exists.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract and conformance suite | DONE |
| M9.2 | Free complex-field solver and exact Gaussian benchmark | DONE |
| M9.3 | Fixed field-to-probability map and coarse-graining clocks | DONE |
| M9.4 | Bounded scalar nonlinear family and localization decision gate | DONE |
| M9.5 | Exact scalar energy, radius, phase-frequency, and scaling ledger | DONE |
| M9.6 | Scalar charge/spin/topology audit and replacement-carrier contract | DONE |
| M9.7a | Bounded 1+1D nonlinear Dirac/Soler spinor qualification | DONE; all gates passed |
| M9.7b | Three-dimensional spinor localization with dynamical gauge sector | NEXT |
| M9.8 | Taichi port, shared instrumentation, and launcher | Gated on M9.7b |

## Completed scalar program: M9.1--M9.6

The scalar program establishes:

- a source-pinned formal CAT/EPT interface;
- a convergent free Gaussian control solver;
- one explicit coarse-graining information clock;
- a stable, exact, neutral 1+1D scalar soliton family;
- exact dimensionless radius, energy, and phase-frequency scaling;
- an executable boundary showing that the scalar carrier does not itself derive
  electric charge, spin-1/2, or protected topology.

The scalar result remains a mathematical particle candidate, not a Standard Model
identification.

## M9.7a bounded spinor prerequisite

The selected replacement carrier is the 1+1D cubic Soler equation

```text
i d_t Psi = -i alpha d_x Psi + beta (m - lambda bar(Psi)Psi) Psi
alpha = -sigma_2
beta = sigma_3
m = 1
lambda = 1
omega = 0.8.
```

The exact two-component solitary wave passes:

- analytic stationary-equation closure;
- approximately second-order spinor and density convergence;
- norm and model-energy conservation;
- fixed-window independence;
- a fixed 2% perturbation through `t = 10`;
- discrimination from the free massive-Dirac control;
- a periodic pure-gauge covariance check;
- the existing normalized-density entropic-clock map.

At `N = 2048`, the phase-aligned spinor error is `1.53e-7`, the density
relative-L1 error is `8.73e-8`, fidelity is `0.99999999999998`, norm drift is
`1.69e-13`, and model-energy drift is `1.04e-13`.

The fixed perturbation retains core fraction `0.99978987`, edge fraction
`3.14e-11`, and fidelity `0.99994829`. The identical initial spinor under the
free Dirac control reaches variance ratio `4.27772` and peak ratio `0.40838`.

The background pure-gauge check closes density, norm, and covariant energy to
binary64 precision. This is a local-`U(1)` interface, not a dynamical Maxwell
field or an electric-charge calibration.

See [`findings/m9_7a_method_note.md`](findings/m9_7a_method_note.md) and
[`data/m9_7a_spinor_carrier_result.json`](data/m9_7a_spinor_carrier_result.json).

## Next gate: M9.7b

The next target must move the non-scalar carrier to three spatial dimensions and
freeze the full coupled model before inspection. It must include:

1. a 3D Dirac/Weyl carrier and explicit representation conventions;
2. a dynamical gauge field rather than a background pure gauge;
3. a localized stationary or periodic state;
4. norm, energy, Gauss-law, and boundary-flux ledgers;
5. resolution and window convergence;
6. perturbation stability;
7. preservation of the CAT/EPT density and coarse-graining interfaces;
8. an honest negative if no state survives the bounded family.

No renderer, electron claim, or phenomenology-column promotion is justified before
that gate passes.
