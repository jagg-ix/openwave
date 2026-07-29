# M9.141 — three-dimensional Pauli--Hartree--U(1) carrier

M9.141 advances the latest model lineage from a facade over separate components to one executable three-dimensional charged carrier.

## Closed in this milestone

The new `PauliHartreeU1State` contains one two-component spinor, Hartree potential, scalar and vector U(1) potentials, electric and magnetic fields, coordinate time, entropic time, and measured winding metadata on the shared odd `17^3` Fourier grid.

The carrier uses the same effective mass in the kinetic coefficient and convective current, includes the local cubic--quintic interaction and attractive Hartree term, and recomputes the static periodic Maxwell fields through a Picard iteration. Winding three is measured from the field and agrees with the normalized unit charge ledger.

The frozen-operator discrete imaginary functional is

```text
S_I^n[psi] = gamma/2 ||(H_n - mu_n) psi||_2^2.
```

Its squared-gradient substep has nonnegative entropic production and decreases both the stationary residual and the discrete functional in the reference campaign.

## Numerical reference result

The default campaign checks normalization, spin `1/2`, field-measured winding, the `D=1/(2m)` map, Maxwell fixed-point closure, Gauss/Ampere/divergence residuals, entropic-time monotonicity, and replay fingerprints. The static constraint residuals close near machine precision.

## Retained boundary

This is a dimensionless charged carrier, not a stable physical particle. The stationary residual remains nonzero, no continuum convergence result is claimed, the real-time continuity equation is not yet evolved, and charge, mass, moment, force, and particle identity remain uncalibrated.

The next target is M9.142: solve and perturb a stable measured-winding branch on nested odd grids without changing the 21-row comparison status in advance.
