# M9.7c method note: transverse Maxwell--spinor radiation gate

## Decision

All three M9.7c milestones pass for the frozen planar reduction.

The implementation replaces the symmetry-enforced zero-radiation result of
M9.7b3 with a transverse gauge mode

```text
A_y(x,t), E_y(x,t), B_z(x,t)
```

whose Poynting flux can be nonzero.

## M9.7c1: vacuum Maxwell benchmark

A right-moving analytic pulse is evolved before matter is enabled. Observed
orders are

```text
A: 1.99907, 1.99989
E: 1.99347, 1.99859.
```

This validates the transverse wave operator and time integrator independently of
the spinor-current coupling.

## M9.7c2: neutral spinor-current coupling

A localized pair of local spinors has equal pointwise density and opposite
charge labels. Their transverse polarizations generate a current while total
charge remains zero.

At the finest coupled refinement level (`1024` points, `t=18`):

```text
A self-convergence order = 1.98383
E self-convergence order = 1.95569
max signed charge density = 0
max pair-norm mismatch = 0
corrected-energy relative drift = 5.14e-7
emitted energy through probes = 3.996e-5
final central field-energy fraction = 0.09896.
```

The signed charge cancellation is preserved by the symmetric local spinor
evolution. No Gauss projection is used.

## M9.7c3: radiation and absorber accounting

At `1024` points through `t=80`:

```text
emitted energy = 6.15138e-4
absorbed energy = 4.89886e-4
corrected-energy relative drift = 1.77811e-6
final field energy = 6.02595e-4
final central field-energy fraction = 0.69544.
```

A nonzero outward Poynting flux is therefore present. The conductivity layer
removes a substantial fraction of the emitted field energy while the combined
matter, field, and absorber ledger remains closed.

The three-window absorber study gives

```text
emitted-energy relative spread = 0.0042613
maximum corrected-energy drift = 1.443e-6.
```

## Selection transparency

Exploratory local runs were used to identify the sign convention error in the
initial `sigma_y` expectation and to select practical absorber durations and the
central-field fraction threshold. The final equations, parameters, studies, and
acceptance thresholds are committed explicitly. This is not blind
preregistration.

## Interpretation

M9.7c establishes:

- transverse electric and magnetic field evolution;
- a nonzero-capable Poynting flux;
- two-way energy exchange with a neutral spinor-current pair;
- dynamic zero-charge Gauss closure without electrostatic projection;
- absorbing-boundary and emitted-energy accounting;
- resolution and absorber-window convergence.

It does not establish:

- spatial transport of the spinor envelope;
- a full non-spherical Maxwell--Dirac equation;
- a localized charged single-particle solution;
- electron or positron identity;
- fermionic quantization or statistics;
- derivation of the transverse reduction from CAT/EPT.

## Roadmap consequence

M9.7c is complete as a bounded transverse-radiation qualification. M9.8 may now
add research instrumentation and a launcher for the validated scalar, radial,
and transverse sectors. A future full spatial Maxwell--Dirac program remains a
separate research extension and must not be inferred from this gate.
