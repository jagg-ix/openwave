# M5.21 - Biaxial (1, δ, 0) dynamics: does the spectral gap protect the vortex loop?

**Status**: 🚧 PLANNED 2026-07-11 (top of Backlog, awaiting go). **Spec**: Duda 2026-07-11 14:27 ([`m5_20_convo.md`](m5_20_convo.md)): "topological vortex requires potential with (1, delta, 0) minimum - preferred three different, which should regularize to two equal in center - to prevent discontinuity of infinite energy, activating potential. So maybe there is problem with assumed simpler spectrum." Predecessors: [M5.20](m5_20_task_details.md) (conservative dynamics at δ = 0, all runs unwound) · [M5.19](m5_19_task_details.md) (statics; B2 measured the winding-pair classes at δ = 0.3). Outbound seed round sent 2026-07-11 16:07 (3 questions, [`m5_20_convo.md`](m5_20_convo.md)); answers FOLD IN at go, none hard-gate the run (fallbacks below).

## TASK PLANNING

### Scope: the question in one sentence

M5.20 proved the δ = 0 theory does not protect the loop because the two-equal-eigenvalue face is potential-free in that vacuum (4 zero modes, the removal path). His directive: the vortex sector requires three DISTINCT eigenvalues (1, δ, 0), which gaps that face ("activating potential") and changes the vacuum-manifold topology (SO(3) flag-manifold orbit, π₁ = Q₈, no free escape). M5.21 re-targets the audited M5.20 conservative-dynamics stack to (1, δ, 0) and measures whether the gap protects the loop: **protection as a function of δ**.

Both outcomes are decisive: HELD at δ ≠ 0 = the program's first protected loop (the reopening event); UNWOUND at δ ≠ 0 = the spectrum objection also fails in-framework, and protection has exactly one door left (the Q23 time sector).

### Spec decode (his 2026-07-11, both replies)

| His statement | Consequence for M5.21 |
| --- | --- |
| "(1, delta, 0) minimum - preferred three different" | Potential targets `c_p = 1 + δ^p` (the code's `cps` argument, already general; gate S3 pins the biaxial minimum to machine zero since M5.18) |
| "regularize to two equal in center ... activating potential" | The core seed keeps his two-equal regularization, which now COSTS potential energy: compute the per-cell core cost `V((1+δ)/2, (1+δ)/2, 0)` analytically as the barrier scale |
| "problem with assumed simpler spectrum" | δ = 0 results stand as that sector's verdict; no re-litigation. M5.21 is a NEW theory point, not a fix |
| "clock propulsion ... full 4x4 (g, 1, delta, 0)" | OUT OF SCOPE: the clock sector stays gated on Q23 (the M-variable time term); M5.21 runs the canonical kinetic term, flagged exactly as M5.20 did |

### Definition of done

1. **Gap map**: vacuum mass spectrum at diag(1, δ, 0) vs δ (numeric 6×6 V-Hessian, extending `vacuum_mass_spectrum`, vs analytic): confirm the zero-mode count drops 4 → 3 (Goldstone only) and measure the removability-face gap ω(δ).
2. **Vacuum enumeration**: the axisym-compatible uniform biaxial vacua (eigenvalue assignments to the (ρ̂, φ̂, ẑ) frame) enumerated with exactness checks (V = 0 AND u_curv = 0 per variant), the M5.20 dir-vacuum lesson applied up front.
3. **Instrument adaptation gated**: an eigenframe-based winding read (largest-eigenvector angle of the wound pair, with degeneracy-gap guards) validated on synthetic known-q configurations before any production read.
4. **Statics triage**: FIRE relax per (δ, pairing) seed: does the removability channel close already in statics?
5. **Dynamics verdict**: the M5.20 conservative instrument (gates GF/GA0-GA3 re-run at δ ≠ 0) on the production matrix; pre-registered classifier verdict per (δ, pairing) + per-peak core hunt; **the headline: protection vs δ**.
6. **Remnant re-probe**: is the breather-candidate oscillation present/absent/sharper in the gapped theory (comb vs the δ-dependent vacuum mass lines)?
7. Method-note-grade close page + independent adversarial audit; tracker (Q22/Q23) + convo routing updated; doc checker green.

### Blindspot pass (unknown unknowns the plan must carry)

| # | Blindspot | Mitigation |
| --- | --- | --- |
| 1 | **The winding instrument assumes the δ = 0 director structure**: `winding_measure` reads component angles; at δ ≠ 0 the wound object is an eigenframe, and near-degenerate eigenvalues make the read ill-conditioned | DoD 3: eigenframe read + gap guards, gated on synthetic seeds BEFORE production; keep the M5.20 core-hunt as the second instrument |
| 2 | **wscale confound**: recalibrating w per δ (virial autochi) changes the length scale, entangling "gap effect" with "scale effect" | Primary runs at the FIXED M5.20 w = 7.24e-4 (controlled comparison vs the δ = 0 corpus); ONE recalibrated control at δ = 0.3 to bound the scheme dependence |
| 3 | **Uniform biaxial vacua are not all exact on the axisym grid** (the M5.20 e2-vacuum surprise): assignments with distinct (ρ̂, φ̂) eigenvalues carry the equivariant background gradient `A_φ = [J, M₀]/ρ` | DoD 2 enumeration first; seeds built ONLY on verified-exact (or measured-cost) far fields; the linear-radiation lemma re-derived per chosen vacuum (the corrected M5.20 § 1 logic) |
| 4 | **Stiffness/dt**: the new mass gap raises the top frequency; dt stability must be re-established | GA1 dt² drift scaling re-run at the largest δ before production; dt reduced if needed (budget noted below) |
| 5 | **Winding-pair classes differ by orders of magnitude** (M5.19 B2 at δ = 0.3): the (δ, 0) pair may be so cheap it behaves δ = 0-like, the (1, δ) pair so stiff seeds barely relax | Run BOTH pairings at δ = 0.3 (the Q22 pairing half); expected-cost table from B2 informs seed amplitudes |
| 6 | **Q₈ topology bookkeeping**: at δ ≠ 0 the half-vortex classes are non-abelian (π₁ = Q₈); class labels from a single angle read can mislead | Verdicts rest on the core hunt + energy localization, not the class label; the label is reported as auxiliary |
| 7 | **His answers may arrive mid-plan** (same-day replier) | The folding table below is part of the plan; no redesign at go |

### Phased plan

| Phase | Content | Budget |
| --- | --- | --- |
| **A: vacuum theory** | Gap map (DoD 1) + vacuum enumeration (DoD 2) + core-cost table `V(two-equal)` vs δ; gates: S3 pinning, FD gradient at δ ≠ 0 (`dv_spec` with general `cps`), Hessian analytic-vs-numeric | short (minutes; NumPy) |
| **B: seeds + instrument** | Adapt `loop_field_escaped_z` to biaxial far fields; wind the chosen pair with the two-equal regularized core; eigenframe winding read built + gated on synthetic known-q configs (DoD 3) | short |
| **C: statics triage** | FIRE relax per (δ, pairing): δ ∈ {0.1, 0.3, 0.5} × pairing {(1,δ), (δ,0)} at modest budget; classify holds/dissolves; statics survivors + one dissolver go to dynamics | ~1h total |
| **D: conservative dynamics** | The M5.20 instrument verbatim (fast-path gradient re-gated vs the audited einsum path at δ ≠ 0; GA0-GA3 re-run incl. the pulse test on the chosen vacuum): production matrix below; classifier + core hunt + energy ledger per run | overnight core |
| **E: remnant + synthesis** | Blob probe + breathing comb vs the δ-dependent mass lines; protection-vs-δ synthesis; method note; adversarial audit; tracker/convo routing | ~1h |

**Production matrix (phase D, ~10 runs, M5.20-scale ≈ 1h/run)**: δ ∈ {0.1, 0.3, 0.5} × pairing {(1,δ), (δ,0)} closed-box (6 core runs) + sponge arms on the δ = 0.3 pair-winners (2) + the recalibrated-w control at δ = 0.3 (1) + a δ = 0 back-compat anchor re-run (1, pins continuity with the M5.20 corpus). Gentle-release arms (corepin-style) added only if quench starts unwind everywhere (they were the long-lived class in M5.20).

### Duda-answer folding table (the 2026-07-11 seed round)

| If he answers | Plan change |
| --- | --- |
| Q1: a δ value | Sweep collapses to {his value} + one bracket point each side; freed budget → longer horizons |
| Q2: the intended pairing | The other pairing drops to 1 control run |
| Q3: "spatial (1, δ, 0) is enough" | No change (that is the plan) |
| Q3: "the clock terms act at loop level" + the M-variable time term | SCOPE CHANGE: stop, re-plan (the kinetic term is new physics; M5.21 becomes the clock-augmented run and needs its own gates); if he asserts loop-level clock WITHOUT the term, M5.21 runs as planned and its verdict is explicitly conditional (same flag as M5.20) |
| Nothing by go | Run as planned (sweep + both pairings) |

### Preconditions (all green at plan time)

| Precondition | State |
| --- | --- |
| Potential + gradient at general `cps` | ✅ `potential_density_spec_np` / `dv_spec` ([`../scripts/m5_18_spectral.py`](../scripts/m5_18_spectral.py)), S3 gate exact |
| Conservative-dynamics instrument | ✅ [`../scripts/m5_20_a1_dynamics.py`](../scripts/m5_20_a1_dynamics.py) (Verlet, sponge ledger, gates); fast path re-gate needed at δ ≠ 0 (GF) |
| Verdict instruments | ✅ classifier ([`../scripts/m5_20_b1_verdicts.py`](../scripts/m5_20_b1_verdicts.py); fix the documented RADIATES pre-registration drift before re-use) + core hunt ([`../scripts/m5_20_b2_maps.py`](../scripts/m5_20_b2_maps.py)) + blob probe ([`../scripts/m5_20_c1_blob.py`](../scripts/m5_20_c1_blob.py)) |
| Winding-pair prior data | ✅ M5.19 B2 (classes at δ = 0.3, achieved upper bounds) |
| Blockers | none; the seed-round answers refine, not gate |

### Research-body destinations

Scripts `m5_21_*` in [`../scripts/`](../scripts/), data/plots `m5_21_*` in `../data/` + `../plots/`, close page `../findings/m5_21_method_note.md`, this file = the record; roadmap row [`../m5_roadmap.md`](../m5_roadmap.md); tracker [Q22](../m5_question_tracker.md#q22-detail) / [Q23](../m5_question_tracker.md#q23-detail); convo [`m5_20_convo.md`](m5_20_convo.md). Checkpoints → `../checkpoints/m5_21_progress.md` (OpenWave-local per the checkpoint-location rule).

### Model + effort

Same combo as M5.20 (it closed a comparable scope in 03:28): main-loop model, high effort on the physics derivations (gap map, lemma re-derivation) and the audit; mechanical phases (seed sweeps, run babysitting) at standard effort. Headless throughout; NumPy stack (no GPU need at 128×256).
