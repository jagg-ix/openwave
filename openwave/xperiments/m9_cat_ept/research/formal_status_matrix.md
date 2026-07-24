# CAT/EPT formal interface status

This matrix records the latest inspected status of `jagg-ix/entropic-physlib-private@entropic-physlib-linear-full`, pinned at commit `14ecf025ec58d2ec9e4731081c4ed1853f4468f0`.

It is separate from OpenWave platform validation. Lean remains proof authority; ZIL records source identities, dependency edges, scope, and open boundaries.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-to-Levi-Civita-to-Riemann-to-Ricci-to-Einstein chain | directly proved | chartwise construction plus intrinsic/global representation |
| Einstein--Maxwell--entropic equations from certified stationary action | proved with explicit scope | requires the action derivative certificate and stationarity |
| Global Einstein--Hilbert action | proved with explicit scope | dominated differentiation and declared Lorentzian measure data |
| Global electrogravitic action derivative seam | proved with explicit scope | arbitrary normed variation carrier with certified integrated derivative |
| Intrinsic curved Maxwell PDE and atlas independence | directly proved | equation identity, not automatic Cauchy well-posedness |
| Retarded/advanced Maxwell solutions | conditional | requires well-posed Cauchy/Green data |
| ADM constraint propagation and all-time flow | conditional | requires concrete globally Lipschitz vector field and tangency certificates |
| Maximal Cauchy development | conditional | requires coherent fixed-Cauchy extension maps and smooth quotient instantiation |
| LDDL finite trace preservation | theorem declarations present | separate ZIL evidence state may still require kernel-checked export |
| Cauchy/Lorentz broadening weak limit | theorem declarations present | separate ZIL evidence state may still require kernel-checked export |
| Full CAT/EPT nonlinear continuum generator/semigroup | open end-to-end | M9.57 closes only the finite action-to-generator bridge |
| Continuum kinetic existence, uniqueness, and hypoelliptic regularity | open end-to-end | M9.58 closes nested finite-grid and bracket controls only |

## Source pins

- `formalization/zil/electrogravitic-action-closure.zc` — `cf9110d8b4229c33a1e2cefa34c0719062a3f340`
- `GlobalEinsteinHilbertAction.lean` — `6862565fb915b5c6f1cc561b769e190b70f3156a`
- `GlobalElectrograviticAction.lean` — `39e807f424cf8384135299e84fdffc97fb506ee5`
- `ADMConstraintPropagation.lean` — `600b872eb73611de817df0d00dd6711570c567e2`
- `MaximalCauchyDevelopment.lean` — `2504c579fd8f8afe0a1670911142fb0e7ecdb2c0`
- `docs/EntropicDynamicsClosure.md` — `e9d542ea516492b6e308a5610f952f831f4ed1c5`
