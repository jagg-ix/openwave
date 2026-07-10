# M5.19: the Duda-regularized vortex-loop ansatz (the M5.12 successor)

**Status**: DRAFT, awaiting the user's "go M5.19". Opened 2026-07-10 from Duda's same-day reply to the posted M5.12 close note ([`m5_12_convo.md § 2026-07-10 10:56`](m5_12_convo.md)); the author's diagnosis and construction ARE the spec. Predecessor record: [`m5_12_task_details.md`](m5_12_task_details.md) + [`../findings/m5_12_close_note.md`](../findings/m5_12_close_note.md) (frozen, closed 2026-07-10).

## Why a new task ID (and not reopening M5.12)

M5.12 closed on a measured, audited endpoint whose reopening conditions anticipated exactly this: an author redirect that plausibly relaxes below the floor. Duda's reply redirects the CONSTRUCTION (the ansatz was under-regularized), not the old search, so the successor gets a fresh Duda-facing surface (`m5_19_*`) and the `m5_12_*` corpus stays frozen as the evidence his reply is responding to (the M5.11 → M5.12 precedent). The M5.13-M5.15 IDs were already taken by backlog tasks; M5.19 is the next free ID.

## The spec (the author's construction, verbatim source in the convo record)

| Requirement | Content | Source line |
| --- | --- | --- |
| R1 the core regularization (CENTRAL) | the spatial eigenvalues (1, δ, 0) must deform so TWO eigenvalues become EQUAL at the vortex center in the cross-section (infinite energy otherwise), included in the ansatz "in a general way" | the diagnosis; [diagram](../images/m5_12_duda_ansatz.png) |
| R2 the profile | a radial cross-section profile `M(r)`, r = distance from the vortex center, carrying R1 | "Should be sufficient M(r)..." |
| R3 the planar vortex | rotate the profile in-plane to a topological vortex; **degree 1 (beta decay) AND 1/2 both run** (a measurable residual) | "beta decay suggests of degree 1, but also might be 1/2" |
| R4 the loop | revolve to a closed loop of radius **R as a degree of freedom** (energy conservation demands variable R; density-per-length varies) | "radius R ... should be able to vary"; [torus diagram](../images/m5_12_duda_torus.jpg) |
| R5 the loop center | the field must also be optimized at the loop center (not just the ring neighborhood) | "optimized in the center of such loop" |
| R6 the minimization | energy minimization of the cylindrically-symmetric `M(x,z)` field: EXACTLY the M5.12 axisym (ρ,z) instrument | "finally energy minimization ... cylindrical symmetry" |
| R7 the clock (after statics) | gravity's "tiny boosts of temporal axis, crucial to propel oscillations": the time-mixing channel applied ON the regularized minimizer, via the M5.12 BVP instrument | the gravity line + the standing Q19 intent |

## What M5.19 inherits (the M5.12 toolkit, all audit-confirmed)

| Asset | Use here |
| --- | --- |
| The axisym (ρ,z) stack + `m5_17_energy.py` (the audited functional) | R6 directly |
| The exact `Shat = S0 − ω²Q2` instrument + balance root + `H_mean = 0` identity | R7 (the clock phase) |
| The ω-eliminated LM hard-amplitude solver + honest metrics + stall rule | R7 |
| The standing fixed-(size, a²) metric + control frame + the b17 frame battery | every cross-candidate comparison from day one (no metric war this time) |
| The measured conditional unit map (A1/A2, author-gated) | any band statement (conditionality unchanged) |
| The loop-topology diagnostics (winding, ring readout) | R3/R4 verification |
| The workflow: pre-registered gates, checkpointing, adversarial audit per block, ask-when-gated batched (NEW, codified 2026-07-10) | throughout |

## The phased plan (draft, pre-registered gates at go)

| Phase | What | Gate (pre-registered) |
| --- | --- | --- |
| A the regularized profile | build the `M(r)` family with the R1 eigenvalue-degeneracy condition enforced structurally (a general parametrization, not a hand profile); verify the energy density is FINITE at the core where the (1, δ, 0) ansatz diverges | the core energy-density integrand bounded as r → 0, machine-checked; the unregularized control diverges on the same grid |
| B the planar vortex | rotate to degree 1 and 1/2 vortices; exact energy readouts vs core size | both degrees carry finite core energy; the degree comparison is a measured number |
| C the loop + R relaxation | revolve to the torus with R free (R either a continuation parameter scanned to the energy minimum, or a genuine DOF in the minimizer); R5 loop-center optimization included | an interior optimum R\* exists (dE/dR = 0 bracketed) OR the honest boundary verdict (R runs away / collapses), either way a real number |
| D statics minimization | full (ρ,z) energy minimization from the phase-C seed under the audited functional; stability probe | a stationary regularized loop (gnorm decades + bounded second-variation probe) OR the honest negative with the audit's wording rules |
| E the clock on the minimizer | the M5.12 BVP instrument on the phase-D state: Q2 sign, balance root, chains; the standing metric governs all comparisons | pre-registered at go (depends on D's outcome) |
| F masses/mixing inheritance | ONLY if D+E produce solutions: the disposed M5.12 E/F gates reactivate unchanged (the `E = λ·L` trajectory, the N4c gap map) | as pre-registered in M5.12 |

## Ask-when-gated (the standing loop with the author)

Per the 2026-07-10 amendment (`_AI_flow.md` + the tracker outbound policy): when a branch hits an author-gated unknown, checkpoint that branch, queue the question with a tracker ID, keep ungated work running; asks go out BATCHED with method-note-grade context. Already-queued candidates for the first batch (only if they actually gate a branch at run time): the degree 1-vs-1/2 preference once both numbers exist; the R1 "general way" parametrization if our family choice needs sanction; the A1/A2 unit-map assumptions if any band statement goes outbound.

## Definition of done (draft)

A stationary (or clock-carrying) REGULARIZED vortex loop under the author's construction, or the honest negative stated under the standing metric with the same rigor surface as the M5.12 close (method-note close page, adversarial audits embedded, supersede discipline). The M5.12 lesson is binding: negatives are closed on measured endpoints, not budget exhaustion, wherever a bounded decider exists.

## EXECUTION LOG

| Time | Event |
| --- | --- |
| 07-10 11:50 | Task drafted (setup block, no go yet): the spec from Duda's 2026-07-10 reply ([`m5_12_convo.md`](m5_12_convo.md)), the inherited-toolkit table, the phased plan with draft gates. Awaiting the user's "go M5.19" + reply-to-Duda dispatch |
