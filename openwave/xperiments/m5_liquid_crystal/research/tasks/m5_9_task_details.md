# M5.9: Leptons (e/mu/tau) + Cornell quark strings + neutrino-flavor beat

> Task **M5.9** (M5 / Liquid-Crystal model). Status: **Backlog** · Gated by: M5.8, M5.9.0 calibration · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation.

---

## Current detail (from the roadmap, 2026-07-02 migration)

3 axis-choices → e/μ/τ mass calibration; Cornell `V(r) = −α/r + σr`; the `e_scale` physical-units hook lands here

### 🚧 M5.9 — 3 lepton families + Cornell quark strings

> Standard Model correspondence. The biaxial Λ = (g, 1, δ, 0) gives 3 axis-choices → 3 lepton families with the same Q but different masses (e/μ/τ). Cornell potential for quark strings via topological vortex.
>
> **Handedness / chirality** (matter↔antimatter charge-sign, neutrino helicity, the biaxial `π₁=Q₈` quaternion classes — not a simple `±`) becomes load-bearing here and at composites (15a) / the two-defect demo (5e). Teaching deep-dive deferred to **`0c` Lesson 10** (the handedness/chirality + composites finale, post-2026-05-31 refactor; seeds in L2 ellipse-handedness + L4 winding-sign).
>
> **★ Neutrino oscillation = "axis 2↔3" (Duda Wolfram slide, 2026-06-04; see the M5.8 corroboration note).** In `M = O·diag(g,1,δ,0)·Oᵀ`, a **neutrino = the `δ`–`0` (axis 2↔3) content swinging WITHOUT the full hedgehog winding** — hence **light, stable, chargeless**; flavor oscillation `e↔μ↔τ` = the axis-2↔3 swing, with **3 types** distinguished by axis / energy-&-length / left-right handedness / "sterile" `U(1)` phase, sourced by e.g. QCD quark-string hadronization + β-decay (the slide's bottom strip: neutron → W⁻ → proton + electron + neutrino → composites/15a). ⚠️ Conceptual / UNBUILT — a forward observable, not a result.

- [ ] Seed hedgehogs along the 3 different axes of the biaxial M field
- [ ] **Calibrate `(g, δ) numerically** against observed lepton-mass ratios: μ/e ≈ 207, τ/e ≈ 3477`. Per Duda 2026-04-19 guidance, these are calibration parameters, not ab-initio derivations
- [ ] Topological vortex string (1D defect line, not point hedgehog) for quark-pair binding
- [ ] Validate Cornell form: `V(r) = −α/r + σ·r` with `σ ≈ 1 GeV/fm` (string tension)
- [ ] **Neutrino check (forward, from the Duda slide)** — seed a `δ`–`0` (axis 2↔3) excitation *without* the `π₂` hedgehog charge; verify it is **light + stable + chargeless** (`∇·n̂ ≈ 0`) and **oscillates in the `δ`–`0` block** (the 3-flavor swing). Left/right + sterile-`U(1)` types → `0c` Lesson 10. Ties to the hopfion-as-excited-neutrino direction (`project_particle_defect_correspondence`)
- [ ] **⤳ FROM M5.5: apply the physical-energy-scaling factor** — `compute_energyH_density_M` carries the `e_scale` hook (currently `1.0`, bare "(rel.)" units). Set the physical factor (`ρ_medium × voxel_volume_am³ × INTERNAL_ENERGY_TO_AJ`) here, where the absolute energy scale is pinned by matching lepton masses — so the Hamiltonian reads in aJ, not relative units
- [ ] **Exit criterion**: lepton mass ratios within 10% of observed; Cornell potential reproduced with `σ ≈ 1 GeV/fm`

Neutrino-flavor breadth item (folded in): - [ ] **Neutrino flavor oscillation as explicit 3-mass clock-beating** (paper title's other half; M5.8.4 / M5.9) — `|ν_j(t)⟩ = e^{−iE_jt/ℏ}|ν_j(0)⟩`, three masses beating → flavor oscillation, as a demo (not just a row in the mass→ω table). Sine-Gordon `V` is an allowed alternative to `(1−φ²)²`.

---

## GitHub issue archive (#200)

> Migrated from OpenWave GitHub issue [#200](https://github.com/openwave-labs/openwave/issues/200) on 2026-07-02 (M5 tracking moving to this local roadmap). Title: "M5.9: lepton mass spectrum (mu, tau) from the biaxial hierarchy". State at migration: OPEN. Labels: help wanted.

### Issue body

## Goal (M5.9 sector)

Reproduce the **lepton mass spectrum (μ, τ)** in the M5 model: the three charged leptons as the **energy minima for elementary electric charge**, natural in 3D, via the biaxial hierarchy `0 < δ ≪ 1 ≪ g`.

## Status

This is the **M5.9 target** on the lepton-mass-spectrum row, currently 🚧 not yet tested. The electron rest energy is already pinned (✅ Faber core regularization, `r₀ = 2.2132 fm → 0.511 MeV`); the open work is the μ/τ hierarchy on top of it.

## The hard parts (named up front)

| Piece | Difficulty |
| --- | --- |
| Higgs-like core regularization | details open; sets the core that fixes the mass scale |
| The oscillation | experimentally known only for the electron; propulsion of the excited modes likely needs gravity |
| Discrete-spectrum selection | the mechanism that selects μ, τ as discrete minima (rather than a continuum) is the crux, and is exactly where sibling models report no selectivity |

## Scope

- Set up the biaxial hierarchy `0 < δ ≪ 1 ≪ g` in the M5 field.
- Search for the excited-mode energy minima above the electron ground state; test whether μ and τ appear as discrete, stable minima.
- Report the mass ratios against experiment, and crucially whether a discrete-spectrum mechanism actually selects those modes.

## Note

Long-horizon sector work, gated on the M5.9 regularization + oscillation pieces. Filed as a **tracker** for the open sector so it can be picked up incrementally. References: the Lepton-mass-spectrum row of `MODELS.md` and `m5_liquid_crystal/research/0b_M5_roadmap.md`.


---

## CONTRIBUTOR INPUT (onspotgithub, 2026-06-18) + verification

**Reframe (the key idea): the three leptons are ground states of three different axes, not excited modes of one.** Each charged lepton is the ground state of one of the three distinct eigendirections of the biaxial/triaxial Q-tensor (three axes in 3D). This rides the structure already seeded by `m5_6_2a` (biaxial hedgehog) and explains the **three-ness** geometrically: three axes → exactly three leptons.

**Proposed mass law `m ∝ Λ^(3/2)`.** Dimensional balance of the gradient energy (`~ Λ²/r₀`) against the regularization (`~ V₀ r₀³`, same `V₀` for all) gives `r₀ ∝ Λ^(1/2)` and `E ∝ Λ^(3/2)`, with `Λᵢ` the per-axis eigenvalue scale.

| Status | What |
| --- | --- |
| INPUT (Yukawa-like) | the eigenvalue hierarchy `Λ_τ:Λ_μ:Λ_e ≈ 229:35:1` |
| PREDICTION | the `3/2` power law, and that **exactly three** minima exist (three axes in 3D) |

**Verified on our side** (taking `Λ ∝ m^(2/3)`): `Λ_μ/Λ_e = 34.97 (~35)`, `Λ_τ/Λ_e = 229.5 (~230)`; `m_τ/m_μ` from the rounded `229:35` hierarchy `= 16.74` vs measured `16.82` (**99.5%**), matching the contributor's 99.6%.

**Resolves the N-6a ω-rigidity (and #220).** N-6a's frequency-rigidity (`ω ∝ H^0.033`, flat) is a **V=0 scale-invariance (conformal) artifact**. With V on, each axis carries its own scale, conformal invariance breaks, and `ω` tracks mass, so the same V-on run that tests the mass law also settles #220's clock-scaling.

**Sharpened test:** three hedgehog energy minimizations at different `Λᵢ` with **V on**; fit the exponent. If `E ∝ Λ^(3/2)` holds and `ω` then tracks mass, the mass law and #220's clock-scaling fall out together.

**Connection to validated machinery + open clarification.** The V-on core that pinned the electron (Faber MTF, `m5_6_3a`) gives `E0 = (π/4)(α ℏc)/r₀`, i.e. `E0·r₀ = π/4` constant (the same mass-independent relation flagged in #220), electron anchored at `r₀ = 2.2132 fm → 0.511 MeV`. That is `E ∝ 1/r₀` (r₀ the knob); the `Λ^(3/2)` balance instead varies `Λ` with `r₀` relaxing (`E ∝ r₀³`). The three-`Λ` run also clarifies whether these are the same physics re-parametrized (`Λ ↔ r₀`) or distinct. The pieces exist (`m5_6_2a` hedgehog + `m5_6_3a`/`3b` Faber energy): an assembly + `Λ`-sweep, not a new build.

**Scope note:** this test settles the **scaling** (the `3/2` law, given the hierarchy as input). The discrete **selection** mechanism (why exactly those three `Λ` / three axes are the stable minima) remains the crux named above.

**Updated definition of done (additions):**

- `E ∝ Λ^(3/2)` tested by ≥ 3 V-on hedgehog minimizations at different `Λ` (exponent fit).
- Confirm the **three-ness** (three stable axes/minima, not a continuum).
- Verify V-on **breaks the N-6a ω-rigidity** so `ω` tracks mass (the #220 hinge).


---

## Quarks (M5.9 sector) — detail moved from the MODELS.md coverage cell (2026-06-19)

The M5.9 sector covers quarks as well as the μ/τ leptons; the MODELS.md Quarks cell (M5 column) was condensed and now references this issue for the detail:

> Fractional-charge excitations OF a 1D topological quark string, NOT a 0D hedgehog and NOT merely the string's endpoint: a fraction-of-π inward / outward field rotation sets the fractional charge (a full π gives the elementary charge), enforced in baryons by interactions between quark strings. The Cornell linear term arises naturally: violating topological charge quantization costs asymptotically linear energy ~1 GeV/fm between the conflicting quarks. M5.9 target, non-trivial via the regularization + oscillation pieces; the full SU(3)/CKM quark structure remains the open M5.9 piece (#199 resolved the neutrino SO(3) side: SO(3) leading, broken by the small θ₁₃).

### Issue comments

#### Comment 1 (onspotgithub, 2026-06-19)

The three leptons aren't excited states of one axis — they're ground states of three different axes. Dimensional analysis (gradient energy ~ Λᵢ²/r₀ vs. regularization ~ V₀r₀³, same V₀ for all) gives m ∝ Λ^(3/2). Consistency check: m_τ/m_μ predicted from the individual e-ratios = 16.75 vs measured 16.82 (99.6%). The eigenvalue hierarchy Λ_τ:Λ_μ:Λ_e ≈ 229:35:1 is a model input (like Yukawa couplings); the prediction is the 3/2 power law and that exactly three minima exist (three axes in 3D). The ω-rigidity (N-6a) is a V=0 scale-invariance artifact — turn on V and each axis gets its own scale, breaking conformal invariance so ω tracks mass. Test: three hedgehog energy minimizations at different Λᵢ with V on; if E ∝ Λ^(3/2), the law holds and #220's clock-scaling follows for free.

#### Comment 2 (xrodz, 2026-06-19)

This is a real contribution, thank you. I went through the m ∝ Λ^(3/2) argument on our side and it holds up: the eigenvalue ratios land at 35 and 230, and the τ/μ ratio reproduces to ~99.6%, exactly as you said.

The "three axes, not excited modes" reframe is the part I keep coming back to. It's elegant, and it resolves the N-6a ω-rigidity: if each axis carries its own scale, turning V on breaks the degeneracy and ω tracks mass, which is exactly the piece #220 was stuck on. And it rides structure we already seed (the biaxial hedgehog), so it's not a bolt-on.

What I like most is how it folds the mass law and the clock-scaling into one clean test: three hedgehog minimizations at different Λ with V on. The good news is a lot of the machinery for it already exists on OpenWave side, so it's a very natural thing to try.

Really appreciate you bringing this, it's the kind of contribution that makes the whole project worth doing.

#### Comment 3 (xrodz, 2026-06-20)

## M5.9.1 result: the mass law does not emerge from the current functional (gap identified)

Ran the contributor's proposed test (V-on biaxial-hedgehog energy at different eigenvalue scales, fit the exponent), self-contained in `sandbox_v9/m5_9_1_lepton_mass_law.py` (numpy, headless). With the eigenvalue amplitude `Λ` on the order parameter (`D_full = Λ·diag(1, δ, 0)`):

| Test | Result |
| --- | --- |
| Baseline (`Λ=1`) | `E·r₀ = 18.74` const (CV 0.00%), Faber `E ∝ 1/r₀` reproduced |
| Amplitude sweep, fixed `r₀` | `E_curv ∝ Λ⁴·⁰⁰` (R²=1.000), `E_V ∝ Λ⁰` |
| Lepton hierarchy (`Λ = m^(2/3)`) | `E_μ/E_e ≈ 1.3e6` (measured 207); `E_τ/E_e ≈ 2.4e9` (measured 3477) |
| `r₀`-relaxation, fixed `Λ` | `E(r₀)` monotonic, NO interior minimum |

**Verdict: the `E ∝ Λ^(3/2)` mass law does NOT emerge from the current M5 Faber functional.** Two structural reasons:

1. the curvature energy `∫‖[M_μ,M_ν]‖²` is **quartic** in the order-parameter amplitude (`E_curv ∝ Λ⁴`), not the quadratic `~Λ²/r₀` the dimensional balance assumed;
2. the Faber potential integrates to `E_V ∝ 1/r₀` (scale-balanced), so `r₀` is a **free modulus** (no interior minimum), and there is no gradient-vs-regularization balance that selects `r₀(Λ)`.

This is not a falsification of the three-eigen-axes idea. It identifies the missing piece concretely: a **core-volume confiner** (a `V₀·r₀³` term, the Higgs-like vacuum), so the gradient-vs-confiner balance fixes `r₀(Λ)` and selects the discrete spectrum. The current Faber `V` pins the electron given `r₀` but does not select the lepton scales. The mass-selection mechanism (the named crux) remains the open work.

Findings: `sandbox_v9/m5_9_lepton_mass_clock_findings.md`. Staying open (the selection/confiner build is the next step).

#### Comment 4 (xrodz, 2026-06-20)

## M5.9.3 confiner build: scale-selection CLOSED, mass law E ∝ Λ³, hierarchy origin still open

Built the identified missing piece, the **core-volume confiner** `E_conf = B·∫(1-s²)³ d³x ~ B·r₀³` (a fixed false-vacuum energy density over the melted-core volume; the Faber potential is the same integrand times `1/r₀⁴`, hence scale-covariant, the confiner uses a FIXED `B`, breaking scale-covariance). Script: `sandbox_v9/m5_9_3_confiner.py`. Minimizing `E(r₀)` per eigenvalue amplitude `Λ`:

| Result | Reading |
| --- | --- |
| confiner OFF: `E(r₀)` monotonic | the free-modulus gap (M5.9.1) |
| confiner ON: interior minimum at `r₀*=1.0` | **scale-selection CLOSED** (a core size is now selected) |
| `E* ∝ Λ³·⁰⁰` (Skyrme + confiner, R²=1.000) | the mass law is `Λ³`, NOT the assumed `Λ^(3/2)` |
| Frank + confiner | `E ∝ Λ²` but no interior minimum (both grow with `r₀`); the Skyrme curvature is the stabilizing gradient |

**What is closed.** The confiner fixes the free modulus, so M5 now has scale-selection and a definite mass law `E ∝ Λ³`.

**Exponent correction.** `E ∝ Λ³` (not `Λ^(3/2)`), so the eigenvalue hierarchy that reproduces the masses is `Λ ∝ m^(1/3)` (`Λ_μ/e = 5.9`, `Λ_τ/e = 15.1`), not the assumed `35 : 229`.

**What stays open (the irreducible piece).** Reproducing the masses given the eigenvalue input is near-tautological: once the law (`E ∝ Λ^p`) and the input (`Λ ∝ m^(1/p)`) are set, `E ∝ m` holds by construction, so `m_τ/m_μ = 16.82` falls out under any consistent convention (the contributor's `Λ^(3/2)` route and this `Λ³` route both give it). The three-axes picture supplies the **three-ness** geometrically, but the eigenvalue **values** (`1 : 5.9 : 15.1`) stay Yukawa-like input; the current biaxial `D = diag(1, 0.3, 0)` does not carry them. **Deriving the eigenvalue hierarchy from the biaxial geometry is the remaining frontier.**

So M5 can now **accommodate** the lepton masses (selection + a definite law) but does not yet **predict** them parameter-free. Updated scope: (1) scale-selection ✅ (confiner), (2) mass law ✅ (`E ∝ Λ³`), (3) eigenvalue-hierarchy origin ❌ open.

Findings: `sandbox_v9/m5_9_lepton_mass_clock_findings.md`.

#### Comment 5 (xrodz, 2026-06-20)

## Disposition + next step (for a future session)

#200 stays OPEN (set to Next). The confiner (M5.9.3) is a real advance, it closes scale-selection and pins the mass law `E ∝ Λ³`, but it would be overclaiming to mark μ/τ "predicted": reproducing the masses given the eigenvalue input is near-tautological (`E ∝ m` by construction), so M5 now **accommodates** the lepton masses but does not **predict** them parameter-free.

**The genuine open frontier:** deriving the eigenvalue ratios from the biaxial Q-tensor geometry, whether the three eigendirections of the biaxial/triaxial defect naturally carry a `1 : 5.9 : 15.1` spread (under `E ∝ Λ³`; or the `1 : 35 : 229` the contributor's `Λ^(3/2)` assumed). The three-axes picture supplies the three-ness; the **values** are the missing piece. The current `D = diag(1, 0.3, 0)` does not carry them.

**Next concrete experiment (multi-session):** set up the biaxial/triaxial hedgehog with the confiner and test whether the energy-minimizing eigendirection structure SELECTS a definite eigenvalue spread (rather than taking it as input). If a geometric mechanism fixes the spread, the masses become a prediction; if not, the hierarchy stays Yukawa-like input, and that is the honest ceiling for this route.

Scope to date: (1) scale-selection ✅ (confiner), (2) mass law ✅ (`E ∝ Λ³`), (3) eigenvalue-hierarchy origin ❌ open. Findings: `sandbox_v9/m5_9_lepton_mass_clock_findings.md`.
