# OpenWave M9 CAT/EPT comparison profile

M9 has two intentionally distinct public lineages:

```text
stable registration   openwave/xperiments/m9_cat_ept/model_registration_current.py
stable conformance    openwave/xperiments/m9_cat_ept/model_conformance_current.py
latest registration   openwave/xperiments/m9_cat_ept/model_registration_latest.py
latest conformance    openwave/xperiments/m9_cat_ept/model_conformance_latest.py
canonical model       openwave/xperiments/m9_cat_ept/canonical_particle_model_m141.py
charged carrier       openwave/xperiments/m9_cat_ept/pauli_hartree_u1_carrier_m141.py
```

The stable compatibility aliases remain at **M9.126** with schemas:

```text
openwave.model-registration.v29
openwave.m9.models-conformance.v22
openwave.m9.platform-integration-contract.v9
```

The latest integrated model is **M9.141** with schemas:

```text
openwave.m9.pauli-hartree-u1-carrier.v1
openwave.m9.canonical-particle-contract.v2
openwave.model-registration.latest.v2
openwave.m9.models-conformance.latest.v2
openwave.m9.platform-integration-latest.v2
```

## M9.141 three-dimensional carrier

M9.140 unified the existing particle, reduced dynamics, and theorem-authority surfaces. M9.141 closes the next model-level target by constructing one state containing:

- a two-component Pauli spinor on an odd `17 x 17 x 17` Fourier grid;
- one mass map satisfying `D = 1/(2m)` in both kinetic and current terms;
- the selected local cubic--quintic interaction;
- an attractive Hartree potential;
- periodic scalar and vector U(1) potentials;
- electric and magnetic fields from the same differential complex;
- coordinate time and entropic time;
- declared and field-measured winding.

The reference carrier uses winding three. The winding is measured from the first spinor component and agrees with the normalized unit-charge ledger. Static periodic Gauss, Ampere, and magnetic-divergence residuals close near machine precision after the Maxwell Picard iteration.

## Discrete imaginary action

M9.141 introduces the frozen-operator functional

```text
S_I^n[psi] = gamma/2 ||(H_n - mu_n) psi||_2^2
```

with squared-gradient relaxation

```text
d psi / dt = -gamma (H_n - mu_n)^2 psi
```

and nonnegative entropic production

```text
d tau_ent / dt = gamma ||(H_n - mu_n) psi||_2^2 / hbar^2.
```

This is an explicit discrete substep. It is not presented as the complete nonlinear continuum CAT/EPT imaginary action.

The machine-readable action ledger is `openwave/xperiments/m9_cat_ept/formal/canonical_coupled_action.v2.json`.

## Formal authority

The live formal equation authority remains `jagg-ix/entropic-physlib-private` on branch `entropic-physlib-linear-full`. Lean is proof authority; OpenWave is numerical-model authority. M9.141 reuses the pinned Hartree/local-interaction, Pauli, Maxwell/continuity, and complex-variational source surfaces. A formal theorem, numerical closure, or structural match does not automatically promote another layer.

## Existing experimental evidence

The stable M9.126 evidence registry still recognizes the Planckian-dissipation summaries from Bruin 2013, Legros 2019, and Cao 2020. Those records support retrospective broad-band comparisons. They do not uniquely select entropic time and they are not a prospective blinded test.

## Current comparison status

```text
validated   7
partial    13
negative    1
not_yet     0
```

M9.141 changes no criterion status. The latest conformance alias records the three-dimensional carrier while preserving the stable 21-row evidence matrix.

## Next model target

M9.142 must solve and perturb a stable measured-winding charged stationary branch on nested odd grids. It must report stationary residual, localization, winding, Maxwell fixed-point error, perturbation tubes, and refinement without selecting a physical identity in advance.

## Physical claim boundary

Physical promotion remains blocked. M9.141 does not establish a stable charged particle, an electron identity, calibrated charge or mass, an anomalous magnetic moment, calibrated force laws, continuum convergence, or an external prediction.
