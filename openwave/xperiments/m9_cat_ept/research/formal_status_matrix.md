# CAT/EPT formal interface status

This matrix records `jagg-ix/entropic-physlib-private@entropic-physlib-linear-full` at `e2c06741c3e49deb604082a2e9c2e918eab8d545`. It is separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | action certificate, stationarity and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell PDE | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and maximal development | conditional | concrete vector field, tangency, fixed-Cauchy and quotient data |
| Gauge-covariant cubic Born-density law | directly proved inside an explicit class | locality, gauge covariance, cubic homogeneity and normalization are premises |
| Fixed-spatial-energy cubic continuum flow | jointly continuous contractive nonlinear semiflow | pointwise cubic damping on `C(X,ℂ)`, not a Laplacian PDE |
| Positive-damping asymptotics | strict contraction, convergence to zero, unique fixed field, zero global attractor | exact cubic dissipative sector; the localized conservative branch is not its attractor |
| Mode-diagonal Caticha unbounded generator | self-adjoint/closable with explicit scope | measurable real diagonal symbols |
| Homogeneous CAT/EPT damping and phase-plus-damping | maximally dissipative with explicit contraction `C₀` semigroups | bounded homogeneous sectors |
| Free continuum kinetic Kolmogorov model | positive smooth kernel, bracket certificate, and explicit PDE identities | free constant-coefficient model |
| Entropic time versus physical proper time | proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration |
| M9.63 coefficient selection | scale stationarity derived; peak-density condition not formally derived | M9.66 finds a 48.6% stationary-field residual and alternative positive selections |
| Spatial cubic--quintic Laplacian PDE | exact OpenWave coercive bound plus nested/adversarial numerics | no kernel local/global `H¹` theorem or conserved-quantity formalization |
| Compactness and orbital stability of nonzero branch | open end-to-end | twelve adversarial runs do not replace concentration compactness or a stability theorem |
| M9.65 breathing prediction | independently tested and falsified inside OpenWave | no-refit three-grid result; not an external experiment and not a theory-wide falsification |

## Current source pins

- `IpekCatichaSuperpositionViolation.lean` — `d4f6e760e20dc1a3d7b4db7e21b8569bc9d307a7`
- `IpekCatichaUnboundedGenerator.lean` — `605a3eb7dd7055de4b1d5ce3d8eacecea136f70a`
- `EntropicDynamicsLocalTimeFokkerPlanck.lean` — `99c39cd8dd3629831e7361a5e7e72eaaa7483c35`
- `Clock/EntropicAgreement.lean` — `8d7cb5a9c87dba47beefdc4a6c317aa872536632`
- `GlobalElectrograviticAction.lean` — `39e807f424cf8384135299e84fdffc97fb506ee5`

The formal work closes the exact cubic dissipative semiflow, not the selected conservative spatial cubic--quintic particle theorem.
