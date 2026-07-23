# M9.6 task: scalar charge/spin no-go and replacement contract

## Question

Which particle properties are impossible to infer from the current one-component
nonrelativistic M9 scalar carrier, and what additional carrier structure is
required?

## Scope

The audit applies to the current focusing-NLS carrier. It does not claim that
every complex scalar field theory lacks a signed Noether charge or orbital angular
momentum.

## Frozen executable checks

Using a localized scalar sample with nonzero current:

1. global phase leaves density, norm, and energy unchanged;
2. complex conjugation leaves density, norm, and energy unchanged while reversing
   the probability current;
3. `H_s=(1-s)psi` contracts the localized state continuously to the zero vacuum;
4. the intrinsic scalar rotation character is `+1` at `2pi`;
5. a reference spin-1/2 character is `-1` at `2pi` and `+1` at `4pi`;
6. the carrier record contains no local U(1) connection, Gauss-law flux, or
   opposite-charge sector.

## Interpretation rules

- The nonnegative NLS norm is not identified with signed electric charge.
- Current reversal under conjugation is not sufficient for a Gauss-law charge.
- Scalar orbital angular momentum in a future higher-dimensional model would not
  supply intrinsic spin-1/2.
- Contractibility through the zero vacuum removes protected winding for the
  current localized profile.

## Replacement requirements

A charged spin-1/2 carrier must provide:

```text
local U(1) connection A_mu,
D_mu = partial_mu - i q A_mu,
Gauss-law flux tied to a source current,
opposite-charge/antiparticle sectors,
Spin(3) or Spin(1,3) representation,
2pi = -identity and 4pi = +identity,
positive density psi-dagger psi.
```

## Staged path

- M9.6A: Pauli spinor plus local U(1), for nonrelativistic spin and gauge coupling.
- M9.6B: Dirac spinor plus local U(1), for relativistic opposite-charge sectors.
- M9.6C: a separately gated nonlinear Dirac-gauge localization model.

The contract does not assert that any replacement carrier already localizes.
