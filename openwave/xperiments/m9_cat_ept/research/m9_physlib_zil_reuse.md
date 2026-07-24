# PhysLib/ZIL reuse map through M9.74

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after PR #75 | `ec309cdf9976f16155ef3ec07f8290126a652061` | merged M9.69--M9.71 baseline |
| `jagg-ix/openwave` | frozen campaign baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | immutable ancestry of M9.69--M9.74 results |
| `jagg-ix/openwave` | `agent/m9-deep-h1-closure-72-74` | current work branch | clean post-merge M9.72--M9.74 work |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `496b275336f30c0f934fe4ddcfa9fbfd99fa567c` | complete H¹ compactness, local dynamics, orbital mechanism, and variational authority |
| `jagg-ix/entropic-physlib-private` | PR #16 | `9a15bf5023980f6bc401671de7dc7dca164a52d0` | predicate compactness bridges, constrained direct method, concentration composition, and density coercivity |
| `jagg-ix/entropic-physlib-private` | frozen theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | immutable M9.69--M9.71 dependency |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions |

## Formal sources actually reused

| Path | Blob | Reused result |
| --- | --- | --- |
| `EuclideanSobolevFrequencyLocalization.lean` | `bd421597ff33177f08de1063dc91fec84a6d1420` | complete H¹ carrier; weak compactness with bound retention; weak-plus-norm strong closure; Prokhorov and joint field/density subsequences; direct method |
| `SchrodingerNewtonEnergy.lean` | `43ad108a3c0c08730f3892de2d2480697db8e357` | coercive lower bound, negative level, cubic mass law, strict subadditivity, positive binding gap |
| `SelfBoundSchrodingerNewtonPDE.lean` | `b9a094a57398efc11825885d8c2f3efa5654824c` | local H¹ existence/uniqueness for supplied `C¹` generators and compact-sublevel orbital stability |
| PR #16 `CubicQuinticOrbitalStability.lean` | `24e14292478aeb7c78b52efdb00d30e4d84a870c` | predicate-carrier strong/joint compactness bridges, constrained direct method, concentration composition, density coercivity |
| `LpAeConvergence.lean` / `LpSubsequenceDiagonalization.lean` | live base | finite-measure Vitali/a.e. bridges and local L² diagonal subsequences |

## Corrected decisions

- complete continuum H¹ carrier: `directly proved`
- weak compactness with norm-bound retention: `directly proved`
- weak-plus-norm strong H¹ closure: `directly proved`
- tight probability and joint field/density subsequences: `directly proved once tightness is supplied`
- local H¹ existence/uniqueness for a supplied `C¹` generator: `directly proved`
- compact-sublevel orbital-stability mechanism: `directly proved`
- constrained direct method: `directly proved in PR #16`
- vanishing exclusion: `directly proved`
- dichotomy exclusion: `directly proved`
- compact branch from explicit trichotomy: `directly proved in PR #16`
- concrete target generator H¹ mapping/`C¹`: `open`
- recentered target tightness/trichotomy: `open`
- normalized-mass closure and target-energy lower semicontinuity: `open`
- global conservative target flow/invariants: `open`
- compact target sublevel and branch identification: `open`
- M9.74 independent perturbation/estimator gate: `passed internally`
- external physical test: `not performed`

## Status policy

Lean remains proof authority; OpenWave owns simulation evidence; ZIL records identities and scope. `Directly proved`, `internally tested`, `externally tested`, and `validated` are not interchangeable.
