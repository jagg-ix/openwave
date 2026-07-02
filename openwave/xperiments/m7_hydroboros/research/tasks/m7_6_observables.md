# M7.6, electron observables (mass, charge, μ, spin, KG, two-charge Coulomb)

> Task **M7.6** (M7 / HydroBoros). taskID = M7.N iteration. Status: **Backlog** · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation. **M7.6 reads the QED electron's observables off the relaxed field** (the M7.4 state, validated by M7.5) and lands the two-charge Coulomb law.

---

## Plan

| Observable | How | Target / gate |
| --- | --- | --- |
| mass | `E_ω` of the relaxed state, converted via the units contract (M6 anchors) | reported vs `m_e c²`; Fleury's own analytic ansatz gives `0.795 m_e c²`, so an honest gap is expected and quantified |
| spin | `L = ∫ R×p dV` from the Poynting momentum; **cross-checked against Ceperley's rotating-wave law `L_z = mU/ω`** ([`../../theory/ceperley_rotating_waves.md`](../../theory/ceperley_rotating_waves.md) § 4b: exact for rotating modes, quantized when `U/ω = ℏ`) | `ℏ/2` vs measured; the Ceperley identity validates the lattice integrals independently |
| magnetic moment | `μ = ½∫ R×J dV` (RMS convention per the M7.2 contract) | `μ_B(1 + α/2π)` (the Schwinger factor is the precision bar) |
| charge | `Q_div` Gauss flux (from M7.4) | `= e` in calibrated units; quantization evidence per the M7.4 Q3 table |
| Klein-Gordon twist | the phase/twist sector's dispersion on the lattice | KG form recovered (García López corpus #17 is the gauge-fixing route: KG from the electrovacuum) |
| **two-charge Coulomb** | two relaxed solitons at separation `d` (net-neutral pair OK in a periodic box; opposite + same charge), interaction energy `E(d)` | `E(d) ~ 1/d` (Duda's prescription, the [roadmap](../m7_roadmap.md) Phase A note); **stretch: extract `α_sol` from the fit and compare Faber & Golubich `α⁻¹ = 137.1(1)`, `α_sol ℏc = 1.4387 MeV·fm` (corpus #20)** |

Note on the pair run: same-charge and opposite-charge configurations bracket the sign of the force (repulsion / attraction, the Faber mechanism); box-size + separation scans control the finite-volume tail.

Artifacts: `scripts/m7_6_observables.py` + `data/m7_6_*.npz` + `plots/m7_6_*.png` (observables table, `E(d)` curves, α_sol fit).

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (M7.6) · background [`../m7_background.md`](../m7_background.md) (§ 3 Fleury constraints, § 5d units) · Q3 in [`../m7_question_tracker.md`](../m7_question_tracker.md) · upstream [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md) + [`m7_5_clock_stability.md`](m7_5_clock_stability.md) · milestone [`../m7_roadmap.md`](../m7_roadmap.md) M7.7 (consolidation + MODELS.md column).
