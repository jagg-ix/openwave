# M5.21.1: the electron hedgehog under the author's 2026-07-15 prescription (M5.21 phase 2)

**Status**: 🚧 PLANNED (2026-07-16, from Duda's 2026-07-15 reply: [`m5_20_convo.md § 2026-07-15`](m5_20_convo.md)); awaiting user "go". This plan REPLACES the earlier M5.21.1 framing (free-EL true-L clock on the electron): his redirect prescribes **minimization-first** (3D statics → 4D extension by energy minimization), which sidesteps the ill-posed IVP measured at [M5.20.3](m5_20_3_task_details.md). The free-EL clock question survives inside phase P2 as the orbit-class read, not as raw time integration.

**Lineage**: [M5.21](m5_21_task_details.md) (phase 1: snapshot instrument + the canonical-stack baseline: core rings ω ≈ 0.11-0.13, boost sector exactly 0.0, statics = a Q8 slide) · the M5.20 series kills that make minimization-first the honest route (M5.20.3 ill-posed IVP; M5.20.5 rigid-orbit level out) · [M5.17 phase D](m5_17_task_details.md) (the Fig. 9 ansatz transcription + conformance) · canonical [`../m5_theory_canonical.md`](../m5_theory_canonical.md) § 2 rows 4/4b.

## HIS PRESCRIPTION (2026-07-15, verbatim anchors)

| Element | His words (2026-07-15) | Measured object |
| --- | --- | --- |
| The object | "electron as hedgehog - which (in contrast to neutrino) has to be stable" | STABILITY is his own pre-registered bar: if the statics dissolves it, that is a formulation-level finding |
| The ansatz | "biaxial hedgehog ansatz for Gx, Gy, Gz rotation generators (from Fig. 9 in arXiv:2108.07896)" | `M = O·D·Oᵀ`, spatial `D = diag(1, δ, 0)`, `O = exp(θG_z)·exp(φG_y)·exp(ψG_x)` (M5.17 phase D transcription, conformance-checked) |
| Core structure | "vortex in z axis - requires regularization with two equal eigenvalues, and in the center all three spatial eigenvalues have to be equal" | 2-equal along the z-vortex line, 3-equal at the center (the M5.21 measured seed-adjacent core a = 0.4338 vs (1+δ)/3 = 0.4333 is the transient of exactly this) |
| Mass distribution | "its 511keV mass mainly in the center, vortex should be extremely light" (pairing opposite spins / Cooper pairs) | E(r) concentration (r50/r90) + the vortex-line energy per length |
| The chain | "minimizing energy in 3D ... getting static solution, then extending to 4D - where energy minimization should lead to angular momentum + gravitational mass" | P1 → P2 below |
| The twist limit | "For perpendicular low energy twists (as quantum phase) you should get Klein-Gordon-like equation" | P3 below (the canonical already carries the KG-is-geometric reproduction on the old spec; re-read on the new one) |

## TASK PLANNING (2026-07-16 draft; finalize at go)

### The M5.20-series re-capture (series rule, folded at PLAN)

| Lesson (M5.20.3-5, all audited) | How it binds this task |
| --- | --- |
| The free-EL IVP of the quartic L is ILL-POSED on non-trivial backgrounds (roundoff-seeded boost-sector exponential, E → −∞ in finite time) | NO raw time integration anywhere in this task; dynamics enters only as minimization, orbit classes, or spectra. The M5.21 baseline's boost-sector-exactly-0.0 does NOT license an IVP: the loop's blowup grew from rounding noise |
| The rigid conjugation-orbit level is measured OUT on the loop (directional block: static force 99.9997% time-row) | The a2x alignment diagnostic is on disk and cheap: run it on the HEDGEHOG background before believing any orbit-class claim (the hedgehog's static-force sector split is an open measurement, not assumed equal to the loop's) |
| The φ-averaged kinetic (band-limit gated, nphi = 5 exact) + the s2/qc EL library (9 gates ≤ 8e-16) | Reused as-is wherever 4D kinetic reads appear; band limits GATED, never assumed (the nphi lesson) |
| q never unwinds through blowups; winding instruments validated | The charge-1 hedgehog winding read carries over from M5.21 |
| Film standard | Every state-evolving figure via `m5_film.film_strip`; **BOTH templates, `basic` AND `thermal`** ([`../m5_visualization.md`](../m5_visualization.md)), first row t = 0 |

### Steps

| Step | Content | Kill / survive (pre-registered) |
| --- | --- | --- |
| P0 | **The `(-g)^p` spec correction, both signs (his correction 1)**: potential targets from the η-spectrum of BOTH branch representatives, `ηM = diag(+g,1,δ,0)` (= the current verified build) and `ηM = diag(−g,1,δ,0)` (the corrected reading); gates: target-pinning exactness per sign; loop + hedgehog statics regression per sign (which sign preserves the M5.16/M5.18 anchors: r_half, core spectrum, the a = 0.85·δ/2 read?) | both signs measured; a sign that kills the known-good statics anchors is flagged, not silently adopted |
| P1 | **3D hedgehog statics (his chain, step 1)**: energy-minimize the Fig. 9 biaxial hedgehog on the audited axisym stack (+ 3D spot-check); measure his three structural claims: 2-equal regularization along the z-vortex, 3-equal center, mass-in-center (r50/r90 + vortex-line energy per length vs core energy). Reconcile with the M5.21 Q8-slide finding: does HIS regularization language pin the slide, or does the slide survive (= the stability bar fires) | a stable (or slide-characterized) static solution with the core structure measured either way; "has to be stable" is HIS bar: a dissolve is a headline, not a failure |
| P2 | **4D extension by minimization (his chain, step 2)**: add the g time row (sign per P0), minimize within the rotation-sector orbit class (boost sector quarantined per the M5.21 measurement + the M5.20.2 census; the a2x alignment read on the hedgehog background FIRST, minutes, decides whether rigid conjugation even couples here); read the emergent ANGULAR MOMENTUM + the mass/energy split (his "energy minimization should lead to angular momentum + gravitational mass") | the alignment read is decisive either way; a converged 4D minimizer with J ≠ 0 = his prediction landing; J = 0 or no coupling = the measured characterization goes back sharpened |
| P3 | **The KG twist limit (his chain, step 3)**: perpendicular low-energy twists on the P1/P2 background → dispersion read vs Klein-Gordon (the canonical's KG-is-geometric row re-checked on the new spec) | dispersion measured; KG-like = his Fig. 9 closed on the new stack |
| P4 | **The (g, δ) scaling ladder (his correction 2)**: physical values (δ ~ 1e-10, g ~ 1e10, signs open; paper anchors δ² ~ ħc, g⁴ ~ 1e38) are unreachable directly ("need practical approximations", his words): chart the toy-regime scaling laws of the P1-P3 observables (core spectrum a(δ), r50/r90, J, ω ladder) over a feasible (g, δ) grid so every claim carries its regime qualifier + extrapolation direction | monotone/fitted scaling per observable, or the honest "does not extrapolate" flag |
| P5 | Observables + films: BOTH templates (basic + thermal) on every evolving/relaxing sequence; the mass-in-center + light-vortex panel; optional diagnostic: the positive-vs-negative term balance along any energy descent (his message-2 prevention claim, read on our data) | rendered + embedded in the method note |

NOT in scope: the vortex-loop/neutrino side (parked: [M5.20.6](m5_20_6_task_details.md) archived reserve, [M5.20.7](m5_20_7_task_details.md) parked after the M5.21 series); any IVP time integration; the 2-particle runs (M5.21.2).

### Blindspot pass (finalize at go)

| # | Unknown unknown surfaced | Fold |
| --- | --- | --- |
| 1 | "Energy minimization in 4D" is not well-defined under an indefinite H (M5.18: boost×rotation textures unbounded below) | P2 minimizes within the rotation-sector orbit class with the boost sector quarantined; if his intent differs, that is an author-gated question, flagged not guessed |
| 2 | The `(-g)^p` flip could silently move the vacuum branch structure (M5.18: 4 disjoint orbit branches) | P0 re-runs the branch enumeration per sign before any physics |
| 3 | The hedgehog's static-force sector split may differ completely from the loop's 99.9997%-time-row | measure it (a2x on the hedgehog) before importing ANY loop-side conclusion |
| 4 | The Q8 slide (M5.21 statics) vs his "has to be stable": possible contradiction at the toy δ | treat as P1's central measurement; a slide that VANISHES along the P4 δ-ladder is a resolution, not a contradiction |
| 5 | Scaling sweeps multiply cost | budget from the measured M5.16/M5.21 statics costs; grid pre-registered at go, no silent extension |
| 6 | Two spec knobs moving at once (sign of g, δ-ladder) confounds attribution | one-knob-at-a-time protocol: P0 fixes the sign story on the anchors BEFORE P4 moves δ |

### Definition of done

| ✅ when | Bar |
| --- | --- |
| P0 verdict | both-sign targets gated + statics regression table (which sign keeps the anchors) |
| P1 verdict | the 3D static solution characterized against his three structural claims (2-equal vortex, 3-equal center, mass-in-center) + the stability read |
| P2 verdict | the hedgehog alignment read + a converged 4D minimizer (J, mass split) OR the measured characterization of what blocks |
| Records | method note `../findings/m5_21_1_method_note.md` (equations first, equation-to-code map, both-template films embedded); independent adversarial audit (cardinal rule); tracker + roadmap + checkpoint routing; > 1 MB raw data deleted with regen docs |

### Research-body destinations

| Artifact | Destination |
| --- | --- |
| Scripts | `../scripts/m5_21_1_a_spec.py` (P0) · `m5_21_1_b_statics.py` (P1) · `m5_21_1_c_4d.py` (P2/P3) · `m5_21_1_d_scaling.py` (P4) · `m5_21_1_plots.py` |
| Data / plots | `../data/m5_21_1_*.json` (+ npz ≤ 1 MB) · `../plots/m5_21_1_*.png` (film standard, both templates) |
| Findings | `../findings/m5_21_1_method_note.md` |
| Records | this file (FINDINGS + TASK REVIEW) · [`../m5_question_tracker.md`](../m5_question_tracker.md) (Q24 detail carries the redirect) · `../checkpoints/m5_21_1_progress.md` (opens at go) |

### Gating

Roadmap `Gated By`: **Duda's 2026-07-15 electron redirect (landed: this plan IS the fold) + user "go"**. The M5.20-series re-capture is folded above (series rule satisfied at PLAN); re-verify freshness at go if other tasks run in between.

### Model + effort

Fable 5 high for P0 (branch/vacuum re-enumeration) and P2 (the 4D minimization design); default for the mechanical gates + sweeps; independent agent for the audit (cardinal rule).
