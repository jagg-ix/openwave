# M9.95 method note: canonical particle-pair force bridge

## Scope

M9.95 binds the imported formal electric and magnetic surfaces to one canonical periodic CAT/EPT particle-pair representation and one shared dimensionless interaction ledger.

The two envelopes carry declared winding sectors `+3` and `-3`, corresponding through the existing exact winding arithmetic to dimensionless charges `+1` and `-1`. The winding is deliberately marked as not embedded into either stationary envelope; these are declared-sector controls, not charged stationary particles.

## Electric sector

PhysLib supplies:

- the entropic screened mass;
- the Yukawa potential and its Coulomb upper bound;
- the zero-screening identity `G_0(r) = 1/r`;
- the entropic-action Coulomb endpoint.

OpenWave supplies the finite-size regularized energy and differentiates it to the radial force. The canonical pair closes:

- opposite electric signs;
- energy/force derivative consistency;
- inverse-square asymptote from the legacy multi-distance campaign;
- action-reaction;
- one shared ledger for charge, length, force, couplings, and softening.

## Magnetic sector

The magnetic moments are obtained from the canonical Pauli-current bridge on the same two particle envelopes. PhysLib supplies Lorentz-EM superoperator decomposition and covariance. OpenWave supplies the regularized dipole-energy kernel and closes:

- opposite spin/moment controls;
- energy/force derivative consistency;
- orientation signs;
- the dipole `r^-4` force asymptote from the legacy campaign;
- action-reaction and superposition with the electric force.

## Decision

- Formal screened/Coulomb and Lorentz-EM surfaces imported: **closed**.
- Canonical particle-pair bound to electric and magnetic kernels: **closed in-platform**.
- Shared dimensionless interaction ledger: **closed**.
- Charged stationary CAT/EPT particle pair: **not established**.
- Derivation of the regularized dipole force law from the full CAT/EPT PDE: **not established**.
- Physical charge, magnetic-moment, and force calibration: **not established**.
- Electric-force and magnetic-force criteria: remain **partial**.
