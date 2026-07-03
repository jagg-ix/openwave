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

**Last updated:** 2026-07-03 (**M7.3 delivered**, [`tasks/m7_3_ouroboros_3d.md`](tasks/m7_3_ouroboros_3d.md) § FINDINGS: the verbatim-ODE pre-gate PASSED with convention pins (same-phase azimuthal doublet; coupling `−A·J`; FOCUSING `f`), the 3D lattice reproduces the M6 ledger to 4.7e-5, and three honest discoveries landed: **Q11 opened** (the charged `H/Q = 1.6890` is a WINDOWED quantity, no decaying channel exists at the canonical point), **Q12 opened** (`0d_canonical § 2.2`'s `2ωα` form is not an EL reduction; LoE 9b § 5.1's cos/sin phases decouple), **Q13 opened** (the M6 electron is a 3D constrained SADDLE ending in focusing collapse; helicity guard inert on it); **Q8 RESOLVED** (no gauge fixing needed; the real correction was objective-level: fixed-`Q_can` extremization of `E_ω`, multiplier ω). Q6 gained decisive evidence (the operative `f` is focusing with a λ-term, not the written `(g/4)s²`). Earlier (2026-07-02 night): **M7.2 quadrature delivered**: all reproduction gates pass at O(h²·⁵)/1.4e-4; printed solution reconstructed digit-for-digit; **Q10 evidence in** (Eq 122/124/127 slips, corrected `U ≈ 0.958 m_ec²`, [`tasks/m7_2_fleury_torus.md § 3`](tasks/m7_2_fleury_torus.md)); the Bessel stretch exposed the mask's hidden surface charge. Earlier: restructured to the M5 tracker pattern (ONE priority-sorted OPEN QUESTIONS table = the ask list, Q10 opened); plan refactor (Q2 direction set, Q3/Q5/Q7 sharpened, Q8 + Q9 opened); **M7.1 gate suite ALL PASS** ([`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings).

---

## Active Questions Count

```text
6 ASK MARC     (next contact; list order = priority = the table order)
                 Q7   variable-lambda construction: relax-and-measure reframe
                      + the S&Y eikonal variable-h toroidal recipe
                 Q5   divergence-ful knots: stable, or does div F kill them?
                 Q3   divergence charge vs linking charge: forced equal?
                 Q10  FLDB energy convention: M7.2 delivered the evidence
                      (Eq 122/124/127 slips identified; corrected
                      U = 0.958 m_ec^2); ask = Marc's confirmation
                 Q1   substrate reading + target manifold (S2 vs S3)
                 Q4   the promised Beltrami material + the Spanish school

5 ASK WERBOS   Q11  the charged H/Q = 1.6890 is a WINDOWED quantity (M7.3:
                    no decaying channel at the canonical point; Q grows
                    with r_max) - is the calibration window-defined?
               Q13  the M6 electron is a 3D constrained SADDLE (focusing
                    collapse); is the conjugate-point stability claim
                    1D-radial-manifold only?
               Q12  ODE provenance: 0d_canonical 2.2's "2 omega alpha" form
                    is not an EL reduction; LoE 9b 5.1's cos/sin phases
                    decouple - which ansatz/ODE is intended?
               Q9   (Omega, G) <-> (omega, g, m_J) calibration dictionary
               Q6   f(J.J) potential form (M7.3 evidence: the operative f is
                    FOCUSING with a lambda-term, not the written (g/4)s^2)

1 SELF-        Q2   4th-order stabilizer (direction set; optional M7.4
DETERMINE           experiment, off by default)

1 RESOLVED     Q8   gauge/constraint scheme (M7.3: no gauge fixing; the real
                    fix was the objective: fixed-Q_can extremization)

Total: 13 questions (6 ask-Marc, 5 ask-Werbos, 1 self-determine, 1 resolved).
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
| [Q10](#q10-detail) 🔶 | FLDB energy convention | Confirm the Eq 122/124/127 algebra (M7.2 identified the dropped square + the dropped ½): is the corrected **`U ≈ 0.958 m_ec²`** the intended prediction? | evidence delivered by M7.2 § 3; Marc's confirmation pending |
| [Q1](#q1-detail) 🔶 | Substrate + target manifold | The `(A_μ, J_μ)` doublet (candidate B, built at M7.1) vs single RS field (A); Clebsch as seeder only (D); and the target manifold: Pisello S² vs Faber S³? | M7.3/M7.4 closure |
| [Q4](#q4-detail) 🔶 | Marc's source material | The further Beltrami papers he mentioned (corpus #13) + the status of bringing in Enciso & Peralta-Salas as collaborators? | corpus (M7.0, ongoing) |
| [Q11](#q11-detail) 🔶 | Windowed charged calibration | M7.3 showed `H/Q = 1.6890` is a windowed quadrature (no decaying channel at `ω=1, λ=1`; `Q` grows with `r_max`): is the calibration window-defined, or does a genuinely localized charged branch exist elsewhere in parameter space? | M7.3 delivered the evidence; blocks any physical-mass reading of the M6 charged ledger |
| [Q13](#q13-detail) 🔶 | 3D stability of the chaoiton | M7.3: the M6 electron is a 3D constrained SADDLE of its verbatim functional, ending in focusing collapse (helicity guard inert on it): is the conjugate-point stability claim (LoE 9b § 5) restricted to the 1D radial manifold? | feeds M7.4 blend design; the M7.5 real-time probe |
| [Q12](#q12-detail) 🔶 | M6 ODE / ansatz provenance | The `0d_canonical § 2.2` `2ωα` form is not an EL reduction of the Lagrangian under any scanned harmonic ansatz, and LoE 9b § 5.1's cos/sin phases decouple: which ansatz + ODE does Werbos intend as canonical? | M7.3 delivered the reduction table; documentation fix for `0d_canonical.md` |
| [Q9](#q9-detail) 🚧 | Werbos-v5 calibration dictionary | The `(Ω, G) ↔ (ω, g, m_J)` map between v5's canonical point (`g = 1.0625`, `H/Q = 1.6969`) and M6's repo-validated canonical (`g = 1.0`, `H/Q = 1.6890`)? | M7.3 secondary gate · M7.12 islands |
| [Q6](#q6-detail) 🔶 | Potential form | Keep M6's `f(s) = (g/4) s²` for the toroidal sector, or a better-suited form? (M7.3 evidence: the operative `f` matching the benchmark is FOCUSING, `−(λ/2)s − 2g s²` RWA, and drives the 3D collapse) | M7.4 design |
| [Q2](#q2-detail) 🔶 | 4th-order stabilizer | Is any 4th-order term needed at all, and in which non-inert form? (helicity + confinement is the working stabilization) | M7.4 optional experiment (off by default) |

---

## RESOLVED QUESTIONS

| ID | Question | Resolution |
| --- | --- | --- |
| [Q8](#q8-detail) ✅ | Gauge / constraint scheme for the coupled minimizer | RESOLVED at M7.3 (2026-07-03), as scheduled: **no explicit gauge fixing**. The coupled fixed-`Q_can` relaxation ran gauge-unfixed with no stall or drift pathology; the correction the pre-gate actually forced was **objective-level**, not gauge-level: minimize/extremize `E_ω` at fixed `Q_can` (multiplier ω), never `E_ω` unconstrained (its EL has the ω²-sign flipped). M7.1's G5 evidence (curl sector self-fixes; only `A·J` gauge-sensitive off-shell) stands. Residual: if a future M7.4+ run shows gauge stall, reopen with the Coulomb-projection candidate. [`tasks/m7_3_ouroboros_3d.md § 1, § 4`](tasks/m7_3_ouroboros_3d.md) |

---

## HARDEST PIECES, status board (risks / unknowns)

The long-running load-bearing unknowns, distinct from the discrete Q-numbered questions above (a piece can persist across many tasks). Promote a row to a numbered question once it becomes a decision the build must make.

| Hardest piece | Status / mitigation |
| --- | --- |
| The time-harmonic reduction goes subtly wrong (M6 needed ten sandbox versions to pin its 1D reduction: signs, regularity classes, Laplacians, measures) | ✅ CLOSED at M7.3: the verbatim-ODE pre-gate passed with every sign/normalization pinned by sympy (and it caught three real convention faults: the coupling sign, the focusing `f`, the wrong objective `E_ω`-unconstrained), [`tasks/m7_3_ouroboros_3d.md § 1`](tasks/m7_3_ouroboros_3d.md) |
| The 1D chaoiton may be **unstable to 3D symmetry breaking** (1D radial solutions often are) | ✅ ANSWERED at M7.3, honestly: it is a 3D constrained SADDLE with a focusing-collapse escape (Q13); feeds the M7.4 blend design (the helicity guard is inert on M6's ansatz; the blend activates it) |
| Gauge flat directions stall or misdirect the minimizer (Q8) | ✅ RESOLVED at M7.3: no gauge fixing needed; the coupled fixed-`Q_can` relaxation ran gauge-unfixed cleanly (see Q8 resolution row) |
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
- **Comms plan (2026-07-02, deliver-first-ask-second, the M5.16 pattern):** after **M7.3** runs, prepare the consolidated M7.1-M7.3 report and the collected ask round (Q7, Q5, Q3, Q10, Q1, Q4) as ONE package for Marc; the M7.2 deliverables (the reproduction + the Q10 evidence + the surface-charge result) back the asks. M7.3 ran 2026-07-03: report + ask package = the next step. The **Werbos asks** (Q11, Q13, Q12, Q9, Q6) are a separate audience/package, backed by the M7.3 deliverables (the reduction table, the window plot, the collapse traces).

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

**FLDB energy convention (ask Marc, priority 4).** Originally: which complex-field convention do Eqs 31/32 use? **M7.2 delivered the evidence (2026-07-02, [`tasks/m7_2_fleury_torus.md § 3`](tasks/m7_2_fleury_torus.md)) and the question sharpened**: the appendix declares the standard phasor average `E² = ½E·E*` (its Eq 113-115), but **Eq 122/124 drop the square on `(1+R/R₀)` in `E_φE_φ*` and Eq 127 drops the ½ on the B term**; the two slips produce Eq 31. With the appendix's own convention applied exactly, `U_phys = (6/5)×Eq 32` (thin torus): **`U/m_ec² = 0.795 → 0.958`**, closing most of the paper's acknowledged energy gap. The constraints (Q, μ, L) are slip-free, so the solved parameters stand. Verified three ways (closed form, independent 2D quadrature to 2e-16, 3D lattice to 1.4e-4 at O(h².5)). **The ask is now**: confirm Eq 122/124/127 and whether `U ≈ 0.958 m_ec²` is the intended prediction. Marc is the author; the cheapest, highest-value ask on the list. Opened 2026-07-02; evidence delivered same day by M7.2 (which ran non-blocked, computing both conventions as planned).

### Q1 detail

**Substrate + target manifold (ask Marc, priority 5).** The Ouroboros doublet `(A_μ, J_μ)` read via Riemann-Silberstein (candidate B) vs single-field RS `F = E + icB` (candidate A); does Clebsch/`ψ` (D) enter only as a knot **seeder**? And what **target manifold**: Pisello S² vs Faber S³ ([`m7_background.md § 2`](m7_background.md))? Narrowed to **B** by Marc's **A-primary** commitment (`A` fundamental, `F = dA`, charge derived); RS kept as a derived diagnostic. **M7.1 built the substrate as B** (the 16-component harmonic doublet, [`scripts/m7_1_harmonic_lattice.py`](scripts/m7_1_harmonic_lattice.py) via [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md)); a structural argument now also favors B: Nadirashvili's theorem makes the pure-Maxwell finite-energy Beltrami electron impossible, so the doublet's confinement sector is required for existence ([`m7_background.md § 5b`](m7_background.md)). Formal closure waits on M7.3/M7.4 confirming the doublet carries both charges. **The ask:** his read on the S²-vs-S³ target-space choice.

### Q4 detail

**Marc's source material (ask Marc, priority 6; logistics).** The Beltrami / ABC source papers and further material from Marc. PARTLY IN: Sato-Yamada landed (arXiv:1809.03136 + the note in [`../theory/sato_yamada_beltrami.md`](../theory/sato_yamada_beltrami.md), [M7.0 corpus](tasks/m7_0_bootstrap.md) #11); more material expected (corpus #13). **The asks:** the further papers he mentioned, and the status of bringing in the Spanish Beltrami school (Enciso & Peralta-Salas, corpus #6) as collaborators.

### Q9 detail

**Werbos-v5 calibration dictionary (ask Werbos).** v5's canonical point is `g = 1.0625` (`H/Q = 1.6969`) vs M6's repo-validated canonical `g = 1.0` (`H/Q = 1.6890`), vs physical `1.6875`; and v5's new `(Ω, G)` bifurcation islands (electron `Ω = 1.050` stable `k > 0`; muon `Ω = 0.914` resonant `k < 0`) need the `(Ω, G) ↔ (ω, g, m_J)` map (Zenodo 20866581, the 319-family scan). Route: ask Werbos and/or read the Zenodo record. Until resolved, **M7.3 uses the M6 calibration as primary** (ledger in [`m7_background.md § 4`](m7_background.md)); the islands become an M7.12 falsifiable structure (stable electron vs resonant/metastable muon). Opened 2026-07-02 (plan refactor).

### Q6 detail

**Potential form (ask Werbos).** The `f(J·J)` potential form for M7: keep M6's canonical `f(s) = (g/4) s²` ([`0d_canonical.md § 1`](../../m6_ouroboros/research/0d_canonical.md)), or a form better suited to the toroidal sector? **M7.3 evidence in (2026-07-03,** [`tasks/m7_3_ouroboros_3d.md § 1`](tasks/m7_3_ouroboros_3d.md)**):** the potential that actually reproduces the benchmark ODE verbatim is `f(s) = −(λ/2)s − 2g s²` (RWA; `−4g/3` under exact averaging), FOCUSING in both terms and carrying a λ-term the written `(g/4)s²` lacks entirely; this focusing sign is what drives the 3D collapse (Q13). **The ask:** which `f` (sign, normalization, λ-term) Werbos intends as canonical; M7.4's blend design needs the answer to choose its confinement sector honestly.

### Q11 detail

**Windowed charged calibration (ask Werbos; NEW at M7.3).** The M6 charged benchmark profile at the canonical point (g=1, ω=1, λ=1, A0=B0=0.1) does not decay: `Q` grows ~linearly with the integration window and `H/Q` oscillates through the ledger value, equaling 1.6890 exactly at the benchmark's hard-coded `r_max = 12` ([`tasks/m7_3_ouroboros_3d.md § 2`](tasks/m7_3_ouroboros_3d.md), plot [`plots/m7_3_embed_convergence.png`](plots/m7_3_embed_convergence.png)). Analytic root: the far-field dispersion `(ω² − k²)(ω² + λ − k²) = 1` has both roots `k² = (3±√5)/2 > 0` at the canonical point: **no exponentially decaying channel exists**; the A-sector is a radiation field at ω. Same structure as the neutral-sector windowed-integration artifact the M6 record already caught (sandbox_v8 Q42), never flagged for the charged sector. **The asks:** (a) is `H/Q = 1.6890/1.6969` understood to be window-defined, and what fixes the window physically? (b) does a genuinely localized charged branch exist elsewhere in `(ω, λ, g)` (the localization condition needs both far-field masses positive, i.e. `ω² < 0`-type regions the real-ω scan can't reach; a Yukawa-decaying variant would need a different coupling structure)? Note the constructive side: this is Nadirashvili-consistent and strengthens the HydroBoros confinement thesis ([`m7_background.md § 5b`](m7_background.md)).

### Q12 detail

**M6 ODE / ansatz provenance (ask Werbos; NEW at M7.3).** The M7.3 sympy scan ([`tasks/m7_3_ouroboros_3d.md § 1`](tasks/m7_3_ouroboros_3d.md), [`data/m7_3_pregate_sympy.json`](data/m7_3_pregate_sympy.json)) reduced the M6 Lagrangian over six harmonic ansaetze × two quartic conventions. Results: (a) the benchmark ODE (the validated `H/Q` producer) is the verbatim EL reduction of the **same-phase azimuthal doublet** `A_φ = α(ρ)cos ωt, J_φ = β(ρ)cos ωt` with pins `κ = −1`, focusing `f`; (b) [`0d_canonical.md § 2.2`](../../m6_ouroboros/research/0d_canonical.md)'s `2ωα` chiral form matches NO candidate, with a structural obstruction (time-averaged bilinears give only ω⁰/ω² couplings; the needed `∇X₀·∂ₜX⃗` cross term is geometrically zero), so § 2.2 as written is not an EL reduction of the stated Lagrangian; (c) LoE 9b § 5.1's phase text (`A ∝ cos`, `J ∝ sin`) decouples the α-equation (`⟨cos·sin⟩ = 0`) and its μ=0 J-equation forces α ≡ 0. **The asks:** which ansatz + ODE is the intended canonical (and where the `2ωα` form comes from, e.g. a different derivation route or the "asymmetric helicity prescription"); our `0d_canonical.md § 2.2` needs a correction note either way. Also feeds Q9 (the v5 dictionary presumably shares the provenance).

### Q13 detail

**3D stability of the chaoiton (ask Werbos; NEW at M7.3).** With the verbatim-pinned functional, the embedded M6 electron is a genuine 3D discrete critical point of `(E_ω, Q_can)` with multiplier ω (residual → 0 as h²), but **not a constrained minimum**: fixed-`Q_can` descent departs immediately in both the axisymmetric sector (converges first to a different near-critical state, then finds an axis-concentration channel) and the free 3D sector (supercritical focusing collapse, amplitude → 124× seed before the non-finite guard) ([`tasks/m7_3_ouroboros_3d.md § 4`](tasks/m7_3_ouroboros_3d.md)). Mechanism: the focusing pins (Q6) make `E_ω` unbounded below along concentration at fixed `Q_can` (L²-critical in 2D-symmetric, supercritical in 3D). The M6 ansatz carries zero A-helicity, so helicity-based anti-collapse guards are inert on it. **The asks:** (a) is the LoE 9b § 5 "constrained minimum + conjugate-point" stability claim established only within the 1D radial ansatz manifold? (b) does Werbos have a candidate stabilizing mechanism in the full 3D field space (M7's answer is the M7.4 helicity-carrying blend)? Honest caveats attached: FIRE descent shows a descent direction exists, not a growth rate; the collapse endpoint is lattice-arrested/guarded, not resolved.

### Q8 detail

**Gauge / constraint handling (✅ RESOLVED at M7.3, 2026-07-03; kept for history).** The question: which scheme for the coupled minimizer, Coulomb gauge on `a⃗` + kept `a₀`, projection, or penalty? Evidence trail: M7.1 gate G5 measured `E_ω` exactly gauge-invariant at `m_J = 0` (machine zero) and broken by `m_J²A·J` off-shell (`ΔE/E ≈ 1.3e-3` on random fields); the static curl sector self-fixes (transverse AD gradient; the Woltjer relaxation converged gauge-drift-free), [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings. **Resolution (M7.3,** [`tasks/m7_3_ouroboros_3d.md § 1, § 4`](tasks/m7_3_ouroboros_3d.md)**): no explicit gauge fixing.** The coupled fixed-`Q_can` relaxation ran gauge-unfixed with no stall or drift pathology; the correction the pre-gate actually forced was **objective-level**, not gauge-level: extremize `E_ω` at fixed `Q_can` (multiplier ω), never unconstrained `E_ω` (its EL carries the ω²-sign flip). Residual: if a future M7.4+ run shows a gauge stall, reopen with the Coulomb-projection candidate. Opened 2026-07-02 (plan refactor); resolved 2026-07-03.

### Q2 detail

**4th-order stabilizer (self-determine; optional M7.4 experiment).** Is a 4th-order term needed at all, and in which form? **Direction set** (2026-07-02 theory review): the drafted `\|F×(∇×F)\|²/\|F\|²` term **vanishes identically on every Beltrami configuration** (`∇×F ∥ F` makes the cross product zero, constant AND variable λ; rescaled Beltrami stays Beltrami) and is **singular** where `\|F\| → 0`, so it provides zero Derrick pressure on exactly the target family. Working stabilization = **helicity anti-collapse** (Arnold `E ≥ λ₁\|H\|`) + **Ouroboros confinement anti-expansion** (`~μ³`), with **Nadirashvili's theorem** forcing the confinement term to exist ([`m7_background.md § 5b`](m7_background.md)). The 4th-order term is demoted to an optional M7.4 experiment, **off by default** (any run uses a regularized variant, labeled an experiment). Empirical confirmation so far: the M7.1 Woltjer gate ✅ (2026-07-02: fixed-helicity relaxation from random seeds lands on the constant-λ eigenfield, `λ → 2π/L` at 5.5e-6, [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) § Findings); next: the M7.4 dilation probe.

---

Cross-refs: roadmap [`m7_roadmap.md`](m7_roadmap.md) · background [`m7_background.md`](m7_background.md) (§ 2 math boundaries, § 5 dynamics) · task docs [`tasks/m7_1_infra.md`](tasks/m7_1_infra.md) (Q1/Q2 evidence, Q8 G5 evidence) · [`tasks/m7_2_fleury_torus.md`](tasks/m7_2_fleury_torus.md) (Q10) · [`tasks/m7_3_ouroboros_3d.md`](tasks/m7_3_ouroboros_3d.md) (Q8 resolution; Q6 evidence; Q11/Q12/Q13 openers; Q9 context) · [`tasks/m7_4_charged_soliton.md`](tasks/m7_4_charged_soliton.md) (Q3/Q5/Q7) · the M5 / M6 trackers this mirrors: [`m5_question_tracker.md`](../../m5_liquid_crystal/research/m5_question_tracker.md) (M5) · [`0b_question_tracker.md`](../../m6_ouroboros/research/0b_question_tracker.md) (M6).
