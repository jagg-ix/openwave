# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 comparison criteria and now includes a stationary non-Gaussian branch, complete-continuum `H¹(ℝ³)` Born compactness machinery, corrected weak/mild generator interfaces, recentered translation-orbit evidence, and an aligned long-time five-perturbation campaign.

## Platform status

- Zero criteria are fully validated in-platform.
- Twenty criteria are partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- M9.69 supplies the localized full-equation branch.
- M9.75 rejects the false bounded `H¹ → H¹` Laplacian target, the false global weak closure of the unit-mass sphere, and unconditional weak lower semicontinuity of the attractive energy. The correct interface is weak `H¹ → H⁻¹`, with strong mass closure following localized interaction no-loss.
- M9.76 shows the translation family is separated before recentering but collapses after quotienting; centered first moment, tail, mass, and energy are invariant.
- M9.77 formalizes the global conservative weak/mild-flow certificate consumed by the live minimizing-orbit theorem and keeps phase, translation, chirp, amplitude, and noise perturbations inside a small aligned `H¹` tube.

## Cross-repository sources

| Repository | Ref | Revision | Authority |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | merged `main` after PR #77 | `009efb37d535174712109c550e8da06b77dd8f9c` | simulation evidence through M9.74 |
| `jagg-ix/openwave` | `agent/m9-hminus-one-mild-flow-75-77` | current work branch | M9.75--M9.77 evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` | H¹/Born compactness, interaction no-loss, minimizing orbit, and stability authority |
| `jagg-ix/entropic-physlib-private` | active PR #16 branch | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic compactness and corrected weak/mild-flow composition |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions and tooling |

## Latest closures

- **M9.75:** Fourier ratios are `k²` for a proposed `H¹ → H¹` Laplacian bound and `k²/(1+k²) < 1` for `H¹ → H⁻¹`. A translated normalized Gaussian keeps energy `-0.535157` while converging weakly to zero, exposing the lower-semicontinuity failure without localization.
- **M9.76:** four translated M9.69 profiles have unaligned L² distances up to `1.4079`, recentered distance `0`, centered tail `8.3141e-5`, and translation energy error below `7.8e-16`.
- **M9.77:** five perturbations run for `1.5` units. Maximum mass error is `3.38e-13`, energy drift `1.45e-7`, aligned relative `H¹` distance `0.02152`, and boundary fraction `7.05e-6`.

ZIL records identities, dependencies, scope, and evidence-state transitions. Lean remains theorem authority; OpenWave remains simulation software.

## Next critical targets

1. M9.78 construct the concrete energy-critical Duhamel/Strichartz flow in `H¹` with weak generator in `H⁻¹`.
2. M9.79 prove recentered first-moment/local-interaction closure and global continuum mass/energy conservation.
3. M9.80 identify the analytic minimizing orbit with M9.69 and compare the immutable radial mode with external physical evidence.