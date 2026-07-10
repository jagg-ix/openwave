"""M5.12 block-17 ADVERSARIAL AUDIT, A1: independent re-derivation of the
fixed-(size, a2) control machinery.

Attacks:
  (a) re-derive in-frame omega_bal with an INDEPENDENT zoom: my own
      coordinate map + RegularGridInterpolator (linear) + a PROPER even
      coordinate mirror across the rho axis (the control uses abs(i_src),
      an index-space reflection, not a coordinate mirror) + clip-to-edge
      outside handling. Cases: f2 (s > 1), p1 (s < 1), g48 (cross-grid,
      native n48).
  (b) bound the axis handling and the mode=nearest extrapolation:
      variants = {control zoom, my linear mirror, harmonics ZEROED outside
      the source box (s < 1 worst case), first-radial-cell harmonics
      ZEROED (axis worst case)}; the omega_bal spread bounds both.
  (c) the all-harmonic rescale vs the battery convention (rescale_to
      scales the FIRST harmonic only): recompute in-frame omega_bal with
      first-harmonic-only rescale; measure the 2nd-harmonic a2 share.
  (d) GC2 relevance: adjacent ranking gaps per frame from the control
      JSON vs the 2.7e-3 round trip; plus my own round trip at s = 2.25
      (the c2 zoom depth, deeper than the guard's 1.3).

Run:  python m5_12_audit_b17_zoom.py
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.interpolate import RegularGridInterpolator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_d3a_bvp import x_pack                                           # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_b14_seeds import a2_free, probe                                 # noqa: E402
from m5_12_b17_control import (A2_STAR, H, NR_T, NZ_T, ENDPOINTS,          # noqa: E402
                               load_state, r_mean_of, control_probe,
                               zoom_to_frame)


# ---------------- my independent zoom ----------------
def my_zoom(fields, nr_s, nz_s, s, harm_zero_outside=False):
    """my own route: physical-coordinate map, even mirror across the rho
    axis by array extension, linear interpolation, clip-to-edge outside
    (+ optional harmonics-to-zero outside the source box)."""
    rho_s = (np.arange(nr_s) + 0.5) * H
    z_s = (np.arange(nz_s) - nz_s / 2 + 0.5) * H
    rho_ext = np.concatenate(([-rho_s[0]], rho_s))          # even mirror
    Rt, Zt = grid_coords(NR_T, NZ_T, H)
    rq, zq = Rt / s, Zt / s
    outside = (rq > rho_s[-1]) | (np.abs(zq) > z_s[-1])
    rq_c = np.clip(rq, -rho_s[0], rho_s[-1])
    zq_c = np.clip(zq, z_s[0], z_s[-1])
    pts = np.stack([rq_c.ravel(), zq_c.ravel()], axis=-1)
    out = {}
    for k, arr in fields.items():
        zoomed = np.zeros((NR_T, NZ_T, 4, 4))
        for a in range(4):
            for b in range(4):
                src = arr[..., a, b]
                ext = np.concatenate([src[:1], src], axis=0)  # even
                itp = RegularGridInterpolator((rho_ext, z_s), ext,
                                              method="linear")
                zoomed[..., a, b] = itp(pts).reshape(NR_T, NZ_T)
        if harm_zero_outside and k != "M0":
            zoomed[outside] = 0.0
        out[k] = zoomed
    return out


def frame_probe(zf, wscale, first_harm_only=False):
    """pin, rescale to A2_STAR, exact probe (mirrors control_probe)."""
    pin = pin_mask(NR_T, NZ_T)
    zf = {k: v.copy() for k, v in zf.items()}
    for k in ("A1", "A2", "B1", "B2"):
        zf[k][pin] = 0.0
    X = x_pack(zf["M0"], [zf["A1"], zf["A2"]], [zf["B1"], zf["B2"]])
    a2 = a2_free(X, pin)
    fac = np.sqrt(A2_STAR / a2)
    if first_harm_only:
        X["A"][0] = X["A"][0] * fac
        X["B"][0] = X["B"][0] * fac
    else:
        for arrs in (X["A"], X["B"]):
            for i in range(len(arrs)):
                arrs[i] = arrs[i] * fac
    rec = probe(X, H, wscale)
    rec["a2_pre"] = a2
    return rec, X


def h2_share(X, pin):
    """2nd-harmonic amplitude share of the total harmonic a2."""
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), X["M0"].shape)
    a1 = float(np.sum(X["A"][0][free] ** 2) + np.sum(X["B"][0][free] ** 2))
    a2h = float(np.sum(X["A"][1][free] ** 2) + np.sum(X["B"][1][free] ** 2))
    return a2h / (a1 + a2h)


def main():
    ws_native = wscale_at(NR_T, NZ_T, H, 8.0 * NR_T / 96.0)
    r_target = 4.77
    out = {"audit": "b17 A1", "r_target": r_target, "cases": [],
           "variants": {}, "rescale_convention": [], "gc2": {}}

    ctrl = json.load(open(os.path.join(DATA, "m5_12_b17_control.json")))
    pub = {(r["endpoint"], r["r_target"], r["wscale"]): r
           for r in ctrl["rows"]}

    # (a) independent re-derivation, 3 cases incl. cross-grid g48
    for label, path in ENDPOINTS:
        if label.split()[0] not in ("f2", "p1", "g48"):
            continue
        fields, nr_s, nz_s = load_state(path)
        r0 = r_mean_of(fields, nr_s, nz_s)
        s = r_target / r0
        mine, _ = frame_probe(my_zoom(fields, nr_s, nz_s, s), ws_native)
        theirs = pub[(label, r_target, "native")]
        rel = abs(mine["omega_bal"] - theirs["omega_bal"]) / theirs["omega_bal"]
        out["cases"].append({
            "endpoint": label, "s": s,
            "omega_bal_published": theirs["omega_bal"],
            "omega_bal_independent_linear_mirror": mine["omega_bal"],
            "rel_diff": rel,
            "S0_mine": mine["S0"], "Q2_mine": mine["Q2"]})
        print(f"[A1a] {label:>20} s={s:5.3f} pub={theirs['omega_bal']:.4f} "
              f"mine={mine['omega_bal']:.4f} rel={rel:.2e}")

    # (b) variant spread on p1 (s < 1, outside matters) and c2 (deep zoom)
    for tag, path in (("p1", "m5_12_b12_hard_p1_1_state.npz"),
                      ("c2", "m5_12_b12_hard_c2_1_state.npz")):
        fields, nr_s, nz_s = load_state(path)
        r0 = r_mean_of(fields, nr_s, nz_s)
        s = r_target / r0
        vv = {}
        rec, _ = control_probe(fields, nr_s, nz_s, r0, r_target, ws_native)
        vv["control_cubic_absmirror_nearest"] = rec["omega_bal"]
        rec, _ = frame_probe(my_zoom(fields, nr_s, nz_s, s), ws_native)
        vv["mine_linear_evenmirror_clip"] = rec["omega_bal"]
        rec, _ = frame_probe(
            my_zoom(fields, nr_s, nz_s, s, harm_zero_outside=True),
            ws_native)
        vv["mine_harm_zero_outside"] = rec["omega_bal"]
        zf = zoom_to_frame(fields, nr_s, nz_s, s)
        for k in ("A1", "A2", "B1", "B2"):
            zf[k][0, :] = 0.0                    # axis worst case
        rec, _ = frame_probe(zf, ws_native)
        vv["control_first_cell_harm_zeroed"] = rec["omega_bal"]
        vals = np.array(list(vv.values()))
        spread = float((vals.max() - vals.min()) / vals.min())
        out["variants"][tag] = {"s": s, "values": vv, "rel_spread": spread}
        print(f"[A1b] {tag} s={s:5.3f} spread={spread:.2e}  " +
              "  ".join(f"{k}={v:.4f}" for k, v in vv.items()))

    # (c) rescale convention: all-harmonic vs first-harmonic-only
    for label, path in ENDPOINTS:
        fields, nr_s, nz_s = load_state(path)
        r0 = r_mean_of(fields, nr_s, nz_s)
        s = r_target / r0
        zf = zoom_to_frame(fields, nr_s, nz_s, s)
        rec_all, X = frame_probe(zf, ws_native)
        rec_h1, _ = frame_probe(zf, ws_native, first_harm_only=True)
        pin = pin_mask(NR_T, NZ_T)
        share = h2_share(X, pin)
        d = abs(rec_h1["omega_bal"] - rec_all["omega_bal"]) / rec_all["omega_bal"]
        out["rescale_convention"].append({
            "endpoint": label, "h2_share_of_harm_a2": share,
            "omega_all_harm": rec_all["omega_bal"],
            "omega_first_harm_only": rec_h1["omega_bal"], "rel_diff": d})
        print(f"[A1c] {label:>20} h2share={share:.2e} "
              f"all={rec_all['omega_bal']:.4f} h1only={rec_h1['omega_bal']:.4f}"
              f" rel={d:.2e}")

    # (d) GC2 vs the ranking gaps + my deep round trip at s = 2.25
    gaps = {}
    for rt in (4.77, 3.686):
        for wt in ("native", "rc-matched"):
            rows = sorted((r for r in ctrl["rows"]
                           if r["r_target"] == rt and r["wscale"] == wt),
                          key=lambda r: r["omega_bal"])
            adj = [(rows[i]["endpoint"].split()[0],
                    rows[i + 1]["endpoint"].split()[0],
                    (rows[i + 1]["omega_bal"] - rows[i]["omega_bal"])
                    / rows[i]["omega_bal"]) for i in range(len(rows) - 1)]
            gaps[f"{rt}/{wt}"] = adj
    min_gap = min(g for v in gaps.values() for _, _, g in v)
    p1_gap = min(g for v in gaps.values() for a, b, g in v
                 if "p1" in (a, b))
    fields, nr_s, nz_s = load_state("m5_12_b12_hard_f2_1_state.npz")
    r0 = r_mean_of(fields, nr_s, nz_s)
    direct = probe(x_pack(fields["M0"], [fields["A1"], fields["A2"]],
                          [fields["B1"], fields["B2"]]), H, ws_native)
    up = my_zoom(fields, nr_s, nz_s, 2.25)
    back, _ = frame_probe(my_zoom(up, NR_T, NZ_T, 1 / 2.25), ws_native)
    rt_deep = abs(back["omega_bal"] - direct["omega_bal"]) / direct["omega_bal"]
    out["gc2"] = {"published_roundtrip_1p3": 2.69e-3,
                  "my_roundtrip_s2p25": rt_deep,
                  "min_adjacent_gap_rel": min_gap,
                  "min_gap_involving_p1_rel": p1_gap,
                  "adjacent_gaps": {k: [list(t) for t in v]
                                    for k, v in gaps.items()}}
    print(f"[A1d] min adjacent gap {min_gap:.3e}; min gap at p1 "
          f"{p1_gap:.3e}; my s=2.25 roundtrip {rt_deep:.3e}")

    path = os.path.join(DATA, "m5_12_audit_b17_zoom.json")
    json.dump(out, open(path, "w"), indent=2)
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
