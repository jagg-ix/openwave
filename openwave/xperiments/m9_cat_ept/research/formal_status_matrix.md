# CAT/EPT formal interface status

This matrix records `jagg-ix/entropic-physlib-private@entropic-physlib-linear-full` at `54b4ced090b200fac7ff04ee6a7e8797f1263049`. It is separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | action certificate, stationarity and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell PDE | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and all-time flow | conditional | explicit globally Lipschitz vector field and tangency |
| Maximal development | conditional | fixed-Cauchy extensions and smooth quotient data |
| Gauge-covariant cubic Born-density backreaction uniqueness | directly proved with explicit class | locality, gauge covariance, cubic homogeneity and normalization are premises |
| Cubic continuum `C(X,ℂ)` evolution | local existence/uniqueness plus explicit global positive-time irreversible flow | exact pointwise cubic sector on compact continuous-field carriers |
| Fixed spatial multiplication-energy plus cubic damping | explicit global positive-time pointwise flow and norm contraction | fixed continuous multiplication energy; not a spatial differential or state-dependent Hamiltonian |
| Mode-diagonal Caticha unbounded generator | self-adjoint/closable with explicit scope | measurable real diagonal symbols |
| Homogeneous CAT/EPT damping and phase-plus-damping | maximally dissipative with explicit contraction `C₀` semigroups | bounded homogeneous sectors, not the general unbounded functional differential generator |
| Free continuum kinetic Kolmogorov model | positive smooth kernel, bracket certificate, and explicit PDE derivative identities | free constant-coefficient model, not general curved/nonlinear hypoellipticity |
| Entropic time versus physical proper time | directly proved with explicit physical sector | positive imaginary Einstein energy and action-rate calibration; not every entropy arrow |
| M9.63 coefficient pair | unique under two declared Gaussian self-consistency conditions | the conditions are not derived in Lean from the full coupled action |
| Spatial cubic--quintic Laplacian PDE | exact OpenWave coercive energy bound and nested numerical flow | no kernel-formalized arbitrary-`H¹` local/global theorem |
| Arbitrary-`H¹` orbital stability | open end-to-end | M9.64 qualifies only the preregistered small scale orbit numerically |
| M9.65 breathing prediction | frozen and prediction-ready, not validated | collective-coordinate approximation plus reduced-Compton spatial anchor; no independent comparison yet |

## Current source pins

- `IpekCatichaSuperpositionViolation.lean` — `e46898d0013c22e983051b7248160323e64f468f`
- `IpekCatichaUnboundedGenerator.lean` — `605a3eb7dd7055de4b1d5ce3d8eacecea136f70a`
- `EntropicDynamicsLocalTimeFokkerPlanck.lean` — `99c39cd8dd3629831e7361a5e7e72eaaa7483c35`
- `Clock/EntropicAgreement.lean` — `8d7cb5a9c87dba47beefdc4a6c317aa872536632`
- `EntropicComplexEinstein.lean` — `3e480aca62a95ae4b739dd92e3aa97ffea1b4414`

The new formal work narrows the open continuum boundary. It does not justify reporting the selected cubic--quintic particle branch or its physical prediction as formally or experimentally validated.
