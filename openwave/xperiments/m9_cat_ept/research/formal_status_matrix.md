# CAT/EPT formal interface status

This matrix records the live PhysLib baseline `496b275336f30c0f934fe4ddcfa9fbfd99fa567c`, PR #16 head `9a15bf5023980f6bc401671de7dc7dca164a52d0`, and the immutable M9.69--M9.71 theorem snapshot `51aad63b2541a1377a001df71b85dfe35f26c0af`. Formal theorem status remains separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | action certificate, stationarity, and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell PDE | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and maximal development | conditional | concrete vector field, tangency, fixed-Cauchy, and quotient data |
| Fixed-spatial-energy cubic continuum flow | jointly continuous contractive nonlinear semiflow | dissipative pointwise cubic flow, not the conservative Laplacian PDE |
| Complete continuum `H¹(ℝ³)` carrier | directly constructed on live base | exact Bessel-energy equivalence |
| Bounded H¹ weak compactness with norm-bound retention | directly proved on live base | weak convergence, not automatic mass/norm closure |
| Weak plus norm implies strong H¹ convergence | directly proved on live base | requires target norm convergence |
| Tight probability measures have convergent subsequences | directly proved on live base | recentered target tightness remains model-specific |
| Joint H¹ field/density subsequence | directly proved on live base | consumes H¹ boundedness and probability tightness |
| Predicate-carrier joint field/density bridge | directly proved in PR #16 | transports live compactness through `hOneEnergyEquiv` |
| Complete-carrier direct method | directly proved on live base | bounded minimizing sequence and weak lower semicontinuity required |
| Constrained direct method | directly proved in PR #16 | sequential weak closure additionally required |
| Local H¹ existence and uniqueness | directly proved on live base for every `C¹` generator | concrete target generator must map H¹ to H¹ and be `C¹` |
| Negative normalized variational level | directly proved | excludes vanishing under explicit seed assumptions |
| Strict subadditivity and positive binding gap | directly proved | exclude dichotomy under explicit split/seed assumptions |
| Compact branch from explicit trichotomy | directly proved in PR #16 | target trichotomy and translation tightness remain inputs |
| Compact-sublevel Cazenave--Lions orbital stability | directly proved on live base | requires compact minimizer orbit/sublevel and conserved admissible flow |
| Cubic--quintic density coercivity | directly proved in PR #16 | exact pointwise factorization and lower bound |
| Normalized-mass weak closure | open for target carrier | needed to instantiate constrained attainment |
| Weak lower semicontinuity of promoted target energy | open | target Hartree/cubic--quintic energy must be promoted to complete H¹ |
| Concrete target generator H¹ mapping and `C¹` regularity | open | needed to instantiate live local well-posedness |
| Recentered target tightness / concentration trichotomy | open | Prokhorov and joint compactness consequences are already proved once tightness is supplied |
| Global conservative target flow and invariants | open | local mechanism exists; global mass/energy closure remains model-specific |
| Compact target low-energy sublevel and branch identification | open | needed to instantiate live orbital stability for M9.69 |
| Entropic time versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.69 stationary branch | OpenWave numerical result | no Lean existence theorem; conditional on selected coefficients |
| M9.65 breathing prediction | internally tested and falsified | Gaussian collective-coordinate approximation |
| M9.71 replacement radial mode | passes held-out grids and independent M9.74 method | no external experiment or physical validation |

## Current source pins

- live PhysLib base — `496b275336f30c0f934fe4ddcfa9fbfd99fa567c`
- PhysLib PR #16 head — `9a15bf5023980f6bc401671de7dc7dca164a52d0`
- live H¹ source blob — `bd421597ff33177f08de1063dc91fec84a6d1420`
- live Schrödinger--Newton energy blob — `43ad108a3c0c08730f3892de2d2480697db8e357`
- live H¹ dynamics/orbital blob — `b9a094a57398efc11825885d8c2f3efa5654824c`
- PR #16 theorem blob — `24e14292478aeb7c78b52efdb00d30e4d84a870c`
- frozen M9.69--M9.71 theorem snapshot — `51aad63b2541a1377a001df71b85dfe35f26c0af`

The corrected boundary is substantially narrower than previously reported: weak H¹ compactness, norm-bound retention, strong closure from weak-plus-norm convergence, Prokhorov compactness consequences, local H¹ ODE well-posedness, and the Cazenave--Lions stability mechanism are already formal. Remaining work is target-generator regularity, closure/lower-semicontinuity, derivation of tightness, global conserved flow, and compact-sublevel branch identification.
