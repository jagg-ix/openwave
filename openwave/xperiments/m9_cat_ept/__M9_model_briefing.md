# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 OpenWave comparison criteria and combines a stationary non-Gaussian branch, theorem-guided finite-grid dynamics, explicit claim boundaries, a reusable uncalibrated particle API, branch-wide formalization inventory, current ZIL runtime authority, and a formal/numerical equation reconciliation layer.

## Platform status after M9.99

- Seven criteria are validated in-platform.
- Thirteen remain partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- `entropic-physlib-linear-full` is the current formal equation authority.
- All formal and OpenWave files referenced by the equation comparison are exact-blob pinned and fail closed on drift.
- M9.99 closes internal equation-mapping, mass/current, discrete-operator, and Dirac-observable infrastructure; it changes no criterion status or physical identity.

Validated criteria remain charge quantization, particle stability, spin-1/2 statistics, source-free Maxwell waves, free massive Klein--Gordon evolution, dimensionless Coulomb orbital quantization, and the explicit dimensionless thermal field.

## Canonical implementation surfaces

| Surface | Path | Role |
| --- | --- | --- |
| Current physics profile | `model_conformance_dynamics.py` | M9.97 findings with unchanged statuses |
| ZIL registration | `model_registration_zil.py` | schema-v5 runtime authority |
| Current registration | `model_registration_reconciliation.py` | schema-v6 formal/numerical reconciliation |
| Equation contract | `formal_numerical_equation_contract_current.py` | exact formal/OpenWave source registry and nine relation classes |
| Shared geometry | `compatible_discrete_geometry.py` | odd-grid Fourier gradient/divergence/curl/Laplacian/Poisson/Helmholtz/covariant derivative family |
| Reconciled stationary campaign | `reconciled_gauge_spinor_stationary_current.py` | `D=1/(2m)`, 16-to-17 seed resampling, exact final Maxwell field, Hartree sweep |
| Dirac observables | `dirac_ehrenfest_diagnostics.py` | `d<x>/dt=<alpha>`, retained momentum/Lorentz, theorem-domain classification |
| Reconciliation authority | `formal_numerical_reconciliation_authority.py` | composed no-promotion evidence boundary |
| ZIL graph | `research/zil/m9_99_formal_numerical_reconciliation.zc` | dependencies, mismatches, closures, and remaining obligations |

## M9.99 equation findings

The legacy M9.97 model was not the current formal target:

- current Lean target: attractive Newton/Hartree plus supplied local interaction;
- legacy stationary model: local cubic--quintic only;
- Lean leaves `alpha`, `beta`, and analytic closure hypotheses explicit;
- OpenWave selected `alpha`, `beta` from a Gaussian reference ansatz;
- legacy scalar coefficient `D=0.65` and Pauli/Dirac mass `m=1` violated `D=1/(2m)`;
- legacy matter used exact Fourier derivatives while Maxwell used centered `sin(kh)/h` symbols;
- the periodic neutralized extended-source Maxwell carrier differed from isolated `R³` and momentum-space formal carriers;
- the exact Dirac position theorem is `d<x>/dt=<alpha>`, not direct `d²<x>/dt²=F/m`;
- the exact T-BMT/Dirac--Pauli bridge is rest-frame and vertical-field, not a moving extended packet with globally averaged fields.

The canonical Dirac matrices remain an exact structural overlap.

## M9.99 corrected numerical infrastructure

```text
operational grid    17 × 17 × 17, odd real Fourier
historical seed     16 × 16 × 16, Fourier-resampled
D                   0.65
m_eff               0.7692307692307692
q/m_eff             2Dq
Hartree sweep       0.00, 0.05, 0.10
```

The odd grid avoids the self-conjugate real Nyquist ambiguity. Only the global zero Fourier mode is removed. Even-grid real exact-Fourier derivatives fail closed.

The final stationary Hamiltonian uses the exact Maxwell vector potential whose Gauss and Ampère residuals are reported. The Hartree sweep is executable, but no value is selected as the unique formal or physical coupling.

## Corrected interpretation of M9.97

The retained `2.61%` momentum/Lorentz result remains a valid dimensionless subreduction. The old center-force wrong-sign result is a nonrelativistic diagnostic outside the proved unprojected Dirac position carrier, not a Lean contradiction. The `2.57%` full-generator spin result remains the integration gate. The rest-frame BMT mismatch is outside the moving-packet theorem domain, not a contradiction of the rest-frame theorem.

## Current boundaries

The following remain open:

- derive one coupled gauge-spinor-Hartree action;
- select its dimensionless coupling map;
- construct a stable charged stationary branch;
- construct a Foldy--Wouthuysen packet position projection;
- construct a covariant local packet T-BMT law;
- derive the anomalous moment;
- calibrate physical charge, moment, force, length, time, and mass units;
- execute withheld external predictions.

Magnetic moment/spin, electric force, and magnetic force remain partial. The matrix remains `7 validated / 13 partial / 1 negative`.

## Next critical target

M9.100 should derive one coupled gauge-spinor-Hartree action and its dimensionless parameter map, then solve for a stable charged stationary branch using the M9.99 odd-grid differential complex before repeating pair force and spin studies.
