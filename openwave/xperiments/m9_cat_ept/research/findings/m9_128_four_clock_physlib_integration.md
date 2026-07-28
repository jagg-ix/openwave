# M9.128 — Physlib four-clock integration

OpenWave now records the merged Physlib three-clock closure and the draft four-clock dynamics extension separately.

The executable control checks conditioned-step transport, Page–Wootters/modular/entropic/proper-time path commutation, roundtrip recovery, and strict temporal-order preservation on a deterministic affine carrier.

## Boundary

The control is not physical calibration. Promotion remains blocked until the pairwise maps and their monotonicity are independently measured, a held-out four-clock observation exists, and Physlib PR #38 is merged and compiler-verified.
