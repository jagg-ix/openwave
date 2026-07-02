# M7.1, infra (define the substrate field + stand up the lattice / minimizer)

> Task **M7.1** (M7 / HydroBoros). taskID = M7.N iteration. Status: **In Progress** · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

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

The decision between A and B (and whether D enters only as a seeder) is **open**, tracked as **Q1** in [`../m7_question_tracker.md`](../m7_question_tracker.md), the M5-style question tracker (cf. [`0b_question_tracker.md`](../../../m6_ouroboros/research/0b_question_tracker.md)); the open questions Q1-Q9 live there. A structural argument now favoring **B**: Nadirashvili's theorem makes the pure-Maxwell (single-field) finite-energy Beltrami electron impossible, so the doublet's confinement sector is required for existence ([`../m7_background.md § 5b`](../m7_background.md)).

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
| **Units contract** | M6 natural units wholesale: `c = 1`, electron `ω = 1`, `m_e` anchor; conversion table [`0d_canonical.md § 5`](../../../m6_ouroboros/research/0d_canonical.md) | prevents unit chaos at M7.2/M7.3; Fleury targets are dimensionless ratios so M7.2 works in `r_c = 1` units directly |

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (task M7.1, Phase A + the method frame note) · full background [`../m7_background.md`](../m7_background.md) (§ 5a harmonic frame, § 5b stabilization, § 5d decisions); open questions Q1/Q2/Q8 in [`../m7_question_tracker.md`](../m7_question_tracker.md) · M7.0 corpus [`m7_0_bootstrap.md`](m7_0_bootstrap.md) · downstream: [`m7_2_fleury_torus.md`](m7_2_fleury_torus.md) (parallel-safe) · [`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md) (verbatim-ODE gate) · [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md).
