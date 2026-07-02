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

---

## FINDINGS (2026-07-02 run)

Run record: go 15:07 EDT; in-flight state in [`../findings/m5_16_checkpoints.md`](../findings/m5_16_checkpoints.md). All artifacts `m5_16_*` under [`../scripts/`](../scripts/), [`../data/`](../data/), [`../plots/`](../plots/).

### The instrument (P-B + P-D): built, gated, converged

`m5_16_axisym.py`: the equivariant reduction `M(ρ,φ,z) = R₁₂(φ)·M̃(ρ,z)·R₁₂(φ)ᵀ` turns the 3D functional into an exact 2D `(ρ,z)` problem (azimuthal derivative = the algebraic channel `(1/ρ)[J, M̃]`; axis handled by a cell-centered ρ grid + mirror ghost `P·M̃·P`, `P = diag(1,−1,−1,1)`). Production gradient = the ANALYTIC numpy adjoint (hand-derived: `∇_A‖[A,B]‖² = 2[[A,B],B]` pattern, azimuthal adjoint `−[J,G]/ρ`, ghost fold-back); Taichi AD kept as opt-in cross-check only (its JIT never completed on this kernel shape, 28 min CPU, killed: recorded so nobody re-treads it). Minimizers: mass-preconditioned FIRE (P0 heritage) + nonlinear CG Polak-Ribière with bracketing/golden-section line search (the Faber-group recipe, [`m5_4g_convo_2026.07.02.md`](m5_4g_convo_2026.07.02.md)).

| Gate (pre-registered) | Result | ✅/❌ |
| --- | --- | --- |
| G2 analytic gradient vs central FD | max rel 3.6e-7 (FD-truncation-limited), incl. the axis `i=0` ghost path | ✅ |
| G3 pure-hedgehog density `r⁴·d = 8` (hand-derived) | 7.987 (0.17%) | ✅ |
| G4 shell energy = `32π(1/r₁ − 1/r₂)` closed form | 0.73% | ✅ |
| G5 3D evaluator == `m5_11_p0` lineage | rel 0.0 (bit-identical on the shared-convention region) | ✅ |
| G6 2D reduction == 3D energy under h-refinement | 1.06% at h=1 → 0.27% at h/2, shrink 3.90 ≈ h² | ✅ |
| G7 global-frame invariance (R₁₂ conjugation) | 6e-16 | ✅ |
| G8 g-decoupling: E(g=8) == E(g=1e10) | rel 0.0, EXACT | ✅ |
| R1/R2/R4 relax quality (all four β) | monotone; 6 decades; **virial E_curv/3E_pot = 1.006** | ✅ |

Gate record: [`../data/m5_16_axisym_gates.json`](../data/m5_16_axisym_gates.json).

### P-A: the physical regime, handled structurally (not by brute floats)

| Physical scale | How it enters | Measured |
| --- | --- | --- |
| `g ~ 1e10` | statics are EXACTLY g-decoupled (the time row/col never enters derivatives, `[J,·]`, or the spatial-block V): gate G8 shows E(g=8) == E(g=1e10) with rel 0.0 | ✅ structural, no arithmetic risk |
| `δ ~ 1e-10` | E(δ) is an exact QUARTIC polynomial in δ, so sampling at O(1) nodes + Vandermonde solve gives the orders `E₀..E₄` cancellation-free; `E(δ_phys)` then follows to machine precision (the N1 lesson delivered without graded commutators) | ✅ `m5_16_grade_b100_n96.json` |

δ-grading on the converged β=1 electron: `E₁ = −24.82` (δ-axis along `φ̂`) / `−24.89` (along `θ̂`), `E₂ ≈ −22.3` → at `δ_phys = 1e-10` the δ-sector shifts the electron rest energy by **fractional −1.5e-10** (Duda's "QM contribution should be relatively tiny" now has a measured number); the two admissible axisymmetric δ-textures split by only 0.27% at O(δ), `θ̂` (in-plane) preferred.

### P-C + P-E: the anchor chain and THE LOCK

| Step | Content | Status |
| --- | --- | --- |
| 1. Vacuum structure | zero forcing at the uniaxial vacuum `s=1`, spectrum `(1, δ→0, 0)`: `a = (3b−4c)/2`, melt cost `c − b/2 > 0`, `b > 0` required for shape selection (b=0 leaves a degenerate Tr2-valley) → one free shape ratio `β = b/c ∈ (0,2)` | ✅ derived |
| 2. Coulomb anchor | far-field hedgehog curvature density is EXACTLY `8c₂/r⁴` (gate G3); matching the exterior integral to the classical EM self-energy `αħc/2r` gives **`c₂ = αħc/64π = 7.1618e-3 MeV·fm`**, analytic | ✅ locked |
| 3. Mass anchor | per β one relaxed solution: `E_phys = m_e c²` fixes the grid unit `ℓ = c₂·E_sim/m_e ≈ 0.2495 fm` (β=1) → `(a,b,c)` in MeV/fm³ via the energy-density unit `c₂/ℓ⁴` | ✅ locked per β |
| 4. Size prediction | with both anchors spent, the electron's energy-median radius is a PREDICTION: see below | ✅ |
| 5. β residual | `r_half(β)` is nearly flat (2.916→2.939 fm across β 0.25→1.5): β canNOT be pinned by the electron sector. Its physical meaning: **`κ_δ = (3/2)·b_phys`** is the δ-axis stiffness (the cubic alone restores the δ eigenvalue), so the NEUTRINO sector (M5.12 phase E) is its natural anchor. Honest 1-dof residual, carried forward | 🔶 |
| 6. g | statics carry no g information (structural, G8); g comes only from the clock/boost sector: `GEM ∝ (b_boost·g)²` ([`m5_4c_convo_2026.06.08.md`](m5_4c_convo_2026.06.08.md) § 5), electron-clock absolute ω (`#220`), or baryon gravitational mass (Duda `4e`). Working value `g ~ 1/δ ~ 1e10` (`g·δ = 1`) | 🔶 hypothesis |

**Locked parameter table (β=1.0 canonical row; full β family in [`../data/m5_16_parameter_lock.json`](../data/m5_16_parameter_lock.json)):**

| Parameter | Value | Anchor |
| --- | --- | --- |
| `c₂` | `7.1618e-3 MeV·fm` (= `αħc/64π`, exact) | Coulomb |
| `ℓ` (grid unit) | `0.2495 fm` | m_e |
| `a` | `−3.484e-3 MeV/fm³` (β=1; `a = −c/2` at β=1) | vacuum structure + m_e |
| `b` | `6.968e-3 MeV/fm³` (β=1) | shape ratio β (residual) |
| `c` | `6.968e-3 MeV/fm³` | m_e |
| `κ_δ = (3/2)b` | `1.045e-2 MeV/fm³` at β=1; range `1.69e-3` (β=0.25) to `2.48e-2` (β=1.5) | the M5.12 phase-E handoff equation |
| `δ` | `1e-10` 🔶 (Duda, QED Dirac coefficient); arithmetic exact via grading | pending sharp anchor (κ_δ route) |
| `g` | `1e10` 🔶 (`g·δ = 1` hierarchy); statics g-blind (G8) | clock/boost sector (`#220`) |

### THE HEADLINE: a parameter-free cross-model agreement with Faber

With Coulomb fixing `c₂` and `m_e` fixing the scale, **nothing is left to tune**, and the M5 electron's energy-median radius comes out

| Observable | M5 (this run) | Faber SU(2) reference | Gap |
| --- | --- | --- | --- |
| `r_half` (radius enclosing half the rest energy, tail-inclusive) | **2.916-2.939 fm** (whole β family) | **3.0749 fm** (= `u_half·r₀`, `u_half = 1.3894` from the arctan profile, integrand verified `I = π/4` to 1e-11) | **≈ −4.7%** |

Two different field theories (the M5 quartic tensor-commutator functional vs Faber's SU(2) soliton), same two anchors, independently land on the same electron size to ~5%. The gap is stable across β and, per the h-convergence section below, is GENUINE model difference (discretization is converged out at 0.01%): the M5 electron is 4.8% more compact than Faber's at the energy median. Plot: [`../plots/m5_16_calibration.png`](../plots/m5_16_calibration.png).

### The stability finding (Q8, M5-native): the spherical hedgehog is not the unconstrained minimum

The unconstrained 2D axisym relax ESCAPES the spherical hedgehog: the melt core collapses toward lattice scale while the winding spreads to box scale (E → 8.5 vs the spherical 21.7 at the smoke settings): with no Frank quadratic term, the M5 quartic functional prefers a non-spherical texture in the axisym class (the LdG point-defect-vs-ring escape, textbook analog). The calibration therefore runs in the **spherically-constrained class** (exactly Duda's "assuming initial field configuration like hedgehog", and Faber's own ansatz), converging cleanly there (virial 1.006). The constrained-vs-unconstrained tension IS the M5-native face of Duda's Q8 ("regularization in the center ... details still to be established") and goes into the pre-flight ask round.

**Explicit probe (✅ measured, `data/m5_16_axisym_b100_n64_stability.json`):** seeding the unconstrained 2D relax from the CONVERGED radial solution plus a 3% symmetry-breaking bump, the energy descends 35% below the spherical minimum (25.14 → 16.23 in 6000 iters, still descending) and the melt minimum moves off-origin to `(ρ, z) ≈ (1.5, 2.5)`: the spherical hedgehog at β=1 is a SADDLE of the unconstrained axisym functional. Duda-facing formulation for the ask round: does the model intend the electron as the symmetric hedgehog (then what holds it: a Frank-type quadratic term? sixth-order LdG? the clock dressing?), or is the escaped/ring-core texture acceptable as the electron?

### P-G: the δ-continuation probe (the M5.12 unlock read)

`m5_16_delta_continuation.py` (fork of the frozen P2 machinery, δ promoted to the sweep variable, everything else at the M5.11 run-3/run-2 settings; 106 s, Taichi cache hit). δ ∈ {0.3, 0.2, 0.1, 0.05, 0.02}:

| Indicator | δ = 0.3 → 0.02 | Read |
| --- | --- | --- |
| helix background deformation `dMsp_max` (L=1.7) | 1.26 → 1.03 | monotone relaxation toward uniaxial |
| same at L=5.0 | 1.39 → 1.17 | monotone |
| amplitude deviation (L=5.0) | 0.85 → 0.81 | mild monotone |
| blue-phase melt fraction | 0.000 at every δ | no melt network forms at these settings |
| heliknoton excess retention | 154% → 104% | the seeded texture stops being distorted as δ → 0 |
| localization (peak/mean) | 1.39 → 1.62, rising monotonically toward uniaxial | supportive trend, but far below the ≥4 localized-knot bar: ⚠️ no localized knot at ANY δ with the sandbox potential |

**Verdict 🔶: directionally supportive of the 2026-07-02 unlock hypothesis (all FOUR indicators move monotonically the right way as δ → 0: background deformation down, amplitude deviation down, excess retention → 100%, localization up), but δ alone does not stabilize a knot: the calibrated potential + the M5.12 phase A-C constructions remain necessary.** The M5.11 P2 negatives stay classified as regime artifacts pending the physical-regime re-run, not verdicts. Data: [`../data/m5_16_delta_continuation.json`](../data/m5_16_delta_continuation.json) · plot: [`../plots/m5_16_delta_continuation.png`](../plots/m5_16_delta_continuation.png).

### Convergence (h-refinement): ✅ converged, the gap is genuine

β=1 family with box/core ratio fixed (core resolved by 5.3 / 8 / 10.7 cells); the χ-invariant `J_half = E_sim·r_half` is the compared quantity:

| NR (core cells) | `J_half` | `r_half_phys` | virial |
| --- | --- | --- | --- |
| 64 (5.3) | 206.06 | 2.888 fm | 1.016 |
| 96 (8.0) | 208.71 | 2.925 fm | 1.006 |
| 128 (10.7) | 208.74 | 2.926 fm | 1.003 |

`J_half` moves 0.01% from n96 to n128: the instrument is CONVERGED at the production resolution, and the virial marches toward exact Derrick balance at ~h² order. Richardson from the (96,128) pair puts the continuum prediction at `r_half = 2.926 fm`, so the **−4.8% gap vs the Faber reference is a genuine cross-model difference, not discretization**: the honest number to report.

### Honest caveats (do not overclaim)

| Caveat | Status |
| --- | --- |
| `r_half` is an energy-median observable, not Faber's profile-parameter `r₀`; the cross-model comparison uses the SAME observable on both (his arctan profile integrand), which is the defensible apples-to-apples | by construction |
| the quartic trace-LdG cannot be exactly stationary at the biaxial `(1, δ, 0)`: residual force `3bδ ≈ 3e-10·b` at δ_phys: the δ eigenvalue is a perturbative dressing, not an exact vacuum eigenvalue, unless a higher-order (sixth-order) LdG term pins it (Q7 refinement for Duda) | honest remainder |
| β (= b/c) is NOT pinned by the electron sector (r_half flat in β): 1-dof family carried to M5.12 phase E via `κ_δ = (3/2)b` | open by design |
| the spherical hedgehog is a CONSTRAINED stationary solution (saddle suspicion in the unconstrained axisym class): the stability probe quantifies it; resolution of point-vs-ring is Q8 territory | flagged |
| `g = 1e10`, `δ = 1e-10` remain Duda's order-of-magnitude hierarchy (🔶), not sharp anchors; the lock delivers the EQUATIONS they enter (G8 g-blindness, κ_δ, GEM ∝ (b_boost·g)²) so any sharp anchor converts directly | labeled |
| α⁻¹ itself was not re-derived here (that is the M5.11 P1b charge-quantization result, banked); this task USES α as the anchor | inherited |

### Artifacts

| Type | Files |
| --- | --- |
| scripts | [`m5_16_axisym.py`](../scripts/m5_16_axisym.py) (gates · radial · relax · stability · grade) · [`m5_16_calibrate.py`](../scripts/m5_16_calibrate.py) (sweep · lock) · [`m5_16_delta_continuation.py`](../scripts/m5_16_delta_continuation.py) (P-G) |
| data | `m5_16_axisym_gates.json` · `m5_16_axisym_b{025,050,100,150}_n96.json` · `m5_16_axisym_b100_n{64,128}.json` · `m5_16_parameter_lock.json` · `m5_16_grade_b100_n96.json` · `m5_16_delta_continuation.json` (all < 100 KB; nothing to delete under the 1 MB rule) |
| plots | [`m5_16_calibration.png`](../plots/m5_16_calibration.png) · [`m5_16_delta_continuation.png`](../plots/m5_16_delta_continuation.png) |
| in-flight state | [`../findings/m5_16_checkpoints.md`](../findings/m5_16_checkpoints.md) |

## Gating / relations

- **Gates (unblocks):** M5.9.0 (the real calibration axis, currently a residual), M5.9 (lepton masses), M5.12 (the neutrino re-entry, gated on this lock + the pre-flight ask round), `#220` (absolute-ω).
- **Inputs (interim forms exist, not blockers):** Q7 (`V(M)` form, [`../m5_question_tracker.md`](../m5_question_tracker.md)) and Q8 (Faber regularization) — M5.16 turns these from "open" toward "pinned" by using the anchors to fix their parameters.
- **Builds on:** the M5.11 P0-P1 minimizer + Taichi-AD engine (above); the `m5_4c` δ/g decoder-ring; the `#208`/`#218` calibration findings.
- **Sequencing:** runs FIRST: M5.12 (the neutrino re-entry, successor of the closed M5.11) is gated on the parameter-lock this task supplies plus the pre-flight ask round it opens ([`m5_12_task_details.md`](m5_12_task_details.md) § Entry gates).

## Cross-links

- Origin convo: [`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md) · prior δ/g threads [`m5_4c_convo_2026.06.08.md`](m5_4c_convo_2026.06.08.md), [`m5_4d_convo_2026.06.11.md`](m5_4d_convo_2026.06.11.md)
- Calibration record: [`../m5_summary_report.md`](../m5_summary_report.md) (§3 N-6b absolute-ω; DUDA follow-up) · [`../m5_question_tracker.md`](../m5_question_tracker.md) (Q7, Q8)
- Downstream: [`m5_9_0_task_details.md`](m5_9_0_task_details.md) · [`m5_9_task_details.md`](m5_9_task_details.md) · [`m5_12_task_details.md`](m5_12_task_details.md) (predecessor record: [`m5_11_task_details.md`](m5_11_task_details.md), closed)
