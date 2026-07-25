# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 comparison criteria and now includes a stationary non-Gaussian branch, complete-continuum `H¹(ℝ³)` Born compactness machinery, corrected weak/mild interfaces, a finite-Galerkin Duhamel fixed point, dynamically recentered conservation evidence, and a finite-grid minimizing-orbit identification campaign.

## Platform status

- Zero criteria are fully validated in-platform.
- Twenty criteria are partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- M9.78 constructs the spectral Volterra/Duhamel map on `16³`, closes Picard residuals, and converges toward the existing Strang trajectory under time refinement.
- M9.79 estimates the evolving density centroid, recenters by Fourier translation, and refines centered moments, tails, local interaction, mass, and energy.
- M9.80 shows positive constrained curvature in radial, quadrupole, and shell directions and relaxation back into one finite-grid phase/translation orbit tube.
- The immutable M9.71 mode remains internally robust, but external comparison is blocked until analytic branch identity, particle identity, independent calibration, and an external dataset are supplied.

## Cross-repository sources

| Repository | Ref | Revision | Authority |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after merged PR #78 | `c3cdd5725e9b5455cf3f2fb35164e79cab1265d8` | merged simulation evidence through M9.77 |
| `jagg-ix/openwave` | `agent/m9-duhamel-conservation-identification-78-80` | current work branch | M9.78--M9.80 implementation and evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `bd17dacbb5118e89eb58acacf11c1da8f9a9cc82` | `H¹`/Born compactness, interaction no-loss, minimizing orbit, and stability authority |
| `jagg-ix/entropic-physlib-private` | active PR #16 | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic compactness and corrected weak/mild-flow composition |
| `jagg-ix/entropic-physlib-private` | active PR #17 | `2cb1003ede54dc7d8487a8b397a1cacf15728feb` | Lean/ZIL evidence lifecycle and open-obligation reconciliation |
| `jagg-ix/zil-lean` | `main` | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions and tooling |

## Latest closures

- **M9.78:** maximum Picard ratio `0.02277`; fixed-point residual below `3e-16`; Duhamel/Strang `H¹` differences `3.161e-4 → 1.581e-4 → 7.903e-5`.
- **M9.79:** centered first-moment excursion below `0.01109`, tail below `1.411e-4`, mass error below `2.8e-13`, and energy drift `5.781e-7 → 1.442e-7 → 3.603e-8`.
- **M9.80:** positive second variations `5.831`, `1.852`, and `3.643`; six relaxed deformations return within phase-aligned `H¹` distance `0.00468`; external comparison remains fail-closed.

ZIL records identities, dependencies, scope, and evidence-state transitions. Lean remains theorem authority; OpenWave remains simulation software.

## Next critical targets

1. M9.81 construct the actual continuum energy-critical Duhamel/Strichartz theorem in PhysLib, rather than another finite-Galerkin proxy.
2. M9.82 prove recentered localization, local-interaction convergence, and continuum mass/energy conservation.
3. M9.83 analytically identify the minimizing orbit with M9.69, then register an independent calibration and external dataset before any physical mode comparison.
