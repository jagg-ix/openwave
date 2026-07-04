# HydroBoros (M7): the canonical numerical specification

> The results-of-record spec for the M7 electron, consolidated at the **M7.7 milestone** (2026-07-03) from tasks M7.1-M7.6. Shaped per [`dev_docs/METHOD_NOTE.md`](../../../../dev_docs/METHOD_NOTE.md): **equations first**, an equation-to-code map, results after methods, and an explicit not-computed list. The runnable reproduction is ONE script: [`scripts/m7_7_canonical.py`](scripts/m7_7_canonical.py); the physics lives in ONE small module: [`scripts/m7_functional.py`](scripts/m7_functional.py) (~200 lines, docstring = these equations).

## 1. The theory (all conventions pinned, with provenance)

The Lagrangian (Werbos's Ouroboros doublet; Minkowski `(−,+,+,+)`, natural units `c = m_J = 1`, canonical `g = λ = ω = 1`):

```text
L = −¼ F_μν F^μν − ¼ G_μν G^μν + m_J² A·J − f(J·J),    f(s) = c1 s + c2 s²
F = dA (massless A sector),  G = dJ (the J "current-field" sector)
```

| Convention | Value | Provenance |
| --- | --- | --- |
| quartic branch | **written/repulsive: `c1 = +λ/2, c2 = +g/4`** (LoE v5's own `f = gs²`, λ separate) | decided EMPIRICALLY at M7.4: the only branch with stable 3D solitons; the M6 benchmark's focusing signs expel charge or collapse ([`tasks/m7_4_charged_soliton.md § 2b`](tasks/m7_4_charged_soliton.md)) |
| coupling sign | `κ = −1` (a pure `J → −J` relabeling) | the M7.3 verbatim-ODE pre-gate ([`tasks/m7_3_ouroboros_3d.md § 1`](tasks/m7_3_ouroboros_3d.md)) |
| sector | pure-vector (`A₀ = J₀ = 0` frozen) | the M7.4 scalar-sector instability finding; the Gauss/charge extension uses a fixed-`j₀` reservoir (§ 5) |

**The time-harmonic frame** (the de Broglie clock is IN the state):

```text
A(x,t) = a_c(x) cos ωt + a_s(x) sin ωt ,   J(x,t) = j_c(x) cos ωt + j_s(x) sin ωt

E_ω = ∫ d³x [ quad − κ⟨A·J⟩ + f_avg ]           (the PERIOD-AVERAGED ENERGY;
                                                 identity exact to 1.85e-14, M7.5)
quad  = ¼( |E_Ac|² + |E_As|² + |E_Jc|² + |E_Js|² + |B_Ac|² + ... + |B_Js|² )
        E_Ac = −ω a_s , E_As = +ω a_c  (temporal gauge);  B = ∇×(·)
⟨A·J⟩ = ½( a_c·j_c + a_s·j_s )
f_avg = c1 s0 + c2 ( s0² + (s1² + s2²)/2 )       (EXACT quartic average)
        s0 = (|j_c|²+|j_s|²)/2 , s1 = (|j_c|²−|j_s|²)/2 , s2 = j_c·j_s
```

**The constrained objective** (the M7.5 real-time-orbit frame): minimize `E_ω` at fixed

```text
Q_can = (ω/2) ∫ ( |a_c|² + |a_s|² + |j_c|² + |j_s|² )      (the clock's conjugate)
H_A   = ½ ∫ ( a_c·∇×a_c + a_s·∇×a_s )                      (the localization guard)
```

Why these two, measured: the fixed-`Q_can` extremal is the real-time orbit (`ω` is the multiplier; the fixed-`H_A`-only state misses the orbit by exactly `−2ω²`, measured −1.978, M7.5 § 4); the `ω`-`Q_can` conjugacy is verified in 3D (`dE*/dω = Q_can` to ~1-2%, M7.5 § 3); helicity is load-bearing (zero-`H_A` states evaporate at fixed `H_A` [M7.4] and delocalize to the band-edge condensate at fixed `Q_can` [M7.6]).

**Discretization:** uniform cubic lattice, `h = L/N`, central differences (curl self-adjoint), vacuum Dirichlet shell (3 cells), volume element `h³`; FIRE minimizer with Gram-Schmidt tangent projection on both constraint gradients and exact interleaved rescale restores; Taichi f64 engine cross-validated against the numpy reference module on the final state (gate ≤ 1e-10).

## 2. Equation-to-code map

| Term / observable | Function | Where |
| --- | --- | --- |
| `E_ω` density (quad, coupling, `f_avg`) | `energy_density` | [`m7_functional.py`](scripts/m7_functional.py) (reference) ↔ `TaichiBlend.e_kernel` in [`m7_4_linked_vortex.py`](scripts/m7_4_linked_vortex.py) (engine) |
| `Q_can` + `H_A` | `q_can`, `helicity_A` | [`m7_functional.py`](scripts/m7_functional.py) |
| the two-constraint relaxation | `relax_qcan` | [`m7_6_observables.py`](scripts/m7_6_observables.py) |
| momentum / spin / `j_z` per quantum | `momentum_avg`, `spin_Lz`, `jz_per_quantum` | [`m7_functional.py`](scripts/m7_functional.py) |
| RMS charge / Gauss | `charge_rms` | [`m7_functional.py`](scripts/m7_functional.py) |
| the canonical run + gate table | `main` | [`m7_7_canonical.py`](scripts/m7_7_canonical.py) |

(Commit-pinned GitHub permalinks are added when the milestone commit lands; the map above is repo-relative and stable.)

## 3. The canonical electron (results of record, N = 64, L = 16)

The state: the **rotating blend** (m = 1 azimuthal pair of the M6-torus + poloidal-twist profile), relaxed at fixed `Q_can = 13.2017` + fixed `H_A = −7.890`:

| Observable | Value | Gate / caveat |
| --- | --- | --- |
| `E_ω` | **6.3246** program units | grid-convergent family (0.15% N 64→96 at M7.4); absolute anchor = the § 4 units contract |
| `‖∇E‖` (projected) | 1.6e-7 | converged |
| spin quantum `⟨j_z⟩` | **0.9939 (A), 0.9934 (J)** | a clean `j_z = 1` rotating wave (0.6%); Poynting `L_z = 13.10` with the energy budget closing exactly (M7.6 § 3) |
| RMS charge `Q_ρ(<0.3L)` | 0.026 | localized, persistent |
| Coulomb (fixed-reservoir) | Gauss flux = **99.1%** of source; far field **−2.14** (vs −2); two-charge `1/d` reference-matched, dressing **1.17 ± 0.02** | the monopole is externally sourced (§ 5 limit) |
| KG sector | both fluctuation branches exact KG; `m_eff² = (1+√5)/2` | dispersion anchored by the measured tachyon rate (0.785 vs 0.786, M7.5) |
| existence threshold | solitons only for **`ω > ω* = 0.786`** | measured (bracketed 0.75-0.79); the clock IS the stabilizer |

## 4. The units contract (decision table, open)

Measured dimensionless inputs: `⟨j_z⟩ = 1` per quantum; `ωL_z/E_ω = 2.07`; `E_ω = 6.3246 p.u.` The physical mapping needs ONE choice:

| Choice | Mapping | Consequence |
| --- | --- | --- |
| `ω = ω_Compton = m_ec²/ℏ` | `E_ω = m_ec²` sets the unit | `L_z ≈ 2.07 ℏ` (total field angular momentum ~ 2ℏ; the per-quantum `j_z = 1` reads as ℏ) |
| `ω = ω_Dirac = 2m_ec²/ℏ` (Zitter) | same energy anchor | `L_z ≈ 1.03 ℏ`; the per-quantum `j_z = 1` reads as **ℏ/2-per-2ω-cycle** (the Zitter reading: bilinears at 2ω) |

Recommendation on record: the Dirac/Zitter mapping (bilinears oscillate at 2ω, matching the M5.8 clock structure and Fleury's `ω/ω_D` targets), which lands the total `L_z` at ℏ within 3%; the spin-½ STATISTICS question (double cover) is untouched either way (🚧 in the column). Decision = the model owner's/lead's call, recorded here when made.

## 5. Known limits (the not-computed list, explicit)

| Limit | Status |
| --- | --- |
| the real-time vacuum is tachyonic (`det M(0) = −1`, band `k² < 0.618`; NO `β*` threshold) | measured + analytic (M7.5); **Q14**, the top theory question to Werbos; harmonic states above ω\* are immune; blocks M7.11-style real-time runs |
| the self-consistent charge (dynamic `j₀`) | not computed; the fixed-reservoir prescription is the validated stand-in (M7.6); Q7(b)/Q14 |
| absolute `μ` / `μ_B(1+α/2π)` | charge-unit-blocked (needs the monopole unit); de-phased `μ_J = 36.5 p.u.` on record |
| the M6 charged ledger `H/Q = 1.6890` | reproduced in 3D to 4.7e-5 but **window-defined** (no decaying channel at the canonical point; Q11): not used as a mass anchor |
| spin-½ statistics (720°), knot-sector persistence, masses beyond the electron | 🚧 Phase 2 + 4 tasks (topology-preserving constraints needed for knot sectors, M7.4 § 4) |

---

Cross-refs: milestone task [`tasks/m7_7_consolidation.md`](tasks/m7_7_consolidation.md) · the six source task docs [`m7_1`](tasks/m7_1_infra.md)·[`m7_2`](tasks/m7_2_fleury_torus.md)·[`m7_3`](tasks/m7_3_ouroboros_3d.md)·[`m7_4`](tasks/m7_4_charged_soliton.md)·[`m7_5`](tasks/m7_5_clock_stability.md)·[`m7_6`](tasks/m7_6_observables.md) · open questions [`m7_question_tracker.md`](m7_question_tracker.md) · the coverage matrix [`MODELS.md`](../../../../MODELS.md) · background [`m7_background.md`](m7_background.md).
