# OpenWave M9 maturity profile

The historical `7 validated / 13 partial / 1 negative` table is retained for compatibility only. It is not the current primary assessment.

M9.100 derives one headline from six independent axes for every criterion:

- formal theorem status;
- numerical closure;
- state construction;
- physical identity;
- calibration;
- prediction readiness.

## Current headline summary

| Headline | Count | Meaning |
| --- | ---: | --- |
| Validated in scope | 7 | The literal dimensionless or algebraic criterion closes; broader physical interpretation can remain open. |
| Conditional validated | 5 | Strong formal/numerical closure exists, but theorem scope, state existence, physical identity, or calibration blocks the full named claim. |
| Reduced-model validated | 3 | The reduced carrier closes its declared test; the full coupled field model remains open. |
| Calibration pending | 1 | A stable dimensionless state exists, but the named physical quantity is not independently predicted. |
| Candidate | 4 | Structural or variational ingredients exist without the required dynamical state or prediction. |
| Negative | 1 | A preregistered predictive test failed. |
| **Total** | **21** | |

## Resolution of the legacy 13 partial rows

| Criterion | Current headline | Closed | Principal remaining boundary |
| --- | --- | --- | --- |
| Electron rest energy | Calibration pending | localized branch, scale, binding candidate | independent mass prediction and shared energy/length map |
| de Broglie clock | Conditional validated | scoped entropic/proper-time theorem and internal clock tests | physical Zitterbewegung identity and external calibration |
| Magnetic moment and spin | Conditional validated | `Jz=1/2`, tree-level `g=2`, current/response moment, Dirac-generator evolution | stable charged spinor, anomaly, covariant packet law, calibration |
| Antimatter and annihilation | Reduced-model validated | opposite-sector capture, reduced annihilation, radiation ledger | unassisted full coupled-PDE annihilation |
| Dark matter | Candidate | neutral variational candidate | stability, production, abundance, phenomenology |
| Quarks | Candidate | finite SU(3), singlet, Wilson-loop, fractional-charge and CKM controls | dynamical QCD, confinement, running coupling, spectrum |
| Baryons | Candidate | charged-triplet graph and ledgers | three-body field state and proton/neutron spectrum |
| Mesons | Candidate | neutral-pair graph and ledgers | two-body field state, flavor dynamics, spectrum and decays |
| Electric force | Conditional validated | Gauss closure, force triangle, inverse-square law, action-reaction, momentum/Lorentz agreement | stable charged pair, single action, physical unit map |
| Magnetic force | Conditional validated | magnetization current, Ampere closure, magnetic force and Dirac-generator evolution | stable spinorial pair, covariant torque, anomaly, calibration |
| Strong force | Reduced-model validated | Cornell, flux-tube and string-breaking controls | dynamical Yang-Mills/QCD and joint predictions |
| Weak force | Reduced-model validated | left-selective transitions and reduced decay ledger | electroweak gauge dynamics and calibrated rates |
| Gravity | Conditional validated | weak-field/equivalence controls, Einstein-Maxwell-entropic interfaces, metric-curvature and conservation structure | one end-to-end coupled evolution and calibrated predictions |

## Policy change

The canonical model no longer:

- requires `7/13/1` as an acceptance condition;
- requires equality with a fixed `PROMOTED_KEYS` set;
- treats the legacy scalar status as evidence authority;
- interprets a maturity reclassification as physical identification or calibration.

The previous scalar profile remains embedded as compatibility metadata so older reports and consumers continue to load.

## Current implementation

- `criterion_maturity.py`: complete six-axis evidence records;
- `criterion_maturity_current.py`: current precedence and headline derivation;
- `model_conformance_maturity_current.py`: schema-v17 canonical maturity profile;
- `model_registration_maturity_current.py`: schema-v8 canonical registration;
- `research/zil/m9_100_multi_axis_maturity.zc`: dependency and policy graph;
- `tests/test_m9_criterion_maturity.py`: axis/headline and anti-freeze regressions;
- `tests/test_m9_maturity_registration.py`: profile and registration checks.

No physical identity, calibrated parameter, or external prediction is created by this reclassification.
