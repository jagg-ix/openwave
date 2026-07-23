# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** M9.1 pins the Lean-to-Python contract, M9.2 certifies the
> free complex-field control, M9.3 fixes an explicit coarse-graining clock, and
> M9.4 validates a neutral 1+1D bright soliton in the first bounded nonlinear
> family. M9.5 now characterizes its exact scaling, radius, energy, and phase
> frequency without converting a dimensionless identity into a mass prediction.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; Caticha-style entropic dynamics; Madelung reconstruction; Compton/de Broglie internal clocks |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | `formal_contract.py`, `free_solver.py`, `entropic_clock.py`, `localized_particle.py`, `soliton_scaling.py`, and M9.1--M9.5 research records |

## Model profile

| Attribute | M9 status |
| --- | --- |
| Carrier | One-component complex scalar `psi(x,t)` with `rho = |psi|^2` |
| Vacuum | Zero-field asymptotic state represented on a wide periodic box with exponentially small tails |
| Dynamics | Free control plus selected focusing cubic `i psi_t = -1/2 psi_xx - g |psi|^2 psi`; the interaction is not derived from CAT/EPT |
| Localized family | `eta = gN/2`, `psi = eta/sqrt(g) sech(eta x) exp(i eta^2 t/2)` |
| Reference candidate | `g=2`, `N=1`: amplitude `1/sqrt(2)`, phase frequency `1/2`, energy `-1/6`, RMS radius `pi/(2sqrt(3))` |
| Entropic clock | Cell probabilities `p_i proportional to dx |psi_i|^2`; accumulated clock is KL information discarded by a fixed channel. Channel depth is not physical time |
| Phase clock | `omega_phase = eta^2/2`; a dimensionless family property, not a physical Compton or Zitterbewegung frequency |
| Conditional clock bridge | Compton identification gives `R_rms/lambda_C = pi/sqrt(24)`; ZBW identification gives `pi/sqrt(48)`. Both are assumptions, not mass predictions |
| Charge | Absent. No gauge field, Gauss flux, or opposite-charge sector |
| Spin | Absent. The scalar carrier supplies no intrinsic spin-1/2 representation |
| Dimensional scope | Exact and numerically verified in 1+1 dimensions; no 3D Derrick result |
| Remaining choices | Derivation/replacement of the cubic term, physical units, charged spinor carrier, 3D dynamics, irreversible back-reaction |

## Field configurations

| Particle | Configuration | Status |
| --- | --- | --- |
| Neutral M9 candidate | Bright scalar soliton in 1+1D | Validated mathematical candidate |
| Electron | No charge or spin carrier | Not established |
| Positron | No opposite-charge sector | Not established |
| Free Gaussian packet | Dispersive control state | Not a particle |
| Photon / radiation | No vector/gauge carrier | Not established |

## Implementation status

| Sector | Status |
| --- | --- |
| M9.1 formal contract | Complete |
| M9.2 free solver | Complete; approximately second-order phase, density, and current convergence |
| M9.3 coarse-graining clock | Complete; remaining KL contracts and accumulated discarded information grows along channel depth |
| M9.4 localization | Complete; focusing candidate passes convergence, residual, tail, window, conservation, and perturbation gates; controls disperse |
| M9.5 scaling family | Complete; nine `(g,N)` members verify exact norm, energy, radius, phase, and scaling identities |
| Scale invariant | `omega_phase R_rms^2 = pi^2/24` |
| Energy identity | `E/(mu N) = 1/3` |
| Physical particle identity | Open; no absolute mass or length scale is predicted |
| Charge/spin audit | M9.6 next; must state the scalar no-go and replacement-carrier requirements |
| Interactive launcher | Deferred until validated 3D dynamics exists |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). M9.6 is the next
reviewable target: an explicit scalar charge/spin no-go plus a staged gauge-spinor
replacement contract that preserves the CAT/EPT density and clock interfaces.

## Help wanted

Useful independent contributions are a derivation of the nonlinear functional,
a hostile audit of the clock-unit bridge, a charged spinor carrier design, or a
bounded 3D extension with explicit failure criteria.
