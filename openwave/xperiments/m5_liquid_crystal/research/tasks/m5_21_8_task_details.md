# M5.21.8: verify + confront the analytical twisting massive hedgehog

**Status**: 🚧 PLANNED STUB (2026-07-19, from his 05:09 group message; [`m5_21_convo.md § 2026-07-19 05:09`](m5_21_convo.md)). His direct ask: "Maybe please ask Fable to verify it, and if agreeing analyze why its simulations lead to infinites for electron ... I suspect due to use of inadequate g, delta parameters (?)". Source: [`../../theory/duda_2026-07-19_3p1D_analytical_twisting_massive_hedgehog.pdf`](../../theory/duda_2026-07-19_3p1D_analytical_twisting_massive_hedgehog.pdf). Full PLAN at go.

## Scope (stub level)

| Phase | Content | Notes |
| --- | --- | --- |
| P0 symbolic reproduction | Reproduce the notebook end-to-end with our own CAS route (SymPy): the ansatz M = Qb(m)·Qh(ωt)·d·(...)ᵀ, F_ij = [∂_i M, ∂_j M]_ξ, his component-split H, the time average, **m* = ½ ln((1+g)/(g−1))**, the Hm density, the two divergences (vortex cone; constant-ω r-integral), the piecewise ω-minimum incl. its −∞ regions | The verification he asked for, done adversarially (his own −∞ branches and dropped divergences are part of the honest read-back) |
| P1 convention bridge | His H (component-wise ± split of F entries, ξ-sandwich) vs our η-trace u_η on the SAME ansatz: identical / proportional / different, term-by-term; locate his twist × spatial cross terms (the claimed ω-stabilizers) in our functional | Decides whether the M5.21.3 verdict and his benchmark even talk about the same energy |
| P2 lattice confrontation | Implement the Qb(m) boost-hedgehog dressing in the 4D stack; scan E(m, ω) at (g = 8, δ = 0.3): rigid (his approximation) AND profile-relaxed; finite (m*, ω*) or not; explain any difference (his rigid eigenvalue-pinned family + dropped divergences vs our relaxing lattice; IR: his constant-ω kinetic diverges, our envelope-localized kinetic is IR-finite by construction) | The M5.21.3 ω-ladder had NO boost-hedgehog dressing; his m-parameter is a genuinely new direction in the ansatz space |
| P3 the g-ladder scaling test | His critique measured: kin_boost(g) and m*(g) along g = 8/16/32/64...: does the negative boost channel shrink ~ 1/g as his m* formula implies? Extrapolation statement toward g ~ 1e10 | The [Q33](../m5_question_tracker.md#q33-detail) bridge in action; the cheapest honest answer to "resolved at real g" |
| P4 the premise correction + outbound | The reply paragraph: M5.21.3 measured NO infinities (bounded shallow slope, no stationary point; the divergence era was the pre-symmetrization signature dive, cured); what is missing is a turning point, and where his cross-terms/IR structure could supply one; package with the held [M5.21.6](m5_21_6_task_details.md) note | The combined outbound closes both threads |

Series rules: independent adversarial audit before anything author-facing; method-note grade; [Q35](../m5_question_tracker.md#q35-detail) (negative-Hamiltonian literature) can ride as a P0 side-read.

**Staged follow-on (his Larmor protocol, spelled out 2026-07-19)**: "introduce constant external magnetic field by constant field derivative in its direction, and temporal field derivative - should lead to electron precession with frequency proportional to magnetic field strength"; runs on whichever stable-oscillation state survives this task (a true (m*, ω*) minimum if P2 finds one, else the fixed-J/enforced state, which he now explicitly allows: "maybe enforced if numerical problems remain"). The linear-in-B precession slope is the acceptance observable.

**Reference map for P1**: his F_μν structural dictionary ([`../../theory/duda_2026-07-18_Fmunu_decomposition.png`](../../theory/duda_2026-07-18_Fmunu_decomposition.png), decoded in [`m5_21_convo.md § 2026-07-18 19:44`](m5_21_convo.md)): EM = tilt-tilt (R¹ + g²Γ̃¹), QM = tilt-twist (δR² − g²Γ̃²), gravity = boosts, "clock propulsion?" on the twist-boost cross blocks; the bridge should express our η-trace u in exactly these blocks.

**Gated by**: user "go" (all inputs delivered; no 4D re-run needed for P0/P1).
