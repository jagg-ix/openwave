# M7 HydroBoros: Model Briefing

> **What M7 brings.** The rigorous full-3D-PDE toroidal Beltrami electron that neither parent
> built: it fuses Fleury's toroidal-EM electron (analytic) with Werbos's Ouroboros
> self-confinement (1D radial) on OpenWave's M5-proven Taichi lattice, so the electron's
> field configuration is both *specified* and *earned* as the energy-minimizer. It is
> pre-implementation (planning stage); its [`MODELS.md`](../../../MODELS.md) column is the
> M7.7 milestone.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M7 |
| Name | HydroBoros (Hydrodynamics + Ouroboros; evokes the Hydra water-snake) |
| Author | Marc Fleury (toroidal-EM electron) + Paul Werbos (Ouroboros / M6): the two physics parents |
| Blend | Fleury's toroidal EM electron (arXiv:2510.22384) fused with Werbos's Ouroboros self-confinement (M6) |
| Lineage | force-free / Beltrami (Trkalian → variable-λ) + knotted-EM / Clebsch + Faber geometric soliton |
| Primary sources | Fleury / dos Santos arXiv:2510.22384; Werbos M6; Faber arXiv:2201.13262 + Faber & Golubich arXiv:2604.12021; Sato-Yamada arXiv:1809.03136; Ceperley; Pisello 1977 |
| In-repo | [`research/m7_roadmap.md`](research/m7_roadmap.md) (roadmap) + [`m7_background.md`](research/m7_background.md) (background) + [`m7_question_tracker.md`](research/m7_question_tracker.md) (Q1-Q7); `theory/` (64-doc electron-Beltrami corpus + notes); `images/` icon |

## Model Profile (what it brings, short form)

| Attribute | M7 |
| --- | --- |
| Substrate | A-primary ontology; leading candidate = the Ouroboros doublet `(A_μ, J_μ)` read via Riemann-Silberstein (diagnostic); target manifold S² / S³ open (Q1); worked in the **time-harmonic (fixed-ω) frame**, both parents are time-periodic |
| Particle | electron = self-linked toroidal Beltrami vortex (approximately Beltrami: the relaxed minimizer of the full functional) |
| Charge | the **measured** divergence `∇·F` the Ouroboros coupling drives, unified with Chern-Simons linking / helicity `∫A·B` (the Q3 experiment) |
| Stabilization | **helicity anti-collapse** (Arnold bound) + **Ouroboros confinement anti-expansion**; Nadirashvili's theorem forces the blend (no finite-energy pure-Beltrami field exists); a 4th-order term is optional (Q2, off by default) |
| Energy functional | period-averaged Maxwell kinetic (both fields) + Ouroboros coupling `m_J²A·J − f(J·J)` (Werbos), minimized at fixed ω + helicity |
| Solve method | fixed-ω minimization (FIRE / L-BFGS) + fixed-helicity relaxation + Taichi reverse-mode AD gradient (vs numpy FD to ~1e-12) + constrained Minkowski leapfrog; the M5.11 machinery in the time-harmonic frame |
| Free parameters | `m_J`, `g` (M6 canonical g = 1.0; Werbos-v5 point g = 1.0625, dictionary = Q9); ω swept for the spectrum |
| Reproduction targets | Fleury `U ≈ 0.795 m_e c²`, `ω = 2c/R₀`; M6 `H/Q = 1.6890` at the same `(g=1.0, ω=1)` calibration, in full 3D; Faber & Golubich α⁻¹ ≈ 137 (M7.6 stretch) |

## Field Configuration of Particles

The electron's field configuration *is* the self-linked toroidal Beltrami vortex (a
topological vortex).

| Test | M7's answer | Phase |
| --- | --- | --- |
| Coulomb | two charge configs → read the `1/r` interaction energy `E(d)` | M7.4 (single-charge `1/r`) + M7.6 (two-charge `E(d) ~ 1/d`) |
| Clock | the de Broglie frequency = the energy-minimizing one | M7.5 (= the M5.8 mechanism) |

Other particles ride the same substrate later: the neutral knot = dark matter (M7.13), the
lepton / neutrino family (M7.12), quarks / baryons / mesons (M7.14).

## Implementation Status

**Pre-implementation / planning stage.** No runs yet (`research/scripts/`, `data/`, `plots/`
are empty), and there is no MODELS.md column yet (adding it is the M7.7 milestone). The
plan is complete and the 64-doc Beltrami theory corpus is assembled. The decisive
credibility gates are M7.1-M7.3: reproduce *both* parents (Fleury's torus and M6's `H/Q`)
from one lattice code, then earn the new physics (the charged variable-λ soliton) at M7.4.

## Roadmap

Five phases, M7.1 → M7.16 (full detail in [`research/m7_roadmap.md`](research/m7_roadmap.md)):

| Phase | Tasks | What lands |
| --- | --- | --- |
| A , electron + the column | M7.1-M7.7 | infra → reproduce Fleury → reproduce M6 in 3D → charged soliton (constant-λ → variable-λ, the new physics) + Coulomb → clock + stability → observables → consolidate the M7 column (milestone) |
| B , forces + sectors | M7.8-M7.13 | magnetic, gravity (hard), nuclear (strong / weak), antimatter / annihilation, lepton + neutrino family, dark matter |
| C , composites | M7.14 | quarks, baryons, mesons, orbital quantization |
| D , MODELS.md column | M7.15 | complete + govern the 21-cell HydroBoros column |
| E , production | M7.16 | graduate the canonical recipe to `medium.py` + engines + `_launcher.py` rendering |

Open questions Q1-Q9: substrate + target manifold (Q1), whether a 4th-order stabilizer is needed
at all (Q2, direction set: helicity + confinement carry the load), whether divergence-charge and
linking-charge are forced equal (Q3, a first-class M7.4 measurement), whether divergence-ful fields
hold clean knots (Q5), the charge-carrying construction (Q7, reframed to relax-and-measure), gauge /
constraint handling (Q8), and the Werbos-v5 calibration dictionary (Q9).

## Help Wanted

M7 is the newest and most open program, actively recruiting. It is the natural home for the
hydrodynamics / Beltrami and toroidal-electron communities.

| You can contribute | How |
| --- | --- |
| Build a phase | pick a sandbox phase (M7.1 infra, M7.2 Fleury reproduction, ...) and land its gate |
| Bring Beltrami expertise | the variable-λ (charge-carrying) construction is the research core (the Spanish Beltrami school is being invited) |
| Contribute a source or seeder | knotted-EM / Bateman / Trkalian seed generators |
| Answer an open question | Q1-Q7, especially the substrate manifold (S² vs S³) and the `λ(x)` profile |

Flow: open an issue or discussion → fork → branch → PR with a DCO sign-off
(`git commit -s`), under Apache 2.0. New-model governance: open an issue first so a
maintainer adds the column at the M7.7 milestone. See
[`../../../MODELS.md`](../../../MODELS.md) § Contributing,
[`../../../ONBOARDING_MODELS.md`](../../../ONBOARDING_MODELS.md),
[`../../../CONTRIBUTING.md`](../../../CONTRIBUTING.md). Model discussion runs in the
Models-of-Particles group.

## Rich Context for Deep Reader

This is a top level documentation and orientation content. For additional context on this model, a detailed read in the /theory and /research folders is recommended, as well as the production files in this model root folder, that may contain the canonical full PDE implementation of the theory.
