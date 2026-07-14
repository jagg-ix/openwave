# M5.20.4: the formulation search: a usable dynamics for the quartic L, found by us

**Status**: roadmap row at the top of [BACKLOG](../m5_roadmap.md) (PLAN written 2026-07-14 at the M5.20.3 close). Opens on the user's "go". Deliberately NOT gated on a Duda answer: the strategy (user, 2026-07-14) is to search the formulation space ourselves first and gate on him only where a question is genuinely author-gated: he himself said the regularization is the hardest part and that he has tried many: we search where he has not.

**Lineage**: [M5.20.3](m5_20_3_task_details.md) (the verdict this task answers: free-EL IVP ill-posed, every regularization blows up, E → −∞, his BVP branch fires; the true-L instrument `m5_20_3_a_constraint.py` with GC0a-e green) · tracker [Q24](../m5_question_tracker.md#q24-detail) (the formulation question: rides the next outbound in parallel; his answer, if it lands, folds in mid-task) · the M5.12 phase-D time-periodic BVP instrument (the arm-A machinery) · [`../m5_particle_hunt.md`](../m5_particle_hunt.md) (both hunts funnel into this task's outcome).

## TASK PLANNING (2026-07-14, at the M5.20.3 close)

### Scope

Search three self-directed formulation routes for a USABLE dynamics of the purely-quartic verified L on the vortex-loop background, each with pre-registered kill criteria; deliver a per-arm verdict and, if an arm survives, demonstrate it on the loop (the M5.21.1 hedgehog run then inherits the winner). One contingency arm held in reserve.

| Arm | Route | The question it answers | Kill criterion (pre-registered) |
| --- | --- | --- | --- |
| **A** (primary) | **Time-periodic least-action BVP under the true L**: extremize the action over periodic orbits (the period IS the clock); re-derive the M5.12 phase-D instrument (`Shat = S0 − ω²Q2`, balance root, the `H_mean = 0` identity) with Q2 built from the TRUE kinetic form K(M) instead of the canonical norm; start at the rigid-orbit level (the M5.20.2 H(ω) machinery re-read through the action), then Fourier-in-time profile relaxation if the rigid level signals | Does a finite-ω periodic orbit (a particle clock) EXIST in the formulation he himself endorses (least action, two-sided BCs)? If yes: containment + the radius-breathing observable become measurable at last | No balance root on any orbit family at budget, or every extremum is a runaway direction (S unbounded along the family): then the BVP search is honestly negative at the seed-family level and the result is the sharpest possible Q24 follow-up |
| **B** | **Dirac consistent initial data**: the from-rest EL-inconsistency (98.6% null-force) says (M, V = 0) at loop seeds is off the theory's constraint surface. Find data ON it: (i) config route: solve P_null(M)·G_static(M) = 0 near the loop (q intact); (ii) velocity route: at fixed M solve RHS_null(M, V) = 0 for V (quadratic in V, Newton). Then evolve and measure surface preservation (nff(t)) and whether the blowup persists on-surface | Is the IVP well-posed on the theory's OWN consistent sector (the mathematically required Dirac-Bergmann treatment, not an added restriction)? Almost certainly unsearched by the author | The surface is empty near loop states (decisive, reportable), or evolution leaves it at a rate that makes it useless, or the blowup persists on-surface (which strengthens the BVP-only conclusion) |
| **C** (diagnostic) | **The sanctioned-term kinetic fix**: enumerate the Lorentz-invariant gradient-term classes he has sanctioned (the Q13 redirect: Skyrme-like terms on the 4×4 tensor; note the η-metric QUADRATIC term tr(ηṀηṀ) is itself indefinite in the time-mixing sector: the derivation decides what is admissible), derive each candidate's contribution to K(M), and MEASURE whether any closes the indefiniteness (K positive-semidefinite on the measured backgrounds) while preserving the statics anchors (r_half, the Coulomb lock, the core gate: gate re-runs, not production) | Does a term HE already sanctioned fix the kinetic form at the source? Nobody has computed the K-effect of the Q13 class | No sanctioned term closes K on the measured backgrounds, or every term that does breaks a statics anchor gate |
| **D** (contingency, only if A-C all kill) | **The ε-canonical bridge**: L + ε·canonical kinetic; t*(ε) and stability-window scan; if a stable window exists, measure the oscillation observables and study the ε → 0 limit | A pragmatic numerical bridge to the observables, documented as regularization | No stable window, or observables do not converge as ε shrinks |

Run order: **C-census first** (cheapest; if a term fixes K the other arms change meaning), then **B**, then **A** (the deepest and highest-payoff). D only on triple kill. All arms on the loop at 64×128 (the M5.20.3 grids), δ = 0.3, the recipe seed as primary.

NOT in scope: production oscillation runs under a winning formulation (that is the successor, with M5.21.1 taking the hedgehog); any new outbound content beyond folding (the Q24 email is already drafted and user-gated); the AMBer fit.

### Definition of done

| ✅ when | Bar |
| --- | --- |
| Per-arm verdict delivered | Each arm reaches its pre-registered survive/kill criterion, machine-checked (try cap 3 per gate); timeboxes: C ≈ 2 h, B ≈ 2-3 h, A ≈ 4-5 h; the tail ships partials |
| Instruments gated before physics | Arm A: the quartic-Q2 derivation gated complex-step against the discrete action (the GC0 pattern); Arm B: the surface residual + its Jacobian gated; Arm C: each candidate term's K-contribution gated against a from-scratch build (the GC0d pattern) |
| A winner demonstrated (if any survives) | Arm A: a balance-root orbit with its ω, energy, and containment read on the loop; Arm B: an on-surface evolution to T ≥ 50 with nff ≈ 0 and the ledger clean; Arm C: a K-closing term with ALL statics anchor gates re-run green |
| Honest disposition if all kill | The triple negative + arm-D scan = the sharpest possible Q24 follow-up (we searched his space AND ours); the outbound updates only through the user |
| Records | Method note `../findings/m5_20_4_method_note.md` (equations first, code map, figures per the film standard where states evolve); independent adversarial audit (cardinal rule); tracker Q24 + convo + roadmap routing; film strips per [`../m5_visualization.md`](../m5_visualization.md) (basic template; blowup spacing where applicable) |

### Gating

Roadmap `Gated By`: user "go" only. Q24's outbound rides in parallel; **folding rule**: if Duda's Q24 answer lands mid-task, fold it as a branch decision at the next arm boundary (the M5.20.3 folding-table pattern), log the fold in this file, and continue: his answer refines, never blocks.

### Blindspot pass (unfamiliar territory: action-level search + constraint surfaces + term enumeration)

| # | Unknown unknown surfaced | Fold into plan |
| --- | --- | --- |
| 1 | The quartic Q2 may itself be degenerate/indefinite on orbit families (the K_eff census in action language): the balance-root machinery assumed a sign | Pre-register the reading: an indefinite Q2 is the H(ω) census re-derived, reported as structure, not failure; the orbit family census comes FIRST in arm A |
| 2 | Arm B's config-route solve may converge to the unwound remnant (the statics slide) instead of a loop state | Constrain the solve (winding read in the loop, the M5.19 corepin precedent as fallback); an empty ON-loop surface is itself the decisive answer |
| 3 | Arm C's admissible-term enumeration is a derivation risk (the η-quadratic is indefinite; Skyrme-like on a symmetric tensor has several contraction patterns) | Enumerate ALL contraction patterns at quadratic and quartic order first, machine-check each for Lorentz invariance with the M5.18 check-1 instrument, THEN derive K-contributions only for the invariant ones |
| 4 | Wall-clock: three deep arms in one task | Hard timeboxes per arm (DoD); the run order puts the cheapest decisives first; hard cap ~1 day, ship partials + the sharpest question |
| 5 | The winner may behave differently on the hedgehog (different K census: rank 8 core vs rank 5) | Out of scope here: M5.21.1 inherits the winner AND re-runs its gates on the hedgehog before physics (the series re-capture rule) |

### Research-body destinations

| Artifact | Destination |
| --- | --- |
| Scripts | `../scripts/m5_20_4_a_bvp.py` · `m5_20_4_b_dirac.py` · `m5_20_4_c_terms.py` · (`m5_20_4_d_bridge.py` contingency) · `m5_20_4_plots.py` |
| Data / plots | `../data/m5_20_4_*.json` (+ npz ≤ 1 MB; larger deleted at FINISH with regen docs) · `../plots/m5_20_4_*.png` (film standard) |
| Findings | `../findings/m5_20_4_method_note.md` |
| Records | This file (FINDINGS + TASK REVIEW) · tracker Q24 · [`m5_20_convo.md`](m5_20_convo.md) if outbound content changes (user-gated) · `../checkpoints/m5_20_4_progress.md` (opens at go, resume-complete) |

### Preconditions

| Precondition | State |
| --- | --- |
| M5.20.3 instrument + verdicts (K builds, accel, the blowup card) | ✅ closed 2026-07-14 |
| M5.12 phase-D BVP scripts on disk | ✅ frozen at the M5.12 close (regen documented there) |
| The Q13 sanctioned-term record (his 2026-07-06 slides + the redirect decode) | ✅ tracker Q13 + `m5_18_convo` record |
| Q24 outbound | drafted, user-gated, independent of this task |
| Resume ping + checkpoint | 🚧 at go (user supplies resets_at) |

### Model + effort

Fable 5 high for the arm-A action re-derivation and the arm-C term enumeration (novel derivations); default effort for the mechanical gate loops; independent agent with own instruments for the audit (cardinal rule).

### Contingencies + comms

| Trigger | Action |
| --- | --- |
| Duda's Q24 answer lands mid-task | Fold at the next arm boundary (folding rule above), log, continue |
| Hard cap (~1 day) | Ship per-arm partials + ONE sharp follow-up question |
| An arm produces an outbound-worthy positive early (e.g. a balance-root clock) | Checkpoint it, finish the arms, present at REVIEW; outbound stays user-gated |
