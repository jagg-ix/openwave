# CAT/EPT formal interface status

This matrix separates the merged PhysLib baseline `e2c06741c3e49deb604082a2e9c2e918eab8d545` from the M9.70 work branch `agent/m9-cubic-quintic-h1-certificate-70` at `51aad63b2541a1377a001df71b85dfe35f26c0af`. It is separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | action certificate, stationarity, and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell PDE | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and maximal development | conditional | concrete vector field, tangency, fixed-Cauchy, and quotient data |
| Gauge-covariant cubic Born-density law | directly proved inside an explicit class | locality, gauge covariance, cubic homogeneity, and normalization are premises |
| Fixed-spatial-energy cubic continuum flow | jointly continuous contractive nonlinear semiflow | pointwise cubic damping on `C(X,ℂ)`, not a Laplacian PDE |
| Positive-damping asymptotics | strict contraction, convergence to zero, unique fixed field, zero global attractor | exact dissipative cubic sector |
| Cubic--quintic density slack factorization | directly proved on M9.70 branch | exact algebra for arbitrary real `alpha`, nonzero `beta`, and density |
| Cubic--quintic density coercivity | directly proved on M9.70 branch | requires `beta > 0` and nonnegative density |
| `H1OrbitalCertificate` energy-excess invariance | proved from explicit certificate data | requires a supplied flow and energy conservation |
| Uniform orbital-distance theorem | proved from explicit certificate data | requires flow, conservation, nonnegative distance, and coercive Lyapunov estimate |
| Compactness modulo symmetry | exported from explicit certificate data | concentration compactness is a premise, not derived from the PDE |
| Spatial cubic--quintic `H¹` flow | open end-to-end | local/global well-posedness and conserved quantities are not yet constructed |
| Nonzero-branch orbital stability from the PDE | open end-to-end | must instantiate every M9.70 certificate field for the M9.69 branch |
| Entropic time versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.69 stationary branch | OpenWave numerical result | no Lean existence theorem; conditional on selected coefficients |
| M9.65 breathing prediction | internally tested and falsified | Gaussian collective-coordinate approximation |
| M9.71 replacement radial mode | passes internal held-out grids | no external experiment or physical validation |

## Current source pins

- `CubicQuinticOrbitalStability.lean` — `b1bbf0bd6e58b41796aba1d63919f3cd6fe7aca4`
- `IpekCatichaSuperpositionViolation.lean` — `d4f6e760e20dc1a3d7b4db7e21b8569bc9d307a7`
- `IpekCatichaUnboundedGenerator.lean` — `605a3eb7dd7055de4b1d5ce3d8eacecea136f70a`
- `EntropicDynamicsLocalTimeFokkerPlanck.lean` — `99c39cd8dd3629831e7361a5e7e72eaaa7483c35`
- `Clock/EntropicAgreement.lean` — `8d7cb5a9c87dba47beefdc4a6c317aa872536632`

The M9.70 formalization closes the algebraic and certificate-level theorem. It does not close the analytic construction needed to instantiate that certificate for the conservative spatial particle PDE.
