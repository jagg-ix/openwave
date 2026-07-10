"""M5.12 block-17 ADVERSARIAL AUDIT, A2/A3/A4: the metric adjudication,
the descent-rate analysis, and the controlled distance factor.

A2: the candidate normalizations at COMMON size (n32 frame, r = 4.77):
    - matched total a2 (the control's choice; at common size total a2 and
      a2 density are the same budget: the frame volume is common)
    - matched harmonic ENERGY share: scale harmonics so the harmonic part
      of S0 (S0(X) - S0(harmonics zeroed)) matches a common target
      (f2's value at the a2-matched point), solved by bisection on the
      exact probe. If the ranking holds under BOTH, the fixed-(size, a2)
      ruling is normalization-robust.

A3: per-family gains of the controlled floor sequence
    bmix -> wd -> f-cluster -> p1 in all four control frames +
    families-to-band extrapolation at the observed gain rates.

A4: the controlled distance factor: p1 re-probed at every defensible
    M5.8 size anchor (early window 3.47, breathing 4.61/4.77, settled
    4.941, static core 2.628) x wscale {native, rc-matched}, factors vs
    the band [1.07, 1.15].

Run:  python m5_12_audit_b17_metric.py
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

from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_d3a_bvp import x_pack, shat                                      # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_b14_seeds import a2_free, probe                                 # noqa: E402
from m5_12_b17_control import (A2_STAR, H, NR_T, NZ_T, ENDPOINTS,          # noqa: E402
                               load_state, r_mean_of, zoom_to_frame)

BAND = (1.07, 1.15)


def framed_X(path, r_target):
    fields, nr_s, nz_s = load_state(path)
    r0 = r_mean_of(fields, nr_s, nz_s)
    zf = zoom_to_frame(fields, nr_s, nz_s, r_target / r0)
    pin = pin_mask(NR_T, NZ_T)
    for k in ("A1", "A2", "B1", "B2"):
        zf[k][pin] = 0.0
    X = x_pack(zf["M0"], [zf["A1"], zf["A2"]], [zf["B1"], zf["B2"]])
    fac = np.sqrt(A2_STAR / a2_free(X, pin))
    for arrs in (X["A"], X["B"]):
        for i in range(len(arrs)):
            arrs[i] = arrs[i] * fac
    return X, pin


def scaled(X, fac):
    return {"M0": X["M0"],
            "A": [a * fac for a in X["A"]], "B": [b * fac for b in X["B"]]}


def harm_energy(X, wscale):
    """harmonic share of S0: S0(X) - S0(harmonics zeroed)."""
    s0 = shat(X, 0.0, H, wscale)
    X0 = scaled(X, 0.0)
    return s0 - shat(X0, 0.0, H, wscale)


def match_s0(X, wscale, s0_star):
    """find the harmonic scale factor (branch nearest fac = 1) at which
    the TOTAL S0 hits s0_star. S0(fac) is non-monotone (the mix channel
    lowers S0 quadratically before the quartic term wins), so scan for
    the bracket nearest 1, then bisect."""
    facs = np.linspace(0.05, 3.0, 60)
    vals = np.array([shat(scaled(X, f), 0.0, H, wscale) - s0_star
                     for f in facs])
    br = [i for i in range(len(facs) - 1) if vals[i] * vals[i + 1] <= 0]
    if not br:
        return None, None
    i = min(br, key=lambda j: abs(0.5 * (facs[j] + facs[j + 1]) - 1.0))
    lo, hi, f_lo = facs[i], facs[i + 1], vals[i]
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        fm = shat(scaled(X, mid), 0.0, H, wscale) - s0_star
        if f_lo * fm <= 0:
            hi = mid
        else:
            lo, f_lo = mid, fm
    fac = 0.5 * (lo + hi)
    return fac, scaled(X, fac)


def main():
    out = {"audit": "b17 A2/A3/A4", "A2_energy_ranking": {},
           "A3_gains": {}, "A4_distance": {}}
    ws_native = wscale_at(NR_T, NZ_T, H, 8.0 * NR_T / 96.0)
    r_common = 4.77

    # ---------- A2: energy-matched ranking at common size ----------
    Xs = {}
    for label, path in ENDPOINTS:
        Xs[label.split()[0]] = framed_X(path, r_common)[0]
    for wtag, ws in (("native", ws_native),
                     ("rc-matched", wscale_at(NR_T, NZ_T, H, r_common))):
        s0_star = shat(Xs["f2"], 0.0, H, ws)     # f2's a2-matched S0
        rows = []
        for tag, X in Xs.items():
            s0_static = shat(scaled(X, 0.0), 0.0, H, ws)
            e0 = harm_energy(X, ws)
            fac, Xm = match_s0(X, ws, s0_star)
            if Xm is None:
                rows.append({"tag": tag, "S0_static": s0_static,
                             "e_harm_a2matched": e0, "fac": None,
                             "omega_bal": None,
                             "note": "s0_star unreachable at any amplitude"})
                print(f"[A2 {wtag}] {tag:>4}: UNREACHABLE "
                      f"(S0_static {s0_static:.1f} vs target {s0_star:.1f})")
                continue
            rec = probe(Xm, H, ws)
            pin = pin_mask(NR_T, NZ_T)
            rows.append({"tag": tag, "S0_static": s0_static,
                         "e_harm_a2matched": e0, "s0_star": s0_star,
                         "fac": fac, "a2_at_match": a2_free(Xm, pin),
                         "omega_bal": rec["omega_bal"], "Q2": rec["Q2"],
                         "S0": rec["S0"]})
        ranked = sorted((r for r in rows if r["omega_bal"]),
                        key=lambda r: r["omega_bal"])
        out["A2_energy_ranking"][wtag] = rows
        print(f"[A2 {wtag}] S0-matched rank: " + " < ".join(
            f"{r['tag']}={r['omega_bal']:.3f}" for r in ranked))

    # the well-posed budget robustness: the common-a2 budget swept x0.5/1/2
    out["A2_budget_sweep"] = {}
    for wtag, ws in (("native", ws_native),
                     ("rc-matched", wscale_at(NR_T, NZ_T, H, r_common))):
        sweep = {}
        for mult in (0.5, 1.0, 2.0):
            fac = np.sqrt(mult)
            rows = []
            for tag, X in Xs.items():
                rec = probe(scaled(X, fac), H, ws)
                rows.append((tag, rec["omega_bal"]))
            rows.sort(key=lambda t: (t[1] is None, t[1]))
            sweep[f"a2_x{mult:g}"] = rows
            print(f"[A2 {wtag} budget x{mult:g}] " + " < ".join(
                f"{t}={w:.3f}" if w else f"{t}=None" for t, w in rows))
        out["A2_budget_sweep"][wtag] = sweep

    # ---------- A3: controlled per-family gains ----------
    ctrl = json.load(open(os.path.join(DATA, "m5_12_b17_control.json")))
    fam = {"bmix": ("c2", "g48"), "wd": ("wd",), "f": ("f1", "f2"),
           "p1": ("p1",)}
    seq = ["bmix", "wd", "f", "p1"]
    gains = {}
    for rt in (4.77, 3.686):
        for wt in ("native", "rc-matched"):
            rows = {r["endpoint"].split()[0]: r["omega_bal"]
                    for r in ctrl["rows"]
                    if r["r_target"] == rt and r["wscale"] == wt}
            floors = {f: min(rows[t] for t in tags)
                      for f, tags in fam.items()}
            g = [(seq[i], seq[i + 1],
                  1.0 - floors[seq[i + 1]] / floors[seq[i]])
                 for i in range(len(seq) - 1)]
            gains[f"{rt}/{wt}"] = {"floors": floors,
                                   "gains": [list(t) for t in g]}
            print(f"[A3 {rt}/{wt}] floors " +
                  " ".join(f"{f}={v:.3f}" for f, v in floors.items()) +
                  "  gains " + " ".join(f"{a}->{b}:{x*100:.1f}%"
                                        for a, b, x in g))
    # extrapolation: families to band at best / median observed gain
    p1_floor = {k: v["floors"]["p1"] for k, v in gains.items()}
    all_gains = [x for v in gains.values() for _, _, x in v["gains"]]
    best_g, med_g = max(all_gains), float(np.median(all_gains))
    extra = {}
    for k, wb in p1_floor.items():
        for gname, g in (("best", best_g), ("median", med_g)):
            n = np.log(BAND[1] / wb) / np.log(1.0 - g)
            extra[f"{k}/{gname}_gain_{g*100:.0f}%"] = float(n)
    out["A3_gains"] = {"per_frame": gains, "best_gain": best_g,
                       "median_gain": med_g,
                       "families_to_band_at_rate": extra}
    print(f"[A3] families to band: best-rate {min(extra.values()):.1f}"
          f" .. median-rate {max(extra.values()):.1f}")

    # ---------- A4: controlled distance across M5.8 anchors ----------
    anchors = {"early_window_3p47": 3.47, "breathing_4p61": 4.61,
               "breathing_4p77": 4.77, "settled_4p941": 4.941,
               "static_core_2p628": 2.628}
    rows = []
    for aname, rt in anchors.items():
        X, _ = framed_X("m5_12_b12_hard_p1_1_state.npz", rt)
        for wtag, ws in (("native", ws_native),
                         ("rc-matched", wscale_at(NR_T, NZ_T, H, rt))):
            rec = probe(X, H, ws)
            wb = rec["omega_bal"]
            rows.append({"anchor": aname, "r_target": rt, "wscale": wtag,
                         "omega_bal": wb,
                         "factor_vs_band": [wb / BAND[1], wb / BAND[0]]})
            print(f"[A4] {aname:>18} {wtag:>10} w_bal={wb:.4f} "
                  f"factor {wb/BAND[1]:.2f}-{wb/BAND[0]:.2f}")
    facs = [f for r in rows for f in r["factor_vs_band"]]
    breathing = [f for r in rows for f in r["factor_vs_band"]
                 if "breathing" in r["anchor"]]
    out["A4_distance"] = {"rows": rows,
                          "headline_breathing_window":
                              [min(breathing), max(breathing)],
                          "full_bracket_all_anchors":
                              [min(facs), max(facs)],
                          "band": list(BAND)}
    print(f"[A4] breathing-window bracket {min(breathing):.2f}-"
          f"{max(breathing):.2f}; all-anchor {min(facs):.2f}-{max(facs):.2f}")

    path = os.path.join(DATA, "m5_12_audit_b17_metric.json")
    json.dump(out, open(path, "w"), indent=2)
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
