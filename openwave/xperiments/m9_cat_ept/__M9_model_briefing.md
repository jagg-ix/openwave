# M9 CAT/EPT: Entropic Particle Dynamics

M9 is a dimensionless simulation model inside OpenWave. It now includes bounded
localization, field winding, scale selection, separated clock channels, Pauli
spin/magnetic controls, two-body kernels, reduced capture/annihilation, converged
standing-wave quantization, composite-state graphs, a screened weak-field geometry
plugin, deterministic multi-domain scheduling, and adaptive numerical error budgets.

## Current decisions

- A constrained 1D localized family exists; no stable 3D particle is accepted.
- Integer winding is field-derived; electric-charge identity is open.
- A dimensionless scale is selected; physical mass is open.
- Reversible phase is an intrinsic-clock candidate; physical time is not identified.
- Spin/magnetic/double-cover controls exist; exchange statistics and emergent g remain open.
- Reduced annihilation closes its radiation ledger; full-PDE annihilation is open.
- A radial bound-mode ladder is resolved; native CAT/EPT atomic structure is open.
- Neutral-pair and charged-triplet graphs bind; physical mesons/baryons are not established.
- Matter sources a scalar metric/lapse control; Einstein gravity and physical coupling remain open.

## Comparison status

[`MODELS_M9.md`](../../../MODELS_M9.md) records thirteen partial criteria, one
honest negative, and six not-yet criteria.

## Next critical targets

1. M9.37 three-dimensional minimizer/BVP and continuation methods.
2. M9.38 manifest-driven GPU adapter.
3. M9.39 lepton-family hierarchy and parameter-selection audit.
