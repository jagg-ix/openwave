# OpenWave M14.7 AdS radial/boundary pointwise double copy

M14.7 transports a continuous BCJ numerator field from a periodic boundary into an AdS radial coordinate with the Poisson semigroup. Jacobi closure and weighted color replacement survive every radial slice, the bulk field converges to its boundary datum, and the same D3 coupling normalizes the BCJ, GKP, Complex-Einstein, and Ryu--Takayanagi faces. The formal pin is `entropic-physlib-linear-full@35f98f147771a4e250ec01b4cbf2afab72313db7`.

## Toolchain

- Lean `4.31.0` (`leanprover/lean4:v4.31.0`)
- `jagg-ix/zil-lean@6daee2698304feb203c6adb91b2e8853613f85b5`

## Run

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m14_continuum_ads_double_copy.model_registration_m147 import run_model_study
print(run_model_study()["passed"])
PY
```

This is a linear harmonic radial carrier. It does not prove AdS/CFT, construct an interacting Witten functional, or identify the BCJ amplitude with RT entropy.
