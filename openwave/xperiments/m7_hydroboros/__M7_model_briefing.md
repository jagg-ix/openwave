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
| In-repo | [`research/0a_implementation_plan.md`](research/0a_implementation_plan.md) (master plan); `theory/` (52-PDF electron-Beltrami corpus + notes); `images/` icon |

## Model Profile (what it brings, short form)

| Attribute | M7 |
| --- | --- |
| Substrate | A-primary ontology; leading candidate = the Ouroboros doublet `(A_μ, J_μ)` read via Riemann-Silberstein (diagnostic); target manifold S² / S³ open (Q1) |
| Particle | electron = self-linked toroidal Beltrami vortex |
| Charge | variable-λ Beltrami divergence `∇·F`, unified with Chern-Simons linking / helicity `∫A·B` |
| Derrick escape | Faddeev-Niemi 4th-order stabilizer (outward pressure balancing collapse) |
| Energy functional | Maxwell / fluid kinetic (Fleury) + 4th-order (Faddeev-Niemi) + Ouroboros confinement `m_J²A·J − f(J·J)` (Werbos) |
| Solve method | Taichi reverse-mode AD gradient (vs numpy FD to ~1e-13) + FIRE / L-BFGS relaxation + constrained Minkowski leapfrog; inherits the M5.11 method |
| Free parameters | `m_J`, `g` (from M6, canonical g = 1); `κ` (4th-order, Q2); `λ(x)` profile (Q7) |
| Reproduction targets | Fleury `U ≈ 0.795 m_e c²`, `ω = 2c/R₀`; M6 `H/Q = 1.6969` (in full 3D); Faber & Golubich α⁻¹ ≈ 137 |

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

**Pre-implementation / planning stage.** No sandbox runs yet (`research/sandbox_v1` is an
empty stub), and there is no MODELS.md column yet (adding it is the M7.7 milestone). The
master plan is complete and the 52-PDF Beltrami theory corpus is assembled. The decisive
credibility gates are M7.1-M7.3: reproduce *both* parents (Fleury's torus and M6's `H/Q`)
from one lattice code, then earn the new physics (the charged variable-λ soliton) at M7.4.

## Roadmap

Three arcs, phases M7.1 → M7.14 (full detail in
[`research/0a_implementation_plan.md`](research/0a_implementation_plan.md) § 6):

| Arc | Phases | What lands |
| --- | --- | --- |
| A , electron + the column | M7.1-M7.7 | infra → reproduce Fleury → reproduce M6 in 3D → charged soliton (constant-λ → variable-λ, the new physics) + Coulomb → clock + stability → observables → consolidate the M7 column (milestone) |
| B , forces + sectors | M7.8-M7.13 | magnetic, gravity (hard), nuclear (strong / weak), antimatter / annihilation, lepton + neutrino family, dark matter |
| C , composites | M7.14 | quarks, baryons, mesons, orbital quantization |

Open questions Q1-Q7: substrate + target manifold (Q1), the 4th-order form + κ (Q2), whether
divergence-charge and linking-charge are forced equal (Q3), whether variable-λ fields still
hold clean knots (Q5), and the `λ(x)` charge-carrying ansatz (Q7, the core of M7.4).

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
