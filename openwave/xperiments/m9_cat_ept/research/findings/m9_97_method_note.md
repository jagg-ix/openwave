# M9.97 method note: gauge-spinor stationarity and full pair dynamics

## Objective

M9.97 tests three dynamical obligations left by M9.96:

1. whether a self-consistent electromagnetic and Pauli extension produces a charged spinorial stationary branch;
2. whether full Maxwell--Dirac kinetic-momentum transfer and center motion agree with the field-derived Lorentz force;
3. whether finite-time spin precession agrees with both the exact Dirac generator and the imported rest-frame Dirac--Pauli/T-BMT rate.

A failed reduction is retained as model evidence. It is not converted into a software-test failure or a criterion-level negative.

## M9.97a -- self-consistent gauge-spinor stationary equation

The M9.96 winding-three amplitude is embedded as

```text
Psi = (psi_3, 0)^T
```

and evolved by normalized imaginary time using

```text
H[Psi,A,phi]
  = -D (grad - i q A)^2
    + q phi
    - alpha rho
    + beta rho^2
    - (g q / 4m) sigma.B,

rho = Psi^dagger Psi.
```

At every iteration the same spinor regenerates its charge density, gauge-covariant convective current, Pauli magnetization current, scalar/vector potentials, and electric/magnetic fields. The campaign uses the selected M9.63 coefficients, `q = 1`, `m = 1`, and tree-level `g = 2`.

Measured checkpoints:

| Iteration | Relative stationary residual | Radius | Spin z |
| ---: | ---: | ---: | ---: |
| 0 | `0.5071084764` | `1.5595442312` | `0.5000000000` |
| 100 | `0.5128543258` | `1.5633543312` | `0.4999999970` |
| 300 | `0.5148664832` | `1.5712259574` | `0.4999999748` |
| 600 | `0.5190695504` | `1.5835697888` | `0.4999999088` |

The state retains winding `3`, exact-third charge `1`, normalization, localization, and spin one-half within the measured `2e-7` finite-iteration gate. Projected Gauss, static Ampere, and magnetic-divergence residuals remain below `4e-16`.

The stationary residual stays above `0.50` and increases rather than approaching the `0.10` gate.

**Result:** the explicit gauge-covariant Pauli equation is constructed and executed, but it does not construct a charged spinorial stationary branch. Static self-fields plus the selected density action are insufficient.

## M9.97b -- four-spinor Maxwell--Dirac momentum and center response

Two opposite winding-three candidates are shifted to separation `6` and embedded into positive-energy four-spinors. The Pauli fields seed only the embedding. After embedding, charge density, Dirac current, Maxwell fields, Lorentz force, and the matched control field are regenerated from the actual four-spinors evolved by the bounded Maxwell--Dirac RK4 engine.

The pair has integrated charges `+1` and `-1` to discrete precision and zero net charge.

The external Lorentz-volume force predicts

```text
F_z / norm = 0.001645074525562959.
```

The pair-minus-self-control kinetic-momentum response gives

```text
d<P_z>/dt = 0.0016022176381169852,
relative error = 0.0261161575.
```

This closes the preregistered `10%` momentum-force gate.

The independently fitted center response gives

```text
d^2<z>/dt^2 = -0.0002424759822742363,
relative error from the positive Lorentz momentum rate = 1.1473951353.
```

The center response has the wrong sign and differs by more than `100%`; it is not merely a noisier estimate of the closed momentum transfer.

**Result:** kinetic-momentum transfer is a closed dimensionless subreduction. Center acceleration fails both sign and magnitude gates and blocks electric-force promotion.

## M9.97c -- spin generator and rest-frame BMT comparison

The pair is initialized with spin along `x`. The finite-time interaction-induced spin rate is compared with:

1. the interaction part of the exact instantaneous Dirac generator used by the PDE;
2. the rest-frame Pauli/T-BMT shadow `dS/dt = (g q / 2m) S x B_eff`.

Using the shortest preregistered four-sample fit window:

```text
finite-time interaction spin rate, y = 1.45073921e-4
instantaneous Dirac-generator rate, y = 1.45128373e-4
relative vector error = 0.0257324740
```

The full-generator integration closes under the `3%` gate.

The rest-frame Pauli/T-BMT prediction is

```text
rest-frame BMT rate, y = -8.69424870e-5
relative vector mismatch = 2.6689649932.
```

It has the opposite transverse sign and a materially different magnitude for the moving, spatially extended winding packet.

This matches the formal boundary: PhysLib proves rest-frame Dirac--Pauli precession and equality with the rest-frame T-BMT rate, while the covariant boost/Thomas extension and full moving-packet reduction remain outside that theorem.

**Result:** numerical integration of the exact Dirac generator closes. Reduction to the rest-frame BMT torque does not close and blocks magnetic-moment and magnetic-force promotion.

## Formal dynamics overlay

M9.97 blob-pins and imports:

- `MuonAnomaly/ThomasBMTMagicCancellation.lean`;
- `ParametrizedTetradGravity/EMParticleDynamics.lean`;
- `Electromagnetism/PointParticle/ThreeDimension.lean`.

The imported declarations cover Heisenberg precession from the Dirac--Pauli dipole Hamiltonian, rest-frame T-BMT equality, the QED coupling/operating-point chain with its loop-value boundary, exact Coulomb symmetry, radiation-gauge Helmholtz decomposition, and a distributional point-charge electric field with Gauss source.

The overlay fails closed on missing or changed source blobs and promotes no physical criterion.

## Status impact

| Criterion | New closed subreduction | Retained blocker |
| --- | --- | --- |
| Magnetic moment and spin | finite-time spin follows the exact Dirac generator within `2.57%` | no stationary charged spinor; rest-frame/covariant BMT reduction, anomaly, identity, and calibration open |
| Electric force | four-spinor kinetic-momentum transfer agrees with Lorentz force within `2.61%` | center response has wrong sign; no stable pair or physical unit map |
| Magnetic force | full-generator precession and magnetic force contribution are nonzero | rest-frame/covariant spin-torque reduction, stable pair, and calibration open |

The global comparison matrix remains:

```text
7 validated
13 partial
1 negative
```

## Next target

The next target should construct an independently varied coupled action that can supply:

1. a converged charged spinorial stationary branch;
2. a controlled relation between kinetic momentum and center motion;
3. a covariant moving-packet spin law derived from the same action;
4. refinement across grid, time step, box size, separation, and spin orientation.
