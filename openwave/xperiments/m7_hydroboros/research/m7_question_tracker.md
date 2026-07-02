# M7 / HydroBoros, question tracker

**Purpose:** single source of truth for M7's open research questions, **grouped by the task that resolves each**. Mirrors the M5 / M6 tracker pattern, scaled to M7's start (7 open, 0 resolved). Update when a question opens, gets sent to the group (Marc / Duda / Werbos), gets answered, or gets demoted. The **hardest-pieces / risk board** is the second half.

**Sister docs:**

| Doc | Purpose |
| --- | --- |
| [`m7_roadmap.md`](m7_roadmap.md) | the task roadmap (M7.0-M7.14 + Phases D-E); where each question resolves |
| [`m7_background.md`](m7_background.md) | full implementation background: the two physics parents, the M5 method, the dynamics (§ 5) |
| `m7_theory_canonical.md` (planned) | the canonical build-spec, lands at the M7.7 milestone |
| [`tasks/`](tasks/) | per-task detail docs (`m7_N_*.md`) |

**Last updated:** 2026-07-01 (migrated the open-questions + risk boards out of the implementation plan into this dedicated tracker; regrouped Q1-Q7 by resolving task; Q1 narrowed to candidate **B** by Marc's A-primary commitment).

---

## Active count

```text
7 OPEN  (0 resolved)
  substrate / infra (M7.1):  Q1 🔶 narrowed to B   Q2 🚧
  potential form    (M7.3):  Q6 🚧
  charged soliton   (M7.4):  Q3 🔶   Q5 🔶   Q7 🔶
  sources           (M7.0):  Q4 🔶 partly in
```

Legend: 🔶 open, direction known / partial · 🚧 open, not yet started · ✅ resolved · ❌ closed negative.

---

## Open questions, by resolving task

### Substrate + infrastructure (resolves at M7.1)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q1** | **Substrate field:** the Ouroboros doublet `(A_μ, J_μ)` read as Riemann-Silberstein (candidate B) vs single-field RS `F = E + icB` (candidate A); does Clebsch/`ψ` (D) enter only as a knot **seeder**? what **target manifold** (Pisello S² vs Faber S³, see [`m7_background.md § 0`](m7_background.md))? | 🔶 OPEN: narrowed to **B** by Marc's **A-primary** commitment (`A` fundamental, `F = dA`, charge derived); RS kept as a derived diagnostic; confirm at M7.1 |
| **Q2** | Exact 4th-order stabilizer form: Faddeev-Niemi `\|F×(∇×F)\|²/\|F\|²` vs a Skyrme-Faddeev variant; coefficient `κ` scale | 🚧 OPEN: settle empirically at M7.1 / M7.4 |

### Potential form (resolves at M7.3)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q6** | The `f(J·J)` potential form for M7: keep M6's `(g/4) s²`, or a form better suited to the toroidal sector? | 🚧 OPEN: revisit at M7.3 |

### The charged soliton (resolves at M7.4)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q3** | Are Fleury's divergence charge and Ouroboros's helicity/linking charge **forced equal**, or independent observables that must be reconciled? | 🔶 OPEN: **Pisello's toroidal knot** ([`m7_background.md § 0`](m7_background.md), corpus #16) is a published precedent that **unifies** them (charge quantized ∝ homotopy class AND non-homogeneous / divergence); the conceptual core of the blend |
| **Q5** | Does a **variable-λ (divergence-ful)** Beltrami field still admit clean, stable knots, or does non-zero `∇·F` destabilize the Hopfion? | 🔶 OPEN: **Pisello** answers YES in principle (a charged toroidal Hopf-knot exists, corpus #16); M7.4 must reproduce it on the lattice |
| **Q7** | The **charge-carrying ansatz**: start from exact Trkalian (constant-λ) solutions (S&Y) and **generalize to variable-λ** to introduce `∇·F` = charge; what is the right `λ(x)` profile + how does it evolve? | 🔶 OPEN: **approach endorsed by Marc** (2026-06-30, "the way to build it"); the specific `λ(x)` profile is the open part; the core of M7.4 |

### Sources (M7.0, ongoing)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q4** | Beltrami / ABC source papers + further material from Marc | 🔶 PARTLY IN: Sato-Yamada landed (arXiv:1809.03136 + note in `theory/`, [M7.0 corpus](tasks/m7_0_bootstrap.md) #11); more Marc material expected (corpus #13) |

---

## Risks / unknowns (the hardest pieces)

The accepted risks + open unknowns, each with its mitigation. Promote a row here to a numbered question (above) once it becomes a decision the build must make.

| Risk | Status / mitigation |
| --- | --- |
| 4th-order term cost on a 3D lattice (multi-hour GPU runs) | accepted; same regime as M5.11's vortex-loop relaxation |
| Complex-field / gauge constraints (`∇·B = 0`, RS reality) | constrained integrator + projection, as M5 does for the tensor |
| Variable-λ Beltrami math "gets very hairy" (Marc) | start from exact Trkalian (constant-λ) cases (S&Y), generalize incrementally (Q7); do not jump straight to the charged case |
| Does the variable-λ (divergence-ful) field admit clean knots (Q5) | the open research question; honest pass / fail at M7.4 |
| **Marc's AI-exchange material hallucinates** (his own warning: 2 months / 3 AIs, output not great) | treat it as **seeds only**, never as validated input; every claim re-derived in-platform (the MODELS.md reproducibility bar). A marathon-session review for extractable signal is optional, low priority |
| Masses (M7.6) may stay in tension with data | report honestly, including partial, as M5.11 did |

---

Cross-refs: roadmap [`m7_roadmap.md`](m7_roadmap.md) · background [`m7_background.md`](m7_background.md) (§ 5 dynamics + Derrick argument) · the M5 / M6 trackers this mirrors: [`m5_question_tracker.md`](../../m5_liquid_crystal/research/m5_question_tracker.md) (M5) · [`0b_question_tracker.md`](../../m6_ouroboros/research/0b_question_tracker.md) (M6).
