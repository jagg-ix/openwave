# M9.9 task: spatially transported planar Maxwell--Dirac qualification

## Question

Can the bounded transverse M9.7c matter sector be extended from pointwise spinor
rotation to spatial Dirac transport while retaining norm, energy, charge,
longitudinal Gauss, transverse-field, and radiation ledgers?

## Frozen reduction

Two 1+1D Dirac packets carry opposite dimensionless charge labels:

```text
i psi_s,t = [sigma_x(-i d_x - s q A_x)
             + m sigma_z - s q A_y sigma_y] psi_s
s in {+1,-1}.
```

The Maxwell sector is

```text
A_x,t = -E_x
E_x,t = -J_x
A_y,t = -E_y
E_y,t = -A_y,xx - J_y - sigma(x) E_y.
```

Charge and current are

```text
rho = q(|psi_+|^2-|psi_-|^2)
J_i = q psi_+^dagger sigma_i psi_+
      - q psi_-^dagger sigma_i psi_-.
```

The initial longitudinal electric field is obtained by inverting the same centered
finite-difference symbol used by the evolution and Gauss diagnostic.

## Frozen parameters

```text
m = 1
q = 0.25
packet width = 2.5
packet centers = -8, +8
packet momenta = +0.9, -0.9
transverse seed amplitude = 0.008
transverse seed width = 4.
```

The total matter norm is one. The pair is net neutral but not pointwise neutral.

## Numerical method

- periodic centered second-order derivatives;
- fourth-order Runge--Kutta method of lines;
- conductivity absorber on the transverse electric field;
- longitudinal Gauss evolution through Ampere current, with no projection;
- matter, longitudinal-field, transverse-field, absorber, and Poynting ledgers.

## Scored runs

- refinement: points `{128,256,512}`, `t=6`, `dt=0.08 dx`;
- transported interaction: 512 points, `t=14`;
- packet center motion is measured independently for both species.

## Acceptance

- transported-spinor self-convergence order at least `1.6`;
- maximum norm drift at most `2e-8`;
- maximum corrected-energy relative drift at most `2e-6`;
- final Gauss residual at most `0.05` relative and `4e-4` absolute;
- maximum net charge at most `1e-10`;
- final packet separation below 75% of the initial separation;
- final transverse field at least `1e-4`;
- emitted Poynting energy at least `1e-7`.

## Scope boundary

Passing M9.9 establishes a bounded transported planar Maxwell--Dirac reduction.
It does not establish a stable localized charged particle, a full 2D/3D
Maxwell--Dirac solution, calibrated units, fermionic quantization, or an electron
identity.
