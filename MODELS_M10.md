# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic comparison model to the M9 Pauli--Hartree--U(1) carrier.

## What M10.1 establishes

M10.1 constructs one executable three-dimensional four-spinor state with:

- the complete 120-element binary icosahedral quaternion set `2I`;
- a unitary `2I` action lifted to the four-spinor;
- central-pair descent of quadratic observables from `2I` to the `A5` rotation shadow;
- a minimally coupled Dirac--U(1) operator;
- field-measured winding and normalized charge;
- algebraic axial Cartan contorsion and the eliminated contact interaction;
- a Yukawa mass `m_Y = yv/sqrt(2)`;
- the Compton clock `omega_C = m_Y c^2/hbar`;
- the complex mass `M = m_Y + i Sdot_I/c^2`;
- the CAT/EPT entropy rate `Sdot_I = y omega_C/(2 hbar)`;
- self-consistent periodic electric and magnetic fields.

The model checks the full finite `2I` multiplication table, unitarity of all 120 Dirac lifts, the free Dirac mass-shell matrix identity, the Cartan spin-source residual, the mass-clock identity, the complex-mass entropy identity, winding quantization, charge normalization, and static Maxwell constraints.

## Formal authority

The formal bridge is developed in `jagg-ix/entropic-physlib-private`, branch `agent/dirac-cartan-2i-compton-yukawa`, through:

- `BinaryIcosahedralDiracSpinor.lean`;
- `EinsteinCartanAxialTorsion.lean`;
- `DiracCartanComptonYukawaBridge.lean`.

The machine-readable equation map is `openwave/xperiments/m10_cat_ept/formal/dirac_cartan_2i_yukawa.v1.json`.

## Reproduction

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import run_m10_core_study
import json
print(json.dumps(run_m10_core_study(), indent=2, sort_keys=True, default=float))
PY
```

## Next closure

M10.2 will add imaginary-time stationary solving, nested odd-grid refinement, perturbation tubes, binary-icosahedral covariance residuals of the interacting operator, central-pair stress-energy descent, and real-time continuity diagnostics.
