"""M5.17: two-charge Coulomb figure (compensated interaction + running coupling).

Left: (E_pair(d) - E0_fit) . d vs d; a 1/d Coulomb interaction is a FLAT line
whose level is the coefficient A, compared against the +/- 64 pi prediction of
the M5.16 lock. Right: the running-coupling readout alpha_eff(d)/alpha =
|E_pair - E0| d / (64 pi) vs d in fm. Fixed-ansatz curves always plotted;
pinned-core relaxed points overlaid when their JSONs exist.
"""
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

BLUE, ORANGE = "#2a78d6", "#c65a1e"          # categorical slots 1-2 (validated)
INK, MUTED, GRID = "#1a1a19", "#5f5e56", "#e3e2da"
A_PRED = 64.0 * np.pi

fx = json.load(open(os.path.join(DATA, "m5_17_two_charge_fixed.json")))
ell = fx["ell_fm_per_grid"]
# relax overlay: LIKEPAIR only. The antipair relax ANNIHILATES (melt-bridge
# unwinding, E -> vacuum residual): no equilibrium exists to plot. The likepair
# relax does not converge either (melt-line restructuring, gradient rising):
# its points are shown but labeled non-converged.
relax = {}
p = os.path.join(DATA, "m5_17_two_charge_relax_like.json")
if os.path.exists(p):
    relax["like"] = json.load(open(p))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=160)
fig.patch.set_facecolor("white")

series = (("antipair", "anti", BLUE, "o", "hedgehog + anti (q2 = -1)"),
          ("likepair", "like", ORANGE, "s", "like charges (q2 = +1)"))

for key, tag, col, mk, label in series:
    cv = fx["curves"][key]
    d = np.array(cv["d"])
    Eint = np.array(cv["E_pair"]) - cv["fit_E0"]
    ax1.plot(d, Eint * d, mk + "-", color=col, lw=1.8, ms=6,
             label=f"{label}, fixed ansatz")
    if tag in relax:
        rr = relax[tag]
        dr = np.array([r["d"] for r in rr["rows"]])
        Er = np.array([r["E_relaxed"] for r in rr["rows"]]) - rr["fit_E0"]
        ax1.plot(dr, Er * dr, mk, color=col, ms=8, mfc="white", mew=1.8,
                 label=f"{label}, relaxed: NOT converged (melt-line escape)")
    # running coupling (right panel)
    ax2.plot(d * ell, np.abs(Eint) * d / A_PRED, mk + "-", color=col,
             lw=1.8, ms=6, label=f"{label}, fixed ansatz")
    if tag in relax:
        ax2.plot(dr * ell, np.abs(Er) * dr / A_PRED, mk, color=col, ms=8,
                 mfc="white", mew=1.8, label=f"{label}, relaxed")

for A, txt in ((A_PRED, "+64π (Coulomb, M5.16 lock)"),
               (-A_PRED, "−64π")):
    ax1.axhline(A, color=MUTED, lw=1.2, ls="--")
    ax1.annotate(txt, xy=(0.99, A), xycoords=("axes fraction", "data"),
                 ha="right", va="bottom", fontsize=8.5, color=MUTED,
                 xytext=(0, 2), textcoords="offset points")
ax1.set_xlabel("separation d  (grid units)", color=INK)
ax1.set_ylabel(r"$(E_{pair}(d) - E_0)\cdot d$   (grid units)", color=INK)
ax1.set_title("Compensated interaction: flat = Coulomb 1/d", fontsize=10.5,
              color=INK)

ax2.axhline(1.0, color=MUTED, lw=1.2, ls="--")
ax2.annotate("α_eff = α", xy=(0.99, 1.0),
             xycoords=("axes fraction", "data"), ha="right", va="bottom",
             fontsize=8.5, color=MUTED, xytext=(0, 2),
             textcoords="offset points")
ax2.set_xlabel("separation d  (fm, via the β = 1 lock)", color=INK)
ax2.set_ylabel(r"$\alpha_{eff}(d)\,/\,\alpha$", color=INK)
ax2.set_title("Running-coupling readout", fontsize=10.5, color=INK)

for ax in (ax1, ax2):
    ax.grid(True, color=GRID, lw=0.7)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=MUTED, labelsize=8.5)
    ax.legend(fontsize=8, frameon=False, labelcolor=INK)

fig.suptitle("M5.17 two-charge Coulomb anchor (locked β = 1 potential)",
             fontsize=11.5, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.96))
out = os.path.join(PLOTS, "m5_17_two_charge.png")
fig.savefig(out, facecolor="white")
print("plot ->", out)
