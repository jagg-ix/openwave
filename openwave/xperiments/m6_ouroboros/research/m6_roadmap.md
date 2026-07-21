# M6 / OUROBOROS, ROADMAP (the refresh era)

> **Refresh baseline (2026-07-20).** The M6 program restarts against the author's current corpus. The archive era (sandbox v1-v11, the "permanent hold" verdict) validated the two-vector May 2026 Lagrangian and is closed, preserved read-only in [`archive/`](archive/) (its roadmap: [`archive/0b_M6_roadmap.md`](archive/0b_M6_roadmap.md)). The refresh corpus is the full latest-version Zenodo record set ([`../theory/_CITATIONS.md`](../theory/_CITATIONS.md), 29 records, harvested 2026-07-20); the specs of record and the provenance ledger live in [`m6_theory_canonical.md`](m6_theory_canonical.md) (FIRST READ).
>
> **THE PRE-ANALYSIS DECISION (2026-07-20, user-approved).** The full-corpus read split the theory in two, and the program scope follows the split. The frozen two-vector v11 spec (Zenodo 20357670) is a real, well-posed model: our archive validated its neutral sector, and M7 carries it in 3D. The July trajectory (+Eli → +Eli+Fable v4 → the correspondence-only v5) is NOT a stable validation target: three versions in 18 days, the particle sector silently abandoned in v4, fit-machinery and cannot-fail tests documented in the canonical § 4 ledger. **Scope therefore = CLOSE THE LEDGER ON THE FROZEN v11 SPEC, not track the moving theory.** [M6.2](m6_roadmap.md) is the DECISION GATE: if the electron benchmark survives a pre-registered no-search derivation, the electron sector is re-earned and the program continues (M6.3/M6.4); if it does not, the ledger closes honestly, MODELS.md is updated, and M6 returns to hold with the DM sector and the M7 lineage as its durable legacy. The July-era fitting programs are PARKED below with a named reopening condition.
>
> **What the program is for.** Grade the M6 column of [`MODELS.md`](../../../../MODELS.md) (21 criteria; today 4 ✅ / 5 ⚠️ / 12 🚧, all archive-era) and the particle-hunt scorecards ([`m6_particle_hunt.md`](m6_particle_hunt.md)) at M5-series rigor: pre-registered gates and conventions BEFORE each run, adversarial audit of every substantive claim, method notes per [`dev_docs/METHOD_NOTE.md`](../../../../dev_docs/METHOD_NOTE.md), honest negatives as results. Cells may move in BOTH directions; a downgrade is a deliverable.
>
> **Standing rules (from the canonical § 6):** version-pin every result to a Zenodo record id; no calibrated conventions (derive and pre-register, or record as a fit with its search space); tautology-screen every test suite; papers are the citable layer, the local thread corpus is context only; outbound to the author is user-gated. Task workflow: each task gets `tasks/m6_<id>_task_details.md`, scripts/data/plots under `research/` with `m6_<id>_` prefixes, roadmap row moves In Progress → Done at user-approved REVIEW; newly done rows APPEND at the END of DONE.

---

## IN PROGRESS

| TaskID | Title | Description | Gated By |
| --- | --- | --- | --- |
| [M6.2](tasks/m6_2_task_details.md) | THE DECISION GATE: H/Q under pre-registered conventions | The electron benchmark carries the corpus's heaviest provenance defects (canonical § 4: target drift, variant-search reproduction, the author's own July 8 window-defined downgrade). Re-derive H/Q from the frozen v11 spec with EVERY convention fixed in advance: the Q_CS normalization DERIVED (not selected to match), the H functional stated term-by-term, the ansatz pinned to the papers' production form, the quartic term's inclusion decided by derivation, NO search. Report the number against both candidate targets (physical 1.6875; model-internal 1.6969). **Branch (a), survives**: the electron cell is re-earned, M6.3/M6.4 proceed. **Branch (b), fails**: the electron sector is closed honestly (MODELS.md + briefing + hunt synced), and M6 returns to hold with the DM sector + M7 lineage as the durable record; only M6.4 remains optionally live. Cross-check either way: the M7 full-3D window-defined measurement (4.7e-5 code-to-code). Pre-registration target: [convention sheet § 4](m6_1_v11_convention_sheet.md) | M6.1 ✅ + user "go" ✅ 2026-07-20 |

## BACKLOG (the active, decidable core: frozen-spec work)

| TaskID | Title | Description | Gated By |
| --- | --- | --- | --- |
| M6.4 | The stability census rerun + the ω-selection hunt | Valuable on EITHER M6.2 branch (a clean bound is publishable). (a) Rerun `chaoiton_gf_verification.py` (Zenodo 20866581 v2, the corpus's most reproducible artifact): reconcile the 62 vs 319 vs 62 count, reconcile the Lean-vs-integrated ODE mismatch, extend Gelfand-Fomin beyond radial perturbations (the admitted gap). (b) The ω-selection question (canonical OQ3, open since the archive era): scan for ANY discreteness mechanism in the frozen term set; a clean negative bounds the lepton-spectrum claims and decides whether the μ/τ rows are physics or curve-labeling. | M6.1 ✅ + user "go" (independent of the M6.2 branch) |

## PARKED (the July-era moving target; reopening condition named)

> **Reopening condition:** the author freezes a spec (a single record declared canonical, equations complete including C[φ], stable across ≥ 1 month) OR a task below is explicitly pulled forward by user decision. Rationale: three theory versions in 18 days mean any verdict risks obsolescence on arrival, and the record shows corrections get absorbed without stabilizing the target (canonical § 4; provenance notes, local).

| TaskID | Title | Description | Reopen note |
| --- | --- | --- | --- |
| M6.3 | Charge quantization in-platform: Q_CS on a converged chaoiton | The MODELS.md charge cell is ⚠️ (Lean artifacts statement-level, existence `sorry`-discharged, formalized-vs-integrated ODE mismatch; proof static-only vs time-periodic solutions). Compute the mutual Chern-Simons linking number numerically on the M6.2 converged profile: integer? deformation-invariant? Target: ⚠️ → ✅ or the honest negative. | M6.2 branch (a) + user "go" |
| M6.5 | The nuclear-sector suite, rebuilt honestly | v4's six-domain A-linear case (DAMA, thermal neutron, A-scaling, NIF residuals, Sawada, global constraints) with named datasets, stated metrics, pre-registered pass/fail, train/test hygiene, tautology screen; includes checking the g_J = 0.0054 extraction against the Sawada source data and reconciling the three Sawada redefinitions + the DAMA reversal | parked: entirely July-era, spec-dependent |
| M6.6 | The DM sector under the current spec | (a) Re-derive the neutral-sector chain under v4 (m_φ = 0.460 MeV as fundamental): what survives of the parameter-free m_J, β(r), and the dipole-suppression chain (the \|F_dipole\|⁴ independence is asserted, not derived). (b) Execute P1-P3 of our adversarial solar-wind review ([`ai_analysis/2026-07-11_1630_dm_solar_wind_review.md`](ai_analysis/2026-07-11_1630_dm_solar_wind_review.md)): solar-vs-sidereal splitting, raw L1 rerun, synthetic controls | parked; NOTE: arm (b) is a DATA claim on public data, spec-independent, and can be pulled forward alone on user call |
| M6.7 | The two-theories fork: v4 vs the two-vector spec | Characterize what is lost if v4 supersedes the two-vector theory vs what it must reduce to as an effective description; produces the decision-grade question set for the author (canonical OQ1/OQ2/OQ5) | OPTIONAL: run only if continued engagement with the author is wanted; otherwise the fork answers itself by parking |

## STATUS AT A GLANCE (2026-07-20)

| Question | Answer |
| --- | --- |
| Where is M6? | REFRESHED from "permanent hold" and RE-SCOPED same day (pre-analysis, user-approved): close the ledger on the frozen v11 spec; do not chase the July-era moving target. Active core = M6.1 ✅ (2026-07-20, the certified convention sheet) → M6.2 (decision gate, NEXT) → M6.3/M6.4; July-era programs parked with a named reopening condition |
| Why the re-scope? | The corpus read found the July trajectory (+Eli → v4 → v5) carrying a strong drift signature: version churn faster than any validation cycle, the particle sector silently dropped in v4, fitted conventions, cannot-fail tests (canonical § 4). The frozen two-vector spec is the real, decidable object |
| What decides the program? | M6.2: the pre-registered no-search H/Q derivation. Both branches are deliverables: re-earned electron sector, or an honest close with M6 returning to hold on the strength of its DM sector + the M7 lineage |
| Relation to M7 | M7 HydroBoros carries the two-vector Lagrangian in full 3D and owns that program; M6 owns the frozen-spec ledger + the provenance-hardened grading of the published record |
| Rigor bar | M5-series: pre-registered gates, adversarial audits, method notes, honest negatives as results; canonical § 6 consumption rules standing |

## DONE (refresh era)

> Newly done tasks APPEND at the end. The archive-era validated record (sandbox v1-v11, gates G1+, the DM-paper supplement) stays in [`archive/`](archive/), read-only; do not conflate the two eras.

| TaskID | Title | Description | Completed |
| --- | --- | --- | --- |
| (setup) | The 2026-07-20 refresh setup | Corpus harvested (29 latest-version Zenodo records + local context corpus, manifest [`../theory/_CITATIONS.md`](../theory/_CITATIONS.md)); full corpus read digested; [`m6_theory_canonical.md`](m6_theory_canonical.md) + [`m6_particle_hunt.md`](m6_particle_hunt.md) + [`../__M6_model_briefing.md`](../__M6_model_briefing.md) refresh + this roadmap written | 2026-07-20 |
| (pre-analysis) | The scope decision: frozen-spec ledger, not the moving target | Corpus-wide drift assessment presented and user-approved: active core = M6.1/M6.2 (decision gate)/M6.3/M6.4 against the frozen v11 spec; M6.5/M6.6 parked with the reopening condition; M6.7 optional. Evidence base: canonical § 4 ledger + the local provenance notes | 2026-07-20 |
| [M6.1](tasks/m6_1_task_details.md) | The spec certification gate | v11 certified: [`m6_1_v11_convention_sheet.md`](m6_1_v11_convention_sheet.md) (FIXED-vs-GAP pre-registration checklist; ℒ_ref reconstruction; targets pinned) + v4 characterized script-backed (EL unclosable, boundedness verified, A-linearity generic). Four print-level v11 defects added to canonical § 4; OQ6 resolved. Adversarial audit 9/10 CONFIRMED + 1 PARTIAL, auditor findings AF1/AF2 recorded. [Method note](m6_1_method_note.md) | 2026-07-20 |
