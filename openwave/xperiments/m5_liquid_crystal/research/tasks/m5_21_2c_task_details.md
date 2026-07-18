# M5.21.2c: the 3D vortex-line visualization: 3 lepton candidates + the closure read

**Status**: 🚧 PLANNED STUB (2026-07-18, from his reply to the M5.21.2b package; [`m5_21_convo.md § 2026-07-18 03:22`](m5_21_convo.md)). His ask verbatim: "Maybe you could visualize it, these vortices in 3D? Preferably for 3 lepton candidates - for humans to better understand, their differences." Full PLAN at go. Cheap (no new physics, no new minimization); can run before or parallel to [M5.21.3](m5_21_3_task_details.md).

## Scope (stub level)

| Piece | Content | Notes |
| --- | --- | --- |
| Line tracing | Trace the ½-line cores in 3D on the [M5.21.2b](m5_21_2b_task_details.md) T2 endpoints: per-plane contour-winding centers (the validated instrument; mid-band angle on circles + gap flags) stitched along z into 3D curves | Band-clean on T2 (gap held 0.012-0.038); the braid (pair azimuth 72° → 169° → 135°) becomes directly visible as two winding curves |
| The 3 candidates | Run the trace + render for A, C, B (the electron-family global minimum + the two heavier certified minima), side by side: line count, geometry, braid pitch, core-scale differences | "for humans to better understand, their differences"; B/C cell-scale interior structure stated honestly (lattice-flagged energies) |
| THE CLOSURE READ | His new residual ([Q31 receipt](../m5_question_tracker.md#q31-detail)): the half-lines "should close" into loops. In-box our lines run boundary to boundary: read whether the run-out is a box artifact (do the two lines connect through the far field / at larger N?) + note the spin-axis alignment hypothesis (lines along the would-be spin axis) | The one genuinely new measurement in this task; feeds his neutrino-release picture ([M5.21.6](m5_21_6_task_details.md)) |
| Render route | Headless matplotlib 3D for the repo figures; optionally the engine's 3D renderer for an animation on the OpenWave YouTube channel (the channel already carries "Charged Ring topological defect", the launcher-xperiment animation of the SEEDED ring: label it as the seed configuration when shared, since the relaxed state is the merged object) | Repo docs embed the stills; the animation is channel material |
| Presentation note | Candidate visual framing for the humans-explainer: the relaxed core reads as a central energy bulge + two braided axial line structures, morphologically reminiscent of a bipolar-outflow / quasar-engine cartoon (equatorial bulge + axial jets). If used, it is a MORPHOLOGY-ONLY visual analogy, one sentence, no mechanism claim: the measured core is prolate (z_rms 7-10 vs transverse 2.5-3.4, not an oblate disk), and the lines are static topological defects, not outflows | Grounds assessment + go/no-go at PLAN; outbound phrasing stays terminal-only per the standing rule |

Series rules: any film output on both TRUE templates; independent adversarial audit before anything author-facing; method-note-grade record if the result goes back to the author.

**Gated by**: user "go" (non-gating for the 4D line).
