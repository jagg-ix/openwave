# M9.120 task contract — spectra, response, and refinement

## M9.120a

Construct finite Hermitian covariant operators for both M9.119 gauge carriers.

Required gates:

- Hermiticity and nonnegative spectrum;
- local-gauge similarity and eigenvalue invariance;
- explicit low-mode eigenpair residuals;
- three Higgs gauge-orbit tangent zero modes and one radial curvature mode;
- no physical mass or particle-name promotion.

## M9.120b

Construct a gauge-scalar source and finite spectral response.

Required gates:

- source commutes with local internal gauge transformations;
- broadened response is gauge invariant;
- completeness sum rule closes;
- Higgs radial source is orthogonal to gauge-orbit tangents;
- numerical broadening is not reported as intrinsic decay.

## M9.120c

Execute spectral refinement on one fixed physical periodic domain.

Required gates:

- odd grids `5, 7, 9, 11`;
- links scale as `exp(i h A)`;
- flat first-mode error decreases;
- smooth strong and electroweak low-cluster changes decrease;
- calibration, particle identity, continuum proof and external prediction remain false.

## Formal authority

Use merged `entropic-physlib-linear-full@3923d802339c957066fcccd579362f739775797a`. Draft Physlib PRs #19 and #20 may be recorded as candidates but must not be accepted as merged authority.

## Stop conditions

Fail closed on:

- formal head, root, or source-blob drift;
- non-Hermitian covariant operators;
- gauge-dependent spectra or response;
- failed completeness sum rules;
- non-improving refinement sequences;
- any automatic promotion to physical masses, decay rates, particle identities, continuum closure, or external validation.
