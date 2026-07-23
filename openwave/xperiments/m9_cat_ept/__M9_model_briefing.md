# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9.1--M9.6 establish the formal interface, scalar controls,
> information clock, scalar localization family, scaling ledger, and scalar-carrier
> boundary. M9.7a validates a localized nonlinear Dirac carrier in 1+1D. M9.7b1
> qualifies the spherical electrostatic Maxwell sector. M9.7b2 now closes a
> self-consistent stationary 3D radial spinor--electrostatic branch. Time-dependent
> Maxwell/spinor stability and physical particle identity remain open.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; entropic dynamics; nonlinear scalar and spinor solitary waves; stationary electrostatic Maxwell--Dirac systems |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | `formal_contract.py`, scalar and spinor control/localization modules, `electrostatic_gauge_3d.py`, `dirac_electrostatic_3d.py`, and M9.1--M9.7b2 research records |

## Model profile

| Attribute | M9 status |
| --- | --- |
| Scalar carrier | One-component complex scalar with exact neutral 1+1D bright-soliton family |
| 1+1D spinor carrier | Exact two-component Soler solitary wave passing M9.7a |
| 3D spinor ansatz | Spherical four-spinor `exp(-i omega t)(v chi, i u sigma.rhat chi)^T` |
| Coupled 3D dynamics | Stationary radial Soler attraction plus self-consistent electrostatic potential |
| Frozen M9.7b2 inputs | `m=epsilon0=q=N=1`, `lambda=64` |
| Stationary frequency | `omega=0.9914633829359464`, inside the mass gap |
| Localization scale | `R_rms=5.8792323633`; fraction inside `r<=16` is `0.98942404` |
| Electrostatic field | Spinor density sources `Q` and `phi`; the potential feeds back into the same Dirac equations |
| Signed sectors | `q -> -q` reverses `Q`, `phi`, and flux while preserving the stationary spinor and field energy |
| Entropic clock | Shell probability proportional to `(v^2+u^2) Delta V`; reflecting channel ledger closes |
| Electric charge | Dimensionless source label only; no physical charge-unit calibration |
| Spin | 3D spinor representation is used; fermionic quantization/statistics and measured spin observables remain absent |
| Stability | Stationary BVP branch and local initial-guess basin validated; no time-dependent orbital-stability result |
| CAT/EPT relation | Density and information interfaces are preserved; `lambda=64` and electrostatic dynamics are selected real-sector inputs, not derived from `S_I` |

## Field configurations

| Candidate | Configuration | Status |
| --- | --- | --- |
| Neutral scalar candidate | Bright scalar soliton in 1+1D | Validated mathematical candidate |
| 1+1D spinor candidate | Two-component Soler solitary wave | Validated replacement-carrier prerequisite |
| 3D stationary spinor candidate | Normalized spherical Soler spinor with electrostatic back-reaction | Validated selected-model stationary solution |
| Electron | No physical mass/charge calibration, magnetic moment, statistics, or experimental identification | Not established |
| Opposite source sector | Algebraic `q=-1` branch with reversed potential and flux | Dimensionless sector, not positron identification |
| Photon / radiation | No transverse Maxwell-wave or magnetic dynamics | Not established |

## Implementation status

| Sector | Status |
| --- | --- |
| M9.1--M9.6 | Complete scalar/formal/clock/carrier program |
| M9.7a | Complete 1+1D nonlinear spinor qualification |
| M9.7b1 | Complete 3D electrostatic source-and-field qualification |
| M9.7b2 | Complete coupled stationary radial spinor--electrostatic solve |
| Finest stationary residual | Spinor `2.83e-7`; Gauss relative `3.01e-6`; potential `3.69e-9` |
| Energy closure | Field/source mismatch `4.52e-10`; eigenvalue identity `5.72e-8` |
| Refinement | Spinor, density, and frequency observed orders approximately `3.96` |
| Window study | Frequency spread `7.38e-6`; central-potential spread `3.57e-5`; RMS-radius spread `2.32e-3` |
| Time-dependent 3D evolution | Open M9.7b3 |
| Interactive launcher | Deferred until M9.7b3 closes |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). The next target is
M9.7b3: evolve the converged stationary branch with dynamical gauge degrees of
freedom and close conservation, Gauss, radiation-flux, convergence, and
perturbation ledgers.

## Help wanted

Useful independent contributions are an independent radial BVP implementation, a
hostile audit of the `lambda=64` branch selection, a time-dependent spherical
Maxwell--Dirac/Soler solver, or a formal spinor-current/Gauss-law bridge in
entropic-physlib.
