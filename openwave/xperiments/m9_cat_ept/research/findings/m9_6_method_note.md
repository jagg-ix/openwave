# M9.6 method note: scalar-carrier capability boundary

## Decision

The current M9 field has a global `U(1)` phase symmetry and conserved scalar norm.
It does not derive electric charge, an opposite electric-charge sector, spin-1/2,
or a protected topological sector.

## Global versus local phase

A constant phase leaves density, norm, phase current, and scalar energy unchanged.
The executable errors are `1.11e-16` for norm and `0` for energy.

A periodic position-dependent phase leaves norm unchanged but changes the
ordinary-gradient energy by `1.5791`. A local gauge symmetry therefore requires a
covariant derivative and gauge potential, neither of which exists in the current
carrier.

The scalar norm may be interpreted as a conserved global number. It must not be
relabeled as electric charge without a gauge source equation, Gauss-law flux, and
physical charge normalization.

## Conjugation is not opposite electric charge

Complex conjugation preserves norm and energy to roundoff and reverses the phase
current. The maximum current-reversal residual is `3.16e-12`; its `1e-11` gate is
set by the exponentially small `sech` tail on the periodic spectral grid.

This gives a reversed phase-flow state, not a positron or opposite electric-charge
sector: no gauge field, Gauss-law sign, or electric charge label exists.

## Continuous contraction and topology

The explicit path

```text
psi_s = s psi,  0 <= s <= 1
```

connects the localized profile continuously to the zero vacuum. Norm follows
`s^2`, and the scalar energy remains finite and continuous along the path. The
current profile therefore has no protected topological sector under the declared
carrier and boundary data.

This is not a theorem about every multi-component scalar extension. A nontrivial
target manifold and boundary class could support winding in a replacement model.

## Spin representation

The intrinsic scalar factor is

```text
D_scalar(theta) = 1,
```

so the field returns with `+1` after both `2pi` and `4pi`. The reference spinor
factor `exp(-i theta/2)` is `-1` at `2pi` and returns only at `4pi`. The current
carrier therefore represents spin 0, not spin-1/2.

## Density-preserving replacement contract

The staged spinor embedding

```text
Psi = (psi, 0)
```

satisfies `Psi-dagger Psi = |psi|^2` exactly. It therefore preserves the normalized
density and coarse-graining interface already used by the entropic clock.

| Carrier | Supplies | Still open |
| --- | --- | --- |
| Locally gauge-coupled scalar | Local `U(1)`, gauge current, charged spin-0 matter | Gauge dynamics, charge units, spin-1/2 |
| Dirac/Weyl spinor plus local `U(1)` | Double cover, fermionic current, gauge charge carrier | Localization, statistics layer, CAT/EPT action coupling |
| Multi-component topological order parameter | Possible winding and defects | Target manifold, boundary class, physical invariant map |

None of these replacement carriers is claimed to localize before a new numerical
gate is run.

## Scope

M9.6 is an executable carrier audit. It does not add a gauge field, spinor dynamics,
topological target, quantized statistics, electric charge, or a Standard Model
identity.
