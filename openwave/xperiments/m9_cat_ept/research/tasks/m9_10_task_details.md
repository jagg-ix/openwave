# M9.10 task: two-dimensional transported Maxwell--Dirac qualification

## Goal

Lift M9.9 from one transported coordinate to a bounded 2+1D temporal-gauge
Maxwell--Dirac reduction with non-axis-aligned packet motion, two electric-field
components, magnetic curl, Poynting transport, absorber accounting, and domain-shape
checks.

## Equations

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

The absorber-induced charge obeys

```text
rho_abs,t = -div(sigma E),
```

so the Gauss ledger uses matter plus absorber charge.

## Frozen inputs

```text
m = 1
q = 0.20
packet width = 2.2
centers = (-5,-2), (5,2)
momenta = (0.95,0.35), (-0.95,-0.2275)
gauge seed amplitude = 0.006
gauge seed width = 4.
```

## Numerical method

- periodic spectral derivatives;
- fourth-order Runge--Kutta time evolution;
- spectral Poisson initialization of the longitudinal electric field;
- conductivity absorber with induced-charge continuity;
- matter, field, absorber, Gauss, magnetic, Poynting, and packet-moment ledgers.

## Scored studies

- refinement: square grids `{32,64,128}`, `t=2`;
- long run: `96x96`, `t=8`;
- domain shapes: `72x60`, `72x72`, and `72x84` at fixed spacing.

## Acceptance

- transported-spinor order at least `3`;
- norm drift at most `2e-8`;
- corrected-energy drift at most `5e-5`;
- final Gauss residual at most `2e-4` absolute and `5e-2` relative;
- net charge at most `1e-10`;
- packet separation decreases;
- magnetic field is nonzero;
- transport direction changes by at least `1e-3` radians;
- domain-shape spreads remain within frozen budgets.

## Scope boundary

M9.10 is a bounded classical 2+1D field-model qualification. It does not establish
a stable charged particle, full 3D Maxwell--Dirac dynamics, calibrated units,
fermionic quantization, or an electron identity.
