# OpenWave M14.5 pointwise Mizera BCJ model

M14.5 executes the newer Mizera residue and twisted-cohomology surface from `entropic-physlib-linear-full@35f98f147771a4e250ec01b4cbf2afab72313db7`. A continuous L2 family of three-channel numerators obeys Jacobi pointwise, its finite four-puncture residues reconstruct every channel, regularity at infinity returns the same Jacobi relation, and weighted generalized-gauge and twisted-exact shifts remain invisible.

## Toolchain

- Lean `4.31.0` (`leanprover/lean4:v4.31.0`)
- `jagg-ix/zil-lean@6daee2698304feb203c6adb91b2e8853613f85b5`

## Run

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m14_continuum_ads_double_copy.model_registration_m145 import run_model_study
print(run_model_study()["passed"])
PY
```

The result is a conditional compatibility model. It does not construct the full CHY measure, Deligne--Mumford compactification, or loop-level BCJ numerators.
