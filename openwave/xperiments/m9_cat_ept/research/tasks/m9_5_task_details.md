# M9.5 task: exact soliton scaling and clock ledger

## Question

What does the accepted M9.4 bright soliton determine exactly, and which physical
quantities remain calibrations?

## Frozen equation

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi,  g > 0.
```

For conserved scalar norm `N > 0`, the tested family is

```text
eta = g N / 2
phi(x) = eta/sqrt(g) sech(eta x)
psi(x,t) = phi(x) exp(i eta^2 t / 2).
```

No new interaction or coefficient is introduced in M9.5.

## Exact targets

```text
mu = -eta^2/2
omega_phase = eta^2/2
E = -eta^3/(3g) = -g^2 N^3/24
R_rms = pi/(2 sqrt(3) eta)
FWHM_density = 2 acosh(sqrt(2))/eta
P(|x| <= R) = tanh(eta R).
```

The exact invariant and energy relation are

```text
omega_phase R_rms^2 = pi^2/24
E/(mu N) = 1/3.
```

## Tested family

The quadrature ledger covers all nine products

```text
g in {1, 2, 4}
N in {0.5, 1, 2}.
```

Each member is integrated on the same scaled interval `|eta x| <= 16` using
8193 points.

## Frozen acceptance

- norm, energy and RMS-radius relative errors `<= 1e-10`;
- stationary residual relative L2 `<= 1e-12`;
- 90% and 99% enclosed-probability errors `<= 2e-3`;
- invariant and energy-relation errors `<= 1e-12`;
- observed norm-scaling exponents agree with `1, 2, 3, -1` to `1e-12`.

## Clock bridge rule

The dimensionless phase frequency is not a mass prediction. Two optional unit-map
hypotheses are recorded only as conditional identities:

- identify the physical phase frequency with `omega_C = mc^2/hbar`;
- identify it with rest-frame `omega_Z = 2mc^2/hbar`.

Neither hypothesis fixes `m`, `L0`, or an absolute energy scale independently.
