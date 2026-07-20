# M5.26, fixed-J isorotation dynamics → production port (the former M5.24 round 4)

> 🚧 PLANNED STUB (2026-07-19, staged at the [M5.24](m5_24_task_details.md) close, user-approved re-home of its round-4 scope). Roadmap row: [`m5_roadmap.md § RENDERING TASKS`](../m5_roadmap.md). The full `## TASK PLANNING` lands at "go".

**Why**: [M5.24](m5_24_task_details.md) brought the launcher to the verified-L canonical stack, and the live demo now shows (correctly) that free evolution never spins up the ZBW clock: the two-stack consensus ([M5.21.3](m5_21_3_task_details.md) + [M5.21.8](m5_21_8_task_details.md)) is that the clock exists only as a FIXED-J isorotation state (ω* = J/2kin, measured clock inertia kin ≈ 0.119). Once [M5.21.9](m5_21_9_task_details.md) builds + verifies that state research-side (with the author's Larmor protocol as the acceptance observable), this task ports the validated fixed-J evolution into the production engines: the same catch-up pattern as M5.24 (taichi-first, per-gap selftests against the research reference, launcher wiring, live verification).

**Scope sketch (to be firmed at go)**:

| Step | Deliverable |
| --- | --- |
| 1 | Port the M5.21.9-validated fixed-J machinery (the constraint-carried J evolution) into `engine2_pde`, gated against the research scripts |
| 2 | Launcher wiring on the canonical path (a fixed-J xperiment config; the RELAX → set-J → EVOLVE flow) |
| 3 | Live verification: the stable rotating state on screen = the first honest ZBW δ-sweep (simulated dynamics only, per the standing no-display-only-kinematics directive, [`m5_visualization.md`](../m5_visualization.md)) |

**Gating**: [M5.21.9](m5_21_9_task_details.md) (itself gated on the author's fork answer, sent 2026-07-19) + user "go". Feeds [M5.25](m5_25_task_details.md) (the J/μ twist demo arm rides this port).
