# M9 CAT/EPT: Entropic Particle Dynamics

> **What M9 brings.** A formal-to-numerical program in which a complex field state
> is reconstructed from an entropic probability density and phase, while an
> information-theoretic clock supplies the imaginary-action cost and the exact
> complex-action damping factor. The first task only certifies the translation of
> pinned Lean identities into Python. M9 does **not** yet contain a localized
> particle, a charge invariant, spin, or a mass prediction.

## Identity

| Field | Value |
| --- | --- |
| Model ID | M9 |
| Name | CAT/EPT Entropic Particle Dynamics |
| Author | Jorge A. Garcia |
| Lineage | Complex Action Theory / Entropic Proper Time; Caticha-style entropic dynamics; Madelung reconstruction; Compton/de Broglie internal clocks |
| Formal source | `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, commit `f6e2b37571086e5ef6de40f77439a5eab468f71f` |
| In-repo | `formal/entropic_spine_contract.json`, `formal_contract.py`, `research/scripts/m9_1_formal_contract.py`, `research/m9_theory_canonical.md` |

## Model profile

| Attribute | M9 status at scaffold |
| --- | --- |
| Candidate state carrier | Complex scalar state `psi(x,tau)` with `rho = |psi|^2` and phase/current potential `Phi` |
| Vacuum | Not fixed yet; must be frozen before the particle search |
| Dynamics | Not fixed yet. M9.2 will certify a free entropic-dynamics solver; M9.4 will preregister the nonlinear families used for localization |
| Particle | Not established. Target: finite-energy, localized, stationary or time-periodic solution that survives convergence, window, and perturbation gates |
| Entropic clock | `tau_ent = gamma D_KL(p_XY || p_X p_Y)` for an explicitly declared partition or coarse-graining map |
| Imaginary action | `S_I = hbar tau_ent` |
| Complex weight | Formal modulus `|W| = exp(-tau_ent)`; not yet promoted to a local imaginary potential |
| Internal clocks | Formal identities for Compton, de Broglie and rest-frame Zitterbewegung frequencies; no dynamical frequency-selection result yet |
| Charge | Absent. No topological or Noether charge has been selected |
| Spin | Absent. A scalar carrier does not supply spin-1/2 statistics |
| Derrick escape | Open; depends on the preregistered nonlinear dynamics |
| EM / gravity | Formal bridges exist in the source repository, but no M9 particle-level OpenWave simulation exists |
| Free choices currently exposed | state carrier, vacuum, real-action functional, nonlinear family, partition/coarse-graining map, boundary conditions, scale map, calibration anchors |
| First decisive falsifier | No grid- and window-convergent localized state in the complete preregistered M9.4 family |

## Field configuration of particles

M9 has no accepted particle configuration at scaffold stage.

| Particle | Configuration | Topological vortex? |
| --- | --- | --- |
| Electron | Not established | Not established |
| Positron | Not established | Not established |
| Neutral scalar candidate | Target of the first localization search; no accepted solution yet | No topology selected |
| Photon / radiation | Not established | No |

## Implementation status

The formal conformance layer is infrastructure, not a phenomenological cell. All
21 shared OpenWave criteria remain `not yet tested` until a script measures the
corresponding physical observable.

| Sector | Status |
| --- | --- |
| Formal equation-to-code contract | Implemented in M9.1; pinned source and limitations recorded |
| Born/Madelung transcription | Deterministic numerical identity check |
| Compton/de Broglie/Zitterbewegung relations | Deterministic numerical identity checks; no particle frequency selection |
| Entropic clock and complex-weight modulus | Deterministic finite-distribution checks; no claim of monotonicity for arbitrary dynamics |
| Free field evolution | Planned M9.2 |
| Entropic-clock dynamics | Planned M9.3 |
| Localized particle existence and stability | Planned decisive gate M9.4 |
| Particle observables and clock comparison | Gated on M9.4 |
| Interactive Taichi launcher | Deliberately deferred until a particle dynamics validates headlessly |

## Roadmap

See [`research/m9_roadmap.md`](research/m9_roadmap.md). The sequence is formal
contract, free-solver certification, clock measurement, preregistered particle
search, particle observables, then rendering.

## Help wanted

The most useful independent contributions are: audit the theorem-to-code map;
propose a sharply bounded localization functional before seeing results; implement
an independent solver; or attempt to falsify localization and clock monotonicity
under the stated gates.
