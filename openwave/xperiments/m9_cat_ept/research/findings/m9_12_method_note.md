# M9.12 method note: 3D controls pass

The four-component Dirac matrices close all Clifford identities exactly in
binary64 arithmetic.

The free-spinor RK4 comparison gives

```text
errors = 1.54399e-6, 9.65094e-8, 6.03200e-9
orders = 3.99985, 3.99996
maximum norm drift = 2.56698e-7.
```

The vacuum Maxwell wave gives

```text
A relative L2 = 0.00301029
E relative L2 = 0.00485267
field-energy drift = 5.75908e-14.
```

All six control gates pass. These results qualify the numerical representation;
they do not test matter-field back-reaction.

Focused local validation:

```text
pytest -q tests/test_m9_spatial_3d_controls.py
8 passed
```

No CI workflow was run or inspected.
