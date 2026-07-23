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
| K. S. Yee | 1966 | Numerical solution of initial boundary value problems involving Maxwell's equations in isotropic media | IEEE Transactions on Antennas and Propagation 14, 302--307 |
| Jorge A. Garcia | 2026 | Entropic Physlib formal development | `jagg-ix/entropic-physlib-private`, pinned commit in `../formal/entropic_spine_contract.json` |

## M9.7a provenance

The 1+1D spinor model follows the nonlinear Dirac/Soler and massive Gross--Neveu
literature. OpenWave's convergence, perturbation, gauge-interface, and information
gates are repository-specific.

## M9.7b provenance

The stationary Maxwell--Dirac literature establishes localized stationary
configurations as a meaningful mathematical target. OpenWave's `lambda=64`
radial branch and finite-time results are selected repository-specific
constructions rather than reproductions of one published profile.

## M9.7c provenance

Finite-difference Maxwell literature motivates the transverse wave benchmark and
energy/Poynting accounting. M9.7c uses a repository-specific potential formulation,
RK4 integration, neutral-pair current, and conductivity absorber.

## M9.9 provenance

M9.9 combines the standard 1+1D Dirac Hamiltonian with a temporal-gauge planar
Maxwell reduction. Its packet construction, parameters, discretization, absorber,
and gates are OpenWave-specific.

## M9.10 provenance

M9.10 extends the selected temporal-gauge reduction to two transported spatial
coordinates using spectral differentiation, RK4 integration, a spectral Poisson
initial field, and conductivity damping with induced-charge accounting. The cited
Maxwell--Dirac and numerical-Maxwell literature motivates the equation class and
conservation diagnostics but does not validate the selected packets, parameters,
benchmark order, numerical results, CAT/EPT interpretation, or particle identity.

## Local corpus

No third-party source files are tracked. The M9 tasks require only this citation
ledger and the executable equations committed in the repository.
