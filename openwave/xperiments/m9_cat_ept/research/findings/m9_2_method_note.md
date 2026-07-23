# M9.2 method note: free Gaussian-packet solver

## Decision

**PASS.** The periodic Crank--Nicolson implementation converges at approximately
second order to the exact free Gaussian packet while conserving the norm and
energy of its discrete Hamiltonian to roundoff.

This certifies the M9 base evolution engine. It does not produce a localized
particle: free Schrödinger evolution disperses the packet by construction.

## Equation

The numerical equation is

```text
i hbar d_t psi = -(hbar^2 / 2m) d_xx psi.
```

For the initial state

```text
psi(x,0) = (2 pi sigma^2)^(-1/4)
           exp(-(x-x0)^2/(4 sigma^2) + i k0 (x-x0)),
```

the exact state used for comparison is

```text
beta = hbar t/(2m sigma^2)
v = hbar k0/m
psi(x,t) = (2 pi sigma^2)^(-1/4) / sqrt(1+i beta)
           * exp(-(x-x0-vt)^2/(4 sigma^2(1+i beta)))
           * exp(i k0 (x-x0-vt/2)).
```

The exact density variance is `sigma^2 (1 + beta^2)`, the packet center is
`x0 + vt`, and the exact energy is

```text
E = hbar^2/(2m) * (k0^2 + 1/(4 sigma^2)).
```

## Discrete update

With the periodic centered Laplacian `D2`, each step solves

```text
(I - i hbar dt D2/(4m)) psi_(n+1)
  = (I + i hbar dt D2/(4m)) psi_n.
```

The sparse factorization of the left matrix is reused at every step. The energy
ledger uses the same operator,

```text
E_h = dx <psi, -(hbar^2/(2m)) D2 psi>.
```

This separation matters: exact conservation of `E_h` does not imply that `E_h`
already equals the continuum energy. The latter is measured by refinement.

## Frozen run

| Quantity | Value |
| --- | ---: |
| Domain | `[-20,20)` |
| Final time | `2` |
| Packet `(sigma, x0, k0, m, hbar)` | `(1, -4, 1.5, 1, 1)` |
| Refinement | `N = 128, 256, 512` |
| Time step | `dt = 0.1 dx` |
| Exact energy | `1.25` |

## Results

| N | phase-aligned L2 | density L1 | current relative L2 | fidelity | continuum-energy relative error |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 128 | 8.5237e-2 | 9.3492e-2 | 1.1339e-1 | 0.992748 | 2.7688e-2 |
| 256 | 2.1813e-2 | 2.3017e-2 | 2.8168e-2 | 0.999524 | 6.9946e-3 |
| 512 | 5.4805e-3 | 5.7241e-3 | 7.0202e-3 | 0.999970 | 1.7532e-3 |

Observed orders under each doubling:

| Observable | 128 -> 256 | 256 -> 512 |
| --- | ---: | ---: |
| phase-aligned wave function | 1.9663 | 1.9928 |
| density | 2.0221 | 2.0076 |
| current | 2.0092 | 2.0045 |

The largest norm drift is `7.40e-14`; the largest discrete-energy drift is
`9.15e-14`. The finest overlap phase error is `4.43e-3` radians. Probability in
the outer 20 percent of the periodic box is `1.20e-26`, so the comparison is not
contaminated by wraparound.

All eleven preregistered acceptance checks pass. The complete machine-readable
ledger is in `../data/m9_2_free_solver_result.json`.

## Equation-to-code map

| Mathematical object | Code |
| --- | --- |
| exact Gaussian `psi(x,t)` | `analytic_gaussian_state` |
| exact current | `analytic_gaussian_current` |
| periodic `D2` | `periodic_laplacian` |
| Crank--Nicolson update | `evolve_free_packet` |
| discrete norm | `discrete_norm` |
| probability current | `probability_current` |
| discrete energy | `discrete_energy` |
| one-level comparison | `benchmark_metrics` |
| three-level gate | `run_refinement_study` |

## Reproduction

```bash
python -m openwave.xperiments.m9_cat_ept.research.scripts.m9_2_free_solver
pytest -q tests/test_m9_free_solver.py
```

## Scope boundary

M9.2 establishes a verified free-wave control solver only. It does not establish
an entropic arrow, imaginary-potential dynamics, a soliton, a particle mass,
charge, spin, or experimental agreement. The next task must freeze the mapping
from the complex field to a probability/coarse-graining clock before measuring
any entropy monotonicity.
