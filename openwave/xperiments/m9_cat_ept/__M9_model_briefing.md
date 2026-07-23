# M9 CAT/EPT: Entropic Particle Dynamics

M9 is a dimensionless simulation model inside OpenWave. It now includes bounded
localization, field winding, scale selection, separated clock channels, Pauli
spin/magnetic controls, two-body kernels, reduced capture/annihilation, converged
standing-wave quantization, and composite-state graphs.

## Current decisions

- A constrained 1D localized family exists; no stable 3D particle is accepted.
- Integer winding is field-derived; electric-charge identity is open.
- A dimensionless scale is selected; physical mass is open.
- Reversible phase is an intrinsic-clock candidate; physical time is not identified.
- Spin/magnetic/double-cover controls exist; exchange statistics and emergent g remain open.
- Reduced annihilation closes its radiation ledger; full-PDE annihilation is open.
- A radial bound-mode ladder is resolved; native CAT/EPT atomic structure is open.
- Neutral-pair and charged-triplet graphs bind; physical mesons/baryons are not established.

## Comparison status

[`MODELS_M9.md`](../../../MODELS_M9.md) records twelve partial criteria, one
honest negative, and seven not-yet criteria.

## Next critical targets

1. M9.34 geometry/metric back-reaction plugin.
2. M9.35 multi-domain coupling graph and dependency scheduler.
3. M9.36 adaptive refinement and propagated error budgets.
