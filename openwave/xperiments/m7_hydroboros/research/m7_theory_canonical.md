# HydroBoros (M7): the canonical numerical specification

> The results-of-record spec for the M7 electron, consolidated at the **M7.7 milestone** (2026-07-03) from tasks M7.1-M7.6. Shaped per [`dev_docs/METHOD_NOTE.md`](../../../../dev_docs/METHOD_NOTE.md): **equations first**, an equation-to-code map, results after methods, and an explicit not-computed list. The runnable reproduction is ONE script: [`scripts/m7_7_canonical.py`](scripts/m7_7_canonical.py); the physics lives in ONE small module: [`scripts/m7_functional.py`](scripts/m7_functional.py) (~200 lines, docstring = these equations).
>
> ⚠️ **Scheduled refreshes (2026-07-06):** **#1 applied at M7.8 (2026-07-07)**: the search recipe (§ 1b), the real-time integrator (§ 1c), the M7.8 map rows (§ 2), the helicity-pair measurement (§ 3b/§ 4). **#2 rides M7.21** (publication-grade, alongside the MODELS.md column entry). The [Phase 1 walkthrough](tasks/m7_phase1_walkthrough.md) is the companion for under-the-hood reading.

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

**Discretization:** uniform cubic lattice, `h = L/N`, central differences (curl self-adjoint), vacuum Dirichlet shell (3 cells), volume element `h³`; FIRE minimizer with Gram-Schmidt tangent projection on both constraint gradients and exact interleaved rescale restores (through-zero-safe helicity variant since M7.8: Newton step along `dH` when `sign(H) ≠ sign(H₀)`); Taichi f64 engine cross-validated against the numpy reference module on the final state (gate ≤ 1e-10).

### 1b. The search recipe (ansatz → relax → gates), self-contained

| Step | Content |
| --- | --- |
| Seed (the ansatz) | an explicit doublet built from the parents' geometry; the electron of record uses the **rotating blend**: the M6 torus profile + a poloidal A-twist (nonzero `H_A`), rotated to `m = 1` (`a_c ∝ cos φ, a_s ∝ sin φ`); construction [`m7_4_linked_vortex.py:278-322`](scripts/m7_4_linked_vortex.py) + the m1 rotation [`m7_6_observables.py:181-192`](scripts/m7_6_observables.py). The M7.8 helicity pair adds the CK/LG two-mode ansatz from the closure notes ([`m7_8_helicity_pair.py`](scripts/m7_8_helicity_pair.py) `_one_mode`/`build_pair_seed`; conventions and repairs in [`tasks/m7_8_helicity_pair.md § 4a`](tasks/m7_8_helicity_pair.md)) |
| Relax | FIRE descent of `E_ω` at fixed `(Q_can, H_A)`: gradient from Taichi reverse-mode AD, both constraint gradients Gram-Schmidt-projected out of the descent direction, constraints restored exactly (rescales / Newton) every step; [`m7_6_observables.py:90-173`](scripts/m7_6_observables.py) `relax_qcan` (through-zero-safe variant: `m7_8_helicity_pair.py` `relax_qcan_safe`) |
| Converge | `‖∇E‖ → ~1e-7`, constraints held to 5+ digits, `maxf` bounded |
| Gate | dilation probe (interior `E(scale)` minimum), grid ladder 48³ → 64³ → 96³ (0.15%), the observables battery, real-time frame identity (§ 1c) |

### 1c. The real-time integrator (the validation frame)

Temporal gauge, pure-vector sector; the evolution equations the leapfrog steps:

```text
d²A/dt² = −∇×∇×A − J
d²J/dt² = −∇×∇×J − A − 2(c1 + 2c2|J|²) J
```

Velocity-Verlet (kick-drift-kick), `dt = 0.2h`, Dirichlet shell, optional absorbing sponge; drift measured `O(dt²)` (0.59 → 0.148 at half dt). Initial data from the relaxed doublet: `A(0) = a_c, Ȧ(0) = ω a_s` (same for J). The frame identity `⟨E_real⟩ = E_ω` holds to 1.85e-14 (M7.5), which is what licenses the harmonic search. Engine: [`m7_5_clock_stability.py:89-233`](scripts/m7_5_clock_stability.py) (forces at `:134-146`).

## 2. Equation-to-code map

Every term findable in one click; permalinks are pinned to the Phase 1 merge commit [`bc51a09`](https://github.com/openwave-labs/openwave/commit/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7) so line anchors never drift (repo-relative links alongside, for in-repo reading).

| Term / observable | Function | Permalink (commit-pinned) | In-repo |
| --- | --- | --- | --- |
| `E_ω` density (quad, coupling, `f_avg`), term by term | `energy_density` | [m7_functional.py#L98-L127](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_functional.py#L98-L127) | [`m7_functional.py`](scripts/m7_functional.py) |
| `E_ω` integral | `energy` | [m7_functional.py#L130-L131](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_functional.py#L130-L131) | same |
| the Taichi engine's identical kernel (cross-validated to 1.4e-14) | `TaichiBlend._build.e_kernel` | [m7_4_linked_vortex.py#L127-L152](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_4_linked_vortex.py#L127-L152) | [`m7_4_linked_vortex.py`](scripts/m7_4_linked_vortex.py) |
| `Q_can` (the clock's conjugate) | `q_can` | [m7_functional.py#L137-L139](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_functional.py#L137-L139) | [`m7_functional.py`](scripts/m7_functional.py) |
| `H_A` (helicity, the localization guard) | `helicity_A` | [m7_functional.py#L142-L144](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_functional.py#L142-L144) | same |
| the two-constraint relaxation (tangent projection + exact restores) | `relax_qcan` | [m7_6_observables.py#L90-L173](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_6_observables.py#L90-L173) | [`m7_6_observables.py`](scripts/m7_6_observables.py) |
| momentum `⟨E×B⟩` + spin `L_z` | `momentum_avg`, `spin_Lz` | [m7_functional.py#L150-L161](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_functional.py#L150-L161) | [`m7_functional.py`](scripts/m7_functional.py) |
| `j_z` per quantum (orbital + spin, circular components) | `jz_per_quantum` | [m7_functional.py#L164-L179](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_functional.py#L164-L179) | same |
| RMS charge / Gauss reading | `charge_rms` | [m7_functional.py#L182-L192](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_functional.py#L182-L192) | same |
| the canonical run + gate table (the driver; no physics of its own) | `main` | [m7_7_canonical.py#L55-L121](https://github.com/openwave-labs/openwave/blob/bc51a0985b9ca4ae9e6b4c91017d1f9946e947e7/openwave/xperiments/m7_hydroboros/research/scripts/m7_7_canonical.py#L55-L121) | [`m7_7_canonical.py`](scripts/m7_7_canonical.py) |
| per-helicity energies `U±` + longitudinal/charge bucket (Waleffe split, discrete-curl-exact; Parseval gate 1.5e-16) | `helical_split` | [m7_8_helicity_pair.py](https://github.com/openwave-labs/openwave/blob/main/openwave/xperiments/m7_hydroboros/research/scripts/m7_8_helicity_pair.py) (blob/main until the M7.8 merge pins it) | [`m7_8_helicity_pair.py`](scripts/m7_8_helicity_pair.py) |
| through-zero-safe constrained relaxation (M7.8 tooling fix) | `relax_qcan_safe` | same file | same |

**How charge is computed** (the audit question, answered in one place): the instantaneous charge density is `ρ = ∇·E_A` read directly off the doublet (`E_Ac = −ω a_s`, `E_As = +ω a_c`; with scalars, the `−∇a₀` terms add); the **RMS/Fleury charge** integrates `√((ρ_c² + ρ_s²)/2)` inside a stated window (`charge_rms`, map row above); the **net Gauss monopole** is the boundary flux `∮E_A·dS`, nonzero only with the fixed-`j₀` reservoir (§ 5 limit; M7.6 measured 99.1% flux closure). The M7.8 longitudinal bucket `U_long` is the k-space face of the same content: the curl-free part of the doublet, exactly where `∇·A ≠ 0` lives.

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

### 3b. The M7.8 helicity-pair measurement (2026-07-07, N = 64)

The closure-notes two-mode ansatz (CK/LG helicity pair), five seeded asymmetries bracketing √3, each relaxed at fixed `(Q_can, H_A)`:

| Measured | Value |
| --- | --- |
| stationarity of the `U₊/U₋ = 3` pair | **not stationary at any rung**: the minus mode is expelled (relaxed `U₊/U₋` 104 → 1077, asym 0.981 → 0.998); adversarially audited (minus re-insertion at fixed constraints gives `dE ∝ +ε²`) |
| the basin | the § 3 electron family: `E/\|H_A\|` → 0.808 (family law 0.802), `j_z` → 0.99 per quantum |
| the pair-asymmetry spin `(U₊ − U₋)/(U₊ + U₋)` | **≈ 1 (one quantum), not 1/2** |
| honest boundary | this frame only (fixed NET `Q_can` + `H_A`, pure-vector); separately-constrained helicities / scalar sector / resonant states not excluded |

Run record + gates: [`tasks/m7_8_helicity_pair.md § FINDINGS`](tasks/m7_8_helicity_pair.md).

## 4. The units contract (resolved as a directive 2026-07-06; both readings versioned pending the M7.8 measurement)

Measured dimensionless inputs: `⟨j_z⟩ = 1` per quantum; `ωL_z/E_ω = 2.07`; `E_ω = 6.3246 p.u.` The physical mapping needs ONE choice:

| Choice | Mapping | Consequence |
| --- | --- | --- |
| `ω = ω_Compton = m_ec²/ℏ` | `E_ω = m_ec²` sets the unit | `L_z ≈ 2.07 ℏ` (total field angular momentum ~ 2ℏ; the per-quantum `j_z = 1` reads as ℏ) |
| `ω = ω_Dirac = 2m_ec²/ℏ` (Zitter) | same energy anchor | `L_z ≈ 1.03 ℏ`; the per-quantum `j_z = 1` reads as **ℏ/2-per-2ω-cycle** (the Zitter reading: bilinears at 2ω) |

Recommendation on record was the Dirac/Zitter mapping (bilinears oscillate at 2ω, matching the M5.8 clock structure and Fleury's `ω/ω_D` targets), which lands the total `L_z` at ℏ within 3%; the spin-½ STATISTICS question (double cover) is untouched either way (🚧 in the column). **Decision (2026-07-06, author directive at the Phase-1-review call, [tracker Q15](m7_question_tracker.md#q15-detail)):** no mapping is pinned; the frequency is treated as **emergent** and the target is the **observable `S_z = ℏ/2`**, read from the helicity-pair asymmetry `(U₊ − U₋)/ω`, which [M7.8](tasks/m7_8_helicity_pair.md) measures. **Measurement (2026-07-07, § 3b):** the pair asymmetry reads **≈ 1 quantum, not ½**, at every stable state of this frame (the two-mode mechanism is expelled by relaxation). Consequence for this table: the ℏ/2 target is NOT met via pair asymmetry; it survives via the **frequency mapping** (the `ω_D` / Zitter row: per-quantum `j_z = 1` reads ℏ/2-per-2ω-cycle, and the bilinears do oscillate at 2ω). Both rows stay versioned; the measurement now weights the Zitter row, and the question the data poses back to the author is whether a separately-constrained-helicity (or charge-sector-active, or resonant) ensemble can rescue the pair mechanism.

## 5. Known limits (the not-computed list, explicit)

| Limit | Status |
| --- | --- |
| the real-time vacuum is tachyonic (`det M(0) = −1`, band `k² < 0.618`; NO `β*` threshold) | measured + analytic (M7.5); **Q14**, the top theory question to Werbos; harmonic states above ω\* are immune; blocks M7.18-style real-time runs |
| the self-consistent charge (dynamic `j₀`) | not computed; the fixed-reservoir prescription is the validated stand-in (M7.6); Q7(b)/Q14 |
| absolute `μ` / `μ_B(1+α/2π)` | charge-unit-blocked (needs the monopole unit); de-phased `μ_J = 36.5 p.u.` on record |
| the M6 charged ledger `H/Q = 1.6890` | reproduced in 3D to 4.7e-5 but **window-defined** (no decaying channel at the canonical point; Q11): not used as a mass anchor |
| spin-½ statistics (720°), knot-sector persistence, masses beyond the electron | 🚧 Phase 2 + 4 tasks (topology-preserving constraints needed for knot sectors, M7.4 § 4) |

---

Cross-refs: milestone task [`tasks/m7_7_consolidation.md`](tasks/m7_7_consolidation.md) · the six source task docs [`m7_1`](tasks/m7_1_infra.md)·[`m7_2`](tasks/m7_2_fleury_torus.md)·[`m7_3`](tasks/m7_3_ouroboros_3d.md)·[`m7_4`](tasks/m7_4_charged_soliton.md)·[`m7_5`](tasks/m7_5_clock_stability.md)·[`m7_6`](tasks/m7_6_observables.md) · open questions [`m7_question_tracker.md`](m7_question_tracker.md) · the coverage matrix [`MODELS.md`](../../../../MODELS.md) · background [`m7_background.md`](m7_background.md).
