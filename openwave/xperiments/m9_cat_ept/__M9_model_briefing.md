# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9.1--M9.6 establish the formal interface, scalar controls,
> information clock, scalar localization family, scaling ledger, and scalar-carrier
> boundary. M9.7a validates a localized nonlinear Dirac carrier in 1+1D. M9.7b1
> qualifies the spherical electrostatic Maxwell sector, M9.7b2 solves a coupled
> stationary 3D radial spinor branch, and M9.7b3 now validates finite-time
> constrained spherical spinor--electrostatic dynamics. Transverse Maxwell
> radiation and physical particle identity remain open.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; entropic dynamics; nonlinear scalar and spinor solitary waves; stationary and constrained-dynamic electrostatic Maxwell--Dirac systems |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | Formal/clock/scalar modules, `spinor_carrier.py`, `electrostatic_gauge_3d.py`, `dirac_electrostatic_3d.py`, `dirac_electrostatic_dynamics_3d.py`, and M9.1--M9.7b3 research records |

## Model profile

| Attribute | M9 status |
| --- | --- |
| Scalar carrier | One-component complex scalar with exact neutral 1+1D bright-soliton family |
| 1+1D spinor carrier | Exact two-component Soler solitary wave passing M9.7a |
| 3D spinor ansatz | Spherical four-spinor `exp(-i omega t)(v chi, i u sigma.rhat chi)^T` |
| Selected 3D model | Soler scalar attraction plus longitudinal electrostatic self-field |
| Frozen inputs | `m=epsilon0=q=N=1`, `lambda=64` |
| Stationary branch | `omega=0.9914633829359464`, `R_rms=5.8792323633` |
| Time-dependent branch | Weighted-unitary radial Dirac evolution with Poisson projection at each local substep |
| Frozen perturbation | 2% opposite amplitude modulation plus 2% opposite component phase |
| Long-time result | At `t=20`, fidelity `0.99989203`, core `0.98975304`, outer fraction `7.22e-5` |
| Conservation | Norm drift below `1e-14`; total-energy relative drift below `8.2e-8` in the long run |
| Dynamic Gauss law | Constraint projected after every local half-step; sampled residual below `2e-14` |
| Entropic clock | Shell probability proportional to `rho Delta V`; reflecting radial channel remains closed |
| Signed sectors | `q -> -q` reverses potential and flux while preserving the selected spinor density and field energy |
| Electric charge | Dimensionless source label only; no physical charge-unit calibration |
| Spin | Classical 3D spinor representation; no fermionic quantization/statistics or measured spin observable |
| Radiation | Spherical electrostatic sector has `B=0` and exactly zero Poynting flux; transverse radiation remains absent |
| CAT/EPT relation | Density/information interfaces are preserved; `lambda=64` and gauge dynamics are selected real-sector inputs, not derived from `S_I` |

## Field configurations

| Candidate | Configuration | Status |
| --- | --- | --- |
| Neutral scalar candidate | Bright scalar soliton in 1+1D | Validated mathematical candidate |
| 1+1D spinor candidate | Two-component Soler solitary wave | Validated replacement-carrier prerequisite |
| 3D stationary candidate | Normalized spherical Soler spinor with electrostatic back-reaction | Validated selected-model stationary solution |
| 3D dynamic candidate | Same branch under frozen finite perturbation through `t=20` | Finite-time constrained spherical stability evidence |
| Electron | No physical mass/charge calibration, magnetic moment, statistics, or experimental identification | Not established |
| Opposite source sector | Algebraic `q=-1` branch with reversed potential and flux | Dimensionless sector, not positron identity |
| Photon / radiation | No transverse Maxwell or magnetic mode | Honest negative in current symmetry sector |

## Implementation status

| Sector | Status |
| --- | --- |
| M9.1--M9.6 | Complete scalar/formal/clock/carrier program |
| M9.7a | Complete 1+1D nonlinear spinor qualification |
| M9.7b1 | Complete 3D electrostatic source-and-field qualification |
| M9.7b2 | Complete coupled stationary radial spinor--electrostatic solve |
| M9.7b3 | Complete constrained spherical time evolution, perturbation, conservation, Gauss, refinement, window, boundary-current, and clock gates |
| Dynamic refinement | Spinor order `1.92689`; density order `2.09472` |
| Long-time conservation | Norm drift `9.99e-15`; total-energy relative drift `8.15e-8` |
| Long-time localization | Fidelity `0.99989203`; core `0.98975304`; outer fraction `7.22e-5` |
| Radiation ledger | Electromagnetic Poynting flux exactly zero by spherical electrostatic symmetry |
| Non-spherical radiative gauge evolution | Open M9.7c |
| Interactive launcher | Deferred until M9.7c closes |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). The next target is
M9.7c: a non-spherical or transverse Maxwell/spinor evolution with electric,
magnetic, Poynting, absorbing-boundary, and radiation-energy ledgers.

## Help wanted

Useful independent contributions are an independent weighted radial evolution
solver, a hostile audit of the reflecting boundary and Poisson projection, a
non-spherical Maxwell--Dirac/Soler implementation, or a formal
spinor-current/Gauss-law bridge in entropic-physlib.
