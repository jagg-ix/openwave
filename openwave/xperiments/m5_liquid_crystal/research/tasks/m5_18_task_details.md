# M5.18: 4D Lagrangian verification + the universal spectral potential

> Task **M5.18** (M5 / Liquid-Crystal model). Status: **Backlog** (opened 2026-07-05, ready to go) · Gates: **[M5.12](m5_12_task_details.md)** (runs on the new potential) · Roadmap: [`../m5_roadmap.md`](../m5_roadmap.md) · Origin: Duda's 2026-07-05 second reply ([`m5_17_convo.md`](m5_17_convo.md) entry 2)

This doc is the task's full record: planning + findings + documentation.

---

## TASK PLANNING

### Why this task exists (the origin, so we remember what we're doing)

Duda's 2026-07-05 12:24 reply ([`m5_17_convo.md`](m5_17_convo.md) entry 2) delivered three things at once:

1. A practical ANSWER to Q15: the universal spectral potential `V(M) = Σ_p (Tr(M^p) − c_p)²`, `c_p = Σ_i Λ_i^p`, target spectrum `(1, δ, 0)` in 3D and `(g, 1, δ, 0)` in 4D. It supersedes the quartic LdG `(a,b,c)` instrument the M5.16/M5.17 statics ran on.
2. The explicit 4D Lorentz-invariant Lagrangian (`L = −Σ F_{μναβ}F^{μναβ} − V(M)`, `[A,B] = AηB − BηA`, η-raising everywhere including the Frobenius norm) WITH a delegation addressed to this agent by name: "maybe Fable5 could verify that this Lagrangian is Lorentz-invariant, and derived from it Hamiltonian is right (by Legendre transform)? I think it is, but **nobody else has checked it. Should be used if it is right**."
3. Two back-questions about the M5.17 two-charge diagram (does "fixed ansatz" mean no optimization; is the energy finite only on the lattice) that need an answer in the next email.

The adopted recommendation (2026-07-05 session, verbatim): "open this as M5.18 (title along the lines of '4D Lagrangian verification + the universal spectral potential'), gate M5.12 on it, and fold the fixed-ansatz answer into the next email together with the verification result, so the reply carries a deliverable rather than just an answer."

### Scope (three phases)

| Phase | What | Gate (pre-registered) |
| --- | --- | --- |
| **A: the verification** (owner-requested, analytic) | Prove or refute: (A1) the 4D Lagrangian is Lorentz-invariant with the η-signature insertions (index shifts, Frobenius norm, `[A,B] = AηB − BηA`); (A2) his Hamiltonian `H = Σ_{0≤μ<ν≤3} F_{μναβ}F_{μν}^{αβ} + V` follows by Legendre transform, treating the field-dependent (possibly degenerate) kinetic quadratic form honestly: constraint structure, not just the naive sign flip; (A3) characterize boundedness: the internal-η contraction makes H INDEFINITE (his own blue-boxed `−Σ_α (F_{μνα0})²` terms); state precisely when/whether energy is bounded below. First-pass check already done (session note in [`m5_17_convo.md`](m5_17_convo.md) entry 2 § 3 item 3): the naive Legendre DOES reproduce his H; the careful derivation is the deliverable | A method-note-grade derivation doc, every step checkable by reading; verdict stated as ✅ holds / ❌ fails with the exact failing term; independent second-agent audit before sending (the multi-agent rule, [`m5_4h_convo_2026.07.03.md § 6`](m5_4h_convo_2026.07.03.md)) |
| **B: the potential swap** (numerical) | Implement `V(M) = Σ_p (Tr(M^p) − c_p)²` (3D statics first: target `(1, δ, 0)`, p = 1..3) alongside the quartic LdG in [`../scripts/m5_17_energy.py`](../scripts/m5_17_energy.py); re-run the FULL M5.16 gate suite on the new potential (the calibrated-instrument rule: any functional change re-runs the gates first); re-calibrate the m_e scale anchor (the `c2 = αħc/64π` Coulomb lock is curvature-side, potential-independent, and carries over); re-measure `r_half` (now with the β slot dissolved: fewer free parameters than the −4.8% LdG prediction had); re-measure the MELT COST `V(0) = Σ_p c_p²` and re-run the M5.17 melt-channel analysis (hedgehog perturbed relax + two-charge relax both signs) | Gate suite green on the new potential; the melt-channel verdict is the headline: does the channel CLOSE (hedgehog stops escaping, antipair stops annihilating through melt bridges)? Either answer is publishable to him; this is the empirical Q14 test |
| **C: the reply email** (Rodrigo's voice; agent supplies content bullets only) | Fold into ONE email: the phase-A verification verdict (with the derivation doc linked, method-note standard), the phase-B outcome (gate suite + melt channel on HIS potential), and the answer to his fixed-ansatz back-questions (fixed = no optimization, the relaxed curves are the other panel; energy finite in the continuum too because the melt core `s(r)` regularizes the center, plus the cell-centered grid never samples the singular point) | The reply carries a deliverable, not just an answer; method-note standard applies (equations first, commit-pinned permalinks) |

### Definition of done

| Item | Done when |
| --- | --- |
| Phase A | Derivation doc written (`../findings/m5_18_verification_note.md`), verdict explicit, second-agent audit passed |
| Phase B | New-potential module + gate-suite JSON + melt-channel numbers + plots in the repo, `m5_17_energy.py`-style auditability (the physics stays in ONE module) |
| Phase C | Content bullets handed to Rodrigo for the email; the email is HIS voice (Scientific bucket) |
| Tracking | Q15 detail updated with the phase-B empirical outcome; Q14 detail updated with the melt-channel verdict; roadmap row moved to Done on approved review |

### What this task does NOT do

| Out of scope | Where it lives |
| --- | --- |
| The 4D DYNAMIC implementation (ξ-commutator kernel, live time axis, clock) | M5.12 phase D (this task only verifies the math it will run on) |
| The chiral term (Q13) | still pending Duda's "will study further" |
| The g value + overall-scale anchors | Q17, next ask round |
| Neutrino loops | M5.12 (gated on this task) |

### Preconditions + inherited rules

| Rule | Source |
| --- | --- |
| Calibrated-instrument rule: any functional change re-runs the M5.16 gate suite before new physics | [`m5_12_task_details.md § Rigor compliance`](m5_12_task_details.md) |
| Method-note standard for anything owner-facing | [`../../../../dev_docs/METHOD_NOTE.md`](../../../../dev_docs/METHOD_NOTE.md) |
| Multi-agent verification of headline claims | Duda 2026-07-03b, [`m5_4h_convo_2026.07.03.md § 6`](m5_4h_convo_2026.07.03.md) |
| Headless + matplotlib only; physics in one auditable module | M5.16/M5.17 pattern |

### Cross-links

- Origin exchange: [`m5_17_convo.md`](m5_17_convo.md) entry 2 (2026-07-05, the universal potential + the Fable5 ask)
- Supersedes as instrument: the quartic LdG lock of [`m5_16_task_details.md`](m5_16_task_details.md) (its record stays valid AS the LdG-potential result)
- Consumer: [`m5_12_task_details.md`](m5_12_task_details.md) (gated on this task; its § 2026-07-05 spec updates carry the same 4D specs)
- Question registry: [`../m5_question_tracker.md`](../m5_question_tracker.md) (Q15 answered-with-residual; Q14 empirical test = phase B; Q17 restructured)
- The audited module phase B extends: [`../scripts/m5_17_energy.py`](../scripts/m5_17_energy.py) + [`../findings/m5_17_methods_note.md`](../findings/m5_17_methods_note.md)
