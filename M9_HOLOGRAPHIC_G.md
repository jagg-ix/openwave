# M9.110 holographic Newton-G hierarchy

## Primary coupling

The primary CAT/EPT gravitational coupling is the screen information density

```text
G = (A/N_H) c^3/hbar
A/N_H = l_P^2.
```

For the entanglement screen

```text
A(m,eta) = 4 pi lambda_C(m)^2 (log K(eta))^2,
lambda_C = hbar/(m c),
```

the holographic count is

```text
N_H = A/l_P^2
    = 4 pi (m_P/m)^2 (log K)^2.
```

Both `A` and `N_H` scale as `m^-2`, so their ratio and the resulting `G` are species invariant.

## Compton-cell specialization

The separate Compton-cell count is

```text
N_C = A/lambda_C^2 = 4 pi (log K)^2.
```

It is species independent at fixed entanglement, but it is not the microscopic holographic bit count. The count ratio is

```text
N_H/N_C = lambda_C^2/l_P^2 = (m_P/m)^2.
```

Therefore one sub-Planckian Compton cell represents many Planck-area bits. The two counts coincide only at the Planck crossover.

The mass-dependent expression

```text
G_C(m) = (A/N_C)c^3/hbar = hbar c/m^2
```

is the coupling obtained after replacing the Planck-area bit with one Compton-area cell. It is not the primary universal holographic coupling.

## Completed targets

### M9.110a — count hierarchy

`holographic_count_hierarchy.py` computes `A`, `N_H`, `N_C`, `N_H/N_C`, and both area-per-count couplings for electron, muon, and proton controls. It verifies that holographic `G` remains universal while the previously reported large ratios are exactly the number of Planck bits per Compton cell.

### M9.110b — scale-flow diagnostics

`holographic_coarse_graining.py` evaluates the exact scale law

```text
d log(N_H/N_C) / d log(m/m_P) = -2
```

through the Planck crossover. This is an exact count ratio. It is not yet a dynamical renormalization or degeneracy derivation.

### M9.110c — screen-density coupling

`holographic_gravity_coupling.py` makes `A/N` the primary OpenWave coupling source. It requires an independent screen anchor before physical injection. The weak-field configuration accepts the resulting coupling. The nonlinear configuration still reconstructs its own default through `matter_config()`, so the nonlinear one-G injection remains an explicit failed sub-gate and the next implementation target.

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_110_holographic_counts.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_110_holographic_coarse_graining.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_110_screen_gravity_coupling.py
```

## Boundaries

- exact `N_H/N_C` is not yet a microscopic coarse-graining dynamics;
- a synthetic `A/N` fixture is not external calibration;
- weak-field injection does not imply nonlinear injection;
- this work preserves the holographic universal `G`; it does not repeat the earlier particle-clock no-go as a primary-`G` conclusion.
