# M5.25, the disclination-line tracer + the J/μ clock demo

> 🚧 PLANNED STUB (2026-07-19, staged at the M5.23 Stage D close). Roadmap row: [`m5_roadmap.md § RENDERING TASKS`](../m5_roadmap.md). These are the two arms M5.23 Stage D explicitly deferred ([`m5_23_task_details.md § Stage D`](m5_23_task_details.md)). Note on the ID: this number was briefly held by the rod render itself before it was folded back into M5.23 as Stage D; it is reused here for the genuinely-future arms. The full `## TASK PLANNING` lands at "go".

**Scope sketch (to be firmed at go)**:

| Arm | Deliverable | Key input |
| --- | --- | --- |
| (1) The disclination-line TRACER | Per-voxel defect-core detection + line assembly, so rods, ring cords, and split-vortex loops are FOUND in the live field rather than assumed from the seed geometry: required for dynamic states, defect motion / reconnection, and the μ/τ split-vortex animation arc ([`m5_23_convo.md`](m5_23_convo.md), rides [M5.21.6](m5_21_6_task_details.md)) | The detection criterion is already MEASURED (M5.23 Stage D): the disclination core is an exact **uniaxial escape**, λ₂−λ₃ = 0.000 on the rod axis vs ≈ 0.265 (≈ δ) in the biaxial bulk: threshold the minor-eigenvalue split, then assemble connected voxel chains into lines |
| (2) The J/μ twist DEMO | The disclination rods twisting under the live 4D clock: the angular-momentum / magnetic-dipole demonstration from simulation (the author's electron-clock figure animated), rendered with the VIZ.5 rod machinery already in production | Needs a STABLE ROTATING state in the production engines: the canonical stack landed at [M5.24](m5_24_task_details.md) (✅ closed 2026-07-19), and the clock itself is the FIXED-J construction, ported at [M5.26](m5_26_task_details.md) behind the [M5.21.9](m5_21_9_task_details.md) physics (the two-stack consensus: no free-evolution clock exists) |

**Gating (updated at the M5.24 close, 2026-07-19)**: arm (1), the tracer, is UNGATED on physics (the M5.24 canonical stack + the measured λ₂−λ₃ criterion suffice); arm (2), the J/μ demo, is gated by [M5.26](m5_26_task_details.md) (→ [M5.21.9](m5_21_9_task_details.md) → the author's fork answer). Both arms: user "go". Feeds [M5.8.8](m5_8_8_task_details.md) (the rod-localization energy question) and the μ/τ split-vortex program.
