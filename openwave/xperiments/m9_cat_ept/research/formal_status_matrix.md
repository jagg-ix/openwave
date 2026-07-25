# CAT/EPT formal interface status

This matrix records live PhysLib baseline `c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3`, criterion-bridge PR #18 at `19ef639d0ab849f92fb462d5899817ac1a5c4161`, active PR #16 at `83542cc13af0a966a072d90f2082c49785d20c55`, and active PR #17 at `2cb1003ede54dc7d8487a8b397a1cacf15728feb`. Formal theorem status remains separate from OpenWave platform and physical validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Fermion exchange, harmonic Maxwell wave, finite spectral heat flow | formal surfaces available or packaged in PR #18 | criterion closure does not imply particle identity, photons, or microscopic thermodynamics |
| Complete continuum `H¹(ℝ³)` carrier and weak compactness | directly proved | norm/no-loss comes from target interaction closure |
| Local `L1` Rellich plus recentered tails gives global `L1` convergence | directly proved on live base | model must supply local convergence and uniform tail estimates |
| `L1` plus uniform `L3` gives strong `L^(6/5)` | directly proved on live base | model must supply the finite `L3` bound |
| Recentered localized Rellich gives Born `L^(6/5)` and Hartree convergence | directly proved on live base | OpenWave M9.84 qualifies premises only on nested finite grids |
| Energy-split no-loss, minimizer, compact orbit, stability mechanism | directly proved | consumes target local interaction closure and a conserved flow |
| Cubic--quintic coercivity and corrected weak/mild composition | proved in PR #16 | concrete Duhamel construction and conservation remain inputs |
| Lean/ZIL evidence lifecycle and omission reconciliation | proved in PR #17 | proof verification remains distinct from declaration identity |
| M9.84 nested Rellich/Hartree campaign | OpenWave finite-grid evidence | not a continuum compactness proof |
| M9.85 local interaction and `H1` no-loss campaign | OpenWave finite-grid evidence | not continuum local-interaction convergence or conservation |
| M9.86 branch feature certificate | OpenWave finite-grid evidence | not analytic minimizing-orbit identity or particle identity |
| Continuum energy-critical Duhamel/Strichartz flow | open | must construct the actual `H¹` mild evolution |
| Model-level recentered Rellich and local interaction convergence | open end-to-end | theorem infrastructure exists; target hypotheses remain to be proved |
| Global continuum mass and energy conservation | open | finite-grid ledgers do not prove it |
| Analytic identification of M9.69 with minimizing orbit | open | fingerprint and seed/grid convergence are insufficient |
| Independent branch calibration and external dataset | open | required before physical mode comparison |

The platform matrix remains `3 validated / 17 partial / 1 negative`. M9.84--M9.86 strengthen the particle-stability evidence chain without transferring any stronger physical claim.
