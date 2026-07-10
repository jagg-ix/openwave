# M7.1, infra (define the substrate field + stand up the lattice / minimizer)

> Task **M7.1** (M7 / HydroBoros). taskID = M7.N iteration. Status: **Done** (2026-07-02, all gates pass) · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation. **M7.1 (infra)** stands up the A-primary doublet on a 3D lattice **in the time-harmonic (fixed-ω) frame** ([`../m7_background.md § 5a`](../m7_background.md): both parents are time-periodic, no static electron exists in this model), the **helicity observable + fixed-helicity relaxation**, the AD energy gradient (validated to `1e-12` vs a numpy finite-difference reference), the FIRE / L-BFGS minimizer, and the Bateman/Hopf + Trkalian (constant-λ) Beltrami seeders. It also fixes three design decisions (BCs, gauge, units, § below) and passes the **Woltjer-Taylor known-answer gate**. Its first design decision, captured here, is **which substrate field** the lattice evolves (Open Question Q1).

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

The decision between A and B (and whether D enters only as a seeder) is **open**, tracked as **Q1** in [`../m7_question_tracker.md`](../m7_question_tracker.md), the M5-style question tracker (cf. [`0b_question_tracker.md`](../../../m6_ouroboros/research/archive/0b_question_tracker.md)); the open questions Q1-Q10 live there (priority-sorted, the ask list for Marc). A structural argument now favoring **B**: Nadirashvili's theorem makes the pure-Maxwell (single-field) finite-energy Beltrami electron impossible, so the doublet's confinement sector is required for existence ([`../m7_background.md § 5b`](../m7_background.md)).

**Duda's field-configuration bar (2026-07-01) constrains this decision.** On the models-of-particles list (2026-07-01, continuing the 2026-06-29 prescription captured in [`../m7_roadmap.md`](../m7_roadmap.md) § Phase A / Ouroboros [#247](https://github.com/openwave-labs/openwave/issues/247)), Duda re-stated the precondition for any particle model: **specify the field configuration of every particle** (photons, neutrinos, leptons, mesons, baryons, nuclei) and answer **"do you use topological vortices? for which particles?"** before simulating, validated against an independent benchmark ([MODELS.md](https://github.com/openwave-labs/openwave/blob/main/MODELS.md)), "not just talking to an LLM chatbot." He attached a comprehensive **liquid-crystal field-configuration sketch** (his own model's answer), decoded in [`../../../m5_liquid_crystal/research/tasks/m5_4f_convo_2026.07.01.md`](../../../m5_liquid_crystal/research/tasks/m5_4f_convo_2026.07.01.md) § 2; figure [`../../../m5_liquid_crystal/theory/duda_2026-07-01_particle_field_configs.png`](../../../m5_liquid_crystal/theory/duda_2026-07-01_particle_field_configs.png).

That demand IS the blend test above: the substrate must carry a **topological-vortex** particle config with both the divergence charge (Fleury, `∇·F`) and the linking/helicity (Ouroboros, `∫A·B`) as one object. HydroBoros's answer, the electron **is** the self-linked toroidal Beltrami vortex, is only representable on a knot-native substrate, which is the structural case for candidate **B** (the `A_μ` doublet) over the divergence-free Faddeev-Niemi candidate **C** (no charge) and confirms why Q1 must not pick a config that breaks Fleury's `∇·E` charge. Duda's sketch is the reference standard the M7 column must match particle-by-particle at MODELS.md (Phase D); the electron config is **earned as the energy-minimizer** at M7.1/M7.4, not assumed, sidestepping the "assume vs predict" objection.

---

## Deliverables (the build list)

| # | Deliverable | Gate |
| --- | --- | --- |
| 1 | **Time-harmonic reduced functional `E_ω`**: every field component carries one global ω via a `(cos ωt, sin ωt)` component pair; `E_ω` = period-averaged energy; exact component bookkeeping + constraint structure derived and documented here | symbolic + numeric self-checks; final arbiter is the M7.3 verbatim-ODE pre-gate ([`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md)) |
| 2 | **Helicity observable** `H = ∫A·B` (+ the J-sector analog) and **fixed-helicity relaxation** (projection or Lagrange-multiplier during descent) | `H` conserved along descent to integrator tolerance |
| 3 | **Taichi reverse-mode AD gradient** `δE_ω/δ(fields)` | == numpy finite-difference gradient to `1e-12` on random fields, **before any run is trusted** |
| 4 | **FIRE / L-BFGS minimizer** | descends monotonically; passes deliverable 6 |
| 5 | **Seeder inventory** (see table below) | each seeder's analytic invariants (helicity, energy, λ) reproduced on the lattice to grid accuracy |
| 6 | **Woltjer-Taylor known-answer gate**: on the periodic box, relax `∫\|B\|²` at fixed helicity from a random div-free seed | converges to the **constant-λ curl eigenfield** (ABC family): `∇×B = λB` pointwise, `λ → 2π/L` (the smallest curl eigenvalue), `E → λH`, all to grid accuracy. Theorem-anchored (Woltjer 1958, corpus #1) |
| 7 | **Design decisions documented**: BCs, gauge (Q8), units (below) | recorded in this doc + reflected in the code |

## Seeder inventory

| Seeder | Construction | Serves |
| --- | --- | --- |
| **ABC / Trkalian eigenfield** | the periodic-box curl eigenfields (Dombre 1986, corpus); exact constant-λ Beltrami | the Woltjer gate; M7.4 Trkalian seeds |
| **S&Y toroidal Beltrami** | Sato-Yamada eikonal + equal-scale-factor recipe ([`../../theory/sato_yamada_beltrami.md`](../../theory/sato_yamada_beltrami.md)) | toroidal constant-λ seeds (M7.4) |
| **Bateman / Kedia Hopf knots** | the Bateman construction (Kedia 2013, corpus #5); knotted null EM initial data | knotted seeds (M7.4); Q1's candidate-D role (seed-only) |
| **Fleury torus** | the FLDB ansatz verbatim ([`m7_2_fleury_torus.md`](m7_2_fleury_torus.md) conventions contract) | M7.2 quadrature; M7.4 blend seeds |
| **M6 chaoiton embedding** | the M6 1D `(α,β)` profile revolved into the 3D torus/cylinder ([`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md)) | M7.3; M7.4 blend seeds |
| **Ceperley rotating modes** | `J_m(k_c r)` Bessel-envelope rotating waves ([`../../theory/ceperley_rotating_waves.md`](../../theory/ceperley_rotating_waves.md) § 4) | the M7.2 Bessel stretch; smooth-envelope alternatives to the Heaviside mask |

## Design decisions (fixed at M7.1)

| Decision | Resolution | Why |
| --- | --- | --- |
| **Boundary conditions** | **vacuum-fixed** boundary for any net-charged configuration; **periodic** box for neutral / net-zero configs (Woltjer gate, M7.6 two-charge dipole) | a net charge on a periodic lattice is Gauss-inconsistent (boundary flux 0 ≠ `Q/ε₀`); Faber & Golubich and Sutcliffe both use vacuum-fixed in practice |
| **Gauge handling** | OPEN = **Q8**: Coulomb gauge on `a⃗` + kept `a₀`, vs projection, vs penalty; decided empirically here by minimizer conditioning | gauge orbits of `A` are flat directions; `m_J²A·J` is gauge-sensitive off-shell; M6's ansatz has `A₀ ≠ 0` (Weyl incompatible) |
| **Units contract** | M6 natural units wholesale: `c = 1`, electron `ω = 1`, `m_e` anchor; conversion table [`0d_canonical.md § 5`](../../../m6_ouroboros/research/archive/0d_canonical.md) | prevents unit chaos at M7.2/M7.3; Fleury targets are dimensionless ratios so M7.2 works in `r_c = 1` units directly |

---

## FINDINGS (2026-07-02, the gate suite run)

Deliverables 1-7 built and gated. Code: [`../scripts/m7_1_harmonic_lattice.py`](../scripts/m7_1_harmonic_lattice.py) (the core module: harmonic fields, `E_ω` twins, AD, FIRE, helicity, seeders) + [`../scripts/m7_1_gates.py`](../scripts/m7_1_gates.py) (the gate suite). Results: [`../data/m7_1_gates.json`](../data/m7_1_gates.json) · plots [`../plots/m7_1_woltjer_gate.png`](../plots/m7_1_woltjer_gate.png), [`../plots/m7_1_seeder_gallery.png`](../plots/m7_1_seeder_gallery.png).

### The harmonic reduction, exact bookkeeping (deliverable 1)

Every component of `A_μ = (A⁰, A⃗)` and `J_μ = (J⁰, J⃗)` carries one global ω through a `(cos ωt, sin ωt)` pair: 16 real fields per lattice point (`a0c, a0s, a⃗c, a⃗s, j0c, j0s, j⃗c, j⃗s`). Conventions: Minkowski `(−,+,+,+)`, A-primary, `E⃗ = −∇A⁰ − ∂ₜA⃗`, `B⃗ = ∇×A⃗`, `A_μJ^μ = −A⁰J⁰ + A⃗·J⃗`, `s = J_μJ^μ = −(J⁰)² + \|J⃗\|²`, `f(s) = (g/4)s²` (M6 canonical, [`0d_canonical.md § 1`](../../../m6_ouroboros/research/archive/0d_canonical.md)).

| Piece | Exact closed form |
| --- | --- |
| derived fields per harmonic component | `E⃗c = −∇a0c − ω a⃗s`, `E⃗s = −∇a0s + ω a⃗c` (time derivative is algebraic in harmonic space); `B⃗c = ∇×a⃗c`, `B⃗s = ∇×a⃗s`; J sector identical |
| bilinear averages | `⟨X(t)Y(t)⟩ = ½(XcYc + XsYs)` |
| quartic average (NO rotating-wave truncation) | `s(t) = s₀ + s₁cos 2ωt + s₂sin 2ωt` with `s_cc = −j0c² + \|j⃗c\|²`, `s_ss = −j0s² + \|j⃗s\|²`, `s_cs = −j0c j0s + j⃗c·j⃗s`, `s₀ = ½(s_cc+s_ss)`, `s₁ = ½(s_cc−s_ss)`, `s₂ = s_cs`; then `⟨s²⟩ = s₀² + ½(s₁² + s₂²)` exactly |
| the functional | `E_ω = ∫ [¼(\|E⃗c\|²+\|E⃗s\|²+\|B⃗c\|²+\|B⃗s\|²)_A + ¼(...)_J − m_J²⟨A·J⟩ + ⟨f(s)⟩] d³x` (interaction terms carry no time derivative, so `H_int = −L_int`) |

Caveat kept honest: these signs and pairings are OUR reading of the M6 Lagrangian; the final arbiter is the M7.3 verbatim-ODE pre-gate ([`m7_3_ouroboros_3d.md § 1`](m7_3_ouroboros_3d.md)).

### Gate results

All gates ✅ measured (suite wall time 69 s, Taichi CPU f64; Metal has no f64, and the 1e-12 AD bar needs double precision):

| Gate | Result | Key numbers |
| --- | --- | --- |
| **G1 bookkeeping** | ✅ | closed-form `E_ω` vs brute-force 16-sample period average: rel diff **0.0** (uniform sampling is exact for the degree-4 trig polynomial `u(t)`, so this gate is all-or-nothing) |
| **G2 AD gradient** | ✅ | Taichi energy vs numpy twin: 1.6e-15; AD gradient vs **complex-step** directional derivatives (holomorphic twin, exact to machine precision, stronger than finite differences): max rel err **2.3e-15** over 10 random directions (the bar was 1e-12) |
| **G3 Woltjer-Taylor** | ✅ | fixed-helicity FIRE from a pure-random seed converges to the constant-λ curl eigenfield: `λ_hat = E/H` matches the discrete curl eigenvalue `sin(kh)/h` to **3e-12** per N; Richardson `λ(h→0) = 6.283151` vs `2π/L = 6.283185` (rel 5.5e-6); pointwise `λ_eff` std/\|λ\| ≤ 1.1e-6; 471/620/1083 FIRE iterations at N = 24/32/48, 67 s |
| **G4 ABC/Trkalian** | ✅ | discrete eigenrelation `∇×A = λ_h A` residual 1.8e-14 (machine); lattice `H`, `E_B` equal continuum × `sinc(kh)`, `sinc²` to 3e-16 (the closed-form O(h²) law) |
| **G4 CK spheromak** | ✅ | toroidal constant-λ seed: interior `λ_eff` median dev 0.71% → 0.40% → 0.18% at N = 48/64/96 (O(h²)); the S&Y eikonal variable-h construction stays deferred to M7.4 |
| **G4 Bateman hopfion** | ✅ | interior div-free O(h²) (1.1% → 0.28%); helicity Richardson `H_m = 9.6684`, `H_e = H_m` exactly (self-dual null field); `U = 19.7237 ≈ 2π²` (0.08% low, box-tail truncation) |
| **G4 Fleury torus** | ✅ | inverted-Heaviside tube support 0.003311 vs analytic `2π²R₀r₀²/L³ = 0.003321` (0.3%, N = 128); `ω = 2/R₀` enforced; finite `E_ω`; observable reproduction is M7.2's |
| **G4 M6 embedding** | ✅ | 1D profile solver reproduces the **ledger `H/Q = 1.68897` vs 1.6890** (benchmark ODE at g = 1.0, ω = 1); 3D straight-cylinder embedding quadrature err 0.062% → 0.013% (O(h²)); the toroidal-vs-cylindrical question stays M7.3's |
| **G4 Ceperley mode** | ✅ | `m = 1` azimuthal winding measured 0.990 (nearest-grid loop sampling); `J₁` Bessel envelope, the M7.2 mask-replacement stretch |
| **G5 gauge probe (Q8)** | ✅ | harmonic gauge transform (`A⁰ → A⁰ − ∂ₜχ`, `A⃗ → A⃗ + ∇χ`): `ΔE_ω/E = 0.0` at `m_J = 0` (machine zero, the Maxwell structure of the functional verified); `1.3e-3` at `m_J = 0.8` (the `m_J²A·J` term is gauge-sensitive off-shell, exactly as Q8 predicted) |

### Design decisions concluded (deliverable 7)

| Decision | Outcome |
| --- | --- |
| **BCs** | both modes in the module: periodic (gates ran periodic) + vacuum-fixed as a pinned zero boundary shell (`vacuum_mask`); charged sectors use vacuum-fixed per the design table above, box-size extrapolation at M7.3/M7.4 |
| **Gauge (Q8)** | measured evidence, not yet a scheme decision: the static curl sector needs NO gauge fixing (its AD gradient is transverse: discrete div∘curl = 0 exactly, and G3 converged from random seeds with no gauge drift); the full `E_ω` is exactly gauge-invariant at `m_J = 0` and broken by `m_J²A·J` off-shell (G5). Q8 stays OPEN for the coupled-minimizer scheme (Coulomb-on-`a⃗` vs projection vs penalty), to be decided when the coupled sector first relaxes (M7.3) |
| **Units** | M6 natural units adopted; every gate number is dimensionless, no conversion entered the code; the Fleury seed works in `r_c = 1` units directly |

Method notes worth carrying forward: (1) the fixed-helicity constraint is enforced by gradient projection + the exact quadratic rescale `A → A√(H₀/H)` (helicity restored exactly every step, no drift term needed); (2) FIRE needed no tuning beyond defaults (dt_max 0.5), converging in ~500-1100 iterations; (3) the complex-step trick requires the numpy twin to be written holomorphically (`x·x`, never `abs`), which the module documents and enforces by construction.

---

## TASK REVIEW (2026-07-02)

**Task Duration:** 00:23 (from 17:35 to 17:58 EDT)
**Usage Cap Triggered:** NO

**Results**: all deliverables 1-7 ✅ measured; the full gate table is in § Findings above (G1 bookkeeping bit-exact; G2 AD vs complex-step `2.3e-15`; G3 Woltjer `λ → 2π/L` at `5.5e-6` from pure-random seeds; G4 six seeders incl. the M6 ledger `H/Q = 1.68897` reproduced; G5 gauge probe = the Q8 evidence).

**Issues / blockers**: none blocking. Three first-run G4 failures were gate-implementation artifacts (λ_eff division at ABC stagnation points, periodic-wrap contamination of the hopfion's non-periodic tail, thin-tube voxelization), fixed and documented; the physics never failed. Flagged: the S&Y seeder role is filled by the CK spheromak; the S&Y eikonal variable-h construction is deferred to M7.4 (an ask for Marc, [`../m7_question_tracker.md`](../m7_question_tracker.md) § Ask Marc). Workflow correction (Rodrigo): OpenWave-task resume checkpoints live in `research/checkpoints/` in THIS repo (gitignored), not in any external tracker.

**Action needed**: Q8 scheme decision lands at the first coupled relaxation (M7.3). Next per the roadmap: M7.2 (parallel-safe Fleury quadrature) or the M7.3 verbatim-ODE pre-gate.

**Findings**: The M7 substrate infrastructure is stood up and theorem-gated: the time-harmonic `(A_μ, J_μ)` doublet lattice with AD gradients exact to `2e-15` and a fixed-helicity relaxer that reproduces Woltjer's 1958 theorem from random seeds (`λ → 2π/L` at `5.5e-6`). The M6 parent's calibration point (`H/Q = 1.6890` at `g = 1.0`) is independently reproduced by the seeder pipeline, and the Q8 gauge-sensitivity structure is now measured, not conjectured.

**Research docs created / updated**: this doc (§ Findings) · script [`../scripts/m7_1_harmonic_lattice.py`](../scripts/m7_1_harmonic_lattice.py) · script [`../scripts/m7_1_gates.py`](../scripts/m7_1_gates.py) · data [`../data/m7_1_gates.json`](../data/m7_1_gates.json) · tracker [`../m7_question_tracker.md`](../m7_question_tracker.md) (Q1/Q2/Q8 + the Ask-Marc list) · roadmap row → Done.

### Plots

![`../plots/m7_1_woltjer_gate.png`](../plots/m7_1_woltjer_gate.png)
(key plot: the λ → 2π/L convergence)

![`../plots/m7_1_seeder_gallery.png`](../plots/m7_1_seeder_gallery.png)

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (task M7.1, Phase A + the method frame note) · full background [`../m7_background.md`](../m7_background.md) (§ 5a harmonic frame, § 5b stabilization, § 5d decisions); open questions Q1/Q2/Q8 in [`../m7_question_tracker.md`](../m7_question_tracker.md) · M7.0 corpus [`m7_0_bootstrap.md`](m7_0_bootstrap.md) · downstream: [`m7_2_fleury_torus.md`](m7_2_fleury_torus.md) (parallel-safe) · [`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md) (verbatim-ODE gate) · [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md).
