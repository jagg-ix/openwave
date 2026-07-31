# OpenWave M14.6 continuum kernel/operator double copy

M14.6 places Jacobi-compatible numerator triples on `X × X`, integrates the weighted double-copy density, verifies a finite Hilbert--Schmidt kernel limit, exercises commuting left/right pointwise multipliers, and evaluates positive pointwise-background kernel composition. It is pinned to `entropic-physlib-linear-full@35f98f147771a4e250ec01b4cbf2afab72313db7`.

## Toolchain

- Lean `4.31.0` (`leanprover/lean4:v4.31.0`)
- `jagg-ix/zil-lean@6daee2698304feb203c6adb91b2e8853613f85b5`

## Run

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m14_continuum_ads_double_copy.model_registration_m146 import run_model_study
print(run_model_study()["passed"])
PY
```

The L2, measurability, maximal-domain, summability, and weighted-orthogonality premises remain explicit. No arbitrary interacting continuum double-copy theorem is claimed.
