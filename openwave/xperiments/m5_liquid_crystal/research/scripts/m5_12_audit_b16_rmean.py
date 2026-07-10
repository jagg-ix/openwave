"""M5.12 block 16 ADVERSARIAL AUDIT, leg 2: C2 (growth discrimination) +
C3 evidence (is omega_bal * r_mean the right scale invariant, and does the
size ranking survive alternative radius observables?).

Own r_mean implementation + variants (amp^2, |amp|, RMS, median r50),
zoom covariance test (load_warmstart n32 -> n24/n48, scale-family wscale),
and the g48-vs-c2 lineage product check.

Run:  python m5_12_audit_b16_rmean.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_d3a_bvp import shat, x_pack                                     # noqa: E402
from m5_12_d3b_newton import wscale_at, load_warmstart                     # noqa: E402

ENDPOINTS = (
    ("f2", "m5_12_b12_hard_f2_1_state.npz", "m5_12_b12_hard_ladder_f2_.json"),
    ("f1", "m5_12_b12_hard_f1_1_state.npz", "m5_12_b12_hard_ladder_f1_.json"),
    ("wd", "m5_12_b12_hard_wd_1_state.npz", "m5_12_b12_hard_ladder_wd_.json"),
    ("p1", "m5_12_b12_hard_p1_1_state.npz", "m5_12_b12_hard_ladder_p1_.json"),
    ("p2", "m5_12_b12_hard_p2_1_state.npz", "m5_12_b12_hard_ladder_p2_.json"),
    ("c2", "m5_12_b12_hard_c2_1_state.npz", "m5_12_b12_hard_ladder_c2_.json"),
    ("g48", "m5_12_b12_hard_g48_1_state.npz",
     "m5_12_b12_hard_ladder_g48_.json"),
)


def load_state(path):
    d = np.load(path)
    return x_pack(d["M0"].astype(np.float64),
                  [d["A1"].astype(np.float64), d["A2"].astype(np.float64)],
                  [d["B1"].astype(np.float64), d["B2"].astype(np.float64)])


def radius_observables(X, h=1.0):
    """own implementation: amp^2-weight (claimant convention), |amp|-weight,
    RMS radius, and median radius r50, all with the 2 pi R h^2 volume
    weight and pins zeroed."""
    nr, nz = X["M0"].shape[:2]
    R, Z = grid_coords(nr, nz, h)
    pin = pin_mask(nr, nz)
    vol = 2.0 * np.pi * R * h * h
    amp2 = np.zeros((nr, nz))
    for k in range(len(X["A"])):
        amp2 += np.sum(X["A"][k] ** 2, axis=(-2, -1))
        amp2 += np.sum(X["B"][k] ** 2, axis=(-2, -1))
    amp2[pin] = 0.0
    r = np.sqrt(R ** 2 + Z ** 2)
    out = {}
    for tag, wgt in (("amp2", vol * amp2), ("amp1", vol * np.sqrt(amp2))):
        tot = float(np.sum(wgt))
        out[f"r_{tag}"] = float(np.sum(wgt * r)) / tot
    w2 = vol * amp2
    out["r_rms"] = float(np.sqrt(np.sum(w2 * r ** 2) / np.sum(w2)))
    order = np.argsort(r.ravel())
    cw = np.cumsum(w2.ravel()[order])
    out["r_50"] = float(r.ravel()[order][np.searchsorted(
        cw, 0.5 * cw[-1])])
    return out


def omega_bal_of(X, h, wscale):
    s0 = shat(X, 0.0, h, wscale)
    q2 = s0 - shat(X, 1.0, h, wscale)
    if q2 >= 0 or s0 <= 0:
        return None, s0, q2
    return float(np.sqrt(s0 / -q2)), s0, q2


def main():
    t0 = time.time()
    h = 1.0
    out = {"task": "M5.12 block 16 audit leg 2 (C2/C3)",
           "date": "2026-07-09", "rows": [], "zoom": [], "lineage": {}}

    rows = {}
    for tag, spath, lpath in ENDPOINTS:
        X = load_state(os.path.join(DATA, spath))
        nr = X["M0"].shape[0]
        wb = json.load(open(os.path.join(DATA, lpath)))["rungs"][-1][
            "omega_bal_end"]
        obs = radius_observables(X, h)
        rec = {"tag": tag, "nr": nr, "omega_bal": wb, **obs,
               "product_amp2": wb * obs["r_amp2"]}
        rows[tag] = rec
        out["rows"].append(rec)
        print(f"[{tag:>3}] nr{nr} w {wb:7.4f}  r_amp2 {obs['r_amp2']:.3f}  "
              f"r_amp1 {obs['r_amp1']:.3f}  r_rms {obs['r_rms']:.3f}  "
              f"r_50 {obs['r_50']:.3f}  w*r_amp2 {wb*obs['r_amp2']:.2f}")

    # rankings at common radius 4.77 under each observable
    fams = ("f2", "f1", "wd", "p1", "p2")
    out["rankings"] = {}
    for key in ("r_amp2", "r_amp1", "r_rms", "r_50"):
        scored = sorted(((rows[t]["omega_bal"] * rows[t][key] / 4.77, t)
                         for t in fams))
        out["rankings"][key] = [{"tag": t, "omega_at_4p77": v}
                                for v, t in scored]
        print(f"[rank {key:>6}] " + "  ".join(
            f"{t}={v:.3f}" for v, t in scored))

    # lineage check: g48 vs c2 (both bmix_rz, scale family, relaxed)
    pg = rows["g48"]["omega_bal"] * rows["g48"]["r_amp2"]
    pc = rows["c2"]["omega_bal"] * rows["c2"]["r_amp2"]
    out["lineage"] = {
        "c2_product": pc, "g48_product": pg,
        "rel_dev": abs(pg - pc) / pc,
        "omega_ratio": rows["g48"]["omega_bal"] / rows["c2"]["omega_bal"],
        "r_ratio": rows["g48"]["r_amp2"] / rows["c2"]["r_amp2"],
        "expected_omega_ratio_1_over_L": 32.0 / 48.0}
    print(f"[lineage] c2 w*r {pc:.2f}  g48 w*r {pg:.2f}  "
          f"rel dev {out['lineage']['rel_dev']:.3f}  "
          f"(w ratio {out['lineage']['omega_ratio']:.4f}, "
          f"1/L expects {32/48:.4f}, r ratio "
          f"{out['lineage']['r_ratio']:.4f} vs 1.5)")

    # zoom covariance: p1 and f2, n32 -> n24 and n48 (scale-family wscale)
    for tag, spath in (("f2", "m5_12_b12_hard_f2_1_state.npz"),
                       ("p1", "m5_12_b12_hard_p1_1_state.npz")):
        base = rows[tag]
        for n2 in (24, 48):
            Xz, _ = load_warmstart(os.path.join(DATA, spath), n2, 2 * n2, 2)
            pin = pin_mask(n2, 2 * n2)
            for k in range(2):
                Xz["A"][k][pin] = 0.0
                Xz["B"][k][pin] = 0.0
            wsc = wscale_at(n2, 2 * n2, h, 8.0 * n2 / 96)
            wz, s0z, q2z = omega_bal_of(Xz, h, wsc)
            obs = radius_observables(Xz, h)
            prod = (wz * obs["r_amp2"]) if wz else None
            rec = {"tag": tag, "nr_from": base["nr"], "nr_to": n2,
                   "omega_bal": wz, "r_amp2": obs["r_amp2"],
                   "product": prod,
                   "product_rel_dev": (abs(prod - base["product_amp2"])
                                       / base["product_amp2"]
                                       if prod else None),
                   "omega_ratio": (wz / base["omega_bal"]) if wz else None,
                   "expected_1_over_L": base["nr"] / n2}
            out["zoom"].append(rec)
            print(f"[zoom {tag} n32->n{n2}] w {wz if wz else -1:.4f} "
                  f"(ratio {rec['omega_ratio'] if wz else -1:.4f}, 1/L "
                  f"{rec['expected_1_over_L']:.4f})  r {obs['r_amp2']:.3f}  "
                  f"w*r {prod if prod else -1:.2f} vs base "
                  f"{base['product_amp2']:.2f} "
                  f"(rel {rec['product_rel_dev'] if prod else -1:.3f})")

    out["wall_s"] = round(time.time() - t0, 1)
    path = os.path.join(DATA, "m5_12_audit_b16_rmean.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"[done] {out['wall_s']}s -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
