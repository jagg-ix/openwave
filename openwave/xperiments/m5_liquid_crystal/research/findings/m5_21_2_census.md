# M5.21.2: the 3D 3-lepton axis-permutation scan (census record)

**Status**: 🚧 IN PROGRESS 2026-07-17 (P0 gates ✅, P1 ladder ✅, P2 census running). Task: [`../tasks/m5_21_2_task_details.md`](../tasks/m5_21_2_task_details.md). Prescription: Duda 2026-07-17 ([`../tasks/m5_21_convo.md § 2026-07-17`](../tasks/m5_21_convo.md)): "first focus on 3D case, where the hedgehog is topologically protected"; minimize from the biaxial hedgehog diag(1, δ, 0) and the rotated (δ, 0, 1) / (0, 1, δ), "searching for local minima (e.g. just gradient descent, global should be electron), hopefully getting candidates for 3 leptons". Method-note standard ([`../../../../../dev_docs/METHOD_NOTE.md`](../../../../../dev_docs/METHOD_NOTE.md)): equations first, every term mapped to code, gates next to results.

## 1. The 3D functional (equations first)

The field is a 3×3 REAL SYMMETRIC tensor M(x) on a cubic grid (spacing h = 1, box N³, cell-centered coordinates, N even so the axis/origin are never sampled). This is the verified 4×4 Minkowski stack of [`m5_21_1_method_note.md`](m5_21_1_method_note.md) with the time row dropped and η → identity (the author's 3D-first directive; no g in 3D).

```text
A_i   = d_i M                      (i = x, y, z; central differences
                                    interior, one-sided at edges)
C_ij  = [A_i, A_j] = A_i A_j - A_j A_i          (antisymmetric)
u     = 4 * sum_{i<j} tr(C_ij^T C_ij)           (curvature density)
V     = w * sum_{p=1..3} (tr(M^p) - C_p)^2      (trace-target potential)
C_p   = 1 + delta^p                (vacuum spectrum (1, delta, 0))
E     = sum_x h^3 (u + V),  w = WSCALE = 7.24023879e-4 (carried
        unchanged from the verified 4D stack, continuity)
```

Derrick scaling in 3D: under x → λx, E(λ) = E_u/λ + λ³E_V, so a finite-size stationary point must satisfy the virial balance **E_u = 3 E_V** (the Faber Eq 48 mechanism; the quartic-only curvature is why a stable size can exist at all). u/3V = 1 is therefore the convergence figure of merit throughout.

The p-range choice: in 3D three trace invariants pin all three eigenvalues, so p = 1..3 is the complete spectrum target (the 4D stack's p = 1..4 was the 4-eigenvalue analog). The potential FORM itself remains the author-open Q25; this record uses his 2026-07-05 trace-target candidate.

**The seeds** (his axis-permutation family): with r̂ the radial unit vector, φ̂ the azimuth (ẑ × r̂ normalized), t̂ = φ̂ × r̂, and the core smoothing w(r) = 1 − exp(−(r/r_c)²), r_c = 4, a = (1 + δ)/3:

```text
S(x)      = lam_r r̂r̂^T + lam_phi φ̂φ̂^T + lam_t t̂t̂^T
M_seed(x) = w(r) S(x) + (1 - w(r)) a I
seed A "electron": (lam_r, lam_phi, lam_t) = (1,     delta, 0)
seed B:            (delta, 0,     1)
seed C:            (0,     1,     delta)
```

Each seed carries the SAME spectrum {1, δ, 0} in a different alignment between the eigenframe and the spatial frame: exactly "the space of possible rotations of hedgehog ansatz" (FRAME p. 15). The z-axis is the regularized vortex line (the transverse eigen-pair is discontinuous there in the raw ansatz; the core smoothing plus relaxation regularize it, and the grid never samples the axis).

**Descent**: FIRE (dt0 = 0.02, dt_max = 0.2, force refreshed EVERY iteration, non-finite guard), boundary either PINNED (the outermost cell shell held at the seed's own far field: the R³ proxy, winding enforced at the boundary the way infinity enforces it in R³) or FREE (all cells update: the protection test).

## 2. Equation-to-code map

Script: [`../scripts/m5_21_2_a_scan3d.py`](../scripts/m5_21_2_a_scan3d.py) (self-contained; numpy only).

| Term / object | Function | Notes |
| --- | --- | --- |
| A_i, adjoint | `d_ax`, `d_ax_adj` | exact adjoint pair (the complex-step gate covers both) |
| u, V, E | `e_split`, `e_total` | complex-safe (analytic in M: the complex-step path) |
| analytic gradient | `grad3` | curvature part: ∂u/∂A_i = 8[C_ij, A_j] chained through `d_ax_adj`; potential part: w·Σ_p 2p(tr(M^p) − C_p)M^(p−1); symmetric-preserving |
| seeds | `seed3`, `frame`, `SEEDS` | the permutation table |
| vacuum | `vac3` | G2 reference |
| FIRE | `fire3` | plateau stop: ΔE < 1e-10 across 2000 iters; f_tol 1e-8 |
| boundary pin | `pin_shell` | outermost cell shell |
| retention (scalar) | `retention` | shell-mean (v_k · ê_σ(k))² per eigen index, σ = the seed's assignment |
| frame-overlap profile | `overlap_profile` | O_kl(r) + eigenvalue profiles, 24 shells |
| core / axis reads | `axis_center_reads` | three-equal center + two-equal axis diagnostics |
| half-energy radius | `r_half` | on the potential-excess density |
| films | `film` | basic (eigen/alignment) + thermal (log u / log V) strips, y = 0 slice |
| gates | `gates` | G0-G3 below |
| ladder / census | `ladder`, `scan`, `collect` | per-run JSON files, race-free; `collect` merges |

## 3. Gates (all green, try 1)

| Gate | What | Measured | Bar |
| --- | --- | --- | --- |
| G0 | complex-step vs analytic gradient, random 8³ lattice + the 16³ seed, 4 directions each | 1.2e-15 rand / 5.2e-14 seed | ≤ 1e-10 ✅ |
| G1 | internal SO(3): E(QMQᵀ) = E(M), random orthogonal Q | 7.6e-16 | ≤ 1e-10 ✅ |
| G1n | negative control: non-orthogonal Q must move E | 4.0e-2 shift | > 1e-6 ✅ |
| G2 | vacuum energy | 0.0 exact | ≤ 1e-12 ✅ |
| G3 | seed far-field spectrum (ascending), all seeds | (1.3e-7, 0.3000000, 0.9999998) | = (0, δ, 1) ✅ |

Data: `gates` key of [`../data/m5_21_2_scan3d.json`](../data/m5_21_2_scan3d.json).

## 4. P1: the boundary-integrity ladder (his flagged risk, measured)

Seed A, 800-iteration probes, N ∈ {32, 48, 64} × δ ∈ {0.3, 0.1, 0.03} × BC ∈ {pinned, free}. Retention = shell-mean squared overlap between each eigenvector and its seed-assigned frame axis (1 = perfect hedgehog, 1/3 = unwound).

| n | δ | BC | retention end | E seed → end | u/3V | core min λ |
| --- | --- | --- | --- | --- | --- | --- |
| 32 | 0.3 | free | 0.771 | 15.76 → 0.22 | 0.029 | −0.220 |
| 32 | 0.3 | pinned | 0.858 | 15.76 → 5.00 | 1.638 | 0.374 |
| 32 | 0.1 | free | 0.709 | 18.37 → 0.42 | 0.042 | −0.197 |
| 32 | 0.1 | pinned | 0.742 | 18.37 → 6.61 | 1.248 | 0.424 |
| 32 | 0.03 | free | 0.629 | 20.74 → 0.52 | 0.052 | 0.011 |
| 32 | 0.03 | pinned | 0.630 | 20.74 → 7.53 | 1.179 | 0.436 |
| 48 | 0.3 | free | 0.917 | 17.81 → 2.12 | 0.782 | −0.021 |
| 48 | 0.3 | pinned | 0.920 | 17.81 → 5.00 | 0.970 | 0.226 |
| 48 | 0.1 | free | 0.930 | 19.85 → 4.93 | 0.665 | 0.073 |
| 48 | 0.1 | pinned | 0.909 | 19.85 → 7.02 | 0.792 | 0.209 |
| 48 | 0.03 | free | 0.871 | 22.37 → 6.83 | 0.531 | 0.358 |
| 48 | 0.03 | pinned | 0.777 | 22.37 → 8.09 | 0.721 | 0.403 |
| 64 | 0.3 | free | 0.945 | 19.17 → 3.45 | 1.029 | 0.133 |
| 64 | 0.3 | pinned | 0.929 | 19.17 → 5.10 | 1.115 | 0.239 |
| 64 | 0.1 | free | 0.970 | 20.60 → 7.42 | 0.782 | 0.237 |
| 64 | 0.1 | pinned | 0.968 | 20.60 → 7.61 | 0.815 | 0.237 |
| 64 | 0.03 | free | 0.969 | 23.19 → 8.73 | 0.719 | 0.359 |
| 64 | 0.03 | pinned | 0.974 | 23.19 → 8.90 | 0.737 | 0.379 |

**The P1 read (probe depth)**: box size is the protective variable, not δ, and the protection becomes INTRINSIC as the box grows. At N = 32 the FREE boundary drains the object at every δ (E collapses to 0.2-0.5, u/3V ≈ 0.03-0.05, worst at δ = 0.3: his "small box + huge delta" failure mode, measured). At N = 48 the free-boundary object SURVIVES (retention 0.87-0.93). At N = 64 the pinned/free distinction nearly vanishes (retention 0.93-0.97 both; δ = 0.3 free at u/3V = 1.029): the boundary no longer matters, which is the finite-box version of "rather impossible in full R^3". δ = 0.3 needs no reduction at N ≥ 48.

**Working point**: N = 48, δ = 0.3. Census: seeds A/B/C pinned (each shell holds its OWN far field) + seed A free (the protection control).

## 5. P2 + P3: the census (3 axis-permutation seeds + the charged ring)

**The deep-run table (24k iterations, N = 48, δ = 0.3; all `max_iter` stops, still relaxing slowly: these are characterized endpoints, NOT converged minima):**

| Run | E_end | E_u | E_V | u/3V | r_half | retention (8-16) | Verdict |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A pinned (electron) | **3.722** | 3.350 | 0.372 | 3.00 | 19.3 | 0.70 | LOWEST of the three seeds ✅ |
| C pinned | 5.600 | 5.500 | 0.100 | 18.3 | 20.9 | 0.55 | middle level |
| B pinned | 17.370 | 16.833 | 0.537 | 10.4 | 19.0 | 0.74 | highest level |
| A free | 0.024 | 0.004 | 0.020 | 0.07 | 12.8 | 0.62 | DRAINED: the 800-iter survival was transient; by 24k the winding left through the free boundary |
| R ring / A ×100 stiffness | 🚧 running | | | | | | |

**Two headline reads:**

1. **The 3-level ordering exists, with the electron lowest**: E_A < E_C < E_B (3.72 < 5.60 < 17.37), three distinct energy levels from the three rotation seeds: the qualitative FRAME p. 15 lepton signature, measured (with the honest caveat that these are non-converged endpoints; the ORDERING is the robust read, the values are not final).
2. **Topology holds, size does not (at toy wscale)**: the A-pinned overlap profile shows a near-perfect hedgehog far field (alignment 0.99+, vacuum spectrum at r > 25: the winding is intact, exactly his topological-protection claim) around a MELTED, INFLATED core (alignment 0.32-0.65 and slightly negative min eigenvalue inside r ≲ 15; r_half 19.3; u/3V = 3.0 = the state still wants to expand). Derrick decodes it: λ* = (E_u/3E_V)^(1/4) ≈ 1.3 at the endpoint and the balance size at wscale = 7.24e-4 exceeds the box, so the object inflates against the pinned wall instead of converging. The deep free-boundary run drains entirely: at 24k iterations even N = 48 is a "small box" in his sense (the 800-iter ladder survival was a transient; the N = 64 rungs were probe-depth only, flagged for the successor).

The stiffness arm (wscale ×100, shrinking the Derrick size by 100^(1/4) ≈ 3.2) is running as the pre-registered fallback: does a compact virial-balanced electron form when the balance size fits the box?

Boundary caveat for the audit: the single-cell `vmax` locus reads on pinned runs sit at the shell (pin-vs-relaxed mismatch); the shell-averaged `shell_peak_r` (2.9 for A/B, 1.0 for C) is the physical read. The P3 ring arm (user amendment mid-run): the charged disclination ring in seed A's exact winding sector (half-disclination ring core, radius a = 4, escaped interior; the meridional-angle construction `seed_ring` in the script), pinned at the working point. Discriminator: E_ring vs E_A endpoints, testing the [`../m5_particle_hunt.md`](../m5_particle_hunt.md) synthesis nuance (hedgehog and small charged ring = same topological sector) and the M5.16 Q8 off-origin melt.

The schematic (illustration, not data; script [`../scripts/m5_21_2_b_topo_illustration.py`](../scripts/m5_21_2_b_topo_illustration.py)): the three objects side by side, with the Toulouse-Kleman placement of the charged ring (locally the s = 1, d = 1 line cell as a closed cord; globally the s = 2, d = 0 erizo cell, far sphere q = 1). Note the loop/ring inside-out duality in the equatorial cuts: it is WHY one is chargeless and the other charged.

![topology catalog: loop vs hedgehog vs charged ring](../plots/m5_21_2_topo_catalog.png)

## 6. Films

🚧 (basic + thermal strips per run, y = 0 meridional slice, adapted from the 4×4 templates to the 3×3 stack.)

## 7. Not computed (this task)

| Item | Why |
| --- | --- |
| The 4D lift (time row, g, field rotation, J) | [M5.21.3](../tasks/m5_21_3_task_details.md), gated on this census |
| The potential-form comparison (Eq 12 eigenvalue vs trace-target vs LdG vs det-constraint) | Q25 remains author-open; this record runs the trace-target candidate only |
| Physical scales (δ ~ 1e-10, g ~ 1e10) | scaling ladders are the vehicle (the M5.21.1 P4 pattern); not re-run here |
| Lattice topological degree (integer q) | the frame-overlap retention + profiles are the primary observable (director sign ambiguity makes naive degree sums fragile); the winding is enforced/tested via the BC arms instead |

## 8. Audit

🚧 (independent adversarial audit before the review; verdicts land here.)
