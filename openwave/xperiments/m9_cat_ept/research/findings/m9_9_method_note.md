# M9.9 method note: transported planar Maxwell--Dirac dynamics

M9.7c couples a transverse Maxwell field to local spinor rotations. M9.9 adds the
missing spatial Dirac derivative and a longitudinal gauge sector. The two
opposite-charge packets begin at `x=-8` and `x=+8` with momenta directed toward
one another.

The longitudinal initial field is not produced by an unrelated continuum solver.
It inverts the exact Fourier symbol of the centered derivative used by the
finite-difference evolution. Initial discrete Gauss residual therefore closes to
binary64 precision for the smooth neutral source.

## Results

The 128/256/512 refinement gives transported-spinor self-convergence order

```text
1.8991759529.
```

At the finest refinement level through `t=6`:

```text
max norm drift = 2.31e-10
max corrected-energy relative drift = 4.25e-7
final Gauss residual = 0.009904 relative
packet centers = -4.13767, +4.13767.
```

At 512 points through `t=14`:

```text
norm = 0.999999999398
max norm drift = 6.02e-10
max corrected-energy relative drift = 1.073e-6
final Gauss residual = 2.754e-4 absolute, 0.02264 relative
max net charge = 1.04e-16
final packet centers = +1.10664, -1.10664
emitted energy = 2.84143e-5
max transverse field = 0.0100947.
```

The packet centers cross. This is transport and interaction evidence, not a
localized-particle stability result. The relative Gauss diagnostic may become
large at intermediate samples when the charge-density scale is small; acceptance
therefore requires both final absolute and relative closure and separately audits
net charge.

Focused local validation:

```text
pytest -q tests/test_m9_transported_maxwell_dirac.py
8 passed in 1.74s
```

No CI workflow was run or inspected.
