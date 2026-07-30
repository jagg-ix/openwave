# OpenWave M13 CAT/EPT scale-dilation and holographic-amplitude model

M13 isolates the exact scale geometry underlying the CAT/EPT entropic-time arc, applies it to the M11 pointwise/infinite-mode carrier, and then composes that scale line with the finite AdS/CFT, twistor, BCJ-QCD and Wilson-loop theorem surfaces of `entropic-physlib-linear-full`.

## Lineage

| Milestone | Executable result |
| --- | --- |
| M13.1 | dilation/Noether group, invariant logarithmic metric, block-spin ladder, `sqrt(2)` half-step, M11 soliton/tensor scale transport |
| M13.2 | GKP/RT and extended AdS/CFT checks, projective twistor incidence, finite BCJ and primitive-QCD relations, M10 Wilson-loop reuse and ABJM Wilson algebra |
| M13.3 | Yukawa mass and Compton clock transported by the dilation group with invariant mass-radius product and GKP dimension |

## M13.1 scale and carrier surface

- dilation group `lambda(t) = exp(H t)`, including composition and inverses;
- scale Lagrangian `L = 1/2 (lambda_dot/lambda)^2` and common-dilation invariance;
- Euler--Lagrange residual `lambda_ddot lambda - lambda_dot^2`;
- conserved Noether charge `Q = lambda_dot/lambda = H`;
- invariant scale metric `d(x,y) = |log(x/y)|` and exact log-coordinate transport;
- entropic proper distance `r = lambda_C log K`;
- block-spin ladder `a_n = 2^n a_0`, `sqrt(2)` half-step and continuous `2^r` geodesic;
- pointwise-soliton and finite-cutoff infinite-mode Liouville-tensor transport.

## M13.2 holographic amplitude closure

### AdS/CFT

- GKP--Witten mass/dimension relation, BF stability margin and conformal roots;
- bulk-to-boundary kernel covariance and normalized noncoincident boundary limit;
- cubic contact Witten-density/Jacobian covariance;
- finite regularized source response and Hessian;
- Ryu--Takayanagi regulated semicircle length, Brown--Henneaux prefactor, vacuum and BTZ adjacent-interval strong subadditivity;
- Regge/hydrogen, Cutkosky and Gegenbauer conformal dimensions and operator tower;
- finite-baryon-density second-order transition and mean-field scaling;
- Lovelock on-shell, Wald-area and symplectic-flow coefficient termination on AdS.

### Twistor and amplitudes

- projective Weyl/twistor direction and scale-invariant nullity;
- Penrose incidence with a Hermitian spacetime point implies a null twistor;
- the `SL(2,C)` spinor action agrees with the boundary Möbius action;
- color and kinematic Jacobi identities;
- finite BCJ gauge and double-copy amplitudes and color replacement;
- primitive-QCD forward/backward BCJ equivalence, three-point closure and supplied contour-residue obligations.

### Wilson observables

- reuses M10.8 nested-lattice SU(3) Wilson loops, area/perimeter fit, Creutz ratio, Polyakov-center and gauge-invariance diagnostics;
- checks finite Wilson damping/source-insertion authority;
- checks ABJM effective Planck constant, positive/factorized Fermi-gas kernel, convergence range and normalized `1/6` Wilson-loop algebra.

## M13.3 Yukawa--dilation--GKP bridge

- holds the supplied Yukawa coupling fixed while the Higgs scale and mass transform inversely under the scale flow;
- scales the AdS radius oppositely, preserving the dimensionless mass-radius product and both GKP conformal roots;
- checks the isolated Yukawa/Compton-clock identity;
- keeps the Weyl--Cartan dilatonic charge distinct from the global dilation group.

## Claim boundary

M13.3 remains a finite adapter over the M13.2 closure. It does not derive the Yukawa coupling, the inverse-mass scale law, AdS/CFT, or a dilaton gauge theory. The Weyl--Cartan dilatonic charge is recorded separately from the global dilation group.

## Formal authority

`jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, TIP `8bafa9ab93cbb39e85909fc3837bb4b6e0dec748`. The M13.3 ledger pins the Yukawa, dilation, GKP and Weyl--Cartan source blobs.

## Reproduction

```bash
PYTHONPATH=. python - <<'PY'
from openwave.xperiments.m13_scale_dilation_soliton import run_m13_model_study
import json
print(json.dumps(run_m13_model_study(), indent=2, sort_keys=True, default=str))
PY
```
