# The M6 particle hunt: chaoitons claimed, identifications graded

Modeled on the M5 hunt page ([`../../m5_liquid_crystal/research/m5_particle_hunt.md`](../../m5_liquid_crystal/research/m5_particle_hunt.md)): the SHAPE (a localized time-periodic two-field soliton, the chaoiton) is what the record contains; the particle NAME riding each shape is a hypothesis that keeps its "possibly" until the anchors survive re-derivation. M6's grading problem differs from M5's: most M5 anchors are our own in-platform measurements, while most M6 anchors are the author's published claims whose provenance the refresh has now mapped ([`m6_theory_canonical.md § 4`](m6_theory_canonical.md)). Scores below therefore carry a PROVENANCE grade alongside the status icon.

![the ouroboros chaoiton](images/ouroboros_icon.jpg)

**The v4 caveat that hangs over this whole page**: the current published spec (Ouroboros+Eli+Fable v4, 2026-07-20) is a scalar-field recast whose particle sector is SILENT: none of the identifications below is restated in it, none is retracted ([`m6_theory_canonical.md § 1`](m6_theory_canonical.md), OQ1). Until the two-theories fork is resolved (roadmap M6.7), every row below is graded against the two-vector spec lineage (v11-class) it was claimed under.

## The chaoiton catalog (identification hypotheses, by particle)

| Particle | Field configuration claimed | Status + provenance grade | Fate in v4 |
| --- | --- | --- | --- |
| Electron | charged chaoiton, mutual Chern-Simons linking Q_CS = +1, ω = 1 | 🔶 the H/Q mass benchmark is the corpus's most provenance-laden number (target drift; the "independent reproduction" was a variant search, our own 2026-05-21 disclosure; publicly downgraded to a window-defined internal quantity on July 8): re-derivation = roadmap M6.2 | silent |
| Positron | Q_CS = −1 (opposite linking) | 🚧 statement only, never computed | silent |
| Muon / tau | higher-ω states of the same couplings: ω = 11.0 / 40.7 (May 16, g = 1.0625) then 12.82 / 50.0 (May 23, g = 1.0) then "(Ω, G) bifurcation islands" (June 29, no mass values) | ⚠️ the ω values are scan-fitted, the discreteness mechanism is admitted open (every ω in 1-60 localizes equally); our archive-era scan measured the mass scaling H/Q ∝ ω^2.04 against the published ω^2.22, which is what the observed mass ratios require | silent |
| Pion+ | chaoiton at ω = 15.0, 3.25% from 139.57 MeV | ⚠️ same scan-fit class; π⁰ (ω = 0) unexplained | silent |
| Proton | three-chaoiton bound state (the Schwinger "H particle" lineage); the proton-radius puzzle as probe-dependent Yukawa sampling | 🚧 narrative-level, no bound-state computation anywhere in the record | v4 couples to nucleon density ρ_n but derives no nucleon |
| Neutrinos | not addressed in any era (the Q_CS = 0 object is positioned as dark matter, not a neutrino) | 🚧 open gap in the framework | silent |
| Neutral chaoiton (DM) | Q_CS = 0, l = 1 p-wave ground state | ✅ in-platform (archive era): m_χ = 0.460 MeV with mediator m_J = 0.6184 MeV parameter-free via the exact scaling symmetry, nodeless BVP ground state with K₁ tail; our strongest M6 result | promoted: m_φ ≈ 0.460 MeV becomes the FUNDAMENTAL field mass in v4 |

## ELECTRON HUNT scorecard (criteria synced with [`MODELS.md`](../../../../MODELS.md))

| Criterion | Status | The record, honestly |
| --- | --- | --- |
| Charge quantization (±e) | ⚠️ | Q_CS = Hopf-invariant integer: Lean 4 artifacts are statement-level (existence theorem `sorry`-discharged; formalized ODE differs from the integrated one), the mathematical proof is for STATIC configurations while every chaoiton is time-periodic; never re-derived in-platform → M6.3 |
| Coulomb far field | 🚧 | the record contains BOTH claims: the foundational paper derives a Yukawa (exponential) far field "not Coulombic" (its nuclear-force selling point), while LoE v11 § 6.1 derives V_int = Q₁Q₂/(4πR) from the J·A coupling; force-level Coulomb between two chaoitons has never been computed in-platform |
| Mass anchor (0.511 MeV) | 🔶 | H/Q: the full provenance ledger is [`m6_theory_canonical.md § 4`](m6_theory_canonical.md) (target drift 1.6875 → 1.6969; g recalibrated 1.0625 → 1.0 improving the headline to 0.09%; the July 8 public downgrade to "window-defined, code-to-code 4.7×10⁻⁵"). The clean pre-registered re-derivation is M6.2 |
| de Broglie clock (ZBW) | ⚠️ | time-periodicity is BUILT INTO the e^{iωt} ansatz, not derived as the energy minimizer; the claimed ZBW-frequency match (1.2%) is near-automatic once R_phys is fixed by m_e; contrast M5, where the clock is the measured energy-minimizing state |
| Particle stability (Derrick escape) | ✅ (era) | oscillation is the genuine third Derrick escape and the archive-era BVP ground state is real; the Gelfand-Fomin census covers RADIAL perturbations only, and the count is unreconciled across the record (62 / 319 / 62) → M6.4; the M7 3D continuation found the truncation's real-time vacuum unconditionally tachyonic, the honest 3D caveat |
| Spin J + magnetic moment (g ≈ 2) | ❌ as evidence | 2L/Q = 2ω = 2.000 "vs 2.00232 (0.116%)" reduces to the identity L = ωQ with ω = 1 chosen; v11's own footnote concedes it is "a consistency check on ω, not an independent derivation of spin from topology" |
| Spin-½ statistics (720°) | 🚧 | never addressed in any era |
| Antimatter + annihilation | 🚧 | Q_CS = −1 named; no annihilation computation |
| **Anchored rows** | **1 era-✅ / 8** | the hunt's honest core: stability-by-oscillation is real and in-platform; everything identification-grade routes through M6.2/M6.3 |

## NEUTRAL CHAOITON (DM) HUNT scorecard

| Criterion | Status | The record, honestly |
| --- | --- | --- |
| Chargeless (no EM coupling) | ✅ (era) | Q_CS = 0 by construction; the l = 1 monopole-coupling cancellation (∫dΩ Y_1m = 0) is clean at Born level |
| Mass + mediator | ✅ (era) | m_χ = 0.460 MeV, m_J = 0.6184 MeV parameter-free via the exact neutral-sector scaling symmetry; computed in-platform ([`archive/sandbox_v11/`](archive/sandbox_v11/)); the one M6 number with fully local provenance |
| Ground-state stability | ✅ (era) | nodeless BVP ground state, K₁ exponential tail, zero sign changes; earlier "23 solutions" and "1,208 solutions" claims were artifacts, corrected in-era |
| Direct-detection suppression | 🔶 | σ_p ≈ 9×10⁻⁴¹ cm² rests on multiplying two suppression factors (S_vert, \|F_dipole\|²) whose independence is asserted, not derived (DM v12's own wording: "a plausible estimate") |
| Bullet Cluster (self-interaction) | 🔶 | the \|F_dipole\|⁴ rescue spans 14 orders of magnitude and the angular integrals "do not trivially factorise" (paper's own caveat); the NEGF vertex check is named as in progress on the author's side |
| Annual / sidereal modulation | 🔶 | six-peak Gaia-stream annual prediction (traceable kinematics) + the solar-wind sidereal claim, which our adversarial review found unsupported as an inference (findings F1-F6, executable falsification protocol P1-P5: [`ai_analysis/2026-07-11_1630_dm_solar_wind_review.md`](ai_analysis/2026-07-11_1630_dm_solar_wind_review.md)) → M6.6 |
| Relic abundance | 🚧 | order-of-magnitude overlap with Planck claimed (freeze-in); no in-platform computation |
| **Anchored rows** | **3 era-✅ / 7** | the DM hunt is M6's strongest: the candidate's core numbers are ours; the phenomenology chain above them is the unverified layer |

## Reading the hunts together

The asymmetry is the inverse of M5's. In M5 the electron hunt leads (five validated rows) and the neutrino is structural; in M6 the NEUTRAL chaoiton leads (its mass, mediator, and ground state are in-platform results with local provenance) while the electron identification rests on the benchmark chain whose provenance the refresh has now documented. The sharpest discriminators going forward: the pre-registered H/Q re-derivation (M6.2, no search allowed, THE DECISION GATE of the re-scoped program), Q_CS computed on a converged state (M6.3), and any ω-discreteness mechanism (M6.4b, the question that decides whether the μ/τ rows are physics or curve-labeling). The A-linear vs A² nuclear program (M6.5), where the current spec (v4) stakes its entire empirical case, is PARKED with the July-era work until the author freezes a spec (the roadmap's pre-analysis decision, 2026-07-20).
