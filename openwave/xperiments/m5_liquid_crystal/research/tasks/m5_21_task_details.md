# M5.21: the particle-clock film strip: electron cross-section snapshots

**Status**: roadmap row in [BACKLOG](../m5_roadmap.md) (PLAN-ready, **ungated**: phase 1 runs in the measured-stable rotation sector, no Duda dependency). The M5.21 **series**: this task = phase 1 (rotation clock, snapshot pipeline); successor stub **M5.21.1** = the full constrained 4×4 time term on the electron, gated on the same Duda constraint answer as [M5.20.3](m5_20_3_task_details.md) (add its roadmap row at M5.21 close).

**Lineage**: [M5.20.2](m5_20_2_task_details.md) (the 4×4 EOM machinery + the census this task rides: all rotation generators K_eff > 0, rotation injections measured stable over T = 400) · [M5.16](m5_16_task_details.md) (the audited axisym hedgehog minimizer + parameter lock; the **Q8 saddle finding** this task probes dynamically) · [M5.11](m5_11_task_details.md) (Faber electron statics, 511 keV) · [`m5_4b_rendering_features.md`](m5_4b_rendering_features.md) (the viz framework this task previews headlessly: Part 4 observable catalog, § 4.1.1 the clock-visibility recipe, § 5.3 placeholder-sample strategy) · [M5.13](m5_13_task_details.md) (the future on-screen demo suite this feeds).

## TASK PLANNING (2026-07-13, specs interview folded)

### Interview outcomes (user decisions, 2026-07-13)

| Decision | Chosen |
| --- | --- |
| Clock sector | **Phased**: rotation sector now (ungated), full constrained 4×4 later (M5.21.1, gated with M5.20.3) |
| Geometry | **Axisym (ρ,z) primary + one 3D spot-check** (the saddle direction the axisym box freezes) |
| Plot style | **Ellipse glyphs + heat maps**, film-strip at chosen timesteps |
| Audience | **Internal preview + feeder for the rendering block**: the snapshot pipeline is itself a deliverable, previewing the future full-3D Taichi production engine's viz features (flux mesh of energies, electric/magnetic field, scalar + vector viz, magnitude + direction views, glyphs). The [`m5_4b`](m5_4b_rendering_features.md) framework catalog it feeds, per the user's 2026-07-13 enumeration: charge, mass/energy, deBroglie clock/ZBW, particle stability, angular momentum, spin, magnetic moment, **2-particle attraction/repulsion**, LC director vector, **Coulomb**, force fields (ele-mag-grav), EM waves, and thermal energy in the future if it lands. This task's panels cover the electron-relevant subset; the rest are future pipeline cases (the 2-particle film-strip is the natural next reuse). Promote to a Duda-facing note only if the movie earns it |

### Scope

Two deliverables, in order:

| # | Deliverable | Content |
| --- | --- | --- |
| 1 | **The reusable snapshot instrument** (headless matplotlib, no GUI/Taichi rendering) | Given a field state M (axisym cross-section or a 3D slice), render one panel set; a film-strip = the panel set at chosen timesteps. Channel mapping mirrors the launcher features so the pipeline is a 1:1 headless preview of the future engine |
| 2 | **The electron rotation-clock movie** | Hedgehog charge defect (Duda's 3-equal core prescription) evolved under the M5 Lagrangian in the 4×4 tensor, a rotation-sector clock seeded on it; film-strip showing the clock ticking while the defect holds (or fails to hold): "see the particle clock creating particle stability" |

**Particle size (the user's feasibility question, answered at PLAN)**: the electron is NOT harder due to size. In lattice units the defect core is a few cells regardless of species; the physical fm scale is the M5.16 unit map applied afterwards (parameter-free `r_half = 2.926 fm` already demonstrated). The real difficulty axes are time-integration well-posedness (dodged by staying in the measured-stable rotation sector) and 3D-vs-axisym geometry (handled by the axisym-primary + 3D-spot-check decision).

**The hidden physics question (upgrade from preview to measurement)**: M5.16's Q8 found the spherical hedgehog is a SADDLE of the unconstrained statics (perturbed relax drops 35%, melt moves off-origin). This task watches the same object under conservative DYNAMICS with a rotation clock on it: does the clock stabilize what statics calls unstable? Either answer is a real finding.

**Visual bar** (the user-named inspiration, to be upgraded with the glyph layer):

![t = 0: the seeded loop, both pairings at delta = 0.3](../plots/m5_20_1_seed_maps.png)

![endpoints at t = 2000](../plots/m5_20_1_endpoints.png)

### The panel set (one snapshot)

| Panel | Observable | Launcher-feature analog ([`m5_4b`](m5_4b_rendering_features.md)) |
| --- | --- | --- |
| Ellipse glyph field | Eigenvalues = radii, eigenvectors = axes, grayness = activated potential V(M) (Duda's diagram language), **plus the δ-axis tick per glyph** (the middle eigenvector): the § 4.1.1 correction says the director is the axle, ONLY the δ-axis sweeping shows the spin: without the tick the clock is invisible | Glyph states 0/1 (Director / Director + Delta) |
| Amplitude A | Frobenius deviation from vacuum (heat map, ironbow-like) | WM2 Amp |
| Clock rate | Ṁ Frobenius norm (heat map, blueprint-like) | WM3 Clock ω |
| Energy density | Hamiltonian density (heat map) | WM4 Energy H |
| Charge | Director-splay magnitude at cross-section (gauge-safe: magnitude or defect-relative sign, per the § 3 sign caveat) | WM6 EM div |
| Circulation | Curl magnitude (the B analog; near-zero for the static charge, lights up with the clock: the "B appears with motion" reading) | WM7 EM curl |

Layout: film-strip rows = timesteps (t = 0, then log- or event-spaced), columns = panels; plus a per-run trace figure (E(t), core spectrum λ_i(ρ→0, t), clock phase read-back, charge Q(t)).

**Magnitude + direction views (the launcher's glyph size/color toggles, previewed)**: the glyph panels render in the two launcher variants: `unit + single` (every glyph same length, flat color: the structure-everywhere / far-field view) and `magnitude + gradient` (shaft scales with field strength, color carries the signed value: the field-strength view). Default film-strip uses the structure view for the frame panel and the strength view for the E/B panels; both variants are one flag in the instrument so the future Taichi engine's toggles have a validated headless twin.

### Definition of done

| ✅ when | Bar |
| --- | --- |
| Instrument validated BEFORE physics (the § 5.3 placeholder pattern) | Glyph + panel renderer reproduces analytic placeholder fields exactly: uniform vacuum (no glyph structure), analytic hedgehog (splay 2/r matched, curl ≈ 0), synthetic rotating texture (rendered δ-axis phase == seeded phase, read-back ω == seeded ω) |
| Electron baseline reproduced | Axisym statics re-run reproduces the M5.16-class hedgehog (3-equal core per Duda's charge prescription) before any dynamics |
| The movie landed | Rotation-clock run(s) with the film-strip rendered; energy ledger ≤ 1e-5; seed + endpoint cross-sections (standing rule) plus the intermediate frames (this task's point) |
| The stability question answered honestly | Q8-dynamic verdict instrumented (E localization, core spectrum, topological charge conservation, drift of the defect center), labeled ✅ measured / 🔶 / ⚠️, axisym scope-boxed |
| 3D spot-check run | One short small-grid 3D run probing the saddle direction axisymmetry freezes; slice snapshots through the same pipeline |
| Record + reuse | Findings page (internal) with film-strips embedded; the snapshot instrument documented as a reusable module (the rendering-block feeder); doc checker exit 0 |

### Gating

Ungated (phase 1). The roadmap `Gated By` notes only: M5.20.2 assets (present) + the rotation-sector stability result it rides. M5.21.1 (phase 2) inherits the M5.20.3 gate.

### Pre-registered gates

| Gate | Criterion |
| --- | --- |
| GV0 placeholders | The three analytic placeholder renders above, exact (rendering validated before the physics produces it) |
| GS statics | Axisym hedgehog baseline: energy + core spectrum consistent with the M5.16 lock; 3-equal core reads (a, a, a) at center |
| GD ledger | dt² max-deviation scaling on the dynamics stack; production dt from the measured stiffest mode (4-target V: the g-restoring ω = 78.28 bound applies if the time eigenvalue is active; recompute if the electron sector changes it) |
| GR clock read-back | Seeded rotation ω recovered from the rendered δ-axis phase sweep AND from the Ṁ channel, matching to the FFT bin honesty bar |
| GB runaway watch | The rotation sector is measured stable, but the hedgehog + clock nonlinearity could couple into boost directions: monitor the boost-sector projection per snapshot; if it grows, the documented fallback is the frozen-time-row run (still shows the spatial clock) and the finding is reported, not hidden |
| GQ stability instruments | Topological charge (winding/degree) conserved; defect-center drift; E localization fraction vs t |

### Blindspot pass (unfamiliar territory: electron dynamics + glyph rendering)

| # | Unknown unknown surfaced | Fold into plan |
| --- | --- | --- |
| 1 | The clock is invisible on the director alone (the § 4.1.1 correction: a line has no roll feature; the director is the axle) | The δ-axis tick is REQUIRED in the glyph panel; GR reads the clock from it |
| 2 | Charge-sign gauge flips under evolution (the § 3 caveat: apolar director, neighbouring sign drift) | Charge panel uses magnitude or the defect-relative gauge fix; the conserved charge is the topological winding (GQ), never the splay sign |
| 3 | The Q8 saddle may be an axisym artifact OR may be hidden by axisymmetry (the unstable direction could be non-axisym) | The 3D spot-check exists exactly for this; axisym verdicts scope-boxed |
| 4 | Near-degenerate eigenvalues at the 3-equal core make eigenvector fields noisy there (spurious glyph orientation at the core, the known near-degenerate-zone amplification) | Glyph panel masks or fades glyphs where the eigenvalue gap is below a floor; the core is read via the spectrum trace, not the glyph |
| 5 | Rotation about WHICH axis: three rotation generators exist; the physical ZBW is the twist about the director | Seed the J aligned with the hedgehog's radial structure per Duda's charge picture; one alternate-axis control run |
| 6 | Wall-clock + file size: film-strips at many timesteps can bloat plots/ | Fixed frame budget (~8-12 frames/run); > 1 MB raw state files deleted at FINISH with regen docs (standing rule) |

### Unknowns quadrants self-test

| Quadrant | Biggest unknown | Route |
| --- | --- | --- |
| Known knowns | Rotation-sector stability, the EOM, the axisym stacks, the statics lock | Reuse; GS/GD guard the joins |
| Known unknowns | Does the clock stabilize the Q8 saddle (machine-checkable, THE run); the right rotation axis (control run) | GQ + blindspot 5 |
| Unknown knowns | The user's visual bar: the M5.20.1 maps + Duda's ellipse diagram + the launcher features (now explicit via the interview) | Wired into the panel set |
| Unknown unknowns | The blindspot list; whatever the audit finds | Deviations log at EXECUTE + adversarial audit on any substantive stability claim |

### Research-body destinations

| Artifact | Destination |
| --- | --- |
| Scripts | `../scripts/m5_21_a_snap.py` (the reusable snapshot instrument + GV0 placeholders) · `m5_21_b_electron.py` (statics baseline + seeds) · `m5_21_c_clockrun.py` (rotation dynamics + snapshot hooks) · `m5_21_d_3dcheck.py` |
| Data / plots | `../data/m5_21_*.json` · `../plots/m5_21_*` (film-strips + traces) |
| Findings | `../findings/m5_21_films.md` (internal findings page, film-strips embedded; promote-to-Duda decision at REVIEW) |
| Records | This file (FINDINGS + TASK REVIEW) · `../checkpoints/m5_21_progress.md` at go · Q8 cross-link back to the M5.16 record |

### Sub-experiments (phase plan)

| Phase | Content | Gate |
| --- | --- | --- |
| A | The snapshot instrument against analytic placeholders (§ 5.3 pattern) | GV0 |
| B | Electron statics baseline + clock seeding (rotation sector, axis per blindspot 5) | GS |
| C | Rotation-clock production run(s) + film-strips + the Q8-dynamic verdict | GD, GR, GB, GQ |
| D | 3D spot-check (small grid, short run, slices through the same pipeline) | GQ (3D) |
| E | Findings page + (if a substantive stability claim emerged) adversarial audit + REVIEW | Doc checker exit 0 |

### Preconditions

| Precondition | State |
| --- | --- |
| M5.20.2 EOM + census machinery | ✅ frozen on disk |
| M5.16 minimizer + parameter lock | ✅ frozen on disk |
| The rendering-features doc (panel mapping source) | ✅ [`m5_4b_rendering_features.md`](m5_4b_rendering_features.md) Parts 3-5 |
| Resume ping + checkpoint file | 🚧 at go |

### Model + effort

Default effort for A/B/D (instrument + mechanical baselines, try cap 3 per gate); high for C if the Q8-dynamic result is surprising (it becomes a finding needing careful claims); independent agent for the audit if any stability claim is substantive.

### Contingencies

| Trigger | Action |
| --- | --- |
| Boost coupling fires (GB) | Fall back to the frozen-time-row run; report the coupling as a measured finding |
| Duda's constraint answer arrives mid-run | M5.20.3 takes priority (program-critical); M5.21 checkpoints and resumes after (both are checkpoint-complete by construction) |
| The movie is Duda-gold (clock visibly stabilizing the electron) | Promotion decision at REVIEW: method-note standard + audit before any outbound (never auto-send) |
