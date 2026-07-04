# M5.17: The Duda-legible methods surface + the two-charge Coulomb anchor

> Task **M5.17** (M5 / Liquid-Crystal model). Status: **Backlog, ⭐ next run** · Gated by: nothing (consumes the closed M5.16; unblocks the M5.12 comms path) · Roadmap: [`m5_roadmap.md`](../m5_roadmap.md)

This doc is the task's full record: planning + findings + documentation.

---

## TASK PLANNING

## Origin: the 2026-07-03 audit event

Duda's reply to the M5.16 report ([`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md)): he read the Python, could not find the potential or the Hamiltonian, and concluded "still I have no idea what does it calculate", answering none of the five ask-round questions. Diagnosis (agreed 2026-07-03): a **legibility failure of the verification surface, not a correctness failure**. His restated prescription largely matches what M5.16 implemented; he could not see that it was done. This task is the first application of the repo-wide **method note** standard the incident produced: [`dev_docs/METHOD_NOTE.md`](../../../../../dev_docs/METHOD_NOTE.md).

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
| **B / methods note** | Write `../findings/m5_17_methods_note.md` (created by this task): equations FIRST (Lagrangian/free-energy density, `V_M` explicit, ansatz + boundary conditions, discretization, minimizer, every observable's definition), then the **equation-to-code map**: each term → function → `file.py:line` → commit-pinned GitHub permalink (`#L` anchors), then the results (each next to its gate), then the not-computed list (clock frequency, angular momentum, magnetic dipole, dynamics) in his vocabulary | passes the [`METHOD_NOTE.md`](../../../../../dev_docs/METHOD_NOTE.md) pre-send checklist: `V_M` and the Hamiltonian findable from the note in ONE click; physics-first inspection set ≤ 4 artifacts, module first, driver last |
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

Inherits the full M5.16 bar ([`m5_16_task_details.md § Rigor compliance`](m5_16_task_details.md)) + the [`METHOD_NOTE.md`](../../../../../dev_docs/METHOD_NOTE.md) checklist (this task is its first application). Phase-A rule restated: ANY change to the functional's code re-runs the M5.16 gate suite before any new number is produced.

## Definition of done

(1) The functional lives in a small auditable module, gates green, energies bit-identical; (2) the methods note passes the METHOD_NOTE checklist; (3) the two-charge `E_int(d)` curve exists with the large-d coupling cross-check quantified and the fm-scale running curve reported; (4) the Fig. 9 conformance table exists; (5) the 4-observable bar is routed into M5.12/M5.9; (6) the next Duda email is drafted (methods-note-first shape).

---

## FINDINGS (2026-07-03 run)

Run record: go 20:16 EDT; in-flight state in [`../checkpoints/m5_17_progress.md`](../checkpoints/m5_17_progress.md). All artifacts `m5_17_*` under [`../scripts/`](../scripts/), [`../data/`](../data/), [`../plots/`](../plots/), [`../findings/`](../findings/).

### Phase A: the functional extracted, gates green, energies bit-identical

[`../scripts/m5_17_energy.py`](../scripts/m5_17_energy.py) (~240 lines) now carries THE physics: functional, LdG potential + `ldg_coeffs`, analytic gradient, `ext_tail`, seeds, with the equations in the docstring. `m5_16_axisym.py` became a pure driver importing it (CLI, Taichi cross-check, minimizers, observables, gates, modes). Acceptance evidence:

| Check | Result |
| --- | --- |
| Bit-identity harness (9 checksums: energies, gradient sums/norm, densities, tail, coefficients, on 2 deterministic fields) | 9/9 EXACT equality pre/post refactor |
| The M5.16 gate suite G2-G8 re-run on the refactored stack | 7/7 PASS, every reported number IDENTICAL to the frozen 2026-07-02 values (`m5_16_axisym_gates.json`) |

### Phase B: the methods note (the audit page)

[`../findings/m5_17_methods_note.md`](../findings/m5_17_methods_note.md): equations first (§ 1 convention, § 2 functional, § 3 vacuum structure, § 4 exact axisymmetric reduction, § 5 discretization + analytic-gradient adjoints + minimizers, § 6 anchors + observable definitions), then § 7 THE EQUATION-TO-CODE MAP (15 rows: equation → function → `file.py:line` → GitHub URL; anchors verified against the code), § 8 the two-charge configuration + prediction, § 9 Fig. 9 conformance, § 10 the not-computed list. METHOD_NOTE checklist: `V(M)` and the Hamiltonian findable in ONE click ✅; equations before results ✅; inspection set ≤ 4, physics-first (module → note → lock JSON → plot) ✅. ⚠️ Links point at `blob/main`; swap to commit-pinned permalinks when the merge commit exists (one `sed`, flagged for the email draft).

### Phase C: the two-charge Coulomb run (his prescription, executed)

Instrument: [`../scripts/m5_17_two_charge.py`](../scripts/m5_17_two_charge.py) (imports the module; gate C0: the ansatz reduces to the single melted hedgehog exactly, 4.4e-16). Potential = the LOCKED β = 1 calibration, autochi OFF (the run TESTS the lock, it must not retune it). Prediction under the M5.16 lock: `E_int(d) = q2·64π·c2/d` (grid form of `±αħc/d`), i.e. `|A| = 64π ≈ 201.1`.

| Measurement | Result | Verdict |
| --- | --- | --- |
| LIKEPAIR (q2 = +1, total degree 2, topologically protected), fixed ansatz, fit d ≥ 16 | `A = +215.9` (rms 0.23; `+234.6` at 128×256 with d ≥ 20: box-tail drift band) | **ratio to +64π: 1.07-1.17** ✅ sign + magnitude consistent with the Coulomb lock at the ansatz level |
| LIKEPAIR, pinned-core relaxed (3000 iters) | **NOT an equilibrium**: gradient norm RISES (−0.5 decades), E drops 16-20 per point, melt line forms along the axis (`melt_min ≈ 0.008`), E(d) non-monotonic: the pair restructures through the melt channel (degree 2 is conserved, so no annihilation, but the two-defect texture is not stationary). The fit on these transients (`A = +152`, ratio 0.76) is NOT an anchor number | ⚠️ protocol finding: a relaxed anchor needs a topology/melt-preserving constrained method (routed below) |
| ANTIPAIR (q2 = −1), fixed ansatz | `A = −422.6`, ratio 2.10, stable across grid/box/fit-window | ⚠️ ansatz-level only (the superposition is not a solution); superseded by the relax finding below |
| ANTIPAIR, full relax with 2.5h pinned disks | **ANNIHILATES**: E collapses to the vacuum residual (0.30-0.59) at every d via a melt bridge along the axis (`melt_min ≈ 0.008` over the whole strip) | ✅ measured: the (+1,−1) pair is topologically trivial and unwinds through the melt channel: the static face of the pair-annihilation program ([M5.14](m5_14_task_details.md)); EXCLUDED from the anchor (no equilibrium exists to measure) |
| Running-coupling readout `α_eff(d)/α` | curve reported in `m5_17_two_charge_fixed.json` + the plot, d = 1.0-10.0 fm via ℓ = 0.2495 fm | 🔶 ansatz-level at small d (relaxed curve = the likepair rows) |

![two-charge Coulomb anchor](../plots/m5_17_two_charge.png)

### THE STRUCTURAL FINDING: the melt channel is open by two orders of magnitude

At the LOCKED parameters the melt cost is `c − b/2 = cscale·(1 − β/2) = 1.885e-3` per grid cell, so a unit-radius melt line of length 32 costs ≈ **0.19** grid energy units while the observed escapes release **16-32**: thin melt lines are essentially FREE. One mechanism now explains three independent observations: the M5.16 hedgehog saddle (perturbed relax −35%, melt moves off-origin: Q14), the antipair annihilation (unwinding through a melt bridge), and the likepair restructuring (melt line + non-convergence). Consequence for the theory questions: a Frank-type quadratic term, a sixth-order LdG invariant, or the chiral pair (exactly Q13 / Q14 / Q15) are the terms that would CLOSE this channel; the ask round is now backed by a measured, quantified instability, not just a stability probe. Follow-up routed: a melt-preserving constrained relax (amplitude floor or true topological pinning) for the relaxed anchor number.

### Phase D: Fig. 9 conformance (the prescribed ansatz, checked not assumed)

Fig. 9 of arXiv:2108.07896 (p. 10) read from the paper: `M = O·D·Oᵀ`, spatial `D = diag(1, δ, 0)`, `O = exp(θG_z)·exp(φG_y)·exp(ψG_x)` (radial major axis; ψ = the local twist phase, `Ψ = exp(iψ)` = the clock), NO core regularization in the figure. Conformance table = methods note § 9: our seed is Fig. 9's texture at the uniaxial limit + the melt `s(r)` (which is exactly his "activate potential to avoid singularity" step); the δ-sector textures are the ψ = const slices, graded exactly in M5.16; the DYNAMICAL ψ is the clock sector (M5.12 phase D). Bonus from p. 11, re-surfaced: the paper's own anchor hints `δ² ~ ħc`, `g⁴ ~ ke²/Gm² ≈ 1e38` (feeds Q17; logged in [`m5_9_task_details.md § SPEC UPDATE`](m5_9_task_details.md)).

### Phase E: routing (the 2026-07-03 reply's content wired into its consumers)

The [`m5_4h_convo_2026.07.03.md § 3`](m5_4h_convo_2026.07.03.md) routing-audit table verifies all five items landed: 4-observable electron bar → [`m5_9_task_details.md`](m5_9_task_details.md) + [`m5_12_task_details.md § Ask-round outcome`](m5_12_task_details.md); two-charge method → this task + [`m5_9_0_task_details.md`](m5_9_0_task_details.md); Fig. 9 → methods note § 9 + Q14; vortex-loop-first + PMNS-from-time-derivatives → M5.12; parametrization-search framing → Q15 + methods note § 10.

### Honest caveats

| Caveat | Status |
| --- | --- |
| The likepair fixed-ansatz A sits 7-17% above 64π with the spread dominated by the finite-box charge-2 tail (its far field is degree 2, so the box correction is larger than the single-defect case); the anchor cross-check therefore stands at the ANSATZ level (which is also what "for large [d] we get anchor for Coulomb, uniaxial should suffice" asks for) | quantified by the 96×192 vs 128×256 band |
| NEITHER sign yields a relaxed equilibrium pair at the locked parameters (the melt channel, above): the relaxed-anchor number awaits a melt-preserving constrained method | measured, routed (annihilation physics → M5.14; the channel-closing terms → the ask round) |
| Methods-note links are `blob/main`, not yet commit-pinned (no commit exists) | swap at email time |
| The running-coupling small-d branch is ansatz-level (fixed superposition, not solutions) | labeled in the JSON + plot |

### Artifacts

| Type | Files |
| --- | --- |
| module (THE physics) | [`../scripts/m5_17_energy.py`](../scripts/m5_17_energy.py) |
| scripts | [`../scripts/m5_17_two_charge.py`](../scripts/m5_17_two_charge.py) · [`../scripts/m5_17_plot.py`](../scripts/m5_17_plot.py) · `m5_16_axisym.py` (refactored to driver) |
| methods note | [`../findings/m5_17_methods_note.md`](../findings/m5_17_methods_note.md) |
| data | `m5_17_two_charge_fixed.json` · `m5_17_two_charge_relax_anti.json` · `m5_17_two_charge_relax_like.json` (all < 10 KB; nothing to delete under the 1 MB rule) |
| plot | [`../plots/m5_17_two_charge.png`](../plots/m5_17_two_charge.png) |
| run state | [`../checkpoints/m5_17_progress.md`](../checkpoints/m5_17_progress.md) |

## Cross-links

- Origin event: [`m5_4h_convo_2026.07.03.md`](m5_4h_convo_2026.07.03.md) · the standard: [`dev_docs/METHOD_NOTE.md`](../../../../../dev_docs/METHOD_NOTE.md)
- Consumes: [`m5_16_task_details.md`](m5_16_task_details.md) (instrument, gates, lock, § POST-DELIVERY AUDIT) · report to be superseded-in-part: [`../findings/m5_16_report.md`](../findings/m5_16_report.md)
- Feeds: [`m5_12_task_details.md`](m5_12_task_details.md) (comms gate + phase-D spec) · [`m5_9_task_details.md`](m5_9_task_details.md) (observables routing) · [`../m5_question_tracker.md`](../m5_question_tracker.md) (Q13/Q14/Q15 re-ask, Q16 partial)
- Roadmap row: [`m5_roadmap.md § BACKLOG`](../m5_roadmap.md)
