# CAT/EPT formal interface status

This matrix records live PhysLib baseline `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82`, active PR #16 head `83542cc13af0a966a072d90f2082c49785d20c55`, and active PR #17 head `2cb1003ede54dc7d8487a8b397a1cacf15728feb`. Formal theorem status remains separate from OpenWave platform validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Complete continuum `H¹(ℝ³)` carrier and weak compactness | directly proved | norm/no-loss comes from target interaction closure |
| Actual Born probability and first-moment compactness | directly proved | recentered first-moment bound remains target-specific |
| Hartree convergence from `L^(6/5)` Born convergence | directly proved | local cubic--quintic interaction convergence remains separate |
| Energy-split no-loss, level attainment, normalization closure | directly proved | consumes localized interaction convergence |
| Born-law minimizer and compact minimizing orbit | directly proved | consumes localization, weak admissibility, and interaction closure |
| Cazenave--Lions minimizing-orbit stability | directly proved | consumes a global admissible energy-conserving flow |
| Cubic--quintic coercivity and corrected weak/mild composition | proved in PR #16 | concrete Duhamel construction and conservation remain inputs |
| Lean/ZIL evidence lifecycle and omission reconciliation | proved in PR #17 | proof verification remains distinct from declaration identity |
| Bounded `H¹ → H¹` Laplacian generator | rejected | Fourier ratio grows as `k²`; natural weak bound is `H¹ → H⁻¹` |
| Global weak closure of unit mass sphere | rejected | orthonormal modes converge weakly to zero |
| Unconditional weak lower semicontinuity of attractive energy | rejected | translated negative-energy states converge weakly to zero |
| M9.78 finite-Galerkin Duhamel fixed point | OpenWave numerical result | contracting Volterra map and refinement, not continuum Strichartz |
| M9.79 dynamically recentered localization/conservation | OpenWave numerical result | finite grid and finite time, not continuum theorems |
| M9.80 minimizing-orbit identification | OpenWave numerical result | positive directional curvature and relaxation, not Lean identity |
| Continuum energy-critical Duhamel/Strichartz flow | open | must construct the actual `H¹` mild evolution |
| Analytic recentered localization and local interaction convergence | open | needed for continuum minimizing-orbit compactness |
| Global continuum mass and energy conservation | open | finite-grid ledgers do not prove it |
| Analytic identification of M9.69 with minimizing orbit | open | finite stationary residual and relaxation are insufficient |
| Independent branch calibration and external dataset | open | required before physical mode comparison |
| M9.71 replacement radial mode | internally robust and externally blocked | no physical validation |

## Current source pins

- OpenWave merged base — `c3cdd5725e9b5455cf3f2fb35164e79cab1265d8`
- live PhysLib base — `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82`
- active PhysLib PR #16 — `83542cc13af0a966a072d90f2082c49785d20c55`
- active PhysLib PR #17 — `2cb1003ede54dc7d8487a8b397a1cacf15728feb`

The next correct target is a PhysLib continuum theorem stack, not another finite-grid substitute. External comparison remains inadmissible until branch identity and calibration are fixed independently.
