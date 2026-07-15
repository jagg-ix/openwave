"""M5.12 block 16 ADVERSARIAL AUDIT: verdict assembly.

Reads the three leg outputs (endpoints, rmean, unitmap_attack), recomputes
the two small controls inline (seed-level r_mean for the growth
decomposition; omega_bal amplitude sensitivity at fixed shape), and writes
the final data/m5_12_audit_b16.json.

Run:  python m5_12_audit_b16_verdicts.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_12_d3a_bvp import shat, x_pack                                     # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_audit_b16_rmean import load_state, radius_observables           # noqa: E402


def wbal(X, h, wsc):
    s0 = shat(X, 0.0, h, wsc)
    q2 = s0 - shat(X, 1.0, h, wsc)
    return float(np.sqrt(s0 / -q2)) if (q2 < 0 and s0 > 0) else None


def main():
    legs = {k: json.load(open(os.path.join(DATA, f"m5_12_audit_b16_{k}.json")))
            for k in ("endpoints", "rmean", "unitmap_attack")}
    wsc = wscale_at(32, 64, 1.0, 8 * 32 / 96)

    # control 1: seed-level radii (growth decomposition)
    seed_r = {}
    for tag, p in (("p1_seed", "m5_12_b16_seed_rayleigh_opt_n32.npz"),
                   ("p2_seed", "m5_12_b16_seed_aniso_r4z1_n32.npz"),
                   ("f2_seed", "m5_12_b15_seed_shell_k1_n32.npz"),
                   ("c2_seed", "m5_12_d3b_breather_n32_c2seed_state.npz")):
        X = load_state(os.path.join(DATA, p))
        seed_r[tag] = radius_observables(X)["r_amp2"]

    # control 2: omega_bal amplitude sensitivity at fixed shape
    amp_sens = {}
    for tag, p in (("f2", "m5_12_b12_hard_f2_1_state.npz"),
                   ("c2", "m5_12_b12_hard_c2_1_state.npz")):
        X = load_state(os.path.join(DATA, p))
        row = {}
        for k in (0.7, 1.0, 1.5, 2.26):
            Xs = {"M0": X["M0"], "A": [a * k for a in X["A"]],
                  "B": [b * k for b in X["B"]]}
            row[f"a2_x{k*k:.2f}"] = wbal(Xs, 1.0, wsc)
        amp_sens[tag] = row

    rows = {r["tag"]: r for r in legs["rmean"]["rows"]}
    out = {
        "task": "M5.12 block 16",
        "role": ("INDEPENDENT ADVERSARIAL AUDIT (block 16): chains p1/p2, "
                 "growth discrimination, saturation rule, O2 unit map, "
                 "probe integrity"),
        "date": "2026-07-09",
        "scripts": ["m5_12_audit_b16_endpoints.py",
                    "m5_12_audit_b16_rmean.py",
                    "m5_12_audit_b16_unitmap_attack.py",
                    "m5_12_audit_b16_verdicts.py"],
        "instrument_note": ("shat/residual (m5_12_d3a_bvp) as the meter "
                            "(block-11-audit verified); r_mean variants, "
                            "channel split, a2, J^T F, Cauchy step, zoom "
                            "tests and the M5.8 box asymptote are "
                            "audit-owned."),
        "controls": {"seed_r_amp2": seed_r,
                     "omega_bal_amplitude_sensitivity": amp_sens},
        "claims": {},
    }

    ep = {e["tag"]: e for e in legs["endpoints"]["endpoints"]}
    out["claims"]["C1_chains"] = {
        "verdict": "CONFIRMED",
        "statement": (
            "Both endpoints reproduce exactly from the state files: p1 "
            "omega_bal 5.5440 (pub 5.5440), p2 6.5717 (pub 6.5717); a2 "
            "conserved to <2e-8 rel; H_mean/H_swing ~ 1e-15/1e-13 (zero by "
            "construction verified); p1 mix share 1.0000, p2 0.9980; "
            "H_swing/S0 1.984/1.992 honest. |F| recomputed from the "
            "float32 states is 194.7/196.4 vs published 169.7/182.0 (8-15% "
            "high): consistent with the measured landscape stiffness "
            "(|J^T F|/|F| ~ 1.3e7, a float32 truncation moves |F| by ~10%), "
            "same class as the block-14 audit's 1-2% at lower stiffness. "
            "NOT stationary points, independently verified: |J^T F| = "
            "2.6e9 (p1) / 2.0e9 (p2), and the audit's own Cauchy step "
            "descends 9.6% (p1) / 5.6% (p2) in |F| from the reloaded "
            "states. 'Honest progress-rate stalls' is the correct wording."),
        "evidence": {
            "p1": ep["p1"]["recomputed"], "p2": ep["p2"]["recomputed"],
            "p1_cauchy": ep["p1"]["cauchy_trials"],
            "p2_cauchy": ep["p2"]["cauchy_trials"]},
    }

    out["claims"]["C2_growth_discrimination"] = {
        "verdict": ("MIXED (arithmetic + f2-first ranking CONFIRMED and "
                    "robust to radius observable; the GROWTH mechanism "
                    "wording REFUTED; the f2-floor identification REFUTED "
                    "by the block's own excluded endpoints; the ranking is "
                    "amplitude-confounded at measured ranking-breaking "
                    "size)"),
        "statement": (
            "CONFIRMED: r_amp2 reproduces exactly (p1 5.371, f2 3.686), "
            "the size-corrected ranking at 4.77 reproduces to the digit "
            "(f2 5.400 < p1 6.242 < wd 6.454 < f1 8.585 < p2 9.248), "
            "products 25.76/29.78; the order is unchanged under r_rms and "
            "r_50, and f2 stays first under all four radius observables "
            "(under linear-amplitude weight p1 drops to 4th: its diffuse "
            "halo). The product invariant is validated: c2-vs-g48 lineage "
            "products agree to 0.2% (18.26 vs 18.22) and audit zoom tests "
            "(n32->n24/n48, f2 and p1) hold it to 4-6%. REFUTED "
            "(mechanism): the p1 object did NOT grow during relaxation; "
            "the seed already had r_amp2 5.370 and the endpoint has 5.371. "
            "The chain improved omega_bal 29.8% AT FIXED SIZE (invariant "
            "product 42.4 -> 29.8, genuine within-size progress); p1's raw "
            "advantage over f2 is inherited seed size, not relaxation "
            "growth. REFUTED (floor identification): applying the block's "
            "own size correction to the excluded comparable endpoints puts "
            "c2 at 3.83 and g48 at 3.82 at r = 4.77, far below f2's "
            "5.400; same a2_star, same solver, comparable stall quality "
            "(F_rel 0.019 vs 0.014). f2 is not the invariant floor of the "
            "program's endpoint set. CAVEAT (cuts both ways): the "
            "common-radius construction is amplitude-uncontrolled; the "
            "implied a2 at r = 4.77 spans 0.24 (p1) to 1.55 (c2), and the "
            "directly measured amplitude sensitivity at fixed shape "
            "(f2: omega_bal 10.12 at 0.49x a2, 6.99 at 1x, 5.03 at 2.25x) "
            "exceeds the ranking margins; an amplitude-matched estimate "
            "moves p1 to or below f2. No cross-family invariant ranking "
            "is settled until a fixed-(size, a2) control is run."),
        "evidence": {
            "endpoint_radii": {t: rows[t]["r_amp2"] for t in rows},
            "rankings": legs["rmean"]["rankings"],
            "lineage": legs["rmean"]["lineage"],
            "zoom": legs["rmean"]["zoom"],
            "seed_radii": seed_r,
            "c2_g48_at_4p77": {
                "c2": rows["c2"]["omega_bal"] * rows["c2"]["r_amp2"] / 4.77,
                "g48": rows["g48"]["omega_bal"] * rows["g48"]["r_amp2"]
                / 4.77},
            "amplitude_sensitivity": amp_sens},
    }

    out["claims"]["C3_saturation_rule"] = {
        "verdict": ("ADJUDICATED: the rule binds on the INVARIANT metric; "
                    "block 16 is a no-gain strike; applied consistently "
                    "the invariant floor has not advanced since block 12"),
        "statement": (
            "Raw omega_bal is disqualified as the rule's metric by "
            "measurement: the same-lineage pair c2 -> g48 shows a 33.8% "
            "raw 'gain' at 0.2% invariant-product change (pure "
            "kinematics), and the pancake seeds bake size into the family "
            "(the p2 seed is a 4x-wide gaussian), so a raw-metric rule is "
            "gameable by seeding ever-larger objects. Binding the "
            "pre-registered rule on the invariant metric is therefore the "
            "only defensible reading, and it must be logged as a "
            "mid-course amendment (the rule was pre-registered on raw). "
            "Under it: the pancake family's best invariant number (p1 "
            "29.78) does not beat the standing f2 25.76, so block 16 is a "
            "strike. Consistency then also forces the c2/g48 endpoints "
            "into the comparison, where the invariant floor is 18.2 "
            "(bmix, block 12) and NO family since (wd 30.8, f1 41.0, f2 "
            "25.8, p1 29.8, p2 44.1) has advanced it: the rule fired "
            "retroactively at block 15, not 'strike 1' now. One control "
            "is owed before declaring hard saturation: the invariant is "
            "amplitude-confounded (see C2), so an amplitude-matched "
            "re-ranking (fixed size AND fixed a2) is the next gate."),
        "headline_sentence": (
            "Block 16 headline: in the size-invariant metric the pancake "
            "family did not advance the floor (strike, and retroactively "
            "no invariant-floor advance since the block-12 bmix lineage: "
            "the raw 'floor still falling' narrative was rescaling "
            "kinematics); hard 'saturated' awaits one amplitude-matched "
            "control."),
    }

    out["claims"]["C4_unit_map"] = {
        "verdict": ("MIXED (arithmetic CONFIRMED; O1 1.8-2.7x stays "
                    "unfound in every variant; 'replaces the identity "
                    "reading 6.1-6.5x' WEAKENED: it survives window "
                    "honesty; floor identification moves the number)"),
        "statement": (
            "(a) Observable mismatch: measured NEGLIGIBLE on the M0 side. "
            "The BVP time-average of ||M(t)-M_ref||^2 equals dc2 + amp2/2 "
            "with dc2 = ||M0_end - M0_seed||^2 carrying < 0.5% of the "
            "weight: r_dep 3.685 vs r_amp2 3.686 (f2). The M5.8 core "
            "exclusion (r <= 2 RC = 1.6) raises the matched-mask BVP "
            "radius ~4% (f2 3.686 -> 3.840), pushing the factor slightly "
            "UP; the claimed factor is conservative on this axis. (b) "
            "Window drift: the strong attack. M5.8 r_mean(dep) drifts "
            "3.47 -> 4.77 over t 4-48 while the uniform-weight asymptote "
            "of the wide mask is 5.07: the late-window value sits 81% of "
            "the way to full delocalization, so it measures the heating "
            "background as much as the breather; earlier windows are "
            "equally defensible and give (f2 floor) up to 6.9x. Honest "
            "motion-window spans: f2 4.7-6.9x, c2 3.3-4.9x. The claimed "
            "4.5-5.2x is the late-window low edge. 'Replaces the identity "
            "reading (6.1-6.5x)' does not survive: 6.1-6.5 lies inside "
            "the f2-floor honest span. 'Refutes the O1 1.8-2.7x' "
            "survives: the global minimum over every probed variant "
            "(floor x window x static anchors x masks) is 3.2x, no "
            "overlap. (c) Static anchors do not change the verdict class "
            "(seed 2.628 gives 8.5-9.2x, settled 4.941 gives 4.5-4.9x; "
            "all 'several x above band'). (d) A1/A2 from source reading: "
            "the unitmap docstring mislabels M5.8 r_mean as 'lattice "
            "cells'; it is in x-units (box [-6,6]^3, h = 0.522). Harmless "
            "arithmetically because the factor is a ratio of "
            "dimensionless omega*r products, which needs only A2 (c = 1 "
            "in each code's own units), and c = 1 IS verified in the "
            "curvature sector of both codes (M5.8 2c1: T and U carry "
            "equal coefficients 2/2; BVP d3a: 4/4). BUT the potential "
            "sectors differ structurally: M5.8 2h evolves with +beta u^2 "
            "(beta = 1.558) and no V_4D, the BVP carries wscale*V_4D "
            "(0.034) and no beta u^2, so 'same 4D Lagrangian family' is "
            "NOT established; the band frequency is partly set by "
            "restoring terms the two codes do not share. The size of that "
            "correction is not decidable from source reading; every "
            "factor above is conditional on it. Provenance nit: the "
            "docstring's 'kicked 4.61/4.64' are R2-seed values; kicked "
            "late-window is 4.69/4.74 (numerically immaterial)."),
        "evidence": {
            "bvp_weight_variants": legs["unitmap_attack"]["rows"],
            "m58_box": legs["unitmap_attack"]["m58_box"],
            "factor_spans": {
                "f2_motion_windows": [4.70, 6.94],
                "c2_motion_windows": [3.33, 4.92],
                "global_min_all_variants": 3.21,
                "claimed": [4.53, 5.22]}},
    }

    sd = {s["family"]: s for s in legs["endpoints"]["seeds"]}
    out["claims"]["C5_probe_integrity"] = {
        "verdict": "CONFIRMED",
        "statement": (
            "Anchors reproduce from the saved seed npz to < 3e-9 rel "
            "(iso (1,1) 11.0306, (2,2) 8.6194); the assembled rayleigh_opt "
            "seed probes 7.8955 under the standing matched-a2 convention "
            "(3.5e-9 rel from the published 7.8955); a2_star recomputed "
            "0.303724649 from the c2seed reference; an audit-owned "
            "re-forge of the p2 seed (r4z1, own formula) lands on 8.0577 "
            "to 4 digits. The 16-point grid is internally consistent."),
        "evidence": {"seed_checks": legs["endpoints"]["seeds"],
                     "reforge": legs["endpoints"]["reforge"]},
    }

    out["honest_paragraph"] = (
        "Block 16 established, calibration-relative (n32, matched a2 = "
        "0.3037, hedgehog-calibrated wscale): a 16-point anisotropic probe "
        "grid whose numbers reproduce exactly; two honest progress-rate "
        "stalls (p1 5.5440, p2 6.5717) that are demonstrably not "
        "stationary points; and the correct insight that raw omega_bal "
        "comparisons across families are size-dominated (the product "
        "omega_bal * r_mean is invariant to 0.2% within a lineage). What "
        "it got wrong: p1's radius was inherited from the Rayleigh seed, "
        "not grown in relaxation (the chain improved the invariant 29.8% "
        "at fixed size), and f2 is not the invariant floor once the "
        "block's own c2/g48 endpoints are scored by the same rule (they "
        "sit at 18.2 vs f2's 25.8, meaning no family since block 12 has "
        "advanced the invariant floor); the ranking additionally carries "
        "an unresolved amplitude confound of ranking-breaking size. The "
        "O2 unit map, WITH its A1/A2 conditionality (c = 1 verified in "
        "the shared curvature sector, but the potential sectors differ: "
        "beta u^2 vs wscale V_4D, so 'same Lagrangian family' is "
        "unconfirmed), gives a floor 3.2-6.9x above the M5.8 band across "
        "defensible floor/window choices: the block-14 n96-anchor reading "
        "(1.8-2.7x) stays unfound in every variant, but the claimed "
        "4.5-5.2x is the late-window low edge of that bracket, and the "
        "identity reading (6.1-6.5x) is inside it, not replaced. No "
        "free-period orbit has been found; none has been shown "
        "nonexistent.")

    out["saturation_adjudication"] = {
        "ruling": out["claims"]["C3_saturation_rule"]["statement"],
        "block_headline": out["claims"]["C3_saturation_rule"][
            "headline_sentence"]}

    path = os.path.join(DATA, "m5_12_audit_b16.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"verdicts -> {os.path.basename(path)}")
    for k, v in out["claims"].items():
        print(f"  {k}: {v['verdict'][:80]}")


if __name__ == "__main__":
    main()
