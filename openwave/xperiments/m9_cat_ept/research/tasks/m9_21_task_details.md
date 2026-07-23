# M9.21 task: preregistered experimental discriminant and power gate

## Question

What fixed-sample, blinded acquisition protocol would test the M9.18 signatures
without promoting monotonicity or synthetic power to physical evidence?

## Frozen planning assumptions

- two-sided `alpha=0.01`;
- target power `0.90`;
- systematic floor `0.02`;
- 25% sample reserve rounded to the next power of two;
- 5000 deterministic Monte Carlo trials per contrast.

Primary binary contrasts are accessible trace, two-copy purity agreement, and
reservoir-capture fraction.

## Required protocol controls

- zero-coupling, dark-count, efficiency-reference, and time-anchor controls;
- randomized interleaved acquisition;
- hashed condition labels until exclusions are frozen;
- fixed sample size and no optional stopping;
- held-out model selection with out-of-family rejection.

`apparatus_data_available=false` and `physical_mechanism_selected=null` are
mandatory outputs.
