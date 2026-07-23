# M9.5 method note: soliton scaling and phase-clock ledger

## Decision

M9.4's reference state belongs to an exact two-parameter dimensionless family.
M9.5 verifies the family identities over nine `(g,N)` members and records the
phase-frequency bridge without converting it into a mass prediction.

## Exact family

For

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi,
```

the norm-`N` bright soliton is

```text
eta = gN/2,
phi = eta/sqrt(g) sech(eta x),
psi = phi exp(i eta^2 t/2).
```

The reference M9.4 member is `g=2`, `N=1`, hence

```text
eta = 1,
amplitude = 1/sqrt(2),
mu = -1/2,
omega_phase = 1/2,
E = -1/6,
R_rms = pi/(2 sqrt(3)) = 0.9068996821.
```

## Numerical verification

All frozen checks pass.

Maximum errors across the nine-member ledger:

| Check | Maximum error |
| --- | ---: |
| Norm relative error | `2.55e-14` |
| Energy relative error | `7.56e-14` |
| RMS-radius relative error | `4.18e-12` |
| Stationary residual relative L2 | `2.79e-16` |
| 90% enclosed probability | `6.62e-4` |
| 99% enclosed probability | `4.24e-5` |
| `omega R_rms^2 = pi^2/24` | `0` |
| `E/(mu N) = 1/3` | `0` |

Observed exponents at fixed `g=2` are

```text
eta proportional to N^1,
omega_phase proportional to N^2,
|E| proportional to N^3,
R_rms proportional to N^-1.
```

The fitted exponents differ from `1,2,3,-1` by at most `4.45e-16`.

## Conditional Compton and Zitterbewegung bridges

Let `L0` and `T0` be the physical length and time units. Matching the kinetic
coefficient gives

```text
T0 = m L0^2 / hbar.
```

If the dimensionless phase frequency is additionally identified with the Compton
frequency, the reference family yields

```text
L0/lambda_C = sqrt(omega_phase),
R_rms/lambda_C = pi/sqrt(24) = 0.6412749151.
```

If it is identified with rest-frame Zitterbewegung instead,

```text
L0/lambda_C = sqrt(omega_phase/2),
R_rms/lambda_C = pi/sqrt(48) = 0.4534498411.
```

These are conditional radius ratios. They do not determine the mass, an absolute
length, or which clock identification Nature uses.

## Scope

M9.5 establishes exact dimensionless family structure. It does not establish a
physical mass, electron identity, charge, spin, 3D stability, or a CAT/EPT
derivation of the cubic interaction.
