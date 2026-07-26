# M9.101 findings: current formal branch to executable coupled targets

## Refreshed authorities

OpenWave starts from merged `main` commit:

```text
809ce9a152ac94e24a5f199db2473b5d8370f491
```

The current formal authority is:

```text
repository  jagg-ix/entropic-physlib-private
branch      entropic-physlib-linear-full
head        acdbe8ce6456e66837bd18604cf3107d3181c4de
Physlib.lean cf0c719c3249c48174df8923380287bcaf33f04b
```

The formal branch is 135 commits beyond the base of its latest located merged PR. The important new surfaces are not only additional declarations: they close the action derivative seam and add current clock, coupling, gauge, and metric-built interfaces.

## Formal changes recognized

### Global integrated electrogravitic action

`Curvature/GlobalElectrograviticAction.lean` now provides an actual integrated nonlinear action-data carrier. Its pointwise Fréchet derivative passes through the Lorentzian volume integral under explicit domination assumptions. A surjective variation realization makes metric, gauge, and entropic variations jointly available, and stationarity implies the metric-built Einstein--Maxwell--entropic equations.

The action density and its derivative identification remain supplied analytic data. OpenWave therefore implements a declared finite periodic reduction rather than claiming that Physlib generated the numerical density.

### G-free Newton coupling

`ComptonClock/ComptonCellNewtonConstant.lean` supplies

```text
G = hbar*c/m^2
G = hbar*c*sigma0^4, when m = 1/sigma0^2.
```

The relation removes definitional circularity but remains conditional on the Compton-cell screen model and an independently selected `sigma0`. M9.101 uses a declared natural-unit realization and preserves the ansatz-loaded status.

### Clock/action interfaces

The current branch supplies:

```text
m_clock = hbar*omega/c^2
y = sqrt(2)*hbar*omega/(c^2*v)
Sdot_I proportional to m_clock
```

plus relative-entropy entropic time and exact frequency-lapse Tolman algebra. The equations isolate a calibration map but do not predict the physical clock frequency.

### Packet spin interfaces

The gauge-invariant Pauli tensor coupling and Dirac-plus-anomaly split are exact. The T-BMT module supplies the lab scalar coefficients, anomaly frequency, magic cancellation, and rest-frame QED grounding. It explicitly retains the covariant boost/Thomas extension as imported dynamics.

## Completed executable targets

### M9.101b — coupled gauge-spinor-Hartree action

One finite periodic action now contains:

- gauge-covariant spinor kinetic energy;
- local cubic--quintic energy;
- eliminated electrostatic self-energy;
- attractive Newton/Hartree self-energy;
- transverse magnetic field energy;
- Pauli spin coupling.

A directional derivative audit compares the reduced action with its Hamiltonian pairing. A normalized imaginary-time solver operates in an explicit spin-up winding-three symmetry sector. The output reports both the symmetry-reduced residual and leakage into the omitted spin sector.

A passing reduced branch is not relabeled as unrestricted charged-particle stability.

### M9.101c — local packet Thomas--BMT

The old averaged-field rest-frame shadow is deprecated. The new adapter computes pointwise:

```text
beta(x) = j_D(x)/rho(x)
gamma(x) = 1/sqrt(1-|beta(x)|^2)
Omega_BMT(x)
Omega_BMT(x) cross s(x)
```

and integrates the local torque density. Pair and matched self-field-control rates are subtracted before comparison with the exact Dirac-generator spin rate.

The campaign separately reports whether the adapter improves on the old shadow and whether it closes within the existing generator tolerance.

### M9.101d — clock/action-rate calibration

The derivation-grid radial mode supplies `omega`. In natural units the campaign derives one Yukawa coupling and one entropy-action normalization, then carries both unchanged across the held-out grids.

The campaign checks:

- phase slope equals `omega`;
- `hbar*omega` equals the action rate;
- Yukawa mass equals Compton-clock mass;
- the frozen entropy normalization reconstructs the derivation mean rate;
- held-out grids use no normalization refit;
- frequency-lapse Tolman reconstruction closes;
- nonconstant entropy-rate modulation remains visible.

This is an internal calibration, not external clock validation.

### M9.101e — end-to-end weak-field electrogravity

At every step one spinor generates:

1. charge and Dirac/Pauli current;
2. periodic Maxwell fields;
3. matter plus electromagnetic gravitational source;
4. Newton potential using `G = hbar*c*sigma0^4`;
5. weak metric component `g00 = 1 + 2 Phi/c^2`;
6. the Hamiltonian for the next state.

The campaign checks Maxwell constraints, weak Einstein-00/Poisson closure, norm and charge preservation, metric signature, and probe-mass cancellation of gravitational acceleration.

This closes an end-to-end weak-field source/evolution chain. It does not construct a nonlinear four-dimensional Einstein Cauchy development.

## Maturity impact

The headline classes remain conditional because the new evidence closes internal or reduced axes rather than physical identity or external prediction axes.

Axis changes are:

| Criterion | Axis update |
| --- | --- |
| de Broglie clock | calibration `open -> partial` |
| magnetic moment and spin | state `not_constructed -> reduced_constructed` |
| electric force | state `not_constructed -> reduced_constructed` |
| magnetic force | state `not_constructed -> reduced_constructed` |
| gravity | state `candidate -> reduced_constructed` |

Whether the symmetry-reduced stationary gate and packet BMT numerical gate pass is recorded dynamically in the M9.101 authority. Neither outcome changes physical identity automatically.

## Remaining critical targets

1. remove the winding/spin symmetry projection and demonstrate unrestricted charged stability;
2. derive rather than import the covariant Thomas extension, or state it as an explicit independent postulate;
3. fix `sigma0`, clock frequency, Yukawa scale, and unit maps independently of the observables they are used to fit;
4. extend weak-field electrogravity to constraint-preserving nonlinear metric evolution;
5. perform external, preregistered prediction tests only after the above calibrations are frozen.
