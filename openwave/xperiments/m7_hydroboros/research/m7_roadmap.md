# M7 / HydroBoros, roadmap

> Local task roadmap for the **M7 (HydroBoros)** model, replicating the M5 local-roadmap structure (2026-07-01). M7 has **no GitHub issues**; tasks are tracked here. **taskID = M7.N**. Full planning + findings live in each [`tasks/m7_N_*.md`](tasks/) detail doc; scripts / data / plots live in [`scripts/`](scripts/) · [`data/`](data/) · [`plots/`](plots/), all named `m7_N_*.{py,npz,png}`. Ordering is the build sequence (M7.0 → M7.23, Phases 1 → 5; task IDs are stable, table order = build order); the **top of Backlog is the next task**.
>
> The program runs in five **phases** (renumbered 2026-07-04, extended 2026-07-06 after the Fleury Phase-1-review call): **Phase 1** builds the electron and drafts the coverage column (M7.0-M7.7, ✅ DONE), then **extends through the Fleury collaboration track** (M7.8 helicity pair + walkthrough, M7.9 ChaosBook benchmark, M7.10 the pure-Maxwell no-Lagrangian test, run in that order; **M7.11-M7.14 reserved** for the rest of the pure-Maxwell/Beltrami orbit-hunting work as it firms up post-August; the walkthrough report bundles the M7.8 + M7.9 + M7.10 results for the author); **Phase 2** expands across the forces and the remaining particle sectors (M7.15-M7.20); **Phase 3** publishes the M7 column to MODELS.md for cross-model benchmarking (M7.21, advanced to right after Phase 2: a good publication milestone); **Phase 4** groups the composites still untested in M5 (M7.22); **Phase 5** graduates to production rendering (M7.23). Each task M7.N is an iteration gated against a KNOWN result; every MODELS.md cell (see **Phase 3** below) is assigned to a task. Columns: **taskID · task title · description (the build) · validation gate** (the credibility anchor). Migrated from the implementation plan (now [`m7_background.md`](m7_background.md)) on 2026-07-01.

## IN PROGRESS

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| [M7.9](tasks/m7_9_chaosbook.md) | ChaosBook study + canonical-exercise benchmark | from the call: build dynamical-systems competency + a self-test the author can trust: select 3-5 canonical exercises with published solutions from Cvitanović's ChaosBook (chaosbook.org; chapter-selection strategy in the task doc, the full book is ~1000 pages), implement headless with unit tests, compare to the known answers; supports the 4-7 book-walkthrough sessions + the Burak Budan review; agent-run (Rodrigo reads TOC + early chapters only, not the bottleneck) | each implemented exercise reproduces its published solution (Poincaré sections, periodic-orbit finding, cycle stability); a benchmark report suitable for the author's review; the orbit-hunting toolkit ready for the M7.10-M7.14 Maxwell track |
| [M7.10](tasks/m7_10_pure_maxwell.md) | Pure-Maxwell sector: the no-Lagrangian test | switch the coupling terms off (`m_J² A·J` and `f(J·J)` zero, leaving plain Maxwell evolution `∂E/∂t = ∇×B`, `∂B/∂t = −∇×E`; the Ouroboros vortex theme stays, only the Lagrangian machinery is removed); four experiments: E1a exact discrete ABC eigenmode (integrator-floor known answer) + E1b Trkalian cavity control (CK spheromak + Dirichlet shell, ≥ 20 periods), E2 free-space evaporation (same seed + sponge boundary), E3 electron destruction as a mechanism comparison (the Phase-1 winner evolved twice from identical data: coupling ON dies by the tachyon in ~2T per M7.5, coupling OFF disperses on the light-crossing time), E4 the coupling ladder (`ε_x`/`ε_q` two-switch scaling: minimizer existence, vacuum growth rate + destruction time vs ε against the pre-registered analytic curve `ω*(ε) = 0.786√ε`); uses the M7.9 orbit toolkit (`find_cycle`/`floquet` on the cavity mode); runs after M7.8 and M7.9 | **Theorem 2 from the closure notes** as a known-answer gate (Trkalian at `ω = cλ₀` solves free Maxwell: period, `λ_eff ≈ 1.0` alignment, energy drift at integrator floor); linear-dispersion escape rate + helicity conservation + Arnold bound in E2; the honest boundary (free-space pure Maxwell holds nothing) as a measurement, not an assertion; the Q14 tachyon attributed to the **bilinear** term specifically (`det M(0) = −ε_x²`) via the ladder + the single-switch points; results into the [walkthrough](tasks/m7_phase1_walkthrough.md) § 7 (one report: M7.8 + M7.9 + M7.10) |

## BACKLOG

## PHASE 1 EXTENSION, reserved band (M7.10-M7.14): the pure-Maxwell / Beltrami orbit track

**M7.10 is now defined** (2026-07-07: the no-Lagrangian test, § IN PROGRESS above); M7.11-M7.14 stay reserved for the Fleury-track work as it firms up (his re-entry is post-August): plain **linear Maxwell evolution** (the `m_J = 0, f = 0` sector of the existing engine, bootstrapped by M7.10), Beltrami / variable-λ ansatz as seeds, a defined notion of a stable orbit in the field flow (the ChaosBook methodology from M7.9), and the static→dynamic charge transition he plans to lead. Two-track principle (2026-07-06): the Maxwell track runs alongside the harmonic/functional track that produced Phase 1, on the same lattice; measurements adjudicate. Honest boundary, stated up front: pure free-space linear Maxwell cannot hold a localized finite-energy state indefinitely (Nadirashvili; our Q11 dispersion work; M7.10 turns this into a measurement), so this track searches and verifies with the variable-λ profile as the localizer, and what sustains that profile (back-reaction) remains the open physics.

## PHASE 2, forces and the remaining particle sectors (M7.15-M7.20)

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.15 | magnetic force | the per-defect magnetic structure carried by the electron's clock (Coulomb already landed in M7.4/M7.6) | magnetic force from the clock's `Γ₀` (pure twist is EM-silent; the M5 mechanism) |
| M7.16 | gravity | the time-axis boost of the field (the M5 4×4 route) | a GEM coupling that vanishes at zero boost; honest pass / fail (Ouroboros stops before gravity, so this is genuinely hard for M7) |
| M7.17 | nuclear forces | strong = the 4th-order short-range roll-off + linking tension; weak = a topology-reconnection (defect-class transition) | running-coupling onset at the core; a reconnection channel; partial, mirroring M5 |
| M7.18 | antimatter + annihilation | **pre-step = the Q14 vacuum-cure check (self-determine, 2026-07-05)**: linearize the vacuum WITH the scalar/Gauss sector (does it lift `det M(0) = −1`?) + test the variable-λ mass profile; then seed a soliton + anti-soliton (`Q → −Q`); evolve | Q14 answered or cured in-model (real-time runs blocked until then); charge ledger `±1 → 0`; rest energy released as outgoing waves; pair → vacuum |
| M7.19 | the lepton + neutrino family | vary knot size / linking: charged = self-linked torus, neutrino = the lighter loop; carries the **Q11 localized-branch hunt** with the 2026-07-05 scan design: the decaying-channel condition `ω²(ω² + λ) < m_c⁴` is `ω < ω*` at canonical `(λ, m_c)` (localization and existence mutually exclusive there), so the scan moves **`(λ, m_c)`**, not `(ω, g)` ([`m7_13_q11_window.py`](scripts/m7_13_q11_window.py) pre-work) | the lepton mass family (μ, τ); light neutral neutrino loops; flavour-rotation mixing; a localized charged branch found or excluded over the `(λ, m_c)` plane |
| M7.20 | dark matter | the **neutral** knot (helicity-only, zero net `∇·F`), inheriting M6's neutral chaoiton | a stable neutral soliton; sub-MeV mass à la M6's `m_χ = 0.460 MeV` |

## PHASE 3, the MODELS.md column (the coverage scoreboard)

A primary deliverable is the **HydroBoros (M7)** column in the repo-root [`MODELS.md`](../../../../MODELS.md) coverage matrix, evaluated against the same shared criteria as M5 / M6 / M4. The column was **drafted at the M7.7 milestone and STAGED in [`preview_models.md`](preview_models.md)** (0✅/8⚠️/13🚧, honest icons; not yet benchmark-ready); the electron cells come from Phase 1, the forces + sector cells from Phase 2, and the task here (M7.21) **publishes**: enters the column via governance (issue + script-backed PR), with the composites cells honestly still 🚧 until Phase 4.

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.21 | complete + govern the MODELS.md column | open the new-model issue; land each of the 21 cells script-backed with honest icons (🚧 → 🔶 → ✅ / ⚠️ / ❌); PR + DCO + light review per governance; includes the **second scheduled refresh of [`m7_theory_canonical.md`](m7_theory_canonical.md)** (the first rides M7.8): publication-grade, METHOD_NOTE-current, self-sufficient for an author audit | all 21 criteria carry an honest, script-backed icon; the M7 column is live in MODELS.md; the canonical spec answers the under-the-hood questions standalone |

The M5 prescription governs every cell:

| Rule | What it means for M7 |
| --- | --- |
| Every cell is **script-backed** | each filled cell links to a runnable `scripts/m7_N_*.py` script (or a research note), reproducible by anyone |
| **Honest status icons** | ✅ validated in-platform · ⚠️ partial / caveats · ❌ tested + failed · 🔶 in progress · 🚧 planned |
| **Negatives are results** | a divergence-ful field that refuses to hold a knot (Q5) lands as a documented ❌, not a silence |
| **The column is earned, cell by cell** | M7 cells start 🚧, go 🔶 during a task, settle to ✅ / ⚠️ / ❌ when the run lands |
| **New-model governance** | M7 is a new column: open an issue first so a maintainer adds it, then a script-backed PR + DCO + light review, per [`MODELS.md`](../../../../MODELS.md) § Contributing, [`ONBOARDING_MODELS.md`](../../../../ONBOARDING_MODELS.md), [`CONTRIBUTING.md`](../../../../CONTRIBUTING.md) |

Each task fills specific cells, so the table is the running scoreboard of the program:

| Task | MODELS.md cells targeted | Backing script |
| --- | --- | --- |
| **M7.1** | (infrastructure, no cell) | `scripts/m7_1_*.py` |
| **M7.2** | Charge quantization · Electron rest energy · Magnetic moment μ + spin J · EM waves (Maxwell) · de Broglie clock | `scripts/m7_2_fleury_torus.py` |
| **M7.3** | Electron rest energy (`H/Q = 1.6969` in full 3D) · Particle stability | `scripts/m7_3_ouroboros_3d.py` |
| **M7.4** | Particle stability (Derrick escape) · Charge quantization (helicity / linking + divergence) · Electric force (Coulomb 1/r, single-charge field) | `scripts/m7_4_linked_vortex.py` |
| **M7.5** | de Broglie clock (Zitterbewegung) · Particle stability | `scripts/m7_5_clock_stability.py` |
| **M7.6** | Magnetic moment μ + spin J · Spin-½ statistics · Quantum wave equation (Klein-Gordon) · Electric force (Coulomb, two-charge `E(d)~1/d`) | `scripts/m7_6_observables.py` |
| **M7.7 (milestone)** | consolidate the column + the M7 deep-dive ([`m7_theory_canonical.md`](m7_theory_canonical.md), the future "Per-model results of record" row) | `scripts/m7_7_canonical.py` + `scripts/m7_functional.py` |
| **M7.8** | Spin-½ statistics · Magnetic moment μ + spin J (the `U₊/U₋` reading) | `scripts/m7_8_helicity_pair.py` |
| **M7.9** | (validation infrastructure, no cell: the ChaosBook benchmark suite) | `scripts/m7_9_chaosbook_*.py` |
| **M7.15** | Magnetic force | `scripts/m7_15_magnetic_force.py` |
| **M7.16** | Gravity | `scripts/m7_16_gravity.py` |
| **M7.17** | Strong force / confinement · Weak force | `scripts/m7_17_nuclear_forces.py` |
| **M7.18** | Antimatter + annihilation | `scripts/m7_18_annihilation.py` |
| **M7.19** | Neutrinos · Lepton mass spectrum (μ, τ) | `scripts/m7_19_lepton_neutrino.py` |
| **M7.20** | Dark matter candidate | `scripts/m7_20_dark_matter.py` |
| **M7.22** | Quarks · Baryons (p, n) · Mesons (π, K) · Orbital quantization | `scripts/m7_22_composites.py` |

All 21 MODELS.md criteria are covered: Phase 1 (M7.0-M7.7) earns the electron cells, **including Coulomb** (tied to the electron's charge, M5-style), and drafts + stages the column at the M7.7 milestone ([`preview_models.md`](preview_models.md)); Phase 2 (M7.15-M7.20) fills the remaining forces (magnetic, gravity, nuclear) + annihilation / neutrinos / dark matter, opening with the M7.8 helicity-pair check of the Fleury closure notes; Phase 3 (M7.21) publishes the column; Phase 4 (M7.22) fills the cells still 🚧 in M5 (quarks, baryons, mesons, orbital quantization). Each task upgrades its cells from 🚧 to a verified icon, as M5's column grew.

## PHASE 4, the composites still untested in M5, grouped (M7.22)

Per the M5 prescription, the cells that remain 🚧 [not yet tested] in M5 itself are grouped into one later task, after the column is published. They depend on the electron + force primitives of Phases 1-2 already being in place.

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.22 | composites + atomic structure | quark = fractional-charge string segment; baryon / meson = linked / twisted knots; atom = pilot-wave orbital quantization | Quarks · Baryons (p, n) · Mesons (π, K) · Orbital quantization |

## PHASE 5, production rendering upgrade (post-canonical)

After the electron is canonical (the M7.7 milestone), graduate the winning recipe from the research scripts to the production engine, exactly the path M5 followed.

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.23 | graduate to the production engine + rendering | fold the canonical recipe (M7.7) into `medium.py` + `engine1_seeds` / `engine2_pde` / `engine3_observables` / `engine4_render` + `_launcher.py`; the Phase 2 + 4 observables feed the renderer as they land | HydroBoros runs via `openwave -x` with toroidal field-line / vorticity rendering; first-try reproducible |

```text
research/scripts/ data/ plots/   headless Taichi scripts + data + PNG diagnostics   (tasks M7.1-M7.22)
research/tasks/                  per-task detail docs  m7_N_*.md
        │  winning recipe →
medium.py                  the (A,J) / RS substrate definition
engine1_seeds.py           Bateman/Hopf + toroidal-Beltrami seeders
engine2_pde.py             the nonlinear PDE evolution + minimizer
engine3_observables.py     charge (∇·F), helicity, energy, spin, μ
engine4_render.py          toroidal field-line / vorticity rendering
_launcher.py               registers HydroBoros for `openwave -x`
```

Reference layout: [`../../m5_liquid_crystal/`](../../m5_liquid_crystal/) (`medium.py`, `engine1_seeds.py` … `_launcher.py`). Headless first (matplotlib PNG diagnostics in `research/plots/`); rendering graduates once the electron is canonical (the M7.7 milestone), and the Phase 2 + 4 coverage tasks feed their observables into the renderer as they land, identical to how M5 reached `_launcher.py`. No GUI / viz work before the physics is canonical.

## DONE

## PHASE 1 EXTENSION, the author-collaboration track (M7.8 ✅; M7.9/M7.10 still queued above)

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| [M7.8](tasks/m7_8_helicity_pair.md) | helicity-pair 3:1 test + the Phase 1 walkthrough (Fleury closure) | the three-deliverable Phase 1 extension task: (a) the amplitude-ratio ladder on the repaired CK/LG helicity pair at fixed `(Q_can, H_A)`; (b) the under-the-hood [walkthrough](tasks/m7_phase1_walkthrough.md); (c) the canonical-spec refresh #1 | ✅ DELIVERED (2026-07-07, [findings](tasks/m7_8_helicity_pair.md)): machinery gates green (helical split Parseval **1.5e-16** incl. the new longitudinal/charge bucket; projector 93.5%, sign gate caught a left-handed-frame bug); **the closure pair is NOT stationary at any seeded asymmetry**: the minus mode is expelled at all 5 rungs (asym 0.981 → 0.998, `U₊/U₋` 104 → 1077 vs the predicted 3), the states converge to the Phase 1 electron family (`E/\|H_A\|` → 0.808), so the **pair-asymmetry spin reads one quantum, not ℏ/2** (the ℏ/2 route shifts to the frequency mapping); **adversarial audit CONFIRMED** (`dE ∝ +ε²` under minus re-insertion); grid-converged (96³: asym identical, E shift 0.57%); walkthrough §§ 2-8 filled + canonical refresh #1 applied; the author package awaits M7.9 + M7.10 (§ 7 completes, then it ships for his external pass) |

## PHASE 1, the electron and the M7 column (M7.0-M7.7) ✅ DONE 2026-07-04

M7.1-M7.3 are the decisive credibility gates (reproduce **both** parents from the same lattice code). M7.4 is the research core (the thing neither parent did). **M7.7 is the milestone: the column drafted + STAGED in [`preview_models.md`](preview_models.md); publication = M7.21 (Phase 3).** Note: **Coulomb rides with the electron**, not as a later forces task: once the divergence charge `∇·F` exists (M7.4), its `1/r` field is immediate (Gauss's law), and the two-body `E(d) ~ 1/d` is confirmed at M7.6, exactly as M5 got Coulomb in its first `m5_1` milestone.

**Method frame (2026-07-02 plan refactor, [`m7_background.md § 5`](m7_background.md)).** Both parents are time-periodic, so the whole Phase 1 runs in the **time-harmonic (fixed-ω) frame**: the minimizer works on the period-averaged functional `E_ω` at fixed ω, and the de Broglie clock is in the soliton from M7.1 (M7.5 validates it in real time). Stabilization = **helicity anti-collapse + Ouroboros confinement anti-expansion** (the drafted Faddeev-Niemi term is inert on Beltrami fields and demoted to an optional Q2 experiment). **Sequencing note:** M7.2 is pure quadrature (no minimizer), so it can run in parallel with the M7.1 minimizer build and land the first trust-builder early; M7.3's verbatim-ODE pre-gate must pass before any 3D relaxation run is trusted.

**Prescription (Jarek Duda, 2026-06-29 models-of-particles thread; Ouroboros [#247](https://github.com/openwave-labs/openwave/issues/247)).** Standing demand of any particle-model framework: *specify the field configuration of each particle* (electron, neutrino, photon, mesons, baryons), and *does it use topological vortices?* HydroBoros answers head-on, the electron's field configuration **is** the self-linked toroidal Beltrami vortex ([`m7_background.md § 0`](m7_background.md)), a topological vortex. His two concrete tests map onto the plan exactly:

| Test | What it prescribes | M7 task |
| --- | --- | --- |
| **Coulomb** | assume **two** charge field-configurations, read the `1/r` interaction energy `E(d)` | M7.4 (single-charge `1/r`) + M7.6 (two-charge `E(d)~1/d`), the M5 `m5_1` way |
| **the clock** | the de Broglie frequency is the one that **minimizes the energy** | M7.5 (clock + stability), = the M5.8 energy-minimizing-clock mechanism |

His deeper point, that pinning the field configurations is the **precondition to passing OpenWave's tests** (not assuming them = "just hallucinations"), is precisely M7's premise: M7 specifies the config (the toroidal Beltrami seed) **and** earns it as the energy-minimizer of the functional ([`m7_background.md § 5`](m7_background.md)), then reads observables off the relaxed field. That sidesteps the Werbos-vs-Duda "assume vs predict" tension in the thread (M7 does both: a seeded config, relaxed to the true minimum).

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| [M7.0](tasks/m7_0_bootstrap.md) | bootstrap | Collect the theory-source corpus (Fleury torus, Ouroboros/M6, Beltrami/Trkalian, Marc's evolving `electron_beltrami/` library, 66 docs as of 2026-07-05) and stand up the planning scaffolding (background, question-tracker, roadmap, the `research/` folder structure). | ✅ corpus consolidated (64 docs) in [`../theory/`](../theory/) + [manifest](../theory/_CITATIONS.md); plan + roadmap + tracker in place (2026-07-02) |
| [M7.1](tasks/m7_1_infra.md) | infra | A-primary doublet on a 3D lattice in the **time-harmonic (fixed-ω) frame**; helicity observable + fixed-helicity relaxation; Taichi-AD energy gradient; FIRE minimizer; six seeders (ABC/Trkalian, CK spheromak, Bateman/Hopf, Fleury torus, M6 embedding, Ceperley mode); design decisions documented (BCs, gauge = Q8 evidence, M6 natural units) | ✅ ALL GATES PASS (2026-07-02, [findings](tasks/m7_1_infra.md)): AD vs complex-step `2.3e-15`; **Woltjer-Taylor**: random seed → constant-λ eigenfield, `λ → 2π/L` at `5.5e-6`, `E = λH`; M6 ledger `H/Q = 1.68897` reproduced by the seeder pipeline |
| [M7.2](tasks/m7_2_fleury_torus.md) | reproduce Fleury on the lattice | lattice quadrature of the FLDB toroidal ansatz under the pinned conventions contract; grid-convergence study; Bessel-envelope stretch | ✅ ALL GATES PASS (2026-07-02, [findings](tasks/m7_2_fleury_torus.md)): `Q/μ/L/U` to closed forms at `1.4e-4`, order ~2.5; printed solution reconstructed digit-for-digit; **Q10 finding: corrected-convention `U = 0.958 m_ec²`** (was 0.795); the Bessel stretch exposed the mask's hidden surface charge (~18× bulk) |
| [M7.3](tasks/m7_3_ouroboros_3d.md) | reproduce M6's electron in full 3D | **pre-gate first**: the 3D harmonic functional, restricted to M6's ansatz, reproduces the M6 ODE **verbatim**; then embed the M6 1D profile as a 3D seed, relax at fixed ω, watch for 3D symmetry breaking | ✅ ALL GATES (2026-07-03, [findings](tasks/m7_3_ouroboros_3d.md)): verbatim reduction pinned (same-phase doublet; `κ = −1`; FOCUSING `f`; fixed-`Q_can` frame); 3D windowed `H/Q = 1.68889` vs ledger `1.68897` (dev **4.7e-5**); 3 discoveries: the charged ledger is **WINDOWED** (Q11), `0d_canonical § 2.2` is not an EL reduction (Q12), the M6 electron is a **3D saddle with focusing collapse**, helicity guard inert on it (Q13); Q8 resolved (no gauge fixing needed) |
| [M7.4](tasks/m7_4_charged_soliton.md) | the charged soliton (approximately-Beltrami) + its Coulomb field (NEW physics) | relax the full functional from multiple seeds at fixed ω + helicity; charge = the measured `∇·F`, never an imposed exact variable-λ ansatz; diagnostic `λ_eff` | ✅ PRIMARY GATE PASS (2026-07-03, [findings](tasks/m7_4_charged_soliton.md)): **first stable finite-size 3D soliton**: a Taylor-dressed spheromak family, `E = 0.802\|H_A\|`, `H_cross = −0.390 H_A` universal across 3 seeds; helicity load-bearing (zero-helicity seeds evaporate); **written `f` wins** (focusing benchmark signs expel charge / collapse); RMS charge interior + persistent; ⚠️ net-Gauss charge + Coulomb deferred (scalar-sector instability finding); topology reconnects under global-H (knot sectors = follow-up); Q2 + Q5 resolved |
| [M7.5](tasks/m7_5_clock_stability.md) | validate the clock (real-time) + stability | Minkowski leapfrog evolution of the relaxed harmonic states: validates the reduction in real time; probe the Werbos-v5 `β*` vacuum-stability threshold | ✅/❌ SPLIT, honest (2026-07-03, [findings](tasks/m7_5_clock_stability.md)): translation exact (`⟨E_real⟩ = E_ω` to 1.85e-14; O(dt²) conservation) and the reduction vindicated (3ω leakage 0.2%; Legendre gate `dE*/dω = Q_can` to ~1-2%), BUT the vacuum is **unconditionally tachyonic** at long wavelength (`det M(0) = −1`; measured rate 0.785 vs 0.786 analytic; **no `β*` threshold**: **Q14 opened**); solitons exist only above **`ω* = 0.786`** (threshold measured, bracketed 0.75-0.79: the clock IS the stabilizer); the M7.4 winner is a standing doublet → M7.6 runs fixed-`Q_can` + rotating seeds; Q6 RESOLVED-empirical |
| [M7.6](tasks/m7_6_observables.md) | electron observables | mass = field energy; spin (Ceperley cross-check); μ; KG; two-charge Coulomb `E(d)`; M7.5 design inputs (fixed-`Q_can` + `H_A` frame, rotating seeds) | ✅ 6 of 7 gates (2026-07-03, [findings](tasks/m7_6_observables.md)): **the rotating electron candidate** (blend_m1, E = 6.3246, `\|g\| = 1.6e-7`) is a clean **`j_z = 1` per-quantum wave (0.6%)**; **Coulomb landed** (fixed-reservoir prescription self-resolved: Gauss 99.1%, far field −2.14, two-charge `1/d` reference-matched with a measured **1.17 dressing**); oscillatory RKKY exchange discovered in the neutral channel; KG exact (`m_eff² = φ`); 🔶 μ charge-unit-blocked (scalar sector); ℏ/2-vs-ℏ → the M7.7 units contract |
| [M7.7](tasks/m7_7_consolidation.md) | consolidate the M7 column (MILESTONE) | canonical spec + small auditable physics module (METHOD_NOTE standard); the 21-cell column; units-contract decision table; both comms packages | ✅ MILESTONE (2026-07-04, [findings](tasks/m7_7_consolidation.md)): [`m7_theory_canonical.md`](m7_theory_canonical.md) (equations first) + `m7_functional.py` (~200 lines) + `m7_7_canonical.py` **all-gates-pass first-try at N = 64 AND N = 48, engine-vs-reference 1.4e-14**; the column drafted honestly (0✅/8⚠️/13🚧) and **STAGED in [`preview_models.md`](preview_models.md)** (review decision: benchmark entry deferred to M7.21; MODELS.md untouched); comms packages ready (W: Q14-led · M: Q7-led) |

---

Artifacts follow the `research/` structure: scripts in [`scripts/`](scripts/), data in [`data/`](data/), plots in [`plots/`](plots/), per-task detail docs in [`tasks/`](tasks/), all named `m7_N_*.{py,npz,png,md}` (e.g. `scripts/m7_1_harmonic_lattice.py`, `scripts/m7_2_fleury_torus.py`, … `scripts/m7_22_composites.py`). Cross-refs: [`m7_background.md`](m7_background.md) (full background: § 5 dynamics; the MODELS.md cell map + production path are **Phases 3 + 5** above), the open questions + risks in [`m7_question_tracker.md`](m7_question_tracker.md), the Phase 1 report [`tasks/m7_phase1_report.md`](tasks/m7_phase1_report.md), the column preview [`preview_models.md`](preview_models.md), the MODELS.md publication goal at repo-root [`MODELS.md`](../../../../MODELS.md).
