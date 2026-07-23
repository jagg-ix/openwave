# M9 theory citations

> Third-party papers are not committed to this repository. Obtain them from the
> original venue. This file records provenance only.

## Bibliography

| Author(s) | Year | Title | Venue / ID |
| --- | --- | --- | --- |
| A. Caticha | 2019 | Entropic Dynamics, Time and Quantum Theory | Entropy 21, 943; DOI 10.3390/e21100943 |
| S. Ipek, M. Abedi, A. Caticha | 2019 | Entropic Dynamics: Reconstructing Quantum Field Theory in Curved Space-time | Classical and Quantum Gravity 36, 205013; arXiv:1803.07493 |
| M. Soler | 1970 | Classical, Stable, Nonlinear Spinor Field with Positive Rest Energy | Physical Review D 1, 2766; DOI 10.1103/PhysRevD.1.2766 |
| G. Berkolaiko, A. Comech | 2009 | On spectral stability of solitary waves of nonlinear Dirac equation on a line | arXiv:0910.0917 |
| J. Cuevas-Maraver et al. | 2017 | Solitary waves in the Nonlinear Dirac Equation | arXiv:1707.01946 |
| M. J. Esteban, V. Georgiev, E. Sere | 1996 | Stationary solutions of the Maxwell-Dirac and the Klein-Gordon-Dirac equations | Calculus of Variations and PDE 4, 265--281; DOI 10.1007/BF01254347 |
| C. Radford | 2001 | The Stationary Maxwell-Dirac Equations | arXiv:math-ph/0112037 |
| A. G. Lisi | 1994/1995 | A Solution of the Maxwell-Dirac Equations in 3+1 Dimensions | arXiv:hep-th/9410244; Journal of Physics A 28, 5385 |
| P. d'Avenia, G. Siciliano | 2021 | A normalized solitary wave solution of the Maxwell-Dirac equations | Annales de l'Institut Henri Poincare C 38, 1681; DOI 10.1016/j.anihpc.2020.12.006 |
| Jorge A. Garcia | 2026 | Entropic Physlib formal development | `jagg-ix/entropic-physlib-private`, pinned commit in `../formal/entropic_spine_contract.json` |

## M9.7a provenance

The implemented 1+1D equation, representation, stationary ansatz, and explicit
cubic solitary-wave family follow the nonlinear Dirac/Soler and massive
Gross--Neveu literature. OpenWave's convergence, perturbation, gauge-interface,
and entropic-clock gates are repository-specific.

## M9.7b1 provenance

Higher-dimensional nonlinear Dirac solitary waves and Maxwell--Dirac localized
states motivate the staged three-dimensional program. M9.7b1 validates a regular
spherical source ansatz and its electrostatic Maxwell constraint only.

## M9.7b2 provenance

The stationary Maxwell--Dirac literature establishes that regular localized
stationary configurations are a meaningful target. M9.7b2 solves OpenWave's
selected spherical Soler--electrostatic boundary-value problem with `lambda=64`,
unit norm, and dimensionless charge normalization. It does not claim to reproduce
a specific published profile or variational construction.

## M9.7b3 provenance

M9.7b3 evolves the selected M9.7b2 branch with a repository-specific weighted
radial split method. The longitudinal electrostatic field is constrained by
Gauss/Poisson projection at every local substep. The cited stationary literature
does not validate this discretization, perturbation, finite-time stability result,
CAT/EPT interpretation, or particle identity.

Spherical electrostatics has no transverse magnetic mode. The recorded zero
Poynting flux follows from the selected symmetry reduction and is not a claim
about general Maxwell--Dirac radiation.

## Local corpus

No third-party source files are tracked. The M9 tasks require only the citation
ledger and the executable equations committed in this repository.
