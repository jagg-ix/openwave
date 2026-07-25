# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 OpenWave comparison criteria and combines a stationary non-Gaussian branch, theorem-guided finite-grid dynamics, explicit claim boundaries, a reusable uncalibrated particle-model API, a branch-wide CAT/EPT formalization inventory, and a versioned ZIL runtime authority.

## Platform status after M9.98

- Seven criteria are validated in-platform.
- Thirteen criteria remain partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- The formalization importer pins `entropic-physlib-linear-full` by exact tree `239a663a3192a3144fb998e7bb200e09689a3bb9`, current `Physlib.lean` blob `182a06e0f50314ec54436da602b4ac86eba4ee08`, 11 ZIL graphs, 422 graph entities, 12 open/external boundaries, and 24 Lean sources.
- M9.96 adds two force-specific formal sources; M9.97 adds three dynamics sources covering rest-frame Dirac--Pauli/T-BMT precession, Coulomb/radiation-gauge particle dynamics, and a distributional point-charge Maxwell source.
- M9.98 upgrades the current ZIL authority to `jagg-ix/zil-lean` commit `3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc`.
- `import Zil` is the PhysLib-facing Datalog compatibility root. `import Zil.Native` is the native facts/rules/query/provenance/workflow root used by OpenWave `.zc` graphs.
- The older `f39758f...` and `64462a3...` revisions remain historical evidence pins, not current runtime authority.
- M9.98 changes no Lean theorem status and no physical simulation result.

Validated criteria remain:

1. charge quantization;
2. particle stability / Derrick escape;
3. spin-1/2 statistics;
4. source-free Maxwell waves;
5. free massive Klein-Gordon evolution;
6. dimensionless Coulomb orbital quantization;
7. the explicit dimensionless thermal field.

## Canonical implementation surfaces

| Surface | Path | Role |
| --- | --- | --- |
| Historical 21-row profile | `model_conformance.py` | profile through M9.95 |
| M9.96 profile | `model_conformance_current.py` | charged-source and field-force overlay |
| Current physics profile | `model_conformance_dynamics.py` | M9.97 findings with unchanged statuses |
| Historical registration | `model_registration.py` | M9.96-compatible registration |
| M9.97 registration | `model_registration_current.py` | dynamics authority before runtime upgrade |
| Current registration | `model_registration_zil.py` | schema-v5 M9.98 component with ZIL runtime authority |
| Particle kernel | `particle_model.py` | reusable state, flow, observables, and historical identity gate |
| Branch-wide formal inventory | `formalization_inventory*.py` and `formalization_import.py` | 11-graph current-tree coverage |
| Force formal overlay | `formalization_force_extension.py` | Pauli--Maxwell/current/stress witnesses |
| Dynamics formal overlay | `formalization_dynamics_extension.py` | rest-frame spin, Coulomb, gauge, and point-source witnesses |
| ZIL runtime authority | `zil_runtime_upgrade.py` and `zil_runtime_upgrade_current.py` | current commit, dual-root roles, exact blobs, graph assignments, and drift checks |
| Datalog smoke fixture | `research/lean/M9ZilDatalogSurface.lean` | validates the PhysLib-facing `Zil` root |
| Native smoke fixture | `research/lean/M9ZilNativeSurface.lean` | validates the `Zil.Native` graph runtime root |
| Gauge-spinor stationary audit | `gauge_spinor_stationary_current.py` | self-consistent Pauli equation and explicit residual failure |
| Four-spinor pair dynamics | `spinorial_pair_dynamics_authoritative.py` | source-consistent momentum, center, and spin response |
| Dynamics authority | `dynamics_evidence_authority.py` | current no-promotion identity authority |
| Dynamics calibration ledger | `physical_calibration_ledger_v3.py` | promotion and falsification rules for the three partial rows |

## M9.98 ZIL runtime contract

Current exact pin:

```text
repository  jagg-ix/zil-lean
branch      main
head        3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc
```

The default `zil-lean` library build includes both public roots:

```text
Zil
Zil.Native
```

The root roles are intentionally different:

| Root | Consumer | Responsibility |
| --- | --- | --- |
| `Zil` | PhysLib embedded formalization | Datalog semantics, compatibility aliases, attachments, theorem intents, file contracts, tactics, embedded validation |
| `Zil.Native` | OpenWave native graphs | facts, theorem-shaped rules, parsing, queries, provenance, workflow, authorization, and audits |

Six upstream runtime/build/example source blobs and four OpenWave graph blobs are pinned. Commit, source, or graph drift fails closed. The M9.98 self-describing graph is externally blob-pinned to avoid a self-hash fixed point. The formalization-tree fingerprint remains independent from the runtime fingerprint.

## Retained M9.97 measured result

```text
gauge-spinor stationary residual 0.5190695504
momentum/Lorentz error           2.61 percent
center/Lorentz mismatch          114.74 percent, wrong sign
spin/full-generator error        2.57 percent
spin/rest-frame BMT mismatch     266.90 percent
```

Momentum transfer and exact-generator spin integration close as dimensionless subreductions. Charged spinorial stationarity, center dynamics, and the moving-packet T-BMT reduction remain open.

## Current boundaries

The following remain open:

- a converged charged spinorial stationary branch;
- a center-of-energy response with the Lorentz-force sign and magnitude;
- a covariant moving-packet spin law derived from the same action;
- anomalous-moment derivation;
- physical charge, moment, force, length, time, and mass calibration;
- withheld external predictions.

Magnetic moment/spin, electric force, and magnetic force remain partial. The matrix remains `7 validated / 13 partial / 1 negative`.

## Next critical target

M9.99 should construct an independently varied coupled action whose Euler--Lagrange system supplies the stationary spinor, gauge field, momentum/center relation, and covariant spin dynamics together. Then repeat M9.97 across refined grids, time steps, boxes, separations, and spin orientations before any calibration campaign.
