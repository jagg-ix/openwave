"""M5.20.4 plots: the formulation-search figures.

    a1b      the elliptic-family Q2(chi) crossings + root ladder
    closure  arm C: min-eig(K_total) vs beta per background + a-window
    a4       the orbit-residual descent curve
Run:  python m5_20_4_plots.py a1b|closure|a4|all
Out:  ../plots/m5_20_4_<name>.png
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def plot_a1b():
    with open(os.path.join(DATA, "m5_20_4_a_a1b_recipe.json")) as f:
        d = json.load(f)
    U = d["U"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    for name, fam in d["families"].items():
        chi = np.array(fam["chi"])
        q2 = np.array(fam["Q2"])
        ax1.plot(chi, np.sign(q2) * np.log10(1 + np.abs(q2)), label=name)
        rr = [(c, r) for c, r in zip(fam["chi"], fam["root_omega"])
              if r is not None]
        if rr:
            ax2.semilogy([c for c, _ in rr], [r for _, r in rr],
                         "o-", ms=3, label=name)
    ax1.axhline(0.0, color="k", lw=0.8)
    ax1.set_xlabel("chi (boost rapidity of the conjugation)")
    ax1.set_ylabel("sign(Q2) log10(1 + |Q2|)")
    ax1.set_title("Q2 along the elliptic (periodic) families\n"
                  "all six cross 0: periodic orbits with Q2 < 0 exist")
    ax1.legend(fontsize=8)
    ax2.set_xlabel("chi")
    ax2.set_ylabel("balance root omega* = sqrt(-U/Q2)")
    ax2.set_title(f"the root ladder (U = {U:.3f} > 0, H = 0 exact)")
    ax2.legend(fontsize=8)
    fig.suptitle("M5.20.4 arm A: free-period balance roots on "
                 "boost-conjugated rotation orbits (recipe loop)",
                 fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    p = os.path.join(PLOTS, "m5_20_4_a1b_roots.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    print("wrote", os.path.relpath(p, HERE))


def plot_closure():
    import sys as _s
    _s.argv = _s.argv[:1]
    from m5_20_4_c_terms import (A_STAR, build_k10, k10_add, load_seed,
                                 a_window_vacuum, NR, H)
    with open(os.path.join(DATA, "m5_20_4_c_census.json")) as f:
        cen = json.load(f)
    betas = np.logspace(-3, 1, 25)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    for tag in ("recipe", "raw", "remnant"):
        M = load_seed(tag)
        K10q4 = 4.0 * build_k10(M, H)
        K10c = k10_add(M[: NR - 1, 1:-1], 1.0, A_STAR)
        mins = [float(np.linalg.eigvalsh(K10q4 + b * K10c).min())
                for b in betas]
        ax1.plot(betas, mins, "o-", ms=3,
                 label=f"{tag} (beta* = {cen[tag]['beta_star']:.3f})")
    ax1.set_xscale("log")
    ax1.axhline(0.0, color="k", lw=0.8)
    ax1.set_xlabel("beta (dressing coefficient)")
    ax1.set_ylabel("min eig of K_total over cells")
    ax1.set_title("arm C: the qc dressing closes K at beta* ~ 1.31\n"
                  "(P = aI - etaM, a = 4.5)")
    ax1.legend(fontsize=8)
    win = cen["a_window_vacuum"]["scan"]
    ax2.plot([r[0] for r in win], [r[1] for r in win], "o-", ms=3)
    ax2.axhline(0.0, color="k", lw=0.8)
    ax2.set_xlabel("dressing root a")
    ax2.set_ylabel("vacuum kinetic min-eig")
    ax2.set_title("the closure window a in (1, g): measured "
                  f"({cen['a_window_vacuum']['window'][0]:.2f}, "
                  f"{cen['a_window_vacuum']['window'][1]:.2f})")
    fig.suptitle("M5.20.4 arm C: the two-sided dressed quadratic closes "
                 "the kinetic form (but breaks the statics: see the "
                 "statics gate)", fontsize=13)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    p = os.path.join(PLOTS, "m5_20_4_c_closure.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    print("wrote", os.path.relpath(p, HERE))


def plot_a4():
    with open(os.path.join(DATA, "m5_20_4_a_a4.json")) as f:
        d = json.load(f)
    hist = d["hist"]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.semilogy([h["it"] for h in hist], [h["phi_gnorm"] for h in hist],
                "o-")
    ax.set_xlabel("descent iteration")
    ax.set_ylabel("|grad Shat|")
    ax.set_title(f"M5.20.4 arm A4: orbit-residual descent at the "
                 f"deepest root\n{d['rot']}^{d['boost']} chi = "
                 f"{d['chi']}, omega* = {d['omega']:.3e}; residual "
                 f"x{d['resid_reduction']:.4f}, q stays "
                 f"{d['q_r4']}")
    fig.tight_layout()
    p = os.path.join(PLOTS, "m5_20_4_a4_descent.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    print("wrote", os.path.relpath(p, HERE))


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "all"
    if which in ("a1b", "all"):
        plot_a1b()
    if which in ("closure", "all"):
        plot_closure()
    if which in ("a4", "all"):
        plot_a4()
