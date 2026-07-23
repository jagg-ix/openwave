# M9.6 method note: scalar carrier limitations

## Decision

The current one-component nonrelativistic scalar carrier supports a positive
density, phase, current, norm, energy, localization, and the M9 entropic-clock
map. It does not supply signed electric charge or intrinsic spin-1/2.

All frozen executable checks pass.

## Charge audit

For the sampled localized state:

- a global phase changes neither density, norm, nor energy;
- complex conjugation changes neither density, norm, nor energy;
- conjugation reverses the probability current;
- the norm remains nonnegative in both sectors;
- no gauge field or Gauss-law flux is present;
- no separately represented opposite-charge sector exists.

Therefore the current norm/current pair cannot be promoted to signed electric
charge. Reversing a flow direction is not the same as reversing a gauge source.

## Topology audit

The current target includes the zero vacuum. The explicit homotopy

```text
H_s(x) = (1-s) psi(x),  0 <= s <= 1,
```

contracts the localized profile to zero. The midpoint norm is exactly one quarter
of the original norm, as expected from amplitude scaling. The present soliton has
no protected winding invariant.

## Spin audit

The intrinsic scalar rotation representation is trivial:

```text
R_scalar(2pi) = +1.
```

A reference spin-1/2 representation has

```text
R_spinor(2pi) = -1,
R_spinor(4pi) = +1.
```

A future scalar field could carry orbital angular momentum through spatial phase
structure, but this would not create intrinsic spin-1/2.

## Replacement contract

The packaged target is a Dirac spinor with local U(1):

- four complex components;
- `Spin(1,3)` transformation law;
- local connection and covariant derivative;
- Gauss-law flux observable;
- opposite-charge sectors;
- positive density `psi-dagger psi`, preserving the CAT/EPT probability interface.

The staged route begins with Pauli+U(1), advances to Dirac+U(1), and only then
attempts a separately preregistered three-dimensional localization model.

## Scope

This result does not claim that every complex scalar QFT lacks signed charge,
that scalar fields cannot carry orbital angular momentum, or that the proposed
replacement carrier automatically localizes.
