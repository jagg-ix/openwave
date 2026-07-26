# OpenWave M9 CAT/EPT comparison profile

The canonical conformance profile is now `model_conformance_m101.py`, schema v18. The canonical registration is `model_registration_m101.py`, schema v9.

Lean theorem status, ZIL orchestration, numerical carrier identity, state construction, physical identity, calibration, and prediction readiness remain separate layers.

## Evidence-derived maturity

| Headline | Count |
| --- | ---: |
| Validated in scope | 7 |
| Conditional validated | 5 |
| Reduced-model validated | 3 |
| Calibration pending | 1 |
| Candidate | 4 |
| Negative | 1 |
| **Total** | **21** |

The old `7 validated / 13 partial / 1 negative` table remains compatibility metadata only.

## Current formal authority

```text
repository   jagg-ix/entropic-physlib-private
branch       entropic-physlib-linear-full
head         acdbe8ce6456e66837bd18604cf3107d3181c4de
Physlib.lean cf0c719c3249c48174df8923380287bcaf33f04b
```

M9.101 recognizes exact current blobs for:

- the global integrated electrogravitic action;
- the coupled metric/gauge/entropic derivative interface;
- the metric-built entropic-dynamics Einstein--Maxwell capstone;
- the G-free relations `G = hbar*c/m²` and `G = hbar*c*sigma0⁴`;
- clock relative entropy, clock/action-rate, and Yukawa isolation;
- gauge-invariant Pauli tensor coupling;
- T-BMT coefficients, magic cancellation, and rest-frame QED grounding;
- Schrödinger/Ehrenfest curved gauge-density interfaces;
- epistemically typed derived-prediction auditing.

The global action data still requires an explicit physical density and derivative identification. The Newton coupling remains conditional on the Compton-cell model and an independently fixed `sigma0`. The covariant Thomas equation remains imported physical dynamics rather than a QED derivation.

## M9.101 coupled action

`coupled_gauge_spinor_hartree_action.py` implements one finite periodic action with:

- gauge-covariant spinor kinetic energy;
- local cubic--quintic interaction;
- eliminated electrostatic self-energy;
- Newton/Hartree self-energy;
- transverse magnetic energy;
- Pauli spin coupling.

It includes an action/Hamiltonian directional audit and a normalized winding-three symmetry-sector solver. The solver outcome is reported dynamically. A symmetry-reduced candidate is not relabeled as unrestricted charged-particle stability.

## M9.101 packet spin

`covariant_packet_tbmt.py` replaces the averaged rest-frame magnetic shadow with a local packet integral:

```text
beta(x) = j_D(x)/rho(x)
gamma(x) = 1/sqrt(1-|beta(x)|²)
rate = integral [Omega_BMT(x) cross s(x)] d³x
```

Pair and self-field-control torques are subtracted before comparison with the exact Dirac-generator spin rate. Improvement over the old rest-frame shadow and numerical closure are separate decisions.

## M9.101 clock/action calibration

`clock_action_rate_calibration.py` uses the preregistered stationary-branch frequency to derive one internal natural-unit map:

```text
m_clock = hbar*omega/c²
y = sqrt(2)*hbar*omega/(c²*v)
action rate = hbar*omega
```

One entropy-action normalization is determined on the derivation grid and transported without refitting across the held-out grids. The nonconstant entropy-rate modulation is retained as a residual. This is not external clock or mass calibration.

## M9.101 weak-field electrogravity

`electrogravitic_weak_field_evolution.py` closes one executable source chain:

```text
spinor
 -> charge/current
 -> Maxwell E,B
 -> matter + EM gravitational source
 -> Newton potential
 -> weak g00
 -> next Schrödinger step
```

The campaign checks Maxwell constraints, weak Einstein-00/Poisson closure, norm and charge, metric signature, and probe-mass cancellation. It is not a nonlinear four-dimensional Einstein Cauchy development.

## Maturity-axis updates

| Criterion | M9.101 update |
| --- | --- |
| de Broglie clock | internal calibration becomes partial |
| magnetic moment and spin | reduced state construction and packet adapter |
| electric force | reduced state construction from one coupled action |
| magnetic force | reduced state construction and local packet torque adapter |
| gravity | reduced end-to-end weak-field evolution |

All five remain `conditional_validated`: physical identity, independent calibration, and external validation are not inferred.

## Current authority surfaces

- `formalization_m101_extension.py`;
- `coupled_gauge_spinor_hartree_action.py`;
- `covariant_packet_tbmt.py`;
- `clock_action_rate_calibration.py`;
- `electrogravitic_weak_field_evolution.py`;
- `m101_evidence_authority.py`;
- `criterion_maturity_m101.py`;
- `model_conformance_m101.py`;
- `model_registration_m101.py`;
- `research/zil/m9_101_coupled_physics.zc`.

## Remaining critical targets

1. establish unrestricted charged stationary stability without winding/spin projection;
2. derive or explicitly postulate the covariant Thomas extension and close it across refined packet carriers;
3. fix `sigma0`, clock, mass, Yukawa, charge, and force maps independently;
4. extend weak-field gravity to constraint-preserving nonlinear metric evolution;
5. freeze all maps before preregistered external prediction tests.
