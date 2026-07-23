# M9.6 method note: scalar-carrier capability boundary

## Decision

The current M9 field supports a global `U(1)` phase symmetry and conserved scalar
norm. It does not currently derive electric charge, spin-1/2, or a topological
charge sector.

## Global versus local phase

For constant `alpha`,

```text
psi -> exp(i alpha) psi
```

leaves `|psi|^2`, the norm, and the scalar Hamiltonian unchanged. This supports a
conserved global number.

For position-dependent `alpha(x)`, the ordinary derivative transforms with an
extra gradient term. The executable check applies `exp(i kx)` to a localized
state: the norm stays fixed, while the ordinary-gradient kinetic energy changes.
A local gauge symmetry therefore requires a gauge potential and covariant
derivative; neither exists in the current M9 carrier.

Consequently, the conserved scalar norm must not be relabeled as electric charge
without a Maxwell/gauge source equation and a physical charge normalization.

## Spin representation

The current field transforms in the trivial intrinsic scalar representation:

```text
D_scalar(theta) = 1.
```

It is unchanged at both `2pi` and `4pi`. By contrast, the reference spinor factor

```text
D_spinor(theta) = exp(-i theta/2)
```

is `-1` at `2pi` and returns to `+1` only at `4pi`. M9 therefore does not contain
the representation structure needed for spin-1/2.

## Topology

The accepted `sech` profile has no declared target manifold, compactified boundary
class, or winding-number computation. This is an absent certificate, not a proof
that every multi-component scalar or order-parameter extension is topologically
trivial.

## Replacement routes

| Carrier | Supplies | Does not settle by itself |
| --- | --- | --- |
| Locally gauge-coupled complex scalar | Local `U(1)`, gauge current, charged spin-0 matter | Spin-1/2, charge-unit calibration |
| Dirac/Weyl spinor plus local `U(1)` | Double-cover spin-1/2 and fermionic gauge current | Localization, quantization/statistics implementation, CAT/EPT coupling |
| Multi-component topological order parameter | Winding and defect sectors may become available | Identification of winding with electric charge or spin |

## Scope

M9.6 is a carrier audit. It does not add a gauge field, spinor, topological target,
quantized statistics, or a Standard Model identity.
