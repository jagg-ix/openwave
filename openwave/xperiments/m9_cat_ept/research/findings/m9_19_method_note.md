# M9.19 method note: calibration is structurally underdetermined without an anchor

The amplitude-loss trace depends on the ratio of dimensionless rate to physical
time scale. Its Jacobian with respect to log-rate and log-time-scale therefore has
rank one. Adding an independent time-anchor row restores rank two with condition
number `2.51411`.

The synthetic roundtrip recovers the three dimensionless rates with maximum error
`5.55112e-17`. The displayed per-second values (`68000`, `92000`, and `48000`)
are consequences of the synthetic `2.5 microsecond` fixture and are not physical
measurements.

Focused validation: `9 passed`. No CI workflow was run or inspected.
