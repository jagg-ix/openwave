"""M5.12 block-14 ADVERSARIAL AUDIT: verdict assembly.

Reads the three section JSONs (probe / loop / stall) plus the live chain
records and writes the per-claim verdict file ../data/m5_12_audit_b14.json.

Run:  python3 -u m5_12_audit_b14_verdicts.py
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
sys.argv = sys.argv[:1]


def j(name):
    p = os.path.join(DATA, name)
    return json.load(open(p)) if os.path.exists(p) else None


probe = j("m5_12_audit_b14_probe.json")
loop = j("m5_12_audit_b14_loop.json")
stall = j("m5_12_audit_b14_stall.json")

secC = probe["sections"]["C_out_of_battery"]
secD = probe["sections"]["D_fixed_wscale"]
secE = probe["sections"]["E_matched_amplitude"]
secF = probe["sections"]["F_h_refinement"]
secG = probe["sections"]["G_scaling"]

OUT = {
    "task": "M5.12 block 14",
    "role": "INDEPENDENT ADVERSARIAL AUDIT (block 14): seed battery, "
            "scale family, loop transplant, stall floors",
    "date": "2026-07-09",
    "scripts": ["m5_12_audit_b14_probe.py", "m5_12_audit_b14_loop.py",
                "m5_12_audit_b14_stall.py", "m5_12_audit_b14_verdicts.py"],
    "instrument_note": "shat/residual (m5_12_d3a_bvp) used as the meter "
        "(independently verified by the block-11 audit); all seeds, "
        "flattenings, windings, line searches and GN steps are "
        "audit-owned reimplementations.",
    "claims": {},
}

OUT["claims"]["N1_class_negative"] = {
    "verdict": "WEAKENED (all stall data CONFIRMED, floor robust to "
        "phase-row choice; but the stalls are NOT stationary points of "
        "|F|^2, descent demonstrably continues at sub-1%/step, the "
        "floors sit BELOW the grid-transfer discretization scale so "
        "failing the discrete-root bar cannot show nonexistence, and "
        "the '~5-8x above the band' framing is scale-inconsistent with "
        "the block's own N3 scaling)",
    "evidence": {
        "confirmed": [
            "stall endpoints reproduced independently (audit flattening, "
            "own phase row): |F| = 217.05/141.99/208.57 vs published "
            "215.78/139.06/206.84 (1-2%: float32 storage + different "
            "phase-row U); omega_bal 8.6377/6.5747/5.8068 exact",
            "H_swing/S0 = 1.994/1.981/2.711: the claimed 2-2.7 range is "
            "honest arithmetic",
            "floor NOT an artifact of the phase row or retraction point: "
            "the phase row carries 1e-16..1e-11 of |F|; recomputing with "
            "a random U or no phase row leaves the floor at 217.05 "
            "unchanged",
        ],
        "kills": [
            "NOT A STATIONARY POINT: |J^T F| = 2.7e8/4.1e8/3.4e8 at the "
            "three stalls (|J^T F|/|F| ~ 1e6): in exact arithmetic a "
            "descent direction exists at every stall; the natural "
            "steepest-descent step is t ~ phi/|g|^2 ~ 1e-13 (my line "
            "search grid, min t = 1e-5, correctly found nothing: the "
            "landscape curvature is enormous, conditioning ~1e6), and "
            "my own independent damped-GN step from the c2 stall "
            "DESCENDS 0.73% at full lam = 1. The chains stop on the "
            "'3 consecutive sub-1% steps' RULE: the floors are "
            "progress-rate stalls, not demonstrated obstructions",
            "WORDING: 'no reachable orbit EXISTS' asserts nonexistence "
            "from budget-limited stalls of chains in ONE seed lineage "
            "(c1/c2/s all descend from the same bmix warm-start family). "
            "Honest form: 'no orbit was FOUND; every chain enters a "
            "sub-1%-per-step regime at |F| ~ 140-220'",
            "THE BAR vs DISCRETIZATION: grid transfer (order-1 zoom) "
            "puts the cross-grid consistency scale at |F| ~ 631 (c2 "
            "n32->n48) and ~867 (g48 ck n48->n32): the in-grid floors "
            "139-216 are ALREADY BELOW the scale at which n32 can "
            "distinguish continuum physics. The 1e-5 rel bar (absolute "
            "|F| ~ 2e-3..0.11, denominators differing 55x across "
            "chains) probes the exact DISCRETE root; failing it at n32 "
            "does not rule out a continuum orbit near these states",
            "SCALE MISMATCH: under the block's own omega_bal ~ 1/L "
            "scaling (w*nr = 347-360 const; relaxed states too: 283 at "
            "n32 vs 275 at n48), the n32 stalls 5.8-8.6 rescale to "
            "1.9-2.9 at the n96 calibration scale, i.e. 1.7-2.7x the "
            "band, not 5-8x. Either N3's scale covariance or 'far "
            "above the band' must yield. Whether the sqrt(70/61) band "
            "lives at the n96 object scale is an author-gated question "
            "that must be answered before ANY band comparison is quoted",
        ],
        "stall_numbers": stall["sections"]["floors_and_descent"]
        if stall else "PENDING",
        "gn_step": stall["sections"].get("independent_GN_step_c2")
        if stall else "PENDING",
        "grid_transfer": stall["sections"].get("grid_transfer")
        if stall else "PENDING",
    },
}

OUT["claims"]["N2_class_coverage"] = {
    "verdict": "REFUTED as a coverage statement (battery numbers "
        "themselves CONFIRMED; A1/B1 degeneracy CONFIRMED and proven "
        "structural, hence vacuous as coverage)",
    "evidence": {
        "probe_numbers": "all 12 published seed records reproduced to "
            "<= 3e-8 rel (float32 storage floor); grid + fixobj series "
            "reproduced to 0 (bit-identical formulas)",
        "degeneracy": "bmix_B1 == bmix_rz is EXACT FOR ANY SEED: "
            "(A1,B1) = (P cos phi0, P sin phi0) is a time translation "
            "and the N_s = 10 trapezoid is exact for the degree <= 8 "
            "density: verified at 4 arbitrary phases with a RANDOM "
            "field (spread S0 7e-15, Q2 3e-11). The B1 battery entry "
            "adds ZERO coverage: it is the same state",
        "the_kill": {
            "statement": "two cheap seeds OUTSIDE the battery, same M0, "
                "same wscale, same matched a2 = 0.3037, undercut "
                "bmix_rz's omega_bal 11.03 by ~20%",
            "node_rz (radial-node profile eps b2 (1-2r^2/w^2))":
                {"S0": 67.27, "Q2": -0.8403, "omega_bal": 8.947},
            "wide_rz_2x (w_b doubled)":
                {"S0": 64.29, "Q2": -0.8654, "omega_bal": 8.619},
            "control bmix_rz reproduced": 11.0306,
            "battery minimum": 11.03,
        },
        "metric_fragility": "an A2 (second-harmonic) transplant of the "
            "same mix shows omega_bal 5.515 at matched norm, but the "
            "physical oscillation frequency is 2 omega = 11.03: "
            "omega_bal is not class-comparable when amplitude sits in "
            "higher harmonics: any future battery must compare k*omega",
        "caveat": "seed-level omega_bal orderings may not survive "
            "relaxation (block-13: bmix 11.03 relaxed to 8.83); but the "
            "claim under audit IS a seed-level statement and dies at "
            "seed level",
        "rows": secC["rows"],
    },
}

OUT["claims"]["N3_object_scale"] = {
    "verdict": "WEAKENED (series arithmetic CONFIRMED and h-convergence "
        "VERIFIED here at ~2%, but 'object-size physics' holds ONLY "
        "under per-grid wscale recalibration and the fixed-eps "
        "amplitude convention; the trend REVERSES in any fixed theory "
        "and under weighted amplitude matching; fixobj is a BOX test "
        "and never tested discretization)",
    "evidence": {
        "confirmed": [
            "grid series reproduced exactly; w_bal*nr = 360.5/353.0/"
            "348.4/347.0: the fall IS the kinematic 1/L law of a "
            "shape-preserving family (log-log slope -1.038)",
            "fixobj: Q2 box-independent to 1e-12 rel (trivially exact: "
            "the added cells carry zero harmonic), S0 drift 2.1% = tail "
            "truncation: box-independence claim honest",
            "TRUE h-refinement (n32 h=1 vs n48 h=2/3 vs n64 h=1/2, same "
            "object, same box: the test the block did NOT run): "
            "omega_bal 11.031/10.886/10.843, order ~2.4, h->0 limit "
            "10.800: n32 discretization error 2.1%: the seed-level "
            "numbers ARE h-converged (the 'not discretization' clause "
            "is true, but was never established by fixobj, whose "
            "docstring mislabels it 'pure resolution')",
        ],
        "kills": [
            "FIXED-WSCALE REVERSAL: at wscale frozen at the n32 "
            "calibration the series is 12.46/11.03/12.11/14.88; frozen "
            "at n48: 11.30/8.78/7.26/7.61: in ANY fixed theory "
            "omega_bal has a minimum at the calibration scale and "
            "RISES for larger objects. The monotone fall exists only "
            "because wscale is recalibrated per object (it varies 46x "
            "across the family). 'Object-size physics' is a property "
            "of the family-of-theories, not of objects in a theory",
            "AMPLITUDE CONVENTION: fixed eps means raw a2 grows as "
            "nr^2 (0.171/0.304/0.683/1.215) and |Q2| tracks it. At "
            "matched raw a2 the fall shrinks to 13.47/11.03/9.78/9.46 "
            "(-30% vs the published -64%); at matched WEIGHTED a2w it "
            "is NON-monotonic: 13.38/11.03/11.63/13.04 (minimum at "
            "n32). The 'story' is a convention choice",
        ],
        "fixed_wscale_rows": secD["rows"],
        "matched_amplitude_rows": secE["rows"],
        "h_refinement_rows": secF["rows"],
    },
}

lp_traj = loop["sections"]["c_S0"].get("chain_S0_trajectory") \
    if loop else None
OUT["claims"]["N4_loop_transplant"] = {
    "verdict": "MIXED: under-resolution refutation FAILS (the n32 object "
        "IS a genuine loop: CONFIRMED); topology preserved so far "
        "(CONFIRMED, provisional at 2 Newton iterations); 'deepest Q2' "
        "arithmetic CONFIRMED but misleading as an advantage; S0 = "
        "217.6 as a physical energy REFUTED (seed artifact)",
    "evidence": {
        "loopness": "measured nematic winding q = 0.5 (at rc/2 and rc) "
            "at n32/n48/n96; hedgehog control on the same circle: q = 0; "
            "ring melt floor min_s = 0.038 at n32 (vs 0.008 at n96: "
            "shallower core but a real melt ring at (5.5, -0.5))",
        "topology_after_chain": "lp checkpoint (iter 2): winding still "
            "0.5, ring at (5.5,-0.5), min_s 0.0384; |dM0| from seed = "
            "0.006 vs distance-to-hedgehog 19.4: NOT relaxing toward "
            "the hedgehog sector (yet; only 2 iterations)",
        "S0_kill": "S0 fell 217.6 -> 97.9 -> 97.1 under a total field "
            "move of L2 norm ~0.007 (|F|0 = 4.9e4: the seed sits on an "
            "extremely steep wall): 55% of the number is unrelaxed "
            "gradient, not object energy. Background-only (harmonics "
            "zeroed) S0: loop 141.0 vs hedgehog 50.7: the honest "
            "seed-level background ratio is 2.8x, not 217.6-vs-69; and "
            "the wscale is HEDGEHOG-calibrated (seed-virial of the "
            "rc=2.67 hedgehog), never recalibrated for the loop",
        "deepest_Q2": "loop Q2 -0.9425 is indeed the battery's deepest, "
            "but its omega_bal 15.19 was second-WORST in the battery, "
            "and the out-of-battery wide_rz seed carries Q2 -0.865 with "
            "omega_bal 8.62: depth of Q2 alone is not an advantage",
        "chain_trajectory": lp_traj,
        "chain_note": "omega_bal 15.19 -> 10.72 -> 10.20 (|F| 48869 -> "
            "2942 -> 555, unconverged): 'relaxes toward lower "
            "omega_bal' is true so far but is the generic S0-relaxation "
            "effect at fixed a2; still above the hedgehog-class relaxed "
            "value 8.83 at the SAME amplitude (block-13 audit)",
    },
}

OUT["claims"]["N5_honesty_check"] = {
    "verdict": "the tempting sentence is UNSUPPORTED; the honest "
        "sentence is written below",
    "seed_level_facts": {
        "fixed_eps_law": "omega_bal * nr = 347-360 (1/L kinematics), "
            "log-log slope -1.038",
        "band_crossing_fixed_eps": "nr-equivalent 284-304 (object rc "
            "24-25), raw a2 there 24-27 (~80-90x the c2 amplitude); "
            "block-13's rescaling analysis found the balance root DIES "
            "(Q2 >= 0) near a2 ~ 5-7: the extrapolation crosses into a "
            "region where the root's existence is already refuted at "
            "seed level",
        "at_n96_calibration_scale": "fixed-eps law gives seed omega_bal "
            "~ 3.55 at the n96 object: still 3.1x the band",
        "matched_a2_saturation": "S0/|Q2| = 181/122/96/89: decelerating "
            "toward ~85-90, i.e. omega_bal saturates ~9.2-9.5 at "
            "matched raw a2: the band is NOT approached",
        "fixed_theory": "in any fixed-wscale theory the trend reverses: "
            "bigger objects RAISE omega_bal beyond the calibration "
            "scale",
    },
    "honest_sentence": "Seed-level omega_bal follows the kinematic "
        "1/L law of a shape-preserving family under the per-grid "
        "seed-virial recalibration (w*nr ~ 350); the fall to 5.4 at "
        "n64 is amplitude- and convention-driven, reverses in any "
        "fixed theory, and extrapolating it to the M5.8 band requires "
        "an object ~25 cells and raw a2 ~ 25, inside the regime where "
        "the balance root is already known to die; no chain has "
        "converged anywhere, so seed-level omega_bal carries no "
        "existence content about orbits in the band.",
}

OUT["constructive_findings"] = [
    "b14_seeds.py fixobj docstring mislabels a BOX test as 'pure "
    "resolution': with h = 1 fixed, growing nr grows the box, not the "
    "resolution. The h-refinement gap is now closed by this audit "
    "(order ~2.4, n32 error ~2%)",
    "the A1/B1 degeneracy is a provable time-translation identity: "
    "battery slots should not be spent on it",
    "omega_bal comparisons need k*omega (physical frequency), not the "
    "fundamental omega, once higher harmonics carry amplitude",
    "the seed battery's real gap is SHAPE (profile/width) not component "
    "structure: node and 2x-width rz seeds undercut every battery "
    "entry by ~20% at matched a2",
    "two claims in the block's stack (N1's 'far above the band' and "
    "N3's scale covariance) are mutually inconsistent: fix the unit "
    "map (author-gated) before any band comparison is published",
]

path = os.path.join(DATA, "m5_12_audit_b14.json")
with open(path, "w") as f:
    json.dump(OUT, f, indent=1)
print(f"verdicts -> {os.path.basename(path)}")
for k, v in OUT["claims"].items():
    print(f"  {k}: {v['verdict'][:100]}")
