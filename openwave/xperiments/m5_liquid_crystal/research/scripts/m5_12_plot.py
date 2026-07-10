"""M5.12 figures: (a) phase D0 core-prescription verdict vs the M5.17/18
baselines; (b) phase A loop-scan ring trajectories. Headless matplotlib.

Run:  python m5_12_plot.py
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
os.makedirs(PLOTS, exist_ok=True)


def _load(name):
    p = os.path.join(DATA, name)
    if not os.path.exists(p):
        return None
    with open(p) as f:
        return json.load(f)


def main():
    d0h = _load("m5_12_d0_hedgehog.json")
    d0p = _load("m5_12_d0_pair_anti.json")
    scan = _load("m5_12_loop_scan_melt.json")
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))

    # (a) melt-channel verdict: bridge melt_min across treatments
    ax = axes[0]
    labels, vals, colors = [], [], []
    base = _load("m5_18_spectral_pair_anti.json")
    if base:
        for r in base["rows"]:
            labels.append(f"M5.18 d={r['d']:g}\n(melt core)")
            vals.append(r["melt_min_axis_strip"])
            colors.append("0.6")
    if d0p:
        for r in d0p["rows"]:
            lat = "lat" if r["z_centers_on_cell_centers"] else "off"
            labels.append(f"D0 d={r['d']:g}\n(aI core, {lat})")
            vals.append(r["melt_min_axis_strip"])
            colors.append("#1f77b4" if r["z_centers_on_cell_centers"] else "#17becf")
    if vals:
        e_relaxed = ([r["E_relaxed"] for r in base["rows"]] if base else []) + \
                    ([r["E_relaxed"] for r in d0p["rows"]] if d0p else [])
        ax.bar(range(len(vals)), vals, color=colors)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(labels, fontsize=7)
        ax.axhline(0.008, color="r", ls="--", lw=1, label="M5.18 bridge (open)")
        ax.set_yscale("log")
        ax.set_ylabel("melt_min on axis strip (bars)")
        ax2 = ax.twinx()
        ax2.plot(range(len(e_relaxed)), e_relaxed, "kx", ms=8, mew=2,
                 label="E after relax (x)")
        ax2.set_ylabel("E_relaxed (vacuum residual = annihilated)")
        ax2.legend(loc="center right", fontsize=7)
        ax.set_title("(a) antipair: ALL annihilate (E -> ~0); D0's high melt_min\n"
                     "is the aI cores themselves (unwinding needs no bridge)",
                     fontsize=9)
        ax.legend(fontsize=7, loc="upper left")

    # (b) hedgehog leg: energy drop comparison
    ax = axes[1]
    rows = []
    if d0h:
        rows.append(("D0 aI-core\n(a*=%.2f)" % d0h["a_star"],
                     d0h["drop_rel"], d0h["melt_min_s"]))
    rows.append(("M5.18 spectral\n(melt core)", 0.548, 0.508))
    rows.append(("M5.17 LdG n64\n(melt core)", 0.35, float("nan")))
    x = np.arange(len(rows))
    ax.bar(x - 0.2, [r[1] for r in rows], width=0.4, label="rel. E drop after bump relax")
    ax.bar(x + 0.2, [r[2] for r in rows], width=0.4, label="melt_min_s after")
    ax.set_xticks(x)
    ax.set_xticklabels([r[0] for r in rows], fontsize=7)
    ax.axhline(0.05, color="r", ls="--", lw=1, label="escape threshold (5%)")
    ax.set_title("(b) hedgehog escape: core prescription vs baselines")
    ax.legend(fontsize=7)

    # (c) loop-scan ring trajectories
    ax = axes[2]
    if scan:
        for row in scan["rows"]:
            tag = f"R{int(row['R0'])}_q{str(row['q']).replace('.', 'p')}_{scan['core']}"
            single = _load(f"m5_12_loop_{tag}.json")
            if not single:
                continue
            tr = single["trajectory"]
            v = row["verdict"]
            if v == "stable" and row.get("gnorm_decades", 0) < 5:
                v = "contracting stall"        # the double-criterion override
            ax.plot([t["it"] for t in tr], [t["ring_rho"] for t in tr],
                    marker=".", ms=3,
                    label=f"R0={row['R0']:g} q={row['q']:g}: {v}")
        ax.set_xlabel("iteration")
        ax.set_ylabel("ring radius rho (cells)")
        ax.set_title(f"(c) loop ring radius, core={scan['core']}")
        ax.legend(fontsize=6)
    fig.suptitle("M5.12 phases D0 + A: the core prescription and the rotated vortex loop")
    fig.tight_layout()
    out = os.path.join(PLOTS, "m5_12_d0_loop.png")
    fig.savefig(out, dpi=130)
    print(f"plot -> {out}")


if __name__ == "__main__":
    main()
