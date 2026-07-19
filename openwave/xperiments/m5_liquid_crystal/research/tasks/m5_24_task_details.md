# M5.24, production-engine catch-up (audit + port the M5.x-era physics)

> 🚧 PLANNED STUB (2026-07-19, maintainer directive at the M5.23 review). Roadmap row: [`m5_roadmap.md § RENDERING TASKS`](../m5_roadmap.md) (top = next rendering task). The full `## TASK PLANNING` lands at "go".

**Why**: the launcher's production Evolve-PDE path (`engine2_pde.py` + the engine stack the GGUI app runs) largely predates the M5.9-M5.21 research era: the research body validated recipes (the M5.16 parameter locks, the verified Lagrangian work, the 4D integrator findings, the quartic-saturation era results) that production never received. The maintainer flagged this at the M5.23 review: the live app should evolve with the certified physics, not the old-era kernels.

**Scope sketch (to be firmed at go)**:

| Step | Deliverable |
| --- | --- |
| 1. Audit | Production kernels vs the canonical registry ([`m5_theory_canonical.md`](../m5_theory_canonical.md): verified equations, locked parameters, working recipes + anti-recipes, the 4D stack) and the Done-task lineage in [`m5_roadmap.md`](../m5_roadmap.md) |
| 2. Gap table | Per kernel: research-validated vs production-implemented, with the source task/method-note link for each gap |
| 3. Port | The gaps, taichi-first, each with a per-gap headless selftest (goal-loop gates) |
| 4. Verify | Live launcher run on the standard configs; no regression in the certified views |

**Merged scope (2026-07-19)**: the former [M5.8.3](m5_8_3_task_details.md) residual row folded in whole (maintainer call at the M5.23 review):

| From M5.8.3 | Now an M5.24 scope item |
| --- | --- |
| 4D extension of the M5.6.5a production seeder | Part of step 3 (port), audited in step 1 like every other kernel |
| The faithful-kinetic engine variant (the 5d diagnosis: frequency correction only) | Evaluated in the step-2 gap table; ported only if production-scale clock runs need it |

**Gating**: user "go".
