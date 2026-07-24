# CAT/EPT formal interface status

This matrix records `jagg-ix/entropic-physlib-private@entropic-physlib-linear-full` at `adbe9ead533d56ea7acd18e4c9ad5dacafd973ff`. It is separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | action certificate, stationarity and declared carriers |
| Global Einstein--Hilbert/electrogravitic actions | proved with explicit scope | dominated differentiation and analytic hypotheses |
| Intrinsic curved Maxwell PDE | directly proved | equation identity, not automatic physical Cauchy data |
| ADM constraint propagation and all-time flow | conditional | explicit globally Lipschitz vector field and tangency |
| Maximal development | conditional | fixed-Cauchy extensions and smooth quotient data |
| Gauge-covariant cubic Born-density backreaction uniqueness | directly proved with explicit class | locality, gauge covariance, cubic homogeneity and normalization are premises |
| Cubic continuum `C(X,ℂ)` evolution | local existence and uniqueness proved with explicit scope | cubic pointwise generator on compact continuous-field carrier |
| Mode-diagonal Caticha unbounded generator | self-adjoint/closable with explicit scope | requires measurable real diagonal symbols |
| Homogeneous CAT/EPT damping | maximally dissipative with explicit `C₀` contraction semigroup | exact `-γI` sector, not full nonlinear generator |
| Free continuum kinetic Kolmogorov model | positive smooth kernel and bracket certificate directly proved | free constant-coefficient model, not general nonlinear/curved hypoellipticity |
| Entropic time versus physical proper time | directly proved with explicit physical sector | positive imaginary Einstein energy and derived action-rate clock; not every entropy arrow |
| Selected cubic--quintic generator | open end-to-end | quintic saturation and numerical coefficients not formally derived |
| Arbitrary-`H¹` orbital stability | open end-to-end | M9.61 is a Gaussian-orbit/tightness bridge only |
| Physical calibration | open end-to-end | M9.62 defines gates but promotes zero physical predictions |

## New source pins

- `IpekCatichaSuperpositionViolation.lean` — `7791ba4af4381052865294434b070f2b1e6ba9df`
- `IpekCatichaUnboundedGenerator.lean` — `ddc009e49b64d8b33bede7c67c8392c1ef7cf30a`
- `EntropicDynamicsLocalTimeFokkerPlanck.lean` — `00734bf484cd0dd724120d68fc8d41066acae582`
- `Clock/EntropicAgreement.lean` — `8d7cb5a9c87dba47beefdc4a6c317aa872536632`
- `EntropicComplexEinstein.lean` — `3e480aca62a95ae4b739dd92e3aa97ffea1b4414`
