# M5.21.5: the μ + g-factor closure under the verified L (the 4-observable electron)

**Status**: 🚧 PLANNED STUB (2026-07-16, created as M5.21.3 at the electron-hunt scorecard sync: [`../m5_particle_hunt.md § ELECTRON HUNT`](../m5_particle_hunt.md) coverage map; the g ≈ 2 row was the one non-validated row no task covered). **Renumbered M5.21.5 on 2026-07-17** (run-order renumber, user decision: it now runs LAST in the series, after the 3D scan [M5.21.2](m5_21_2_task_details.md), the 4D sequel [M5.21.3](m5_21_3_task_details.md), and the 2-particle films M5.21.4). Finalize at PLAN on the best stable state the series produces; awaiting user "go".

**Lineage**: [M5.21.1](m5_21_1_task_details.md) (supplies the converged verified-L state this task measures on) · the canonical-era baseline: g = 1.97 at 24³ via the K = 4/α bridge, box ladder [1.97, 2.22] bracketing 2.0023, #219 ([`../findings/m5_8_2za_findings.md`](../findings/m5_8_2za_findings.md), [`../scripts/m5_8_2za_g_factor.py`](../scripts/m5_8_2za_g_factor.py)) · the μ channel mechanism: clock tilt/precession, pure twist EM-silent, EID-C ([`../scripts/m5_8_2r_electron_id.py`](../scripts/m5_8_2r_electron_id.py)) · the e_scale anchor: c₂ = αħc/64π locked at M5.16 ([`../findings/m5_16_report.md`](../findings/m5_16_report.md)).

## Scope (stub level)

| Step | Content | Kill / survive (pre-registered at PLAN) |
| --- | --- | --- |
| G1 | Re-establish the μ channel (clock tilt/precession) on the M5.21.1 converged 4D state: verified L, not the canonical stack | channel present/absent measured either way |
| G2 | The μ box-convergence ladder (the #219 caveat: μ was not box-converged) | monotone ladder or the honest divergence record |
| G3 | Replace the structurally-motivated K = 4/α bridge with the locked Coulomb e_scale (c₂ = αħc/64π, M5.16) for a first-principles g read | the bridge either derives or stays flagged as the residual assumption |
| G4 | Verdict: g vs 2.0023 + the 4-observable electron (mass, charge, μ, J) closed under the verified L | closure, or the measured characterization of the gap |

**Pre-registered contingency**: if M5.21.1 ends WITHOUT a converged verified-L clock state, this task re-plans on the best measured state (partials labeled 🔶) or holds, user's call at that review.

## Records + gating

| Item | Content |
| --- | --- |
| Destinations | scripts `../scripts/m5_21_5_*.py` · data/plots `m5_21_5_*` (film standard, both templates where states evolve) · findings `../findings/m5_21_5_method_note.md` · checkpoint at go |
| Standards | method note (equations first, code map) + independent adversarial audit (cardinal rule) |
| Scorecard | closes the electron-hunt g ≈ 2 row ([`../m5_particle_hunt.md`](../m5_particle_hunt.md)); MODELS.md's μ + spin row updates in the post-program sweep (user 2026-07-16: MODELS.md stays as-is until the particle-hunt program completes) |
| Gated By | the best stable state from the series (the [M5.21.2](m5_21_2_task_details.md) 3D minima / the [M5.21.3](m5_21_3_task_details.md) 4D rotating state; the M5.21.1-negative contingency clause above stands) + user "go" |
