# M5.16 run checkpoints (in-flight state)

> Task: [`../tasks/m5_16_task_details.md`](../tasks/m5_16_task_details.md) · go 2026-07-02 15:07 EDT · resume ping armed (fires 18:35 EDT if a cap hits). Each completed sub-result lands here on arrival; a resuming agent re-reads this file and relaunches only dead work.

## Plan of record (set 15:20 EDT)

| # | Sub-result | Script | Status |
| --- | --- | --- | --- |
| 1 | Axisym instrument + gates (gradcheck, analytic shell, 3D-equivalence, sphericity, virial) | `m5_16_axisym.py` | 🚧 building |
| 2 | Calibration lock: c2 from Coulomb tail, (a,b,c) from m_e + β-sweep, r₀ prediction vs Faber | `m5_16_calibrate.py` | pending |
| 3 | P-G δ-continuation (chiral response as δ walks 0.3 → quasi-uniaxial) | `m5_16_delta_continuation.py` | pending |
| 4 | FINISH: findings into task_details + TASK REVIEW + parameter handoff | task_details | pending |

## Design decisions (derived 15:07-15:20, before any code)

| Decision | Content |
| --- | --- |
| Equivariant reduction (P-B) | `M(ρ,φ,z) = R₁₂(φ) M̃(ρ,z) R₁₂(φ)ᵀ`; at φ=0: `M_x = ∂_ρM̃`, `M_y = (1/ρ)[J,M̃]`, `M_z = ∂_zM̃`, J = (1,2)-plane generator. Volume weight 2πρ. Cell-centered ρ (ρ_i = (i+½)dρ) regularizes the axis; on-axis regularity ([J,M̃]→0) is enforced energetically by the 1/ρ² weight |
| Analytic hedgehog density | For M = r̂⊗r̂ (s=1): only [∂ₓM,∂ᵧM] ≠ 0 at r̂=ẑ, norm²=2, density = c2·4·2/r⁴ = 8c2/r⁴; shell energy 32πc2(1/r_min − 1/r_max) = closed-form gate |
| LdG structure (P-C) | V = a·Tr2 − b·Tr3 + c·Tr2² on the spatial block. Vacuum spectrum (1,δ,0) with δ→0: stationarity at s=1 ⇒ a = (3b−4c)/2; ordered-below-isotropic ⇒ c > b/2; b > 0 REQUIRED for shape selection (b=0 leaves the degenerate Tr2-valley, no spectrum pinning). Free ratio β = b/c ∈ (0,2). δ-axis stiffness κ_δ = (3/2)b exactly (the cubic alone restores the δ eigenvalue); O(δ) residual force on the vacuum = 3bδ (honest residual, V cannot be exactly stationary at biaxial (1,δ,0) with b≠0) |
| Coulomb anchor (P-C/P-E) | Far-field s→1 hedgehog tail density 8c2/r⁴ ≡ classical EM self-energy density (E_out = αħc/2r) ⇒ c2 = αħc/(64π) ≈ 7.1618e-3 MeV·fm, ANALYTIC. Verify C_M5 = 8 numerically |
| Mass + size lock | Per β: relax at χ=1 (grid unit ℓ absorbs c_pot = c2/ℓ⁴), read Î(β) = E·ℓ/c2 and r̂*(β); then E = m_e fixes ℓ ⇒ r₀_phys(β) = c2·Î·r̂*/m_e PREDICTED vs Faber 2.2132 fm; (a,b,c) in MeV/fm³ follow. Derrick: E(λ) = A/λ + Bλ³ ⇒ stable finite size; virial gate E_curv = 3·E_pot |
| g/δ (P-E) | Static electron sector is g-decoupled (measured gate); g comes from the clock/boost anchor: report constraint chain (g·δ=1 hierarchy + QM ∝ δ², GEM ∝ (b·g)² scaling laws from the EID record) + graded-δ E(δ) = E₀ + δE₁ + δ²E₂ on the calibrated solution. No new dynamics run (that is #220) |
| Physical regime arithmetic (P-A) | g frozen background (decoupled in statics); δ via the validated N1 graded expansion, never summed against the g-scale |

## Completed sub-results

> Times: go 15:07 EDT, all compute done 16:19 EDT (1h12m wall); rows are in execution order.

| Seq | Result |
| --- | --- |
| 1 | Scripts written: `m5_16_axisym.py` (instrument + 8 gates), `m5_16_calibrate.py` (anchor-chain driver), `m5_16_delta_continuation.py` (P-G) |
| 2 | ✅ **Gate G6 PASSED standalone** (the load-bearing one): 2D equivariant reduction == 3D energy of the reconstructed field on the same cylinder mask; rel diff 1.06% at h=1 → 0.27% at h=0.5, shrink factor 3.90 ≈ h² as predicted. The (1/ρ)[J,M̃] azimuthal channel + mirror-ghost axis treatment are CORRECT |
| 3 | ⚠️ full-gates run slow: Taichi JIT compile of the axisym AD kernel suspected (>12 min at 99% CPU); compile-time probe running; numpy-side physics is already validated independently of Taichi |
| 4 | Engine decision: wrote the ANALYTIC numpy gradient (hand-derived adjoints: `∇_A\|\|[A,B]\|\|² = 2[C,B]`, azimuthal adjoint `−[J,G]/ρ`, ghost fold-back through mirror signs); gradcheck 2.8e-7 vs FD; 2.3 ms/eval. numpy = production engine, Taichi AD = opt-in cross-check (`--ti 1`), so the JIT stall can never block the calibration |
| 5 | ✅ **ALL 7 GATES PASS** (`data/m5_16_axisym_gates.json`): G2 gradcheck 3.6e-7; G3 hedgehog density r⁴·d = 7.987 vs 8 analytic; G4 shell 0.73% vs closed form; G5 == P0 lineage rel 0.0 (after matching P0's boundary-face counting on the interior region); G6 2D==3D shrink 3.9; G7 frame invariance 6e-16; G8 g-decoupling EXACT at g=1e10 (the physical-regime g is structurally inert in statics) |
| 6 | ⚠️ **FINDING (Q8-relevant): the unconstrained 2D relax ESCAPES the spherical hedgehog.** Smoke run (48x96, β=1): melt core collapses toward lattice scale while the winding spreads box-scale, E → 8.5 ≪ the spherical value; the M5 quartic functional (no Frank quadratic term) prefers a non-spherical texture in the axisym class (LdG point-vs-ring escape, textbook analog). The calibration therefore runs in the SPHERICALLY-CONSTRAINED class (Duda/Faber's hedgehog ansatz proper), escape reported honestly; `stability` mode added as the explicit probe |
| 7 | ✅ **Radial (spherically-constrained) solver CONVERGES**: exact chain rule through the 2D discrete functional; mass-preconditioned FIRE + CG polish. Smoke (48x96, β=1): E = 21.74, **virial = 1.012** (Derrick balance, gate R4 ✅), 6.3 gradient decades, monotone, chain gradcheck 9.7e-7. `data/m5_16_axisym_rsmoke.json` |
| 8 | Taichi verdict recorded: the axisym AD kernel JIT never completed (28 min CPU, killed twice); numpy analytic-gradient engine (FD-gated) is the production path, Taichi stays opt-in (`--ti 1`). β sweep (0.25/0.5/1.0/1.5 at 96x192, radial mode, parallel) RUNNING; P-G δ-continuation (32³, P2-shaped kernel) RUNNING |
| 9 | ✅ **P-G COMPLETE** (106 s, `data/m5_16_delta_continuation.json` + plot): δ ∈ {0.3, 0.2, 0.1, 0.05, 0.02}, M5.11 run-3/run-2 settings held fixed. No blue-phase melt network at any δ (melt_frac = 0). Every obstruction indicator relaxes MONOTONICALLY toward uniaxial: helix deformation dMsp 1.26→1.03 (L=1.7), 1.39→1.17 (L=5.0); ampdev 0.85→0.81 (L=5); knot-excess retention 154%→104% (seeded texture stops being distorted). 🔶 Directionally supportive of the 2026-07-02 unlock hypothesis, NOT sufficient alone: localization stays ~1.5 (no stable localized knot at any δ with the sandbox potential), so M5.12 phases A-C (calibrated V + uniaxial-native construction) remain necessary |
| 10 | `grade` mode added (P-A): E(δ) is an exact quartic in δ → Vandermonde fit at O(1) nodes gives E₀..E₄ cancellation-free → E(δ_phys=1e-10) to machine precision; runs on each sweep profile after the sweep |
| 11 | Faber cross-model reference computed + verified: the arctan-profile integrand integrates to π/4 (1e-11); energy-median radius u_half = 1.3894 → **r_half_Faber = 3.0749 fm** (the β-crossing target) |

## Headline results (final, 16:19 EDT)

| # | Result | Where |
| --- | --- | --- |
| 1 | ✅ **β sweep COMPLETE** (338 s wall, 4 parallel radial solves at 96x192): virial = 1.006 at every β, 6 decades, monotone, chain gradcheck ≤ 4e-6 | `data/m5_16_axisym_b{025,050,100,150}_n96.json` |
| 2 | ✅ **THE PREDICTION: r_half(M5) = 2.916-2.939 fm vs Faber 3.0749 fm, parameter-free agreement within ~5%** across the ENTIRE admissible β family (Coulomb → c2 analytic, m_e → scale; nothing left to tune). The two models (M5 quartic tensor commutator vs Faber SU(2)) independently land on the same electron size | `data/m5_16_parameter_lock.json` + `plots/m5_16_calibration.png` |
| 3 | β NOT pinnable by r_half (curve flat: 2.92→2.94 across β 0.25→1.5, no Faber crossing): stays the honest 1-dof residual, physical meaning = δ-sector stiffness κ_δ = (3/2)b_phys; the neutrino sector (M5.12 phase E) is its natural anchor | lock JSON § delta_sector |
| 4 | Locked numbers at the canonical β=1.0 row: ℓ = 0.2495 fm/grid-unit, (a,b,c)_phys = see lock JSON rows; c2 = 7.1618e-3 MeV·fm exact | lock JSON |
| 5 | ✅ **δ-grading (P-A)**: E(δ) quartic fit exact; E₁ = −24.82 (φ̂ texture) / −24.89 (θ̂), E₂ ≈ −22.3 → at δ_phys = 1e-10 the δ-sector shifts the electron energy by **fractional −1.5e-10** (Duda's "QM tiny" quantified); texture split 0.27% at O(δ), θ̂ preferred | `data/m5_16_grade_b100_n96.json` |
| 6 | 🚧 in flight: h-convergence n128 + the hedgehog stability probe. n64 vs n96 already read: J_half 206.06 → 208.71, r_half_phys 2.888 → 2.925 fm, INCREASING toward Faber under refinement; naive (1/core)² Richardson points at ≈ 2.96 fm continuum (≈ −3.8% residual model gap), n128 will confirm | tags `b100_n64` ✅, `b100_n128` 🚧, stability 🚧 |
| 7 | Tracker Q7/Q8 rows updated with the delivered refinements (κ_δ equation, 3bδ residual, point-vs-ring); legacy em dashes in the touched rows converted; added-lines dash count 0 | `../m5_question_tracker.md` |
| 8 | FINDINGS section written into the task_details (convergence + stability cells marked 🚧, patched when the runs land) | `../tasks/m5_16_task_details.md § FINDINGS` |
| 9 | ✅ **Stability probe MEASURED**: perturbed 2D relax from the converged radial solution descends 35% below the spherical minimum (25.14 → 16.23), melt moves off-origin to (ρ,z) ≈ (1.5, 2.5): the spherical hedgehog at β=1 is a SADDLE of the unconstrained axisym functional (the Q8 ask-round question is now concrete: what holds the symmetric hedgehog: Frank term? sixth-order LdG? clock dressing?) | `data/m5_16_axisym_b100_n64_stability.json` |
| 10 | ✅ **n128 convergence run DONE + lock rerun**: J_half = 206.06 / 208.71 / 208.74 at core = 5.3 / 8 / 10.7 cells (0.01% move at the last refinement: CONVERGED); virial 1.016 → 1.006 → 1.003; continuum `r_half = 2.926 fm` → the −4.8% gap vs Faber is GENUINE model difference, not discretization | `data/m5_16_axisym_b100_n128.json`, lock JSON + plot refreshed |
| 11 | ✅ ALL COMPUTE COMPLETE. FINISH executed: findings finalized in the task_details, terminal TASK REVIEW presented, completion ping sent, resume routine parked | task_details § FINDINGS |

## P-E constraint chain (assembled from the record, goes into the lock)

| Parameter | Status | Basis |
| --- | --- | --- |
| `c2 = αħc/64π = 7.1618e-3 MeV·fm` | ✅ analytic | far-field hedgehog density `8c2/r⁴` == classical EM self-energy tail `αħc/2r` (gate G3 verifies the 8) |
| `(a, b, c)` | ✅ from anchors | `a = (3b−4c)/2` (vacuum stationarity + zero forcing), scale from the m_e anchor per β, β from the Faber r_half crossing |
| `κ_δ = (3/2)b` | ✅ derived equation | the cubic term ALONE restores the δ eigenvalue (the M5.12 phase-E δ-sector anchor) |
| δ vacuum residual | honest remainder | quartic trace-LdG cannot be exactly stationary at biaxial `(1,δ,0)`: residual force `3bδ ≈ 3e-10·b` at δ_phys (Q7 refinement for Duda) |
| `g` | 🔶 hypothesis | statics exactly g-decoupled (G8: rel 0.0 at g=1e10) → the m_e/Coulomb anchors carry NO g information, STRUCTURALLY. g must come from the clock/boost sector: GEM ∝ (b_boost·g)² (m5_4c § 5), electron-clock absolute ω (#220), or baryon gravitational mass (Duda 4e). Working value g ~ 1/δ ~ 1e10 (g·δ = 1, Duda hierarchy) |
| `δ` | 🔶 hypothesis | δ_phys ~ 1e-10 (Duda, QED Dirac-kinetic coefficient); handled EXACTLY in arithmetic via the quartic grading (no f64 loss); a sharp anchor would come from the neutrino sector via κ_δ (M5.12 phase E) |
