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

| Step | Content |
| --- | --- |
| Seeds | the repaired helicity-pair state per the closure notes: CK modes `(m, n, s) = (1, +1, +1)` and `(1, −1, −1)` **with `A_r ≠ 0`** (repair #1) and helicity sign tied to `±λ₀` (repair #2); LG radial profile `Ψ = (r/σ)e^{−r²/2σ²}` under the closures `λ₀σ = 2`, `w = λ₀σ²`; amplitude ratio seeded at √3 (the closure value) and ALSO at 1.0 (a no-prejudice control: does relaxation FIND the asymmetry?) |
| Relax | fixed `Q_can` (+ helicity), the frame validated in M7.3-M7.6 (`relax_qcan` lineage); grid ladder 48³ smoke → 64³ record, `L = 16`, per the Phase 1 pattern |
| Measure | per-helicity energy split `U₊/U₋` (project onto the `s = ±` curl eigensectors); the pair-asymmetry spin `(U₊ − U₋)/ω` vs ℏ/2 (the Q15 directive); the standard battery (energy budget closure, `\|g\|`, localization r50, `λ_eff` alignment, `j_z` per quantum) for continuity with M7.6 |
| Outcomes | prediction lands → the closure postulates survive 3D and the spin-½ cell gains an in-model measurement; prediction fails → the failure mode says whether a postulate or the thin-torus truncation broke; either is a result |
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
| 7 | The M7.8 results (from deliverable a) | the agreed data handoff |
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
| § 8 after-the-call | the restructured [roadmap](../m7_roadmap.md) (Phase 1 extension M7.8/M7.9 + reserved M7.10-M7.14 + Phase 2 = M7.15+) |

## 7. Cross-refs

[Roadmap](../m7_roadmap.md) · [tracker](../m7_question_tracker.md) (Q15 resolution, Q3/Q4/Q7 call addenda) · [Phase 1 report](m7_phase1_report.md) · [call-prep (archived)](m7_7_call_prep.md) · closure-notes provenance: [`theory/_CITATIONS.md`](../../theory/_CITATIONS.md) · author-convo record: `theory/author_convos/m7_phase1_convo.pdf` (local-only) · [`AI_HYGIENE.md`](../../../../../AI_HYGIENE.md) (the audit-loop contract).
