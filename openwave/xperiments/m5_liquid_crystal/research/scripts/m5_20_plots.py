"""M5.20 plots: energy ledger + ring/winding trajectories per run.

Usage: python m5_20_plots.py <run_name> [<run_name> ...]
Reads ../data/m5_20_<run_name>.json, writes ../plots/m5_20_dynamics.png
(one row per run: energy ledger | ring + winding | PE split).
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def load(name):
    with open(os.path.join(DATA, f"m5_20_{name}.json")) as f:
        return json.load(f)


def main(names, out="m5_20_dynamics.png"):
    runs = [(n, load(n)) for n in names]
    fig, axes = plt.subplots(len(runs), 3, figsize=(15, 3.2 * len(runs)),
                             squeeze=False)
    for k, (name, d) in enumerate(runs):
        tr = d["trajectory"]
        t = np.array([r["t"] for r in tr])
        pe = np.array([r["PE"] for r in tr])
        ke = np.array([r["KE"] for r in tr])
        ab = np.array([r["E_abs"] for r in tr])
        tot = np.array([r["E_tot"] for r in tr])
        ax = axes[k, 0]
        ax.plot(t, pe, label="PE")
        ax.plot(t, ke, label="KE")
        ax.plot(t, ab, label="E_abs")
        ax.plot(t, tot, "k--", lw=1, label="total")
        ax.set_title(f"{name}: energy ledger", fontsize=10)
        ax.set_xlabel("t")
        ax.legend(fontsize=7)
        ax = axes[k, 1]
        q = np.array([r.get("q_meas", np.nan) for r in tr], dtype=float)
        rr = np.array([r.get("ring13_rho", np.nan) for r in tr], dtype=float)
        ax.plot(t, rr, "C0", label="ring rho (|M13|^2 centroid)")
        ax.set_ylabel("ring rho", color="C0")
        ax2 = ax.twinx()
        ax2.plot(t, q, "C3.", ms=3, label="q_meas")
        ax2.set_ylabel("q_meas", color="C3")
        ax2.set_ylim(-0.1, 1.1)
        ax.set_title(f"{name}: ring + winding", fontsize=10)
        ax.set_xlabel("t")
        ax = axes[k, 2]
        pin = np.array([r.get("PE_in8", np.nan) for r in tr], dtype=float)
        ax.plot(t, pin, "C2", label="PE within r<8 of ring")
        ax.plot(t, pe - pin, "C4", label="PE outside")
        ax.set_title(f"{name}: PE split", fontsize=10)
        ax.set_xlabel("t")
        ax.legend(fontsize=7)
    fig.tight_layout()
    path = os.path.join(PLOTS, out)
    fig.savefig(path, dpi=110)
    print("wrote", path)


if __name__ == "__main__":
    args = sys.argv[1:]
    out = "m5_20_dynamics.png"
    if args and args[0].startswith("--out="):
        out = args[0].split("=", 1)[1]
        args = args[1:]
    main(args, out)
