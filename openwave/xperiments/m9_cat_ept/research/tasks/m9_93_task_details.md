# M9.93 task details

## Objective

Promote the existing CAT/EPT campaign from a collection of evidence modules into one reusable, version-pinned OpenWave model component while preserving the distinction between mathematical branch, formal theorem, calibration, and physical particle identity.

## Deliverables

### M9.93a — PhysLib contract v2

- Pin `jagg-ix/entropic-physlib-private` / `entropic-physlib-linear-full` at an exact commit.
- Pin every referenced source file by Git blob SHA.
- Record declaration, semantic role, numerical adapter, assumptions, established scope, and excluded scope.
- Resolve Python adapters without requiring Lean at runtime.
- Detect simulated commit drift, blob drift, and missing formal sources.

### M9.93b — reusable particle kernel

- Define action, particle, and state records.
- Wrap the existing M9 coefficient selection and stationary solver.
- Expose exact free and local subflows plus Strang composition.
- Expose phase chirp, periodic translation, evolution, observables, and deterministic fingerprints.
- Keep nonzero winding declared but unembedded until a charged stationary solution is constructed.
- Block physical naming unless calibration and all identity gates pass.

### M9.93c — canonical model registration

- Register the M9 ID, package directory, launcher, comparison profile, conformance runner, particle API, formal contract, and briefing.
- Preserve the current 21-row status counts: `7 validated / 13 partial / 1 negative / 0 not-yet`.
- Prove through focused tests that no default physical identity is assigned.

## Acceptance

- Focused contract, particle-kernel, and registration tests pass.
- Every formal interface has a source blob and claim boundary.
- Exact subflows reverse and preserve mass within floating-point tolerance.
- The split flow preserves mass on the control state.
- Model registration reproduces the executable conformance profile exactly.
- M9.93 does not alter any criterion status.
