# M9.14 task: 3D nonlinear localization and radiation decision

## Family

The M9.13 equations receive a per-species Soler effective mass:

```text
M_s = m - lambda psi_s^dagger beta psi_s
lambda in {0,2,4,8}.
```

## Scored studies

- survey: `16^3`, `t=3`, four couplings;
- fixed perturbation: `20^3`, `t=3`;
- long horizon: `20^3`, `t=5`.

The perturbation is

```text
packet width factor = 1.05
momentum-z factor = 1.05
gauge seed factor = 1.10.
```

## Candidate gates

Finite-time candidate:

```text
RMS ratio <= 1.55
peak ratio >= 0.55
core fraction >= 0.88.
```

Long-horizon particle gate:

```text
RMS ratio <= 1.20
peak ratio >= 0.80
core fraction >= 0.98.
```

## Procedure acceptance

- all four members complete;
- strongest member improves RMS spreading by at least `0.002`;
- finite candidate and fixed perturbation pass;
- the long-horizon particle claim is explicitly decided;
- global norm drift at most `2e-5`;
- global corrected-energy drift at most `2e-4`;
- final Gauss residual at most `1e-3` absolute and `0.55` relative;
- every member records a nonnegative emitted-energy ledger.

## Selection transparency

The coarse 3D survey was exploratory. The final improvement and long-horizon
thresholds were frozen after the first complete family run. M9.14 is a transparent
bounded decision, not a blind preregistration or a proof of stability.
