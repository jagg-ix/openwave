# M7.8: the helicity-pair 3:1 test + the Phase 1 walkthrough

> **Status: GO** (confirmed at the 2026-07-06 Phase-1-review call with the author; Phase 1 extension). Roadmap row: [`m7_roadmap.md`](../m7_roadmap.md) § IN PROGRESS. Author-convo record: `theory/author_convos/m7_phase1_convo.pdf` (local-only). This doc carries the plan; FINDINGS land here at FINISH.

## 1. Context and what changed at the call

| Input | State |
| --- | --- |
| The Q15 units contract | **RESOLVED-directive** ([tracker](../m7_question_tracker.md#q15-detail)): the author pins no frequency mapping ("the frequency is emergent... there is only one frequency that works"); the directive is "make the decision that gives us the proper spin ℏ/2, whatever's coming out of your model is fine". The **observable `S_z = ℏ/2` is the target**; this task measures it |
| The 3:1 ratio | The author suspects early-model drift in his own notes but ruled: "it's part of the model right now, so we run with it, that's part of the ansatz". The two-line algebra (§ 3) is not in dispute; whether the closure postulates survive full 3D nonlinear relaxation is the measurable question |
| The audit loop | Agreed at the call: we run at zero cost to him, send the data + the walkthrough, and **he runs his own adversarial pass** (his tools, his framing). We treat whatever comes back as external-audit evidence per [`AI_HYGIENE.md`](../../../../../AI_HYGIENE.md) |
| Trust context | The author's stated blocker is under-the-hood visibility ("how could a single-person team on a laptop run extensive complex simulations..."): deliverable (b) answers it head-on |

## 2. Deliverables (three)

| # | Deliverable | Gate |
| --- | --- | --- |
| a | The helicity-pair run (§ 4) | `U₊/U₋` measured vs the closure prediction `3 + α/2 + 4f_bb`; the pair-asymmetry spin `(U₊ − U₋)/ω` measured vs the ℏ/2 directive |
| b | [`m7_phase1_walkthrough.md`](m7_phase1_walkthrough.md), the under-the-hood report (§ 5) | readable by the author standalone; every § 5 question from the call answered with evidence links |
| c | Refresh [`m7_theory_canonical.md`](../m7_theory_canonical.md) (scheduled refresh #1; #2 rides M7.21) | METHOD_NOTE-current (file:line audit links, not just section permalinks); self-sufficient on: the ansatz, the integrator, the lattice, how charge is computed, how energy is computed; both Q15 frequency readings versioned in § 4 until the measurement decides |

## 3. The prediction being tested (from the 2026-07-05 closure notes, re-derived at receipt)

With `U₊ + U₋ = ℏω` (one quantum, P2) and `(U₊ − U₋)/ω = ℏ/2` (spin, P3):

```text
U₊ = 3ℏω/4,  U₋ = ℏω/4   ⟹   U₊/U₋ = 3                       (δ = 0)
U₊/U₋ = (3 − 2δ)/(1 − 2δ) ≈ 3 + α/2 + 4f_bb ≈ 3.004 + 4f_bb   (δ = α/8 + f_bb)
```

The arithmetic is forced; the physics under test is whether P2 + P3 survive in the full nonlinear 3D theory. Cross-formalism design: the notes predict analytically in a thin-torus ansatz; the lattice relaxes to the true minimizer with no ansatz assumed in the final state, then reads the observables.

## 4. Run plan (deliverable a)

### 4a. Seed recipe (the repaired pair, concrete lattice construction)

Angle conventions follow the closure notes: **φ = poloidal, θ = toroidal** (note this is the REVERSE of the usual plasma convention; the notes' `m` counts poloidal winding). Lattice angles: `θ_tor = atan2(y, x)`; `φ_pol = atan2(z, ρ − R₀)` with `ρ = √(x²+y²)`; minor radius `d` from the existing `_ring_frame` (`m7_4_linked_vortex.py:261`).

| Item | Value |
| --- | --- |
| Closure parameters in lattice units | `ω = cλ₀` (P1) with the canonical `ω = 1` gives `λ₀ = 1`, `σ = 2/λ₀ = 2`, `w = λ₀σ² = 4` (the Case-B pinning expressed in program units) |
| Radial profile | LG ground state `Ψ(d) = (d/σ)e^{−d²/2σ²}` (exact under the closures; replaces the Bessel `F` of the constant-λ modes) |
| Mode components (from the notes' CK formulas, `F → Ψ`) | `A_r = −[(m/d)Ψ + (k/(sλ₀))Ψ′]sin χ` · `A_φ = −[Ψ′ + (mk/(sλ₀ d))Ψ]cos χ` · `A_θ = (sα²/λ₀)Ψ cos χ`, with `k = n/R₀`, `α² = λ₀² − n²/R₀²`; **`A_r ≠ 0` kept (repair #1)** |
| The pair | mode `(+)`: `(m, n, s) = (1, +1, +1)`, phase `χ₊ = φ + θ − ωt`, amplitude `a₊`; mode `(−)`: `(1, −1, −1)`, `χ₋ = φ − θ − ωt`, amplitude `a₋`; **the curl-eigenvalue sign `s` flips WITH the winding (repair #2)**, which is what makes the two helicities genuinely opposite (`A·B = sλ₀\|A\|²`) |
| Harmonic doublet split | `cos(χ₀ − ωt) = cos χ₀ cos ωt + sin χ₀ sin ωt` → seed `a_c` from the `cos χ₀` parts, `a_s` from the `sin χ₀` parts (a rotating pair, `a_s ≠ 0`, per the M7.5 design rule) |
| J priming | `j = −0.1·a` per the `build_seed` convention (`κ = −1` basin, `m7_4_linked_vortex.py:278`) |
| Geometry | `R₀ = 4 (= L/4)` primary; note `σ/R₀ = 0.5`, exactly the "moderate, keep symbolic" regime the notes flag, so run ONE `R₀ = 6, L = 24` check; the finite-R width splitting `σ± ≈ σ(1 + 1/(2R₀²))` is below grid resolution at these R₀ (state it, do not chase it) |

### 4b. Design decision: the asymmetry is a LADDER, not one run (registered caveat)

Two facts from Phase 1 make a single √3-seeded run insufficient:

| Fact | Consequence |
| --- | --- |
| For near-Beltrami sectors `U± ≈ ±λ H±`, so the net helicity `H_A = H₊ + H₋` largely PINS `U₊ − U₋` (`U₊ − U₋ ≈ λ_eff H_A`), and our relaxation FIXES `H_A` | the spin observable is partially imposed by the constraint, not discovered by relaxation; an honest design treats **`H_A` as the dial**: run an amplitude-ratio ladder, let each rung relax, and ask WHERE the target sits and whether the closure's √3 rung is energetically special |
| At `a₊/a₋ = 1` exactly, the seed has `H_A ≈ 0`, and both Phase 1 frames kill zero-helicity states (evaporation at fixed `H_A`, M7.4; band-edge delocalization at fixed `Q_can`, M7.6); worse, the current rescale restore DISARMS when H crosses zero (the `H·H0 > 0` guard in `relax_qcan`, the M7.6 blend_standing hole) | the "unbiased control" cannot be ratio 1.0; the control question ("does relaxation FIND the asymmetry?") is answered by whether off-√3 rungs drift toward √3 under a **through-zero-safe restore** (small tooling fix, budgeted in § 4d) or show an energy minimum at √3 |

**The ladder:** `a₊/a₋ ∈ {1.2, 1.5, √3 ≈ 1.732, 2.0, 2.5}` at fixed total `Q_can` (the pair's own, from seed normalization). Per rung: relax, measure `U₊/U₋`, the asymmetry `(U₊ − U₋)/(U₊ + U₋)`, and `E`. The deliverables are the two curves `U₊/U₋` vs seeded ratio and `E` vs asymmetry.

### 4c. Measurement definitions (pinned before the run, so the numbers are unambiguous)

| Quantity | Definition |
| --- | --- |
| `U±` (per-helicity energy) | helical (Waleffe) decomposition in k-space: FFT the complex doublet `F = f_c + i f_s`, project onto the `e±(k)` helical basis (eigenvectors of `i k̂ ×`), sum the quadratic energy per sector; computed for the A sector (where the helicity guard lives), J-sector reported alongside |
| Cross-check on `U±` | (i) sector identity: `U₊ − U₋` vs `λ_eff H_A` (near-Beltrami consistency); (ii) overlap of the relaxed state with the two seeded CK modes (construction-specific reading); agreement across the three readings is itself a finding |
| The spin target, in-model | the Q15 directive `S_z = ℏ/2` with the P2 quantum `U = ℏω` becomes the **dimensionless asymmetry `(U₊ − U₋)/(U₊ + U₋) = 1/2`** (equivalently `U₊/U₋ = 3`); no unit contract needed to test it. The δ-corrected closure shifts it to `1/(2(1−δ))`, i.e. `U₊/U₋ = 3 + α/2 + 4f_bb` |
| Resolution honesty | the α/2 correction is 0.37% of the ratio; Phase 1 grid convergence is 0.15% (N 64→96): the PURE 3:1 test is well within resolution, the α-correction is at the edge: report the measured deviation with the grid-ladder error bar, do not claim the α digit unless the ladder supports it |
| Continuity battery | energy budget closure, `\|g\|`, r50, `λ_eff` alignment map, `j_z` per quantum (`jz_per_quantum`, `m7_functional.py:164`), per the M7.6 pattern |

### 4d. Execution ladder

| Step | Content |
| --- | --- |
| 0 | tooling: through-zero-safe helicity restore in `relax_qcan` (additive correction or penalty fallback when `\|H\|` is small); budgeted first, it gates the low-ratio rungs |
| 1 | seed builder + seed-level gates: measured seed `H_A` vs the analytic `s`-weighted expectation; `∇·A` pattern vs the notes' divergence identity `∇·A = −A_r λ′/λ` (qualitative: charge on the gradient shell, zero at core) |
| 2 | 48³ smoke: one rung (√3), 500 iterations, constraints hold, no blow-up |
| 3 | 64³ record: the five-rung ladder, 1500+ iterations each (~4 min/rung at the M7.5 regen rate) |
| 4 | measure per § 4c, assemble the two curves, grid-check the winner rung at 96³ |
| Outcomes | closure lands → the postulates survive 3D and the spin-½ cell gains an in-model measurement; closure fails → the failure mode localizes it (which postulate, or the thin-torus truncation); the ladder design makes EITHER outcome quantitative: even a null is "the asymmetry the functional actually selects is X" |
| Artifacts | `scripts/m7_8_helicity_pair.py` · `data/m7_8_*.json` · `plots/m7_8_*.png`, checkpoints to `research/checkpoints/m7_8_progress.md` |

## 5. Walkthrough plan (deliverable b): [`m7_phase1_walkthrough.md`](m7_phase1_walkthrough.md)

Skeleton already in place; filled during this task. Tuned to the author's register (flow and orbits, evolution-first language, the Lagrangian relegated to a derivation note). Section plan and the call question each section answers:

| § | Content | Call question it answers |
| --- | --- | --- |
| 1 | The discovery narrative: the five-step chain to the stable rotating electron (pre-filled) | "show me how it was found" |
| 2 | What is actually integrated: the evolution equations at each step, energies as field quadratures, line-by-line code map | "what's the PDE, what's the actual equation you're integrating" |
| 3 | Numerics: the integrator (velocity-Verlet / leapfrog), the drift-fix history, `O(dt²)` convergence evidence, conservation traces, why it does not explode at Zitter-like scales | his own symplectic/Taylor crash experience |
| 4 | The automated test suite: inventory + current pass report (auto-generated from the gate JSONs) | "let's make sure we have tests automated that show the PDE is behaving correctly... generate me a report" |
| 5 | "Approximately Beltrami", precisely: `λ_eff = F·(∇×F)/\|F\|²` defined, the 0.96 alignment map shown | "is that word salad?" |
| 6 | The system under the hood: human + AI + repo governance (AI_HYGIENE, method notes, script-backed claims, adversarial audits), and the honest answer to "one person + a laptop": GPU lattice + AD gradients + agent throughput + validated gates + known-answer tests at every step | the David-and-Goliath question |
| 7 | The extension results, one report: § 7.1 = the M7.8 results (from deliverable a); § 7.2 = the [M7.9](m7_9_chaosbook.md) benchmark scorecard; § 7.3 = the [M7.10](m7_10_pure_maxwell.md) pure-Maxwell results (2026-07-07: the walkthrough ships to the author once all three land) | the agreed data handoff |
| 8 | Reproduce everything: `m7_7_canonical.py` quick mode, the grid ladder, and the local-install path for when he takes it | "I do want to install OpenWave at some point" |

## 6. Folded from the call-prep sheet (so nothing is lost and that doc can retire)

| call_prep § | Where it lives now |
| --- | --- |
| § 1 goals | done at the call; outcomes in the [tracker chronology](../m7_question_tracker.md) |
| § 2 the 3:1 two-liner | § 3 here + walkthrough § 1 |
| § 3 the test spec | § 4 here |
| § 4 pipeline capabilities | walkthrough § 6 + § 8 |
| § 5 units contract table | Q15 resolved-directive; both readings versioned in the canonical spec § 4 (deliverable c) |
| § 6 question list | tracker (Q15 resolved; Q7/Q3 post-August; Q1 open; Q4 addendum) |
| § 7 already-answered + the Q11 window measurement | tracker Q10/Q11 details |
| § 8 after-the-call | the restructured [roadmap](../m7_roadmap.md) (Phase 1 extension M7.8/M7.9/[M7.10](m7_10_pure_maxwell.md) + reserved M7.11-M7.14 + Phase 2 = M7.15+) |

## 7. Cross-refs

[Roadmap](../m7_roadmap.md) · [tracker](../m7_question_tracker.md) (Q15 resolution, Q3/Q4/Q7 call addenda) · [Phase 1 report](m7_phase1_report.md) · [call-prep (archived)](m7_7_call_prep.md) · closure-notes provenance: [`theory/_CITATIONS.md`](../../theory/_CITATIONS.md) · author-convo record: `theory/author_convos/m7_phase1_convo.pdf` (local-only) · [`AI_HYGIENE.md`](../../../../../AI_HYGIENE.md) (the audit-loop contract).
