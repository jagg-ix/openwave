# PhysLib/ZIL reuse map through M9.86

## Repository identities

| Repository | Ref | Revision | Role |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | current `main` after PR #80 | `5df88b26a51dccd9d9cc2b3b1182acb384b01b78` | merged evidence baseline through M9.83 |
| `jagg-ix/openwave` | `agent/m9-rellich-interaction-branch-84-86` | current work branch | M9.84--M9.86 evidence |
| `jagg-ix/entropic-physlib-private` | live `entropic-physlib-linear-full` | `c7283b7fc1ec9ef8acbfd6ed292b34e7ba8d5dd3` | local Rellich/interpolation/Hartree theorem authority |
| `jagg-ix/entropic-physlib-private` | PR #18 | `19ef639d0ab849f92fb462d5899817ac1a5c4161` | criterion bridges |
| `jagg-ix/entropic-physlib-private` | active PR #16 | `83542cc13af0a966a072d90f2082c49785d20c55` | cubic--quintic weak/mild-flow and identified-branch interfaces |
| `jagg-ix/entropic-physlib-private` | active PR #17 | `2cb1003ede54dc7d8487a8b397a1cacf15728feb` | Lean-backed ZIL evidence lifecycle |

## Reused theorem surfaces

| OpenWave target | PhysLib theorem/interface | Use |
| --- | --- | --- |
| M9.84 | `lintegral_tendsto_zero_of_localizedRellich_of_recenteredTight` | local-to-global `L1` gluing |
| M9.84 | `lintegral_lsixFifths_tendsto_zero_of_lone_of_lthree_bound` | `L1`/`L3` interpolation to `L^(6/5)` |
| M9.84 | `hOneBornLSixFifthsConverges_of_recentered_localizedRellich` | Born-density convergence carrier |
| M9.84 | `hOneAttractiveNewtonInteraction_tendsto_of_recentered_localizedRellich` | Hartree interaction convergence consequence |
| M9.85 | `targetInteraction_tendsto` | combine Hartree and local interaction convergence |
| M9.85 | `hOne_tendsto_of_minimizing_energySplit` | no-loss and strong `H¹` consequence |
| M9.85 | `hOneLTwoNormalized_of_tendsto` | normalization closure after strong convergence |
| M9.86 | `IdentifiedTargetBranchCertificate` | explicit formal branch-identity interface |
| M9.86 | `identifiedBranch_mem_minimizingOrbit` | consequence once the certificate is discharged |

## Current decisions

- finite-grid local Rellich premise: `qualified`;
- finite-grid recentered-tail premise: `qualified`;
- finite-grid density-difference `L3` bound: `qualified`;
- finite-grid Born `L^(6/5)` and Hartree closure: `qualified`;
- finite-grid local and target interaction convergence: `qualified`;
- nested-grid `H¹` no-loss sequence: `qualified`;
- reproducible branch feature fingerprint: `frozen`;
- nested-grid and independent-seed candidate identity: `qualified`;
- continuum model hypotheses: `open`;
- continuum flow and conservation: `open`;
- analytic minimizing-orbit identity: `open`;
- independent calibration and external comparison: `blocked`.

## ZIL status

The M9.84--M9.86 graphs record theorem dependencies, finite-grid evidence, and non-transfer boundaries. Lean remains proof authority; OpenWave owns the simulations and frozen ledgers. The platform count remains `3 validated / 17 partial / 1 negative`.
