# M9 global target plan

## Closure through M9.80

- **M9.78:** constructs the finite spectral Volterra/Duhamel map, closes a seven-step Picard iteration, and compares the mild trajectory with the existing Strang flow over three time refinements. The observed Duhamel/Strang error halves with the time step. This is not the continuum energy-critical Strichartz theorem.
- **M9.79:** estimates the evolving density centroid, recenters with the Fourier shift theorem, and refines centered first moment, tail mass, local cubic--quintic interaction, total mass, and energy. Energy drift is second order. Continuum localization and conservation remain open.
- **M9.80:** tests radial, quadrupole, and shell deformation directions. Each raises constrained energy, has positive symmetric second variation, and relaxes back to one finite-grid phase/translation orbit tube. The immutable M9.71 mode is preserved, while external comparison is blocked by missing analytic identity, particle identity, calibration, and dataset prerequisites.

## Current cross-repository state

| Repository | Revision | Contribution |
| --- | --- | --- |
| OpenWave merged base | `c3cdd5725e9b5455cf3f2fb35164e79cab1265d8` | merged PR #78 / closure through M9.77 |
| OpenWave work branch | `agent/m9-duhamel-conservation-identification-78-80` | M9.78--M9.80 implementation and evidence |
| PhysLib live base | `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` | complete `H¹`/Born compactness, interaction no-loss, minimizing orbit, and orbital-stability infrastructure |
| PhysLib PR #16 | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic compactness and corrected weak/mild-flow certificate composition |
| PhysLib PR #17 | `2cb1003ede54dc7d8487a8b397a1cacf15728feb` | Lean/ZIL evidence lifecycle, resolved omissions, and open-obligation registry |
| ZIL | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions and operational tooling |

## Theory boundary

The platform remains `0 validated / 20 partial / 1 negative`. The lepton hierarchy remains the sole criterion-level negative. M9.78--M9.80 materially strengthen internal mathematical and computational coherence but do not create an externally tested physical prediction.

The remaining analytic chain is now explicit:

1. construct the continuum energy-critical `H¹` Duhamel/Strichartz flow with weak generator in `H⁻¹`;
2. prove recentered Born localization and local-interaction convergence;
3. prove continuum mass and energy conservation;
4. identify the analytic minimizing orbit with M9.69;
5. independently calibrate the branch and register an external dataset before comparing the frozen mode.

## Next phase

| Target | Deliverable | State |
| --- | --- | --- |
| M9.81 | PhysLib continuum energy-critical Duhamel/Strichartz construction | NEXT |
| M9.82 | Analytic recentered localization, interaction convergence, and continuum conservation | GATED |
| M9.83 | Analytic branch identification and prerequisite-complete external protocol | PLANNED |
