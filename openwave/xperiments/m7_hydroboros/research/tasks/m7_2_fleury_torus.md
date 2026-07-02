# M7.2, reproduce Fleury's torus on the lattice (quadrature, the trust-builder)

> Task **M7.2** (M7 / HydroBoros). taskID = M7.N iteration. Status: **Backlog** · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation. **M7.2 reproduces the dos Santos & Fleury electron ([arXiv:2510.22384](https://arxiv.org/abs/2510.22384), corpus #1) on the M7 lattice.** It is **pure quadrature**: the ansatz is analytic, the lattice evaluates it and integrates observables. **No minimizer is needed, so M7.2 can run in parallel with the M7.1 minimizer build** (it needs only the lattice, the field containers, and the integration kernels). This is M7's equivalent of M5.11's "reproduce Faber first" trust-builder.

---

## 1. What the paper actually does (read 2026-07-02, full text)

The ansatz satisfies **Maxwell-with-sources where the sources are read off the fields** (the "geometrical charge" ontology): Gauss-B and Faraday are verified (Faraday forces `ω = 2c/R₀`, monochromatic), and Ampère-Maxwell *defines* `J` from the fields; the consistency check is `∇·J` (from Ampère) == `−∂ρ/∂t` (continuity). So the lattice job is:

```text
1. evaluate  E, B  from the ansatz on the grid          (complex fields; physical = Re[·])
2. compute   ρ = ε₀ ∇·E ,   J = (∇×B − c⁻² ∂ₜE)/μ₀     (finite differences)
3. integrate Q_rms, μ, L (spin), U over the torus       (the paper's four constraint observables)
4. compare to the paper's solved values                  (all dimensionless ratios)
```

## 2. Conventions contract (the reproduction traps, pinned)

| # | Trap | Contract |
| --- | --- | --- |
| 1 | **The Heaviside is inverted**: the paper defines `H(r−r₀) = 1 for r < r₀`, 0 outside (their Eq 1 text), the opposite of the standard `H` | implement their stated definition (fields live INSIDE the tube), never the formula's face value |
| 2 | **Instantaneous charge integrates to zero** (`ρ ∝ sin(φ−ωt)` over one wavelength around the ring) | the electron charge is `Q_rms` (RMS over volume), their Eq 19: `√2 π² ε₀ E₀ r₀² = e`; compute RMS, not the plain integral |
| 3 | **Complex-field energy convention**: the paper's `u(t) = ε₀E₀²(1 + R/4R₀)` (Eq 31) comes from the appendix's specific convention | pin the convention against the **FLDB Appendix** (corpus #1, Appendix PDF) before comparing `U`; if ambiguous, compute both real-part-instantaneous and complex-modulus averages and report which matches Eq 32 |
| 4 | **The mask's delta shell**: `∇·E` at the tube boundary is a distribution; the lattice smears it | grid-convergence study is mandatory (§ 4); report observables vs `h` with Richardson extrapolation |
| 5 | `ω` is not free | enforce `ω = 2c/R₀` (Faraday); phase velocity `v_p = 2c` is a check, not a violation |

## 3. Reproduction targets (paper Eqs 37-41, 43; all dimensionless)

| Observable | Target |
| --- | --- |
| amplitude | `E₀/E_S ≈ 0.286` (Schwinger scale) |
| major radius | `R₀/r_c ≈ 1.573` (`= π/2`) |
| minor radius | `r₀/r_c ≈ 0.152` (`= √(πα)`... per Eq 39) |
| rest energy | `U/m_ec² ≈ 0.795` (`= 5/2π`) |
| frequency | `ω/ω_D ≈ 0.636`, `ℏω/m_ec² ≈ 1.27` |
| charge | `Q_rms = e` (constraint Eq 19 reproduced by the lattice integral) |
| magnetic moment | `μ = μ_B(1 + α/2π)` (constraint Eq 21) |
| spin | `L_z = ℏ/2` (constraint Eq 29) |

Procedure: set `(E₀, R₀, r₀, ω)` to the paper's solved values in `r_c = 1` natural units (M7.1 units contract) and verify the lattice integrals return the four constraints. This validates our integration kernels against a published result, exactly what "reproduce Faber" did for M5.11.

## 4. Grid plan

The tube is thin (`r₀ ≈ 0.152 r_c` vs `R₀ ≈ 1.573 r_c`): resolving it needs `h ≲ r₀/8 ≈ 0.02 r_c`. Box `~4 r_c` across → `~200³` at the finest level; run `h ∈ {r₀/4, r₀/8, r₀/16}` and Richardson-extrapolate. Report every observable as (value, convergence order, extrapolated value).

## 5. Stretch: the Bessel-envelope variant (first beyond-the-paper result)

Fleury § 5.5 names the fix for the unphysical Heaviside mask: Bessel envelopes. Ceperley's rotating mode ([`../../theory/ceperley_rotating_waves.md`](../../theory/ceperley_rotating_waves.md) § 4, Eq 15) is the same phase structure with a `J_m(k_c r)` radial envelope. The stretch: replace the mask with the `J_1` envelope, re-integrate the four observables, report how the constraint solution shifts (does `U/m_ec²` move toward 1?). Cheap (same quadrature machinery), and it is M7's **first new result** beyond the published paper.

## 6. Gates

| Gate | Criterion |
| --- | --- |
| primary | all § 3 targets recovered at demonstrated grid convergence |
| consistency | `∇·J` (Ampère) == `−∂ρ/∂t` (continuity) on the lattice to grid accuracy |
| honest limits restated | the mask is unphysical at the boundary, far field suppressed, `U = 0.795 m_ec²` short of 1: reproduced AS the paper states them, not repaired silently |
| stretch | the Bessel-envelope observables table |

Artifacts: `scripts/m7_2_fleury_torus.py` + `data/m7_2_*.npz` + `plots/m7_2_*.png` (field sections, convergence curves, observables table).

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (M7.2) · background [`../m7_background.md § 3`](../m7_background.md) (the Fleury model + targets) · conventions sources: FLDB Main + Appendix (corpus #1), [`../../theory/ceperley_rotating_waves.md`](../../theory/ceperley_rotating_waves.md) (Bessel stretch), [`../../theory/feynman_maxwell_equations.md`](../../theory/feynman_maxwell_equations.md) (the Maxwell baseline) · upstream [`m7_1_infra.md`](m7_1_infra.md) (lattice + units; minimizer NOT required) · downstream [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md) (the Fleury seed).
