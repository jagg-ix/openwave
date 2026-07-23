# M9.17 method note: matter-to-reservoir transfer

The spatial refinement order is `3.92286`. At `t=6`:

```text
matter probability = 0.405077933099811
reservoir probability = 0.594922067151256
extended probability error = 2.51068e-10
extended charge error = 1.00174e-11
maximum continuity residual = 4.17635e-10
tau_ent = 0.451837901490217.
```

The reservoir remains nonnegative, matter contracts monotonically, and the
reservoir and operational clock increase monotonically. The zero-loss matter
probability drift is `6.81342e-10`.

Focused validation: `8 passed`. No CI workflow was run or inspected.
