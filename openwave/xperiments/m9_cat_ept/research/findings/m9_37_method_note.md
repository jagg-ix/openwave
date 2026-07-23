# M9.37 finding: 3D continuation works, self-binding does not

The trapped noninteracting minimizer recovers energy `1.5` and RMS radius
`sqrt(3/2)` to machine precision. Continuation through couplings
`0, 0.5, 1, 2` closes projected residuals below `3e-7`; the repulsive branch
expands monotonically and remains boundary-clean. Resolution differences fall
from `1.09e-5` to `9.79e-8` in energy.

The untrapped control expands to RMS radius `5.9003` with boundary fraction
`0.48185`. The reference state is therefore trap-bound, not a self-bound CAT/EPT
particle. Focused validation: `8 passed`.
