# PhysLib/ZIL reuse map through M9.71

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | merged simulation baseline |
| `jagg-ix/openwave` | `agent/m9-stationary-formal-mode-69-71` | current work branch | M9.69--M9.71 implementation and evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `f148278ec8264d031753d9def49cd2133ac4768d` | current Lean baseline with compact-core binding-gap results |
| `jagg-ix/entropic-physlib-private` | theorem snapshot | `51aad63b2541a1377a001df71b85dfe35f26c0af` | revision pinned by generated M9.69--M9.71 ledgers |
| `jagg-ix/entropic-physlib-private` | PR #16 / `agent/m9-cubic-quintic-h1-certificate-70-current` | `f165cd8ba524a4274cb46bcd4c4ba1f12a274bf7` | rebased audited M9.70 theorem branch |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing and evidence conventions |

PR #16 preserves the theorem statements used by the frozen numerical ledgers while adding ZIL attachments, a dedicated axiom/non-vacuity audit, and compatibility with the latest formal baseline.

## Current formal source identities

| Path | Identity | Reused result |
| --- | --- | --- |
| `CubicQuinticOrbitalStability.lean` theorem snapshot | blob `b1bbf0bd6e58b41796aba1d63919f3cd6fe7aca4` | exact density factorization/coercivity and conditional `H¹` orbital theorem pinned by ledgers |
| audited `CubicQuinticOrbitalStability.lean` | PhysLib PR #16 | same theorem surface plus ZIL scope attachments |
| `CubicQuinticOrbitalStabilityAudit.lean` | PhysLib PR #16 | axiom-clean and non-vacuity registrations |
| `SchrodingerNewtonEnergy.lean` | current formal base | strict subadditivity and quantitative compact-core cluster-binding gaps |
| `IpekCatichaSuperpositionViolation.lean` | current formal base | cubic uniqueness, contractive semiflow, strict decay, and zero attractor |
| `Clock/EntropicAgreement.lean` | existing source | operational clock calibration interface |

## M9.69--M9.71 use

- M9.69 uses selected cubic--quintic coefficients and spectral spatial infrastructure to construct a full-equation stationary branch. It does not claim PhysLib proves existence of that branch.
- M9.70 adds the formal module and audit. The exact density inequality is unconditional. Uniform orbital control is derived from explicit analytic certificate fields, so missing PDE construction and concentration-compactness results cannot be hidden.
- M9.71 uses the M9.69 branch and freezes a small-chirp radial mode on one grid before comparing with two held-out grids. ZIL records the no-refit dependency and the distinction between internal testing and external validation.

## Current decisions

- stationary non-Gaussian branch constructed numerically: `true`
- exact cubic--quintic density coercivity kernel-proved: `true`
- conditional orbital theorem kernel-proved: `true`
- formal theorem surface ZIL-attached and audit-registered: `true`
- formal PR rebased on current PhysLib: `true`
- spatial `H¹` flow constructed in Lean: `false`
- M9.71 replacement mode passes internal held-out grids: `true`
- external experimental comparison: `false`
- platform counts: `0 validated / 20 partial / 1 negative`

## Open boundaries

- construct the conservative spatial cubic--quintic `H¹` flow;
- prove mass and energy conservation for that flow;
- derive compactness modulo phase/translation and coercivity of the M9.69 branch;
- compare the immutable M9.71 radial mode with an independent implementation or external observable.

## Status policy

Use `directly proved`, `proved from explicit certificate data`, `numerically qualified`, `prediction-ready`, `internally tested`, `externally tested`, and `validated` as distinct states. Lean remains proof authority; OpenWave owns simulation evidence; ZIL records identities and scope; human review controls physical promotion.
