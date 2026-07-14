# M5 / Liquid Crystal: the theory canonical (working recipes of record)

> **Purpose.** The living registry of what WORKS in the M5 program: every equation, numerical recipe, and anchor that has survived its gates, in one place, with provenance. The per-task method notes ([`findings/`](findings/)) document the back-and-forth (what was tried, what failed, why); this doc is the consolidated specification: if a simulation needs a seed, a relaxer, an integrator, a formulation, or a locked number, it comes from here. Inspired by the M7 canonical ([`m7_theory_canonical.md`](../../m7_hydroboros/research/m7_theory_canonical.md)) and the M6 archive canonical; in sync with the model briefing ([`__M5_model_briefing.md`](../__M5_model_briefing.md)).
>
> **Maintenance rule (standing).** At every task REVIEW that lands a working equation, recipe, or anchor, ADD or AMEND the row here (one row, method-note link as provenance); measured negatives land in § 6 (anti-recipes are recipes too). Superseded rows are struck or annotated, never silently deleted. Consolidated 2026-07-14 from the method notes M5.16 → M5.20.4 + M5.21.

## 1. The verified theory (conventions pinned, with provenance)

**Field content + conventions** (index-0 = time/g axis, the Duda convention; [`findings/m5_18_verification_note.md`](findings/m5_18_verification_note.md) § 1):

```text
M(x)   real symmetric 4x4 tensor field,  eta = diag(-1, 1, 1, 1)
M'(x') = Lam^-T M(x) Lam^-1  (rank-2 covariant;  Lam^T eta Lam = eta)
[A, B]_eta = A.eta.B - B.eta.A          F_mu nu = [d_mu M, d_nu M]_eta
Tr_eta(M^p) = tr((eta M)^p)             (the mixed tensor eta.M carries the spectrum)
```

**The Lagrangian of record** (M5.18-verified, 15/15 machine checks; Lorentz invariance 1.3e-11, potential drift 2.0e-14, no-η negative control fails as required):

```text
L = - SUM_{mu<nu} eta^mumu eta^nunu <F_mu nu, F_mu nu>_eta  -  V(M)
V = w SUM_{p=1..4} (Tr_eta(M^p) - C_p)^2 ,   C_p = g^p + 1 + delta^p
g = 8,  delta = 0.3 (working; see the delta lock row in § 4)
```

| Verified structure | Statement | Gate / precision | Source |
| --- | --- | --- | --- |
| Covariant vacuum | `M_vac = diag(-g, 1, delta, 0)` (time-time NEGATIVE); `V(M_vac) = 0` exactly; `diag(+g,1,delta,0)` is NOT a vacuum (`V ≈ 1.05e6` at g = 8): spectrum statements always mean spectrum of `eta.M` | machine-exact | [m5_18 § 5](findings/m5_18_verification_note.md) |
| Vacuum manifold | union of 4 disjoint Lorentz orbits (timelike-eigenvalue label); the g-timelike branch is the physical one in current use | measured | [m5_18 § 6](findings/m5_18_verification_note.md) |
| Legendre structure | `H = T + U` exact (`pi:Mdot = 2T`; `H = L(Mdot) - 2L(0)` to 3.6e-16); T exactly quadratic in Mdot | machine | [m5_18 § 3](findings/m5_18_verification_note.md) |
| THE kinetic operator (closed form) | `T_tot = 1/2 Mdot.KK(M).Mdot`, `KK = 4 w_cell k_apply(M)`; `k_apply(M)[X] = 2 SUM_i (eta X W_i + W_i X eta - 2 Y_i X Y_i)`, `W_i = eta A_i eta A_i eta`, `Y_i = eta A_i eta` | GC0d: fast == 10-pass build 7e-18 | [m5_20_3 § 1](findings/m5_20_3_method_note.md) |
| The primary constraint | `Mdot ∝ eta` is an EXACT global null of k_apply (`[eta, B]_eta = 0` for every symmetric B); K(M) vanishes on gradient-free states and is degenerate everywhere | exact null 8e-19 | [m5_18 § 4](findings/m5_18_verification_note.md), [m5_20_3 § 1](findings/m5_20_3_method_note.md) |
| K(M) structure on loops | rank 5/10 EXACT (98.8% of cells; rank 8 at 392 core cells); 2 negative-inertia directions generic, 3 at core; uniform-vacuum active spectrum `(8c², 2c², 2c², −2c², −2c²)` = two ± pairs + one unpaired positive | measured + audited | [m5_20_3 § 3](findings/m5_20_3_method_note.md) |
| H is indefinite | boost-gradient × rotation-gradient product textures on the vacuum manifold reach density −97.8 to −127.7 at V = 0: H unbounded below in the unconstrained functional | measured | [m5_18 § 6](findings/m5_18_verification_note.md) |
| The free-EL energy identity | `dE/dt = − SUM_cells 4w (V_null · RHS_null)` (the null-projection leak is the ONLY channel besides integrator error) | GC0e 6e-17; re-derived 9.7e-12 | [m5_20_3 § 1](findings/m5_20_3_method_note.md) |
| Statics spatial sector | `u_eta = 4 SUM_{i<j} <F_ij, F_ij>_eta` reduces EXACTLY to the audited M5.17 plain `u_curv` on spatial-block fields (GB0); every M5.16 static number carries over to the 4D signature (blindness check 1.4e-14) | GB0 ≤ 1e-12 | [m5_20_2 § II](findings/m5_20_2_method_note.md), [m5_18 § 7](findings/m5_18_verification_note.md) |
| Superseded potential | the quartic trace-LdG `V = a·Tr(M²) − b·Tr(M³) + c·(TrM²)²` (M5.16/M5.17 era) is SUPERSEDED by the universal spectral potential above; the M5.16 results stay valid as the quartic-LdG record and the c₂ lock is curvature-side (carries over) | recorded | [m5_17 § 10](findings/m5_17_methods_note.md) |

## 2. The dynamics formulation of record (settled 2026-07-14)

The load-bearing verdict chain, each step measured and adversarially audited:

| # | Verdict | The recipe consequence | Source |
| --- | --- | --- | --- |
| 1 | **The free-EL IVP of the purely-quartic L is ILL-POSED**: no Lipschitz bound (unregularized blowup in a fixed step count ~3, amplitude-independent); EVERY regularization (spectral cutoff ladder 1e-8 → 1e-1, Tikhonov) blows up in finite time, monotone in cutoff, NO plateau; mechanism = roundoff-seeded boost-sector exponential (σ = 6.31-80.9/t; t* ≈ onset + ln(0.1/1e-16)/σ reproduces every run); E → −∞ | do NOT integrate the free EL and expect convergence; regularized runs are diagnostics only, trusted to t ≲ 1.8-2.4 (winding reads) | [m5_20_3 § 4](findings/m5_20_3_method_note.md), audit 6C/2Q/1R |
| 2 | **No single sanctioned term fixes K**: no commutator-class ("Skyrme-like") term lifts the η-null (lemma L1, class-structural) or removes its negatives (dressed-Skyrme measured negative everywhere); the unique closing family (`qc`: two-sided dressing `−β η^μν tr(X_μPX_νP)`, `P = aI − ηM`, window a ∈ (1, g)) closes everything at β\* = 1.306 but is FORCED to charge the zero-energy co-rotating vacuum texture (9.1e4 at β*) and destroys the loop statics | no single-term regularization; the closure-vs-texture sign algebra is rigid (incl. P ≠ Q) | [m5_20_4 § 1](findings/m5_20_4_method_note.md) |
| 3 | **Zero-energy Dirac data does not exist at the loop**: null-bundle velocities cannot touch the b0-sector static force (null-projected cancellation EXACTLY 0; from-rest nff = 0.9999977); full-velocity consistent data is OPEN (structured (0,2) time-mixing velocities reach 11.5%: hard solve, successor) | "from rest" is EL-inconsistent under the true L; do not build initial data by V = 0 + hope | [m5_20_4 § 2](findings/m5_20_4_method_note.md) |
| 4 | ✅ **THE WORKING FORMULATION: the free-period least-action BVP.** Rigid conjugation orbits `M(x,t) = Λ(ωt)M₀(x)Λ(ωt)ᵀ`: `S(ω) = (2π/ω)(ω²Q2 − U)`, stationarity `dS/dω = 0 ⇒ ω*² = −U/Q2` with the EXACT identity `H = ω*²Q2 + U = 0`. Roots need sign(U) ≠ sign(Q2): pure rotations fail (Q2 > 0), but **boost-conjugated rotations `ΛJΛ⁻¹` are exactly periodic and all six families cross Q2 = 0**: real roots with U > 0, ω*(χ) spanning ~6e-5 … 2e-2. Confirmed under the audit-corrected φ-averaged kinetic (`Q2_avg`, § 3 below). The theory's negative kinetic directions ARE the clock's enabler ("negative Hamiltonian terms propel angular momentum", quantified) | the oscillation program runs through least-action orbits, not initial-value integration; root recipe: `q2_avg` + `u_of` + the balance formula; extremal solve = [M5.20.5](tasks/m5_20_5_task_details.md) | [m5_20_4 § 3](findings/m5_20_4_method_note.md) |
| 5 | 🔶 **Candidate completion (audit-discovered, HYPOTHESIS)**: `L − 1·s2(a = 4.5) + β→0⁺·qc(a = 4.5)` is kinetically PSD-marginal at machine zero on all measured backgrounds with vanishing texture cost (s2 carries no texture charge; s2 statics on the loop +0.69). Gates pending: γ = −1 sign admissibility (author-gated), statics anchors, ghosts, band confinement (PSD holds only on the physical spectral band [0, g]) | not a working recipe yet; its gate program rides M5.20.5 arm B | [m5_20_4 § 1.3 + § 5](findings/m5_20_4_method_note.md) |
| 6 | **The runnable REGULARIZATION stack** (documented as such, NOT the theory's dynamics): canonical kinetic `(1/2)‖Ṁ‖_F²` + the η-curvature + 4-target static sector; well-posed, symplectic, E-ledgers ≤ 1e-5 over 100k steps. Everything M5.20/20.1/21 measured lives in this stack | fine for statics-adjacent dynamics questions and films; NEVER present its dynamics as the true-L evolution | [m5_20_2 § II](findings/m5_20_2_method_note.md), [m5_20 § 1](findings/m5_20_method_note.md) |

Historical precedent worth knowing: the M5.8-era stack (pre-verified-L) ALREADY hit this disease and shipped a constrained spectral-projection integrator ("every cheap positive-inertia kinetic has slow growing modes"; per-voxel 10×10 inertia operator, keep λ > 0.05·max, project the momentum every step): the same degeneracy + indefiniteness that M5.20.3 later proved structural. [archive/m5_summary_report.md § 4.2](archive/m5_summary_report.md)

## 3. The axisym instrument (the reduction of record)

| Piece | Content | Gate | Source |
| --- | --- | --- | --- |
| Equivariant ansatz | `M(ρ,φ,z) = R₁₂(φ)·M̃(ρ,z)·R₁₂(φ)ᵀ`; channels at φ = 0: `A_ρ = ∂_ρM̃`, `A_φ = [J, M̃]/ρ`, `A_z = ∂_zM̃`; 3D integral reduces EXACTLY to the (ρ,z) half-plane, weight `2πρ dρ dz` | G6: 2D ≡ 3D at h² order | [m5_17 § 4](findings/m5_17_methods_note.md) |
| Axis scheme | cell-centered ρ grid `ρ_i = (i+1/2)h` + mirror ghost `M̃(−ρ) = P·M̃(ρ)·P`, `P = diag(1,−1,−1,1)`: no one-sided bias | G6 | [m5_17 § 4](findings/m5_17_methods_note.md) |
| Standard grids | 64×128 (M5.20.3/4 production; box-independence spot-checked at 128×256) · 128×256 (M5.21 electron statics) · 48³ h = 1 (the 3D twin) | per-task h-checks | method notes |
| ⚠️ The equivariance boundary (load-bearing, audit-found) | `A_φ = [J₁₂, M]/ρ` is equivariant ONLY under the J₁₂-commutant: internal conjugation by anything else leaves the sector, so slice evaluations of conjugation-orbit quantities are the WRONG functional. The correct rigid-orbit kinetic is the φ-AVERAGE with the rotated generator `G_φ = e^(−φJ₁₂) G e^(φJ₁₂)` (`q2_avg`); T and U are constant along the true 3D orbit. Band-limit: the integrand has harmonics ≤ 4, so trapezoid nphi ≥ 5 is EXACT (gate nphi 8 == 16) | a1c re-scan | [m5_20_4 § 3.3](findings/m5_20_4_method_note.md) |
| The co-rotating vacuum texture | the equivariant vacuum carries `A_φ ≠ 0` (the biaxial frame winds azimuthally): a ZERO-energy Goldstone texture of the quartic L (u_eta = V4 = 0 exactly) with real K (Q2_J23 = 1706, the M5.20.3 chirped ladder lives on it). Any η-lifting quadratic term charges it (§ 2 row 2) | measured | [m5_20_4 § 1](findings/m5_20_4_method_note.md) |
| The 3D twin | full-3D central differences (`grad_static_3d`, complex-step gated 1.75e-15) + Verlet (dt = 0.005, boundary pinned); ⚠️ pinned 48³ reflects radiation after t ≈ 12 (clean reading t < 12); non-axisym leakage: a_break slow-growth e-fold ≈ 46 tu ⇒ axisym verdicts safe on T ≲ 50 | GD3a | [m5_21 § 4](findings/m5_21_films.md) |

## 4. Locked parameters + measured anchors

| Anchor | Value | Provenance / gate |
| --- | --- | --- |
| `c₂` (curvature coefficient) | `7.1618e-3 MeV·fm = αħc/64π` EXACT (Coulomb anchor via the analytic hedgehog `u_curv = 8c₂/r⁴`, gates G3/G4) | [m5_16 lock](findings/m5_16_report.md), [m5_17 § 6](findings/m5_17_methods_note.md) |
| Length unit | `0.2495 fm` per grid unit (at β = 1; m_e anchor) | [m5_16 lock](findings/m5_16_report.md) |
| Electron size | `r_half = 2.926 fm` (quartic-LdG, h-converged) · `2.935 fm` (spectral potential) · Faber SU(2) ref `3.075 fm` (gap −4.8%, genuine model difference); β-robust 2.916-2.939 over β ∈ (0.25, 1.5) | [m5_16 headline](findings/m5_16_report.md), [m5_18 § 7](findings/m5_18_verification_note.md) |
| LdG-era coefficients | `(a, b, c) = (−3.48e-3, 6.97e-3, 6.97e-3) MeV/fm³` at β = 1; `a = (3b − 4c)/2` (vacuum identity); `κ_δ = (3/2)b = 1.05e-2 MeV/fm³` | [m5_16 lock](findings/m5_16_report.md) |
| Working potential weight | `w = 7.24e-4` (WSCALE, the M5.12 pin; fixed across δ) | [m5_20 § 1](findings/m5_20_method_note.md) |
| δ, g | working values δ = 0.3, g = 8 (dynamics era); locked-era δ = 1e-10, g = 1e10 with `g·δ = 1` (statics measured g-blind: gate G8 exact) | [m5_16 lock](findings/m5_16_report.md), [m5_20_2](findings/m5_20_2_method_note.md) |
| The core gate (loop, statics) | `spectrum(ηM_core) = (g, 1, a, a)`, **a = 0.1269 ± 0.011 = 0.85 × δ/2** (his prediction ~δ/2); box-independent 4e-10 | [m5_20_3 § 5b](findings/m5_20_3_method_note.md) |
| The chirped vacuum ladder | **ω₁(ρ) = 0.0674ρ + 0.0000**, K10 ∝ ρ^−2.00 exactly (gen-eig(Hess_V, K10) on the co-rotating vacuum): ANY spectral comparison under the true L must use it (the flat canonical ladder is the unit-inertia assumption, superseded) | [m5_20_3 § 5c](findings/m5_20_3_method_note.md) |
| Canonical-stack gap ladders | vacuum masses at diag(1,0,0): ω = {0.05156, 0.14322} = `√(2w(8∓√38))`-family; activated rungs δ = 0.1/0.3/0.5: 0.0041/0.0099/0.0125 (Hessian), Rayleigh `√(w(4δ² + 9δ⁴))`; 4×4 g-branch map: ω = {0.0093, 0.0466, 0.1349, 78.28 (stiff g-mode)} | [m5_20 § 1](findings/m5_20_method_note.md), [m5_20_1 § 3](findings/m5_20_1_method_note.md), [m5_20_2](findings/m5_20_2_method_note.md) |
| The particle-clock breathing mode | M5.21 electron core breathing: windowed FFT peak **0.1255 ± 0.0078** vs the analytic activated rung 0.1349 (~15% below, anharmonic softening) | [m5_21 § 3](findings/m5_21_films.md) |
| Winding persistence | q = 0.500 EXACT through every true-L blowup (loop's own read, multi-radius, 2e-16); the canonical stack unwinds 10/10 with E conserved (~1e-5): unwinding needs NO radiation | [m5_20_3 § 5a](findings/m5_20_3_method_note.md), [m5_20 § 3](findings/m5_20_method_note.md) |
| From-rest inconsistency | nff = 0.9999977 (strict cutoff; 98.6% at run-cutoff); the null force is b0/time-diagonal sector (0.43 vs ≤ 2.8e-4) | [m5_20_4 § 2](findings/m5_20_4_method_note.md) |
| Closure / roots | β* = 1.3056/1.3061/1.3050 (recipe/raw/remnant; audit 1e-12); qc window a ∈ (1.25, 7.75) measured; root crossings (corrected Q2_avg): J23^K2 ≡ J13^K1 at χ = 0.75, K3/J12 families at 0.25 | [m5_20_4 § 1, § 3.3](findings/m5_20_4_method_note.md) |
| Two-charge Coulomb | large-d fixed-ansatz fit matches `q₂·64π` (ansatz level; full two-defect relaxation does not settle: § 6) | [m5_17 § 8](findings/m5_17_methods_note.md) |
| Loop statics record | corepin ring holds q = 0.5 exactly, E → 7.51; twist-escaped q = 1/2 loop interior R* = 17-18; recipe-seed E 2.68 → 0.34 at the core gate | [m5_19](findings/m5_19_method_note.md), [m5_20_3 § 5b](findings/m5_20_3_method_note.md) |

### 4b. The M5.8-era anchors (pre-M5.16 functional; the archived results-of-record)

⚠️ Era caveat: these ran on the EARLIER stack (the Eq.18 signed Hamiltonian + the saturating quartic `V_u = u + βu²`, β = 1.558 + the canonical-kinetic constrained-projection integrator; index-3-era labels relabeled per the convention note). They are the substrate/clock record that pre-dates the verified L: era-anchors, not directly comparable numbers. Full detail + reproduction commands: [`archive/m5_summary_report.md`](archive/m5_summary_report.md).

| Anchor | Value | Source (archived report) |
| --- | --- | --- |
| Topological charge | integer, additive winding: Q = ±0.996 single hedgehogs, ±1 per core of a pair, 0.000 enclosing both: quantization + additivity EMERGENT | § 1 |
| Coulomb 1/d | attraction R² = 0.9781 (matrix substrate) + 0.9959 on Duda's own page-18 geometry | § 1 |
| Maxwell, two independent routes | hydro↔EM dictionary (E = ∇·n̂, B = ∇×n̂: full Maxwell set to machine precision) AND Faber curvature (R = Γ×Γ closed 2-form, ‖R‖ ~ 1/r² with running-coupling onset at r₀) | § 1 |
| KG mass is GEOMETRIC | the explicit mass term cancels exactly under minimal coupling to the hedgehog connection (Fig. 9 reproduced) | § 1 |
| Faber mass handle | `E·r₀ = const` (CV 0.0%): r₀ = 2.2132 fm → 0.511 MeV (the calibration knob that became the M5.16 lock) | § 1 |
| The time-crystal mechanism | quadratic action runs away at FIXED PHASE (dt-invariant, grid/precision-independent); the quartic floor bounds it; the SIGNATURE is the engine (Euclidean twin decays while Minkowski grows 3×, same seed + kick); the state SELF-STARTS from P = 0 exact (T 0 → 5.76, H to 0.5%); the dressed minimum is UN-SITTABLE (K_bb = −67.6 < 0): compulsory motion | § 2 |
| The molten clock | ω is an attractor (ω₁ ≈ 1.1 + 2ω₁ harmonic, preparation-independent); RIGID across a 2.6× mass family (exponent 0.03, not 1: the frequency belongs to the core); classified molten (persistent comb on low-dimensional chaos, D₂ 2.7-3.0) regularizing toward a near-regular cold state (D₂ 1.68) | § 3 |
| The ZBW ratio + the absolute gap | ω₁/(2H_rest) = 0.0326-0.0343; under the two unit postulates the clock runs 5.5e19 rad/s ≈ 28× below the electron ZBW, STRUCTURAL (ω rigid): the gap is a calibration split (energy anchor 28× low, length anchor 36× high; jointly recoverable: the `E·r₀ = α(π/4)ħc` exact relation), not an energy-bookkeeping fix | § 3 + the [briefing](../__M5_model_briefing.md) #217/#218 rows |
| The EM/GEM split | g enters the energy ONLY through the boost tilt `b·g` (GEM exactly 0 at b = 0); `GEM ∝ (b·g)²` small-tilt; GEM is NEGATIVE (the clock reduces rest energy: ~0.5% at physical boost, ~50% at the clock dressing); EM:GEM = 210:1 physical → 2:1 at clock dressing | § 2026-06-09 addendum |
| The δ/g calibration verdicts | H_static is δ-FLAT at fixed g (∝ δ^−0.04 over δ 0.3 → 0.001); the δ knob does NOT calibrate the clock (R ≈ 0.033·δ moves AWAY from 1 as δ shrinks); the literal `g = 1/δ` hierarchy diverges (§ 6) | § DUDA follow-up |
| Electron-ID structure (EID) | μ exists ONLY via the TILT (precession) channel: the pure twist clock (Γ¹) is EM-SILENT (μ = 0 structurally); μ(tilt) = 0.221/0.248/0.277 at 24³/32³/48³ (tail-dominated, ~11%/step); orbital J = 0 structurally (the hedgehog is dyon-like, E ∥ B); spin lives in the Noether clock charge L_int = 61.6 (φ-flat 0.03%); g ≈ 2 testable only after the Coulomb `e_scale` unit fix (the box ladder [1.97, 2.22] brackets 2.0023) | § ELECTRON-ID + briefing |

## 5. Working recipes

### 5.1 Seeds

| Seed | Recipe | Source |
| --- | --- | --- |
| The loop recipe seed (4D, the owner's prescription) | 3D-minimize while the loop is intact (frozen-time-row FIRE on the spatial sector), THEN add the g time row: `m5_20_3_b_triage.relax_spatial_frozen_time` → `m5_20_3_b_seed_recipe.npz` (q = 0.500) | [m5_20_3 § 5b](findings/m5_20_3_method_note.md) |
| Biaxial escaped loop | `loop_field_biax` / `pairing_spec` (both winding pairings seeded, core equalization MEASURED not chosen); pair_d0 winds (δ,0) (the neutrino-hunt object), pair_1d winds (1,δ) | [m5_20_1 § 2](findings/m5_20_1_method_note.md) |
| Twist-escaped loop far field | far field = EXACT enumerated vacuum (e2e2ᵀ or e3e3ᵀ), two-equal core, blend beyond ~2.5 core widths (`loop_field_escaped`) | [m5_19 § 1](findings/m5_19_method_note.md) |
| Electron hedgehog | melted hedgehog `M_sp = s(r)·n nᵀ` + equivariant rotation; 3-equal core `a = (1+δ)/3` is seed-adjacent (the deep relax splits it: Q8) | [m5_17 § 6](findings/m5_17_methods_note.md), [m5_21 § 2](findings/m5_21_films.md) |
| Time-mixing texture bumps | Gaussian bump injections per sector (`inject`: rotation/clock/boost4b), the B5/a2 probe pattern | [m5_20_3](findings/m5_20_3_method_note.md) |

### 5.2 Statics relaxers

| Recipe | Settings that work | Source |
| --- | --- | --- |
| Frozen-time-row FIRE (the bounded sector) | `fire_relax` with free4 mask + `1/w` precondition, dt0 0.005, dt_max 0.05, tol 1e-9, 500-iter chunks; ring/q/core logged per chunk | [m5_20_3 § 5b](findings/m5_20_3_method_note.md) |
| ⚠️ Free-4D relaxation | FIRE adaptive dt MUST stay under the stiff-mode bound `2/√λ_max ≈ 0.0256`: use **dt_max 0.02**, or monotone GD / L-BFGS (the dt_max 0.05 dive was an integrator artifact, RETRACTED at audit) | [m5_20_3 § 8 C8](findings/m5_20_3_method_note.md) |
| Spherically-constrained radial solve | the calibration class (exact chain rule dE/ds_k): the unconstrained spherical hedgehog is a SADDLE (§ 6) | [m5_16](findings/m5_16_report.md) |
| Convergence certificate | gradient falls ~6 decades monotone; Derrick virial `E_curv = 3E_pot` to 0.3-0.6%; h-refinement last step ≤ 0.01% | [m5_16 method](findings/m5_16_report.md) |

### 5.3 Dynamics integrators

| Recipe | Settings that work | Source |
| --- | --- | --- |
| Canonical-kinetic stack (the regularization, § 2 row 6) | velocity Verlet + exact sponge ledger (quadratic ramp width 16, γmax 0.5); dt = 0.02 (dt² ratios ≈ 4.0); drift ≤ 1.3e-5 over 100k steps; fast-path gradient gated (GF 1.3e-16) | [m5_20 § 2-3](findings/m5_20_method_note.md), [m5_20_1 § 3](findings/m5_20_1_method_note.md) |
| True-L EL solve (diagnostics only) | per-cell 10×10 spectral pseudo-inverse, null projection (`accel`), leak bookkept exactly; **dt = 0.00125** (converged); rel_cut 1e-2 standard / 1e-1 longest-lived; blowup guard `max\|M\| > 1e6` + isfinite per step; velocity-in-force at the Verlet half step | [m5_20_3 § 2, § 4](findings/m5_20_3_method_note.md) |
| Full-rank (dressed) dynamics | `accel_fixed`/`evolve_fixed` with `K_tot = 4·k10 + k10_add`: E conserved 3.7e-8 over 8000 steps at β* (well-posed; a DIFFERENT theory: § 2 row 2) | [m5_20_4 § 1.3](findings/m5_20_4_method_note.md) |
| Balance-root evaluation (the BVP entry point) | `Q2_avg` via the φ-averaged generator (nphi 8, exact by band limit), `U = e_static_c`; root `ω* = √(−U/Q2_avg)` where signs oppose; H = 0 is the exactness certificate | [m5_20_4 § 3](findings/m5_20_4_method_note.md) |

### 5.4 Measurement instruments

| Instrument | Recipe | Source |
| --- | --- | --- |
| Winding q (guarded) | bilinear guarded read (`winding_measure_bilin`/`_biax`) at MULTIPLE radii around the \|M13\|² centroid; DECLINE the read when λ₁ ≈ λ₂ (branch-swap churn, the M5.21 lesson); final-state verdicts add the many-center \|M13\| scan (the audit's 1218-center pattern) | [m5_20_1 § 2](findings/m5_20_1_method_note.md), [m5_20_4 § 5](findings/m5_20_4_method_note.md) |
| Ring locator + core read | `ring_by_m13` (\|M13\|² centroid) + `core_spectrum` (which pair holds equalized) | [m5_19 § 2](findings/m5_19_method_note.md) |
| Snapshot / film | the film standard ([`m5_visualization.md`](m5_visualization.md)): basic + thermal templates, first row t = 0, steps-only titles, N_SNAP = 6 (7-row log-spaced tail for blowups); the GV0-gated renderer (`m5_21_a_snap.py`: splay 3.1e-4, rotator phase 1.1e-16) | [m5_21 § 1](findings/m5_21_films.md) |
| Clock probes | rigid-orbit `H(ω) = H(0) + ω²K_eff` (exact to 5e-14); the control-frame Ŝ = S0 − ω²Q2 probe (GE0 2e-12) | [m5_20_2](findings/m5_20_2_method_note.md), [m5_19 § 1](findings/m5_19_method_note.md) |
| Spectra | windowed FFT with bin width quoted; band language unless the peak is resolved by ≥ 3 bins (the 0.1466 "on the mass line" retraction was bin quantization); no peak within ~2 bins of DC; combs at bin multiples are automatic; vary the detrend/window length as a dial (the M5.8 "0.262 comb" catch) | [m5_20_1 § 6](findings/m5_20_1_method_note.md), [archive/m5_summary_report.md § 4.3](archive/m5_summary_report.md) |

### 5.5 Verification practices (what keeps the recipes honest)

| Practice | Content | Source |
| --- | --- | --- |
| Complex-step gates | every derived gradient/momentum/operator gated complex-step BEFORE physics (the energies are polynomial: cancellation-free at 1e-15; real central diff floors at ~5e-6 at the g⁴ trace scale) | all method notes since M5.17 |
| Polarization cross-builds | every einsum-assembled operator (K10, k10_add, k10_s2) cross-checked against a from-scratch per-cell polarization of its density | [m5_20_3 GC0d](findings/m5_20_3_method_note.md), [m5_20_4 CG5](findings/m5_20_4_method_note.md) |
| Adversarial audit | independent agent, OWN instruments, per-claim verdicts, before any claim is trusted (cardinal rule, `AI_HYGIENE.md`); the M5.20.4 audit both refuted two claims AND discovered the § 2 row 5 candidate | audit sections of every note |
| Quadratic-system solves | r = r₀ + Q(c,c) structures have zero Jacobian at the origin: multi-start mandatory; a stall at the SAME residual across starts signals a range obstruction: measure alignment before concluding impossibility (and probe STRUCTURED directions, not just random: the C6 lesson) | [m5_20_4 § 2](findings/m5_20_4_method_note.md) |
| Rigid-orbit quantities on the slice | ALWAYS φ-average the generator (§ 3 equivariance boundary) | [m5_20_4 § 3.3](findings/m5_20_4_method_note.md) |
| The dt-invariance discriminator | real dynamics reproduces at matched τ under dt-halving; stepper-driven growth shifts with dt (the test that killed "the runaway is numerical") | [archive/m5_summary_report.md § 4.3](archive/m5_summary_report.md) |
| The knob gate | verify a parameter family actually CHANGES the seed (fixed-domain invariant spread > 5%) BEFORE spending compute (caught a no-op scan) | [archive/m5_summary_report.md § 4.3](archive/m5_summary_report.md) |
| Surrogate guides, direct quadrature decides | spline/few-point surrogates carry mesh artifacts; only machine-exact direct evaluation is load-bearing | [archive/m5_summary_report.md § 4.3](archive/m5_summary_report.md) |

## 6. Anti-recipes (measured negatives: do not repeat)

| Anti-recipe | What was measured | Source |
| --- | --- | --- |
| Free-EL initial-value integration | ill-posed; every regularization blows up (§ 2 row 1) | [m5_20_3 § 4](findings/m5_20_3_method_note.md) |
| Single η-lifting kinetic terms | closure destroys the loop statics (texture charge forced) | [m5_20_4 § 1](findings/m5_20_4_method_note.md) |
| Zero-energy (null-velocity) consistent data | does not exist at the loop (directional obstruction, exact) | [m5_20_4 § 2](findings/m5_20_4_method_note.md) |
| "Protection by spectral gap / energy conservation" | the loop unwinds 10/10 in the canonical stack WITH E conserved (closed boxes): the activated barrier is only ~3% of the driving energy; unwinding needs no radiation | [m5_20 § 3](findings/m5_20_method_note.md), [m5_20_1 § 3](findings/m5_20_1_method_note.md) |
| Unconstrained kinetic twist as a ZBW clock | the seeded twist stalls (25-95% below seeded slopes) and radiates; a rotation kick does NOT stabilize the hedgehog saddle | [m5_21 § 3](findings/m5_21_films.md) |
| Unconstrained spherical hedgehog statics | a SADDLE (point-vs-ring escape): calibrate in the spherically-constrained class | [m5_16](findings/m5_16_report.md) |
| Two-defect full relaxation | does not settle (melt-channel restructuring; thin melt lines nearly free at locked coefficients): the Coulomb anchor stands at ansatz level | [m5_17 § 8](findings/m5_17_methods_note.md) |
| FIRE with dt_max 0.05 on free-4D statics | step-size instability masquerading as an energy dive (retracted at audit): cap at 0.02 | [m5_20_3 § 8 C8](findings/m5_20_3_method_note.md) |
| Winding reads on churned states | branch-swap flips (±1/0 flickers) are read artifacts, not charge changes: guard + decline | [m5_21 § 3](findings/m5_21_films.md) |
| Slice-evaluated conjugation orbits | the wrong functional outside the J₁₂-commutant (φ-average instead) | [m5_20_4 § 3.3](findings/m5_20_4_method_note.md) |
| exp of SUMMED Lorentz generators as an orbit witness | negative only near the origin (the M5.18 § 6 retraction): use product textures / shared-axis constructions | [m5_18 § 10](findings/m5_18_verification_note.md) |
| FFT peak == theory line at bin resolution | the 0.1466 "on the top mass line to 0.2%" claim was bin quantization (deleted); quote bin widths | [m5_20_1 § 6](findings/m5_20_1_method_note.md) |
| The literal `g = 1/δ` hierarchy in simulation | H_static diverges ∝ δ^−6.8 (9e16 at δ = 0.001): the physical scale is numerically impossible; decouple gravity instead (matches the author's own "neglect gravity" guidance) | [archive/m5_summary_report.md](archive/m5_summary_report.md) |
| Raising g at fixed boost as a "gravity" probe | inflates the tilt `b·g` unphysically (the ∝ g⁸ read was retracted): gravity enters ONLY through `b·g` (author-corrected 2026-06-09) | [archive/m5_summary_report.md](archive/m5_summary_report.md) |

## 7. Sync map

| Doc | Relationship to this canonical |
| --- | --- |
| [`__M5_model_briefing.md`](../__M5_model_briefing.md) | the outward-facing model card (audience: contributors); this doc is its technical backbone: when a § 1-§ 4 row changes, check the briefing's profile/status tables |
| [`findings/*_method_note.md`](findings/) | the provenance layer: every row here links its note; notes are frozen task records, this doc is the living consolidation |
| [`m5_roadmap.md`](m5_roadmap.md) | tasks produce/consume the rows here; the Done column narrates what each task added |
| [`m5_question_tracker.md`](m5_question_tracker.md) | author-gated unknowns behind rows marked 🔶 (currently: Q24 formulation confirmation + the γ = −1 sign; the tu → s calibration) |
| [`m5_visualization.md`](m5_visualization.md) | the film/snapshot standard referenced by § 5.4 |
| [`archive/m5_summary_report.md`](archive/m5_summary_report.md) | the M5.8-era results-of-record (archived 2026-07-14; § 4b's provenance + the pre-M5.16 reproduction command table) |
