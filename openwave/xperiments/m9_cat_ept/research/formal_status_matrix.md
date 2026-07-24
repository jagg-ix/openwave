# CAT/EPT formal interface status

This matrix records the live PhysLib baseline `0a04328a01b7911078c4f9d01cc0c8c963519dc2` and the updated PR #16 head `5d0cdf07c891b1dbe7381b93c2d794b593fae09d`. Earlier M9.69--M9.71 generated ledgers retain their immutable theorem snapshot `51aad63b2541a1377a001df71b85dfe35f26c0af`. Formal theorem status remains separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | action certificate, stationarity, and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell PDE | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and maximal development | conditional | concrete vector field, tangency, fixed-Cauchy, and quotient data |
| Gauge-covariant cubic Born-density law | directly proved inside an explicit class | locality, gauge covariance, cubic homogeneity, and normalization are premises |
| Fixed-spatial-energy cubic continuum flow | jointly continuous contractive nonlinear semiflow | pointwise cubic damping on `C(X,ℂ)`, not the conservative Laplacian PDE |
| Positive-damping asymptotics | strict contraction, convergence to zero, unique fixed field, zero global attractor | exact dissipative cubic sector |
| Complete continuum `H¹(ℝ³)` carrier | directly constructed on live base | exact Bessel-energy equivalence with the predicate-defined Sobolev carrier |
| Bounded `H¹` weak sequential compactness | directly proved on live base | weak, not strong Rellich compactness; mass preservation needs a separate argument |
| Conditional complete-carrier direct method | directly proved on live base | requires Sobolev-bounded minimizing sequence and sequential weak lower semicontinuity |
| Constrained `H¹` direct method | directly proved in PR #16 | additionally requires sequential weak closure of the chosen constraint |
| Schrödinger--Newton negative normalized level | directly proved on live base | excludes concentration--compactness vanishing under explicit seed hypotheses |
| Exact cubic mass law and strict subadditivity | directly proved on live base | compact-core variational result |
| Quantitative positive cluster binding gap | directly proved on live base | excludes dichotomy under explicit mass-split and seed hypotheses |
| Compactness branch from explicit trichotomy | directly proved in PR #16 | trichotomy and branch-identification implications remain inputs |
| Cubic--quintic density slack factorization | directly proved in PR #16 | exact algebra for arbitrary real `alpha`, nonzero `beta`, and density |
| Cubic--quintic density coercivity | directly proved in PR #16 | requires `beta > 0` and nonnegative density |
| Uniform orbital-distance theorem | proved from explicit dynamics certificate | requires conservative flow, energy conservation, compactness, and coercivity |
| Normalized-mass weak closure | open for target carrier | needed to instantiate constrained attainment |
| Weak lower semicontinuity of promoted target energy | open | Hartree/cubic--quintic functional must be promoted to the complete carrier |
| Translation tightness / concentration trichotomy | open end-to-end | vanishing and dichotomy are excluded once the trichotomy is supplied |
| Conservative spatial cubic--quintic `H¹` flow | open end-to-end | local/global well-posedness and mass/energy conservation are not yet constructed |
| Nonzero-branch coercivity modulo phase/translation | open end-to-end | needed to instantiate orbital stability for the M9.69 branch |
| Entropic time versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.69 stationary branch | OpenWave numerical result | no Lean existence theorem; conditional on selected coefficients |
| M9.65 breathing prediction | internally tested and falsified | Gaussian collective-coordinate approximation |
| M9.71 replacement radial mode | passes held-out grids and independent M9.74 method | no external experiment or physical validation |

## Current source pins

- live PhysLib base — `0a04328a01b7911078c4f9d01cc0c8c963519dc2`
- PhysLib PR #16 head — `5d0cdf07c891b1dbe7381b93c2d794b593fae09d`
- live H¹ source blob — `a3e5f79be6c3d650f48ea1c164541eedf8588c5b`
- live Schrödinger--Newton energy blob — `43ad108a3c0c08730f3892de2d2480697db8e357`
- updated PR #16 theorem blob — `3a5b8737331fb1bbae0dea62af2db21f58f1b332`
- frozen M9.69--M9.71 theorem snapshot — `51aad63b2541a1377a001df71b85dfe35f26c0af`

The corrected boundary is substantially narrower than previously reported: weak continuum H¹ compactness, a direct-method engine, vanishing exclusion, and dichotomy exclusion are already formal. The remaining work is to instantiate closure/lower-semicontinuity, derive translation tightness, build the conservative flow, and prove nonzero-branch coercivity.
