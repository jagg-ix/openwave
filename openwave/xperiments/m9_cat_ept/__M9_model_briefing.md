# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** A formal-to-numerical program in which a complex field state
> is reconstructed from an entropic probability density and phase. M9.1 pins the
> Lean-to-Python contract, M9.2 certifies the free complex-field control, M9.3
> fixes an explicit coarse-graining clock, and M9.4 finds a convergent neutral
> 1+1D bright soliton in the first bounded nonlinear family. The soliton is a
> mathematical particle candidate, not yet an electron or a 3D matter model.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; Caticha-style entropic dynamics; Madelung reconstruction; Compton/de Broglie internal clocks |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | `formal_contract.py`, `free_solver.py`, `entropic_clock.py`, `localized_particle.py`, and the M9.1--M9.4 research records |

## Model profile

| Attribute | M9 status |
| --- | --- |
| Candidate state carrier | Complex scalar state `psi(x,t)` with `rho = |psi|^2` and phase/current potential `Phi` |
| Vacuum | Zero-field asymptotic state for the localized line solution; represented on a wide periodic box with exponentially small tails |
| Dynamics | Certified free Schrödinger control plus the bounded cubic family `i psi_t = -1/2 psi_xx + kappa |psi|^2 psi`; the cubic term is selected, not derived from CAT/EPT |
| Particle | Accepted mathematical candidate: `psi = sech(x)/sqrt(2) exp(i t/2)` at `kappa = -2`, neutral and localized in 1+1 dimensions |
| Entropic clock | Fixed cell map `p_i proportional to dx |psi_i|^2`; accumulated clock is KL information discarded by a declared doubly stochastic channel. Channel depth is not physical time |
| Imaginary action | `S_I = hbar tau_ent` at the formal weighting layer; no local imaginary potential is inserted into the evolution |
| Complex weight | Formal modulus `|W| = exp(-tau_ent)` |
| Internal clocks | Formal Compton/de Broglie/Zitterbewegung identities; the soliton phase frequency is measured next and has no physical mass interpretation yet |
| Charge | Absent. No topological or Noether electric charge is implemented |
| Spin | Absent. The scalar carrier supplies no spin-1/2 statistics |
| Derrick escape | In 1D the focusing cubic nonlinearity balances dispersion; this does not prove a 3D Derrick escape |
| EM / gravity | Formal source bridges exist, but the accepted candidate has no particle-level EM or gravitational coupling |
| Remaining structural choices | Derivation or replacement of the cubic term, 3D carrier, physical unit map, charge/spin structure, and any irreversible back-reaction |
| Next decisive falsifier | Failure of a declared 3D extension or failure to derive a localization functional independently of the target soliton |

## Field configuration of particles

| Particle | Configuration | Topological vortex? |
| --- | --- | --- |
| Neutral M9 candidate | Bright scalar soliton `sech(x)/sqrt(2) exp(i t/2)` in 1+1D | No |
| Electron | Not established; no charge or spin carrier | Not established |
| Positron | Not established | Not established |
| Free Gaussian packet | Certified dispersive control state; not a particle | No |
| Photon / radiation | Not established | No |

## Implementation status

| Sector | Status |
| --- | --- |
| Formal equation-to-code contract | M9.1 complete; pinned theorem paths, hypotheses, and limitations |
| Free field evolution | M9.2 complete; norm and discrete energy conserved, with phase, density, and current converging at approximately second order |
| Coarse-graining clock | M9.3 complete; fixed probability map and Markov channel, remaining KL contracts and accumulated gain grows along channel depth |
| Physical-time arrow | Not established; the M9.3 result is data processing, not unitary-time monotonicity |
| Localized candidate | M9.4 complete: focusing `kappa=-2` candidate passes convergence, stationary residual, tail, window, conservation, and perturbation gates |
| Negative controls | The identical seed disperses for free `kappa=0` and defocusing `kappa=+2` evolution |
| Finest candidate result | Fidelity `1.0`; density L1 `1.41e-8`; energy drift `7.00e-13`; core probability `0.999913`; edge probability `1.32e-12` |
| Physical particle identity | Open; candidate is neutral, scalar, 1+1D, and uncalibrated |
| Particle clock and scale | M9.5 next: phase frequency, energy, radius, scaling family, and explicit Compton-clock non-identification or bridge |
| Charge and spin | Gated on a new carrier, not inferred from the scalar soliton |
| Interactive Taichi launcher | Deferred until a validated 3D dynamics exists |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). M9.1--M9.4 are
complete. M9.5 must characterize the accepted soliton without converting its
dimensionless phase frequency into a particle mass by definition.

## Help wanted

Useful independent contributions are an alternate solver reproduction, a hostile
review of the M9.4 tolerance and perturbation budgets, a derivation of the
nonlinear functional from an information principle, or a bounded 3D extension
that can fail honestly.
