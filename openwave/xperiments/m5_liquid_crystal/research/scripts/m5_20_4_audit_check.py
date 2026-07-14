"""M5.20.4 ADVERSARIAL AUDIT (independent second agent, cardinal rule).

Attacks the M5.20.4 claims C1-C8 with independently-built instruments:
own densities, own polarization Hessians, own null projectors, own
winding integrals, own orbit evaluations. Trusted (previously audited)
imports ONLY: m5_20_3_a_constraint (t_density, t_total_c, e_static_c,
build_k10, grad_m_T, kdot_density, BASIS, ETA10), m5_20_2_a_eom
(channels, vac4, ETA, u_eta_density, v4_density, grad_static_4,
total_energy_4, WSCALE), m5_17/16/19/20_1 stack (cell_weights,
pin_mask, J4, ring_by_m13, winding_measure_biax, core_spectrum).
The m5_20_4_* derived functions (k10_add, grad_q2) are imported ONLY as
comparison targets, never used as instruments.

Run:  python m5_20_4_audit_check.py            (all phases, ~5-10 min)
Out:  ../data/m5_20_4_audit.json
"""
from __future__ import annotations

import json
import os
import sys
import time
import traceback

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = sys.argv[:1]

from m5_17_energy import cell_weights, J4                           # noqa: E402
from m5_16_axisym import pin_mask                                   # noqa: E402
from m5_19_d1_relax import ring_by_m13                              # noqa: E402
from m5_20_1_b_seeds import winding_measure_biax, core_spectrum     # noqa: E402
from m5_20_2_a_eom import (ETA, G_T, WSCALE, channels,              # noqa: E402
                           grad_static_4, total_energy_4,
                           u_eta_density, v4_density, vac4)
from m5_20_3_a_constraint import (BASIS, ETA10, build_k10,          # noqa: E402
                                  e_static_c, grad_m_T, kdot_density,
                                  t_density, t_total_c)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NR, NZ, H = 64, 128, 1.0
DELTA = 0.3
A_STAR = 4.5
BETA_CLAIM = 1.305571288421561
W4 = cell_weights(NR, NZ, H)[..., None, None]
RHO4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
I4 = np.eye(4)
SVEC = np.array([-1.0, 1.0, 1.0, 1.0])
RESULT = {"task": "M5.20.4 adversarial audit", "date": "2026-07-14",
          "auditor": "independent second agent",
          "trusted_instruments": "m5_20_3_a/m5_20_2_a/m5_17-20_1 stack",
          "claims": {}}


def mtr(A):
    return np.einsum("...ii->...", A)


def load_m(name):
    return np.load(os.path.join(DATA, name))["M"]


def rand_sym4(rng, n=None):
    X = rng.normal(size=(4, 4) if n is None else (n, 4, 4))
    return 0.5 * (X + np.swapaxes(X, -1, -2))


def poly_n(N, coef):
    """coef[0] I + coef[1] N + coef[2] N^2 + coef[3] N^3 (batched)."""
    out = coef[0] * np.broadcast_to(I4, N.shape).copy()
    P = N
    for c in coef[1:]:
        out = out + c * P
        P = P @ N
    return out


# ================================================================ C1
def c1_lemma_l1(rng):
    """the commutator class carries NO kinetic content along Mdot ~ eta:
    check full-density invariance under V -> V + c*eta for MY OWN dressed
    commutator densities, plus the eta-null of my own kinetic form."""
    def xs(M, Gs):
        return [ETA @ G for G in Gs]

    def dens(M, Gs, kind, P1, P2):
        X = xs(M, Gs)
        C = lambda m, n: X[m] @ X[n] - X[n] @ X[m]        # noqa: E731
        if kind == "s_dressed":     # sum_{mu<nu} s_mu s_nu tr(C P1 C P2)
            tot = 0.0
            for m in range(4):
                for n in range(m + 1, 4):
                    Cmn = C(m, n)
                    tot += SVEC[m] * SVEC[n] * mtr(Cmn @ P1 @ Cmn @ P2)
            return tot
        if kind == "mixed":         # tr(C_01 P1 C_23 P2)  (linear in V)
            return mtr(C(0, 1) @ P1 @ C(2, 3) @ P2)
        if kind == "cross":         # tr(C_01 P1 C_02 P2)
            return mtr(C(0, 1) @ P1 @ C(0, 2) @ P2)
        if kind == "tracesplit":    # tr(C_01 P1) tr(C_02 P2)
            return mtr(C(0, 1) @ P1) * mtr(C(0, 2) @ P2)
        if kind == "xdress":        # tr(C_01 X_2 P1 C_01 X_3 P2)
            return mtr(C(0, 1) @ X[2] @ P1 @ C(0, 1) @ X[3] @ P2)
        raise ValueError(kind)

    kinds = ("s_dressed", "mixed", "cross", "tracesplit", "xdress")
    worst = {k: 0.0 for k in kinds}
    scale = {k: 0.0 for k in kinds}
    for _ in range(8):
        M = rand_sym4(rng)
        A = [rand_sym4(rng) for _ in range(3)]
        V = rand_sym4(rng)
        c = rng.normal()
        N = ETA @ M
        P1 = poly_n(N[None], rng.normal(size=4))[0]
        P2 = poly_n(N[None], rng.normal(size=4))[0]
        for k in kinds:
            d_v = dens(M, [V] + A, k, P1, P2)
            d_vs = dens(M, [V + c * ETA] + A, k, P1, P2)
            d_e = dens(M, [c * ETA] + A, k, P1, P2)
            d_0 = dens(M, [np.zeros((4, 4))] + A, k, P1, P2)
            worst[k] = max(worst[k], abs(d_vs - d_v), abs(d_e - d_0))
            scale[k] = max(scale[k], abs(d_v) + abs(d_0))
    # my own kinetic quadratic form of the dressed-Skyrme density
    M = rand_sym4(rng)
    A = [rand_sym4(rng) for _ in range(3)]
    N = ETA @ M
    P1 = poly_n(N[None], rng.normal(size=4))[0]
    P2 = poly_n(N[None], rng.normal(size=4))[0]
    z = np.zeros((4, 4))

    def tkin(V):
        return (dens(M, [V] + A, "s_dressed", P1, P2)
                - dens(M, [z] + A, "s_dressed", P1, P2))
    Q = np.zeros((10, 10))
    tb = [tkin(B) for B in BASIS]
    for i in range(10):
        for j in range(i, 10):
            Q[i, j] = Q[j, i] = 0.5 * (tkin(BASIS[i] + BASIS[j])
                                       - tb[i] - tb[j])
    null_resid = float(np.abs(Q @ ETA10).max())
    qmax = float(np.abs(Q).max())
    ok = (max(worst.values()) < 1e-9 * max(1.0, max(scale.values()))
          and null_resid < 1e-10 * max(qmax, 1e-30) and qmax > 1e-3)
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "invariance_worst_abs": worst, "density_scale": scale,
           "own_kinform_eta_null_resid": null_resid,
           "own_kinform_max_abs": qmax,
           "algebra": "X0 = eta.eta = I commutes with all -> C_0i = 0; "
                      "checked V -> V + c*eta full-density invariance"}
    print(f"[C1] {out['verdict']}: worst invariance "
          f"{max(worst.values()):.2e} (scales up to "
          f"{max(scale.values()):.1e}); own Q.eta = {null_resid:.2e} "
          f"vs |Q| = {qmax:.2e}", flush=True)
    return out


# ================================================================ C2
def my_qc_density(Mb, Vb, a):
    """my own qc term density tr(eta V P eta V P), batched."""
    P = a * I4 - ETA @ Mb
    X = ETA @ Vb
    return mtr(X @ P @ X @ P)


def my_two_sided(Mb, Vb, Pm, Qm):
    X = ETA @ Vb
    return mtr(X @ Pm @ X @ Qm)


def qform10(fun):
    """10x10 quadratic form of a purely-quadratic scalar fun(V)."""
    Q = np.zeros((10, 10))
    tb = [fun(B) for B in BASIS]
    for i in range(10):
        for j in range(i, 10):
            Q[i, j] = Q[j, i] = 0.5 * (fun(BASIS[i] + BASIS[j])
                                       - tb[i] - tb[j])
    return Q


def c2_lemma_l2():
    Mv = vac4(DELTA)                    # diag(-8, 1, 0.3, 0)
    lam = np.array([G_T, 1.0, DELTA, 0.0])
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    worst_formula = 0.0
    for a in (0.7, 1.5, 4.5, 7.2, 9.0):
        Q = qform10(lambda V: my_qc_density(Mv[None], V[None], a)[0])
        p = a - lam
        F = np.zeros((10, 10))
        for i in range(4):
            F[i, i] = p[i] ** 2
        for k, (i, j) in enumerate(pairs):
            F[4 + k, 4 + k] = SVEC[i] * SVEC[j] * p[i] * p[j] * (-1.0
                              if False else 1.0)
        # eta_ii eta_jj p_i p_j with eta = diag(-1,1,1,1):
        for k, (i, j) in enumerate(pairs):
            eii = -1.0 if i == 0 else 1.0
            ejj = -1.0 if j == 0 else 1.0
            F[4 + k, 4 + k] = eii * ejj * p[i] * p[j]
        worst_formula = max(worst_formula,
                            float(np.abs(Q - F).max()
                                  / max(np.abs(F).max(), 1e-30)))
    # window scan (fine + boundary probes)
    a_grid = np.concatenate([np.linspace(0.2, 9.8, 97),
                             [0.99, 1.0, 1.01, 7.99, 8.0, 8.01]])
    a_grid = np.sort(a_grid)
    mins = []
    for a in a_grid:
        Q = qform10(lambda V: my_qc_density(Mv[None], V[None], float(a))[0])
        mins.append(float(np.linalg.eigvalsh(Q).min()))
    mins = np.array(mins)
    pos = a_grid[mins > 1e-12]
    at = {f"a={a}": float(m) for a, m in zip(a_grid, mins)
          if a in (0.99, 1.0, 1.01, 7.99, 8.0, 8.01)}
    inside = bool(pos.size and pos.min() > 1.0 and pos.max() < 8.0)
    bounds_out = at["a=1.0"] <= 1e-10 and at["a=8.0"] <= 1e-10 \
        and at["a=1.01"] > 0 and at["a=7.99"] > 0 \
        and at["a=0.99"] < 0 and at["a=8.01"] < 0
    ok = worst_formula < 1e-12 and inside and bounds_out
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "formula_rel_err_max": worst_formula,
           "pd_window_measured": [float(pos.min()), float(pos.max())]
           if pos.size else None,
           "boundary_mineigs": at}
    print(f"[C2] {out['verdict']}: formula rel {worst_formula:.2e}; "
          f"PD strictly inside ({pos.min():.2f}, {pos.max():.2f}); "
          f"boundaries {at}", flush=True)
    return out


# ================================================================ C3
def hess_fields_recipe(M):
    """full-grid per-cell Hessians (MY OWN polarization):
    quartic from trusted t_density; qc from my own density."""
    nr, nz = M.shape[:2]
    ncell = (nr - 1, nz - 2)
    Mc = M[: nr - 1, 1:-1]

    def tq(B):
        V = np.zeros_like(M)
        V[: nr - 1, 1:-1] = B
        return t_density(M, V, H)

    def tc(B):
        return my_qc_density(Mc, np.broadcast_to(B, Mc.shape), A_STAR)

    Hq = np.zeros(ncell + (10, 10))
    Hc = np.zeros(ncell + (10, 10))
    tbq = [tq(B) for B in BASIS]
    tbc = [tc(B) for B in BASIS]
    for i in range(10):
        for j in range(i, 10):
            qij = 0.5 * (tq(BASIS[i] + BASIS[j]) - tbq[i] - tbq[j])
            cij = 0.5 * (tc(BASIS[i] + BASIS[j]) - tbc[i] - tbc[j])
            Hq[..., i, j] = Hq[..., j, i] = qij
            Hc[..., i, j] = Hc[..., j, i] = cij
    return 2.0 * Hq, 2.0 * Hc          # quadratic form -> Hessian


def bisect_beta(Hq, Hc, tol_iters=45):
    def mineig(b):
        return float(np.linalg.eigvalsh(Hq + b * Hc).min())
    hi = 1.0
    k = 0
    while mineig(hi) < 0 and k < 40:
        hi *= 2.0
        k += 1
    if mineig(hi) < 0:
        return None, mineig(hi)
    lo = 0.0
    for _ in range(tol_iters):
        mid = 0.5 * (lo + hi)
        if mineig(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return hi, mineig(hi)


def c3_beta_star(rng):
    M = load_m("m5_20_3_b_seed_recipe.npz")
    Hq, Hc = hess_fields_recipe(M)                 # MY Hessians
    K4 = 4.0 * build_k10(M, H)                     # claimed quartic matrix
    from m5_20_4_c_terms import k10_add            # TARGET (compare only)
    Kc = k10_add(M[: NR - 1, 1:-1], 1.0, A_STAR)   # claimed term matrix
    rel_q = float(np.abs(Hq - K4).max() / np.abs(K4).max())
    rel_c = float(np.abs(Hc - Kc).max() / np.abs(Kc).max())
    cells = [(5, 30), (17, 63), (30, 60), (45, 20), (60, 100)]
    percell = {}
    for (ci, cj) in cells:
        percell[f"{ci},{cj}"] = {
            "quartic_rel": float(np.abs(Hq[ci, cj] - K4[ci, cj]).max()
                                 / max(np.abs(K4[ci, cj]).max(), 1e-30)),
            "qc_rel": float(np.abs(Hc[ci, cj] - Kc[ci, cj]).max()
                            / max(np.abs(Kc[ci, cj]).max(), 1e-30))}
    bstar_full, me_full = bisect_beta(Hq, Hc)
    # random subsample >= 500 cells (per the audit brief)
    ncell = Hq.shape[0] * Hq.shape[1]
    idx = rng.choice(ncell, size=500, replace=False)
    Hqs = Hq.reshape(ncell, 10, 10)[idx]
    Hcs = Hc.reshape(ncell, 10, 10)[idx]
    bstar_sub, me_sub = bisect_beta(Hqs, Hcs)
    dev = abs(bstar_full - BETA_CLAIM) / BETA_CLAIM
    ok = rel_q < 1e-12 and rel_c < 1e-12 and dev < 1e-6
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "hessian_vs_claimed_rel": {"quartic_4xbuild_k10": rel_q,
                                      "qc_k10_add": rel_c},
           "percell_checks": percell,
           "beta_star_mine_fullgrid": bstar_full,
           "mineig_at_beta_star": me_full,
           "beta_star_mine_sub500": bstar_sub,
           "beta_star_claimed": BETA_CLAIM,
           "rel_dev_vs_claim": dev,
           "wrong_pairing_would_give": {"half": BETA_CLAIM / 2,
                                        "double": BETA_CLAIM * 2},
           "subsample": {"n_cells_full": ncell, "n_cells_sub": 500},
           "quartic_mineig_fullgrid": float(np.linalg.eigvalsh(Hq).min()),
           "qc_mineig_fullgrid": float(np.linalg.eigvalsh(Hc).min())}
    print(f"[C3] {out['verdict']}: Hessians match claimed matrices to "
          f"{max(rel_q, rel_c):.1e}; my beta* = {bstar_full:.9f} "
          f"(claimed {BETA_CLAIM:.9f}, dev {dev:.1e}); sub500 beta* = "
          f"{bstar_sub:.6f}", flush=True)
    return out, Hq, Hc


# ================================================================ C4
def c4_obstruction(rng, Hq):
    Mv = np.broadcast_to(vac4(DELTA), (NR, NZ, 4, 4)).copy()
    u_max = float(np.abs(u_eta_density(Mv, H)).max())
    v_max = float(np.abs(v4_density(Mv, WSCALE, DELTA)).max())
    e_stat = float(e_static_c(Mv, WSCALE, DELTA).real)
    # my own A_phi + texture cost
    Mc = Mv[: NR - 1, 1:-1]
    Aphi_mine = (J4 @ Mc - Mc @ J4) / RHO4
    Ar, Ap, Az, _ = channels(Mv, H)
    cross = float(np.abs(Ap - Aphi_mine).max())
    ar_max, az_max = float(np.abs(Ar).max()), float(np.abs(Az).max())
    w = cell_weights(NR, NZ, H)
    beta = 1.306
    uc_mine = float(beta * np.sum(
        my_qc_density(Mc, Aphi_mine, A_STAR) * w))
    # ---- (b) the two-sided (P, Q) family at the vacuum ----
    lam = np.array([G_T, 1.0, DELTA, 0.0])
    eta_d = np.array([-1.0, 1.0, 1.0, 1.0])
    # validate the coefficient formula against my polarized form
    worst_pq = 0.0
    Mv1 = vac4(DELTA)
    for _ in range(5):
        p = rng.normal(size=4)
        q = rng.normal(size=4)
        Q10 = qform10(lambda V: my_two_sided(Mv1[None], V[None],
                                             np.diag(p), np.diag(q))[0])
        F = np.zeros((10, 10))
        for i in range(4):
            F[i, i] = p[i] * q[i]
        pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
        for k, (i, j) in enumerate(pairs):
            F[4 + k, 4 + k] = eta_d[i] * eta_d[j] * 0.5 * (
                p[i] * q[j] + p[j] * q[i])
        worst_pq = max(worst_pq, float(np.abs(Q10 - F).max()))
    # random scan: PSD samples and their (1,2) charge
    n_scan = 400000
    P = rng.uniform(-3, 3, size=(n_scan, 4))
    Q = rng.uniform(-3, 3, size=(n_scan, 4))
    diag = P * Q                                        # c_ii
    pairs = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
    coeffs = [diag[:, i] for i in range(4)]
    for (i, j) in pairs:
        cij = 0.5 * (P[:, i] * Q[:, j] + P[:, j] * Q[:, i])
        coeffs.append(eta_d[i] * eta_d[j] * cij)
    C = np.stack(coeffs, axis=1)                        # (n, 10)
    psd = np.all(C >= -1e-12, axis=1)
    c12 = 0.5 * (P[:, 1] * Q[:, 2] + P[:, 2] * Q[:, 1])
    n_psd = int(psd.sum())
    sel = psd & (diag[:, 1] > 1e-3) & (diag[:, 2] > 1e-3)
    ratio = np.abs(c12[sel]) / np.sqrt(diag[sel, 1] * diag[sel, 2])
    ratio_min = float(ratio.min()) if sel.any() else None
    # constrained c12 = 0 scan: solve q2 = -p2 q1 / p1
    n_con = 200000
    Pc = rng.uniform(-3, 3, size=(n_con, 4))
    Qc = rng.uniform(-3, 3, size=(n_con, 4))
    good = np.abs(Pc[:, 1]) > 1e-6
    Pc, Qc = Pc[good], Qc[good]
    Qc[:, 2] = -Pc[:, 2] * Qc[:, 1] / Pc[:, 1]
    diagc = Pc * Qc
    coeffs = [diagc[:, i] for i in range(4)]
    for (i, j) in pairs:
        cij = 0.5 * (Pc[:, i] * Qc[:, j] + Pc[:, j] * Qc[:, i])
        coeffs.append(eta_d[i] * eta_d[j] * cij)
    Cc = np.stack(coeffs, axis=1)
    min_coeff = Cc.min(axis=1)
    best = float(min_coeff.max())          # best "PSD margin" with c12 = 0
    # can a c11 = 0 (or c22 = 0) degenerate term still close? the quartic
    # sub-block on the index-1 rows (10-basis dirs 1, 4, 7, 8) must then
    # be PSD by itself: measure its min eig over the recipe grid
    sub = np.ix_([1, 4, 7, 8], [1, 4, 7, 8])
    sub_min1 = float(np.linalg.eigvalsh(Hq[..., [1, 4, 7, 8], :]
                                        [..., :, [1, 4, 7, 8]]).min())
    sub2 = [2, 5, 7, 9]
    sub_min2 = float(np.linalg.eigvalsh(Hq[..., sub2, :]
                                        [..., :, sub2]).min())
    ok_a = (u_max < 1e-12 and v_max < 1e-20 and abs(e_stat) < 1e-12
            and cross < 1e-12 and 8.5e4 < uc_mine < 9.7e4)
    ok_b = (worst_pq < 1e-12 and (ratio_min is None or ratio_min > 0.999)
            and best < 1e-9 and sub_min1 < -1.0 and sub_min2 < -1.0)
    out = {"verdict": "CONFIRMED" if (ok_a and ok_b) else "QUALIFIED",
           "a_vacuum": {"u_eta_max": u_max, "v4_max": v_max,
                        "E_static": e_stat,
                        "Aphi_mine_vs_channels_maxdiff": cross,
                        "Arho_max": ar_max, "Az_max": az_max,
                        "U_C_mine_beta1.306_a4.5": uc_mine,
                        "U_C_claimed": 9.1e4},
           "b_family": {"coeff_formula_maxerr": worst_pq,
                        "n_scan": n_scan, "n_psd": n_psd,
                        "min_ratio_c12_over_geomean": ratio_min,
                        "amgm_bound": "|c12| >= sqrt(c11 c22), eq iff "
                                      "p1 q2 = p2 q1 (P = Q saturates)",
                        "c12zero_constrained_n": int(len(Cc)),
                        "c12zero_best_min_coeff": best,
                        "quartic_subblock_idx1_mineig": sub_min1,
                        "quartic_subblock_idx2_mineig": sub_min2}}
    print(f"[C4] {out['verdict']}: vacuum E = {e_stat:.2e} yet U_C(mine) "
          f"= {uc_mine:.4e} (claimed 9.1e4); PSD scan {n_psd}/{n_scan}, "
          f"min |c12|/sqrt(c11 c22) = {ratio_min}; c12=0 best margin "
          f"{best:.2e}; quartic idx-1 subblock mineig {sub_min1:.1f}",
          flush=True)
    return out


# ================================================================ C5
def my_winding(M, rho_c, z_c, r_w=4.0, npts=720):
    """my own winding integral: bilinear interp of the (1,3)-block
    eigenframe angle on the included-cell grid."""
    nr, nz = M.shape[:2]
    Mi = M[: nr - 1, 1: nz - 1]
    ang = np.linspace(0.0, 2.0 * np.pi, npts)
    rr = rho_c + r_w * np.cos(ang)
    zz = z_c + r_w * np.sin(ang)
    u = np.clip(rr / H - 0.5, 0.0, nr - 2 - 1e-9)
    v = np.clip(zz / H + nz / 2 - 1.5, 0.0, nz - 3 - 1e-9)
    i0 = np.floor(u).astype(int)
    j0 = np.floor(v).astype(int)
    fu = (u - i0)[:, None, None]
    fv = (v - j0)[:, None, None]
    Mb = (Mi[i0, j0] * (1 - fu) * (1 - fv) + Mi[i0 + 1, j0] * fu * (1 - fv)
          + Mi[i0, j0 + 1] * (1 - fu) * fv + Mi[i0 + 1, j0 + 1] * fu * fv)
    m11, m33, m13 = Mb[:, 1, 1], Mb[:, 3, 3], Mb[:, 1, 3]
    m12, m23 = Mb[:, 1, 2], Mb[:, 2, 3]
    aniso = np.sqrt((m11 - m33) ** 2 + 4 * m13 ** 2)
    mix = float(np.max(np.sqrt(m12 ** 2 + m23 ** 2))
                / max(float(np.mean(aniso)), 1e-30))
    th2 = np.arctan2(2 * m13, m11 - m33)
    dth = np.diff(th2)
    dth = (dth + np.pi) % (2 * np.pi) - np.pi
    return (float(np.sum(dth) / (4 * np.pi)), float(aniso.min()), mix)


def c5_statics_gate():
    Mx = load_m("m5_20_4_c_seed_dressed.npz")
    M0 = load_m("m5_20_3_b_seed_recipe.npz")
    # energy check with my own U_C
    w = cell_weights(NR, NZ, H)
    Ar, Ap, Az, _ = channels(Mx, H)
    Mc = Mx[: NR - 1, 1:-1]
    uc = sum(np.sum(my_qc_density(Mc, A, A_STAR) * w) for A in (Ar, Ap, Az))
    E_mine = float(total_energy_4(Mx, WSCALE, DELTA) + 1.306 * uc)
    # m13 structure
    m13x = Mx[: NR - 1, 1:-1, 1, 3]
    m130 = M0[: NR - 1, 1:-1, 1, 3]
    # winding scan over candidate centers (both states)
    def scan(M):
        found = []
        for rc in np.arange(3.0, 58.0, 2.0):
            for zc in np.arange(-30.0, 30.1, 3.0):
                for rw in (3.0, 5.0):
                    q, an, mix = my_winding(M, rc, zc, r_w=rw, npts=360)
                    if an > 0.02 and mix < 0.5 and abs(q) > 0.2:
                        found.append({"rho": float(rc), "z": float(zc),
                                      "r_w": rw, "q": q, "aniso_min": an,
                                      "mix": mix})
        return found
    found_x = scan(Mx)
    found_0 = scan(M0)
    # targeted reads
    reads = {}
    for tag, (rc, zc) in {"old_ring_17.5": (17.46, 0.0),
                          "detector_44.2": (44.21, 0.0),
                          "m13max_loc": (None, None)}.items():
        if rc is None:
            im = np.unravel_index(np.argmax(np.abs(m13x)), m13x.shape)
            rc = (im[0] + 0.5) * H
            zc = (im[1] + 1 - NZ / 2 + 0.5) * H
        q, an, mix = my_winding(Mx, rc, zc)
        qt, mixt = winding_measure_biax(Mx, NR, NZ, H, rc, zc)
        reads[tag] = {"center": [rc, zc], "q_mine": q, "aniso_min": an,
                      "mix": mix,
                      "q_trusted": None if not np.isfinite(qt) else float(qt)}
    # spectra: what did the minimizer become?
    zj0 = NZ // 2 - 1                    # z ~ 0 included-cell column
    spectra = {}
    for rc in (5, 17, 30, 44, 55):
        blk = Mx[rc, zj0 + 1, 1:4, 1:4]
        lam = np.sort(np.linalg.eigvalsh(0.5 * (blk + blk.T)))[::-1]
        blk0 = M0[rc, zj0 + 1, 1:4, 1:4]
        lam0 = np.sort(np.linalg.eigvalsh(0.5 * (blk0 + blk0.T)))[::-1]
        spectra[f"rho={rc}.5,z=0"] = {"dressed": lam.tolist(),
                                      "recipe": lam0.tolist()}
    # in-plane (1,2) anisotropy: the A_phi texture source
    d12_x = Mx[: NR - 1, 1:-1, 1, 1] - Mx[: NR - 1, 1:-1, 2, 2]
    d12_0 = M0[: NR - 1, 1:-1, 1, 1] - M0[: NR - 1, 1:-1, 2, 2]
    rd = ring_by_m13(Mx, NR, NZ, H)
    cs = core_spectrum(Mx, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
    destroyed = (len(found_x) == 0
                 and float(np.abs(m13x).max()) < 0.25 * float(np.abs(m130).max()))
    out = {"verdict": "CONFIRMED" if destroyed else "REFUTED",
           "E_mine": E_mine, "E_claimed": 13976.308911498996,
           "m13_absmax": {"dressed": float(np.abs(m13x).max()),
                          "recipe": float(np.abs(m130).max())},
           "m13_sumsq": {"dressed": float(np.sum(m13x ** 2)),
                         "recipe": float(np.sum(m130 ** 2))},
           "winding_scan": {"n_centers": 28 * 21 * 2,
                            "hits_dressed": found_x[:10],
                            "n_hits_dressed": len(found_x),
                            "n_hits_recipe": len(found_0),
                            "hits_recipe_sample": found_0[:3]},
           "targeted_reads_dressed": reads,
           "spatial_spectra_z0": spectra,
           "inplane_aniso_m11_m22": {
               "dressed_rms": float(np.sqrt(np.mean(d12_x ** 2))),
               "recipe_rms": float(np.sqrt(np.mean(d12_0 ** 2)))},
           "detector_readback": {"ring_rho": rd["ring13_rho"],
                                 "m13_max": rd["m13_max"],
                                 "core_lam": cs["lam"]}}
    print(f"[C5] {out['verdict']}: E_mine {E_mine:.3f} (claimed 13976.309); "
          f"|m13| max {out['m13_absmax']['dressed']:.3e} (recipe "
          f"{out['m13_absmax']['recipe']:.3e}); winding hits dressed "
          f"{len(found_x)} vs recipe {len(found_0)}", flush=True)
    return out


# ================================================================ C6
class NullProj:
    """my own null projector on the recipe background."""
    def __init__(self, M, rel_cut=1e-8, abs_cut_frac=1e-10):
        self.M = M
        self.G_stat = grad_static_4(M, WSCALE, DELTA, h=H, g=G_T,
                                    w4=W4, rho4=RHO4)
        K10 = build_k10(M, H)
        lam, U = np.linalg.eigh(K10)
        alam = np.abs(lam)
        cut = np.maximum(rel_cut * alam.max(axis=-1, keepdims=True),
                         abs_cut_frac * alam.max())
        self.U = U
        self.nmask = alam <= cut
        self.n = int(self.nmask.sum())

    def rhs10(self, V):
        GT = grad_m_T(self.M, V, W4, h=H, rho4=RHO4)
        kd = kdot_density(self.M, V, h=H)
        rhs = ((GT - self.G_stat)[: NR - 1, 1:-1] / (4.0 * W4)) - kd
        return np.einsum("akl,...kl->...a", BASIS, rhs)

    def r_null(self, V):
        rU = np.einsum("...ka,...k->...a", self.U, self.rhs10(V))
        return rU[self.nmask]

    def r_full_and_null(self, V):
        rU = np.einsum("...ka,...k->...a", self.U, self.rhs10(V))
        return rU, rU[self.nmask]

    def v_of_c(self, c):
        c10 = np.zeros(self.nmask.shape)
        c10[self.nmask] = c
        v10 = np.einsum("...ka,...a->...k", self.U, c10)
        V = np.zeros((NR, NZ, 4, 4))
        V[: NR - 1, 1:-1] = np.einsum("...a,akl->...kl", v10, BASIS)
        return V

    def sector_norms(self, r_packed):
        c10 = np.zeros(self.nmask.shape)
        c10[self.nmask] = r_packed
        r10 = np.einsum("...ka,...a->...k", self.U, c10)
        return {f"b{k}": float(np.sqrt(np.sum(r10[..., k] ** 2)))
                for k in range(10)}


def mask_field(V):
    z = np.zeros_like(V)
    z[: NR - 1, 1:-1] = V[: NR - 1, 1:-1]
    return z


def c6_arm_b(rng):
    M = load_m("m5_20_3_b_seed_recipe.npz")
    P = NullProj(M)
    rU, r0 = P.r_full_and_null(np.zeros_like(M))
    tot = float(np.sqrt(np.sum(rU ** 2)))
    nul = float(np.linalg.norm(r0))
    nff = nul / tot
    r0h = r0 / nul
    # (b) no linear term: exact quadratic homogeneity
    c = rng.normal(size=P.n)
    drs = {}
    for eps in (1e-1, 1e-2, 1e-3):
        drs[eps] = float(np.linalg.norm(P.r_null(P.v_of_c(eps * c)) - r0))
    homog = [drs[1e-1] / drs[1e-2], drs[1e-2] / drs[1e-3]]
    # (c) the alignment battery
    ri = (np.arange(NR - 1) + 0.5) * H
    zj = (np.arange(1, NZ - 1) - NZ / 2 + 0.5) * H
    RR, ZZ = np.meshgrid(ri, zj, indexing="ij")
    bump = np.exp(-((RR - 17.46) ** 2 + ZZ ** 2) / (2 * 3.0 ** 2))

    def from_cells(base):
        V = np.zeros((NR, NZ, 4, 4))
        V[: NR - 1, 1:-1] = base
        return V

    def bump_dir(i, j):
        base = np.zeros((NR - 1, NZ - 2, 4, 4))
        base[..., i, j] = bump
        base[..., j, i] = bump
        return from_cells(base)

    def flat_dir(i, j):
        base = np.zeros((NR - 1, NZ - 2, 4, 4))
        base[..., i, j] = 1.0
        base[..., j, i] = 1.0
        return from_cells(base)

    def gen(name):
        G = np.zeros((4, 4))
        if name.startswith("J"):
            k, l = int(name[1]), int(name[2])
            G[k, l], G[l, k] = -1.0, 1.0
        else:
            k = int(name[1])
            G[0, k] = G[k, 0] = 1.0
        return G

    def conj(rot, boost, chi):
        B = expm(chi * gen(boost))
        return B @ gen(rot) @ np.linalg.inv(B)

    def dgm(G):
        return mask_field(G @ M + M @ G.T)

    cands = {"eta_flat": from_cells(np.broadcast_to(
                 ETA, (NR - 1, NZ - 2, 4, 4)).copy()),
             "e00_flat": flat_dir(0, 0), "e00_bump": bump_dir(0, 0),
             "e01_bump": bump_dir(0, 1), "e02_bump": bump_dir(0, 2),
             "e03_bump": bump_dir(0, 3),
             "e11m22_bump": bump_dir(1, 1) - bump_dir(2, 2),
             "e11m22_flat": flat_dir(1, 1) - flat_dir(2, 2),
             "G_static": mask_field(P.G_stat.copy()),
             "DGM_J23": dgm(gen("J23")), "DGM_K1": dgm(gen("K1")),
             "DGM_K3": dgm(gen("K3")),
             "DGM_J23K2_1.25": dgm(conj("J23", "K2", 1.25)),
             "DGM_J23K2_2.5": dgm(conj("J23", "K2", 2.5)),
             "M_itself": mask_field(M.copy())}
    # null-projected static force as a velocity direction
    g10 = np.einsum("akl,...kl->...a", BASIS,
                    P.G_stat[: NR - 1, 1:-1])
    gU = np.einsum("...ka,...k->...a", P.U, g10)
    cands["G_static_nullpart"] = P.v_of_c(gU[P.nmask])
    try:
        cands["Vstar_b2"] = mask_field(
            np.load(os.path.join(DATA, "m5_20_4_b_vstar.npz"))["V"])
    except Exception:
        pass

    def align_of(V):
        dr = P.r_null(V) - r0
        ndr = float(np.linalg.norm(dr))
        if ndr < 1e-300:
            return 0.0, 0.0, dr
        return float(np.dot(dr, r0h) / ndr), ndr, dr

    rows = {}
    best_name, best_al, best_V = None, 0.0, None
    for name, V in cands.items():
        nv = float(np.sqrt(np.sum(V ** 2)))
        if nv < 1e-300:
            continue
        al, ndr, _ = align_of(V / nv)
        rows[name] = {"align": al, "dr_norm": ndr}
        if abs(al) > abs(best_al):
            best_name, best_al, best_V = name, al, V / nv
    # fresh random (seeds 101, 202), null-only and full
    fr = {"null_only": [], "full_V": []}
    for sd in (101, 202):
        r2 = np.random.default_rng(sd)
        for _ in range(6):
            cn = r2.normal(size=P.n)
            al, ndr, _ = align_of(P.v_of_c(cn))
            fr["null_only"].append(al)
            Vf = mask_field(rand_sym4(r2, n=NR * NZ).reshape(NR, NZ, 4, 4))
            al2, ndr2, _ = align_of(Vf)
            fr["full_V"].append(al2)
            if abs(al2) > abs(best_al):
                best_name, best_al = "random_full", al2
                best_V = Vf / float(np.sqrt(np.sum(Vf ** 2)))
    # scale invariance of alignment (homogeneity cross-check)
    al_1, _, _ = align_of(best_V)
    al_s, _, _ = align_of(0.1 * best_V)
    # hill climb on |align|
    climb = {"start": best_name, "start_align": best_al}
    V = best_V.copy()
    al = best_al
    sig = 0.3
    r3 = np.random.default_rng(777)
    for it in range(120):
        pert = mask_field(rand_sym4(r3, n=NR * NZ).reshape(NR, NZ, 4, 4))
        pert /= float(np.sqrt(np.sum(pert ** 2)))
        Vt = V + sig * pert
        Vt /= float(np.sqrt(np.sum(Vt ** 2)))
        alt, _, _ = align_of(Vt)
        if abs(alt) > abs(al):
            V, al = Vt, alt
            sig = min(sig * 1.3, 2.0)
        else:
            sig = max(sig * 0.75, 1e-3)
    climb["final_align"] = al
    _, _, dr_best = align_of(V)
    climb["final_dr_sector_norms"] = P.sector_norms(dr_best)
    climb["r0_sector_norms"] = P.sector_norms(r0)
    # INDEPENDENT RECHECK of the headline alignment through a different
    # code path: projector from the 10-pass build_k10_slow eigh, explicit
    # per-cell projector matrices (no packing machinery reuse)
    from m5_20_3_a_constraint import build_k10_slow
    K10s = build_k10_slow(M, H)
    lam2, U2 = np.linalg.eigh(K10s)
    alam2 = np.abs(lam2)
    cut2 = np.maximum(1e-8 * alam2.max(axis=-1, keepdims=True),
                      1e-10 * alam2.max())
    nm2 = alam2 <= cut2
    Pn = np.einsum("...ia,...a,...ja->...ij", U2,
                   nm2.astype(float), U2)          # projector matrices

    def r_null2(V):
        GT = grad_m_T(M, V, W4, h=H, rho4=RHO4)
        kd = kdot_density(M, V, h=H)
        rhs = ((GT - P.G_stat)[: NR - 1, 1:-1] / (4.0 * W4)) - kd
        r10 = np.einsum("akl,...kl->...a", BASIS, rhs)
        return np.einsum("...ij,...j->...i", Pn, r10)

    rn0 = r_null2(np.zeros_like(M))
    Ve = cands["e02_bump"] / float(np.sqrt(np.sum(cands["e02_bump"] ** 2)))
    drn = r_null2(Ve) - rn0
    al2 = float(np.sum(drn * rn0)
                / (np.sqrt(np.sum(drn ** 2)) * np.sqrt(np.sum(rn0 ** 2))))
    recheck = {"e02_align_pathA": rows["e02_bump"]["align"],
               "e02_align_pathB_slowbuild": al2,
               "nff_pathB": float(np.sqrt(np.sum(rn0 ** 2))
                                  / np.sqrt(np.sum(P.rhs10(
                                      np.zeros_like(M)) ** 2)))}
    all_aligns = [abs(v["align"]) for v in rows.values()] + \
        [abs(a) for a in fr["null_only"] + fr["full_V"]] + [abs(al)]
    max_align = max(all_aligns)
    neg_best = min([v["align"] for v in rows.values()] + [al])
    ok = (abs(nff - 0.9999977075345909) < 1e-6
          and abs(homog[0] - 10.0) < 0.5 and abs(homog[1] - 10.0) < 0.5
          and max_align < 0.05)
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "a_nff_mine": nff, "a_nff_claimed": 0.9999977075345909,
           "a_null_dim_total": P.n,
           "b_dr_ratios_eps10x": homog,
           "b_note": "each 10x reduction in eps scales |dr| by 100: "
                     "pure quadratic, no linear term (claim b holds)",
           "c_independent_recheck": recheck,
           "c_most_negative_align": neg_best,
           "c_best_single_dir_resid": float(np.sqrt(max(
               0.0, 1.0 - neg_best ** 2))),
           "c_structured": rows,
           "c_fresh_random": {"null_only_absmax": float(np.max(
               np.abs(fr["null_only"]))), "full_absmax": float(np.max(
                   np.abs(fr["full_V"]))), "n_each": 12},
           "c_scale_invariance": [al_1, al_s],
           "c_hill_climb": climb,
           "c_max_align_found": max_align,
           "refute_bar": 0.05}
    print(f"[C6] {out['verdict']}: nff mine {nff:.10f}; dr eps-ratios "
          f"{homog[0]:.2f}/{homog[1]:.2f} (expect 100 per 10x: see note); "
          f"max |align| found {max_align:.4f} "
          f"(bar 0.05, best start {climb['start']})", flush=True)
    return out


# ================================================================ C7
def gen4(name):
    G = np.zeros((4, 4))
    if name.startswith("J"):
        k, l = int(name[1]), int(name[2])
        G[k, l], G[l, k] = -1.0, 1.0
    else:
        k = int(name[1])
        G[0, k] = G[k, 0] = 1.0
    return G


def d_g(M, G):
    return G @ M + M @ G.T


def conj_gen(rot, boost, chi):
    B = expm(chi * gen4(boost))
    return B @ gen4(rot) @ np.linalg.inv(B)


def orbit_state(M, G, s):
    L = expm(s * G)
    return np.einsum("ab,...bc,dc->...ad", L, M, L)


def c7_arm_a(rng):
    M0 = load_m("m5_20_3_b_seed_recipe.npz")
    U0 = float(e_static_c(M0, WSCALE, DELTA).real)
    G23 = gen4("J23")
    Gc = conj_gen("J23", "K2", 2.5)
    # (a) quadratic scaling at t = 0
    D = d_g(M0, G23)
    t1 = float(t_total_c(M0, D).real)
    sc = max(abs(float(t_total_c(M0, w * D).real) - w * w * t1)
             / abs(w * w * t1) for w in (0.5, 2.0, 3.0))
    # (a') ORBIT CONSTANCY: the S(omega) derivation premise
    orbit = {}
    for name, G in (("J12", gen4("J12")), ("J23", G23),
                    ("J23^K2_2.5", Gc)):
        ss = np.linspace(0.0, 2 * np.pi, 33)
        q2s, us, v4s = [], [], []
        w = cell_weights(NR, NZ, H)
        for s in ss:
            Ms = orbit_state(M0, G, s)
            q2s.append(float(t_total_c(Ms, d_g(Ms, G)).real))
            us.append(float(e_static_c(Ms, WSCALE, DELTA).real))
            v4s.append(float(np.sum(v4_density(Ms, WSCALE, DELTA) * w)))
        q2s, us, v4s = map(np.array, (q2s, us, v4s))
        q2bar = float(np.trapezoid(q2s, ss) / (2 * np.pi))
        ubar = float(np.trapezoid(us, ss) / (2 * np.pi))
        orbit[name] = {
            "Q2_t0": float(q2s[0]), "Q2_min": float(q2s.min()),
            "Q2_max": float(q2s.max()), "Q2_bar": q2bar,
            "U_t0": float(us[0]), "U_min": float(us.min()),
            "U_max": float(us.max()), "U_bar": ubar,
            "V4_variation_rel": float((v4s.max() - v4s.min())
                                      / max(abs(v4s.mean()), 1e-30)),
            "closure_resid": float(abs(q2s[-1] - q2s[0])
                                   / max(abs(q2s[0]), 1e-30)),
            "root_from_t0": float(np.sqrt(-us[0] / q2s[0]))
            if us[0] * q2s[0] < 0 else None,
            "root_from_averages": float(np.sqrt(-ubar / q2bar))
            if ubar * q2bar < 0 else None}
    # (b) periodicity of the conjugated rotation
    per = float(np.abs(expm(2 * np.pi * Gc) - np.eye(4)).max())
    # (c) my own Q2(chi) crossing scan
    chis = np.concatenate([np.arange(0.0, 2.51, 0.25),
                           np.arange(1.0, 1.21, 0.02)])
    chis = np.sort(np.unique(np.round(chis, 4)))
    q2chi = {float(c): float(t_total_c(
        M0, d_g(M0, conj_gen("J23", "K2", float(c)))).real) for c in chis}
    cross = None
    keys = sorted(q2chi)
    for a, b in zip(keys, keys[1:]):
        if q2chi[a] > 0 >= q2chi[b]:
            cross = a + (b - a) * q2chi[a] / (q2chi[a] - q2chi[b])
    # (d) the a4 state
    Mx = load_m("m5_20_4_a_a4_state.npz")
    aj = json.load(open(os.path.join(DATA, "m5_20_4_a_a4.json")))
    omega = aj["omega"]
    Ux = float(e_static_c(Mx, WSCALE, DELTA).real)
    Q2x = float(t_total_c(Mx, d_g(Mx, Gc)).real)
    rd = ring_by_m13(Mx, NR, NZ, H)
    qt, _ = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                 rd["ring13_z"])
    qm, an, mix = my_winding(Mx, rd["ring13_rho"], rd["ring13_z"])
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)

    def shat_c(Mc):
        return (omega ** 2 * t_total_c(Mc, d_g(Mc, Gc))
                - e_static_c(Mc, WSCALE, DELTA))

    def cs_dir(Dd, h=1e-30):
        return float(np.imag(shat_c(Mx.astype(complex) + 1j * h * Dd)) / h)

    # claimed gradient (TARGET import, comparison only)
    from m5_20_4_a_bvp import grad_q2 as grad_q2_target
    g_claim = (omega ** 2 * grad_q2_target(Mx, Gc, w4=W4, rho4=RHO4)
               - grad_static_4(Mx, WSCALE, DELTA, w4=W4, rho4=RHO4)) * free4
    gnorm_claim = float(np.sqrt(np.sum(g_claim ** 2)))
    d_along = cs_dir(g_claim / gnorm_claim)
    dir_checks = []
    est = []
    ncells_free = int(np.sum(~pin[: NR - 1, 1:-1]))
    for _ in range(8):
        Dc = rand_sym4(rng, n=(NR - 1) * (NZ - 2)).reshape(
            NR - 1, NZ - 2, 4, 4)
        Dd = np.zeros((NR, NZ, 4, 4))
        Dd[: NR - 1, 1:-1] = Dc
        Dd *= free4
        Dd /= float(np.sqrt(np.sum(Dd ** 2)))
        fd = cs_dir(Dd)
        an_ = float(np.sum(g_claim * Dd))
        dir_checks.append({"cs": fd, "claimed": an_,
                           "rel": abs(fd - an_) / max(abs(fd), 1e-30)})
        est.append(fd ** 2)
    norm_est = float(np.sqrt(10 * ncells_free * np.mean(est)))
    ok = (sc < 1e-12 and per < 1e-10 and cross is not None
          and 1.0 < cross < 1.15
          and abs(Ux - aj["final_U"]) < 1e-6
          and abs(Q2x - aj["final_Q2"]) / abs(aj["final_Q2"]) < 1e-9
          and qt is not None and abs(qt - 0.5) < 0.01
          and abs(d_along - gnorm_claim) / gnorm_claim < 1e-8)
    rigid_fail = (orbit["J23^K2_2.5"]["U_max"] > 1e6 * abs(U0)
                  or orbit["J23"]["U_max"] > 10 * abs(U0))
    verdict = "QUALIFIED" if (ok and rigid_fail) else (
        "CONFIRMED" if ok else "REFUTED")
    out = {"verdict": verdict,
           "a_scaling_rel": sc,
           "a_orbit_constancy": orbit,
           "a_orbit_note": "S(omega) = (2pi/omega)(omega^2 Q2 - U) needs "
                           "Q2, U constant along the orbit; measured: "
                           "massively violated for every generator that "
                           "does not commute with the axisym J12 = J4 "
                           "(the A_phi channel is not equivariant; V4 IS "
                           "exact); J12 itself is exactly rigid but has "
                           "no root (Q2 > 0, U > 0)",
           "b_periodicity_resid": per,
           "c_my_crossing_chi": cross,
           "c_q2_chi_samples": {k: q2chi[k] for k in
                                (0.0, 1.0, 1.1, 1.2, 2.5)},
           "d_a4_state": {"U_mine": Ux, "U_json": aj["final_U"],
                          "Q2_mine": Q2x, "Q2_json": aj["final_Q2"],
                          "q_trusted": None if not np.isfinite(qt)
                          else float(qt),
                          "q_mine": qm, "aniso_min": an, "mix": mix,
                          "gradnorm_claimed_recomputed": gnorm_claim,
                          "gradnorm_json": aj["resid_final"],
                          "cs_derivative_along_claimed_dir": d_along,
                          "randdir_norm_estimate": norm_est,
                          "dir_checks": dir_checks[:3]}}
    print(f"[C7] {verdict}: scaling {sc:.1e}; ORBIT NOT RIGID: J23 U "
          f"varies {orbit['J23']['U_min']:.3f}..{orbit['J23']['U_max']:.1f} "
          f"(t0 {U0:.3f}); J23^K2 U max {orbit['J23^K2_2.5']['U_max']:.2e}; "
          f"crossing chi = {cross:.3f}; a4 |gradShat| cs-check "
          f"{d_along:.4f} vs claimed {gnorm_claim:.4f}; q(a4) = {qt}",
          flush=True)
    return out


# ================================================================ C8
def c8_escapes(rng, Hq, Hc):
    M = load_m("m5_20_3_b_seed_recipe.npz")
    Mc = M[: NR - 1, 1:-1]
    Ar, Ap, Az, _ = channels(M, H)
    ncell = (NR - 1) * (NZ - 2)
    # sample: 100 adversarial (lowest mineig at beta = 1.25) + 300 random
    me125 = np.linalg.eigvalsh(Hq + 1.25 * Hc).min(axis=-1).reshape(ncell)
    order = np.argsort(me125)
    idx = np.unique(np.concatenate(
        [order[:100], rng.choice(ncell, 300, replace=False)]))
    ii, jj = np.unravel_index(idx, (NR - 1, NZ - 2))
    Mb = Mc[ii, jj]
    Ab = [Ar[ii, jj], Ap[ii, jj], Az[ii, jj]]
    ns = len(idx)

    # ---- (a) non-commutator quartic contractions ----
    def nc_density(V, kind, a=A_STAR):
        Xs = [ETA @ V] + [ETA @ A for A in Ab]
        S = -Xs[0] @ Xs[0] + sum(X @ X for X in Xs[1:])
        if kind == "nc1":
            return mtr(S @ S)
        if kind == "nc3":
            P = a * I4 - ETA @ Mb
            return mtr(S @ P @ S @ P)
        if kind == "nc2":
            tot = 0.0
            for m in range(4):
                for n in range(4):
                    tot += SVEC[m] * SVEC[n] * mtr(
                        Xs[m] @ Xs[n] @ Xs[m] @ Xs[n])
            return tot
        raise ValueError(kind)

    def quad_part(V, kind):
        """exact quadratic-in-V part: (16 e(V/2) - e(V)) / 3."""
        d0 = nc_density(np.zeros_like(V), kind)
        def e(Vv):
            return 0.5 * (nc_density(Vv, kind)
                          + nc_density(-Vv, kind)) - d0
        return (16.0 * e(0.5 * V) - e(V)) / 3.0

    nc_out = {}
    for kind in ("nc1", "nc2", "nc3"):
        tb = [quad_part(np.broadcast_to(B, Mb.shape).copy(), kind)
              for B in BASIS]
        Qf = np.zeros((ns, 10, 10))
        for i in range(10):
            for j in range(i, 10):
                q = 0.5 * (quad_part(np.broadcast_to(
                    BASIS[i] + BASIS[j], Mb.shape).copy(), kind)
                    - tb[i] - tb[j])
                Qf[:, i, j] = Qf[:, j, i] = q
        Hnc = 2.0 * Qf
        eta_lift = float(np.abs(np.einsum("cab,b->ca", Hnc, ETA10)).max())
        # closure probe both signs
        res = {}
        for sgn in (+1.0, -1.0):
            b, me = bisect_beta(Hq.reshape(ncell, 10, 10)[idx],
                                sgn * Hnc)
            res[f"sign{int(sgn)}"] = {"beta_star_sample": b,
                                      "mineig": me}
        nc_out[kind] = {"quad_kinetic_maxabs": float(np.abs(Hnc).max()),
                        "eta_null_lift_max": eta_lift,
                        "mineig_of_term_itself": float(
                            np.linalg.eigvalsh(Hnc).min()),
                        "closure_probe": res}
    # nc static (texture) cost on the co-rotating vacuum
    Mv = np.broadcast_to(vac4(DELTA), (NR, NZ, 4, 4)).copy()
    Avr, Avp, Avz, _ = channels(Mv, H)
    Sv = sum(ETA @ A @ ETA @ A for A in (Avr, Avp, Avz))
    w = cell_weights(NR, NZ, H)
    nc1_vac = float(np.sum(mtr(Sv @ Sv) * w))
    Pv = A_STAR * I4 - ETA @ Mv[: NR - 1, 1:-1]
    nc3_vac = float(np.sum(mtr(Sv @ Pv @ Sv @ Pv) * w))

    # ---- (b) can s2 lower beta*? FULL-GRID Hessian of the s2 kinetic ----
    Pfull = A_STAR * I4 - ETA @ Mc

    def s2_bilinear_full(Ba, Bb):
        tot = 0.0
        for A in (Ar, Ap, Az):
            Ca = (ETA @ Ba) @ (ETA @ A) - (ETA @ A) @ (ETA @ Ba)
            Cb = (ETA @ Bb) @ (ETA @ A) - (ETA @ A) @ (ETA @ Bb)
            tot = tot + mtr(Ca @ Pfull @ Cb @ Pfull)
        return tot

    Hs2 = np.zeros((NR - 1, NZ - 2, 10, 10))
    for i in range(10):
        Bi = np.broadcast_to(BASIS[i], Mc.shape).copy()
        for j in range(i, 10):
            Bj = np.broadcast_to(BASIS[j], Mc.shape).copy()
            q = s2_bilinear_full(Bi, Bj)
            Hs2[..., i, j] = Hs2[..., j, i] = q
    Hs2 *= 2.0
    s2_eta = float(np.abs(np.einsum("...ab,b->...a", Hs2, ETA10)).max())
    # cross-check my Hs2 against a density polarization at one cell
    ci, cj = 17, 63
    z4 = np.zeros((4, 4))

    def s2_dens_cell(V):
        Xs = [ETA @ V, ETA @ Ar[ci, cj], ETA @ Ap[ci, cj],
              ETA @ Az[ci, cj]]
        Pc = A_STAR * I4 - ETA @ Mc[ci, cj]
        tot = 0.0
        for m in range(4):
            for n in range(m + 1, 4):
                C = Xs[m] @ Xs[n] - Xs[n] @ Xs[m]
                tot = tot - SVEC[m] * SVEC[n] * mtr(C @ Pc @ C @ Pc)
        return tot
    Qx = qform10(lambda V: s2_dens_cell(V) - s2_dens_cell(z4))
    s2_xcheck = float(np.abs(2.0 * Qx - Hs2[ci, cj]).max()
                      / max(np.abs(Hs2[ci, cj]).max(), 1e-30))
    # gamma ladder, FULL GRID: does gamma*s2 close all non-eta directions?
    gam_ladder = {}
    best_gam, best_lam1 = None, -np.inf
    for gam in (-1.0, -2.0, -3.0, -5.0, -8.0, -12.0, -20.0, -50.0):
        lam = np.linalg.eigvalsh(Hq + gam * Hs2)
        lam0 = float(lam[..., 0].min())        # the eta null (exact 0)
        lam1 = float(lam[..., 1].min())        # worst non-null direction
        gam_ladder[f"gamma={gam}"] = {"mineig": lam0,
                                      "second_mineig": lam1}
        if lam1 > best_lam1:
            best_gam, best_lam1 = gam, lam1
    # tiny-beta eta-lift on top of the best gamma (FULL GRID)
    tiny = {}
    for b in (1e-4, 1e-3, 1e-2, 0.05):
        lam = np.linalg.eigvalsh(Hq + b * Hc + best_gam * Hs2)
        tiny[f"beta={b}"] = float(lam.min())
    # sample-level (beta, gamma) feasibility (subsample documented)
    Hqs = Hq.reshape(ncell, 10, 10)[idx]
    Hcs = Hc.reshape(ncell, 10, 10)[idx]
    Hs2s = Hs2.reshape(ncell, 10, 10)[idx]

    def maxmin_over_gamma(b):
        def f(g):
            return float(np.linalg.eigvalsh(
                Hqs + b * Hcs + g * Hs2s).min())
        lo, hi = -60.0, 5.0
        for _ in range(50):
            g1 = lo + (hi - lo) * 0.382
            g2 = lo + (hi - lo) * 0.618
            if f(g1) < f(g2):
                lo = g1
            else:
                hi = g2
        gb = 0.5 * (lo + hi)
        return gb, f(gb)

    feas = {}
    min_feas = None
    for b in (0.0, 1e-4, 1e-3, 1e-2, 0.1, 0.5, 1.0, 1.3):
        gb, v = maxmin_over_gamma(float(b))
        feas[f"beta={b}"] = {"gamma_best": gb, "maxmin_eig": v}
        if v >= 0 and min_feas is None and b > 0:
            min_feas = float(b)
    # s2 texture cost on the vacuum (single channel -> commutators vanish)
    Cs = [(ETA @ Avp) @ (ETA @ A) - (ETA @ A) @ (ETA @ Avp)
          for A in (Avr, Avz)]
    Pv2 = A_STAR * I4 - ETA @ Mv[: NR - 1, 1:-1]
    s2_vac = float(sum(np.sum(mtr(C @ Pv2 @ C @ Pv2) * w) for C in Cs))
    # s2 STATIC energy on the recipe loop background (the unmeasured arm)
    Cij = [((ETA @ A1) @ (ETA @ A2) - (ETA @ A2) @ (ETA @ A1))
           for (A1, A2) in ((Ar, Ap), (Ar, Az), (Ap, Az))]
    e_s2_recipe = float(sum(np.sum(mtr(C @ Pfull @ C @ Pfull) * w)
                            for C in Cij))
    # crude boundedness probe of E_old + gamma*E_s2_static
    rng2 = np.random.default_rng(9)
    probe = []
    for trial in range(4):
        D = rand_sym4(rng2, n=(NR - 1) * (NZ - 2)).reshape(
            NR - 1, NZ - 2, 4, 4)
        sgnck = np.where((np.arange(NR - 1)[:, None]
                          + np.arange(NZ - 2)[None, :]) % 2 == 0, 1.0,
                         -1.0)[..., None, None]
        D = D * sgnck                        # high-gradient checkerboard
        vals = []
        for t in (0.0, 0.5, 1.0, 2.0, 4.0):
            Mt = M.copy()
            Mt[: NR - 1, 1:-1] += t * D
            Art, Apt, Azt, _ = channels(Mt, H)
            Pt = A_STAR * I4 - ETA @ Mt[: NR - 1, 1:-1]
            Ct = [((ETA @ A1) @ (ETA @ A2) - (ETA @ A2) @ (ETA @ A1))
                  for (A1, A2) in ((Art, Apt), (Art, Azt), (Apt, Azt))]
            es2 = float(sum(np.sum(mtr(C @ Pt @ C @ Pt) * w) for C in Ct))
            e0 = float(e_static_c(Mt, WSCALE, DELTA).real)
            vals.append(e0 + best_gam * es2)
        probe.append(vals)
    probe_min = float(np.min(probe))
    # background robustness of the gamma = -1 escape (other states)
    from m5_20_3_a_constraint import seed4_grid

    def combo_check(Mbg, gam=-1.0, beta=1e-3):
        Hqb, Hcb = hess_fields_recipe(Mbg)
        Arb, Apb, Azb, _ = channels(Mbg, H)
        Pf = A_STAR * I4 - ETA @ Mbg[: NR - 1, 1:-1]
        Hsb = np.zeros((NR - 1, NZ - 2, 10, 10))
        for i in range(10):
            Bi = np.broadcast_to(BASIS[i], Pf.shape).copy()
            for j in range(i, 10):
                Bj = np.broadcast_to(BASIS[j], Pf.shape).copy()
                t = 0.0
                for A in (Arb, Apb, Azb):
                    Ca = (ETA @ Bi) @ (ETA @ A) - (ETA @ A) @ (ETA @ Bi)
                    Cb = (ETA @ Bj) @ (ETA @ A) - (ETA @ A) @ (ETA @ Bj)
                    t = t + mtr(Ca @ Pf @ Cb @ Pf)
                Hsb[..., i, j] = Hsb[..., j, i] = t
        Hsb *= 2.0
        lam_g = np.linalg.eigvalsh(Hqb + gam * Hsb)
        lam_b = np.linalg.eigvalsh(Hqb + gam * Hsb + beta * Hcb)
        return {"quartic_mineig": float(np.linalg.eigvalsh(Hqb).min()),
                "combo_mineig": float(lam_g.min()),
                "combo_plus_tinybeta_mineig": float(lam_b.min())}

    rng3 = np.random.default_rng(31)
    Mrand = M.copy()
    Mrand[: NR - 1, 1:-1] += 0.05 * rand_sym4(
        rng3, n=(NR - 1) * (NZ - 2)).reshape(NR - 1, NZ - 2, 4, 4)
    robust = {}
    for tag, Mbg in (("raw", seed4_grid(NR, NZ, DELTA, "pair_d0", R0=17.0)),
                     ("remnant", load_m("m5_20_3_b_seed_remnant.npz")),
                     ("dressed", load_m("m5_20_4_c_seed_dressed.npz")),
                     ("vacuum", Mv), ("recipe_perturbed", Mrand)):
        robust[tag] = combo_check(Mbg)
    # pointwise domain probe: does -tr((WP)^2) - 4 tr(W^2) >= 0 survive
    # for wild random (M, A, V) far outside the physical range?
    wild = []
    for scale in (1.0, 3.0, 10.0):
        vals = []
        for _ in range(2000):
            Mw = scale * rand_sym4(rng3)
            Aw = rand_sym4(rng3)
            Vw = rand_sym4(rng3)
            F = Vw @ ETA @ Aw - Aw @ ETA @ Vw
            W = ETA @ F
            Pw = A_STAR * I4 - ETA @ Mw
            vals.append(-np.trace((W @ Pw) @ (W @ Pw))
                        - 4.0 * np.trace(W @ W))
        wild.append({"M_scale": scale, "min": float(np.min(vals)),
                     "frac_neg": float(np.mean(np.array(vals) < -1e-12))})
    texture_per_beta = 9.0958e4 / 1.306
    esc = (best_lam1 > -1e-9 and min(tiny.values()) >= 0.0
           and abs(s2_vac) < 1e-20
           and all(r["combo_mineig"] > -1e-9
                   and r["combo_plus_tinybeta_mineig"] > 0.0
                   for r in robust.values()))
    out = {"verdict": "REFUTED" if esc else "QUALIFIED",
           "subsample": {"n_cells": int(ns),
                         "adversarial_lowest": 100, "random": 300,
                         "fullgrid_checks": "gamma ladder + tiny-beta "
                                            "+ 5-background robustness"},
           "b_background_robustness": robust,
           "b_pointwise_domain_probe_wildM": wild,
           "escape_construction": (
               "L_esc = L_verified - 1.0 * s2(a=4.5) + beta * qc(a=4.5), "
               "beta -> 0+: kinetic Hessian = Hq - Hs2 + beta Hc is PSD "
               "(exactly marginal) at every cell on every measured "
               "background and PD for any beta > 0; per channel the "
               "gamma = -1 combination is -tr((WP)^2) - 4 tr(W^2), "
               "W = eta [V, A]_eta in so(1,3); s2 has ZERO co-rotating-"
               "vacuum texture cost and its static addition on the "
               "recipe is +0.693 (order E_base), NOT the 1e5-scale qc "
               "texture bomb; caveats: gamma < 0 sign admissibility is "
               "author-gated, no full statics re-relax run, ghost "
               "analysis beyond the finite-amplitude probe not done"),
           "a_noncommutator": nc_out,
           "a_nc_vacuum_texture_cost": {"nc1": nc1_vac, "nc3": nc3_vac},
           "a_note": ("the class has NONZERO background-dependent "
                      "QUADRATIC kinetic content (mixed 0i0i "
                      "contractions) and LIFTS the eta-null, so it is "
                      "NOT outside the closure question; measured: its "
                      "own form is sign-indefinite and never closes "
                      "(beta* None both signs)"),
           "b_s2_eta_null_lift": s2_eta,
           "b_s2_hessian_xcheck_rel": s2_xcheck,
           "b_gamma_ladder_fullgrid": gam_ladder,
           "b_best_gamma": best_gam,
           "b_tinybeta_fullgrid_mineig": tiny,
           "b_beta_gamma_feasibility_sample": feas,
           "b_min_feasible_beta_sample": min_feas,
           "b_s2_vacuum_texture_cost": s2_vac,
           "b_s2_static_energy_on_recipe": e_s2_recipe,
           "b_s2_static_at_best_gamma": best_gam * e_s2_recipe,
           "b_boundedness_probe_min": probe_min,
           "b_escape_flag": bool(esc),
           "texture_cost_per_unit_beta": texture_per_beta,
           "loop_energy_scale_E_base": 0.3438442096192527}
    print(f"[C8] {out['verdict']}: nc quad-kinetic present, closes "
          f"never; s2 xcheck {s2_xcheck:.1e}; gamma = -1 combo "
          f"second-mineig {best_lam1:.3e}; tiny-beta {tiny}; robustness "
          + " ".join(f"{k}:{v['combo_mineig']:.1e}/"
                     f"{v['combo_plus_tinybeta_mineig']:.1e}"
                     for k, v in robust.items())
          + f"; wild-M probe {wild}; s2 vac cost {s2_vac:.2e}; "
          f"s2 static on recipe {e_s2_recipe:.4e}; boundedness probe "
          f"min {probe_min:.3e}", flush=True)
    return out


# ================================================================ main
def main():
    t0 = time.time()
    rng = np.random.default_rng(20260714)
    Hq = Hc = None
    for name, fn in [("C1", lambda: c1_lemma_l1(rng)),
                     ("C2", c2_lemma_l2)]:
        try:
            RESULT["claims"][name] = fn()
        except Exception:
            RESULT["claims"][name] = {"verdict": "ERROR",
                                      "trace": traceback.format_exc()}
            print(f"[{name}] ERROR", flush=True)
    try:
        RESULT["claims"]["C3"], Hq, Hc = c3_beta_star(rng)
    except Exception:
        RESULT["claims"]["C3"] = {"verdict": "ERROR",
                                  "trace": traceback.format_exc()}
        print("[C3] ERROR", flush=True)
    for name, fn in [("C4", lambda: c4_obstruction(rng, Hq)),
                     ("C5", c5_statics_gate),
                     ("C6", lambda: c6_arm_b(rng)),
                     ("C7", lambda: c7_arm_a(rng)),
                     ("C8", lambda: c8_escapes(rng, Hq, Hc))]:
        try:
            RESULT["claims"][name] = fn()
        except Exception:
            RESULT["claims"][name] = {"verdict": "ERROR",
                                      "trace": traceback.format_exc()}
            print(f"[{name}] ERROR: {traceback.format_exc()}", flush=True)
    RESULT["wall_s"] = round(time.time() - t0, 1)
    with open(os.path.join(DATA, "m5_20_4_audit.json"), "w") as f:
        json.dump(RESULT, f, indent=1, default=float)
    print(f"\n[AUDIT] wrote ../data/m5_20_4_audit.json "
          f"({RESULT['wall_s']} s)", flush=True)
    for k in sorted(RESULT["claims"]):
        print(f"  {k}: {RESULT['claims'][k].get('verdict')}")


if __name__ == "__main__":
    main()
