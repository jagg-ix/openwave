# M9.19 task: physical calibration and identifiability contract

## Question

What independent SI anchors and detector calibrations are required before the
M9 back-reaction rates can be interpreted physically?

## Contract

The contract requires:

- a physical time-scale anchor in seconds with uncertainty and provenance;
- trace-channel detection efficiency;
- coherence/purity estimator efficiency;
- reservoir-capture efficiency;
- mechanism-blind acquisition times.

The synthetic reference values are `T0=2.5e-6 s`, trace efficiency `0.91`,
coherence efficiency `0.88`, and reservoir efficiency `0.84`. They are test
fixtures, not measured apparatus values.

## Gates

- schema and SI-unit validation;
- invalid/missing anchors rejected;
- unanchored rate/time-scale Jacobian rank is one for two parameters;
- an independent time anchor restores local rank two;
- exact synthetic rate roundtrip for all three interfaces;
- `physical_calibration_completed=false` remains explicit.
