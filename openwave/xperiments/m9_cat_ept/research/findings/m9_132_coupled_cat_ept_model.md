# M9.132 — Coupled CAT/EPT model evolution

This milestone improves the CAT/EPT simulation core rather than adding another evidence-only layer.

1. A single periodic solver evolves the complex matter field, self-consistent geometry potential, density-dependent imaginary-action relaxation, and accumulated entropic time.
2. Matter density and kinetic density source geometry; geometry feeds back into the real Hamiltonian; the centered Hamiltonian drives norm-preserving irreversible relaxation.
3. Shared-parameter campaigns compare the full model with gravity-off, dissipation-off, and fully uncoupled baselines without per-observable refitting.

## Boundary

The carrier is dimensionless and reduced. Its scalar geometry is not full general relativity, normalization is a numerical projection, and the ablation results are internal model discrimination rather than external validation.
