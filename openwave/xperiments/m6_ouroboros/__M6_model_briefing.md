# M6 Ouroboros: Model Briefing

> **What M6 brings.** A classical two-vector-field theory where every particle is a knotted,
> time-periodic soliton (a "chaoiton") whose integer Chern-Simons / Hopf linking number *is*
> electric charge, reproducing the electron, the lepton spectrum, and a sub-MeV dark-matter
> candidate from one Lagrangian. It is a published, externally-cited credibility anchor,
> currently on permanent hold at the sandbox level.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M6 |
| Name | Ouroboros (Chaoiton framework) |
| Author | Paul J. Werbos (NSF, retired) |
| Collaboration | AI co-authorship disclosed on the papers: DeepSeek + Claude (Sonnet 4.6, Code Opus 4.7); OpenWave contributed the neutral-chaoiton BVP profile + scaling symmetry |
| Lineage | Schwinger 1969 dyons + Maxwell extension (toroidal-poloidal mutual confinement); shares the Schwinger ancestor with M5 |
| Primary sources | [`research/0d_canonical.md`](research/0d_canonical.md); Werbos Zenodo 20030162 (chaoitons), 20296060 (Lean Hopf proof), 20350105 (DM paper v2) |
| In-repo | `research/` + `theory/` + `research/sandbox_v8..v11` scripts (sandbox-only; no Taichi production port) |

## Model Profile (what it brings, short form)

| Attribute | M6 |
| --- | --- |
| Substrate | two coupled Lorenz-constrained vector fields `A_μ, J_μ` on Minkowski (−,+,+,+) |
| Lagrangian | `L = −¼F·F − ¼G·G + m_J² A·J − f(J·J)`, `f(s) = (g/4)s²` (F = dA, G = dJ) |
| Particle | chaoiton = localized time-periodic soliton; charge = mutual Chern-Simons linking `Q_CS` (= Hopf invariant) |
| Derrick escape | time-periodicity / oscillation (the "third escape") |
| EM | `A_μ` IS the EM 4-potential; Maxwell exact in the J→0 linear limit |
| Electron benchmark | `H/Q = 1.6969` (0.090% at g = 1, ω = 1) |
| Free parameters | 3 claimed (g, λ, ω); the neutral-sector exact scaling closes the (g, λ) plane → `m_J` parameter-free |
| Formal artifacts | Lean 4 proofs (linking-number quantization Zenodo 20296060, mountain-pass existence, power counting) |
| Solve method | 1D radial ODE / BVP (scipy), sandbox-only |
| Next falsifier | sub-MeV direct-detection; six-peak Gaia-stream annual modulation of the J-field flux; NEGF vertex check |

## Decision-Relevant Attributes

Model-level attributes to weigh the column: parameter economy, the formal artifacts that
back the claims, and what would falsify the model next. (Held here for now; a consolidated
cross-model version may return to `MODELS.md` later.)

| Attribute | M6 |
| --- | --- |
| Free parameters | 3 claimed (g, λ, ω); the neutral sector's exact scaling symmetry closes the (g, λ) plane, making m_J parameter-free (in-platform result)<br>[`research/0c_sandbox_v11.md`](research/0c_sandbox_v11.md) |
| Formal artifacts | Author's Lean 4 proof artifacts (linking number, mountain-pass existence, power counting) + our independent numerical reproduction of the canonical profile and benchmark<br>[`research/0d_canonical.md`](research/0d_canonical.md) |
| Falsifiable near-term tests | Author's roadmap: NEGF vertex check, sub-MeV searches, six-peak Gaia-stream annual modulation of the J-field flux<br>[`research/0e_dm_paper_review.md`](research/0e_dm_paper_review.md) |
| Direct-detection compatibility (DM) | Dipole-suppressed chaoiton-proton cross section claimed compatible with direct-detection bounds (the monopole coupling vanishes by angular-momentum orthogonality; the numerical chain is still being reconciled on the author's side)<br>[`research/0e_dm_paper_review.md`](research/0e_dm_paper_review.md), [`research/sandbox_v11/dm_paper_supplement/`](research/sandbox_v11/dm_paper_supplement/) |

## Field Configuration of Particles

Standing demand of any particle model: *state the field configuration of each
particle, and say whether it uses topological vortices.* M6's answers:

| Particle | Field configuration in M6 | Topological vortex? |
| --- | --- | --- |
| Electron | charged chaoiton, `Q_CS = +1`, ω = 1 → `H/Q = 1.6969` | ✅ knot (linking) |
| Positron | `Q_CS = -1` (opposite linking sign) | ✅ |
| Muon / tau | ω-harmonics (12.82 → 0.80%, 50.0 → 6.47%) | ✅ |
| Pion+ (candidate) | charged chaoiton at ω = 15.0 → 3.25% | ✅ |
| Neutral chaoiton (DM) | `Q_CS = 0`, l = 1 p-wave → m_χ = 0.460 MeV, m_J = 0.6184 MeV, C = 770 MeV·fm | ✅ neutral knot |

Honest caveat on this test: the clock is *built into* the `e^{iωt}` ansatz (assumed, not
yet derived as the energy-minimizer), and no discrete-spectrum mechanism selects the lepton
ω values (every ω in 1-60 localizes equally). Charge quantization is Lean-proved plus
author-claimed, not yet re-derived in-platform.

## Implementation Status

9 of 21 MODELS.md criteria carried (4 ✅ validated in-platform, 5 ⚠️ partial), 0 ❌,
12 🚧 planned. All results are sandbox / 1D radial BVP; there is no Taichi production port
(Stage-2 NO-GO → permanent hold). The dark-matter paper (ApJ-targeted, Zenodo 20350105 v2)
uses OpenWave's numbers verbatim and is M6's credibility anchor.

| Sector | Status |
| --- | --- |
| Electron rest mass | ✅ `H/Q = 1.6969` (0.090%) |
| Particle stability | ✅ neutral BVP ground state (K₁ tail, zero sign changes) |
| Dark-matter candidate | ✅ neutral chaoiton m_χ = 0.460 MeV, parameter-free m_J |
| Maxwell EM | ✅ `A_μ` is the 4-potential by construction |
| Charge quantization | ⚠️ Lean-proved + author claim, not re-derived in-platform |
| de Broglie clock | ⚠️ built into the ansatz, not emergent |
| Lepton spectrum | ⚠️ μ / τ fit at chosen harmonics; no ω-selection mechanism |
| Magnetic moment · spin · quarks · gravity · weak | 🚧 not addressed / paper-level |

Deep dives: [`research/0d_canonical.md`](research/0d_canonical.md) (canonical numerical
spec), [`research/0b_M6_roadmap.md`](research/0b_M6_roadmap.md),
[`research/0b_question_tracker.md`](research/0b_question_tracker.md),
[`research/0e_dm_paper_review.md`](research/0e_dm_paper_review.md).

## Roadmap

Status: **permanent hold**. Stage-1 is a strong pass at the sandbox level; Stage-2 (the
Taichi production port) is a NO-GO unless a trigger lands. The full-3D route M6 never took is
picked up by **M7 HydroBoros**, which carries M6's Lagrangian, `m_J`, `g`, and the `H/Q`
benchmark onto a 3D lattice (see [`../m7_hydroboros/__M7_model_briefing.md`](../m7_hydroboros/__M7_model_briefing.md)).

| Next | What lands |
| --- | --- |
| Author's near-term tests | NEGF vertex check; sub-MeV searches; six-peak Gaia-stream annual modulation |
| Discrete-ω mechanism | find what selects the lepton ω values (the key open question) |
| QCD reconciliation | the 3-chaoiton proton (Schwinger H-particle); active neutrinos |
| Full-3D continuation | M7 HydroBoros (above) |

## Help Wanted

M6 is on hold but fully reproducible from the canonical spec. Contributions welcome.

| You can contribute | How |
| --- | --- |
| A full-3D validation | the biggest open gap: run the chaoiton on a lattice (M7's program) |
| A discrete-ω mechanism | find what selects the lepton ω values |
| An independent re-derivation | reproduce `H/Q` or the DM inputs from [`research/0d_canonical.md`](research/0d_canonical.md) |
| A falsifier test | the Gaia-stream modulation or a sub-MeV direct-detection comparison |

Flow: open an issue or discussion → fork → branch → PR with a DCO sign-off
(`git commit -s`), under Apache 2.0. See [`../../../MODELS.md`](../../../MODELS.md)
§ Contributing, [`../../../ONBOARDING_MODELS.md`](../../../ONBOARDING_MODELS.md),
[`../../../CONTRIBUTING.md`](../../../CONTRIBUTING.md). Model discussion runs in the
Models-of-Particles group.
