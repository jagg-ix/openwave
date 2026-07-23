# M9 CAT/EPT canonical specification

This document separates exact identities, numerical results, physical
identifications, and open model choices.

## 1. Formal CAT/EPT interface

The pinned contract supplies

```text
psi = sqrt(rho) exp(i Phi),
|psi|^2 = rho,
tau_ent = gamma C,
S_I = hbar tau_ent,
|W| = exp(-tau_ent),
omega_C = mc^2/hbar,
omega_Z(0) = 2 omega_C.
```

These identities do not select a particle equation or unit map.

## 2. Numerical carrier and controls

The current carrier is a one-component complex scalar field. M9.2 certifies the
free Schrödinger control. M9.3 fixes the cell-probability map and one periodic
coarse-graining channel. Channel depth remains distinct from physical time.

## 3. Localized nonlinear family

M9.4 selects the dimensionless focusing equation

```text
i psi_t = -1/2 psi_xx - g |psi|^2 psi,  g > 0.
```

The interaction is an explicit model input, not a consequence of the formal
imaginary action.

### 3.1 Exact norm-`N` family

M9.5 records

```text
eta = gN/2,
phi(x) = eta/sqrt(g) sech(eta x),
psi(x,t) = phi(x) exp(i eta^2 t/2).
```

It satisfies

```text
mu = -eta^2/2,
omega_phase = eta^2/2,
E = -eta^3/(3g) = -g^2 N^3/24,
R_rms = pi/(2 sqrt(3) eta),
FWHM_density = 2 acosh(sqrt(2))/eta,
P(|x| <= R) = tanh(eta R).
```

The reference M9.4 member is `g=2`, `N=1`:

```text
eta = 1,
amplitude = 1/sqrt(2),
mu = -1/2,
omega_phase = 1/2,
E = -1/6,
R_rms = pi/(2 sqrt(3)).
```

Nine family members verify the norm, energy, radius, stationary equation, and
scaling exponents. Two exact relations are

```text
omega_phase R_rms^2 = pi^2/24,
E/(mu N) = 1/3.
```

### 3.2 Status of the phase clock

`omega_phase` is the rotation frequency of the dimensionless stationary state.
It is not by itself a Compton or Zitterbewegung frequency.

Let `L0,T0` be physical units. Matching the kinetic coefficient gives

```text
T0 = m L0^2/hbar.
```

Under an additional Compton identification,

```text
R_rms/lambda_C = pi/sqrt(24).
```

Under an additional rest-frame Zitterbewegung identification,

```text
R_rms/lambda_C = pi/sqrt(48).
```

These are conditional consistency ratios. They do not determine `m`, an absolute
radius, or which identification is physical.

## 4. Entropic clock

M9.3 fixes

```text
p_i = dx |psi_i|^2 / sum_j dx |psi_j|^2,
(Kp)_i = 1/4 p_{i-1} + 1/2 p_i + 1/4 p_{i+1}.
```

Remaining KL disequilibrium contracts and accumulated discarded information
grows along channel depth. This is data processing, not unitary-time monotonicity.

## 5. Real and imaginary action sectors

- the free and focusing real Hamiltonians are explicit numerical models;
- the focusing cubic term is not derived from CAT/EPT;
- `S_I` and `|W|` remain formal weighting observables;
- no local imaginary potential or irreversible back-reaction is inferred.

## 6. Current evidential status

Established:

- a source-pinned formal interface;
- a convergent free control solver;
- one explicit coarse-graining information clock;
- one stable, exact, neutral 1+1D scalar soliton family;
- exact dimensionless scaling and conditional clock-radius ratios.

Not established:

- electron, positron, photon, or other Standard Model identity;
- signed electric charge, Gauss flux, or antiparticle sector;
- intrinsic spin-1/2 or 720-degree behavior;
- three-dimensional existence or Derrick escape;
- physical mass or absolute unit calibration;
- necessity of the focusing cubic interaction;
- irreversible physical-time evolution from the imaginary action.

M9.6 must convert the charge/spin limitations into executable no-go checks and a
replacement-carrier contract.
