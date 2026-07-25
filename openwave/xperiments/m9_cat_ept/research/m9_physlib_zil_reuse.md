# PhysLib/ZIL reuse map through M9.74

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after PR #75 | `ec309cdf9976f16155ef3ec07f8290126a652061` | merged M9.69--M9.71 simulation baseline |
| `jagg-ix/openwave` | frozen campaign baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | immutable ancestry of generated M9.69--M9.74 results |
| `jagg-ix/openwave` | `agent/m9-stationary-formal-mode-69-71` | current work branch | synchronized M9.72--M9.74 evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` | complete H¹ compactness, local dynamics, orbital mechanism, and current Schrödinger--Newton variational authority |
| `jagg-ix/entropic-physlib-private` | PR #16 / `agent/m9-cubic-quintic-h1-certificate-70-current` | `86366ca14330f1037e6a76f5b36e52a34f7bf3fe` | rebased predicate compactness bridges, constrained direct method, concentration composition, and density coercivity |
| `jagg-ix/entropic-physlib-private` | frozen theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | immutable dependency of generated M9.69--M9.71 ledgers |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing and evidence conventions |

## Deep formal source inventory

| Path | Reused result |
| --- | --- |
| `EuclideanSobolevFrequencyLocalization.lean` | complete `EuclideanHs 3 1` carrier; bounded weak subsequences with retained norm bounds; weak-plus-norm strong closure; Prokhorov compactness; common field/density subsequences; direct-method engine |
| `SchrodingerNewtonEnergy.lean` | continuum coercive lower bounds; negative normalized level; cubic mass scaling; strict subadditivity; exact positive cluster-binding gaps; compact-core vanishing and dichotomy exclusion inputs |
| `SelfBoundSchrodingerNewtonPDE.lean` | local H¹ existence and uniqueness for supplied `C¹` vector fields; eventual uniqueness; compact-energy-sublevel Cazenave--Lions orbital-stability mechanism |
| `CubicQuinticOrbitalStability.lean` | exact density coercivity; predicate-carrier strong/joint compactness bridges; constrained direct method; explicit concentration-compactness branch elimination |
| `CubicQuinticOrbitalStabilityAudit.lean` | axiom-clean and non-vacuity registration of the new bridges together with reused local dynamics and stability mechanisms |
| `IpekCatichaSuperpositionViolation.lean` | cubic uniqueness, local polynomial continuum ODE, exact contractive semiflow, strict decay, and zero global attractor in the fixed-energy dissipative sector |
| `LpAeConvergence.lean` | finite-measure Vitali convergence and almost-everywhere subsequence extraction from `Lp` convergence |
| `LpSubsequenceDiagonalization.lean` | one subsequence converging locally in `L²` over every exhaustion level |
| `Clock/EntropicAgreement.lean` | operational entropic/physical clock calibration interface |

## Corrected target interpretation

- **M9.72** does not rebuild generic H¹ compactness or local ODE theory. Those are already in the base. It records the complete carrier, weak compactness with bound retention, weak-plus-norm strong closure, tight-measure compactness, local `C¹`-generator ODE theory, and compact-sublevel stability. PR #16 adds only the predicate-carrier and constrained direct-method bridges absent from the base.
- **M9.73** does not claim a new concentration-compactness theorem from scratch. The live branch already supplies negative level, strict subadditivity, and positive binding gaps. PR #16 composes those facts with an explicit trichotomy: vanishing and dichotomy are eliminated, leaving compactness modulo translations once target tightness/trichotomy data are proved.
- **M9.74** reuses the immutable M9.71 prediction without refitting, while changing both perturbation and estimator: amplitude deformation replaces phase chirp, and a zero-padded periodogram replaces the least-squares frequency scan.

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
- compact branch follows from an explicit trichotomy: `true`
- concrete target generator H¹ mapping and `C¹`: `false`
- translation tightness/trichotomy derived from the target binding functional: `false`
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
