# M5.17: The Duda-legible methods surface + the two-charge Coulomb anchor

> Task **M5.17** (M5 / Liquid-Crystal model). Status: **Backlog, ⭐ next run** · Gated by: nothing (consumes the closed M5.16; unblocks the M5.12 comms path) · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

This doc is the task's full record: planning + findings + documentation.

---

## TASK PLANNING

## Origin: the 2026-07-03 audit event

Duda's reply to the M5.16 report ([`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md)): he read the Python, could not find the potential or the Hamiltonian, and concluded "still I have no idea what does it calculate", answering none of the five ask-round questions. Diagnosis (agreed 2026-07-03): a **legibility failure of the verification surface, not a correctness failure**. His restated prescription largely matches what M5.16 implemented; he could not see that it was done. This task is the first application of the repo-wide **method report** standard the incident produced: [`dev_docs/METHOD_REPORT.md`](../../../../../dev_docs/METHOD_REPORT.md).

## What failed vs what stands (do not over-rebuild)

| Item | Verdict |
| --- | --- |
| The M5.16 physics content: equivariant (ρ,z) reduction, 7 gates, analytic gradient, anchor chain, r_half headline, δ-grading, saddle finding | STANDS (unaudited, not refuted); reused as-is, its gates become the refactor's acceptance tests |
| The verification surface: functional buried in a ~1000-line script docstring; the report's inspection list led with a physics-free driver; results before methods | FAILED the audit; replaced by phases A + B below |
| The single-hedgehog far-field Coulomb anchor (`c₂ = αħc/64π` from the self-energy match) | SUPERSEDED as the Coulomb leg by Duda's two-charge prescription (phase C tests whether the analytic lock survives it) |
| The 3D rendered production-solver route | PARKED (decision 2026-07-03): an author-side control loop, not an audit surface; revisit only if this task's route also fails to land |

## The phased plan

| Phase | What | Gate (pre-registered) |
| --- | --- | --- |
| **A / functional extraction** | Extract the physics into a small single-purpose module `m5_17_energy.py` (~200 lines): the functional `U = c₂·4·Σ_{μ<ν}‖[∂_μM, ∂_νM]‖² + V_M`, the LdG potential `V_M = a·Tr(Msp²) − b·Tr(Msp³) + c·(Tr Msp²)²` with the anchor-locked coefficients, the equivariant azimuthal channel, the observable definitions (r_half, virial). Docstring = the same equations as the methods note. `m5_16_axisym.py` (or a thin `m5_17_axisym.py` fork) imports it; drivers never re-implement physics | the full M5.16 gate suite G1-G8 re-runs GREEN on the refactored stack, energies bit-identical to the frozen M5.16 JSONs (calibrated-instrument rule) |
| **B / methods note** | Write `../findings/m5_17_methods_note.md` (created by this task): equations FIRST (Lagrangian/free-energy density, `V_M` explicit, ansatz + boundary conditions, discretization, minimizer, every observable's definition), then the **equation-to-code map**: each term → function → `file.py:line` → commit-pinned GitHub permalink (`#L` anchors), then the results (each next to its gate), then the not-computed list (clock frequency, angular momentum, magnetic dipole, dynamics) in his vocabulary | passes the [`METHOD_REPORT.md`](../../../../../dev_docs/METHOD_REPORT.md) pre-send checklist: `V_M` and the Hamiltonian findable from the note in ONE click; physics-first inspection set ≤ 4 artifacts, module first, driver last |
| **C / two-charge Coulomb anchor** (his prescription, verbatim: "two such charges in various distances") | Seed TWO hedgehogs on the z-axis at separations d (axisymmetry preserved, the existing instrument runs it); relax; measure the interaction energy `E_int(d) = E(d) − 2·E_single`. Large d: fit `E_int ∝ 1/d` and extract the effective coupling → cross-check against the analytic `c₂ = αħc/64π` lock. Small d (fm scale): report the running-coupling curve (his bonus prediction: "should bring some details of potential") | large-d 1/d tail fit quality reported with h-evidence; the extracted coupling vs the analytic lock agreement quantified (pass = consistent within the discretization error; a genuine gap is ALSO a first-class result, reported as such); the running curve reported either way |
| **D / Fig. 9 ansatz conformance** | Check the hedgehog seed against the biaxial-nematic hedgehog of **Fig. 9, arXiv:2108.07896** (his named starting point); document match / mismatch component by component | a conformance table in the methods note (his figure's texture vs our seed), no silent assumption |
| **E / observables gap routing** (doc work) | Log his 4-observable electron bar (mass + clock frequency + angular momentum + magnetic dipole; 3 of 4 dynamical) into the M5.12 phase-D spec and the M5.9 planning, wiring the EID-B/EID-C heritage (μ via the tilt channel; J = Noether clock charge) as the starting points | the routing recorded in [`m5_12_task_details.md`](m5_12_task_details.md) + [`m5_9_task_details.md`](m5_9_task_details.md) |

## Explicit non-goals

| Not in scope | Why |
| --- | --- |
| 3D rendering / production-solver rebuild | parked 2026-07-03 ([`m5_4h_convo_2026.07.03.md § 5`](m5_4h_convo_2026.07.03.md)) |
| Ground-zero rewrite of the M5.16 solver | the physics stands; the surface is what changes (phase A gate = bit-identical energies) |
| Re-sending the ask round before the methods note lands | the re-ask (Q13/Q14/Q15 + the banked Q16 partial) rides the next email, WITH the note |
| The dynamical observables themselves (clock ω, J, μ on the calibrated electron) | routed (phase E), executed in M5.12 phase D / M5.9 |

## Comms plan (the next email)

One email after FINISH: leads with the **methods note link** (equations page first, not results), one short paragraph on the two-charge Coulomb result (his own prescription, run), the Fig. 9 conformance line, then re-references Q13 / Q14 / Q15 (+ notes we banked his Q16 partial answer: single rotated vortex loop first). Short; everything auditable sits behind the note's links.

## Rigor compliance

Inherits the full M5.16 bar ([`m5_16_task_details.md § Rigor compliance`](m5_16_task_details.md)) + the [`METHOD_REPORT.md`](../../../../../dev_docs/METHOD_REPORT.md) checklist (this task is its first application). Phase-A rule restated: ANY change to the functional's code re-runs the M5.16 gate suite before any new number is produced.

## Definition of done

(1) The functional lives in a small auditable module, gates green, energies bit-identical; (2) the methods note passes the METHOD_REPORT checklist; (3) the two-charge `E_int(d)` curve exists with the large-d coupling cross-check quantified and the fm-scale running curve reported; (4) the Fig. 9 conformance table exists; (5) the 4-observable bar is routed into M5.12/M5.9; (6) the next Duda email is drafted (methods-note-first shape).

## Cross-links

- Origin event: [`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md) · the standard: [`dev_docs/METHOD_REPORT.md`](../../../../../dev_docs/METHOD_REPORT.md)
- Consumes: [`m5_16_task_details.md`](m5_16_task_details.md) (instrument, gates, lock, § POST-DELIVERY AUDIT) · report to be superseded-in-part: [`../findings/m5_16_report.md`](../findings/m5_16_report.md)
- Feeds: [`m5_12_task_details.md`](m5_12_task_details.md) (comms gate + phase-D spec) · [`m5_9_task_details.md`](m5_9_task_details.md) (observables routing) · [`../m5_question_tracker.md`](../m5_question_tracker.md) (Q13/Q14/Q15 re-ask, Q16 partial)
- Roadmap row: [`m5_roadmap.md § BACKLOG`](../m5_roadmap.md)
