# M9 global target plan

## Closure through M9.71

- **M9.69:** normalized imaginary-time evolution solves the full stationary cubic--quintic equation from super-Gaussian, anisotropic, and shell seeds. Maximum seed distance is `0.002245`, maximum relative residual is `0.002671`, nested radius spread is `0.012753`, and the best Gaussian remains at least `0.06790` away in `L²`.
- **M9.70:** PhysLib proves the exact cubic--quintic density factorization and lower bound. An `H1OrbitalCertificate` makes flow, conservation, compactness modulo symmetry, and coercivity explicit and yields a uniform orbital-distance theorem. Construction of those analytic certificate fields from the spatial PDE remains open.
- **M9.71:** the replacement stationary-branch radial mode is frozen at `omega_radial / omega_Compton = 1.074356835825` on `20³`. Held-out `24³` and `28³` discrepancies are `2.34%` and `4.18%`, both inside the fixed `5%` gate. No external experiment was used.

## Current cross-repository state

| Repository | Revision | Contribution |
| --- | --- | --- |
| OpenWave baseline | `2dfaf6da88b24fe43799b53d79ef2f7aa3244a32` | merged M9.68 state |
| OpenWave work branch | `agent/m9-stationary-formal-mode-69-71` | stationary solver, formal bridge, replacement mode, tests, and ledgers |
| PhysLib merged branch | `e2c06741c3e49deb604082a2e9c2e918eab8d545` | cubic semiflow and zero global attractor |
| PhysLib M9.70 branch | `51aad63b2541a1377a001df71b85dfe35f26c0af` | exact density coercivity and conditional orbital certificate |
| ZIL | `7ef24a8557b610f8f0f560cf375c2a1600083591` | evidence conventions and operational tooling |

## Theory status

The platform remains `0 validated / 20 partial / 1 negative`. The lepton hierarchy remains the sole criterion-level negative. The methodological ledger contains two frozen subpredictions: M9.65 is internally falsified; M9.71 passes internal held-out grids. Neither has been externally tested or physically validated.

## Next phase

| Target | Deliverable | State |
| --- | --- | --- |
| M9.72 | Construct the conservative spatial cubic--quintic `H¹` flow and prove mass/energy conservation | NEXT |
| M9.73 | Prove minimizing-sequence compactness and nonzero-branch coercivity modulo phase/translation | GATED |
| M9.74 | Compare the immutable M9.71 radial ratio with an independent implementation or external observable | PLANNED |
