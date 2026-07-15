# M5.19 method note: the author-regularized vortex loop, statics + seed-level clock (task close)

**Status**: task CLOSED 2026-07-10 (opened the same day from the author's reply to the M5.12 close, [`../tasks/m5_12_convo.md`](../tasks/m5_12_convo.md)). Task record: [`../tasks/m5_19_task_details.md`](../tasks/m5_19_task_details.md); predecessor: [`m5_12_close_note.md`](m5_12_close_note.md) (frozen).

**One-line verdict**: the author's core regularization is CORRECT and energetically selected (it makes the vortex core energy finite and scheme-independent, and energy minimization walks to it unprompted), an ansatz-level interior loop radius R\* exists for the twist-escaped q = 1/2 loop, but pure statics dissolves every regularized loop seed through the removability channel, and no new background approaches the M5.12 clock floor in the standing metric: the M5.12 statics-level negative COMPOUNDS under the regularized construction, and stabilization, if it exists, must come from the temporal-boost channel (the author's R7) on a constrained or dynamically-maintained core, which the statics instrument cannot decide.

**Task span**: go 2026-07-10 12:22 EDT → close the same day (~3.7 h through phases A-E, three adversarial audits inline).

## 1. Equations first

**The static functional** (the audited M5.16/M5.17 stack, spectral potential since M5.18):

```text
E[M] = INT d^3x { u_curv + V(M_sp) },  M = 4x4 real symmetric, spatial block M_sp = M[1:4,1:4]
u_curv = c2 . 4 . SUM_{mu<nu} ||[d_mu M, d_nu M]||_F^2          (commutator / Skyrme-like)
V(M_sp) = wscale . SUM_{p=1..3} (Tr M_sp^p - c_p)^2,  c_p = 1 + delta^p   (target spectrum (1, delta, 0))
axisym reduction: M(rho,phi,z) = R12(phi) Mt(rho,z) R12(phi)^T,  M_phi = [J, Mt]/rho
```

**The straight-vortex cross-section** (phases A/B; degree d generalizes the equivariant channel):

```text
Mt = diag(g, lam_p(rho), lam_m(rho), lam_3(rho)),   M_phi = d [J, Mt] / rho
u_curv = 8 c2 d^2 s^2 (lam_p' - lam_m')^2 / rho^2,  s = lam_p - lam_m     (closed form, diagonal profiles)
the R1 regularization: s(0) = 0 STRUCTURAL (two equal in-plane eigenvalues at the core)
unregularized control (s(0) = s0 != 0, kink k):  E_core/L ~ 16 pi c2 d^2 s0^2 k^2 ln(1/h)
Derrick (2D cross-section): E(lambda) = E_c/lambda^2 + E_v lambda^2  =>  E* = 2 sqrt(E_c E_v), E_c ~ d^2
```

**The loop** (phases C/D): the cross-section revolved around the ring core (R0, 0) with the meridional winding director chi = atan2(z, rho − R0) (the M5.12 `loop_field` geometry, verbatim); the twist-escaped variant blends the tensor beyond ~2.5 core widths to the azimuthal background `e2 e2^T`, which is an EXACT zero of the functional (M_rho = M_z = 0, the lone M_phi channel has no commutator partner; spectrum (1,0,0) so V = 0).

**The winding observable** (phase D): the nematic winding of the meridional (1,3)-block eigenframe angle, `2 theta = atan2(2 M13, M11 − M33)`, accumulated mod-2π around a circle centered on the |M13|² centroid; q = Δ(2θ)/4π.

**The clock probe** (phase E, the audited M5.12 instrument): `Shat(X, ω) = S0(X) − ω² Q2(X)` exactly; balance root `ω_bal = sqrt(S0 / −Q2)` where Q2 < 0; comparisons ONLY in the b17 control frame (common n32 grid, common r_target ∈ {4.77, 3.686}, common a² = 0.303725, one wscale per convention).

## 2. Equation-to-code map

| Equation / object | Function | Location |
| --- | --- | --- |
| u_curv (commutator form, axisym) | `curvature_density_np` | [`m5_17_energy.py` L115](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_17_energy.py#L115) |
| V spectral (LdG quartic variant for the A/B run) | `potential_density_spec_np` (`potential_density_np`) | [`m5_18_spectral.py` L77](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_18_spectral.py#L77) ([`m5_17_energy.py` L133](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_17_energy.py#L133)) |
| the R1 family (s(0) = 0 structural, far-field general) | `family_profiles` | [`m5_19_ab_vortex.py` L103](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_ab_vortex.py#L103) |
| the d-generalized 1D vortex energy | `energy_1d` | [`m5_19_ab_vortex.py` L144](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_ab_vortex.py#L144) |
| the Cartesian cross-check (the scheme-ambiguity measurement) | `cartesian_energy` | [`m5_19_ab_vortex.py` L215](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_ab_vortex.py#L215) |
| V spectral with delta (c_p = 1 + delta^p) | `pot_spec`, `cps_of` | [`m5_19_b2_spectral.py` L77, L73](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_b2_spectral.py#L73) |
| the tensor loop seed (meridional winding pair) | `loop_field_tensor`, `winding_director` | [`m5_19_c1_loop.py` L103, L89](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_c1_loop.py#L89) |
| the twist-escaped loop (far field = e2e2^T exact vacuum) | `loop_field_escaped` | [`m5_19_c1_loop.py` L127](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_c1_loop.py#L127) |
| box-independence gate | `gate_gc2` | [`m5_19_c1_loop.py` L151](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_c1_loop.py#L151) |
| ring core locator (\|M13\|² centroid) | `ring_by_m13` | [`m5_19_d1_relax.py` L64](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_d1_relax.py#L64) |
| the winding observable q_meas | `winding_measure` | [`m5_19_d1_relax.py` L86](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_d1_relax.py#L86) |
| FIRE relaxation driver (+ resume, + corepin) | `run_case` | [`m5_19_d1_relax.py` L113](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_d1_relax.py#L113) |
| the mix forge on the current ring (b14 convention) | `forge_fields` | [`m5_19_e1_clock.py` L71](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_19_e1_clock.py#L71) |
| the control-frame probe (zoom + a² rescale + exact S0/Q2) | `control_probe`, `r_mean_of`, `zoom_to_frame` | [`m5_12_b17_control.py` L118, L84, L96](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b17_control.py#L84) |
| S0, Q2, ω_bal | `s0_q2`, `probe` | [`m5_12_b14_seeds.py` L73, L159](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b14_seeds.py#L73) |

## 3. Results (each next to its gate)

| Phase | Gate (pre-registered) | Result |
| --- | --- | --- |
| A the regularized profile | core integrand bounded under refinement; the unregularized control diverges on the same grid | ✅ PASSED. The unregularized control diverges logarithmically with its ANALYTIC coefficient (fitted slope 3.175 vs 16π c2 d² s0²k² = 3.1416, 1.1%; the audit extended the series to n = 8192: monotone to π). The constant-eigenvalue control is scheme-AMBIGUOUS (equivariant exactly 0, Cartesian ~1/h²: the divergence lives at the core point discontinuity); the regularized family is bounded, O(h²)-convergent, and SCHEME-INDEPENDENT (Cartesian → equivariant in both degrees). The author's diagnosis holds in a precise computational sense: the regularization does not just bound the energy, it makes it well-defined |
| B the planar vortex, both degrees | finite core energy both degrees; a measured degree comparison | ✅ PASSED. LdG-variant optima E\*(d=1) = 4.3025, E\*(d=1/2) = 2.1512, ratio 0.5000 exact (a structural identity: E\* ∝ d when the optimal shape is degree-independent; family-scoped per the audit's channel-exclusion caveat). Under the author's spectral potential the identity breaks (shape becomes degree-dependent) and the TWO-EQUAL CORE IS NEARLY FREE: at δ = 0 the escaped center (0,0,1) is an exact vacuum of V: his regularization is what energy minimization wants. B2 numbers recorded as achieved upper bounds (the ansatz optimizer hit its pre-set 3-config cap on a flat escape valley, surfaced honestly) |
| C the loop, R free | interior R\* bracketed OR the honest boundary verdict | ✅ PASSED (first arm), with the audit-sharpened caveat. The LITERAL meridional construction is box-coupled (E ~ log(box), minima migrate with the box: no verdict licensed from it). The twist-escaped family (far field = the exact e2e2^T vacuum) is box-independent to 3e-16 and carries a deep interior R\*: q = 1/2 narrow cores R\* = 17-18, E\* = 92.7 / 94.6 / 98.3 (melt / planar / escape centers), 16-28% below the curve ends. Caveat (audit-measured): R\* LOCATION tracks the blend cutoff (R\* ≈ shell radius + 6.5); only the EXISTENCE of an interior minimum is cutoff-robust |
| D statics minimization | a stationary regularized loop OR the honest negative | ❌ the honest negative. All three R\*-seeds DISSOLVE AS LOOPS under unconstrained FIRE relaxation (24000-iteration budgets on the q = 1/2 cases): winding annihilated, m13 → 0.0004-0.002; the endpoints are LOCALIZED UNWOUND REMNANTS carrying 68-90% of the residual energy (extrapolated E_inf ≈ 0.6-1.0, audit-measured), not vacuum-bound radiation. The q = 1/2 melt ring is long-lived (winding EXACTLY 0.5 at the saved 8k state, machine precision at r_w = 5-12 by two independent measures; persistence beyond 8k inferred from m13, not directly measured) before unwinding through the removability channel: the SAME two-equal degeneracy the regularization uses at the core, applied globally. The corepin constrained arm (ring core frozen, M5.12 convention) HOLDS (winding magnitude 0.5 throughout, pin exact, E → 7.51 with a geometric tail to E_inf ≈ 7.44): the constrained quasi-minimizer exists and is the clock background |
| E the clock on the phase-D states | the pre-registered floor rule: any background beating the M5.12 per-frame floor in ALL FOUR control frames fires the M5.12 reopening condition; none beating → the negative compounds | ❌ **the statics negative COMPOUNDS**. GE0 identity 2e-12; Q2 < 0 in every frame (the time-mixing channel works on the new backgrounds); controlled ω_bal 13k-53k vs the floor 5.108-5.611 in all four frames (native-frame values 2800-3400, r_mean ≈ 20-24: these objects live 4-6× above the M5.8 anchors and are not candidates at the anchor frame). The reopening condition does NOT fire |
| F masses / mixing | reactivates only on solutions | stays disposed (no solutions; the M5.12 N4c scorecard remains the baseline) |

**The licensed close sentence**: under the author's regularized construction, implemented end-to-end on the audited M5.12 statics stack with pre-registered gates and per-phase adversarial audits: the core regularization is vindicated (finite, scheme-independent, energetically selected), the twist-escaped q = 1/2 loop has an ansatz-level interior radius, but no stationary regularized loop exists under pure statics at the seeds probed (unfound at these seeds and budgets, not proven nonexistent), and no new background undercuts the M5.12 clock floor in the standing metric: stabilization, if it exists, is not in the statics sector this instrument measures.

Inspection artifacts (all embedded in the [task_details findings](../tasks/m5_19_task_details.md)): [`m5_19_ab_profiles.png`](../plots/m5_19_ab_profiles.png) · [`m5_19_ab_refinement.png`](../plots/m5_19_ab_refinement.png) · [`m5_19_c1_loop.png`](../plots/m5_19_c1_loop.png) · [`m5_19_d1_relax.png`](../plots/m5_19_d1_relax.png)

## 4. Not computed

| Item | Why |
| --- | --- |
| δ ≠ 0 loop statics | the sector value of δ for the neutrino is an open parameter (cross-section classes measured at δ ∈ {0, 0.3}; loops run at δ = 0 matching the M5.12 corpus) |
| The R7 clock DYNAMICS (time-periodic orbits) on the new backgrounds | phase E ran the exact seed-level probe only; solver chains were NOT licensed (the probe sits 4 orders above the floor; the M5.12 chain corpus already holds the exhaustive free-period negative at the floor) |
| Hedgehog-embedded loops with the regularized core | the M5.12 hedgehog-background loop family was not re-run with the two-equal cross-section (a named reopening path below) |
| Physical-unit band statements | the A1/A2 unit-map conditionality is unchanged from M5.12 (author-gated) |
| Phase F masses / mixing | no solutions to feed it |

## 5. The audit record

Three independent adversarial audits ran inline (fresh agent each, own scripts, no calls into the audited functions), per the AI_HYGIENE cardinal rule:

| Audit | Verdict | Catches (all applied) |
| --- | --- | --- |
| Phases A+B (7 claims) | ALL CONFIRMED | GA2 stencil conservatism; the w3 flat direction misdescribed as √d-scaled; the per-n branch-jump series not archived; a dead code line. Adopted: the d = 1/2 channel-exclusion caveat; the whole-equivariant-class d² factorization (stronger than claimed) |
| Phase C | HEADLINE CONFIRMED | the q = 1 melt-narrow R\* = 6 record was a refine-trap artifact (true R\* = 13, E\* = 201.685; the script now fine-scans the full range); gate GC0 as coded was tautological (re-routed through the real assembler, still 0.0); sharpened: R\* ≈ blend-shell radius + 6.5 (location cutoff-set, existence robust) |
| Phases D+E (6 claims) | EVERY LOAD-BEARING NEGATIVE CONFIRMED (independent diagnostics: eigenvector-tracked winding, own forge/zoom/rescale pipeline reproducing ω_bal to 5 digits; corepin pin exact at diff 0.0; no convention brings any background within 120× of the floor) | REFUTED at the margin, corrected: the dissolution endpoints are localized unwound remnants with nonzero E_inf ≈ 0.6-1.0 (not vacuum-bound radiation); "winding exact through ~18k" outran the saved data (exact at the saved 8k state); one corepin sign flip hidden by "every logged step"; the r_w = 3-4 winding readings fail an honest interpolated guard (instrument limitation documented) |

Self-caught before audits (documented in the task_details): the phase A/B LdG-vs-spectral potential deviation; the winding-measure center + normalization bugs (fixed BEFORE the long runs); the GE0 amplitude-matching design error (9.65% was physics, not interpolation); the q = 1 "order-of-magnitude" wording (actual: ~2.2× escaped-family, narrow cores); two fast-stamp timestamp corrections.

## 6. Supersede rule + reopening conditions

**Superseded within M5.19** (unquotable except as history): the meridional-family E(R0) minima (box artifacts); the q = 1 melt-narrow R\* = 6 / E\* = 204.65 record; the B2 first-run optima at bounds 4/16 (window-truncated); the "escape ring stabilized at 22" reading (a transient); the phase-B "widths × √d all three" sentence (w3 is flat).

**The M5.12 relationship**: nothing in M5.12 is superseded; its close (no free-period orbit; the controlled floor; the reopening conditions) now carries the ADDITIONAL evidence that the author's regularized construction does not relax below it at seed level.

**M5.19 reopening conditions** (any one): (1) an author-sanctioned protection mechanism for the loop (a conserved charge beyond the local meridional winding, e.g. a Hopf/hedgehog-sector embedding) that blocks the removability channel; (2) the R7 temporal-boost prescription stated as an equation applicable to a NON-stationary or constrained background (the corepin state is saved and ready); (3) a sector δ ≠ 0 directive with loop-level consequences; (4) any seed family whose controlled ω_bal enters within 10× of the M5.12 floor.

## 7. Queued asks for the author (ask-when-gated, batched; the user sends, his voice)

| Tracker ID | Ask | Born at |
| --- | --- | --- |
| [Q20](../m5_question_tracker.md) | Under the M5 commutator-only curvature, the ideal constant-eigenvalue vortex costs exactly ZERO in the equivariant scheme (the divergence appears only in schemes that sample the core discontinuity, or when radial structure coexists with an unclosed split): does "infinite energy otherwise" assume a Dirichlet `\|∇M\|²` term? (Not load-bearing: the regularization is selected either way) | phase A |
| [Q16](../m5_question_tracker.md) (sharpened) | The degree question now has numbers (E\* ∝ d exactly under LdG; only q = 1/2 rings long-lived; q = 1 dissolves fastest) AND the protection question is sharp: the meridional winding is locally protected but globally removable (measured); a stationary loop needs a conserved charge (Hopf / hedgehog embedding / knot?) or dynamic maintenance. Which does the construction intend, and does beta-decay degree 1 survive the 1/2 preference? | phases B/C/D |
| [Q21](../m5_question_tracker.md) | The R7 prescription ("tiny boosts of temporal axis... propel oscillations") as an equation: applied to WHICH background: the constrained (frozen-core) quasi-minimizer? A dynamically-maintained core? The statics instrument cannot decide this | phase E |
| [Q22](../m5_question_tracker.md) | The sector value of δ for the neutrino (a vacuum variable under the spectral potential; winding-pair classes at δ ≠ 0 differ by orders of magnitude in cross-section cost) | phase B2 |

## 8. Task close-out

| Item | State |
| --- | --- |
| Roadmap | M5.19 → DONE (appended at the END of the Done list) on the user's approval |
| Scripts | `m5_19_ab_vortex.py` · `m5_19_b2_spectral.py` · `m5_19_c1_loop.py` · `m5_19_d1_relax.py` · `m5_19_e1_clock.py` (all re-runnable) |
| Data | `m5_19_ab_vortex.json` · `m5_19_b2_spectral.json` · `m5_19_c1_loop.json` · `m5_19_d1_*.json` + endpoint `_state.npz` · `m5_19_e1_clock.json` |
| Group share | HELD at close (the user decides; the queued-asks batch above is the natural next outbound, method-note-grade context per item) |
| Successor | none opened; the reopening conditions (§ 6) gate any successor |
