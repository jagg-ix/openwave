"""M5.20.1 synthesis plots: trajectories per run + the protection-vs-delta
headline figure.

Usage: python m5_20_1_plots.py traj <run_tag> [...]
       python m5_20_1_plots.py headline
Out:   ../plots/m5_20_1_dynamics.png, ../plots/m5_20_1_protection.png
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ARGV = sys.argv[1:]
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def load(tag):
    with open(os.path.join(DATA, f"m5_20_1_run_{tag}.json")) as f:
        return json.load(f)


def traj(tags, out="m5_20_1_dynamics.png"):
    fig, axes = plt.subplots(4, 1, figsize=(11, 12), sharex=True)
    for tag in tags:
        d = load(tag)
        tr = d["trajectory"]
        t = [r["t"] for r in tr]
        lab = f"d={d['delta']} {d['pairing']} {d['mode']}" \
              + (" recal" if d.get("recal") else "")
        axes[0].plot(t, [r.get("q_meas") for r in tr], ".-", ms=2, lw=0.8,
                     label=lab)
        axes[1].plot(t, [r["m13_max"] for r in tr], lw=1)
        axes[2].plot(t, [r.get("PE_in8") for r in tr], lw=1)
        eq = [{"pair_1d": 1, "pair_d0": -1}.get(r.get("core_equalized"), 0)
              for r in tr]
        axes[3].plot(t, eq, ".", ms=3)
    axes[0].set_ylabel("q_meas (centroid read; endpoint verdicts\n"
                       "use the bilinear multi-r_w set)")
    axes[0].legend(fontsize=6, ncol=2)
    axes[1].set_ylabel("m13_max")
    axes[2].set_ylabel("PE_in8 (ring nbhd)")
    axes[3].set_ylabel("core equalized pair\n(+1 = (1,d), -1 = (d,0))")
    axes[3].set_xlabel("t")
    fig.tight_layout()
    path = os.path.join(PLOTS, out)
    fig.savefig(path, dpi=120)
    print("wrote", path)


def headline():
    with open(os.path.join(DATA, "m5_20_1_verdicts.json")) as f:
        V = json.load(f)
    with open(os.path.join(DATA, "m5_20_1_a_theory.json")) as f:
        A = json.load(f)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    # panel 1: verdict grid (closed-box core runs)
    deltas = (0.1, 0.3, 0.5)
    pairs = ("pair_1d", "pair_d0")
    colmap = {"HELD": "#2a9d2a", "UNWOUND": "#c23b3b",
              "MIXED": "#d9a53c", "RADIATES": "#7a4bbf"}
    for i, dd in enumerate(deltas):
        for j, p in enumerate(pairs):
            tag = f"d{str(dd).replace('.', 'p')}_{p}_closed"
            v = V.get(tag, {}).get("verdict", "n/a")
            axes[0].add_patch(plt.Rectangle((i, j), 0.94, 0.94,
                              color=colmap.get(v, "0.8")))
            axes[0].text(i + 0.47, j + 0.47, v, ha="center", va="center",
                         fontsize=9)
    axes[0].set_xticks([i + 0.47 for i in range(3)])
    axes[0].set_xticklabels([str(d) for d in deltas])
    axes[0].set_yticks([0.47, 1.47])
    axes[0].set_yticklabels(["winds (1,d)", "winds (d,0)"])
    axes[0].set_xlim(0, 3)
    axes[0].set_ylim(0, 2)
    axes[0].set_xlabel("delta")
    axes[0].set_title("verdict grid: protection vs delta (closed box)")
    # panel 2: the gap map with production points
    rows = A["gap_map"]
    ds = [r["delta"] for r in rows]
    axes[1].plot(ds, [r["omega_split"] for r in rows], "k-o", ms=3,
                 label="omega_split (activated face)")
    om = np.array([r["omegas"] for r in rows])
    axes[1].plot(ds, om[:, 3], "b--", ms=2, lw=1,
                 label="softest gapped Hessian omega")
    for dd in deltas:
        axes[1].axvline(dd, color="0.8", lw=0.8)
    axes[1].set_xlabel("delta")
    axes[1].set_ylabel("omega")
    axes[1].legend(fontsize=7)
    axes[1].set_title("the activating gap (phase A)")
    # panel 3: m13 last-quarter retention vs delta per pairing
    for p, mk in (("pair_1d", "o-"), ("pair_d0", "s--")):
        xs, ys = [], []
        for dd in deltas:
            tag = f"d{str(dd).replace('.', 'p')}_{p}_closed"
            if tag in V:
                xs.append(dd)
                ys.append(V[tag]["m13_lastq_median"]
                          / max(V[tag]["m13_seed"], 1e-30))
        axes[2].plot(xs, ys, mk, label=f"winds {p[5:]}")
    axes[2].axhline(0.5, color="0.6", ls=":", lw=1)
    axes[2].set_xlabel("delta")
    axes[2].set_ylabel("m13_max last-quarter median / seed")
    axes[2].legend(fontsize=8)
    axes[2].set_title("core amplitude retention")
    fig.tight_layout()
    path = os.path.join(PLOTS, "m5_20_1_protection.png")
    fig.savefig(path, dpi=130)
    print("wrote", path)


if __name__ == "__main__":
    if ARGV and ARGV[0] == "traj":
        traj(ARGV[1:])
    else:
        headline()
