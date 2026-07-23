# M9 input, calibration, and prediction ledger

## M9.12--M9.14 selected inputs

The 3D transport uses `m=1`, `q=0.15`, width `1.8`, offsets `(4,1.5,0.75)`,
selected momenta, centered differences, RK4, and a conductivity absorber.

M9.14 adds the bounded family `lambda={0,2,4,8}`, a `16^3,t=3` survey, a
`20^3,t=3` fixed perturbation, and a `20^3,t=5` long-horizon gate. `lambda=8` is
selected by minimum finite-time RMS spreading; it is not derived from CAT/EPT.

Result: finite-time improvement `0.00340278`, but `accepted_particle_candidate=false`.
M9 remains a selected multi-parameter research model without physical calibration.
