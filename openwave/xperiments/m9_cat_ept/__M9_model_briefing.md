# M9 CAT/EPT: Entropic Particle Dynamics

M9 now covers all 21 comparison criteria and includes a coupled finite-grid PDE, finite semigroup and phase-space bridges, nonlinear generator and nested-grid controls, live PhysLib/ZIL status reconciliation, a finite kinetic convergence campaign, and an action-derived 3D localization candidate.

## Platform status

- Zero criteria are fully validated in-platform.
- Twenty criteria are partial or bounded.
- One criterion remains an honest negative: the predictive lepton-mass hierarchy.
- M9.49 and M9.52 remain valid negatives for the original action and tested profile families.
- M9.59 changes the particle-stability row to partial by selecting a finite-grid candidate from an explicit bounded cubic--quintic action term. It does not establish orbital stability, continuum existence, uniqueness of the term, or a physical particle.

## Formal status

The exact formal source is `jagg-ix/entropic-physlib-private@entropic-physlib-linear-full`, inspected at `14ecf025ec58d2ec9e4731081c4ed1853f4468f0`.

PhysLib contains scoped metric-built Einstein--Maxwell--entropic action/PDE constructors, global Einstein--Hilbert and electrogravitic action interfaces, intrinsic Maxwell equations, ADM constraint propagation, and conditional maximal-development infrastructure. These results strengthen the formal evidence attached to the gravity and electromagnetic rows; they do not convert those rows into calibrated OpenWave validation.

## Latest closures

- **M9.57:** live blob-pinned formal reconciliation and a finite action-to-generator derivative/flow bridge. Full continuum generator closability and semigroup generation remain open.
- **M9.58:** nested phase-space convergence, positive mass-conserving generators, and algebraic Hörmander bracket rank. Continuum existence, uniqueness, subelliptic estimates, and hypoellipticity remain open.
- **M9.59:** bounded cubic--quintic action derivative and 3D discrimination against the merged untrapped baseline. A finite-grid localization candidate is selected across three grids; physical-particle status remains open.

ZIL supplies orchestration, source traceability, scope labels, and open-target queries. Lean remains proof authority.

## Next critical targets

1. M9.60 derive or reject uniqueness of the selected binding action from the CAT/EPT axioms and formal action stack.
2. M9.61 continuum orbital-stability and compactness theorem for the selected candidate.
3. M9.62 calibrated mass, charge, clock, and coupling map with external falsification gates.
