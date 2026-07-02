# M5.16: Axisymmetric energy-minimization calibration solver (the parameter-lock gate)

> Task **M5.16** (M5 / Liquid-Crystal model). Status: **Backlog (recommended next)** · Gated by: - (interim `V(M)` + Faber melt already in engine1_seeds; Q7/Q8 are inputs, not blockers) · Gates: M5.9.0 real-calibration axis, M5.9, M5.11, `#220` absolute-ω · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation.

---

## Origin

Duda, 2026-07-01 ([`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md)): the honest bar for convincing mainstream is a **static energy-minimization** simulation, "assuming initial field configuration like hedgehog for electron or vortex loop for neutrino, and numerically performing energy minimization", with **cylindrical symmetry to reduce dimension**, and the hardest part being **regularization in the center + the potential**. His ordered prescription: **first fix `g`, `δ`** (clock / neutrino-oscillation / baryon gravitational-mass anchors + Coulomb), then the LdG potential (minima = eigenspectrum `(g,1,δ,0)`, parameters TBD).

## The strategic fork (why this task exists)

M5.8 established the de Broglie clock by **dynamical leapfrog at V=0**. That route is **scale-free**: the frequency is rigid against energy (`2m`, exponent ≈0.03) and the first absolute ω came out **~28× below** the electron ZBW, a **structural** gap the V=0 sandbox cannot close ([`../m5_summary_report.md`](../m5_summary_report.md) §3, N-6b). `#218` then showed the ZBW scale is recoverable only by anchoring **energy AND length jointly** (the `E·r₀` line, geo-mean to ~13%). The length anchor lives in the **static minimization-with-potential** route, not the scale-free dynamical one.

So the plausible reason the absolute scale never closed is a **method choice**, not a model failure: the calibration belongs to energy minimization under a regularizing potential at the **physical `(g, δ)` regime**, which has never been run.

## What already exists (this is a graduation, not a from-scratch build)

M5.11 P0-P1 built the machinery and validated it at placeholder parameters:

| Asset | Where | State |
| --- | --- | --- |
| Static energy minimizer (FIRE + L-BFGS to `\|dE/dM\|→0`), mirrors the production functional | [`../scripts/m5_11_p0_minimizer.py`](../scripts/m5_11_p0_minimizer.py) | ✅ all gates pass (gradcheck 1e-6, φ⁴-kink, V_M ≡ engine2_pde) |
| Faber electron reproduced | [`../scripts/m5_11_p1_faber_electron.py`](../scripts/m5_11_p1_faber_electron.py) | ✅ 511.00 keV at `r₀=2.2132 fm`, `I=π/4` to 6e-6 |
| `α⁻¹ → 137.03` from charge quantization | [`../scripts/m5_11_p1b_lattice.py`](../scripts/m5_11_p1b_lattice.py), `m5_11_p1b_dipole.py` | ✅ 3D + axisym Γ/R; charge→1e |
| Taichi reverse-mode AD gradient ≡ production functional | [`../scripts/m5_11_ad_energy.py`](../scripts/m5_11_ad_energy.py) | ✅ E 4e-16, grad 1.8e-13 |
| Chiral Lifshitz + Frank terms | [`../scripts/m5_11_p2_heliknoton.py`](../scripts/m5_11_p2_heliknoton.py) | ✅ AD ≡ numpy 1e-14 |

**The gap:** the minimizer runs at placeholder `g=8, δ=0.3` (`m5_11_p0_minimizer.py:41-42`), never at the physical `g~1e10, δ~1e-10`; the `V(M)` coefficients `(a, b, c)` are uncalibrated; cylindrical-symmetry reduction is not yet used to make the physical regime tractable; and the whole thing is scoped inside the neutrino task rather than being the program's calibration instrument.

## What M5.16 adds

| Sub-piece | Deliverable |
| --- | --- |
| **P-A / physical (g, δ) regime** | run the minimizer at `g~1e10`, `δ~1e-10` via a **non-dimensionalized formulation or a perturbative δ-expansion** (the ~`1e20` dynamic range exceeds f32/f64) |
| **P-B / cylindrical reduction** | reduce the electron hedgehog + the neutrino vortex loop to an **axisymmetric (r, z) BVP** (Duda's dimension-reduction trick), so the physical regime is computationally reachable |
| **P-C / potential calibration (Q7)** | fix the LdG `V(M)` coefficients `(a, b, c)` by **requiring the minimizer to reproduce the anchors** (electron 511 keV via Faber `r₀`; Coulomb; the electron-clock time scale) rather than guessing them; verify the minimum sits at eigenspectrum `(g,1,δ,0)` |
| **P-D / core regularization (Q8)** | the hedgehog/vortex center regularization (Duda's "hardest part") under the calibrated potential, on the axisymmetric mesh |
| **P-E / g from an anchor** | pin `g` from one of: the electron clock, neutrino oscillations, or baryon gravitational mass (Duda's three routes; "certain of only for baryons") |
| **P-F / handoff** | publish locked `(g, δ, a, b, c, r₀)` + the run recipe as the calibration input consumed by M5.9.0 / M5.9 / M5.11 / `#220` |

## Numerical recipe (Golubich 2026-07-02) , the concrete minimizer build

Dr. Rudolf Golubich (co-author of Faber & Golubich [arXiv:2604.12021](https://arxiv.org/abs/2604.12021)) handed us the exact static-minimization recipe used for the source SU(2) soliton model ([`m5_4g_convo_2026.07.02.md`](m5_4g_convo_2026.07.02.md)); it is the concrete build for M5.16's minimizer and de-risks its numerics:

| Element | Recipe |
| --- | --- |
| Objective | minimize the **total energy** on the field DOF; the minimum **directly gives the mass** |
| Minimizer | **nonlinear conjugate gradient**, **Polak-Ribière** update (vs the current FIRE + L-BFGS in `m5_11_p0_minimizer.py`, a candidate swap / cross-check) |
| Line search | **bracketing + golden-section** along the gradient |
| Derivatives | the difference-quotient scheme in Faber's `derivatives.tex` (local-only, `theory/golubich_faber_su2/`); integrating it is the "main challenge" Golubich flags, maps onto P-D |
| Free parameters | **one**: `r₀`; `r₀ = (π/4)·r_classical` reproduces electron mass + `α` + the perturbative-QED vacuum-polarization corrections (the source-model anchor M5.11 P1 already hit) |
| Cost | weeks on large lattices (confirms the M5.16 "serious simulation" scale; corroborates Duda `4e §1`) |

**Topological readouts (adopt at the observable stage):** charge = the sign of `nᵢ` (radial field rotation out of the core); spin = `α(r)` covering the upper (`+½`) or lower (`−½`) half of SU(2)-S²; the SU(2) field couples to ED via the rotation axis `n̂`, constant along E field lines. These are analytic invariants of the solitonic solution, not fitted.

## Definition of done

A documented, reproducible **axisymmetric energy-minimization** run at the physical `(g, δ)` regime that (1) reproduces the electron anchors (mass, `α⁻¹`, Coulomb) with a **calibrated** `V(M)` and core regularization, (2) reports the **locked `(g, δ)` + `V(M)` coefficients** with their derivation/anchor, and (3) hands that parameter set to the calibration cluster. Matching every downstream observable is not the bar; the locked parameters + the honest run recipe are.

## Gating / relations

- **Gates (unblocks):** M5.9.0 (the real calibration axis, currently a residual), M5.9 (lepton masses), M5.11 (neutrino vortex loop, whose own blocker is this exact parameter-lock), `#220` (absolute-ω).
- **Inputs (interim forms exist, not blockers):** Q7 (`V(M)` form, [`../m5_question_tracker.md`](../m5_question_tracker.md)) and Q8 (Faber regularization) — M5.16 turns these from "open" toward "pinned" by using the anchors to fix their parameters.
- **Builds on:** the M5.11 P0-P1 minimizer + Taichi-AD engine (above); the `m5_4c` δ/g decoder-ring; the `#208`/`#218` calibration findings.
- **Sequencing:** recommended **ahead of resuming M5.11** — M5.11 is parked precisely on the missing parameter-lock this task supplies ([`m5_11_task_details.md`](m5_11_task_details.md), SESSION_STATE fork B).

## Cross-links

- Origin convo: [`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md) · prior δ/g threads [`m5_4c_convo_2026.06.08.md`](m5_4c_convo_2026.06.08.md), [`m5_4d_convo_2026.06.11.md`](m5_4d_convo_2026.06.11.md)
- Calibration record: [`../m5_summary_report.md`](../m5_summary_report.md) (§3 N-6b absolute-ω; DUDA follow-up) · [`../m5_question_tracker.md`](../m5_question_tracker.md) (Q7, Q8)
- Downstream: [`m5_9_0_task_details.md`](m5_9_0_task_details.md) · [`m5_9_task_details.md`](m5_9_task_details.md) · [`m5_11_task_details.md`](m5_11_task_details.md)
