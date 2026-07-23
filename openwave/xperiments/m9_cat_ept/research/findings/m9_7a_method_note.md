# M9.7a method note: bounded nonlinear Dirac/Soler carrier

## Decision

The two-component 1+1D Soler carrier passes the complete frozen qualification
gate. It remains localized, converges to its exact solitary-wave solution,
survives the declared perturbation, preserves the M9 normalized-density clock,
and supports a local-`U(1)` covariant background-connection interface.

The accepted object is a **localized spinor mathematical candidate in 1+1
 dimensions**. It is not yet an electron or a three-dimensional particle.

## Equation and representation

```text
i d_t Psi = -i alpha d_x Psi + beta (m - lambda bar(Psi)Psi) Psi
alpha = -sigma_2
beta = sigma_3
m = 1
lambda = 1
omega = 0.8
kappa = sqrt(m^2 - omega^2) = 0.6
```

The upper profile is even, the lower profile is odd, and both decay exponentially.
The analytic stationary residual is `1.96e-16` relative.

## Refinement result

| N | Spinor phase-aligned L2 | Density relative L1 | Fidelity |
| ---: | ---: | ---: | ---: |
| 512 | `2.42205e-6` | `1.39071e-6` | `0.9999999999961` |
| 1024 | `6.07659e-7` | `3.49092e-7` | `0.9999999999998` |
| 2048 | `1.53398e-7` | `8.72859e-8` | `0.99999999999998` |

Observed orders:

```text
spinor: 1.99490, 1.98598
density: 1.99414, 1.99979
```

At the finest level:

- norm drift: `1.69e-13`;
- model-energy drift: `1.04e-13`;
- variance ratio: `1.0000000846`;
- peak ratio: `0.9999998744`;
- core fraction inside `|x| <= 8`: `0.9998332656`;
- edge fraction: `2.82e-11`.

## Window and control discrimination

At fixed `dx = 0.05859375`, the three declared windows change the final variance
ratio by `8.23e-10` and the peak ratio by `7.56e-10`.

The identical initial spinor evolved under the free massive Dirac equation
(`lambda = 0`) disperses:

```text
variance ratio = 4.27772
peak ratio = 0.40838
```

Localization is therefore not a property of the seed alone.

## Perturbation gate

A fixed 2% component-opposite periodic modulation is normalized to the original
charge and evolved to `t = 10`. The final state retains:

- fidelity: `0.99994829`;
- variance ratio: `1.01115`;
- peak ratio: `0.99364`;
- core fraction: `0.99978987`;
- edge fraction: `3.14e-11`;
- norm drift: `7.36e-13`.

The perturbation result is a finite-time nonlinear stability test, not a proof of
orbital or asymptotic stability.

## Local gauge interface

For the periodic pure gauge

```text
Psi' = exp(i q chi) Psi
A_x' = A_x + d_x chi,
```

measured errors are:

- norm: `0`;
- density: `1.67e-16`;
- covariant energy: `2.22e-16`.

This certifies the implemented background-connection interface. The connection is
not dynamical, and no Maxwell field energy, Gauss law, charge calibration, or
opposite-charge sector is present.

## Entropic-clock preservation

The map

```text
rho_i = Psi_i^dagger Psi_i
p_i = dx rho_i / sum_j dx rho_j
```

feeds the existing M9.3 channel without modification. The initial and evolved
spinor distributions both have nonincreasing remaining KL divergence,
nondecreasing accumulated gain, nonnegative one-step correlation, and zero ledger
closure error at binary64 precision.

A pure gauge changes the probability vector by at most `6.94e-18`.

## Scope

M9.7a establishes a bounded 1+1D spinor-carrier qualification result. It does not
establish three-dimensional localization, a dynamical electromagnetic field,
electric charge units, fermionic quantization, a Standard Model identity, or a
CAT/EPT derivation of the Soler self-interaction.
