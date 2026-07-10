"""M5.12 block 16 leg (b): the unit map (option O2, measured).

The question (author-gated, opened by the block-14 audit): at which object
scale does the M5.8 molten-clock band omega_1 = 1.07-1.15 live, in the
units of the M5.12 axisym BVP? Without it, no distance-to-band statement
is licensed: the stall roots omega_bal scale as 1/L (measured to 0.7%),
so the quoted distance moves by 3x depending on the assumed scale.

THE MEASUREMENT: compare like observables. The M5.8 2h record retains
(log `_m5_8_2h_run.log` + npz `_m5_8_2h_dense.npz`):
    static seed (dressed defect)   r_mean = 2.628  (base_seed[3])
    settled cold ground state      r_mean = 4.941  (base_set[3])
    breathing arms, late window    r_mean(dep) = 4.61-4.77
                                   (kicked t 44-48: 4.61/4.64;
                                    jittered: 4.72/4.77; w_dep-weighted)
where r_mean is the ||M - M_ref||^2-weighted mean radius in lattice cells
(24^3-class box, dt = 0.001, beta = 1.558). On the BVP side this script
computes the SAME observable on the relaxed stall endpoints: the
harmonic-amplitude-squared weighted mean radius
    r_mean = sum(w * r * sum_k(Ak^2 + Bk^2)) / sum(w * sum_k(Ak^2 + Bk^2)),
w = 2 pi R h^2 (axisym cell volume), r = sqrt(R^2 + Z^2).

THE MAP (assumptions DECLARED, both author-gated):
    A1 cell = cell: one M5.8 lattice unit = one BVP h unit (both codes
       discretize the same 4x4 tensor family at unit spacing).
    A2 c = 1 in both: both actions descend from the same 4D Lagrangian
       family, curvature-normalized, so times compare when lengths do.
Under A1+A2 and the measured 1/L covariance, a BVP stall of motion radius
r_bvp rescaled to the M5.8 breather's motion radius r_m58 has
    omega_at_m58_size = omega_bal * (r_bvp / r_m58)
and the licensed distance factor is that / band. The sensitivity table
spans r_m58 in {4.61, 4.77, 4.94} and band in {1.07, 1.15}, plus the two
bracketing conventions (identity n32, and the n96 anchor rc = 8) so the
O1-style readings appear as labeled rows of the same table.

Run:  python m5_12_b16_unitmap.py
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

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import pin_mask                                          # noqa: E402

# M5.8 side (provenance: _m5_8_2h_run.log static-baseline header + the
# late-window r_mean(dep) table rows; npz base_seed/base_set indices 3)
M58 = {
    "static_seed_core": 2.628,      # dressed defect, static
    "settled_ground": 4.941,        # cold ground state, static
    "breathing_late": (4.61, 4.64, 4.72, 4.77),  # kicked + jit, t 44-48
    "band": (1.07, 1.15),           # omega_1 attractor, +- one bin 0.13
}

ENDPOINTS = (
    ("f2 shell (b15 floor)", "m5_12_b12_hard_f2_1_state.npz",
     "m5_12_b12_hard_ladder_f2_.json"),
    ("f1 rgauss", "m5_12_b12_hard_f1_1_state.npz",
     "m5_12_b12_hard_ladder_f1_.json"),
    ("wd wide (b14)", "m5_12_b12_hard_wd_1_state.npz",
     "m5_12_b12_hard_ladder_wd_.json"),
    ("p1 rayleigh_opt (b16)", "m5_12_b12_hard_p1_1_state.npz",
     "m5_12_b12_hard_ladder_p1_.json"),
    ("p2 pancake r4z1 (b16)", "m5_12_b12_hard_p2_1_state.npz",
     "m5_12_b12_hard_ladder_p2_.json"),
)


def r_mean_bvp(path, h=1.0):
    d = np.load(path)
    nr, nz = d["M0"].shape[:2]
    R, Z = grid_coords(nr, nz, h)
    pin = pin_mask(nr, nz)
    w = 2.0 * np.pi * R * h * h
    amp2 = np.zeros((nr, nz))
    for k in ("A1", "A2", "B1", "B2"):
        amp2 += np.sum(d[k].astype(np.float64) ** 2, axis=(-2, -1))
    amp2[pin] = 0.0
    r = np.sqrt(R ** 2 + Z ** 2)
    num, den = float(np.sum(w * r * amp2)), float(np.sum(w * amp2))
    return num / den, nr


def main():
    out = {"task": "M5.12 block 16 leg b", "assumptions": [
        "A1 cell=cell (1 M5.8 lattice unit = 1 BVP h unit)",
        "A2 c=1 in both codes (same 4D Lagrangian family)",
        "author-gated: both must be sanctioned before any outbound use"],
        "m58": M58, "rows": [], "table": []}
    print(f"{'endpoint':>24}  {'w_bal':>7}  {'r_bvp':>6}  "
          f"{'w@4.61':>7} {'w@4.77':>7} {'w@4.94':>7}  factor(band 1.07-1.15)")
    for label, spath, lpath in ENDPOINTS:
        sp = os.path.join(DATA, spath)
        lp = os.path.join(DATA, lpath)
        if not (os.path.exists(sp) and os.path.exists(lp)):
            print(f"{label:>24}  MISSING (chain not closed yet), skipped")
            continue
        with open(lp) as f:
            wb = json.load(f)["rungs"][-1]["omega_bal_end"]
        rb, nr = r_mean_bvp(sp)
        rescaled = {rm: wb * rb / rm for rm in (4.61, 4.77, 4.941)}
        fmin = rescaled[4.941] / M58["band"][1]
        fmax = rescaled[4.61] / M58["band"][0]
        out["rows"].append({"endpoint": label, "state": spath, "nr": nr,
                            "omega_bal": wb, "r_mean_bvp": rb,
                            "omega_at_m58_size": rescaled,
                            "factor_range": [fmin, fmax]})
        print(f"{label:>24}  {wb:7.4f}  {rb:6.3f}  "
              f"{rescaled[4.61]:7.3f} {rescaled[4.77]:7.3f} "
              f"{rescaled[4.941]:7.3f}  {fmin:.1f}-{fmax:.1f}x")
    # bracketing conventions on the standing floor (f2), for the table
    if out["rows"]:
        f2 = out["rows"][0]
        wb, rb = f2["omega_bal"], f2["r_mean_bvp"]
        for conv, rm in (("identity n32 (rc 2.667)", rb),
                         ("O1 n96 anchor (x32/96)", rb * 3.0),
                         ("O2 measured (breathing 4.61-4.94)", None)):
            if rm is None:
                w_lo, w_hi = wb * rb / 4.941, wb * rb / 4.61
            else:
                w_lo = w_hi = wb * rb / rm
            out["table"].append({
                "convention": conv,
                "omega_floor_rescaled": [w_lo, w_hi],
                "factor_vs_band": [w_lo / M58["band"][1],
                                   w_hi / M58["band"][0]]})
            print(f"[conv] {conv:>34}: floor -> "
                  f"{w_lo:.2f}-{w_hi:.2f}, factor "
                  f"{w_lo / M58['band'][1]:.1f}-"
                  f"{w_hi / M58['band'][0]:.1f}x")
    path = os.path.join(DATA, "m5_12_b16_unitmap.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
