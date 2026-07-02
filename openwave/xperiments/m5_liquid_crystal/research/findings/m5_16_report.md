# M5.16 calibration report: axisymmetric energy minimization + the parameter lock

> The static energy-minimization program prescribed 2026-07-01 (lattice minimization, hedgehog initial configuration, cylindrical symmetry to reduce dimension, regularization in the center, potential parameters fixed by agreement with physics), implemented and run 2026-07-02. This page is the review surface: the method, the locked parameters, the one headline number, the honest residuals, and the five questions the results raise. Everything is reproducible from the three scripts linked at the bottom.

Convention throughout: `M = O·D·Oᵀ`, `D = diag(g, 1, δ, 0)` index-0, `η = diag(−1, 1, 1, 1)`.

## Method (the prescription, item by item)

| Prescribed | Implemented |
| --- | --- |
| cylindrical symmetry to reduce dimension | equivariant ansatz `M(ρ,φ,z) = R₁₂(φ)·M̃(ρ,z)·R₁₂(φ)ᵀ`: the azimuthal derivative becomes the exact algebraic channel `(1/ρ)[J, M̃]`, reducing the full 3D functional to the (ρ,z) half-plane with weight `2πρ` |
| energy minimization | preconditioned FIRE + nonlinear conjugate gradient (Polak-Ribière, bracketing/golden-section line search, the Faber-group recipe), independent cross-checks; analytic gradient validated against finite differences to 3.6e-7 |
| regularization in the center | the melt profile `s(r)` (eigenvalue amplitude → 0 at the core) under the calibrated potential; the axis `ρ = 0` handled by a cell-centered grid + the mirror ghost `M̃(−ρ) = P·M̃(ρ)·P`, no one-sided bias |
| verification before claims | 7 pre-registered gates, all pass, including two closed-form anchors derived by hand: the pure-hedgehog curvature density is exactly `8c₂/r⁴`, and a spherical shell integrates to `32πc₂(1/r₁ − 1/r₂)`; plus 2D ≡ 3D equivalence converging at h² order |
| the physical `g ~ 1e10`, `δ ~ 1e-10` regime | `g`: measured EXACTLY decoupled from statics (E identical at `g = 8` and `g = 1e10`, relative difference 0.0), so the electron sector carries no g-arithmetic risk. `δ`: the energy is an exact quartic polynomial in δ, so its orders are extracted cancellation-free at O(1) sample nodes and evaluated at `δ = 1e-10` to machine precision (no f64 catastrophic loss) |
| heavy, not seconds | the production runs are converged (gradient falls 6 decades, monotone; the Derrick virial `E_curv = 3·E_pot` holds to 0.3-0.6%; the h-refinement study moves the result by 0.01% at the last step) |

## The anchor chain and the locked parameters

The potential coefficients were not guessed; they were forced by the anchors:

1. **Vacuum structure**: zero forcing at the uniaxial vacuum `s = 1` (spectrum `(1, δ→0, 0)`) pins `a = (3b − 4c)/2` with melt cost `c − b/2 > 0`; one shape ratio `β = b/c ∈ (0, 2)` remains.
2. **Coulomb**: the relaxed hedgehog's far field is the pure director hedgehog with curvature density exactly `8c₂/r⁴`; matching the exterior energy to the classical EM self-energy `αħc/2r` gives, analytically, `c₂ = αħc/64π`.
3. **Electron mass**: `E = m_e c²` at the minimum fixes the length unit, hence `(a, b, c)` in physical units.

| Parameter | Value | Anchor |
| --- | --- | --- |
| `c₂` | `7.1618e-3 MeV·fm` = `αħc/64π`, exact | Coulomb |
| length unit | `0.2495 fm` per grid unit (β = 1 row) | m_e |
| `(a, b, c)` at β = 1 | `(−3.48e-3, 6.97e-3, 6.97e-3) MeV/fm³` (full β family in the JSON) | vacuum structure + m_e |
| `κ_δ = (3/2)·b` | `1.05e-2 MeV/fm³` at β = 1 | the δ-axis stiffness: the cubic term alone restores the δ eigenvalue (derived); the natural neutrino-sector calibration handle |
| `δ` | `1e-10` working value; its energy contribution computed exactly (below) | pending a sharp anchor |
| `g` | `1e10` working value (`g·δ = 1`) | statics are measured g-blind; g must come from the clock/boost or baryon-mass anchor |

## The headline: a parameter-free size agreement with the SU(2) soliton

With Coulomb fixing `c₂` and `m_e` fixing the scale, nothing is left to tune, and the electron's energy-median radius (the radius enclosing half the rest energy, tail included; the same observable evaluated on the arctan profile of Faber & Golubich for the reference) is a prediction:

| Observable | M5 functional | Faber SU(2) reference | Gap |
| --- | --- | --- | --- |
| `r_half` | **2.926 fm** (h-converged: 2.888 / 2.925 / 2.926 fm at core resolutions 5.3 / 8 / 10.7 cells) | **3.075 fm** (`u_half = 1.389`, integrand verified to `π/4` at 1e-11) | **−4.8%**, genuine model difference (discretization converged out at the 0.01% level) |

Two different field theories, the M5 quartic tensor-commutator functional and the SU(2) topological-fermion soliton, anchored the same way, land on the same electron size to five percent. The prediction is stable across the entire admissible shape-ratio family (2.916 to 2.939 fm for β from 0.25 to 1.5), which also means `β` is NOT determined by the electron sector: it survives as the one honest free ratio, and its physical meaning `κ_δ = (3/2)b` hands the neutrino sector its calibration equation.

The δ-sector energy on this solution, computed exactly: at `δ = 1e-10` the δ eigenvalue shifts the electron rest energy by a fractional `−1.5e-10` (the two admissible axisymmetric δ-textures differ by 0.27% at first order). The quantum-phase contribution to the static electron is indeed tiny, now with a number.

## Honest residuals (what the run could not decide)

| Residual | Status |
| --- | --- |
| the spherical hedgehog is a SADDLE of the unconstrained axisymmetric functional: a perturbed relax descends 35% below the spherical minimum and the melt moves off-origin (the liquid-crystal point-vs-ring escape; there is no Frank-type quadratic term to hold the point defect). The calibration therefore ran in the spherically-constrained class | measured; raises the point-vs-ring question below |
| the quartic trace-LdG cannot be exactly stationary at the biaxial `(1, δ, 0)`: the residual force on the δ eigenvalue is `3bδ` | derived; raises the sixth-order / dynamical-δ question below |
| `β = b/c` un-pinned by the electron sector; `g` un-pinned by statics (structurally) | the two open slots of the lock table |
| the δ-continuation probe (biaxiality walked from the old placeholder 0.3 toward the quasi-uniaxial physical regime, everything else held at the prior vortex-loop run settings): all four obstruction indicators relax monotonically toward the uniaxial limit, but no localized knot forms from biaxiality reduction alone | supportive for the physical-regime vortex-loop re-entry, not sufficient by itself |

## The five questions these results raise

In priority order (full statements in [`../m5_question_tracker.md`](../m5_question_tracker.md) § QUESTIONS TO DUDA): (1) does the M5 substrate carry a chiral Lifshitz invariant, or is achirality intended; (2) the neutrino seed topology, linked pair vs trefoil vs the two-vortex-type sketch; (3) point vs ring at the hedgehog core, and if the symmetric hedgehog is intended, what holds it; (4) is a sixth-order LdG invariant intended to pin the biaxial vacuum, or is δ dynamical; (5) preferred anchors for the two open slots, β (via the δ-sector stiffness) and g.

## What to inspect (the minimal set)

| Artifact | What it shows |
| --- | --- |
| [`../scripts/m5_16_axisym.py`](../scripts/m5_16_axisym.py) | the instrument: the reduction, the analytic gradient, the 7 gates, the radial (spherically-constrained) solver, the stability probe, the exact δ-grading. The docstring carries the derivations |
| [`../scripts/m5_16_calibrate.py`](../scripts/m5_16_calibrate.py) | the anchor chain end to end: Coulomb → `c₂`, m_e → scale, the β sweep, the Faber reference, the lock output |
| [`../data/m5_16_parameter_lock.json`](../data/m5_16_parameter_lock.json) | the deliverable: every locked number with its anchor, the sweep rows, the convergence family |
| [`../plots/m5_16_calibration.png`](../plots/m5_16_calibration.png) | the melt profiles, the r_half-vs-Faber panel, the virial, the h-convergence |

Supporting (only if of interest): the δ-continuation probe [`../scripts/m5_16_delta_continuation.py`](../scripts/m5_16_delta_continuation.py) + [`../plots/m5_16_delta_continuation.png`](../plots/m5_16_delta_continuation.png), and the full task record with the gate-by-gate rigor table: [`../tasks/m5_16_task_details.md`](../tasks/m5_16_task_details.md).
