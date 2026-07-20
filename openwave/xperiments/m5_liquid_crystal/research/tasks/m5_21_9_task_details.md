# M5.21.9: the fixed-J + Larmor acceptance run (fork (c), EXPANDED)

**Status**: 🔶 IN PROGRESS, **GO 2026-07-20 11:22 EDT** (reset 12:50pm, resume ping armed at 12:55pm). Gate record: the fork-answer half of the original gate was **WAIVED by the user 2026-07-20** ("not fundamental, even if we need to rework afterwards"): the run uses only author-sanctioned choices (the "maybe enforced if numerical problems remain" fixed-J allowance + the author's own Larmor protocol, both 2026-07-19 05:09), the author's 14:53 partial reply was verified same-day ([`../findings/m5_21_9_negdelta_note.md`](../findings/m5_21_9_negdelta_note.md), audit 7/8 + 1 nuance), and rework is accepted if the pending "morning" study redirects. Roadmap: [`m5_roadmap.md § IN PROGRESS`](../m5_roadmap.md).

## TASK PLANNING

**Scope (expanded at go, user 2026-07-20)**: the original stub scope (fixed-J state + Larmor + clock re-read + film + Q33 rung) plus two phases from the negative-δ verify pass: the δ < 0 lattice rung and the core-profile sensitivity read.

| Phase | Content | Instrument | Machine-checkable gate (try cap 3) |
| --- | --- | --- | --- |
| P0 the δ < 0 lattice rung | The dressed family at δ = −0.3 (and −0.05 spot check) on the certified 4D stack: E(m) landscape, kin(m) sign, FIRE relax survival | `m5_21_8_b_lattice.py` machinery, dl parameter flipped | E(m) interior minima found; relax survival verdict (the +δ family was lattice-singular: does the bounded family relax?) |
| P1 core-profile sensitivity | The one author-gated choice left (fork (a)'s radius dependence): smooth the vortex-axis core with 2-3 different profiles, measure whether m\*, kin, and E respond | Same stack, profile-blended ansatz | The reads agree across profiles to a stated tolerance, or the profile-dependence is quantified |
| P2 the fixed-J state + hold read | Build the isorotating electron with constraint-carried J (ω\* = J/(2·kin), kin measured per state), evolve on the canonical integrator, measure the HOLD: energy bounded, core intact, topology preserved vs the ω = 0 control | The M5.21.3 4D stack + canonical integrator | The state survives the window with bounded ledger, or the honest failure mode is characterized |
| P3 the Larmor acceptance | The author's protocol verbatim: "introduce constant external magnetic field by constant field derivative in its direction, and temporal field derivative - should lead to electron precession with frequency proportional to magnetic field strength": weak-field ladder, precession frequency vs B, linearity + the ħ/2-consistency read | P2 state + a weak applied-field term | Precession measured at ≥ 3 field strengths; linear fit quality reported; the gyromagnetic read stated with its honest error |
| P4 the clock re-read + close | The verified-L de Broglie clock re-read on the converged state; the Q33 rung report (g-ladder behavior of the fixed-J state if time allows); the containment film ONLY if the state holds (physics-first: films stay small, matplotlib) | Existing verified-L instruments | Clock read done or explicitly deferred with reason |

**Definition of done**: the fixed-J state's hold verdict + the Larmor linear-response read (or the honest characterization of why either fails), documented method-note grade with adversarial audit before anything author-facing.

**Blindspot pass (unfamiliar territory)**: (a) the Larmor instrument is NEW (what exactly is "constant field derivative" in the M-field language: the author's F_μν decomposition tags EM = tilt-tilt R¹ + g²Γ̃¹, so the applied field must enter through that block; design decision logged when made, flagged as ours); (b) constraint-carried evolution vs constraint-carried minimization are different reads (hold = evolution; build = minimization at fixed J); (c) the δ < 0 family's vacuum branch on the lattice (which s-branch matches δ < 0) needs a pre-check, not an assumption.

**Unknowns routing**: machine-checkable → the phase gates above; author-gated → the core profile (P1 measures sensitivity instead of guessing the author's choice) + the Larmor field-normalization convention (flagged in the note); nature-gated → none at toy parameters.

**Research-body destinations**: scripts `research/scripts/m5_21_9_c_*.py` onward (a/b taken by the pre-gate pass), data `research/data/m5_21_9_*`, plots `research/plots/m5_21_9_*`, findings note `research/findings/m5_21_9_note.md` (the pre-gate negative-δ note stays separate), checkpoints `research/checkpoints/m5_21_9_progress.md`.

**Q35 mini-pass**: the constraint-carried-stabilization literature arm (Q-balls / spinning Skyrmions / isorotation) rides into the results note as the theory backbone; the full read is [M5.21.12](m5_21_12_task_details.md).

## RESULTS (2026-07-20 run; canonical record = the method note)

The full findings, verdict tables, equations, and audit live in [`../findings/m5_21_9_note.md`](../findings/m5_21_9_note.md). One-table summary:

| Phase | Verdict |
| --- | --- |
| P0 δ < 0 lattice rung | ✅ statics verify (twin minima \|m\| ≈ 0.15 = the audited analytic 0.1508; pinning exact; kin > 0 at minima) with the ⚠️ sub-vacuum flag E_u(m\*) = −6.5; ❌ free FIRE descent still dies (boost channel) |
| P1 profile sensitivity | ✅ closed NEGATIVE: profiled core dies identically → fork (a)'s core-profile choice is moot for lattice relaxability |
| P2 the fixed-J electron | ✅ EXISTS + HOLDS at three J rungs on the certified state (rel_move ≤ 1.3e-4, core intact, textbook kin-dressing response) |
| P4 clock thermodynamics | ✅ dE/dJ = ω\* closes at 0.996 / 0.989: the constraint-carried clock is an exact thermodynamic family |
| P3 Larmor | 🔶 instrument CERTIFIED (E-conservation 2.2e-8, dt-margin 4× post-audit; accelerating floor characterized; saturation mapped; ±B protocol working). The LINEAR (Larmor) read is UNRESOLVED this round: the audit downgraded the antisymmetric split to an artifact-scale upper bound (trajectory-divergence time signature) while its own static-texture discriminator EXCLUDED the simplest non-Larmor alternative. Bonus finding promoted by the audit: a clean QUADRATIC (ε²) field-induced drift slowdown resolved across the ladder. Next discriminators designed: the J-flip run + the modeled-floor ± ladder (native on [M5.26](m5_26_task_details.md)) |
| Q35 backbone | ✅ 8/8 verified citations: fixed-J is the standard rotating-soliton construction (Coleman → Radu-Volkov); Ostrogradsky language for the runaway; positive-energy theorems for the indefinite-density anchor |

Deviations from plan (logged live in [`../checkpoints/m5_21_9_progress.md`](../checkpoints/m5_21_9_progress.md)): (1) P2 re-arena'd from the dressed family to the certified M5.21.3 endpoint after the P0b collapse read; (2) P1 re-scoped to the moot-demonstration after the same read; (3) the Larmor raw background saturated → the enveloped (localized) field variant was designed and used; (4) the ω = 0.2 rung rerun at full depth after a stop-string bug (disclosed in the note § 5); (5) the ±ε replica turned into a determinism control after catching that B ∝ ε² (the true mirror is the commutator-reversed background).

**Datasets (local, gitignored, manifest regenerated)**: 5 npz endpoints (`fixedj_om{0.2,0.5,1}_end.npz`, `lat_relax_dl-0.3_*_end.npz`, ~0.9-1.1 MB each). Regen: `python3 m5_21_9_d_fixedj.py om=<v> maxit=1200 refresh=300` (~6 min each) and `python3 m5_21_9_c_lattice.py relax dl=-0.3 m=-0.150 [prof=tanh rc=3.0]` (~2 min); tracked JSON + plots carry the analysis.

## Scope (stub level)

| Piece | Content | Notes |
| --- | --- | --- |
| The state | Build the FIXED-J isorotation electron on the certified stack: constraint-carried J with ω\* = J/2kin, using the measured clock inertia (kin ≈ 0.119 undressed, [M5.21.3](m5_21_3_task_details.md); kin = +75.5 boost-dressed, [M5.21.8](m5_21_8_task_details.md)) | The TWO-STACK CONSENSUS route: no free-minimization clock exists anywhere (our descent + the author's own analytics) |
| The acceptance test | The author's Larmor protocol (spelled out 2026-07-19) as the spin observable: precession under a weak applied field, the ħ/2-consistency read | Acceptance = the author's own protocol, not ours; the sharp go/no-go on the spin credential |
| The clock re-read | The verified-L de Broglie-clock re-read on the converged fixed-J state (the coverage-table item parked since M5.21.1 P3) | Closes the clock row's verified-L gap if it lands |
| The film | "The particle clock creating particle stability": the containment film staged since the M5.21 findings, made only if the state holds | Both film templates per series rules ([`m5_visualization.md`](../m5_visualization.md)) |
| The Q33 rung | Report what the run adds to the realistic-parameter bridge (the g-ladder behavior of the fixed-J state) | Standing [Q33](../m5_question_tracker.md#q33-detail) duty |

**Feeds**: [M5.21.5](m5_21_5_task_details.md) (the μ + g-factor closure prefers this state) and the [M5.21.10](m5_21_10_task_details.md) decay-grade extension.

**Gated by**: the author's fork answer (recommendation (c), sent 2026-07-19) + user "go".

## Pre-gate verify (2026-07-20): the negative-delta suggestion

The author's partial reply (2026-07-19 14:53, [`m5_21_convo.md`](m5_21_convo.md)) conceded the omega verdict, did NOT pick a fork ("Will study further in the morning"), and offered new analytics: maybe δ should be NEGATIVE (the minus-infinity Minimize region "could be for (g > 1 && δ ≤ 0)"). Verified same-day per the M5.21.8 verify-first pattern: [`../findings/m5_21_9_negdelta_note.md`](../findings/m5_21_9_negdelta_note.md).

| Outcome | Consequence for this task |
| --- | --- |
| CONFIRMED, stronger than stated: at δ < 0, g > 1 BOTH runaway channels flip to bounded (the omega² coefficient factors as 8δ³[(g−1)δ − 2g]/(g−1), positive on the whole half-plane incl. (1e10, −1e-10); the cone term becomes positive core mass) | A δ < 0 rung joins the run matrix when this task goes: the fixed-J state should be built (or at least probed) on the bounded-family side too |
| REFUTED half: the free minimum stays STATIC (omega\* = 0 by exact linearity in omega²); no free de Broglie clock at either sign of δ | The task's premise is UNCHANGED: constraint-carried omega (fixed-J) + the author's Larmor protocol remains the only live route to the clock credential |
| Nuance: "shifting spectrum" is broken by the boost dressing at toy m (N7) | Carry into the next outbound as the qualification on the author's parenthetical |
