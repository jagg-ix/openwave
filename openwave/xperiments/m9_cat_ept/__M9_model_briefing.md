# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 comparison criteria and now includes cross-repository evidence control, coefficient-condition falsification, adversarial spatial-flow tests, and the first no-refit test of a frozen physical subprediction.

## Platform status

- Zero criteria are fully validated in-platform.
- Twenty criteria are partial or bounded.
- One criterion remains an honest negative: the predictive lepton-mass hierarchy.
- Particle stability remains partial. The branch survives the M9.67 adversarial numerical campaign, but M9.66 rejects the Gaussian peak-density selection premise as a current first-principles derivation and the full `H¹` theorem remains open.
- The M9.65 breathing prediction has now been tested and falsified inside OpenWave. This is a negative result for that Gaussian collective-coordinate approximation, not for every CAT/EPT clock or particle mechanism.

## Cross-repository sources

| Repository | Ref | Current revision | Authority |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` | `e11e8fce88ce886812860ce747c48d32c8eaeb57` | simulation evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `e2c06741c3e49deb604082a2e9c2e918eab8d545` | Lean theorem authority |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence orchestration and install/test infrastructure |

M9.66--M9.68 result ledgers were frozen against ZIL snapshot `f39758f85ee6300b8060e4f8ea1ecf344ed32c96`. The later ZIL commit changes installation lifecycle tooling and does not alter the theorem/evidence interfaces consumed by these results.

## Latest formal changes consumed

- A jointly continuous nonlinear semiflow for fixed spatial multiplication energy plus cubic damping.
- Strict norm contraction for positive damping.
- Uniform convergence to the zero field and a singleton zero global attractor.

These are exact results for the cubic dissipative `C(X,ℂ)` sector. They do not prove the conservative spatial Laplacian-plus-quintic particle equation or stability of a nonzero localized branch.

## Latest closures

- **M9.66:** Gaussian scale stationarity is reduced-action-derived. Peak-density matching is not the normalized stationary field equation: the selected Gaussian has relative residual `0.485819`, and alternative local landmarks yield distinct positive coefficient pairs.
- **M9.67:** twelve anisotropic, phase, translation, noise, and scale perturbation runs preserve mass and energy numerically, remain boundary-clean, and respect the coercive gradient estimate. The formal `H¹` target remains open.
- **M9.68:** the frozen `omega_breath / omega_Compton = 2.634371114527` prediction was tested without refitting. Three grids measure `1.3468`--`1.4949`, missing by `43%`--`49%`; the subprediction fails its 5% gate.

ZIL records identities, receipts, scope, and evidence-state transitions. Lean remains proof authority; OpenWave remains simulation software.

## Next critical targets

1. M9.69 construct a stationary non-Gaussian localized branch from the full normalized spatial equation.
2. M9.70 kernel-formalize the conservative spatial cubic--quintic `H¹` PDE, compactness, and orbital stability.
3. M9.71 derive a replacement mode prediction from the stationary branch and test it independently without refitting.
