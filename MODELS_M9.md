# OpenWave M9 CAT/EPT comparison profile

The canonical physics profile remains `openwave/xperiments/m9_cat_ept/model_conformance_dynamics.py`. The current canonical registration is `model_registration_reconciliation.py`, schema v6. It composes the M9.98 ZIL authority with the M9.99 formal/numerical equation, operator, mass, and observable reconciliation without changing any of the 21 criterion rows.

Platform validation, Lean theorem status, ZIL runtime/orchestration status, numerical equation identity, discretization closure, physical identity, calibration, and external validation remain separate layers.

## Platform summary after M9.99

| Status | Count |
| --- | ---: |
| validated in-platform | 7 |
| partial / bounded | 13 |
| honest negative | 1 |
| planned / not yet | 0 |
| **Explicit criteria** | **21** |

Validated rows remain charge quantization, particle stability, spin-1/2 statistics, source-free Maxwell waves, free massive Klein--Gordon evolution, dimensionless Coulomb orbital quantization, and the explicit dimensionless thermal field. The predictive lepton-mass hierarchy remains the sole criterion-level negative.

## Formal proof authority

The current equation contract reads exact source blobs from:

```text
repository  jagg-ix/entropic-physlib-private
branch      entropic-physlib-linear-full
```

It covers the current Hartree-plus-local mild-flow target, cubic--quintic coercivity and conditional stability, the self-bound Schrödinger--Newton carrier, Foldy--Wouthuysen Pauli structure, four-spinor Dirac algebra and velocity, Maxwell/continuity, rest-frame Dirac--Pauli/T-BMT, isolated Coulomb/radiation gauge, and the distributional three-dimensional point charge.

All formal and OpenWave sources referenced by the comparison are blob-pinned. Formal-source or numerical-source drift fails closed. Lean remains proof authority.

## Why the legacy M9.97 numbers were not Lean contradictions

The machine-readable equation contract records nine relations.

| Relation | Current formal side | Legacy numerical side | Classification |
| --- | --- | --- | --- |
| Binding | Newton/Hartree plus local interaction | local cubic--quintic only | formal term missing numerically |
| Coefficients | parameters with coercivity and closure hypotheses | Gaussian-reference selection | parameter mismatch |
| Mass | nonrelativistic `D = 1/(2m)` | `D = 0.65`, `m = 1` | parameter mismatch |
| Pauli equation | FW matrix carrier with relativistic, Darwin, and spin--orbit terms | nonlinear self-consistent `D_A²`, `rho`, `rho²`, `sigma.B` PDE | different carrier/equation |
| Maxwell | isolated `R³` or momentum-space `F=dA` | periodic neutralized extended source | carrier mismatch |
| Discretization | one derivative family | spectral matter plus centered Maxwell | discrete-operator mismatch |
| Dirac position | `d<x>/dt = <alpha>` | `d²<x>/dt²` versus force per norm | observable-domain mismatch |
| Spin | rest-frame vertical-field bridge | moving extended packet with averaged field | observable-domain mismatch |
| Clifford algebra | canonical Dirac matrices | same numerical matrices | exact structural overlap |

The legacy center-force and rest-frame BMT discrepancies remain useful diagnostics, but they are not counterexamples to the proved Lean statements.

## M9.99 discrete and mass reconciliation

M9.99 introduces one exact Fourier differential complex for:

- gradient;
- divergence;
- curl;
- Laplacian;
- Helmholtz projection;
- scalar and vector Poisson inversion;
- gauge-covariant matter Laplacian.

Real Maxwell fields use a `17 × 17 × 17` odd grid so there is no self-conjugate Nyquist ambiguity. The historical `16 × 16 × 16` winding seed is Fourier-resampled and normalized onto that operational grid. Even-grid real exact-Fourier derivatives fail closed rather than silently dropping an imaginary Nyquist contribution.

The reconciled mass is

```text
D     = 0.65
m_eff = 1/(2D) = 0.7692307692307692
q/m   = 2Dq
```

The kinetic operator, convective current, magnetization current, and Pauli coupling now use this same mass map.

The final stationary residual is evaluated with the exact Maxwell vector potential whose Gauss and Ampère residuals are reported, not a relaxed intermediate vector.

## Hartree boundary

The current formal target includes attractive Newton/Hartree interaction. No unique OpenWave dimensionless coupling has been derived, so the reconciled campaign exposes an explicit control sweep:

```text
G = 0.00, 0.05, 0.10
```

The zero row is the reconciled local-only control. No row is called the unique formal target, a calibrated coupling, or a physical particle.

## Correct Dirac observables

The current center observable tests

```text
d<x_i>/dt = <alpha_i>
```

for the pair, the matched self-field control, and their interaction difference. Kinetic-momentum transfer versus the Lorentz-volume force remains the force gate.

The old direct comparison `d²<x>/dt² = F/norm` is retained only as a nonrelativistic diagnostic until a Foldy--Wouthuysen packet position projection and positive-energy limit are constructed. The rest-frame T-BMT shadow is similarly outside the domain of the moving, extended, nonuniform-field packet; the full Dirac generator remains the spin-integration gate.

## Current authority surfaces

- `formal_numerical_equation_contract_current.py`;
- `compatible_discrete_geometry.py`;
- `reconciled_gauge_spinor_stationary_current.py`;
- `dirac_ehrenfest_diagnostics.py`;
- `formal_numerical_reconciliation_authority.py`;
- `model_registration_reconciliation.py`;
- `research/zil/m9_99_formal_numerical_reconciliation.zc`.

## Current three-row status

| Criterion | Retained evidence | Promotion blocker |
| --- | --- | --- |
| Magnetic moment and spin | field-derived moment/response and exact-generator spin evolution | no stationary charged spinor; covariant packet BMT, anomaly, identity, and calibration open |
| Electric force | force triangle and four-spinor momentum/Lorentz agreement | no stable charged pair, selected Hartree coupling, FW packet-center reduction, or unit map |
| Magnetic force | field-derived magnetic contribution and exact-generator precession | covariant local torque law, stable pair, and common calibration open |

All three remain **partial**.

## Explicit retained boundaries

- derive one coupled gauge-spinor-Hartree action;
- select its dimensionless coupling map;
- construct a stable charged stationary branch;
- construct a Foldy--Wouthuysen packet position projection;
- construct a covariant local packet T-BMT law;
- derive the anomalous moment;
- calibrate physical charge, moment, force, mass, length, and time units;
- complete global nonlinear coupled-action, Cauchy-development, continuum, and withheld-prediction targets.

The matrix remains `7 validated / 13 partial / 1 negative`. The next critical target is M9.100: derive one coupled gauge-spinor-Hartree action, select its dimensionless coupling map, and construct a stable charged stationary branch before repeating the force and spin campaigns.
