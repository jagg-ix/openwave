# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 OpenWave comparison criteria and combines a stationary non-Gaussian branch, theorem-guided finite-grid dynamics, explicit claim boundaries, and a reusable uncalibrated particle-model API.

## Platform status after M9.93c

- Seven criteria are validated in-platform.
- Thirteen criteria remain partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- The reusable particle kernel wraps the existing coefficient selection, stationary branch, exact subflows, perturbations, observables, serialization fingerprints, and fail-closed physical-identity gate.
- The PhysLib contract pins the live `entropic-physlib-linear-full` branch, exact source blobs, theorem declarations, numerical adapters, assumptions, and per-interface claim boundaries.

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
| Model registration | `model_registration.py` | canonical M9 component identity and surface map |
| Particle kernel | `particle_model.py` | reusable state construction, perturbation, flow, observables, and identity gate |
| PhysLib contract | `formal/physlib_contract.v2.json` and `physlib_contract.py` | version-pinned formal authority and drift validation |
| Instrumentation | `_launcher.py`, `instrumentation.py`, and preset ledgers | headless or rendered evidence panels |

## Cross-repository authority

| Repository | Ref | Revision | Authority |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` | `bbc3fd392e0553ddd94080831e42196891911360` | merged numerical evidence through M9.92 |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `e10af9a3b47bf90afc0a88167a5d495b6935f4dc` | Lean proof authority pinned by contract v2 |

The formal contract includes the elementary U(1), Klein-Gordon, and Coulomb quantization layer; winding-charge arithmetic; the Euclidean free Schrödinger group; a scoped nonlinear continuum interface; and an optional zero-point-length extension. Lean is not required at simulation runtime.

## Particle-model boundary

`CatEptParticleModel.repository_default()` constructs a model specification with:

- the current dimensionless dispersion and selected cubic-quintic coefficients;
- the assumptions used to select those coefficients;
- an exact formal-contract fingerprint;
- no default physical particle name or calibration record.

The existing stationary solver can construct the neutral non-Gaussian branch. Nonzero winding may be declared in a model specification, but a charged stationary branch is not claimed until winding is embedded into the same solved state and passes the identity gates.

A physical assignment requires one certificate covering localization, normalization, embedded winding, calibration, rest energy, clock identity, spin/exchange, magnetic moment, far-field force, and an out-of-sample prediction. The default state intentionally fails that certificate.

## Boundary

The M9 stack establishes a reproducible mathematical particle kernel and seven criterion-scoped OpenWave validations. It does not establish an electron, positron, quark, or other observed-particle identity; calibrated physical units; a derived elementary charge scale; or external experimental agreement.

## Next critical targets

1. M9.94: bind magnetic moment and spin observables to one canonical particle state and the live Pauli-current theorem surface.
2. M9.95: bind Coulomb and magnetic force measurements to two canonical states with one shared calibration ledger.
3. M9.96: construct a charged stationary branch whose field-derived winding, localization, and dynamical stability close simultaneously.
