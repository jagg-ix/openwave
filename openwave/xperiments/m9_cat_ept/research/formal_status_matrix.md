# CAT/EPT formal interface status

This matrix records live PhysLib baseline `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` and active PR #16 branch head `83542cc13af0a966a072d90f2082c49785d20c55`. Formal theorem status remains separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Metric-built Einstein--Maxwell--entropic action/PDE chain | proved with explicit scope | declared action, carrier, and analytic hypotheses |
| Fixed-spatial-energy cubic continuum flow | jointly continuous contractive nonlinear semiflow | pointwise damping, not the conservative Laplacian PDE |
| Complete continuum `H¹(ℝ³)` carrier | directly constructed | exact Bessel-energy realization |
| Bounded weak subsequences and strong closure from weak plus norm | directly proved | norm/no-loss must come from target interaction closure |
| Actual Born-law probability and first-moment compactness | directly proved | recentered first-moment bound remains target-specific |
| Hartree interaction convergence from `L^(6/5)` Born convergence | directly proved | local cubic--quintic interaction convergence remains separate |
| Energy-split no-loss, level attainment, and normalization closure | directly proved | consumes localized interaction convergence and lower-level property |
| Born-law energy minimizer and compact minimizing orbit | directly proved | consumes first moment, weak admissibility, and interaction closure |
| Cazenave--Lions minimizing-orbit stability | directly proved | consumes a global admissible energy-conserving flow |
| Cubic--quintic density coercivity and concentration branch composition | proved in PR #16 | trichotomy/localization inputs remain explicit |
| Correct target interaction convergence wrapper | proved in PR #16 | Hartree closure plus supplied local-interaction convergence |
| Corrected weak/mild `H¹` flow certificate | proved in PR #16 | generator is tested in the `H¹` dual; concrete Duhamel construction remains open |
| Compact target minimizing orbit from Born localization | proved in PR #16 | recentered first moment and local interaction closure remain inputs |
| Uniformly stable minimizing orbit from global conservative weak/mild flow | proved in PR #16 | global flow and conservation laws remain certificate fields |
| Bounded `H¹ → H¹` Laplacian generator | rejected | Fourier ratio grows as `k²`; natural bound is `H¹ → H⁻¹` |
| Global weak closure of unit `L²` mass sphere | rejected | orthonormal modes converge weakly to zero while mass remains one |
| Unconditional weak lower semicontinuity of attractive target energy | rejected | translated negative-energy states converge weakly to zero |
| Concrete energy-critical Duhamel/Strichartz target flow | open | must construct `H¹` mild flow with weak generator in `H⁻¹` |
| Target recentered localization and local interaction convergence | open end-to-end | required for analytic minimizing-orbit compactness |
| Global target mass/energy conservation | open end-to-end | finite-grid conservation is not a continuum theorem |
| Analytic identification of M9.69 with minimizing orbit | open end-to-end | finite stationary residual is insufficient |
| M9.75 corrected generator audit | OpenWave exact/Fourier evidence | scoped closure, not a PDE construction |
| M9.76 recentered orbit audit | OpenWave numerical result | periodic translation quotient, not general continuum tightness |
| M9.77 aligned long-time orbit campaign | OpenWave numerical result | five perturbations, finite time and grid |
| M9.71 replacement radial mode | internally robust | no external experiment or physical validation |

## Current source pins

- live PhysLib base — `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82`
- active PhysLib PR #16 branch — `83542cc13af0a966a072d90f2082c49785d20c55`
- live `H¹`/Born compactness source blob — `211f40b255b0f4816260a726f3bc6ed7b1b011e9`
- live Schrödinger--Newton energy blob — `43ad108a3c0c08730f3892de2d2480697db8e357`
- live H¹ dynamics/orbital source blob — `6897b5cbdc2f36a2297f3d26ba4891d88231d3f8`

The corrected remaining target is not a generic Banach ODE on `H¹`. It is the concrete energy-critical weak/Duhamel flow, its localization and interaction convergence, continuum conservation, and analytic branch identification.