# M6 Ouroboros: Model Briefing

> **What M6 brings.** A classical field theory in which every particle is a localized,
> time-periodic soliton (a "chaoiton"): in the two-vector formulation the integer
> Chern-Simons / Hopf linking number *is* electric charge, and the theory claims the
> electron, the lepton spectrum, and a sub-MeV dark-matter candidate from one Lagrangian.
> **REFRESHED 2026-07-20**: the former "permanent hold" is lifted; the model column now
> tracks the author's CURRENT theory (Ouroboros+Eli+Fable v4, published 2026-07-20), and a
> new validation program ([`research/m6_roadmap.md`](research/m6_roadmap.md), M6.1+) will
> re-earn or re-grade every cell at M5-series rigor.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M6 |
| Name | Ouroboros (Chaoiton framework) |
| Author | Paul J. Werbos (NSF program director, retired; QAGI LLC) |
| Collaboration | AI co-authorship disclosed on the papers (DeepSeek; Claude Sonnet 4.6 + Claude Code; "Nuclear Gemini"); OpenWave contributed the neutral-chaoiton BVP profile + scaling symmetry, and the Test 1 corrections acknowledged in the July 8 record |
| Lineage | Schwinger 1969 dyons + Maxwell extension (toroidal-poloidal mutual confinement); shares the Schwinger ancestor with M5 |
| Primary sources | The full latest-version Zenodo corpus, 29 records: manifest [`theory/_CITATIONS.md`](theory/_CITATIONS.md) (local corpus, gitignored; every record openly downloadable at its DOI). Current spec: Zenodo [21447590](https://zenodo.org/records/21447590) (v4) |
| In-repo | [`research/m6_theory_canonical.md`](research/m6_theory_canonical.md) (specs of record + provenance ledger), [`research/m6_roadmap.md`](research/m6_roadmap.md), [`research/m6_particle_hunt.md`](research/m6_particle_hunt.md); archive-era validated record in [`research/archive/`](research/archive/) (sandbox v1-v11) |

## Model Profile (what it brings, short form)

| Attribute | M6 |
| --- | --- |
| Substrate (two-vector era, all validated results) | two coupled Lorenz-constrained vector fields `A_μ, J_μ` on Minkowski; `ℒ_JA = −F·F − G·G + J·A − g(J·J)²` (v11 normalization; notation drifts across records, see the canonical § 2) |
| Substrate (current spec, v4, paper-level) | ONE scalar chaoiton field φ coupled to nucleon density: `L = ½∂φ∂φ − ½m_φ²φ² − (λ/4!)φ⁴ − gφρ_n(x) + λC[φ]`, m_φ ≈ 0.460 MeV; A-linear nuclear coupling derived from a surface-saturation constraint; the two-theories relation is open (canonical OQ1) |
| Particle | chaoiton = localized time-periodic soliton; charge = mutual Chern-Simons linking Q_CS (= Hopf invariant) in the two-vector era |
| Derrick escape | time-periodicity / oscillation (the "third escape"): genuine and in-platform |
| EM | `A_μ` IS the EM 4-potential; Maxwell exact in the J→0 linear limit (two-vector era; v4's scalar has no EM sector) |
| Electron benchmark | H/Q: publicly downgraded by the author's July 8 record to a WINDOW-DEFINED internal quantity (code-to-code reproduction 4.7e-5, M7); the full provenance ledger is the canonical § 4; clean re-derivation = M6.2 |
| DM candidate | neutral chaoiton m_χ = 0.460 MeV + mediator m_J = 0.6184 MeV parameter-free (in-platform, archive era); v4 promotes 0.460 MeV to the fundamental field mass |
| Free parameters | two-vector era: 3 claimed (g, λ, ω), with ω scan-fitted per lepton and no discreteness mechanism (the standing open question); v4: m_φ, λ, g plus the unspecified constraint C[φ] |
| Formal artifacts | Lean 4: theorem STATEMENTS formalized; the existence proof is `sorry`-discharged and the formalized ODE differs from the integrated one (canonical § 4); the June GF-stability script is the corpus's most reproducible artifact |
| Solve method | 1D radial ODE / BVP (scipy) + statistics notebooks; no production port (the full-3D continuation is M7's program) |
| Next falsifier | A-linear vs A² nuclear discrimination (v4's own six-domain program, M6.5); the solar-wind sidereal protocol P1-P3 ([`research/ai_analysis/2026-07-11_1630_dm_solar_wind_review.md`](research/ai_analysis/2026-07-11_1630_dm_solar_wind_review.md)); sub-MeV direct detection |

## Decision-Relevant Attributes

| Attribute | M6 |
| --- | --- |
| Parameter economy | "3 parameters" is the era claim; the refresh's corpus read documents scan-fitted ω per lepton, a recalibrated g (1.0625 → 1.0000 with the harmonics silently moving), and fit-grade conventions behind the benchmark: the honest count awaits M6.2's pre-registered re-derivation ([`research/m6_theory_canonical.md § 4`](research/m6_theory_canonical.md)) |
| Formal artifacts | Lean 4 statements + the attached `chaoiton_gf_verification.py` scan (319/360 radial-GF-stable); our independent numerical reproduction of the canonical neutral profile ([`research/archive/0d_canonical.md`](research/archive/0d_canonical.md)) |
| Self-correction record | The record contains genuine public corrections: the July 5 retraction notice (LLM-generated placeholder numbers), the July 8 Test 1 walk-back, the in-era artifact retractions (23-solution and 1,208-solution claims). The refresh treats this as the working norm: claims are graded by what survives independent rerun |
| Falsifiable near-term tests | v4's A-linear vs A² six-domain suite; DAMA per-bin amplitude table; solar-wind modulation (sidereal split); sub-MeV searches; the A-scaling sensor discriminator (R = 1.125 nuclear vs 1.108 EM) from the author's detection-disclosure record |

## Field Configuration of Particles

Standing demand of any particle model: *state the field configuration of each particle,
and say whether it uses topological vortices.* M6's answers, with the v4 caveat that the
current spec's particle sector is silent (details: [`research/m6_particle_hunt.md`](research/m6_particle_hunt.md)):

| Particle | Field configuration in M6 (two-vector era) | Topological vortex? |
| --- | --- | --- |
| Electron | charged chaoiton, `Q_CS = +1`, ω = 1 | ✅ knot (linking) |
| Positron | `Q_CS = −1` (opposite linking sign) | ✅ (statement only) |
| Muon / tau | higher-ω states (values version-dependent: 11.0/40.7 → 12.82/50.0 → "bifurcation islands"); no ω-discreteness mechanism | ✅ claimed |
| Pion+ (candidate) | chaoiton at ω = 15.0 (3.25%) | ✅ claimed |
| Neutral chaoiton (DM) | `Q_CS = 0`, l = 1 p-wave → m_χ = 0.460 MeV, m_J = 0.6184 MeV, C = 770 MeV·fm | ✅ neutral knot (in-platform) |
| Proton | three-chaoiton bound state (Schwinger H-particle lineage) | 🚧 narrative-level |

Honest caveats preserved from the archive era and confirmed by the refresh read: the clock
is *built into* the `e^{iωt}` ansatz (assumed, not derived as energy minimizer); no
discrete-spectrum mechanism selects the lepton ω values; charge quantization is
Lean-stated plus author-claimed, not re-derived in-platform, and the underlying proof is
for static configurations while the solutions are time-periodic.

## Implementation Status

9 of 21 [`MODELS.md`](../../../MODELS.md) criteria carried (4 ✅, 5 ⚠️), 0 ❌, 12 🚧, ALL
earned in the archive era against the two-vector May 2026 spec. The refresh may move
cells in both directions: M6.2/M6.3 re-derive the electron-sector cells under
pre-registered conventions, and a failed re-derivation downgrades the cell as a
deliverable. Nothing from the July-era theory (+Eli, v4) is validated in-platform yet.

| Sector | Status |
| --- | --- |
| Particle stability | ✅ era: nodeless neutral BVP ground state (K₁ tail); oscillation as the genuine Derrick escape; census caveats (radial-only GF, 62/319/62 count) → M6.4 |
| Dark-matter candidate | ✅ era: m_χ = 0.460 MeV, parameter-free m_J (our strongest M6 result); the phenomenology chain above it (suppression factors, modulation inference) is unverified → M6.6 |
| Maxwell EM | ✅ era: `A_μ` is the 4-potential by construction (two-vector spec; absent from v4) |
| Electron rest mass | ✅ era, provenance-qualified: the H/Q chain is the canonical § 4 ledger (target drift; July 8 window-defined downgrade) → M6.2 re-derivation decides the cell |
| Charge quantization | ⚠️ Lean-stated + claimed; static-proof vs time-periodic gap; never computed in-platform → M6.3 |
| de Broglie clock | ⚠️ built into the ansatz, not emergent |
| Lepton spectrum | ⚠️ scan-fitted ω, no selection mechanism (the standing open question) → M6.4b |
| Magnetic moment + spin | the published g-factor match is the identity L = ωQ with ω chosen (v11's own footnote concedes this); honest status: not independently evidenced |
| Nuclear sector (v4's stake) | 🚧 the six-domain A-linear program is public-notebook grade, unaudited; the Sawada anomaly is described three inconsistent ways across the record → M6.5 |
| Quarks · baryons · weak · gravity · KG · orbitals | 🚧 not addressed (gravity explicitly out of scope "prior to gravity"; a Carmeli 5D embedding is asserted without equations) |

Deep dives: [`research/m6_theory_canonical.md`](research/m6_theory_canonical.md) (specs of
record, version lineage, THE PROVENANCE LEDGER § 4, consumption rules),
[`research/m6_roadmap.md`](research/m6_roadmap.md) (the M6.1+ program),
[`research/m6_particle_hunt.md`](research/m6_particle_hunt.md) (identification scorecards),
[`research/archive/0d_canonical.md`](research/archive/0d_canonical.md) (archive-era numerical
record).

## Roadmap (refresh era, re-scoped 2026-07-20)

The pre-analysis decision (recorded in [`research/m6_roadmap.md`](research/m6_roadmap.md)):
the program CLOSES THE LEDGER ON THE FROZEN two-vector v11 spec rather than tracking the
July-era moving target (three theory versions in 18 days; the drift evidence is the
canonical § 4 ledger). [M6.2](research/m6_roadmap.md) is the decision gate.

| Next | What lands |
| --- | --- |
| [M6.1](research/m6_roadmap.md) spec certification gate (small) | the v11 validation target frozen into one convention sheet; v4 characterized for the record (what is checkable in a day + the unspecified C[φ] documented) |
| [M6.2](research/m6_roadmap.md) THE DECISION GATE | H/Q under pre-registered conventions, no search: the electron cell re-earned (program continues) or honestly closed (M6 returns to hold on its DM sector + M7 lineage) |
| [M6.3](research/m6_roadmap.md) charge quantization in-platform | Q_CS computed on the converged chaoiton: ⚠️ → ✅ or the honest negative (rides M6.2 branch (a)) |
| [M6.4](research/m6_roadmap.md) stability census + ω-selection | the GF scan rerun + reconciled; any discreteness mechanism, or the clean bound (valuable on either M6.2 branch) |
| PARKED: [M6.5](research/m6_roadmap.md) / [M6.6](research/m6_roadmap.md) | the July-era nuclear + DM fitting programs, parked until the author freezes a spec (reopening condition in the roadmap); M6.6's solar-wind arm is spec-independent and can be pulled forward alone |
| OPTIONAL: [M6.7](research/m6_roadmap.md) the two-theories fork | only if continued engagement with the author is wanted |

The full-3D route remains **M7 HydroBoros**, which carries the two-vector Lagrangian,
`m_J`, `g`, and the benchmark onto a 3D lattice
([`../m7_hydroboros/__M7_model_briefing.md`](../m7_hydroboros/__M7_model_briefing.md)).

## Help Wanted

M6 is an open column mid-refresh; the highest-leverage contributions are exactly the
roadmap's re-derivations. A documented *negative* counts as much as a positive.

| You can contribute | How |
| --- | --- |
| The pre-registered H/Q re-derivation | derive the Q_CS normalization + H functional from the v11 spec, state conventions BEFORE running, report what falls out (M6.2's core) |
| An ω-discreteness mechanism | find what selects the lepton ω values, or bound the term sets that cannot (M6.4b) |
| A nuclear-domain audit | rerun any of v4's six A-linear domains from the named datasets with stated metrics (M6.5) |
| The solar-wind protocol | execute P1-P3 from [`research/ai_analysis/2026-07-11_1630_dm_solar_wind_review.md`](research/ai_analysis/2026-07-11_1630_dm_solar_wind_review.md) on public OMNI/L1 data (M6.6b) |
| A full-3D validation | M7's program; see its roadmap |

Flow: open an issue or discussion → fork → branch → PR with a DCO sign-off
(`git commit -s`), under Apache 2.0. See [`../../../MODELS.md`](../../../MODELS.md)
§ Contributing, [`../../../ONBOARDING_MODELS.md`](../../../ONBOARDING_MODELS.md),
[`../../../CONTRIBUTING.md`](../../../CONTRIBUTING.md). Model discussion runs in the
Models-of-Particles group.

## Rich Context for Deep Reader

This is top-level orientation content. For the full picture read
[`research/m6_theory_canonical.md`](research/m6_theory_canonical.md) first (its § 4
provenance ledger and § 6 consumption rules govern how every M6 number may be used), then
the roadmap and hunt pages, then the archive-era record in
[`research/archive/`](research/archive/). The author's paper corpus itself is local-only
([`theory/_CITATIONS.md`](theory/_CITATIONS.md)) with every record openly available at its
Zenodo DOI.
