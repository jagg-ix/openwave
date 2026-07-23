# M9.4 task: nonlinear localization decision gate

## Frozen scientific question

Does the first bounded M9 nonlinear family contain a finite-energy localized
state that remains stable under refinement, larger windows, and a fixed shape
perturbation, while the same seed disperses in the controls?

## Frozen equation family

Use

```text
i psi_t = -1/2 psi_xx + kappa |psi|^2 psi
```

with exactly three members:

| Member | `kappa` | Role |
| --- | ---: | --- |
| Free | `0` | dispersive negative control |
| Defocusing cubic | `+2` | nonlinear dispersive negative control |
| Focusing cubic | `-2` | localization candidate |

No coefficient scan is allowed. The value `-2` is selected because the
normalized analytic profile

```text
psi(x,t) = sech(x) / sqrt(2) * exp(i t/2)
```

solves that equation on the infinite line. This makes the run a solver and
stability gate, not a mass fit.

## Common seed

Every family member starts from the same normalized `sech(x)` profile. The
candidate is not allowed a separately optimized initial state.

## Numerical method

- periodic Strang split-step Fourier integration;
- main domain `[-20,20)`;
- final time `2`;
- refinement `N = 256, 512, 1024` with `dt = 0.01 dx` adjusted to end exactly;
- window test at `L = 16, 20, 24` with fixed `dx = 0.0625`;
- perturbation test: multiply the seed by `1 + 0.05 cos(x/2)`, renormalize, evolve to `t = 5`.

## Numerical tolerance calibration

The family, signs, coefficient values, seed, resolutions, windows, and
perturbation were fixed before the scored run. A non-scoring dry run was used to
set only three numerical truncation budgets:

- stationary residual `<= 5e-8`, dominated by embedding a nonperiodic `sech`
  tail in a periodic spectral box;
- edge probability `<= 2e-12`, consistent with the analytic `sech` tail in the
  chosen outer region;
- perturbed edge probability `<= 1e-7`, allowing emitted radiation while still
  requiring core survival.

These tolerances are numerical budgets, not physical parameters or fitted
observables. The dry-run values are not reported as independent validation.

## Acceptance conditions

The focusing candidate must satisfy all of:

1. norm drift `<= 1e-11`;
2. energy drift `<= 2e-8`;
3. stationary residual `<= 5e-8`;
4. phase and density convergence order `>= 1.8`;
5. finest fidelity `>= 0.999999`;
6. edge probability `<= 2e-12` and core probability inside `|x|<=5` `>= 0.999`;
7. variance and peak ratios within `1e-4` of one;
8. window variation of variance and peak `<= 1e-8`;
9. perturbed state retains core probability `>= 0.99`, edge probability
   `<= 1e-7`, and variance ratio `<= 1.5`.

The free and defocusing controls must each have variance ratio `>= 1.5` and peak
ratio `<= 0.8`.

## Classification boundary

A pass establishes a localized **1+1-dimensional neutral mathematical
candidate** for the selected cubic equation. It does not establish an electron,
charge, spin, three-dimensional stability, a mass prediction, or that CAT/EPT
uniquely requires the cubic term.
