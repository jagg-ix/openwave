# M5.20 convo record (the program thread, continued: the spectrum directive)

Per-task convo record (technical exchange, no author-private content, so tracked in-repo per the convo-records rule). Outbound context: the M5.20 close message sent 2026-07-11 morning with the method-note link ([`../findings/m5_20_method_note.md`](../findings/m5_20_method_note.md)); tracker registry [`../m5_question_tracker.md`](../m5_question_tracker.md); predecessor exchange [`m5_19_convo.md`](m5_19_convo.md). Successor task planned from this entry: [M5.21](m5_21_task_details.md).

## 2026-07-11: Duda's replies to the M5.20 note: the (1, delta, 0) spectrum directive (spec for M5.21)

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
| "(1,0,0) spectrum, while topological vortex requires (1, delta, 0) minimum - three different" | The load-bearing catch: at δ = 0 the two lower eigenvalues are ALREADY equal in vacuum, so the two-equal face is potential-free (M5.19 B2 measured "the two-equal core is nearly free"; the M5.20 vacuum Hessian's 4 zero modes include the 2 pair-splitting directions, gapped only at quartic order). His diagnosis names exactly the channel the unwinding used. At δ ≠ 0 the pair-splitting face gets an energy gap ("activating potential") and the vacuum manifold topology changes (π₁ = Q₈, no free escape) | Machine-checkable → **[M5.21](m5_21_task_details.md)** (the δ ≠ 0 rerun). Tracker [Q22](../m5_question_tracker.md#q22-detail) REOPENED: his "I don't know in this moment" (2026-07-10) is superseded by a structural directive (the vortex sector requires δ ≠ 0); the VALUE stays unknown |
| "maybe there is problem with assumed simpler spectrum" | Correct reading of M5.20's scope: the verdict is a statement about the δ = 0 theory (his electron-sector spec, run because Q22 was parked-unknown and disclosed in the note § 4). Not a computational bug: the audit stands; the theory he intends is different and now testable | The M5.20 record keeps its licensed close sentence unchanged (in-scope); M5.21 tests the intended theory |
| "clock propulsion ... require full 4x4 tensor field with (g, 1, delta, 0) spectrum" | Confirms the clock sector needs the time eigenvalue g in the potential AND the time/kinetic term (the negative `Γ·Γ̃` contributions, "from Hamiltonian we have agreed to" per his 12:59 line, i.e. the M5.18-verified 4D Lagrangian) | Tracker [Q23](../m5_question_tracker.md#q23-detail) rider added; the clock stays out of M5.21 scope unless the M-variable time term arrives |

### Same-day outbound (Rodrigo, 16:07 EDT): the "unwinds" explanation + the M5.21 seed round

The reply (drafted per the message-drafting rule) explained the unwinding mechanism in his core-regularization language, conceded the spectrum point with the measured evidence (exact-zero two-equal face at δ = 0, the 4 zero modes), framed M5.20 as the δ = 0 verdict, announced the (1, δ, 0) rerun with a δ sweep, and asked three questions:

| # | Question | Tracker |
| --- | --- | --- |
| 1 | δ value or range for the neutrino sector, or bless the sweep {0.1, 0.3, 0.5} | [Q22](../m5_question_tracker.md#q22-detail) (value half) |
| 2 | Which eigenvalue pair carries the cross-section winding (the (1, δ) pair regularizing to two-equal at center?) | [Q22](../m5_question_tracker.md#q22-detail) (pairing half) |
| 3 | Is spatial (1, δ, 0) enough for the protection question, or do the negative clock terms act already at the loop level (then we need the time term in M variables) | [Q23](../m5_question_tracker.md#q23-detail) |

**Process note (standing from this message on)**: the outbound debuted the **voice separation format**: a `RODRIGO VOICE` section (his own words: intent, workflow, relationship) and a `FABLE VOICE` section (the technical body, first-person plural "we"), so the author can weigh the two sources explicitly. All future Duda-channel drafts follow it.
