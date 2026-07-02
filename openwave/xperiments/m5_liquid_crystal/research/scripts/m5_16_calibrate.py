"""M5.16 P-C/P-E/P-F: the parameter-lock calibration driver.

CONVENTION (Duda index-0): M is 4x4, D = diag(g, 1, delta, 0), eta =
diag(-1, 1, 1, 1); the static electron sector is exactly g-decoupled
(m5_16_axisym.py gate G8).

THE ANCHOR CHAIN (design record: findings/m5_16_checkpoints.md):

  1. COULOMB anchor fixes c2 analytically. The relaxed hedgehog's far field is
     the pure director hedgehog, whose curvature density is exactly 8 c2 / r^4
     (m5_16_axisym.py gate G3). Matching the exterior energy to the classical
     EM self-energy outside r (E_out = alpha hbar c / (2 r), Faber Eq. 24's
     Coulomb tail) gives
         32 pi c2 / r = alpha hbar c / (2 r)   =>   c2 = alpha hbar c / (64 pi).
  2. LdG vacuum structure (P-C). Zero forcing at the uniaxial vacuum s = 1
     (spectrum (1, delta->0, 0)) pins a = (3b - 4c)/2 with melt cost c - b/2 > 0.
     One shape ratio beta = b/c in (0, 2) remains: the sweep parameter.
  3. MASS anchor (electron). Per beta, one relaxed run gives the chi-invariant
     J_half(beta) = E_sim . r_half_sim (Derrick scaling removes the potential
     scale choice). Setting E_phys = m_e c^2 fixes the grid unit
         l(beta) = c2 E_sim / m_e   [fm per grid unit]
     and PREDICTS the electron's energy-median radius
         r_half_phys(beta) = c2 J_half(beta) / m_e.
  4. FABER cross-model reference: the same energy-median radius of the
     arctan(u) profile (I[a] integrand), r_half_Faber = u_half . 2.2132 fm.
     The beta where the two meet = the Faber-consistent shape ratio beta*.
  5. Lock output (P-F handoff): (a, b, c) in MeV/fm^3 via the energy-density
     unit c2/l^4, the delta-axis stiffness kappa_delta = (3/2) b (the cubic
     alone restores the delta eigenvalue: the M5.12 phase-E anchor equation),
     the honest O(delta) vacuum residual force 3 b delta, and the g/delta
     constraint chain (g decoupled from statics; clock/boost anchors, m5_4c).

Run:  python m5_16_calibrate.py [sweep|lock|all]  (default all)
  sweep: parallel beta sweep at NR=96, NZ=192 + convergence runs at the
         selected beta (64x128, 128x256)
  lock:  read the sweep JSONs, apply the anchor chain, emit
         ../data/m5_16_parameter_lock.json + ../plots/m5_16_calibration.png
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
os.makedirs(DATA, exist_ok=True)
os.makedirs(PLOTS, exist_ok=True)

# ---- physical constants (CODATA 2018, as Faber cites) ----
HBAR_C = 197.3269804              # MeV fm
ALPHA_F = 1.0 / 137.035999084
ALPHA_F_HBAR_C = ALPHA_F * HBAR_C  # 1.43996 MeV fm
M_E_C2 = 0.51099895               # MeV
R0_FABER = 2.21320516             # fm
C2_PHYS = ALPHA_F_HBAR_C / (64.0 * np.pi)   # MeV fm, the Coulomb lock

BETAS = [0.25, 0.5, 1.0, 1.5]
NR_MAIN, NZ_MAIN = 96, 192
CONV_GRIDS = [(64, 128), (128, 256)]
ITERS = 8000


def run_relax(beta, nr, nz, tag, rc=8.0, iters=ITERS):
    cmd = [sys.executable, os.path.join(HERE, "m5_16_axisym.py"), "radial",
           str(nr), str(nz), "--beta", str(beta), "--cscale", "2e-3",
           "--rc", str(rc), "--iters", str(iters), "--autochi", "1",
           "--tag", tag]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)


def collect(tag):
    path = os.path.join(DATA, f"m5_16_axisym_{tag}.json")
    with open(path) as f:
        return json.load(f)


def faber_r_half():
    """energy-median radius of Faber's analytic arctan(u) electron profile:
    integrand f(u) = 2u^2/(1+u^2)^3 + u^2/(2(1+u^2)^2), integral = pi/4."""
    u = np.linspace(0.0, 4000.0, 4_000_001)
    f = 2.0 * u ** 2 / (1 + u ** 2) ** 3 + u ** 2 / (2.0 * (1 + u ** 2) ** 2)
    cum = np.cumsum(f) * (u[1] - u[0])
    I_tot = cum[-1] + 1.0 / (2.0 * u[-1])          # analytic tail beyond u_max
    u_half = float(np.interp(0.5 * I_tot, cum, u))
    return u_half, float(I_tot)


def do_sweep():
    t0 = time.time()
    procs = {}
    for b in BETAS:
        tag = f"b{int(round(b * 100)):03d}_n{NR_MAIN}"
        procs[tag] = run_relax(b, NR_MAIN, NZ_MAIN, tag)
        print(f"launched beta={b} -> {tag}")
    for tag, p in procs.items():
        out, _ = p.communicate()
        print(f"--- {tag} ---")
        print(out.strip().splitlines()[-2] if out.strip() else "(no output)")
    print(f"sweep wall: {round(time.time() - t0, 1)}s")


def do_convergence(beta_star):
    procs = {}
    for (nr, nz) in CONV_GRIDS:
        tag = f"b{int(round(beta_star * 100)):03d}_n{nr}"
        rc = 8.0 * nr / NR_MAIN            # keep box/core ratio fixed
        procs[tag] = run_relax(beta_star, nr, nz, tag, rc=rc)
        print(f"launched convergence run {tag}")
    for tag, p in procs.items():
        out, _ = p.communicate()
        print(f"--- {tag} ---")
        print(out.strip().splitlines()[-2] if out.strip() else "(no output)")


def do_lock():
    u_half, I_faber = faber_r_half()
    r_half_faber_fm = u_half * R0_FABER
    rows = []
    for b in BETAS:
        tag = f"b{int(round(b * 100)):03d}_n{NR_MAIN}"
        try:
            d = collect(tag)
        except FileNotFoundError:
            print(f"missing {tag}, skip")
            continue
        E_sim = d["obs"]["E_tot"]
        r_half = d["obs"]["r_half"]
        J_half = E_sim * r_half
        ell = C2_PHYS * E_sim / M_E_C2               # fm per grid unit
        r_half_phys = C2_PHYS * J_half / M_E_C2      # fm
        csc = d["params"]["cscale_used"]
        dens_unit = C2_PHYS / ell ** 4               # MeV/fm^3 per sim unit
        rows.append({
            "beta": b, "tag": tag, "E_sim": E_sim, "r_half_sim": r_half,
            "J_half": J_half, "ell_fm": ell, "r_half_phys_fm": r_half_phys,
            "virial": d["obs"]["virial_ratio_curv_over_3pot"],
            "sphericity": d["obs"]["sphericity_max_ds"],
            "minimizer_agreement": d.get(
                "minimizer_agreement_rel",
                abs(d["E_fire"] - d["E_best"]) / (abs(d["E_best"]) + 1e-300)),
            "a_phys_MeV_fm3": d["params"]["a"] * dens_unit,
            "b_phys_MeV_fm3": d["params"]["b"] * dens_unit,
            "c_phys_MeV_fm3": d["params"]["c"] * dens_unit,
            "cscale_used": csc,
            "s_profile": d["obs"]["s_profile"],
            "r_bins": d["obs"]["r_bins"],
        })
    if not rows:
        print("no sweep data; run sweep first")
        return
    # beta*: where r_half_phys crosses the Faber reference (linear interp)
    bs = np.array([r["beta"] for r in rows])
    rh = np.array([r["r_half_phys_fm"] for r in rows])
    diff = rh - r_half_faber_fm
    beta_star = None
    for i in range(len(bs) - 1):
        if diff[i] * diff[i + 1] <= 0:
            f = diff[i] / (diff[i] - diff[i + 1])
            beta_star = float(bs[i] + f * (bs[i + 1] - bs[i]))
            break
    closest = rows[int(np.argmin(np.abs(diff)))]
    # convergence data if present
    conv = []
    for (nr, nz) in [(64, 128), (NR_MAIN, NZ_MAIN), (128, 256)]:
        tag = f"b100_n{nr}"          # convergence family runs at beta = 1.0
        try:
            d = collect(tag)
            conv.append({"NR": nr, "NZ": nz, "E_sim": d["obs"]["E_tot"],
                         "r_half": d["obs"]["r_half"],
                         "J_half": d["obs"]["E_tot"] * d["obs"]["r_half"],
                         "virial": d["obs"]["virial_ratio_curv_over_3pot"]})
        except FileNotFoundError:
            pass
    lock = {
        "task": "M5.16", "date": "2026-07-02",
        "convention": "Duda index-0: D=diag(g,1,delta,0), eta=diag(-1,1,1,1)",
        "anchors": {
            "coulomb": {"c2_MeV_fm": C2_PHYS,
                        "formula": "c2 = alpha hbar c / (64 pi)",
                        "basis": "far-field 8 c2/r^4 == classical EM self-energy"
                                 " alpha hbar c/(2 r^2 ... ) exterior integral"},
            "mass": {"m_e_c2_MeV": M_E_C2,
                     "fixes": "grid unit l = c2 E_sim / m_e per beta"},
            "faber_reference": {"r0_fm": R0_FABER, "u_half": u_half,
                                "r_half_fm": r_half_faber_fm,
                                "I_check_pi4": I_faber},
        },
        "sweep_rows": [{k: v for k, v in r.items()
                        if k not in ("s_profile", "r_bins")} for r in rows],
        "beta_star_faber_crossing": beta_star,
        "closest_row": {k: v for k, v in closest.items()
                        if k not in ("s_profile", "r_bins")},
        "convergence": conv,
        "delta_sector": {
            "kappa_delta_equation": "kappa_delta = (3/2) b_phys (the cubic term"
                                    " alone restores the delta eigenvalue)",
            "kappa_delta_MeV_fm3": 1.5 * closest["b_phys_MeV_fm3"],
            "vacuum_residual_force": "dV/dlambda_2 at delta = 3 b delta"
                                     " (the quartic LdG cannot be exactly"
                                     " stationary at biaxial (1,delta,0));"
                                     " at delta=1e-10 this is a 3e-10 b"
                                     " residual, the honest Q7 remainder",
        },
        "g_sector": {
            "statics": "exactly decoupled (gate G8): the electron mass anchor"
                       " carries no g information",
            "anchors": "g from the clock/boost sector only: GEM ~ (b_boost g)^2"
                       " (m5_4c Phase E), electron-clock absolute omega (#220),"
                       " or baryon gravitational mass (Duda 4e). Duda hierarchy"
                       " g ~ 1/delta ~ 1e10 with g*delta = 1 stands as the"
                       " working value, label: hypothesis",
        },
    }
    path = os.path.join(DATA, "m5_16_parameter_lock.json")
    with open(path, "w") as f:
        json.dump(lock, f, indent=2)
    # ---- report ----
    print("=" * 78)
    print("M5.16 PARAMETER LOCK")
    print("=" * 78)
    print(f"c2 (Coulomb anchor)      = {C2_PHYS:.6e} MeV fm"
          f"  [= alpha hbar c / 64 pi]")
    print(f"Faber r_half reference   = {r_half_faber_fm:.4f} fm"
          f"  (u_half = {u_half:.4f}, I = {I_faber:.6f} vs pi/4 = {np.pi/4:.6f})")
    for r in rows:
        print(f"beta={r['beta']:<5} E_sim={r['E_sim']:8.3f}  r_half_sim="
              f"{r['r_half_sim']:6.2f}  -> l={r['ell_fm']:.4e} fm/unit  "
              f"r_half_phys={r['r_half_phys_fm']:.4f} fm  "
              f"virial={r['virial']:.3f} spher={r['sphericity']:.4f}")
    print(f"beta* (Faber crossing)   = {beta_star}")
    print(f"closest row: beta={closest['beta']}  "
          f"(a,b,c)_phys = ({closest['a_phys_MeV_fm3']:.4e}, "
          f"{closest['b_phys_MeV_fm3']:.4e}, {closest['c_phys_MeV_fm3']:.4e})"
          f" MeV/fm^3")
    print(f"kappa_delta = {1.5 * closest['b_phys_MeV_fm3']:.4e} MeV/fm^3")
    if conv:
        print("convergence:", [(c['NR'], round(c['J_half'], 2)) for c in conv])
    print(f"json -> {path}")
    make_plot(rows, r_half_faber_fm, beta_star, conv)
    return lock


def make_plot(rows, r_half_faber_fm, beta_star, conv):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(12, 9))
    for r in rows:
        rb = np.array(r["r_bins"])
        sp = np.array(r["s_profile"])
        ax[0, 0].plot(rb, sp, lw=1.5, label=f"beta={r['beta']}")
    ax[0, 0].axhline(1.0, ls=":", c="gray")
    ax[0, 0].set_xlabel("r (grid units)")
    ax[0, 0].set_ylabel("s(r) = largest eigenvalue")
    ax[0, 0].set_title("relaxed melt profiles (core regularization, P-D)")
    ax[0, 0].legend(fontsize=8)
    ax[0, 0].set_xlim(0, 30)
    bs = [r["beta"] for r in rows]
    rh = [r["r_half_phys_fm"] for r in rows]
    ax[0, 1].plot(bs, rh, "o-", label="M5 prediction r_half(beta)")
    ax[0, 1].axhline(r_half_faber_fm, ls="--", c="r",
                     label=f"Faber arctan profile ({r_half_faber_fm:.3f} fm)")
    if beta_star:
        ax[0, 1].axvline(beta_star, ls=":", c="g", label=f"beta*={beta_star:.3f}")
    ax[0, 1].set_xlabel("beta = b/c")
    ax[0, 1].set_ylabel("r_half (fm)")
    ax[0, 1].set_title("energy-median radius: M5 vs Faber (m_e + Coulomb anchored)")
    ax[0, 1].legend(fontsize=8)
    vir = [r["virial"] for r in rows]
    ax[1, 0].plot(bs, vir, "s-")
    ax[1, 0].axhline(1.0, ls="--", c="r")
    ax[1, 0].set_xlabel("beta = b/c")
    ax[1, 0].set_ylabel("E_curv / (3 E_pot)")
    ax[1, 0].set_title("Derrick virial at the minimum (gate R4)")
    if conv:
        ns = [c["NR"] for c in conv]
        js = [c["J_half"] for c in conv]
        ax[1, 1].plot(ns, js, "o-")
        ax[1, 1].set_xlabel("NR (resolution)")
        ax[1, 1].set_ylabel("J_half = E_sim * r_half")
        ax[1, 1].set_title("h-convergence of the chi-invariant")
    fig.suptitle("M5.16 parameter-lock calibration (Coulomb + m_e anchors, "
                 "index-0, delta=0 electron sector)", fontweight="bold")
    fig.tight_layout()
    path = os.path.join(PLOTS, "m5_16_calibration.png")
    fig.savefig(path, dpi=110)
    print(f"plot -> {path}")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode in ("sweep", "all"):
        do_sweep()
    if mode == "all":
        # convergence at the closest-to-Faber beta from the fresh sweep
        u_half, _ = faber_r_half()
        rhf = u_half * R0_FABER
        best_b, best_d = None, 1e30
        for b in BETAS:
            try:
                d = collect(f"b{int(round(b * 100)):03d}_n{NR_MAIN}")
            except FileNotFoundError:
                continue
            rhp = C2_PHYS * d["obs"]["E_tot"] * d["obs"]["r_half"] / M_E_C2
            if abs(rhp - rhf) < best_d:
                best_d, best_b = abs(rhp - rhf), b
        if best_b is not None:
            do_convergence(best_b)
    if mode in ("lock", "all"):
        do_lock()
