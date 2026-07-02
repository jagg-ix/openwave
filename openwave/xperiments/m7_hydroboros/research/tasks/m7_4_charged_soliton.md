# M7.4, the charged soliton (approximately-Beltrami) + its Coulomb field (the NEW physics)

> Task **M7.4** (M7 / HydroBoros). taskID = M7.N iteration. Status: **Backlog** · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation. **M7.4 is the research core**: the charged, knotted, finite-size soliton neither parent produced. Reframed 2026-07-02 after the corpus math review ([`../m7_background.md § 2`](../m7_background.md) "What the Beltrami mathematics allows"): the task does **not** hunt an exact variable-λ Beltrami ansatz; it relaxes the full functional and **measures** what charge the coupling drives.

---

## 1. The physics frame (why relax-and-measure, not construct-exactly)

| Math fact | Consequence |
| --- | --- |
| divergence identity `∇·w = −(w·∇λ)/λ` | charge requires λ varying **along** field lines |
| rigidity (Clelland-Klotz 2020; Enciso-PS): nonconstant-λ Beltrami obstructed even locally | an exact charged Beltrami ansatz likely does not exist for generic profiles |
| Nadirashvili: no finite-`L²` Beltrami field in ℝ³ at all | the soliton is NOT an exact Beltrami field; it is the minimizer of the **full** functional, approximately Beltrami in the core, with the Ouroboros confinement holding it (the § 5b stabilization story) |
| Kaiser 2000: variable-α exists perturbatively (small α) | the small-charge regime is safe ground to enter from |
| Enciso-PS 2012: constant-λ realizes **arbitrary knots** | the Trkalian seed inventory is topologically complete |

So: seed Trkalian (exactly Beltrami, zero charge), switch on the Ouroboros coupling, relax `E_ω` at fixed ω + helicity, and measure the deviation. The charge is **output, not input**. Marc's "start Trkalian, take off the training wheels" (2026-06-30) survives intact in this implementation.

## 2. Seeds (multiple, per Sutcliffe's local-minima lesson)

Sutcliffe (corpus #8): the Hopfion energy landscape is dense with local minima; seed variety is not optional. The inventory (built at M7.1):

| Seed | Topology | Why |
| --- | --- | --- |
| Trkalian / ABC eigenfield torus | unknot, tunable helicity | the clean entry point |
| S&Y toroidal Beltrami | unknot, toroidal geometry | Marc's endorsed recipe |
| Bateman / Kedia knots | trefoil + torus knots | knotted sector (Q5) |
| the M6-embedded chaoiton (from M7.3) | `Q_CS = 1` | the Ouroboros parent's own configuration |
| the Fleury torus (from M7.2) | `m = 1` rotating wave | the Fleury parent's own configuration |

**Blend design item** (explicit, from [`../m7_background.md § 4`](../m7_background.md) structural note): the two parents' electrons are different configurations (Fleury: `B = ∇×A ≠ 0`; M6: `A⃗ = 0`, `B = 0`). Which components carry the torus and which the confinement is decided HERE, by relaxing both parent seeds (+ hybrids) under the same functional and reporting which basin wins.

## 3. Procedure + diagnostics

| Step | Diagnostic |
| --- | --- |
| relax each seed: `E_ω` at fixed ω + helicity, vacuum-fixed BCs | `‖∇E‖ → 0` |
| **dilation probe**: evaluate `E(μ)` along lattice rescalings of the relaxed state | interior minimum at `μ = 1` (the direct Derrick verification; replaces trust in any stabilizer argument) |
| **the Q3 measurement** (first-class deliverable) | per relaxed state: `Q_div` (Gauss flux at increasing radii), helicity `H = ∫A·B`, field-line **linking / Hopf number** (tracer); the `(Q_div, H, linking)` table + ratio analysis across states answers whether divergence-charge and topological charge are slaved (Q3) |
| `λ_eff(x) = F·(∇×F)/\|F\|²` map | where the state is Beltrami (core?) and where the charge-carrying deviation lives |
| far field | `\|E\| ~ Q_div/4πε₀r²` fit (Coulomb from Gauss) |
| charge quantization | does `Q_div` land on discrete values across seeds/parameters? assessed honestly (Pisello and Faber say yes topologically; this is the lattice test) |

Optional experiment (Q2, off by default): switch a 4th-order term on and quantify what it changes; the drafted `\|F×(∇×F)\|²/\|F\|²` form is documented-inert on Beltrami configs and singular at zeros, so any 4th-order run uses a regularized variant and is labeled an experiment, not the baseline.

## 4. Gates + honest outcomes

| Gate | Criterion |
| --- | --- |
| primary | a **stable, finite-size, charged** (`Q_div ≠ 0`) soliton: `‖∇E‖ → 0` + the dilation probe's interior minimum |
| Q3 deliverable | the `(Q_div, H, linking)` table published regardless of outcome |
| Coulomb | `1/r` far-field fit sourced by `Q_div` |
| honest negatives | expansion (the Rañada / M5.11-P2 mode, if confinement loses), collapse, or charge → 0 under relaxation are all documented results with the seed + parameter map |

Risk register for this task: rigidity + Nadirashvili (mitigated by the reframe), M5.11's P2 lesson (smooth knots expand; the confinement term is what M7 has that M5's functional lacked), gauge flat directions (Q8, from M7.1), multi-hour GPU cost (accepted).

Artifacts: `scripts/m7_4_linked_vortex.py` + `data/m7_4_*.npz` + `plots/m7_4_*.png` (λ_eff maps, dilation curves, the Q3 table, far-field fits).

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (M7.4) · background [`../m7_background.md`](../m7_background.md) (§ 2 the math boundaries, § 4 structural note, § 5b stabilization) · Q2/Q3/Q5/Q7/Q8 in [`../m7_question_tracker.md`](../m7_question_tracker.md) · upstream [`m7_1_infra.md`](m7_1_infra.md) (seeders, helicity, BCs) + [`m7_2_fleury_torus.md`](m7_2_fleury_torus.md) + [`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md) (the parent seeds) · downstream [`m7_5_clock_stability.md`](m7_5_clock_stability.md) (real-time validation) + [`m7_6_observables.md`](m7_6_observables.md) (observables + two-charge Coulomb).
