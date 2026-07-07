# M7.10: Pure-Maxwell sector, the no-Lagrangian test

> **Status: PLANNED** (defined 2026-07-07; first task of the Phase 1 extension Maxwell track, runs after [M7.8](m7_8_helicity_pair.md) and [M7.9](m7_9_chaosbook.md)). Roadmap row: [`m7_roadmap.md`](../m7_roadmap.md) § IN PROGRESS. Results land in the [Phase 1 walkthrough](m7_phase1_walkthrough.md) § 7, the single report bundling M7.8 + M7.9 + M7.10 for the author's review. This doc carries the plan; FINDINGS land here at FINISH.

## 0. Naming note

"No-Lagrangian" names what is switched off: the coupling terms (`m_J² A·J` and `f(J·J)`), leaving only the plain Maxwell **evolution equations**, `∂E/∂t = ∇×B`, `∂B/∂t = −∇×E` (equivalently `d²A/dt² = −∇×∇×A` in temporal gauge on the div-free sector). The **Ouroboros theme stays**: the snake eating its tail (a rotating vortex of energy, spin as self-linked rotational motion) is the M6/M7 model identity and survives in the pure-Maxwell sector as the CK/Trkalian vortex itself; only the Lagrangian coupling machinery is removed. Evolution-first by construction: the whole task is stated in equations of motion, no variational formalism anywhere in the deliverable.

## 1. Objective

Establish, by measurement, exactly what pure Maxwell can and cannot do on our lattice. This bootstraps the M7.10-M7.14 Maxwell track with the two results the author's post-August re-entry needs: **Theorem 2 from the 2026-07-05 closure notes verified as a known-answer gate** (a Trkalian field `∇×F = λ₀F` solves free Maxwell exactly at `ω = cλ₀`), and the **honest boundary demonstrated rather than asserted** (pure free-space linear Maxwell holds no localized finite-energy state indefinitely: Nadirashvili + our Q11 dispersion work).

Two-track principle (2026-07-06 call): the Maxwell track runs alongside the harmonic/functional track that produced Phase 1, on the same lattice; measurements adjudicate.

## 2. The four experiments

Nomenclature for the switches (they are TWO, and they separate): `ε_x` scales the bilinear cross force (`−J` in the A equation, `−A` in the J equation, from `m_J²A·J`); `ε_q` scales the quartic coefficients `(c1, c2)` (from `f(J·J)`). "Coupling off" = both zero. The linearized vacuum matrix at scaled couplings is `M(k) = [[k², −ε_x], [−ε_x, k² + 2ε_q c1]]`, so **`det M(0) = −ε_x²`: the tachyon is carried entirely by the bilinear term** (with `ε_x = 0` and `ε_q > 0` the J sector is simply massive, `m² = 2ε_q c1`, and the vacuum is healthy). This one-line determinant is itself a pre-registered claim the runs confirm.

| # | Experiment | Setup | Prediction (pre-registered) | Gate (known answer) |
| --- | --- | --- | --- | --- |
| E1a | Exact discrete eigenmode (integrator floor) | ABC/Trkalian eigenfield on the **periodic** box (`seed_abc`, `m7_1_harmonic_lattice.py:512`): an exact eigenfield of the DISCRETE curl with eigenvalue `λ_h = sin(kh)/h` (recorded by the seeder as `lam_discrete`) | oscillates as `A(x) cos(λ_h t)` indefinitely; period known EXACTLY including discretization | energy drift + period error at the integrator floor (O(dt²), the M7.5 gate pattern); this is the cleanest known-answer test the Maxwell track has |
| E1b | Trkalian cavity control (the walls story) | CK spheromak (`seed_ck_spheromak`, `m7_1_harmonic_lattice.py:530`; `a = 0.30L`, `λ = 4.4934/a ≈ 0.936` at `L = 16`), Dirichlet shell, evolve ≥ 20 periods at `ω` set to the **measured lattice** `λ_eff` (apply the discrete curl to the seed once and read it; do not assume the continuum value) | persists: pure Maxwell CAN hold a Trkalian standing wave when walls confine it | **Theorem 2** (audited at receipt): standing oscillation at `ω = λ`, `λ_eff` alignment ≈ 1.0 across the ball, energy drift at the integrator floor; any period offset vs continuum `λ` calibrates the lattice dispersion, not the physics |
| E2 | Free-space evaporation | same CK seed, sponge absorbing boundary (`set_sponge(width=8, gamma0=0.5)`, `m7_5_clock_stability.py:203`) instead of walls; one `L = 24` run to separate sponge from core | evaporates on the light-crossing time (~`L/2` at group velocity 1); windowed energy `E(<r, t)` decays, `r50(t)` grows | linear dispersion `ω = k`: escape rate matches the wave-packet prediction; helicity conserved until absorbed; Arnold bound `E ≥ λ\|H\|` never violated while the field remains in the window |
| E3 | Electron destruction: two mechanisms, one state | load the Phase-1 winner (`get_winner_state`, `m7_5_clock_stability.py:241`; regen ~4 min, the npz cache is deleted per the >1MB rule), evolve twice from identical initial data: (i) coupling ON (`ε_x = ε_q = 1`) and (ii) coupling OFF | **both die, differently** (the M7.5 correction: the coupled real-time state is destroyed in ~2T by the vacuum tachyon, growth rate 0.786; the harmonic frame is immune, real time is not). ON: amplitude GROWTH, `\|A\|²` doubling by `t ≈ 0.4T`, FFT peak at the band-edge 0.62-0.64. OFF: the vacuum is healthy, no growth; the state DISPERSES (amplitude decay, `r50` growth at speed ≈ 1, `E_core` draining on the light-crossing time) | the `⟨E_real⟩ = E_ω` identity (1.85e-14 at M7.5) re-verified on the first period of the ON run; the OFF run's spreading rate vs the `ω = k` wave-packet prediction; the two destruction signatures (growth vs spreading) cleanly distinguished in `A²(t)`, `r50(t)`, and the probe FFT |
| E4 | The coupling ladder | diagonal `ε_x = ε_q = ε ∈ {1, 0.5, 0.25, 0.1, 0.05, 0.025, 0}` + the two attribution points (`ε_x = 0, ε_q = 1`) and (`ε_x = 1, ε_q = 0`); at each ε: (a) vacuum-noise growth rate (the M7.5 `vacuum` mode), (b) harmonic relaxation at `ω = 1` fixed `Q_can + H_A` (does a localized minimizer exist? `r50(ε)`), (c) real-time destruction time from the relaxed state | **analytic curve, pre-registered**: band edge `k*(ε) = 0.786√ε`, max growth rate `0.786√ε` at `k = 0`, existence threshold `ω*(ε) = 0.786√ε`; destruction-time crossover: tachyon-dominated (`t_d ~ 1/(0.786√ε)`) above `ε ≈ 0.03`, dispersion-dominated (light-crossing, ε-independent) below it. Open (nature-gated): does `r50(ε)` diverge smoothly as `ε → 0` (continuous delocalization) or is there a critical ε? | endpoint anchors: `ε = 1` reproduces the M7.5 numbers (rate 0.785, `ω* = 0.786`), `ε = 0` reproduces E2/E3-OFF; the measured rates vs the `0.786√ε` curve at every rung |

## 3. The two headline claims this buys

| Claim | Evidence |
| --- | --- |
| Localization requires either walls or the coupling; free-space pure Maxwell holds nothing (the honest boundary, now a measurement) | E1b vs E2: identical seed, only the boundary differs; E3: identical state, only the coupling differs (and the coupled state dies too, by the OTHER mechanism: what the coupling buys at canonical strength is the harmonic orbit's existence, not real-time immortality: the honest statement of the two-track trade) |
| The tachyon and the confinement have one source, and it is the bilinear term specifically | pure Maxwell's vacuum is healthy (`ω = k`); `det M(0) = −ε_x²` puts the tachyon entirely in the cross term (the `ε_x = 0, ε_q = 1` attribution point verifies: healthy vacuum, massive J); the E4 ladder traces `ω*(ε) = 0.786√ε`, the measured price curve of the stabilizer |

## 4. M7.9 inputs (why this runs after the ChaosBook benchmark)

| From M7.9 | Used here |
| --- | --- |
| `find_cycle` (Newton / multiple shooting, `m7_9_orbits.py`) | E1b's cavity CK mode IS a periodic orbit of the Maxwell flow (period `2π/λ`): the cycle finder verifies it a second, independent way (beyond direct evolution), through a state-vector adapter on the lattice leapfrog |
| `floquet` + Poincaré-section vocabulary | E1b's multipliers on the unit circle = marginal stability, the orbit-language statement that pure Maxwell provides no attractor; E3's two destructions described in the same language (tachyon = a multiplier off the unit circle from the coupling; dispersion = the marginal spectrum spreading the packet); sets up the M7.11+ orbit hunt in the variable-λ flow |

## 5. Implementation

| Item | Content |
| --- | --- |
| Engine | the M7.5 `TaichiLeapfrog` (velocity-Verlet, cached accelerations, Dirichlet shell, `m7_5_clock_stability.py:89`) with the forces `FA = −∇×∇×A − ε_x J`, `FJ = −∇×∇×J − ε_x A − 2ε_q(c1 + 2c2\|J\|²)J`; two scalar parameters, no new kernels. `ε = 0` makes A and J two decoupled free-Maxwell copies, so E1/E2 run single-field (the factorization noted in FINDINGS) |
| Time step | `dt = 0.2h` (the M7.5 record value), one halved-dt repeat on E1a to show the O(dt²) floor; 20 periods at ω ≈ 1 is ~16k steps at 64³ |
| Diagnostics to reuse | the `evolve` trace battery (`m7_5_clock_stability.py:272`): E/E_kin/E_curl/E_pot, doublet overlaps `ov_c/ov_s` + `clock_fit` for the period, probe-point FFT, and the heavy channel (`q_abs`, `r50`, `E_core`) that E2/E3 read their evaporation curves from; `λ_eff` maps per M7.4; helicity via `helicity_A` |
| Constraint watch | seeds are div-free (curl eigenfields); monitor `∇·A` drift (`div_np`), since the second-order temporal-gauge form equals the wave equation only on the div-free sector |
| Harmonic rungs (E4b) | `relax_qcan` (`m7_6_observables.py:90`) at fixed `Q_can + H_A` with the ε-scaled engine params; seed = the blend; watch the `maxf` guard (the small-ε relaxations may delocalize slowly: cap iterations, report `r50` at cap honestly) |
| Grids | 48³ smoke → 64³ record, `L = 16`, per the Phase 1 pattern; E2 adds one `L = 24` run to separate the sponge from the core |
| Cost | real-time runs are minutes each on Taichi; the ladder is ~8 relaxations + ~10 short evolutions; one focused session total |
| Artifacts | `scripts/m7_10_pure_maxwell.py` · `data/m7_10_*.json` · `plots/m7_10_*.png` · checkpoints to `research/checkpoints/m7_10_progress.md` |

## 6. Unknowns pass (blindspots at PLAN)

| Unknown | Route |
| --- | --- |
| Does the cavity CK mode survive the discrete curl's dispersion at 64³? (lattice `λ_eff` vs continuum `λ₀ = 4.4934/a`) | machine-checkable: measure the discrete eigenvalue up front (one curl application) and set ω to IT; E1a makes the discretization itself a known answer (`λ_h = sin(kh)/h`); any residual drift calibrates the lattice, not the physics |
| The CK ball seed is only C⁰ at `r = a` (hard cutoff at the Bessel zero) | the corner radiates a transient; let it ring down for ~2 periods before measuring drift, and report the transient honestly |
| What happens to the J field of the winner at `ε = 0` (drop it, or evolve it decoupled)? | both, cheaply: A-only and decoupled-pair variants of E3; FINDINGS records which is the honest "no-Lagrangian" reading |
| Is a sponge a fair "free space"? | stated caveat + the `L = 24` check; an author-facing doc must not oversell |
| Whether the ε-ladder minimizers exist at small ε (and whether the relaxation converges there at all) | nature-gated, the point of E4; slow-delocalization runs are capped and reported at cap; either outcome is a result |
| The `0.786√ε` analytic curve assumes the diagonal scaling `ε_x = ε_q` | stated; the two single-switch attribution points bound the off-diagonal behavior |

## 7. Cross-refs

[Roadmap](../m7_roadmap.md) · [M7.8](m7_8_helicity_pair.md) · [M7.9](m7_9_chaosbook.md) (orbit-hunting toolkit input) · [Phase 1 walkthrough](m7_phase1_walkthrough.md) (§ 7 carries the results, one report for M7.8 + M7.9 + M7.10) · [tracker](../m7_question_tracker.md) (Q14 tachyon attribution, Q13 flow definition) · closure-notes provenance: [`theory/_CITATIONS.md`](../../theory/_CITATIONS.md).
