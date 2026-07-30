# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic, second-quantized, and non-Abelian QCD comparison model to the M9 Pauli--Hartree--U(1) carrier.

## M10.1--M10.5 established lineage

- **M10.1:** four-spinor Dirac--Cartan--2I--Compton--Yukawa carrier.
- **M10.2:** stationary descent, refinement, perturbation and continuity closure.
- **M10.3:** 16-dimensional four-mode fermionic Fock realization with CAR and fermion parity.
- **M10.4:** finite `Z3 subset SU(3)` functional, connected correlators and history decoherence.
- **M10.5:** genuine matrix-valued `SU(3)` links, local gauge covariance and quark-color backreaction.

## M10.6 periodic Hamiltonian SU(3) lattice

M10.6 places the matrix-valued links on a `2 x 2` periodic lattice. Eight oriented links carry

```text
U_x,mu in SU(3)
E_x,mu = E_x,mu^dagger
Tr(E_x,mu) = 0.
```

Each periodic plaquette is

```text
P_x = U_x,0 U_x+0,1 U_x+1,0^dagger U_x,1^dagger
```

and the Hamiltonian is

```text
H = (1/2) sum_links Tr(E_l^2)
    + beta sum_plaquettes (1 - Re Tr(P_p)/3).
```

The source-free lattice Gauss generator is

```text
G_x = sum_mu(E_x,mu - U_x-mu,mu^dagger E_x-mu,mu U_x-mu,mu).
```

A symmetric kick--drift--kick trajectory advances the fields:

```text
E_n+1/2 = E_n + (dt/2) F(U_n)
U_n+1   = exp(i dt E_n+1/2 / 2) U_n
E_n+1   = E_n+1/2 + (dt/2) F(U_n+1).
```

The reference campaign establishes:

- local plaquette covariance and Wilson-action gauge invariance;
- preservation of link unitarity and unit determinant;
- preservation of electric-field Hermiticity and tracelessness;
- source-free Gauss-law closure through the trajectory;
- relative Hamiltonian drift below `2e-8`;
- forward/backward reversibility near `1e-12`;
- nontrivial magnetic evolution;
- finite `1 x 1` and winding `2 x 1` Wilson loops.

## Exact formal authority

The M10 lineage remains pinned to Physlib PRs **#41** and **#42**. M10.6 additionally content-pins:

- `YangMillsGaugeDynamics.yangMillsEquation_gauge_covariant`;
- `WilsonLoopAreaLaw.wilsonAction_nonneg`;
- `GellMannStructureConstants.gellMann_structure_constants`;
- `FiniteWilsonGaugeModel.boltzmannFactor_le_one`.

Machine-readable ledgers:

```text
formal/dirac_cartan_2i_yukawa.v1.json
formal/second_quantized_fock.v1.json
formal/qcd_functional_decoherence.v1.json
formal/su3_link_backreaction.v1.json
formal/periodic_su3_hamiltonian.v1.json
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
    run_periodic_su3_hamiltonian_study,
)
from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
import json
for result in (
    run_m10_core_study(),
    run_m10_closure_study(),
    run_second_quantized_fock_study(),
    run_qcd_functional_decoherence_study(),
    run_su3_link_backreaction_study(),
    run_periodic_su3_hamiltonian_study(),
    run_model_registration_study(),
):
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
PY
```

## Next development

M10.7 adds dynamical fundamental-color matter, gauge-covariant hopping, link currents, sourced Gauss law and discrete continuity. M10.8 then closes Wilson-loop/refinement and confinement-spectrum diagnostics.
