"""M5.12 block-18 AUDIT, leg 2 (D2): the rule adjudication numbers.

(a) The pencil leg found the decider's I-Gram distorted the model
    objective (true-Gram model optimum 6.24 vs the probed direction's
    7.46): exact-probe the TRUE-Gram top-3 model directions in-frame
    (both wscales), the directions the decider never tested.
(b) Seed-level in-frame battery: control_probe the seeds that PRODUCED
    the relaxed floors (p1 <- rayleigh_opt, p2 <- aniso_r4z1,
    f2 <- shell_k1, f1 <- rgauss_k2, wd <- wide_rz) at r_target 4.77,
    both wscales, and compute the measured in-frame seed -> relaxed
    gains of the prior chains.
(c) Project the best fresh seed direction through the measured gain
    distribution: does it plausibly relax below p1's floor?

Run:  python m5_12_audit_b18_seeds.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.linalg import eigh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_b14_seeds import s0_q2                                          # noqa: E402
from m5_12_b17_control import (load_state, r_mean_of, control_probe,       # noqa: E402
                               NR_T, NZ_T, H, A2_STAR)
from m5_12_b18_decider import (frame_bg, analytic_basis, endpoint_basis,   # noqa: E402
                               a2_of, make_X, R_TARGET, TAU)


def main():
    out = {"leg": "D2 rule adjudication"}
    ws_native = wscale_at(NR_T, NZ_T, H, 8.0 * NR_T / 96.0)
    ws_matched = wscale_at(NR_T, NZ_T, H, R_TARGET)
    M0, Rg, Zg = frame_bg()
    pin = pin_mask(NR_T, NZ_T)

    # ---- (a) true-Gram top-3 exact in-frame ----
    basis = analytic_basis(Rg, Zg) + endpoint_basis()
    names = [n for n, _ in basis]
    B = []
    for _, A1 in basis:
        A1 = A1.copy()
        A1[pin] = 0.0
        B.append(A1 / np.sqrt(a2_of(A1, pin)))
    n = len(B)
    d = np.load(os.path.join(DATA, "m5_12_b18_pencil.npz"), allow_pickle=True)
    S_pub, Q_pub = d["S"], d["Q"]
    S_static = s0_q2(make_X(M0, np.zeros_like(B[0])), H, ws_native)[0]
    free = ~pin
    Bf = np.stack([b[free] for b in B]).reshape(n, -1)
    M = Bf @ Bf.T
    w, V = eigh(-Q_pub)
    keep = w > TAU * w.max()
    P = V[:, keep] / np.sqrt(w[keep])
    A_true = S_pub + (S_static / A2_STAR) * M
    lam, U = eigh(P.T @ A_true @ P)
    out["trueGram_candidates"] = []
    for k in range(3):
        c = P @ U[:, k]
        A1 = np.tensordot(c, np.stack(B), axes=(0, 0))
        A1[pin] = 0.0
        A1 = A1 * np.sqrt(A2_STAR / a2_of(A1, pin))
        fields = {"M0": M0, "A1": A1, "A2": np.zeros_like(M0),
                  "B1": np.zeros_like(M0), "B2": np.zeros_like(M0)}
        r0 = r_mean_of(fields, NR_T, NZ_T)
        rec = {"k": k, "model_omega": float(np.sqrt(max(lam[k], 0.0))),
               "r_mean_raw": r0,
               "coeff_top": sorted(zip(names, np.abs(c).round(4)),
                                   key=lambda p: -p[1])[:5]}
        for wtag, ws in (("native", ws_native), ("rc-matched", ws_matched)):
            pr, _ = control_probe(fields, NR_T, NZ_T, r0, R_TARGET, ws)
            rec[f"inframe_{wtag}"] = pr["omega_bal"]
        out["trueGram_candidates"].append(rec)
        print(f"[trueGram k={k}] model {rec['model_omega']:.4f}  in-frame "
              f"native {rec['inframe_native']:.4f}  rc "
              f"{rec['inframe_rc-matched']:.4f}  r_raw {r0:.2f}")
        print("        top:", rec["coeff_top"])

    # ---- (b) seed-level in-frame battery ----
    seeds = (("p1", "m5_12_b16_seed_rayleigh_opt_n32.npz"),
             ("p2", "m5_12_b16_seed_aniso_r4z1_n32.npz"),
             ("f2", "m5_12_b15_seed_shell_k1_n32.npz"),
             ("f1", "m5_12_b15_seed_rgauss_k2_n32.npz"),
             ("wd", "m5_12_b14_seed_wide_rz_n32.npz"))
    relaxed = {  # b17 control, r_target 4.77 (native, rc-matched)
        "p1": (5.439268243152651, 5.108307986562202),
        "p2": (6.386411401421985, 6.119417929499873),
        "f2": (7.975384358724495, 6.50009192221767),
        "f1": (7.119983690060274, 6.780246485879416),
        "wd": (7.863217256045582, 6.8698341972975925)}
    out["seed_battery"] = []
    gains = {"native": [], "rc-matched": []}
    for tag, path in seeds:
        fields, nr_s, nz_s = load_state(path)
        r0 = r_mean_of(fields, nr_s, nz_s)
        rec = {"seed_of": tag, "state": path, "r_mean_native": r0}
        for i, (wtag, ws) in enumerate((("native", ws_native),
                                        ("rc-matched", ws_matched))):
            pr, _ = control_probe(fields, nr_s, nz_s, r0, R_TARGET, ws)
            rec[f"seed_inframe_{wtag}"] = pr["omega_bal"]
            rec[f"relaxed_inframe_{wtag}"] = relaxed[tag][i]
            g = 1.0 - relaxed[tag][i] / pr["omega_bal"]
            rec[f"gain_{wtag}"] = g
            gains[wtag].append(g)
        out["seed_battery"].append(rec)
        print(f"[seed {tag}] in-frame native {rec['seed_inframe_native']:.4f}"
              f" -> relaxed {rec['relaxed_inframe_native']:.4f} "
              f"(gain {100*rec['gain_native']:.1f}%)   rc "
              f"{rec['seed_inframe_rc-matched']:.4f} -> "
              f"{rec['relaxed_inframe_rc-matched']:.4f} "
              f"(gain {100*rec['gain_rc-matched']:.1f}%)")

    # ---- (c) projection of the fresh directions ----
    fresh = {"decider_k0": {"native": 7.2131317823101355,
                            "rc-matched": 6.147527393784886}}
    tg0 = out["trueGram_candidates"][0]
    fresh["trueGram_k0"] = {"native": tg0["inframe_native"],
                            "rc-matched": tg0["inframe_rc-matched"]}
    best_tg = min(out["trueGram_candidates"],
                  key=lambda r: r["inframe_native"])
    fresh["trueGram_best"] = {"native": best_tg["inframe_native"],
                              "rc-matched": best_tg["inframe_rc-matched"],
                              "k": best_tg["k"]}
    floor = {"native": 5.439268243152651, "rc-matched": 5.108307986562202}
    proj = {}
    for name, v in fresh.items():
        proj[name] = {}
        for wtag in ("native", "rc-matched"):
            gmin, gmax = min(gains[wtag]), max(gains[wtag])
            gmed = float(np.median(gains[wtag]))
            lo, hi = v[wtag] * (1 - gmax), v[wtag] * (1 - gmin)
            proj[name][wtag] = {
                "seed_value": v[wtag],
                "gain_range_pct": [100 * gmin, 100 * gmax],
                "gain_median_pct": 100 * gmed,
                "projected_relaxed_range": [lo, hi],
                "projected_relaxed_median": v[wtag] * (1 - gmed),
                "p1_floor": floor[wtag],
                "beats_floor_at_max_gain": bool(lo < floor[wtag]),
                "beats_floor_at_median_gain": bool(
                    v[wtag] * (1 - gmed) < floor[wtag])}
            p = proj[name][wtag]
            print(f"[proj {name}/{wtag}] seed {v[wtag]:.3f} -> relaxed "
                  f"[{lo:.3f}, {hi:.3f}] (median "
                  f"{p['projected_relaxed_median']:.3f}) vs floor "
                  f"{floor[wtag]:.3f}  beats@max={p['beats_floor_at_max_gain']}"
                  f" beats@med={p['beats_floor_at_median_gain']}")
    out["projection"] = proj
    out["p1_seed_vs_decider_rule"] = {
        "note": ("the pre-registered rule compared vs p1's RELAXED A1 on "
                 "the standard background (7.596/5.384); the seed that "
                 "produced p1 measures in-frame as above")}

    with open(os.path.join(DATA, "m5_12_audit_b18_seeds.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("json -> m5_12_audit_b18_seeds.json")


if __name__ == "__main__":
    main()
