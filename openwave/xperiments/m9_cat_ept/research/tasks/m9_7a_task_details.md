# M9.7a task: bounded Soler spinor-carrier qualification

## Question

Can the scalar M9 carrier be replaced by a two-component spinor while preserving
localization, conservation, an explicit local-`U(1)` interface, and the existing
normalized-density entropic clock?

This is the prerequisite to the roadmap's three-dimensional replacement-carrier
gate. It is not itself a 3D or Maxwell result.

## Frozen equation

```text
i d_t Psi = -i alpha d_x Psi + beta (m - lambda bar(Psi)Psi) Psi
alpha = -sigma_2
beta = sigma_3
m = 1
lambda = 1
omega = 0.8
```

The exact solitary wave is the cubic Soler / massive Gross-Neveu profile with
`kappa = sqrt(m^2 - omega^2) = 0.6`.

## Frozen numerical method

- periodic Fourier grid;
- second-order Strang splitting;
- exact kinetic Dirac substep;
- exact pointwise nonlinear mass substep;
- refinement levels `N = 512, 1024, 2048` on `[-30,30)`;
- final time `t = 2`;
- `dt = 0.05 dx`, adjusted to end exactly at the final time.

## Localization and stability checks

1. analytic stationary residual on the exact profile;
2. phase-aligned spinor and density refinement;
3. norm and model-energy conservation;
4. window study at fixed `dx = 0.05859375`;
5. fixed 2% component-opposite periodic modulation evolved to `t = 10`;
6. free massive-Dirac control using the identical initial spinor with the nonlinear
   scalar term disabled;
7. core and boundary probability fractions.

## Local gauge-interface check

The connection is a nondynamical background used only to check covariance:

```text
Psi' = exp(i q chi) Psi
A_x' = A_x + d_x chi
```

with a periodic pure gauge `chi(x)`. The covariant energy, density, and norm must
remain invariant. No Maxwell field equation or electromagnetic self-energy is
introduced.

## Entropic-clock compatibility

The spinor-to-probability map is fixed as

```text
rho_i = Psi_i^dagger Psi_i
p_i = dx rho_i / sum_j dx rho_j.
```

The existing M9.3 channel must retain its nonincreasing remaining KL divergence,
nondecreasing accumulated gain, and closed information ledger. A pure gauge must
leave the probability vector unchanged.

## Frozen acceptance

- analytic stationary residual `<= 1e-12`;
- observed spinor and density orders `>= 1.8`;
- finest phase-aligned L2 error `<= 2e-7`;
- finest density relative L1 error `<= 1e-7`;
- finest fidelity `>= 0.999999999999`;
- norm drift `<= 2e-12` and energy drift `<= 2e-10` across refinement;
- core fraction inside `|x| <= 8` at least `0.999`;
- edge fraction at most `1e-9`;
- window variance- and peak-ratio spread at most `1e-6`;
- perturbed core fraction at least `0.999`, edge fraction at most `1e-7`,
  variance ratio in `[0.9,1.2]`, and fidelity at least `0.999`;
- free control variance ratio at least `2` and peak ratio at most `0.6`;
- pure-gauge norm, density, and covariant-energy errors below their declared
  binary64 tolerances;
- both clock trajectories contract remaining KL and close the ledger.

## Scope boundary

Passing M9.7a establishes a localized 1+1D spinor carrier and a gauge-covariant
background-connection interface. It does not establish 3D localization, a
dynamical Maxwell field, an electric charge unit, fermionic quantization, or an
electron identity.
