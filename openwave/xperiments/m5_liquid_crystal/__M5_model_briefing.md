# M5 Liquid Crystal (LC): Model Briefing

> **What M5 brings.** Particles as topological defects of a Landau-de Gennes matrix
> field (extended to a 4×4 tensor, with a Skyrme kinetic term): the electron is a biaxial hedgehog whose de Broglie clock is the
> energy-minimizing state, charge is the defect's topological winding, and the four
> forces plus gravity emerge from the geometry of the same field. It is OpenWave's
> most-validated model (16 of 21 [`MODELS.md`](../../../MODELS.md) cells).

## Identity

| Field | Value |
| --- | --- |
| Model ID | M5 |
| Name | Liquid Crystal (LC) |
| Author | Jarek Duda (Jagiellonian University, Kraków) |
| Key inputs | Manfried Faber (TU Wien) EM and core regularization; liquid-crystal discussions with [Samo Kralj](https://scholar.google.com/citations?user=Bojz5CkAAAAJ&hl=en) |
| Lineage | Landau-de Gennes nematics + Skyrme term + Einstein teleparallel gravity |
| Primary sources | Duda arXiv:2501.04036 (time crystal), arXiv:2108.07896 (superfluid / KG-around-hedgehog); Faber arXiv:2201.13262, Faber & Golubich arXiv:2604.12021; liquid-crystal particle-analog experiments ([Wikipedia: Liquid crystal particle analogs](https://en.wikipedia.org/wiki/Draft:Liquid_crystal_particle_analogs)) |
| In-repo | `medium.py` + `engine1-4` + `_launcher.py` (production); `research/sandbox_v1..v11` (headless); [`__M5_course.md`](__M5_course.md) (intuition) |

## Model Profile (what it brings, short form)

| Attribute | M5 |
| --- | --- |
| Substrate | `M`, a 4×4 real symmetric tensor field (`M = O·D·Oᵀ`); the eigenspectrum `D` is fixed only in vacuum (the potential minimum) |
| Vacuum | the preferred shape `D = diag(g, 1, δ, 0)`, the minimum of the potential, SO(1,3) vacuum dynamics unifies EM (tilts) + QM (twists) + GEM (boosts) |
| Particle | defect of `M`: a point-like topological charge (elementary electric charge), a topological vortex line (quark string) |
| Charge | integer winding of the director (Gauss-Bonnet), `\|Q\| = ±1`, additive |
| Derrick escape | time-periodic resonance (no static soliton; the stable object is 4D) |
| de Broglie clock | bounded, self-starting, frequency-rigid time crystal = the energy-minimizing state |
| EM | Maxwell from tilts of the 1-axis (two independent routes, at c) |
| Quantum | Klein-Gordon from biaxial twist, mass geometric (no added mass term) |
| Gravity | curved space (perpendicular to the local time axis) in flat spacetime; boost of the time axis → gravitoelectromagnetism (GEM), no dynamical metric required |
| Free parameters | δ (QM/EM contribution), g (EM/GEM contribution), 1-2 potential coefficients; calibration knobs: Faber r₀ (mass), Coulomb units |
| Lab anchor | hopfions/skyrmions in real media (Liu et al. 2026, Nature Physics); pilot-wave droplets (Bush-Couder) |
| Formal artifacts | every MODELS.md cell backed by a runnable script + note; negatives preserved (M5.2, M5.7) |
| Next falsifier | g-factor ≈ 2 (order confirmed), the absolute-ω calibration chain, neutrino δ_CP = 180° (JUNO/DUNE) |

## Decision-Relevant Attributes

Model-level attributes to weigh the column: parameter economy, the formal artifacts that
back the claims, and what would falsify the model next. (Held here for now; a consolidated
cross-model version may return to `MODELS.md` later.)

| Attribute | M5 |
| --- | --- |
| Free parameters | δ (QM/EM contribution), g (EM/GEM contribution), plus 1-2 potential coefficients; the boost dressing b enters the clock sector. Calibration handles: Faber r₀ (mass), Coulomb units<br>[`research/4c_convo_2026.06.08.md`](research/tasks/m5_4c_convo_2026.06.08.md) |
| Formal artifacts | Every claim backed by a runnable open script + research note; documented negatives (M5.2, the M5.7 nulls) preserved as results<br>[`research/m5_summary_report.md`](research/m5_summary_report.md) § Reproduction |
| Falsifiable near-term tests | Unit-free g-factor ≈ 2 from the fixed-clock electron (**#219 ✅: right-order g ≈ 2, the box ladder [1.97, 2.22] brackets 2.0023**); the absolute-ω calibration chain (Coulomb units + LdG-to-rest-energy). **Calibration Phase A+B (2026-06-17, #208):** the scale-free unit map has two free dials (`c` emergent, `ℏ`=action unit); **α = \|b\|/(ℏc) ≈ 1/178** from the Coulomb coupling (right order vs 137.036, pure-topology un-tuned, c-cone factor pending); the clock runs **28.2× below** the electron ZBW under the energy anchor (structural, ω rigid vs energy). Faber's `E₀=α·ℏc·π/(4r₀)` contains α, so the clock is the lone independent absolute-frequency test. **Lever budget (#217, 2026-06-17):** V-on is **null** on frequency (V is rotation-invariant; the clock is a pure rotation, so `∂V/∂clock=0` exactly), the **faithful F-commutator kinetic** is the one real lever but bounded **×3.04**, leaving **~9-20×** = the missing length anchor. **Length anchor (#218, 2026-06-17):** anchoring on the Faber `r₀` (length) gives ω **~36× HIGH** (mirror of the energy route's 28× low); the two anchors **BRACKET the ZBW** and their **geometric mean reproduces it to ~13%** (c=2). The model's particle obeys `E·r₀ = α·(π/4)·ℏc` **exactly** (the classical-radius relation, `r₀ = α·(π/4)·ƛ_C` ~174× below the Compton wavelength). **So the gap is a calibration SPLIT, not an irreducible deficit**: the ZBW scale is recoverable by anchoring energy + length **jointly** (the `E·r₀=const` line), not the energy postulate alone; the geometric-mean law awaits a mass-family test (**#220**). **Neutrino sector (#199 ✅, 2026-06-18):** the SO(3) route's **δ_CP = 180°** is a sharp near-term falsifier: JUNO/DUNE settling δ_CP far from 180° kills the pure-SO(3) neutrino structure (currently CONSISTENT, NuFIT 6.0 best fit ~177°)<br>[`research/m5_roadmap.md`](research/m5_roadmap.md) § ELECTRON-ID, [`research/findings/m5_8_2x_findings.md`](research/findings/m5_8_2x_findings.md), [`research/findings/m5_8_2y_findings.md`](research/findings/m5_8_2y_findings.md), [`research/findings/m5_8_2z_findings.md`](research/findings/m5_8_2z_findings.md) |

## Field Configuration of Particles

Standing demand of any particle model: *state the field configuration of each
particle, and say whether it uses topological vortices.* M5's answers:

| Particle | Field configuration in M5 | Topological vortex? |
| --- | --- | --- |
| Electron | biaxial hedgehog defect of `M`, winding `Q = -1`, with internal de Broglie clock | ✅ disclination hedgehog |
| Positron | the `Q → -Q` reflected defect | ✅ |
| Neutrinos | light, charge-0 loop of quark string; flavour = SO(3) spatial rotation | ✅ loop |
| Quarks | fractional-charge segment of a 1D quark string (fraction-of-π rotation) | ✅ string |
| Baryons / mesons | knots of quark strings (baryon = simplest knot; pion = twist / reconnection) | ✅ knot |
| Photon / EM wave | a twist-like wave, like the wake behind a marine propeller (at c) | ❌ (radiation, not a defect) |

The de Broglie clock is *derived*, not assumed: the Zitterbewegung frequency is the one
that minimizes the field energy (M5.8), exactly the "preferred time derivative". Neutrino mixing (PMNS, δ_CP) falls out of the SO(3) flavour rotation, a
testable parameter reachable in the model that mainstream physics reaches only through
large neutrino experiments.

## Implementation Status

16 of 21 MODELS.md criteria carried (8 ✅ validated in-platform, 8 ⚠️ partial), 0 ❌,
5 🚧 planned. It is the most-validated column in the coverage matrix. Phases M5.0 → M5.11
complete.

| Sector | Status |
| --- | --- |
| Electron (4 observables) | ✅ mass (Faber r₀ → 0.511 MeV), charge (winding), μ + spin, spin-½ (apolar 720°) |
| Coulomb 1/r | ✅ R² = 0.978 between two hedgehogs (pure topology) |
| Maxwell EM | ✅ recovered two routes (hydrodynamic + Faber curvature) |
| Klein-Gordon (QM) | ✅ geometric mass from biaxial twist (Fig 9) |
| de Broglie clock | ✅ bounded self-starting time crystal; ZBW scale recovered to ~13% (geo-mean of energy + length anchors) |
| Neutrino mixing | ⚠️ PMNS from SO(3): tri-bimaximal + δ_CP ≈ 180° parameter-free; θ₁₃ ≈ 8.5° = the SO(3)-breaking |
| Lepton mass spectrum | ⚠️ mass law `E ∝ Λ³` fixed; the 1 : 5.9 : 15.1 hierarchy origin open |
| Gravity | ⚠️ GEM ∝ (b·g)² measured (boost-tilt route); no dynamical metric required (curved space ⊥ the local time axis, in flat spacetime) |
| Strong / weak | ⚠️ short-range running-coupling onset ✅; Cornell confinement + SU(2) chiral open |
| Quarks · baryons · mesons · nuclei | 🚧 planned (15a composite-particles stage); nuclei are the most practical direction |
| Orbital quantization | 🚧 a different level: the coupled pilot wave set up by the electron clock |

Deep dives: [`research/m5_summary_report.md`](research/m5_summary_report.md) (results of
record), [`research/m5_roadmap.md`](research/m5_roadmap.md) (full program),
[`research/m5_question_tracker.md`](research/m5_question_tracker.md) (open questions).

## Roadmap

| Next | What lands |
| --- | --- |
| Lepton hierarchy origin (#200) | why the eigenvalue ratios give 1 : 5.9 : 15.1 (the mass law `E ∝ Λ³` is already fixed) |
| Absolute-ω calibration (#220) | close the ZBW scale from a mass-family test + the Coulomb-unit map |
| Neutrino field follow-up (#200) | the charged-lepton second-rotation matrix behind θ₁₃ |
| Quarks / hadrons / nuclei (15a) | Cornell confinement via 1D vortex string; baryons / mesons as knots; nuclei (the most practical direction) |
| Weak force | a clean SU(2) chiral reconnection mechanism (currently sketched) |
| Orbital quantization | pilot-wave standing-wave resonance around the electron clock |

## Help Wanted

M5 is an open column in an open arena. Anyone can extend it, and a documented *negative*
(a runnable script showing "this doesn't work, here's why") counts as much as a positive.

| You can contribute | How |
| --- | --- |
| A new validation of an M5 cell | runnable script + short note, pass/fail against the shared criteria |
| A harder falsifier | pick an open ⚠️ / 🚧 cell (hierarchy origin, weak force, quarks) |
| A rival field configuration | propose an alternative ansatz for a particle, test it head-to-head |
| A whole new model | a new `openwave/xperiments/<model>/` column, same shared criteria |

Flow: open an issue or discussion → fork → branch → PR with a DCO sign-off
(`git commit -s`), under Apache 2.0. Light review checks only reproducibility + honest
documentation, not orthodoxy. Start here: [`../../../MODELS.md`](../../../MODELS.md)
§ Contributing, [`../../../ONBOARDING_MODELS.md`](../../../ONBOARDING_MODELS.md),
[`../../../CONTRIBUTING.md`](../../../CONTRIBUTING.md). Model discussion runs in the
Models-of-Particles group.
