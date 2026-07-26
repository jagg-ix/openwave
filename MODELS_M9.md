# OpenWave M9 CAT/EPT comparison profile

The canonical conformance profile is `model_conformance_m108.py`, schema v21. The canonical registration is `model_registration_m108.py`, schema v12.

## Authorities

```text
OpenWave base  e9900880b4c54d7d68cbf468819dc361c6518a78
Physlib        128974a501d3d0a43108a3ab9a1bd9d4fea5d7db
zil-lean       e09723a44185a1e70031ad2661c8009dc98bef74
```

## M9.106 — nonlinear constraint evolution

`nonlinear_constraint_gravity.py` evolves a conformally flat spatial metric `gamma_ij = exp(4u) delta_ij`, the trace of the extrinsic curvature, one Pauli matter state, Maxwell fields, and the matter-plus-EM gravitational source.

It measures and projects Hamiltonian and momentum constraints at every step. The physical gate requires bounded constraints, Lorentzian signature, and non-worsening projection. This is a nonlinear reduced 3+1 model, not a general Einstein solver.

## M9.107 — coupled interaction-sector fields

`coupled_sector_fields.py` replaces the earlier low-dimensional controls with:

- particle/antiparticle complex fields, electrostatic potential, and radiation;
- color-triplet quark/antiquark amplitudes and a dynamical flux field;
- left/right flavor fields, a dynamical chiral mediator, and a positive reservoir.

The executed default result closes all three declared reduced-field gates. It does not establish QED, QCD, or electroweak theory.

## M9.108 — dynamical candidate states

`composite_candidate_states.py` constructs and perturbs:

- a neutral Hartree dark-matter candidate;
- a color-balanced quark candidate;
- a three-center baryon candidate;
- a quark-antiquark meson candidate.

The executed default result closes all four reduced candidate gates. These results establish only finite periodic carrier stability, not observed particle identity or calibrated spectra.

## Run

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_106_nonlinear_constraint_gravity.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_107_coupled_sector_fields.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_108_candidate_states.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_108_current_registration.py
```

## Current authority surfaces

- `formalization_m108_extension.py`
- `nonlinear_constraint_gravity.py`
- `coupled_sector_fields.py`
- `composite_candidate_states.py`
- `m106_108_evidence_authority.py`
- `criterion_maturity_m108.py`
- `model_conformance_m108.py`
- `model_registration_m108.py`
- `research/zil/m9_106_108_nonlinear_sectors_candidates.zc`
- `M9_DYNAMICAL_FIELDS.md`
