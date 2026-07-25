# M9 global target plan

## Closure through M9.77

- **M9.75:** rejects the earlier `H¹ → H¹` bounded-generator premise. Fourier modes make the Laplacian ratio grow as `k²`, while its `H¹ → H⁻¹` ratio is `k²/(1+k²) < 1`. The unit-mass sphere is not globally weakly closed, and translated negative-energy states disprove unconditional weak lower semicontinuity. PhysLib now derives strong no-loss, level attainment, and normalized-mass closure from localized Hartree/local-interaction convergence and the positive kinetic energy split.
- **M9.76:** the M9.69 translation orbit is noncompact before quotienting but collapses exactly after recentering. Centered first moment, tail mass, total mass, and energy are invariant. PhysLib composes Born first-moment localization and interaction convergence into existence and compactness of the complete minimizing orbit. General recentered target tightness remains an analytic input.
- **M9.77:** an explicit global conservative weak/mild-flow certificate instantiates the live Born-law Cazenave--Lions theorem. OpenWave evolves phase, translation, chirp, amplitude, and noise perturbations for `1.5` dimensionless time units; all remain in a small aligned `H¹` tube with mass/energy and boundary controls. The continuum Duhamel flow itself is not claimed constructed.

## Current cross-repository state

| Repository | Revision | Contribution |
| --- | --- | --- |
| OpenWave merged base | `009efb37d535174712109c550e8da06b77dd8f9c` | merged PR #77 / closure through M9.74 |
| OpenWave work branch | `agent/m9-hminus-one-mild-flow-75-77` | corrected M9.75--M9.77 implementation and evidence |
| PhysLib live base | `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` | complete H¹/Born compactness, interaction no-loss, ground-state orbit, and orbital-stability infrastructure |
| PhysLib PR #16 branch | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic compactness bridges plus corrected weak/mild-flow certificate composition |
| ZIL | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions and operational tooling |

## Corrected theory boundary

The platform remains `0 validated / 20 partial / 1 negative`. The lepton hierarchy remains the sole criterion-level negative. The replacement radial mode remains internally robust but externally untested.

The formal gap is now stated in the correct topology. The spatial Laplacian and energy-critical quintic term are not required to define a bounded `H¹ → H¹` autonomous ODE. The remaining target is a concrete `H¹` weak/mild Duhamel flow with generator in `H⁻¹`, together with recentered localization, local-interaction convergence, global conservation, and analytic branch identification.

## Next phase

| Target | Deliverable | State |
| --- | --- | --- |
| M9.78 | Construct the concrete energy-critical cubic--quintic Duhamel/Strichartz flow in `H¹` with weak generator in `H⁻¹` | NEXT |
| M9.79 | Prove recentered first-moment bounds, local-interaction convergence, and global mass/energy conservation | GATED |
| M9.80 | Identify the analytic minimizing orbit with M9.69 and compare the immutable radial mode with external physical evidence | PLANNED |