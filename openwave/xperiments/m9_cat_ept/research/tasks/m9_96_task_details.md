# M9.96 task details

## Objective

Move the three partial force-related criteria from detached controls to one shared field-derived charged candidate, while preserving the requirement that a stable charged stationary branch must exist before any criterion can be promoted.

## M9.96a — charged branch feasibility

- Reuse the validated neutral M9.69 stationary amplitude.
- Embed winding `n = 3` with a regularized vortex core.
- Measure winding from the field rather than copying a sector label.
- Test multiple core radii.
- Evolve the seeds under the full unconstrained selected scalar action.
- Require winding, normalization, localization, compact radius, and stationary residual simultaneously.
- Report an explicit negative model result when no candidate passes.

## M9.96b — charge/current and Maxwell fields

- Derive charge density from measured winding and `|psi|^2`.
- Derive convective and Pauli magnetization currents from the same field.
- Solve periodic scalar and transverse-vector Poisson equations.
- Check projected Gauss law, static Ampere law, and `div B = 0`.
- Measure the magnetic moment from both the current integral and weak uniform-field energy response.
- Import the Pauli--Maxwell and conserved-current formal witnesses omitted by M9.94--M9.95.

## M9.96c — force triangle

- Construct opposite candidates by conjugation and periodic translation.
- Generate each source's electric and magnetic fields independently.
- Measure the force through:
  1. Lorentz volume density;
  2. interaction-energy derivative;
  3. cross Maxwell-stress flux.
- Require nonzero electric and magnetic contributions.
- Require agreement within preregistered finite-grid tolerances.
- Preserve the distinction between static field consistency and full-PDE center acceleration.

## M9.96d — evidence authority and registration

- Compose the current formal tree, criterion-specific formal overlay, charged feasibility result, Maxwell source closure, and force triangle.
- Add a versioned calibration ledger for the three rows.
- Register the M9.96 surfaces in the canonical model registration.
- Retain `magnetic_moment_spin`, `electric_force`, and `magnetic_force` as partial.

## Acceptance boundary

A successful M9.96 implementation does not require the selected scalar action to produce a charged stationary branch. It requires the result to be measured honestly and to fail closed:

```text
field-derived source closure + no charged stationary branch
=> stronger partial evidence, no physical promotion
```

The next phase must construct a self-consistent gauge/spinorial stationary equation and then measure full-PDE acceleration, torque, and precession.
