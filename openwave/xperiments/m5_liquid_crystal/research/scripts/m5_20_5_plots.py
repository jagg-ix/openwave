"""M5.20.5 plots: root ladders + working points (a1), solver
convergence (a2/a3), observables (a4obs), escape gates (b), field-state
cross-section strips (the film standard, m5_visualization.md).

Run:  python m5_20_5_plots.py a1|a2|a4|b|maps_a|film_b
Out:  ../plots/m5_20_5_*.png
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                                    # noqa: E402
import numpy as np                                                 # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def plot_a1():
    a1 = load("m5_20_5_a_a1.json")
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    colors = {"J23^K2": "C0", "J23^K3": "C1", "J12^K1": "C2"}
    for name, fam in a1["families"].items():
        rows = fam["rows"]
        chi = [r["chi"] for r in rows]
        q2 = [r["Q2_avg"] for r in rows]
        axes[0].plot(chi, q2, "o-", ms=3, color=colors[name], label=name)
        rc = [(r["chi"], r["root_omega"]) for r in rows
              if r["root_omega"] is not None]
        if rc:
            axes[1].semilogy([c for c, _ in rc], [w for _, w in rc],
                             "o-", ms=3, color=colors[name], label=name)
        if fam["chi_crossing"] is not None:
            axes[0].axvline(fam["chi_crossing"], color=colors[name],
                            ls=":", lw=1)
    axes[0].axhline(0, color="k", lw=0.6)
    axes[0].set_yscale("symlog", linthresh=1.0)
    axes[0].set_xlabel("chi (boost rapidity of the conjugation)")
    axes[0].set_ylabel("Q2_avg (corrected phi-averaged kinetic)")
    axes[0].set_title("Q2_avg(chi): the three distinct elliptic families\n"
                      "(recipe loop seed; dotted = sign crossing chi_c)")
    axes[1].axhline(a1["w_ladder"], color="r", ls="--", lw=1.2,
                    label=f"chirped ladder w1(ring) = {a1['w_ladder']:.2f}")
    for wp in a1["working_points"]:
        axes[1].plot([wp["chi"]], [wp["omega"]], "k*", ms=14, zorder=5)
    axes[1].set_xlabel("chi")
    axes[1].set_ylabel("balance root w* = sqrt(-U / Q2_avg)")
    axes[1].set_title("the root ladders w*(chi) + working points (stars)\n"
                      "(monotone: no interior dS/dchi extremum; the ladder\n"
                      "scale sits AT the crossing edge)")
    for ax in axes:
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.tight_layout()
    p = os.path.join(PLOTS, "m5_20_5_a1_ladders.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    print("wrote", p)


def plot_a2():
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6), squeeze=False)
    axes = axes[0]
    for k, wp in enumerate((0, 1, 2)):
        fn = f"m5_20_5_a_a2_wp{wp}.json"
        if not os.path.exists(os.path.join(DATA, fn)):
            axes[k].set_title(f"wp{wp}: (not run)")
            continue
        a2 = load(fn)
        ax = axes[k]
        for run in a2["runs"]:
            qv = run.get("q_r4")
            q_lost = qv is None or abs(abs(qv) - 0.5) > 0.01
            lbl = (f"{run['method']}/{run['start']}"
                   + (" (q lost)" if q_lost else ""))
            if "hist" in run:
                ax.semilogy([hh["it"] for hh in run["hist"]],
                            [hh["rel"] for hh in run["hist"]],
                            "o-", ms=2, label=lbl)
            else:
                # no per-iteration history: show the endpoint only
                ax.semilogy([400], [run["rel_final"]], "s", ms=9,
                            label=lbl + f" end {run['rel_final']:.3f}")
        ax.axhline(1e-3, color="r", ls="--", lw=1,
                   label="bar 1e-3 (pre-registered)")
        w = a2["wp"]
        ax.set_title(f"wp{wp}: {w['fam']} chi={w['chi']:.3f} "
                     f"w*={w['omega']:.3g}")
        ax.set_xlabel("iteration")
        ax.set_ylabel("|gradShat| / |G_static|")
        ax.grid(alpha=0.3)
        ax.legend(fontsize=7)
    fig.suptitle("M5.20.5 a2: the extremal solve, 3 methods x 2 starts "
                 "per working point", fontsize=12)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    p = os.path.join(PLOTS, "m5_20_5_a2_convergence.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    print("wrote", p)


def plot_a4(wp=0):
    obs = load(f"m5_20_5_a_a4obs_wp{wp}.json")
    a3 = load(f"m5_20_5_a_a3_wp{wp}.json")
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    c = obs["containment"]
    for tag, st, ls in (("converged/best state", c["state"], "-"),
                        ("baseline (recipe loop)", c["baseline"], "--")):
        axes[0].semilogy(st["rho"], np.maximum(st["profile"], 1e-16),
                         ls, label=f"{tag}: r50={st['r50']:.1f} "
                         f"r90={st['r90']:.1f}")
    axes[0].set_xlabel("rho")
    axes[0].set_ylabel("static energy per rho shell (z-summed)")
    axes[0].set_title("containment: the energy stays at the ring?")
    axes[0].legend(fontsize=8)
    rounds = a3["rounds"]
    axes[1].semilogy([r["round"] for r in rounds],
                     [abs(r["H"]) for r in rounds], "o-", label="|H|")
    axes[1].semilogy([r["round"] for r in rounds],
                     [r["resid_rel"] for r in rounds], "s-",
                     label="resid rel")
    axes[1].set_xlabel("a3 round")
    axes[1].set_title("coupled stationarity: H -> 0 certificate + "
                      "residual")
    axes[1].legend(fontsize=8)
    cl = obs["clock_vs_ladder"]
    axes[2].bar(["w* (root)", "w1 ladder @ ring"],
                [cl["omega_star"], cl["w_ladder_at_ring"]])
    axes[2].set_yscale("log")
    axes[2].set_title(f"clock vs chirped ladder: ratio = "
                      f"{cl['ratio']:.2e}")
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    p = os.path.join(PLOTS, f"m5_20_5_a4_observables_wp{wp}.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    print("wrote", p)


def plot_b():
    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8))
    # b1 statics traces (the beta ladder: ring drift = the anchor break)
    verdicts = []
    for i, (btag, lbl) in enumerate((("0.01", "beta = 1e-2"),
                                     ("0.0001", "beta = 1e-4"),
                                     ("0", "beta = 0 (pure -s2)"))):
        fn = f"m5_20_5_b_b1_b{btag}.json"
        if not os.path.exists(os.path.join(DATA, fn)):
            continue
        b1 = load(fn)
        hist = [hh for hh in b1["hist"] if "E" in hh]
        axes[0].plot([hh["it"] for hh in hist],
                     [hh["ring_rho"] for hh in hist], "o-", ms=3,
                     color=f"C{i}", label=lbl)
        verdicts.append(b1["anchors_survive"])
    if verdicts:
        b1 = load("m5_20_5_b_b1_b0.01.json")
        axes[0].axhline(b1["baseline"]["ring_rho"], color="k", ls=":",
                        lw=1, label="baseline ring rho = 17.46")
        axes[0].set_title("b1 statics (gamma = -1): ring drift; anchors "
                          + ("SURVIVE" if all(verdicts) else
                             "BREAK at every beta (q -> 0)"))
        axes[0].set_xlabel("FIRE iteration")
        axes[0].set_ylabel("ring rho")
        axes[0].legend(fontsize=8, loc="upper left")
    # b2 PSD margins: |mineig| on log scale, sign annotated
    fn = "m5_20_5_b_b2.json"
    if os.path.exists(os.path.join(DATA, fn)):
        b2 = load(fn)
        tags = list(b2["backgrounds"])
        betas = ["beta=0", "beta=0.0001", "beta=0.01"]
        w = 0.25
        for i, b in enumerate(betas):
            vals = [b2["backgrounds"][t][b]["mineig"] for t in tags]
            xs = np.arange(len(tags)) + (i - 1) * w
            axes[1].bar(xs, [abs(v) for v in vals], w, label=b)
            for x, v in zip(xs, vals):
                axes[1].annotate(f"{v:+.2e}", (x, abs(v)),
                                 ha="center", va="bottom", fontsize=7,
                                 rotation=90, xytext=(0, 3),
                                 textcoords="offset points")
        axes[1].set_xticks(range(len(tags)))
        axes[1].set_xticklabels(tags, fontsize=8)
        axes[1].set_yscale("log")
        axes[1].set_ylim(1e-14, 30)
        axes[1].set_ylabel("|min-eig| (sign annotated)")
        axes[1].set_title("b2: min-eig of K_esc = Kq - Ks2 + beta Kc\n"
                          "(own build: beta = 0 marginal at machine zero;\n"
                          "margins match the audit exactly)")
        axes[1].legend(fontsize=8)
    for ax in axes:
        ax.grid(alpha=0.3)
    fig.tight_layout()
    p = os.path.join(PLOTS, "m5_20_5_b_gates.png")
    fig.savefig(p, dpi=110)
    plt.close(fig)
    print("wrote", p)


def maps_a(wp=0):
    """field-state cross-section prints (the standing simulation rule):
    the recipe seed (t = 0 analog) + the a3 converged/best state, basic
    template rows (pseudo-time = solver stage)."""
    import m5_film
    from m5_20_4_a_bvp import load_seed
    M0 = load_seed("recipe")
    fn = os.path.join(DATA, f"m5_20_5_a_a3_wp{wp}_state.npz")
    if not os.path.exists(fn):
        fn = os.path.join(DATA, f"m5_20_5_a_a2_wp{wp}_best.npz")
    Mx = np.load(fn)["M"]
    states = [{"it": 0, "t": 0.0, "M": M0},
              {"it": 1, "t": 1.0, "M": Mx}]
    p = os.path.join(PLOTS, f"m5_20_5_a_maps_wp{wp}.png")
    m5_film.film_strip(
        states, p, template="basic",
        suptitle="M5.20.5 arm A: the recipe loop seed (top) vs the "
                 "extremal-solve end state (bottom; pseudo-time = "
                 "solver stage, not dynamics)")
    return p


def film_b(beta=1e-2):
    """b3 film strip per the standard (basic template)."""
    import m5_film
    z = np.load(os.path.join(DATA, f"m5_20_5_b_b3_b{beta:g}_films.npz"))
    ts = z["ts"]
    states = [{"it": i, "t": float(ts[i]), "M": z[f"M{i}"]}
              for i in range(len(ts))]
    p = os.path.join(PLOTS, f"m5_20_5_b_film_b{beta:g}.png")
    m5_film.film_strip(
        states, p, template="basic",
        suptitle=f"M5.20.5 arm B: the loop seed under the escape "
                 f"dynamics (gamma = -1 s2 + beta = {beta:g} qc, "
                 f"a = 4.5)")
    return p


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "a1"
    if which == "a1":
        plot_a1()
    elif which == "a2":
        plot_a2()
    elif which == "a4":
        plot_a4(int(ARGV[1]) if len(ARGV) > 1 else 0)
    elif which == "b":
        plot_b()
    elif which == "maps_a":
        maps_a(int(ARGV[1]) if len(ARGV) > 1 else 0)
    elif which == "film_b":
        film_b()
    else:
        raise SystemExit(f"unknown phase {which}")
