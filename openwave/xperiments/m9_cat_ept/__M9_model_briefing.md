# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9 contains a source-pinned CAT/EPT interface, verified
> scalar and spinor controls, localized scalar and spinor candidates, a coupled
> spherical spinor--electrostatic branch, constrained radial dynamics, transverse
> Maxwell radiation, shared instrumentation, and a bounded spatially transported
> planar Maxwell--Dirac reduction.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Formal source | `jagg-ix/entropic-physlib-private`, `entropic-physlib-linear-full@f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| Instrumentation | Shared scalar, radial, transverse, and transported-planar presets with explicit claim boundaries |

## Accumulated model profile

| Attribute | M9 status |
| --- | --- |
| Scalar carrier | Exact neutral 1+1D bright-soliton family |
| 1+1D spinor carrier | Exact two-component Soler solitary wave |
| 3D stationary carrier | Normalized spherical Soler spinor with electrostatic back-reaction |
| Spherical dynamics | Finite-time radial Dirac evolution with longitudinal Gauss projection |
| Transverse radiation | Bounded planar `A_y,E_y,B_z` mode with nonzero Poynting flux and absorber accounting |
| Spatial transport | Opposite-charge 1+1D Dirac packets coupled to longitudinal and transverse gauge fields |
| Dynamic Gauss | Initial discrete closure and monitored evolution without projection in M9.9 |
| Electric charge | Dimensionless labels only; no physical calibration |
| Spin/statistics | Classical spinor representations only; no fermionic quantization |
| Particle identity | Electron, positron, photon, and Standard Model assignments remain unestablished |

## Key validated results

### Stationary and spherical dynamic branch

For the selected radial model

```text
m = epsilon0 = q = N = 1
lambda = 64
omega = 0.9914633829359464
R_rms = 5.879232363303192.
```

At `t=20`, fidelity is `0.9998920265`, norm drift is `9.99e-15`, and
relative total-energy drift is `8.15e-8`.

### Bounded transverse radiation

M9.7c reaches approximately second-order field convergence, nonzero emitted
Poynting energy, and corrected-energy closure with a conductivity absorber. At
`t=80`:

```text
emitted energy = 6.15138e-4
absorbed energy = 4.89886e-4
corrected-energy relative drift = 1.77811e-6.
```

### Spatially transported planar dynamics

M9.9 evolves

```text
i psi_s,t = [sigma_x(-i d_x - s q A_x)
             + m sigma_z - s q A_y sigma_y] psi_s
```

with longitudinal and transverse Maxwell equations. Results:

```text
transported-spinor order = 1.89918
long-run norm drift = 6.02e-10
corrected-energy drift = 1.073e-6
final Gauss residual = 2.754e-4 absolute, 0.02264 relative
max net charge = 1.04e-16
packet separation: 16 -> -2.21328
emitted energy = 2.84143e-5.
```

The packets cross. This is a transport result, not a localized-particle result.

## Implementation status

| Sector | Status |
| --- | --- |
| M9.1--M9.6 | Complete formal/scalar/clock/carrier program |
| M9.7a | Complete 1+1D nonlinear spinor qualification |
| M9.7b1--M9.7b3 | Complete spherical electrostatic stationary and dynamic program |
| M9.7c | Complete bounded transverse-radiation qualification |
| M9.8 | Complete shared instrumentation, renderer, and launcher |
| M9.9 | Complete transported planar Maxwell--Dirac qualification |
| M9.10 | Next: two-dimensional transported Maxwell--Dirac qualification |

## Claim boundary

M9.9 is a bounded 1+1D classical field reduction. It does not establish a stable
localized charged particle, full 2D/3D Maxwell--Dirac dynamics, calibrated units,
fermionic quantization, Standard Model identity, or unique CAT/EPT derivation of
the selected equations.
