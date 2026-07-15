"""M5.12 block-18 AUDIT, leg 3: assemble the D1-D4 verdicts, the licensed
phase-D close sentence, the supersede list and the honest paragraph into
data/m5_12_audit_b18.json (reads the two audit-leg JSONs + the decider).

Run:  python m5_12_audit_b18_verdicts.py
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def jload(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def main():
    pencil = jload("m5_12_audit_b18_pencil.json")
    seeds = jload("m5_12_audit_b18_seeds.json")
    decider = jload("m5_12_b18_decider.json")

    out = {
        "task": "M5.12 block 18",
        "role": ("INDEPENDENT ADVERSARIAL AUDIT (block 18): the decider "
                 "machinery, the rule adjudication, the PHASE-D CLOSE "
                 "sentence, the supersede list"),
        "date": "2026-07-09",
        "scripts": ["m5_12_audit_b18_pencil.py", "m5_12_audit_b18_seeds.py",
                    "m5_12_audit_b18_verdicts.py"],
        "instrument_note": ("shat/probe (m5_12_d3a_bvp + m5_12_b14_seeds) as "
                            "the meter (block-11-audit verified) and the b17 "
                            "control_probe zoom (b17-audit verified to "
                            "0.5-1.5% where load-bearing); the independent "
                            "polarization, the true-Gram re-solve, the "
                            "seed-level in-frame battery and the gain "
                            "projection are audit-owned."),
    }

    out["D1_decider_machinery"] = {
        "verdict": ("MIXED: the exact layer is CONFIRMED (probes, "
                    "references, eigensolve, truncation); the model layer "
                    "carries a REFUTED mechanism claim: the 3.275 -> 7.213 "
                    "model-exact gap is NOT S0-quartic nonlinearity, it is "
                    "the decider's identity-Gram proxy (a coding choice); "
                    "outcome-irrelevant after correction"),
        "statement": (
            "(a) Pencil entries re-derived by an independent polarization "
            "(different formula, half the amplitude): Q entries reproduce "
            "to <= 2.6e-4 (exact-quadratic, as the b15 audit found); S "
            "entries reproduce only to 0.6-8.3% because the S-form is "
            "amplitude-contaminated at the polarization scale: acceptable "
            "for a screening model, not quotable as a quadratic form. "
            "(b) The eigensolve reproduces exactly (lam0 rel 0.0, top-5 "
            "coefficients identical) and is truncation-insensitive: tau "
            "1e-4..1e-10 all give model omega 3.2747-3.2748, so whitening/"
            "truncation manufactured nothing. (c) THE GRAM DEFECT: the "
            "decider minimized c'(S + (S_static/a2_star) I)c / c'(-Q)c, "
            "but the 32 members are far from a2-orthonormal (off-diagonal "
            "Gram up to 0.997); the k=0 direction's true a2 content is "
            "c'Mc = 0.294 vs the assumed c'Ic = 0.0246 (12x), so the "
            "static-energy weight was underweighted 12x and the 'model "
            "optimum 3.275' is not a quadratic-model prediction of the "
            "probed objective. With the TRUE Gram the same direction "
            "models at 7.464; exact on-frame at full a2 is 7.899 (genuine "
            "S0 nonlinearity only +5.8%); the zoom to r_target gives "
            "7.213 (-8.7%). At a2_star/100 the true-Gram model matches "
            "the exact probe to 4 digits (70.11 both): the model is "
            "accurate at small amplitude; the published narrative 'the "
            "quadratic model fails at full amplitude' is refuted in "
            "mechanism. (d) The k=0 exact in-frame numbers reproduce to "
            "all printed digits (7.2131 native / 6.1475 rc-matched), and "
            "re-solving the eigenproblem with the true Gram and exact-"
            "probing its top-3 directions finds nothing better (best "
            "native 8.23, best rc-matched 5.51, both worse than the "
            "decider's candidate or the p1 seed): the defect does not "
            "change the outcome, only the story."),
        "evidence": {
            "polarization": pencil["polarization_rederivation"],
            "eig_reproduce": pencil["eig_reproduce"],
            "tau_sweep": pencil["tau_sweep"],
            "gram": pencil["gram"],
            "k0_gram_content": pencil["k0_gram_content"],
            "amplitude_scan": pencil["amplitude_scan"],
            "k0_inframe_reprobe": pencil["k0_inframe_reprobe"],
            "gap_decomposition": pencil["gap_decomposition"],
            "trueGram_candidates_exact": seeds["trueGram_candidates"],
        },
    }

    out["D2_rule_adjudication"] = {
        "verdict": ("ADJUDICATED + RULED: the two references COINCIDE at "
                    "seed level (measured), the pre-registered equal-"
                    "background reference is the right one, and the seed-"
                    "level shape search is SATURATED-AT-THIS-BUDGET "
                    "(marginal): no candidate beats the floor-producing "
                    "seed in both wscale conventions, and the median-gain "
                    "projection of the best candidate lands well above the "
                    "floor; the coded optimizer_saturated = False is a "
                    "knife-edge single-convention reading and is not the "
                    "decision-grade statement"),
        "statement": (
            "Which reference answers 'can shape search find anything the "
            "relax-chain pipeline has not already found': the floor-"
            "producing SEED, because every candidate would be relax-"
            "chained. Measured: p1's seed (the b15-audit rayleigh_opt "
            "state) probes in-frame at 7.5914 native / 5.3840 rc-matched, "
            "numerically the SAME as the pre-registered p1-A1-on-standard-"
            "background reference (7.5955 / 5.3840, 0.05%): the reference "
            "ambiguity dissolves, reference (i) IS the seed benchmark. "
            "Reference (ii), the full relaxed p1 (5.44/5.11), is a relaxed "
            "endpoint and not a seed-level bar. Against the seed "
            "benchmark the decider's best candidate gains 5.0% native "
            "but LOSES 14.2% rc-matched; the audit's true-Gram re-solve "
            "candidates lose in both conventions. Measured in-frame "
            "seed->relaxed gains of the five prior chains: native 7.2, "
            "12.6, 14.6, 18.2, 28.3% (median 14.6); rc-matched -3.3..5.1% "
            "(median 0.5): under rc-matched the seed value nearly IS the "
            "relaxed value. Projecting the best candidate (7.213/6.148) "
            "through those gains: native median 6.16 (floor 5.44; "
            "undercuts only at the single best observed gain, 28.3%, "
            "p1's own chain, giving 5.17); rc-matched 5.83-6.35 (floor "
            "5.11; never undercuts). A relaxed landing below p1 is "
            "therefore IMPLAUSIBLE on every measured trend though not "
            "excluded: the b15 lesson stands that relaxation has "
            "reordered seeds before, and the p1 comparison itself shows "
            "the relax gain lives mostly in background (M0) adaptation "
            "(p1's A1 back on the standard background probes 7.60 vs the "
            "full relaxed 5.44), which no seed-level metric can see. "
            "RULING: seed-level shape search within the probed 32-member "
            "basis is exhausted at this budget; 'optimizer-saturated' is "
            "licensed as a basis-and-instrument-bounded statement with "
            "the relaxation-dynamics caveat, and only a relax chain on "
            "the 7.21 direction could convert 'implausible' into "
            "'measured'."),
        "evidence": {
            "seed_battery": seeds["seed_battery"],
            "projection": seeds["projection"],
            "decider_best": decider["best"],
            "decider_coded_flag": decider["optimizer_saturated"],
        },
    }

    close_sentence = (
        "Phase D closes on a measured endpoint plus a bounded decider, not "
        "on a found orbit: no free-period orbit was found (every chain ends "
        "in an honest progress-rate stall, none at a stationary point, so "
        "the negative is unfound, not nonexistent). Under the standing "
        "fixed-(size, a2) metric (common n32 frame, common r_target, common "
        "first-harmonic a2 = 0.3037, one wscale, orderings quoted only "
        "across the frame battery) the controlled floor is p1 at 5.11-5.61 "
        "at the M5.8 size anchors, 4.4-5.5x above the band, A1/A2-"
        "conditional throughout with the potential-sector gap author-gated. "
        "The block-18 seed-level decider, audit-corrected for its Gram "
        "convention, found no fresh shape direction that beats the floor-"
        "producing seed in both wscale conventions (best candidate 5.0% "
        "better native-only, 14.2% worse rc-matched, projecting to ~6.2 at "
        "the median measured seed-to-relaxed gain, above the floor), so "
        "seed-level shape search within the probed basis is exhausted at "
        "this budget and the b17 'still descending' status is retired, with "
        "the standing caveat that relaxation dynamics have reordered seeds "
        "before and most of the measured relax gain lives in background "
        "adaptation that no seed-level metric can see. Phase D reopens on "
        "any of: a solver rung that converges at the floor (the stalls are "
        "non-stationary); the author sanctioning or refuting the A1/A2 "
        "unit-map assumptions; or any measured seed direction that beats "
        "the floor-producing seed in both conventions (equivalently, one "
        "that plausibly relaxes below p1's 5.44/5.11).")

    out["D3_close_sentence"] = {
        "verdict": "LICENSED (assembled per the D1/D2 rulings)",
        "notes": ("Updates the b17 phase_d_sentence: 'STILL DESCENDING' is "
                  "retired by the decider outcome; the close is now a "
                  "measured seed-level endpoint plus the standing floor and "
                  "distance, with explicit reopening conditions."),
    }
    out["close_sentence"] = close_sentence

    supersede_list = [
        {"stale": "b12: 'if Q2 saturates near -1.2, omega_bal floors at "
                  "~6, the M5.8 band is UNREACHABLE in this seed class'",
         "superseded_by": "b13: the x32 bend was substantially solver "
                          "stall; Q2 never settled; the hypothesis is dead, "
                          "not merely gated"},
        {"stale": "b13: '~18 more doublings at this trend to reach the "
                  "band' extrapolation",
         "superseded_by": "raw-metric trend line, void under the b17 "
                          "standing metric; never a physics claim"},
        {"stale": "b14: 'at the n96 calibration scale the stalls sit "
                  "1.8-2.7x above the band' (also inside the b14 quoted "
                  "honest paragraph) and the older '5-8x'",
         "superseded_by": "b16 audit refuted O1 in every variant; the "
                          "measured controlled bracket is 4.4-5.5x (b17, "
                          "A1/A2-conditional)"},
        {"stale": "b14 N5: 'matched-a2 omega_bal saturates ~9.2-9.5'",
         "superseded_by": "b15/b16 floors passed it (raw 6.99 then 5.44); "
                          "the controlled floor is p1 5.11-5.61"},
        {"stale": "b15: 'the relaxed floor is 6.99 and still falling' and "
                  "the seed floor 8.23 quoted without the frame qualifier",
         "superseded_by": "raw own-frame values; the standing metric quotes "
                          "p1 5.11-5.61 in-frame; 8.23/7.90 only with the "
                          "own-frame qualifier"},
        {"stale": "b15 unit-map memo options O1/O2/O3 as an open decision",
         "superseded_by": "b16 killed O1; b17 measured the map at the "
                          "standing metric: 4.4-5.5x, wscale-convention-"
                          "dominated, A1/A2 author-gated"},
        {"stale": "b16: 'the invariant floor has been the bmix c2/g48 "
                  "lineage (18.2) since block 12', the product ranking "
                  "c2/g48 < f2 < p1 < wd < f1 < p2, and 'no family since "
                  "block 12 advanced the invariant floor' (the two "
                  "retroactive saturation strikes)",
         "superseded_by": "b17 metric adjudication: the product is a "
                          "within-lineage invariant only, void as a cross-"
                          "family ranking; the controlled floor is p1; the "
                          "strikes are void"},
        {"stale": "b16: distance '3.3-4.9x' and bracket '3.2-6.9x'",
         "superseded_by": "b17: 4.4-5.5x, anchor-flat, wscale-dominated"},
        {"stale": "b17: 'STILL DESCENDING, not saturated' and the b17 "
                  "licensed phase_d_sentence + the block-18 fork framing",
         "superseded_by": "the block-18 decider + this audit: seed-level "
                          "search exhausted at this budget; the b18 close "
                          "sentence replaces the b17 sentence"},
        {"stale": "b18 decider JSON: 'optimizer_saturated = false' and the "
                  "docstring/JSON narrative 'the quadratic model fails at "
                  "full amplitude, the optimizer exploited model error'",
         "superseded_by": "audit D1/D2: the coded flag is a knife-edge "
                          "single-convention reading (no two-convention "
                          "gain exists); the model-exact gap is the "
                          "identity-Gram proxy (12x static underweight), "
                          "not amplitude nonlinearity (+5.8%)"},
        {"stale": "b13/b14 raw cross-family omega_bal quotes (deep stalls "
                  "5.81-8.64; g48 5.720 'band approach')",
         "superseded_by": "void cross-family under the standing metric; "
                          "within-lineage statements only"},
        {"stale": "b17 mid-pack internal order (wd/f1/f2) and c2/g48 "
                  "absolute in-frame values",
         "superseded_by": "unresolved/soft (~14% deep-zoom) per the b17 "
                          "audit; not quotable in the close"},
    ]
    out["D4_close_completeness"] = {
        "verdict": ("COMPLETE with the 12-item supersede list below; no "
                    "other phase-D claim in FINDINGS blocks 11-18 survives "
                    "as quotable against the close"),
        "notes": ("Blocks 11 (Q2_mix theorem, corrected arms), 13 (LM + "
                  "zero-mean-energy identity), 14 (loop topology positive) "
                  "carry structural findings that remain valid and are NOT "
                  "superseded; only the listed distance/floor/saturation "
                  "numbers go stale."),
    }
    out["supersede_list"] = supersede_list

    out["honest_paragraph"] = (
        "Block 18's decider is sound where it is exact and wrong where it "
        "is a model: the pencil, eigensolve and truncation are clean "
        "(reproduced to machine precision, tau-insensitive over six "
        "decades), the exact in-frame probes and references reproduce to "
        "all printed digits, but the 'model optimum 3.275' rode an "
        "identity-Gram proxy that underweighted the static energy of the "
        "winning direction 12-fold, so the dramatic model-exact gap was a "
        "bookkeeping artifact, not the claimed full-amplitude nonlinearity "
        "(which measures +5.8%). Correcting the Gram and re-probing its "
        "own top directions changes nothing material: no direction, under "
        "either Gram, beats the seed that produced the p1 floor in both "
        "wscale conventions; the best candidate's 5.0% native-only gain "
        "inverts to -14.2% rc-matched and projects above the floor at the "
        "median measured seed-to-relaxed gain. The p1 seed measurement "
        "also dissolved the reference ambiguity (the equal-background "
        "reference IS the seed benchmark to 0.05%) and exposed the honest "
        "caveat for any future reopening: the relax chains earn most of "
        "their gain through background adaptation invisible at seed level, "
        "so seed-level exhaustion bounds the search strategy, not the "
        "physics. Phase D therefore closes as a bounded, audited negative: "
        "orbit unfound (not nonexistent), controlled floor p1 at 5.11-5.61, "
        "4.4-5.5x above the band, A1/A2-conditional, seed-level shape "
        "search exhausted at this budget, reopening conditions on record.")

    path = os.path.join(DATA, "m5_12_audit_b18.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {os.path.basename(path)}")
    for k in ("D1_decider_machinery", "D2_rule_adjudication",
              "D3_close_sentence", "D4_close_completeness"):
        print(f"[{k}] {out[k]['verdict'][:110]}")


if __name__ == "__main__":
    main()
