# CAT/EPT formal interface status

This matrix records the live PhysLib baseline `496b275336f30c0f934fe4ddcfa9fbfd99fa567c` and PR #16 head `9a15bf5023980f6bc401671de7dc7dca164a52d0`. Earlier M9.69--M9.71 generated ledgers retain their immutable theorem snapshot `51aad63b2541a1377a001df71b85dfe35f26c0af`. Formal theorem status remains separate from OpenWave platform validation.

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
| Bounded `H¹` weak sequential compactness with norm-bound retention | directly proved on live base | weak convergence, not automatic mass or norm convergence |
| Weak plus norm convergence implies strong `H¹` convergence | directly proved on live base | requires norm closure from the target variational problem |
| Tight probability measures have convergent subsequences | directly proved on live base | tightness after recentering remains model-specific |
| Joint field/density subsequence | directly proved on live base | consumes H¹ boundedness and probability tightness |
| Predicate-carrier joint field/density subsequence | directly proved in PR #16 | transports the live theorem through `hOneEnergyEquiv` |
| Conditional complete-carrier direct method | directly proved on live base | requires bounded minimizing sequence and weak lower semicontinuity |
| Constrained `H¹` direct method | directly proved in PR #16 | additionally requires sequential weak closure of the constraint |
| Local `H¹` existence and uniqueness | directly proved on live base for every `C¹` autonomous generator | target generator must map `H¹ → H¹` and be `C¹` |
| Schrödinger--Newton negative normalized level | directly proved on live base | excludes concentration--compactness vanishing under explicit seed hypotheses |
| Exact cubic mass law and strict subadditivity | directly proved on live base | compact-core variational result |
| Quantitative positive cluster binding gap | directly proved on live base | excludes dichotomy under explicit mass-split and seed hypotheses |
| Compactness branch from explicit trichotomy | directly proved in PR #16 | trichotomy and translation-tightness implications remain inputs |
| Compact-sublevel Cazenave--Lions orbital stability | directly proved on live base | requires compact minimizer orbit/sublevel and conserved admissible flow |
| Cubic--quintic density slack factorization | directly proved in PR #16 | exact algebra for arbitrary real `alpha`, nonzero `beta`, and density |
| Cubic--quintic density coercivity | directly proved in PR #16 | requires `beta > 0` and nonnegative density |
| Normalized-mass weak closure | open for target carrier | needed to instantiate constrained attainment |
| Weak lower semicontinuity of promoted target energy | open | target Hartree/cubic--quintic functional must be promoted to the complete carrier |
| Concrete target generator maps `H¹ → H¹` and is `C¹` | open | needed to instantiate live local existence/uniqueness |
| Translation tightness / concentration trichotomy | open end-to-end | Prokhorov and joint compactness consequences are already proved once tightness is supplied |
| Global conservative target flow and invariants | open end-to-end | local mechanism exists; global mass/energy closure remains model-specific |
| Compact target low-energy sublevel and branch identification | open end-to-end | needed to instantiate live orbital-stability theorem for M9.69 |
| Entropic time versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.69 stationary branch | OpenWave numerical result | no Lean existence theorem; conditional on selected coefficients |
| M9.65 breathing prediction | internally tested and falsified | Gaussian collective-coordinate approximation |
| M9.71 replacement radial mode | passes held-out grids and independent M9.74 method | no external experiment or physical validation |

## Current source pins

- live PhysLib base — `496b275336f30c0f934fe4ddcfa9fbfd99fa567c`
- PhysLib PR #16 head — `9a15bf5023980f6bc401671de7dc7dca164a52d0`
- live H¹ source blob — `bd421597ff33177f08de1063dc91fec84a6d1420`
- live Schrödinger--Newton energy blob — `43ad108a3c0c08730f3892de2d2480697db8e357`
- live H¹ dynamics/orbital source blob — `b9a094a57398efc11825885d8c2f3efa5654824c`
- PR #16 theorem blob — `24e14292478aeb7c78b52efdb00d30e4d84a870c`
- frozen M9.69--M9.71 theorem snapshot — `51aad63b2541a1377a001df71b85dfe35f26c0af`

The corrected boundary is substantially narrower than previously reported: complete weak H¹ compactness, norm-bound retention, strong closure from weak-plus-norm convergence, Prokhorov compactness consequences, local H¹ ODE well-posedness, and the Cazenave--Lions stability mechanism are already formal. Remaining work is target-generator regularity, closure/lower-semicontinuity, derivation of tightness, global conserved flow, and compact-sublevel identification.
