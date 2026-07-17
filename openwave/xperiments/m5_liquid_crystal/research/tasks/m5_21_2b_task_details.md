# M5.21.2b: the well-posed 3D instrument (term-set discrimination + converged census)

**Status**: 🚧 PLANNED STUB (2026-07-17, staged at the [M5.21.2](m5_21_2_task_details.md) close; user decision: more runs before any Duda checkpoint, consolidate the package). Full PLAN at go.

## Scope (stub level)

M5.21.2 ended instrument-blocked: at toy parameters the quartic commutator functional has NO stencil-consistent minimizer (each stencil's descent hides curvature in its blind directions, ×7-128 cross-stencil disagreement, audited). This task builds the instrument that CAN converge a 3D electron, then re-runs the census on it for converged minima.

| Arm | What | Kill / survive read |
| --- | --- | --- |
| I1 the instrument | Candidate fixes, cheapest first: (a) stencil-symmetrized functional (average fwd/bwd stencil energies: kills both known blind families); (b) a tiny Dirichlet regularizer ε‖∇M‖² with ε → 0 extrapolation (kills the aligned-gradient soft directions); (c) grid-refinement ladder (h-halving at fixed physical box) as the convergence CHECK on whichever wins | an instrument whose deep endpoints read consistently across stencils AND refinement rungs; else the honest negative that the term set itself is deficient |
| I2 term-set discrimination (the Q25 arms, self-determined) | On the winning instrument: the trace-target vs the Eq 12 eigenvalue-penalty potential; the det-constraint variant with the author's own caveat folded (spectrum must shift off zero first, his 2026-07-17 reply) | which term set pins a compact virial-balanced minimum (u = 3V landed, not just bracketed) |
| I3 the converged census | Seeds A/B/C + the charged ring R on the winning (instrument, term set): converged minima, the real lepton-hierarchy read (three minima? energy ratios?) and the ring-vs-point verdict at conviction | the M5.21.2 qualitative ordering (A < C < B, electron lowest) either survives to convergence or the honest re-verdict |
| Films | THE FILM-TEMPLATE FIX (user catch at the M5.21.2 review): a 4×4-embed adapter (block-diag with g) so the TRUE `m5_film.py` basic + thermal templates render the 3D states; regenerate the census films on it | series film rule compliant |

Consolidation goal: this task + M5.21.2 together form the next Duda package (the Q25 sharpening lands WITH its constructive answer, not as a bare negative).

**Gated by**: M5.21.2 ✅ + user "go" (runs ahead of [M5.21.3](m5_21_3_task_details.md), which re-gates on THIS task's converged minima).
