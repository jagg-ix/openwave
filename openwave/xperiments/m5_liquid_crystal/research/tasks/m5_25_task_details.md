# M5.25, the disclination-rod render (VIZ.6): the author's vortex case done right

> 🚧 PLANNED STUB (2026-07-19, from the M5.23 review discussion). Roadmap row: [`m5_roadmap.md § RENDERING TASKS`](../m5_roadmap.md). Lineage: the M5.23 Stage C equatorial ring was built then removed ([`m5_23_task_details.md § Stage C`](m5_23_task_details.md)); this task is its corrected successor. The full `## TASK PLANNING` lands at "go".

**The physics**: the two bipolar rods animated in the author's electron-clock figure ([`../images/clock.gif`](../images/clock.gif)) are the **disclination rods** along the spin axis: the hedgehog's radial director cannot stay smooth everywhere once the clock/spin structure rides it (the hairy-ball constraint), so a line-defect pair forms along one axis, and that axis IS the angular-momentum / magnetic-dipole axis of the author's electron picture. Every biaxial M5 seed constructs this structure explicitly (the escaped-core axis melt), and the maintainer's observation stands as the empirical hook: the Hamiltonian energy-density view already shows the energy lines exactly on the rod sectors (the [M5.8.8](m5_8_8_task_details.md) localization question is its quantitative test).

**Scope sketch (to be firmed at go)**:

| Arm | Deliverable | Engine readiness |
| --- | --- | --- |
| (a) Rod-line ellipsoids | Eigen-ellipsoid samples ALONG the seed's rod axis (one per height, both poles), reusing the whole VIZ.5 M·u machinery with a line sampler instead of the sphere; the melted / degenerate cores read directly off the ellipsoid shapes | READY NOW: the derived fields + mesh pool suffice; the axis is known from the seed |
| (b) Rod rings (per 2D angle) | Small circles AROUND the rod cord at several z-heights, one ellipsoid per azimuth: the winding around the actual vortex line (what the M5.23 Stage C equator ring failed to be) | READY NOW for seeded configs (cord = the seed axis); per-config cord geometry for the charged ring |
| (c) The disclination-line TRACER | General defect-line extraction (eigenvalue-degeneracy / melt detection per voxel + line assembly) so rods, rings, and future split-vortex loops are FOUND, not assumed from the seed | NEW engine logic; required for dynamic states and the μ/τ split-vortex arc ([`m5_23_convo.md`](m5_23_convo.md), [M5.21.6](m5_21_6_task_details.md)) |

**The demo payoff**: rods twisting under the live 4D clock = the angular-momentum / magnetic-dipole demonstration from simulation (the author's animated figure reproduced). The launcher's current 4D path is the safe-v1 (Euclidean flux + live time-axis); the certified 4D physics arrives with [M5.24](m5_24_task_details.md), so the demo arm prefers M5.24 first. Rendering is NOT gated by [M5.8.8](m5_8_8_task_details.md); it feeds it.

**Gating**: arms (a)+(b): user "go" (parallel-safe); arm (c) + the demo: [M5.24](m5_24_task_details.md) preferred first.
