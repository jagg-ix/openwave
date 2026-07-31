# OpenWave M15 CAT/EPT Kuchař relational-time model

M15 executes the semantic contracts formalized for Kuchař Sections 1--2 and
connects them to the existing Page--Wootters, Wheeler--DeWitt, Dirac-constraint,
ADM entropic-time, and physical-kernel-inner-product theorem families.

## M15.1 executable surface

The campaign verifies:

- the absolute-time constraint `P_T + h = 0`;
- the embedding Hamilton--Jacobi residual `δS/δX^A + h_A = 0`;
- the functional Schrödinger residual `i δΨ/δX^A - h_A Ψ = 0`;
- vanishing embedding and Dirac commutator anomaly channels;
- Page--Wootters/Wheeler--DeWitt clock-system anti-balance;
- equivalence of the selected clock quantizations on declared spectral invariants;
- embedding independence of the selected physical inner product;
- monotonicity of the supplied entropic clock `τ_ent = S_I / ℏ`.

## Formal authority

The model is pinned to:

```text
jagg-ix/entropic-physlib-private
entropic-physlib-linear-full
1061988e0c356075562ced1bd88758ba4922375c
```

The primary new authority is
`Physlib/Gravity/Canonical/KucharSectionsOneTwo.lean`.

## Claim boundary

M15.1 is a **local-consistency model**. It does not prove that full general
relativity has a global preferred time, that every Dirac-closed canonical system
admits a global Kuchař decomposition, that all clock choices yield equivalent
quantizations, or that one preferred physical inner product has been derived.

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m15_kuchar_relational_time import run_m15_model_study
import json
print(json.dumps(run_m15_model_study(), indent=2, sort_keys=True, default=str))
PY
```
