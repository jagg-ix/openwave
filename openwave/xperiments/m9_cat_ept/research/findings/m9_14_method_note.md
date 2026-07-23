# M9.14 method note: finite candidate, negative long-horizon decision

The four-member survey selects `lambda=8`:

```text
free maximum RMS ratio = 1.10212568
lambda=8 maximum RMS ratio = 1.09872290
improvement = 0.00340278
lambda=8 minimum peak ratio = 0.86413188
lambda=8 minimum core fraction = 0.99345635.
```

The fixed perturbation gives

```text
maximum RMS ratio = 1.10496901
minimum peak ratio = 0.86314069
minimum core fraction = 0.99529574.
```

At `t=5`, the selected member gives

```text
maximum RMS ratio = 1.25296679
minimum peak ratio = 0.76569894
minimum core fraction = 0.97693768
emitted energy = 5.55013e-6.
```

It fails the frozen long-horizon particle gate. Canonical decision:

> `lambda=8` is the strongest finite-time 3D member, but no stable
> three-dimensional particle candidate is accepted.

Global maxima are

```text
norm drift = 1.31900e-7
corrected-energy drift = 1.36056e-7
final Gauss residual = 7.55032e-4 absolute, 0.485731 relative.
```

All nine decision-procedure gates pass; `accepted_particle_candidate` is false.

Focused local validation:

```text
pytest -q tests/test_m9_spatial_3d_localization_decision.py
8 passed
```

No CI workflow was run or inspected.
