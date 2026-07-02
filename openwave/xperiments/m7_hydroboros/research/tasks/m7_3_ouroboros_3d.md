# M7.3, reproduce M6's electron in full 3D (the verbatim-ODE gate + the 3D chaoiton)

> Task **M7.3** (M7 / HydroBoros). taskID = M7.N iteration. Status: **Backlog** · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

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

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (M7.3) · M6 canonical spec [`0d_canonical.md`](../../../m6_ouroboros/research/0d_canonical.md) (§ 2 recipe, § 5 units, § 6 graveyard) · background [`../m7_background.md`](../m7_background.md) (§ 4 ledger + structural note, § 5a harmonic frame) · Q6/Q9 in [`../m7_question_tracker.md`](../m7_question_tracker.md) · upstream [`m7_1_infra.md`](m7_1_infra.md) (the functional this task gates) · downstream [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md) (the M6-embedded seed).
