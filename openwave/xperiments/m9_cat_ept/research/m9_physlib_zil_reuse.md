# PhysLib/ZIL reuse map through M9.77

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | merged `main` after PR #77 | `009efb37d535174712109c550e8da06b77dd8f9c` | simulation/evidence baseline through M9.74 |
| `jagg-ix/openwave` | `agent/m9-hminus-one-mild-flow-75-77` | current work branch | corrected M9.75--M9.77 evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` | complete H¹/Born compactness, interaction no-loss, ground-state orbit, and orbital-stability authority |
| `jagg-ix/entropic-physlib-private` | active PR #16 branch | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic compactness plus corrected weak/mild-flow composition |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing and evidence conventions |

## Deep formal source inventory

| Path | Reused result |
| --- | --- |
| `EuclideanSobolevFrequencyLocalization.lean` | complete `H¹(ℝ³)` carrier; Born density/probability; first-moment compactness; energy-split no-loss; normalized minimizer; compact minimizing orbit |
| `SchrodingerNewtonEnergy.lean` | HLS/Sobolev control, negative normalized level, mass scaling, strict subadditivity, positive binding gaps |
| `SelfBoundSchrodingerNewtonPDE.lean` | Hartree interaction convergence, local supplied-`C¹` flow mechanism, actual Born-law minimizing orbit, and Cazenave--Lions stability composition |
| `CubicQuinticOrbitalStability.lean` | density coercivity, predicate-carrier bridges, constrained direct method, concentration branch composition |
| `CubicQuinticMildFlow.lean` | corrected weak-generator interface, target interaction convergence, no-loss normalization closure, compact minimizing orbit, global conservative mild-flow certificate |
| `CubicQuinticMildFlowAudit.lean` | axiom-clean/non-vacuity registration for M9.75--M9.77 bridge theorems |

## Corrected target interpretation

- **M9.75:** the Laplacian is not a bounded `H¹ → H¹` map. The natural topology is weak/dual `H¹ → H⁻¹`. The unit-mass sphere is not globally weakly closed, and the attractive energy is not unconditionally weakly lower semicontinuous. Strong no-loss and mass closure follow after localized interaction convergence.
- **M9.76:** translation drift is the compactness obstruction. Recentring makes the M9.69 finite-grid orbit collapse, while the live Born first-moment and interaction-closure theorem supplies the correct continuum compactness implication from explicit localization data.
- **M9.77:** the live theorem already converts a global admissible energy-conserving flow and Born compactness data into a nonempty compact uniformly stable minimizing orbit. PR #16 exposes the corrected weak/mild-flow certificate; OpenWave supplies finite-grid long-time evidence only.

## Current decisions

- bounded `H¹ → H¹` Laplacian target: `rejected`
- weak/dual `H¹ → H⁻¹` generator interface: `selected`
- global weak closure of unit mass sphere: `false`
- strong no-loss normalized-mass closure from interaction convergence: `proved`
- unconditional attractive-energy weak lower semicontinuity: `false`
- target minimizer/compact orbit from Born localization and interaction closure: `proved from explicit premises`
- stable minimizing orbit from global conservative weak/mild-flow certificate: `proved from explicit premises`
- finite-grid translation orbit recentered: `true`
- five-perturbation aligned long-time campaign passes: `true`
- concrete energy-critical Duhamel/Strichartz flow constructed: `false`
- external experimental comparison: `false`
- platform counts: `0 validated / 20 partial / 1 negative`

## Open boundaries

- construct the concrete cubic--quintic Duhamel/Strichartz flow in `H¹` with weak generator in `H⁻¹`;
- prove recentered first-moment bounds and local cubic--quintic interaction convergence for the target minimizing family;
- prove global mass and energy conservation for the continuum target flow;
- analytically identify the minimizing orbit with M9.69;
- compare the immutable radial mode with external physical evidence.

## Status policy

Use `directly proved`, `proved from explicit premises`, `numerically qualified`, `internally tested`, `externally tested`, and `validated` as distinct states. Lean remains proof authority; OpenWave owns simulation evidence; ZIL records identities and scope; human review controls physical promotion.