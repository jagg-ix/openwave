# M5.21.2: the 3D 3-lepton axis-permutation scan (his 2026-07-17 prescription)

**Status**: IN PROGRESS (go 2026-07-17 09:37 EDT; reset 13:50, resume ping armed 13:55). Opened 2026-07-17 at the Q25-Q28 reply decode ([`m5_21_convo.md § 2026-07-17`](m5_21_convo.md); staged as M5.21.4 at creation, renumbered M5.21.2 same day in the run-order renumber: it runs FIRST). Roadmap row: [`m5_roadmap.md § IN PROGRESS`](../m5_roadmap.md).

## TASK PLANNING

**Scope**: run the author's 2026-07-17 3D-FIRST prescription end-to-end. Build the genuine 3×3 spatial stack (no time row, no g: vacuum spectrum (1, δ, 0), symmetry group SO(3), full-3D cubic grid), gate it, control the ONE numerical risk he flagged (small box + δ = 0.3 destroying the topological constraints through the boundary), then the scan: energy minimization from the three axis-permutation hedgehog seeds diag(1, δ, 0) / (δ, 0, 1) / (0, 1, δ), censusing the local minima ("global should be electron"; three distinct minima = the lepton-hierarchy signature, FRAME p. 15 = the [M5.9](m5_9_task_details.md) lepton row's first concrete run). The headline physics question: does the 3D hedgehog CONVERGE (topological protection real at statics) where the 4D one diluted ([M5.21.1](m5_21_1_task_details.md) P1 negative, mechanism bracketed at [M5.21.1e](m5_21_1e_task_details.md))?

**Definition of done** (testable):

| # | Criterion |
| --- | --- |
| 1 | Gates green: complex-step gradient check ≤ 1e-10 rel; global SO(3) energy invariance ≤ 1e-10 rel + a negative control; vacuum energy ≈ 0; seed spectrum verified (far-field = the permuted vacuum, two-equal on the vortex axis, three-equal center) |
| 2 | Boundary-integrity ladder measured: hedgehog retention vs (N, δ, BC pinned/free) with a stated working point, or the honest negative that no rung protects |
| 3 | The 3-seed census at the working point: per-seed endpoint characterized (E, virial ratio u/3V, r_half, radial alignment/charge, spectrum profiles) + the three-minima verdict |
| 4 | Independent adversarial audit of every substantive claim before the review |
| 5 | Doc checker clean; TASK REVIEW in the terminal with the two log lines; >1 MB raw data deleted + documented |

**Gating**: user "go" ✅ 2026-07-17. Consumes: the [M5.21.1](m5_21_1_task_details.md) full-3D 4×4 machinery (`m5_21_1_c_4d.py`, ported to 3×3 with η → identity, time row dropped) + the M5.21.1/1e results as comparators. Feeds: [M5.21.3](m5_21_3_task_details.md) (the 3 minima = its 4D descent seeds), [M5.21.5](m5_21_5_task_details.md), the Q25/Q26 discrimination, the Duda thread ([`m5_21_convo.md`](m5_21_convo.md)).

**Blindspot pass** (unknown unknowns surfaced):

| Blindspot | Route |
| --- | --- |
| The 3D potential p-range (p = 1..3 pins all three invariants; p = 1..4 is the 4D habit) | machine-checkable: p = 1..3 is the primary (3 eigenvalues ↔ 3 invariants); a p = 1..4 control at the working point, cheap |
| Boundary-condition semantics: pinned ENFORCES the winding (protection by construction), free TESTS it | run BOTH; the interpretation caution goes in the findings, never blended |
| The M5.21.1 amplitude-dilution escape may reappear in 3D | watch the same diagnostics (spectral force fraction, coreball, r90); pre-registered fallback = a wscale ×100 stiffness arm at the working point |
| Director sign ambiguity (±v identified) breaks naive degree sums | primary observable = the radial-alignment profile a(r) = mean((v·r̂)²) (1 = hedgehog, 1/3 = unwound); the lattice degree is secondary |
| Near-degenerate (δ, 0) pair churns eigenvector ORDER at small δ (the M5.21.1e audit lesson: gap-dip radii unreliable) | census reads use whole profiles, never single radii |
| FIRE dt stability on the 3D h = 1 grid | dt0 = 0.02, force refreshed EVERY iteration, non-finite backoff (the M5.21.1e toy lesson) |
| N = 64 runtime blowup | N = 48 is the workhorse; N = 64 only as the boundary-ladder spot-check |

**Research body**: script `../scripts/m5_21_2_a_scan3d.py` (one script, phase modes: gates / ladder / scan / plots, the M5.21.1e pattern) + the audit agent's own script `../scripts/m5_21_2_audit_check.py`. Data `../data/m5_21_2_*.json` (+ transient `.npz` endpoints, deleted if > 1 MB and documented). Plots `../plots/m5_21_2_*.png` (seed maps + endpoint maps REQUIRED per the field-state rule; ladder heatmap; census panel; film strips adapted to 3×3 meridional cross-sections, both templates where portable). Findings `../findings/m5_21_2_census.md` (method-note-grade: this goes back to the author). Checkpoint `../checkpoints/m5_21_2_progress.md`.

**Sub-experiments** (pre-registered):

| Phase | What | Kill / survive read |
| --- | --- | --- |
| P0 stack + gates | Port the 4×4 3D statics to 3×3 (curvature u = commutator norm over the 3 derivative channels; V = wscale·Σ_p (Tr(M^p) − C_p)², C_p = 1 + δ^p, wscale = 7.2402e-4 carried for continuity); complex-step + SO(3) + vacuum + seed gates | gates green before ANY physics; goal-loop cap 3 tries then stop and surface |
| P1 boundary ladder | Seed A (electron); N ∈ {32, 48, 64} × δ ∈ {0.3, 0.1, 0.03} × BC {pinned, free}; ~800-iter probes; read a(r)/q retention, boundary-layer energy, far-field spectrum drift | any rung where FREE BC keeps the winding → protection measured; only-pinned-holds → protection is boundary-enforced (honest label); pick the working point |
| P2 the 3-seed census | Seeds A/B/C at the working point; long FIRE (≤ 30k iters, convergence = force max + E plateau); snapshots → films; endpoint census (E, u/3V, r_half, a(r), spectra) | three DISTINCT minima vs collapse-to-one vs dilution; the virial balance read per endpoint |
| P3 the charged-ring arm (user amendment 2026-07-17 mid-run, replacing the optional barrier read) | The charged disclination ring: seed A's exact far field (same unit winding sector), core opened into a half-disclination ring (radius a = 4, escaped interior), pinned, working point; `seed_ring` + `core_locus` in the script | E_ring vs E_A endpoints = does the electron ground state prefer a ring core (the m5_particle_hunt synthesis nuance + the M5.16 Q8 off-origin melt, made testable); the barrier read drops unless time allows |
| Audit | independent agent tries to REFUTE: minima genuineness (stationarity), gate reproduction, census numbers | verdicts per claim recorded in the findings |

**Preconditions**: numpy (vectorized einsum, float64) suffices at N ≤ 64; no GPU dependency. Model/effort: Fable 5 / high (research default). `resets_at` = 13:50 EDT is the RELEASE time, not a deadline: checkpoint eagerly, work normally.

## DEVIATIONS LOG

(running; entries added as they happen)

| When | Entry |
| --- | --- |
| 10:55 | USER AMENDMENT (not a deviation): P3 redefined from the optional barrier read to the charged-ring arm (the topology-catalog discussion while P2 ran: the ring is the one same-winding-sector alternative that could beat the hedgehog on stability). Ring seed verified (far lams (0, δ, 1) exact; core locus ρ ≈ 3.8; boundary values within 0.9% of A's, noted for the audit) and launched pinned at the working point (bg bqtpl97dw). The A/B/C census rows predate `core_locus` (added with the ring); it will be post-computed from their endpoint npz at collect |
