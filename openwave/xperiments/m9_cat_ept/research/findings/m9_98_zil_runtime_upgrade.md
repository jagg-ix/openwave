# M9.98 method note: ZIL runtime upgrade

## Reason for the upgrade

OpenWave carried two older `jagg-ix/zil-lean` revisions in its M9 evidence:

```text
f39758f85ee6300b8060e4f8ea1ecf344ed32c96  installation/bootstrap era
64462a3c5e2ffb51a7b226675491cc3a9b156a8d  durable-control-event era
```

Those revisions predate the repaired compiling native Lean stack and the unification of the PhysLib clause-logic surface with the current repository. The canonical runtime is now pinned to:

```text
repository  jagg-ix/zil-lean
branch      main
head        3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc
```

The change is architectural rather than cosmetic. Between the M9.63 pin and the current revision, ZIL added or repaired:

- a compiling native Lean stack;
- a green Lean and legacy example/test surface;
- source bundles and versioned installation lifecycle;
- the complete clause-logic/Datalog core consumed by PhysLib;
- generated formalization snapshots;
- a real PhysLib formalization-arc example.

## Dual-root contract

Current `zil-lean` intentionally has two public default build roots.

### `import Zil`

This is the PhysLib-facing Datalog root. It provides:

- `zil attach` declaration attachments;
- `zil_claim`, `zil_requires`, `zil_level`, and related attributes;
- `#zil_validate_embedded`;
- `zil_solve` and `zil_apply`;
- `Holds` and clause-logic semantics;
- theorem intents;
- file contracts with abstraction levels, executable requirements, witness levels, and forbidden-substitute checks;
- compatibility aliases such as `Zil.Program` for the Datalog program type.

It is not the standalone native query/provenance engine.

### `import Zil.Native`

This is the explicit native knowledge-system root. It provides:

- facts and theorem-shaped rules;
- native program parsing;
- query execution;
- derivation/provenance traces;
- workflows;
- authorization and impact analysis;
- proof-obligation, theorem, and recovery audits;
- exchange/control-plane services.

OpenWave `.zc` graphs are assigned to this root.

The two roots are tested in separate Lean smoke fixtures. They are not imported implicitly or combined in one fixture, preventing compatibility aliases from masking native types.

## Exact pinned surfaces

| Surface | Blob |
| --- | --- |
| `Zil.lean` | `faf28e701e4a02781e410491a6d3daf5d47f8879` |
| `Zil/Native.lean` | `2e6c87a85ef2f80d2424c8251ffe524067e27dee` |
| `Zil/Datalog/Compat.lean` | `d72fd52996eb2418037ed329b97c280e2f187b1a` |
| `Zil/Datalog/FormalizationContract.lean` | `b5753801f2564f17a684a1d8da77bc3b024e7c0a` |
| `lakefile.lean` | `8dc0dd81f8c3d80192f9467792a617fde5ec24b5` |
| PhysLib native-arc example | `91ec7daf0dd351e5de480149b77eea903a472ea3` |

The `lakefile.lean` default library roots are exactly `Zil` and `Zil.Native`.

## OpenWave graph assignment

The following graphs are exact-blob pinned to `Zil.Native`:

| Graph | Blob |
| --- | --- |
| M9.94--M9.95 formalization/spin/force | `d2952ca95134e67ff3cf37a46df4d630e9eb0aa1` |
| M9.96 charged-source/force | `19eef18ae3869c7165e1a7880e97e3702c9015b5` |
| M9.97 gauge-spinor dynamics | `261de47286a0c1c7c4c4369dd8b2973b813a50a8` |
| M9.98 runtime migration graph | `7efb843b62c48087853cc83fead2e9fb8cdda33d` |

The M9.98 graph is self-describing: it declares its own native-root role, while its exact blob is pinned externally by `zil_runtime_upgrade_current.py`. This avoids an impossible self-hash fixed point.

PhysLib embedded ZIL declarations remain on the `Zil` Datalog root. The imported 11-graph formalization inventory remains a declaration/status inventory and is not reclassified as native proof evidence.

## Fail-closed behavior

The base `zil_runtime_upgrade.py` validates the upstream runtime and the three pre-upgrade OpenWave graphs. The current `zil_runtime_upgrade_current.py` additionally validates the self-describing M9.98 graph. Together they reject:

- a different observed ZIL commit;
- a missing or changed upstream runtime blob;
- a missing or changed OpenWave graph blob;
- an implicit or reversed root assignment;
- treating either historical pin as current authority.

The runtime fingerprint is independent of the PhysLib formalization-tree fingerprint. This allows either dependency to evolve without silently rewriting the other evidence layer.

## Status impact

The ZIL upgrade improves orchestration, parsing, queries, provenance, and formalization-contract validation. It does not prove a Lean theorem and does not change any physical simulation result.

The M9 matrix remains:

```text
7 validated
13 partial
1 negative
```

Magnetic moment/spin, electric force, and magnetic force remain partial for the same M9.97 model reasons: no charged stationary spinor, wrong-sign center response, and failure of the rest-frame T-BMT reduction on the moving winding packet.

## Validation limitation

The execution container still cannot resolve `github.com`, so a direct clone and full combined Lean/Python build are not claimed. The migration is validated by exact connector-backed commit and blob inspection, deterministic Python contract tests, separate Lean smoke fixtures, and fail-closed drift tests.
