# M9 global target plan

## Closure through M9.65

- **M9.63:** imposes two explicit dimensionless self-consistency conditions on the normalized Gaussian branch: the local density-action minimum equals the Gaussian peak density, and the variational scale derivative vanishes at the reference scale. The resulting linear system is nondegenerate and selects `alpha = 74.6630446265`, `beta = 415.7483217224`. The pair remains within 10% of M9.59 and retains localization on all three existing grids. The conditions are not yet derived from the full CAT/EPT action.
- **M9.64:** constructs the conservative spatial cubic--quintic flow with the M9.63 pair. The exact inequality `V(rho) >= -(3 alpha²/(16 beta)) rho` supplies an `H¹` a-priori bound from conserved mass and energy. Nested 16³/20³/24³ spectral evolution preserves mass to approximately `5e-13`, keeps energy drift below `6e-7`, refines, and keeps the preregistered ±4% scale orbit bounded. A kernel-formalized theorem for arbitrary `H¹` perturbations remains open.
- **M9.65:** freezes the first prediction-ready physical claim before external comparison. With the reduced Compton length as spatial anchor, the Gaussian collective-coordinate branch predicts `omega_breath / omega_Compton = 2.634371114527` with a preregistered 5% failure threshold. No external measurement was used and the prediction is not validated.

## Current cross-repository status

| Repository | Revision | Contribution |
| --- | --- | --- |
| OpenWave | `421c962fdaa4aa7359c00cd6b37f985d297f0dac` | merged M9.62 baseline and simulation evidence |
| PhysLib `entropic-physlib-linear-full` | `54b4ced090b200fac7ff04ee6a7e8797f1263049` | exact cubic continuum flows, fixed spatial-energy phase coupling, homogeneous complex semigroups, stronger kinetic PDE identities |
| ZIL | `f39758f85ee6300b8060e4f8ea1ecf344ed32c96` | evidence orchestration plus current installation/testing infrastructure |

The formal cubic continuum sector is now stronger than the prior status implied. The unresolved mathematical target is the selected **spatial differential cubic--quintic** PDE and arbitrary-`H¹` orbital theorem, not every continuum CAT/EPT flow.

## Theory status

The platform remains at 20 partial criteria, one negative, and zero validations. M9.65 changes the methodological prediction count from zero to one prediction-ready record, but does not change a platform criterion to validated. The remaining negative is the lepton-mass hierarchy.

## Next phase

| Target | Deliverable | State |
| --- | --- | --- |
| M9.66 | Derive or falsify the Gaussian peak/stationarity selection conditions from the full action, normalization, gravity, and clock stack | NEXT |
| M9.67 | Formalize spatial cubic--quintic local/global evolution, compactness modulo symmetries, and orbital stability on an `H¹` carrier | GATED |
| M9.68 | Compare the immutable M9.65 prediction against an independent higher-fidelity simulation or external measurement | PLANNED |
