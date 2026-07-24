# M9 CAT/EPT: Entropic Particle Dynamics

M9 now includes all 21 comparison controls, finite color/flavor carriers, one coupled finite-grid PDE, multiple 3D stability and self-binding campaigns, finite-grid and phase-space semigroup bridges, nonlinear generator graph controls, fail-closed formal evidence refresh, and nested-grid convergence evidence.

## Current decisions

- Nineteen criteria remain partial and two remain honest negatives.
- M9.49 selects no self-bound candidate in its merged untrapped unified scan.
- M9.52 selects no candidate across Gaussian, exponential, super-Gaussian, shell, and unit-winding toroidal families.
- The vortex winding remains resolved, but topology in the current action does not prevent dispersal.
- M9.53 closes a finite positive, mass-conserving Fokker--Planck bridge with detailed balance and entropy decay; continuum hypoelliptic well-posedness remains open.
- M9.54 shows smooth finite-Galerkin state and generator-graph convergence plus bounded-set shifted dissipativity. It does not prove full nonlinear continuum closability or semigroup generation.
- M9.55 refreshes exact kernel evidence and promotes zero formal proofs because the relevant declarations remain `pending_ci`, interface-only, or open.
- M9.56 shows monotonically decreasing nested-grid errors for the unified nonlinear state while preserving all balance, positivity, and entropy controls. It does not construct a continuum solution.
- ZIL supplies orchestration and source traceability; Lean remains proof authority.

## Exact formal source

`jagg-ix/entropic-physlib-private@entropic-physlib-linear-full`

## Next critical targets

1. M9.57 formal nonlinear generator closability, maximal dissipativity, and semigroup generation.
2. M9.58 continuum kinetic/Fokker--Planck convergence and hypoelliptic well-posedness.
3. M9.59 theory-derived binding term and untrapped 3D discrimination.
