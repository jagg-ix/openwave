# M9.93 method note: formal contract, particle kernel, and model registration

## Question

Can the existing CAT/EPT research campaign be exposed as one reusable OpenWave model without converting theorem references into runtime dependencies or converting a localized mathematical branch into an asserted physical particle?

## Method

M9.93 is split into three executable audits.

1. `m9_93a_physlib_contract.py` loads `formal/physlib_contract.v2.json`, checks the exact `jagg-ix/entropic-physlib-private` repository, `entropic-physlib-linear-full` branch, commit, source blobs, declaration identities, numerical adapters, assumptions, and positive/negative scope. Simulated stale and missing observations fail closed in the focused tests.
2. `m9_93b_particle_kernel.py` constructs the repository-default action specification, a normalized three-dimensional control state, exact free and local subflows, Strang composition, state fingerprints, observables, and the physical-identity certificate. The default certificate must fail because no physical name, calibration, or external evidence is supplied.
3. `m9_93c_model_registration.py` binds the M9 launcher, dedicated comparison profile, conformance runner, particle API, formal contract, and briefing to the current 21-row `7 validated / 13 partial / 1 negative` profile.

## Result

The new infrastructure makes the existing M9 numerical and formal surfaces addressable through stable APIs. Lean remains build-time proof authority and is not imported as a simulation runtime. The selected cubic-quintic coefficients retain their existing explicit assumption boundary. The neutral stationary branch can be constructed through the existing solver, while nonzero winding remains declared-but-unembedded until one charged stationary state closes winding, localization, and stability simultaneously.

## Decision

- Reusable CAT/EPT particle-model infrastructure: **available**.
- Version-pinned PhysLib contract with drift checks: **available**.
- Canonical M9 model-component registration: **available**.
- Physical electron or other observed-particle identity: **not established**.
- Physical calibration or out-of-sample prediction: **not established**.

M9.93 changes infrastructure and evidence discipline only. It does not promote any of the 21 comparison criteria.
