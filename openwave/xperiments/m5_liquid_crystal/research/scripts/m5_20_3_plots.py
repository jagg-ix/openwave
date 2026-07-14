"""M5.20.3 synthesis plots.

    anatomy   E/KE/sector-amplitude/winding traces of the regularized
              free-EL runs up to t* (one column per run)
    sections  seed + last-finite-endpoint cross-section maps in the
              M5.20-SERIES spec (|M13| / max eigenvalue / log10 energy
              density; the m5_20_1_endpoints.png format)
    chirp     the rho-chirped true-L vacuum ladder (D2)
    card      the ill-posedness card: t*(rel_cut) per seed + t*(dt)

Usage: python m5_20_3_plots.py anatomy|sections|chirp|card|all
Out:   ../plots/m5_20_3_*.png
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
TAGS = ["recipe_rc1e-2", "recipe_rc1e-1", "raw_rc1e-2", "remnant_rc1e-2"]


def _load_c(tag):
    p = os.path.join(DATA, f"m5_20_3_c_{tag}.json")
    if not os.path.exists(p):
        return None
    with open(p) as f:
        d = json.load(f)
    d["fin"] = [r for r in d["trajectory"]
                if np.isfinite(r.get("E_tot", float("nan")))]
    return d


def anatomy():
    ds = [(t, _load_c(t)) for t in TAGS]
    ds = [(t, d) for t, d in ds if d]
    fig, axes = plt.subplots(4, len(ds), figsize=(4.2 * len(ds), 11),
                             squeeze=False, sharex="col")
    for k, (tag, d) in enumerate(ds):
        fin = d["fin"][:-1] or d["fin"]     # drop the singular last snap
        t = np.array([r["t"] for r in fin])
        ax = axes[0, k]
        E = np.array([r["E_tot"] for r in fin])
        ax.plot(t, E - E[0], lw=1.2, label="E(t) - E(0)")
        ax.axhline(0, color="gray", lw=0.5)
        ax.set_title(f"{tag}\nt* = {d['tstar']}", fontsize=9)
        ax.legend(fontsize=7)
        ax = axes[1, k]
        ax.plot(t, [r["KE"] for r in fin], lw=1.2, color="tab:orange")
        ax.set_ylabel("KE (indefinite T)" if k == 0 else "")
        ax = axes[2, k]
        for key, lab in (("sec_sp_diag", "spatial diag"),
                         ("sec_sp_off", "spatial off-diag"),
                         ("sec_time_mix", "time-mixing 0i"),
                         ("sec_time_diag", "time diag 00")):
            y = np.maximum([r.get(key, 0) for r in fin], 1e-16)
            ax.semilogy(t, y, lw=1, label=lab)
        ax.set_ylim(1e-13, 10)
        if k == 0:
            ax.set_ylabel("max |dM| per sector")
        ax.legend(fontsize=6)
        ax = axes[3, k]
        q = [r.get("q_r4") if r.get("q_r4") is not None else np.nan
             for r in fin]
        ax.plot(t, q, ".-", ms=2, lw=0.8, label="q (r_w = 4)")
        ax.plot(t, [r.get("ring_rho", np.nan) / 40 for r in fin], lw=0.8,
                label="ring rho / 40")
        ax.set_ylim(-0.1, 0.8)
        ax.set_xlabel("t")
        ax.legend(fontsize=7)
        if k == 0:
            ax.set_ylabel("winding + ring")
    axes[0, 0].set_ylabel("E(t) - E(0)")
    fig.suptitle("M5.20.3: the anatomy of the free-EL (true-L) blowup: "
                 "E conserved, spatial sector grows, q NEVER unwinds",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = os.path.join(PLOTS, "m5_20_3_anatomy.png")
    fig.savefig(path, dpi=120)
    print("wrote", path)


def sections(tags=("recipe_rc1e-2", "raw_rc1e-2", "remnant_rc1e-2")):
    from m5_20_2_a_eom import WSCALE, u_eta_density, v4_density
    NR, NZ, H = 64, 128, 1.0
    rows = []
    for tag in tags:
        for stage in ("seed", "end"):
            p = os.path.join(DATA, f"m5_20_3_c_{tag}_{stage}.npz")
            if os.path.exists(p):
                rows.append((tag, stage, np.load(p)["M"]))
    fig, axes = plt.subplots(len(rows), 3, figsize=(15, 3.2 * len(rows)),
                             squeeze=False)
    ext = [0.5, NR - 1.5, -(NZ / 2 - 1.5), NZ / 2 - 1.5]
    for k, (tag, stage, M) in enumerate(rows):
        m13 = M[: NR - 1, 1:-1, 1, 3]
        msp = M[: NR - 1, 1:-1, 1:4, 1:4]
        s = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
        dens = u_eta_density(M, H) + v4_density(M, WSCALE, 0.3)
        for ax, arr, ttl, cm in (
                (axes[k, 0], np.abs(m13).T, f"{tag} {stage}: |M13|",
                 "magma"),
                (axes[k, 1], s.T, "max eigenvalue s", "viridis"),
                (axes[k, 2],
                 np.log10(np.maximum(np.abs(dens), 1e-12)).T,
                 "log10 |energy density|", "inferno")):
            im = ax.imshow(arr, origin="lower", aspect="auto", extent=ext,
                           cmap=cm)
            ax.set_title(ttl, fontsize=9)
            plt.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    path = os.path.join(PLOTS, "m5_20_3_sections.png")
    fig.savefig(path, dpi=110)
    print("wrote", path)


def chirp():
    with open(os.path.join(DATA, "m5_20_3_d_d2.json")) as f:
        d = json.load(f)
    rows = d["rows"]
    rho = np.array([r["rho"] for r in rows])
    om1 = np.array([r["omega_pos"][0] if r["omega_pos"] else np.nan
                    for r in rows])
    km = np.array([r["K_absmax"] for r in rows])
    fit = d["omega1_linear_fit"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(rho, om1, "o", ms=4, label="omega_1 (gen-eig, measured)")
    axes[0].plot(rho, fit["slope"] * rho + fit["intercept"], "-", lw=1,
                 label=f"fit: {fit['slope']:.4f} rho + "
                       f"{fit['intercept']:.4f}")
    axes[0].set_xlabel("rho")
    axes[0].set_ylabel("omega_1")
    axes[0].set_title("the true-L vacuum ladder is rho-CHIRPED "
                      "(axisym sector)", fontsize=10)
    axes[0].legend(fontsize=8)
    axes[1].loglog(rho, km, "s", ms=4)
    axes[1].set_xlabel("rho")
    axes[1].set_ylabel("max |eig K10|")
    axes[1].set_title(f"K10 ~ rho^{d['K_absmax_powerlaw_in_rho']:.2f} "
                      "(equivariant background)", fontsize=10)
    fig.tight_layout()
    path = os.path.join(PLOTS, "m5_20_3_ladder_chirp.png")
    fig.savefig(path, dpi=120)
    print("wrote", path)


def card():
    with open(os.path.join(DATA, "m5_20_3_b_b2.json")) as f:
        b2 = json.load(f)
    with open(os.path.join(DATA, "m5_20_3_b_b1.json")) as f:
        b1 = json.load(f)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for stag, mk in (("raw", "o"), ("recipe", "s"),
                     ("remnant_unwound", "v")):
        lad = b2[stag]["ladder"]
        rcs = [float(k) for k in lad]
        ts = [lad[k]["tstar"] for k in lad]
        rcs_p = [r for r, t in zip(rcs, ts) if t is not None]
        ts_p = [t for t in ts if t is not None]
        axes[0].loglog(rcs_p, ts_p, mk + "-", ms=5, label=stag)
        surv = [(r, 8.0) for r, t in zip(rcs, ts) if t is None]
        if surv:
            axes[0].loglog([s[0] for s in surv], [s[1] for s in surv],
                           mk, ms=9, mfc="none", mec="green",
                           label=f"{stag}: no blowup in window")
    axes[0].set_xlabel("rel_cut (null-projection cutoff)")
    axes[0].set_ylabel("t* (blowup time)")
    axes[0].set_title("t* monotone in the cutoff, NO plateau:\n"
                      "no cutoff-independent free-EL evolution", fontsize=9)
    axes[0].legend(fontsize=7)
    for rc, det in b1["detail"].items():
        dts = [float(k) for k in det["tstar_per_dt"]]
        ts = list(det["tstar_per_dt"].values())
        axes[1].semilogx(dts, ts, "o-", ms=5, label=f"loop, rel_cut {rc}")
    axes[1].set_xlabel("dt")
    axes[1].set_ylabel("t*")
    axes[1].set_title("t* dt-ROBUST at fixed cutoff\n(genuine finite-time "
                      "blowup of the regularized ODE)", fontsize=9)
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    path = os.path.join(PLOTS, "m5_20_3_illposedness.png")
    fig.savefig(path, dpi=120)
    print("wrote", path)


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "all"
    fns = {"anatomy": anatomy, "sections": sections, "chirp": chirp,
           "card": card}
    for name, fn in fns.items():
        if which in (name, "all"):
            fn()
