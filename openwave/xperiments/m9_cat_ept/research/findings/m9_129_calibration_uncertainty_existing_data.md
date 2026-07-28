# M9.129 — calibration, uncertainty, and existing-data reuse

This milestone advances four-clock testing without requiring a new experiment first.

1. A non-affine monotone calibration family verifies invertibility, positive derivatives, roundtrip recovery, and temporal-order preservation.
2. Monotone interval propagation transports clock uncertainties to proper-time intervals and checks whether temporal order remains robust under uncertainty.
3. A fail-closed protocol registers existing Page–Wootters and relaxation datasets that can be reanalyzed with calibration/holdout separation and source digests.

## Boundary

The calibration functions and uncertainties are deterministic control fixtures. Existing papers are registered as targets but their raw data are not ingested. Physical promotion remains blocked until a qualified package is supplied and Physlib PR #38 is merged and compiler-verified.
