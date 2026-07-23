# M9.21 method note: powered synthetic protocol, no physical promotion

Recommended shots per arm are:

```text
trace contrast = 16
purity-agreement contrast = 128
reservoir-capture contrast = 32
```

The total primary budget is `352` shots and all deterministic Monte Carlo powers
are `1.0` under the frozen idealized Bernoulli assumptions. Every effect exceeds
the `0.02` systematic floor by more than a factor of eleven.

All three candidate processes contain a monotone quantity, so monotonicity alone
is explicitly rejected as a mechanism or physical-time discriminator.

Focused validation: `8 passed`. Combined M9.19--M9.21: `25 passed`.
No CI workflow was run or inspected.
