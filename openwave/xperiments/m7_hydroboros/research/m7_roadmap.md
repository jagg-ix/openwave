# M7 / HydroBoros, roadmap

> Local task roadmap for the **M7 (HydroBoros)** model, replicating the SABER science-roadmap structure (2026-07-01). M7 has **no GitHub issues**; tasks are tracked here. **taskID = M7.N**. Full planning + findings live in each [`tasks/m7_N_*.md`](tasks/) detail doc; scripts / data / plots live in [`scripts/`](scripts/) · [`data/`](data/) · [`plots/`](plots/), all named `m7_N_*.{py,npz,png}`. Ordering is the build sequence (M7.0 → M7.14, then Phases D-E); the **top of Backlog is the next task**.
>
> The program runs in five **phases** (formerly "arcs"): **A** builds the electron and earns the MODELS.md column (M7.1-M7.7), **B** expands across the forces and the remaining particle sectors (M7.8-M7.13), **C** groups the composites still untested in M5 (M7.14), **D** completes + governs the MODELS.md column, and **E** graduates to production rendering. Each task M7.N is an iteration gated against a KNOWN result; every MODELS.md cell (see **Phase D** below) is assigned to a task. Columns: **taskID · task title · description (the build) · validation gate** (the credibility anchor). Migrated from the implementation plan (now [`m7_background.md`](m7_background.md)) on 2026-07-01.

## IN PROGRESS

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| [M7.4](tasks/m7_4_charged_soliton.md) | the charged soliton (approximately-Beltrami) + its Coulomb field (NEW physics) | relax the full functional from **multiple seeds** (Trkalian eigenfield torus, Bateman/Hopf knots, the M6-embedded torus) at fixed ω + helicity; **charge = the measured `∇·F` the coupling drives**, NOT an imposed exact variable-λ ansatz (rigidity + Nadirashvili, [`m7_background.md § 2`](m7_background.md)); diagnostic `λ_eff = F·(∇×F)/\|F\|²` | stable finite-size soliton (`‖∇E‖ → 0` + a **dilation probe**: `E(μ)` has an interior minimum); **the Q3 deliverable**: `(Q_div, helicity H, linking)` measured on every relaxed state; **Coulomb `1/r`** far field sourced by `Q_div` (Gauss); charge quantization assessed honestly |

## BACKLOG

### Phase A, the electron and the M7 column (M7.1-M7.7)

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| [M7.5](tasks/m7_5_clock_stability.md) | validate the clock (real-time) + stability | Minkowski leapfrog evolution of the relaxed harmonic states: the clock is IN the soliton from M7.1 (§ 5a), this task **validates the reduction in real time**; probe the Werbos-v5 **`β*` vacuum-stability threshold** | persists many periods, no collapse mode; emergent `ω` matches the input harmonic `ω`; `ω` vs Dirac `ω_D` reported; energy conserved to integrator tolerance |
| [M7.6](tasks/m7_6_observables.md) | electron observables | mass = field energy; spin `ℏ/2` (cross-checked vs Ceperley's rotating-wave law `L_z = mU/ω`); `μ_B(1 + α/2π)`; the Klein-Gordon twist sector; **two-charge Coulomb `E(d) ~ 1/d`** | the 4-observable electron (mass, charge, μ, spin) + KG + the two-body force law, from the relaxed field; **stretch: extract `α_sol` from `E(d)` vs Faber & Golubich `α⁻¹ ≈ 137.1`** |
| M7.7 | consolidate the M7 column (MILESTONE) | fold the winning recipe into a `canonical.md`-style spec; **add HydroBoros (M7) to MODELS.md** | one runnable canonical script, reproducible first-try; the electron cells land as the new column |

M7.1-M7.3 are the decisive credibility gates (reproduce **both** parents from the same lattice code). M7.4 is the research core (the thing neither parent did). **M7.7 is the milestone: the M7 column exists in MODELS.md.** Note: **Coulomb rides with the electron**, not as a later forces task: once the divergence charge `∇·F` exists (M7.4), its `1/r` field is immediate (Gauss's law), and the two-body `E(d) ~ 1/d` is confirmed at M7.6, exactly as M5 got Coulomb in its first `m5_1` milestone.

**Method frame (2026-07-02 plan refactor, [`m7_background.md § 5`](m7_background.md)).** Both parents are time-periodic, so the whole Phase A runs in the **time-harmonic (fixed-ω) frame**: the minimizer works on the period-averaged functional `E_ω` at fixed ω, and the de Broglie clock is in the soliton from M7.1 (M7.5 validates it in real time). Stabilization = **helicity anti-collapse + Ouroboros confinement anti-expansion** (the drafted Faddeev-Niemi term is inert on Beltrami fields and demoted to an optional Q2 experiment). **Sequencing note:** M7.2 is pure quadrature (no minimizer), so it can run in parallel with the M7.1 minimizer build and land the first trust-builder early; M7.3's verbatim-ODE pre-gate must pass before any 3D relaxation run is trusted.

**Prescription (Jarek Duda, 2026-06-29 models-of-particles thread; Ouroboros [#247](https://github.com/openwave-labs/openwave/issues/247)).** Standing demand of any particle-model framework: *specify the field configuration of each particle* (electron, neutrino, photon, mesons, baryons), and *does it use topological vortices?* HydroBoros answers head-on, the electron's field configuration **is** the self-linked toroidal Beltrami vortex ([`m7_background.md § 0`](m7_background.md)), a topological vortex. His two concrete tests map onto the plan exactly:

| Test | What it prescribes | M7 task |
| --- | --- | --- |
| **Coulomb** | assume **two** charge field-configurations, read the `1/r` interaction energy `E(d)` | M7.4 (single-charge `1/r`) + M7.6 (two-charge `E(d)~1/d`), the M5 `m5_1` way |
| **the clock** | the de Broglie frequency is the one that **minimizes the energy** | M7.5 (clock + stability), = the M5.8 energy-minimizing-clock mechanism |

His deeper point, that pinning the field configurations is the **precondition to passing OpenWave's tests** (not assuming them = "just hallucinations"), is precisely M7's premise: M7 specifies the config (the toroidal Beltrami seed) **and** earns it as the energy-minimizer of the functional ([`m7_background.md § 5`](m7_background.md)), then reads observables off the relaxed field. That sidesteps the Werbos-vs-Duda "assume vs predict" tension in the thread (M7 does both: a seeded config, relaxed to the true minimum).

### Phase B, forces and the remaining particle sectors (M7.8-M7.13)

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.8 | magnetic force | the per-defect magnetic structure carried by the electron's clock (Coulomb already landed in M7.4/M7.6) | magnetic force from the clock's `Γ₀` (pure twist is EM-silent; the M5 mechanism) |
| M7.9 | gravity | the time-axis boost of the field (the M5 4×4 route) | a GEM coupling that vanishes at zero boost; honest pass / fail (Ouroboros stops before gravity, so this is genuinely hard for M7) |
| M7.10 | nuclear forces | strong = the 4th-order short-range roll-off + linking tension; weak = a topology-reconnection (defect-class transition) | running-coupling onset at the core; a reconnection channel; partial, mirroring M5 |
| M7.11 | antimatter + annihilation | seed a soliton + anti-soliton (`Q → −Q`); evolve | charge ledger `±1 → 0`; rest energy released as outgoing waves; pair → vacuum |
| M7.12 | the lepton + neutrino family | vary knot size / linking: charged = self-linked torus, neutrino = the lighter loop | the lepton mass family (μ, τ); light neutral neutrino loops; flavour-rotation mixing |
| M7.13 | dark matter | the **neutral** knot (helicity-only, zero net `∇·F`), inheriting M6's neutral chaoiton | a stable neutral soliton; sub-MeV mass à la M6's `m_χ = 0.460 MeV` |

### Phase C, the composites still untested in M5, grouped (M7.14)

Per the M5 prescription, the cells that remain 🚧 [not yet tested] in M5 itself are grouped into one later task, after the column is consolidated. They depend on the electron + force primitives of phases A-B already being in place.

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.14 | composites + atomic structure | quark = fractional-charge string segment; baryon / meson = linked / twisted knots; atom = pilot-wave orbital quantization | Quarks · Baryons (p, n) · Mesons (π, K) · Orbital quantization |

### Phase D, the MODELS.md column (the coverage scoreboard)

A primary deliverable is the **HydroBoros (M7)** column in the repo-root [`MODELS.md`](../../../../MODELS.md) coverage matrix, evaluated against the same shared criteria as M5 / M6 / M4. This phase is the running **scoreboard**: most cells are earned by the Phase A-C tasks and the column is stood up at the M7.7 milestone; the task here (M7.15) is completing + governing the full 21-cell column.

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.15 | complete + govern the MODELS.md column | open the new-model issue; land each of the 21 cells script-backed with honest icons (🚧 → 🔶 → ✅ / ⚠️ / ❌); PR + DCO + light review per governance | all 21 criteria carry an honest, script-backed icon; the M7 column is live in MODELS.md |

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
| **M7.7 (milestone)** | consolidate the column + the M7 deep-dive (a `0d_canonical.md`, the "Per-model results of record" row) | `scripts/m7_7_*.py` |
| **M7.8** | Magnetic force | `scripts/m7_8_magnetic_force.py` |
| **M7.9** | Gravity | `scripts/m7_9_gravity.py` |
| **M7.10** | Strong force / confinement · Weak force | `scripts/m7_10_nuclear_forces.py` |
| **M7.11** | Antimatter + annihilation | `scripts/m7_11_annihilation.py` |
| **M7.12** | Neutrinos · Lepton mass spectrum (μ, τ) | `scripts/m7_12_lepton_neutrino.py` |
| **M7.13** | Dark matter candidate | `scripts/m7_13_dark_matter.py` |
| **M7.14** | Quarks · Baryons (p, n) · Mesons (π, K) · Orbital quantization | `scripts/m7_14_composites.py` |

All 21 MODELS.md criteria are covered: Phase A (M7.1-M7.7) earns the electron cells, **including Coulomb** (tied to the electron's charge, M5-style), and consolidates the column at the M7.7 milestone; Phase B (M7.8-M7.13) fills the remaining forces (magnetic, gravity, nuclear) + annihilation / neutrinos / dark matter; Phase C (M7.14) groups the cells still 🚧 in M5 (quarks, baryons, mesons, orbital quantization). Each task upgrades its cells from 🚧 to a verified icon, as M5's column grew.

### Phase E, production rendering (post-canonical)

After the electron is canonical (the M7.7 milestone), graduate the winning recipe from the research scripts to the production engine, exactly the path M5 followed.

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| M7.16 | graduate to the production engine + rendering | fold the canonical recipe (M7.7) into `medium.py` + `engine1_seeds` / `engine2_pde` / `engine3_observables` / `engine4_render` + `_launcher.py`; the Phase B-C observables feed the renderer as they land | HydroBoros runs via `openwave -x` with toroidal field-line / vorticity rendering; first-try reproducible |

```text
research/scripts/ data/ plots/   headless Taichi scripts + data + PNG diagnostics   (tasks M7.1-M7.14)
research/tasks/                  per-task detail docs  m7_N_*.md
        │  winning recipe →
medium.py                  the (A,J) / RS substrate definition
engine1_seeds.py           Bateman/Hopf + toroidal-Beltrami seeders
engine2_pde.py             the nonlinear PDE evolution + minimizer
engine3_observables.py     charge (∇·F), helicity, energy, spin, μ
engine4_render.py          toroidal field-line / vorticity rendering
_launcher.py               registers HydroBoros for `openwave -x`
```

Reference layout: [`../../m5_liquid_crystal/`](../../m5_liquid_crystal/) (`medium.py`, `engine1_seeds.py` … `_launcher.py`). Headless first (matplotlib PNG diagnostics in `research/plots/`); rendering graduates once the electron is canonical (the M7.7 milestone), and the Phase B-C coverage tasks feed their observables into the renderer as they land, identical to how M5 reached `_launcher.py`. No GUI / viz work before the physics is canonical.

## DONE

| TaskID | Task title | Description | Validation gate |
| --- | --- | --- | --- |
| [M7.3](tasks/m7_3_ouroboros_3d.md) | reproduce M6's electron in full 3D | **pre-gate first**: the 3D harmonic functional, restricted to M6's ansatz, reproduces the M6 ODE **verbatim**; then embed the M6 1D profile as a 3D seed, relax at fixed ω, watch for 3D symmetry breaking | ✅ ALL GATES (2026-07-03, [findings](tasks/m7_3_ouroboros_3d.md)): verbatim reduction pinned (same-phase doublet; `κ = −1`; FOCUSING `f`; fixed-`Q_can` frame); 3D windowed `H/Q = 1.68889` vs ledger `1.68897` (dev **4.7e-5**); 3 discoveries: the charged ledger is **WINDOWED** (Q11), `0d_canonical § 2.2` is not an EL reduction (Q12), the M6 electron is a **3D saddle with focusing collapse**, helicity guard inert on it (Q13); Q8 resolved (no gauge fixing needed) |
| [M7.2](tasks/m7_2_fleury_torus.md) | reproduce Fleury on the lattice | lattice quadrature of the FLDB toroidal ansatz under the pinned conventions contract; grid-convergence study; Bessel-envelope stretch | ✅ ALL GATES PASS (2026-07-02, [findings](tasks/m7_2_fleury_torus.md)): `Q/μ/L/U` to closed forms at `1.4e-4`, order ~2.5; printed solution reconstructed digit-for-digit; **Q10 finding: corrected-convention `U = 0.958 m_ec²`** (was 0.795); the Bessel stretch exposed the mask's hidden surface charge (~18× bulk) |
| [M7.1](tasks/m7_1_infra.md) | infra | A-primary doublet on a 3D lattice in the **time-harmonic (fixed-ω) frame**; helicity observable + fixed-helicity relaxation; Taichi-AD energy gradient; FIRE minimizer; six seeders (ABC/Trkalian, CK spheromak, Bateman/Hopf, Fleury torus, M6 embedding, Ceperley mode); design decisions documented (BCs, gauge = Q8 evidence, M6 natural units) | ✅ ALL GATES PASS (2026-07-02, [findings](tasks/m7_1_infra.md)): AD vs complex-step `2.3e-15`; **Woltjer-Taylor**: random seed → constant-λ eigenfield, `λ → 2π/L` at `5.5e-6`, `E = λH`; M6 ledger `H/Q = 1.68897` reproduced by the seeder pipeline |
| [M7.0](tasks/m7_0_bootstrap.md) | bootstrap | Collect the theory-source corpus (Fleury torus, Ouroboros/M6, Beltrami/Trkalian, Marc's evolving `electron_beltrami/` library, now 64 docs) and stand up the planning scaffolding (background, question-tracker, roadmap, the `research/` folder structure). | ✅ corpus consolidated (64 docs) in [`../theory/`](../theory/) + [manifest](../theory/_CITATIONS.md); plan + roadmap + tracker in place (2026-07-02) |

---

Artifacts follow the `research/` structure: scripts in [`scripts/`](scripts/), data in [`data/`](data/), plots in [`plots/`](plots/), per-task detail docs in [`tasks/`](tasks/), all named `m7_N_*.{py,npz,png,md}` (e.g. `scripts/m7_1_minimizer.py`, `scripts/m7_2_fleury_torus.py`, … `scripts/m7_14_composites.py`). Cross-refs: [`m7_background.md`](m7_background.md) (full background: § 5 dynamics; the MODELS.md cell map + production path are **Phases D-E** above), the open questions + risks in [`m7_question_tracker.md`](m7_question_tracker.md), the MODELS.md column goal at repo-root [`MODELS.md`](../../../../MODELS.md).
