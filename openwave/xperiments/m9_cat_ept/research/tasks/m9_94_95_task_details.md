# M9.94--M9.95 task details

## Objective

Import the CAT/EPT formalization corpus on the pinned `entropic-physlib-linear-full` branch, retain every indexed ZIL declaration and status boundary, incorporate the latest Eddington gravity surface, then bind spin, magnetic-moment, electric-force, and magnetic-force interfaces to canonical M9 particle states.

## M9.94a — branch-wide formalization import

- Pin the exact current branch tree and current `Physlib.lean` blob.
- Import the five operational/status ZIL graphs: electrogravity, LDDL, Liouville second quantization, Cauchy weak limit, and Lindblad trace preservation.
- Import the six merged formalization-corpus graphs: two Rivers graphs, three Lovelock–Rund graphs, and the Veliev periodic-Schrödinger graph.
- Preserve components, sources, assumptions, claims, proof tokens, rules, queries, dependency edges, pending states, constructive-QFT boundaries, and external analytic requirements.
- Pin aggregate and selected Lean source blobs and map witness namespaces to those sources.
- Subsume the existing selected `physlib_contract.v2.json` without promoting its scope.
- Fail closed under tree drift, blob drift, missing files, duplicate declarations, unresolved namespaces, or unavailable adapters.

Acceptance count:

```text
ZIL graphs                = 11
ZIL entities              = 422
open/external boundaries  = 12
Lean aggregate/sources    = 24
current formal tree       = 239a663a3192a3144fb998e7bb200e09689a3bb9
```

## M9.94b — Eddington affine first integral

- Import affine connection residual contraction and density-parallel equivalence.
- Import Ricci and scalar-curvature first-integral identities.
- Import Einstein-Λ recovery and nonsingular-Λ consequences.
- Import torsion-vacuum contorsion elimination and the Lovelock field-equation bridge.
- Preserve the explicit boundary that the connection field equation is assumed rather than re-derived from the action.
- Do not promote gravity without global coupled evolution and physical calibration.

## M9.94 — canonical spin and magnetic moment

- Embed the three-dimensional CAT/EPT particle envelope into a Pauli spinor.
- Use periodic spectral derivatives for current and orbital observables.
- Close normalization, `J_z = 1/2`, orbital-zero control, Pauli-current moment, tree-level `g = 2`, spin reversal, and periodic translation covariance.
- Import the Pauli tensor, spin-orbit, and anomalous-moment formal declarations.
- Keep the Schwinger anomaly and physical electron identity outside the derived claim.

## M9.95 — canonical electric and magnetic force

- Construct one periodic pair with declared winding sectors `+3` and `-3`.
- Use exact winding arithmetic to obtain dimensionless charges `+1` and `-1`.
- Derive canonical magnetic moments from the M9.94 Pauli-current bridge.
- Use one shared interaction ledger for electric and magnetic kernels.
- Import screened/Coulomb and Lorentz-EM formal declarations.
- Close energy derivatives, signs, asymptotes, action-reaction, and screening controls.
- Keep charged stationary branches and physical-unit calibration explicitly open.

## Status policy

M9.94 and M9.95 improve formal and canonical-state integration. They do not promote any comparison row. The platform matrix must remain `7 validated / 13 partial / 1 negative`.
