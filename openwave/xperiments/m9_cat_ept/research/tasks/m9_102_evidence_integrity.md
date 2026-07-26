# M9.102 task: evidence integrity and reproducibility

## Objective

Correct three evidence-authority gaps discovered after merged PR #92.

## Target A — formal authority drift

Preserve `acdbe8ce6456e66837bd18604cf3107d3181c4de` as the exact historical PR #92 formal pin and register `eba0124fcfbc1216d973bb6f504c5a6d324de60c` as the live `entropic-physlib-linear-full` authority.

Acceptance:

- both heads and root blobs are exact;
- the six-commit drift is explicit;
- the eleven M9.101 physics-source blobs remain pinned;
- the three new governance sources are pinned;
- historical reproduction is not called live branch resolution.

## Target B — carrier/state separation

Record equation, solver, adapter, and evolution implementation independently from state existence.

Acceptance:

- the three spin/force rows remain `not_constructed` if the symmetry-reduced stationary-state gate is false;
- they advance to `reduced_constructed` only if that gate is true;
- packet-adapter implementation does not imply packet-reduction closure;
- gravity advances only on the weak-field state gate;
- identity, calibration, and external prediction axes remain unchanged.

## Target C — quantitative snapshot contract

Generate four complete M9.101 result files and one deterministic manifest.

Acceptance:

- exact schemas and required quantitative paths are checked;
- every full component payload receives a SHA-256 hash;
- campaign-level passage and physical sub-gates are both present;
- any changed measurement changes the corresponding component hash;
- a verifier rejects missing files, missing fields, hash drift, or summary drift.

## Scope boundary

This task changes evidence governance and reproducibility. It does not solve unrestricted charged stability, packet T-BMT closure, independent physical calibration, or nonlinear Einstein evolution.
