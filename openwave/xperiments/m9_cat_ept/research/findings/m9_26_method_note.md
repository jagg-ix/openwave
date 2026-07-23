# M9.26 finding: integer winding is field-derived but not electric charge

The contour observable recovers winding sectors `-2,-1,0,1,2` with maximum
quantization error `2.220e-16`. The result is invariant under a global phase,
stable across four contour radii, and preserved by a fixed smooth perturbation.

For two separated defects, local windings add exactly to the total contour
winding. The field must remain nonzero on the contour; otherwise the observable
is rejected as undefined.

The winding sector is seeded in the initial state. Therefore
`spontaneous_sector_selection=false` and `identified_with_electric_charge=false`.

Focused validation: `8 passed`. No CI workflow was run or inspected.
