# M9.11 method note: finite-time candidate, long-time rejection

The nonlinear survey monotonically reduces the measured RMS spreading across the
frozen family. The strongest selected member is `lambda=8`.

At `t=8`:

```text
free maximum RMS ratio = 1.52762639
lambda=8 maximum RMS ratio = 1.40072364
spreading improvement = 0.12690276
lambda=8 minimum peak ratio = 0.85486943
lambda=8 minimum core fraction = 0.95543175.
```

The fixed perturbation remains inside the finite-time gate:

```text
maximum RMS ratio = 1.34175227
minimum peak ratio = 0.88188286
minimum core fraction = 0.95992433.
```

At `t=12`, however:

```text
maximum RMS ratio = 1.73615505
minimum peak ratio = 0.67364906
minimum core fraction = 0.92050318.
```

Therefore the finite-time candidate does not survive the long-horizon particle
gate. The accepted conclusion is negative:

> `lambda=8` is a finite-time reduced-spreading candidate, but no stable
> two-dimensional particle candidate is accepted.

All nine decision-procedure gates pass, including the explicit rejection gate.
Across every run, the maximum norm drift is `1.835e-7`, corrected-energy drift is
`2.091e-7`, and final relative Gauss residual is `0.003406`.

Focused local validation:

```text
pytest -q tests/test_m9_planar_2d_localization_decision.py
8 passed in 10.90s
```

No CI workflow was run or inspected.
