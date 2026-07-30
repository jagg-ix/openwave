# OpenWave M10 CAT/EPT Dirac--Cartan--2I--Compton--Yukawa model

M10 is the relativistic, second-quantized, and QCD-functional comparison model to the M9 Pauli--Hartree--U(1) carrier.

## M10.1 one-particle carrier

M10.1 constructs one executable three-dimensional four-spinor state with the complete 120-element binary icosahedral group, minimally coupled U(1) fields, measured winding, the canonical axial current, algebraic Cartan contorsion and Hehl--Datta contact interaction, Yukawa mass, Compton clock, complex CAT/EPT mass, and self-consistent electromagnetic fields.

## M10.2 stationary and robustness closure

M10.2 establishes residual-reducing stationary descent, positive entropic-time advance, nested odd-grid retention of winding/norm/charge, bounded localization-radius variation, perturbation-tube stability, interacting central-pair descent, and integrated Dirac continuity.

## M10.3 fermionic second quantization

M10.3 constructs the complete four-mode fermionic Fock realization of the internal Dirac carrier:

```text
Fock dimension: 2^4 = 16
sector dimensions: 1, 4, 6, 4, 1
```

It establishes exact Jordan--Wigner CAR, Pauli exclusion, determinant exterior-power lifts for all 120 binary-icosahedral transformations, all 14,400 functorial group products, creation intertwining, central sign as fermion parity, the occupation Hamiltonian `dGamma(E_C I_4)=E_C N`, the finite fermion partition function, and occupation-dependent CAT/EPT suppression.

## M10.4 finite QCD functional and history decoherence

M10.4 couples the M10.3 occupation sector to a complete finite center-valued Wilson ensemble.

Four `Z3 subset SU(3)` plaquettes give

```text
3^4 = 81
```

histories. Every history carries

```text
S_R[c] = theta n_c
S_I[c] = beta S_W[c] + N Sdot_I t
w[c] = exp(i S_R[c] - S_I[c]/hbar).
```

The executable functional establishes:

- exact enumeration of all 81 finite Wilson histories;
- nonnegative Wilson action;
- theta-phase, confinement-damping, and Fock-entropy factorization;
- QCD charge-conjugation pairing and a real total partition;
- the source-coupled partition `Z[J]`;
- `d log Z/dJ = <O>`;
- `d2 log Z/dJ2 = <O^2>-<O>^2`;
- occupation multiplication of the Yukawa entropy contribution to the partition;
- the Feynman-parameter identity for two propagator denominators;
- convergence of the QCD scalar-bubble finite part to `-2`;
- a history decoherence matrix

```text
D_ab = w_a conjugate(w_b)
       exp[-(2 M gamma t/beta_env) ||x_a-x_b||^2];
```

- Hermiticity, unit trace, Born diagonal, positive semidefiniteness, and the Dowker--Halliwell off-diagonal bound;
- strict suppression of every pair of distinct histories;
- stronger suppression when the environment coupling is increased.

## Exact formal authority

The one-particle bridge is pinned to Physlib PR **#41** at:

```text
b894a64e180b46c9bc1dd7e0100422b0cc6fb143
```

The second-quantized bridge is pinned to Physlib PR **#42** at:

```text
45269fa04dc16ae1588925f0a8c167ee9dfbc7b8
```

The QCD/functionals/decoherence ledger content-pins:

- `QCDComplexActionUnification.qcd_theta_confinement_factorization`;
- `FiniteWilsonGaugeModel.connectedGeneratingFunctional_linearSource_hasDerivAt_zero`;
- `CaldeiraLeggettInfluenceFunctional.feynmanVernon_modulus_is_decoherence`;
- `DecoherenceFunctionalSorkinJohnston.decoherenceFunctional_isDecoherenceFunctional`;
- `OneLoopScalarIntegralsQCD.feynman_parametrization`.

The machine-readable maps are:

```text
formal/dirac_cartan_2i_yukawa.v1.json
formal/second_quantized_fock.v1.json
formal/qcd_functional_decoherence.v1.json
```

## Reproduction

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import (
    run_m10_core_study,
    run_m10_closure_study,
    run_second_quantized_fock_study,
    run_qcd_functional_decoherence_study,
)
from openwave.xperiments.m10_cat_ept.model_registration import run_model_registration_study
import json
for result in (
    run_m10_core_study(),
    run_m10_closure_study(),
    run_second_quantized_fock_study(),
    run_qcd_functional_decoherence_study(),
    run_model_registration_study(),
):
    print(json.dumps(result, indent=2, sort_keys=True, default=float))
PY
```

## Next development

The next layer can replace the finite center ensemble with sampled non-Abelian `SU(3)` link matrices, add dynamical color-fermion backreaction, and compare the resulting confinement/decoherence spectrum with the existing M9 and M10 stationary carriers.
