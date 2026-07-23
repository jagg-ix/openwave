# M9.11 task: two-dimensional localization and radiative-stability decision

## Goal

Test whether a bounded four-member nonlinear Soler coupling family can reduce
spreading in the M9.10 2+1D Maxwell--Dirac model and whether the strongest member
survives a fixed perturbation and a longer radiative horizon.

## Bounded family

```text
lambda in {0,2,4,8}
M_s = m - lambda psi_s^dagger sigma_z psi_s.
```

Each survey member uses a `48x48` grid through `t=8`. The strongest member is
selected only by reduced RMS spreading.

## Fixed perturbation

For `lambda=8`:

```text
packet width factor = 1.05
momentum_y factor = 1.05
gauge seed factor = 1.10
```

The perturbation run uses `64x64` through `t=8`.

## Long-horizon gate

The unperturbed `lambda=8` member is evolved on `64x64` through `t=12`.

## Finite-time candidate gate

```text
maximum RMS ratio <= 1.42
minimum peak ratio >= 0.80
minimum core fraction >= 0.95.
```

The perturbed gate allows maximum RMS ratio `1.45` with the same peak/core limits.

## Long-time rejection gate

A particle claim is rejected when

```text
maximum RMS ratio >= 1.60
or minimum peak ratio <= 0.75.
```

All survey, perturbation, and long-time runs must also close norm, corrected
energy, final Gauss, and radiation ledgers within the frozen coarse-survey budgets.

## Required decision

Passing M9.11 means the decision procedure completed honestly. It does not require
a positive particle result. If the strongest member fails the long-time gate, the
result must explicitly reject a stable particle candidate.
