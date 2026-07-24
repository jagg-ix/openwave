# PhysLib/ZIL reuse map through M9.65

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` | `421c962fdaa4aa7359c00cd6b37f985d297f0dac` | simulation and platform evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `54b4ced090b200fac7ff04ee6a7e8797f1263049` | Lean theorem authority |
| `jagg-ix/zil-lean` | `main` | `f39758f85ee6300b8060e4f8ea1ecf344ed32c96` | semantic routing, durable evidence conventions, and current test/install infrastructure |

## Current formal source identities

| Path | Git blob SHA | Reused result |
| --- | --- | --- |
| `IpekCatichaSuperpositionViolation.lean` | `e46898d0013c22e983051b7248160323e64f468f` | cubic uniqueness; local nonlinear evolution; exact global positive-time pure-cubic and fixed multiplication-energy flows; norm contraction |
| `IpekCatichaUnboundedGenerator.lean` | `605a3eb7dd7055de4b1d5ce3d8eacecea136f70a` | dense/closable and self-adjoint mode-diagonal generators; maximal homogeneous damping and phase-plus-damping `C₀` semigroups |
| `EntropicDynamicsLocalTimeFokkerPlanck.lean` | `99c39cd8dd3629831e7361a5e7e72eaaa7483c35` | free kinetic bracket, covariance, positive smooth kernel, and explicit PDE derivative identities |
| `Clock/EntropicAgreement.lean` | `8d7cb5a9c87dba47beefdc4a6c317aa872536632` | operational clock calibration interface |
| `EntropicComplexEinstein.lean` | `3e480aca62a95ae4b739dd92e3aa97ffea1b4414` | positive imaginary-Einstein entropic/physical-time identification |

Earlier global action, ADM, maximal-development, LDDL, Liouville, trace-preservation, and Cauchy-limit sources remain reusable.

## M9.63--M9.65 use

- M9.63 uses the formal cubic uniqueness result as its structural anchor, then imposes two OpenWave self-consistency conditions to select the numerical pair. It does not claim Lean derives those conditions.
- M9.64 uses the exact cubic flows and homogeneous semigroups to narrow the formal boundary. OpenWave supplies the new exact coercive density inequality and nested spatial cubic--quintic spectral campaign. The selected Laplacian-plus-quintic theorem remains open in PhysLib.
- M9.65 uses the selected coefficients and an internal Gaussian collective-coordinate derivation to create one immutable prediction-ready record. ZIL-style identity and scope tracking are used; no external comparison is performed.

## Current decisions

- selected `alpha`: `74.66304462649356`
- selected `beta`: `415.7483217223993`
- frozen prediction: `omega_breath / omega_Compton = 2.634371114526885`
- prediction tolerance: `5%`
- prediction tested: `false`
- platform validation counts: `0 validated / 20 partial / 1 negative`

## Open boundaries

- derive or reject the Gaussian peak/stationarity conditions from the coupled action and clock sector;
- kernel-formalize the spatial cubic--quintic `H¹` differential PDE;
- compactness modulo translations/phase and orbital stability for arbitrary `H¹` perturbations;
- compare the frozen prediction against an independent higher-fidelity simulation or external measurement without refitting.

## Status policy

Use `directly proved`, `proved with explicit scope`, `conditional on explicit analytic data`, `prediction-ready`, `tested`, and `validated` as separate states. OpenWave validation remains separate from Lean proof status. ZIL records identities and receipts; Lean remains proof authority; human review controls physical promotion.
