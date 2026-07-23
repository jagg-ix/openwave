# M9 CAT/EPT roadmap

Research mode is headless first. No `_launcher.py` or visualization port is added
until a field dynamics passes the localization and stability gate.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract, equation-to-code map, deterministic conformance script, tests, method note | DONE; scaffold contract passed |
| M9.2 | One-dimensional free complex-field solver; analytic Gaussian benchmark; norm, energy, phase, current and convergence ledgers | DONE; all 11 gates passed |
| M9.3 | Fixed field-to-probability map; total-correlation, remaining-disequilibrium and accumulated-clock measurements; explicit monotonicity conditions | Startable after M9.2 |
| M9.4 | Preregistered nonlinear family and complete localization decision gate; report positive or negative without expanding the search after inspection | M9.2, M9.3 |
| M9.5 | Rest energy, radius, internal frequency and Compton-clock comparison for an accepted state | Positive M9.4 |
| M9.6 | Charge/spin carrier survey; no claim unless a genuine symmetry or topological invariant is implemented | Positive M9.4 |
| M9.7 | Taichi 3D port, shared instrumentation and `_launcher.py` | Audited positive dynamics |

## Completed gates

### M9.1 formal contract

- exact source branch, commit and Lean version recorded;
- theorem paths and hypotheses recorded;
- deterministic identities pass at absolute error `<= 1e-12`;
- malformed probability data and negative density are rejected;
- no phenomenology cell is promoted by transcription alone.

### M9.2 free solver

- periodic second-order finite differences and Crank--Nicolson;
- exact free Gaussian comparison at `N = 128, 256, 512`;
- observed order `>= 1.8` for phase, density and current;
- norm and discrete energy conserved to better than `1e-12`;
- finest density and current errors below `1e-2`;
- finest fidelity above `0.9999` and continuum-energy error below `5e-3`;
- edge probability below `1e-12`, excluding periodic wraparound.

See [`findings/m9_2_method_note.md`](findings/m9_2_method_note.md) and
[`data/m9_2_free_solver_result.json`](data/m9_2_free_solver_result.json).

## Next gate: M9.3

M9.3 must freeze the map from `psi` to a finite or coarse-grained probability
state before inspecting entropy curves. It must distinguish total correlation,
remaining disequilibrium, and accumulated clock gain rather than treating every
entropy-like quantity as the same direction of time.
