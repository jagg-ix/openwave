# PhysLib/ZIL reuse map through M9.68

## Repository identities

| Repository | Ref | Current revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` | `e11e8fce88ce886812860ce747c48d32c8eaeb57` | simulation and platform evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `e2c06741c3e49deb604082a2e9c2e918eab8d545` | Lean theorem authority |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing, evidence conventions, and install/test infrastructure |

The M9.66--M9.68 generated ledgers retain ZIL snapshot `f39758f85ee6300b8060e4f8ea1ecf344ed32c96`, which was current when the campaigns were frozen. ZIL later advanced only in installation-lifecycle tooling.

## Current formal source identities

| Path | Git blob SHA | Reused result |
| --- | --- | --- |
| `IpekCatichaSuperpositionViolation.lean` | `d4f6e760e20dc1a3d7b4db7e21b8569bc9d307a7` | cubic uniqueness; jointly continuous contractive semiflow; strict decay and zero global attractor |
| `IpekCatichaUnboundedGenerator.lean` | `605a3eb7dd7055de4b1d5ce3d8eacecea136f70a` | self-adjoint mode-diagonal generators and homogeneous contraction semigroups |
| `EntropicDynamicsLocalTimeFokkerPlanck.lean` | `99c39cd8dd3629831e7361a5e7e72eaaa7483c35` | free kinetic bracket, kernel, and PDE derivative identities |
| `Clock/EntropicAgreement.lean` | `8d7cb5a9c87dba47beefdc4a6c317aa872536632` | operational clock calibration interface |
| `GlobalElectrograviticAction.lean` | `39e807f424cf8384135299e84fdffc97fb506ee5` | integrated coupled-action derivative interface |

Earlier global action, ADM, maximal-development, LDDL, Liouville, trace-preservation, and Cauchy-limit sources remain reusable.

## M9.66--M9.68 use

- M9.66 uses the global action/clock stack as scope anchors. It derives Gaussian scale stationarity from the reduced action, then rejects peak-density matching as the current full-field selection law.
- M9.67 reuses the exact cubic semiflow to avoid underreporting formal closure, while explicitly retaining the missing Laplacian-plus-quintic `H¹` theorem. OpenWave supplies twelve adversarial numerical runs.
- M9.68 reuses the immutable M9.65 record and tests it with an independently relaxed spatial branch. The result is written as a falsified subprediction, not reinterpreted as a criterion-level or theory-wide negative.

## Current decisions

- M9.63 pair first-principles unique: `false`
- M9.67 spatial `H¹` kernel theorem proved: `false`
- M9.65 prediction tested: `true`
- M9.65 prediction passed: `false`
- external experimental comparison: `false`
- platform counts: `0 validated / 20 partial / 1 negative`

## Open boundaries

- solve the full normalized stationary spatial equation for a non-Gaussian localized branch;
- kernel-formalize the conservative spatial cubic--quintic `H¹` PDE and its invariants;
- prove compactness modulo translation/phase and orbital stability;
- derive and test a replacement mode prediction without refitting.

## Status policy

Use `directly proved`, `proved with explicit scope`, `conditional`, `prediction-ready`, `tested`, `passed`, `falsified`, and `validated` as distinct states. Lean remains proof authority; OpenWave owns simulation evidence; ZIL records identities and scope; human review controls physical promotion.
