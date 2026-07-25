# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 comparison criteria and combines the stationary non-Gaussian branch with a theorem-guided finite-grid compactness and interaction program.

## Platform status after M9.86

- Three criteria are validated in-platform.
- Seventeen criteria remain partial or bounded.
- The predictive lepton-mass hierarchy remains the sole criterion-level negative.
- M9.84 executes the live PhysLib local-Rellich, recentered-tail, `L³`, `L^(6/5)`, and Hartree chain on four nested grids.
- M9.85 qualifies quartic/sextic local interaction, combined target interaction, normalization, energy-split closure, and decreasing `H¹` no-loss distance.
- M9.86 freezes a reproducible `32³` branch feature fingerprint and qualifies nested-grid plus independent-seed candidate identity.

## Cross-repository sources

| Repository | Ref | Revision | Authority |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after merged PR #80 | `5df88b26a51dccd9d9cc2b3b1182acb384b01b78` | merged implementation through M9.83 |
| `jagg-ix/openwave` | `agent/m9-rellich-interaction-branch-84-86` | current work branch | M9.84--M9.86 evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3` | local Rellich/interpolation/Hartree theorem authority |
| `jagg-ix/entropic-physlib-private` | PR #18 | `19ef639d0ab849f92fb462d5899817ac1a5c4161` | criterion bridge modules and audit |
| `jagg-ix/entropic-physlib-private` | active PR #16 | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic weak/mild-flow composition |
| `jagg-ix/entropic-physlib-private` | active PR #17 | `2cb1003ede54dc7d8487a8b397a1cacf15728feb` | Lean/ZIL evidence lifecycle |

## Latest closure values

- Born-density `L^(6/5)` adjacent-grid error: `0.01854 → 0.00621 → 0.00298`.
- Periodic Hartree error: `0.00514 → 0.00329 → 0.000644`.
- Target-interaction error: `0.04461 → 0.02497 → 0.000727`.
- Nested `H¹` no-loss distance: `0.1865 → 0.1060 → 0.0446`.
- Independent-seed branch distance: maximum `0.01093`.

## Boundary

These are finite-grid qualifications of newly proved formal implications. They do not construct the continuum energy-critical Duhamel flow, prove continuum conservation, discharge the analytic identified-branch certificate, calibrate a physical particle, or admit an external comparison.

## Next critical targets

1. M9.87 construct the actual continuum energy-critical Duhamel/Strichartz theorem in PhysLib.
2. M9.88 prove the target model's local Rellich/tightness/local-interaction hypotheses and continuum conservation.
3. M9.89 discharge analytic branch identity, then register independent calibration and external evidence.
