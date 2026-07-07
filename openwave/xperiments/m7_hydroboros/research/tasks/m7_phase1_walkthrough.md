# M7 / HydroBoros: the Phase 1 walkthrough (under the hood)

> A reader-first companion to the [Phase 1 report](m7_phase1_report.md), written for a physicist who wants to see **what was actually done** before trusting it: how the stable electron candidate was found, which equations are integrated, how the numerics are kept honest, and how a one-engineer-plus-AI team runs this at all. Everything links to runnable code and raw data; nothing here rests on prose. Produced as deliverable (b) of [M7.8](m7_8_helicity_pair.md) and completed across the Phase 1 extension: **§ 7 bundles the results of all three extension tasks (M7.8 helicity pair, M7.9 ChaosBook benchmark, M7.10 pure-Maxwell no-Lagrangian test) into the one report that goes to the author**; sections marked 🚧 fill as those tasks land.

## 1. How the stable dynamical orbit was found (the discovery chain)

Both parent models are time-periodic, so the electron is sought as a **periodic orbit of the field equations**: `A, J ~ (cos ωt, sin ωt)`. The search frame, forced by the M7.3 pre-gate rather than chosen: **extremize the period-averaged energy `E_ω` at fixed canonical charge `Q_can`** (the wave action), with the rotation rate ω emerging as the Lagrange multiplier. That is textbook orbit-hunting translated to fields: find the orbit by minimizing energy at fixed action. The Legendre relation `dE*/dω = Q_can` was later verified on the lattice to 1-2%, confirming ω and `Q_can` are true conjugates.

| Step | What happened | Where |
| --- | --- | --- |
| 1. The parents' electron is NOT stable in 3D | Embedding M6's validated 1D electron into full 3D reproduced its ledger (`H/Q` to 4.7e-5) but revealed a **constrained saddle**: fixed-`Q_can` descent departs immediately and ends in focusing collapse. The M6 ansatz carries zero helicity, so nothing guards it against concentration | [`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md) |
| 2. Helicity makes it stable | A 6-seed × 2-convention relaxation matrix at fixed `Q_can` **+ fixed helicity `H_A = ∫A·B`**: all three helicity-carrying seeds relax to stable, finite-size, approximately-Beltrami solitons (§ 5 defines "approximately" as a number); **both zero-helicity seeds evaporate**, the control experiment inside the matrix. The balance: helicity blocks collapse (Arnold's bound `E ≥ λ₁\|H\|`), the confinement coupling blocks expansion, and the dilation probe measures a genuine interior energy minimum on every survivor | [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md) · ![winner](../plots/m7_4_winner_sections.png) |
| 3. It is a real orbit in real time, and the clock is why it lives | The relaxed state handed to a real-time leapfrog: `⟨E_real⟩ = E_ω` to 1.85e-14, so the harmonic solution IS a periodic orbit of the actual evolution equations. Sharp discovery: the truncation's vacuum is tachyonic at long wavelength, and the orbit survives **only because it rotates above the unstable band**: solitons exist iff `ω ≥ ω* = 0.786` (measured: 0.70/0.75 run away, 0.79+ are clean). The de Broglie clock is the stabilizer. Also caught: the step-2 winner was a **standing** wave, not yet a rotation | [`m7_5_clock_stability.md`](m7_5_clock_stability.md) · ![threshold](../plots/m7_5_tachyon_scan.png) |
| 4. The rotating electron | Same constrained frame, rotating `m = 1` seeds (`a_c ∝ cos φ, a_s ∝ sin φ`): relaxes to the candidate of record: `E = 6.3246`, gradient 1.6e-7, energy budget closing exactly, and a clean **`j_z = 1` per-quantum rotating wave** (0.994 in both field sectors): one unit of angular momentum per quantum of wave action, measured, never imposed | [`m7_6_observables.md`](m7_6_observables.md) · ![observables](../plots/m7_6_observables.png) |
| 5. One-script reproduction | The whole chain re-earns itself from one command at two grid resolutions, engine cross-validated against an independent reference implementation to 1.4e-14 | [`m7_7_canonical.py`](../scripts/m7_7_canonical.py) · [`m7_7_consolidation.md`](m7_7_consolidation.md) |

In one sentence: **fix the action and the knottedness, let the field fall to its energy minimum, and what survives is a knotted wave rotating above the vacuum's instability band; the unknotted version dies, the knotted one cannot collapse (helicity), cannot expand (confinement), and cannot dissolve (it out-rotates the instability).**

How "stable" is evidenced, since that word carries the weight:

| Stability test | Result |
| --- | --- |
| Critical point | constrained gradient driven to `\|g\| = 1.6e-7` (an extremum, not a stalled descent) |
| Against scaling (Derrick) | measured interior minimum of `E(scale)` at fixed constraints on every survivor; the zero-helicity controls have none and evaporate |
| Against real-time perturbation | 12 full periods of leapfrog evolution, `O(dt²)` conservation, `⟨E_real⟩ = E_ω` to 1.85e-14; drift falls ×4 when dt halves |
| Against the vacuum | the orbit sits above the measured existence threshold `ω* = 0.786`; forced below it, the same construction runs away, as the dispersion predicts |

Honest boundary: what exists is a stable rotating knotted soliton with unit angular momentum per quantum **in model units**. The absolute readings (mass in `m_ec²`, spin in ℏ) hang on the units contract, now resolved as a directive (target `S_z = ℏ/2`, [tracker Q15](../m7_question_tracker.md#q15-detail)), which the M7.8 helicity-pair measurement addresses.

## 2. What is actually integrated

Two frames, one theory. Everything below is stated as **evolution equations and field quadratures**; the variational origin is a one-line derivation note at the end, never load-bearing.

**The real-time evolution** (what the leapfrog steps; temporal gauge, pure-vector sector):

```text
d²A/dt² = −∇×∇×A − J
d²J/dt² = −∇×∇×J − A − 2(c1 + 2c2|J|²) J        c1 = +½, c2 = +¼ (canonical)
```

Two coupled wave equations: A is a massless field, J a self-interacting one, and the linear cross-terms (`−J`, `−A`) tie them. The conserved energy is the direct quadrature `E = ∫ [½|Ȧ|² + ½|J̇|² + ½|∇×A|² + ½|∇×J|² + A·J + f(|J|²)]`.

**The harmonic frame** (where the electron is found): both parent models are time-periodic, so the electron is sought as a **periodic orbit**: `A = a_c(x)cos ωt + a_s(x)sin ωt`, same for J. On that ansatz the period-averaged energy is an explicit quadrature of the four spatial fields (`E_ω`), and the orbit is the extremum of `E_ω` at fixed wave action `Q_can` (ω = the multiplier) and fixed helicity `H_A`. The two frames are tied by a measured identity, not by trust: `⟨E_real(t)⟩ over one period = E_ω` to **1.85e-14** on the state of record.

The quadrature-to-code map (every term one click away; the physics module is ~200 lines of plain numpy):

| Quantity | Formula (in words) | Code |
| --- | --- | --- |
| `E_ω` density | quadratic (E and B of both sectors) − coupling `⟨A·J⟩` + exact quartic average | [`m7_functional.py:98-127`](../scripts/m7_functional.py) |
| `Q_can` | `(ω/2)∫(\|a_c\|² + \|a_s\|² + \|j_c\|² + \|j_s\|²)` | [`m7_functional.py:137-139`](../scripts/m7_functional.py) |
| `H_A` | `½∫(a_c·∇×a_c + a_s·∇×a_s)` | [`m7_functional.py:142-144`](../scripts/m7_functional.py) |
| momentum / spin | `⟨E×B⟩` per sector; `L = ∫x×⟨E×B⟩` | [`m7_functional.py:150-161`](../scripts/m7_functional.py) |
| `j_z` per quantum | `⟨F\|−i∂_φ + S_z\|F⟩/⟨F\|F⟩` on `F = f_c + i f_s` | [`m7_functional.py:164-179`](../scripts/m7_functional.py) |
| charge (RMS Gauss reading) | `ρ = ∇·E_A`, RMS over the window | [`m7_functional.py:182-192`](../scripts/m7_functional.py) |
| real-time forces | the two wave equations above, verbatim | [`m7_5_clock_stability.py:106-146`](../scripts/m7_5_clock_stability.py) |
| helicity split `U±` | Waleffe helical decomposition, discrete-curl-exact | [`m7_8_helicity_pair.py`](../scripts/m7_8_helicity_pair.py) `helical_split` |

Derivation note (for completeness only): both frames descend from one Lagrangian density (`−¼F² − ¼G² + m_J²A·J − f(J·J)`, the M6 inheritance); the canonical spec [`m7_theory_canonical.md`](../m7_theory_canonical.md) carries it with all conventions pinned.

## 3. The numerics, and why they do not explode

| Item | What is actually done | Evidence |
| --- | --- | --- |
| Integrator | velocity-Verlet leapfrog (kick-drift-kick), cached accelerations, `dt = 0.2h` | drift is `O(dt²)`: 0.59 → 0.148 when dt halves (ratio 4.0, the textbook signature) ([`m7_5_clock_stability.md § 1`](m7_5_clock_stability.md)) |
| Lattice | uniform cubic, central differences (the discrete curl is self-adjoint, so the discrete force is the EXACT gradient of the discrete energy), 3-cell frozen vacuum shell | the frame-consistency identity `⟨E_real⟩ = E_ω` to 1.85e-14 is only possible because the discretizations match term-for-term |
| Grid ladder | 48³ smoke → 64³ record → 96³ check, `L = 16` (`h = 0.25` at 64³) | `E` grid-converges to 0.15% (64³ → 96³, M7.4) |
| Gradient | Taichi reverse-mode AD, validated against numpy finite differences BEFORE any physics run | agreement ~1e-12 (M7.1); engine vs independent numpy reference on final states: 1.4e-14 (M7.7) |
| Relaxation | FIRE descent with Gram-Schmidt tangent projection on both constraint gradients + exact interleaved constraint restores | constraints held to 5+ digits through every run; converged states reach `‖∇E‖ ~ 1e-7` |
| Why no explosion at Zitter-like scales | the electron search does NOT time-step through fast oscillations: the clock is carried analytically inside the harmonic ansatz, so the stiff timescale is integrated exactly, by construction | real-time runs are short-window validations, not the discovery engine |
| The honest instability | released real-time evolution IS destroyed in ~2 periods, and the cause is physics, not numerics: the truncated theory's vacuum is tachyonic at long wavelength (measured growth rate 0.785 vs analytic 0.786, amplitude-independent) | the integrator's `O(dt²)` behavior in the same runs proves the destruction is not integrator failure ([`m7_5_clock_stability.md § 2`](m7_5_clock_stability.md)); the harmonic orbit survives because `ω = 1 > ω* = 0.786` |

## 4. The automated test suite, reported

Every task is gated against a known answer before its results count. The one-command reproduction re-runs the core suite: `python research/scripts/m7_7_canonical.py` (quick, N = 48, ~10 min CPU; `--full` for N = 64): it prints the gate table and **ALL GATES PASS / FAILED**. The full inventory, known-answer tests first:

| Gate (known answer) | Measured | Where |
| --- | --- | --- |
| Woltjer-Taylor relaxation → constant-λ eigenfield, `λ → 2π/L`, `E → λH` | to grid accuracy | M7.1 ([`m7_1_infra.md`](m7_1_infra.md)) |
| AD gradient vs numpy finite differences | ~1e-12 | M7.1 |
| `E_ω` gauge invariance at `m_J = 0` | machine zero | M7.1 (gate G5) |
| Fleury torus closed-form quadratures (energy, charge, μ, spin) | `O(h^2.5)`, 1.4e-4; printed solution reconstructed digit-for-digit | M7.2 ([`m7_2_fleury_torus.md`](m7_2_fleury_torus.md)) |
| M6 verbatim-ODE pre-gate (3D functional restricted to the 1D ansatz = the M6 equation, term by term) | exact | M7.3 ([`m7_3_ouroboros_3d.md`](m7_3_ouroboros_3d.md)) |
| M6 charged ledger `H/Q` in full 3D | 1.6890 to 4.7e-5 | M7.3 |
| Soliton convergence + stability | `‖∇E‖ ~ 1e-7`; dilation-probe interior minimum on every survivor; grid 0.15% | M7.4 ([`m7_4_charged_soliton.md`](m7_4_charged_soliton.md)) |
| Frame-consistency identity `⟨E_real⟩ = E_ω` | 1.85e-14 | M7.5 ([`m7_5_clock_stability.md`](m7_5_clock_stability.md)) |
| Integrator drift order | `O(dt²)` (ratio 4.0 at half dt) | M7.5 |
| Vacuum growth rate vs the analytic dispersion | 0.7850 vs 0.7862 (0.15%) | M7.5 |
| Existence threshold `ω*` | bracketed 0.75-0.79 vs predicted 0.786 | M7.5 |
| Legendre conjugacy `dE*/dω = Q_can` | ~1-2% at every scan point | M7.5 |
| Gauss's law (fixed-reservoir Coulomb) | flux = 99.1% of source; far field slope −2.14 vs −2 | M7.6 ([`m7_6_observables.md`](m7_6_observables.md)) |
| Two-charge interaction vs Poisson-in-the-same-box reference | constant ratio 1.17 ± 0.02 across d (the raw `d^−2.1` is box images, reference-matched) | M7.6 |
| Spin quantum `j_z` per quantum | 0.9939 / 0.9934 (A / J) | M7.6 |
| Engine vs independent reference implementation | 1.4e-14 | M7.7 ([`m7_7_consolidation.md`](m7_7_consolidation.md)) |
| M7.8 helical-split completeness (Parseval, incl. the longitudinal bucket) | 1.5e-16 | M7.8 ([`m7_8_helicity_pair.md`](m7_8_helicity_pair.md)) |
| M7.8 projector calibration (single `s = ±1` mode lands in its sector) | 93.5% (the 6.5% = toroidal-curvature mixing at `σ/R = 0.5`, a seed property) | M7.8 |

## 5. "Approximately Beltrami", precisely

The phrase is a measured number, not word salad. Define the local alignment eigenvalue `λ_eff(x) = F·(∇×F)/\|F\|²` and the global alignment `align = ⟨B·∇×B⟩/(‖B‖‖∇×B‖)` on `B = ∇×a_c`. Measured on every surviving Phase 1 state: **`\|align\| = 0.96`**, with `λ_eff` near-constant (≈ −1, sign following `H_A`) across the core ([`m7_4_charged_soliton.md § 2-4`](m7_4_charged_soliton.md), sections plot [`m7_4_winner_sections.png`](../plots/m7_4_winner_sections.png)). The 4% deviation is not error: it is where the physics lives (the confinement dressing and the charge-carrying divergence). And it is FORCED: Nadirashvili's theorem says no finite-energy exact Beltrami field exists in ℝ³ at all, so any localized state can only ever be approximately Beltrami; 0.96 with the deviation carrying the structure is exactly what an honest realization looks like.

## 6. The system under the hood: one engineer, one laptop, and why that works

The stated blocker ("how could a single-person team on a laptop run extensive complex simulations") deserves a mechanical answer, not reassurance:

| Leverage | What it does |
| --- | --- |
| Taichi lattice engine (f64, CPU/GPU) | a 64³ × 16-component relaxation runs in minutes on a MacBook; the M5-proven engine was inherited, not rebuilt |
| Reverse-mode AutoDiff | exact gradients of the full functional with no hand-derived adjoints to get wrong; validated against finite differences before first use |
| AI agent throughput | the human directs; agents write scripts, run sweeps, and draft docs at high parallelism. **What the agent output is NOT**: a result. Model output is a draft or hypothesis until something that is not a language model verifies it (a runnable script, a hand-checked derivation, a measurement): the standing contract in [`AI_HYGIENE.md`](../../../../../AI_HYGIENE.md) |
| Known-answer gates | every task is anchored to something already known (a theorem, a closed form, a parent model's number) before its new claims count; § 4 is the inventory |
| Adversarial audits | substantive claims get an independent refutation pass (own script, own method) before they are trusted or sent; the audit is recorded in the deliverable |
| Method notes | anything author-facing ships equations-first with an equation-to-code map ([`dev_docs/METHOD_NOTE.md`](../../../../../dev_docs/METHOD_NOTE.md)), so verification happens by reading, not by trusting |

The honest summary: the system's credibility rests on runnable code plus known answers plus audits, not on team size. Every claim in this document traces to a script you can run and a number you can check.

## 7. The extension results: M7.8 + M7.9 + M7.10, one report 🚧

Three subsections, one per task, filled as each lands (run order M7.8 → M7.9 → M7.10):

| § | Task | What lands here |
| --- | --- | --- |
| 7.1 | [M7.8](m7_8_helicity_pair.md) helicity pair ✅ | below |
| 7.2 | [M7.9](m7_9_chaosbook.md) ChaosBook benchmark ✅ | below |
| 7.3 | [M7.10](m7_10_pure_maxwell.md) pure-Maxwell no-Lagrangian test 🚧 | Theorem 2 verified as a known-answer gate (Trkalian cavity mode persists); the honest boundary as a measurement (free-space evaporation, electron destruction time with the coupling off); the coupling ladder and the tachyon-attribution result |

### 7.1 The M7.8 helicity-pair results (run of record: 2026-07-07, N = 64)

The repaired two-mode ansatz from the closure notes (CK/LG modes `(1, ±1, ±1)`, `A_r ≠ 0`, LG profile under `λ₀σ = 2, w = λ₀σ²`) was seeded at five amplitude ratios `a₊/a₋ ∈ {1.2 … 2.5}` bracketing the closure value √3, each relaxed at fixed `(Q_can, H_A)`:

![m7_8_ladder](../plots/m7_8_ladder.png)

| Measured | Result |
| --- | --- |
| Is the `U₊/U₋ = 3` pair a constrained minimum? | **No, at any seeded asymmetry**: relaxation expels the minus mode at every rung (relaxed `U₊/U₋` = 104 → 1077, asymmetry 0.981 → 0.998); an adversarial re-insertion test confirms the pure-plus state is a directional minimum (`dE ∝ +ε²`) |
| Where does the pair go? | into the **known electron family**: `E/\|H_A\|` → 0.808 (the Phase 1 family law 0.802), alignment → 0.95, `j_z` → 0.99 per quantum: the single-helicity rotating state of § 1 |
| The spin observable | the pair-asymmetry `(U₊ − U₋)/(U₊ + U₋)` reads **≈ 1, not 1/2**: one quantum of angular momentum per quantum of action, matching the Phase 1 per-quantum measurement. The ℏ/2 reading survives via the frequency mapping (bilinears at 2ω, the Zitter route), not via pair asymmetry |
| What stands vs what broke | the closure ARITHMETIC stands (re-derived at receipt); the LG profile relaxes cleanly; what breaks is the **two-mode stationarity postulate** in this frame. Not excluded (the open question the data poses back): an ensemble with the two helicities constrained separately, the charge/scalar sector active, or a resonant rather than minimal pair |
| Full record | [`m7_8_helicity_pair.md § FINDINGS`](m7_8_helicity_pair.md) (gates, the five-rung table, the low-`H_A` longitudinal-reservoir caveat, the audit) |

### 7.2 The M7.9 ChaosBook benchmark (run of record: 2026-07-07)

The self-test asked for at the Phase-1-review call ("your AI should kill it in 10 minutes, but I want to see that"): canonical ChaosBook exercises implemented headless and compared against the published solutions, with the hygiene rule that every published value is transcribed from the chapter PDFs with a page citation, never from an AI model's memory. Full scorecard + equations + audit: [`m7_9_benchmark_report.md`](m7_9_benchmark_report.md).

| Measured | Result |
| --- | --- |
| Pre-book analytic gates | 4/4 green before any book content was consulted (Lorenz eigenvalues vs a sympy-derived characteristic cubic to 1.2e-14; Hénon fixed points at machine precision; Poincaré return time exact to 5e-13) |
| Rössler equilibria + exponents ((2.29), (4.36)) | reproduced to the printed precision (the book truncates its decimals; agreement at 1 ULP of print) |
| The analytic Floquet cycle (exercise 5.1) | `find_cycle` + `floquet` recover `T = 2π` and multipliers `{1, e^{−4π}}` to 1.3e-15 |
| **The full exercise 16.9 cycle table** | **14/14 Rössler periodic orbits to topological length 7 found and reproduced** (close-return seeding → multiple shooting → Floquet): worst section-point deviation 2.0e-6, worst `Λ_e` relative deviation 1.3e-6 against the published values |
| Counting (tables 18.2/18.3) | exact integer match, `N = 2, 3, 4` alphabets to `n = 10` |
| Adversarial audit | CONFIRMED by a machinery-independent route (LSODA + finite-difference Jacobians + brute-force necklace enumeration; no shared code with the pipeline) |
| The toolkit the Maxwell track inherits | [`m7_9_orbits.py`](../scripts/m7_9_orbits.py): `integrate` / `poincare_section` / `close_returns` / `find_cycle` (multiple shooting, period free) / `floquet`; M7.10 E1 applies it verbatim to the Trkalian cavity mode (`find_cycle` fixed point at period `2π/λ`, multipliers on the unit circle = the orbit-language statement of pure-Maxwell marginal stability) |

## 8. Reproduce everything

| Step | Command | Expected |
| --- | --- | --- |
| Install (clone + deps) | `git clone https://github.com/openwave-labs/openwave && cd openwave && pip install -e .` | Python ≥ 3.10; Taichi installs CPU-only by default, no GPU needed |
| The whole Phase 1 chain, one command | `python openwave/xperiments/m7_hydroboros/research/scripts/m7_7_canonical.py` | quick mode (N = 48), ~10 min laptop CPU, prints the gate table + ALL GATES PASS |
| Full resolution | `... m7_7_canonical.py --full` | N = 64, the results-of-record numbers (§ 4) |
| The M7.8 helicity ladder | `python ... m7_8_helicity_pair.py seed` then `smoke` then `run` | seed gates seconds; smoke ~1.5 min (N = 48); the 5-rung ladder ~1 h (N = 64) |
| The M7.9 ChaosBook benchmark | `python ... m7_9_gates.py` then `m7_9_benchmark.py` then `m7_9_audit.py` | 4/4 gates (seconds); 5/5 benchmarks (~3 min); audit CONFIRMED (~4 min) |
| Raw data | small distilled JSONs live in [`data/`](../data/); large `.npz` intermediates are deleted by policy, and every deletion is documented in the task doc with the exact regen command | e.g. the M7.5 winner state regens in ~4 min (`python m7_5_clock_stability.py main`) |
| Where to read next | the canonical spec [`m7_theory_canonical.md`](../m7_theory_canonical.md) (equations + equation-to-code map) → the task docs in [`tasks/`](.) (each carries plan + findings + gates) | |

---

Cross-refs: [Phase 1 report](m7_phase1_report.md) · [M7.8 task](m7_8_helicity_pair.md) · [M7.9 task](m7_9_chaosbook.md) · [M7.10 task](m7_10_pure_maxwell.md) · [canonical spec](../m7_theory_canonical.md) · [roadmap](../m7_roadmap.md) · [question tracker](../m7_question_tracker.md).
