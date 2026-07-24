# CAT/EPT formal interface status

This matrix separates the current PhysLib baseline `f148278ec8264d031753d9def49cd2133ac4768d`, the theorem snapshot `51aad63b2541a1377a001df71b85dfe35f26c0af` pinned by generated OpenWave ledgers, and the rebased audited PR #16 head `f165cd8ba524a4274cb46bcd4c4ba1f12a274bf7`. It is separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | action certificate, stationarity, and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell PDE | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and maximal development | conditional | concrete vector field, tangency, fixed-Cauchy, and quotient data |
| Gauge-covariant cubic Born-density law | directly proved inside an explicit class | locality, gauge covariance, cubic homogeneity, and normalization are premises |
| Fixed-spatial-energy cubic continuum flow | jointly continuous contractive nonlinear semiflow | pointwise cubic damping on `C(X,ℂ)`, not a Laplacian PDE |
| Positive-damping asymptotics | strict contraction, convergence to zero, unique fixed field, zero global attractor | exact dissipative cubic sector |
| Schrödinger--Newton compact-core binding gaps | directly quantified on current base | excludes compact-core dichotomy under explicit seed assumptions; not full `H¹` attainment |
| Cubic--quintic density slack factorization | directly proved in PR #16 | exact algebra for arbitrary real `alpha`, nonzero `beta`, and density |
| Cubic--quintic density coercivity | directly proved in PR #16 | requires `beta > 0` and nonnegative density |
| `H1OrbitalCertificate` energy-excess invariance | proved from explicit certificate data | requires a supplied flow and energy conservation |
| Uniform orbital-distance theorem | proved from explicit certificate data | requires flow, conservation, nonnegative distance, and coercive Lyapunov estimate |
| Compactness modulo symmetry | exported from explicit certificate data | concentration compactness is a premise, not derived from the PDE |
| ZIL theorem scope | attached in PR #16 | records unconditional algebra versus conditional analytic theorem |
| Axiom/non-vacuity audit | registered in a dedicated PR #16 module | no local Lean toolchain was available in this execution environment |
| Spatial cubic--quintic `H¹` flow | open end-to-end | local/global well-posedness and conserved quantities are not yet constructed |
| Nonzero-branch orbital stability from the PDE | open end-to-end | must instantiate every M9.70 certificate field for the M9.69 branch |
| Entropic time versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.69 stationary branch | OpenWave numerical result | no Lean existence theorem; conditional on selected coefficients |
| M9.65 breathing prediction | internally tested and falsified | Gaussian collective-coordinate approximation |
| M9.71 replacement radial mode | passes internal held-out grids | no external experiment or physical validation |

## Current source pins

- PhysLib PR #16 head — `f165cd8ba524a4274cb46bcd4c4ba1f12a274bf7`
- current PhysLib base — `f148278ec8264d031753d9def49cd2133ac4768d`
- frozen theorem snapshot — `51aad63b2541a1377a001df71b85dfe35f26c0af`
- theorem-snapshot source blob pinned by generated ledger — `b1bbf0bd6e58b41796aba1d63919f3cd6fe7aca4`
- audited theorem source in PR #16 — same theorem statements plus ZIL scope attachments

The M9.70 formalization closes the algebraic and certificate-level theorem. It does not close the analytic construction needed to instantiate that certificate for the conservative spatial particle PDE.
