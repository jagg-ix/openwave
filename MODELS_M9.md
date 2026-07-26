# OpenWave M9 CAT/EPT comparison profile

The canonical conformance profile is `model_conformance_m102.py`, schema v19. The canonical registration is `model_registration_m102.py`, schema v10.

Lean theorem status, formal-source identity, numerical carrier implementation, state construction, physical identity, calibration, prediction readiness, and external evidence remain separate layers.

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

The historical `7 validated / 13 partial / 1 negative` table remains compatibility metadata only.

## Formal authority

Exact reproduction of merged PR #92 uses:

```text
repository   jagg-ix/entropic-physlib-private
branch       entropic-physlib-linear-full
head         acdbe8ce6456e66837bd18604cf3107d3181c4de
Physlib.lean cf0c719c3249c48174df8923380287bcaf33f04b
```

The current live formal authority is:

```text
head         eba0124fcfbc1216d973bb6f504c5a6d324de60c
Physlib.lean 56813b617e44f1ebd2ce5716fec72db4327ed0d0
```

The six-commit update adds:

- `ClaimMaturity.lean`: six-axis maturity, prerequisite coherence, assertion honesty, and witness-backed formal closure;
- `EvidenceIntegrity.lean`: falsification/supersession consistency, structured numerical gates, and internal-versus-external evidence classification;
- `TheoremIntentAudit.lean`: on-demand comparison of theorem abstraction intents with graph support.

These are evidence-governance surfaces. They add no new OpenWave numerical result or physical identity.

## M9.101 physics campaigns

### Coupled action

`coupled_gauge_spinor_hartree_action.py` implements one finite periodic action with gauge-covariant spinor kinetic energy, local cubic--quintic interaction, electrostatic and Hartree self-energy, transverse magnetic energy, and Pauli coupling. The equation and solver are implementation evidence. The symmetry-reduced stationary-state gate and unrestricted-state gate are reported separately.

### Packet spin

`covariant_packet_tbmt.py` integrates the pointwise lab-frame BMT torque over the packet after subtracting a matched self-field control. Adapter implementation, improvement over the old rest-frame shadow, and numerical reduction closure are distinct decisions.

### Clock/action calibration

`clock_action_rate_calibration.py` transports one internal action/Yukawa/entropy normalization across held-out grids without refitting. This is internal calibration, not physical clock or mass validation.

### Weak-field electrogravity

`electrogravitic_weak_field_evolution.py` evolves one state through charge/current, Maxwell fields, a matter-plus-EM gravitational source, Newton potential, weak `g00`, and the next Schrödinger step. Weak-field passage is not nonlinear Einstein evolution.

## M9.102 evidence correction

The previous M9.101 maturity overlay assigned `reduced_constructed` to magnetic moment, electric force, and magnetic force whenever the coupled-action campaign existed. M9.102 corrects this:

- an implemented action, solver, or adapter is stored under `implementation`;
- the state axis remains `not_constructed` unless the symmetry-reduced stationary-state gate passes;
- unrestricted stability remains separate;
- gravity advances only when the weak-field state gate passes;
- all five headline classes remain `conditional_validated`.

## Quantitative reproduction

Generate a complete four-component M9.101 snapshot bundle:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_102_reproduce_m101.py \
  --write build/m9_101_snapshots
```

Verify schemas, required measurements, SHA-256 hashes, and the quantitative summary:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_102_reproduce_m101.py \
  --verify build/m9_101_snapshots
```

The manifest reports campaign passage beside the actual stationary-state, packet-reduction, external-calibration, and full-Einstein sub-gates. A top-level campaign result cannot substitute for a nested physical gate.

## Current authority surfaces

- `formalization_m102_extension.py`;
- `criterion_maturity_m102.py`;
- `m101_reproducibility_contract.py`;
- `model_conformance_m102.py`;
- `model_registration_m102.py`;
- `research/zil/m9_102_evidence_integrity.zc`;
- `M9_EVIDENCE_INTEGRITY.md`.

Historical M9.101 modules remain available for exact PR #92 reproduction.

## Remaining critical targets

1. establish unrestricted charged stationary stability without winding/spin projection;
2. derive or explicitly postulate the covariant Thomas extension and close it across refined packet carriers;
3. fix `sigma0`, clock, mass, Yukawa, charge, and force maps independently;
4. extend weak-field gravity to constraint-preserving nonlinear metric evolution;
5. freeze all maps before preregistered external prediction tests.
