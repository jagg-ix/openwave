# M7.1, infra (define the substrate field + stand up the lattice / minimizer)

> Task **M7.1** (M7 / HydroBoros). taskID = M7.N iteration. Status: **In Progress** · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation. **M7.1 (infra)** stands up the A-primary field on a 3D periodic lattice, the AD energy gradient (validated to `1e-12` vs a numpy finite-difference reference), the FIRE / L-BFGS minimizer, and the Bateman/Hopf + Trkalian (constant-λ) Beltrami seeders. Its first design decision, captured here, is **which substrate field** the lattice evolves (Open Question Q1).

---

## Define the substrate field (DECISION DEFERRED, see Open Question Q1)

The medium representation, in the M5 / M6 vocabulary (`M5 = 3×3 matrix`, `M6 = double vector field`). Candidates under consideration:

| Candidate | Field / point | Keeps Fleury (charge = ∇·) | Keeps Ouroboros (linking) | Knot-native | Note |
| --- | --- | --- | --- | --- | --- |
| **A. Riemann-Silberstein** `F = E + icB ∈ ℂ³` | 6 real | ✅ `∇·F` | ✅ helicity `∫A·B` | ✅ (Rañada / Bateman) | single complex field; clean but loses the explicit doublet |
| **B. Ouroboros doublet** `(A_μ, J_μ)` read via RS | 8 real | ✅ | ✅ native | ✅ via Bateman seed | reuses M6 substrate verbatim; current lean |
| C. Faddeev-Niemi `n : ℝ³→S²` | 3 real | ❌ divergence-free → **no charge** | ✅ Hopf charge | ✅✅ | breaks Fleury's central claim |
| D. Clebsch `(α,β)` / `ψ : ℝ³→ℂ` | 2 real | ❌ | partial | ✅✅ | useful as a **seed generator**, not the evolved DOF |

What any acceptable substrate must satisfy (the blend test):

| Requirement | Why it matters |
| --- | --- |
| Fleury's charge `= ∇·E` | the whole point of `2510.22384` vs divergence-free knots |
| Ouroboros charge `= ∫A·B` (linking) | the "snake eats tail" topological charge |
| The two charges are the **same object** (divergence + helicity of one field/pair) | this is the unification HydroBoros claims |
| Beltrami `∇×F = (ω/c) F` reproduces Fleury's `ω = 2c/R₀` | the force-free eigenstate = the steady vortex |
| M6 work carries over (`m_J`, `g`, `H/Q`) | do not re-derive what M6 already validated |
| Derrick stability via a 4th-order term | static stable soliton must exist (see [`../m7_background.md § 5`](../m7_background.md)) |

**A-primary ontology (Marc, committed 2026-06-30):** the work starts from an **"A primary"** ontology, the vector potential `A` is the fundamental field, with `F = dA`, the `E, B` fields and the charge `∇·E` all derived from it. This favors the potential-primary candidate **B** (the `A_μ` doublet, where `A` is literally the primary DoF) over the field-primary RS candidate **A**; the Riemann-Silberstein `F` reading is kept as a derived diagnostic, not the evolved DoF.

The decision between A and B (and whether D enters only as a seeder) is **open**, tracked as **Q1** in [`../m7_question_tracker.md`](../m7_question_tracker.md), the M5-style question tracker (cf. [`0b_question_tracker.md`](../../../m6_ouroboros/research/0b_question_tracker.md)); the open questions Q1-Q7 live there.

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (task M7.1, Phase A) · full background [`../m7_background.md`](../m7_background.md) (§ 5 dynamics + Derrick argument); open questions Q1/Q2 in [`../m7_question_tracker.md`](../m7_question_tracker.md) · M7.0 corpus [`m7_0_bootstrap.md`](m7_0_bootstrap.md).
