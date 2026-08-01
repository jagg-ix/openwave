# OpenWave M15 CAT/EPT Kuchař relational-time, AdS double-copy, and clock-synthesis model

M15 begins with the Kuchař Sections 1--2 relational-time consistency contract,
composes the executable BCJ/AdS surfaces already present in M13 and M14, and
then adds the latest conditioned-dynamics, functorial-calibration, and
information/force/correlation clock theorems.

## Lineage

| Milestone | Executable coverage |
| --- | --- |
| M15.1 | absolute-time, Hamilton--Jacobi, functional Schrödinger, anomaly, clock-choice and physical-inner-product consistency |
| M15.2 | finite BCJ, primitive QCD, massive/Yukawa BCJ, weighted GKP source kernel, generalized gauge checks and explicit pointwise Jacobi modes |
| M15.3 | square-summable infinite BCJ direct limit, quantitative tails, causal Green/Pauli--Jordan transport and Hadamard probe compatibility |
| M15.4 | D3/central-charge normalization, continuum GKP kernel, RT/Complex-Einstein identities, smooth Lorentzian direct limit and harmonic-Einstein uniqueness |
| M15.5 | exact conditioned evolution and ordered Page--Wootters/modular/entropic/proper-time calibration |
| M15.6 | functorial conditioning, observable/predicate transport, and conjugated clock endomorphisms |
| M15.7 | reversible KL clock, tick-conjugate force, classical CHSH ceiling, eight-clock quantum optimum, and damped clock phase |

## Latest formal authority

```text
jagg-ix/entropic-physlib-private
entropic-physlib-linear-full
b44d8ab215568d2239ab2ea20aca483df3b1076b
```

The new M15.5--M15.7 authority is concentrated in:

- `ThreeClockClosure.lean`;
- `ThreeClockDynamics.lean`;
- `ThreeClockFunctoriality.lean`;
- `EntropicClockSynthesis.lean`.

## Coverage boundary

M15.7 has status **conditional-relational-clock-synthesis-model**.

The conditioned-state equality, clock equivalences, strict monotonicity of the
physical calibration maps, and selected finite thermodynamic inputs remain
explicit premises. The model does not infer a global preferred time, automatic
equivalence of arbitrary clocks, a single action deriving all clock,
information, force and correlation faces, a Pinsker-type quantitative
information/correlation inequality, loop-level color--kinematics duality, or
Einstein equations from a Bell certificate.

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m15_kuchar_relational_time import run_m15_model_study
import json
print(json.dumps(run_m15_model_study(), indent=2, sort_keys=True, default=str))
PY
```
