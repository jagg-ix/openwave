"""M5.20.3 phase D: the observables that SURVIVE the NO-GO, honestly
re-scoped (deviation logged in the task_details):

    D1  G-CORE at the statics level: his (g, 1, a, a), a ~ delta/2 core
        prediction read on the frozen-time-row minimization path while
        the loop is intact (64x128 from B3; 128x256 grid spot-check here)
    D2  the true-L vacuum ladder omega(rho): generalized eig(Hess_V,
        K10(rho)) across rho: K10 ~ 1/rho^2 (equivariant background)
        predicts omega ~ rho (a rho-CHIRPED spectrum: NEW true-L
        prediction, replaces the flat canonical ladder comparison)
    D3  the ill-posedness card: t*(dt) / t*(rel_cut) / t*(amplitude) /
        channel / seed-dependence assembled from the phase-B + phase-C
        data into one JSON (the note's central table)
    D4  the pre-registered radius-breathing + spectrum gates: NOT REACHED
        (recorded as such: no stable evolution exists to measure them on)

The amplitude ladder is re-run here so its numbers live in repo data
(first measured in a scratch probe): clock texture t* is
amplitude-INDEPENDENT over 0.0002..0.02 at rel_cut 1e-8 (fixed step
count: the unbounded-RHS signature) and the 2e-5 run survives (the
linearized vacuum is marginal: omega^2 = 0 flats).

Run:  python m5_20_3_d_observables.py d1|d2|d3
Out:  ../data/m5_20_3_d_<gate>.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import pin_mask                                  # noqa: E402
from m5_16_axisym import fire_relax                                # noqa: E402
from m5_17_energy import cell_weights                              # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_20_1_b_seeds import core_spectrum, winding_measure_biax    # noqa: E402
from m5_20_2_a_eom import (G_T, WSCALE, grad_static_4,             # noqa: E402
                           hessian4_analytic, total_energy_4, vac4)
from m5_20_3_a_constraint import (build_k10, evolve_true,          # noqa: E402
                                  seed4_grid)
from m5_20_3_b_triage import (DELTA, H, R0, inject, tstar_of,      # noqa: E402
                              vac_field)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


# ---------------- D1: the core gate on the big grid ----------------
def relax_frozen(nr, nz, iters=500):
    w4 = cell_weights(nr, nz, H)[..., None, None]
    rho4 = ((np.arange(nr - 1) + 0.5) * H)[:, None, None, None]
    pin = pin_mask(nr, nz)
    free4 = (~pin)[..., None, None].astype(float)
    wfull = np.ones((nr, nz))
    wfull[: nr - 1, 1:-1] = w4[..., 0, 0]
    precond = (1.0 / wfull)[..., None, None]

    def g_frozen(MM):
        G = grad_static_4(MM, WSCALE, DELTA, w4=w4, rho4=rho4)
        G[..., 0, :] = 0.0
        G[..., :, 0] = 0.0
        return G

    egf = lambda MM: (total_energy_4(MM, WSCALE, DELTA), g_frozen(MM))  # noqa: E731
    M = seed4_grid(nr, nz, DELTA, "pair_d0", R0=R0)
    Mx, h = fire_relax(M.copy(), egf, free4, precond, max_iter=iters,
                       tol_rel=1e-9, dt0=0.005, dt_max=0.05,
                       log_every=iters)
    return M, Mx, h


def d1():
    out = {"prediction": "(g, 1, a, a) with a ~ delta/2 = 0.15 "
                         "(Duda 2026-07-12 evening)"}
    for (nr, nz) in ((64, 128), (128, 256)):
        M0, Mx, h = relax_frozen(nr, nz, iters=500)
        rd = ring_by_m13(Mx, nr, nz, H)
        qm, mix = winding_measure_biax(Mx, nr, nz, H, rd["ring13_rho"],
                                       rd["ring13_z"])
        cs = core_spectrum(Mx, nr, nz, H, rd["ring13_rho"], rd["ring13_z"])
        lam = cs["lam"]
        a_mean = 0.5 * (lam[1] + lam[2])
        out[f"{nr}x{nz}"] = {
            "E_after_500": h["E"][-1], "q": None
            if not np.isfinite(qm) else float(qm),
            "core_lam_spatial": lam, "time_row": -G_T,
            "spectrum_4d": [G_T, *[round(x, 4) for x in lam]],
            "a_mean": a_mean, "a_over_deltahalf": a_mean / (DELTA / 2.0),
            "pair_split": abs(lam[1] - lam[2])}
        print(f"  [{nr}x{nz}] q={out[f'{nr}x{nz}']['q']} core "
              f"(1, a, a) read: {np.round(lam, 4).tolist()} "
              f"a_mean {a_mean:.4f} = {a_mean / (DELTA / 2):.2f} x delta/2",
              flush=True)
    a64 = out["64x128"]["a_mean"]
    a128 = out["128x256"]["a_mean"]
    out["grid_shift_rel"] = abs(a128 - a64) / max(a128, 1e-30)
    out["gate"] = {"a_within_30pct_of_deltahalf":
                   bool(abs(a128 / (DELTA / 2) - 1.0) < 0.30),
                   "loop_intact_at_read": bool(out["128x256"]["q"]
                                               is not None)}
    print(f"[D1] a(128x256) = {a128:.4f} vs delta/2 = {DELTA / 2:.3f} "
          f"({a128 / (DELTA / 2):.2f}x); grid shift "
          f"{out['grid_shift_rel']:.1%}", flush=True)
    return out


# ---------------- D2: the rho-chirped vacuum ladder ----------------
def d2(nr=64, nz=128):
    M = vac_field()
    K10 = build_k10(M)
    Hv = hessian4_analytic(DELTA)
    from scipy.linalg import eig
    rows = []
    cj = (nz - 2) // 2
    for ci in range(2, nr - 2, 3):
        rho = (ci + 0.5) * H
        Kc = K10[ci, cj]
        lam, U = np.linalg.eigh(Kc)
        keep = np.abs(lam) > 1e-10 * np.abs(lam).max()
        Ur = U[:, keep]
        w2 = np.real(eig(Ur.T @ Hv @ Ur, np.diag(lam[keep]))[0])
        pos = sorted(float(np.sqrt(x)) for x in w2 if x > 1e-12)
        rows.append({"rho": rho, "K_absmax": float(np.abs(lam).max()),
                     "omega_pos": pos,
                     "n_zero": int(np.sum(np.abs(w2) <= 1e-12)),
                     "n_neg_omega2": int(np.sum(w2 < -1e-12))})
    rhos = np.array([r["rho"] for r in rows])
    om1 = np.array([r["omega_pos"][0] if r["omega_pos"] else np.nan
                    for r in rows])
    good = np.isfinite(om1)
    slope, icpt = np.polyfit(rhos[good], om1[good], 1)
    kmax = np.array([r["K_absmax"] for r in rows])
    p_k = np.polyfit(np.log(rhos), np.log(kmax), 1)[0]
    out = {"rows": rows, "omega1_linear_fit": {
               "slope": float(slope), "intercept": float(icpt)},
           "K_absmax_powerlaw_in_rho": float(p_k),
           "n_neg_omega2_anywhere": int(sum(r["n_neg_omega2"]
                                            for r in rows)),
           "reading": "K10 ~ rho^p (p ~ -2) => omega1 ~ rho: the true-L "
                      "vacuum spectrum is rho-chirped, not a flat ladder"}
    print(f"[D2] omega1(rho) = {slope:.4f} rho + {icpt:.4f}; "
          f"K_absmax ~ rho^{p_k:.2f}; negative omega^2 anywhere: "
          f"{out['n_neg_omega2_anywhere']}", flush=True)
    return out


# ---------------- D3: the ill-posedness card ----------------
def amp_ladder():
    rows = {}
    for amp in (0.02, 0.002, 0.0002, 0.00002):
        M0 = inject(vac_field(), "clock", amp=amp)
        _, _, recs, _ = evolve_true(M0, None, 2.0, 0.0025, WSCALE, DELTA,
                                    snap_every=200)
        rows[str(amp)] = tstar_of(recs)
        print(f"  amp={amp}: t*={rows[str(amp)]}", flush=True)
    return rows


def d3():
    card = {"reading": (
        "unregularized (rel_cut -> 0): blowup in a fixed STEP COUNT at any "
        "dt (unbounded RHS: the IVP is ill-posed); regularized (any fixed "
        "cutoff): finite-time blowup, t* dt-robust, t* monotone in cutoff "
        "with NO plateau; channel = SPATIAL sector; seeds: raw loop, "
        "recipe loop, unwound remnant, vacuum+textures ALL blow")}
    for name in ("b1", "b2", "b3", "b4"):
        p = os.path.join(DATA, f"m5_20_3_b_{name}.json")
        if os.path.exists(p):
            with open(p) as f:
                d = json.load(f)
            d.pop("relax_hist", None)
            card[name] = d
    p = os.path.join(DATA, "m5_20_3_b_b5corr.json")
    if os.path.exists(p):
        with open(p) as f:
            card["b5_regularized"] = json.load(f)
    print("  amplitude ladder (clock texture, rel_cut 1e-8):", flush=True)
    card["amplitude_ladder_clock_rc1e-8"] = amp_ladder()
    for tag in ("recipe_rc1e-2", "recipe_rc1e-1", "raw_rc1e-2",
                "remnant_rc1e-2"):
        p = os.path.join(DATA, f"m5_20_3_c_{tag}.json")
        if os.path.exists(p):
            with open(p) as f:
                d = json.load(f)
            fin = [r for r in d["trajectory"]
                   if np.isfinite(r.get("E_tot", float("nan")))]
            card[f"anatomy_{tag}"] = {
                "tstar": d["tstar"],
                "E_first_last": [fin[0]["E_tot"], fin[-1]["E_tot"]],
                "leak_final": fin[-1].get("leak_rate"),
                "q_r4_first_last": [fin[0].get("q_r4"),
                                    fin[-1].get("q_r4")],
                "sectors_last": {k: fin[-1].get(k) for k in
                                 ("sec_time_diag", "sec_time_mix",
                                  "sec_sp_diag", "sec_sp_off")}}
    card["not_reached"] = {
        "G-RADIUS (R(t) breathing at conserved E)": "NOT REACHED: no "
        "stable evolution exists under the free EL to measure it on",
        "G-SPECTRUM (lines vs the gap ladder)": "NOT REACHED: same; the "
        "D2 rho-chirped ladder is the surviving spectral statement",
        "unwind DURATION (his shrink-to-R=0 branch)": "the loop does not "
        "shrink-and-unwind under free EL: it blows up at t*(cutoff); the "
        "duration observable is regularization-dependent, i.e. NOT "
        "defined by the theory without his least-action BVP formulation"}
    print("[D3] card assembled", flush=True)
    return card


def main(which):
    os.makedirs(DATA, exist_ok=True)
    fn = {"d1": d1, "d2": d2, "d3": d3}[which]
    out = fn()
    with open(os.path.join(DATA, f"m5_20_3_d_{which}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"wrote data/m5_20_3_d_{which}.json", flush=True)
    return out


if __name__ == "__main__":
    main(ARGV[0] if ARGV else "d1")
