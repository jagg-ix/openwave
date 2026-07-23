# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9 contains source-pinned CAT/EPT density and information
> interfaces, validated scalar and spinor controls, a coupled spherical
> spinor--electrostatic branch, constrained radial dynamics, transverse radiation,
> shared instrumentation, and bounded one- and two-dimensional Maxwell--Dirac
> transport.

## Model status

| Sector | Current result |
| --- | --- |
| Scalar | Exact neutral 1+1D bright-soliton family and scaling ledger |
| 1+1D spinor | Exact two-component Soler solitary wave |
| Spherical 3D | Normalized stationary Soler spinor with electrostatic back-reaction |
| Radial dynamics | Finite-time localization with longitudinal Gauss projection |
| Transverse radiation | Nonzero Poynting flux and absorber-energy accounting |
| M9.9 transport | Opposite-charge packets transported in one spatial coordinate |
| M9.10 transport | Opposite-charge packets transported in two spatial coordinates |
| Instrumentation | Deterministic presets, common panels, JSON/PNG export, launcher |
| Physical identity | No calibrated electron, positron, photon, or Standard Model assignment |

## M9.10 result

The selected 2+1D temporal-gauge model evolves

```text
i psi_s,t = [sigma_x(-i d_x-s q A_x)
             + sigma_y(-i d_y-s q A_y)
             + m sigma_z] psi_s.
```

Its Maxwell sector contains `E_x`, `E_y`, and
`B_z=d_x A_y-d_y A_x`. The conductivity absorber carries an induced-charge ledger
so Gauss continuity remains explicit.

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

All nine M9.10 gates pass, including refinement and domain-shape robustness.

## Claim boundary

M9.10 establishes a bounded classical 2+1D transport calculation. It does not
establish a stable localized charged particle, full 3D Maxwell--Dirac dynamics,
physical units, charge calibration, fermionic quantization, Standard Model
identity, or a unique CAT/EPT derivation of the selected equations.

The next target is M9.11: a bounded nonlinear localization and radiative-stability
decision gate with an explicit negative result if no member survives.
