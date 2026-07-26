# OpenWave M9.101 coupled-physics profile

## Current authorities

```text
OpenWave main before this work
809ce9a152ac94e24a5f199db2473b5d8370f491

Physlib repository
jagg-ix/entropic-physlib-private

Physlib branch
entropic-physlib-linear-full

Physlib head
acdbe8ce6456e66837bd18604cf3107d3181c4de
```

M9.101 recognizes the current global electrogravitic action, metric-built
entropic-dynamics capstone, G-free Newton coupling, clock/action bridges,
gauge-invariant Pauli tensor coupling, and T-BMT coefficient surfaces.

## Executable campaigns

| Campaign | Constructed result | Retained boundary |
| --- | --- | --- |
| Coupled gauge-spinor-Hartree action | finite periodic action, exact field regeneration, derivative audit, winding-sector stationary solver | not the full continuum action; unrestricted stability separate |
| Packet Thomas--BMT | local velocity/gamma/E/B torque integral, self-control subtraction, Dirac-generator comparison | covariant Thomas extension imported, not QED-derived |
| Clock/action calibration | Compton/Yukawa mass identity, action rate, entropy normalization, held-out no-refit checks, Tolman reconstruction | internal natural-unit calibration, not external clock identity |
| Weak-field electrogravity | one state drives Maxwell source, gravity source, Newton potential, weak metric, and next evolution step | not nonlinear four-dimensional Einstein evolution |

## Maturity-axis changes

| Criterion | New evidence axis |
| --- | --- |
| de Broglie clock | internal calibration becomes partial |
| magnetic moment and spin | reduced state construction |
| electric force | reduced state construction |
| magnetic force | reduced state construction |
| gravity | reduced end-to-end evolution |

The five rows remain `conditional_validated`: physical identity, independent
calibration, and external prediction readiness are not inferred.

## Canonical code

```text
formalization_m101_extension.py
coupled_gauge_spinor_hartree_action.py
covariant_packet_tbmt.py
clock_action_rate_calibration.py
electrogravitic_weak_field_evolution.py
m101_evidence_authority.py
criterion_maturity_m101.py
model_conformance_m101.py
model_registration_m101.py
```

Current schemas:

```text
openwave.m9.formalization-m101-extension.v1
openwave.m9.coupled-gauge-spinor-hartree-action.v1
openwave.m9.covariant-packet-tbmt.v1
openwave.m9.clock-action-rate-calibration.v1
openwave.m9.electrogravitic-weak-field-evolution.v1
openwave.m9.m101-evidence-authority.v1
openwave.m9.criterion-maturity.v3
openwave.m9.models-conformance.v18
openwave.model-registration.v9
```
