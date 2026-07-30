# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic and second-quantized comparison model to the M9 Pauli--Hartree--U(1) carrier.

## M10.1 one-particle carrier

M10.1 constructs one executable three-dimensional four-spinor state with:

- the complete 120-element binary icosahedral quaternion set `2I`;
- a unitary `2I` action lifted to all four spinor components;
- central-pair descent of the complete spinor density from `2I` to the `A5` rotation shadow;
- a minimally coupled Dirac--U(1) operator;
- field-measured winding and normalized charge;
- the canonical gamma-matrix axial current `J5^mu`;
- algebraic Cartan contorsion `K_mu = kappa J5_mu` and the eliminated Hehl--Datta contact interaction;
- a Yukawa mass `m_Y = yv/sqrt(2)`;
- the Compton clock `omega_C = m_Y c^2/hbar`;
- the complex mass `M = m_Y + i Sdot_I/c^2`;
- the CAT/EPT entropy rate `Sdot_I = y omega_C/(2 hbar)`;
- self-consistent periodic electric and magnetic fields.

The model checks the full finite `2I` multiplication table, unitarity of all 120 Dirac lifts, the free Dirac mass-shell matrix identity, the Cartan spin-source residual, the mass-clock identity, the complex-mass entropy identity, winding quantization, charge normalization, and static Maxwell constraints.

## M10.2 stationary and robustness closure

M10.2 adds an adaptive normalized stationary solver. Each accepted line-search step strictly lowers the frozen real-operator stationary residual and advances entropic time by a positive residual-squared increment.

The closure campaign additionally establishes:

- retention of winding, norm, charge, and the mass-clock identity on `9^3`, `13^3`, and `17^3` odd grids;
- bounded localization-radius variation across those grids;
- preservation of winding and normalization inside a deterministic smooth amplitude/phase perturbation tube;
- bounded stationary residual throughout that tube;
- central-pair descent of the interacting Dirac operator, density, and Cartan contact density;
- integrated continuity closure for the real Dirac evolution on the periodic Fourier grid.

## M10.3 fermionic second quantization

M10.3 constructs the complete four-mode fermionic Fock realization of the M10 internal Dirac carrier.

The finite Fock basis has dimension

```text
2^4 = 16
```

with occupation-sector dimensions

```text
1, 4, 6, 4, 1.
```

The executable carrier establishes:

- exact Jordan--Wigner canonical anticommutation relations;
- Pauli exclusion for every internal mode;
- the determinant exterior-power lift `Gamma(U)_{I,J}=det U[I,J]`;
- unitary Fock lifts for all 120 binary-icosahedral transformations;
- functorial composition for all 14,400 group products;
- creation intertwining `Gamma(U) a_i^dagger = sum_j U_ji a_j^dagger Gamma(U)`;
- central-sign descent as fermion parity `Gamma(-U)=(-1)^N Gamma(U)`;
- the second-quantized Hamiltonian

```text
dGamma(E_C I_4) = E_C N,
E_C = hbar omega_C = m_Y c^2;
```

- the finite fermion partition function `(1 + exp(-beta E_C))^4`;
- occupation-dependent CAT/EPT suppression `exp(-2 N Sdot_I t/hbar)`.

## Exact formal authority

The one-particle bridge is content-pinned to Physlib PR **#41**, branch `agent/dirac-cartan-2i-compton-yukawa`, commit:

```text
b894a64e180b46c9bc1dd7e0100422b0cc6fb143
```

The second-quantized bridge is content-pinned to Physlib PR **#42**, branch `agent/dirac-cartan-2i-second-quantized-qcd`, commit:

```text
45269fa04dc16ae1588925f0a8c167ee9dfbc7b8
```

Its load-bearing source blob and theorem are recorded in `formal/second_quantized_fock.v1.json`:

```text
DiracCartan2ISecondQuantizedQCD.lean@033a992c8b144554c5edfdccdb4d95e7d6e4a3b9
dirac_cartan_2I_second_quantized_qcd_assembly
```

## Reproduction

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import (
    run_m10_core_study,
    run_m10_closure_study,
    run_second_quantized_fock_study,
)
from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
import json
for result in (
    run_m10_core_study(),
    run_m10_closure_study(),
    run_second_quantized_fock_study(),
    run_model_registration_study(),
):
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
PY
```

## Next development

M10.4 couples the finite Fock occupation sectors to a finite Wilson/QCD source functional, its connected correlators, the complex-action history decoherence matrix, and an explicit environment-induced suppression law.
