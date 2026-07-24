# PhysLib/ZIL reuse map through M9.74

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after PR #75 | `ec309cdf9976f16155ef3ec07f8290126a652061` | merged M9.69--M9.71 simulation baseline |
| `jagg-ix/openwave` | frozen campaign baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | immutable ancestry of M9.69--M9.74 generated results |
| `jagg-ix/openwave` | `agent/m9-stationary-formal-mode-69-71` | current work branch | post-merge M9.72--M9.74 reconciliation and evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `496b275336f30c0f934fe4ddcfa9fbfd99fa567c` | complete H¹ compactness, local dynamics, orbital mechanism, and Schrödinger--Newton variational authority |
| `jagg-ix/entropic-physlib-private` | PR #16 / `agent/m9-cubic-quintic-h1-certificate-70-current` | `9a15bf5023980f6bc401671de7dc7dca164a52d0` | predicate compactness bridges, constrained direct method, concentration composition, and density coercivity |
| `jagg-ix/entropic-physlib-private` | frozen theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | immutable dependency of generated M9.69--M9.71 ledgers |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing and evidence conventions |

## Current formal source identities

| Path | Identity | Reused result |
| --- | --- | --- |
| `EuclideanSobolevFrequencyLocalization.lean` | blob `bd421597ff33177f08de1063dc91fec84a6d1420` | complete H¹ carrier; norm-bound retaining weak subsequence; weak-plus-norm strong closure; Prokhorov compactness; joint field/density subsequence; direct method |
| `SchrodingerNewtonEnergy.lean` | blob `43ad108a3c0c08730f3892de2d2480697db8e357` | coercive lower bound, negative normalized level, exact cubic mass law, strict subadditivity, positive binding gap |
| `SelfBoundSchrodingerNewtonPDE.lean` | blob `b9a094a57398efc11825885d8c2f3efa5654824c` | local H¹ existence/uniqueness for supplied `C¹` generators and compact-sublevel Cazenave--Lions orbital stability |
| updated `CubicQuinticOrbitalStability.lean` | blob `24e14292478aeb7c78b52efdb00d30e4d84a870c` | predicate-carrier strong/joint compactness bridges, constrained direct method, concentration branch composition, density coercivity |
| `CubicQuinticOrbitalStabilityAudit.lean` | PR #16 | axiom-clean and non-vacuity registrations including live dynamics/stability mechanisms |
| `IpekCatichaSuperpositionViolation.lean` | live formal base | cubic uniqueness, local polynomial continuum ODE, contractive semiflow, strict decay, zero attractor |
| `LpAeConvergence.lean` | live formal base | finite-measure Vitali bridge and a.e. subsequence extraction from Lp convergence |
| `LpSubsequenceDiagonalization.lean` | live formal base | one subsequence converging locally in L² on every exhaustion level |
| `Clock/EntropicAgreement.lean` | existing source | operational clock calibration interface |

## M9.72--M9.74 use

- **M9.72** reuses the complete carrier, weak compactness with bound retention, weak-plus-norm strong closure, tight-measure compactness consequences, local `C¹`-generator ODE theory, and the compact-sublevel orbital mechanism. PR #16 adds the predicate-carrier and constrained bridges that are actually absent.
- **M9.73** reuses the negative variational level to exclude vanishing and the positive binding gap to exclude dichotomy. Once recentered tightness is supplied, the live branch already supplies a common field/density subsequence; PR #16 composes the explicit trichotomy.
- **M9.74** reuses the immutable M9.71 prediction record, but changes both perturbation and estimator. ZIL records that no coefficient, frequency, or tolerance refit occurred.

## Current decisions

- complete continuum H¹ carrier directly proved: `true`
- bounded H¹ weak subsequence with norm-bound retention directly proved: `true`
- weak-plus-norm strong H¹ closure directly proved: `true`
- tight probability compactness consequence directly proved: `true`
- common field/density subsequence from tightness directly proved: `true`
- local H¹ existence/uniqueness for supplied `C¹` generator directly proved: `true`
- compact-sublevel orbital-stability mechanism directly proved: `true`
- constrained direct method directly proved in PR #16: `true`
- vanishing excluded by negative level: `true`
- dichotomy excluded by positive binding gap: `true`
- compact branch follows from explicit trichotomy: `true`
- concrete target generator H¹ mapping/`C¹`: `false`
- trichotomy/translation tightness derived from target binding: `false`
- normalized-mass weak closure instantiated: `false`
- target-energy weak lower semicontinuity instantiated: `false`
- global conservative target flow and invariants constructed: `false`
- target compact low-energy sublevel proved: `false`
- M9.74 independent perturbation/estimator passes frozen mode gate: `true`
- external experimental comparison: `false`
- platform counts: `0 validated / 20 partial / 1 negative`

## Open boundaries

- prove the concrete Hartree/cubic--quintic generator maps H¹ to H¹ and is `C¹`;
- prove normalized-mass weak closure and target-energy weak lower semicontinuity;
- derive recentered tightness and the target concentration trichotomy;
- construct a global mass/energy-preserving target flow;
- prove compactness of target low-energy sublevels modulo phase/translation and identify the M9.69 branch;
- compare the immutable M9.71 mode with external physical evidence.

## Status policy

Use `directly proved`, `proved from explicit premises`, `numerically qualified`, `prediction-ready`, `internally tested`, `externally tested`, and `validated` as distinct states. Lean remains proof authority; OpenWave owns simulation evidence; ZIL records identities and scope; human review controls physical promotion.
