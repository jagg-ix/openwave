# HydroBoros (M7): MODELS.md column PREVIEW (staged, not yet entered)

> **Status (2026-07-04, the M7.7 milestone):** the 21-cell HydroBoros column is DRAFTED here and deliberately **not yet entered in the repo-root [`MODELS.md`](../../../../MODELS.md)**: the M7 research program is still in flight and the model is not yet ready for the cross-model benchmark. The column lands via the new-model governance flow (issue + script-backed PR, MODELS.md § Contributing) when the program calls it ready (M7.21). Icons follow the honest-status legend; every cell is script-backed. Canonical spec: [`m7_theory_canonical.md`](m7_theory_canonical.md); one-script reproduction: [`scripts/m7_7_canonical.py`](scripts/m7_7_canonical.py) (all gates first-try, engine-vs-reference 1.4e-14).

## PARTICLES (full spectrum)

| Criteria | HydroBoros (M7) |
| --- | --- |
| Charge quantization | ⚠️ [partially validated]<br>Helicity/linking gates existence (both zero-helicity parent seeds evaporate; measured); the RMS divergence charge is persistent and independent of linking at this level; a net Gauss monopole exists via the fixed-`j0` reservoir (99.1% flux closure) but its value is set by the source: quantization not yet emergent<br>[`m7_4_linked_vortex.py`](scripts/m7_4_linked_vortex.py), [`m7_6_observables.py`](scripts/m7_6_observables.py) |
| Electron rest energy (mass) | ⚠️ [partially validated]<br>The M6 charged ledger H/Q = 1.6890 reproduced in full 3D to 4.7e-5, and measured to be WINDOW-defined (no decaying far-field channel at the canonical point, so it is not used as a mass anchor); the stable rotating electron carries E = 6.3246 program units (grid-convergent 0.15%), absolute anchor pending the units contract<br>[`m7_3_ouroboros_3d.py`](scripts/m7_3_ouroboros_3d.py), [`m7_theory_canonical.md`](m7_theory_canonical.md) |
| de Broglie clock (Zitterbewegung) | ⚠️ [partially validated]<br>Fixed-ω harmonic frame by construction, PLUS two measured clock structures: the ω-Q_can Legendre conjugacy dE*/dω = Q_can (1-2% at every scan point) and the existence threshold ω* = 0.786 (solitons exist only above the vacuum's tachyonic band: the clock IS the stabilizer)<br>[`m7_5_clock_stability.py`](scripts/m7_5_clock_stability.py) |
| Particle stability (Derrick escape) | ⚠️ [partially validated]<br>Harmonic-frame soliton fully verified: helicity anti-collapse + Ouroboros confinement, no 4th-order term needed, constrained-Derrick interior minimum measured, grid-convergent; honest caveat: the truncation's real-time vacuum is unconditionally tachyonic (det M(0) = −1, measured growth rate 0.785 vs 0.786), so real-time persistence fails in ~2 periods (the open theory question)<br>[`m7_4_linked_vortex.py`](scripts/m7_4_linked_vortex.py), [`m7_5_clock_stability.py`](scripts/m7_5_clock_stability.py) |
| Magnetic moment μ + spin J | ⚠️ [partially validated]<br>The rotating electron is a clean j_z = 1 per-quantum wave (0.9939/0.9934, A/J sectors); Poynting L_z = 13.10 with the energy budget closing exactly; μ measured de-phased (36.5 p.u.) but the μ_B comparison is blocked on the charge unit (scalar sector); ℏ/2-vs-ℏ = the units-contract decision table<br>[`m7_6_observables.py`](scripts/m7_6_observables.py), [`m7_theory_canonical.md`](m7_theory_canonical.md) |
| Spin-½ statistics (720° double cover) | 🚧 [not yet tested]<br>Not addressed; the measured per-quantum j_z = 1 (photon-loop reading) leaves the double-cover question open either way<br>[`m7_theory_canonical.md`](m7_theory_canonical.md) |
| Antimatter + annihilation | 🚧 [not yet tested]<br>M7.18 target (soliton + anti-soliton, charge ledger); the real-time route is blocked by the vacuum tachyon (Q14) until the full model's cure is known<br>[`m7_question_tracker.md`](m7_question_tracker.md) |
| Neutrinos | 🚧 [not yet tested]<br>M7.19 target: the lighter neutral loop of the lepton family<br>(none yet) |
| Lepton mass spectrum (μ, τ) | 🚧 [not yet tested]<br>M7.19 target; prerequisite discovered: fixing only global helicity permits reconnection into one Taylor family (E = 0.802\|H_A\|), so distinct knot sectors need topology-preserving constraints<br>[`m7_4_charged_soliton.md`](tasks/m7_4_charged_soliton.md) |
| Dark matter candidate | 🚧 [not yet tested]<br>M7.20 target: the neutral helicity-only knot, inheriting M6's chaoiton<br>(none yet) |
| Quarks | 🚧 [not yet tested]<br>M7.22 (composites)<br>(none yet) |
| Baryons (p, n) | 🚧 [not yet tested]<br>M7.22 (composites)<br>(none yet) |
| Mesons (π, K) | 🚧 [not yet tested]<br>M7.22 (composites)<br>(none yet) |

## FORCES

| Criteria | HydroBoros (M7) |
| --- | --- |
| Electric force (Coulomb 1/r) | ⚠️ [partially validated]<br>Fixed-reservoir monopole: Gauss flux closes at 99.1%, single-charge far field slope −2.14 (vs −2), and the two-charge splitting reference-matches Poisson-in-the-same-box at a constant 1.17 ± 0.02 dressing (the measured coupling renormalization); bonus discovery: neutral pairs interact via an oscillatory RKKY-style exchange (period π/k). Caveat: the source is external; the self-consistent charge pends the scalar-sector cure<br>[`m7_6_observables.py`](scripts/m7_6_observables.py) |
| Magnetic force | 🚧 [not yet tested]<br>M7.15 target (the clock-carried per-defect magnetic structure)<br>(none yet) |
| Strong force / confinement | 🚧 [not yet tested]<br>M7.17 target (4th-order short-range roll-off + linking tension)<br>(none yet) |
| Weak force | 🚧 [not yet tested]<br>M7.17 target (topology-reconnection channel; the M7.4 reconnection observation is the seed)<br>[`m7_4_charged_soliton.md`](tasks/m7_4_charged_soliton.md) |
| Gravity | 🚧 [not yet tested]<br>M7.16 target; honestly hard: the parent framework stops before gravity<br>(none yet) |

## WAVES + QUANTUM EMERGENCE

| Criteria | HydroBoros (M7) |
| --- | --- |
| EM waves (Maxwell) | ⚠️ [partially validated]<br>A_μ is the Maxwell four-potential by construction, and the coupled vacuum's band structure is MEASURED (growth rate 0.785 vs analytic 0.786): a propagating KG branch plus an unconditional long-wavelength tachyonic band (det M(0) = −1): the truncation's vacuum is not pure Maxwell, the honest open theory question (Q14)<br>[`m7_5_clock_stability.py`](scripts/m7_5_clock_stability.py) |
| Quantum wave equation (Klein-Gordon) | ⚠️ [partially validated]<br>Both transverse fluctuation branches are exact KG dispersions ω² = k² + m_eff² with m_eff² = (1+√5)/2 (upper) and −(√5−1)/2 (the tachyonic band), lattice-anchored via the measured rate; the collective-coordinate (phase/twist) KG remains open<br>[`m7_6_observables.md`](tasks/m7_6_observables.md) |
| Orbital quantization (atomic structure) | 🚧 [not yet tested]<br>M7.22 target<br>(none yet) |

## Summary count (as drafted)

| Status | HydroBoros (M7) |
| --- | --- |
| ✅ validated in-platform | 0 |
| ⚠️ partial / with caveats | 8 |
| ❌ honest negative | 0 |
| 🔶 in progress | 0 |
| 🚧 planned / not yet | 13 |
| **Total criteria** | **21** |

Entering the benchmark today, the column would rank fourth (✅+⚠️ = 8, tied with M4). No icon inflation: each ⚠️ carries its named caveat (the windowed ledger Q11, the real-time vacuum tachyon Q14, the fixed-reservoir monopole, the charge-unit-blocked μ, the open units contract).

---

Cross-refs: milestone task [`tasks/m7_7_consolidation.md`](tasks/m7_7_consolidation.md) · spec [`m7_theory_canonical.md`](m7_theory_canonical.md) · roadmap [`m7_roadmap.md`](m7_roadmap.md) (Phase D / M7.21 = completing + governing the column) · open questions [`m7_question_tracker.md`](m7_question_tracker.md) · the live matrix [`MODELS.md`](../../../../MODELS.md).
