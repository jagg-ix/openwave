# M9 CAT/EPT roadmap

M9 is complete through shared instrumentation and a bounded spatially transported
planar Maxwell--Dirac gate. Presentation remains separate from physical-identity
claims.

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
| M9.7b3 | Time-dependent constrained spherical spinor--gauge evolution | DONE |
| M9.7c | Bounded transverse Maxwell--spinor qualification | DONE |
| M9.8 | Shared instrumentation, launcher, and renderer | DONE |
| M9.9 | Spatially transported planar Maxwell--Dirac qualification | DONE; all gates passed |
| M9.10 | Two-dimensional transported Maxwell--Dirac qualification | NEXT |

## Accumulated program

### Formal, scalar, and information layers

M9.1--M9.6 establish the source-pinned CAT/EPT interface, free control,
coarse-graining information clock, exact neutral scalar family and scaling ledger,
and the scalar carrier's charge/spin/topology boundary.

### Spinor and spherical electrostatic layers

M9.7a validates an exact localized two-component 1+1D Soler carrier. M9.7b1--b3
add a spherical electrostatic Maxwell constraint, a normalized stationary radial
spinor branch, and finite-time constrained dynamics with norm, energy, Gauss,
window, perturbation, localization, and information ledgers.

### Transverse radiation

M9.7c introduces a bounded transverse mode

```text
A_t = -E
E_t = -A_xx - J - sigma(x) E
B = A_x
```

with nonzero Poynting flux, electric/magnetic energy, neutral spinor-current
back-reaction, absorber accounting, and refinement/window robustness.

### Instrumentation

M9.8 provides a shared preset registry, deterministic ledger/runner links, common
metric and claim-boundary panels, headless JSON/PNG export, an interactive
Matplotlib dashboard, and OpenWave launcher discovery. M9.9 adds a fourth
`transported-maxwell-dirac` preset.

### Transported planar Maxwell--Dirac gate

M9.9 evolves two opposite-charge spatial Dirac packets:

```text
i psi_s,t = [sigma_x(-i d_x - s q A_x)
             + m sigma_z - s q A_y sigma_y] psi_s
s in {+1,-1}
```

with

```text
A_x,t = -E_x
E_x,t = -J_x
A_y,t = -E_y
E_y,t = -A_y,xx - J_y - sigma(x) E_y.
```

Frozen inputs are

```text
m = 1
q = 0.25
packet centers = -8, +8
packet momenta = +0.9, -0.9
packet width = 2.5
transverse seed amplitude = 0.008.
```

Results:

```text
transported-spinor order = 1.89918
long-run max norm drift = 6.02e-10
long-run corrected-energy drift = 1.073e-6
final Gauss residual = 2.754e-4 absolute, 0.02264 relative
max net charge = 1.04e-16
initial packet separation = 16
final packet separation = -2.21328
emitted energy = 2.84143e-5
max transverse field = 0.0100947.
```

The packets cross. This establishes spatial transport and bounded gauge
back-reaction; it is not a stable localized-particle result.

## Next gate: M9.10

M9.10 must lift the transported reduction to two spatial dimensions and include:

1. two-dimensional Dirac transport;
2. both longitudinal and transverse gauge components;
3. two-dimensional charge continuity and Gauss closure;
4. magnetic curl and non-axis-aligned Poynting transport;
5. norm, energy, absorber, and emitted-energy balance;
6. refinement and domain-shape convergence;
7. localized packet collision or dispersal classification;
8. explicit CAT/EPT density and information projections.

M9.10 remains a bounded classical field-model target. Physical units, fermionic
quantization, Standard Model identity, and experimental calibration remain open.
