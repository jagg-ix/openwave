# M9 CAT/EPT canonical specification

This document is the specification of record. It separates exact formal
identities, numerical definitions, physical identifications, and open model
choices.

## 1. Exact imported identities

The pinned M9 formal contract consumes:

```text
omega_C = m c^2 / hbar
omega_Z(0) = 2 omega_C
lambda_C omega_C = c
psi = sqrt(rho) exp(i Phi)
|psi|^2 = rho
C = D_KL(p_XY || p_X p_Y)
tau_ent = gamma C
S_I = hbar tau_ent
|W| = exp(-tau_ent)
lambda_Q = hbar^2 / 8.
```

The theorem paths, hypotheses, source commit, and Python symbols are recorded in
`../formal/entropic_spine_contract.json`. These identities do not select a
particle Lagrangian.

## 2. Numerical state carrier

The dynamical carrier is a complex scalar lattice field

```text
psi : space x evolution-parameter -> Complex
rho = |psi|^2.
```

Direct Madelung evolution is avoided because `log rho` and `grad(rho)/rho` are
singular at nodes. No density floor enters the physical equations.

### 2.1 Certified free control dynamics

M9.2 fixes the linear control equation

```text
i hbar d_t psi = -(hbar^2 / 2m) d_xx psi.
```

A periodic second-order finite-difference Laplacian and Crank--Nicolson update
converge at approximately second order to the exact Gaussian packet. Norm and
the energy of the discrete Hamiltonian are conserved to roundoff. The Gaussian
spreads, so this layer is explicitly a nonparticle control.

### 2.2 First nonlinear localization family

M9.4 fixes the bounded dimensionless family

```text
i psi_t = -1/2 psi_xx + kappa |psi|^2 psi,
kappa in {0, +2, -2}.
```

Every member receives the same normalized `sech(x)` seed. The free and
defocusing members disperse. The focusing member admits

```text
psi_*(x,t) = sech(x) / sqrt(2) * exp(i t/2),
kappa = -2,
mu = -1/2,
E = -1/6.
```

The candidate passes convergence, stationary residual, conservation, tail,
window, shape, and perturbation-survival gates. Its classification is limited to
**localized neutral mathematical candidate in 1+1 dimensions**.

The cubic term is not derived by the formal CAT/EPT layer. Its inclusion is an
explicit model choice and therefore part of the freedom ledger.

## 3. Entropic clock

### 3.1 Fixed field-to-probability map

M9.3 fixes, without adaptive bins or phase information,

```text
p_i = dx |psi_i|^2 / sum_j dx |psi_j|^2.
```

### 3.2 Fixed coarse-graining channel

The declared periodic Markov channel is

```text
(Kp)_i = 1/4 p_{i-1} + 1/2 p_i + 1/4 p_{i+1}.
```

It is doubly stochastic and fixes the uniform distribution. Three quantities are
kept distinct:

```text
I_n = I(X_n ; X_{n+1})
D_rem(n) = D_KL(p_n || uniform)
G_acc(n) = D_KL(p_0 || uniform) - D_rem(n).
```

Under repeated channel application, `D_rem` contracts and `G_acc` grows. The
ledger `D_rem(0) = D_rem(n) + G_acc(n)` closes. One-step total correlation is
nonnegative but is not assumed monotone.

**Channel depth is not physical time.** M9.3 proves no irreversible arrow for the
unitary M9.2 or M9.4 evolution parameter.

## 4. Real and imaginary action sectors

At the current stage:

- the free real Hamiltonian is a certified control;
- the focusing cubic functional supplies the first accepted mathematical
  localization mechanism;
- no theorem derives that cubic functional from `S_I` or the entropic clock;
- `S_I = hbar tau_ent` and `|W| = exp(-tau_ent)` remain weighting observables;
- no local equation `i hbar d_t psi = (H_R - i V_I) psi` is inferred.

A local imaginary potential or dissipative back-reaction remains a separate
physical postulate and formalization target.

## 5. Particle acceptance gate

The M9.4 candidate was required to pass:

1. finite norm and finite declared energy;
2. exponentially small boundary probability and dominant core probability;
3. stationary-equation and phase-return residuals;
4. convergence over `N = 256, 512, 1024`;
5. consistency over three larger/smaller windows at fixed spacing;
6. survival of a fixed 5% shape perturbation;
7. closed norm and energy ledgers;
8. dispersal of the identical seed in both bounded controls.

This is enough to classify a mathematical localized state. It is not enough to
classify a physical elementary particle.

## 6. Open physical obligations

The completed M9.1--M9.4 stack does not establish:

- an electron, positron, photon, quark, or other Standard Model identity;
- electric charge or a topological charge invariant;
- spin, spin-1/2 statistics, or a 720-degree return;
- three-dimensional existence or stability;
- a dimensional unit map or an independently predicted mass;
- a physical Compton-clock identification for the soliton phase;
- monotone entropic time under unitary physical evolution;
- gravity or electromagnetic forces from the candidate;
- uniqueness or necessity of the focusing cubic term;
- equivalence of the global complex weight and a local dissipative PDE.

M9.5 must characterize the soliton scaling family and separate definitions,
calibrations, identities, and predictions before any particle-scale comparison.
