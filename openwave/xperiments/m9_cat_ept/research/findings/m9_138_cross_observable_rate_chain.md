# M9.138 — calibrated linewidth, relaxation, and KL chain

Physlib branch `entropic-physlib-linear-full` now points to commit
`deb1eb3ecb4aabbba1555b24253d9dd8f6fba1f2`, which adds
`OneLevelCrossObservable.lean` at blob
`d99136a02b3d09fa5338f8187ebf023e47be91f0`.

The formal chain is now closed for one `RateData.gamma` independently fixed by
counted transition rates:

- `gamma = (Gamma_in + Gamma_out)/2`;
- Lorentzian HWHM equals `gamma`;
- Lorentzian FWHM equals `2 gamma = Gamma_in + Gamma_out`;
- population `T1 = 1/(2 gamma) = 1/(Gamma_in + Gamma_out)`;
- the exact binary-KL derivative uses the same `gamma` in its production rate.

OpenWave M9.138 implements the same identities numerically, checks both unique
half-maximum points, verifies the e-fold relaxation time, and compares a finite-
difference KL derivative with the analytic production rate.

## Remaining boundary

This is an anti-circular cross-observable consistency theorem, not empirical
confirmation. It assumes the carrier is described by the one-level Markov/GKSL
rate model. Cross-carrier validation, pure-dephasing separation, uncertainty
propagation, and comparison with conventional open-system models remain open.
