# M7.10: Pure-Maxwell sector, the no-Lagrangian test

> **Status: PLANNED** (defined 2026-07-07; first task of the Phase 1 extension Maxwell track, runs after [M7.8](m7_8_helicity_pair.md) and [M7.9](m7_9_chaosbook.md)). Roadmap row: [`m7_roadmap.md`](../m7_roadmap.md) § IN PROGRESS. Results land in the [Phase 1 walkthrough](m7_phase1_walkthrough.md) § 7, the single report bundling M7.8 + M7.9 + M7.10 for the author's review. This doc carries the plan; FINDINGS land here at FINISH.

## 0. Naming note

"No-Lagrangian" names what is switched off: the coupling terms (`m_J² A·J` and `f(J·J)`), leaving only the plain Maxwell **evolution equations**, `∂E/∂t = ∇×B`, `∂B/∂t = −∇×E` (equivalently `d²A/dt² = −∇×∇×A` in temporal gauge on the div-free sector). The **Ouroboros theme stays**: the snake eating its tail (a rotating vortex of energy, spin as self-linked rotational motion) is the M6/M7 model identity and survives in the pure-Maxwell sector as the CK/Trkalian vortex itself; only the Lagrangian coupling machinery is removed. Evolution-first by construction: the whole task is stated in equations of motion, no variational formalism anywhere in the deliverable.

## 1. Objective

Establish, by measurement, exactly what pure Maxwell can and cannot do on our lattice. This bootstraps the M7.10-M7.14 Maxwell track with the two results the author's post-August re-entry needs: **Theorem 2 from the 2026-07-05 closure notes verified as a known-answer gate** (a Trkalian field `∇×F = λ₀F` solves free Maxwell exactly at `ω = cλ₀`), and the **honest boundary demonstrated rather than asserted** (pure free-space linear Maxwell holds no localized finite-energy state indefinitely: Nadirashvili + our Q11 dispersion work).

Two-track principle (2026-07-06 call): the Maxwell track runs alongside the harmonic/functional track that produced Phase 1, on the same lattice; measurements adjudicate.

## 2. The four experiments

| # | Experiment | Setup | Prediction (pre-registered) | Gate (known answer) |
| --- | --- | --- | --- | --- |
| E1 | Trkalian cavity control | CK Beltrami mode (`∇×F = λ₀F`), Dirichlet shell, evolve ≥ 20 periods | persists indefinitely: pure Maxwell CAN hold a Trkalian standing wave when walls confine it | **Theorem 2** (audited at receipt): period matches `ω = λ₀`, `λ_eff` alignment stays ≈ 1.0, energy drift at the integrator floor |
| E2 | Free-space evaporation | same CK seed, sponge absorbing boundary (the M7.5 `set_sponge`) instead of walls | evaporates on the light-crossing time (~`L/2`); windowed energy `E(<r, t)` decays, `r50(t)` grows at group velocity ≈ 1 | linear dispersion `ω = k`: escape rate matches the wave-packet prediction; helicity conserved until absorbed; Arnold bound `E ≥ λ₀\|H\|` never violated |
| E3 | Electron destruction test | load the Phase-1 winner (the M7.5/M7.6 rotating state), switch the coupling off at `t = 0`, evolve; a with-coupling twin run as control | control orbits stably (the M7.5 result); the no-coupling twin disperses; **destruction time measured** | the control's `⟨E_real⟩ = E_ω` identity (1.85e-14 at M7.5) re-verified in the same run |
| E4 | The coupling ladder | scale the cross force and `(c1, c2)` by `ε ∈ {1, 0.5, 0.25, 0.1, 0.05, 0}`; at each ε: harmonic relaxation (does a minimizer exist?) + real-time destruction time | genuinely open: does the soliton family continuously terminate at `ε → 0` with destruction time diverging smoothly, or is there a critical coupling? | endpoint anchors: `ε = 1` reproduces Phase 1, `ε = 0` reproduces E2/E3 |

## 3. The two headline claims this buys

| Claim | Evidence |
| --- | --- |
| Localization requires either walls or the coupling; free-space pure Maxwell holds nothing (the honest boundary, now a measurement) | E1 vs E2: identical seed, only the boundary differs; E3: identical state, only the coupling differs |
| The tachyon and the confinement have one source | pure Maxwell's vacuum is healthy (`ω = k`, no tachyon band); the Q14 tachyon (`det M(0) = −1`) lives entirely in the coupling sector. E4 locates where the tachyon band opens as ε rises, so the ladder measures the trade directly: the stabilizer and the pathology are bought with the same term |

## 4. M7.9 inputs (why this runs after the ChaosBook benchmark)

| From M7.9 | Used here |
| --- | --- |
| Periodic-orbit finding (Newton / multiple shooting) | E1's cavity CK mode IS a periodic orbit of the Maxwell flow: the cycle-finding tools verify it a second, independent way (beyond direct evolution) |
| Poincaré-section vocabulary + cycle-stability (Floquet) machinery | E3's destruction described as an orbit losing stability, in the language the author asked the program to learn; sets up the M7.11+ orbit hunt in the variable-λ flow |

## 5. Implementation

| Item | Content |
| --- | --- |
| Engine | the M7.5 `LeapfrogEngine` with an `eps_couple` scalar multiplying the `−J` / `−A` cross forces and `(c1, c2)`; `ε = 0` makes A and J two decoupled free-Maxwell copies, so E1/E2 run single-field (the factorization noted in FINDINGS) |
| Constraint watch | seeds are div-free (curl eigenfields); monitor `∇·A` drift, since the second-order temporal-gauge form equals the wave equation only on the div-free sector |
| Grids | 48³ smoke → 64³ record, `L = 16`, per the Phase 1 pattern; E2 adds one `L = 24` run to separate the sponge from the core |
| Cost | real-time runs are cheap (20 periods ≈ 16k leapfrog steps at 64³, minutes on Taichi); the ladder is 6 relaxations + 6 short evolutions; one focused session total |
| Artifacts | `scripts/m7_10_pure_maxwell.py` · `data/m7_10_*.json` · `plots/m7_10_*.png` · checkpoints to `research/checkpoints/m7_10_progress.md` |

## 6. Unknowns pass (blindspots at PLAN)

| Unknown | Route |
| --- | --- |
| Does the cavity CK mode survive the discrete curl's dispersion at 64³? (lattice `λ_eff` vs continuum `λ₀`) | machine-checkable: E1 measures it; if drift appears, it calibrates the lattice, not the physics |
| What happens to the J field of the winner at `ε = 0` (drop it, or evolve it decoupled)? | both, cheaply: A-only and decoupled-pair variants of E3; FINDINGS records which is the honest "no-Lagrangian" reading |
| Is a sponge a fair "free space"? | stated caveat + the `L = 24` check; an author-facing doc must not oversell |
| Whether the ε-ladder minimizers exist at small ε | nature-gated, the point of E4; either outcome is a result |

## 7. Cross-refs

[Roadmap](../m7_roadmap.md) · [M7.8](m7_8_helicity_pair.md) · [M7.9](m7_9_chaosbook.md) (orbit-hunting toolkit input) · [Phase 1 walkthrough](m7_phase1_walkthrough.md) (§ 7 carries the results, one report for M7.8 + M7.9 + M7.10) · [tracker](../m7_question_tracker.md) (Q14 tachyon attribution, Q13 flow definition) · closure-notes provenance: [`theory/_CITATIONS.md`](../../theory/_CITATIONS.md).
