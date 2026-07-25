# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 OpenWave comparison criteria and combines a stationary non-Gaussian branch, theorem-guided finite-grid dynamics, explicit claim boundaries, a reusable uncalibrated particle-model API, and a branch-wide imported inventory of the CAT/EPT Lean/ZIL formalization corpus.

## Platform status after M9.96

- Seven criteria are validated in-platform.
- Thirteen criteria remain partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- The reusable particle kernel wraps coefficient selection, stationary branch construction, exact subflows, perturbations, periodic-covariant observables, serialization fingerprints, and a fail-closed physical-identity gate.
- The formalization importer pins `entropic-physlib-linear-full` by exact tree `239a663a3192a3144fb998e7bb200e09689a3bb9`, current `Physlib.lean` blob `182a06e0f50314ec54436da602b4ac86eba4ee08`, 11 ZIL graphs, 422 graph entities, 12 open/external boundaries, and 24 Lean sources.
- A two-source current-tree overlay imports the previously omitted gauge-invariant Pauli--Maxwell and conserved-current/Maxwell witnesses.
- M9.96 constructs field-derived winding-three source candidates, closes projected static Maxwell constraints, independently verifies the magnetic moment by weak-field energy response, and closes a Lorentz/energy/stress force triangle.
- The selected scalar cubic--quintic action does not construct a charged stationary branch across the tested core scales. Magnetic moment, electric force, and magnetic force therefore remain partial.

Validated criteria:

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
| 21-criterion profile | `model_conformance.py` and `MODELS_M9.md` | executable comparison status |
| Model registration | `model_registration.py` | canonical M9 component, formal revision, imported surfaces, and M9.96 authority |
| Particle kernel | `particle_model.py` | reusable state construction, perturbation, flow, periodic observables, and historical identity gate |
| Selected PhysLib contract | `formal/physlib_contract.v2.json` and `physlib_contract.py` | historical selected theorem contract and drift validation |
| Branch-wide formal inventory | `formalization_inventory*.py` and `formalization_import.py` | 11-graph current-tree declaration and boundary coverage |
| Force formal overlay | `formalization_inventory_force_extensions.py` and `formalization_force_extension.py` | Pauli--Maxwell, conserved-current, and Maxwell-stress witnesses |
| Canonical spin bridge | `canonical_spin_magnetic_bridge.py` | Pauli embedding, current, moment, angular momentum, tree `g=2` |
| Canonical force bridge | `canonical_force_formal_bridge.py` | historical declared-winding pair and asymptotic kernel controls |
| Charged feasibility | `charged_branch_feasibility.py` | winding-three seeds and unconstrained stationary-flow test |
| Charged Maxwell source | `charged_maxwell_source_bridge.py` | charge/current, periodic fields, Maxwell constraints, and magnetic response |
| Field-force triangle | `field_force_triangle.py` | Lorentz volume, interaction-energy, and Maxwell-stress comparison |
| Current evidence authority | `current_evidence_authority.py` | current-tree identity and no-promotion authority |
| Three-row calibration ledger | `physical_calibration_ledger_v2.py` | promotion/failure rules for spin moment, electric force, and magnetic force |

## M9.96 measured result

### Charged stationary feasibility

The neutral M9.69 amplitude is given a field-measured winding-three vortex. All four seeds are normalized and carry exact charge `q = n/3 = 1`. Under the unconstrained selected scalar imaginary-time flow:

- three seeds retain winding three;
- no seed simultaneously closes the stationary residual and compact-radius gates;
- the best evolved residual remains approximately `0.512`;
- the best evolved radius is approximately `1.999`.

This is a negative subresult for the selected scalar action, not evidence against a gauge- or spinor-extended CAT/EPT equation.

### Static source and moment response

The same winding candidate supplies charge density, convective current, Pauli magnetization current, and periodic electric and magnetic fields.

```text
projected Gauss residual   3.67e-16
static Ampere residual     5.38e-16
max |div B|                6.94e-18
magnetic moment            1.4150287474588639
weak-field response moment 1.4150287474588639
```

### Field-force triangle

For opposite candidates at separation `16/3`:

```text
electric force z           2.07159e-3
magnetic force z           4.58535e-4
full Lorentz force z       2.53013e-3
energy derivative force z  2.47118e-3
Maxwell stress force z     2.59376e-3
energy/Lorentz error        2.33 percent
stress/Lorentz error        2.52 percent
action-reaction error       2.72e-9
```

The earlier softened Coulomb and dipole kernels remain useful asymptotic controls, but M9.96 no longer relies on them as the candidate-level force evidence.

## Particle, force, and gravity boundaries

The neutral stationary branch is available. A nonzero winding source candidate is now field-derived and linked to static Maxwell fields, but it is not a stable charged stationary particle.

The magnetic moment is independently closed on the candidate through both the current integral and weak-field energy response. The electric and magnetic forces are independently compared through Lorentz density, interaction-energy derivative, and Maxwell stress. Full coupled-PDE center acceleration, torque, precession, stable charged-pair dynamics, and physical calibration remain open.

The Eddington affine first integral derives an Einstein equation with cosmological constant algebraically after assuming the affine connection field equation. It does not supply a full variational derivation, global nonlinear Cauchy development, or calibrated CAT/EPT gravity.

A physical assignment still requires one certificate covering localization, normalization, embedded winding, calibration, rest energy, clock identity, spin/exchange on the same branch, magnetic moment, full-PDE force, and an out-of-sample prediction.

## Boundary

The M9 stack establishes a reproducible mathematical particle kernel, a branch-wide formalization inventory, field-derived charged-source consistency, a static Maxwell force triangle, and seven criterion-scoped OpenWave validations. It does not establish a stable charged stationary particle, observed-particle identity, calibrated units, a CAT/EPT derivation of the anomalous magnetic moment, full-PDE force acceleration, or external experimental agreement.

## Next critical targets

1. M9.97: construct a self-consistent gauge/spinorial stationary equation rather than another detached force kernel.
2. Measure center acceleration, torque, and spin precession under the same coupled PDE and compare them with the M9.96 stress/energy/Lorentz triangle.
3. Apply a stable charged branch to annihilation, composite sectors, calibration, and withheld physical predictions.
