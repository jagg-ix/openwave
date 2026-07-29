# M9.133 — Gauge-coupled CAT/EPT model

This milestone extends the M9.132 matter–geometry–entropy solver with a dynamical reduced U(1) vector potential, electric field, covariant charged-matter evolution, current sourcing, and Gauss-residual diagnostics.

It also adds joint matter/gauge energy accounting and a three-grid bounded-refinement campaign at a common final time.

The public repository now runs focused M9.132 and M9.133 validation in GitHub Actions on Python 3.12. The workflow compiles the coupled modules and executes their dedicated pytest files without installing the unrelated GUI/Taichi application stack.

## Boundary

The carrier is dimensionless and one-dimensional. It is not complete Maxwell theory, general relativity, or a physically calibrated CAT/EPT prediction. Finite-grid boundedness is not a continuum convergence theorem.
