# OpenWave M9 maturity profile

The historical `7 validated / 13 partial / 1 negative` table is compatibility metadata only. The current assessment derives one headline from six independent axes:

- formal theorem status;
- numerical closure;
- state construction;
- physical identity;
- calibration;
- prediction readiness.

Implementation evidence is now recorded separately from those six claim axes. An equation, solver, adapter, or evolution can exist without a state-existence gate passing.

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

## M9.102 correction to M9.101

M9.101 added one finite action, one winding-sector solver, one packet T-BMT adapter, one internal clock calibration, and one weak-field gravity evolution. M9.102 separates those implementations from their nested state and physical gates.

| Criterion | Implementation evidence | State-axis rule | Remaining boundary |
| --- | --- | --- | --- |
| de Broglie clock | clock/action/Yukawa/entropy calibration campaign | calibration becomes `partial` only when the internal calibration gate passes | physical clock identity and external calibration |
| Magnetic moment and spin | coupled action, winding-sector solver, packet adapter | remains `not_constructed` unless the symmetry-reduced stationary-state gate passes | unrestricted state, packet reduction, QED covariant derivation, anomaly, calibration |
| Electric force | coupled action and winding-sector solver | remains `not_constructed` unless the symmetry-reduced stationary-state gate passes | unrestricted stable pair, physical unit map, external test |
| Magnetic force | coupled action, solver, packet torque adapter | remains `not_constructed` unless the symmetry-reduced stationary-state gate passes | unrestricted pair, packet reduction, QED covariant torque, anomaly, calibration |
| Gravity | weak-field Schrodinger-Maxwell-Poisson implementation | advances to `reduced_constructed` only when the weak-field evolution gate passes | independent `sigma0`, nonlinear Einstein development, calibration |

The five headlines remain `conditional_validated`; the correction changes evidence precision, not physical status.

## Formal authority

Exact PR #92 reproduction uses:

```text
acdbe8ce6456e66837bd18604cf3107d3181c4de
```

The live `entropic-physlib-linear-full` authority is:

```text
eba0124fcfbc1216d973bb6f504c5a6d324de60c
```

The live branch adds claim-maturity, evidence-integrity, and theorem-intent auditing. These additions improve evidence governance and create no new numerical physics evidence.

## Quantitative snapshots

M9.102 can generate and verify complete M9.101 result bundles:

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_102_reproduce_m101.py \
  --write build/m9_101_snapshots

python openwave/xperiments/m9_cat_ept/research/scripts/m9_102_reproduce_m101.py \
  --verify build/m9_101_snapshots
```

The manifest hashes every full payload and reports campaign passage beside the stationary-state, packet-reduction, external-calibration, and full-Einstein sub-gates.

## Resolution of the legacy 13 partial rows

| Criterion | Current headline | Closed | Principal remaining boundary |
| --- | --- | --- | --- |
| Electron rest energy | Calibration pending | localized branch, scale, binding candidate | independent mass prediction and shared energy/length map |
| de Broglie clock | Conditional validated | scoped theorem, internal clock tests, action-rate and entropy normalization | physical clock identity and external calibration |
| Magnetic moment and spin | Conditional validated | `Jz=1/2`, tree-level `g=2`, moment response, Dirac generator, finite-action and packet carriers | constructed charged state, covariant/QED closure, anomaly and calibration |
| Antimatter and annihilation | Reduced-model validated | opposite-sector capture, reduced annihilation, radiation ledger | unassisted full coupled-PDE annihilation |
| Dark matter | Candidate | neutral variational candidate | stability, production, abundance, phenomenology |
| Quarks | Candidate | finite SU(3), singlet, Wilson-loop, fractional-charge and CKM controls | dynamical QCD, confinement, running coupling, spectrum |
| Baryons | Candidate | charged-triplet graph and ledgers | three-body field state and proton/neutron spectrum |
| Mesons | Candidate | neutral-pair graph and ledgers | two-body field state, flavor dynamics, spectrum and decays |
| Electric force | Conditional validated | Gauss closure, force triangle, momentum/Lorentz agreement, finite-action carrier | constructed stable pair, physical unit map and external test |
| Magnetic force | Conditional validated | magnetization/Ampere closure, magnetic force, generator evolution, finite-action and packet carriers | constructed pair, QED-covariant torque, anomaly and calibration |
| Strong force | Reduced-model validated | Cornell, flux-tube and string-breaking controls | dynamical Yang-Mills/QCD and joint predictions |
| Weak force | Reduced-model validated | left-selective transitions and reduced decay ledger | electroweak gauge dynamics and calibrated rates |
| Gravity | Conditional validated | formal action interface, G-free map, weak-field source/evolution chain | independent coupling selection, nonlinear metric evolution and calibration |

## Current implementation

- `formalization_m102_extension.py`: historical/current formal-head separation and governance pins;
- `criterion_maturity_m102.py`: carrier/state separation and outcome-driven state axes;
- `m101_reproducibility_contract.py`: snapshot generation, hashing, summaries, and verification;
- `model_conformance_m102.py`: schema-v19 current conformance;
- `model_registration_m102.py`: schema-v10 current registration;
- `research/zil/m9_102_evidence_integrity.zc`: dependency and retained-boundary graph;
- `M9_EVIDENCE_INTEGRITY.md`: public audit and reproduction guide.

No physical identity, externally calibrated parameter, or independent experimental prediction is created by these evidence-integrity changes.
