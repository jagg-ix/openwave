# M9.96 method note: charged-source and field-force closure

## Objective

Re-evaluate the three force-related partial rows on one shared field candidate:

- magnetic moment and spin `J`;
- electric force;
- magnetic force.

The campaign replaces declared charge metadata and hand-selected force kernels with a field-derived winding source, a periodic Maxwell solve, an independent magnetic-response measurement, and a three-way field-force comparison.

## M9.96a — charged stationary feasibility

The validated neutral M9.69 non-Gaussian amplitude is multiplied by a regularized phase vortex

```text
psi_n(x,y,z) = phi_0(x,y,z) tanh(r_xy/r_core)^|n| exp(i n theta)
```

with `n = 3`. Winding is measured from the resulting field on a closed periodic contour; charge is then the exact arithmetic value `q = n/3 = 1`.

Four unrelated vortex core scales are tested. Each seed is normalized, localized, and has measured winding three. The seeds are then evolved by the full unconstrained cubic--quintic imaginary-time equation used by the neutral branch.

Measured reference values:

| Quantity | Result |
| --- | ---: |
| Neutral relative stationary residual | `9.35e-4` |
| Neutral RMS radius | `1.21074` |
| Seed winding quantization error | `0` on all four seeds |
| Seed charge from winding | `1` on all four seeds |
| Best evolved charged residual | `0.51234` |
| Best evolved charged radius | `1.99868` |
| Passing charged stationary candidates | `0` |

Three of four evolved candidates retain winding three, but none simultaneously closes the stationary residual and compact-radius gates. One narrow-core seed changes sector under the unconstrained flow. The selected scalar action therefore does not construct the required charged stationary branch.

This is an explicit negative subresult for the current model, not a failed test execution.

## M9.96b — field-derived source and Maxwell closure

One winding-three candidate supplies all of the following from the same scalar field:

- charge density `rho = q |psi|^2`;
- convective phase current;
- Pauli magnetization current `curl(q S/m)`;
- scalar and vector potentials on the periodic grid;
- electric and magnetic fields.

The periodic zero mode is removed, as required by a neutral periodic cell. The resulting projected source equations close:

| Quantity | Result |
| --- | ---: |
| Integrated charge | `0.9999999999999997` |
| Poisson zero-mode projection loss | `9.56e-3` |
| Relative projected Gauss residual | `3.67e-16` |
| Relative static Ampere residual | `5.38e-16` |
| Maximum magnetic divergence | `6.94e-18` |
| Electric self-field energy | `2.026e-2` |
| Magnetic self-field energy | `2.804e-2` |

The magnetic moment is measured independently by

```text
mu_current = 1/2 integral r x j d^3x
mu_response = -d E_int(B) / dB at B = 0
```

and closes exactly at discrete precision:

```text
mu_current  = 1.4150287474588639
mu_response = 1.4150287474588639
error       = 0
```

The formal overlay adds the previously omitted gauge-invariant Pauli--Maxwell coupling and conserved-current/Maxwell witnesses. Formal availability still does not establish a stationary charged particle or physical calibration.

## M9.96c — field-force triangle

Two opposite field-derived candidates are separated on one periodic lattice. Their individual charge and current distributions generate their own electric and magnetic fields. The force on the positive source is calculated by three field-theory routes:

1. Lorentz volume force
   `integral (rho E + j x B) d^3x`;
2. derivative of the cross interaction energy;
3. flux of the cross Maxwell stress tensor through a surface enclosing one source.

Measured values at separation `16/3`:

| Quantity | Result |
| --- | ---: |
| Electric force, axial | `2.07159e-3` |
| Magnetic force, axial | `4.58535e-4` |
| Full Lorentz force, axial | `2.53013e-3` |
| Interaction-energy derivative | `2.47118e-3` |
| Maxwell-stress flux | `2.59376e-3` |
| Energy/Lorentz relative error | `2.33e-2` |
| Stress/Lorentz relative error | `2.52e-2` |
| Action--reaction relative error | `2.72e-9` |

This replaces the earlier direct use of softened Coulomb and dipole formulas for the M9.96 candidate-level closure. Those earlier formulas remain useful asymptotic controls.

## Formal evidence extension

Two exact current-tree Lean sources are added to the OpenWave formal evidence overlay:

- `FirstQuantizedQED/AnomalousMomentLinks.lean`;
- `Electromagnetic/MaxwellContinuityCovariant.lean`.

The extension records:

- the magnetic-moment/spin-projector operator link;
- gauge invariance of `sigma^(mu nu) F_(mu nu)`;
- Dirac and anomalous Pauli interaction splits;
- Maxwell-implies-continuity;
- the conditional conserved-current-to-Maxwell construction;
- gauge invariance of the Maxwell stress source.

The existing 11-graph, 422-entity, 24-source branch inventory remains unchanged. The two sources form a criterion-specific current-tree overlay.

## Status result

The three rows remain partial.

| Criterion | New closure | Remaining blocker |
| --- | --- | --- |
| Magnetic moment and spin | One winding candidate supplies charge, current, moment, and independent weak-field response | No stable charged spinorial stationary branch; no anomalous-moment derivation or physical calibration |
| Electric force | Field-derived electric source, projected Gauss law, Lorentz/energy/stress agreement | No stable charged pair or full-PDE center acceleration |
| Magnetic force | Field-derived magnetization current, static Ampere closure, magnetic contribution to the force triangle | No stable spinorial pair, dynamical torque/precession, or calibrated moment/force map |

The shared blocker is now sharper:

```text
The selected neutral scalar cubic--quintic action does not support the required
stable nonzero-winding charged branch under the tested unconstrained flow.
```

The next model target must extend the stationary equation with self-consistent gauge and/or spinorial structure rather than continuing to tune detached force kernels.
