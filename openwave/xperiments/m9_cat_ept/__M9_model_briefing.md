# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 OpenWave comparison criteria and combines a stationary non-Gaussian branch, theorem-guided finite-grid dynamics, explicit claim boundaries, a reusable uncalibrated particle-model API, and a branch-wide imported inventory of the CAT/EPT Lean/ZIL formalization corpus.

## Platform status after M9.97

- Seven criteria are validated in-platform.
- Thirteen criteria remain partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- The formalization importer pins `entropic-physlib-linear-full` by exact tree `239a663a3192a3144fb998e7bb200e09689a3bb9`, current `Physlib.lean` blob `182a06e0f50314ec54436da602b4ac86eba4ee08`, 11 ZIL graphs, 422 graph entities, 12 open/external boundaries, and 24 Lean sources.
- M9.96 adds two current-tree force sources; M9.97 adds three dynamics sources covering rest-frame Dirac--Pauli/T-BMT precession, Coulomb/radiation-gauge particle dynamics, and a distributional point-charge Maxwell source.
- M9.97 constructs a self-consistent gauge-covariant Pauli stationary equation and a source-consistent four-spinor Maxwell--Dirac pair/control campaign.
- Kinetic-momentum transfer agrees with the external Lorentz force within `2.61%`.
- Finite-time spin evolution agrees with the exact Dirac generator within `2.57%`.
- The gauge-spinor stationary residual remains `0.519`, the center response has the wrong Lorentz sign, and the moving winding packet does not reduce to the imported rest-frame T-BMT shadow.

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
| Current M9.97 profile | `model_conformance_dynamics.py` | dynamics findings with unchanged statuses |
| Historical registration | `model_registration.py` | M9.96-compatible registration |
| Current registration | `model_registration_current.py` | canonical M9.97 component and authority |
| Particle kernel | `particle_model.py` | reusable state, flow, observables, and historical identity gate |
| Branch-wide formal inventory | `formalization_inventory*.py` and `formalization_import.py` | 11-graph current-tree coverage |
| Force formal overlay | `formalization_force_extension.py` | Pauli--Maxwell/current/stress witnesses |
| Dynamics formal overlay | `formalization_dynamics_extension.py` | rest-frame spin, Coulomb, gauge, and point-source witnesses |
| M9.96 charged source | `charged_maxwell_source_bridge.py` | static fields and magnetic response |
| M9.96 force triangle | `field_force_triangle.py` | Lorentz/energy/stress comparison |
| Gauge-spinor stationary audit | `gauge_spinor_stationary_current.py` | self-consistent Pauli equation and explicit residual failure |
| Four-spinor pair dynamics | `spinorial_pair_dynamics_authoritative.py` | source-consistent momentum, center, and spin response |
| Dynamics authority | `dynamics_evidence_authority.py` | current no-promotion identity authority |
| Dynamics calibration ledger | `physical_calibration_ledger_v3.py` | promotion and falsification rules for the three partial rows |

## M9.97 measured result

### Gauge-spinor stationary feasibility

The winding-three candidate is embedded in a two-component Pauli field with gauge-covariant kinetic energy, selected cubic--quintic density terms, self-consistent periodic Maxwell fields, and tree-level Pauli coupling.

```text
initial stationary residual 0.5071084764
final stationary residual   0.5190695504
initial radius              1.5595442312
final radius                1.5835697888
final spin z                0.4999999088
```

Winding, exact-third charge, localization, normalization, spin one-half within `2e-7`, and Maxwell constraints close. Stationarity does not.

### Four-spinor momentum and center response

The Pauli fields seed positive-energy embeddings only. All canonical pair fields and forces are regenerated from the actual four-spinor charge densities and Dirac currents.

```text
Lorentz momentum rate       0.001645074525562959
Maxwell-Dirac momentum rate 0.0016022176381169852
relative momentum error     2.61 percent
center acceleration        -0.0002424759822742363
center relative mismatch    114.74 percent
```

Momentum transfer closes; the center response has the wrong sign.

### Spin response

```text
finite-time spin rate y     1.45073921e-4
Dirac-generator rate y      1.45128373e-4
generator relative error    2.57 percent
rest-frame T-BMT rate y    -8.69424870e-5
rest-frame BMT mismatch     266.90 percent
```

The exact numerical generator is integrated consistently. The rest-frame reduction is rejected for the moving, extended winding packet.

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

Construct an independently varied coupled action whose Euler--Lagrange system supplies the stationary spinor, gauge field, momentum/center relation, and covariant spin dynamics together. Then repeat M9.97 across refined grids, time steps, boxes, separations, and spin orientations before any calibration campaign.
