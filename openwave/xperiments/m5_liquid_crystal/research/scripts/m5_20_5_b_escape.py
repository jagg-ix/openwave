"""M5.20.5 arm B: the audit-escape's own gate program.

THE CANDIDATE (m5_20_4 audit, C8; findings/m5_20_4_method_note.md § 1):
    L_esc = L_verified + gamma * s2(a = 4.5) + beta * qc(a = 4.5),
    gamma = -1 (the audit's best), beta -> 0+ (here beta = 1e-2 / 1e-4),
where s2 is the dressed-Skyrme density and qc the two-sided dressing
(m5_20_4_c_terms conventions, P = a I - eta M):
    s2 = -SUM_{mu<nu} s_mu s_nu tr(C_munu P C_munu P), C_munu = [X_mu, X_nu]
    qc = -eta^munu tr(X_mu P X_nu P),                  X_mu  = eta d_mu M.
The audit measured: kinetic Hessian Hq + gamma Hs2 + beta Hc is PSD
(exactly marginal at beta = 0, min-eig ~ -1e-13; margin 0.245 at
beta = 1e-2) on every measured background, with texture cost -> 0 as
beta -> 0. STATUS: hypothesis. The candidate lives or dies HERE on its
own gates before any ask is spent (the gamma = -1 sign admissibility
stays author-gated regardless).

PRE-REGISTERED GATES (tasks/m5_20_5_task_details.md):
    b1  statics anchors: frozen-time re-relax of the loop under the
        combined statics; ring / q / core spectrum vs baseline; any
        anchor break = the escape dies at its own statics gate.
    b2  the k10_s2 kinetic-operator build (fast outer-product einsum),
        gated per-cell against density polarization; then the full-grid
        PSD-margin re-check with OUR OWN build (audit cross-check).
    b3  evolution under the combined dynamics from the loop seed:
        bounded to T = 50? band-kept (K_esc PSD along the trajectory,
        |M| bounded, eta-M spectrum sane)? anchors at the endpoint?

NEW EL ALGEBRA (this file; every piece complex-step gated in b0,
try cap 3 per gate). For the s2 term with coefficient +1:
    static energy   U_s2 = SUM_{i<j} tr(C_ij P C_ij P)
    kinetic         T_s2 = SUM_i tr(C_0i P C_0i P),  C_0i = [eta V, X_i]
    pi_s2   = dT/dV     = 2 SUM_i [X_i, P C_0i P] eta
    dT/dA_k (stencil)   = 2 [P C_0k P, X_0] eta
    dT/dM   (pointwise) = -2 SUM_i C_0i P C_0i eta
    dU/dA_k (stencil)   = 2 SUM_{j != k} [X_j, P C_kj P] eta
    dU/dM   (pointwise) = -2 SUM_{i<j} C_ij P C_ij eta
    kdot_s2 = (d pi_s2/dt)|_V : chains Xdot_i = eta A_i(V), Pdot = -eta V
(derivations in the method note; all pieces symmetrized onto the
symmetric cotangent).

Run:  python m5_20_5_b_escape.py b0|b1 [beta]|b2|b3 [beta] [T]
Out:  ../data/m5_20_5_b_<phase>*.json
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import fire_relax, pin_mask                      # noqa: E402
from m5_17_energy import J4, cell_weights                          # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_20_1_b_seeds import core_spectrum, winding_measure_biax    # noqa: E402
from m5_20_2_a_eom import (ETA, G_T, MIR, WSCALE, channels,        # noqa: E402
                           grad_static_4, total_energy_4)
from m5_20_3_a_constraint import (BASIS, BMAT, _cs_dir, build_k10,  # noqa: E402
                                  e_static_c, grad_m_T, kdot_density,
                                  t_density, t_total_c)
from m5_20_4_c_terms import (A_STAR, e_add_static_c, g_u_add,      # noqa: E402
                             grad_m_t_add, k10_add, kdot_add,
                             kin_form_point, load_seed, pi_add,
                             t_add_total_c)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NR, NZ, H = 64, 128, 1.0
DELTA = 0.3
W4 = cell_weights(NR, NZ, H)[..., None, None]
RHO4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
I4 = np.eye(4)
GAMMA = -1.0                    # the audit's best (sign author-gated)


def p_of(Mc, a):
    return a * I4 - ETA @ Mc


def _comm(A, B):
    return A @ B - B @ A


def _symlast(A):
    return 0.5 * (A + np.swapaxes(A, -1, -2))


# ---------------- s2: energies (complex-safe) ----------------
def u_s2_density(Mnp, a, h=H):
    """SUM_{i<j} tr(C_ij P C_ij P) per cell (coefficient +1)."""
    nr = Mnp.shape[0]
    As = channels(Mnp, h)[:3]
    Xs = [ETA @ A for A in As]
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    tot = 0.0
    for i in range(3):
        for j in range(i + 1, 3):
            C = _comm(Xs[i], Xs[j])
            tot = tot + np.einsum("...ij,...ji->...", C @ P, C @ P)
    return tot


def e_s2_static_c(Mnp, a, h=H):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return np.sum(u_s2_density(Mnp, a, h) * w)


def t_s2_density(Mnp, Vnp, a, h=H):
    """SUM_i tr(C_0i P C_0i P) per cell, C_0i = [eta V, X_i]."""
    nr = Mnp.shape[0]
    As = channels(Mnp, h)[:3]
    X0 = ETA @ Vnp[: nr - 1, 1:-1]
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    tot = 0.0
    for A in As:
        C = _comm(X0, ETA @ A)
        tot = tot + np.einsum("...ij,...ji->...", C @ P, C @ P)
    return tot


def t_s2_total_c(Mnp, Vnp, a, h=H):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return np.sum(t_s2_density(Mnp, Vnp, a, h) * w)


# ---------------- s2: EL pieces ----------------
def pi_s2(Mnp, Vnp, a, h=H):
    """dT_s2/dV per cell (symmetrized)."""
    nr = Mnp.shape[0]
    As = channels(Mnp, h)[:3]
    X0 = ETA @ Vnp[: nr - 1, 1:-1]
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    out = 0.0
    for A in As:
        Xi = ETA @ A
        W = P @ _comm(X0, Xi) @ P
        out = out + _comm(Xi, W)
    return _symlast(2.0 * (out @ ETA))


def _scatter(Gr, Gp, Gz, nr, h, rho4):
    """the g_u_add stencil-scatter pattern (rho / phi / z channels)."""
    inv2h = 1.0 / (2.0 * h)
    G = np.zeros(Gr.shape[:2] + (4, 4), dtype=Gr.dtype)
    Gfull = np.zeros((nr, Gr.shape[1] + 2, 4, 4), dtype=Gr.dtype)
    Gfull[1:, 1:-1] += Gr * inv2h
    Gfull[: nr - 2, 1:-1] -= Gr[1:] * inv2h
    Gfull[0, 1:-1] -= (MIR * Gr[0]) * inv2h
    Gfull[: nr - 1, 2:] += Gz * inv2h
    Gfull[: nr - 1, :-2] -= Gz * inv2h
    Gp_r = Gp / rho4
    Jb = np.broadcast_to(J4, Gp_r.shape)
    Gfull[: nr - 1, 1:-1] += -(Jb @ Gp_r - Gp_r @ Jb)
    del G
    return Gfull


def g_u_s2(Mnp, a, w4=None, rho4=None, h=H):
    """dU_s2/dM (w-folded, stencil-scattered + pointwise)."""
    nr = Mnp.shape[0]
    if w4 is None:
        w4 = cell_weights(nr, Mnp.shape[1], h)[..., None, None]
    Arho, Aphi, Az, r4 = channels(Mnp, h)
    if rho4 is None:
        rho4 = r4
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    Xs = [ETA @ Arho, ETA @ Aphi, ETA @ Az]
    Cs = {}
    for i in range(3):
        for j in range(3):
            if i != j:
                Cs[(i, j)] = _comm(Xs[i], Xs[j])
    Ds = []
    for k in range(3):
        D = 0.0
        for j in range(3):
            if j != k:
                W = P @ Cs[(k, j)] @ P
                D = D + _comm(Xs[j], W)
        Ds.append(_symlast(2.0 * (D @ ETA)) * w4)
    G = _scatter(Ds[0], Ds[1], Ds[2], nr, h, rho4)
    pt = 0.0
    for i in range(3):
        for j in range(i + 1, 3):
            C = Cs[(i, j)]
            pt = pt + C @ P @ C
    G[: nr - 1, 1:-1] += w4 * _symlast(-2.0 * (pt @ ETA))
    return G


def g_t_s2(Mnp, Vnp, a, w4=None, rho4=None, h=H):
    """dT_s2/dM at fixed V (w-folded, stencil + pointwise)."""
    nr = Mnp.shape[0]
    if w4 is None:
        w4 = cell_weights(nr, Mnp.shape[1], h)[..., None, None]
    Arho, Aphi, Az, r4 = channels(Mnp, h)
    if rho4 is None:
        rho4 = r4
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    X0 = ETA @ Vnp[: nr - 1, 1:-1]
    Xs = [ETA @ Arho, ETA @ Aphi, ETA @ Az]
    Cs = [_comm(X0, X) for X in Xs]
    Ds = []
    for k in range(3):
        W = P @ Cs[k] @ P
        Ds.append(_symlast(2.0 * (_comm(W, X0) @ ETA)) * w4)
    G = _scatter(Ds[0], Ds[1], Ds[2], nr, h, rho4)
    pt = 0.0
    for C in Cs:
        pt = pt + C @ P @ C
    G[: nr - 1, 1:-1] += w4 * _symlast(-2.0 * (pt @ ETA))
    return G


def kdot_s2(Mnp, Vnp, a, h=H):
    """(d pi_s2 / dt)|_V per cell: chains Xdot_i = eta A_i(V),
    Pdot = -eta V (symmetrized)."""
    nr = Mnp.shape[0]
    As = channels(Mnp, h)[:3]
    Adots = channels(Vnp, h)[:3]
    Vc = Vnp[: nr - 1, 1:-1]
    X0 = ETA @ Vc
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    Pdot = -(ETA @ Vc)
    out = 0.0
    for A, Ad in zip(As, Adots):
        Xi = ETA @ A
        Xd = ETA @ Ad
        C = _comm(X0, Xi)
        Cd = _comm(X0, Xd)
        W = P @ C @ P
        Wd = Pdot @ C @ P + P @ Cd @ P + P @ C @ Pdot
        out = out + _comm(Xd, W) + _comm(Xi, Wd)
    return _symlast(2.0 * (out @ ETA))


def k10_s2(Mnp, a, h=H):
    """the s2 kinetic operator (10x10 per cell, K = 2Q convention),
    fast outer-product build from
    tr(C P C P) = tr(nVXPnVXP) - tr(nVXPXnVP) - tr(XnVPnVXP)
                  + tr(XnVPXnVP),   n = eta, X = X_i,
    each term tr(P1 V P2 V P3) with
    K16[(bc),(de)] = (P2)_cd (P3 P1)_eb."""
    nr = Mnp.shape[0]
    As = channels(Mnp, h)[:3]
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    K16 = 0.0
    for A in As:
        X = ETA @ A
        XP = X @ P
        XPn = XP @ ETA
        XPXn = XP @ X @ ETA
        Pn = P @ ETA
        PXn = P @ X @ ETA
        PX = P @ X
        # (P2, P3P1) per term
        for sgn, P2, P31 in ((1.0, XPn, XPn), (-1.0, XPXn, Pn),
                             (-1.0, Pn, XPXn), (1.0, PXn, PXn)):
            K16 = K16 + sgn * np.einsum("...cd,...eb->...bcde", P2, P31)
    K16 = K16.reshape(K16.shape[:-4] + (16, 16))
    Kop = K16 + np.swapaxes(K16, -1, -2)        # operator = 2Q
    K10 = np.einsum("ai,...ij,bj->...ab", BMAT, Kop, BMAT, optimize=True)
    return 0.5 * (K10 + np.swapaxes(K10, -1, -2))


# ---------------- b0: gates ----------------
def _rand_sym(shape, rng):
    D = rng.normal(size=shape)
    D = 0.5 * (D + np.swapaxes(D, -1, -2))
    out = np.zeros(shape)
    out[: shape[0] - 1, 1:-1] = D[: shape[0] - 1, 1:-1]
    return out


def phase_b0(seed=7, a=A_STAR):
    from m5_20_4_c_terms import density_point
    rng = np.random.default_rng(seed)
    M0 = load_seed("recipe") + 0.05 * _rand_sym((NR, NZ, 4, 4), rng)
    V0 = 0.1 * _rand_sym((NR, NZ, 4, 4), rng)
    D = _rand_sym((NR, NZ, 4, 4), rng)
    out = {}
    # BG1: u_s2 density == density_point static sector (sample cells)
    dens = u_s2_density(M0, a)
    Arho, Aphi, Az, _ = channels(M0, H)
    worst = 0.0
    for (ir, iz) in ((5, 30), (17, 63), (30, 60), (45, 20)):
        Al = [Arho[ir, iz], Aphi[ir, iz], Az[ir, iz]]
        ref = -density_point(M0[: NR - 1, 1:-1][ir, iz],
                             [np.zeros((4, 4))] + Al, "s2", a)
        rel = abs(dens[ir, iz] - ref) / max(abs(ref), 1e-12)
        worst = max(worst, rel)
    out["bg1_static_density"] = worst
    # BG2: g_u_s2 == cs dU/dM
    lhs = float(np.sum(g_u_s2(M0, a, w4=W4, rho4=RHO4) * D))
    rhs = _cs_dir(lambda MM: e_s2_static_c(MM, a), M0, D)
    out["bg2_g_u_s2"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # BG3: t_s2 == density_point kinetic sector (sample) + quadratic
    worst = 0.0
    tden = t_s2_density(M0, V0, a)
    for (ir, iz) in ((5, 30), (30, 60)):
        Al = [Arho[ir, iz], Aphi[ir, iz], Az[ir, iz]]
        Vc = V0[: NR - 1, 1:-1][ir, iz]
        full = density_point(M0[: NR - 1, 1:-1][ir, iz], [Vc] + Al,
                             "s2", a)
        stat = density_point(M0[: NR - 1, 1:-1][ir, iz],
                             [np.zeros((4, 4))] + Al, "s2", a)
        ref = full - stat
        rel = abs(tden[ir, iz] - ref) / max(abs(ref), 1e-12)
        worst = max(worst, rel)
    out["bg3_kin_density"] = worst
    t1 = float(t_s2_total_c(M0, V0, a).real)
    t3 = float(t_s2_total_c(M0, 3.0 * V0, a).real)
    out["bg3_quadratic"] = abs(t3 - 9.0 * t1) / max(abs(t1), 1e-300)
    # BG4: pi_s2 == cs dT/dV
    Dc = D[: NR - 1, 1:-1]
    lhs = float(np.sum(pi_s2(M0, V0, a) * W4 * Dc))
    rhs = _cs_dir(lambda VV: t_s2_total_c(M0, VV, a), V0, D)
    out["bg4_pi"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # BG5: g_t_s2 == cs dT/dM
    lhs = float(np.sum(g_t_s2(M0, V0, a, w4=W4, rho4=RHO4) * D))
    rhs = _cs_dir(lambda MM: t_s2_total_c(MM, V0, a), M0, D)
    out["bg5_g_t"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # BG6: kdot_s2 == cs_M(pi_s2 . T) along V
    T = _rand_sym((NR, NZ, 4, 4), rng)[: NR - 1, 1:-1]
    lhs = float(np.sum(kdot_s2(M0, V0, a) * T))
    rhs = _cs_dir(lambda MM: np.sum(pi_s2(MM, V0, a) * T), M0, V0)
    out["bg6_kdot"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # BG7: k10_s2 einsum == 2 x density polarization (sample cells)
    K10e = k10_s2(M0, a)
    worst = 0.0
    for (ir, iz) in ((5, 30), (17, 63), (30, 60), (45, 20), (60, 100)):
        Al = [Arho[ir, iz], Aphi[ir, iz], Az[ir, iz]]
        Q = kin_form_point(M0[: NR - 1, 1:-1][ir, iz], Al, "s2", a)
        rel = np.abs(K10e[ir, iz] - 2.0 * Q).max() / max(
            np.abs(Q).max() * 2.0, 1e-12)
        worst = max(worst, rel)
    out["bg7_k10_build"] = worst
    # BG8: pi_s2 == k10_s2 . v (operator consistency, sample cells)
    worst = 0.0
    pi = pi_s2(M0, V0, a)
    for (ir, iz) in ((5, 30), (30, 60)):
        v10 = np.einsum("akl,kl->a", BASIS, V0[: NR - 1, 1:-1][ir, iz])
        pi10 = np.einsum("akl,kl->a", BASIS, pi[ir, iz])
        ref = K10e[ir, iz] @ v10
        rel = np.abs(pi10 - ref).max() / max(np.abs(ref).max(), 1e-12)
        worst = max(worst, rel)
    out["bg8_pi_vs_k10"] = worst
    ok = all(v < 1e-8 for v in out.values())
    out["pass"] = bool(ok)
    with open(os.path.join(DATA, "m5_20_5_b_b0.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("[B0] " + " ".join(f"{k}={v:.1e}" for k, v in out.items()
                             if k != "pass")
          + f" -> {'PASS' if ok else 'FAIL'}", flush=True)
    return out


# ---------------- b1: statics anchors ----------------
def phase_b1(beta=1e-2, a=A_STAR, gamma=GAMMA, max_iter=3000):
    M0 = load_seed("recipe")
    rd0 = ring_by_m13(M0, NR, NZ, H)
    q0, _ = winding_measure_biax(M0, NR, NZ, H, rd0["ring13_rho"],
                                 rd0["ring13_z"])
    cs0 = core_spectrum(M0, NR, NZ, H, rd0["ring13_rho"], rd0["ring13_z"])
    comp0 = {"E_old": total_energy_4(M0, WSCALE, DELTA),
             "E_s2_x_gamma": gamma * float(e_s2_static_c(M0, a).real),
             "E_qc_x_beta": float(e_add_static_c(M0, beta, a).real)}
    print(f"[B1] recipe components: {comp0}", flush=True)
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = W4[..., 0, 0]
    precond = (1.0 / wfull)[..., None, None]

    def g_frozen(MM):
        G = grad_static_4(MM, WSCALE, DELTA, w4=W4, rho4=RHO4) \
            + gamma * g_u_s2(MM, a, w4=W4, rho4=RHO4) \
            + g_u_add(MM, beta, a, w4=W4, rho4=RHO4)
        G[..., 0, :] = 0.0
        G[..., :, 0] = 0.0
        return G

    def e_tot(MM):
        return (total_energy_4(MM, WSCALE, DELTA)
                + gamma * float(e_s2_static_c(MM, a).real)
                + float(e_add_static_c(MM, beta, a).real))

    egf = lambda MM: (e_tot(MM), g_frozen(MM))  # noqa: E731
    Mx = M0.copy()
    hist = []
    done = 0
    while done < max_iter:
        Mx, hh = fire_relax(Mx, egf, free4, precond, max_iter=500,
                            tol_rel=1e-9, dt0=0.005, dt_max=0.05,
                            log_every=500)
        done += hh["iter"][-1]
        if not np.all(np.isfinite(Mx)):
            hist.append({"it": done, "blowup": True})
            print("  B1 BLOWUP (non-finite state)", flush=True)
            break
        rd = ring_by_m13(Mx, NR, NZ, H)
        qm, _ = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                     rd["ring13_z"])
        cs = core_spectrum(Mx, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
        hist.append({"it": done, "E": hh["E"][-1], "gnorm": hh["gnorm"][-1],
                     "ring_rho": rd["ring13_rho"],
                     "q": None if not np.isfinite(qm) else float(qm),
                     "core_lam": cs["lam"]})
        print(f"  B1 it {done}: E {hh['E'][-1]:.4f} ring "
              f"{rd['ring13_rho']:.2f} q {hist[-1]['q']}", flush=True)
        if not np.isfinite(hh["E"][-1]):
            break
        if hh["iter"][-1] < 500:
            break
    fin = hist[-1] if hist else {}
    survived = bool(fin.get("q") == 0.5 and not fin.get("blowup")
                    and np.isfinite(fin.get("E", np.nan))
                    and abs(fin.get("ring_rho", 0) - rd0["ring13_rho"])
                    < 3.0)
    out = {"beta": beta, "a": a, "gamma": gamma,
           "components_recipe": comp0,
           "baseline": {"ring_rho": rd0["ring13_rho"],
                        "q": None if not np.isfinite(q0) else float(q0),
                        "core_lam": cs0["lam"]},
           "relaxed": fin, "hist": hist, "anchors_survive": survived}
    if survived:
        np.savez_compressed(
            os.path.join(DATA, f"m5_20_5_b_seed_esc_b{beta:g}.npz"), M=Mx)
        out["seed_file"] = f"m5_20_5_b_seed_esc_b{beta:g}.npz"
    with open(os.path.join(DATA, f"m5_20_5_b_b1_b{beta:g}.json"),
              "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[B1 beta={beta:g}] anchors_survive = {survived} "
          f"(ring {rd0['ring13_rho']:.2f} -> {fin.get('ring_rho')}, "
          f"q {out['baseline']['q']} -> {fin.get('q')})", flush=True)
    return out


# ---------------- b2: PSD margins (own build) ----------------
def phase_b2(a=A_STAR, gamma=GAMMA):
    out = {"a": a, "gamma": gamma, "backgrounds": {}}
    tags = [("recipe", None)]
    for b in (1e-2,):
        fn = os.path.join(DATA, f"m5_20_5_b_seed_esc_b{b:g}.npz")
        if os.path.exists(fn):
            tags.append((f"esc_relaxed_b{b:g}", fn))
    fn = os.path.join(DATA, "m5_20_5_a_a2_wp0_best.npz")
    if os.path.exists(fn):
        tags.append(("a2_wp0_best", fn))
    for tag, fn in tags:
        M = load_seed("recipe") if fn is None else np.load(fn)["M"]
        Mc = M[: NR - 1, 1:-1]
        Kq = 4.0 * build_k10(M, H)
        Ks2 = k10_s2(M, a)
        Kc1 = k10_add(Mc, 1.0, a)
        rows = {}
        for beta in (0.0, 1e-4, 1e-2):
            lam = np.linalg.eigvalsh(Kq + gamma * Ks2 + beta * Kc1)
            rows[f"beta={beta:g}"] = {
                "mineig": float(lam.min()),
                "frac_cells_neg": float(
                    (lam.min(axis=-1) < -1e-10).mean())}
        out["backgrounds"][tag] = rows
        print(f"[B2 {tag}] " + " ".join(
            f"b={b}: {rows[f'beta={b:g}']['mineig']:.3e}"
            for b in (0.0, 1e-4, 1e-2)), flush=True)
    with open(os.path.join(DATA, "m5_20_5_b_b2.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- b3: the combined evolution ----------------
def accel_esc(Mnp, Vnp, gamma, beta, a, w4, h=H, rho4=None,
              want_diag=False):
    """EL solve under L_esc: (4 kq + gamma ks2 + beta kc)[Mddot] = rhs."""
    nr, nz = Mnp.shape[:2]
    Mc = Mnp[: nr - 1, 1:-1]
    Vc = Vnp[: nr - 1, 1:-1]
    G_stat = grad_static_4(Mnp, WSCALE, DELTA, h=h, w4=w4, rho4=rho4) \
        + gamma * g_u_s2(Mnp, a, w4=w4, rho4=rho4, h=h) \
        + g_u_add(Mnp, beta, a, w4=w4, rho4=rho4, h=h)
    GT = grad_m_T(Mnp, Vnp, w4, h=h, rho4=rho4) \
        + gamma * g_t_s2(Mnp, Vnp, a, w4=w4, rho4=rho4, h=h)
    GT[: nr - 1, 1:-1] += w4 * grad_m_t_add(Mc, Vc, beta, a)
    kd = kdot_density(Mnp, Vnp, h=h)
    rhs = (((GT - G_stat)[: nr - 1, 1:-1]) / w4) - 4.0 * kd \
        - gamma * kdot_s2(Mnp, Vnp, a, h=h) - kdot_add(Mc, Vc, beta, a)
    r10 = np.einsum("akl,...kl->...a", BASIS, rhs)
    K10 = 4.0 * build_k10(Mnp, h) + gamma * k10_s2(Mnp, a, h) \
        + k10_add(Mc, beta, a)
    lam, U = np.linalg.eigh(K10)
    rU = np.einsum("...ka,...k->...a", U, r10)
    floor = 1e-14 * float(np.abs(lam).max())
    safe = np.where(np.abs(lam) > floor, lam, np.inf)
    a10 = np.einsum("...ka,...a->...k", U, rU / safe)
    acc = np.zeros_like(Mnp)
    acc[: nr - 1, 1:-1] = np.einsum("...a,akl->...kl", a10, BASIS)
    acc[pin_mask(nr, nz)] = 0.0
    diag = None
    if want_diag:
        eig = np.linalg.eigvalsh(ETA @ Mnp[: nr - 1, 1:-1])
        diag = {"mass_mineig": float(lam.min()),
                "max_abs_acc": float(np.max(np.abs(acc))),
                "n_floor_cells": int((np.abs(lam) <= floor).any(-1).sum()),
                "etaM_eig_min": float(eig.min()),
                "etaM_eig_max": float(eig.max())}
    return acc, diag


def phase_b3(beta=1e-2, a=A_STAR, gamma=GAMMA, T=50.0, dt=0.00125,
             seed_kind="recipe", n_film=6):
    M0 = load_seed(seed_kind)
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    Mx = M0.copy()
    v = np.zeros_like(Mx)
    n_steps = int(round(T / dt))
    snap_every = max(1, int(0.25 / dt))
    film_every = max(1, n_steps // (n_film - 1))
    frames = [{"it": 0, "t": 0.0, "M": M0.copy()}]
    recs = []
    t0 = time.time()

    def snap(it, diag):
        ke_q = float(np.sum(t_density(Mx, v, H) * W4[..., 0, 0]))
        ke_s2 = gamma * float(t_s2_total_c(Mx, v, a).real)
        ke_c = float(t_add_total_c(Mx, v, beta, a).real)
        pe_q = float(e_static_c(Mx, WSCALE, DELTA).real)
        pe_s2 = gamma * float(e_s2_static_c(Mx, a).real)
        pe_c = float(e_add_static_c(Mx, beta, a).real)
        rd = ring_by_m13(Mx, NR, NZ, H)
        qm, _ = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                     rd["ring13_z"])
        r = {"it": it, "t": it * dt, "KE_q": ke_q, "KE_s2": ke_s2,
             "KE_C": ke_c, "PE_q": pe_q, "PE_s2": pe_s2, "PE_C": pe_c,
             "E_tot": ke_q + ke_s2 + ke_c + pe_q + pe_s2 + pe_c,
             "ring_rho": float(rd["ring13_rho"]),
             "q_r4": None if not np.isfinite(qm) else float(qm),
             "max_abs_M": float(np.max(np.abs(Mx))),
             "max_v": float(np.max(np.abs(v)))}
        if diag:
            r.update(diag)
        recs.append(r)
        print(f"  it {it:7d} t {r['t']:8.2f} E {r['E_tot']:12.6f} "
              f"q {r['q_r4']} ring {r['ring_rho']:.1f} "
              f"kmin {r.get('mass_mineig', float('nan')):.2e}", flush=True)

    acc, diag = accel_esc(Mx, v, gamma, beta, a, W4, H, RHO4,
                          want_diag=True)
    snap(0, diag)
    blow = False
    for it in range(1, n_steps + 1):
        vh = v + 0.5 * dt * acc
        Mx += dt * vh * free4
        if (not np.all(np.isfinite(Mx))) or float(np.max(np.abs(Mx))) > 1e6:
            recs.append({"it": it, "t": it * dt, "E_tot": float("nan"),
                         "blowup": True})
            print(f"  BLOWUP at it {it} (t {it * dt:.2f})", flush=True)
            blow = True
            break
        want = (it % snap_every == 0) or (it == n_steps)
        acc, diag = accel_esc(Mx, vh, gamma, beta, a, W4, H, RHO4,
                              want_diag=want)
        v = (vh + 0.5 * dt * acc) * free4
        if want:
            snap(it, diag)
        if it % film_every == 0 and len(frames) < n_film:
            frames.append({"it": it, "t": it * dt, "M": Mx.copy()})
    fin = [r for r in recs if np.isfinite(r.get("E_tot", np.nan))]
    drift = (abs(fin[-1]["E_tot"] - fin[0]["E_tot"])
             / max(abs(fin[0]["E_tot"]), 1e-12)) if len(fin) > 1 else None
    kmin_traj = min((r["mass_mineig"] for r in recs
                     if "mass_mineig" in r), default=None)
    out = {"beta": beta, "a": a, "gamma": gamma, "T": T, "dt": dt,
           "seed_kind": seed_kind, "wall_s": round(time.time() - t0, 1),
           "reached_T": bool(fin and fin[-1]["t"] >= T - 2 * dt
                             and not blow),
           "E_rel_drift": drift, "kinetic_mineig_along_traj": kmin_traj,
           "trajectory": recs}
    np.savez_compressed(os.path.join(DATA,
                                     f"m5_20_5_b_b3_b{beta:g}_end.npz"),
                        M=Mx, V=v)
    np.savez_compressed(os.path.join(DATA,
                                     f"m5_20_5_b_b3_b{beta:g}_films.npz"),
                        **{f"M{i}": fr["M"] for i, fr in enumerate(frames)},
                        ts=np.array([fr["t"] for fr in frames]))
    with open(os.path.join(DATA, f"m5_20_5_b_b3_b{beta:g}.json"),
              "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[B3 beta={beta:g}] reached_T={out['reached_T']} drift={drift} "
          f"kmin_traj={kmin_traj} wall {out['wall_s']}s", flush=True)
    return out


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "b0"
    if which == "b0":
        phase_b0()
    elif which == "b1":
        phase_b1(float(ARGV[1]) if len(ARGV) > 1 else 1e-2)
    elif which == "b2":
        phase_b2()
    elif which == "b3":
        phase_b3(float(ARGV[1]) if len(ARGV) > 1 else 1e-2,
                 T=float(ARGV[2]) if len(ARGV) > 2 else 50.0)
    else:
        raise SystemExit(f"unknown phase {which}")
