# PhysLib/ZIL reuse map through M9.71

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | merged simulation baseline |
| `jagg-ix/openwave` | `agent/m9-stationary-formal-mode-69-71` | current work branch | M9.69--M9.71 implementation and evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `e2c06741c3e49deb604082a2e9c2e918eab8d545` | merged Lean baseline |
| `jagg-ix/entropic-physlib-private` | `agent/m9-cubic-quintic-h1-certificate-70` | `51aad63b2541a1377a001df71b85dfe35f26c0af` | M9.70 formal theorem source |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing and evidence conventions |

## Current formal source identities

| Path | Git blob SHA | Reused result |
| --- | --- | --- |
| `CubicQuinticOrbitalStability.lean` | `b1bbf0bd6e58b41796aba1d63919f3cd6fe7aca4` | exact density factorization/coercivity and conditional `H¹` orbital certificate theorem |
| `IpekCatichaSuperpositionViolation.lean` | `d4f6e760e20dc1a3d7b4db7e21b8569bc9d307a7` | cubic uniqueness, contractive semiflow, strict decay, and zero attractor |
| `IpekCatichaUnboundedGenerator.lean` | `605a3eb7dd7055de4b1d5ce3d8eacecea136f70a` | self-adjoint diagonal generators and homogeneous contraction semigroups |
| `EntropicDynamicsLocalTimeFokkerPlanck.lean` | `99c39cd8dd3629831e7361a5e7e72eaaa7483c35` | free kinetic bracket, kernel, and PDE identities |
| `Clock/EntropicAgreement.lean` | `8d7cb5a9c87dba47beefdc4a6c317aa872536632` | operational clock calibration interface |

## M9.69--M9.71 use

- M9.69 uses the selected cubic--quintic coefficients and the existing spectral spatial solver infrastructure to construct a full-equation stationary branch. It does not claim PhysLib proves existence of that branch.
- M9.70 adds a new PhysLib module. The exact density inequality is unconditional. Uniform orbital control is derived from explicit analytic certificate fields, so missing PDE construction and concentration-compactness results cannot be hidden.
- M9.71 uses the M9.69 branch and freezes a small-chirp radial mode on one grid before comparing with two held-out grids. ZIL records the no-refit dependency and the distinction between internal testing and external validation.

## Current decisions

- stationary non-Gaussian branch constructed numerically: `true`
- exact cubic--quintic density coercivity kernel-proved: `true`
- conditional orbital theorem kernel-proved: `true`
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
