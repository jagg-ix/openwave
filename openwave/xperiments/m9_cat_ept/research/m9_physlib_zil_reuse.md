# PhysLib/ZIL reuse map through M9.74

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | merged simulation baseline |
| `jagg-ix/openwave` | `agent/m9-stationary-formal-mode-69-71` | current work branch | M9.69--M9.74 implementation and evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `0a04328a01b7911078c4f9d01cc0c8c963519dc2` | complete H¹ weak compactness and Schrödinger--Newton variational/binding authority |
| `jagg-ix/entropic-physlib-private` | PR #16 / `agent/m9-cubic-quintic-h1-certificate-70-current` | `5d0cdf07c891b1dbe7381b93c2d794b593fae09d` | constrained direct method, concentration branch elimination, and orbital certificate |
| `jagg-ix/entropic-physlib-private` | frozen theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | immutable dependency of generated M9.69--M9.71 ledgers |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing and evidence conventions |

## Current formal source identities

| Path | Identity | Reused result |
| --- | --- | --- |
| `EuclideanSobolevFrequencyLocalization.lean` | blob `a3e5f79be6c3d650f48ea1c164541eedf8588c5b` | complete `EuclideanHs 3 1` carrier, Bessel-energy equivalence, weak H¹ subsequence extraction, conditional direct method |
| `SchrodingerNewtonEnergy.lean` | blob `43ad108a3c0c08730f3892de2d2480697db8e357` | coercive lower bound, negative normalized level, exact cubic mass law, strict subadditivity, positive binding gap |
| updated `CubicQuinticOrbitalStability.lean` | blob `3a5b8737331fb1bbae0dea62af2db21f58f1b332` | constrained direct method, concentration branch composition, density coercivity, certified orbital control |
| `CubicQuinticOrbitalStabilityAudit.lean` | PR #16 | axiom-clean and non-vacuity registrations |
| `IpekCatichaSuperpositionViolation.lean` | live formal base | cubic uniqueness, local polynomial continuum ODE, contractive semiflow, strict decay, zero attractor |
| `LpAeConvergence.lean` | live formal base | finite-measure Vitali bridge and a.e. subsequence extraction from Lp convergence |
| `LpSubsequenceDiagonalization.lean` | live formal base | one subsequence converging locally in L² on every exhaustion level |
| `Clock/EntropicAgreement.lean` | existing source | operational clock calibration interface |

## M9.72--M9.74 use

- **M9.72** reuses the actual complete `H¹(ℝ³)` carrier and weak subsequence theorem. PR #16 adds the constrained direct method rather than replacing existing compactness infrastructure with a generic certificate.
- **M9.73** reuses the negative variational level to exclude vanishing and the positive binding gap to exclude dichotomy. PR #16 composes those results with an explicit trichotomy to obtain compactness modulo translations.
- **M9.74** reuses the immutable M9.71 prediction record, but changes both perturbation and estimator. ZIL records that no coefficient, frequency, or tolerance refit occurred.

## Current decisions

- complete continuum H¹ carrier directly proved: `true`
- bounded H¹ weak subsequence directly proved: `true`
- constrained direct method directly proved in PR #16: `true`
- vanishing excluded by negative level: `true`
- dichotomy excluded by positive binding gap: `true`
- compact branch follows from explicit trichotomy: `true`
- trichotomy/translation tightness derived from first principles: `false`
- normalized-mass weak closure instantiated: `false`
- target-energy weak lower semicontinuity instantiated: `false`
- conservative spatial H¹ flow and invariants constructed: `false`
- M9.74 independent perturbation/estimator passes frozen mode gate: `true`
- external experimental comparison: `false`
- platform counts: `0 validated / 20 partial / 1 negative`

## Open boundaries

- prove normalized-mass weak closure on the promoted carrier;
- prove sequential weak lower semicontinuity of the promoted Hartree/cubic--quintic energy;
- construct the conservative state-dependent spatial cubic--quintic H¹ flow and its invariants;
- derive the concentration trichotomy and translation tightness;
- identify the compact limit with the M9.69 branch and prove coercivity modulo phase/translation;
- compare the immutable M9.71 mode with external physical evidence.

## Status policy

Use `directly proved`, `proved from explicit certificate data`, `numerically qualified`, `prediction-ready`, `internally tested`, `externally tested`, and `validated` as distinct states. Lean remains proof authority; OpenWave owns simulation evidence; ZIL records identities and scope; human review controls physical promotion.
