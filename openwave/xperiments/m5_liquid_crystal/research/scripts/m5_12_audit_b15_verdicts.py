"""M5.12 block-15 ADVERSARIAL AUDIT: assemble the per-claim verdicts into
data/m5_12_audit_b15.json from the three probe JSONs
(m5_12_audit_b15_reprobe.json, _rayleigh.json, _stall.json).

Run:  python3 m5_12_audit_b15_verdicts.py
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def j(name):
    return json.load(open(os.path.join(DATA, name)))


rp = j("m5_12_audit_b15_reprobe.json")
ry = j("m5_12_audit_b15_rayleigh.json")
st = j("m5_12_audit_b15_stall.json")

pen = ry["sections"]["pencil"]
nl = ry["sections"]["nonlinearity"]
wa = ry["sections"]["weighted_a2"]
hr = ry["sections"]["harmonic_relabel"]
p4 = rp["sections"]["p4_sweep"]
ep = rp["sections"]["p2_endpoints"]
ids = rp["sections"]["identities"]

full_best = pen["full"]["best_exact"]
d1_best = pen["D1_only"]["best_exact"]
w_full_quad = full_best.get("omega_quad")
w_full_exact = full_best.get("omega_exact_at_a2star")
w_d1_quad = d1_best.get("omega_quad")
w_d1_exact = d1_best.get("omega_exact_at_a2star")
indef = any(r["indefinite_P"] for r in pen["full"]["per_tau"])
floor_claim = 8.2348

# ---------------- P1 ----------------
below = (w_full_exact is not None and w_full_exact < floor_claim * 0.99)
p1_verdict = (
    "REFUTED as a class floor (the sweep arithmetic itself is CONFIRMED): "
    "8.23 is the floor of the 23-profile isotropic-radial slice, not of "
    "the mixing class. The audit's generalized-Rayleigh minimization over "
    "a 72-vector basis (the claimant's profiles PLUS single-component, "
    "0phi, swapped, z-odd, z-anisotropic, spatial-block, (0,0) and random "
    f"directions) finds omega_bal = {w_full_exact:.4f} at the SAME matched "
    "a2 and calibration, verified by exact Shat probe at full amplitude; "
    "the winning direction is a z-flattened (pancake) anisotropic mix "
    "(aniso 3x1 / 4x2 dominated), a direction family the isotropic sweep "
    "cannot see. Linear combinations WITHIN the claimant's own 23-profile "
    f"span already dip to {w_d1_exact:.4f}. The 'interior floor' wording "
    "survives only for the probed 1-D width scans."
) if below else (
    "CONFIRMED within resolution of a 72-direction Rayleigh-quotient "
    "attack: the class optimum at matched a2 is "
    f"{w_full_exact if w_full_exact else float('nan'):.4f} vs the "
    "claimed 8.23; no probed direction class undercuts materially."
)
P1 = {
    "verdict": ("REFUTED (as a class floor; slice arithmetic CONFIRMED)"
                if below else "CONFIRMED (within the probed attack basis)"),
    "statement": p1_verdict,
    "evidence": {
        "claimant_floor": floor_claim,
        "rayleigh_full_basis": full_best,
        "rayleigh_full_per_tau": pen["full"]["per_tau"],
        "P_indefinite_seen": indef,
        "rayleigh_D1_slice": d1_best,
        "nonlinearity_check_P1b": {
            "q2_eps_over_epshalf_target_4": nl["q2_eps_over_epshalf"],
            "rows": nl["rows"],
            "reading": "Q2 is quadratic to 6e-4 at full amplitude "
                       "(ratio 3.9983 vs 4); the S0 quartic part shifts "
                       "omega_bal by ~4% on the floor shape (quad model "
                       "7.894 vs exact 8.235) and by ~20% on optimized "
                       "directions: quadratic-model floors must be exact-"
                       "probed before they count"},
        "a2_convention_P1c": {
            "top6_plain": wa["top6_plain"],
            "top6_weighted": wa["top6_weighted"],
            "reading": "cell-weighted amplitude matching REORDERS the "
                       "leaderboard: the floor identity is convention-"
                       "relative"},
        "harmonic_relabel_hole": hr,
    },
}

# ---------------- P2 ----------------
rows = {r["tag"]: r for r in ep}
strows = {r["tag"]: r for r in st["rows"]}
gn_desc = {t: strows[t]["gn_drop_rel"] for t in strows}
p2_conf = all(rows[t]["rel_omega"] < 2e-4 for t in rows) and \
    all(rows[t]["a2_rel_err_vs_star"] < 1e-6 for t in rows)
P2 = {
    "verdict": "CONFIRMED (arithmetic exact; 'stall' = progress-rate stall,"
               " descent still available, consistent with the b14 audit)",
    "statement": (
        "Both new endpoints verify exactly on the instrument: omega_bal "
        f"f1 {rows['f1_rgauss']['omega_re']:.4f} / f2 "
        f"{rows['f2_shell']['omega_re']:.4f} (claims 7.3755 / 6.9869), "
        "H_mean/S0 at machine zero, a2 conserved by the hard retraction to "
        "float32 storage precision, H_swing/S0 = 1.99 both, and the "
        "seed-to-relaxed ORDERING SWAP (seed rgauss < shell, relaxed shell "
        "< rgauss) is real. The endpoints are NOT stationary points: "
        f"|JtF|/|F| ~ 2e6 and an independent damped GN step still descends "
        f"(f2 {gn_desc.get('f2_shell', 0)*100:.2f}%, f1 "
        f"{gn_desc.get('f1_rgauss', 0)*100:.2f}%), so 'floor' means "
        "'progress-rate stall of this solver', exactly as the b14 audit "
        "already established for the older stalls."),
    "evidence": {"endpoints": ep, "stall_probes": st["rows"],
                 "identity_spot_checks": ids,
                 "ordering_swap": {
                     "seed": {"rgauss_k2": 8.2348, "shell_k1": 8.2676},
                     "relaxed": {"rgauss_k2": rows["f1_rgauss"]["omega_re"],
                                 "shell_k1": rows["f2_shell"]["omega_re"]}},
                 "scale_covariance_note":
                     "not independently rerun (needs an n48 chain, ~hours); "
                     "b14 audit N3 verdict stands: scale reading holds only "
                     "under per-grid wscale recalibration"},
}
if not p2_conf:
    P2["verdict"] = "MIXED (see evidence)"

# ---------------- P3 ----------------
P3 = {
    "verdict": "WEAKENED (no saturation evidence; the family floor is "
               "open-ended downward on the audit's own probes)",
    "statement": (
        "The relaxed floor has dropped monotonically with every newly "
        "probed shape family (bmix 8.64 -> wide 7.455 -> rgauss 7.376 / "
        "shell 6.987 at the same a2 and grid) and the gains are NOT "
        "demonstrably saturating; the block's own ordering swap shows the "
        "seed map cannot certify a relaxed floor. The audit's Rayleigh "
        f"direction ({w_full_exact:.3f} at seed level vs the 8.23 seed "
        "floor) shows the SEED family itself is still open downward, so "
        "6.99 is an upper bound on the class floor, not a floor. Any band "
        "comparison additionally stays blocked pending the unit map "
        "(n32-calibrated numbers rescale by the block's own 1/L reading)."),
    "evidence": {
        "relaxed_floor_trend_matched_a2": [
            {"block": 13, "family": "bmix", "w_end": 8.6377},
            {"block": 14, "family": "wide_rz", "w_end": 7.4546},
            {"block": 15, "family": "rgauss_k2", "w_end": 7.3755},
            {"block": 15, "family": "shell_k1", "w_end": 6.9869}],
        "seed_floor_undercut_by_audit": w_full_exact,
        "probe_chain": "not run (seed-level evidence decisive; a bounded "
                       "chain from the audit optimum is the natural block-16"
                       " follow-up)"},
}

# ---------------- P4 ----------------
P4 = {
    "verdict": "CONFIRMED",
    "statement": (
        "All 23 sweep rows reproduce from the saved seed npz files on an "
        "independent reprobe: worst relative deviation "
        f"{max(p4['worst_rel'].values()):.1e} (float32 storage level) on "
        "omega_bal/S0/Q2/a2; the floor ranking matches row for row; the "
        "three b14 anchors match the b14 JSON exactly; the quadratic "
        "identity Shat(w) = S0 - w^2 Q2 and H_mean(omega_bal) = 0 hold at "
        "1e-14 or better on spot checks."),
    "evidence": {"worst_rel": p4["worst_rel"],
                 "rank_match": p4["rank_match"],
                 "my_floor_ranked": p4["my_floor_ranked"],
                 "anchors": rp["sections"]["anchors"]},
}

honest = (
    "Block 15 mapped the omega_bal landscape of a 23-point isotropic "
    "(profile, width) slice of first-harmonic 0i-mixing seeds at n32 "
    "calibration and matched a2 = 0.3037: within that slice the seed "
    "floor is ~8.23 (rgauss k2, displaced shell close behind), the sweep "
    "arithmetic is exact, and two bounded relax chains produced new "
    "progress-rate stalls at omega_bal 7.376 and 6.987 (H_swing/S0 ~ 2, "
    "|F| ~ 187-194 on reprobe, not stationary points), swapping the seed "
    "ordering. The audit's generalized-Rayleigh minimization over a "
    "72-direction basis shows the slice floor is not the class floor: a "
    "z-flattened anisotropic mix reaches omega_bal = "
    f"{w_full_exact:.2f} at seed level under the same convention (exact "
    "Shat probe at full amplitude), and the relaxed floor has dropped "
    "with every family probed so far, so 6.99 is an upper bound that is "
    "still moving, not a converged floor. The floor is also convention-"
    "relative: cell-weighted amplitude matching reorders the leaderboard, "
    "and moving the same shape to the second harmonic exactly halves "
    "omega_bal while being invisible to the a2_free convention. No "
    "comparison to any band reading is licensed at this calibration until "
    "the unit map is fixed; every negative here is an 'unfound at this "
    "budget', not a nonexistence."
)

OUT = {
    "task": "M5.12 block 15",
    "role": "INDEPENDENT ADVERSARIAL AUDIT (block 15): shape-family floor "
            "map, relax chains f1/f2, sweep integrity",
    "date": "2026-07-09",
    "scripts": ["m5_12_audit_b15_reprobe.py", "m5_12_audit_b15_rayleigh.py",
                "m5_12_audit_b15_stall.py", "m5_12_audit_b15_verdicts.py"],
    "instrument_note": "shat/residual (m5_12_d3a_bvp) as the meter "
                       "(block-11-audit verified); seeds, forms, pencil, "
                       "flattenings and GN step are audit-owned.",
    "claims": {"P1": P1, "P2": P2, "P3": P3, "P4": P4},
    "honest_paragraph": honest,
}
path = os.path.join(DATA, "m5_12_audit_b15.json")
with open(path, "w") as f:
    json.dump(OUT, f, indent=1)
print("verdicts:")
for k in ("P1", "P2", "P3", "P4"):
    print(f"  {k}: {OUT['claims'][k]['verdict']}")
print(f"json -> {os.path.basename(path)}")
