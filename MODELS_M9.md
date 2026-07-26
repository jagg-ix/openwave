# OpenWave M9 CAT/EPT comparison profile

The canonical conformance profile is `model_conformance_m105.py`, schema v20. The canonical registration is `model_registration_m105.py`, schema v11.

Lean theorem status, source identity, implementation, numerical closure, state construction, physical identity, calibration, prediction readiness, and external evidence remain separate layers.

## Baseline maturity before M9.103--M9.105 execution

| Headline | Count |
| --- | ---: |
| Validated in scope | 7 |
| Conditional validated | 5 |
| Reduced-model validated | 3 |
| Calibration pending | 1 |
| Candidate | 4 |
| Negative | 1 |
| **Total** | **21** |

The M9.103--M9.105 runner derives any state or calibration changes from the actual sub-gates. This document does not predetermine those outcomes.

## Current authorities

```text
OpenWave base  ca40b8648fcb02c23e56951f08c9988c24e763ab
Physlib        eba0124fcfbc1216d973bb6f504c5a6d324de60c
zil-lean       e09723a44185a1e70031ad2661c8009dc98bef74
```

The current Physlib physics surfaces retain the integrated action, T-BMT scalar/rest-frame grounding, Coulomb/radiation-gauge interfaces, G-free mass/variance maps, clock identities, Yukawa inversion, and evidence-governance modules. `zil-lean` retains the same `Zil` and `Zil.Native` root blobs while adding a Make-driven `ZIL-EXAMPLES-REPORT/1` harness.

## M9.103 -- unrestricted charged state

`unrestricted_charged_stationary.py` uses the winding projection only to prepare initial data. It then evolves the complete two-component spinor without projection. Three tilted/anisotropic seeds are compared using:

- the full stationary residual;
- measured winding and lower-component fraction;
- action monotonicity and cross-seed distance;
- exact-periodic Maxwell constraints;
- spin-tilt, quadrupole, and phase-chirp real-time tubes.

Campaign passage means the audit executes. `unrestricted_stationary_state_constructed` and `unrestricted_orbital_stability_qualified` are the state gates.

## M9.104 -- refined packet Thomas--BMT

`packet_tbmt_refinement.py` registers the covariant Thomas equation as an explicit external postulate, not as a QED derivation. It compares the pointwise packet torque and finite-time Maxwell--Dirac response with the exact initial Dirac generator on `16^3` and `20^3` grids at time steps `0.004` and `0.002`.

The refined packet gate is reported dynamically and cannot advance the state axis by itself.

## M9.105 -- independent calibration

`independent_calibration_protocol.py` audits `sigma0`, clock frequency, mass, charge unit, and force unit. Internal, derived, absent, circular, or target-fitted anchors are rejected as independent calibration.

Three predictions are preregistered with explicit failure rules:

- Newton coupling from an independently measured inference width;
- clock/mass consistency on a withheld physical state;
- electric and magnetic force scales across withheld separations.

The current default anchors do not close independent calibration, so these predictions remain unexecuted unless an external bundle passes the audit.

## Run

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_103_unrestricted_charged_stationary.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_104_packet_tbmt_refinement.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_105_independent_calibration.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_105_current_registration.py
```

## Current authority surfaces

- `formalization_m105_extension.py`;
- `zil_runtime_reporting_m105.py`;
- `unrestricted_charged_stationary.py`;
- `packet_tbmt_refinement.py`;
- `independent_calibration_protocol.py`;
- `m103_105_evidence_authority.py`;
- `criterion_maturity_m105.py`;
- `model_conformance_m105.py`;
- `model_registration_m105.py`;
- `research/zil/m9_103_105_scientific_closure.zc`;
- `M9_SCIENTIFIC_CLOSURE.md`.

## Remaining critical targets

1. extend weak-field gravity to constraint-preserving nonlinear metric evolution;
2. replace reduced antimatter, strong-force, and weak-force controls with full coupled-field campaigns;
3. advance dark matter and composite candidates through stable dynamical states;
4. execute frozen external predictions only after independent calibration closes.
