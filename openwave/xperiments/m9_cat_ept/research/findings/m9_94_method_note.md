# M9.94 method note: branch-wide formalization import and canonical spin-magnetic bridge

## Scope

M9.94 imports the CAT/EPT formal corpus from `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, pinned by base commit `e10af9a3b47bf90afc0a88167a5d495b6935f4dc` and exact current tree `239a663a3192a3144fb998e7bb200e09689a3bb9`.

The import separates two authorities:

- Lean declarations and source blobs are proof authority.
- ZIL graphs record components, claims, assumptions, sources, dependencies, verification/status vocabulary, rules, queries, and explicit boundaries.

## Deep inventory

| Graph family | Graphs | Entities | Open/external boundaries |
| --- | ---: | ---: | ---: |
| Electrogravity and open systems | 5 | 180 | 9 |
| Rivers scalar Green functions | 2 | 128 | 2 |
| Lovelock–Rund | 3 | 84 | 0 |
| Veliev periodic Schrödinger | 1 | 30 | 1 |
| **Total** | **11** | **422** | **12** |

Twenty-four Lean aggregate/source blobs are pinned. The current `Physlib.lean` blob is `182a06e0f50314ec54436da602b4ac86eba4ee08`. The source registry includes the selected CAT/EPT theorem modules, Rivers scalar Green functions, Lovelock–Rund, Veliev periodic Schrödinger, and the latest Eddington affine first-integral module.

The existing `physlib_contract.v2.json` is subsumed as the selected historical contract. Tree drift, blob drift, missing sources, unresolved namespaces, missing boundaries, duplicate graph declarations, and unavailable numerical adapters fail closed. Pending-CI, pending-kernel, conditional, constructive-QFT, and external-analytic states remain unpromoted.

## Latest Eddington gravity surface

`EddingtonAffineFirstIntegral.lean` adds:

- affine connection residual contraction and density-parallel equivalence;
- the Ricci-plus-matter first integral;
- scalar-curvature contraction;
- Einstein equation with cosmological constant;
- nonsingular-first-integral consequences for nonzero `Λ`;
- torsion-vacuum contorsion elimination;
- a Lovelock first-integral field-equation bridge.

The result is algebraic on a finite index type after assuming the affine connection field equation. It is not a complete derivation of that connection equation from the action and does not provide global nonlinear Cauchy evolution or physical calibration.

## Canonical spin-magnetic bridge

The existing scalar CAT/EPT particle envelope is embedded into a two-component Pauli spinor on the same three-dimensional periodic lattice. Spectral derivatives yield:

- integrated spin `J_z = 1/2`;
- zero orbital-angular-momentum control;
- Pauli magnetization current;
- magnetic moment and inferred tree-level `g = 2`;
- spin reversal under the opposite Pauli component;
- periodic translation covariance.

PhysLib supplies the Pauli tensor involution, Dirac-energy compatibility, Foldy-Wouthuysen spin-orbit structure, and the structural identities

```text
g(a) = 2(1 + a),
a_Schwinger = alpha/(2 pi),
g(a_Schwinger) = 2 + alpha/pi.
```

## Decision

- Branch-wide imported Lean/ZIL inventory for the located formal corpus: **closed**.
- Latest Eddington affine first-integral surface: **imported with scope**.
- Canonical three-dimensional CAT/EPT envelope bound to a Pauli spinor: **closed**.
- Tree-level `g = 2` from the canonical Pauli current: **closed in-platform**.
- Schwinger anomaly derived from CAT/EPT particle dynamics: **not established**.
- Calibrated electron magnetic moment, physical electron identity, and calibrated global gravity: **not established**.
- Criterion statuses remain **partial** where physical obligations remain.
