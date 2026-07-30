# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic, second-quantized, and non-Abelian QCD comparison model to the M9 Pauli--Hartree--U(1) carrier.

## M10.1 one-particle carrier

M10.1 constructs one executable three-dimensional four-spinor state with the complete 120-element binary icosahedral group, minimally coupled U(1) fields, measured winding, the canonical axial current, algebraic Cartan contorsion and Hehl--Datta contact interaction, Yukawa mass, Compton clock, complex CAT/EPT mass, and self-consistent electromagnetic fields.

## M10.2 stationary and robustness closure

M10.2 establishes residual-reducing stationary descent, positive entropic-time advance, nested odd-grid retention of winding, norm and charge, perturbation-tube stability, interacting central-pair descent, and integrated Dirac continuity.

## M10.3 fermionic second quantization

M10.3 constructs the complete four-mode fermionic Fock realization:

```text
Fock dimension: 2^4 = 16
sector dimensions: 1, 4, 6, 4, 1
```

It establishes exact Jordan--Wigner CAR, Pauli exclusion, determinant exterior-power lifts for all 120 binary-icosahedral transformations, all 14,400 group products, creation intertwining, central sign as fermion parity, `dGamma(E_C I_4)=E_C N`, the finite fermion partition function, and occupation-dependent CAT/EPT suppression.

## M10.4 finite QCD functional and history decoherence

M10.4 couples the Fock occupation sector to all `3^4=81` histories of a four-plaquette `Z3 subset SU(3)` Wilson ensemble. It establishes the theta/confinement/Fock-entropy complex-action weight, source-coupled partitions, connected correlators, one-loop scalar functional checks, and an `81 x 81` positive environment-suppressed history decoherence matrix.

## M10.5 matrix-valued SU(3) links and color backreaction

M10.5 strictly extends the center reduction to genuine `3 x 3` link matrices generated from the eight Gell-Mann directions.

The four links of one oriented plaquette transform locally as

```text
U_xy -> G_x U_xy G_y^dagger,
P -> G_0 P G_0^dagger,
S_W = 1 - Re Tr(P)/3.
```

A normalized quark color vector supplies the traceless adjoint current

```text
J_x = |q_x><q_x| - I/3.
```

The target-end current is parallel transported to the source and the link is advanced by

```text
K_xy = J_x - U_xy J_y U_xy^dagger,
U_xy' = exp(i epsilon K_xy) U_xy.
```

The executable campaign establishes:

- Hermiticity, tracelessness and `Tr(lambda_a lambda_b)=2 delta_ab` for the eight Gell-Mann matrices;
- the representative commutator `[lambda_1,lambda_2]=2 i lambda_3` and the Jacobi identity;
- the fundamental Casimir `sum_a (lambda_a/2)^2=(4/3)I`;
- unitarity and unit determinant for every original and updated link;
- genuine link noncommutativity in every deterministic sample;
- local plaquette covariance and Wilson-action gauge invariance;
- adjoint covariance of every quark color current;
- exact reconstruction of each current from its eight color components;
- gauge covariance of the current-gradient backreaction step;
- a nonzero Wilson-action and partition response in every sampled configuration;
- source-functional first and connected second derivatives for the oriented plaquette observable.

## Exact formal authority

The one-particle and second-quantized bridges remain pinned to Physlib PRs **#41** and **#42**. The QCD and matrix-valued `SU(3)` ledgers additionally content-pin:

- `GellMannStructureConstants.gellMann_structure_constants`;
- `NonAbelianThreeVertex.three_vertex_jacobi`;
- `SuNGaugeSector.su3_adjoint_eq_gluonCount`;
- `FiniteWilsonGaugeModel.sourceCoupledPartition_linearSource_hasDerivAt_zero`;
- `QCDComplexActionUnification.qcd_theta_confinement_factorization`.

The machine-readable maps are:

```text
formal/dirac_cartan_2i_yukawa.v1.json
formal/second_quantized_fock.v1.json
formal/qcd_functional_decoherence.v1.json
formal/su3_link_backreaction.v1.json
```

## Reproduction

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import (
    run_m10_core_study,
    run_m10_closure_study,
    run_second_quantized_fock_study,
    run_qcd_functional_decoherence_study,
    run_su3_link_backreaction_study,
)
from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
import json
for result in (
    run_m10_core_study(),
    run_m10_closure_study(),
    run_second_quantized_fock_study(),
    run_qcd_functional_decoherence_study(),
    run_su3_link_backreaction_study(),
    run_model_registration_study(),
):
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
PY
```

## Next development

The next layer can place these links on a multi-plaquette periodic lattice, evolve color electric fields with a symplectic update, and compare gauge-invariant Wilson-loop and decoherence spectra across lattice refinement.
