# M5.16: Axisymmetric energy-minimization calibration solver (the parameter-lock gate)

> Task **M5.16** (M5 / Liquid-Crystal model). Status: **Backlog (recommended next)** · Gated by: - (interim `V(M)` + Faber melt already in engine1_seeds; Q7/Q8 are inputs, not blockers) · Gates: M5.9.0 real-calibration axis, M5.9, M5.12 (the neutrino re-entry), `#220` absolute-ω · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

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
| **P-A / physical (g, δ) regime** | run the minimizer at `g~1e10`, `δ~1e-10` via a **non-dimensionalized formulation or a perturbative δ-expansion** (the ~`1e20` dynamic range exceeds f32/f64). **Reuse the validated N1 perturbative-δ machinery** (§ Existing machinery below), do not rebuild it |
| **P-B / cylindrical reduction** | reduce the electron hedgehog + the neutrino vortex loop to an **axisymmetric (r, z) BVP** (Duda's dimension-reduction trick), so the physical regime is computationally reachable |
| **P-C / potential calibration (Q7)** | fix the LdG `V(M)` coefficients `(a, b, c)` by **requiring the minimizer to reproduce the anchors** (electron 511 keV via Faber `r₀`; Coulomb; the electron-clock time scale) rather than guessing them; verify the minimum sits at eigenspectrum `(g,1,δ,0)` |
| **P-D / core regularization (Q8)** | the hedgehog/vortex center regularization (Duda's "hardest part") under the calibrated potential, on the axisymmetric mesh |
| **P-E / g from an anchor** | pin `g` from one of: the electron clock, neutrino oscillations, or baryon gravitational mass (Duda's three routes; "certain of only for baryons") |
| **P-F / handoff** | publish locked `(g, δ, a, b, c, r₀)` + the run recipe as the calibration input consumed by M5.9.0 / M5.9 / M5.12 / `#220` |
| **P-G / δ-continuation study (the M5.12 unlock probe)** | sweep δ from the placeholder 0.3 down (0.1 / 0.01 / 1e-3 / perturbative to 1e-10) and track (a) the substrate's **chiral response** (does the run-3 blue-phase obstruction relax toward a stable helix as the spatial spectrum `diag(1, δ, 0)` degenerates to quasi-uniaxial `(1, 0, 0)`?) and (b) whether the run-4 melt-heal behaviour changes. Tests the 2026-07-02 hypothesis that the M5.11 P2 loop negatives are **artifacts of the strongly-biaxial δ=0.3 regime**, cheaply, before any new loop construction. See [`m5_12_task_details.md`](m5_12_task_details.md) § The standing hypothesis |

## The δ-continuation hypothesis (P-G origin, 2026-07-02 roadmap review)

All five M5.11 P2 loop experiments (the 2×2 elimination) ran at the placeholder `δ = 0.3`, where the spatial tensor `diag(1, 0.3, 0)` is **strongly biaxial**; run 3's obstruction was precisely biaxiality (the chiral term drives a blue-phase texture, the Tai/Smalyukh thesis's flagged hard case, p.132). But Duda's 2026-07-01 sketch ([`m5_4f_convo_2026.07.01.md`](m5_4f_convo_2026.07.01.md) § 2) states the neutrino is a **uniaxial** nematic field with **1 distinguished axis**, and at the physical `δ ~ 1e-10` the substrate is **quasi-uniaxial**, exactly the regime where Smalyukh's chiral knots are known to stabilize. So the loop hunt may have been run in the wrong corner of parameter space, and M5.16's physical-regime run is the unlock, not just bookkeeping. P-G is the cheap test of that reading.

## Existing machinery to reuse (do not rebuild)

The `1e20` dynamic range already has a **built + validated** solution from the neutrino N-program foundation; P-A should reuse it, not re-derive it:

| Asset | Where | State |
| --- | --- | --- |
| Perturbative-δ precision method (order-by-order in δ; recovers the θ₁₃-class breaking channel to **9.4e-16** where naive f64 returns exactly 0) | [`../scripts/m5_11_n1_precision_method.py`](../scripts/m5_11_n1_precision_method.py) | ✅ validated (cancellation test) |
| Engine ↔ numpy-port equivalence gate (the f64 port verified against the production engine, not asserted) | [`../scripts/m5_11_n0_engine_equivalence.py`](../scripts/m5_11_n0_engine_equivalence.py) | ✅ validated |
| Foundation record (method + gates + the honest tension log) | [`../findings/n_foundation_findings.md`](../findings/n_foundation_findings.md) | record of record |

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

## Rigor compliance: implementing Duda's model the way he asks (the bar, with sources)

M5.11 was built to answer Duda's 2026-06-22 "too simple" critique ("I am trying to read these Python files, but they look very far from simulations I was expecting ... the code is much too simple ... I am very far from trusting them"), with the explicit standard "**a simulation a working physicist trusts. No cut corners**" ([`m5_11a_vortex_loop.md`](m5_11a_vortex_loop.md) § 0). M5.16 inherits and completes that standard. His rigor requirements, collected from the record, each mapped to how this task satisfies it:

| Duda's requirement (source) | How M5.16 complies |
| --- | --- |
| "needs lattice or FEM, assuming initial field configuration like hedgehog for electron or vortex loop for neutrino, and numerically performing **energy minimization**" ([`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md) § 1) | the task IS that instrument: the graduated M5.11-P0 static minimizer (FIRE + L-BFGS, plus the Golubich CG/Polak-Ribière cross-check, § Numerical recipe) |
| "for both electron and neutrino we can assume **cylindrical symmetry** to reduce dimension" (`4e` § 1) | P-B: the axisymmetric `(r, z)` reduction for both the hedgehog and the vortex ring |
| "the most difficult is **regularization in the center** of hedgehog or vortex, also requiring potential, which details are still to be established" (`4e` § 1; Q8) | P-D: core regularization on the axisymmetric mesh under the calibrated potential, guided by Faber's `derivatives.tex` difference-quotient scheme ([`m5_4g_convo_2026.07.02.md`](m5_4g_convo_2026.07.02.md)) |
| "the first step should be **establishing two basic parameters: g, delta**"; the physical regime is `δ~1e-10`, `g~1e10`, NOT the placeholders 0.3/8 he flagged ([`m5_10a_neutrino_oscillations.md`](m5_10a_neutrino_oscillations.md) rounds 2-3; `4e` § 2) | P-A/P-E: every REPORTED number at the physical regime via the validated N1 perturbative-δ machinery; placeholder-parameter results are labelled scaffolding, never headlines |
| potential minima = eigenspectrum `(g,1,δ,0)`, "Landau-de Gennes with traces of powers, still requiring to find its parameters" (`4e` § 2; Q7) | P-C: `(a, b, c)` FIXED by requiring the anchors (511 keV, Coulomb, clock), not guessed; the minimum verified to sit at `(g,1,δ,0)` |
| his convention: `D = diag(g,1,δ,0)` with `η = diag(-1,1,1,1)`, minus on the g axis (rounds 2-3, the η correction he made twice) | the engine's index-0 convention since 2026-06-21; every M5.16 script states it in its docstring, no re-derivation ambiguity |
| "**do less, but more rigorously**" (round 2, `10a`) | scope = the parameter lock ONLY; downstream observables are explicitly not the bar (§ Definition of done) |
| serious sims are heavy: "not seconds but weeks; Faber said about weeks" (`4e` § 1; Golubich `4g` confirms weeks on large lattices) | the compute budget is accepted up front; convergence order + Richardson extrapolation where applicable (the P1b pattern), no fast-setup numbers reported as final |
| the validation bar: state field configurations + pass an **independent benchmark** with "actual simulations", reproducible ([`m5_4f_convo_2026.07.01.md`](m5_4f_convo_2026.07.01.md) § 1, the MODELS.md bar) | every claim = a runnable script + a pre-registered pass/fail gate vs a KNOWN anchor (the M5.11 P0-P1 trust-rebuilder pattern: reproduce Faber's electron + `α⁻¹` before any new claim); article-standard documentation of parameters / potential / configurations |
| the earned method discipline ([`../m5_summary_report.md`](../m5_summary_report.md) § 4.3) | dt/discretization convergence as the discriminator; surrogate guides, direct quadrature decides; FFT-window + knob-gate rules where spectra/families appear |

## Comms plan: deliver first, ask second (decided 2026-07-02)

Strategy (Rodrigo): fix the infrastructure first, show Duda something **concrete, rigorous, and aligned with his theory design**, and only then ask questions, so the asks land as "doing our job right", not as leaning on him.

| Step | What | When |
| --- | --- | --- |
| 1 | Run M5.16 with NO outbound questions (the parameter/potential search is ours; he handed it over: "you should start here") | now |
| 2 | **Report the deliverable**: the locked `(g, δ, a, b, c, r₀)` + the rigor-compliant run recipe (the table above, satisfied item by item) | at M5.16 FINISH |
| 3 | **The M5.12 pre-flight ask round**: ALL pending neutrino-re-entry questions batched in ONE email, backed by the deliverable: Q13 (chiral invariant), the loop-vs-knot choice (Hopf-linked pair vs trefoil vs the sketch's "two vortex types"), the δ_CP fork framing ([`../m5_question_tracker.md`](../m5_question_tracker.md) § Ask queue) | right before starting M5.12 |
| 4 | His answers feed the phase A/C design; go M5.12 ([`m5_12_task_details.md`](m5_12_task_details.md)) | after replies |

The prize is his own framing (round 3, `10a`): deriving the 4 PMNS parameters rigorously, "if writing convincing article able to pass peer review, this already would be huge."

## Definition of done

A documented, reproducible **axisymmetric energy-minimization** run at the physical `(g, δ)` regime that (1) reproduces the electron anchors (mass, `α⁻¹`, Coulomb) with a **calibrated** `V(M)` and core regularization, (2) reports the **locked `(g, δ)` + `V(M)` coefficients** with their derivation/anchor, and (3) hands that parameter set to the calibration cluster. Matching every downstream observable is not the bar; the locked parameters + the honest run recipe are.

## Gating / relations

- **Gates (unblocks):** M5.9.0 (the real calibration axis, currently a residual), M5.9 (lepton masses), M5.12 (the neutrino re-entry, gated on this lock + the pre-flight ask round), `#220` (absolute-ω).
- **Inputs (interim forms exist, not blockers):** Q7 (`V(M)` form, [`../m5_question_tracker.md`](../m5_question_tracker.md)) and Q8 (Faber regularization) — M5.16 turns these from "open" toward "pinned" by using the anchors to fix their parameters.
- **Builds on:** the M5.11 P0-P1 minimizer + Taichi-AD engine (above); the `m5_4c` δ/g decoder-ring; the `#208`/`#218` calibration findings.
- **Sequencing:** runs FIRST: M5.12 (the neutrino re-entry, successor of the closed M5.11) is gated on the parameter-lock this task supplies plus the pre-flight ask round it opens ([`m5_12_task_details.md`](m5_12_task_details.md) § Entry gates).

## Cross-links

- Origin convo: [`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md) · prior δ/g threads [`m5_4c_convo_2026.06.08.md`](m5_4c_convo_2026.06.08.md), [`m5_4d_convo_2026.06.11.md`](m5_4d_convo_2026.06.11.md)
- Calibration record: [`../m5_summary_report.md`](../m5_summary_report.md) (§3 N-6b absolute-ω; DUDA follow-up) · [`../m5_question_tracker.md`](../m5_question_tracker.md) (Q7, Q8)
- Downstream: [`m5_9_0_task_details.md`](m5_9_0_task_details.md) · [`m5_9_task_details.md`](m5_9_task_details.md) · [`m5_12_task_details.md`](m5_12_task_details.md) (predecessor record: [`m5_11_task_details.md`](m5_11_task_details.md), closed)
