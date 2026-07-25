# M9.99 method note: formal/numerical reconciliation

## Objective

Make OpenWave and `entropic-physlib-linear-full` comparable at the equation,
carrier, parameter, discrete-operator, and observable levels before attempting
another physical interpretation or criterion promotion.

The previous M9.97 results were not numerical counterexamples to the Lean
formalization. They mixed equations and theorem domains that were only
structurally related.

## Current formal authority

```text
repository  jagg-ix/entropic-physlib-private
branch      entropic-physlib-linear-full
```

M9.99 pins exact source blobs for:

- the current Hartree plus local-interaction mild-flow target;
- cubic--quintic coercivity and conditional orbital stability;
- the self-bound Schrödinger--Newton carrier;
- Foldy--Wouthuysen Pauli structure;
- the four-spinor Dirac algebra and velocity operator;
- Maxwell/continuity and conditional Green inversion;
- rest-frame Dirac--Pauli/T-BMT precession;
- isolated Coulomb/radiation-gauge particle dynamics;
- the distributional three-dimensional point charge.

## Equation reconciliation

The machine-readable contract records nine relations.

| Relation | Formal side | Legacy numerical side | Classification |
| --- | --- | --- | --- |
| Binding interaction | Newton/Hartree plus supplied local interaction | local cubic--quintic only | formal term missing numerically |
| Coefficients | free parameters with coercivity/closure hypotheses | Gaussian-reference selection | parameter mismatch |
| Kinetic mass | `D = 1/(2m)` in the Pauli reduction | `D = 0.65`, `m = 1` | parameter mismatch |
| Pauli Hamiltonian | FW matrix carrier with relativistic, Darwin and spin--orbit terms | nonlinear self-consistent `D_A²`, `rho`, `rho²`, and `sigma.B` PDE | different carrier/equation |
| Maxwell | isolated `R³` point source or momentum-space `F=dA` | periodic neutralized extended source | carrier mismatch |
| Discrete geometry | one derivative under all differential identities | spectral matter plus centered Maxwell | discrete-operator mismatch |
| Dirac center | `d<x>/dt = <alpha>` | `d²<x>/dt²` compared directly with `F/norm` | observable-domain mismatch |
| Spin | rest-frame vertical-field Dirac--Pauli/T-BMT bridge | moving extended packet with averaged field | observable-domain mismatch |
| Clifford algebra | canonical Dirac matrices | same numerical matrices | exact structural overlap |

## Shared Fourier differential complex

M9.99 introduces one periodic Fourier geometry using the exact symbols

```text
k_i = 2 pi fftfreq(N_i, d=h_i)
```

for all of:

- gradient;
- divergence;
- curl;
- Laplacian;
- Helmholtz projection;
- scalar and vector Poisson inversion;
- gauge-covariant matter Laplacian.

It therefore closes the discrete identities

```text
curl grad = 0
div curl = 0
div grad = Laplacian
```

within floating-point tolerance using one operator family.

The legacy centered symbol `sin(kh)/h` has eight null nodes on an even cubic
three-dimensional grid: every coordinate may independently be the zero or
Nyquist frequency. The exact Fourier Laplacian removes only the one global zero
mode and retains Nyquist modes.

## Mass and current reconciliation

The legacy stationary campaign declared

```text
D = 0.65
m = 1
```

but the nonrelativistic Pauli map requires

```text
D = 1/(2m).
```

M9.99 uses

```text
m_eff = 1/(2D) = 0.7692307692307692
```

and the convective current coefficient becomes

```text
q/m_eff = 2Dq.
```

The matter kinetic operator, Pauli current, magnetization current, and
Pauli-coupling mass now use the same effective mass.

## Hartree boundary

The current formal target includes an attractive Newton/Hartree interaction.
OpenWave has not derived a unique dimensionless coupling `G` from its existing
unit-free parameter map. M9.99 therefore exposes `G` as an explicit sweep:

```text
0.00, 0.05, 0.10
```

The zero row is the reconciled local-only control. Positive rows show how the
current formal term enters the same executable operator. None is called the
unique formal target or a calibrated physical coupling.

## Dirac observable correction

The exact four-spinor position observable is tested as

```text
d<x_i>/dt = <alpha_i>.
```

Pair and self-field-control trajectories are checked separately, followed by the
interaction difference. Momentum transfer remains compared with the
Lorentz-volume force.

The old comparison

```text
d²<x>/dt² = F/norm
```

is retained only as a nonrelativistic diagnostic because no Foldy--Wouthuysen
position projection or positive-energy packet limit has been established.

The rest-frame T-BMT shadow is similarly retained only as an out-of-domain
comparison for the moving, extended, nonuniform-field packet. The full Dirac
generator remains the spin-integration gate.

## Status impact

M9.99 completes infrastructure, not physical closure.

Closed:

- current formal equations are machine mapped to numerical terms;
- the `D`/`m`/current map is internally consistent;
- matter and Maxwell use one discrete differential complex;
- the exact Dirac center-velocity observable is measured;
- legacy center and rest-frame BMT mismatches are no longer mislabeled as Lean contradictions.

Open:

- selection of the dimensionless Hartree coupling;
- derivation of one coupled gauge-spinor action;
- a stable charged stationary branch;
- a Foldy--Wouthuysen position projection for the packet;
- a covariant local packet T-BMT law;
- physical calibration.

The comparison matrix remains:

```text
7 validated
13 partial
1 negative
```

No criterion is promoted.

## Validation limitation

The execution container cannot resolve `github.com`, so a direct clone and full
repository test run are not claimed. The PR provides deterministic unit tests,
exact source/blob contracts, synthetic Dirac-observable tests, Fourier identity
tests, and executable full-campaign runners for the repository environment.
