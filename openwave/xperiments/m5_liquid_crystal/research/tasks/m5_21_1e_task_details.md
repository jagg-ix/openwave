# M5.21.1e: canonical-spec review + implementation-conformance audit (the M5.21.1 retrospective)

**Status**: 🔶 EXECUTED 2026-07-16 (go 13:36 EDT); doc collection (4-way fan-out + first-hand page verification), conformance matrix, three-arm constraint experiment, toy regression, and independent adversarial audit all complete; awaiting REVIEW. Full record: [`../findings/m5_21_1e_spec_review.md`](../findings/m5_21_1e_spec_review.md).

**Lineage**: born at the [M5.21.1](m5_21_1_task_details.md) close (user directive 2026-07-16): before spending more simulation budget on the electron hedgehog, re-derive what the canonical spec IS from ALL sources and audit what our stack actually implements against it. Roadmap row: [`../m5_roadmap.md § IN PROGRESS`](../m5_roadmap.md). Canonical registry consumed + fed: [`../m5_theory_canonical.md`](../m5_theory_canonical.md).

## TASK PLANNING (2026-07-16)

**Scope**: a full re-read of every spec source (Duda's four papers, his email corrections, the Faber papers, the production engine `medium.py`/`engine*.py`, MODELS.md, the archived M5.8-era summary report, the model briefing, and every prior implementation era M5.8 → M5.21.1 in the research folder), then a term-by-term comparison against what M5.21.1 actually ran, an explicit verdict on the user's concern (**are we implementing the 4×4 tensor field in 3D, or a reduction inherited from the 1D/toy model?**), a ranked list of candidate explanations/fixes for the M5.21.1 negatives (non-converging statics, time-mixing saddle, rigid-J kill, roton dip), and a back-to-back run of the highest-leverage machine-checkable candidates.

**Definition of done**:

| # | Criterion |
| --- | --- |
| 1 | Source-by-source spec extraction (paper + page/equation references) for: field content, kinetic term(s), potential form + targets, vacuum, dimensionality, hedgehog ansatz, stability mechanism |
| 2 | Implementation-conformance matrix: spec term × stack era (production engine · M5.8 · M5.16-18 · M5.20/21 verified-L) × verdict (conform / deviates / absent) |
| 3 | Explicit measured/verified answer to "4×4 in 3D vs 1D toy model" |
| 4 | Ranked potential-solutions list for the M5.21.1 negatives, each routed (machine-checkable → run here; author-gated → tracker; nature-gated → roadmap) |
| 5 | Top machine-checkable candidate(s) actually run (scripts + data + plots under `m5_21_1e_*`), gates pre-registered |
| 6 | Findings doc at method-note grade + adversarial audit of any substantive new claim |

**Gating**: M5.21.1 (closed 2026-07-16) + user "go" (given 2026-07-16 13:36 EDT).

**Blindspot pass**: (a) the toy-model papers may be the SOURCE of our V4 trace-target potential: if the full LC papers specify a different functional, the whole verified-L era inherits a toy spec; (b) the production engine may implement terms the research stack dropped (the briefing names a Skyrme kinetic term); (c) Faber's electron is STABLE in his model: his stabilizer (whatever it is) is a direct candidate for our missing containment; (d) prior eras may already have run a full-3D 4×4 stack whose lessons were lost in the sandbox consolidation; (e) his figures/conventions may use a different generator normalization (a silent factor in our Fig. 9 transcription).

**Research body**: this file (`## FINDINGS`), a findings doc `../findings/m5_21_1e_spec_review.md`, scripts/data/plots under `../scripts|data|plots/m5_21_1e_*`.

**Sub-experiments**: decided AFTER the doc collection (the comparison table names them); pre-commitment: only machine-checkable candidates run; anything author-gated goes to the tracker, no ask spent (no Duda checkpoint for now, user 2026-07-16).

**Source list (user-supplied + standing)**:

| Source | What to extract |
| --- | --- |
| `../../theory/liquid_crystal_model.pdf` | the full LC field theory: functional, terms, vacuum, dimensionality |
| `../../theory/liquid_crystal_particles.pdf` (arXiv:2108.07896) | the particle constructions: Fig. 9 hedgehog, KG limit, stability language |
| `../../theory/Time_crystal_toy_model_Wolfram_Community.pdf` + `../../theory/time_crystal_toy_model.pdf` | what the TOY model is (dimensionality, matrix size, potential targets) and which parts of our stack descend from it |
| Faber papers (`../../theory/FaberManfried.pdf`, `../../theory/faber_universe_2025.pdf`) | his model spec + what stabilizes his electron |
| `../../medium.py`, `../../engine*.py` (production) | the production PDE as implemented: field type, dims, terms |
| research folder eras (M5.8 scripts, M5.16-18, M5.20/21, sandbox remnants, `../archive/m5_summary_report.md`) | prior spec choices + any earlier spec review |
| `../../../../MODELS.md`, `../../__M5_model_briefing.md`, `../m5_roadmap.md` legacy sections | claimed-implemented statements to check against the code |
| his 2026-07-13/15 emails ([`m5_20_convo.md`](m5_20_convo.md)) + the M5.18 verification | the freshest author-stated spec |

## FINDINGS (2026-07-16)

Full auditable record (source extraction, conformance matrix, experiments, audit): [`../findings/m5_21_1e_spec_review.md`](../findings/m5_21_1e_spec_review.md). Headlines:

| Question | Answer | Status |
| --- | --- | --- |
| Are we implementing the 4×4 tensor in 3D (not the 1D toy)? | **YES, since M5.8.1**: full-3D 4×4 through the M5.8 era (24³-63³), the EXACT equivariant axisym reduction + full-3D 48³ spot-checks since M5.16 (his own cylindrical prescription), production engine full-3D 4×4 throughout. The 1+1D toy has no matrices and no trace targets to inherit; its one transplant (u + βu²) was retired with the M5.8 stack | ✅ verified (4-way archaeology) |
| Does the implementation conform to the papers? | Kinetic: ✅ (the ξ-commutator 4-index term, M5.18-verified; F = [∂M, ∂M] IS the paper primitive, Eq 15/19-20). Potential: the trace-target V4 is a paper-sanctioned CANDIDATE ("we could use e.g.", FRAME p. 12), adopted via his 2026-07-05 email; the paper's primary 3D form (Eq 12 eigenvalue penalty), LdG, and a possibly-REQUIRED `det(M) = const` volume constraint (flagged TWICE: pp. 8, 12) were never implemented. Paper vacuum branch = our s = −1 (runs used s = +1, 1% lower; anchors sign-robust). Production still runs the pre-4D spec (no η in V, LdG/p=2 well) | ✅ matrix in findings § 3 |
| Why did M5.21.1 P1 fail his stability bar? | **The slide is an amplitude-mode descent through the soft spectral channel**: 97-99.97% of the static force is orthogonal to the isospectral orbit class (tan_frac 0.0003 → 0.054); virial never balanced. The paper ANTICIPATES this escape (p. 8: det-constraint "to prevent using only long axes which allow for low curvature"); Faber's S³ norm constraint closes the same channel in his stable electron. **The stiffness ladder arrests it monotonically: at wscale ×1000 the hedgehog is CONTAINED** (r90 flat from it 1000, coreball 0.93, 3-equal core holds, no u_eta dilution); the physical regime (g ~ 1e10, stiff mode ∝ g³) is effectively harder still. The toy-regime negative is a soft-potential regime artifact, not a property of the physical-parameter model | ✅ measured (§ 5a-5b) |
| Is there a localized hedgehog statics minimum in the exact orbit class? | **NO, and the failure is the OTHER channel**: with the ηM-spectrum pinned exactly (drift ≤ 1.4e-3, V4 frozen), the centered hedgehog's interior depletes (u-coreball 0.53 → 0.095) while the charge survives INTACT at the outer radii (q = +1.00 at r = 35-58, audit's independent read): moved, not unwound. Small-core control migrates FASTER (hatch-size hypothesis killed); boosts decouple exactly (rot3 ≡ full6, audit: ⟨G, t_K⟩ = 0.0). Mechanism (analytic + audit-confirmed scaling law E_u ∝ 1/λ, V4 ∝ λ^3.05): the hard pin freezes the potential = Faber's λ³ compressor, leaving pure quartic curvature that prefers expansion. ⚠️ Audit catch: the iso endpoint carries a stencil-null checkerboard (sawtooth 164 vs 1.07), so its quantitative E_u trajectory is partly artifact; future orbit-class descents need a compact-stencil functional. **Three-arm synthesis: soft = amplitude dilution · hard = frozen-potential expansion · the stable object, if any, lives at the Faber virial balance u = 3V4 at finite size (exactly the class M5.16 measured, 0.3-0.6%)**: the missing piece is the balance, not a bare constraint (findings § 5c-5d) | ✅ measured (audited) |
| Why did rigid rotation fail to give J? | **It was never the spec**: FRAME plans J "hopefully through regularization" (never computed); Faber REJECTS rigid rotation structurally (fixed vacuum at infinity) and locates spin in Π₃ coverings + INTERNAL rotations (the clock). The M5.21.1 P2 kill and the M5.20.5 loop kill CONFORM to both authors | ✅ verified (reframe, no experiment needed) |
| Was the P3 "NOT KG-like" bar right? | The paper's own hedgehog operator is nonstandard (2∂_tt ψ = ((∇−A)² + (Â·∇)²)ψ, FRAME Fig 9): the roton-dip measurement stands, but the conformance label softens to "not plain-KG (his operator differs from plain KG too)" | ✅ documented |
| Toy-model conformance | Closed form + tanh family reproduce his published numbers to 3.4e-7 / 3.2e-6; the in-family clock is propelled (2.126 < 8/3). NEW: the free variational problem under ψ = ωt has NO minimizer (ripple escape below the kink at αω² > 1, cutoff-dependent): his kink numbers are family minima, the 1+1D miniature of the 3+1D amplitude escape | ✅ measured |

### Artifacts

| Type | Files |
| --- | --- |
| Findings | [`../findings/m5_21_1e_spec_review.md`](../findings/m5_21_1e_spec_review.md) |
| Scripts | [`m5_21_1e_b_constraint.py`](../scripts/m5_21_1e_b_constraint.py) · [`m5_21_1e_c_toy.py`](../scripts/m5_21_1e_c_toy.py) · [`m5_21_1e_audit_check.py`](../scripts/m5_21_1e_audit_check.py) (the independent audit) |
| Data | `m5_21_1e_constraint.json` · `m5_21_1e_toy.json` · `m5_21_1e_audit.json` · endpoint npz (w1000, iso) + run logs (all < 1 MB, none deleted) |
| Plots / films | `m5_21_1e_constraint.png` · `m5_21_1e_toy.png` · `m5_21_1e_iso_film_basic/thermal.png` |
| Checkpoint | [`../checkpoints/m5_21_1e_progress.md`](../checkpoints/m5_21_1e_progress.md) (fan-out synthesis + run log) |
