# M7.3, reproduce M6's electron in full 3D (the verbatim-ODE gate + the 3D chaoiton)

> Task **M7.3** (M7 / HydroBoros). taskID = M7.N iteration. Status: **Done** (2026-07-03, review approved; gate outcomes in [`§ FINDINGS 5`](#5-gate-outcomes-vs-the-plan--5)) · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation. **M7.3 carries the M6 Ouroboros electron from its 1D radial reduction into the full 3D lattice**, the second parent-reproduction gate. M6's canonical spec is [`0d_canonical.md`](../../../m6_ouroboros/research/0d_canonical.md); its § 6 ("things that DON'T work": ten sandbox versions of sign, regularity-class, Laplacian, and measure failures) is the reason this task leads with a derivation gate, not a run.

---

## 1. Pre-gate: the verbatim-ODE check (MANDATORY before any relaxation run)

The M6 charged-sector ansatz is **time-periodic**:

```text
A₀ = α(r) cos(ωt),   A⃗ = 0
J₀ = 0,              J⃗ = β(r) sin(ωt) φ̂
```

and its canonical reduced ODE ([`0d_canonical.md § 2.2`](../../../m6_ouroboros/research/0d_canonical.md)):

```text
α'' + α'/r − α/r²         + (ω² − m_J²) α + 4g α (α² + β²) = 0
β'' + β'/r − β/r² + 2ωα   − m_J² β        + 4g β (α² + β²) = 0
```

**The gate:** the M7 3D time-harmonic functional `E_ω` (built at M7.1), restricted to this ansatz, must reproduce this ODE **verbatim, term by term**, including the `2ωα` chiral cross-term, the vector cylindrical Laplacian, and the `r dr` measure. Do it twice: **symbolically** (sympy reduction of the functional's Euler-Lagrange equations under the ansatz) and **numerically** (evaluate `E_ω` on M6's converged 1D profile; compare against the 1D quadrature of the same energy). Any mismatch means OUR functional is wrong, and it is fixed before any 3D run is trusted. Note the subtlety this gate exists to catch: on this ansatz the coupling `m_J²A_μJ^μ` vanishes pointwise (the `2ωα` term enters through the derivative/EOM structure), so naive term-matching intuition fails ([`../m7_background.md § 4`](../m7_background.md), structural note).

## 2. The 3D run

| Step | What | Check |
| --- | --- | --- |
| 1 | **Embed** the M6 converged 1D `(α,β)` profile as the 3D seed (the 1D profile is the cylindrical section of the 3D toroidal chaoiton, per M6 § 2.1) | seed energy matches the 1D quadrature |
| 2 | **Relax** `E_ω` at fixed `ω = 1`, `g = 1.0`, M6's `f(s) = (g/4)s²`, first WITH the cylindrical-symmetry constraint | converges back to the 1D profile (the embedding is consistent) |
| 3 | **Release the symmetry constraint**, relax free in 3D | the decisive result either way (§ 4) |
| 4 | Measure `H`, `Q`, `H/Q`, `Q_CS` (linking), `2L/Q` | vs the calibration ledger (§ 3) |

BCs: the charged chaoiton has a Coulomb-tail `A₀ ~ Q/r`, so **vacuum-fixed boundary** with box-size extrapolation (the M7.1 BC decision; a net charge in a periodic box is Gauss-inconsistent).

## 3. Calibration ledger (pinned; the M7.3 gate compares like with like)

| Calibration | `g` | `H/Q` | Role here |
| --- | --- | --- | --- |
| **M6 canonical** ([`0d_canonical.md § 2.5`](../../../m6_ouroboros/research/0d_canonical.md)) | 1.0 | **1.6890** | **the primary target**: the 3D lattice vs the M6 1D BVP at the SAME `(g, ω, f)`, gate ≤ 1% |
| Werbos v5 point (corpus #10, June 2026) | 1.0625 | 1.6969 | tracked secondary until Q9 (the `(Ω,G)` dictionary) resolves |
| physical | , | 1.6875 | reference (`≈ 27/16`) |

The old gate ("recover `H/Q = 1.6969` from the 3D field") conflated the Werbos-v5 number with the M6 calibration; a 3D-vs-1D comparison is only meaningful at identical parameters. Full ledger + the v5 novelties (the `(Ω,G)` islands, `β*`): [`../m7_background.md § 4`](../m7_background.md).

## 4. Honest outcomes

| Outcome | Reading |
| --- | --- |
| 3D relaxation holds the chaoiton, `H/Q` matches the 1D value ≤ 1% | ✅ M6 reproduced in 3D, the first-ever full-3D chaoiton (M6 never had one) |
| the free 3D relaxation breaks the cylindrical symmetry / the profile drifts | ⚠️ a real physics result: the 1D chaoiton is not a 3D minimum; characterize the instability mode; feeds M7.4's blend design |
| no localized 3D minimum at the M6 parameters | ❌ documented honestly with the parameter scan; the Werbos-v5 islands (Q9) are the next place to look |

## 5. Gates

| Gate | Criterion |
| --- | --- |
| pre-gate | verbatim-ODE reproduction (symbolic + numeric), documented in this doc BEFORE step-2 runs |
| primary | `H/Q` (3D) vs `H/Q` (M6 1D BVP) ≤ 1% at `(g=1.0, ω=1)` |
| secondary | `2L/Q = 2ω` spin lock-in; `Q_CS = 1` from the 3D field-line linking |
| honest | symmetry-breaking / no-minimum outcomes reported per § 4 |

Artifacts: `scripts/m7_3_ouroboros_3d.py` + the sympy reduction note + `data/m7_3_*.npz` + `plots/m7_3_*.png`.

---

## FINDINGS (2026-07-03, execution)

Artifacts: [`../scripts/m7_3_ouroboros_3d.py`](../scripts/m7_3_ouroboros_3d.py) (modes `pregate` / `embed` / `relax`) · [`../data/m7_3_pregate_sympy.json`](../data/m7_3_pregate_sympy.json) · [`../data/m7_3_embed.json`](../data/m7_3_embed.json) · [`../data/m7_3_relax.json`](../data/m7_3_relax.json)

### Plots

![`../plots/m7_3_embed_convergence.png`](../plots/m7_3_embed_convergence.png)
![`../plots/m7_3_relax_traces.png`](../plots/m7_3_relax_traces.png)

### 1. Pre-gate part A (symbolic): the verbatim reduction found, with convention pins

The sympy scan reduces `L = −¼F² − ¼G² + κ A·J − f(J·J)`, `f(s) = c1 s + c2 s²` (metric (−,+,+,+), cylindrical, z-independent) over six candidate ansaetze × two quartic time-average conventions, takes the Euler-Lagrange equations of the period-averaged Lagrangian `⟨L⟩`, and solves `(κ, c1, c2)` for a verbatim match against the benchmark ODE (the `H/Q = 1.6890` producer, [`sandbox_v8/ouroboros_benchmark.py`](../../../m6_ouroboros/research/sandbox_v8/ouroboros_benchmark.py)) and against the [`0d_canonical.md § 2.2`](../../../m6_ouroboros/research/0d_canonical.md) form.

| Candidate | vs benchmark ODE | vs canonical § 2.2 |
| --- | --- | --- |
| C1: § 2.1 text ansatz (`A₀ = α cos ωt` scalar, `J_φ = β sin ωt`) | no (equations decouple; the μ=0 J-equation even forces α ≡ 0) | no |
| **C2: same-phase azimuthal doublet `A_φ = α(ρ)cos ωt`, `J_φ = β(ρ)cos ωt`** | **VERBATIM MATCH** (both quartic conventions) | no |
| C3: quadrature phases (`A_φ` cos, `J_φ` sin, the LoE 9b § 5.1 phase text) | no (α-equation decouples: `⟨cos·sin⟩ = 0`) | no |
| C4-C6: rotating (φ̂, ẑ) doublets (in-phase / quarter-turn / counter) | no | no |

Convention pins solved by the match (the pre-gate's key deliverable):

| Pin | Value | Reading |
| --- | --- | --- |
| coupling `κ` | **−1** | the operative interaction is `−A·J` (sign-flipped vs the written `+m_J²A·J` at `m_J = 1` in (−,+,+,+)) |
| `c1` (f linear) | **−λ/2** | the λ-term is a FOCUSING (negative) mass term; `0d_canonical § 1` writes `f(s) = (g/4)s²` with no λ at all: the benchmark ODE requires it |
| `c2` (f quartic) | **−2g** (RWA, `f` at `s₀ = ⟨s⟩`) or **−4g/3** (exact `⟨s²⟩` bookkeeping) | FOCUSING quartic, forced by the benchmark's `+4gβ³`; both time-average conventions match verbatim on-ansatz and differ only off-ansatz |
| reduced conserved charge | `Q_can = ω(α² + β²)/2` (both sectors) | `⟨L⟩ = ω Q_can − E_ω` verified symbolically: the correct 3D objective is fixed-`Q_can` extremization of `E_ω` with multiplier ω, exactly Werbos's own "constrained minimum of `H' = H − λQ`" frame (LoE 9b § 5) |
| `E_ω` (averaged Hamiltonian) EL | matches **nothing** | minimizing `E_ω` unconstrained has the ω²-sign flipped in every equation (harmonic-oscillator structure); the M7.1 as-built `E_ω`-minimization frame is corrected by this gate, as designed |

Structural corollaries (both are M6-documentation findings, Werbos-question material, tracked in [`../m7_question_tracker.md`](../m7_question_tracker.md)):

1. **`0d_canonical.md § 2.2` as written is not an EL reduction of the M6 Lagrangian** under any scanned single-frequency ansatz. Time-averaging bilinears of harmonic fields produces only ω⁰ and ω² sector couplings; the `2ωα` (ω¹) chiral term would need a `∇X₀·∂ₜX⃗` cross term, which is geometrically zero on every candidate. The § 2.2 quartic `4gβ(α²+β²)` (both amplitudes inside `s`) also fits no candidate.
2. **The LoE 9b § 5.1 phase assignment (`A ∝ cos ωt`, `J ∝ sin ωt`) is inconsistent with its own benchmark**: quadrature phases decouple the α-equation. The benchmark ODE is the same-phase reduction.

### 2. Pre-gate part B: the charged calibration is a WINDOWED quantity (delocalization)

Probing the benchmark profile (g=1, ω=1, λ=1, A0=B0=0.1) as a function of the integration window:

| window `r_max` | `H/Q` | `Q` |
| --- | --- | --- |
| 8 | 1.641 | 0.199 |
| **12 (the benchmark `R_MAX`)** | **1.68896** | 0.293 |
| 16 | 1.439 | 0.430 |
| 24 | 1.473 | 0.634 |
| 40 | 1.396 | 1.097 |

`Q` grows without bound; the profile does not decay (`max|α| = 0.225` at all windows). The reason is analytic: the far-field linear system gives the dispersion `(ω² − k²)(ω² + λ − k²) = 1`, at the canonical point `k⁴ − 3k² + 1 = 0` with both roots `k² = (3±√5)/2 > 0`: **no decaying channel exists at the canonical point**; the A-sector is a radiation field at frequency ω. `H/Q = 1.6890` is therefore a windowed quadrature pinned to `r_max = 12`, the same windowed-integration disease the M6 record itself caught in the neutral sector ([`0c_sandbox_v8.md`](../../../m6_ouroboros/research/0c_sandbox_v8.md) Q42) but never flagged for the charged calibration. This retroactively strengthens the HydroBoros thesis: a localized pure-Maxwell-like electron needs confinement ([`../m7_background.md § 5b`](../m7_background.md), Nadirashvili), and the M6 charged sector alone does not provide it in the radial reduction.

Gate consequence: the 3D comparison is defined **windowed like-with-like**: the benchmark quadratures implemented as 3D per-unit-length lattice integrals on the window ρ ≤ 12 (M7.2 interface weights), against the 1D reference on the same window.

### 3. Pre-gate part C (numeric): the 3D lattice carries the M6 electron to 0.005%

Embedding the converged 1D profile as `avc = α(ρ)φ̂`, `jvc = β(ρ)φ̂` (the C2 winner) on the periodic box (L = 28.8 in-plane, thin periodic z, cubic cells):

| N (h) | windowed `H/Q` (3D) | rel EL residual `‖gE − ω gQ‖` |
| --- | --- | --- |
| 96 (0.300) | 1.67121 | 4.5e-3 |
| 144 (0.200) | 1.68121 | 1.1e-3 |
| 192 (0.150) | 1.68457 | 3.6e-4 |
| **Richardson (h²)** | **1.68889** | → 0 |

**Primary gate: PASS.** `H/Q` (3D, extrapolated) = 1.68889 vs the native 1D ledger 1.68897: deviation **4.7e-5 (0.005%)**, 200× inside the ≤ 1% gate. The identity `S_ω = ωQ_can − E_ω` holds on the lattice to machine precision (1e-16); the Taichi-AD twin matches the numpy functional to 5e-14; the EL residual at the embedded profile falls with h as expected, confirming the embedded 1D solution is a genuine discrete critical point of the pinned functional pair `(E_ω, Q_can)` with multiplier ω.

### 4. The 3D relaxation (stages 2-3): the M6 electron is a SADDLE in 3D, ending in focusing collapse

Setup: N = 96 (h = 0.3), fixed-`Q_can` FIRE (tangent projection + exact quadratic restore; `Q_can` conserved to 8 digits throughout), Dirichlet freeze at ρ > 13 (fields pinned to the profile), stage 2 with the gradient projected onto the axisymmetric z-independent subspace (z-variance stays at 1e-32), stage 3 free at Nz = 32 with a 1e-3 smoothed random perturbation. Data: [`../data/m7_3_relax.json`](../data/m7_3_relax.json), traces + final sections: [`../plots/m7_3_relax_traces.png`](../plots/m7_3_relax_traces.png).

| Stage | Trajectory | End state |
| --- | --- | --- |
| stage 2 (symmetric) | leaves the chaoiton immediately (E: 13.15 → 4.14 by it 200; windowed H/Q: 1.671 → 0.29), converges to a DIFFERENT near-critical state (E = 2.6398, `\|g\| = 5e-8`, broad bump peaked at ρ ≈ 6), lingers ~400 iterations | finds an axis-concentration channel (peak jumps to ρ = 0.21, it 900) and blows up non-finite at it ≈ 1000 |
| stage 3 (free 3D) | near seed at it 100 (drift 0.17), then supercritical focusing collapse: E = +51 → −8.9e6, max\|field\| 0.25 → 124, collapse spike at ρ ≈ 2.5, z-variance 0.94 | non-finite at it ≈ 300 (guarded abort) |

Reading, per the plan's § 4 honest-outcomes table (row 2/3): **the embedded M6 electron is a genuine 3D critical point (§ 3) but NOT a constrained minimum**: constrained descent departs immediately in both sectors and terminates in focusing collapse. The mechanism is structural, not a lattice artifact: the verbatim pins force a FOCUSING potential (`c1, c2 < 0`, the benchmark's own `+λβ + 4gβ³`), which at fixed `Q_can` is L²-critical in the symmetric (effectively 2D) sector and supercritical in free 3D, so `E_ω` is unbounded below along concentration. Werbos's "constrained minimum + conjugate-point" stability claim (LoE 9b § 5) can hold at most within the 1D radial ansatz manifold; the 3D lattice opens the collapse channel. Caveat kept honest: FIRE descent demonstrates instability (a descent direction exists and is followed) but does not measure a growth rate; the escape is seeded by the O(h²) truncation residual in stage 2 and by the explicit perturbation in stage 3.

The M6 ansatz carries **zero A-sector helicity** (`αφ̂ · ∇×(αφ̂) ≡ 0`, and the measured `H_A` stays at 0 in stage 2, ≤ 1e-2 injected by the perturbation in stage 3): M7's helicity anti-collapse guard ([`../m7_background.md § 5b`](../m7_background.md)) is exactly INERT on the M6 electron. This is the direct motivation for the M7.4 blend: the Fleury torus sector activates `B_A` and helicity, which is precisely the missing collapse guard.

### 5. Gate outcomes vs the plan (§ 5)

| Gate | Outcome |
| --- | --- |
| pre-gate (verbatim ODE, symbolic + numeric) | ✅ PASS: C2 reduction verbatim with convention pins (§ 1); embedded profile is a discrete critical point, residual → 0 as h² (§ 3) |
| primary (`H/Q` 3D vs 1D ≤ 1% at `g=1, ω=1`) | ✅ PASS (windowed like-with-like): 1.68889 vs 1.68897, dev 4.7e-5 (§ 3); the window itself is the § 2 finding |
| secondary (`2L/Q = 2ω`; `Q_CS = 1` linking) | ⚠️ documented as degenerate here: `L = ωQ_J` is definitional in the benchmark (sandbox_v8 Q38, not an independent check); the A-J cross-helicity/linking is identically zero on the straight-cylinder ansatz (`φ̂ · ẑ` orthogonality): the `Q_CS = 1` topology lives on the torus compactification, deferred to M7.4 |
| honest (symmetry-breaking / no-minimum reported) | ✅ delivered: saddle + focusing collapse characterized (§ 4); no localized 3D minimum exists at the M6 parameters within the verbatim functional, and § 2 shows even the 1D "localization" is windowed |

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (M7.3) · M6 canonical spec [`0d_canonical.md`](../../../m6_ouroboros/research/0d_canonical.md) (§ 2 recipe, § 5 units, § 6 graveyard) · background [`../m7_background.md`](../m7_background.md) (§ 4 ledger + structural note, § 5a harmonic frame) · tracker [`../m7_question_tracker.md`](../m7_question_tracker.md) (Q8 resolved here; Q6 evidence; Q11/Q12/Q13 opened here) · upstream [`m7_1_infra.md`](m7_1_infra.md) (the functional this task gates) · downstream [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md) (the M6-embedded seed + the helicity-guard motivation, § FINDINGS 4).

---

## TASK REVIEW (2026-07-03)

**Task Duration:** 01:38 (from 11:48 to 13:26 EDT)
**Usage Cap Triggered:** NO (finished before the 3:10pm reset; resume ping disarmed without firing)

**Results** (full detail: [`§ FINDINGS`](#findings-2026-07-03-execution)):

| Gate | Outcome |
| --- | --- |
| Pre-gate A: verbatim ODE (symbolic) | ✅ PASS: the benchmark ODE is the verbatim EL reduction on the same-phase azimuthal doublet, with the convention pins solved (`κ = −1`; FOCUSING `f`; fixed-`Q_can` objective, multiplier ω) |
| Pre-gate B: delocalization probe | ⚠️ discovery: `H/Q = 1.6890` is a windowed quadrature at the benchmark's `r_max = 12`; no decaying far-field channel exists at the canonical point (both `k² = (3±√5)/2 > 0`) |
| Pre-gate C: numeric embed | ✅ PASS: windowed 3D `H/Q` → 1.68889 vs ledger 1.68897 (dev 4.7e-5, 200× inside the ≤1% gate); EL residual falls as h²; identity + Taichi twin at machine precision |
| Stage 2/3 relaxation | ⚠️ honest result: the embedded M6 electron is a genuine 3D critical point but a constrained SADDLE; symmetric descent departs then axis-concentrates; free 3D collapses (supercritical focusing); `Q_can` conserved to 8 digits |
| Secondary gates | ⚠️ degenerate here: `2L/Q = 2ω` definitional (sandbox_v8 Q38); `Q_CS` linking is zero on the straight cylinder, lives on the torus, deferred to M7.4 |

**Issues / blockers**: `0d_canonical.md § 2.2` not an EL reduction (Q12 opened); the charged calibration window-defined (Q11 opened); 3D saddle vs the conjugate-point claim (Q13 opened); M7.1's unconstrained-`E_ω` frame corrected to fixed-`Q_can` (Q8 RESOLVED); no >1MB data created.

**Action needed**: M7.4 next (nothing blocks it; it directly probes the missing helicity guard); the consolidated M7.1-M7.3(-M7.4) report + ask packages per the tracker comms plan; `0d_canonical.md` correction note after Werbos answers Q12.

**Findings**: The M6 electron survives the trip to 3D as arithmetic but not as physics: the 3D lattice reproduces the 1D ledger to 0.005% (pre-gate airtight, every sign pinned), but the ledger itself is a windowed quadrature of a non-decaying radiating profile, and the configuration is a 3D constrained saddle that collapses under its own focusing potential, with the helicity guard exactly inert on it. All three discoveries point the same way: the M6 sector alone cannot localize or stabilize the electron, which is precisely the confinement + helicity role the M7.4 Fleury blend was designed to supply.

**Research docs created / updated**:

- [this task doc](m7_3_ouroboros_3d.md) (§ FINDINGS 1-5, plots inline)
- [`../scripts/m7_3_ouroboros_3d.py`](../scripts/m7_3_ouroboros_3d.py) (modes `pregate` / `embed` / `relax`)
- [`../data/m7_3_pregate_sympy.json`](../data/m7_3_pregate_sympy.json) · [`../data/m7_3_embed.json`](../data/m7_3_embed.json) · [`../data/m7_3_relax.json`](../data/m7_3_relax.json)
- [`../plots/m7_3_embed_convergence.png`](../plots/m7_3_embed_convergence.png) (key plot: the windowed-H/Q panel) · [`../plots/m7_3_relax_traces.png`](../plots/m7_3_relax_traces.png) (key plot: collapse traces + final sections)
- [`../m7_question_tracker.md`](../m7_question_tracker.md) (Q8 → RESOLVED; Q6 evidence; Q11/Q12/Q13 opened; hardest-pieces board: 3 rows closed)
