# M9.10 method note: bounded 2+1D Maxwell--Dirac transport

M9.10 adds a second transported coordinate and both vector-potential components.
The smooth periodic benchmark uses spectral derivatives and RK4, producing a high
observed refinement order over the frozen interval. This is a solver result, not a
claim of universal eighth-order accuracy.

The conductivity absorber changes Gauss continuity unless its induced charge is
included. The implementation therefore evolves

```text
rho_abs,t = -div(sigma E)
```

and audits `div(E) = rho_matter + rho_abs`.

## Results

```text
transported-spinor observed order = 8.18686268
long-run max norm drift = 5.73621e-9
long-run corrected-energy drift = 6.53843e-9
final Gauss residual = 1.49202e-8 absolute
final Gauss residual = 1.71900e-5 relative
max net charge = 5.51630e-11
initial separation = 10.77033
final separation = 1.03495
transport angle = 0.38051 -> 1.34895
emitted energy = 1.12278e-5
absorbed energy = 4.42916e-5
max magnetic field = 0.00770611.
```

The domain-shape study gives relative spreads `2.49e-5` for final separation and
`0.03147` for emitted energy.

Focused local validation:

```text
pytest -q tests/test_m9_planar_2d_maxwell_dirac.py
8 passed in 19.48s
```

No CI workflow was run or inspected.
