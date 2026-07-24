# PhysLib/ZIL reuse map through M9.62

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` | `ce17d7126f0c9a9f6564c7bce04df29ea383a558` | simulation and platform evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `adbe9ead533d56ea7acd18e4c9ad5dacafd973ff` | Lean theorem authority |
| `jagg-ix/zil-lean` | `main` | `64462a3c5e2ffb51a7b226675491cc3a9b156a8d` | semantic routing, durable source events, receipts, and runtime evaluation |

## New formal source identities

| Path | Git blob SHA | Reused result |
| --- | --- | --- |
| `IpekCatichaSuperpositionViolation.lean` | `7791ba4af4381052865294434b070f2b1e6ba9df` | cubic gauge-covariant uniqueness; local continuum cubic evolution |
| `IpekCatichaUnboundedGenerator.lean` | `ddc009e49b64d8b33bede7c67c8392c1ef7cf30a` | dense/closable and self-adjoint mode-diagonal generators; maximal homogeneous damping and `C₀` semigroup |
| `EntropicDynamicsLocalTimeFokkerPlanck.lean` | `00734bf484cd0dd724120d68fc8d41066acae582` | free continuum kinetic bracket, covariance, positive smooth kernel |
| `Clock/EntropicAgreement.lean` | `8d7cb5a9c87dba47beefdc4a6c317aa872536632` | operational clock calibration interface |
| `EntropicComplexEinstein.lean` | `3e480aca62a95ae4b739dd92e3aa97ffea1b4414` | positive imaginary-Einstein entropic/physical-time identification |
| `zil-lean/architecture/capability-ownership.edn` | `36e75ea2885c4fd2941ba65c6f4835144ddda84c` | `ZIL-CONTROL-EVENT/1`, receipt, evidence, and human-decision authority split |

Earlier global action, ADM, maximal-development, LDDL, Liouville, trace-preservation, and Cauchy-limit sources remain reusable.

## M9.60--M9.62 use

- M9.60 combines the formal cubic uniqueness result with a polynomial boundedness audit. It does not infer unique numerical coefficients.
- M9.61 uses the formal cubic local-evolution theorem only as a scope anchor; its cubic--quintic Gaussian-orbit result is an OpenWave variational calculation.
- M9.62 emits a local verified hash chain shaped as `ZIL-CONTROL-EVENT/1` and `ZIL-CONTROL-RECEIPT/1`. It does not replace the Clojure durable store or Lean semantic authority.

## Open boundaries

- derive or reject unique `(alpha,beta)` from the coupled action;
- full cubic--quintic continuum generator and semigroup;
- arbitrary-`H¹` compactness modulo translations/phase and orbital stability;
- calibrated mass, charge, clock, coupling, lifetime, and one out-of-sample prediction.

## Status policy

Use `directly proved`, `proved with explicit scope`, `conditional on explicit analytic data`, and `not closed end-to-end`. OpenWave validation remains separate. ZIL records identities and receipts; Lean remains proof authority; human review controls physical promotion.
