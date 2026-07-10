"""M5.19 phases A+B: the regularized straight-vortex cross-section.

The author's construction (M5.19 spec R1-R3): a radial cross-section profile
M(r) whose two IN-PLANE spatial eigenvalues become EQUAL at the vortex center
(the core regularization, "in a general way"), rotated to a planar topological
vortex of degree d (1 for beta decay, maybe 1/2). This script measures, on the
audited M5.17 static functional (m5_17_energy.py, verbatim conventions):

  A. whether the regularized family has BOUNDED core energy under grid
     refinement while the unregularized controls diverge (the phase-A gate),
     including the Skyrme-degeneracy subtlety flagged at PLAN: the commutator
     curvature charges only non-commuting gradient PAIRS, so the constant-
     eigenvalue winding control may cost ZERO in the equivariant scheme while
     the Cartesian discretization of the same field diverges (a scheme
     ambiguity that the author's regularization removes);
  B. the exact energy-per-length readouts vs core size for degree 1 AND 1/2
     (Derrick-balanced optima per degree).

EQUIVARIANT 1D REDUCTION (straight vortex line = the z-axis; z-uniform)
    M(rho, phi) = R12(d phi) . Mt(rho) . R12(d phi)^T,
    Mt = diag(g, lam_p(rho), lam_m(rho), lam_3(rho))   (winding plane = 1,2),
    M_phi = d [J, Mt] / rho,  M_z = 0,  M_rho = central diff + mirror ghost
    (identical stencils to m5_17_energy.curvature_density_np), so
        u_curv = 4 c2 ||[M_rho, M_phi]||_F^2 ,
        E/L    = SUM_i 2 pi rho_i h (u_i + v_i),   v = V(M_sp) - V_vac.
    Closed form for diagonal profiles (gate GA1):
        [J, Mt] = s (E12 + E21),  s = lam_p - lam_m,
        u_curv = 8 c2 d^2 s^2 (lam_p' - lam_m')^2 / rho^2 .
    Unregularized control C1 (s(0) = s0 != 0, kink m'(0) = k != 0):
        E_core/L ~ 16 pi c2 d^2 s0^2 k^2 ln(1/h)   (log-divergent).
    Regularized family (s(0) = 0 structural): bounded, convergent.

THE FAMILY ("in a general way", R1 structural)
    s(rho)    = f(rho / w_s),  f in {tanh x, tanh^2 x, 1 - exp(-x^2)}
                (vanishing order 1 or 2 at the core; s -> 1 = vacuum split),
    m(rho)    = 1/2 + (mu0 - 1/2) exp(-(rho/w_m)^2)   (in-plane mean),
    lam_3(rho)= nu0 exp(-(rho/w_3)^2)                 (out-of-plane),
    lam_pm    = m +/- s/2;  center spectrum (mu0, mu0, nu0): two equal ALWAYS.
    Named centers: planar-isotropic (1/2, 0), trace melt (1/3, 1/3),
    full melt (0, 0), escape-to-axis (0, 1), (1/2, 1/2).

DERRICK BALANCE (2D cross-section, per unit length)
    rho -> lambda rho:  E_c -> E_c / lambda^2,  E_v -> E_v lambda^2
    =>  lambda* = (E_c/E_v)^(1/4),  E* = 2 sqrt(E_c E_v)   (gate GA2).

GATES (pre-registered at go, 2026-07-10)
    GA0  d=1 equivariant 1D == m5_17_energy 2D on a z-uniform field (<=1e-12)
    GA1  numeric curvature == closed form for diagonal profiles (<=1e-10)
    GA0b Cartesian full-grid energy -> equivariant energy under refinement
         for the regularized profile at d=1 and d=1/2 (ratio -> 1); the same
         Cartesian scheme DIVERGES on the unregularized constant control
    GA2  Derrick stationarity at the reported optima (|dE/dln lambda| <= 1% E)
    A    regularized: E(h) convergent + bounded core integrand;
         C1 control: fitted log slope matches the closed form
    B    finite E* for BOTH degrees + the measured degree comparison

Units: sim units c2 = 1, cscale = 1, beta = 1 (a = -1/2, b = c = 1,
V_vac = -1/2, melt cost 1/2 > 0). Physical anchoring enters only at
comparison time under the standing fixed-(size, a^2) metric (M5.12 b17).

Outputs: ../data/m5_19_ab_vortex.json, ../plots/m5_19_ab_{profiles,refinement}.png
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
import m5_17_energy as m17  # noqa: E402

PI = np.pi
G = m17.G_TIME
BETA, CSCALE, C2 = 1.0, 1.0, 1.0
A_, B_, C_, VVAC = m17.ldg_coeffs(BETA, CSCALE)
RMAX = 12.0
RWIN = 6.0          # common comparison window (densities ~vacuum outside)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")

SHAPES = {
    "tanh": lambda x: np.tanh(x),          # s ~ x   (order 1)
    "tanh2": lambda x: np.tanh(x) ** 2,    # s ~ x^2 (order 2)
    "gauss": lambda x: 1.0 - np.exp(-x * x),  # s ~ x^2 (order 2)
}
CENTERS = {
    "planar_iso": (0.5, 0.0),
    "trace_melt": (1.0 / 3.0, 1.0 / 3.0),
    "full_melt": (0.0, 0.0),
    "escape_axis": (0.0, 1.0),
    "half_half": (0.5, 0.5),
}


# ---------------- profiles ----------------
def family_profiles(rho, mu0, nu0, ws, wm, w3, shape, far=(1.0, 0.0, 0.0)):
    """regularized family; far = (lam_p, lam_m, lam_3) at rho -> inf
    (default = the LdG uniaxial vacuum (1, 0, 0)); center spectrum is
    ALWAYS (mu0, mu0, nu0): two equal by construction (R1)."""
    lp_f, lm_f, l3_f = far
    s = (lp_f - lm_f) * SHAPES[shape](rho / ws)
    mfar = 0.5 * (lp_f + lm_f)
    m = mfar + (mu0 - mfar) * np.exp(-((rho / wm) ** 2))
    lam3 = l3_f + (nu0 - l3_f) * np.exp(-((rho / w3) ** 2))
    return m + 0.5 * s, m - 0.5 * s, lam3


def c1_profiles(rho, mu0p=0.5, w=1.0):
    """unregularized control C1: split never closes (s(0) = mu0p != 0) +
    a core kink (lam_p' (0) = (1 - mu0p)/w != 0)."""
    lam_p = mu0p + (1.0 - mu0p) * (1.0 - np.exp(-rho / w))
    return lam_p, np.zeros_like(rho), np.zeros_like(rho)


def c0_profiles(rho, delta=0.0):
    """unregularized control C0: constant eigenvalues (1, delta, 0)."""
    return np.ones_like(rho), delta * np.ones_like(rho), np.zeros_like(rho)


# ---------------- equivariant 1D energy ----------------
def diag_field(lam_p, lam_m, lam3):
    M = np.zeros(lam_p.shape + (4, 4))
    M[..., 0, 0] = G
    M[..., 1, 1] = lam_p
    M[..., 2, 2] = lam_m
    M[..., 3, 3] = lam3
    return M


def potential_v(Msp):
    m2 = np.einsum("...ab,...bc->...ac", Msp, Msp)
    tr2 = np.einsum("...aa->...", m2)
    tr3 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, Msp))
    return A_ * tr2 - B_ * tr3 + C_ * tr2 * tr2 - VVAC


def energy_1d(lam_p, lam_m, lam3, h, d, pot_fn=None):
    """per-cell (rho_i, u_curv, v, w) on included cells i = 0..nr-2,
    stencils IDENTICAL to m5_17_energy.curvature_density_np.
    pot_fn(Msp) -> v density; default = the LdG quartic potential_v."""
    nr = lam_p.shape[0]
    M = diag_field(lam_p, lam_m, lam3)
    Mminus = np.empty_like(M[: nr - 1])
    Mminus[1:] = M[: nr - 2]
    Mminus[0] = m17.MIR * M[0]
    Mrho = (M[1:] - Mminus) / (2.0 * h)
    Mc = M[: nr - 1]
    rho = ((np.arange(nr - 1) + 0.5) * h)
    Mphi = d * m17._comm_np(np.broadcast_to(m17.J4, Mc.shape), Mc) / rho[:, None, None]
    u = C2 * 4.0 * m17._norm2_np(m17._comm_np(Mrho, Mphi))
    v = (pot_fn or potential_v)(Mc[..., 1:4, 1:4])
    w = 2.0 * PI * rho * h
    return rho, u, v, w


def energy_totals(profile_fn, n, d, rmax=RMAX, rwin=None, pot_fn=None):
    h = rmax / n
    rho_all = (np.arange(n) + 0.5) * h
    lam_p, lam_m, lam3 = profile_fn(rho_all)
    rho, u, v, w = energy_1d(lam_p, lam_m, lam3, h, d, pot_fn=pot_fn)
    sel = slice(None) if rwin is None else rho <= rwin
    ec = float(np.sum((u * w)[sel]))
    ev = float(np.sum((v * w)[sel]))
    return ec, ev, (rho, u, v, w)


# ---------------- gates ----------------
def gate_ga0(n=256):
    """d=1 1D energy == m5_17_energy on a z-uniform 2D grid, exact."""
    h = RMAX / n
    nz = 6
    rho_all = (np.arange(n) + 0.5) * h
    lam_p, lam_m, lam3 = family_profiles(rho_all, 0.5, 0.0, 1.0, 1.0, 1.0, "tanh")
    M1 = diag_field(lam_p, lam_m, lam3)
    M2 = np.repeat(M1[:, None], nz, axis=1)
    u2 = m17.curvature_density_np(M2, h, C2)
    v2 = m17.potential_density_np(M2, A_, B_, C_, VVAC)
    w2 = m17.cell_weights(n, nz, h)
    e2 = float(np.sum((u2 + v2) * w2)) / ((nz - 2) * h)
    ec, ev, _ = energy_totals(
        lambda r: family_profiles(r, 0.5, 0.0, 1.0, 1.0, 1.0, "tanh"), n, 1.0)
    e1 = ec + ev
    rel = abs(e1 - e2) / max(abs(e2), 1e-30)
    return {"e_1d": e1, "e_2d_per_len": e2, "rel_err": rel, "pass": bool(rel <= 1e-12)}


def gate_ga1(n=512):
    """numeric curvature vs closed form 8 c2 d^2 s^2 (lam_p'-lam_m')^2 / rho^2."""
    h = RMAX / n
    rho_all = (np.arange(n) + 0.5) * h
    d = 0.5
    lam_p, lam_m, lam3 = family_profiles(rho_all, 1.0 / 3, 1.0 / 3, 0.8, 1.2, 1.0, "gauss")
    rho, u, v, w = energy_1d(lam_p, lam_m, lam3, h, d)
    # closed form with the SAME discrete stencils
    s_all = lam_p - lam_m
    dif_p = np.empty(n - 1)
    dif_m = np.empty(n - 1)
    dif_p[1:] = (lam_p[2:] - lam_p[:-2]) / (2 * h)
    dif_m[1:] = (lam_m[2:] - lam_m[:-2]) / (2 * h)
    dif_p[0] = (lam_p[1] - lam_p[0]) / (2 * h)   # mirror ghost of a diagonal = itself
    dif_m[0] = (lam_m[1] - lam_m[0]) / (2 * h)
    u_cf = 8.0 * C2 * d * d * (s_all[: n - 1] ** 2) * (dif_p - dif_m) ** 2 / rho ** 2
    rel = float(np.max(np.abs(u - u_cf)) / max(np.max(np.abs(u_cf)), 1e-30))
    return {"max_rel_err": rel, "pass": bool(rel <= 1e-10)}


# ---------------- Cartesian cross-check (GA0b) ----------------
def cartesian_energy(profile_fn, n, d, L=RMAX, rwin=RWIN):
    """full 2D Cartesian (x, y) energy over the disk rho <= rwin; cell-centered
    grid (no cell at the origin); central differences; u = 4 c2 ||[Mx, My]||^2."""
    h = 2.0 * L / n
    xs = -L + (np.arange(n) + 0.5) * h
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    rho = np.hypot(X, Y)
    th = np.arctan2(Y, X)
    lam_p, lam_m, lam3 = profile_fn(rho)
    cth, sth = np.cos(d * th), np.sin(d * th)
    M = np.zeros(X.shape + (4, 4))
    M[..., 0, 0] = G
    M[..., 1, 1] = cth ** 2 * lam_p + sth ** 2 * lam_m
    M[..., 2, 2] = sth ** 2 * lam_p + cth ** 2 * lam_m
    M[..., 1, 2] = M[..., 2, 1] = cth * sth * (lam_p - lam_m)
    M[..., 3, 3] = lam3
    # single-valuedness across the d=1/2 branch cut at theta = pi (x < 0, y -> 0+/-):
    # compare the two rows adjacent to y = 0 at x < -1 (away from the core);
    # diagonal Mt => the tensor is exactly single-valued, so this must be O(h)
    j0, j1 = n // 2 - 1, n // 2
    cutsel = xs < -1.0
    jump = float(np.max(np.abs(M[cutsel, j1] - M[cutsel, j0])))
    Mx = (M[2:, 1:-1] - M[:-2, 1:-1]) / (2 * h)
    My = (M[1:-1, 2:] - M[1:-1, :-2]) / (2 * h)
    u = C2 * 4.0 * m17._norm2_np(m17._comm_np(Mx, My))
    v = potential_v(M[1:-1, 1:-1, 1:4, 1:4])
    mask = rho[1:-1, 1:-1] <= rwin
    return float(np.sum((u + v)[mask]) * h * h), jump


# ---------------- main ----------------
def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(PLOTS, exist_ok=True)
    out = {"units": {"c2": C2, "beta": BETA, "cscale": CSCALE,
                     "a": A_, "b": B_, "c": C_, "vvac": VVAC, "g_time": G},
           "grids": {"rmax": RMAX, "rwin": RWIN}}

    print("== gates GA0 / GA1 ==")
    out["GA0"] = gate_ga0()
    out["GA1"] = gate_ga1()
    print(f"GA0 (1D == m5_17 2D): rel {out['GA0']['rel_err']:.2e} pass={out['GA0']['pass']}")
    print(f"GA1 (closed form):    rel {out['GA1']['max_rel_err']:.2e} pass={out['GA1']['pass']}")

    # ---- A: refinement scaling, equivariant scheme ----
    print("== A: equivariant refinement ==")
    ns = [128, 256, 512, 1024, 2048]
    reg_fn = lambda r: family_profiles(r, 0.5, 0.0, 1.0, 1.0, 1.0, "tanh")
    c1_fn = lambda r: c1_profiles(r, 0.5, 1.0)
    c0_fn = lambda r: c0_profiles(r, 0.0)
    c0d_fn = lambda r: c0_profiles(r, 0.2)
    ref = {"n": ns}
    for tag, fn in [("regularized", reg_fn), ("C1_unreg", c1_fn),
                    ("C0_const", c0_fn), ("C0_const_d02", c0d_fn)]:
        es = []
        for n in ns:
            ec, ev, _ = energy_totals(fn, n, 1.0, rwin=RWIN)
            es.append(ec + ev)
        ref[tag] = es
        print(f"  {tag:14s} E/L(h): " + "  ".join(f"{e:.6f}" for e in es))
    # C1 log fit vs the closed-form slope 16 pi c2 d^2 s0^2 k^2
    hs = np.array([RMAX / n for n in ns])
    slope_fit = float(np.polyfit(np.log(1.0 / hs), np.array(ref["C1_unreg"]), 1)[0])
    s0, k = 0.5, 1.0 - 0.5  # C1: s(0) = mu0p, lam_p'(0) = (1-mu0p)/w
    slope_cf = 16.0 * PI * C2 * 1.0 * s0 ** 2 * k ** 2
    ref["C1_log_slope_fit"] = slope_fit
    ref["C1_log_slope_closed_form"] = slope_cf
    print(f"  C1 log slope: fit {slope_fit:.4f} vs closed form {slope_cf:.4f}")
    # bounded-core check: max cell integrand within rho < 1 across refinements
    core_max = []
    for n in ns:
        _, _, (rho, u, v, w) = energy_totals(reg_fn, n, 1.0)
        core_max.append(float(np.max((u + v)[rho < 1.0])))
    ref["regularized_core_density_max"] = core_max
    out["A_refinement"] = ref

    # ---- GA0b: Cartesian vs equivariant ----
    print("== GA0b: Cartesian cross-check ==")
    cart = {"n": [128, 256, 512, 1024]}
    for tag, fn, d in [("regularized_d1", reg_fn, 1.0),
                       ("regularized_d05", reg_fn, 0.5),
                       ("C0_const_d1", c0_fn, 1.0)]:
        es, jumps = [], []
        for n in cart["n"]:
            e, jump = cartesian_energy(fn, n, d)
            es.append(e)
            jumps.append(jump)
        ec, ev, _ = energy_totals(fn, 2048, d, rwin=RWIN)
        cart[tag] = {"cartesian": es, "equivariant": ec + ev,
                     "branch_jump_per_n": jumps}
        print(f"  {tag:16s} cart: " + "  ".join(f"{e:.5f}" for e in es)
              + f"   equiv: {ec + ev:.5f}")
    out["GA0b"] = cart

    # ---- B: named-center scan + Derrick-balanced optima per degree ----
    print("== B: family scan + optima ==")
    scan = []
    nsc = 1024
    for d in (1.0, 0.5):
        for shape in SHAPES:
            for cname, (mu0, nu0) in CENTERS.items():
                fn = lambda r: family_profiles(r, mu0, nu0, 1.0, 1.0, 1.0, shape)
                ec, ev, _ = energy_totals(fn, nsc, d)
                if ev <= 0 or ec <= 0:
                    scan.append({"d": d, "shape": shape, "center": cname,
                                 "ec": ec, "ev": ev, "e_star": None})
                    continue
                lam = (ec / ev) ** 0.25
                fnl = lambda r: family_profiles(r, mu0, nu0, lam, lam, lam, shape)
                ecl, evl, _ = energy_totals(fnl, nsc, d)
                scan.append({"d": d, "shape": shape, "center": cname,
                             "ec": ec, "ev": ev, "lambda_star": lam,
                             "e_star_analytic": 2.0 * (ec * ev) ** 0.5,
                             "e_star_rescaled": ecl + evl})
    out["B_scan"] = scan

    optima = {}
    for d in (1.0, 0.5):
        cands = [r for r in scan if r["d"] == d and r.get("e_star_rescaled") is not None]
        best = min(cands, key=lambda r: r["e_star_rescaled"])
        mu0, nu0 = CENTERS[best["center"]]
        lam = best["lambda_star"]
        x0 = np.array([mu0, nu0, np.log(lam), np.log(lam), np.log(lam)])

        def obj(x, shape=best["shape"], dd=d):
            mu, nu, lws, lwm, lw3 = x
            ws, wm, w3 = np.exp(np.clip([lws, lwm, lw3], np.log(0.2), np.log(4.0)))
            fn = lambda r: family_profiles(r, mu, nu, ws, wm, w3, shape)
            ec, ev, _ = energy_totals(fn, nsc, dd)
            return ec + ev

        res = minimize(obj, x0, method="Nelder-Mead",
                       options={"maxiter": 800, "xatol": 1e-5, "fatol": 1e-10})
        mu, nu, lws, lwm, lw3 = res.x
        ws, wm, w3 = np.exp(np.clip([lws, lwm, lw3], np.log(0.2), np.log(4.0)))
        fn_opt = lambda r, mu=mu, nu=nu, ws=ws, wm=wm, w3=w3, sh=best["shape"]: \
            family_profiles(r, mu, nu, ws, wm, w3, sh)
        ec, ev, _ = energy_totals(fn_opt, nsc, d)
        # GA2: Derrick stationarity at the optimum
        des = []
        for lamt in (0.98, 1.02):
            fnt = lambda r: family_profiles(r, mu, nu, ws * lamt, wm * lamt, w3 * lamt,
                                            best["shape"])
            e2c, e2v, _ = energy_totals(fnt, nsc, d)
            des.append(e2c + e2v)
        dE_dlnl = (des[1] - des[0]) / np.log(1.02 / 0.98)  # central difference
        ga2 = abs(dE_dlnl) <= 0.01 * (ec + ev)
        # refinement convergence of the optimum
        ec_h, ev_h, _ = energy_totals(fn_opt, nsc // 2, d)
        optima[f"d{d}"] = {
            "shape": best["shape"], "seed_center": best["center"],
            "mu0": float(mu), "nu0": float(nu),
            "ws": float(ws), "wm": float(wm), "w3": float(w3),
            "ec": ec, "ev": ev, "e_star": ec + ev,
            "e_star_n512": ec_h + ev_h,
            "GA2_dE_dln_lambda": float(dE_dlnl), "GA2_pass": bool(ga2),
            "nm_converged": bool(res.success), "nm_iters": int(res.nit)}
        print(f"  d={d}: E* = {ec + ev:.6f} (shape {best['shape']}, seed {best['center']}, "
              f"mu0 {mu:.3f}, nu0 {nu:.3f}, w ({ws:.2f},{wm:.2f},{w3:.2f})) "
              f"GA2 {'PASS' if ga2 else 'FAIL'}")
    optima["degree_ratio_e_star"] = optima["d0.5"]["e_star"] / optima["d1.0"]["e_star"]
    out["B_optima"] = optima
    print(f"  E*(d=1/2) / E*(d=1) = {optima['degree_ratio_e_star']:.4f}")

    # ---- plots ----
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    rr = np.linspace(1e-3, 6, 600)
    for d in (1.0, 0.5):
        o = optima[f"d{d}"]
        lp, lm, l3 = family_profiles(rr, o["mu0"], o["nu0"], o["ws"], o["wm"], o["w3"],
                                     o["shape"])
        ls = "-" if d == 1.0 else "--"
        axes[0].plot(rr, lp, ls, color="C0", label=f"lam+ d={d}")
        axes[0].plot(rr, lm, ls, color="C1", label=f"lam- d={d}")
        axes[0].plot(rr, l3, ls, color="C2", label=f"lam3 d={d}")
    axes[0].set_xlabel("rho")
    axes[0].set_ylabel("eigenvalue")
    axes[0].set_title("per-degree optimal regularized profiles")
    axes[0].legend(fontsize=7)
    for tag, fn, d, col in [("regularized opt d=1",
                             lambda r: family_profiles(
                                 r, optima["d1.0"]["mu0"], optima["d1.0"]["nu0"],
                                 optima["d1.0"]["ws"], optima["d1.0"]["wm"],
                                 optima["d1.0"]["w3"], optima["d1.0"]["shape"]),
                             1.0, "C0"),
                            ("C1 unregularized", c1_fn, 1.0, "C3")]:
        _, _, (rho, u, v, w) = energy_totals(fn, 2048, d)
        axes[1].loglog(rho, np.maximum((u + v) * 2 * PI * rho, 1e-12), color=col, label=tag)
    axes[1].set_xlabel("rho")
    axes[1].set_ylabel("2 pi rho (u + v)")
    axes[1].set_title("radial energy integrand (log-log)")
    axes[1].legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m5_19_ab_profiles.png"), dpi=150)

    fig2, axes2 = plt.subplots(1, 2, figsize=(11, 4.2))
    axes2[0].semilogx(1.0 / hs, ref["C1_unreg"], "o-", color="C3",
                      label=f"C1 unreg (fit slope {slope_fit:.2f}, cf {slope_cf:.2f})")
    axes2[0].semilogx(1.0 / hs, ref["regularized"], "s-", color="C0", label="regularized")
    axes2[0].set_xlabel("1/h")
    axes2[0].set_ylabel("E/L (window)")
    axes2[0].set_title("A: equivariant refinement (log divergence vs bounded)")
    axes2[0].legend(fontsize=8)
    hc = 2.0 * RMAX / np.array(cart["n"], dtype=float)
    for tag, col in [("regularized_d1", "C0"), ("regularized_d05", "C2"),
                     ("C0_const_d1", "C3")]:
        axes2[1].loglog(1.0 / hc, cart[tag]["cartesian"], "o-", color=col,
                        label=f"{tag} (cartesian)")
        axes2[1].axhline(cart[tag]["equivariant"], color=col, ls=":", lw=1)
    axes2[1].set_xlabel("1/h")
    axes2[1].set_ylabel("E/L (window)")
    axes2[1].set_title("GA0b: Cartesian vs equivariant (dotted)")
    axes2[1].legend(fontsize=7)
    fig2.tight_layout()
    fig2.savefig(os.path.join(PLOTS, "m5_19_ab_refinement.png"), dpi=150)

    with open(os.path.join(DATA, "m5_19_ab_vortex.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("wrote data/m5_19_ab_vortex.json + plots/m5_19_ab_{profiles,refinement}.png")


if __name__ == "__main__":
    main()
