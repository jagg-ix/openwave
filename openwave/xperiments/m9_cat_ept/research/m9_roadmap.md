# M9 CAT/EPT roadmap

Research mode is headless first. No `_launcher.py` or visualization port is added
until a field dynamics passes the localization and stability gate.

| Task | Deliverable | Gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract, equation-to-code map, deterministic conformance script, tests, method note | Scaffold |
| M9.2 | One-dimensional free complex-field solver; analytic Gaussian benchmark; norm, energy and convergence ledgers | M9.1 |
| M9.3 | Fixed field-to-probability map; total-correlation, remaining-disequilibrium and accumulated-clock measurements; explicit monotonicity conditions | M9.2 |
| M9.4 | Preregistered nonlinear family and complete localization decision gate; report positive or negative without expanding the search after inspection | M9.2, M9.3 |
| M9.5 | Rest energy, radius, internal frequency and Compton-clock comparison for an accepted state | Positive M9.4 |
| M9.6 | Charge/spin carrier survey; no claim unless a genuine symmetry or topological invariant is implemented | Positive M9.4 |
| M9.7 | Taichi 3D port, shared instrumentation and `_launcher.py` | Audited positive dynamics |

## M9.1 acceptance criteria

- exact source branch, commit and Lean version recorded;
- theorem paths and hypotheses recorded;
- Python symbols mapped one-to-one;
- deterministic algebraic checks pass at absolute error `<= 1e-12`;
- invalid distributions and negative density are rejected;
- method note states that the result is transcription conformance, not particle verification;
- no OpenWave phenomenology cell is promoted by this task alone.
