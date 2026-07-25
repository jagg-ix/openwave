# OpenWave M9 CAT/EPT comparison profile

The canonical physics profile remains `openwave/xperiments/m9_cat_ept/model_conformance_dynamics.py`. The current canonical registration is now `model_registration_zil.py`, which adds the M9.98 ZIL runtime authority without changing any of the 21 criterion rows.

Platform validation, Lean theorem status, ZIL runtime/orchestration status, physical identity, calibration, and external validation remain separate layers.

## Platform summary after M9.98

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 7 |
| ⚠️ partial / bounded | 13 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

Validated rows remain charge quantization, particle stability, spin-1/2 statistics, source-free Maxwell waves, free massive Klein--Gordon evolution, dimensionless Coulomb orbital quantization, and the explicit dimensionless thermal field. The sole criterion-level negative remains the predictive lepton-mass hierarchy.

## Formal proof authority

```text
repository   jagg-ix/entropic-physlib-private
branch       entropic-physlib-linear-full
base commit  e10af9a3b47bf90afc0a88167a5d495b6935f4dc
current tree 239a663a3192a3144fb998e7bb200e09689a3bb9
Physlib.lean 182a06e0f50314ec54436da602b4ac86eba4ee08
```

| Imported surface | Count |
| --- | ---: |
| formalization/status ZIL graphs | 11 |
| graph entity identifiers | 422 |
| explicit open/external boundaries | 12 |
| branch-wide Lean aggregate/source files | 24 |
| M9.96 Pauli/Maxwell extension sources | 2 |
| M9.97 dynamics extension sources | 3 |

Lean remains proof authority. ZIL records and evaluates orchestration, dependencies, source links, statuses, queries, contracts, and audits; it does not turn graph presence into a theorem.

## M9.98 ZIL runtime authority

The previous M9 evidence carried two old ZIL revisions:

```text
f39758f85ee6300b8060e4f8ea1ecf344ed32c96
64462a3c5e2ffb51a7b226675491cc3a9b156a8d
```

They are retained as historical pins only. Current authority is:

```text
repository  jagg-ix/zil-lean
branch      main
head        3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc
```

Current `zil-lean` has two explicit public roots:

| Import root | Consumer | Surface |
| --- | --- | --- |
| `Zil` | PhysLib embedded formalization | `Zil.Datalog` clause logic, compatibility aliases, attachments, embedded validation, tactics, theorem intents, file contracts, witness/abstraction checks |
| `Zil.Native` | OpenWave native `.zc` programs | facts, theorem-shaped rules, parser, queries, provenance, workflow, authorization, impact, proof/theorem/recovery audits |

The latest package builds both roots as default library targets. OpenWave validates them in separate Lean smoke modules so compatibility aliases cannot silently replace native types.

### Exact runtime controls

| Source | Blob |
| --- | --- |
| `Zil.lean` | `faf28e701e4a02781e410491a6d3daf5d47f8879` |
| `Zil/Native.lean` | `2e6c87a85ef2f80d2424c8251ffe524067e27dee` |
| `Zil/Datalog/Compat.lean` | `d72fd52996eb2418037ed329b97c280e2f187b1a` |
| `Zil/Datalog/FormalizationContract.lean` | `b5753801f2564f17a684a1d8da77bc3b024e7c0a` |
| `lakefile.lean` | `8dc0dd81f8c3d80192f9467792a617fde5ec24b5` |
| real PhysLib native-arc example | `91ec7daf0dd351e5de480149b77eea903a472ea3` |

The M9.94--M9.97 native graph blobs are also pinned. Head, runtime-source, or graph drift fails closed. The runtime fingerprint is independent of the PhysLib formalization-tree fingerprint.

## Retained M9.97 physics result

### Gauge-spinor stationarity

```text
initial residual 0.5071084764
final residual   0.5190695504
final radius     1.5835697888
final spin z     0.4999999088
```

Winding, exact-third charge, normalization, localization, spin one-half within `2e-7`, and Maxwell constraints close. The stationary residual does not.

### Four-spinor momentum and center response

```text
Lorentz momentum rate            0.001645074525562959
Maxwell-Dirac momentum rate      0.0016022176381169852
relative momentum error          2.61 percent
center acceleration             -0.0002424759822742363
center/Lorentz relative mismatch 114.74 percent
```

Kinetic-momentum transfer closes. The center response has the wrong sign.

### Spin response

```text
finite-time spin rate y       1.45073921e-4
Dirac-generator rate y        1.45128373e-4
generator relative error      2.57 percent
rest-frame T-BMT rate y      -8.69424870e-5
rest-frame relative mismatch 266.90 percent
```

The exact numerical generator is integrated consistently. The moving finite-size winding packet does not reduce to the rest-frame T-BMT torque.

## Current three-row status

| Criterion | Closed subreduction | Promotion blocker |
| --- | --- | --- |
| Magnetic moment and spin | field-derived moment/response and exact-generator spin evolution | no stationary charged spinor; rest-frame/covariant BMT reduction, anomaly, identity, and calibration open |
| Electric force | M9.96 force triangle and four-spinor momentum/Lorentz agreement | center response has wrong sign; no stable charged pair or unit map |
| Magnetic force | field-derived magnetic contribution and exact-generator precession | moving-packet torque law, stable pair, and common moment/force calibration open |

All three remain **partial**. The ZIL upgrade promotes none of them.

## Current authority surfaces

- `zil_runtime_upgrade.py`;
- `model_registration_zil.py`;
- `research/lean/M9ZilDatalogSurface.lean`;
- `research/lean/M9ZilNativeSurface.lean`;
- `research/zil/m9_98_zil_runtime_upgrade.zc`;
- retained M9.97 dynamics and calibration authorities.

## Explicit retained boundaries

- independently varied coupled gauge-spinor action;
- stable charged spinorial stationary branch;
- converged relation between kinetic momentum and center motion;
- covariant moving-packet spin and torque law;
- anomalous-moment derivation;
- physical charge, moment, force, mass, length, and time calibration;
- global nonlinear coupled-action and Cauchy-development boundaries;
- continuum open-system and constructive-QFT boundaries;
- withheld external predictions.

The matrix remains `7 validated / 13 partial / 1 negative`. The next critical target is M9.99: an independently varied coupled action that can produce a stable charged spinorial branch and derive both center and covariant spin dynamics from the same equations.
