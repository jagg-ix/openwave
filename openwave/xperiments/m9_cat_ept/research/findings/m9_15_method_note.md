# M9.15 method note: exact scalar imaginary-action control

The scalar-loss run closes

```text
final norm = 0.182683525390592
final tau_ent = 0.849999996338320
max tau error = 3.66168e-9
weight identity error = 1.11022e-16.
```

The RK4 orders are `4.02023` and `4.01016`. The zero-loss state error is
`3.56893e-9`, with norm drift `1.09776e-10`.

The positive nonuniform loss changes normalized `sigma_z` by `0.42995633`; this
shows that a positive loss matrix is not generally a single scalar weight.

Focused validation: `8 passed`. No CI workflow was run or inspected.
