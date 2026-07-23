# M9 CAT/EPT canonical specification

This document is the specification of record. It separates exact formal
identities, numerical definitions, physical identifications, and open model
choices.

## 1. Exact imported identities

The first M9 contract consumes these equations from the pinned formal source:

```text
omega_C = m c^2 / hbar
omega_Z(p) = 2 sqrt(p^2 c^2 + m^2 c^4) / hbar
omega_Z(0) = 2 omega_C
lambda_C = hbar / (m c)
lambda_C omega_C = c
psi = sqrt(rho) exp(i Phi)
|psi|^2 = rho
C = D_KL(p_XY || p_X p_Y)
tau_ent = gamma C
S_I = hbar tau_ent
|W| = exp(-tau_ent)
lambda_Q = hbar^2 / 8
```

The complete theorem paths, hypotheses, commit, and Python symbols are recorded
in `../formal/entropic_spine_contract.json`.

## 2. Numerical state carrier

The dynamical carrier is a complex scalar lattice field

```text
psi : space x evolution-parameter -> Complex
rho = |psi|^2.
```

Direct Madelung variables contain `log rho` and `grad(rho)/rho`, which are
singular at nodes. A density floor may be used for diagnostics but must not
silently enter the physical evolution.

### 2.1 Certified free control dynamics

M9.2 fixes the linear control equation

```text
i hbar d_t psi = -(hbar^2 / 2m) d_xx psi
```

and implements a periodic second-order finite-difference Laplacian with a
Crank--Nicolson update. Against the exact infinite-line Gaussian packet, phase,
density and current converge at approximately second order over
`N = 128, 256, 512`. The method conserves the norm and the energy of its own
discrete Hamiltonian to roundoff.

This equation is the control solver, not the final CAT/EPT particle dynamics.
Its Gaussian solution spreads and therefore supplies no localized particle.
The nonlinear real-action sector remains an open, preregistered M9.4 choice.

## 3. Entropic clock

A simulation must declare, before a run, how its field state induces `p_XY` and
which split `X | Y` is used. Candidate mappings include a spatial bipartition, a
field/environment split, or a fixed coarse-graining kernel. The mapping is a
model choice and must be counted in the parameter/information ledger.

The finite contract tests the definition and positivity on explicit probability
tables. It does not prove that `tau_ent(t)` is monotone for an arbitrary PDE.
Monotonicity requires the corresponding Liouville and reduced-entropy hypotheses,
or a concrete data-processing theorem for the implemented channel.

M9.3 must distinguish at least three quantities:

- total correlation generated between declared subsystems;
- remaining relative-entropy disequilibrium, which contracts under an accepted
  coarse-graining channel;
- accumulated clock gain, defined from the loss of remaining disequilibrium.

They are not interchangeable clocks and need not have the same monotonicity under
free unitary evolution.

## 4. Real and imaginary action sectors

At the current stage:

- the free real Hamiltonian is certified as a numerical control;
- the nonlinear real-action functional that could localize a particle is open;
- `S_I = hbar tau_ent` is measured as an observable;
- `|W| = exp(-tau_ent)` is a formal state/path weight;
- no local equation `i hbar d_t psi = (H_R - i V_I) psi` is inferred.

A local imaginary potential would be an additional physical postulate and requires
its own formal and numerical task.

## 5. Particle acceptance gate

A field configuration counts as a candidate particle only if it passes all of:

1. finite norm and finite declared energy;
2. tail localization at a preregistered boundary threshold;
3. stationary-PDE residual or periodic-return residual;
4. convergence over at least three resolutions;
5. stability under a larger simulation window;
6. survival under preregistered perturbations;
7. a closed norm/energy/flux ledger;
8. no parameter selection outside the frozen search budget.

Failure is an honest negative result.

## 6. Explicit nonclaims

The completed M9.1--M9.2 stack does not establish:

- a particle solution;
- an electron identification;
- charge quantization;
- spin or 720-degree behavior;
- a mass spectrum;
- monotone entropic time for arbitrary unitary evolution;
- gravity or electromagnetic forces from the candidate field;
- equivalence of the global complex weight and a local dissipative PDE.
