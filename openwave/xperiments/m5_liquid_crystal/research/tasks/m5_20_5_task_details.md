# M5.20.5: the extremal-orbit solve: converging the particle clock on the loop

**Status**: roadmap row at the top of [BACKLOG](../m5_roadmap.md) (PLAN written 2026-07-14 at the M5.20.4 close). Opens on the user's "go". Not Duda-gated: every step is machine-checkable; his Q24 answer folds at arm boundaries (the standing folding rule). If his answer lands BEFORE the go and contradicts the BVP framing, re-plan at PLAN.

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

### Contingencies + comms

| Trigger | Action |
| --- | --- |
| Duda's Q24 answer lands mid-task | Fold at the next arm boundary, log, continue |
| A2 converges early at the first working point | Spend the freed budget on A5 (one-harmonic breathing) rather than more working points |
| B fails an early gate | Stop arm B there (the escape is dead by measurement), log, give the time to A |
| Hard cap | Ship per-arm partials + the residual-vs-budget record |
