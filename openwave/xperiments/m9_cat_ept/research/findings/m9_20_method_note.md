# M9.20 method note: full-panel separation and trace-only no-go

The full trace/purity/reservoir panel classifies all `120/120` synthetic trials
correctly at `sigma=0.015`. The minimum held-out validation margin is
`0.0236604`; the median is `0.0531849`.

Trace alone is structurally insufficient: amplitude loss at rate `0.12` and
reservoir matter loss at rate `0.24` differ by only `1.11022e-16` on the frozen
time grid. The benchmark also rejects an oscillatory out-of-family signature.

This is synthetic identifiability evidence, not apparatus performance.

Focused validation: `8 passed`. No CI workflow was run or inspected.
