# M7.5, validate the clock in real time + stability

> Task **M7.5** (M7 / HydroBoros). taskID = M7.N iteration. Status: **Backlog** · Roadmap: [`../m7_roadmap.md`](../m7_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation. **Repositioned 2026-07-02**: in the time-harmonic frame the de Broglie clock is IN the soliton from M7.1 (the fixed-ω minimization, [`../m7_background.md § 5a`](../m7_background.md)); this task does not "add" a clock, it **validates the harmonic reduction against real-time dynamics** and establishes stability.

---

## Plan

| Step | What | Gate |
| --- | --- | --- |
| 1 | evolve the relaxed M7.3/M7.4 states with the **constrained Minkowski leapfrog** (full time-dependent EOM, no harmonic assumption) | energy conserved to integrator tolerance over the run |
| 2 | **clock validation**: measure the emergent oscillation frequency from the evolution | matches the input harmonic `ω` (the reduction is self-consistent); reported vs Dirac `ω_D` |
| 3 | **stability**: long runs (many periods), perturbation kicks (amplitude + shape) | persists, no collapse / expansion mode; perturbations ring down or orbit |
| 4 | **`β*` threshold probe** (Werbos v5 Test 1, corpus #10): drive small-amplitude fluctuations below / above the nonlinear coupling threshold | sub-threshold fluctuations behave linear-Maxwell (vacuum stability); the threshold located, if it exists in this sector |
| 5 | energy-minimizing-clock check (the M5.8 mechanism, Duda's prescription in the [roadmap](../m7_roadmap.md) Phase A note): scan `E_ω(ω)` around the soliton | the soliton's ω sits at the energy minimum of the scan |

Honest outcomes: a drift between the emergent and input ω quantifies the harmonic reduction's error (report it, do not hide it); an instability found here invalidates the M7.4 state and sends it back with the measured unstable mode.

Artifacts: `scripts/m7_5_clock_stability.py` + `data/m7_5_*.npz` + `plots/m7_5_*.png` (ω spectrogram, energy trace, perturbation response, `E_ω(ω)` scan).

---

Cross-refs: roadmap [`../m7_roadmap.md`](../m7_roadmap.md) (M7.5) · background [`../m7_background.md`](../m7_background.md) (§ 5a frame, § 5c leapfrog) · Q9 (the v5 `β*` context) in [`../m7_question_tracker.md`](../m7_question_tracker.md) · upstream [`m7_4_charged_soliton.md`](m7_4_charged_soliton.md) · downstream [`m7_6_observables.md`](m7_6_observables.md).
