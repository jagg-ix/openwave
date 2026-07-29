# OpenWave M9 CAT/EPT comparison profile

M9 has two intentionally distinct public lineages:

```text
stable registration   openwave/xperiments/m9_cat_ept/model_registration_current.py
stable conformance    openwave/xperiments/m9_cat_ept/model_conformance_current.py
latest registration   openwave/xperiments/m9_cat_ept/model_registration_latest.py
latest conformance    openwave/xperiments/m9_cat_ept/model_conformance_latest.py
canonical model       openwave/xperiments/m9_cat_ept/canonical_particle_model_m140.py
```

The stable compatibility aliases remain at **M9.126** with schemas:

```text
openwave.model-registration.v29
openwave.m9.models-conformance.v22
openwave.m9.platform-integration-contract.v9
```

The latest integrated model is **M9.140** with schemas:

```text
openwave.m9.canonical-particle-contract.v1
openwave.model-registration.latest.v1
openwave.m9.models-conformance.latest.v1
openwave.m9.platform-integration-latest.v1
```

## M9.140 canonical integration

M9.140 does not create another CAT/EPT model. It exposes one facade over the existing executable surfaces:

- three-dimensional localized-branch particle API;
- M9.132 matter--geometry--entropic-time evolution;
- M9.133 reduced gauge-coupled evolution;
- M9.99 exact formal/numerical equation relations;
- M9.138 complex-action, entropic-gradient, and gauge authority;
- M9.139 retarded-causality, Pauli-coupling, and axial-topology authority.

The machine-readable action ledger is `openwave/xperiments/m9_cat_ept/formal/canonical_coupled_action.v1.json`.

## Formal authority

The live formal equation authority remains `jagg-ix/entropic-physlib-private` on branch `entropic-physlib-linear-full`. Lean is proof authority; OpenWave is numerical-model authority. A formal theorem, numerical closure, or structural match does not automatically promote another layer.

M9.140 records these remaining equation-level gaps explicitly:

- one consistent kinetic mass map `D = 1/(2m)`;
- one 3D Hartree plus local interaction carrier;
- one constraint-preserving 3D U(1) differential complex;
- one explicit discrete imaginary action whose variation produces the irreversible law;
- one coupled Pauli/Foldy--Wouthuysen particle equation rather than separate bridges.

## Existing experimental evidence

The stable M9.126 evidence registry still recognizes the Planckian-dissipation summaries from Bruin 2013, Legros 2019, and Cao 2020. Those records support retrospective broad-band comparisons. They do not uniquely select entropic time and they are not a prospective blinded test.

## Current comparison status

```text
validated   7
partial    13
negative    1
not_yet     0
```

M9.140 changes no criterion status. The latest conformance alias composes the canonical model contract while preserving the stable 21-row evidence matrix.

## Next model target

The next canonical carrier is a three-dimensional Pauli--Hartree--U(1) state on the shared odd-grid Fourier geometry. Required outputs include measured winding, charge continuity, Gauss closure, stationary residual, entropic production, perturbation stability, and grid refinement.

The nonzero winding must be measured from the solved field. It cannot be inherited only from model metadata.

## Physical claim boundary

Physical promotion remains blocked. M9.140 does not establish a stable charged particle, an electron identity, calibrated charge or mass, an anomalous magnetic moment, calibrated force laws, or an external prediction.
