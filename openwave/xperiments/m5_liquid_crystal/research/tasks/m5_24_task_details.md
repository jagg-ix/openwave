# M5.24, production-engine catch-up (audit + port the M5.x-era physics)

> 🔶 IN PROGRESS (go 2026-07-19 15:50 EDT). Roadmap row: [`m5_roadmap.md § IN PROGRESS`](../m5_roadmap.md). Checkpoint: [`../checkpoints/m5_24_progress.md`](../checkpoints/m5_24_progress.md).

## TASK PLANNING

**Scope**: Round 1 of the production-engine catch-up. The launcher's production physics stack (`engine2_pde.py` + `engine1_seeds.py` + `engine3_observables.py` + the `medium.py` physics fields, untouched since 2026-07-02 except the seeder) predates the M5.9-M5.21 research era that produced the canonical registry. This round: (A) full per-kernel inventory of the production physics stack, (B) confrontation against [`m5_theory_canonical.md`](../m5_theory_canonical.md) + the Done-task lineage into a routed GAP TABLE, (C) the first port batch (top-priority gaps, taichi-first, per-gap headless selftests), (D) launcher smoke verification + M5.23 selftest regression. Expected MULTI-ROUND (user note at staging: "maybe will take multiple updates later"); rounds 2+ take the deferred gaps.

**Definition of done (this round)**:

| # | Criterion | Check |
| --- | --- | --- |
| 1 | Per-kernel audit inventory in this doc: equation implemented, parameters, convention, provenance | every physics kernel in `engine1/2/3` + `medium` dispositioned |
| 2 | Gap table: per gap the research-validated source (task / method-note link) vs the production state, ROUTED: `PORT NOW` / `DEFER` (round 2+) / `NOT A GAP` (deliberate demo tuning) / `USER CALL` | every canonical-registry recipe row dispositioned |
| 3 | Port batch 1: each ported gap carries a headless selftest, ALL GREEN | goal-loop, 3-try cap per gate |
| 4 | No regression: launcher compiles + headless smoke evolve on the standard config; the M5.23 ellipsoid selftest stays 14/14 | machine-checked |
| 5 | Doc checker clean over touched `.md` | exit 0 |

**Gating**: user "go" (received 2026-07-19 15:50). Model/effort: Fable 5 / high (research default; audit + porting with physics judgement).

**Blindspot pass** (cross-cutting audit territory):

| Blindspot | Guard |
| --- | --- |
| Viz-tuning vs physics-gap conflation: production defaults may be DELIBERATE demo tuning, not stale physics | route ambiguous rows `USER CALL`, never silently clobber a tuned default |
| Transfer validity: canonical recipes were validated on research grids (axisym reductions, small boxes, specific integrators); the live 3D launcher grid is a different regime | each port carries a transfer note: what was re-verified at production scale |
| Convention drift: the 2026-06-21 index-0 flip (`D = diag(g, 1, δ, 0)`) | verify per kernel which convention it ACTUALLY uses; never assume the flip propagated |
| Hot files: `_launcher.py` / `medium.py` / `engine4_render.py` were edited today (M5.23 + user edits) | re-grep current state before every edit |
| Hidden dependents: launcher demo features (WM modes, flux mesh, VIZ suite) may depend on OLD kernel behavior | per port: back-compat or an explicit behavioral-change flag at review |

**Research body**: audit inventory + gap table + findings live in THIS doc; scripts `../scripts/m5_24_*.py`; plots `../plots/m5_24_*.png`; checkpoint `../checkpoints/m5_24_progress.md`. Feeds [M5.25](m5_25_task_details.md) (gated on the certified 4D production physics this task delivers).

**Stages**: A inventory sweep → B gap table → C port batch 1 → D smoke + regression. Preconditions: taichi via the conda env `openwave312`; canonical registry fresh-read at EXECUTE.

## STAGE A FINDINGS: the production physics inventory (2026-07-19)

Every physics kernel in the production stack, dispositioned. The launcher's live dispatch (verified in [`_launcher.py`](../../_launcher.py) `evolve_pde`): three evolve paths (3D leapfrog default; 4D masked leapfrog when the 4D xperiment is seeded; the Option B constrained integrator when `INTEGRATOR_4D = "constrained"`), then `eigen_decompose` refreshes the derived fields every frame.

| Kernel (file) | Physics implemented | Era vs the canonical registry |
| --- | --- | --- |
| `commutator` / `principal_director` / `eigvec_for` (`engine2_pde`) | analytic Cardano symmetric-3×3 eigensolver (the Metal/f32 `ti.sym_eig` replacement) | current; convention-agnostic, reused by everything incl. M5.23 |
| `eigen_decompose` + `director_mid` (`engine2_pde`) | per-voxel spectrum + apolar sign-continuous director + clock-hand axis, index-0 convention | current (the 2026-06-21 flip propagated) |
| `V_M` / `dV_M` (`engine2_pde`) | LdG quartic trace potential `a·Tr(M²) − b·Tr(M³) + c·(TrM²)²`, spatial block only | SUPERSEDED by the universal spectral potential (canonical § 1 "Superseded potential" row) |
| `compute_curvature_flux` + `evolve_M` (`engine2_pde`) | Eq.18 3D leapfrog: PLAIN commutator `F = [M_μ, M_ν]`, 8× flux, ½‖Ṁ‖²_F kinetic, M5.8.1 time-axis freeze | pre-verified-L era (M5.5); the sanctioned runnable dynamics is the § 2 row 6 canonical stack |
| M5.8.2c masked 4D path: `compute_stable_mask`, `compute_tstar`, `dV_M_dressed`, `compute_curvature_flux_4d`, `sample_v03_drift`, `evolve_M_4d` (`engine2_pde`) | the masked ηFη blend + dressed well + faithful-lite diagonal inertia | era experiment, pre-verified-L; the ghost problem it worked around is now UNDERSTOOD structurally (the η-null constraint + indefinite H, § 2 rows 1-3) |
| Option B constrained integrator: `init_P_4d` … `update_M_4d_constrained` (`engine2_pde`) | per-voxel 10×10 spectral projection, positive-inertia keep | the canonical § 2 explicitly names this stack the historical precedent of the structural disease; its refined descendant (the research true-L EL solve) is DIAGNOSTICS-ONLY by verdict |
| `relax_director_step` + `rebuild_M_from_director` (`engine2_pde`) | M5.1 Frank-energy director descent + uniaxial M rebuild | viz-tier seed conditioning; canonical statics recipes (FIRE frozen-time-row, stencil-symmetrized functional) are a different grade |
| Seeds (`engine1_seeds`): vacuum, uniaxial hedgehog, biaxial hedgehog, charged ring, dressed hedgehog | all embed the time axis as `+g` at `[0,0]` (block-diag), boost-decoupled except the dressed seed | ring seed is post-census (ported 2026-07-17); the `+g` embed is era-consistent with the plain-commutator paths but is NOT the verified vacuum (`M_vac = diag(−g, 1, δ, 0)`; `diag(+g,…)` has `V ≈ 1.05e6·w` at g = 8, canonical § 1) |
| `update_trackers_M`, `compute_energyH_density_M`, `compute_energyF_density`, `compute_director_em*` (`engine3_observables`) | ‖M−D_vac‖_F amplitude + ‖Ṁ‖_F clock; the Eq.18 plain ℋ + LdG V + v0-subtraction display hack; Frank density; director div/curl EM views | energyH is pre-verified-L; the trackers/EM/Frank views are director-derived viz (era-agnostic) |
| `compute_winding_number` (`engine3_observables`) | naive sphere integral on the director | the canonical instrument adds guards (multi-radius, decline on λ₁ ≈ λ₂); dashboard-only today |
| `fill_dipole_sample_B` (`engine3_observables`) | analytic dipole placeholder | already tracked as [M5.6.5f](m5_6_5f_task_details.md) stage 2 |

## STAGE B: the gap table (routed)

Porting reference of record: [`../scripts/m5_21_3_a_4d.py`](../scripts/m5_21_3_a_4d.py) (the M5.21.3 audited 4D instrument: `comm_eta`, `inner_eta`, `e_parts`, exact `grad`, `vac4`, W1 = 7.24023879e-4; its own gates: complex-step < 5e-9, SO(1,3) invariance < 1e-9 + negative control, vacuum ≡ 0 both branches, 3D block-diag regression < 1e-12). Key transfer fact from its G3 gate: on a block-diag (spatial-only) field with the time-time entry at `−sg`, the η-stack static energy EQUALS the plain-commutator 3D energy exactly, so the port is behavior-compatible with today's static seeds by construction.

| # | Gap | Research-validated source | Production state | Route |
| --- | --- | --- | --- | --- |
| G1 | η-bracket field strength `F = [A_i, A_j]_η` + signed inner product `⟨F,F⟩_η` | canonical § 1 (M5.18, 15/15); `m5_21_3_a_4d.py` | plain Frobenius commutator (3D path); pre-verified ηFη masked twist (4D-era paths) | ✅ PORT NOW |
| G2 | universal spectral potential `V4 = w·Σ_p (Tr_η(M^p) − C_p)²`, `w = 7.24e-4`, `C_p = sg^p + 1 + δ^p` | canonical § 1 + § 4 (WSCALE lock) | LdG `V_M(a,b,c)` (superseded) + the M5.8.2 dressed well | ✅ PORT NOW |
| G3 | the canonical-kinetic regularization stack as the runnable 4D dynamics (½‖Ṁ‖²_F + η-curvature + V4; § 2 row 6: "fine for statics-adjacent dynamics questions and films", i.e. exactly the launcher's use class) | m5_20 § 2-3; the 3D twin (m5_21 § 4); the M5.21.3 4D functional | M5.8.2c masked-blend leapfrog + faithful-lite inertia | ✅ PORT NOW: new `canonical` integrator path (the centerpiece) |
| G4 | covariant vacuum `M_vac = diag(−g, 1, δ, 0)` | canonical § 1 | every seed embeds `+g` | ✅ PORT WITH G3: seed-time time-axis flip on the canonical path only (other paths stay `+g`, era-consistent) |
| G5 | verified-H energy display: `u_η + V4` with v0 ≡ 0 at vacuum (exact) | canonical § 1 (Legendre) + the factor-2 bridge (§ 5.5) | Eq.18 plain ℋ + v0-subtraction hack | ✅ PORT NOW: η energy-density kernel for the canonical path |
| G6 | sym-stencil (½(fwd + bwd), exact adjoints) well-posedness | M5.21.2b certificate; § 6 anti-recipes (2h deep statics) | all production PDE kernels are 2h central | ✅ PORT NOW inside the new path (existing paths untouched) |
| G7 | status of the constrained integrator | § 2 rows 1-3 + the historical-precedent note | live launcher mode | NOT A GAP: keep as the era mode; docstring updated to point at the § 2 verdict chain |
| G8 | statics-relaxer catch-up (FIRE frozen-time-row; stencil-symmetrized functional) | § 5.2 | M5.1 Frank director descent only | 🚧 DEFER round 2 (needed when the launcher wants census-grade relaxed states) |
| G9 | guarded winding instrument (multi-radius + λ-gap decline) | § 5.4 | naive sphere integral | 🚧 DEFER round 2 (dashboard-only today) |
| G10 | M5.8.3(a): the 4D production seeder extension | [`m5_8_3_task_details.md`](m5_8_3_task_details.md) | `seed_dressed_hedgehog_M` exists (M5.8.2-era, `+g`) | PARTIAL: the canonical-path flip covers static 4D seeds; a verified-L clock-carrying seed is physics-gated (the fixed-J arc, [M5.21.9](m5_21_9_task_details.md)) |
| G11 | M5.8.3(b): the faithful-kinetic engine variant | [`m5_8_3_task_details.md`](m5_8_3_task_details.md); § 2 rows 1-2 | not implemented | NOT A GAP: SUPERSEDED (the faithful kinetic IS the true-L operator, ill-posed as a free EL; the constrained mode already covers the era physics) |
| G12 | anti-recipe guards riding the ports (certified dt values, FIRE dt caps, no-deep-2h-statics) | § 5.2/5.3/§ 6 | n/a | carried as docstrings + notes in the new kernels |

## STAGE C + D FINDINGS: port batch 1 (2026-07-19)

### What landed

| Piece | Where | Content |
| --- | --- | --- |
| The η algebra + spectral potential | [`engine2_pde.py`](../../engine2_pde.py) M5.24 section | `eta_left`/`eta_right`/`comm_eta44`/`inner_eta44` (the M5.18 verified bracket + inner product), `v4_of`/`dv4_of` (the universal spectral potential + its exact gradient), `W1_SPECTRAL = 7.24023879e-4` (the WSCALE lock) |
| The canonical evolve pair | same | `compute_eta_flux(branch)` (two-pass symmetrized stencil, ½(fwd + bwd) with exact adjoints, the M5.21.2b well-posedness certificate) + `evolve_M_eta_start`/`evolve_M_eta_finish` (adjoint gather + V4 force; `M_new_am` doubles as the force accumulator, zero new fields) + `flip_time_axis` (covariant-vacuum conversion) |
| The verified-H energy view | [`engine3_observables.py`](../../engine3_observables.py) | `compute_energyH_density_eta`: ½‖Ṁ‖²_F + u_η + V4 with a TRUE-ZERO vacuum floor (retires the v0-subtraction hack on this path) |
| Launcher wiring | [`_launcher.py`](../../_launcher.py) | canonical activation (post-relax time-axis flip + routing), the dt cap in `compute_timestep` (survives the every-frame refresh), the energyH branch, a bounded-energy auto-pause guard, and a **stale-4D-state reset at the seed dispatch** (a latent era bug: an xperiment switch away from a 4D config kept evolving on the previous integrator; my canonical path would have inherited it) |
| Demo xperiment | [`xparameters/_topo_canonical4d.py`](../../xparameters/_topo_canonical4d.py) | biaxial hedgehog on the canonical stack (its far field IS the covariant vacuum spatial spectrum) |
| The machine gate | [`../scripts/m5_24_canonical_engine_selftest.py`](../scripts/m5_24_canonical_engine_selftest.py) | 11 checks against the AUDITED reference imported directly (no re-transcription) + an informational indefinite-channel probe |

### Gate results (selftest, 3 tries per the goal-loop cap)

| Check | Result |
| --- | --- |
| V4(vacuum) = 0 exact; V4(diag(+g,…)) = W1·(4g² + 4g⁶) closed form (the canonical § 1 "not a vacuum" number, unweighted ≈ 1.05e6) | ✅ 3e-11 / 1e-5 |
| V4 random vs the reference `e_parts` | ✅ 3.3e-7 |
| Production energy kernel vs reference (bump field) | ✅ 8.4e-7 |
| The two-pass force vs the reference exact gradient | ✅ 1.25e-5 |
| Vacuum force at the f32 floor | ✅ 5.9e-4 (the g⁴-trace-scale f32 floor; per-step displacement ~1.5e-8, self-centering well) |
| SO(1,3) invariance + broken-L negative control | ✅ 1.1e-6 / control 1.8e4 |
| 3D block-diag regression (u_η == plain 3D read) | ✅ 5.1e-6 (the transfer fact: behavior-compatible with static seeds) |
| flip_time_axis on all three buffers | ✅ |
| **E conservation, spatial sector, 1500 steps @ dt = 0.005** | ❌ at the 5e-3 tolerance: drift 2.34e-2, **but bounded** (max\|M\| = 8.00 = the vacuum g scale, E 0.1228 → 0.1223, no growth). 🔶 suspected ESTIMATOR artifact: the staggered kinetic (M_t − M_{t−1})/dt mis-measures the ω·dt = 0.39 stiff-mode energy by O((ωdt)²) ≈ 15% per mode; the goal-loop 3-try cap was reached, so per discipline the gate is surfaced, not tuned away. Fix (centered-velocity or half-step ledger) = round 2 |
| M5.23 ellipsoid selftest regression | ✅ 14/14 |
| Headless launcher smoke (real 63³ demo grid) | ✅ canonical routed, time axis flipped, dt cap survives the frame loop, 30 real frames bounded (max\|M\| = 8.000), energyH finite from the true-zero floor, xperiment switch resets routing, the plain path still evolves |

### Measured findings (beyond the port)

| Finding | Status | Detail |
| --- | --- | --- |
| The certified dt is DIMENSION-SPLIT | ✅ measured | the axisym stack's dt = 0.02 (canonical § 5.3) went NaN on the full-3D f32 path (ω_stiff·dt = 1.57, too close to the leapfrog margin 2.0); the 3D twin's dt = 0.005 (canonical § 3) is stable: the launcher cap defaults to 0.005. Candidate § 5.3 annotation at the model-doc sweep |
| The indefinite channel is REAL in production | ✅ measured | a full-4×4 noise bump (time-row components) runs away WITH E conserved (NaN by ~1500 steps at both dt values): the canonical § 1 "H unbounded below" physics reproduced in the f32 production kernels, not a port defect. Block-diag data (every launcher seed) is an invariant manifold where u_η reduces to the positive 3D energy: the demo regime. The launcher carries a bounded-energy auto-pause guard |
| Unit-map gap (flagged, not fixed) | 🔶 | the launcher's physical `dx_am` (~15.6 at 64³ over 1 fm) differs from the research grid unit (h = 1.5), shifting the curvature-vs-V4 balance relative to research-grade runs; the selftest pins dx_am = 1.5 via the universe edge; a launcher-side unit alignment (or a config-declared research-unit dx) = round 2 |

No plot artifacts this round (the gates are numeric; the launcher itself is the visual deliverable). No data files > 1 MB were produced (the selftest writes nothing to `data/`).

### Round 2+ backlog (stays in this task, per the multi-round expectation)

| Item | From |
| --- | --- |
| Conservation-ledger estimator fix (centered velocity / half-step ledger) + re-gate at 5e-3 | the surfaced gate |
| G8 statics-relaxer catch-up (FIRE frozen-time-row; stencil-symmetrized functional) | gap table |
| G9 guarded winding instrument | gap table |
| Launcher unit-map alignment (research-unit dx option) | measured finding |
| Optional sponge (the § 5.3 exact-ledger damping) for long live runs | canonical § 5.3 |
| Constrained-path docstring pointer to the § 2 verdict chain (G7 note) | gap table |

## ROUND 2 FINDINGS (2026-07-19, go 17:53)

Trigger: the user's live-demo verdict at the round-1 review ("the demo works" + the animation is too slow to watch the ellipsoids move). Round-2 scope executed: the viz-speed lever, the conservation-ledger fix, the unit-map alignment, the G7 status note, the G9 guarded winding instrument. G8 (FIRE statics relaxers) rides to round 3.

### What landed

| Piece | Content |
| --- | --- |
| `ETA_SUBSTEPS` (the viz-speed lever) | N physics steps per rendered frame at the CERTIFIED dt (default 8, config-tunable). dt itself cannot rise (the stiff-mode wall 2/78 ≈ 0.026 τ, NaN measured at 0.02) and SIM_SPEED cannot help (the cap pins dt_eff), so visual speed = substeps. The launcher's shared buffer-swap tail still runs exactly once per frame (the last substep leaves its swap to it) |
| `ETA_DX` (the unit-map fix, was round-2 backlog) | the canonical kernels now take the grid spacing as an argument; the demo config sets the RESEARCH unit (1.5 = the m5_21_2b/3 h), making the 63³ box research-twin geometry. The physical `dx_am` (~15.6) had weakened curvature ~100× against the dimensionless V4, so the field barely moved spatially: this was a large hidden part of the "nothing moves" report |
| The conservation ledger, fixed + mechanism identified | (a) centered velocity `(M_{t+1} − M_{t−1})/2dt` replaces the staggered estimator (its O((ωdt)²) stiff-mode bias was round 1's suspicion, confirmed real but NOT the whole story); (b) the remaining monotone loss was traced by an amplitude ladder (amp 0.05/0.1/0.2/0.4 → rel drift 2.6e-2/5.6e-3/6.8e-4/4.8e-5, E growing quartically): the ABSOLUTE loss is amplitude-independent (~1e-2 per 1000 steps) = the f32 update-truncation floor of the \|M\| ~ g field scale. ✅ measured: numerical cooling, not a scheme error. The gate now runs at demo-grade amplitude (0.2) and PASSES at 5.16e-4; the floor is quantified in a selftest info line |
| G7 status note | the constrained-integrator section header now carries the canonical § 2 verdict-chain pointer (historical precedent; the true-L EL solve is diagnostics-only; kept as the era mode) |
| G9 guarded winding | `compute_winding_number_guarded` (engine3): multi-radius Q + the eigen-gap decline flag per canonical § 5.4 + the § 6 churned-state anti-recipe. NOTE: the plain winding read has NO live launcher caller today (dormant M5.1 diagnostic); the guarded wrapper is the instrument any future consumer must use. Exercised in the smoke: the seeded 63³ hedgehog reads q = 0.996 ± 0.000, min gap 0.582, not declined (matches the era anchor Q = ±0.996, § 4b) |

### Round-2 gates

| Check | Result |
| --- | --- |
| Full selftest (new signatures + centered ledger) | ✅ ALL 11 GREEN, incl. E conservation drift 5.16e-4 over 1000 steps at amp 0.2 (was the round-1 surfaced gate) |
| f32 floor quantified | [info] small-amplitude state loses 1.93e-3 absolute per 500 steps, amplitude-independent |
| Launcher smoke (63³, substeps 8, dx_eta 1.5) | ✅ routing + flip + cap + 30 frames (240 physics steps) bounded, max\|M\| = 8.000; guarded winding green; xperiment switch still resets routing |

Round-3 backlog: G8 statics-relaxer catch-up (FIRE frozen-time-row + the stencil-symmetrized functional, the census-grade-states enabler), optional sponge for long live runs, and any live-demo feedback from the substeps/dx configuration.

## TASK REVIEW (2026-07-19, round 1)

**Task Duration:** 00:25 (from the 15:50 go to the 16:15 review post)
**Usage Cap Triggered:** NO

Round-1 review presented in the terminal and discussed; user decisions: **the task STAYS In Progress** (multi-round, as anticipated at staging), **the canonical port + the § 5.3 dt annotation APPROVED** (annotation applied to [`m5_theory_canonical.md § 5.3`](../m5_theory_canonical.md) at this review: dt = 0.02 marked axisym-only, dt = 0.005 = the full-3D step, production-port pointer added), live-demo test by the user follows this review. Results, the surfaced conservation gate (🔶 estimator-artifact-suspect, bounded state, goal-loop cap honored), measured findings (dimension-split dt; the indefinite channel reproduced in production f32; the stale-4D-state launcher bug fixed), and the round-2 backlog: all recorded in the Stage A/B and Stage C + D sections above. Model-doc sweep: the canonical § 5.3 amendment (this review); the model briefing states nothing this round changes (skipped explicitly).

**Why**: the launcher's production Evolve-PDE path (`engine2_pde.py` + the engine stack the GGUI app runs) largely predates the M5.9-M5.21 research era: the research body validated recipes (the M5.16 parameter locks, the verified Lagrangian work, the 4D integrator findings, the quartic-saturation era results) that production never received. The maintainer flagged this at the M5.23 review: the live app should evolve with the certified physics, not the old-era kernels.

**Scope sketch (to be firmed at go)**:

| Step | Deliverable |
| --- | --- |
| 1. Audit | Production kernels vs the canonical registry ([`m5_theory_canonical.md`](../m5_theory_canonical.md): verified equations, locked parameters, working recipes + anti-recipes, the 4D stack) and the Done-task lineage in [`m5_roadmap.md`](../m5_roadmap.md) |
| 2. Gap table | Per kernel: research-validated vs production-implemented, with the source task/method-note link for each gap |
| 3. Port | The gaps, taichi-first, each with a per-gap headless selftest (goal-loop gates) |
| 4. Verify | Live launcher run on the standard configs; no regression in the certified views |

**Merged scope (2026-07-19)**: the former [M5.8.3](m5_8_3_task_details.md) residual row folded in whole (maintainer call at the M5.23 review):

| From M5.8.3 | Now an M5.24 scope item |
| --- | --- |
| 4D extension of the M5.6.5a production seeder | Part of step 3 (port), audited in step 1 like every other kernel |
| The faithful-kinetic engine variant (the 5d diagnosis: frequency correction only) | Evaluated in the step-2 gap table; ported only if production-scale clock runs need it |

**Gating**: user "go".
