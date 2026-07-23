# M9.8 task: shared instrumentation, renderer, and launcher

## Goal

Expose the validated scalar, radial, and transverse M9 sectors through one
research-facing interface without changing any scientific equation or promoting a
selected dimensionless field solution to a particle identity.

## Deterministic presets

The manifest freezes three presets:

1. `scalar-observables` -> M9.5;
2. `radial-dynamics` -> M9.7b3;
3. `transverse-radiation` -> M9.7c.

Each preset records its committed ledger, deterministic runner, metric selectors,
positive claim boundary, and explicit non-claims.

## Interfaces

- ledger-only summary mode;
- optional deterministic solver refresh;
- shared scalar metric panels;
- headless JSON export;
- headless PNG export using Matplotlib `Agg`;
- interactive Matplotlib dashboard;
- `_launcher.py` discovery by the existing OpenWave CLI.

## Acceptance

- exactly the three validated sectors are registered;
- all committed ledgers pass;
- all selected metric paths resolve;
- every panel includes established and excluded claims;
- no preset defaults to electron, positron, photon, or Standard Model naming;
- headless JSON and PNG exports are reproducible;
- launcher listing works without opening a GUI;
- package data includes preset and result ledgers.

## Scope boundary

M9.8 is instrumentation. It does not add a physical result, alter a solver,
calibrate units, or establish a particle identity.
