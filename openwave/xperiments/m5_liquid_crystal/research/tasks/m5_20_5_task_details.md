# M5.20.5: the extremal-orbit solve: converging the particle clock on the loop

**Status**: ✅ CLOSED 2026-07-14 (go 17:29, FINISH same evening; adversarially audited 7C/2Q, fixes applied). **Both arms returned kills**: no extremal rigid orbit on the loop (directional block), the γ = −1 escape dead at its own statics gate. Full record: [`../findings/m5_20_5_method_note.md`](../findings/m5_20_5_method_note.md). Duda's Q24 answer did NOT land mid-task (no folds).

**Lineage**: [M5.20.4](m5_20_4_task_details.md) (the formulation winner: free-period least-action roots exist on exactly-periodic boost-conjugated rotation orbits under the corrected φ-averaged kinetic Q2_avg; the a4 descent machinery + state; the audit's γ = −1 escape candidate) · [`../findings/m5_20_4_method_note.md`](../findings/m5_20_4_method_note.md) (equations + the audit record) · tracker [Q24](../m5_question_tracker.md#q24-detail) · the M5.20.3 true-L instrument (gates GC0a-e green).

## TASK PLANNING (2026-07-14, at the M5.20.4 close)

### Scope

Converge an actual extremal orbit (the particle clock) on the loop under the corrected rigid-orbit functional and read the payoff observables; in parallel, run the audit-escape's own gate program so that candidate lives or dies on measurements before any ask is spent on it.

| Arm | Step | Content | Kill / survive (pre-registered) |
| --- | --- | --- | --- |
| **A (main): the extremal solve** | A0 | Instrument: `q2_avg` gradient (`grad_q2_avg` = φ-mean of `grad_q2(M, G_φ)`), complex-step gated; nphi exactness gate: the adjoint action has harmonics ≤ 2, Q2 is quadratic in G_φ ⇒ harmonics ≤ 4 ⇒ trapezoid nphi ≥ 5 is EXACT: verify nphi 8 == 16 at machine precision, then run at the cheap nphi | instrument gates green before any physics |
| | A1 | The (χ, ω) working points: refine the corrected root ladders ω*(χ) per family (from the a1c data + finer χ); look for interior dS/dχ extrema; read ω*(χ) against the chirped vacuum ladder scale at the ring (ω₁(ρ = 17) ≈ 1.15): note any crossing as a natural selection point; pick 2-3 working points (moderate ω*, spread across families) | at least one workable (G′, ω*) point exists (already known from a1c: yes) |
| | A2 | The extremal solve at fixed (G′, ω*): drive gradŜ_avg = ω*²·grad_q2_avg − G_static to zero. Try cap 3 methods: (i) the a4 residual-descent (corrected functional), (ii) Newton-Krylov on the gradient field, (iii) L-BFGS on Φ = ½\|gradŜ_avg\|². Convergence bar (pre-registered): residual ≤ 1e-3 × \|G_static\|, q = 0.5 intact, U and Q2_avg finite and loop-scale. Two starts per point: the a4 state (warm) + the recipe seed (cold) | converged orbit at any working point = SURVIVE; all 3 methods × 2 starts fail at every point = ship the residual-vs-budget record + the sharpest characterization of what blocks (saddle structure vs conditioning) |
| | A3 | The coupled stationarity: alternate (M-solve at fixed ω) ↔ (ω ← root(U, Q2_avg)) ↔ (χ-extremal step) to joint stationarity; verify H = ω²Q2_avg + U = 0 at close (the exact identity = the convergence certificate) | joint residuals decrease across rounds; else report the partial (M-stationary at fixed ω is already reportable) |
| | A4 | THE OBSERVABLES on the converged orbit (the M5.20.3 pre-registered targets, finally measurable): the clock frequency ω* vs the ρ-chirped ladder at the ring radius; the energy split (T = −U at the root, the zero-energy clock); CONTAINMENT: energy-localization radius vs the static loop's (does the orbit keep energy at the ring?); the winding + core spectrum on-orbit | measured on the converged orbit; if A2 shipped partials, read the same observables at the best-residual state, labeled 🔶 |
| | A5 (stretch, timebox-gated) | The minimal Fourier extension (one harmonic) for the radius-breathing observable: ONLY if A2-A4 close early; otherwise it is the named successor (the rigid level cannot breathe by construction) | explicitly optional |
| **B (parallel diagnostic): the escape's own gates** | B1 | Statics anchors under L − 1·s2(a = 4.5) + β·qc (β ~ 1e-2): frozen-time re-relax of the loop; core spectrum, ring, q vs baseline (the arm-C statics machinery reused) | any anchor break = the escape dies at its own statics gate |
| | B2 | The combined kinetic operator k10_s2 (einsum build for the dressed-Skyrme form), gated against per-cell polarization at sample cells; then the full-grid PSD-margin re-check (reproduce the audit's machine-zero margin with our own build) | build gate green before evolution |
| | B3 | Evolution under the combined dynamics from the loop seed: bounded to T = 50? Does the trajectory stay in the physical spectral band (the audit's caveat: PSD is band-limited)? Film strip per the standard | bounded + band-kept + anchors green = the escape graduates to a real completion candidate (still author-gated on the γ = −1 sign); any failure = dead by measurement, no ask spent |

Run order: A0 → A1 → A2/A3 (the core) with B1 launched in background early (cheap) and B2/B3 interleaved while A2 iterates. NOT in scope: the full Fourier BVP container (successor unless A5 fires), the hedgehog (M5.21.1 inherits after this task), any outbound content beyond folding.

### Definition of done

| ✅ when | Bar |
| --- | --- |
| Arm A verdict | Either a converged extremal orbit (bar: residual ≤ 1e-3 relative, q intact, H = 0 certificate) with the A4 observables read, OR the honest 3-method × 2-start non-convergence record with the blocking structure characterized |
| Arm B verdict | Per-gate verdicts (statics / build / bounded+band) on the escape candidate; it lives or dies on measurements |
| Instruments gated before physics | A0 complex-step + nphi-exactness; B2 build vs polarization (the GC0 pattern; try cap 3 per gate) |
| Timeboxes | A0+A1 ≈ 1 h; A2+A3 ≈ 2-3 h (each gradŜ_avg eval costs nphi grad_q2 calls: budget iterations accordingly); A4 ≈ 1 h; B ≈ 2 h interleaved; hard cap ~1 day, the tail ships partials |
| Records | Method note `../findings/m5_20_5_method_note.md` (equations first, code map, figures embedded as they land); film strips where states evolve (B3; basic template per [`../m5_visualization.md`](../m5_visualization.md)); independent adversarial audit (cardinal rule); tracker Q24 + roadmap + checkpoint routing |

### Gating

Roadmap `Gated By`: user "go" only. Duda's Q24 answer folds at the next arm boundary if it lands mid-task (log the fold in this file). The γ = −1 sign admissibility stays author-gated regardless of B's outcome: B's gates only decide whether the candidate is WORTH the ask.

### Blindspot pass (saddle search + averaged functionals + a new kinetic operator)

| # | Unknown unknown surfaced | Fold into plan |
| --- | --- | --- |
| 1 | Minimizing Φ = ½\|grad\|² can converge to a stationary point of Φ that is NOT a zero of the gradient (a non-extremal critical point) | the convergence bar is on the RESIDUAL itself, never on Φ-stationarity; verify H = 0 as the independent certificate |
| 2 | The φ-average could be under-resolved and quietly wrong | the band-limit argument (harmonics ≤ 4 ⇒ nphi ≥ 5 exact) is GATED (nphi 8 == 16 to machine precision), not assumed |
| 3 | The warm start (a4 state) biases toward the slice-functional basin | two starts per working point (warm + cold), pre-registered |
| 4 | The winding read flickers under churn (the known artifact) | final-state verdicts use the multi-radius q read + the audit's many-center \|M13\| scan pattern, not a single detector |
| 5 | k10_s2's derivation (commutator form, dressed both sides) is error-prone | einsum build gated against per-cell polarization BEFORE any full-grid claim; the audit's own script is on disk as an independent cross-check |
| 6 | ω* at the crossing edge is stiff (ω → ∞); deep-branch ω → 0 is slow physics | A1 picks moderate-ω working points; the ladder-scale comparison flags the physically natural ones |

### Research-body destinations

| Artifact | Destination |
| --- | --- |
| Scripts | `../scripts/m5_20_5_a_orbit.py` · `m5_20_5_b_escape.py` · `m5_20_5_plots.py` |
| Data / plots | `../data/m5_20_5_*.json` (+ npz ≤ 1 MB; larger deleted at FINISH with regen docs) · `../plots/m5_20_5_*.png` (film standard) |
| Findings | `../findings/m5_20_5_method_note.md` |
| Records | This file (FINDINGS + TASK REVIEW) · tracker Q24 · `../checkpoints/m5_20_5_progress.md` (opens at go, resume-complete) |

### Preconditions

| Precondition | State |
| --- | --- |
| M5.20.4 instruments + verdicts (q2_avg, grad_q2, the a4 state npz, the a1c ladders, the audit script) | ✅ closed 2026-07-14, all on disk |
| M5.20.3 true-L stack (gates green) | ✅ |
| The escape's definition + the audit's PSD identity | ✅ `../data/m5_20_4_audit.json` + `m5_20_4_audit_check.py` |
| Resume ping + checkpoint | 🚧 at go (user supplies resets_at) |

### Model + effort

Fable 5 high for the A2/A3 solver design and the B2 operator derivation (novel numerics + algebra); default effort for the mechanical gate loops; independent agent with own instruments for the audit (cardinal rule).

### Deviations log (EXECUTE, as they happen)

| # | When | Deviation | Why (conservative option taken) |
| --- | --- | --- | --- |
| 1 | 2026-07-14 ~18:20 | Added phase `a2x` (alignment diagnostic, not in the plan) after all 6 wp0 runs failed the bar | the pre-registered kill branch requires "the sharpest characterization of what blocks (saddle structure vs conditioning)"; a2x measures exactly that (cos alignment + sector split), 3 cheap evals, no scope creep |
| 2 | 2026-07-14 ~18:25 | B1 extended to β = 0 and β = 1e-4 beyond the planned β ~ 1e-2 | the candidate is defined at β → 0⁺; killing it only at β = 1e-2 (where the qc texture dominates) would be an unfair gate; the β-limit runs make the statics verdict decisive |
| 3 | 2026-07-14 ~18:40 | A3 started from a regenerated loop-preserving STALL state (new `stall` phase) instead of the a2 best-residual state | the a2 "best" was the winding-destroyed Newton state (q = 0): not a valid clock start; the alternation must be given the best LOOP state to be a fair test |

### Contingencies + comms

| Trigger | Action |
| --- | --- |
| Duda's Q24 answer lands mid-task | Fold at the next arm boundary, log, continue |
| A2 converges early at the first working point | Spend the freed budget on A5 (one-harmonic breathing) rather than more working points |
| B fails an early gate | Stop arm B there (the escape is dead by measurement), log, give the time to A |
| Hard cap | Ship per-arm partials + the residual-vs-budget record |

## FINDINGS (2026-07-14)

Full equations + results + figures: [`../findings/m5_20_5_method_note.md`](../findings/m5_20_5_method_note.md). Data in `../data/m5_20_5_*`, plots in `../plots/m5_20_5_*`.

| # | Finding | Status | Where |
| --- | --- | --- | --- |
| 1 | Instrument gates: `grad_q2_avg` == complex-step (2.8e-16); the band-limit claim MEASURED (nphi 5 == 16 at 1.7e-16, run at nphi = 5); all nine s2 EL pieces (statics, kinetic, pi, both gradients, kdot, fast K10 build, operator consistency) machine-verified FIRST TRY | ✅ | note § 1.2, § 2.2 |
| 2 | The refined root ladders are MONOTONE in χ (no interior dS/dχ extremum); the chirped-ladder scale ω₁(ring) = 1.177 sits AT the sign-crossing edge of every family (within Δχ ≈ 1e-3): the "natural" clock frequency is the stiff edge, not a workable interior point | ✅ measured | note § 1.3 |
| 3 | **The extremal solve FAILS the pre-registered bar at every working point**: 18/18 runs non-converged (3 methods × 2 starts × 3 working points; two of the three distinct families solved, the third audit-probed same-class); loop-preserving methods stall at rel 0.99-1.02; Newton-Krylov lowers the residual 5-470× only by DESTROYING the winding, ending in an unwound rough state (U = 18.7× the loop's, still non-stationary), not the vacuum | ✅ measured (kill branch) | note § 1.4 |
| 4 | **WHAT blocks (the kill branch's required characterization)**: the kinetic gradient is ANTI-ALIGNED with the static residual, cos(g_kin, g_stat) = −0.328 (J23^K2, all χ probed 0.72-2.0, noise-robust) / ≈ 0 (J23^K3, J12^K1): over REAL ω the residual floor is exactly \|g_stat\| (at ω = 0) and every ω > 0 makes it worse (J23) or leaves it unchanged (orthogonal families); g_stat is 99.9997% time-row (the frozen-time-relax legacy force): the block is DIRECTIONAL/structural, not conditioning | ✅ measured + audit-extended | note § 1.4b |
| 5 | The coupled (M, ω, χ) alternation stops at its own guard in round 1: the M-descent flips Q2_avg to POSITIVE (+1.386), the balance root ceases to exist, H = 0 certificate fails by order unity: no rigid-orbit fixed point in the reachable basin | ✅ measured | note § 1.5 |
| 6 | Observables at the best loop-preserving state (pre-registered 🔶 fallback): loop intact (q = 0.5, ring 17.46, r50/r90 = 22.5/27.5 vs baseline 20.5/27.5), H = 0.463 ≠ 0: the state is a loop, not a clock | 🔶 at non-extremal state | note § 1.6 |
| 7 | **The audit-escape candidate (γ = −1 s2 + β·qc) is DEAD at its own statics gate at EVERY β** (1e-2, 1e-4, 0): the loop unwinds (q → 0 within 500 FIRE iterations, ring 17.5 → 27-42); the β = 0 row proves the kill is texture-independent: the loop is statically UNSTABLE under `L − s2` itself. No ask spent on γ = −1 | ✅ measured (kill) | note § 2.3 |
| 8 | The audit's PSD margins REPRODUCED with our own independent `k10_s2` build (marginal −1e-13 at β = 0; 2.45e-3 / 2.45e-1 at β = 1e-4 / 1e-2), including on a background the audit never saw: the candidate's kinetic operator was fine; statics killed it | ✅ measured | note § 2.4 |
| 9 | B3 evolution SKIPPED per the pre-registered contingency (statics dead at every β); the combined-dynamics machinery (accel_esc, k10_s2 fast build) is built, gated, on disk for successors | ✅ per plan | note § 2.5 |


## TASK REVIEW (2026-07-14)

**Task Duration:** 01:13 (from 17:29 to 18:42)
**Usage Cap Triggered:** NO (the resume ping was disarmed at FINISH without firing)

Presented in the terminal at FINISH; approved by the user 2026-07-14 evening. The user's follow-on decisions at approval: **M5 PARKS gated on the Q24 outbound to Duda** (roadmap note added); the Duda draft updated with the sharpened ask (see [`m5_20_convo.md`](m5_20_convo.md)).

**Results**

| # | Result | Status |
| --- | --- | --- |
| 1 | Instrument gates all green FIRST TRY: `grad_q2_avg` == complex-step (2.8e-16); nphi band-limit MEASURED exact (5 == 16 at 1.7e-16; audit: harmonics even tighter, Q2 ≤ 2); all nine s2 EL pieces machine-verified | ✅ measured |
| 2 | A1 ladders monotone in χ (no interior dS/dχ extremum); the chirped-ladder scale ω₁(ring) = 1.177 sits AT the sign-crossing edge of every family | ✅ measured |
| 3 | **ARM A KILL**: 18/18 solver runs fail the pre-registered bar; loop-preserving stalls at rel 0.99-1.02; Newton progress (5-470×) only by destroying the winding (unwound rough state, 18.7× loop energy, still non-stationary) | ✅ measured (kill) |
| 4 | **The WHY**: rotation kinetic gradient ANTI-ALIGNED (J23^K2, cos = −0.328, χ-stable, noise-robust) or orthogonal (other families) to the loop's 99.9997%-time-row static force: over real ω the residual floor is exactly \|G_static\|; a rigid conjugation orbit cannot trade energy with the time-row sector (breathing can: the successor question) | ✅ measured + audit-extended |
| 5 | A3 alternation stops at its guard in round 1 (Q2_avg flips positive: root lost; H = 0 certificate fails); A4 observables read at the best loop-preserving state per the pre-registered fallback | ✅ / 🔶 |
| 6 | **ARM B KILL**: the γ = −1 escape dead at its own statics gate at EVERY β (1e-2/1e-4/0): the loop statically unstable under L − s2 itself; PSD identity reproduced with our own build; B3 skipped per contingency; ask withdrawn, none spent | ✅ measured (kill) |
| 7 | Adversarial audit (independent agent, own instruments): 7 CONFIRMED / 2 QUALIFIED, zero substantive refutations; 9 wording/number fixes applied (headline: "vacuum trap" → "winding destroyed, non-stationary end state"); audit extended coverage (J23^K3 probed: orthogonal class) | ✅ |

**Issues / blockers**: none open. wp1/wp2 solver logs buffer until run completion (cosmetic). No >1 MB data files produced (largest npz 0.64 MB; nothing deleted).

**Deviations from plan**: three, logged in § Deviations as they happened (a2x diagnostic; B1 β-extension to {0, 1e-4}; A3 started from the regenerated loop-preserving stall state).

**Action needed**: Duda draft updated with the sharpened ask (done at review); M5 parked on the Q24 answer (roadmap note + M5.21.1 gate rewired); the one-harmonic breathing container is the named successor task once the formulation lands.

**Model-doc sweep**: canonical [`../m5_theory_canonical.md`](../m5_theory_canonical.md) UPDATED (§ 2 row 4 amended + new row 4b rigid-level kill + row 5 escape annotated dead; § 3 nphi = 5 gate; § 5.4 a2x diagnostic + the s2/qc EL library; § 6 two new anti-recipes; § 7 tracker pointer). Briefing `__M5_model_briefing.md`: EXPLICIT SKIP: no cell it states changes (its clock/status rows are M5.8-era scoped; deep-dive pointers already current).

**Findings**: M5.20.5 measured the rigid-orbit level OUT on the loop: the M5.20.4 balance roots are real but do not extend to extremal orbits, because the rotation kinetic gradient cannot cancel the loop's almost-purely-time-row static force at any real frequency (a directional obstruction, not a solver failure), and the audit-proposed γ = −1 kinetic completion died at its own statics gate before costing an ask. The clock, if it lives in this Lagrangian, must be profile-dynamic (breathing), which is exactly the energy-transfer channel the rigid ansatz lacks.

**Research docs created / updated**:

- [`../findings/m5_20_5_method_note.md`](../findings/m5_20_5_method_note.md) (the record: equations first, code map, § 4 audit; plots embedded)
- This file (FINDINGS + deviations) · [`../m5_question_tracker.md § Q24`](../m5_question_tracker.md) · [`../m5_roadmap.md`](../m5_roadmap.md) (Done row + park note) · [`../m5_theory_canonical.md`](../m5_theory_canonical.md) (model-doc sweep)
- Scripts: [`../scripts/m5_20_5_a_orbit.py`](../scripts/m5_20_5_a_orbit.py) · [`../scripts/m5_20_5_b_escape.py`](../scripts/m5_20_5_b_escape.py) · [`../scripts/m5_20_5_plots.py`](../scripts/m5_20_5_plots.py) · audit [`../scripts/m5_20_5_audit_check.py`](../scripts/m5_20_5_audit_check.py)
- Data `../data/m5_20_5_*` · key plots [`m5_20_5_a1_ladders.png`](../plots/m5_20_5_a1_ladders.png), [`m5_20_5_a2_convergence.png`](../plots/m5_20_5_a2_convergence.png), [`m5_20_5_b_gates.png`](../plots/m5_20_5_b_gates.png), [`m5_20_5_a_maps_wp0.png`](../plots/m5_20_5_a_maps_wp0.png)
