# M9.7b3 task: constrained spherical spinor--gauge dynamics

## Question

Does the normalized M9.7b2 stationary branch remain localized under a fixed
finite perturbation when evolved by the selected nonlinear Dirac equation while
the longitudinal electrostatic gauge field responds self-consistently at every
time step?

## Scope decision

The spherical sector has only a radial electric field. It has no transverse
Maxwell or magnetic degree of freedom, so its electromagnetic Poynting flux is
identically zero. M9.7b3 therefore qualifies constrained longitudinal dynamics.
A later non-spherical gate is required for Maxwell radiation.

## Frozen evolution

```text
i V_t = (d_r + 2/r) U + (q phi + M) V
i U_t = -d_r V + (q phi - M) U
M = m - lambda (|V|^2 - |U|^2)

rho = |V|^2 + |U|^2
Q(r,t) = 4 pi integral_0^r s^2 q rho(s,t) ds
E(r,t) = Q(r,t)/(4 pi epsilon0 r^2)
phi(infinity,t) = 0.
```

The inherited selected-model parameters are

```text
m = epsilon0 = q = N = 1
lambda = 64.
```

## Frozen numerical method

- shell-centered radial finite volumes;
- exact shell volumes as the physical norm weights;
- second-order radial derivative matrix;
- the `(d_r, d_r+2/r)` pair is constructed by weighted adjointness;
- local nonlinear and electrostatic phases are exact substeps;
- the kinetic substep is weighted-unitary Crank--Nicolson;
- second-order Strang composition;
- the Poisson/Gauss constraint is projected after each local substep;
- reflecting self-adjoint outer closure;
- analytic exterior Coulomb tail in the field-energy ledger.

## Frozen perturbation

```text
V -> (1 + 0.02 cos(pi r/R)) exp(+i chi(r)) V
U -> (1 - 0.02 cos(pi r/R)) exp(-i chi(r)) U
chi(r) = 0.02 sin(pi r/R).
```

The amplitudes are renormalized once at the initial time. No later
renormalization is performed.

## Refinement gate

The scored dynamic refinement uses

```text
R = 40
t_final = 5
dt = 0.1 dr
cells in {256, 512, 1024}.
```

Successive phase-aligned spinor and density differences must converge with
observed order at least `1.8`.

## Long-time perturbation gate

```text
R = 40
cells = 512
t_final = 20.
```

The state must retain:

- fidelity at least `0.999` to the stationary branch modulo global phase;
- core fraction inside `r <= 16` at least `0.985`;
- outer-20% fraction at most `2e-4`;
- norm drift at most `2e-12`;
- total-energy relative drift at most `2e-7`.

This is finite-time nonlinear stability evidence, not an orbital-stability proof.

## Window gate

At fixed `dr = 5/64`, independently converged stationary branches are evolved on

```text
R in {30, 40, 50}
```

through `t=10` with the same perturbation. Relative spreads must remain below:

- RMS radius: `1e-2`;
- central electrostatic potential: `5e-3`;
- core fraction: `1e-3`.

## Constraint and flux ledgers

- norm must be conserved by the weighted-unitary scheme;
- total selected-model energy includes matter plus longitudinal field energy;
- shellwise Gauss law must close after every sampled projection;
- continuum-form matter boundary current must remain below `1e-5` in magnitude;
- electromagnetic Poynting flux is recorded as exactly zero because `B=0` in the
  spherical electrostatic truncation.

The zero radiation flux is a negative structural result, not evidence that a full
Maxwell field is non-radiative.

## CAT/EPT interface

Final shell probabilities are

```text
p_i = rho_i Delta V_i / sum_j rho_j Delta V_j.
```

The reflecting M9 radial channel must retain nonincreasing remaining KL,
nondecreasing accumulated gain, nonnegative one-step total correlation, and a
closed information ledger.

## Scope boundary

Passing M9.7b3 establishes finite-time constrained spherical spinor--electrostatic
dynamics for the selected dimensionless model. It does not establish transverse
Maxwell waves, magnetic self-fields, non-spherical stability, fermionic
quantization, calibrated charge, electron identity, or CAT/EPT derivation of
`lambda=64`.
