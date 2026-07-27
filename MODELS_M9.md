# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.125**.

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v28
openwave.m9.platform-integration-contract.v8
```

## M9.125: one reduced carrier for three aspects of time

M9.124 separated the clock roles. M9.125 puts them on one explicitly shared finite state algebra.

| Aspect | Realization on the shared carrier |
| --- | --- |
| Page-Wootters relational time | a clock-indexed classical-quantum history state conditions to the exact thermal-relaxation system state at each reading |
| modular / thermal time | the same equilibrium state defines `K = -log rho_eq`; for the Gibbs carrier `K = beta H + log(Z) I` |
| entropic time | quantum relative entropy to the same equilibrium state decreases, so accumulated entropic time increases |

The conditioned Hamiltonian part and modular generator agree after the explicit `t = beta s` rescaling and an irrelevant identity offset. The dissipative flow and modular flow act on the same qubit operator algebra.

This closes a **reduced common-carrier compatibility result**. It does not derive the full Page-Wootters conditioned dynamics from a Wheeler-DeWitt tensor constraint.

## M9.125a shared finite carrier

The carrier uses a full-rank Gibbs equilibrium and a thermal-relaxation semigroup:

```text
p(t) = p_eq + (p_0 - p_eq) exp(-gamma t)
c(t) = c_0 exp[(-gamma/2 + i DeltaE)t]
```

It verifies:

- positive, unit-trace states throughout the branch;
- exact semigroup composition;
- agreement with the right infinitesimal generator;
- exact conditioning of the clock-indexed history state;
- `K = beta H + log(Z) I`;
- modular/Hamiltonian flow agreement after `t = beta s`;
- monotone remaining and accumulated relative-entropy clocks.

## M9.125b internal calibration contract

The model records explicit maps:

```text
t = a_pw tau_pw
s = t / beta
sigma_nominal = t / N
tau_ent = D(rho_0 || rho_eq) - D(rho_t || rho_eq)
```

The first three are coordinate-like positive maps. The entropic reading is nonlinear but invertible on the selected monotone relaxation branch. Roundtrip and commuting-diagram checks are executable.

These are **model-internal calibration maps**. `a_pw`, `beta`, and `N` are not independently measured physical calibration data.

## M9.125c blinded three-clock protocol

A prediction payload is committed before reveal and contains, at preregistered readings:

```text
Page-Wootters reading
modular parameter
nominal proper-time adapter
conditioned population
coherence magnitude
accumulated entropic time
```

The live package remains blocked because it has no independent physical units, clock identity, calibration source, or observed data. A synthetic fixture exercises all metrics but is permanently ineligible for external promotion.

## Current authority

```text
merged Physlib baseline       master@80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef
clock development source      entropic-physlib-linear-full@af78ea63ee0b39456d8dab023761482196b8c172
public zil-lean               c671f02d8b6dcf7ba689afc86477ff7e35465c35
```

Stacked Physlib PRs #22--#24 are recorded as candidate relaxation/KL-clock work and are not relabeled as merged `master` authority.

## Current decision

```text
three distinct clock roles                         established
shared finite three-clock carrier                  constructed
conditioned/modular generator identification       constructed in reduced Gibbs carrier
internal Page-Wootters/modular maps                constructed
branch-specific modular/entropic map               constructed
nominal proper-time adapter                        constructed but not physically calibrated
three-clock prediction commitment                  constructed
real three-clock data                              not ingested
full constraint-to-conditioned dynamics theorem    open
continuum or field-level common carrier             open
independent proper-time calibration                 open
held-out three-clock test                           open
single universal physical clock                    not established
```

A shared finite carrier is not a carrier-independent equivalence theorem. A nominal proper-time adapter is not measured proper time. A synthetic holdout is not external evidence.
