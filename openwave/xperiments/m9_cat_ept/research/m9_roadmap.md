# M9 CAT/EPT roadmap

M9 is complete through the bounded transverse-radiation and shared-instrumentation
program. Interactive presentation remains separate from physical-identification
claims.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract and conformance suite | DONE |
| M9.2 | Free complex-field solver and exact Gaussian benchmark | DONE |
| M9.3 | Fixed probability map and coarse-graining clocks | DONE |
| M9.4 | Bounded scalar localization decision gate | DONE |
| M9.5 | Exact scalar scaling and observable ledger | DONE |
| M9.6 | Scalar charge/spin/topology audit | DONE |
| M9.7a | Bounded 1+1D nonlinear Dirac/Soler qualification | DONE |
| M9.7b1 | 3D spherical density and electrostatic Maxwell constraint | DONE |
| M9.7b2 | Coupled stationary radial Dirac--electrostatic solve | DONE |
| M9.7b3 | Time-dependent constrained spherical spinor--gauge evolution | DONE |
| M9.7c | Bounded transverse Maxwell--spinor qualification | DONE |
| M9.8 | Shared instrumentation, launcher, and renderer | DONE; all gates passed |
| M9.9 | Spatially transported planar Maxwell--Dirac qualification | NEXT |

## Accumulated scientific program

### Formal, scalar, and information layers

M9.1--M9.6 provide a source-pinned CAT/EPT interface, a convergent free control,
one explicit coarse-graining information clock, an exact neutral scalar soliton
family, exact scaling ledgers, and an executable boundary showing that the scalar
carrier does not supply electric charge, spin-1/2, or protected topology.

### Spinor replacement and spherical electrostatics

M9.7a replaces the scalar with an exact two-component 1+1D Soler carrier. It
passes stationary-profile, convergence, conservation, window, finite-perturbation,
free-control, background-gauge, and information-interface gates.

M9.7b1--M9.7b3 add a spherical electrostatic Maxwell constraint, a coupled
stationary radial spinor branch, and finite-time constrained dynamics. For the
selected dimensionless branch

```text
m = epsilon0 = q = N = 1
lambda = 64
omega = 0.9914633829359464
R_rms = 5.879232363303192.
```

the stationary and dynamic residual, norm, energy, Gauss, flux, convergence,
window, perturbation, localization, and radial-information ledgers pass.

### Transverse radiation

M9.7c leaves spherical electrostatics and evolves

```text
A_t = -E
E_t = -A_xx - J - sigma(x) E
B = A_x.
```

A neutral opposite-charge spinor pair supplies the transverse current while
preserving pointwise charge cancellation. The bounded reduction passes vacuum and
coupled convergence, nonzero Poynting emission, absorber accounting, corrected
energy balance, and absorber/window robustness.

### Shared instrumentation

M9.8 provides:

- deterministic `scalar-observables`, `radial-dynamics`, and
  `transverse-radiation` presets;
- one ledger and runner registry;
- common acceptance, norm, energy, Gauss, Poynting, and information panels;
- headless JSON and PNG exports;
- an interactive Matplotlib dashboard;
- `_launcher.py` discovery through the existing OpenWave CLI;
- explicit established/non-established claim labels;
- no electron, positron, photon, or Standard Model default naming.

The renderer consumes committed scientific ledgers. It does not change equations,
rerank evidence, or add a physical claim.

## Next gate: M9.9

The largest remaining gap in the bounded transverse model is the absence of
spatial spinor transport. M9.9 must add a planar transported Maxwell--Dirac system
with:

1. spatial Dirac propagation rather than pointwise spinor rotation;
2. longitudinal charge/current continuity and dynamic Gauss closure;
3. transverse electric and magnetic back-reaction;
4. norm and total-energy balance;
5. vacuum, free-spinor, and coupled refinement controls;
6. emitted-energy and absorbing-boundary ledgers;
7. a fixed localized wave-packet perturbation;
8. honest classification if the transported state disperses or radiates.

M9.9 remains a bounded planar research extension. A full 2D/3D Maxwell--Dirac
program, physical unit calibration, fermionic quantization, and particle identity
remain separate targets.
