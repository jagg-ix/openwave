# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic, second-quantized, and non-Abelian QCD comparison model to the M9 Pauli--Hartree--U(1) carrier.

## M10.1--M10.6 established lineage

- **M10.1:** four-spinor Dirac--Cartan--2I--Compton--Yukawa carrier.
- **M10.2:** stationary, refinement, perturbation and continuity closure.
- **M10.3:** finite fermionic Fock realization with CAR and fermion parity.
- **M10.4:** finite QCD functional, connected correlators and history decoherence.
- **M10.5:** matrix-valued `SU(3)` links and covariant quark-color backreaction.
- **M10.6:** periodic Hamiltonian `SU(3)` lattice with electric fields, Gauss law and reversible leapfrog.

## M10.7 fundamental-color matter and sourced Gauss law

M10.7 adds a normalized fundamental color field

```text
psi_x in C^3
```

on the periodic M10.6 link background. Its gauge-covariant hopping Hamiltonian is

```text
H psi_x = (m + 4 kappa) psi_x
          - kappa sum_mu(
              U_x,mu psi_x+mu
              + U_x-mu,mu^dagger psi_x-mu).
```

Under local transformations,

```text
psi_x -> G_x psi_x
U_x,mu -> G_x U_x,mu G_x+mu^dagger,
```

both the Hamiltonian action and the exact finite propagator transform covariantly.

The scalar and traceless color densities are

```text
n_x = psi_x^dagger psi_x
rho_x = psi_x psi_x^dagger - (n_x/3) I.
```

The source-oriented traceless color current satisfies

```text
J_x,mu = -i kappa(A_x,mu - A_x,mu^dagger)
         - Tr[-i kappa(A_x,mu - A_x,mu^dagger)] I/3,
A_x,mu = U_x,mu psi_x+mu psi_x^dagger.
```

The executable campaign closes both continuity equations:

```text
dot n_x + div j_x = 0

dot rho_x
  + sum_mu(J_x,mu - U_x-mu,mu^dagger J_x-mu,mu U_x-mu,mu)
  = 0.
```

For each matter state it solves the sourced Gauss constraint

```text
D_mu E_x,mu = g rho_x
```

as the unique minimum-norm electric solution. The solution transforms covariantly under independent local gauges.

The exact matter trajectory establishes:

- Hermiticity of the finite hopping Hamiltonian;
- local gauge covariance of the Hamiltonian and time evolution;
- exact norm and energy conservation;
- scalar and adjoint-color continuity near machine precision;
- initial and final sourced-Gauss closure;
- full rank of the finite Gauss constraint map;
- nontrivial matter transport;
- CAT/EPT Yukawa history suppression `|w|^2=exp(-2 Sdot_I t/hbar)`.

## Exact formal authority

The M10 lineage remains pinned to Physlib PRs **#41** and **#42**. M10.7 additionally content-pins:

- `YangMillsGaugeDynamics.yangMillsEquation_gauge_covariant`;
- `GellMannStructureConstants.gellMann_structure_constants`;
- `SuNGaugeSector.su3_adjoint_eq_gluonCount`;
- `MassDecoherenceProportionality.yukawaEntropyRate_eq_const_mul_mass`.

Machine-readable ledgers now include:

```text
formal/periodic_su3_hamiltonian.v1.json
formal/color_matter_gauss.v1.json
```

## Reproduction

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import (
    run_periodic_su3_hamiltonian_study,
    run_color_matter_gauss_study,
)
from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
import json
for result in (
    run_periodic_su3_hamiltonian_study(),
    run_color_matter_gauss_study(),
    run_model_registration_study(),
):
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
PY
```

## Next development

M10.8 closes Wilson-loop refinement, area/perimeter scaling, transfer-spectrum and decoherence-spectrum diagnostics across nested periodic lattices.
