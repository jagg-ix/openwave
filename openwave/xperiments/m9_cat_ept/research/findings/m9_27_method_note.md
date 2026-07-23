# M9.27 finding: selected topological ansatz has an interior dimensionless scale

For the degree-one baby-Skyrme radial ansatz,

```text
analytic selected scale     = 1.000000000000
numerical scan minimum      = 1.000000000000
energy at selected scale    = 22.619467105847
curvature at minimum        = 40.212385965949
```

Radial quadrature converges at orders
`1.988673` and
`1.997162`. Scale relaxation from `0.6` and
`1.7` converges to the same minimum with nonincreasing energy.

Removing the Skyrme term drives the minimum to the lower scan boundary; removing
the potential term drives it to the upper boundary. Both sectors are required.

This selects a dimensionless scale for the ansatz only.
`physical_rest_mass_established=false` and
`accepted_three_dimensional_particle=false`.

Focused validation: `8 passed`. No CI workflow was run or inspected.
