# OpenWave M9 maturity profile

The historical `7 validated / 13 partial / 1 negative` table is retained for compatibility only. It is not the current primary assessment.

M9 derives one headline from six independent axes for every criterion:

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
| Conditional validated | 5 | Strong formal/numerical closure exists, but theorem scope, unrestricted state existence, physical identity, or external calibration blocks the full named claim. |
| Reduced-model validated | 3 | The reduced carrier closes its declared test; the full coupled field model remains open. |
| Calibration pending | 1 | A stable dimensionless state exists, but the named physical quantity is not independently predicted. |
| Candidate | 4 | Structural or variational ingredients exist without the required dynamical state or prediction. |
| Negative | 1 | A preregistered predictive test failed. |
| **Total** | **21** | |

## M9.101 evidence-axis updates

M9.101 does not change the six headline counts. It closes missing internal axes for the five conditional rows:

| Criterion | M9.101 axis update | Remaining boundary |
| --- | --- | --- |
| de Broglie clock | calibration `open -> partial`; action/Yukawa/entropy normalization frozen across held-out grids | physical Zitterbewegung identity and external clock/mass calibration |
| Magnetic moment and spin | state `not_constructed -> reduced_constructed`; finite coupled action and local packet T-BMT adapter | unrestricted charged stability, numerical packet-TBMT closure if not achieved, QED derivation of covariant Thomas extension, anomaly and calibration |
| Electric force | state `not_constructed -> reduced_constructed`; finite coupled action and winding-sector solver | unrestricted stable charged pair, physical charge/force units, external multi-distance validation |
| Magnetic force | state `not_constructed -> reduced_constructed`; finite action and local packet torque adapter | unrestricted stable spinorial pair, QED-covariant extension, anomaly and moment/force calibration |
| Gravity | state `candidate -> reduced_constructed`; one-state weak-field Schrodinger-Maxwell-Poisson metric evolution | independent `sigma0`, nonlinear four-dimensional Einstein Cauchy development and calibrated predictions |

The exact pass/fail outcomes for the symmetry-reduced stationary gate and local packet-TBMT gate are stored in `m101_evidence_authority.py`; they are not encoded as predetermined labels.

## Resolution of the legacy 13 partial rows

| Criterion | Current headline | Closed | Principal remaining boundary |
| --- | --- | --- | --- |
| Electron rest energy | Calibration pending | localized branch, scale, binding candidate | independent mass prediction and shared energy/length map |
| de Broglie clock | Conditional validated | scoped theorem, internal clock tests, action-rate and entropy normalization | physical clock identity and external calibration |
| Magnetic moment and spin | Conditional validated | `Jz=1/2`, tree-level `g=2`, moment response, Dirac generator, finite action, packet adapter | unrestricted charged state, covariant/QED closure, anomaly and calibration |
| Antimatter and annihilation | Reduced-model validated | opposite-sector capture, reduced annihilation, radiation ledger | unassisted full coupled-PDE annihilation |
| Dark matter | Candidate | neutral variational candidate | stability, production, abundance, phenomenology |
| Quarks | Candidate | finite SU(3), singlet, Wilson-loop, fractional-charge and CKM controls | dynamical QCD, confinement, running coupling, spectrum |
| Baryons | Candidate | charged-triplet graph and ledgers | three-body field state and proton/neutron spectrum |
| Mesons | Candidate | neutral-pair graph and ledgers | two-body field state, flavor dynamics, spectrum and decays |
| Electric force | Conditional validated | Gauss closure, force triangle, momentum/Lorentz agreement, finite action and reduced charged state | unrestricted stable pair, physical unit map and external test |
| Magnetic force | Conditional validated | magnetization/Ampere closure, magnetic force, generator evolution, finite action and packet adapter | unrestricted pair, QED-covariant torque, anomaly and calibration |
| Strong force | Reduced-model validated | Cornell, flux-tube and string-breaking controls | dynamical Yang-Mills/QCD and joint predictions |
| Weak force | Reduced-model validated | left-selective transitions and reduced decay ledger | electroweak gauge dynamics and calibrated rates |
| Gravity | Conditional validated | formal global-action interface, G-free coupling map, weak-field source/evolution chain | independent coupling selection, nonlinear metric evolution and calibration |

## Policy

The canonical model does not:

- require `7/13/1` as an acceptance condition;
- require equality with a fixed promoted-key set;
- treat the legacy scalar status as evidence authority;
- promote a symmetry-reduced state to unrestricted stability;
- promote an imported BMT law to a QED derivation;
- promote internal calibration to external validation;
- promote weak-field gravity to a nonlinear Einstein development.

## Current implementation

- `criterion_maturity_current.py`: base six-axis precedence;
- `criterion_maturity_m101.py`: campaign-driven M9.101 axis updates;
- `model_conformance_m101.py`: schema-v18 canonical conformance;
- `model_registration_m101.py`: schema-v9 canonical registration;
- `m101_evidence_authority.py`: exact campaign outcomes and boundaries;
- `research/zil/m9_101_coupled_physics.zc`: dependency, maturity, and no-promotion graph;
- `M9_COUPLED_PHYSICS.md`: public coupled-target profile.

No physical identity, externally calibrated parameter, or independent experimental prediction is created by these internal closures.
