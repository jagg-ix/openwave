# M5.12: Neutrino vortex-loop at the physical regime (the fresh re-entry)

> Task **M5.12** (M5 / Liquid-Crystal model). Status: **Backlog** · Gated by: ~~M5.16~~ ✅ (delivered 2026-07-02) + **[M5.17](m5_17_task_details.md)** (the methods surface + re-ask; the ask round went out 2026-07-02 but the 2026-07-03 reply was a methods audit, not answers: § Ask-round outcome below) · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation.

---

## Why a new task ID (and not resuming M5.11)

M5.11 is **closed ✅** ([`m5_11_task_details.md`](m5_11_task_details.md)): it answered Duda's 2026-06-22 "too simple" critique with real energy-minimized regularized solitons, banked the electron + `α⁻¹` reproduction, built the AD + chiral machinery, and **precisely isolated** the open frontier (the 2×2 elimination). The re-entry is a genuinely different task: physical `(g, δ, V)` regime instead of placeholders, uniaxial-primary construction instead of biaxial-first, and Duda's pre-flight answers in hand instead of guessed. A fresh ID keeps the Duda-facing surface clean: **everything he needs to review carries `m5_12_`**; the `m5_11_*` corpus stays frozen as the validated evidence behind the closed task, not a pile he must sort through.

## What M5.11 banked (inherited, do NOT redo)

| Result | Where (frozen record) |
| --- | --- |
| Faber's electron reproduced: 511.00 keV at `r₀ = 2.2132 fm`, `I = π/4` to 6e-6, non-circular | `m5_11_p1_faber_electron.py` · [`m5_11b_findings.md`](m5_11b_findings.md) |
| `α⁻¹ → 137.03` from charge quantization (`charge² → 1.00003 e²`) | `m5_11_p1b_dipole.py` |
| Taichi reverse-mode AD gradient == the production functional (E 4e-16, grad 1.8e-13) | `m5_11_ad_energy.py` |
| Chiral Lifshitz + Frank terms built + validated (AD == numpy 1e-14) | `m5_11_p2_heliknoton.py` |
| **The 2×2 elimination map** (5 clean negatives): smooth knots expand, unknotted singular loops contract, painted melts heal; the one un-filled cell = a forced-singular knotted/linked disclination line | [`m5_11b_findings.md`](m5_11b_findings.md) § the full map |
| The PMNS N-ladder honest scorecard: 1 imposed μ-τ symmetry + θ₁₂ pinned-not-selected + θ₁₃ free coupling (`g_chiral* ≈ 0.94`) + CP sign open; masses ~6× compressed; loops not stationary (the foundational gap) | [`m5_10e_findings_N4c.md`](m5_10e_findings_N4c.md) |

## The standing hypothesis (why this task should succeed where M5.11 P2 could not)

All five M5.11 P2 loop experiments ran at the placeholder `δ = 0.3`, where the spatial tensor `diag(1, 0.3, 0)` is **strongly biaxial**; run 3's obstruction was precisely biaxiality (the chiral term drives a blue-phase texture, the Tai/Smalyukh thesis's flagged hard case, p.132). Duda's sketch ([`m5_4f_convo_2026.07.01.md`](m5_4f_convo_2026.07.01.md) § 2) states the neutrino is a **uniaxial** nematic field with **1 distinguished axis** (two vortex types), and at the physical `δ ~ 1e-10` the substrate's spatial spectrum degenerates to quasi-uniaxial `(1, 0, 0)`, exactly the regime where Smalyukh's chiral knots are known stable. **So the M5.11 negatives are regime artifacts until re-tested; only negatives at the physical regime count as verdicts.** The cheap first probe is M5.16 **P-G** (the δ-continuation study, [`m5_16_task_details.md`](m5_16_task_details.md)).

## Entry gates (both must be green before "go M5.12")

| Gate | Delivers |
| --- | --- |
| **M5.16** (the parameter-lock task) | ✅ DELIVERED 2026-07-02: locked `c₂ = αħc/64π` + `(a,b,c)` per β + the calibrated axisymmetric minimizer ([`m5_16_task_details.md § FINDINGS`](m5_16_task_details.md)); P-G read: all four obstruction indicators relax monotonically toward uniaxial (supportive, not sufficient alone) |
| **The pre-flight ask round** (one email to Duda, backed by the M5.16 deliverable) | SENT 2026-07-02; the 2026-07-03 reply audited the methods instead of answering (only Q16 partial: § Ask-round outcome below). The gate is now **[M5.17](m5_17_task_details.md)**: methods note + two-charge Coulomb + the re-ask email; question registry + details: [`../m5_question_tracker.md`](../m5_question_tracker.md) § OPEN QUESTIONS |

## The pre-flight ask round (entry gate 2: the ONE email)

Strategy (Rodrigo, 2026-07-02, recorded in [`m5_16_task_details.md § Comms plan`](m5_16_task_details.md)): deliver first, ask second. The M5.16 deliverable report ([`../findings/m5_16_report.md`](../findings/m5_16_report.md)) leads the email; the five asks follow. ONE email, never a drip; do not ask what we can measure ourselves (Q7/Q8 were delivered, not asked; these five are theory-intent or design-choice questions the minimizer cannot decide). Question registry + full per-question detail: [`../m5_question_tracker.md`](../m5_question_tracker.md).

The ask table (row order = priority; answers feed the phase named in the last column):

| ID | Ask | Why it is critical | Feeds |
| --- | --- | --- | --- |
| **Q13** | Does the M5 LdG substrate carry a chiral (Lifshitz) invariant `2q₀L ε_ikl M_ij ∂_k M_lj` + Frank partner, or is uniform-vacuum achirality intended? Framing: the δ_CP fork (180° pure-SO(3) vs 270° chiral; NuFIT ~212° between) is what this answer decides in-model | Three sectors converge on the ONE term: the CP phase (achiral LdG gives none), θ₁₃ (`g_chiral ≈ 0.94` free until microscopic), loop stabilization (the heliknoton route = Frank + chiral). A "no" reshapes phases A-C and kills the chiral CP story before we build | phases A, C, F |
| **Q16** | The neutrino seed topology: Hopf-linked `+1/2` disclination pair, `+1/2` trefoil, or the `4f` sketch's "two vortex types" composite? | The seed choice is the first line of phase A/C code; the wrong topology class wastes the heaviest compute of the program | phases A, C |
| **Q14** | Hedgehog core, point vs ring: M5.16 measured the spherical hedgehog to be a saddle of the unconstrained functional (perturbed relax −35%, melt moves off-origin). Symmetric hedgehog intended (held by what: Frank term? sixth-order LdG? clock dressing?), or is the ring-core texture acceptable? | Decides whether the calibration's spherically-constrained class is the model's intent; couples to Q13 (the same Frank+chiral pair is the natural point-stabilizer) | phase D + the electron ground state |
| **Q15** | δ-pinning: the quartic trace-LdG cannot be stationary at `(1, δ, 0)` (residual force `3bδ`). Sixth-order invariant intended, or is δ dynamical (his 2026-06-09 remark)? | Decides the vacuum structure the program minimizes toward; `κ_δ = (3/2)b` is the handle either way | the potential every phase minimizes |
| **Q17** | β and g anchor preference: β = b/c un-pinned by the electron sector (`κ_δ = (3/2)b` is its meaning); statics measured g-blind, so g comes from clock/boost or baryon mass. Which anchors first? | Closes the two open slots of the M5.16 lock table | phase E + `#220` |

Not in the email: the δ_CP fork is one framing paragraph under Q13 (not a standalone ask); Q4/Q9/Q10/Q12 are background (later rounds); Q11 is Close's thread.

### Ask-round outcome (2026-07-03) + the spec updates his reply carried

The email went out 2026-07-02; Duda's 2026-07-03 reply audited the report's methods instead of answering (he could not find the potential / Hamiltonian in the code; full exchange + decoding: [`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md)). The re-ask rides the [M5.17](m5_17_task_details.md) methods note. Per-question state:

| ID | State after 2026-07-03 |
| --- | --- |
| Q13 | unanswered, re-ask with the methods note |
| Q16 | 🔶 PARTIAL ANSWER, banked: "topological vortex rotated cylindrically to make it loop" = build the **single rotated vortex loop first** (phase A/C seed order settled); linked-pair vs trefoil discrimination stays open |
| Q14 | unanswered; his Fig. 9 (arXiv:2108.07896) ansatz reference sharpens what "the symmetric hedgehog" means (the M5.17 conformance check feeds this) |
| Q15 | unanswered; his "search for parameters" framing keeps it live |
| Q17 | weak signal: clock frequency is explicitly on his electron checklist (points at the clock/boost g-anchor path); no direct answer |

Design-note spec updates from the same reply (logged here per the rigor rule, before any build):

| Spec (Duda 2026-07-03, verbatim source in [`m5_4h`](m5_4h_convo_2026.07.03.md)) | Lands in |
| --- | --- |
| Neutrino starting point = "topological vortex rotated cylindrically to make it loop" | phase A/C seed (first object to build) |
| "minimization should give preferred time derivatives defining PMNS matrix to compare with" | phase F observable: PMNS from the TIME DERIVATIVES of the minimized loop, not from static overlaps alone |
| Electron bar = mass + "clock frequency, angular momentum and magnetic dipole" | phase D (clock + stability) picks up the 3 dynamical observables; EID-B/EID-C heritage = the starting points |
| Coulomb anchor = two charges at varying distance (large d anchor, fm-scale running coupling) | consumed by M5.17 phase C; this task inherits whatever the cross-check does to the `c₂` lock |

### 2026-07-04 spec updates (the group energy-conservation threads, [`m5_4i_convo_2026.07.04.md`](m5_4i_convo_2026.07.04.md))

| Spec | Lands in |
| --- | --- |
| **The energy-conserving oscillation gate** (Duda's now-PUBLIC mechanism: mass = energy density per length; the loop conserves total energy by changing length while rotating among the 3 axes): pre-register the constraint `E = λ_axis(i) · L_i = const` → length ratios `L_i ∝ 1/λ_i`; the relaxed oscillation must trace that trajectory with `E(t)` conserved | phase E (the mass/length-density map is now THE primary candidate, not one of two) + phase F (the `E(t)` gate along the SO(3) rotation) |
| **The 6.2 pm lab anchor** (Nature s41586-024-08479-6, neutrino wavepacket spatial extent; treat as a lower limit ≥ 6.2 pm) | phase E absolute-scale target; candidate closer of the β lock slot via `κ_δ = (3/2)b` (Q17) |
| **Faber's acceptance spec** ("must NOT be stable solitons, but must oscillate between three stable states"; replicate the SM mechanism: 3 eigen-configurations propagating independently, the flavor state = their oscillating mixture) | phases D/F acceptance criteria: the 3 axis-aligned loops = stable eigen-configurations; the produced flavor object = a rotating superposition; each eigenstate stationary, the mixture oscillating |
| **Urgency note**: Duda publicly cites "AI-written simulations" as confirming the mechanism, but the validated record is one step behind (M5.11 loops not stationary; PMNS numbers placeholder-δ era; the length-varying trajectory never simulated) | the physical-regime run + provenance-labelled scorecard protect the claim he has already made in public; schedule weight accordingly |

## Rigor compliance (inherited bar + M5.12-specific)

The full Duda-requirement table, item by item with verbatim sources, is [`m5_16_task_details.md § Rigor compliance`](m5_16_task_details.md): it applies to this task verbatim (energy minimization, cylindrical symmetry where applicable, center regularization, physical-regime parameters, independent benchmarks, article-standard documentation). M5.12-specific additions:

| M5.12 rule | Content |
| --- | --- |
| Physical-regime headlines only | every REPORTED number at the locked `(g, δ, a, b, c)` from M5.16; placeholder-parameter runs are labelled scaffolding, never headlines (the M5.11 lesson: only physical-regime negatives are verdicts) |
| Pre-registered gates per phase | each phase A-F carries its gate in the phased-plan table BEFORE the run (the M5.16 G1-G8/R1-R5 pattern); no post-hoc success criteria |
| Calibrated instrument only | the minimizer + potential come from M5.16 unmodified; any change to the functional re-runs the M5.16 gate suite first |
| Ask-round answers logged | Duda's Q13/Q16/Q14/Q15/Q17 answers land in [`../m5_question_tracker.md`](../m5_question_tracker.md) § QUESTION DETAILS (per ID) AND in this file's phase-A/C design notes before any build |
| Honest scorecard discipline | phase F reports the 4 PMNS parameters provenance-labelled (derived / consequence / fit), the N4c pattern; negatives and the mass-compression tension reported as falsifiers, not buried |
| Multi-agent verification (Duda 2026-07-03b: "careful small steps, maybe multiple agents verifying each other") | every headline number cross-checked by an independent path (two minimizers, analytic-vs-FD, the M5.16/17 pattern) AND the phase-F scorecard + any outbound method note audited by an independent second agent before sending ([`m5_4h_convo_2026.07.03.md § 6`](m5_4h_convo_2026.07.03.md)) |

## The phased plan

Phases lettered A-F (distinct from M5.11's P0-P6 so the two records never blur). The old P5 (parameter search) is gone: M5.16 owns it.

| Phase | What | Gate |
| --- | --- | --- |
| **A / uniaxial heliknoton (the primary route, was fork B)** | reduce to the unit director `n` with Frank `K\|∇n\|²` + chiral `2q₀ n·(∇×n)`; seed the elementary heliknoton (Ackerman-Smalyukh / Tai thesis Fig 6.5) in a helical background; relax at the physical parameters | a stable localized knot (`\|δF/δn\| → 0`, finite size, Hopf index intact), reproducing the KNOWN uniaxial result first |
| **B / map back to the M5 tensor** | walk δ up from the uniaxial limit (the P-G continuation in reverse) and embed the stable knot in the biaxial `M`; find where/whether biaxiality breaks it | the stable object survives at `δ ~ 1e-10` in the full tensor, or the breaking δ is measured (a real number, either way) |
| **C / biaxial-native backup (was fork A)** | only if A/B fail or Duda's answers redirect: the forced-singular knotted/linked disclination line from a literature single-valued ansatz (Machon & Alexander PNAS 2013; Alexander et al. RMP 2012) | a forced-singular knotted loop holds finite size under the calibrated functional |
| **D / stability + the clock** (was M5.11 P3) | Hessian / real-time evolution over many periods; add the M5.8 clock dressing; the SO(3) 3-axis oscillation on the loop (Duda's SO(2)-vs-SO(3) slide, `4e § 3`) | no collapse mode; the clock lowers energy; ω measured |
| **E / masses** (was P4 + the deferred N6) | mass = regularized loop energy; test Duda's **mass/length density** map + the **knot-family spread** (linked pair vs trefoil vs "two vortex types") against the ~6× splitting compression (N4c-2) | `Δm²` hierarchy honest pass/fail; if no map spreads the spectrum, the compression is reported as the falsifier |
| **F / mixing on real loops** (was P6) | recompute PMNS on the RELAXED stable loops; close the N4c gaps: θ₁₂ energy-selection re-test (`dE/dα = 0` at the magic tilt?), the Gram-bridge vs a true second-variation Hessian, `g_chiral` derived not fitted (per the Q13 answer), and the **δ_CP fork decision** (180° pure-SO(3) vs 270° chiral; tracker § δ_CP fork) | the 4 PMNS parameters from solutions of the field equations, vs NuFIT 6.0, provenance-labelled (derived / consequence / fit) |

### Phase F detail: the N4c gap-closure map

| N4c gap ([`m5_10e_findings_N4c.md`](m5_10e_findings_N4c.md)) | Phase F test on real loops |
| --- | --- |
| Q8 loop stability (foundational: overlaps computed on NON-solutions) | resolved by construction (the loops are stationary solutions) |
| Q4 θ₁₂ not energy-selected (`E_self` flat to 0.09%) | re-test `dE/dα = 0` at the magic tilt with the real potential + stable loops |
| Q7 the `U = eigvecs` Gram-bridge postulate | recompute the overlap matrix on solutions; test against a true second-variation Hessian (now well-defined) |
| Q1/Q2 chiral origin of θ₁₃ + CP | if the substrate carries a chiral invariant (per the Q13 answer), derive `g_chiral` microscopically instead of fitting 0.94 |
| the δ_CP fork (180° pure-SO(3) vs 270° chiral μ-τ reflection; NuFIT ~212 ± 30 sits between) | the real-loop mixing decides it in-model; DUNE/HK decide it in nature (tracker § δ_CP fork) |

### Phase E detail: the mass-compression tension

The N4c-2 flag stands as phase E's target: the M5.11 loop spectrum `1 : 1.15 : 1.68` gives splitting ratios ~5-7× below the observed `Δm²₃₁/Δm²₂₁ ≈ 33.6` under both natural eigenvalue→mass maps. Resolution candidates, testable once a stable loop family exists: Duda's **mass/length density** map (oscillation = the loop changing length, his round-3 email), plus a **knot-family spread** (Hopf-linked pair vs trefoil vs the sketch's "two vortex types" as distinct flavour carriers). If neither spreads the spectrum, the compression is reported as the falsifier.

## Script reuse manifest (fork-on-use, at "go M5.12")

Copies, never moves: the `m5_11_*` originals stay frozen as the closed task's evidence. Fork only what a phase actually uses, when it uses it.

| Source (frozen M5.11 record) | Fork target | Used by |
| --- | --- | --- |
| `m5_11_ad_energy.py` (Taichi-AD gradient engine) | `m5_12_ad_energy.py` | A-D (the gradient engine for every relaxation) |
| `m5_11_p2_heliknoton.py` (functional + chiral/Frank terms + seeds + diagnostics: `melt_diag`, `director_ring_R`, Hopf index) | `m5_12_heliknoton.py` | A, B, C |
| `m5_11_p2_vortex_loop.py` (loop seeder + dissolve-vs-stabilize diagnostic) | `m5_12_loop_diag.py` | B, C |
| `m5_11_n4c_*` mixing pipeline (overlap matrix → angles, scorecard) | `m5_12_mixing.py` | F (re-grounded on real loops) |
| `m5_11_p0_minimizer.py` + `m5_11_n1_precision_method.py` | no fork: consumed via **M5.16**, which hands back the calibrated instrument | A-F inputs |
| NEW: the uniaxial director-field reduction (3-component `n`, Frank + chiral, its own relaxer) | `m5_12_uniaxial.py` | A (new code, no M5.11 ancestor) |

## Definition of done

A **stable, regularized neutrino loop at the physical `(g, δ, V)` regime** (or the honest physical-regime negative, which, unlike the M5.11 placeholders, IS a verdict on the model), then the clock, masses, and mixing computed **on that solution**, documented to article standard. The stake is Duda's own framing (round 3, [`m5_10a_neutrino_oscillations.md`](m5_10a_neutrino_oscillations.md)): a rigorous derivation of the 4 PMNS parameters "able to pass peer review ... would already be huge". Rigor bar: § Rigor compliance above (the inherited M5.16 table + the M5.12-specific rows).

## Cross-links

- Predecessor (closed): [`m5_11_task_details.md`](m5_11_task_details.md) · frozen findings [`m5_11b_findings.md`](m5_11b_findings.md) · resume-state archive [`../findings/SESSION_STATE.md`](../findings/SESSION_STATE.md)
- Gate task: [`m5_16_task_details.md`](m5_16_task_details.md) (parameter lock + P-G + rigor bar + comms plan)
- Ask round: § The pre-flight ask round (above, the queue lives here) · question registry [`../m5_question_tracker.md`](../m5_question_tracker.md) § OPEN QUESTIONS + § QUESTION DETAILS · § δ_CP fork (tracker)
- Theory inputs: [`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md) (serious-sims bar, SO(2)/SO(3) slide) · [`m5_4f_convo_2026.07.01.md`](m5_4f_convo_2026.07.01.md) (uniaxial-neutrino sketch) · [`m5_4g_convo_2026.07.02.md`](m5_4g_convo_2026.07.02.md) (Golubich lattice recipe) · [`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md) (audit reply: vortex-loop-first, PMNS from time derivatives, 4-observable bar) · [`m5_4i_convo_2026.07.04.md`](m5_4i_convo_2026.07.04.md) (energy-conservation mechanism, 6.2 pm anchor, Faber acceptance spec)
- Honest-scorecard baseline the F phase must beat: [`m5_10e_findings_N4c.md`](m5_10e_findings_N4c.md)
