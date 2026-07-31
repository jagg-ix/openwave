# OpenWave M15 CAT/EPT Kuchař relational-time and AdS double-copy model

M15 begins with the Kuchař Sections 1--2 relational-time consistency contract,
then composes every executable BCJ/AdS surface already present in M13 and M14.

## Lineage

| Milestone | Executable coverage |
| --- | --- |
| M15.1 | absolute-time, Hamilton--Jacobi, functional Schrödinger, anomaly, clock-choice and physical-inner-product consistency |
| M15.2 | finite BCJ, primitive QCD, massive/Yukawa BCJ, weighted GKP source kernel, generalized gauge checks and explicit pointwise Jacobi modes |
| M15.3 | square-summable infinite BCJ direct limit, quantitative tails, causal Green/Pauli--Jordan transport and Hadamard probe compatibility |
| M15.4 | D3/central-charge normalization, continuum GKP kernel, RT/Complex-Einstein identities, smooth Lorentzian direct limit and harmonic-Einstein uniqueness |

## Coverage boundary

M15.4 registers finite, pointwise, infinite and continuum double-copy surfaces in
one relational-time model. The status remains
**conditional-relational-continuum-ads-double-copy-model**.

It does not infer a global preferred time, automatic Green/Hadamard existence,
convergence of arbitrary numerator families, loop-level color--kinematics
duality, an interacting renormalized Witten functional, or equality between a
BCJ amplitude and RT entropy.

## Formal authority

```text
jagg-ix/entropic-physlib-private
entropic-physlib-linear-full
1061988e0c356075562ced1bd88758ba4922375c
```

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m15_kuchar_relational_time import run_m15_model_study
import json
print(json.dumps(run_m15_model_study(), indent=2, sort_keys=True, default=str))
PY
```
