# M5.20.3: the 4×4 oscillation run: the constrained clock + radius breathing

**Status**: roadmap row at the top of [BACKLOG](../m5_roadmap.md) (PLAN-ready). Opens on Duda's constraint answer (promised for his morning of 2026-07-13, roughly 00:00-01:00 EDT) + the user's "go".

**Lineage**: [M5.20.2](m5_20_2_task_details.md) (the derived EOM, the boost runaway, the exact H(ω) clock, THE one question) · [M5.20.1](m5_20_1_task_details.md) (the spatial verdict + the measured core selection) · convo record [`m5_20_convo.md`](m5_20_convo.md) (the 2026-07-12 evening entry carries this plan's newest inputs: a ≈ δ/2 named, the radius-breathing mechanism) · combined outbound note [`../findings/m5_20_2_method_note.md`](../findings/m5_20_2_method_note.md) (§ II.3 = the question this task waits on) · tracker [Q18](../m5_question_tracker.md#q18-detail) / [Q19](../m5_question_tracker.md#q19-detail) / [Q23](../m5_question_tracker.md#q23-detail).

## TASK PLANNING (2026-07-12 evening, pre-go)

### Scope

Implement whatever constraint Duda names for the boost sector, re-verify well-posedness under it (the triage ladder), then run the first 4×4 `(g, 1, δ, 0)` oscillation production on the audited axisym stack and measure the oscillation observables he has now spec'd. Three deliverable measurements, in priority order:

| # | Measurement | His spec (2026-07-12 evening reply) |
| --- | --- | --- |
| 1 | Endpoint core spectrum from free minimization | "(g, 1, a, a) for a ~ delta/2": the first time the core VALUE is named; M5.20.1 already measured (1, δ/2, δ/2) in 3D, this task tests it in 4D under the constraint |
| 2 | Loop-radius breathing at conserved total energy | "radius of loop can also oscillate - to maintain total energy, which is density per length depending on flavor, times loop length": measure R(t), E/length, and their exchange |
| 3 | Oscillation spectra vs the 4×4 gap ladder | FFT of R(t) and of the core-spectrum trajectory λ_i(t), compared against the measured ladder ω = {0.0093, 0.0466, 0.1349, 78.28} |

NOT in scope: the full AMBer flavor fit (pre-registered as the long-run target, this task reports qualitatively only; observables scoreboard in [`../../theory/_CITATIONS.md`](../../theory/_CITATIONS.md), local `amber_neutrino_flavor_rl.pdf`); the flavor naming (which core state = e/μ/τ is author-gated, the note says "core states"); charges (3-equal core) and black holes (4-equal core, his regularization ladder): later tasks.

### Definition of done

| ✅ when | Bar |
| --- | --- |
| Constraint implemented + machine-checked | Implemented exactly as sanctioned, derivation section gated against the M5.18-verified Lagrangian (the M5.20.2 GB-gate pattern) |
| Well-posedness re-triaged UNDER the constraint | T1 dt scaling (max-deviation criterion, dt² ratios) + T2/T3 injection reruns: the boost runaway must be CLOSED by the constraint; GO/NO-GO pre-registered, production only on GO |
| Production oscillation runs landed | δ = 0.3 primary (the audit-clean regime) + one companion δ; T = 2000 baseline, dt ≤ 0.01 (the stiff g-mode ω = 78.28 bound); energy ledger ≤ 1e-5; seed + endpoint cross-section prints (flow-doc rule 2026-07-12) |
| The three measurements reported honestly | Core gate vs a ≈ δ/2; R(t) + E/length vs his conservation mechanism; spectra quoted WITH the FFT bin width Δω (the refuted "0.2% on-the-line" lesson) |
| Method note + audit + routing | New note `../findings/m5_20_3_method_note.md` (FIELD CONTENT box up front, plots embedded as they exist), independent adversarial audit (own instruments), tracker Q18/Q19/Q23 resolution routing, convo entry, outbound draft timed to land before 14:00 EDT (the comms window) |

### Gating

Roadmap `Gated By`: **Duda's constraint answer** (the Q18 + Q19 + Q23 fusion sent 2026-07-12) + user "go". At go: log his email verbatim + decode in [`m5_20_convo.md`](m5_20_convo.md), pick the folding-table row, move the roadmap row to In Progress, arm the resume ping, open `../checkpoints/m5_20_3_progress.md`.

### The constraint folding table (branch on his answer; pick ONE row at go)

| His answer names | Implementation | Cost |
| --- | --- | --- |
| Dirac treatment of the primary constraint (Ṁ ∝ η null direction) | Constrained integrator: project Ṁ onto the constraint surface each step (the M5.8.2c spectral-projection precedent); the projection energy ledger becomes its own gate | Heaviest: new gate ladder before production |
| Restriction to rotation orbits (the K_eff > 0 sector) | Dynamics on the rotation-generated subspace, or a penalty/projection removing boost directions from Ṁ | Medium: the generator split already exists in `m5_20_2_c_clock.py` |
| A branch or sign choice we missed (e.g. one_timelike, an η-convention flip) | Rerun the K_eff census on the sanctioned branch FIRST (minutes); if boosts turn positive there, unconstrained dynamics is back on and the task simplifies | Cheapest: census before any integrator work |
| The clock is ansatz-level (rigid orbits only) | No unstable integration at all: extend the exact H(ω) machinery; radius breathing = a quasi-static ladder of constrained minima in R | Light: statics stack exists (`m5_20_1_c_statics.py` FIRE) |
| Energy-minimization-first (the hint in his quick reply: "everything should come from energy minimization") | Constrained descent (FIRE/gradient flow) at fixed winding + fixed E_total; R(t) read from the quasi-static sequence | Light-medium |
| The answer does not close the sector | The hard cap fires (M5.20.2 precedent): document what his answer does give, ship partials + ONE sharp follow-up question | Bounded |

### Pre-registered gates

| Gate | Criterion |
| --- | --- |
| GC0 constraint consistency | The constrained EOM reduces to the M5.20.2 derived EOM when the constraint is inactive; FD gradient/force checks at 1e-7 level |
| GC1 census under constraint | K_eff census rerun with the constraint active: the boost sector must read closed (no negative unbounded directions reachable) |
| G-RUNAWAY | T2/T3 injection reruns under the constraint: no divergence over T = 400 (the t ≈ 21 runaway must be gone, not delayed) |
| G-DT | dt² max-deviation scaling (the patched T1 criterion); production dt ≤ 0.01 |
| G-CORE | Endpoint core spectrum reads (g, 1, a, a) with a ≈ δ/2 from free minimization; genuine-regime bar δ ≥ 0.3 (the M5.20.1 audit caveat: vacuum-confounded below) |
| G-RADIUS | Energy ledger ≤ 1e-5 while R(t) varies; test E_total ≈ (E/length) × 2πR against the measured trajectory |
| G-SPECTRUM | Every frequency claim quoted with Δω (bin width) and window length; band language, never "on-the-line", unless the peak is resolved by ≥ 3 bins |
| Cross-sections | Seed t = 0 AND endpoint field-state prints, embedded in the note (run-evidence rule) |

### Blindspot pass (unfamiliar territory: constrained 4×4 dynamics + oscillation observables)

| # | Unknown unknown surfaced | Fold into plan |
| --- | --- | --- |
| 1 | **The timescale race**: the spatial sector unwinds (pair_d0 half-life t ≈ 125-375; gap-ladder periods 2π/ω ≈ 47-676): the loop may unwind before one radius-oscillation period completes, unless the constraint changes protection | Measure BOTH clocks per run (unwind time vs oscillation period); a "unwinds first" outcome is a reportable result, not a failed run |
| 2 | Axisymmetry represents R(t) (the ring radius is a cross-section coordinate) but FORBIDS non-axisym decay channels and flavor modes | Scope-box in the note § honesty section, same pattern as M5.20.x § 4 |
| 3 | Constraint-projection integrators are not symplectic: the energy ledger cannot be inherited from the unconstrained stack | G-RADIUS re-validates the ledger UNDER the constraint before production |
| 4 | The g value: M5.20.2 used the engine-convention g; his answer may fix g differently (it sets the stiff mode ω = 78.28 and the dt bound) | One-census sensitivity spot-check at an alternate g (minutes); dt bound recomputed from the measured stiff ω |
| 5 | Wall-clock: M5.20.x production was ~4.5 h for 10 runs; the send window is 14:00 EDT | Production matrix capped at ~6 runs; primary δ = 0.3 first so the headline lands even if the tail is cut |
| 6 | Seeds: the M5.20.1 endpoint `_state.npz` files were deleted at close (> 1 MB rule) | Fresh seeds from the loop builder are the default; remnant states regenerate via `python3 m5_20_1_d_dynamics.py run <δ> <pairing> 2000 <mode>` if needed |

### Unknowns quadrants self-test

| Quadrant | Biggest unknown | Route |
| --- | --- | --- |
| Known knowns | EOM, gap map, dt bound, seeds, census machinery (M5.20.2 assets, frozen) | Reuse; GC0 guards the join |
| Known unknowns | THE constraint (author-gated, inbound tonight); δ value (sweep stands); whether a ≈ δ/2 emerges in 4D (machine-checkable) | Folding table; G-CORE |
| Unknown knowns | The user's delivery bar, now explicit: ONE Duda-legible note, 4×4 reinforced, outbound lands before 14:00 EDT | Wired into DoD |
| Unknown unknowns | The blindspot list above; whatever the audit finds | Deviations log at EXECUTE + independent adversarial audit at FINISH (cardinal rule) |

### Research-body destinations

| Artifact | Destination |
| --- | --- |
| Scripts | `../scripts/m5_20_3_a_constraint.py` (implementation + GC gates) · `m5_20_3_b_triage.py` · `m5_20_3_c_production.py` · `m5_20_3_d_observables.py` (R(t) tracker, E/length, core trajectory, spectra) · `m5_20_3_plots.py` |
| Data / plots | `../data/m5_20_3_*.json` (+ logs; > 1 MB raw deleted at FINISH with regen docs) · `../plots/m5_20_3_*.png` |
| Findings | `../findings/m5_20_3_method_note.md` (new note; the combined M5.20.x note stays the Part I + II record and gets a forward link) |
| Records | This file (FINDINGS + TASK REVIEW) · `m5_20_convo.md` (his answer + the outbound) · tracker Q18/Q19/Q23 · `../checkpoints/m5_20_3_progress.md` (opens at go, resume-complete for a model switch) |

### Sub-experiments (phase plan)

| Phase | Content | Gate |
| --- | --- | --- |
| A | Constraint implementation from his answer (folding-table row) + derivation section | GC0, GC1 |
| B | Triage under the constraint: T1 dt / T2 injections / T3 textures | G-RUNAWAY, G-DT → GO/NO-GO |
| C | Production: δ = 0.3 primary + one companion, T = 2000, closed box; cross-section prints | Energy ledger, G-CORE |
| D | Observables: R(t), E/length, λ_i(ρ→0, t), spectra vs the gap ladder | G-RADIUS, G-SPECTRUM |
| E | Method note + independent adversarial audit + routing + outbound draft | Doc checker exit 0; audit verdicts folded |

### Preconditions

| Precondition | State |
| --- | --- |
| Duda's morning email logged + decoded, folding row chosen | 🚧 pending (expected ≈ our midnight) |
| M5.20.2 assets on disk (`m5_20_2_a_eom.py`, hessian4, k_eff, protection machinery) | ✅ frozen at close |
| AMBer scoreboard reference | ✅ `../../theory/_CITATIONS.md` + local PDF |
| Resume ping + checkpoint file | 🚧 at go (user supplies resets_at) |

### Model + effort

Fable 5 high for Phase A (novel constraint derivation) and the audit brief; default effort for B-D (mechanical production against pre-registered gates, try cap 3 per gate). Independent agent with own instruments for the audit (cardinal rule).

### Contingencies + comms

| Trigger | Action |
| --- | --- |
| Hard cap (~1 day) | Ship partials + ONE sharp follow-up question (M5.20.2 precedent) |
| Fable-cap model switch mid-run | Checkpoint file is resume-complete (decision tree, relaunch commands); detached production processes survive |
| Results ready after ~13:00 EDT | Flag to Rodrigo: holding for the next-day 14:00 EDT send costs nothing (deeper replies arrive his morning either way) |
| Outbound content | Next email opens with the brief timing apology (Rodrigo-voice bullet) + the one-sentence "measured, not manual" clarification + the a ≈ δ/2 prediction-confirmed line, then this task's results |

## M5.21 findings feed (2026-07-14, folded pre-go)

> **The decisive framing (measured at M5.21, seeded here by the user 2026-07-14): containment is exactly what the constraint must buy, and that is now a measured statement, not a hunch.** In the unconstrained canonical stack the defect's energy is not contained: the statics is a saddle-slide and a kinetic clock kick radiates away, while the topological charge and an intrinsic core-breathing oscillation survive. This task lands the constraint on the LOOP; [M5.21.1](m5_21_task_details.md) then puts the same constraint on the ELECTRON and reruns the identical clock-vs-noclock comparison against the M5.21 baseline. If the constrained clock contains the energy where the unconstrained kick radiated, that is "the particle clock creating particle stability" on film.

Series framing: [`../m5_particle_hunt.md`](../m5_particle_hunt.md) (M5.20 = the vortex-loop hunt, possibly the neutrino; M5.21 = the hedgehog hunt, possibly the electron). [M5.21](m5_21_task_details.md) (the electron particle-clock film strip, closed 2026-07-14) ran the SAME canonical-completion stack on the hedgehog and produced inputs this task should use. **Presentation boundary (user, 2026-07-14): the M5.20 series KEEPS its own cross-section spec** (the [`m5_20_1_seed_maps.png`](../plots/m5_20_1_seed_maps.png) / [`m5_20_1_endpoints.png`](../plots/m5_20_1_endpoints.png) seed + endpoint map format); the M5.21 film-strip panel format stays M5.21-series-only for now. **Reciprocal series rule: every M5.21-series run re-captures the latest M5.20-series results at PLAN.**

| M5.21 finding | Use in this task |
| --- | --- |
| The boost sector stayed EXACTLY 0.0 through 4 rotation-sector runs on full defect nonlinearity (noclock / twist ω=0.05 T=400 / global-axis / gentle) | Strengthens the census quarantine: rotation-sector dynamics alone never wakes the runaway; the constraint's job is specifically the boost/time sector, as framed in the folding table |
| The core of a defect RINGS coherently at ω ≈ 0.11-0.13, near (~15% below) the 0.1349 activated-face rung; softening consistent with large-amplitude anharmonicity; intrinsic (no clock kick needed) | Direct rehearsal for the radius-breathing + spectra observables: expect the measured lines NEAR but BELOW the analytic ladder at large amplitude; keep the FFT-bin honesty + quadratic-detrend + sub-bin parabolic-peak method (in [`../scripts/m5_21_c_clockrun.py`](../scripts/m5_21_c_clockrun.py) analysis and the checkpoint FFT snippets) |
| An unconstrained velocity kick (kinetic clock) stalls in ~1 sweep and radiates; it never becomes a persistent internal rotation | Sharpens the folding-table framing: the constraint is load-bearing for ANY persistent clock, not just for boost-sector safety; the oscillation production should not expect seeded rates to persist without it |
| dt = 0.02 gave ledgers 1e-6 to 4e-6 over T ≤ 400 with the time row on-branch (the 78.28 stiff mode never excited when unforced) | GD-triage prior: start the dt scan at (0.02, 0.01, 0.005); the stiff bound binds only if the constraint activates the time eigenvalue |
| Real-FD gradient checks hit a ~5e-6 roundoff floor at the g⁴ trace scale; the energy is polynomial in M, so COMPLEX-STEP directional derivatives are exact (1.75e-15 measured) | Gate any new constrained-EOM gradient with complex-step, not real FD (pattern in [`../scripts/m5_21_d_3dcheck.py`](../scripts/m5_21_d_3dcheck.py) `gate_gd3a`) |
| The fixed-radius meridional winding read branch-swaps (±1/0 flips) where λ1 ≈ λ2 after churn; endpoint-only reads mislead | The loop winding measure here (`winding_measure_biax`, multi-r_w) should keep the multi-radius + endpoint-plus-trace practice; treat single-radius q dips as suspect before calling unwinding |
