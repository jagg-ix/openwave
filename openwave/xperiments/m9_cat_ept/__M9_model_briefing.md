# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9.1--M9.6 establish the formal interface, free control,
> coarse-graining clock, scalar localization family, scaling ledger, and scalar
> carrier boundary. M9.7a now validates a bounded two-component nonlinear Dirac
> replacement carrier in 1+1 dimensions while preserving the density-clock
> interface. Three-dimensional localization and dynamical electromagnetism remain
> open.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; entropic dynamics; nonlinear scalar and spinor solitary waves; Compton/de Broglie internal clocks |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | `formal_contract.py`, `free_solver.py`, `entropic_clock.py`, `localized_particle.py`, `soliton_observables.py`, `carrier_audit.py`, `spinor_carrier.py`, and M9.1--M9.7a research records |

## Model profile

| Attribute | M9 status |
| --- | --- |
| Scalar carrier | One-component complex scalar with an exact neutral 1+1D bright-soliton family |
| Spinor replacement | Two-component 1+1D Soler carrier with `alpha=-sigma_2`, `beta=sigma_3`, `m=1`, `lambda=1`, `omega=0.8` |
| Vacuum | Zero-field asymptotic state represented on a wide periodic box with exponentially small tails |
| Scalar dynamics | Selected focusing cubic; not derived from CAT/EPT |
| Spinor dynamics | Selected cubic scalar self-interaction in the nonlinear Dirac equation; not derived from CAT/EPT |
| Scalar candidate | Exact bright soliton; validated but spin-0, neutral, and non-topological |
| Spinor candidate | Exact two-component Soler solitary wave; validated under the M9.7a 1+1D gate |
| Entropic clock | `p_i proportional to dx Psi_i^dagger Psi_i`; the existing periodic coarse-graining channel remains valid. Channel depth is not physical time |
| Local gauge interface | Pure-gauge background connection implemented with covariant energy invariance; no dynamical Maxwell field |
| Electric charge | Not established: `q=1` is a dimensionless interface parameter, not a calibrated electric charge |
| Spin | Spinor carrier structure is present in 1+1D; 3D angular momentum, spin-1/2 particle identity, and fermionic statistics are not established |
| Topology | Neither accepted 1+1D profile carries a protected target-space winding certificate |
| Dimensional scope | Scalar and spinor results are exact/numerically verified in 1+1D only |
| Remaining choices | 3D carrier, dynamical gauge field, physical units, charge normalization, statistics, and irreversible back-reaction |

## Field configurations

| Candidate | Configuration | Status |
| --- | --- | --- |
| Neutral scalar M9 candidate | Bright scalar soliton in 1+1D | Validated mathematical candidate |
| Spinor M9 candidate | Two-component Soler solitary wave in 1+1D | Validated replacement-carrier prerequisite |
| Electron | No 3D gauge-spinor solution, charge unit, magnetic moment, or statistics layer | Not established |
| Positron | No opposite gauge-charge sector or pair dynamics | Not established |
| Free Gaussian packet | Dispersive Schrödinger control | Not a particle |
| Free Dirac spinor | Identical Soler seed disperses when the nonlinear term is disabled | Control, not a particle |
| Photon / radiation | No dynamical vector gauge field | Not established |

## Implementation status

| Sector | Status |
| --- | --- |
| M9.1 formal contract | Complete |
| M9.2 free scalar solver | Complete; approximately second-order convergence |
| M9.3 coarse-graining clock | Complete; data-processing ledger closes |
| M9.4 scalar localization | Complete; focusing branch localizes, controls disperse |
| M9.5 scalar scaling | Complete; nine-case exact observable ledger |
| M9.6 scalar carrier audit | Complete; charge/spin/topology limitations made executable |
| M9.7a spinor qualification | Complete; exact profile, convergence, conservation, window, perturbation, gauge-interface, and clock gates pass |
| Finest spinor result | Spinor L2 `1.53e-7`; density relative L1 `8.73e-8`; fidelity `0.99999999999998`; norm drift `1.69e-13`; energy drift `1.04e-13` |
| Spinor perturbation | At `t=10`, core `0.99978987`, edge `3.14e-11`, fidelity `0.99994829` |
| 3D gauge-spinor carrier | Open M9.7b |
| Interactive launcher | Deferred until M9.7b passes |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). M9.7a closes the
bounded non-scalar prerequisite. The next scientific target is a frozen 3D
spinor-plus-dynamical-gauge family with explicit Gauss-law and localization gates.

## Help wanted

Useful independent contributions are a hostile audit of the Soler implementation,
a bounded 3D Maxwell-Dirac/Soler family, an independent stability solver, or a
formal bridge connecting the spinor density and current to entropic-physlib.
