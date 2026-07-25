# OpenWave M9 CAT/EPT comparison profile

The canonical executable source is `openwave/xperiments/m9_cat_ept/model_conformance_dynamics.py`. It overlays exactly the three M9.97 findings on the historical 21-row profile while preserving criterion identities, domains, statuses, and the seven validated rows. The current canonical registration is `model_registration_current.py`.

Platform validation, formal theorem status, current-tree evidence, physical identity, calibration, and external validation remain separate layers.

## Platform summary after M9.97

| Status | Count |
| --- | ---: |
| ✅ validated in-platform | 7 |
| ⚠️ partial / bounded | 13 |
| ❌ honest negative | 1 |
| 🚧 planned / not yet | 0 |
| **Explicit criteria** | **21** |

Validated rows:

- charge quantization;
- particle stability / Derrick escape;
- spin-1/2 statistics;
- source-free Maxwell waves;
- free massive Klein--Gordon evolution;
- dimensionless Coulomb orbital quantization;
- explicit dimensionless thermal field.

The sole criterion-level negative remains the predictive lepton-mass hierarchy.

## Formal authority

The formal import is pinned to:

```text
repository   jagg-ix/entropic-physlib-private
branch       entropic-physlib-linear-full
base commit  e10af9a3b47bf90afc0a88167a5d495b6935f4dc
current tree 239a663a3192a3144fb998e7bb200e09689a3bb9
Physlib.lean 182a06e0f50314ec54436da602b4ac86eba4ee08
```

| Imported surface | Count |
| --- | ---: |
| ZIL graphs | 11 |
| ZIL entity identifiers | 422 |
| Explicit open/external boundaries | 12 |
| Branch-wide Lean aggregate/source files | 24 |
| M9.96 Pauli/Maxwell extension sources | 2 |
| M9.97 dynamics extension sources | 3 |

The M9.97 dynamics overlay imports:

- rest-frame Dirac--Pauli precession;
- equality of the rest-frame T-BMT and Dirac--Pauli rates;
- the QED coupling and force-law chain with the loop-value boundary retained;
- exact Coulomb potential and symmetry;
- radiation-gauge Helmholtz decomposition;
- a distributional three-dimensional point-charge field and Gauss source.

Formal availability does not promote a physical criterion. The rest-frame theorem does not supply the covariant boost/Thomas dynamics of a moving, extended winding packet.

## Retained M9.90--M9.96 infrastructure

M9.90 closes field-derived winding and exact third-charge arithmetic. M9.91 closes free massive Klein--Gordon evolution. M9.92 closes dimensionless Coulomb orbital quantization. M9.93 adds the reusable particle kernel and selected formal contract. M9.94--M9.95 add canonical spin and force bridges. M9.96 replaces declared-source force controls with:

- field-measured winding-three source candidates;
- periodic charge/current and Maxwell fields;
- current-integral and weak-field-response magnetic moments;
- a Lorentz/interaction-energy/Maxwell-stress force triangle.

M9.96 still finds zero passing scalar charged stationary candidates.

## M9.97a -- self-consistent gauge-spinor stationary equation

The winding-three candidate is embedded into a two-component Pauli field and evolved by normalized imaginary time under

```text
H[Psi,A,phi]
  = -D (grad - i q A)^2
    + q phi
    - alpha rho
    + beta rho^2
    - (g q / 4m) sigma.B.
```

Charge, gauge-covariant current, scalar/vector potentials, and electric/magnetic fields are recomputed at every iteration.

| Iteration | Relative residual | Radius | Spin z |
| ---: | ---: | ---: | ---: |
| 0 | `0.5071084764` | `1.5595442312` | `0.5000000000` |
| 100 | `0.5128543258` | `1.5633543312` | `0.4999999970` |
| 300 | `0.5148664832` | `1.5712259574` | `0.4999999748` |
| 600 | `0.5190695504` | `1.5835697888` | `0.4999999088` |

Winding, exact-third charge, normalization, localization, spin one-half within `2e-7`, and Maxwell constraints close. The stationary residual does not approach the `0.10` gate.

**Result:** a self-consistent gauge-covariant Pauli equation is executable, but the selected action does not construct a charged spinorial stationary branch.

## M9.97b -- source-consistent four-spinor momentum and center response

The Pauli winding fields seed positive-energy embeddings only. After embedding, all canonical charge densities, Dirac currents, Maxwell fields, Lorentz forces, and self-field controls are regenerated from the actual four-spinors evolved by the Maxwell--Dirac engine.

```text
positive integrated charge      +1
negative integrated charge      -1
pair net-charge error            discrete zero
Lorentz momentum rate            0.001645074525562959
Maxwell-Dirac momentum rate      0.0016022176381169852
relative momentum error          2.61 percent
center acceleration             -0.0002424759822742363
center/Lorentz relative mismatch 114.74 percent
```

Kinetic-momentum transfer closes against the Lorentz force. The center response has the wrong sign and does not close the acceleration reduction.

## M9.97c -- spin generator and rest-frame T-BMT comparison

The pair is initialized with transverse spin. The interaction-induced finite-time spin rate is compared with the exact instantaneous Dirac generator used by the PDE and with the imported rest-frame Pauli/T-BMT shadow.

```text
finite-time spin rate y       1.45073921e-4
Dirac-generator rate y        1.45128373e-4
generator relative error      2.57 percent
rest-frame T-BMT rate y      -8.69424870e-5
rest-frame relative mismatch 266.90 percent
```

The numerical evolution integrates its exact Dirac generator consistently. The moving finite-size winding packet does not reduce to the rest-frame T-BMT torque.

## Current three-row status

| Criterion | Closed subreduction | Promotion blocker |
| --- | --- | --- |
| Magnetic moment and spin | field-derived moment/response and exact-generator spin evolution | no stationary charged spinor; rest-frame/covariant BMT reduction, anomaly, identity, and calibration open |
| Electric force | M9.96 force triangle and four-spinor momentum/Lorentz agreement | center response has wrong sign; no stable charged pair or unit map |
| Magnetic force | field-derived magnetic force contribution and exact-generator precession | moving-packet torque law, stable pair, and common moment/force calibration open |

All three remain **partial**.

## Evidence authority

The current authority surfaces are:

- `formalization_dynamics_extension.py`;
- `gauge_spinor_stationary_current.py`;
- `spinorial_pair_dynamics_authoritative.py`;
- `dynamics_evidence_authority.py`;
- `physical_calibration_ledger_v3.py`;
- `model_conformance_dynamics.py`;
- `model_registration_current.py`;
- `research/zil/m9_97_gauge_spinor_dynamics.zc`.

The identity certificate fails closed even if external calibration flags are asserted because the stationary, center-response, and covariant spin-torque gates are false.

## Explicit retained boundaries

- independently varied coupled gauge-spinor action;
- stable charged spinorial stationary branch;
- converged relation between kinetic momentum and center motion;
- covariant moving-packet spin and torque law;
- anomalous-moment derivation;
- physical charge, moment, force, mass, length, and time calibration;
- concrete Maxwell Cauchy construction;
- concrete ADM constraint propagation;
- maximal globally hyperbolic coupled development;
- global nonlinear coupled-action certificate;
- continuum open-system and constructive-QFT boundaries;
- withheld external predictions.

The platform matrix remains `7 validated / 13 partial / 1 negative`. The next critical target is an independently varied coupled action that can produce a stable charged spinorial branch and derive both center and covariant spin dynamics from the same equations.
