# M5.20 convo record (the program thread, continued: the spectrum directive)

Per-task convo record (technical exchange, no author-private content, so tracked in-repo per the convo-records rule). Outbound context: the M5.20 close message sent 2026-07-11 morning with the method-note link ([`../findings/m5_20_method_note.md`](../findings/m5_20_method_note.md)); tracker registry [`../m5_question_tracker.md`](../m5_question_tracker.md); predecessor exchange [`m5_19_convo.md`](m5_19_convo.md). Successor task planned from this entry: [M5.20.1](m5_20_1_task_details.md).

## 2026-07-11: Duda's replies to the M5.20 note: the (1, delta, 0) spectrum directive (spec for M5.20.1)

**From**: Jarek Duda, 2026-07-11, two replies to Rodrigo (12:59 and 14:27 EDT), 1:1 on the thread.

### Verbatim core (his 14:27 reply, after reading the note; the 12:59 first reaction asked "the vortex loop does not radiate, but still collapses? How is it happening?" and confirmed "The negative term is from Hamiltonian we have agreed to")

> I have just read the note, but still don't know what does it mean by "unwinds"?
>
> Topological vortex is topologically protected - to be destroyed would need to shorten to zero, what means energy difference - would need radiation mechanism, you say is not allowed.
>
> There is mentioned (1,0,0) spectrum, while topological vortex requires potential with (1, delta, 0) minimum - preferred three different, which should regularize to two equal in center - to prevent discontinuity of infinite energy, activating potential.
>
> So maybe there is problem with assumed simpler spectrum.
> Also clock propulsion with negative Hamiltonian terms require full 4x4 tensor field with (g, 1, delta, 0) spectrum.

### Decode + routing (per the unknowns discipline; evidence, not resolution, until measured)

| Item | Decode | Routing |
| --- | --- | --- |
| "does not radiate, but still collapses - how?" | A legibility gap on "unwinds", not an objection: his mental model is R → 0 shrinkage (needs energy export). The measured mechanism is local spectral deformation: the cross-section passes through two-equal-eigenvalue configurations until the winding is gone in place; PE converts to the localized remnant, nothing radiates | Answered in the same-day outbound (below); wording lesson for future notes: define "unwinds" up front |
| "(1,0,0) spectrum, while topological vortex requires (1, delta, 0) minimum - three different" | The load-bearing catch: at δ = 0 the two lower eigenvalues are ALREADY equal in vacuum, so the two-equal face is potential-free (M5.19 B2 measured "the two-equal core is nearly free"; the M5.20 vacuum Hessian's 4 zero modes include the 2 pair-splitting directions, gapped only at quartic order). His diagnosis names exactly the channel the unwinding used. At δ ≠ 0 the pair-splitting face gets an energy gap ("activating potential") and the vacuum manifold topology changes (π₁ = Q₈, no free escape) | Machine-checkable → **[M5.20.1](m5_20_1_task_details.md)** (the δ ≠ 0 rerun). Tracker [Q22](../m5_question_tracker.md#q22-detail) REOPENED: his "I don't know in this moment" (2026-07-10) is superseded by a structural directive (the vortex sector requires δ ≠ 0); the VALUE stays unknown |
| "maybe there is problem with assumed simpler spectrum" | Correct reading of M5.20's scope: the verdict is a statement about the δ = 0 theory (his electron-sector spec, run because Q22 was parked-unknown and disclosed in the note § 4). Not a computational bug: the audit stands; the theory he intends is different and now testable | The M5.20 record keeps its licensed close sentence unchanged (in-scope); M5.20.1 tests the intended theory |
| "clock propulsion ... require full 4x4 tensor field with (g, 1, delta, 0) spectrum" | Confirms the clock sector needs the time eigenvalue g in the potential AND the time/kinetic term (the negative `Γ·Γ̃` contributions, "from Hamiltonian we have agreed to" per his 12:59 line, i.e. the M5.18-verified 4D Lagrangian) | Tracker [Q23](../m5_question_tracker.md#q23-detail) rider added; the clock stays out of M5.20.1 scope unless the M-variable time term arrives |

### Same-day outbound (Rodrigo, 16:07 EDT): the "unwinds" explanation + the M5.20.1 seed round

The reply (drafted per the message-drafting rule) explained the unwinding mechanism in his core-regularization language, conceded the spectrum point with the measured evidence (exact-zero two-equal face at δ = 0, the 4 zero modes), framed M5.20 as the δ = 0 verdict, announced the (1, δ, 0) rerun with a δ sweep, and asked three questions:

| # | Question | Tracker |
| --- | --- | --- |
| 1 | δ value or range for the neutrino sector, or bless the sweep {0.1, 0.3, 0.5} | [Q22](../m5_question_tracker.md#q22-detail) (value half) |
| 2 | Which eigenvalue pair carries the cross-section winding (the (1, δ) pair regularizing to two-equal at center?) | [Q22](../m5_question_tracker.md#q22-detail) (pairing half) |
| 3 | Is spatial (1, δ, 0) enough for the protection question, or do the negative clock terms act already at the loop level (then we need the time term in M variables) | [Q23](../m5_question_tracker.md#q23-detail) |

**Process note (standing from this message on)**: the outbound debuted the **voice separation format**: a `RODRIGO VOICE` section (his own words: intent, workflow, relationship) and a `FABLE VOICE` section (the technical body, first-person plural "we"), so the author can weigh the two sources explicitly. All future Duda-channel drafts follow it.

## 2026-07-12: the seed round answered overnight: "start with (1, δ, 0)", the equalization mechanism, and the regularization ladder

**From**: Jarek Duda, 2026-07-12 00:06 EDT (~8h after the seed round), 1:1 on the thread.

### Verbatim core

> Thank you, it goes in right direction - the problem was indeed assuming delta=0 everywhere, for which there is no topological vortex.
>
> Instead, it is crucial that minimum of potential has different eigenvalues - in 3D (1, delta,0) you can start with, but finally to get oscillations requires full 4x4 tensor with potential preferring (1,g,delta,0) eigenvalues.
>
> Energy minimization has to equalize 2 eigenvalues in the center of vortex to prevent discontinuity of infinite energy - regularization to finite energy by activating potential.
>
> Later modeling charges analogously 3 spatial eigenvalues have to be equalized in the center to regularize singularity ... and if modeling black holes, all 4 eigenvalues should equalize in its center for finite energy.

### Decode + routing (folded into the [M5.20.1](m5_20_1_task_details.md) plan same day, per its folding table)

| Item | Decode | Routing |
| --- | --- | --- |
| "goes in right direction - the problem was indeed assuming delta=0 everywhere, for which there is no topological vortex" | The M5.20 reading CONFIRMED by the author: δ = 0 verdict stands, no computational objection; the δ = 0 sector has no protected vortex (matches the measured potential-free two-equal face) | M5.20 record unchanged; M5.20.1 premise author-confirmed |
| "in 3D (1, delta, 0) you can start with" | Seed-round **Q3 ANSWERED, the no-scope-change branch**: the spatial (1, δ, 0) run is the sanctioned START for the protection question; no clock term needed at this level. Also the folding-table Q1 outcome: no δ value given, so the sweep stands | M5.20.1 runs as planned (folding row "spatial is enough"); the canonical-kinetic-term flag softens from "our assumption" to "his sanctioned starting sector" ([Q23](../m5_question_tracker.md#q23-detail) loop-level half answered) |
| "finally to get oscillations requires full 4x4 tensor with potential preferring (1,g,delta,0)" | The recurring 4×4 directive now has a defined PLACE: not this run, the SUCCESSOR (oscillations = the clock sector). Note we HAVE the 4×4 assets: the engine substrate is 4×4 `D = diag(g,1,δ,0)` since M5.8.1 (`medium.py`, MDIM = 4), the M5.18-verified 4D Lagrangian, the spectral potential pins `(g,1,δ,0)` exactly, and a constrained 4D integrator exists (M5.8.2c). What blocks the oscillation RUN is well-posedness, not machinery: the degenerate Legendre map ([Q18](../m5_question_tracker.md#q18-detail)) + indefinite H + branch choice ([Q19](../m5_question_tracker.md#q19-detail)) + the time term in M variables ([Q23](../m5_question_tracker.md#q23-detail)). His "(1,g,delta,0)" here is read as a MISSPELLING of the standing (g, 1, δ, 0) (user call 2026-07-12: matches his own 07-11 "(g, 1, delta, 0)", his repeated reinforcement of the 4×4 spec, and the engine convention `D = diag(g, 1, δ, 0)`); the spectral potential pins the SET via Tr-power targets, and the timelike assignment is exactly Q19 | Successor stub **M5.20.2** added to the roadmap Backlog (gated by Q23/Q18/Q19 + the M5.20.1 verdict); the M5.20.1 method note gets a FIELD CONTENT box stating all of this up front (the legibility fix for the repeated directive) |
| "Energy minimization HAS TO equalize 2 eigenvalues in the center ... activating potential" | The two-equal core is not a seed CHOICE, it is the predicted OUTCOME of minimization at δ ≠ 0. Consequence: which pair equalizes should be MEASURED, not only imposed: seed both pairings, let statics/dynamics select, read the core spectrum `λ_i(ρ→0)` per run | M5.20.1 DoD gains the **core-equalization diagnostic** (the measured answer to the seed-round Q2 / [Q22](../m5_question_tracker.md#q22-detail) pairing half, which his reply left unnamed) |
| "charges: 3 spatial eigenvalues equalized in the center ... black holes: all 4 equalize" | The REGULARIZATION LADDER: vortex = 2-equal core, charge = 3-equal spatial core, black hole = 4-equal core. Retroactively consistent with his 2026-07-06 charge-core prescription `M = aI` (3D) / `(g', a, a, a)` (4D): that IS the 3-spatial-equal core | Recorded here as the program map (charges = the M5.12-line re-run home; black holes = far future); no task change now |

**Same-day group email (separate thread, models-of-particles, 03:02 EDT)**: Duda circulated the AMBer paper (Baretz et al. 2026, Commun. Phys. 9:227: RL agent + physics-software pipeline searching neutrino flavor-symmetry model space) with "We are not the only ones - maybe let's try to work together before being overrun". Different framework (seesaw flavor fitting, not topological solitons); assessed + cited as methodological context and as the lepton-observables scoreboard any eventual 4×4 oscillation sector must fit ([`../../theory/_CITATIONS.md`](../../theory/_CITATIONS.md), local copy `amber_neutrino_flavor_rl.pdf`). Strategic read: his urgency about agent-driven model search is rising; the grounded-collaborator channel we run is exactly his proposed response.
