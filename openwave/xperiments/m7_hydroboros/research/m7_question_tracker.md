# M7 / HydroBoros, question tracker

**Purpose:** single source of truth for M7's open research questions, **grouped by the task that resolves each**. Mirrors the M5 / M6 tracker pattern, scaled to M7's start (7 open, 0 resolved). Update when a question opens, gets sent to the group (Marc / Duda / Werbos), gets answered, or gets demoted. The **hardest-pieces / risk board** is the second half.

**Sister docs:**

| Doc | Purpose |
| --- | --- |
| [`m7_roadmap.md`](m7_roadmap.md) | the task roadmap (M7.0-M7.14 + Phases D-E); where each question resolves |
| [`m7_background.md`](m7_background.md) | full implementation background: the two physics parents, the M5 method, the dynamics (§ 5) |
| `m7_theory_canonical.md` (planned) | the canonical build-spec, lands at the M7.7 milestone |
| [`tasks/`](tasks/) | per-task detail docs (`m7_N_*.md`) |

**Last updated:** 2026-07-02 (plan refactor after the full theory review, [`m7_background.md § 5`](m7_background.md): Q2 rewritten with direction set (helicity + confinement in, Faddeev-Niemi out); Q3/Q5/Q7 sharpened with the corpus math facts (rigidity, Nadirashvili, the divergence identity); **Q8 (gauge/constraints) + Q9 (Werbos-v5 calibration dictionary) opened**. Evening: **M7.1 gate suite ALL PASS** ([`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings): Q1 substrate built as B, Q2's Woltjer gate passed, Q8 gauge evidence measured).

---

## Active count

```text
9 OPEN  (0 resolved)
  substrate / infra    (M7.1):  Q1 🔶 built as B   Q2 🔶 Woltjer gate passed   Q8 🔶 evidence in
  potential + calibr.  (M7.3):  Q6 🚧   Q9 🚧
  charged soliton      (M7.4):  Q3 🔶   Q5 🔶   Q7 🔶
  sources              (M7.0):  Q4 🔶 partly in
```

Legend: 🔶 open, direction known / partial · 🚧 open, not yet started · ✅ resolved · ❌ closed negative.

---

## Open questions, by resolving task

### Substrate + infrastructure (resolves at M7.1)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q1** | **Substrate field:** the Ouroboros doublet `(A_μ, J_μ)` read as Riemann-Silberstein (candidate B) vs single-field RS `F = E + icB` (candidate A); does Clebsch/`ψ` (D) enter only as a knot **seeder**? what **target manifold** (Pisello S² vs Faber S³, see [`m7_background.md § 0`](m7_background.md))? | 🔶 OPEN: narrowed to **B** by Marc's **A-primary** commitment (`A` fundamental, `F = dA`, charge derived); RS kept as a derived diagnostic. **M7.1 built the substrate as B** (the 16-component harmonic doublet, [`scripts/m7_1_harmonic_lattice.py`](scripts/m7_1_harmonic_lattice.py) via [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md)); formal closure waits on M7.3/M7.4 confirming the doublet carries both charges |
| **Q2** | Stabilizer: is a 4th-order term needed at all, and in which form? | 🔶 OPEN, **direction set** (2026-07-02 theory review): the drafted `\|F×(∇×F)\|²/\|F\|²` term **vanishes identically on every Beltrami configuration** (`∇×F ∥ F` makes the cross product zero, constant AND variable λ; rescaled Beltrami stays Beltrami) and is **singular** where `\|F\| → 0`, so it provides zero Derrick pressure on exactly the target family. Working stabilization = **helicity anti-collapse** (Arnold `E ≥ λ₁\|H\|`) + **Ouroboros confinement anti-expansion** (`~μ³`), with **Nadirashvili's theorem** forcing the confinement term to exist ([`m7_background.md § 5b`](m7_background.md)). 4th-order term demoted to an optional M7.4 experiment, **off by default**. Empirical confirmation: the M7.1 Woltjer gate (✅ passed 2026-07-02: fixed-helicity relaxation from random seeds lands on the constant-λ eigenfield, `λ → 2π/L` at 5.5e-6, [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings) + the M7.4 dilation probe |
| **Q8** | **Gauge / constraint handling** for the A-primary minimizer: gauge orbits of `A` are flat directions; `m_J² A·J` is gauge-sensitive off-shell (`∂·J ≠ 0` configs); options: Coulomb gauge on `a⃗` + kept `a₀` / projection / penalty | 🔶 OPEN, **measured evidence in** (M7.1 gate G5, [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings): `E_ω` is **exactly gauge-invariant at `m_J = 0`** (machine zero, the Maxwell structure verified) and broken by `m_J²A·J` off-shell (`ΔE/E ≈ 1.3e-3` on random fields); the **static curl sector self-fixes** (transverse AD gradient, discrete div∘curl = 0; the Woltjer relaxation converged gauge-drift-free from random seeds). Scheme decision (Coulomb-on-`a⃗` / projection / penalty) deferred to the **first coupled relaxation (M7.3)**; M6's ansatz has `A₀ ≠ 0` (Weyl gauge incompatible) |

### Potential form + calibration (resolves at M7.3)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q6** | The `f(J·J)` potential form for M7: keep M6's `(g/4) s²`, or a form better suited to the toroidal sector? | 🚧 OPEN: revisit at M7.3 |
| **Q9** | **Werbos-v5 calibration dictionary**: v5's canonical point is `g = 1.0625` (`H/Q = 1.6969`) vs M6's repo-validated canonical `g = 1.0` (`H/Q = 1.6890`), vs physical `1.6875`; and v5's new `(Ω, G)` bifurcation islands (electron `Ω = 1.050` stable `k > 0`; muon `Ω = 0.914` resonant `k < 0`) need the `(Ω, G) ↔ (ω, g, m_J)` map (Zenodo 20866581) | 🚧 OPEN: ask Werbos / read the Zenodo record; until resolved **M7.3 uses the M6 calibration as primary** (ledger in [`m7_background.md § 4`](m7_background.md)); the islands become an M7.12 falsifiable structure (stable electron vs resonant muon) |

### The charged soliton (resolves at M7.4)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q3** | Are Fleury's divergence charge and Ouroboros's helicity/linking charge **forced equal**, or independent observables that must be reconciled? | 🔶 OPEN: **Pisello's toroidal knot** ([`m7_background.md § 0`](m7_background.md), corpus #16) is a published precedent that **unifies** them (charge quantized ∝ homotopy class AND non-homogeneous / divergence); the conceptual core of the blend. **2nd unification route** ([M7.0 corpus](tasks/m7_0_bootstrap.md) #22, Duda deck pp. 467-491): charge = topological **mapping degree** → **Gauss-Bonnet** `∮ K dS = 2π χ(S)` → **Faber's quantized-EM**; arrives from mapping-degree where Pisello arrives from the electrovacuum Lagrangian, the two **converging** on divergence-charge = topological-charge. **The Q3 experiment is now a first-class M7.4 deliverable**: measure `(Q_div, helicity H, linking)` on every relaxed state and report the ratio analysis ([`tasks/m7_4_charged_soliton.md`](tasks/m7_4_charged_soliton.md)) |
| **Q5** | Does a **divergence-ful** field still admit clean, stable knots, or does non-zero `∇·F` destabilize the Hopfion? | 🔶 OPEN, sharpened by the corpus math ([`m7_background.md § 2`](m7_background.md)): **exact** variable-λ Beltrami knots are heavily obstructed (rigidity: Clelland-Klotz 2020) and finite-energy exact Beltrami fields don't exist at all (Nadirashvili), so the question is properly about the **relaxed minimizer of the full functional** (approximately Beltrami, charge = the coupling-driven deviation). **Pisello** answers YES in principle (a charged toroidal Hopf-knot exists, corpus #16); Kaiser 2000 gives perturbative small-charge existence; M5.11's P2 warns that smooth knots **expand** without confinement (M7 has the confinement term M5's functional lacked). M7.4 answers on the lattice, honest pass / fail |
| **Q7** | The **charge-carrying construction**: start from exact Trkalian (constant-λ) solutions (S&Y, ABC) and introduce charge; what carries `∇·F ≠ 0` and how does it evolve? | 🔶 OPEN, **reframed 2026-07-02**: the divergence identity `∇·w = −(w·∇λ)/λ` says charge needs λ varying **along** field lines, exactly the regime rigidity obstructs, so M7.4 does **not** hunt an exact `λ(x)` ansatz; it relaxes the full functional from Trkalian seeds (+ a λ-perturbation) and **measures** the deviation via `λ_eff = F·(∇×F)/\|F\|²`. Marc's endorsement (2026-06-30, "start Trkalian, take off the training wheels") survives intact, implemented as relax-and-measure rather than construct-exactly; the core of M7.4 |

### Sources (M7.0, ongoing)

| ID | Question | Status / current read |
| --- | --- | --- |
| **Q4** | Beltrami / ABC source papers + further material from Marc | 🔶 PARTLY IN: Sato-Yamada landed (arXiv:1809.03136 + note in `theory/`, [M7.0 corpus](tasks/m7_0_bootstrap.md) #11); more Marc material expected (corpus #13) |

---

## Ask Marc Fleury (queued for the next contact)

The open questions double as the ask-list for Marc (added 2026-07-02 at the M7.1 review). When we connect, these are the concrete asks, each tied to its tracker entry; the agent supplies the factual content, Rodrigo phrases the outbound message.

| Ask | What we need from Marc | Tracker ref |
| --- | --- | --- |
| **S&Y eikonal recipe, variable-h** | the concrete construction steps for a **toroidal variable-`h`** Beltrami seed from Sato-Yamada's eikonal + equal-scale-factor method (M7.1 filled the seeder slot with the constant-λ CK spheromak; the variable-h construction is exactly what M7.4's charge sector wants) | Q7 · [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings (G4) |
| **The relax-and-measure reframe** | confirm the M7.4 reading of his "start Trkalian, take off the training wheels" (2026-06-30): rigidity (Clelland-Klotz) + Nadirashvili force relax-and-**measure** (`λ_eff` diagnostic) instead of hunting an exact `λ(x)` ansatz; does that match his intent, and does he know results beyond Kaiser 2000 on variable-α existence? | Q7 · Q5 · [`m7_background.md § 2`](m7_background.md) |
| **FLDB energy convention (M7.2 trap #3)** | which complex-field energy convention Eq 31/32 of the paper uses (the appendix is the source; if ambiguous we compute both and report which matches), needed before the `U/m_ec² ≈ 0.795` comparison is trusted | [`tasks/m7_2_fleury_torus.md § 2`](tasks/m7_2_fleury_torus.md) |
| **Target manifold, S² vs S³** | his read on the Pisello (S²) vs Faber (S³) target-space choice for the substrate; bears directly on what the doublet maps into | Q1 · [`m7_background.md § 2`](m7_background.md) |
| **The promised Beltrami material** | the further source papers he mentioned (corpus #13) + the status of bringing in the Spanish school (Enciso & Peralta-Salas) as collaborators | Q4 |
| **Divergence-ful knots** | his position on whether nonzero `∇·F` destabilizes the knot (Pisello says a charged toroidal Hopf-knot exists; M5.11's P2 measured smooth knots expanding without confinement) | Q5 · Q3 |

---

## Risks / unknowns (the hardest pieces)

The accepted risks + open unknowns, each with its mitigation. Promote a row here to a numbered question (above) once it becomes a decision the build must make.

| Risk | Status / mitigation |
| --- | --- |
| The time-harmonic reduction goes subtly wrong (M6 needed ten sandbox versions to pin its 1D reduction: signs, regularity classes, Laplacians, measures) | the **M7.3 verbatim-ODE pre-gate**: the 3D functional restricted to M6's ansatz must reproduce the `(α,β)` ODE term by term BEFORE any relaxation run is trusted ([`0d_canonical.md § 6`](../../m6_ouroboros/research/0d_canonical.md) is the cautionary record) |
| The 1D chaoiton may be **unstable to 3D symmetry breaking** (1D radial solutions often are) | an honest result either way; M7.3 relaxes with and without the symmetry constraint and reports the drift |
| Gauge flat directions stall or misdirect the minimizer (Q8) | measured at M7.1 (G5): the curl sector self-fixes, only the `m_J²A·J`-coupled sector is exposed; scheme decision at the first coupled relaxation (M7.3) |
| Confinement-term sign: `m_J² A·J` is not positive-definite, the anti-expansion balance is only empirically established (M6 1D) | the M7.4 **dilation probe** (`E(μ)` along rescalings) verifies the interior minimum directly; honest pass / fail |
| Variable-λ Beltrami math "gets very hairy" (Marc), now sharpened: **rigidity obstructs exact nonconstant-λ solutions even locally** | M7.4 reframed to relax-and-measure (Q7): Trkalian seeds + full-functional relaxation, charge measured as the deviation, never imposed |
| Does the divergence-ful field admit clean knots (Q5) | the open research question; honest pass / fail at M7.4; M5.11's P2 (smooth knots expand) is the cautionary datum, the confinement term is the mitigation |
| Whole-program cost: 3D harmonic relaxations are multi-hour GPU runs | accepted; same regime as M5.11's vortex-loop relaxation |
| **Marc's AI-exchange material hallucinates** (his own warning: 2 months / 3 AIs, output not great) | treat it as **seeds only**, never as validated input; every claim re-derived in-platform (the MODELS.md reproducibility bar). A marathon-session review for extractable signal is optional, low priority |
| Masses (M7.6) may stay in tension with data | report honestly, including partial, as M5.11 did |

---

Cross-refs: roadmap [`m7_roadmap.md`](m7_roadmap.md) · background [`m7_background.md`](m7_background.md) (§ 5 dynamics + Derrick argument) · the M5 / M6 trackers this mirrors: [`m5_question_tracker.md`](../../m5_liquid_crystal/research/m5_question_tracker.md) (M5) · [`0b_question_tracker.md`](../../m6_ouroboros/research/0b_question_tracker.md) (M6).
