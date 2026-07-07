# M5.12: Neutrino vortex-loop at the physical regime (the fresh re-entry)

> Task **M5.12** (M5 / Liquid-Crystal model). Status: **Backlog, READY (all gates green)** · Gated by: ~~M5.16~~ ✅ (delivered 2026-07-02) + ~~M5.17~~ ✅ (delivered 2026-07-04) + ~~M5.18~~ ✅ (delivered 2026-07-05; this task runs on the verified 4D Lagrangian + the spectral potential) + ~~the pre-flight ask round~~ ✅ **CLOSED 2026-07-06** (Duda's two group-cc replies: Q13 redirect + Q14 core prescription + the negative-H intent; § 2026-07-06 spec updates below, full decode [`m5_18_convo.md`](m5_18_convo.md)) · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

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

### 2026-07-05 spec updates (Duda's reply to the M5.17 method note, [`m5_17_convo.md`](m5_17_convo.md))

He confirmed the static 3D functional verbatim (audit PASS; the M5.16 lock now sits on an owner-signed-off energy, no retroactive change to any static number) and issued two 4D specs that are PRE-CONDITIONS for phase D (clock dynamics) and any later gravity-sector work:

| Spec (Duda 2026-07-05, verbatim source in [`m5_17_convo`](m5_17_convo.md)) | Lands in |
| --- | --- |
| **4D potential minimum `(g, 1, δ, 0)`**: "For 4D, required to add clock and gravity, potential needs to have minimum (g,1,delta,0)" | phase D pre-condition: extend V from `M_sp` to the full 4×4 M with enough independent invariants to pin 4 distinct eigenvalues (generically Tr M through Tr M⁴); the p.11 anchor hints (`g⁴ ~ 1e38`, `δ² ~ ħc`) become coefficient constraints (Q17). Any functional change re-runs the M5.16 gate suite first (the calibrated-instrument rule above) |
| **Signature commutator in 4D**: "[A,B] = A xi B - B xi A for xi = diag(-1,1,1,1)" | phase D kernel: mandatory the moment time derivatives or time-mixing textures enter (the ψ clock). Static fields are ξ-blind (zero time block in every ∂M, verified in [`../scripts/m5_17_energy.py`](../scripts/m5_17_energy.py)), so this changes dynamics only |

His SECOND 2026-07-05 reply ([`m5_17_convo.md`](m5_17_convo.md) entry 2) then went further and created the gating task **[M5.18](m5_18_task_details.md)**; what this task inherits from it:

| Spec (Duda 2026-07-05b) | Lands in |
| --- | --- |
| **The universal spectral potential** `V(M) = Σ_p (Tr(M^p) − c_p)²`, `c_p = Σ_i Λ_i^p`, targets `(1,δ,0)` 3D / `(g,1,δ,0)` 4D: supersedes the quartic LdG; β = b/c dissolves | EVERY phase minimizes this potential once M5.18 phase B validates it (gate suite + recalibration); the phase-E `κ_δ = (3/2)b` anchor equation is retired with the LdG form |
| **The explicit 4D Lagrangian** `L = −Σ F_{μναβ}F^{μναβ} − V(M)`, η-raising everywhere, + his Hamiltonian via Legendre: verification delegated to the agent ("nobody else has checked it. Should be used if it is right") | phase D runs the clock on the VERIFIED Lagrangian/Hamiltonian only. ✅ M5.18 DELIVERED 2026-07-05: both claims verified; phase D MUST handle the three qualifications ([`../findings/m5_18_verification_note.md`](../findings/m5_18_verification_note.md)): degenerate Legendre map (constrained evolution), covariant vacuum `diag(−g,1,δ,0)`, and the INDEFINITE boost-texture sector (negative-energy channel on the vacuum manifold: evolution can fall into it; owner-intent question out in the reply email). `r_half` potential-shape robustness (0.3%) means the calibrated instrument behaves identically under the swap |
| "can use delta=0 for uniaxial approximation without QM" | phase A/B seeds: the uniaxial construction is the honest δ=0 approximation; the δ≠0 (QM) sector needs the exact `(1,δ,0)` pin the new potential provides |
| **Faber running-coupling benchmark** (2026-07-05 public group post, [`m5_17_convo.md`](m5_17_convo.md) entry 3: he cited Universe 11/4/113 + arXiv 2604.12021 as the reference bar and reposted our `m5_17_two_charge.png`) | any running-coupling or fm-scale interaction claim this task makes (phase E scale work, phase F observables) is benchmarked against Faber's curves EXPLICITLY, overlay not asymptote-only; the group-public standing of the M5.17 readout raises the provenance-label bar |

### 2026-07-06 spec updates (Duda's two replies to the M5.18 email: THE ASK ROUND CLOSES)

His 2026-07-06 replies (now group-cc'd to models-of-particles; full decode + verbatim: [`m5_18_convo.md`](m5_18_convo.md)) close the pre-flight ask round. Every remaining unknown is either answered, banked, or routed to a phase-D-only gate. The consequences reshape the phase plan:

| Spec (Duda 2026-07-06, verbatim source in [`m5_18_convo`](m5_18_convo.md)) | Lands in |
| --- | --- |
| **Q13 REDIRECT**: the LC chiral Lifshitz + Frank pair "might not translate here ... just focus on consequences of chosen LdGS Lagrangian - with different Lorentz-invariant Skyrme-like term and finally extended to 4x4 tensor" | **Phase A as planned (uniaxial heliknoton via Frank + chiral) is DEMOTED**: a heliknoton needs the cholesteric chiral term, which is now unsanctioned physics; keep it at most as a numerical scaffold, never a headline. The primary construction becomes the Q16-banked **single rotated vortex loop** under the sanctioned functional, with stabilizer candidates in priority order: (1) the Q14 core prescription (below), (2) a **Lorentz-invariant Skyrme-like term** (a MEASUREMENT: which term, what coefficient; the M5.8 N-5 invariant matrix already has a Skyrme candidate, "Skyrme damps"), (3) the clock dressing. Phase F: the δ_CP fork leans **180°** (no sanctioned chirality source); `g_chiral ≈ 0.94` reverts to a free-fit label unless a Skyrme-like source reproduces θ₁₃ |
| **Q14 ANSWERED as a CONSTRAINT**: "constraining centers in lattice points, replacing central value with 'M = a I' (3D), or in 4D (g', a,a,a) eigenspectrum"; static Coulomb centers fixed at lattice points, `(g', a)` optimized; "denser lattice, or some FEM" for small distances | **NEW phase D0 (first measurement of the task, cheap, runs before any loop build)**: re-run the M5.18 melt-channel pair (hedgehog perturbed relax + antipair) with pinned centers AND the replaced `aI` core value, optimizing `(g', a)`. The M5.18 runs pinned cores but did NOT replace the central value, so this is a genuinely untested prescription: if the channel closes, defect stability is solved by constraint and the loop core gets the same treatment; if not, the Skyrme-like-term measurement moves up. Either outcome is reportable to the group |
| **Negative-H channel INTENDED** (M5.18 back-question 3 answered): needed for "oscillations of resting electron/neutrinos, and boosts for gravitational mass"; instabilities handled by "the least action principle (for e.g. Big Bang - Big Crunch boundary conditions) ... not Euler-Lagrange" | **Phase D formulation directive**: the clock is the stationary point of the 4D action as a **time-periodic boundary-value problem** (relax the action with periodic time BCs), not open-ended time stepping; the negative boost-texture sector is the ENGINE (clock + gravitational mass), not a pathology to constrain away. Converges with resolved Q1 ("time-periodic resonance"). The Dirac constraint analysis (now Q18) is bookkeeping, not a blocker, under the BVP formulation |
| M5.18 back-questions 1-2 unanswered → tracker **Q18** (constraints) + **Q19** (vacuum branches; partial core signal: `(g', a, a, a)` at charge cores = spatially degenerate spectrum with a distinct timelike `g'`) | Phase D gates only; phases A-C (loop statics) are NOT gated by either |
| **Weak sector named**: weak = `SU(2)_LR ~ SO(3)` neutrino 3D rotations; strong = `SU(3)` baryon with twist; Yang-Mills from `∂_μ D` eigenspectrum deformation ("activation of potential") | Phase F framing: the SO(3) 3-axis oscillation run doubles as the model's weak-sector object, so the PMNS scorecard is also the first weak-force deliverable; label accordingly |
| Potential open-by-design ("worth to be open especially for modifications of potential, maybe also adding more kinetic terms e.g. like Skyrme people do") + deeper-level derivation direction (Q9) + SM-correspondence ladder (Dirac → QED → QCD; public issue #197 endorsed) | Instrument stance: the spectral potential is the working instrument, not dogma; any kinetic-term addition (Skyrme-like) re-runs the M5.16 gate suite first (the calibrated-instrument rule). The deeper-level and SM-ladder directions are post-M5.12 program, not this task |

**Phase-plan deltas in one line each** (the phased-plan table below is the 2026-07-05 state; read it with these deltas until the "go" re-plan folds them in):

| Phase | Delta |
| --- | --- |
| NEW **D0** | The core-prescription melt-channel re-run (pinned centers + `aI` / `(g', a, a, a)` core, optimize `(g', a)`): the FIRST measurement, before any loop build |
| A | Demoted from "theory-motivated primary" to optional scaffold (Q13 redirect); the primary seed = the rotated vortex loop (Q16) under the sanctioned functional + the D0-validated core treatment |
| B | Unchanged in spirit (δ-continuation into the biaxial tensor), but from the loop of the new phase A, not from a heliknoton |
| C | The forced-singular knotted/linked backup stays, now on equal footing with the Skyrme-like-term route if D0 + the plain loop both fail |
| D | Formulation = time-periodic action BVP (not IVP time stepping); ξ-commutator + 4D spectral potential as per the 2026-07-05 specs; Q18/Q19 tracked, non-blocking |
| E | Unchanged (mass/length density + 6.2 pm anchor + knot-family spread); `(g', a)` join the anchor bookkeeping (Q17) |
| F | δ_CP fork leans 180°; the run doubles as the weak-sector (SO(3)) deliverable; `g_chiral` labeled free-fit unless Skyrme-sourced |

## PRE-GO CONTEXT PACK (2026-07-07 full-corpus refresh)

A four-agent parallel re-read of the entire M5 corpus (M5.16/17/18 instrument docs + scripts, the M5.11 heritage + scripts, the six convo files 4e-4i + m5_17_convo, the N4c/PMNS findings), consolidated so this file alone carries what "go M5.12" needs. Sources are linked per card; when a number matters, trust the linked source over this digest.

### Card 1: the calibrated instrument (what every phase runs on)

Convention everywhere: `M = O·D·Oᵀ`, `D = diag(g, 1, δ, 0)`, time/g = index 0, `η = diag(−1,1,1,1)`.

| Locked item | Value | Status |
| --- | --- | --- |
| `c₂` (curvature) | `αħc/64π = 7.1618e-3 MeV·fm`, analytic, potential-independent | ✅ carries over to the spectral era |
| Potential of record | `V(M_sp) = w Σ_{p=1..3} (Tr(M_sp^p) − c_p)²`, `c_p = Σ_i Λ_i^p`; electron sector δ = 0 → `c_p = (1,1,1)`; δ ≠ 0 → `(1+δ, 1+δ², 1+δ³)` pins `(1, δ, 0)` EXACTLY (gate S3) | ✅ Duda 2026-07-05; equal weights, per-p weights = the flagged freedom |
| `w` fixing | seed virial balance `w = E_curv/(3·E_pot,w=1)` (Derrick length-scale choice); n96 value 7.2402e-4 | protocol, not physics |
| Scale anchor | `E[M] = m_e c²` at the minimum → `ℓ = c₂·E_sim/m_e` (~0.2494 fm/grid-unit at n96); invariant = `J_half = E_sim·r_half_sim` | ✅ |
| Headline banked | `r_half = 2.935 fm` h-converged (n64/96/128, virial 1.016/1.006/1.003, Richardson from (96,128)), −4.6% vs Faber 3.0754, +0.3% vs quartic LdG: potential-shape ROBUST | ✅ measured |
| δ | `1e-10` 🔶; never fed to floats: E(δ) evaluated as an exact polynomial (Vandermonde order extraction, the M5.16 trick); measured effect −1.5e-10 fractional | working value |
| g | `1e10` 🔶 (`g·δ = 1` hypothesis); statics EXACTLY g-blind (gate G8, rel 0.0); enters only via clock/boost + the 4D `c_p` targets | working value |
| Dynamic range | `g/δ ~ 1e20`: perturbative-δ / exact-polynomial grading / non-dimensionalization mandatory (the N1 graded-precision lesson: the θ13 channel recovered to 9.4e-16 where naive f64 returns 0) | standing rule |

Solver that produced every trusted number: exact equivariant axisymmetric (ρ,z) reduction (cell-centered ρ + mirror ghost, volume weight 2πρh²), central differences, ANALYTIC numpy adjoint gradients (Taichi-AD JIT never completed on this kernel shape, 28 min CPU twice: do not re-tread), mass-preconditioned FIRE cross-checked by CG Polak-Ribière + golden-section (the Golubich/Faber recipe, [`m5_4g_convo_2026.07.02.md`](m5_4g_convo_2026.07.02.md)), grids 96×192 production / 64-128 h-family, convergence = 6 gradient decades + monotone E + virial.

Gate suite (re-run ALL after ANY functional change, the calibrated-instrument rule): G2 gradient vs FD 3.6e-7 · G3 hedgehog density `r⁴d = 8` (0.17%) · G4 shell energy closed form (0.73%) · G5 3D lineage bit-identical · G6 2D==3D at h² (0.27% at h/2) · G7 frame invariance 6e-16 · G8 g-blindness EXACT · S1 spectral gradient 1.1e-9 · S2 spectral vacuum exact · S3 biaxial pinning exact. Code: `run_gates()` in [`../scripts/m5_18_spectral.py`](../scripts/m5_18_spectral.py) + [`../scripts/m5_16_axisym.py`](../scripts/m5_16_axisym.py); records `m5_18_spectral_gates.json`, `m5_16_axisym_gates.json`.

Module import-vs-fork: physics single-source = [`../scripts/m5_17_energy.py`](../scripts/m5_17_energy.py) (curvature, gradients, weights, tail, seeds; import, never re-implement); minimizers/basis = `m5_16_axisym.py`; the spectral trio (`potential_density_spec_np` / `dv_spec` / `energy_gradient_spec_np`) = [`../scripts/m5_18_spectral.py`](../scripts/m5_18_spectral.py); its composition pattern (curvature adjoints + new dV scattered into the spatial block) is the template for ANY further term (e.g. a Skyrme-like candidate).

### Card 2: phase D0 protocol (the first measurement, frozen design)

Re-run the M5.17/M5.18 melt-channel pair experiments with Duda's core prescription; everything else in the design is FROZEN (comparability): perturbed-hedgehog stability (3% Gaussian bump, unconstrained 2D FIRE, 8000 iters, n96×192) + antipair relax (`pair_field` tilt ansatz, d ∈ {16, 24}, 3000 iters, `w` from the calibrated hedgehog run). The ONE change: centers constrained to lattice points + the central value REPLACED by `M = aI` (3D) / `diag(g', a, a, a)` (4D reading), `(g', a)` optimized, instead of the melted `s(r)` core + 2.5h pinned disks. Decision criterion already wired in the JSONs: `melt_min` staying O(1) = channel CLOSED (defect stability solved by constraint; the loop core gets the same treatment); `melt_min → 0.008-class` = channel survives (the Skyrme-like-term measurement moves up). Either outcome is group-reportable. Baseline numbers to beat/compare: LdG antipair E → 0.30-0.59 vacuum residual, bridge `melt_min ≈ 0.008` at both d; spectral identical (0.345/0.409, 0.0076/0.0078); hedgehog escape 35% (LdG n64) / 55% shallow-melt `min_s 0.51` (spectral n96).

### Card 3: seeds + the M5.11 heritage (what exists, what to build, what not to repeat)

Existing seeders (all built for the 4×4 tensor, placeholder δ = 0.3 era): plain `+1/2` disclination ring (`seed_vortex_loop_M`, `m5_11_p2_vortex_loop.py`), smooth Hopfion (`hopf_director`), heliknoton (`heliknoton_director`), forced-melt singular `+1/2` loop (`disclination_loop_tensor`, mode `disc`), painted-melt Hopfion (mode `shopf`), all in [`../scripts/m5_11_p2_heliknoton.py`](../scripts/m5_11_p2_heliknoton.py) with diagnostics (`melt_diag`, `director_ring_R`, localization). The directive seed ("topological vortex rotated cylindrically to make it loop") has the ring seeders as ancestors but needs a NEW build with three changes: (a) **uniaxial** cross-section (the 4f sketch + "δ=0 = uniaxial approximation without QM"; winding class integer-vs-half = the Q16 residual, test both), (b) the **Q14 core prescription** (Card 2), not the tanh melt, (c) the **sanctioned functional** (Card 1), no chiral/Frank. The axisymmetric φ-winding machinery of `m5_11_p1b_dipole.py` (validated −0.024%) is the template for exploiting the loop's cylindrical symmetry.

The 5 M5.11 negatives (2×2: smooth/forced-singular × unknotted/knotted; ALL at δ = 0.3, so regime artifacts until re-tested; only physical-regime negatives are verdicts): plain ring dissolves (6% curvature retained) · smooth Hopfion expands (Derrick) · chiral heliknoton → blue-phase, no stable simple helix in the biaxial tensor (the Tai p.132 case) · forced-melt unknotted loop heals + dissolves, chiral does not help · painted melt heals by iter ~100 then expands. Lessons that survive the regime change: a melt must be topologically FORCED, not painted; an unknotted loop bounds a disk the director combs smooth; any "hold" verdict needs BOTH retention bounds AND a localization check (the run-5 blue-phase false positive, guard `curv_keep > 2.5`); the 4th-order curvature term VANISHES on 1D-varying textures, so any added gradient term needs its own boundedness check (the bare-chiral `E → nan` trap). Full map: [`m5_11b_findings.md`](m5_11b_findings.md).

Taichi-AD engine ([`../scripts/m5_11_ad_energy.py`](../scripts/m5_11_ad_energy.py), validated E 4e-16 / grad 1.8e-13): params via a `ti.field` not f64 args, loops-only kernel body, one differentiable loop per term, symmetrize the spatial gradient block, boundary re-pinned each step; ~6 min recompile per kernel edit (batch edits), f64 CPU. Use for 3D verification runs; the axisymmetric analytic-adjoint path (Card 1) is the production instrument.

### Card 4: the owner-spec ledger (standing gates, deduplicated; full ledger in the convo files)

| Standing spec | Source | Constrains |
| --- | --- | --- |
| Seed = single cylindrically-rotated vortex loop, uniaxial, cylindrical symmetry to reduce dimension | Duda 4f/4e/4h | phases A/B |
| Serious-sim bar: lattice/FEM energy minimization, "not seconds but weeks"; center regularization = the hardest part | Duda 4e | all |
| Electron deliverable bar = mass + clock frequency + angular momentum + magnetic dipole (4 observables, 3 dynamical) | Duda 4h | phase D |
| Faber acceptance: "must NOT be stable solitons, but must oscillate between three stable states"; 3 eigen-configs stable + flavor = rotating superposition | Faber 4i | phases D/F |
| Energy-conservation gate: `E = λ_axis(i)·L_i = const`, length ratios `L_i ∝ 1/λ_i`, `E(t)` conserved along the oscillation (his PUBLIC flagship claim, one step ahead of the validated record: reputationally urgent) | Duda 4i | phases E/F |
| PMNS from the preferred TIME DERIVATIVES of the minimized loop | Duda 4h | phase F |
| Size anchor: neutrino wavepacket ≥ 6.2 pm (Nature s41586-024-08479-6, lower limit) | Duda 4i | phase E |
| g anchor candidates: "maybe g can be obtained from electron clock, neutrino oscillations. Otherwise gravitational mass - certain only for baryons" (a g-value read is an M5.12 OUTPUT slot) | Duda 4e | phases D/E |
| Running-coupling benchmark = Faber's curves explicitly (Universe 11(4):113 + arXiv 2604.12021), overlay not asymptote-only | Duda 2026-07-05 public | any fm-scale claim |
| 4D: spectral potential target `(g,1,δ,0)`; ξ-commutator `[A,B] = AξB − BξA` once time derivatives enter; clock = time-periodic action BVP (least-action stance); negative boost-texture channel = the ENGINE, not a pathology | Duda m5_17 convo + [`m5_18_convo.md`](m5_18_convo.md) | phase D |
| Rigor: "careful small steps, maybe multiple agents verifying each other" (4h); "do less, but more rigorously" (round 2, [`m5_10a_neutrino_oscillations.md`](m5_10a_neutrino_oscillations.md), NOT in the convo files: cite 10a); method note + independent adversarial audit before any outbound; assume public reposting (the thread is group-cc'd, podcast-cc'd) | Duda 4h/10a/m5_17 | reporting |
| Reviewer roster: Faber bowed OUT of neutrinos (electron/EM/Coulomb reference only); Sulich (IF PAN) joined; Golubich sources (`MTF.tex` etc.) are local-only, never in public artifacts | 4i, 4g | reporting |

### Card 5: the phase-F baseline (the honest scorecard to beat, [`m5_10e_findings_N4c.md`](m5_10e_findings_N4c.md))

| Parameter | In-model | Provenance | NuFIT 6.0 NO | Pull |
| --- | --- | --- | --- | --- |
| θ₁₂ | 35.26° (trimaximal) | geometrically PINNED, not energy-selected (`E_self` flat to 0.09%) | 33.68 ± 0.70° | +2.3σ |
| θ₂₃ | 45.00° | CONSEQUENCE of the imposed μ-τ mirror | 43.3 ± 1.0° | +1.7σ |
| θ₁₃ | 8.56° | FREE coupling (`g_chiral* ≈ 0.94`, fit; post-Q13-redirect this label is final unless a Skyrme-like source reproduces it) | 8.56 ± 0.11° | 0 (by construction) |
| δ_CP | 270° (\|δ\| = 90, sign open) | consequence of μ-τ reflection; post-redirect the fork LEANS 180° (no sanctioned chirality source) | 212 ± 30° | consistent |

Gaps phase F must close on REAL relaxed loops: loops were NOT stationary (`dE/dL = +6.74`: overlaps of non-solutions, no well-defined Hessian: the foundational gap, resolved by construction if phases A-C deliver); the Gram-bridge `U = eigvecs(overlap)` is a postulate, test against a true second-variation Hessian; θ₁₂ energy-selection re-test (`dE/dα = 0` at the magic tilt?); μ-τ mirror is an INPUT (is there a deeper reason?); CP sign = loop handedness, undetermined. Mass-compression tension (phase E's target): loop eigenvalues `1 : 1.148 : 1.682` give Δm² ratios 5.8-7.3× too compressed vs the observed 33.6; candidate resolutions = the mass/length-density map (primary) + knot-family spread; if neither spreads it, the compression IS the reported falsifier. The deliverable bar (Duda round 3 verbatim, 10a): "first focus on the basic 4 parameters - if writing convincing article able to pass peer review, this already would be huge."

### Card 6: pre-registered gates per phase (no post-hoc success criteria)

| Phase | Pre-registered gate |
| --- | --- |
| D0 | `melt_min` O(1) after the core-prescription re-runs = channel CLOSED; `→ 0.008-class` = survives. Frozen designs of Card 2; both outcomes reportable |
| A | the rotated uniaxial loop is STATIONARY under the sanctioned functional + D0-validated core: `\|δE/δM\| → 0` (6 gradient decades), finite size (ring R off the box edge), retention AND localization both green (the run-5 double criterion), h-robust at two grids |
| B | the stable object survives δ-continuation to `δ ~ 1e-10` in the full tensor (exact-polynomial grading, never raw f64), or the breaking δ* is MEASURED (a number either way) |
| C (backup) | a forced-singular knotted/linked loop (Machon-Alexander / RMP 2012 parametrization, never improvised) holds finite size under the calibrated functional; triggered only if A/B fail and D0 did not close the channel |
| D | clock as a time-periodic action BVP (ω free, the Track C C3 + Duda least-action convergence); ξ-commutator on; 4D spectral potential `(g,1,δ,0)`; no collapse over many periods; the electron 4-observable bar (mass banked + clock ω + J + magnetic dipole) as the sibling calibration; any added Skyrme-like term re-runs the FULL gate suite first + carries the M5.8 N-5 caution (the measured Skyrme candidate SATURATES but DAMPS the clock 10×: measure, don't assume) + a 1D-texture boundedness check |
| E | mass = regularized loop energy; the `E = λ·L = const` trajectory traced with `E(t)` conserved; `L_i ∝ 1/λ_i` ratios; Δm² hierarchy vs 33.6 honest pass/fail; absolute scale vs the ≥ 6.2 pm anchor; the compression reported as falsifier if unresolved |
| F | the 4 PMNS parameters recomputed on stationary loops, provenance-labelled (derived / consequence / fit) vs NuFIT 6.0; PMNS also from the loop's preferred time derivatives (the owner-specified observable); θ₁₂ selection re-test; Gram vs Hessian; the δ_CP fork DECIDED in-model; the run doubles as the weak-sector (SO(3)) deliverable |

### Card 7: blindspot pass (the unknowns quadrant map, per `_AI_flow.md § Unknowns discipline`)

| Quadrant | Biggest known instance | Route |
| --- | --- | --- |
| Known knowns | the calibrated instrument + the closed ask round (Cards 1-5) | this pack |
| Known unknowns | does the core prescription close the melt channel? which winding class is the loop? does a Skyrme-like term help or damp? | machine-checkable: D0, A, D measurements |
| Unknown knowns | tacit acceptance criteria for "a stable loop" (how long, how converged, what counts as finite size) | pre-registered gates (Card 6) + user reacts to the first D0/A plots before phases E/F spend compute |
| Unknown unknowns | (a) the BVP formulation of the clock is NEW numerics (time-periodic boundary conditions on a 4D action: no reference implementation anywhere, his own words); (b) the negative-energy engine may interact with the minimizer (descent can fall into the intended negative channel and read as "instability"); (c) the 1e20 dynamic range in a LOOP geometry (the M5.16 tricks were derived for the hedgehog); (d) vacuum-branch mixing at the loop core (Q19: the `(g',a,a,a)` core sits in a different branch than the bulk) | deviations log at EXECUTE; adversarial audit on every headline; escalate mid-task if (b) or (d) produces sign-confusing energies |

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
| `m5_11_p1b_dipole.py` (axisymmetric φ-winding machinery, validated −0.024%) | template for the rotated-loop cylindrical reduction | A/B (added 2026-07-07 reality check) |
| `m5_11_p2_hopfion.py` (run-2 smooth-Hopfion control) | control re-run at the physical regime if needed | B (added 2026-07-07 reality check; all manifest files verified present on disk) |

## Definition of done

A **stable, regularized neutrino loop at the physical `(g, δ, V)` regime** (or the honest physical-regime negative, which, unlike the M5.11 placeholders, IS a verdict on the model), then the clock, masses, and mixing computed **on that solution**, documented to article standard. The stake is Duda's own framing (round 3, [`m5_10a_neutrino_oscillations.md`](m5_10a_neutrino_oscillations.md)): a rigorous derivation of the 4 PMNS parameters "able to pass peer review ... would already be huge". Rigor bar: § Rigor compliance above (the inherited M5.16 table + the M5.12-specific rows).

## Cross-links

- Predecessor (closed): [`m5_11_task_details.md`](m5_11_task_details.md) · frozen findings [`m5_11b_findings.md`](m5_11b_findings.md) · resume-state archive [`../findings/SESSION_STATE.md`](../findings/SESSION_STATE.md)
- Gate task: [`m5_16_task_details.md`](m5_16_task_details.md) (parameter lock + P-G + rigor bar + comms plan)
- Ask round: § The pre-flight ask round (above, the queue lives here) · question registry [`../m5_question_tracker.md`](../m5_question_tracker.md) § OPEN QUESTIONS + § QUESTION DETAILS · § δ_CP fork (tracker)
- Theory inputs: [`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md) (serious-sims bar, SO(2)/SO(3) slide) · [`m5_4f_convo_2026.07.01.md`](m5_4f_convo_2026.07.01.md) (uniaxial-neutrino sketch) · [`m5_4g_convo_2026.07.02.md`](m5_4g_convo_2026.07.02.md) (Golubich lattice recipe) · [`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md) (audit reply: vortex-loop-first, PMNS from time derivatives, 4-observable bar) · [`m5_4i_convo_2026.07.04.md`](m5_4i_convo_2026.07.04.md) (energy-conservation mechanism, 6.2 pm anchor, Faber acceptance spec) · [`m5_17_convo.md`](m5_17_convo.md) (universal potential + 4D Lagrangian + ξ-commutator) · [`m5_18_convo.md`](m5_18_convo.md) (ask round CLOSED: Q13 redirect, Q14 core prescription, negative-H intent, least-action BVP, weak-SO(3) slide)
- Honest-scorecard baseline the F phase must beat: [`m5_10e_findings_N4c.md`](m5_10e_findings_N4c.md)
