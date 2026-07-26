# OpenWave M9 evidence integrity

M9.102 completes three audit targets discovered after merged PR #92.

## Authority split

PR #92 is reproduced against the exact historical formal pin:

```text
OpenWave   fe9c98a94a0f233c9dda842fa144ae181d01c9e5
Physlib    acdbe8ce6456e66837bd18604cf3107d3181c4de
```

The live `entropic-physlib-linear-full` authority is now:

```text
Physlib    eba0124fcfbc1216d973bb6f504c5a6d324de60c
```

The live head is six commits beyond the PR #92 pin. Historical reproduction and current branch verification are separate operations.

## New formal evidence-governance surfaces

The current formal head adds:

- `Physlib.Meta.ClaimMaturity` — six independent axes, prerequisite coherence, derived levels, assertion honesty, and witness-backed formal closure;
- `Physlib.Meta.EvidenceIntegrity` — falsification/supersession checks, structured numerical gates, and internal-versus-external evidence classification;
- `Physlib.Meta.TheoremIntentAudit` — on-demand comparison of declared theorem abstraction levels with `formalizes` and `supported_by` graph edges.

These modules improve evidence governance. They do not create a new OpenWave numerical result or physical prediction.

## Carrier versus state

An implemented equation, solver, or adapter is recorded separately from state existence.

For magnetic moment, electric force, and magnetic force:

- the finite coupled action can be implemented;
- the winding-sector solver can execute;
- the packet T-BMT adapter can execute;
- the state axis remains `not_constructed` unless the symmetry-reduced stationary-state gate passes;
- unrestricted stability remains a separate gate.

This replaces the M9.101 convention that assigned `reduced_constructed` whenever the action campaign existed.

## Quantitative snapshot contract

Run:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_102_reproduce_m101.py \
  --write build/m9_101_snapshots
```

The command writes:

```text
m9_101_coupled_action.json
m9_101_packet_tbmt.json
m9_101_clock_calibration.json
m9_101_weak_field_gravity.json
m9_101_manifest.json
```

Verify the bundle independently:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_102_reproduce_m101.py \
  --verify build/m9_101_snapshots
```

The manifest contains:

- exact component schemas;
- SHA-256 of every full component payload;
- the historical and current formal heads;
- a compact quantitative summary;
- campaign-level passage;
- stationary, packet-reduction, external-calibration, and full-Einstein sub-gates.

A campaign may pass while a nested physical sub-gate fails. The manifest preserves both values and never substitutes one for the other.

## Current schemas

```text
openwave.m9.formalization-m102-extension.v1
openwave.m9.criterion-maturity.v4
openwave.m9.m101-reproducibility-manifest.v1
openwave.m9.models-conformance.v19
openwave.model-registration.v10
```

## Retained boundaries

M9.102 does not establish:

- unrestricted charged stationary stability;
- packet T-BMT closure;
- a QED derivation of the covariant Thomas extension;
- external clock, mass, charge, moment, or gravity calibration;
- nonlinear four-dimensional Einstein evolution;
- external experimental validation.
