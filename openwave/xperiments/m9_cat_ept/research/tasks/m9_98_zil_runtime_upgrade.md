# M9.98 task details: upgrade the ZIL runtime

## Objective

Move the current OpenWave M9 evidence authority from historical ZIL bootstrap and control-event pins to the current `jagg-ix/zil-lean` dual-root architecture, without changing formal theorem authority or physical criterion statuses.

## Current revision

```text
repository  jagg-ix/zil-lean
branch      main
head        3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc
```

Historical pins remain recorded but are not current authority:

```text
f39758f85ee6300b8060e4f8ea1ecf344ed32c96
64462a3c5e2ffb51a7b226675491cc3a9b156a8d
```

## Required root assignment

### PhysLib embedded formalization

- import root: `Zil`;
- implementation namespace: `Zil.Datalog`;
- retain compatibility aliases for existing PhysLib declarations;
- require attachments, embedded validation, theorem intents, file contracts, tactics, and `Holds` semantics.

### OpenWave native graphs

- import root: `Zil.Native`;
- require native facts/rules, parser, query engine, provenance, workflow, authorization, and audit services;
- assign M9.94--M9.98 `.zc` graphs to this root explicitly.

## Exact-source controls

Pin and validate:

- `Zil.lean`;
- `Zil/Native.lean`;
- `Zil/Datalog/Compat.lean`;
- `Zil/Datalog/FormalizationContract.lean`;
- `lakefile.lean`;
- `examples/lean/06_PhyslibFormalizationArc.lean`;
- the three pre-upgrade OpenWave M9 graph blobs;
- the self-describing M9.98 graph through an external blob pin.

## Integration targets

1. Add `zil_runtime_upgrade.py` as the base runtime authority.
2. Add `zil_runtime_upgrade_current.py` to pin the migration graph externally.
3. Add separate Datalog and native Lean smoke fixtures.
4. Add schema-v5 `model_registration_zil.py`.
5. Add deterministic and adversarial drift tests.
6. Add executable runners, ZIL migration graph, method note, and status docs.
7. Preserve the 11-graph PhysLib corpus fingerprint and M9.97 physics evidence.
8. Promote no criterion.

## Acceptance

```text
current ZIL commit matches exact pin                  required
all upstream runtime blobs match                      required
all four OpenWave graph blobs match                   required
PhysLib root is Zil / Zil.Datalog                     required
OpenWave graph root is Zil.Native                     required
both roots are default lake build roots               required
historical pins are distinct and non-current          required
self-describing graph is externally blob-pinned       required
head or blob drift fails closed                        required
M9 status remains 7 validated / 13 partial / 1 negative
physical or formal claim promotion                     forbidden
```

## Boundary

This task upgrades the compiler/runtime and evidence-orchestration layer. It does not establish a Lean theorem, a stable charged particle, calibrated physical units, or external experimental agreement.
