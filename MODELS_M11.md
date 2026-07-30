# OpenWave M11 CAT/EPT pointwise soliton--Liouville--QDO model

M11 is a separate candidate particle model. It does not replace the M9 Pauli--Hartree carrier or the M10 relativistic SU(3) color-matter carrier.

## Lineage

| Milestone | Executable result |
| --- | --- |
| M11.1 | exact normalized pointwise bright soliton and standing-wave/BPS controls |
| M11.2 | pure Liouville density tensor, infinite-mode cutoff refinement and fixed-particle bookkeeping |
| M11.3 | QDO-calibrated Lennard--Jones `-C6/R6` tail and Axilrod--Teller `C9/R9` sector |
| M11.4 | optional SU(3) color coupling reusing M10 links, hopping, gauge covariance and Gauss diagnostics |
| M11.5 | conservative/dissipative center dynamics, monotone entropic time, tensor dephasing and registration |

## Microscopic interaction closure

The reference parameters obey

```text
C6_LJ = epsilon n re^6/(n-6)
      = C6_QDO
      = 3/4 alpha1^2 hbar omega

alpha1 C6 = 4 C9,
C9 = 3/16 alpha1^3 hbar omega.
```

Thus the LJ dispersion tail and ATM three-body coupling are generated from one QDO response model rather than calibrated independently.

## Formal authority

Lean authority is `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, TIP `8bafa9ab93cbb39e85909fc3837bb4b6e0dec748`. OpenWave supplies executable numerical closure and does not promote the finite-cutoff Liouville implementation to an infinite-particle completed Fock space.

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m11_cat_ept_soliton_qdo import run_m11_model_study
import json
print(json.dumps(run_m11_model_study(), indent=2, sort_keys=True, default=float))
PY
```
