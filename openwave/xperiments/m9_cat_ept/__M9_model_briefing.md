# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9 now contains a source-pinned CAT/EPT interface, verified
> scalar and spinor control models, a localized 1+1D nonlinear spinor, a coupled
> stationary 3D radial spinor--electrostatic branch, constrained spherical time
> evolution, and a bounded transverse Maxwell radiation sector with spinor-current
> back-reaction.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Formal source | `jagg-ix/entropic-physlib-private`, `entropic-physlib-linear-full@f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | Formal, scalar, spinor, electrostatic, radial-dynamic, and transverse-radiation modules plus M9.1--M9.7c research records |

## Accumulated model profile

| Attribute | M9 status |
| --- | --- |
| Scalar carrier | Exact neutral 1+1D bright-soliton family |
| 1+1D spinor carrier | Exact two-component Soler solitary wave |
| 3D stationary carrier | Normalized spherical Soler spinor with electrostatic back-reaction |
| Spherical dynamics | Finite-time weighted-unitary radial Dirac evolution with Poisson/Gauss projection |
| Transverse gauge sector | Planar `A_y,E_y,B_z` Maxwell mode with nonzero-capable Poynting flux |
| Transverse matter sector | Neutral charge-conjugate local spinor pair coupled through `J_y` |
| Dynamic Gauss result | Pointwise zero signed charge preserved without projection in M9.7c |
| Radiation result | Nonzero emitted Poynting energy and conductivity-absorber accounting |
| Entropic clock | Density-to-probability interfaces remain valid in scalar, spinor, and radial sectors |
| Electric charge | Dimensionless labels only; no physical calibration |
| Spin/statistics | Classical spinor representations only; no fermionic quantization |
| Particle identity | Electron, positron, photon, and Standard Model assignments remain unestablished |

## Key validated results

### Stationary radial branch

For

```text
m = epsilon0 = q = N = 1
lambda = 64
```

the normalized radial branch has

```text
omega = 0.9914633829359464
R_rms = 5.879232363303192.
```

### Constrained spherical dynamics

At `t=20`:

```text
fidelity = 0.9998920265
core fraction r<=16 = 0.9897530407
norm drift = 9.99e-15
total-energy relative drift = 8.15e-8.
```

### Transverse Maxwell milestone

The bounded M9.7c reduction uses

```text
A_t = -E
E_t = -A_xx - J - sigma E
B = A_x
J = q psi_+^dagger sigma_y psi_+
    - q psi_-^dagger sigma_y psi_-.
```

At the finest coupled refinement level:

```text
A order = 1.98383
E order = 1.95569
max signed charge density = 0
corrected-energy relative drift = 5.14e-7
emitted energy = 3.996e-5.
```

At `t=80`:

```text
emitted energy = 6.15138e-4
absorbed energy = 4.89886e-4
corrected-energy relative drift = 1.77811e-6.
```

## Implementation status

| Sector | Status |
| --- | --- |
| M9.1--M9.6 | Complete formal/scalar/clock/carrier program |
| M9.7a | Complete 1+1D nonlinear spinor qualification |
| M9.7b1 | Complete 3D electrostatic source-and-field qualification |
| M9.7b2 | Complete coupled stationary radial spinor solve |
| M9.7b3 | Complete constrained spherical time evolution |
| M9.7c1 | Complete vacuum transverse Maxwell benchmark |
| M9.7c2 | Complete neutral spinor-current back-reaction gate |
| M9.7c3 | Complete Poynting, absorber, and emitted-energy gate |
| M9.8 | Next: research instrumentation and launcher |

## Claim boundary

M9.7c is a bounded planar transverse reduction. It does not contain spatial
transport of the spinor envelope and is not a full non-spherical Maxwell--Dirac
solution. Physical units, charge calibration, particle identity, magnetic moment,
fermionic statistics, and CAT/EPT derivation of the selected interactions remain
open.

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). The next implementation
milestone is M9.8: common instrumentation, deterministic launcher controls, and
visualization for the already validated scalar, radial, and transverse sectors.
