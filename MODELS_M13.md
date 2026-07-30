# OpenWave M13 CAT/EPT scale-dilation soliton-tensor model

M13 isolates the exact scale geometry underlying the CAT/EPT entropic-time arc and applies it to the existing M11 pointwise soliton and finite-cutoff infinite-mode Liouville tensor.

## M13.1 executable surface

- dilation group `lambda(t) = exp(H t)`, including composition and inverses;
- scale Lagrangian `L = 1/2 (lambda_dot/lambda)^2` and common-dilation invariance;
- Euler--Lagrange residual `lambda_ddot lambda - lambda_dot^2`;
- conserved Noether charge `Q = lambda_dot/lambda = H`;
- invariant scale metric `d(x,y) = |log(x/y)|` and exact log-coordinate transport;
- entropic proper distance `r = lambda_C log K`;
- block-spin ladder `a_n = 2^n a_0` with exact `log 2` steps;
- `sqrt(2)` half-step and continuous `2^r` geodesic;
- entropic-horizon energy decay as the `H = -2` orbit;
- SU(2) abelian Gauss fixed-point and charged-sector metric checks;
- norm-preserving pointwise soliton scale family;
- trace, Hermiticity, positivity and purity of each finite-cutoff Liouville tensor;
- charged-lepton Compton-scale distances from supplied M12 mass data.

## Claim boundary

The group, Noether, metric, ladder and half-step relations are executable mirrors of exact Lean theorems. M11 supplies the pointwise and infinite-mode carriers. M12 particle masses remain empirical input labels. M13 does not claim a completed infinite-particle Fock space, a first-principles mass spectrum, new lattice simulation data, or a complete holographic dictionary.

## Formal authority

`jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, TIP `8bafa9ab93cbb39e85909fc3837bb4b6e0dec748`, principally `ScaleDilationLogMetric.lean@0c8262ba`.

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m13_scale_dilation_soliton import run_scale_dilation_soliton_study
import json
print(json.dumps(run_scale_dilation_soliton_study(), indent=2, sort_keys=True, default=str))
PY
```
