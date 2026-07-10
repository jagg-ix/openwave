"""M5.19 phase B2: the regularized cross-section under the AUTHOR'S potential.

Deviation logged at EXECUTE (2026-07-10): phases A+B ran on the LdG quartic
(m5_17_energy defaults), but the M5.12 loop relaxations, and the author's own
prescription since M5.18, use the universal SPECTRAL potential
    V(M_sp) = wscale . SUM_{p=1..3} ( Tr(M_sp^p) - c_p )^2 ,
    c_p = 1 + delta^p   (target spectrum Lambda = (1, delta, 0)),
with wscale the M5.12-calibrated scale (m5_18_spectral_spec_n96.json). The
phase-A GATE conclusions are curvature-only (potential-independent) and
stand; the phase-B OPTIMA are potential-dependent and are recomputed here so
phase C consumes author-comparable numbers.

What the spectral potential changes structurally:
  - ANY spectrum {1, delta, 0} is an exact vacuum (V = 0), so delta is a
    VACUUM variable (the author's usage), not a core variable: the LdG
    "area divergence at delta != 0" row does not apply here.
  - With delta != 0 there are THREE inequivalent winding-pair classes: which
    two of (1, delta, 0) span the vortex cross-section plane:
        pair_1d: winding (1, delta), out-of-plane 0
        pair_10: winding (1, 0),     out-of-plane delta
        pair_d0: winding (delta, 0), out-of-plane 1
    (at delta = 0, pair_1d == pair_10 and pair_d0 is split-free/trivial).
  - The center regularization (two equal in-plane eigenvalues, R1) and the
    closed-form curvature u = 8 c2 d^2 s^2 (lam_p' - lam_m')^2 / rho^2 are
    unchanged (curvature never sees the potential).

Derrick balance and the exact degree identity E* proportional to d survive
verbatim (Ec ~ d^2 at fixed profile; Ev potential-agnostic in structure), so
the measured payload here is: E*, optimal center (mu0, nu0), widths, per
(delta, winding pair, degree); the melt-vs-general-center comparison under
the author's potential; sensitivity to delta in {0, 0.3} (the sector value
of delta for the neutrino is NOT fixed by the reply: flagged as an open
parameter, ask-when-gated candidate only if it becomes load-bearing).

GATES
    GS0  this file's spectral v == m5_18_spectral.potential_density_spec_np
         on a z-uniform 2D grid (<= 1e-12 rel)
    GS1  V(far field) = 0 exactly (each delta, pair)          (<= 1e-14)
    GS2  Derrick stationarity at every reported optimum (<= 1% E)

Outputs: ../data/m5_19_b2_spectral.json, ../plots/m5_19_b2_spectral.png
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

import m5_19_ab_vortex as ab                      # noqa: E402
import m5_18_spectral as m18                      # noqa: E402
from m5_12_core_pin import load_wscale            # noqa: E402

PI = np.pi
WSCALE = load_wscale()
NSC = 8192
RMAXS = 96.0
WMAX = 24.0
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def cps_of(delta):
    return (1.0 + delta, 1.0 + delta ** 2, 1.0 + delta ** 3)


def pot_spec(delta):
    cps = cps_of(delta)

    def v(msp):
        m2 = np.einsum("...ab,...bc->...ac", msp, msp)
        t1 = np.einsum("...aa->...", msp)
        t2 = np.einsum("...aa->...", m2)
        t3 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, msp))
        return WSCALE * ((t1 - cps[0]) ** 2 + (t2 - cps[1]) ** 2
                         + (t3 - cps[2]) ** 2)
    return v


def pairs_of(delta):
    out = {"pair_10": (1.0, 0.0, delta)}
    if delta != 0.0:
        out["pair_1d"] = (1.0, delta, 0.0)
        out["pair_d0"] = (delta, 0.0, 1.0)
    return out


def gate_gs0(delta=0.3, n=256):
    """spectral v here == m5_18_spectral on a z-uniform grid."""
    h = ab.RMAX / n
    nz = 6
    rho_all = (np.arange(n) + 0.5) * h
    lam_p, lam_m, lam3 = ab.family_profiles(rho_all, 0.4, 0.1, 1.0, 1.0, 1.0,
                                            "tanh", far=(1.0, delta, 0.0))
    M1 = ab.diag_field(lam_p, lam_m, lam3)
    M2 = np.repeat(M1[:, None], nz, axis=1)
    v2 = m18.potential_density_spec_np(M2, WSCALE, cps=cps_of(delta))
    v1 = pot_spec(delta)(M1[: n - 1, 1:4, 1:4])
    rel = float(np.max(np.abs(v1 - v2[:, 0])) / max(np.max(np.abs(v2)), 1e-30))
    return {"rel_err": rel, "pass": bool(rel <= 1e-12)}


def main():
    out = {"wscale": WSCALE, "grids": {"rmax": RMAXS, "n": NSC, "wmax": WMAX},
           "GS0": gate_gs0()}
    print(f"wscale = {WSCALE}")
    print(f"GS0 (spec potential == m5_18): rel {out['GS0']['rel_err']:.2e} "
          f"pass={out['GS0']['pass']}")

    results = {}
    for delta in (0.0, 0.3):
        vfn = pot_spec(delta)
        for pname, far in pairs_of(delta).items():
            # GS1: far field is an exact vacuum
            far_msp = np.diag(far)[None]
            v_far = float(vfn(far_msp)[0])
            key = f"delta{delta}_{pname}"
            rec = {"far": far, "V_far": v_far, "GS1_pass": bool(abs(v_far) <= 1e-14)}
            scan = []
            for d in (1.0, 0.5):
                # named-center scan (analytic Derrick rescale), then NM polish
                best = None
                for shape in ab.SHAPES:
                    for cname, (mu0, nu0) in ab.CENTERS.items():
                        fn = lambda r: ab.family_profiles(
                            r, mu0, nu0, 1.0, 1.0, 1.0, shape, far=far)
                        ec, ev, _ = ab.energy_totals(fn, NSC, d, rmax=RMAXS, pot_fn=vfn)
                        if ec <= 0 or ev <= 0:
                            continue
                        est = 2.0 * (ec * ev) ** 0.5
                        scan.append({"d": d, "shape": shape, "center": cname,
                                     "e_star_analytic": est})
                        if best is None or est < best[0]:
                            best = (est, shape, cname, (ec / ev) ** 0.25)
                est0, shape, cname, lam = best
                mu0, nu0 = ab.CENTERS[cname]
                x0 = np.array([mu0, nu0, np.log(lam), np.log(lam), np.log(lam)])

                def obj(x, sh=shape, dd=d, ff=far, vv=vfn):
                    mu, nu, lws, lwm, lw3 = x
                    ws, wm, w3 = np.exp(np.clip([lws, lwm, lw3],
                                                np.log(0.2), np.log(WMAX)))
                    fn = lambda r: ab.family_profiles(r, mu, nu, ws, wm, w3,
                                                      sh, far=ff)
                    ec, ev, _ = ab.energy_totals(fn, NSC, dd, rmax=RMAXS, pot_fn=vv)
                    return ec + ev

                res = minimize(obj, x0, method="Nelder-Mead",
                               options={"maxiter": 800, "xatol": 1e-5,
                                        "fatol": 1e-10})
                mu, nu, lws, lwm, lw3 = res.x
                ws, wm, w3 = np.exp(np.clip([lws, lwm, lw3],
                                            np.log(0.2), np.log(WMAX)))
                fn_o = lambda r, mu=mu, nu=nu, ws=ws, wm=wm, w3=w3, sh=shape: \
                    ab.family_profiles(r, mu, nu, ws, wm, w3, sh, far=far)
                ec, ev, _ = ab.energy_totals(fn_o, NSC, d, rmax=RMAXS, pot_fn=vfn)
                des = []
                for lamt in (0.95, 1.05):
                    fnt = lambda r, t=lamt: ab.family_profiles(
                        r, mu, nu, ws * t, wm * t, w3 * t, shape, far=far)
                    e2c, e2v, _ = ab.energy_totals(fnt, NSC, d, rmax=RMAXS, pot_fn=vfn)
                    des.append(e2c + e2v)
                dE = (des[1] - des[0]) / np.log(1.05 / 0.95)
                gs2 = bool(abs(dE) <= 0.01 * (ec + ev))
                at_bound = bool(max(ws, wm, w3) > 0.99 * WMAX
                                or min(ws, wm, w3) < 0.202)
                rec[f"opt_d{d}"] = {
                    "shape": shape, "seed_center": cname, "width_at_bound": at_bound,
                    "mu0": float(mu), "nu0": float(nu),
                    "ws": float(ws), "wm": float(wm), "w3": float(w3),
                    "ec": ec, "ev": ev, "e_star": ec + ev,
                    "GS2_dE_dln_lambda": float(dE), "GS2_pass": gs2}
                print(f"  {key} d={d}: E* = {ec + ev:.5f} "
                      f"(mu0 {mu:.3f}, nu0 {nu:.3f}, {shape}, seed {cname}) "
                      f"GS2 {'PASS' if gs2 else 'FAIL'}")
            rec["degree_ratio"] = (rec["opt_d0.5"]["e_star"]
                                   / rec["opt_d1.0"]["e_star"])
            rec["scan"] = scan
            # the melt-vs-general comparison at d = 1 (tanh)
            melt = [s for s in scan if s["d"] == 1.0 and s["shape"] == "tanh"
                    and s["center"] == "full_melt"]
            rec["full_melt_e_star_analytic_d1"] = (melt[0]["e_star_analytic"]
                                                   if melt else None)
            results[key] = rec
    out["results"] = results

    # plot: E* per (delta, pair, degree) + optimal profiles for the flagship
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    keys = list(results)
    xs = np.arange(len(keys))
    e1 = [results[k]["opt_d1.0"]["e_star"] for k in keys]
    e5 = [results[k]["opt_d0.5"]["e_star"] for k in keys]
    axes[0].bar(xs - 0.18, e1, 0.36, label="d = 1")
    axes[0].bar(xs + 0.18, e5, 0.36, label="d = 1/2")
    fm = [results[k]["full_melt_e_star_analytic_d1"] for k in keys]
    axes[0].plot(xs, fm, "kv", label="full-melt center (d=1, unpolished)")
    axes[0].set_xticks(xs)
    axes[0].set_xticklabels(keys, rotation=20, fontsize=7)
    axes[0].set_ylabel("E*/L (spectral potential, wscale calibrated)")
    axes[0].set_title("optima per (delta, winding pair, degree)")
    axes[0].legend(fontsize=8)
    rr = np.linspace(1e-3, 8, 600)
    o = results["delta0.0_pair_10"]["opt_d1.0"]
    lp, lm, l3 = ab.family_profiles(rr, o["mu0"], o["nu0"], o["ws"], o["wm"],
                                    o["w3"], o["shape"])
    axes[1].plot(rr, lp, label="lam+")
    axes[1].plot(rr, lm, label="lam-")
    axes[1].plot(rr, l3, label="lam3")
    axes[1].set_title(f"delta=0 pair_10 d=1 optimum (E* = {o['e_star']:.4f})")
    axes[1].set_xlabel("rho")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m5_19_b2_spectral.png"), dpi=150)

    with open(os.path.join(DATA, "m5_19_b2_spectral.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("wrote data/m5_19_b2_spectral.json + plots/m5_19_b2_spectral.png")


if __name__ == "__main__":
    main()
