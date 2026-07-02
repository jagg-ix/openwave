# M7 / HydroBoros, question tracker + hardest pieces

**Purpose:** single source of truth for (a) M7's open research questions (the REGISTRY: every question carries a stable ID, `Qn`, never renumbered), (b) the resolution chronology, and (c) the long-running **hardest-pieces** board. Mirrors the [M5 tracker pattern](../../m5_liquid_crystal/research/m5_question_tracker.md). Update this doc when a question opens, gets sent to a collaborator, gets answered, demoted, or resolved. **The [`§ OPEN QUESTIONS`](#open-questions) table IS the ask list**: it is sorted by priority (row order = most critical first = the order to raise them), and the primary audience is **Marc Fleury** at the next contact (Werbos for the M6-calibration items, tagged in the count block). Per the comms rule, this file supplies the factual content; Rodrigo phrases every outbound message.

**Sister docs:**

| Doc | Purpose |
| --- | --- |
| [`m7_roadmap.md`](m7_roadmap.md) | the task roadmap (M7.0-M7.16); where each question resolves |
| [`m7_background.md`](m7_background.md) | full implementation background: the two physics parents, the M5 method, the dynamics (§ 5) |
| `m7_theory_canonical.md` (planned) | the canonical build-spec, lands at the M7.7 milestone |
| [`tasks/`](tasks/) | per-task detail docs (`m7_N_*.md`) |
| [`../../m5_liquid_crystal/research/m5_question_tracker.md`](../../m5_liquid_crystal/research/m5_question_tracker.md) | the M5 tracker this one mirrors (structure + procedure) |
| [`../../m6_ouroboros/research/0b_question_tracker.md`](../../m6_ouroboros/research/0b_question_tracker.md) | the M6 tracker (the other parent's registry) |

**Last updated:** 2026-07-02 late evening (**restructured to the M5 tracker pattern** at Rodrigo's direction: ONE priority-sorted OPEN QUESTIONS table = the ask list for Marc (the separate "Ask Marc" section is folded in), per-ID details moved to [`§ QUESTION DETAILS`](#question-details-open-questions), **Q10 opened** (the FLDB energy convention, previously an ID-less ask; it gates the now-IN-PROGRESS M7.2)). Earlier same day: plan refactor after the full theory review (Q2 direction set, Q3/Q5/Q7 sharpened, Q8 + Q9 opened); evening: **M7.1 gate suite ALL PASS** ([`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings: Q1 substrate built as B, Q2's Woltjer gate passed, Q8 gauge evidence measured).

---

## Active Questions Count

```text
6 ASK MARC     (next contact; list order = priority = the table order)
                 Q7   variable-lambda construction: relax-and-measure reframe
                      + the S&Y eikonal variable-h toroidal recipe
                 Q5   divergence-ful knots: stable, or does div F kill them?
                 Q3   divergence charge vs linking charge: forced equal?
                 Q10  FLDB complex-field energy convention (Eq 31/32)
                      [NON-blocking for the in-progress M7.2: the plan
                      computes both conventions; the answer picks the
                      canonical column]
                 Q1   substrate reading + target manifold (S2 vs S3)
                 Q4   the promised Beltrami material + the Spanish school

2 ASK WERBOS   Q9   (Omega, G) <-> (omega, g, m_J) calibration dictionary
               Q6   f(J.J) potential form for the toroidal sector

2 SELF-        Q8   gauge/constraint scheme (evidence measured at M7.1;
DETERMINE           decide at the first coupled relaxation, M7.3)
               Q2   4th-order stabilizer (direction set; optional M7.4
                    experiment, off by default)

0 RESOLVED

Total: 10 questions (6 ask-Marc, 2 ask-Werbos, 2 self-determine).
```

Legend: 🔶 open, direction known / partial · 🚧 open, not yet started · ✅ resolved · ❌ closed negative.

---

## OPEN QUESTIONS

> Sorted by priority: most critical first; **row order = the order to raise them with Marc**. Full statement + provenance + history + evidence per question: [`§ QUESTION DETAILS`](#question-details-open-questions) (one anchor per ID).

| ID | Title | Question (one line) | Gates |
| --- | --- | --- | --- |
| [Q7](#q7-detail) 🔶 | Charge-carrying construction | Does the relax-and-measure implementation (charge = the measured `∇·F` deviation, `λ_eff` diagnostic) match Marc's "Trkalian first, then take off the training wheels", and is there a concrete S&Y eikonal recipe for a **variable-h toroidal** seed? | M7.4 (the research core) |
| [Q5](#q5-detail) 🔶 | Divergence-ful knots | Does a divergence-ful field still admit clean, stable knots, or does nonzero `∇·F` destabilize the Hopfion? | M7.4 pass/fail |
| [Q3](#q3-detail) 🔶 | The two charges | Are Fleury's divergence charge and Ouroboros's helicity/linking charge **forced equal**, or independent observables to reconcile? | M7.4 (the `(Q_div, H, linking)` deliverable) |
| [Q10](#q10-detail) 🚧 | FLDB energy convention | Which complex-field energy convention do FLDB Eqs 31/32 use (the appendix form), needed to pick the canonical `U/m_ec² ≈ 0.795` comparison column? | M7.2 § 3 `U` target only, **non-blocking** (dual-convention fallback baked into the plan) |
| [Q1](#q1-detail) 🔶 | Substrate + target manifold | The `(A_μ, J_μ)` doublet (candidate B, built at M7.1) vs single RS field (A); Clebsch as seeder only (D); and the target manifold: Pisello S² vs Faber S³? | M7.3/M7.4 closure |
| [Q4](#q4-detail) 🔶 | Marc's source material | The further Beltrami papers he mentioned (corpus #13) + the status of bringing in Enciso & Peralta-Salas as collaborators? | corpus (M7.0, ongoing) |
| [Q9](#q9-detail) 🚧 | Werbos-v5 calibration dictionary | The `(Ω, G) ↔ (ω, g, m_J)` map between v5's canonical point (`g = 1.0625`, `H/Q = 1.6969`) and M6's repo-validated canonical (`g = 1.0`, `H/Q = 1.6890`)? | M7.3 secondary gate · M7.12 islands |
| [Q6](#q6-detail) 🚧 | Potential form | Keep M6's `f(s) = (g/4) s²` for the toroidal sector, or a better-suited form? | M7.3 |
| [Q8](#q8-detail) 🔶 | Gauge / constraints | Which scheme for the coupled minimizer: Coulomb gauge on `a⃗` + kept `a₀`, projection, or penalty? (evidence measured at M7.1) | M7.3 (first coupled relaxation) |
| [Q2](#q2-detail) 🔶 | 4th-order stabilizer | Is any 4th-order term needed at all, and in which non-inert form? (helicity + confinement is the working stabilization) | M7.4 optional experiment (off by default) |

---

## RESOLVED QUESTIONS

| ID | Question | Resolution |
| --- | --- | --- |
| , | none yet | , |

---

## HARDEST PIECES, status board (risks / unknowns)

The long-running load-bearing unknowns, distinct from the discrete Q-numbered questions above (a piece can persist across many tasks). Promote a row to a numbered question once it becomes a decision the build must make.

| Hardest piece | Status / mitigation |
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

## Notes on scope

- This tracker covers **M7 physics/framework questions for the collaborators** (Marc Fleury primary; Paul Werbos for the M6-calibration items) plus the hardest-pieces board. Implementation decisions (lattice layout, kernel design, minimizer settings) are tracked as roadmap tasks in [`m7_roadmap.md`](m7_roadmap.md) and the per-task docs, not here: the same split as M5/M6.
- **Outbound comms:** the [`§ OPEN QUESTIONS`](#open-questions) table order = the ask order at the next Marc contact; the [`§ QUESTION DETAILS`](#question-details-open-questions) entries carry the content bullets for each ask. The agent supplies facts; **Rodrigo phrases every outbound message** (his voice is the credential).

---

## QUESTION DETAILS (open questions)

> The lean [`§ OPEN QUESTIONS`](#open-questions) table links here (one anchor per ID). This section carries each question's full statement, provenance, history, and evidence, plus the concrete ask where the question is outbound.

### Q7 detail

**Charge-carrying construction (ask Marc, priority 1).** What carries `∇·F ≠ 0` when the Trkalian training wheels come off, and how does it evolve? **Reframed 2026-07-02**: the divergence identity `∇·w = −(w·∇λ)/λ` says charge needs λ varying **along** field lines, exactly the regime rigidity obstructs (Clelland-Klotz 2020, even locally), so M7.4 does **not** hunt an exact `λ(x)` ansatz; it relaxes the full functional from Trkalian seeds (+ a λ-perturbation) and **measures** the deviation via `λ_eff = F·(∇×F)/\|F\|²` ([`tasks/m7_4_charged_soliton.md`](tasks/m7_4_charged_soliton.md)). Marc's endorsement (2026-06-30, "start Trkalian, take off the training wheels") survives intact, implemented as relax-and-measure rather than construct-exactly. **The asks:** (a) confirm the reframe matches his intent, and whether he knows results beyond Kaiser 2000 on variable-α existence; (b) the concrete construction steps for a **toroidal variable-h** Beltrami seed from Sato-Yamada's eikonal + equal-scale-factor method (M7.1 filled the seeder slot with the constant-λ CK spheromak, [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings G4; the variable-h construction is exactly what M7.4's charge sector wants).

### Q5 detail

**Divergence-ful knots (ask Marc, priority 2).** Does a divergence-ful field still admit clean, stable knots, or does nonzero `∇·F` destabilize the Hopfion? Sharpened by the corpus math ([`m7_background.md § 2`](m7_background.md)): **exact** variable-λ Beltrami knots are heavily obstructed (rigidity) and finite-energy exact Beltrami fields don't exist at all (Nadirashvili), so the question is properly about the **relaxed minimizer of the full functional** (approximately Beltrami, charge = the coupling-driven deviation). **Pisello** answers YES in principle (a charged toroidal Hopf-knot exists, corpus #16); Kaiser 2000 gives perturbative small-charge existence; M5.11's P2 warns that smooth knots **expand** without confinement (M7 has the confinement term M5's functional lacked). M7.4 answers on the lattice, honest pass / fail. **The ask:** his position on whether `∇·F ≠ 0` destabilizes the knot, given the Pisello precedent and the M5.11 P2 datum.

### Q3 detail

**The two charges (ask Marc, priority 3).** Are Fleury's divergence charge and Ouroboros's helicity/linking charge **forced equal**, or independent observables that must be reconciled? **Pisello's toroidal knot** ([`m7_background.md § 2`](m7_background.md), corpus #16) is a published precedent that **unifies** them (charge quantized ∝ homotopy class AND non-homogeneous / divergence); the conceptual core of the blend. **2nd unification route** ([M7.0 corpus](tasks/m7_0_bootstrap.md) #22, Duda deck pp. 467-491): charge = topological **mapping degree** → **Gauss-Bonnet** `∮ K dS = 2π χ(S)` → **Faber's quantized-EM**; arrives from mapping-degree where Pisello arrives from the electrovacuum Lagrangian, the two **converging** on divergence-charge = topological-charge. **The Q3 experiment is a first-class M7.4 deliverable**: measure `(Q_div, helicity H, linking)` on every relaxed state and report the ratio analysis ([`tasks/m7_4_charged_soliton.md`](tasks/m7_4_charged_soliton.md)).

### Q10 detail

**FLDB complex-field energy convention (ask Marc, priority 4; time-sensitive).** Which convention does the paper's energy density `u(t) = ε₀E₀²(1 + R/4R₀)` (Eq 31) and the rest-energy integral (Eq 32) use for complex fields: real-part-instantaneous, or complex-modulus average? The appendix (FLDB Appendix, corpus #1) is the source; the M7.2 conventions contract carries it as trap #3 ([`tasks/m7_2_fleury_torus.md § 2`](tasks/m7_2_fleury_torus.md)), and the `U/m_ec² ≈ 0.795` target comparison is not trusted until it is pinned. Opened 2026-07-02 (previously an ID-less ask at the M7.1 review; assigned an ID at the tracker restructure). **NON-blocking for M7.2** (decision 2026-07-02: M7.2 runs without waiting for Marc): the plan computes BOTH conventions (real-part-instantaneous and complex-modulus average) and reports which matches Eq 32; only the `U/m_ec²` target is convention-sensitive, the other seven targets (charge, radii, ω, μ, spin, `∇·J` consistency) are not. Marc's answer later picks the canonical column; he is the author, so it is the cheapest possible ask.

### Q1 detail

**Substrate + target manifold (ask Marc, priority 5).** The Ouroboros doublet `(A_μ, J_μ)` read via Riemann-Silberstein (candidate B) vs single-field RS `F = E + icB` (candidate A); does Clebsch/`ψ` (D) enter only as a knot **seeder**? And what **target manifold**: Pisello S² vs Faber S³ ([`m7_background.md § 2`](m7_background.md))? Narrowed to **B** by Marc's **A-primary** commitment (`A` fundamental, `F = dA`, charge derived); RS kept as a derived diagnostic. **M7.1 built the substrate as B** (the 16-component harmonic doublet, [`scripts/m7_1_harmonic_lattice.py`](scripts/m7_1_harmonic_lattice.py) via [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md)); a structural argument now also favors B: Nadirashvili's theorem makes the pure-Maxwell finite-energy Beltrami electron impossible, so the doublet's confinement sector is required for existence ([`m7_background.md § 5b`](m7_background.md)). Formal closure waits on M7.3/M7.4 confirming the doublet carries both charges. **The ask:** his read on the S²-vs-S³ target-space choice.

### Q4 detail

**Marc's source material (ask Marc, priority 6; logistics).** The Beltrami / ABC source papers and further material from Marc. PARTLY IN: Sato-Yamada landed (arXiv:1809.03136 + the note in [`../theory/sato_yamada_beltrami.md`](../theory/sato_yamada_beltrami.md), [M7.0 corpus](tasks/m7_0_bootstrap.md) #11); more material expected (corpus #13). **The asks:** the further papers he mentioned, and the status of bringing in the Spanish Beltrami school (Enciso & Peralta-Salas, corpus #6) as collaborators.

### Q9 detail

**Werbos-v5 calibration dictionary (ask Werbos).** v5's canonical point is `g = 1.0625` (`H/Q = 1.6969`) vs M6's repo-validated canonical `g = 1.0` (`H/Q = 1.6890`), vs physical `1.6875`; and v5's new `(Ω, G)` bifurcation islands (electron `Ω = 1.050` stable `k > 0`; muon `Ω = 0.914` resonant `k < 0`) need the `(Ω, G) ↔ (ω, g, m_J)` map (Zenodo 20866581, the 319-family scan). Route: ask Werbos and/or read the Zenodo record. Until resolved, **M7.3 uses the M6 calibration as primary** (ledger in [`m7_background.md § 4`](m7_background.md)); the islands become an M7.12 falsifiable structure (stable electron vs resonant/metastable muon). Opened 2026-07-02 (plan refactor).

### Q6 detail

**Potential form (ask Werbos / self-determine at M7.3).** The `f(J·J)` potential form for M7: keep M6's canonical `f(s) = (g/4) s²` ([`0d_canonical.md § 1`](../../m6_ouroboros/research/0d_canonical.md)), or a form better suited to the toroidal sector? Not yet started; revisit at M7.3 where the 3D chaoiton first tests the M6 form outside its 1D reduction.

### Q8 detail

**Gauge / constraint handling (self-determine, decide at M7.3).** Gauge orbits of `A` are flat directions of the minimizer; `m_J² A·J` is gauge-sensitive off-shell (`∂·J ≠ 0` configs); candidate schemes: Coulomb gauge on `a⃗` + kept `a₀`, projection, penalty. **Measured evidence in** (M7.1 gate G5, [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings): `E_ω` is **exactly gauge-invariant at `m_J = 0`** (machine zero, the Maxwell structure verified) and broken by `m_J²A·J` off-shell (`ΔE/E ≈ 1.3e-3` on random fields); the **static curl sector self-fixes** (transverse AD gradient, discrete div∘curl = 0; the Woltjer relaxation converged gauge-drift-free from random seeds). Scheme decision deferred to the **first coupled relaxation (M7.3)**. Note: M6's ansatz has `A₀ ≠ 0` (Weyl gauge incompatible). Opened 2026-07-02 (plan refactor).

### Q2 detail

**4th-order stabilizer (self-determine; optional M7.4 experiment).** Is a 4th-order term needed at all, and in which form? **Direction set** (2026-07-02 theory review): the drafted `\|F×(∇×F)\|²/\|F\|²` term **vanishes identically on every Beltrami configuration** (`∇×F ∥ F` makes the cross product zero, constant AND variable λ; rescaled Beltrami stays Beltrami) and is **singular** where `\|F\| → 0`, so it provides zero Derrick pressure on exactly the target family. Working stabilization = **helicity anti-collapse** (Arnold `E ≥ λ₁\|H\|`) + **Ouroboros confinement anti-expansion** (`~μ³`), with **Nadirashvili's theorem** forcing the confinement term to exist ([`m7_background.md § 5b`](m7_background.md)). The 4th-order term is demoted to an optional M7.4 experiment, **off by default** (any run uses a regularized variant, labeled an experiment). Empirical confirmation so far: the M7.1 Woltjer gate ✅ (2026-07-02: fixed-helicity relaxation from random seeds lands on the constant-λ eigenfield, `λ → 2π/L` at 5.5e-6, [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings); next: the M7.4 dilation probe.

---

Cross-refs: roadmap [`m7_roadmap.md`](m7_roadmap.md) · background [`m7_background.md`](m7_background.md) (§ 2 math boundaries, § 5 dynamics) · task docs [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) (Q1/Q2/Q8 evidence) · [`tasks/m7_2_fleury_torus.md`](tasks/m7_2_fleury_torus.md) (Q10) · [`tasks/m7_3_ouroboros_3d.md`](tasks/m7_3_ouroboros_3d.md) (Q6/Q9) · [`tasks/m7_4_charged_soliton.md`](tasks/m7_4_charged_soliton.md) (Q3/Q5/Q7) · the M5 / M6 trackers this mirrors: [`m5_question_tracker.md`](../../m5_liquid_crystal/research/m5_question_tracker.md) (M5) · [`0b_question_tracker.md`](../../m6_ouroboros/research/0b_question_tracker.md) (M6).
