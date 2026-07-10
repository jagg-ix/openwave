# M5.12 close note: the phase-D verdict and the task wrap

**Status**: internal audit page (METHOD NOTE standard, [`dev_docs/METHOD_NOTE.md`](../../../../../dev_docs/METHOD_NOTE.md)). Task record: [`tasks/m5_12_task_details.md`](../tasks/m5_12_task_details.md); running checkpoint: [`checkpoints/m5_12_progress.md`](../checkpoints/m5_12_progress.md).

**One-line verdict**: no free-period orbit was found in the time-mixing class at the physical regime; the negative is measured, audited (seven adversarial audits: b11, b13-b18, plus the two same-day block-2/3 audits), stated under a standing metric, and closed with explicit reopening conditions. Per the task's definition of done, the honest physical-regime negative IS a verdict on the model; masses (phase E) and mixing (phase F) are disposed as designed-but-not-runnable on solutions that do not exist.

**Task span**: 64:52 total (~65h) across 19 blocks, go 2026-07-07 11:23 EDT → close 2026-07-10 04:15 EDT; the final task review approved 2026-07-10 (recorded in [`tasks/m5_12_task_details.md § TASK REVIEW (2026-07-10, final)`](../tasks/m5_12_task_details.md)). No usage cap fired task-wide (no resume ping ever triggered; every reset-time watchdog wake found the session alive).

## 1. Equations first

**The ansatz.** The 4×4 tensor field on the equivariant axisymmetric (ρ, z) reduction, time-periodic with fundamental ω:

```text
M(rho, z, t) = M0(rho, z) + sum_k [ A_k(rho, z) cos(k w t) + B_k(rho, z) sin(k w t) ],   k = 1..Nt (Nt = 2)
```

Boundary conditions: outer ρ boundary and both z boundaries pinned (harmonics zero there); the axis is free (mirror ghost).

**The action.** The time-averaged action of the verified 4D Lagrangian (quartic curvature + the owner's spectral potential; static sector audited in M5.17/M5.18) over one period:

```text
Shat(X, w) = S0(X) - w^2 Q2(X)          exactly (verified to 1e-14 at every endpoint)
S0 = Shat(X, 0),   Q2 = Shat(X, 0) - Shat(X, 1)     (read off, no fit)
```

The potential weight `wscale` is calibrated per grid by the seed-virial protocol on the rc = 8·nr/96 hedgehog (canonical anchor: n96, `m5_18_spectral_spec_n96.json`).

**The free-period balance root.** Free periodicity requires the action balance; with the exact quadratic form above:

```text
w_bal(X) = sqrt( S0 / (-Q2) )    defined where Q2 < 0
H_mean(w_bal) = S0 + w^2 Q2 = 0   BY CONSTRUCTION (b13 audit L5)
```

so the honest conservation metric is the swing `H_swing/S0`, never the mean. The channel split: `Q2_mix` zeroes the spatial block of every harmonic (rows/cols 1:4 × 1:4), `Q2_pos` zeroes the 0-row/col; time-mixing (0i) components are the only negative channel (the block-11 sign theorem: the mixing-free class has Q2 ≥ 0 exactly).

**The solver.** The ω-eliminated residual `R(X, w_bal(X)) = 0` in X alone, Levenberg-Marquardt (damp = fraction × LSMR ‖A‖ estimate, escalating schedule), hard-amplitude retraction holding the first-harmonic amplitude `a2 = sum over free cells of (A1^2 + B1^2)` fixed at 0.303725. Stall rule: three consecutive sub-1% steps. A convergent endpoint requires `|F|_rel < 1e-5`; no chain reached it (all endpoints are progress-rate stalls, and every audited endpoint is demonstrably NOT a stationary point of `|F|^2`).

**The standing metric (b17 adjudication).** Cross-family comparisons are licensed only as fixed-(size, a²) in-frame probes: every state zoomed to a common object radius on the common n32 frame, harmonics rescaled to the common a², probed under one wscale; orderings quoted only where they hold across the frame battery (r_target × wscale) and the amplitude-budget sweep. The size observable:

```text
r_mean = sum( w r amp2 ) / sum( w amp2 ),   w = 2 pi rho h^2,   amp2 = sum_k (A_k^2 + B_k^2),  pins zeroed
```

Raw ω_bal across families is void (size-dominated, 1/L covariance measured to 0.7%); the product ω_bal·r_mean is a within-lineage invariant only (0.2%), not a ranking.

**The unit map (measured, conditional).** Distance-to-band statements map the BVP stall to the M5.8 molten-clock band ω₁ = 1.07-1.15 by matching motion radii, under two DECLARED, still author-gated assumptions: A1 (one M5.8 lattice unit = one BVP h unit) and A2 (c = 1 in both codes; verified in the shared curvature sector, NOT established across the differing potential sectors).

## 2. Equation-to-code map

All links `blob/main` (task-scoped files, frozen at close per the standard).

| Term / observable | Function | Location |
| --- | --- | --- |
| Harmonic state pack | `x_pack` | [`m5_12_d3a_bvp.py#L71`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_d3a_bvp.py#L71) |
| `Shat(X, w)` (time-averaged action) | `shat` | [`m5_12_d3a_bvp.py#L153`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_d3a_bvp.py#L153) |
| Static curvature density (quartic commutator) | `curvature_density_np` | [`m5_17_energy.py#L115`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_17_energy.py#L115) (the M5.17 audited module) |
| `S0`, `Q2` readout | `s0_q2` | [`m5_12_b14_seeds.py#L73`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b14_seeds.py#L73) |
| Channel split `Q2_mix` / `Q2_pos` | `q2_channels` | [`m5_12_b14_seeds.py#L78`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b14_seeds.py#L78) |
| Amplitude convention `a2` | `a2_free` | [`m5_12_b14_seeds.py#L143`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b14_seeds.py#L143) |
| `w_bal` | `omega_bal` | [`m5_12_b12_hard.py#L109`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b12_hard.py#L109) |
| The ω-eliminated LM ladder (retraction, stall rule, honest endpoint metrics) | `run_ladder` | [`m5_12_b12_hard.py#L116`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b12_hard.py#L116) |
| Calibration `wscale` (seed-virial) | `wscale_at` | [`m5_12_d3b_newton.py#L91`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_d3b_newton.py#L91) |
| Size observable `r_mean` | `r_mean_of` | [`m5_12_b17_control.py#L84`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b17_control.py#L84) |
| The control frame (zoom + a² + one wscale) | `zoom_to_frame`, `control_probe` | [`m5_12_b17_control.py#L96`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b17_control.py#L96) |
| The unit map (M5.8 anchors + rescale) | `r_mean_bvp` + module header | [`m5_12_b16_unitmap.py#L79`](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m5_liquid_crystal/research/scripts/m5_12_b16_unitmap.py#L79) |

Minimal inspection set (physics first): `m5_17_energy.py` (the functional) → `m5_12_d3a_bvp.py` (the action) → `m5_12_b17_control.py` (the standing metric) → `m5_12_b12_hard.py` (the driver, last). No figures were produced in the phase-D endgame; all deliverables are JSON + scripts (each block's JSONs listed in the task record).

## 3. Results (gates next to numbers)

**Phase D0 / A / statics (block 1, 2026-07-07).** The owner's core prescription does not close the melt channel (hedgehog corepinned relax lands below the escaped state; antipair annihilates at all d, the isotropic core is a free unwinding surface); the bare functional has no stationary rotated-vortex loop at δ = 0 (6/6 pre-registered negatives); the σ-term pilot's hold was a confound (discriminator: far-field texture). Gates: pre-registered per Card 6.

**Phases D1-D2 (blocks 2-3).** Both audited same-day: the D1 size-selection headline RETRACTED (far-field-driven, box-divergent); D2's balanced minima REFUTED as stated; the constructive residue: the g-powered ghost channel mechanism and the p = 4 modeling requirement. The genuine problem isolated: the time-periodic 4D BVP.

**The BVP campaign (blocks 6-18, condensed).** The instrument (exact `Shat = S0 - w^2 Q2`, the balance root, the LM hard-amplitude solver) was built, gate-checked (HG gates at machine precision every launch) and audit-CONFIRMED (b13 L4). Q2 < 0 exists only in the time-mixing class (sign theorem); small-amplitude orbits are obstructed by the action balance (breathers are necessarily large-amplitude; the 0.3% `c_w = -Shat/w` pin is itself an algebraic identity per the b11 audit, the obstruction content lives in the amplitude-squared scaling of `dShat/dw`). Seven-plus chains across five seed families (bmix radial, wide, node/shell/rgauss, pancake anisotropic, the optimizer's direction, plus the loop transplant) all end in honest progress-rate stalls (`|F|` ~ 100-520, `H_swing/S0` ≈ 2, non-stationary, below the grid-transfer discretization scale). The loop transplant preserved its topology end-to-end (winding q = 1/2 at seed AND endpoint) but showed no energetic advantage. The metric war (raw → product → controlled) was settled by the b17 adjudication; the b18 decider, audit-corrected, exhausted seed-level shape search at this budget.

**THE PHASE D CLOSE (the b18-audit-licensed sentence, verbatim):**

> Phase D closes on a measured endpoint plus a bounded decider, not on a found orbit: no free-period orbit was found (every chain ends in an honest progress-rate stall, none at a stationary point, so the negative is unfound, not nonexistent). Under the standing fixed-(size, a2) metric (common n32 frame, common r_target, common first-harmonic a2 = 0.3037, one wscale, orderings quoted only across the frame battery) the controlled floor is p1 at 5.11-5.61 at the M5.8 size anchors, 4.4-5.5x above the band, A1/A2-conditional throughout with the potential-sector gap author-gated. The block-18 seed-level decider, audit-corrected for its Gram convention, found no fresh shape direction that beats the floor-producing seed in both wscale conventions (best candidate 5.0% better native-only, 14.2% worse rc-matched, projecting to ~6.2 at the median measured seed-to-relaxed gain, above the floor), so seed-level shape search within the probed basis is exhausted at this budget and the b17 'still descending' status is retired, with the standing caveat that relaxation dynamics have reordered seeds before and most of the measured relax gain lives in background adaptation that no seed-level metric can see. Phase D reopens on any of: a solver rung that converges at the floor (the stalls are non-stationary); the author sanctioning or refuting the A1/A2 unit-map assumptions; or any measured seed direction that beats the floor-producing seed in both conventions (equivalently, one that plausibly relaxes below p1's 5.44/5.11).

**Supersede rule**: the 12-item list in [`m5_12_audit_b18.json`](../data/m5_12_audit_b18.json) `supersede_list` is binding; no distance/floor/saturation number from blocks 12-17 is quotable except through the close. The structural findings stand: the Q2_mix sign theorem, the zero-mean-energy identity, the loop-topology survival, the 1/L covariance, the standing metric.

## 4. E/F disposition (designed, not runnable, disposed)

Both phases were designed to run ON stationary/periodic loop solutions; phase D produced none. They close as DISPOSED-NOT-RUN and reopen together with phase D.

| Phase | Pre-registered gate | Disposition |
| --- | --- | --- |
| E (masses) | `Δm²` hierarchy honest pass/fail via the mass/length-density map + knot-family spread; the 6.2 pm scale anchor; the `E = λ·L` energy-conserving trajectory gate | NOT RUN: no loop family exists to map. The M5.11 compression tension (loop spectrum `1 : 1.148 : 1.682` giving splitting ratios 5.8-7.3× below the observed 33.6) REMAINS the standing falsifier-candidate at its M5.11 evidence level (placeholder δ = 0.3, non-solutions), untested at the physical regime |
| F (mixing on real loops) | the 4 PMNS parameters from solutions vs NuFIT 6.0, provenance-labelled; the N4c gap map (Q8 stability, Q4 θ₁₂ energy selection, Q7 Gram-bridge vs true Hessian, Q1/Q2 chiral θ₁₃ + δ_CP fork) | NOT RUN: every N4c gap required solutions. The [`m5_10e_findings_N4c.md`](../tasks/m5_10e_findings_N4c.md) scorecard STANDS as the honest state of the art; nothing in M5.12 weakened or improved it. New F-adjacent asset: loop topology survives relaxation cleanly (b14), so the loop-sector machinery is ready if phase D reopens and converges |

## 5. Not computed (scope honesty)

- No converged free-period orbit; therefore no ω of a solution, no second-variation Hessian, no stability index (BG7 was killed by decision when its target lost solution status).
- No masses, no `Δm²`, no PMNS parameters at the physical regime (E/F disposed).
- The distance-to-band factor is CONDITIONAL: A1 (cell = cell) and A2 (c = 1; the potential sectors of the two codes differ structurally) are author-gated and were neither sanctioned nor refuted.
- No absolute-unit (SI) statement anywhere in the phase-D record.
- The wd/f1/f2 in-frame ordering and the c2/g48 in-frame absolute values are explicitly NOT quotable (below instrument resolution / deep-zoom softness).

## 6. The audit record (part of the rigor surface)

| Audit | Target | Headline outcome |
| --- | --- | --- |
| b11 (2026-07-08) | the rotor/breather arms | C1 rotor headline REFUTED (boundary-driven); the sign theorem + the time-mixing redirect |
| b13 | the block-12 amplitude ladder | L4 solver CONFIRMED exact; L1 "1/a law" refuted as a law; L5 replaced by the `H_mean = 0` identity + honest metrics |
| b14 (+ endpoint addendum) | the class-negative + loop transplant | the class battery's shape blindness exposed (N2 coverage refuted); 1/L calibration kinematics; the unit-map question surfaced (author-gated) |
| b15 | the shape-family sweep | P1 refuted as a class floor (the Rayleigh/anisotropy hole); "6.99 = moving upper bound" |
| b16 | the pancake chains + the O2 unit map | the invariant inversion (later itself corrected); the amplitude confound; A2 partially unverified |
| b17 | the fixed-(size, a²) control | THE STANDING METRIC adjudicated; "saturated" refused; distance 4.4-5.5× anchor-flat |
| b18 | the decider + the close | my Gram bug caught (verdict survived on exact probes); seed-level search ruled saturated-at-budget; the close sentence licensed; the supersede list |
| b19 (this note) | the close note + E/F disposition | see § 7, filled by the wrap audit before this note is considered final |

## 7. Wrap-audit outcome (b19, 2026-07-10)

The independent b19 wrap audit re-traced every quantitative claim in this note and in the block-18/19 task-details sections to the primary artifacts (the b13-b18 audit JSONs, the b17 control, the b16 unit map, the b18 decider, and the ladder endpoint battery), character-diffed the close sentence in both documents against the b18-licensed original, re-walked all 12 equation-to-code map rows to their def lines, and checked the stated equations, the E/F dispositions, and the METHOD NOTE shape against code, pre-registered gates, and the standard. Every number, map row, equation, gate quote, and disposition claim was CONFIRMED; three trivial errors blocked finality and were fixed on the audit's instruction: a 2-character quote-style drift in the "verbatim" close sentence, the audit count "six" against the note's own record of seven, and "audit-caught" misattributed to the self-caught rmatvec bug. Full record: [`m5_12_audit_b19.json`](../data/m5_12_audit_b19.json); mechanical layer re-runnable via `scripts/m5_12_audit_b19_check.py` (exit 0 after the fixes).

## 8. Task close-out (post-approval record, 2026-07-10)

| Step | Status |
| --- | --- |
| Final task review | ✅ approved 2026-07-10; documented in [`tasks/m5_12_task_details.md § TASK REVIEW (2026-07-10, final)`](../tasks/m5_12_task_details.md) |
| Roadmap | ✅ the M5.12 row moved to the END of the [`m5_roadmap.md`](../m5_roadmap.md) DONE list, dated 2026-07-10 |
| Question tracker | ✅ milestone entry prepended to [`m5_question_tracker.md § Last updated`](../m5_question_tracker.md); NO tracker question changed status (the unit-map sanction is user-gated, no new ask opened) |
