# M9 global target plan

This plan is derived from the OpenWave README and model-comparison criteria. It
keeps OpenWave simulation-only and requires runnable evidence for every status.

## Phase A — conformance and canonical core

| Target | Deliverable | State |
| --- | --- | --- |
| M9.22 | README/MODELS conformance profile and criterion audit | COMPLETE |
| M9.23 | One canonical CAT/EPT state and coupled evolution | COMPLETE |
| M9.24 | Shared static/dynamic solver bridge | COMPLETE |

## Phase B — particle foundation

| Target | Deliverable | State / gate |
| --- | --- | --- |
| M9.25 | CAT/EPT-native localized-state search | COMPLETE: partial 1D family; 3D particle remains negative |
| M9.26 | Field-derived charge/topological observable | COMPLETE: integer winding; electric-charge bridge open |
| M9.27 | Rest-energy functional and scale selection | COMPLETE: dimensionless ansatz scale; physical mass open |
| M9.28 | Intrinsic clock reduction | NEXT: separate entropy arrow from ZBW phase |
| M9.29 | Spin, magnetic moment, and double-cover tests | PLANNED: field observables required |

## Phase C — interactions and bound states

| Target | Deliverable |
| --- | --- |
| M9.30 | Two-body electric and magnetic laws |
| M9.31 | Opposite-sector capture, annihilation, and radiation ledger |
| M9.32 | Orbital / standing-wave quantization |
| M9.33 | Composite-state graph for mesons, baryons, and nuclei |

## Phase D — geometry and numerical infrastructure

| Target | Deliverable |
| --- | --- |
| M9.34 | Metric or geometry back-reaction plugin |
| M9.35 | Multi-domain coupling graph and dependency scheduler |
| M9.36 | Adaptive refinement and propagated error budgets |
| M9.37 | Three-dimensional static minimizer, BVP, and continuation |
| M9.38 | GPU adapter generated from theory manifests |

## Phase E — spectrum and force sectors

| Target | Deliverable |
| --- | --- |
| M9.39 | Lepton-family hierarchy and parameter-selection audit |
| M9.40 | Strong-force or confinement sector |
| M9.41 | Weak/chiral transition sector |
| M9.42 | Gravity and equivalence-principle suite |

## Phase F — waves, thermal, and cosmological sectors

| Target | Deliverable |
| --- | --- |
| M9.43 | CAT/EPT-native Maxwell and Klein-Gordon reductions |
| M9.44 | Heat/thermal criterion missing from current MODELS.md matrix |
| M9.45 | Neutral localized-state and dark-sector survey |

Every target must provide a deterministic runner, result ledger, focused tests,
convergence/domain checks where applicable, explicit assumptions, and an honest
validated/partial/negative/not-yet status. Physical-data acquisition is out of scope.
