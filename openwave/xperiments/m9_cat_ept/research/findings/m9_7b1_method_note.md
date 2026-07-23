# M9.7b1 method note: 3D electrostatic gauge ledger

## Decision

The bounded electrostatic gauge gate passes. A normalized regular spherical
spinor-density ansatz sources a finite-volume Coulomb field whose Gauss law,
boundary flux, energy, signed sectors, window behavior, and radial information
ledger close at the declared tolerances.

This is a gauge-sector qualification, not a coupled 3D Dirac--Maxwell soliton.

## Frozen source

```text
F(r) = A exp(-r/a)
G(r) = A eta (r/a) exp(-r/a)
a = 1, eta = 1/2, epsilon0 = 1.
```

The lower component is regular at the origin. `A` normalizes the three-dimensional
number density. The signed gauge source is `rho_q = q(F^2+G^2)`.

## Refinement result

| Observable | 256 -> 512 | 512 -> 1024 |
| --- | ---: | ---: |
| Field energy | 2.00123 | 2.00029 |
| Central potential | 1.94259 | 1.97060 |

At 1024 shells:

- Gauss shell residual: `4.01e-16`;
- boundary-flux error: `1.11e-16`;
- field-energy relative error: `2.185e-5`;
- central-potential relative error: `4.199e-5`;
- source/field energy relative difference: `3.128e-6`;
- core fraction inside `r <= 8`: `0.99981907`;
- outer-20% fraction: `7.04e-8`.

The exterior Coulomb-tail energy `Q^2/(8 pi epsilon0 R)` is included. Omitting
that term gives a systematic finite-window energy deficit.

## Exact references

For the frozen parameters:

```text
raw norm = 5.497787143782138
phi(0) = 0.06252515621467317
U_E = 0.019301216292932542.
```

## Window result

At fixed `dr=1/32`, the `R=12,16,20` study gives relative spreads

```text
field energy: 3.43e-7
central potential: 1.76e-7.
```

## Signed source sectors

Changing `q` from `+1` to `-1` reverses the electric field and potential exactly
at binary64 precision, while preserving the number density and field energy. The
boundary flux equals the signed enclosed charge.

This is a dimensionless signed gauge-source result. It is not a calibration to
the electron charge.

## Perturbation response

A fixed 2% opposite modulation of the upper and lower radial components gives

```text
field-energy ratio = 1.009983
central-potential ratio = 1.011529
core fraction = 0.99981957
outer-20% fraction = 7.03e-8.
```

Gauss law and boundary flux remain closed. This tests source-to-field response;
it is not a time-dependent perturbation-stability result.

## Radial entropic-clock interface

Shell probabilities are

```text
p_i = rho_i Delta V_i / sum_j rho_j Delta V_j.
```

A reflecting doubly-stochastic nearest-neighbor channel is used because the radial
domain has an origin and an outer boundary rather than periodic endpoints. For
both base and perturbed sources, remaining KL is nonincreasing, accumulated gain
is nondecreasing, one-step correlation is nonnegative, and the information ledger
closes exactly.

## Scope

M9.7b1 does not solve the 3D radial Dirac equations or include Maxwell wave
dynamics, magnetic fields, self-consistent spinor back-reaction, an electron
identity, or a physical charge unit. M9.7b2 must solve the coupled stationary
spinor--electrostatic system with the same ledgers and an honest negative if the
bounded family fails.
