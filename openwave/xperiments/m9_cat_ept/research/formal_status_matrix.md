# CAT/EPT formal interface status

This matrix records live PhysLib baseline `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82`, criterion-bridge branch `agent/m9-criterion-reduction-spin-maxwell-thermal` at `34e4ae551304dae31548efeec7969040b3059d58`, active PR #16 at `83542cc13af0a966a072d90f2082c49785d20c55`, and active PR #17 at `2cb1003ede54dc7d8487a8b397a1cacf15728feb`. Formal theorem status remains separate from OpenWave platform and physical validation.

| Interface | Status | Boundary |
| --- | --- | --- |
| Fermion-fermion exchange phase `-1` | directly proved on live base | field-statistics assignment is a declared sector |
| Two-state antisymmetry and identical-state exclusion | packaged on criterion bridge branch | does not dynamically assign a specific CAT/EPT excitation as fermionic |
| Smooth harmonic source-free Maxwell solution | directly proved on live base | free field, not coupled emergence or photon quantization |
| Harmonic Maxwell solution is a plane wave | directly proved on live base | no empirical unit calibration |
| Finite spectral heat multiplier and semigroup | packaged on criterion bridge branch | finite spectral carrier, not microscopic thermodynamics |
| Spectral zero-mode heat conservation and zero-diffusivity limit | packaged on criterion bridge branch | no material-specific transport calibration |
| Complete continuum `H¹(ℝ³)` carrier and weak compactness | directly proved | norm/no-loss comes from target interaction closure |
| Actual Born probability and first-moment compactness | directly proved | recentered first-moment bound remains target-specific |
| Hartree convergence from `L^(6/5)` Born convergence | directly proved | local cubic--quintic interaction convergence remains separate |
| Energy-split no-loss, minimizer, compact orbit, stability mechanism | directly proved | consumes localization, interaction closure, and conserved flow |
| Cubic--quintic coercivity and corrected weak/mild composition | proved in PR #16 | concrete Duhamel construction and conservation remain inputs |
| Lean/ZIL evidence lifecycle and omission reconciliation | proved in PR #17 | proof verification remains distinct from declaration identity |
| Bounded `H¹ → H¹` Laplacian generator | rejected | Fourier ratio grows as `k²`; natural weak bound is `H¹ → H⁻¹` |
| M9.78--M9.80 finite Duhamel, recentering and orbit identification | OpenWave numerical results | not continuum well-posedness, conservation, or Lean identity |
| Continuum energy-critical Duhamel/Strichartz flow | open | must construct the actual `H¹` mild evolution |
| Analytic recentered localization and local interaction convergence | open | needed for continuum minimizing-orbit compactness |
| Global continuum mass and energy conservation | open | finite-grid ledgers do not prove it |
| Analytic identification of M9.69 with minimizing orbit | open | finite stationary residual and relaxation are insufficient |
| Independent branch calibration and external dataset | open | required before physical mode comparison |

## Criterion implications

- `spin_half_statistics`: formal exchange/exclusion plus OpenWave double-cover and two-state controls support platform validation.
- `em_waves`: formal harmonic Maxwell plane wave plus exact executable wave controls support platform validation.
- `thermal_field`: formal finite spectral heat identities plus executable entropy/dissipation controls support platform validation.

These implications do not transfer to physical particle identity, photon quantization, or microscopic thermodynamic derivation.
