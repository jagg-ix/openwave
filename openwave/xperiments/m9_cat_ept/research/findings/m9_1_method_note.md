# M9.1 method note: formal-contract conformance

## Result

The deterministic Python transcription passes the declared algebraic checks at
binary64 precision. This is a software-interface result only. It does not show
that CAT/EPT supplies a localized OpenWave particle.

## Equations and code map

| Equation | Python implementation | Check |
| --- | --- | --- |
| `|sqrt(rho) exp(i Phi)|^2 = rho` | `ed_wave_function` | `born_rule` |
| `omega_Z(0) = 2 omega_C` | `zitterbewegung_frequency`, `compton_frequency` | `zitterbewegung_rest_eq_two_compton` |
| `lambda_C omega_C = c` | `compton_wavelength`, `compton_frequency` | `compton_wavelength_mul_frequency` |
| `lambda_Q = hbar^2 / 8` | `quantum_coupling` | `quantum_coupling` |
| `tau_ent = S_I / hbar` | `entropic_clock`, `imaginary_action` | `entropic_clock_eq_imaginary_action_div` |
| `|W| = exp(-tau_ent)` | `correlation_weight_norm` | `correlation_weight_norm` |
| factorized `p_XY` has zero total correlation | `total_correlation` | `independent_total_correlation` |

## Test distributions

The correlated test state is

```text
[[0.4, 0.1],
 [0.1, 0.4]]
```

and the exactly factorized state is

```text
[0.4, 0.6]^T [0.3, 0.7]
=
[[0.12, 0.28],
 [0.18, 0.42]].
```

## Reproduction

```bash
python -m openwave.xperiments.m9_cat_ept.research.scripts.m9_1_formal_contract
pytest -q tests/test_m9_formal_contract.py
```

The committed JSON in `../data/m9_1_contract_result.json` is the output of the
first command for the pinned source.

## Limitations

- OpenWave does not rerun Lean in this task.
- The formal source was private at export time.
- Test-point equality is not a proof of the general theorem.
- No time evolution, localization search, particle observable or experimental
  comparison is part of M9.1.
