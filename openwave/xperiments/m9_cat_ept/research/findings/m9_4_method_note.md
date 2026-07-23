# M9.4 method note: nonlinear localization decision gate

## Decision

The frozen family produces one positive mathematical localization result:

- `kappa = -2` passes every candidate gate;
- the identical seed disperses for `kappa = 0` and `kappa = +2`.

The accepted object is a neutral 1+1D bright soliton. Its physical identity is
unassigned.

## Equation and exact candidate

```text
i psi_t = -1/2 psi_xx + kappa |psi|^2 psi
psi_*(x,t) = sech(x) / sqrt(2) * exp(i t/2),  kappa = -2.
```

For the stationary form `psi = exp(-i mu t) phi`, the candidate has
`mu = -1/2` and energy

```text
E = integral [|phi_x|^2/2 - |phi|^4] dx = -1/6.
```

## Refinement result

| Observable | `256 -> 512` | `512 -> 1024` |
| --- | ---: | ---: |
| Phase-aligned L2 error order | 1.99545 | 1.93086 |
| Density L1 error order | 2.00011 | 2.00219 |

Finest level (`N = 1024`, `dx = 0.0390625`, `t = 2`):

| Metric | Result |
| --- | ---: |
| Fidelity | `1.0000000000` |
| Phase-aligned L2 error | `1.19190e-8` |
| Density L1 error | `1.40635e-8` |
| Norm drift | `1.39955e-12` |
| Energy drift | `6.99635e-13` |
| Stationary residual | `2.12836e-8` |
| Variance ratio | `1.0000000233` |
| Peak ratio | `0.9999999871` |
| Core probability, `|x| <= 5` | `0.9999127046` |
| Edge probability | `1.32002e-12` |

## Controls

The common seed is not generically stable:

| Member | Variance ratio | Peak ratio | Density change L1 |
| --- | ---: | ---: | ---: |
| Free, `kappa = 0` | 2.62114 | 0.51479 | 0.55326 |
| Defocusing, `kappa = +2` | 4.57730 | 0.36041 | 0.82614 |

Both controls satisfy the frozen dispersal condition.

## Window test

Keeping `dx = 0.0625` while changing the half-width gives:

| Half-width | Final variance | Final peak |
| ---: | ---: | ---: |
| 16 | 0.822467082500 | 0.499999980401 |
| 20 | 0.822467082503 | 0.499999983414 |
| 24 | 0.822467082504 | 0.499999983393 |

The spread is below the `1e-8` gate for both observables.

## Perturbation test

The seed was multiplied by `1 + 0.05 cos(x/2)`, renormalized, and evolved to
`t = 5` under `kappa = -2`.

- core probability: `0.9998977087`;
- edge probability: `2.26489e-8`;
- variance ratio: `1.05003`;
- fidelity to the unperturbed soliton: `0.9999499892`.

The perturbed state breathes and emits a small radiative tail but remains
localized under the frozen survival criterion.

## What the result establishes

It establishes that the selected focusing cubic equation admits a numerically
convergent, window-independent, perturbatively surviving localized state in
1+1 dimensions, while the bounded controls disperse.

## What it does not establish

- The cubic term is not derived from the CAT/EPT imaginary action.
- The result is not three-dimensional.
- No charge, spin, fermionic statistics, electron identity, mass calibration, or
  experimental prediction is present.
- Integrable cubic-NLS stability is a mathematical mechanism, not evidence that
  Nature uses this exact model.

## Reproduction

```bash
python -m openwave.xperiments.m9_cat_ept.research.scripts.m9_4_localized_particle
pytest -q tests/test_m9_localized_particle.py
```

Focused local validation returned `6 passed`.
