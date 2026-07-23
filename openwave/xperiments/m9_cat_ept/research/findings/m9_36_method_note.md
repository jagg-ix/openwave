# M9.36 finding: adaptive error budget closes

A total tolerance of `1e-5` is divided equally among temporal, spatial, domain,
and coupling channels. The selected levels are 256 Heun steps, 1024 spatial
intervals, Gaussian half-width 3.5, and 12 coupling iterations. The propagated
bound is `4.13936e-06`; the actual benchmark error is `1.47375e-06`.
All component allocations, monotonic estimates, deterministic fingerprints, and
insufficient-refinement rejection gates pass.

This is numerical-error infrastructure, not a physical uncertainty statement.
Focused validation: `8 passed`.
