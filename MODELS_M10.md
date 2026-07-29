# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic comparison model to the M9 Pauli--Hartree--U(1) carrier.

## M10.1 carrier

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

## M10.2 closure

M10.2 adds an adaptive normalized stationary solver. Each accepted line-search step strictly lowers the frozen real-operator stationary residual and advances entropic time by a positive residual-squared increment.

The closure campaign additionally establishes:

- retention of winding, norm, charge, and the mass-clock identity on `9^3`, `13^3`, and `17^3` odd grids;
- bounded localization-radius variation across those grids;
- preservation of winding and normalization inside a deterministic smooth amplitude/phase perturbation tube;
- bounded stationary residual throughout that tube;
- central-pair descent of the interacting Dirac operator, density, and Cartan contact density;
- integrated continuity closure for the real Dirac evolution on the periodic Fourier grid.

## Exact formal authority

The formal bridge is content-pinned to Physlib PR **#41**, branch `agent/dirac-cartan-2i-compton-yukawa`, commit:

```text
b894a64e180b46c9bc1dd7e0100422b0cc6fb143
```

The load-bearing theorem sources are pinned by Git blob and declaration name in `openwave/xperiments/m10_cat_ept/formal_authority.py`:

- `BinaryIcosahedralDiracSpinor.binary_icosahedral_dirac_spinor_assembly`;
- `EinsteinCartanAxialTorsion.dirac_cartan_axial_elimination_assembly`;
- `DiracCartanComptonYukawaBridge.dirac_cartan_2I_compton_yukawa_assembly`.

The machine-readable equation map is `openwave/xperiments/m10_cat_ept/formal/dirac_cartan_2i_yukawa.v1.json`.

## Reproduction

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import run_m10_core_study, run_m10_closure_study
from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
import json
print(json.dumps(run_m10_core_study(), indent=2, sort_keys=True, default=float))
print(json.dumps(run_model_registration_study(), indent=2, sort_keys=True, default=float))
print(json.dumps(run_m10_closure_study(), indent=2, sort_keys=True, default=float))
PY
```

## Next development

The next development lifts the internal `2I` action to a simultaneous spatial rotation of the grid, adds a dynamic tetrad/spin-connection carrier, and compares the M9 and M10 stationary branches under the same refinement and perturbation protocol.
