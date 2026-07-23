# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9.1--M9.6 establish the formal interface, scalar controls,
> information clock, scalar localization family, scaling ledger, and scalar-carrier
> boundary. M9.7a validates a localized two-component nonlinear Dirac carrier in
> 1+1D. M9.7b1 now qualifies a self-consistent three-dimensional electrostatic
> Maxwell sector sourced by a regular spherical spinor density. The coupled 3D
> Dirac--Maxwell stationary problem remains open.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; entropic dynamics; nonlinear scalar and spinor solitary waves; electrostatic Maxwell constraints; Compton/de Broglie internal clocks |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | `formal_contract.py`, `free_solver.py`, `entropic_clock.py`, `localized_particle.py`, `soliton_observables.py`, `carrier_audit.py`, `spinor_carrier.py`, `electrostatic_gauge_3d.py`, and M9.1--M9.7b1 research records |

## Model profile

| Attribute | M9 status |
| --- | --- |
| Scalar carrier | One-component complex scalar with an exact neutral 1+1D bright-soliton family |
| Spinor replacement | Two-component 1+1D Soler carrier; exact localized profile passes M9.7a |
| 3D gauge source | Regular spherical four-spinor density ansatz with upper s-wave and lower p-wave radial amplitudes |
| Electrostatic field | Self-consistent spherical Gauss-law solution with Coulomb exterior tail and field energy |
| Vacuum | Zero-field asymptotic state; radial field uses `phi(infinity)=0` and analytic exterior tail |
| Entropic clock | Scalar/spinor density maps remain positive; the radial gate uses shell probabilities and a reflecting doubly-stochastic channel. Channel depth is not physical time |
| Local gauge interface | Background pure-gauge covariance is validated in M9.7a; M9.7b1 adds a source-responsive electrostatic field |
| Signed charge | Dimensionless `q=+1` and `q=-1` reverse field, potential, and boundary flux while preserving density and field energy |
| Electric charge | Not physically calibrated; no electron-charge unit or Standard Model assignment |
| Spin | Spinor representation exists in 1+1D; no solved 3D angular-momentum state or fermionic statistics layer |
| 3D localization | The M9.7b1 density is a frozen regular source ansatz, not a coupled Dirac stationary solution |
| Remaining choices | Coupled 3D spinor equation, self-consistent back-reaction, magnetic/time-dependent Maxwell fields, physical units, charge calibration, statistics, and irreversible CAT/EPT back-reaction |

## Field configurations

| Candidate | Configuration | Status |
| --- | --- | --- |
| Neutral scalar candidate | Bright scalar soliton in 1+1D | Validated mathematical candidate |
| Spinor candidate | Two-component Soler solitary wave in 1+1D | Validated replacement-carrier prerequisite |
| 3D electrostatic source | Regular spherical spinor density plus self-consistent Coulomb field | Gauge-sector qualification only |
| Electron | No coupled 3D gauge-spinor stationary state, physical charge unit, magnetic moment, or statistics layer | Not established |
| Positron | Dimensionless opposite source sign exists; no calibrated antiparticle sector or pair dynamics | Not established |
| Photon / radiation | No Maxwell wave evolution or magnetic field | Not established |

## Implementation status

| Sector | Status |
| --- | --- |
| M9.1 formal contract | Complete |
| M9.2 free scalar solver | Complete |
| M9.3 coarse-graining clock | Complete |
| M9.4 scalar localization | Complete |
| M9.5 scalar scaling | Complete |
| M9.6 scalar carrier audit | Complete |
| M9.7a spinor qualification | Complete; exact 1+1D profile, convergence, conservation, perturbation, background-gauge, and clock gates pass |
| M9.7b1 electrostatic Maxwell gate | Complete; Gauss law, boundary flux, field energy, signed sectors, convergence, window, perturbation-response, and radial-clock gates pass |
| Finest M9.7b1 result | Gauss residual `4.01e-16`; flux error `1.11e-16`; field-energy error `2.19e-5`; central-potential error `4.20e-5` |
| Coupled 3D stationary spinor--electrostatic solve | Open M9.7b2 |
| Interactive launcher | Deferred until coupled 3D dynamics and gauge evolution pass |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). The next target is
M9.7b2: a bounded self-consistent stationary radial Dirac--electrostatic solve.
M9.7b1 supplies the gauge solver and ledgers but does not preselect a successful
coupled spinor profile.

## Help wanted

Useful independent contributions are a derivation and audit of the radial 3D
Dirac conventions, an independent coupled Maxwell--Dirac/Soler BVP solver, a
bounded negative-result search, or a formal bridge for spinor current and Gauss
law in entropic-physlib.
