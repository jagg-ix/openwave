# M9.7b2 method note: coupled radial spinor and electrostatic field

## Decision

The frozen normalized spherical Soler--electrostatic system has a nontrivial
localized stationary branch. The spinor determines the electrostatic source and
the resulting potential appears in the same stationary Dirac equation.

The result is a positive **selected-model stationary solution**, not an electron
calculation.

## Reference solution

For

```text
m = epsilon0 = q = N = 1
lambda = 64
R = 40,
```

the finest scored solve gives

```text
omega = 0.9914633829359464
v(0) = 0.07365091100207258
phi(0) = 0.024408951727442642
R_rms = 5.879232363303192.
```

The unit normalization excludes the zero solution. The frequency lies inside the
mass gap and the spinor tail decays exponentially.

## Refinement

Successive differences show near-fourth-order collocation convergence:

| Observable | Observed order |
| --- | ---: |
| Spinor volume-L2 | `3.95999936` |
| Density volume-L1 | `3.95865476` |
| Frequency | `3.96436926` |

At the finest level:

```text
BVP collocation residual = 5.7785e-7
independent spinor residual = 2.8273e-7
number norm = 1.0000000000740235
signed total charge = 1.
```

## Maxwell and energy closure

```text
relative Gauss residual = 3.0123e-6
potential residual = 3.6943e-9
boundary-flux error = 2.9851e-8.
```

The electrostatic energy is

```text
field ledger = 0.007752284287965573
source-potential ledger = 0.007752284291468033
relative mismatch = 4.5180e-10.
```

The matter and total selected-model energies are

```text
E_matter = 1.0115160502925487
E_total = 1.0192683345805142.
```

The independently evaluated stationary eigenvalue identity closes to
`5.7230e-8` relative.

## Localization and window behavior

At `R=40`:

```text
fraction inside r <= 16 = 0.98942404
outer-20% fraction = 7.9131e-5.
```

At fixed radial spacing, the `R={30,40,50}` relative spreads are

```text
frequency = 7.3787e-6
central potential = 3.5742e-5
RMS radius = 2.3186e-3.
```

A fixed 5% opposite modulation of the initial upper/lower numerical guess
converges to the same branch to below `1e-16` in frequency and profile metrics.
This checks the local solver basin only; it does not establish dynamical or orbital
stability.

## Signed source sectors

The equations depend on the electrostatic sector through `q phi`. Therefore

```text
q -> -q
Q -> -Q
phi -> -phi
```

leaves the stationary spinor and field energy unchanged while reversing signed
charge and boundary flux. This supplies opposite dimensionless source sectors,
not a calibration to the electron and positron charges.

## Radial entropic-clock interface

Shell probabilities use

```text
p_i = (v_i^2 + u_i^2) Delta V_i / N.
```

The reflecting M9.7b1 channel gives

```text
initial remaining KL = 1.3246787392
terminal remaining KL = 1.2983468645
accumulated gain = 0.0263318747
ledger closure error = 0.
```

The density-to-clock interface therefore survives the coupled stationary solve.
Channel depth remains a coarse-graining order, not physical time.

## Selection transparency

A non-scoring exploratory continuation was used to locate the `lambda=64` branch
and establish solver tolerances. The scored family was then frozen. The coupling,
normalization, and dimensionless charge are model inputs and are not predictions.

## Scope

M9.7b2 establishes a localized normalized stationary solution for the selected
3D spherical nonlinear Dirac equation with self-consistent electrostatic
back-reaction. It does not establish:

- time-dependent perturbation stability;
- magnetic fields or Maxwell radiation;
- an absolute mass, length, or electric-charge unit;
- an electron or positron identity;
- fermionic anticommutation or statistics;
- unique derivation of the Soler interaction from CAT/EPT;
- irreversible dynamics from the imaginary-action layer.
