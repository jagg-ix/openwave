# PhysLib/ZIL reuse map through M9.80

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after PR #78 | `c3cdd5725e9b5455cf3f2fb35164e79cab1265d8` | merged simulation/evidence baseline through M9.77 |
| `jagg-ix/openwave` | `agent/m9-duhamel-conservation-identification-78-80` | current work branch | M9.78--M9.80 implementation and evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` | complete `H¹`/Born compactness, interaction no-loss, minimizing orbit, and orbital-stability authority |
| `jagg-ix/entropic-physlib-private` | active PR #16 | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic compactness and corrected weak/mild-flow composition |
| `jagg-ix/entropic-physlib-private` | active PR #17 | `2cb1003ede54dc7d8487a8b397a1cacf15728feb` | Lean-backed ZIL evidence lifecycle and open-obligation reconciliation |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | semantic routing and evidence conventions |

## Reused formal infrastructure

| Source | Reused result |
| --- | --- |
| `EuclideanSobolevFrequencyLocalization.lean` | complete `H¹` carrier, Born law, first-moment compactness, energy-split no-loss, minimizer, compact orbit |
| `SelfBoundSchrodingerNewtonPDE.lean` | Hartree convergence and Cazenave--Lions minimizing-orbit stability composition |
| `CubicQuinticOrbitalStability.lean` | density coercivity, constrained direct method, concentration branch composition |
| `CubicQuinticMildFlow.lean` | weak `H¹ → H⁻¹` interface and conservative mild-flow certificate composition |
| `ZilEvidenceClosureRegistry.lean` | structured implemented/rejected/open states and superseded omission labels |
| `cat-ept-evidence-closure.zc` | queries for resolved omissions, remaining obligations, and awaiting verification |

## M9.78--M9.80 interpretation

- **M9.78:** OpenWave discretizes the Duhamel map after spectral Galerkin truncation and qualifies a fixed point by Picard contraction, residual closure, and refinement against Strang. This consumes the correct weak topology but does not discharge the registry's continuum Duhamel obligation.
- **M9.79:** OpenWave estimates the density centroid and recenters dynamically. First moment, tails, local interaction, mass, and energy refine correctly. The continuum recentered-localization and conservation obligations remain open.
- **M9.80:** OpenWave qualifies one finite-grid minimizing orbit by positive directional curvature and imaginary-time return. The immutable radial-mode record is preserved; ZIL blocks external promotion until analytic identity, particle identity, independent calibration, and an external dataset exist.

## Current decisions

- finite-Galerkin Duhamel fixed point: `qualified`
- Duhamel/Strang refinement agreement: `qualified`
- dynamically recentered first moment and tail: `qualified`
- finite-grid local-interaction convergence: `qualified`
- finite-grid mass/energy conservation: `qualified`
- finite-grid minimizing-orbit identification: `qualified`
- continuum energy-critical Duhamel/Strichartz flow: `open`
- continuum recentered localization and conservation: `open`
- analytic M9.69 minimizing-orbit identity: `open`
- independent calibration and external dataset: `open`
- external physical comparison: `blocked`
- platform counts: `0 validated / 20 partial / 1 negative`

## Status policy

Use `directly proved`, `proved from explicit premises`, `numerically qualified`, `internally tested`, `externally tested`, and `validated` as distinct states. Lean remains proof authority; OpenWave owns simulation evidence; ZIL records identities and scope; human review controls physical promotion.
