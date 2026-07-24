# M9 global target plan

## Closure through M9.68

- **M9.66:** Gaussian scale stationarity is exactly the variation of the reduced normalized action. The second M9.63 condition is not the full stationary field equation: the selected Gaussian has relative Euler--Lagrange residual `0.485819`. Three nondegenerate local density landmarks select three distinct positive coefficient pairs. The current first-principles uniqueness claim is rejected.
- **M9.67:** six perturbation classes on `20^3` and `24^3` grids preserve mass below `7e-13`, control energy drift near `1e-6`, remain boundary-clean, and respect the coercive gradient estimate. PhysLib proves a separate jointly continuous contractive cubic semiflow and zero-field attractor. The spatial Laplacian-plus-quintic `H¹` theorem remains open.
- **M9.68:** the immutable M9.65 value `omega_breath / omega_Compton = 2.634371114527` was tested without refitting. Independent relaxed-state simulations measure `1.3468`--`1.4949`, missing by `43%`--`49%`. The Gaussian collective-coordinate subprediction is falsified inside OpenWave.

## Current cross-repository state

| Repository | Current revision | Contribution |
| --- | --- | --- |
| OpenWave | `e11e8fce88ce886812860ce747c48d32c8eaeb57` | merged M9.65 baseline and simulation evidence |
| PhysLib `entropic-physlib-linear-full` | `e2c06741c3e49deb604082a2e9c2e918eab8d545` | exact cubic nonlinear semiflow, strict contraction, zero global attractor, and broader formal action/clock stack |
| ZIL | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence orchestration plus current installation lifecycle tooling |

The M9.66--M9.68 result ledgers use the earlier frozen ZIL evidence snapshot `f39758f85ee6300b8060e4f8ea1ecf344ed32c96`; the intervening ZIL change is operational installation tooling and does not change the consumed semantic interfaces.

## Theory status

The platform remains at `0 validated / 20 partial / 1 negative`. The single criterion-level negative remains the lepton hierarchy. Separately, the methodological prediction ledger now records one tested and falsified subprediction. This distinction prevents a failed approximation from being inflated into a theory-wide rejection.

## Next phase

| Target | Deliverable | State |
| --- | --- | --- |
| M9.69 | Solve the full normalized stationary spatial equation for a non-Gaussian localized branch and replace the rejected peak rule | NEXT |
| M9.70 | Formalize spatial cubic--quintic `H¹` evolution, conserved quantities, compactness modulo symmetries, and orbital stability | GATED |
| M9.71 | Derive a replacement mode prediction from the stationary branch and test it independently without refitting | PLANNED |
