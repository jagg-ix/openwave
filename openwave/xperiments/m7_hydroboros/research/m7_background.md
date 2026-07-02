# M7 / HydroBoros - Background

  ![hydroboros_icon](../images/hydroboros_icon_small.jpg)

> **Purpose.** Build a rigorous **full 3D PDE simulation** of the electron as a
> self-linked toroidal vortex, blending the **hydrodynamics school** (Marc Fleury's toroidal
> electromagnetic electron + the Beltrami / force-free field tradition) with the **Ouroboros
> model** (Paul Werbos's coupled two-vector-field chaoiton, M6). HydroBoros = Hydrodynamics +
> Ouroboros, also evoking the mythological **Hydra**, the water snake. Both are built on **M5 (Liquid
> Crystal, Duda) as the third source**: M7 inherits OpenWave's M5-proven lattice + energy-minimizer,
> M5's physics primitives, and M5's development workflow (the [`m7_roadmap.md`](m7_roadmap.md) + [`m7_question_tracker.md`](m7_question_tracker.md)).
>
> The work runs headless in
> `research/` (scripts/, data/, plots/, tasks/; Taichi GPU lattice, energy minimizer, matplotlib diagnostics),
> converges to a canonical form, then graduates into the production `medium.py` + `engine1-4` +
> `_launcher.py` for visual rendering, exactly the path M5 followed.
> A primary deliverable is the **HydroBoros (M7) column** of the repo-root
> [`MODELS.md`](../../../../MODELS.md) coverage matrix, every cell backed by a runnable in-platform
> script, the same bar M5 meets (see the [roadmap](m7_roadmap.md) Phase D).
> Rigor standard: [`../../m5_liquid_crystal/research/11a_vortex_loop.md`](../../m5_liquid_crystal/research/11a_vortex_loop.md) (M5.11).
> Theory sources: [`../theory/`](../theory/). Findings as we execute: `research/scripts/`, `research/data/`, `research/plots/`, tracked in [`m7_roadmap.md`](m7_roadmap.md).

---

## 0. The sources , two physics parents + the M5 method

| Source | Substrate | How it is solved today | Charge origin | Role in M7 |
| --- | --- | --- | --- | --- |
| **Fleury** (hydrodynamics school), [arXiv:2510.22384](https://arxiv.org/abs/2510.22384) | EM field `E, B` confined to a torus | closed-form **analytic** ansatz + Heaviside mask | `ρ = ∇·E` (geometric / divergence charge) | physics parent; limit: mask unphysical at boundary, energy `0.795 m_e c²`, **no dynamics/PDE** |
| **Werbos Ouroboros** (M6), [`0d_canonical.md`](../../m6_ouroboros/research/0d_canonical.md) | **double vector field** `(A_μ, J_μ)` | **reduced 1D ODE / BVP** (cylindrical `(α,β)`; spherical `l=1`) | `Q_CS` = Chern-Simons **linking** number | physics parent; limit: never a full **3D** field, electron only a radial profile (`H/Q = 1.6969`) |

The honest gap the two physics parents share: **neither has ever been evolved as a full 3D nonlinear
PDE on a lattice.** Fleury is analytic; M6 is a 1D radial reduction. That is exactly the gap M5.11
closed for the tensor model (Taichi-AD lattice + FIRE / L-BFGS minimizer, reproduce Faber's electron
from the relaxed 3D field). **M7's contribution is to build the rigorous 3D PDE simulation neither
parent did**, with the toroidal vortex as the soliton sector.

## 1. M5 as a reference structure

**M5 as a reference** (Liquid Crystal, Duda) , the **method + rigor** source | 3×3 / 4×4 tensor field `M = ODO^T` | **full 3D Taichi-AD lattice + FIRE / L-BFGS minimizer** (M5.11) | topological winding (Gauss-Bonnet integer) | M7 borrows the **method + engine + workflow + physics primitives**, not the substrate

**M5 is the third source , for its proven method, not its substrate.** M7 is built on OpenWave's
M5-validated lattice + energy-minimizer and inherits M5's physics primitives (the **4th-order term
that evades Derrick**, the **energy-minimizing de Broglie clock** of M5.8, **Coulomb-from-topology**,
**particle-as-field-configuration**), and adopts M5's development **workflow** (roadmap + GitHub
issues + question tracker + research→canonical→production + AI-reviewer passes + the 11a rigor standard,
detailed in the [`m7_roadmap.md`](m7_roadmap.md) + [`m7_question_tracker.md`](m7_question_tracker.md)). M5 is OpenWave's most validated model (16 MODELS.md cells), so it is the natural template for
getting M7 to the same bar.

| Rigor | Details |
| --- | --- |
| **AI-reviewer pass** | every canonical recipe + MODELS.md cell goes through an AI code-review (`/code-review`) before merge , the quality gate M5 uses |
| **11a rigor standard** ([`11a_vortex_loop.md`](../../m5_liquid_crystal/research/11a_vortex_loop.md)) | energy-minimizer to `‖∇E‖ → 0`, AD-validated gradient (`1e-12`), each task gated against a known result, honest pass/fail (§ 5, the [roadmap](m7_roadmap.md)) |

**The wider OpenWave wave-physics library (M1-M4) , mine for insights, not a source.** HydroBoros is
fundamentally a *wave* model (rotating waves, EM waves, Beltrami flows, knotted light), and the other
OpenWave models carry a deep body of wave physics a coding agent should consult: **M1**
([`m1_granule_motion`](../../m1_granule_motion/)) , granule-motion wave propagation (standing /
traveling / spherical / energy waves); **M2** ([`m2_free_wave`](../../m2_free_wave/)) , free-wave
dynamics; **M3** ([`m3_wolff_lafreniere`](../../m3_wolff_lafreniere/)) , Wolff-LaFreniere
wave-structure-of-matter (standing-wave centers, interference → particles); **M4**
([`m4_ewt`](../../m4_ewt/)) , Jeff Yee's Energy Wave Theory (wave constants + equations). These are
**not parents** (they do not define HydroBoros's substrate), but their wave-decomposition,
interference, and wave-center primitives bear directly on the M7 **seeders** (task M7.1, [roadmap](m7_roadmap.md)) and the
wave-propagation layer of the PDE , consult them when building those.

## 2. The HydroBoros thesis

The Ouroboros "snake eating its tail" is a **self-linked toroidal vortex**. Fleury's toroidal EM
wave is what that vortex looks like in the hydrodynamic / Maxwell reading. The **Beltrami**
(force-free) condition `∇×F = λ F` is the steady, self-sustaining circulation that ties the two
together: it is simultaneously Fleury's monochromatic toroidal eigenmode (`ω = 2c/R₀`) and the
Ouroboros self-confinement. The bridge is already documented inside M5 (Fleury's Navier-Stokes ≡
generalized-Maxwell equivalence, Duda's superfluid mapping): see
[`../../m5_liquid_crystal/research/1b_topological_defect.md`](../../m5_liquid_crystal/research/1b_topological_defect.md)
§ "EM-hydrodynamics formal equivalence".

### Trkalian vs Beltrami: where the charge lives (Marc, 2026-06-30)

A Beltrami field `∇×w = λw` splits on whether the proportionality factor `λ` is constant. Taking the
divergence of both sides (`∇·(∇×w) = 0`) gives `∇λ·w + λ ∇·w = 0`, so:

| Case | `λ` | Divergence | Charge |
| --- | --- | --- | --- |
| **Trkalian** | constant | `∇·w = 0` (solenoidal, forced) | none |
| **general Beltrami** | variable `λ(x)` | `∇·w = −(∇λ·w)/λ ≠ 0` | **yes , the charge IS the variable-λ divergence** |

This is the bridge to Fleury's `charge = ∇·E`: the **electric charge is the non-constant-λ Beltrami
divergence**. The **endorsed build approach** (Marc, 2026-06-30, "the way to build it"): use the
**modern decomposition of Beltrami** (Sato-Yamada, [M7.0 corpus](tasks/m7_0_bootstrap.md) #11) and **start the code on Trkalian
(constant-λ) exact solutions, then take off the training wheels on variable-λ** , generalize S&Y to
non-constant λ, find the charge-carrying ansatz, and evolve it. The non-constant case is exactly the
hard part ("the math gets very hairy"), so the Trkalian start is the foothold. This maps directly
onto the tasks: M7.1-M7.3 stay in the charge-free Trkalian/neutral regime, and **M7.4 takes off the
training wheels , the constant-λ → variable-λ transition where the charge `∇·F` first appears** (the [roadmap](m7_roadmap.md), task M7.4).
Marc may bring in the **Spanish Beltrami school** (Enciso & Peralta-Salas, [M7.0 corpus](tasks/m7_0_bootstrap.md) #6) as collaborators.

**Pisello's precedent (via Álvaro García López, Models-of-Particles thread, 2026-06-30).** Daniel
Pisello's 1979 book *Gravitation, Electromagnetism and Quantised Charge* ([M7.0 corpus](tasks/m7_0_bootstrap.md) #16) builds a **toroidal
Hopf-knot** EM solution whose **charge is quantized ∝ the homotopy class of the knot** , not Rañada's
helicity-only zero-charge hopfion, but a genuinely **charged** knot from an electrovacuum Lagrangian
yielding **non-homogeneous equations á la Fleury-Dos Santos** (charge density ∝ the potential and its
derivatives, i.e. gauge-fixed, **A-primary**). This is the **closest published precedent to the M7
target** (a charged toroidal Beltrami knot) and sharpens three open questions: it **unifies** the
divergence charge with the topological / homotopy charge (Q3), shows a divergence-ful field **does**
hold a quantized-charge knot (Q5), and gives a concrete gauge-fixed charge-carrying construction (Q7).
Álvaro García López's own *Massive wave solutions to the Einstein-Maxwell equations* ([M7.0 corpus](tasks/m7_0_bootstrap.md) #17, Zitter
Institute) is the partner mechanism: the **electrovacuum as a charged nonlinear optical medium**, with
**Klein-Gordon from gauge-fixing** (M7.6) and an EM origin of mass.

The primary math is in **Pisello's 1977 paper** ([M7.0 corpus](tasks/m7_0_bootstrap.md) #18, the Lagrangian + **target-space S²**), now in
the corpus, alongside **Faber's geometric model** ([M7.0 corpus](tasks/m7_0_bootstrap.md) #19, arXiv:2201.13262), which builds the same
object on **target-space S³** (a soliton = electron with quantized charge, mass = field energy, spin),
plus **Faber & Golubich's precision lattice electron** ([M7.0 corpus](tasks/m7_0_bootstrap.md) #20, arXiv:2604.12021), the `α⁻¹ ≈ 137`
SU(2)-dipole result that is the M7.2 / M5.11 validation target. The **S² (Pisello) vs S³ (Faber)**
target-space choice is itself a live input to the substrate question **Q1** (what manifold the M7
field maps into).

---

## 3. Fleury's toroidal model , the analytic target to reproduce first

dos Santos & Fleury, *An electromagnetic model of the electron*, [arXiv:2510.22384](https://arxiv.org/abs/2510.22384).
The electron is a rotating EM wave confined to a torus:

```text
E = i E₀ H(r−r₀) e^{i(φ−ωt)} [ â_R + i (1 + R/R₀) â_φ ]
B = i B₀ H(r−r₀) e^{i(φ−ωt)} â_z ,        B₀ = E₀/c
phase ψ = (φ − ωt)  ,  one wavelength around the ring  ,  left-handed triad
```

Free parameters: amplitude `E₀`, major radius `R₀`, minor radius `r₀`, frequency `ω`. The model
identifies **charge with the field divergence** (`ρ = ∇·E`, non-zero in free space, the novelty vs
divergence-free Rañada/Irvine knots), and pins the four parameters with three QED constraints:

| Constraint | Equation (thin-torus limit) |
| --- | --- |
| RMS charge | `√2 π² ε₀ E₀ r₀² = e` |
| Magnetic moment | `√2 ε₀ π c E₀ R₀ r₀² (1 + r₀²/2R₀²) = μ_B (1 + α/2π)` |
| Spin | `(1/c) ε₀ E₀² π² R₀² r₀² (1 + r₀²/4R₀²) = ℏ/2` |
| Faraday (fixes ω) | `ω = 2c/R₀` (monochromatic), phase velocity `v_p = 2c` |

Solved numerical values (the **M7.2 reproduction targets**):

```text
E₀ ≈ 0.286 E_S  (Schwinger limit)        R₀ ≈ 1.573 r_c  ≈ 6.073e−13 m  (Compton scale)
r₀ ≈ 0.152 r_c  ≈ 5.854e−14 m            U  ≈ 0.795 m_e c² ≈ 0.406 MeV
ω  ≈ 0.636 ω_D  ≈ 9.86e20 rad/s          (ω_D = Dirac / zitterbewegung frequency)
```

Acknowledged limits (Fleury, § 5.2): the Heaviside mask is unphysical at the torus boundary
(suggests Bessel-function envelopes), and the energy falls short of `m_e c²`. **M7 replaces the
analytic mask with a relaxed lattice field**, which is precisely where the PDE treatment earns its
keep.

Fleury's ansatz is a **rotating wave** in Ceperley's sense (his ref [13], [M7.0 corpus](tasks/m7_0_bootstrap.md) #14): Ceperley's
circularly-polarized-EM rotating mode `E_r = E₀ e^{i(κz+φ−ωt)}` at `m=1` (his Eq 15) is literally this
torus phase, its **`J_m(κr)` Bessel envelope** is exactly the § 5.2 fix for the Heaviside mask, and
its angular-momentum law **`L_z = m(U/ω)`** (quantized when `U/ω = ℏ`) is the structural origin of the
spin `= ℏ/2` constraint. See [`../theory/ceperley_rotating_waves.md`](../theory/ceperley_rotating_waves.md) § 4b.

---

## 4. Ouroboros (M6) , the self-confinement the blend inherits

Werbos's two coupled vector fields `A_μ, J_μ` on Minkowski `(−,+,+,+)`
([`0d_canonical.md`](../../m6_ouroboros/research/0d_canonical.md), Werbos's
*Evaluating Universe Model Alternatives v5* shared doc):

```text
L = −¼ F_μν F^μν − ¼ G_μν G^μν + m_J² A_μ J^μ − f(J_μ J^μ)
    F = dA  ,  G = dJ  ,  f(s) = (g/4) s²  (canonical electron choice, g = 1.0)
```

In the linear limit (`J→0`) the A-field reproduces Maxwell exactly; the nonlinear `m_J² A·J −
f(J·J)` coupling produces localized time-periodic solitons ("chaoitons"). The electron benchmark is
`H/Q = 1.6969` (within 0.56% of `1.6875`), spin lock-in `2L/Q = 2ω`, charge from the Chern-Simons
linking number `Q_CS = 1`. **All of this exists today only as a 1D radial reduction** (the `(α,β)`
cylindrical ODE for the charged sector; an `l=1` spherical BVP for the neutral sector). M7 carries
the same Lagrangian, `m_J`, `g`, and the `H/Q` benchmark into a full 3D lattice.

---

## 5. The dynamics (what makes it rigorous, not analytic)

The energy functional blends three pieces, mirroring M5.11's `Skyrme curvature + LdG Higgs`:

```text
E[A,J] =  ∫ ½ (|E|² + c²|B|²)              Maxwell / fluid kinetic       (Fleury)
        + κ ∫ |F × (∇×F)|² / |F|²          Faddeev-Niemi 4th-order       (Derrick-evading stabilizer)
        + ∫ [ m_J² A·J − f(J·J) ]          Ouroboros self-confinement    (Werbos)
```

**Derrick scaling** under `x → λx` (the M5.11 argument, reused): kinetic `~ λ`, 4th-order `~ λ⁻¹`,
potential `~ λ³`. So `E(λ)` has an interior minimum: the 4th-order term provides the outward
pressure that balances collapse. **Static, finite-size, stable toroidal solitons are therefore
allowed**, the same Derrick-evasion that makes Faber's electron exist in M5.11.

Solve it two ways, exactly as M5.11 does:

| Method | Use |
| --- | --- |
| **Reverse-mode Taichi AD** for `δE/δ(A,J)`, validated against a numpy finite-difference gradient to `~1e-13` **before trusting any run** | the gradient for relaxation |
| **FIRE / L-BFGS** relaxation to `‖∇E‖ → 0` | the static soliton (M7.2-M7.4, M7.6, and the Phase B-C coverage tasks) |
| **Minkowski leapfrog** (constrained integrator, `∇·B = 0`) | the clock + real-time dynamics (M7.5 stability, M7.11 annihilation) |

---

## Cross-references

- Theory (our notes are in-repo; the source PDFs are local-only / gitignored, cited by public DOI/arXiv):
  [arXiv:2510.22384](https://arxiv.org/abs/2510.22384) (Fleury torus) ·
  Werbos *Evaluating Universe Model Alternatives v5* (shared doc, local only) ·
  [`../theory/sato_yamada_beltrami.md`](../theory/sato_yamada_beltrami.md) ([arXiv:1809.03136](https://arxiv.org/abs/1809.03136)) ·
  [`../theory/ceperley_rotating_waves.md`](../theory/ceperley_rotating_waves.md) (Ceperley rotating-wave equations; [AJP DOI 10.1119/1.17020](https://doi.org/10.1119/1.17020) / [IEEE DOI 10.1109/22.216476](https://doi.org/10.1109/22.216476)) ·
  [`../theory/feynman_maxwell_equations.md`](../theory/feynman_maxwell_equations.md) (Feynman Lectures II Ch 18, the Maxwell baseline for M7.2)
- Source corpus (the consolidated library, 52 PDFs + 1 docx): [`../theory/electron_beltrami/`](../theory/electron_beltrami/) , manifest [`../theory/SOURCES.md`](../theory/SOURCES.md) (Beltrami / force-free / knotted-EM / ball-lightning / LENR / Pisello-Faber canon, the M7.0 corpus)
- Rigor standard: [`../../m5_liquid_crystal/research/11a_vortex_loop.md`](../../m5_liquid_crystal/research/11a_vortex_loop.md) (M5.11 vortex-loop)
- Wave-physics library to mine (§ 0, not parents): [`m1_granule_motion`](../../m1_granule_motion/) · [`m2_free_wave`](../../m2_free_wave/) · [`m3_wolff_lafreniere`](../../m3_wolff_lafreniere/) · [`m4_ewt`](../../m4_ewt/)
- Ouroboros canonical spec: [`../../m6_ouroboros/research/0d_canonical.md`](../../m6_ouroboros/research/0d_canonical.md) ·
  background [`../../m6_ouroboros/research/0a_background.md`](../../m6_ouroboros/research/0a_background.md)
- EM ≡ hydrodynamics bridge (already in M5): [`../../m5_liquid_crystal/research/1b_topological_defect.md`](../../m5_liquid_crystal/research/1b_topological_defect.md) § "EM-hydrodynamics formal equivalence"
- Production-engine template: [`../../m5_liquid_crystal/`](../../m5_liquid_crystal/) (`medium.py`, `engine1_seeds.py` … `_launcher.py`)
- Comparison table (the M7 column goal): [`MODELS.md`](../../../../MODELS.md) · new-model flow [`ONBOARDING_MODELS.md`](../../../../ONBOARDING_MODELS.md), [`CONTRIBUTING.md`](../../../../CONTRIBUTING.md)
- Model briefing stub: [`../__M7_model_briefing.md`](../__M7_model_briefing.md)
- Question Tracker: [m7_question_tracker.md](m7_question_tracker.md)
- Roadmap: [m7_roadmap.md](m7_roadmap.md)
