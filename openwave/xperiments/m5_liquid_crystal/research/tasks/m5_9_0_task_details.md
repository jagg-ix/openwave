# M5.9.0: Duda delta/g calibration + unit-scale prep

> Task **M5.9.0** (M5 / Liquid-Crystal model). Status: **Backlog** · Gated by: - · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

This doc is the task's full record: planning + findings + future planning + documentation.

---

## Current detail (from the roadmap, 2026-07-02 migration)

DONE: seed-level δ/g energy scaling + the EM/GEM boost split (06-09 addendum, `2q` Phase D/E). Residual: (a) the δ (quantum-phase) sector is DYNAMICAL (the fast ~10²¹ Hz clock), not captured by the static split, so weighing it needs the ω-dynamics; (b) the direct ω(δ) on the SETTLED state (the `2h` run_dense path, not the fresh-seed `2q_omega` scaffold); (c) the real calibration axis (fix units via Coulomb + tune LdG to rest energy), folding into NG-1/NG-3

## Duda 2026-07-01 — the real-calibration axis routes through M5.16

Duda ([`m5_4e_convo_2026.07.01.md`](m5_4e_convo_2026.07.01.md)) restated the calibration order: **the first step is establishing `g`, `δ`** ("seems we still don't know"), with δ from the QED Lagrangian, Coulomb as a second anchor, `g` from the electron clock / neutrino oscillations / else baryon gravitational mass ("certain of only for baryons"). His method for it is a **static energy-minimization** run at the physical regime with a regularizing potential, under cylindrical symmetry.

That method is now its own task, [`m5_16_task_details.md`](m5_16_task_details.md) (graduating the M5.11-P0 minimizer to the physical `g~1e10, δ~1e-10` regime). **Residual (c) above — the real calibration axis — is delivered by M5.16**: this task (M5.9.0) consumes M5.16's locked `(g, δ, V-coeffs)` to weigh the δ/g sectors at the physical scale, rather than the seed-level `2q` proxy. See [`../m5_summary_report.md`](../m5_summary_report.md) (DUDA follow-up) for the prior δ/g findings.
