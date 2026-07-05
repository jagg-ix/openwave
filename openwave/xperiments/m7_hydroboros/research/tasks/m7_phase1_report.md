# M7 / HydroBoros - PHASE 1 REPORT

  ![hydroboros_icon](../../images/hydroboros_icon_small.jpg)

> The human-readable summary of Phase 1 (tasks M7.0-M7.7, finished on 2026-07-04). Everything here is a pointer: each claim links its detail doc, script, and data. Written for the two physics parents (Marc Fleury, Paul Werbos) and for anyone auditing the program.

## 1. What M7 is

**HydroBoros** fuses Fleury's toroidal-EM electron (analytic, [arXiv:2510.22384](https://arxiv.org/abs/2510.22384)) with Werbos's Ouroboros self-confinement (M6, 1D radial) into one full-3D-PDE lattice program: the electron's field configuration is both *specified* (a self-linked toroidal Beltrami vortex) and *earned* (as the constrained energy-minimizer of the written functional). One-page orientation: [`__M7_model_briefing.md`](../../__M7_model_briefing.md). Full background (the two parents, the mathematical boundaries, the dynamics frame): [`m7_background.md`](../m7_background.md).

## 2. What Phase 1 did (M7.0 → M7.7)

| Task | What landed | Detail |
| --- | --- | --- |
| M7.0 bootstrap | 64-doc theory corpus + planning scaffolding | [`m7_0_bootstrap.md`](m7_0_bootstrap.md) |
| M7.1 infra | 3D harmonic lattice, Taichi-AD gradients (2.3e-15 vs complex-step), FIRE + constraints; Woltjer-Taylor known-answer gate (`λ → 2π/L` at 5.5e-6) | [`m7_1_infra.md`](m7_1_infra.md) |
| M7.2 reproduce Fleury | the FLDB torus quadrature to closed forms at 1.4e-4; the printed solution reconstructed digit-for-digit; the corrected-convention `U = 0.958 m_ec²` (Q10) | [`m7_2_fleury_torus.md`](m7_2_fleury_torus.md) |
| M7.3 reproduce M6 in 3D | the benchmark ODE pinned as a verbatim EL reduction (sympy scan); the M6 charged ledger `H/Q` reproduced in full 3D to **4.7e-5**; three discoveries: the ledger is window-defined (Q11), the `§ 2.2` form is not an EL reduction (Q12), the M6 electron is a 3D constrained saddle (Q13) | [`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md) |
| M7.4 the charged soliton (new physics) | **the program's first stable finite-size 3D soliton family** (Taylor-dressed, `E = 0.802\|H_A\|` universal); helicity measurably load-bearing; the written `f = gs²` beats the benchmark signs (Q6 resolved empirically) | [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md) |
| M7.5 clock + stability | translation exactness (`⟨E_real⟩ = E_ω` to 1.85e-14); **the vacuum tachyon discovered** (measured rate 0.785 vs analytic 0.786) + the existence threshold **`ω* = 0.786`** (the clock IS the stabilizer); the ω-`Q_can` Legendre conjugacy verified to 1-2% (Q14 opened) | [`m7_5_clock_stability.md`](m7_5_clock_stability.md) |
| M7.6 observables | **the rotating electron**: a clean `j_z = 1` per-quantum wave (0.6%); **Coulomb landed** (Gauss 99.1%, far field −2.14, two-charge `1/d` reference-matched, a measured **1.17 coupling dressing**); the RKKY-style neutral exchange discovered | [`m7_6_observables.md`](m7_6_observables.md) |
| M7.7 consolidation (milestone) | the canonical spec + a ~200-line physics module + a one-script reproduction (**all gates first-try at two resolutions; engine-vs-reference 1.4e-14**); the 21-cell column drafted + staged | [`m7_7_consolidation.md`](m7_7_consolidation.md) |

## 3. The canonical spec (the equations)

**[`m7_theory_canonical.md`](../m7_theory_canonical.md)** is the results-of-record spec: it OPENS with the Lagrangian and every pinned convention (with the provenance of each pin), then the equation-to-code map, then results after methods, then the explicit not-computed list. The physics itself lives in one auditable ~200-line module, [`scripts/m7_functional.py`](../scripts/m7_functional.py) (its docstring carries the same equations), and the whole electron reproduces from one script, [`scripts/m7_7_canonical.py`](../scripts/m7_7_canonical.py): ~3 min quick mode, ~10 min record mode, with the Taichi engine cross-validated against the reference module to 1.4e-14 as a first-class gate.

## 4. Results and findings (the staged column)

The 21-cell coverage column is drafted in **[`preview_models.md`](../preview_models.md)**: **0 ✅ / 8 ⚠️ / 0 ❌ / 13 🚧**, every partial carrying its named caveat. It is deliberately **staged, not yet published to [`MODELS.md`](../../../../../MODELS.md)**: the program still carries its own open theory question (Q14, the vacuum tachyon) and convention questions (Q15, Q10, Q12) that move icons either way; **promotion comes after Phase 2, gated by the question tables below** (the M7.15 publication milestone, Phase 3). What the eight partials say, in three plots:

**The soliton exists and is grid-convergent.** Three helicity-carrying seeds relax to one Taylor-dressed family; the winner is localized (r50 = 3.4), approximately Beltrami in the core (`λ_eff ≈ −1` near-constant), dilation-stable (a measured constrained-Derrick interior minimum), with the J-condensate co-located; both zero-helicity parent seeds die, so helicity is measurably the guard:

![the M7.4 winner sections](../plots/m7_4_winner_sections.png)

**The clock is load-bearing, quantitatively.** The linearized vacuum of the truncation is unconditionally tachyonic at long wavelength (left: both quartic conventions, `det M(0) = −1`); the measured vacuum growth rate matches the analytic band edge to 0.15% with no amplitude threshold (middle); and harmonic solitons exist only above `ω* = 0.786`, exactly the band edge (right: runaway at ω = 0.70/0.75, clean solitons from 0.79 up):

![the M7.5 tachyon + threshold triptych](../plots/m7_5_tachyon_scan.png)

**Coulomb is real once a monopole exists.** With a fixed charge reservoir (`j₀`) and the scalar potential unfrozen, Gauss's law closes at 99.1% (left), the far field is `1/r²` (middle, slope −2.14 vs the chargeless −3.7), and the two-charge splitting matches the Poisson reference in the same grounded box at a constant **1.17 ± 0.02** dressing (right), the program's first fine-structure-flavored number:

![the M7.6 Coulomb triptych](../plots/m7_6_coulomb.png)

## 5. Open questions for Marc Fleury, most critical first

Tracked with stable IDs in [`m7_question_tracker.md`](../m7_question_tracker.md) (full statement + history at each anchor).

| ID | Question | Why we ask |
| --- | --- | --- |
| [Q7](../m7_question_tracker.md#q7-detail) | The charge-carrying construction: the Sato-Yamada variable-h toroidal recipe, and does the FLDB picture single out a `j₀` profile? | your "start Trkalian, take off the training wheels" is validated (approximately-Beltrami cores, `\|align\| = 0.96`; charge measured, never imposed) and the fixed-reservoir prescription landed Coulomb; the **self-consistent** charge profile is the one piece we cannot pick ourselves |
| [Q3](../m7_question_tracker.md#q3-detail) | Divergence charge vs linking charge: we measured them **independent** (linking gates existence; the RMS charge coexists, unslaved): does the Pisello/Gauss-Bonnet reading require a deeper slaving we should test for? | decides whether charge quantization should be sought in topology (then we design that test) or in the source sector |
| [Q10](../m7_question_tracker.md#q10-detail) | The FLDB energy algebra: Eqs 122/124/127 carry a dropped square + a dropped ½; the corrected value is `U ≈ 0.958 m_ec²` (was 0.795): intended? | it moves the paper's headline energy 20% in the right direction; we reproduced the printed solution digit-for-digit first, so the correction is isolated to those steps |
| [Q15](../m7_question_tracker.md#q15-detail) | The units contract: `ω = ω_Compton` or `ω = ω_Dirac` (Zitter)? We measured `j_z = 1` per quantum (0.6%) and `ωL_z/E = 2.07`; the Zitter mapping lands the total at ℏ within 3% (our on-record recommendation) | one convention choice decides the ℏ/2-vs-ℏ spin reading and the absolute mass anchor; the FLDB targets are stated as `ω/ω_D` ratios, so the intent is yours to pin |
| [Q1](../m7_question_tracker.md#q1-detail) | Substrate reading: the `(A_μ, J_μ)` doublet vs a single Riemann-Silberstein field; target manifold S² (Pisello) vs S³ (Faber)? | fixes which topological invariants Phase 2 should constrain (the knot-sector work needs the right manifold) |
| [Q4](../m7_question_tracker.md#q4-detail) | The further Beltrami material you mentioned + the Enciso / Peralta-Salas contact status? | the rigidity/existence theorems shaped the whole relax-and-measure design; more of that literature de-risks Phase 2 |

## 6. Open questions for Paul Werbos, most critical first

| ID | Question | Why we ask |
| --- | --- | --- |
| [Q14](../m7_question_tracker.md#q14-detail) | **The vacuum tachyon**: the linearized vacuum of the written theory has `det M(0) = −1` for ANY `f` (unconditional long-wavelength instability; measured growth rate 0.785 vs analytic 0.786, amplitude-independent, so **no `β*` threshold exists** in the vector truncation): what cures it in the full model (an A-mass / a condensate vacuum / the scalar-Gauss sector / parameter islands)? | the load-bearing theory question: it blocks every real-time run (annihilation, M7.12); it is also a gift: the harmonic frame survives exactly because `ω > ω* = 0.786`, i.e. **the de Broglie clock is the vacuum-stability mechanism**, a strong Ouroboros-thesis statement if the full theory confirms it |
| [Q11](../m7_question_tracker.md#q11-detail) | The charged `H/Q = 1.6890` is window-defined (both far-field roots propagate at the canonical point; `Q` grows with the window): understood? and does a genuinely localized charged branch exist elsewhere in `(ω, λ, g)`? | it blocks any physical-mass reading of the charged ledger; the same dispersion also has a measured consequence (neutral solitons exchange RKKY-style with period `π/k`) |
| [Q13](../m7_question_tracker.md#q13-detail) | The M6 electron is a 3D constrained **saddle** (focusing collapse; the helicity guard is inert on the zero-helicity ansatz): is the conjugate-point stability claim established only on the 1D radial manifold? | adding helicity to the same torus stabilizes it (our M7.4 fix), and the `ω*` threshold now bounds where ANY harmonic soliton exists: the 1D-vs-3D scope of the original claim is the remaining piece |
| [Q12](../m7_question_tracker.md#q12-detail) | ODE provenance (+ the Q6 residual): the benchmark ODE is the verbatim EL of the same-phase doublet with FOCUSING signs, while the written `f = gs²` (the stable branch, which we run) differs; and `0d_canonical § 2.2`'s `2ωα` form matches no EL reduction we scanned: which ansatz + ODE is canonical, and do you confirm the benchmark sign slip + the `(g/4)` transcription fix? | your confirmation closes the convention file and fixes our M6 doc; nothing is blocked on it (we proceed on the empirically stable branch) |
| [Q9](../m7_question_tracker.md#q9-detail) | The `(Ω, G)` dictionary of the v5 scan: definitions in terms of `(ω, g, λ, m_J)` + one concrete electron-island parameter point we can run? | your `k > 0` stable-island label suggests a cured region; our measured threshold `ω* = 0.786` is a candidate anchor (the islands may be the `ω > ω*(g, λ)` region): with the dictionary we can check on the lattice |

## 7. What comes next (Phase 2)

Full roadmap: [`m7_roadmap.md`](../m7_roadmap.md). Phase 2 (M7.8-M7.14) expands across the forces and the remaining particle sectors, none of it blocked on the questions above (pre-agreed tripwire: if a task hits a question we cannot self-resolve, we stop and ask then):

| Next | Task | One line |
| --- | --- | --- |
| 1 | M7.9 magnetic force | the per-defect magnetic structure carried by the electron's clock |
| 2 | M7.10 gravity | the time-axis boost route (honestly hard: Ouroboros stops before gravity) |
| 3 | M7.11 nuclear forces | strong = short-range roll-off + linking tension; weak = topology reconnection |
| 4 | M7.12 antimatter + annihilation | real-time evolution blocked on Q14; harmonic-frame preparations proceed |
| 5 | M7.13 leptons + neutrinos | knot sectors (needs the topology-preserving constraints M7.4 identified) |
| 6 | M7.14 dark matter | the neutral helicity-only knot, inheriting M6's chaoiton |

After Phase 2: **M7.15 publishes the column to MODELS.md** for cross-model benchmarking (Phase 3), gated by the question tables above; then composites (Phase 4) and production rendering (Phase 5).

---

Cross-refs: briefing [`__M7_model_briefing.md`](../../__M7_model_briefing.md) · background [`m7_background.md`](../m7_background.md) · spec [`m7_theory_canonical.md`](../m7_theory_canonical.md) · column preview [`preview_models.md`](../preview_models.md) · tracker [`m7_question_tracker.md`](../m7_question_tracker.md) · roadmap [`m7_roadmap.md`](../m7_roadmap.md) · the milestone task [`m7_7_consolidation.md`](m7_7_consolidation.md).
