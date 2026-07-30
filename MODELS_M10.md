# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic, second-quantized, and non-Abelian QCD comparison model to the M9 Pauli--Hartree--U(1) carrier.

## M10.1--M10.7 established lineage

- **M10.1:** Dirac--Cartan--2I--Compton--Yukawa one-particle carrier.
- **M10.2:** stationary, refinement, perturbation and continuity closure.
- **M10.3:** finite fermionic Fock realization with CAR and fermion parity.
- **M10.4:** finite QCD functional, connected correlators and history decoherence.
- **M10.5:** matrix-valued `SU(3)` links and covariant quark-color backreaction.
- **M10.6:** periodic Hamiltonian `SU(3)` lattice with electric fields and source-free Gauss law.
- **M10.7:** gauge-covariant fundamental-color matter, exact continuity and sourced Gauss closure.

## M10.8 Wilson-loop refinement and confinement-decoherence spectra

M10.8 evaluates smooth periodic `SU(3)` links on nested lattice sizes

```text
L = 4, 6, 8, 10.
```

The normalized plaquette action decreases under refinement. Its observed orders are

```text
2.995, 3.382, 3.626,
```

approaching the expected fourth-order small-loop scaling

```text
1 - Re Tr(P_a)/3 = O(a^4).
```

An eight-history ensemble on `L=6` evaluates every rectangular Wilson loop through `3 x 3`. The mean loops are fitted to

```text
-log W(R,T) = sigma R T + mu 2(R+T) + c.
```

The reference ensemble yields positive area and perimeter coefficients and a positive first Creutz ratio

```text
chi(1,1) = -log[W(2,2) W(1,1) / (W(2,1) W(1,2))].
```

The campaign additionally establishes:

- gauge invariance of the rectangular loops;
- the unit bound for all mean Wilson loops;
- center invariance of the Polyakov-loop norm `|zL|=|L|`;
- finite Polyakov-loop statistics;
- positive-semidefinite normalized weak and strong environment history matrices;
- the Dowker--Halliwell off-diagonal bound through the positive spectrum;
- a nonzero decoherence spectral gap;
- smaller maximum and Frobenius off-diagonal interference at stronger environment coupling.

The history matrix is

```text
D_ab = w_a conjugate(w_b)
       exp[-gamma ||F_a-F_b||^2],
```

where `F_a` contains the complete rectangular Wilson-loop and Polyakov observables for history `a`.

## Exact formal authority

The M10 lineage remains pinned to Physlib PRs **#41** and **#42**. M10.8 additionally content-pins:

- `WilsonLoopAreaLaw.areaLaw_implies_decay`;
- `PolyakovLoopCenterSymmetry.center_preserves_norm`;
- `FiniteWilsonGaugeModel.expectation_and_connectedGeneratingFunctional_tendsto`;
- `DecoherenceFunctionalSorkinJohnston.decoherenceFunctional_isDecoherenceFunctional`;
- `DowkerHalliwellDecoherenceFunctional.decoherence_offdiag_bound`.

Machine-readable ledgers now include:

```text
formal/periodic_su3_hamiltonian.v1.json
formal/color_matter_gauss.v1.json
formal/wilson_refinement_spectrum.v1.json
```

## Reproduction

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import (
    run_periodic_su3_hamiltonian_study,
    run_color_matter_gauss_study,
    run_wilson_refinement_spectrum_study,
)
from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
import json
for result in (
    run_periodic_su3_hamiltonian_study(),
    run_color_matter_gauss_study(),
    run_wilson_refinement_spectrum_study(),
    run_model_registration_study(),
):
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
PY
```

## Next development

A subsequent layer can enlarge the dynamical lattice, integrate matter and gauge backreaction in one constrained trajectory, and perform statistically controlled coupling and volume scans.
