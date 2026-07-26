# OpenWave M9 maturity profile

The historical `7 validated / 13 partial / 1 negative` table is compatibility metadata only. The current assessment derives one headline from six independent axes:

- formal theorem status;
- numerical closure;
- state construction;
- physical identity;
- calibration;
- prediction readiness.

Implementation evidence remains separate. A solver or postulate can exist without the corresponding state, derivation, calibration, or prediction gate passing.

## M9.102 baseline

| Headline | Count |
| --- | ---: |
| Validated in scope | 7 |
| Conditional validated | 5 |
| Reduced-model validated | 3 |
| Calibration pending | 1 |
| Candidate | 4 |
| Negative | 1 |
| **Total** | **21** |

M9.103--M9.105 derive any changes from executable sub-gates. No new count is hardcoded.

## M9.103--M9.105 axis rules

| Criterion | New executable evidence | Axis advancement rule | Retained boundary |
| --- | --- | --- | --- |
| Magnetic moment and spin | unrestricted coupled descent, orbital tubes, refined packet spin | `reduced_constructed` only after unrestricted stationarity; `stable_constructed` only after orbital stability | QED derivation, anomaly, identity, calibration |
| Electric force | same unrestricted charged carrier | state advances only on the charged-state gates | common physical unit map and withheld force test |
| Magnetic force | unrestricted carrier plus refined packet torque | state follows charged-state gates; packet refinement is separate numerical evidence | QED-covariant derivation, anomaly, calibration |
| Electron rest energy | independent-anchor dependency audit | calibration advances only after an external shared bundle closes | withheld rest-energy prediction |
| de Broglie clock | independent clock/mass anchor audit | internal mode identities cannot produce `calibrated` | physical clock identity and external prediction |

The covariant Thomas equation is registered as `explicit-external-postulate`. It is not counted as a QED-derived formal closure.

## Authorities

```text
Physlib   eba0124fcfbc1216d973bb6f504c5a6d324de60c
zil-lean  e09723a44185a1e70031ad2661c8009dc98bef74
```

The current ZIL commit changes example execution and reporting, not root semantics or proof authority.

## Independent calibration rule

The shared calibration gate requires independent support for:

- inference width `sigma0`;
- clock frequency;
- mass;
- charge unit;
- force unit.

A target-dependent fit, missing dependency, dependency cycle, internal simulation value, or algebraically derived value cannot count as independent calibration. Preregistered predictions remain unexecuted until the gate closes.

## Current implementation

- `unrestricted_charged_stationary.py` -- unrestricted stationarity and orbital gates;
- `packet_tbmt_refinement.py` -- explicit Thomas postulate and grid/time refinement;
- `independent_calibration_protocol.py` -- external-anchor and prediction protocol;
- `zil_runtime_reporting_m105.py` -- current ZIL source/report authority;
- `m103_105_evidence_authority.py` -- campaign and physical-subgate composition;
- `criterion_maturity_m105.py` -- outcome-driven maturity v5;
- `model_conformance_m105.py` -- schema v20;
- `model_registration_m105.py` -- schema v11;
- `M9_SCIENTIFIC_CLOSURE.md` -- public execution guide.

No physical identity, calibrated parameter, QED covariant derivation, or external validation is inferred from campaign execution alone.
