# M9.16 method note: trace-preserving information loss

The RK4 orders are `4.05497` and `4.02755`. At `t=4`:

```text
trace error = 2.22045e-16
minimum eigenvalue = 2.22045e-16
population drift = 0
purity = 0.556476454223419
coherence L1 = 0.151502173076287
relative coherence = 0.0118902739272556.
```

Purity and relative coherence are monotone. The zero-rate purity drift is
`4.37274e-10`.

Focused validation: `9 passed`, including canonical JSON boolean serialization.
No CI workflow was run or inspected.
