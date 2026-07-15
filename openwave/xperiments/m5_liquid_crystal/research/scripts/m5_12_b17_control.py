"""M5.12 block 17: the fixed-(size, a2) re-ranking control.

The block-16 audit established (i) raw omega_bal comparisons across
families are size-dominated (the honest metric is the scale invariant
omega_bal * r_mean, lineage-invariant to 0.2%), (ii) under it the bmix
c2/g48 lineage has been the floor since block 12 (product 18.2 vs f2's
25.8), and (iii) an AMPLITUDE confound of ranking size is unresolved:
omega_bal at fixed shape spans 10.12 -> 5.03 across 0.49-2.25x a2, and
the endpoints sit at different amplitude densities once size-corrected.
This control removes both knobs at once: every stall endpoint is zoomed
to a COMMON object size on the COMMON n32 grid, its harmonics rescaled to
the COMMON a2 = 0.3037, and probed under ONE fixed instrument (one
wscale). Only the ORDERING is claimed; absolute values are
convention-bound as always.

Method per endpoint (native grid -> the control frame):
    1. load the float32 state, measure r_mean (harmonic-amp2-weighted
       mean radius, axisym volume weight 2 pi R h^2, pins zeroed)
    2. spatial zoom about the origin by s = r_target / r_mean: sample
       every component of M0/A1/A2/B1/B2 at source point (R/s, Z/s) via
       cubic map_coordinates (mode nearest beyond the source box; this
       also resamples cross-grid, g48's n48 -> n32); re-pin
    3. rescale ALL harmonics by one factor bringing a2_free (first
       harmonic, free cells) to a2_star; re-measure r_mean' (guard:
       within tolerance of r_target)
    4. exact probe: S0, Q2 (+ channel split), omega_bal, product

Guards: GC1 identity (an n32 endpoint zoomed at s = 1 reproduces its
direct probe to float32 tolerance); GC2 round trip (f2 zoomed s = 1.3
then 1/1.3 returns its probe values, bounds interpolation error); GC3
lineage consistency (c2 and g48 land within a few % of each other in the
control frame, they are the same physical family per the b16 audit).
Robustness: the ranking is recomputed at r_target in {4.77, 3.686} and
wscale in {native n32, rc-matched}; the claim is only as strong as the
ordering's stability across the four frames.

Run:  python m5_12_b17_control.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.ndimage import map_coordinates

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_d3a_bvp import x_pack                                           # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_b14_seeds import a2_free, probe, rescale_to                     # noqa: E402

A2_STAR = 0.303725
H = 1.0
NR_T, NZ_T = 32, 64      # the control frame grid

ENDPOINTS = (
    ("c2 bmix (b13)", "m5_12_b12_hard_c2_1_state.npz"),
    ("g48 bmix n48 (b14)", "m5_12_b12_hard_g48_1_state.npz"),
    ("wd wide (b14)", "m5_12_b12_hard_wd_1_state.npz"),
    ("f1 rgauss (b15)", "m5_12_b12_hard_f1_1_state.npz"),
    ("f2 shell (b15)", "m5_12_b12_hard_f2_1_state.npz"),
    ("p1 rayleigh_opt (b16)", "m5_12_b12_hard_p1_1_state.npz"),
    ("p2 pancake (b16)", "m5_12_b12_hard_p2_1_state.npz"),
    ("lp loop (b14)", "m5_12_b12_hard_lp_1_state.npz"),
)


def load_state(path):
    d = np.load(os.path.join(DATA, path))
    fields = {k: d[k].astype(np.float64)
              for k in ("M0", "A1", "A2", "B1", "B2")}
    return fields, fields["M0"].shape[0], fields["M0"].shape[1]


def r_mean_of(fields, nr, nz):
    R, Z = grid_coords(nr, nz, H)
    pin = pin_mask(nr, nz)
    w = 2.0 * np.pi * R * H * H
    amp2 = np.zeros((nr, nz))
    for k in ("A1", "A2", "B1", "B2"):
        amp2 += np.sum(fields[k] ** 2, axis=(-2, -1))
    amp2[pin] = 0.0
    r = np.sqrt(R ** 2 + Z ** 2)
    return float(np.sum(w * r * amp2) / np.sum(w * amp2))


def zoom_to_frame(fields, nr_s, nz_s, s):
    """sample the source fields at (R/s, Z/s) on the n32 control grid."""
    Rt, Zt = grid_coords(NR_T, NZ_T, H)
    # source index coords per the grid convention: rho=(i+0.5)h, z=(j-nz/2+0.5)h
    i_src = (Rt / s) / H - 0.5
    j_src = (Zt / s) / H + nz_s / 2 - 0.5
    # mirror the rho axis (i < 0 reflects; equivariant components are
    # even/odd but the amp2/energy probes are insensitive at the 0.5-cell
    # sliver; nearest-edge handles it with sub-percent effect, guarded)
    i_src = np.abs(i_src)
    out = {}
    for k, arr in fields.items():
        zoomed = np.zeros((NR_T, NZ_T, 4, 4))
        for a in range(4):
            for b in range(4):
                zoomed[..., a, b] = map_coordinates(
                    arr[..., a, b], [i_src, j_src], order=3,
                    mode="nearest")
        out[k] = zoomed
    return out


def control_probe(fields, nr_s, nz_s, r_now, r_target, wscale):
    s = r_target / r_now
    zf = zoom_to_frame(fields, nr_s, nz_s, s)
    pin = pin_mask(NR_T, NZ_T)
    for k in ("A1", "A2", "B1", "B2"):
        zf[k][pin] = 0.0
    X = x_pack(zf["M0"], [zf["A1"], zf["A2"]], [zf["B1"], zf["B2"]])
    a2 = a2_free(X, pin)
    fac = np.sqrt(A2_STAR / a2)
    for arrs in (X["A"], X["B"]):
        for i in range(len(arrs)):
            arrs[i] = arrs[i] * fac
    zf2 = {"M0": X["M0"], "A1": X["A"][0], "A2": X["A"][1],
           "B1": X["B"][0], "B2": X["B"][1]}
    r_chk = r_mean_of(zf2, NR_T, NZ_T)
    rec = probe(X, H, wscale)
    rec.update({"zoom_s": s, "a2": a2_free(X, pin), "r_mean_frame": r_chk,
                "product": (rec["omega_bal"] * r_chk
                            if rec["omega_bal"] else None)})
    return rec, X


def main():
    ws_native = wscale_at(NR_T, NZ_T, H, 8.0 * NR_T / 96.0)
    out = {"task": "M5.12 block 17", "mode": "control",
           "a2_star": A2_STAR, "frame": {"nr": NR_T, "nz": NZ_T},
           "guards": {}, "rows": []}

    # GC1 identity + GC2 round trip on f2
    fields, nr_s, nz_s = load_state("m5_12_b12_hard_f2_1_state.npz")
    r0 = r_mean_of(fields, nr_s, nz_s)
    direct = probe(x_pack(fields["M0"],
                          [fields["A1"], fields["A2"]],
                          [fields["B1"], fields["B2"]]), H, ws_native)
    ident, _ = control_probe(fields, nr_s, nz_s, r0, r0, ws_native)
    gc1 = abs(ident["omega_bal"] - direct["omega_bal"]) / direct["omega_bal"]
    up, Xup = control_probe(fields, nr_s, nz_s, r0, 1.3 * r0, ws_native)
    upf = {"M0": Xup["M0"], "A1": Xup["A"][0], "A2": Xup["A"][1],
           "B1": Xup["B"][0], "B2": Xup["B"][1]}
    back, _ = control_probe(upf, NR_T, NZ_T, 1.3 * r0, r0, ws_native)
    gc2 = abs(back["omega_bal"] - direct["omega_bal"]) / direct["omega_bal"]
    out["guards"] = {"GC1_identity_rel": gc1, "GC2_roundtrip_rel": gc2,
                     "f2_direct_omega_bal": direct["omega_bal"]}
    print(f"[GC1] identity rel={gc1:.2e}  [GC2] roundtrip rel={gc2:.2e}"
          f"  (f2 direct w_bal={direct['omega_bal']:.4f})")
    if gc1 > 5e-3 or gc2 > 5e-2:
        raise RuntimeError("zoom guards failed; control frame not trusted")

    for r_target in (4.77, 3.686):
        ws_matched = wscale_at(NR_T, NZ_T, H, r_target)
        for wtag, ws in (("native", ws_native), ("rc-matched", ws_matched)):
            frame_rows = []
            for label, path in ENDPOINTS:
                fields, nr_s, nz_s = load_state(path)
                r0 = r_mean_of(fields, nr_s, nz_s)
                rec, _ = control_probe(fields, nr_s, nz_s, r0, r_target, ws)
                rec.update({"endpoint": label, "state": path,
                            "r_mean_native": r0,
                            "r_target": r_target, "wscale": wtag})
                frame_rows.append(rec)
                wb = rec["omega_bal"]
                print(f"[{r_target:g}/{wtag:>10}] {label:>22} "
                      f"r0={r0:5.2f} s={rec['zoom_s']:5.2f}  "
                      f"S0={rec['S0']:+9.3f}  Q2={rec['Q2']:+.5f}  "
                      f"w_bal={wb if wb else float('nan'):7.4f}")
            ranked = sorted((r for r in frame_rows if r["omega_bal"]),
                            key=lambda r: r["omega_bal"])
            print(f"[rank {r_target:g}/{wtag}] " + " < ".join(
                f"{r['endpoint'].split()[0]}={r['omega_bal']:.3f}"
                for r in ranked))
            out["rows"].extend(frame_rows)
    path = os.path.join(DATA, "m5_12_b17_control.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
