# M5.23 convo record

> Companion to [`m5_23_task_details.md`](m5_23_task_details.md) (the VIZ.5 "ellipsoid" visualization). Thread lineage: the viz spec first landed in [`m5_21_convo.md § 2026-07-18 19:44`](m5_21_convo.md) ("one value per 3D angle / one value per 2D angle").

## 2026-07-19: the author's ellipsoid-viz feedback (single ellipsoid per angle + the density warning + the split-vortex ask)

**Context**: the author's reply to a visualization share, forwarded mid-M5.23 run; it sharpens the render spec and names the follow-up animation arc.

Verbatim:

> Looks very nice, but to be more readable I would suggest to use single elipsoid per angle, like at the top of <https://community.wolfram.com/groups/-/m/t/3398814> - where I have emphasized single vortex (because split was too difficult for me - I have seen it some years ago, but somehow rejected mentally as too scary to include) - would be great to make similar animations for split vortices, also for muon and taon.
>
> I suspect its four 1/2-vortices are usually connected forming two loops - hence usually emitting two neutrinos in muon/taon decay ... would be great if making such animation, especially from simulation. Again for visibility it cannot be too dense: ellipsoid field only emphasizing central behavior and vortices.

Decode:

| Point | The author's words | Design consequence |
| --- | --- | --- |
| Single ellipsoid per angle + the author's reference render | "use single elipsoid per angle, like at the top of" the Wolfram post (the author's "Time crystal ϕ⁴ kink" Featured-Contributor post) | CONFIRMS the M5.23 shell design (one glyph per direction û); the reference look is individually distinguishable ellipsoids at moderate density, never a continuous field |
| The density warning | "for visibility it cannot be too dense: ellipsoid field only emphasizing central behavior and vortices" | Default direction count LOWERED to 162 (icosphere subdiv 2) with a density option (42 / 162 / 642); shells stay pinned to defect centers + vortex lines, never space-filling |
| Split vortices, muon / taon | "would be great to make similar animations for split vortices, also for muon and taon" | The Stage C vortex arm is reinforced; the μ/τ SPLIT-vortex animation from simulation is the follow-up arc riding the μ/τ decay task ([M5.21.6](m5_21_6_task_details.md)), not this run |
| The two-loop conjecture | "I suspect its four 1/2-vortices are usually connected forming two loops - hence usually emitting two neutrinos in muon/taon decay" | A pre-registerable read for the μ/τ program (loop-count on the simulated split-vortex state); logged here for [M5.21.6](m5_21_6_task_details.md) planning |
