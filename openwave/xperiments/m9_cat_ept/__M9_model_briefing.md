# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** A formal-to-numerical program in which a complex field state
> is reconstructed from an entropic probability density and phase, while an
> information-theoretic clock supplies the imaginary-action cost and the exact
> complex-action damping factor. M9.1 certifies the translation of pinned Lean
> identities into Python; M9.2 certifies a convergent free complex-field control
> solver. M9 does **not** yet contain a localized particle, charge, spin, or a
> mass prediction.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; Caticha-style entropic dynamics; Madelung reconstruction; Compton/de Broglie internal clocks |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | `formal/entropic_spine_contract.json`, `formal_contract.py`, `free_solver.py`, `research/scripts/m9_1_formal_contract.py`, `research/scripts/m9_2_free_solver.py`, `research/m9_theory_canonical.md` |

## Model profile

| Attribute | M9 status |
| --- | --- |
| Candidate state carrier | Complex scalar state `psi(x,tau)` with `rho = |psi|^2` and phase/current potential `Phi` |
| Vacuum | Not fixed yet; must be frozen before the particle search |
| Dynamics | The linear free Schrödinger control is certified at second order by M9.2. The nonlinear real-action functional and any irreversible back-reaction remain open and must be preregistered |
| Particle | Not established. Target: finite-energy, localized, stationary or time-periodic solution that survives convergence, window, and perturbation gates |
| Entropic clock | `tau_ent = gamma D_KL(p_XY || p_X p_Y)` for an explicitly declared partition or coarse-graining map; the map is the M9.3 decision |
| Imaginary action | `S_I = hbar tau_ent` |
| Complex weight | Formal modulus `|W| = exp(-tau_ent)`; not promoted to a local imaginary potential |
| Internal clocks | Formal identities for Compton, de Broglie and rest-frame Zitterbewegung frequencies; no dynamical frequency-selection result yet |
| Charge | Absent. No topological or Noether charge has been selected |
| Spin | Absent. A scalar carrier does not supply spin-1/2 statistics |
| Derrick escape | Open; depends on the preregistered nonlinear dynamics |
| EM / gravity | Formal bridges exist in the source repository, but no M9 particle-level OpenWave simulation exists |
| Free choices currently exposed | vacuum, nonlinear functional, partition/coarse-graining map, boundary conditions for the particle search, scale map, calibration anchors |
| First decisive falsifier | No grid- and window-convergent localized state in the complete preregistered M9.4 family |

## Field configuration of particles

M9 has no accepted particle configuration.

| Particle | Configuration | Topological vortex? |
| --- | --- | --- |
| Electron | Not established | Not established |
| Positron | Not established | Not established |
| Neutral scalar candidate | Target of the first localization search; no accepted solution yet | No topology selected |
| Free Gaussian packet | Certified dispersive control state; not a particle | No |
| Photon / radiation | Not established | No |

## Implementation status

The M9.1 and M9.2 results certify interfaces and a free-wave control solver, not
a phenomenological particle cell. All 21 shared OpenWave criteria remain `not yet
tested` until a script measures the corresponding physical observable.

| Sector | Status |
| --- | --- |
| Formal equation-to-code contract | M9.1 complete; pinned source and limitations recorded |
| Born/Madelung transcription | Deterministic numerical identity check |
| Compton/de Broglie/Zitterbewegung relations | Deterministic numerical identities; no particle frequency selection |
| Entropic clock and complex-weight modulus | Deterministic finite-distribution checks; no arbitrary-dynamics monotonicity claim |
| Free field evolution | M9.2 complete: norm and discrete energy conserved; phase, density and current converge at approximately second order to the exact Gaussian packet |
| Finest free-solver result | Fidelity `0.999970`; density L1 `5.72e-3`; current relative L2 `7.02e-3`; continuum-energy error `1.75e-3`; no periodic wraparound |
| Entropic-clock dynamics | Planned M9.3; probability map must be frozen first |
| Localized particle existence and stability | Planned decisive gate M9.4 |
| Particle observables and clock comparison | Gated on M9.4 |
| Interactive Taichi launcher | Deliberately deferred until a particle dynamics validates headlessly |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). M9.1 and M9.2 are
complete. The next task fixes the field-to-probability/coarse-graining contract
and tests distinct entropic clocks before any nonlinear localization search.

## Help wanted

The most useful independent contributions are: audit the theorem-to-code map;
implement an independent free solver; challenge the M9.2 convergence ledger;
propose a fixed coarse-graining map for M9.3; or design a sharply bounded
localization functional before seeing M9.4 results.
