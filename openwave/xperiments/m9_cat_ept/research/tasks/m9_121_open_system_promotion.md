# M9.121 preregistered gates

## M9.121a — open-system decay

Pass only if both strong and electroweak finite carriers have a positive model-unit rate and satisfy:

- Kraus completeness error at most `2e-14`;
- semigroup relative error at most `2e-13`;
- Lindblad right-derivative relative error at most `2e-5`;
- density minimum eigenvalue at least `-2e-14`;
- lifetime and half-life population errors at most `2e-14`;
- no reuse of M9.120 response broadening as a decay rate.

## M9.121b — calibration and holdout

Pass only if the prediction digest is deterministic, target observables are excluded from fitting, target leakage and commitment tampering are rejected, and missing physical scale data leave every result in model units.

## M9.121c — promotion governance

Internal readiness requires formalization, numerical implementation, kernel-clean status, and deterministic reproduction. External readiness additionally requires independent calibration, pre-reveal commitment, held-out testing, and an independent identity bridge. Every required external relation must be individually load-bearing.

## Forbidden promotions

This task must not promote a model-unit rate to a measured width, a two-level channel to full radiative QFT, a calibration protocol to calibration, or a sealed holdout to external validation.
