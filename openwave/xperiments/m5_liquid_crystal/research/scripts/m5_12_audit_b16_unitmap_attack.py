"""M5.12 block 16 ADVERSARIAL AUDIT, leg 3: C4 (the O2 unit map).

Attacks: (a) observable mismatch (M5.8 w_dep = ||M - M_ref||^2 includes the
DC/M0-sector deformation and excludes the core r <= 2 RC; recompute the BVP
r_mean under matching weights/masks), (b) window drift (which r_58 is
defensible, incl. the uniform-weight delocalization asymptote of the M5.8
box), (c) static anchors, (d) documented from code reading in the verdicts.
Also: the factor table recomputed with the c2/g48 bmix endpoints INCLUDED
(leg 2 found they carry the lowest invariant product).

Run:  python m5_12_audit_b16_unitmap_attack.py
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
from m5_12_d3a_bvp import x_pack                                           # noqa: E402

ENDPOINTS = (
    ("f2", "m5_12_b12_hard_f2_1_state.npz",
     "m5_12_b15_seed_shell_k1_n32.npz", "m5_12_b12_hard_ladder_f2_.json"),
    ("p1", "m5_12_b12_hard_p1_1_state.npz",
     "m5_12_b16_seed_rayleigh_opt_n32.npz", "m5_12_b12_hard_ladder_p1_.json"),
    ("c2", "m5_12_b12_hard_c2_1_state.npz",
     "m5_12_d3b_breather_n32_c2seed_state.npz",
     "m5_12_b12_hard_ladder_c2_.json"),
)

BAND = (1.07, 1.15)
R58 = {"early_t4": 3.47, "window_mean_kicked": 4.29,
       "late_seed_arm": 4.61, "late_jit_arm": 4.77, "late_kicked": 4.74,
       "settled_static": 4.941, "seed_static": 2.628}


def load_state(path):
    d = np.load(path)
    ks = [k for k in ("A1", "A2", "B1", "B2") if k in d]
    As = [d[k].astype(np.float64) for k in ks if k.startswith("A")]
    Bs = [d[k].astype(np.float64) for k in ks if k.startswith("B")]
    return x_pack(d["M0"].astype(np.float64), As, Bs)


def weighted_r(wgt, R, Z, h=1.0, rmin=None):
    vol = 2.0 * np.pi * R * h * h
    r = np.sqrt(R ** 2 + Z ** 2)
    w = vol * wgt
    if rmin is not None:
        w = np.where(r > rmin, w, 0.0)
    return float(np.sum(w * r) / np.sum(w))


def main():
    t0 = time.time()
    out = {"task": "M5.12 block 16 audit leg 3 (C4)", "date": "2026-07-09",
           "rows": [], "factor_table": [], "m58_box": {}}

    # ---- (b) the M5.8 delocalization asymptote: uniform weight over the
    # wide mask of the 24^3 box (L = 6, core r <= 2 RC = 1.6 excluded) ----
    N, L, RC = 24, 6.0, 0.8
    xs = np.linspace(-L, L, N)
    X3, Y3, Z3 = np.meshgrid(xs, xs, xs, indexing="ij")
    r3 = np.sqrt(X3 ** 2 + Y3 ** 2 + Z3 ** 2)
    inter = np.zeros_like(r3, bool)
    inter[2:-2, 2:-2, 2:-2] = True
    wide = inter & (r3 > 2 * RC)
    out["m58_box"] = {
        "h_x_units": float(xs[1] - xs[0]),
        "uniform_r_mean_wide_mask": float(r3[wide].mean()),
        "note": ("M5.8 r_mean lives in x-units (box [-6,6]^3, h = 0.522), "
                 "NOT lattice cells as the unitmap docstring says; the "
                 "factor is a ratio of dimensionless omega*r products so "
                 "the mislabel does not move the number IF c = 1 holds in "
                 "each code's own units (A2)")}
    print(f"[m58 box] h={out['m58_box']['h_x_units']:.4f} x-units; "
          f"uniform-weight r_mean over wide mask = "
          f"{out['m58_box']['uniform_r_mean_wide_mask']:.3f} "
          f"(the delocalization asymptote; late-window 4.61-4.77 sits "
          f"most of the way there from t4's 3.47)")

    # ---- (a) BVP r_mean under matched weights ----
    h = 1.0
    for tag, spath, seedpath, lpath in ENDPOINTS:
        Xe = load_state(os.path.join(DATA, spath))
        Xs = load_state(os.path.join(DATA, seedpath))
        nr, nz = Xe["M0"].shape[:2]
        R, Z = grid_coords(nr, nz, h)
        pin = pin_mask(nr, nz)
        wb = json.load(open(os.path.join(DATA, lpath)))["rungs"][-1][
            "omega_bal_end"]
        amp2 = np.zeros((nr, nz))
        for k in range(len(Xe["A"])):
            amp2 += np.sum(Xe["A"][k] ** 2, axis=(-2, -1))
            amp2 += np.sum(Xe["B"][k] ** 2, axis=(-2, -1))
        amp2[pin] = 0.0
        dc2 = np.sum((Xe["M0"] - Xs["M0"]) ** 2, axis=(-2, -1))
        dc2[pin] = 0.0
        # time-average of ||M(t) - M_ref||^2 = dc2 + amp2 / 2
        dep = dc2 + 0.5 * amp2
        rec = {"tag": tag, "omega_bal": wb,
               "r_amp2": weighted_r(amp2, R, Z),
               "r_dep_timeavg": weighted_r(dep, R, Z),
               "r_dc_only": weighted_r(dc2, R, Z),
               "r_amp2_coremask_1p6": weighted_r(amp2, R, Z, rmin=1.6),
               "r_amp2_coremask_3p07": weighted_r(amp2, R, Z, rmin=3.07),
               "dc2_share_of_dep": float(np.sum(2 * np.pi * R * dc2)
                                         / np.sum(2 * np.pi * R * dep))}
        out["rows"].append(rec)
        print(f"[{tag}] w {wb:.4f}  r_amp2 {rec['r_amp2']:.3f}  "
              f"r_dep(timeavg, M5.8-matched) {rec['r_dep_timeavg']:.3f}  "
              f"r_dc {rec['r_dc_only']:.3f} "
              f"(dc share {rec['dc2_share_of_dep']:.2f})  "
              f"core-masked r>1.6 {rec['r_amp2_coremask_1p6']:.3f} / "
              f"r>3.07 {rec['r_amp2_coremask_3p07']:.3f}")

    # ---- (b)+(c) the factor table: floor x r_58 x band ----
    for row in out["rows"]:
        for robs in ("r_amp2", "r_dep_timeavg"):
            for wtag, r58 in R58.items():
                w_at = row["omega_bal"] * row[robs] / r58
                out["factor_table"].append(
                    {"floor": row["tag"], "r_obs": robs, "window": wtag,
                     "r58": r58, "omega_at_m58_size": w_at,
                     "factor": [w_at / BAND[1], w_at / BAND[0]]})
    # print the span per floor/observable
    for row in out["rows"]:
        for robs in ("r_amp2", "r_dep_timeavg"):
            fs = [f for f in out["factor_table"]
                  if f["floor"] == row["tag"] and f["r_obs"] == robs
                  and "static" not in f["window"]]
            lo = min(f["factor"][0] for f in fs)
            hi = max(f["factor"][1] for f in fs)
            print(f"[factor {row['tag']} {robs:>14}] motion-window span "
                  f"{lo:.2f}-{hi:.2f}x")

    out["wall_s"] = round(time.time() - t0, 1)
    path = os.path.join(DATA, "m5_12_audit_b16_unitmap_attack.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"[done] {out['wall_s']}s -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
