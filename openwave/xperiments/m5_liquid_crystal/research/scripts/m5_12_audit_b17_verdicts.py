"""M5.12 block-17 ADVERSARIAL AUDIT: verdict assembly.

Consumes m5_12_audit_b17_zoom.json (A1) + m5_12_audit_b17_metric.json
(A2/A3/A4) + m5_12_b17_control.json and writes data/m5_12_audit_b17.json.

Run:  python m5_12_audit_b17_verdicts.py
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def main():
    zoom = json.load(open(os.path.join(DATA, "m5_12_audit_b17_zoom.json")))
    met = json.load(open(os.path.join(DATA, "m5_12_audit_b17_metric.json")))
    ctrl = json.load(open(os.path.join(DATA, "m5_12_b17_control.json")))

    out = {
        "task": "M5.12 block 17",
        "role": ("INDEPENDENT ADVERSARIAL AUDIT (block 17): the "
                 "fixed-(size, a2) control, the metric adjudication, the "
                 "phase-D sentence, the controlled distance factor"),
        "date": "2026-07-09",
        "scripts": ["m5_12_audit_b17_zoom.py", "m5_12_audit_b17_metric.py",
                    "m5_12_audit_b17_verdicts.py"],
        "instrument_note": ("shat/probe (m5_12_d3a_bvp + m5_12_b14_seeds) "
                            "as the meter (block-11-audit verified); the "
                            "zoom re-derivation, variant bounds, budget "
                            "sweep, S0-matching attempt, gain analysis and "
                            "anchor scan are audit-owned."),

        "A1_control_correctness": {
            "verdict": "CONFIRMED (floor-relevant machinery; the guards "
                       "understate deep-zoom error and the mid-pack "
                       "internal order is NOT resolved, as the block "
                       "itself already conceded)",
            "statement": (
                "(a) An independent zoom (physical-coordinate map, proper "
                "even coordinate mirror across the rho axis, LINEAR "
                "RegularGridInterpolator vs the control's cubic "
                "map_coordinates) reproduces the in-frame omega_bal to "
                "0.53-1.46% on all three attack cases including the "
                "cross-grid one: f2 s=1.294 rel 1.46e-2, p1 s=0.888 rel "
                "5.3e-3, g48 native-n48 s=1.498 rel 8.4e-3. (b) The "
                "abs(i_src) axis reflection is an INDEX-space reflection, "
                "not a coordinate mirror (wrong by up to one cell for "
                "rho_target/s < 0.5h), and mode=nearest extrapolates "
                "pinned-edge values for s < 1; both bounded by a 4-variant "
                "spread: p1 (the floor) 0.75%, c2 (deepest zoom, s=2.256) "
                "13.7%. The c2/g48 in-frame values are soft at the ~14% "
                "level; they trail the field by 35-170%, so last place is "
                "robust. (c) The rescale applies the FIRST-harmonic a2 "
                "factor to ALL harmonics (deviating from the battery's "
                "rescale_to, which scales the first harmonic only): "
                "difference 0.09-0.67% on wd/f1/f2/p1/p2/lp (h2 share "
                "1.7e-5..1.7e-3) and 6.7% on c2/g48; no ranking "
                "sensitivity, but the convention should be stated with the "
                "result. (d) GC2's 2.7e-3 round trip does NOT bound the "
                "control's deepest zooms: my own round trip at s=2.25 "
                "errs 1.87e-2 (7x the guard), and the smallest adjacent "
                "ranking gap is 3.0e-3 (inside the wd/f1/f2 cluster): the "
                "cluster's internal order is unresolved by the instrument "
                "(the block's own frame-dependence statement is the "
                "correct wording). Every gap involving p1 is >= 16.8%, "
                "9x the worst measured error: the FLOOR identification "
                "is resolved."),
            "evidence": {"independent_rederivation": zoom["cases"],
                         "variant_spreads": zoom["variants"],
                         "rescale_convention": zoom["rescale_convention"],
                         "gc2_vs_gaps": zoom["gc2"]},
        },

        "A2_metric_adjudication": {
            "verdict": "ADJUDICATED: fixed-(size, a2) in-frame probing is "
                       "the standing metric for cross-family claims; raw "
                       "omega_bal is VOID cross-family; the product "
                       "omega_bal*r_mean survives only as a "
                       "WITHIN-LINEAGE invariant",
            "statement": (
                "The three frames answer three different questions. Raw "
                "omega_bal at matched total a2 but native sizes answers "
                "'what root did this chain reach in its own frame': "
                "size-dominated (the b16 audit's c2->g48 disqualification, "
                "33.8% raw at 0.2% invariant, stands). The product at "
                "native states answers 'which lineage is best per unit "
                "size': scale-invariant but amplitude-DENSITY-confounded "
                "(implied a2 at common radius spans 0.24-1.55; the b16 "
                "audit itself predicted amplitude matching would move p1 "
                "to or below f2, and the control confirmed it). The "
                "phase-D question, 'is there a shape in this class whose "
                "balance root approaches the band at a GIVEN object scale "
                "and amplitude budget', is answered by exactly one of the "
                "three: the fixed-(size, a2) frame. On normalization: at "
                "COMMON size, total a2 and a2 density are the same budget "
                "(common frame volume): the distinction dissolves. An "
                "energy normalization is ILL-POSED cross-family here: the "
                "harmonic S0 share is negative and non-monotone in "
                "amplitude, and the zoomed static M0 energies differ by "
                "3.5x (c2/g48 164 vs f2 46 at r=4.77 native), so a common "
                "total-S0 target is unreachable near the operating points "
                "(measured: only f2+wd reachable native, f2+bmix "
                "rc-matched). The well-posed robustness check is the "
                "common-a2-budget sweep: at x0.5/x1/x2 the standing "
                "budget, in both wscales, p1 is the floor in ALL SIX "
                "orderings (and in all four control frames): the ruling "
                "is budget-robust. Mid-pack order shuffles with budget "
                "(at x2 native the cluster compresses to 5.29-5.62 vs p1 "
                "5.12): only the floor and the bmix-last statements are "
                "licensed."),
            "evidence": {"budget_sweep": met["A2_budget_sweep"],
                         "s0_matching_illposed": met["A2_energy_ranking"]},
        },

        "A3_phase_d_descent": {
            "verdict": "(ii) STILL DESCENDING: the controlled floor "
                       "advanced monotonically bmix -> wd -> f -> p1 in "
                       "all four frames; at most ONE sub-5% step (wd->f), "
                       "so the pre-registered two-strike saturation rule "
                       "does NOT close; the descent rate is bounded and "
                       "NOT accelerating: ~6.4-6.8 further family-scale "
                       "advances at the observed median rate stand "
                       "between the floor and the band",
            "statement": (
                "Controlled per-family floor gains (all four frames): "
                "bmix->wd 27.3-62.9%, wd->f 4.2-9.5%, f->p1 19.4-23.6%. "
                "Re-binding the pre-registered rule (two consecutive "
                "families < 5%) onto the standing controlled metric: "
                "wd->f struck in one frame (4.2%) and sat at 5.4-5.8% in "
                "two others; f->p1 at ~20% is unambiguously not a strike. "
                "One strike maximum: saturation is NOT established, and "
                "the b16-audit-era 'no family since block 12 advanced the "
                "floor' is INVERTED in the controlled frame. Honest rate: "
                "the gains oscillate rather than decay monotonically, so "
                "no extrapolation is licensed as a prediction; as a "
                "scale, the p1 floor (5.11-5.61) needs a further factor "
                "of 4.4-4.9 to the band top (1.15), i.e. ~6.4-6.8 "
                "consecutive families each gaining the median observed "
                "21%, or ~29 at 5%. The best-gain extrapolation (1.5 "
                "families) is void: it rides the inflated bmix starting "
                "point. Two honesty flags: (1) the p1 gain came from the "
                "b15 audit's 72-direction Rayleigh OPTIMIZATION, not a "
                "hand family: the cheap-family reservoir is visibly "
                "thinning; (2) the fastest single decider if the user "
                "wants a hard saturation call: run the Rayleigh "
                "optimization of omega_bal DIRECTLY in the controlled "
                "frame (optimize at fixed size AND a2, relax, re-probe); "
                "if the controlled-frame optimum lands within ~5% of p1, "
                "the class is optimizer-saturated."),
            "evidence": met["A3_gains"],
        },

        "A4_controlled_distance": {
            "verdict": "CONFIRMED and completed: 4.4-5.1x at the "
                       "breathing-window anchors as published; the FULL "
                       "honest bracket across every defensible M5.8 "
                       "anchor (early window 3.47, breathing 4.61/4.77, "
                       "settled 4.941, static core 2.628) x both wscales "
                       "is 4.4-5.5x; A1/A2-conditional",
            "statement": (
                "Re-derived with the control machinery at five anchors x "
                "two wscales: p1's controlled root spans only 5.10-5.89 "
                "across anchor radii 2.63-4.94: the controlled comparison "
                "is remarkably ANCHOR-ROBUST (omega_bal at fixed a2 is "
                "nearly flat in size for p1), so the window-drift caveat "
                "that spread the b16 bracket to 3.2-6.9x collapses to "
                "4.4-5.5x under the standing metric; the residual spread "
                "is dominated by the wscale choice (native vs rc-matched), "
                "i.e. by the instrument convention, not the window. "
                "Conditionality stands in full: A1 as corrected by the "
                "b16 audit (M5.8 r_mean lives in x-units, h=0.522, not "
                "lattice cells; the control's r_target identification "
                "assumes 1 BVP h-unit = 1 M5.8 x-unit) and A2 (c=1 "
                "verified in the shared curvature sector only; the "
                "potential sectors differ structurally, beta*u^2 vs "
                "wscale*V_4D, so 'same Lagrangian family' is NOT "
                "established and the band frequency is partly set by "
                "restoring terms the codes do not share). Both remain "
                "author-gated; every factor here is conditional on them."),
            "evidence": met["A4_distance"],
        },

        "metric_ruling": (
            "The standing metric for every cross-family M5.12 claim is "
            "the fixed-(size, a2) in-frame probe (common n32 frame, "
            "common object radius, common first-harmonic a2 budget, one "
            "wscale), with orderings quoted only where they hold across "
            "the frame battery AND the x0.5/x2 budget sweep. Raw "
            "omega_bal comparisons across families are void (size-"
            "dominated); the product omega_bal*r_mean is retained only "
            "as a within-lineage scale invariant (0.2% on c2/g48), not a "
            "cross-family ranking. Rationale: the phase-D question fixes "
            "both the object scale and the amplitude budget by its own "
            "wording, and the control is the only frame that fixes both; "
            "its floor identification is robust at 9x the worst measured "
            "instrument error and across a 4x budget range."),

        "phase_d_sentence": (
            "Phase D found no free-period orbit (every chain ends in an "
            "honest progress-rate stall, none at a stationary point); "
            "under the standing fixed-(size, a2) metric the family "
            "search is STILL DESCENDING, not saturated (controlled floor "
            "bmix -> wd -> f -> p1, one sub-5% step, p1 = 5.11-5.61 at "
            "the M5.8 sizes, 4.4-5.5x above the band, A1/A2-conditional), "
            "so a close here is a bounded-resource decision, not a "
            "measured endpoint."),

        "honest_paragraph": (
            "Block 17's control is sound where it carries load: an "
            "independent zoom reproduces every floor-relevant number to "
            "1.5%, and the p1-floor identification survives a 4-variant "
            "interpolation attack, a rescale-convention attack, and a 4x "
            "amplitude-budget sweep, while the wd/f1/f2 internal order "
            "and the c2/g48 absolute values (soft at ~14% under deep "
            "zoom) stay unresolved and should not be quoted. The "
            "adjudicated metric is fixed-(size, a2): under it the b16 "
            "product-metric strikes are void, the family floor has "
            "descended monotonically through four family generations, "
            "and the pre-registered saturation rule has at most one "
            "strike, so 'saturated' is not a licensed word. The "
            "controlled floor sits 4.4-5.5x above the M5.8 band across "
            "every defensible size anchor, a bracket now dominated by "
            "the instrument's wscale convention rather than the M5.8 "
            "window choice, and conditional throughout on the "
            "author-gated A1/A2 unit-map assumptions (the potential "
            "sectors of the two codes are structurally different). The "
            "orbit remains unfound, not nonexistent: the descent rate "
            "(~20% per family where it moves, with the gains coming "
            "increasingly from optimization rather than hand families) "
            "puts the band ~6-7 family-scale advances away at the "
            "observed rate."),
    }

    path = os.path.join(DATA, "m5_12_audit_b17.json")
    json.dump(out, open(path, "w"), indent=2)
    print(f"json -> {os.path.basename(path)}")
    for k in ("A1_control_correctness", "A2_metric_adjudication",
              "A3_phase_d_descent", "A4_controlled_distance"):
        print(f"{k}: {out[k]['verdict'][:100]}")


if __name__ == "__main__":
    main()
