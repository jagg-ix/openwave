"""M5.20.4 arm C: the sanctioned-term kinetic fix.

QUESTION (pre-registered, tasks/m5_20_4_task_details.md): does a
Lorentz-invariant gradient term in the Q13-sanctioned class ("different
Lorentz-invariant Skyrme-like term ... extended to 4x4 tensor") close
the measured indefiniteness of the true-L kinetic form K(M) on the
measured backgrounds, while the statics anchors stay green?

ENUMERATION (invariants of order <= 4 in derivatives, eta-contracted).
Building blocks: X_mu = eta d_mu M, N = eta M; under a Lorentz map
Lambda both transform by the SAME similarity (Lambda^T)^-1 (.) Lambda^T,
so any trace of products of {X_mu, N} with all mu-indices contracted by
eta^munu is invariant (machine-checked, gate CL1). Cayley-Hamilton caps
dressings at cubic polynomials in N. The candidate families:

    qa  bare quadratic      -eta^munu tr(X_mu X_nu)
    qb  one-sided dressing  -eta^munu tr(X_mu X_nu P)
    qd  trace split         -eta^munu tr(X_mu P) tr(X_nu P)
    qc  two-sided dressing  -eta^munu tr(X_mu P X_nu P),  P = a I - N
    s1  bare Skyrme         -SUM_{mu<nu} s_mu s_nu tr(C_munu C_munu),
                            C_munu = [X_mu, X_nu]  (= eta F_munu: the
                            verified L's own class)
    s2  dressed Skyrme      -SUM_{mu<nu} s_mu s_nu tr(C P C P)

STRUCTURAL LEMMAS (derived, then machine-verified in gate CL2):
    L1  the WHOLE commutator (Skyrme) class keeps the exact eta-null:
        V ~ eta => X_0 = eta.eta = I => C_0i = [I, X_i] = 0, so no
        Skyrme-like term, dressed or not, can lift the primary
        constraint; only non-commutator terms can.
    L2  at a diagonal vacuum (eta M = diag(g, 1, delta, 0)) the kinetic
        form of a two-sided dressing is
            T(V) = SUM_ij p_i p_j eta_ii eta_jj V_ij^2 ,
        so positive-definiteness needs p(time-branch) OPPOSITE in sign
        to p(every spatial branch): satisfied by P = a I - N with
        a strictly between the g-eigenvalue and the largest spatial
        eigenvalue (window a in (1, g), measured in the census).
    L3  one-sided dressings give coefficients (p_i + p_j)/2: the (0,0)
        entry needs p_0 > 0 while the boost entries need p_0 + p_k < 0
        with p_k p_l > 0 spatial: unsatisfiable => qb can NEVER close.
        Trace splits (qd) have rank <= 4 => never PD on 10 dims. The
        bare qa (all p equal) is the known boost-indefinite term.

THE CANDIDATE (the only closing family): with P = a I - eta M,

    L_C = -beta eta^munu tr(eta d_mu M P eta d_nu M P),   beta > 0,
    T_C = +beta tr(eta Mdot P eta Mdot P)      (positive definite for
                                                a in the window: L2)
    U_C = +beta SUM_i tr(eta A_i P eta A_i P)  (SAME form in A_i =>
                                                positive gradient
                                                stiffness: no statics
                                                destabilization)

EL PIECES (derived; each gated complex-step, gates CG1-CG4; the
identity eta P^T = P eta makes every piece manifestly symmetric):
    pi_C     = 2 beta (P eta) V (P eta)                     (dT/dV)
    gradM_TC = -2 beta  eta V P eta V eta                   (dT/dM)
    kdot_C   = -2 beta (eta V eta V P eta + P eta V eta V eta)
    dU/dA_i  = 2 beta (P eta) A_i (P eta)   (stencil-scattered)
    dU/dM|P  = -2 beta SUM_i eta A_i P eta A_i eta          (pointwise)

Run:  python m5_20_4_c_terms.py gates|census|statics|evolve [tag]
Out:  ../data/m5_20_4_c_<phase>.json
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
                           grad_static_4, total_energy_4, vac4)
from m5_20_3_a_constraint import (BASIS, BMAT, ETA10, _cs_dir,     # noqa: E402
                                  build_k10, e_static_c, seed4_grid,
                                  t_density, t_total_c, grad_m_T,
                                  kdot_density)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NR, NZ, H = 64, 128, 1.0
DELTA = 0.3
R0 = 17.0
W4 = cell_weights(NR, NZ, H)[..., None, None]
RHO4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
I4 = np.eye(4)
A_STAR = 4.5            # default dressing root, mid-window (1, g)
SVEC = (-1.0, 1.0, 1.0, 1.0)


def mtr(A):
    return np.einsum("...ii->...", A)


def mtr2(A, B):
    return np.einsum("...ij,...ji->...", A, B)


# ---------------- the candidate term (grid level) ----------------
def p_of(Mc, a):
    return a * I4 - ETA @ Mc


def t_add_density(Mc, Vc, a):
    """+tr(eta V P eta V P) per cell (beta = 1; complex-safe)."""
    X = ETA @ Vc
    P = p_of(Mc, a)
    return mtr(X @ P @ X @ P)


def u_add_density(Mnp, a, h=H):
    """+SUM_i tr(eta A_i P eta A_i P) per cell (beta = 1)."""
    nr = Mnp.shape[0]
    Arho, Aphi, Az, _ = channels(Mnp, h)
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    tot = 0.0
    for A in (Arho, Aphi, Az):
        X = ETA @ A
        tot = tot + mtr(X @ P @ X @ P)
    return tot


def e_add_static_c(Mnp, beta, a, h=H):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return beta * np.sum(u_add_density(Mnp, a, h) * w)


def t_add_total_c(Mnp, Vnp, beta, a, h=H):
    nr = Mnp.shape[0]
    w = cell_weights(nr, Mnp.shape[1], h)
    return beta * np.sum(
        t_add_density(Mnp[: nr - 1, 1:-1], Vnp[: nr - 1, 1:-1], a) * w)


def pi_add(Mc, Vc, beta, a):
    PE = p_of(Mc, a) @ ETA
    return 2.0 * beta * (PE @ Vc @ PE)


def grad_m_t_add(Mc, Vc, beta, a):
    P = p_of(Mc, a)
    return -2.0 * beta * (ETA @ Vc @ P @ ETA @ Vc @ ETA)


def kdot_add(Mc, Vc, beta, a):
    P = p_of(Mc, a)
    Z = ETA @ Vc @ ETA @ Vc @ P @ ETA
    return -2.0 * beta * (Z + np.swapaxes(Z, -1, -2))


def k10_add(Mc, beta, a):
    """the term's 10x10 kinetic form: pi_C = k_add[V] = 2b PE V PE."""
    PE = p_of(Mc, a) @ ETA
    Kop = 2.0 * beta * np.einsum("...ia,...bj->...ijab", PE, PE)
    Kop = Kop.reshape(Kop.shape[:-4] + (16, 16))
    K10 = np.einsum("ai,...ij,bj->...ab", BMAT, Kop, BMAT, optimize=True)
    return 0.5 * (K10 + np.swapaxes(K10, -1, -2))


def g_u_add(Mnp, beta, a, w4=None, rho4=None, h=H):
    """dU_C/dM, stencil-scattered exactly as grad_m_T + the pointwise
    P-piece; w-folded (grad_static_4 conventions)."""
    nr = Mnp.shape[0]
    if w4 is None:
        w4 = cell_weights(nr, Mnp.shape[1], h)[..., None, None]
    Arho, Aphi, Az, r4 = channels(Mnp, h)
    if rho4 is None:
        rho4 = r4
    P = p_of(Mnp[: nr - 1, 1:-1], a)
    PE = P @ ETA
    k = 2.0 * beta * w4
    Grho = k * (PE @ Arho @ PE)
    Gphi = k * (PE @ Aphi @ PE)
    Gz = k * (PE @ Az @ PE)
    inv2h = 1.0 / (2.0 * h)
    G = np.zeros_like(Mnp)
    G[1:, 1:-1] += Grho * inv2h
    G[: nr - 2, 1:-1] -= Grho[1:] * inv2h
    G[0, 1:-1] -= (MIR * Grho[0]) * inv2h
    G[: nr - 1, 2:] += Gz * inv2h
    G[: nr - 1, :-2] -= Gz * inv2h
    Gphi_r = Gphi / rho4
    Jb = np.broadcast_to(J4, Gphi_r.shape)
    G[: nr - 1, 1:-1] += -(Jb @ Gphi_r - Gphi_r @ Jb)
    pt = 0.0
    for A in (Arho, Aphi, Az):
        pt = pt + ETA @ A @ P @ ETA @ A @ ETA
    G[: nr - 1, 1:-1] += w4 * (-2.0 * beta) * pt
    return G


# ---------------- pointwise densities (the enumeration) ----------------
def density_point(M, Gs, kind, a=A_STAR):
    """candidate Lagrangian densities at a point; Gs = [G_0..G_3]
    (values of d_mu M); all invariants of {X_mu = eta G_mu, N = eta M}."""
    N = ETA @ M
    P = a * I4 - N
    Xs = [ETA @ G for G in Gs]
    if kind == "qa":
        return -sum(s * mtr2(X, X) for s, X in zip(SVEC, Xs))
    if kind == "qb":
        return -sum(s * mtr(X @ X @ P) for s, X in zip(SVEC, Xs))
    if kind == "qd":
        return -sum(s * mtr(X @ P) ** 2 for s, X in zip(SVEC, Xs))
    if kind == "qc":
        return -sum(s * mtr(X @ P @ X @ P) for s, X in zip(SVEC, Xs))
    if kind in ("s1", "s2"):
        Q = I4 if kind == "s1" else P
        tot = 0.0
        for mu in range(4):
            for nu in range(mu + 1, 4):
                C = Xs[mu] @ Xs[nu] - Xs[nu] @ Xs[mu]
                tot = tot - SVEC[mu] * SVEC[nu] * mtr(C @ Q @ C @ Q)
        return tot
    raise ValueError(kind)


KINDS = ("qa", "qb", "qd", "qc", "s1", "s2")


def kin_form_point(M, Alist, kind, a=A_STAR):
    """10x10 kinetic quadratic form Q (T = V.Q.V) of a candidate at a
    point with spatial background Alist = [A_1, A_2, A_3], via
    polarization of the density's kinetic sector."""
    zero = np.zeros((4, 4))

    def tkin(V):
        full = density_point(M, [V] + list(Alist), kind, a)
        stat = density_point(M, [zero] + list(Alist), kind, a)
        return full - stat

    Q = np.zeros((10, 10))
    tb = [tkin(B) for B in BASIS]
    for i in range(10):
        for j in range(i, 10):
            Q[i, j] = Q[j, i] = 0.5 * (tkin(BASIS[i] + BASIS[j])
                                       - tb[i] - tb[j])
    return Q


# ---------------- gates ----------------
def _rand_lambda(rng):
    """random proper Lorentz map: boost (rapidity ~0.7, random axis)
    composed with a random spatial rotation."""
    nvec = rng.normal(size=3)
    nvec /= np.linalg.norm(nvec)
    phi = 0.7 * rng.uniform(0.5, 1.5)
    B = np.eye(4)
    ch, sh = np.cosh(phi), np.sinh(phi)
    B[0, 0] = ch
    for k in range(3):
        B[0, k + 1] = B[k + 1, 0] = -sh * nvec[k]
        for l in range(3):
            B[k + 1, l + 1] = (k == l) + (ch - 1.0) * nvec[k] * nvec[l]
    A = rng.normal(size=(3, 3))
    Qr, _ = np.linalg.qr(A)
    if np.linalg.det(Qr) < 0:
        Qr[:, 0] *= -1
    R = np.eye(4)
    R[1:, 1:] = Qr
    return B @ R


def gate_cl1(n=6, seed=0):
    """CL1: Lorentz invariance of every candidate density (pointwise)."""
    rng = np.random.default_rng(seed)
    worst = {k: 0.0 for k in KINDS}
    for _ in range(n):
        M = rng.normal(size=(4, 4))
        M = 0.5 * (M + M.T)
        Gs = [0.5 * (g + g.T) for g in rng.normal(size=(4, 4, 4))]
        Lam = _rand_lambda(rng)
        Li = np.linalg.inv(Lam)
        Mp = Lam @ M @ Lam.T
        Gp = [sum(Li[nu, mu] * (Lam @ Gs[nu] @ Lam.T) for nu in range(4))
              for mu in range(4)]
        for k in KINDS:
            d0 = density_point(M, Gs, k)
            d1 = density_point(Mp, Gp, k)
            rel = abs(d1 - d0) / max(abs(d0), 1e-12)
            worst[k] = max(worst[k], rel)
    ok = all(v < 1e-9 for v in worst.values())
    print(f"[CL1] Lorentz invariance worst rel: "
          + " ".join(f"{k}={v:.1e}" for k, v in worst.items())
          + f"  -> {'PASS' if ok else 'FAIL'}", flush=True)
    return {"worst_rel": worst, "pass": bool(ok)}


def gate_cl2(seed=1):
    """CL2: the structural lemmas, machine-verified."""
    rng = np.random.default_rng(seed)
    M = 0.5 * (lambda X: X + X.T)(rng.normal(size=(4, 4)))
    Alist = [0.5 * (g + g.T) for g in rng.normal(size=(3, 4, 4))]
    # L1: eta is null for the whole commutator class (dressed included)
    l1 = []
    for k in ("s1", "s2"):
        Q = kin_form_point(M, Alist, k)
        l1.append(float(np.abs(Q @ ETA10).max()))
    # qc lifts the null
    Qqc = kin_form_point(M, Alist, "qc")
    lift = float(np.abs(Qqc @ ETA10).max())
    # L2/L3 at the vacuum: kinetic spectra (A = 0)
    Mv = vac4(DELTA)
    zeros = [np.zeros((4, 4))] * 3
    spectra = {}
    for k in ("qa", "qb", "qd", "qc"):
        Q = kin_form_point(Mv, zeros, k)
        spectra[k] = sorted(np.linalg.eigvalsh(Q).tolist())
    ok = (max(l1) < 1e-10 and lift > 1e-6
          and spectra["qc"][0] > 0.0
          and spectra["qa"][0] < 0.0 and spectra["qb"][0] < 0.0
          and spectra["qd"][0] <= 1e-12)
    print(f"[CL2] eta-null in Skyrme class max|Q.eta| = {max(l1):.2e} "
          f"(L1); qc lifts it (|Q.eta| = {lift:.2e}); vacuum min-eigs: "
          + " ".join(f"{k}={spectra[k][0]:+.3f}" for k in spectra)
          + f"  -> {'PASS' if ok else 'FAIL'}", flush=True)
    return {"skyrme_null_max": max(l1), "qc_lift": lift,
            "vac_spectra": spectra, "pass": bool(ok)}


def gate_cg(seed=2):
    """CG1-CG4: complex-step gates of every derived EL piece + the
    einsum K10 build vs density polarization."""
    rng = np.random.default_rng(seed)
    M0 = seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    M0 = M0 + 0.05 * _rand_sym(M0.shape, rng)
    V0 = 0.1 * _rand_sym(M0.shape, rng)
    D = _rand_sym(M0.shape, rng)
    beta, a = 0.37, A_STAR
    Mc = M0[: NR - 1, 1:-1]
    Vc = V0[: NR - 1, 1:-1]
    Dc = D[: NR - 1, 1:-1]
    out = {}
    # CG1: pi_add == cs dT/dV
    lhs = float(np.sum(pi_add(Mc, Vc, beta, a) * W4 * Dc))
    rhs = _cs_dir(lambda V: t_add_total_c(M0, V, beta, a), V0, D)
    out["cg1_pi"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # CG2: gradM_T_add == cs dT/dM
    lhs = float(np.sum(grad_m_t_add(Mc, Vc, beta, a) * W4 * Dc))
    rhs = _cs_dir(lambda MM: t_add_total_c(MM, V0, beta, a), M0, D)
    out["cg2_gradm_t"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # CG3: g_u_add == cs dU/dM (stencils + pointwise + phi channel)
    lhs = float(np.sum(g_u_add(M0, beta, a, w4=W4, rho4=RHO4) * D))
    rhs = _cs_dir(lambda MM: e_add_static_c(MM, beta, a), M0, D)
    out["cg3_g_u"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # CG4: kdot_add == cs_M(pi_add) along Mdot = V
    T = _rand_sym(M0.shape, rng)[: NR - 1, 1:-1]
    lhs = float(np.sum(kdot_add(Mc, Vc, beta, a) * T))
    rhs = _cs_dir(lambda MM: np.sum(
        pi_add(MM[: NR - 1, 1:-1], Vc, beta, a) * T), M0, V0)
    out["cg4_kdot"] = abs(lhs - rhs) / max(abs(rhs), 1e-12)
    # CG5: k10_add einsum == density polarization (per cell, sampled)
    K10e = k10_add(Mc, 1.0, a)
    idx = [(5, 30), (30, 60), (55, 100)]
    worst = 0.0
    for (ir, iz) in idx:
        Mp = Mc[ir, iz]
        Q = np.zeros((10, 10))
        tb = [t_add_density(Mp, B, a) for B in BASIS]
        for i in range(10):
            for j in range(i, 10):
                Q[i, j] = Q[j, i] = 0.5 * (
                    t_add_density(Mp, BASIS[i] + BASIS[j], a)
                    - tb[i] - tb[j])
        rel = np.abs(K10e[ir, iz] - 2.0 * Q).max() / max(
            np.abs(Q).max() * 2.0, 1e-12)
        worst = max(worst, rel)
    out["cg5_k10_build"] = worst
    ok = all(v < 1e-8 for v in out.values())
    print("[CG] complex-step gates: "
          + " ".join(f"{k}={v:.1e}" for k, v in out.items())
          + f"  -> {'PASS' if ok else 'FAIL'}", flush=True)
    out["pass"] = bool(ok)
    return out


def _rand_sym(shape, rng):
    D = rng.normal(size=shape)
    D = 0.5 * (D + np.swapaxes(D, -1, -2))
    out = np.zeros(shape)
    out[: shape[0] - 1, 1:-1] = D[: shape[0] - 1, 1:-1]
    return out


def phase_gates():
    res = {"cl1": gate_cl1(), "cl2": gate_cl2(), "cg": gate_cg()}
    res["all_pass"] = all(res[k]["pass"] for k in res)
    with open(os.path.join(DATA, "m5_20_4_c_gates.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    print(f"[GATES] {'ALL PASS' if res['all_pass'] else 'FAILURES'}",
          flush=True)
    return res


# ---------------- census ----------------
def load_seed(kind):
    if kind == "raw":
        return seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    fn = {"recipe": "m5_20_3_b_seed_recipe.npz",
          "remnant": "m5_20_3_b_seed_remnant.npz"}[kind]
    return np.load(os.path.join(DATA, fn))["M"]


def a_window_vacuum():
    """measured a-window where qc closes at the vacuum (expect (1, g))."""
    Mv = vac4(DELTA)
    zeros = [np.zeros((4, 4))] * 3
    scan = []
    for a in np.linspace(0.25, 9.75, 39):
        Q = kin_form_point(Mv, zeros, "qc", a=float(a))
        scan.append((float(a), float(np.linalg.eigvalsh(Q).min())))
    pos = [a for a, e in scan if e > 0]
    return {"scan": scan, "window": [min(pos), max(pos)] if pos else None}


def beta_star(K10q4, K10c, hi0=1.0):
    """smallest beta with min-eig(K10q4 + beta K10c) >= 0 over cells
    (monotone: K10c > 0)."""
    def mineig(b):
        return float(np.linalg.eigvalsh(K10q4 + b * K10c).min())
    hi = hi0
    tries = 0
    while mineig(hi) < 0 and tries < 40:
        hi *= 2.0
        tries += 1
    if mineig(hi) < 0:
        return None, mineig(hi)
    lo = 0.0
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if mineig(mid) >= 0:
            hi = mid
        else:
            lo = mid
    return hi, mineig(hi)


def phase_census(a=A_STAR):
    out = {"a": a, "a_window_vacuum": a_window_vacuum()}
    print(f"[CENSUS] vacuum qc window a in {out['a_window_vacuum']['window']}",
          flush=True)
    for tag in ("recipe", "raw", "remnant"):
        M = load_seed(tag)
        Mc = M[: NR - 1, 1:-1]
        K10q4 = 4.0 * build_k10(M, H)
        lamq = np.linalg.eigvalsh(K10q4)
        K10c = k10_add(Mc, 1.0, a)
        lamc = np.linalg.eigvalsh(K10c)
        bstar, me = beta_star(K10q4, K10c)
        e_stat = float(e_static_c(M, WSCALE, DELTA).real)
        row = {
            "quartic_mineig": float(lamq.min()),
            "quartic_maxeig": float(lamq.max()),
            "frac_cells_negative": float((lamq.min(axis=-1) < -1e-12).mean()),
            "dressing_mineig_over_cells": float(lamc.min()),
            "beta_star": bstar,
            "mineig_at_beta_star": me,
            "U_add_frac_at_bstar": None if bstar is None else float(
                e_add_static_c(M, bstar, a) / abs(e_stat)),
            "U_add_frac_at_2bstar": None if bstar is None else float(
                e_add_static_c(M, 2.0 * bstar, a) / abs(e_stat)),
            "E_static_base": e_stat,
        }
        # dressed-Skyrme spectra at sample cells (can it go PSD-with-null?)
        s2rows = {}
        for a2 in (2.0, A_STAR, 7.0):
            mins = []
            for (ir, iz) in ((5, 63), (17, 63), (30, 63), (45, 20)):
                Arho, Aphi, Az, _ = channels(M, H)
                Al = [Arho[ir, iz], Aphi[ir, iz], Az[ir, iz]]
                Q = kin_form_point(Mc[ir, iz], Al, "s2", a=a2)
                lam = np.linalg.eigvalsh(Q)
                mins.append(float(lam.min()))
            s2rows[f"a={a2}"] = {"mineig_samples": mins}
        row["s2_dressed_samples"] = s2rows
        out[tag] = row
        print(f"[CENSUS] {tag}: quartic mineig {row['quartic_mineig']:.3e} "
              f"({row['frac_cells_negative']*100:.0f}% cells neg), dressing "
              f"mineig {row['dressing_mineig_over_cells']:.3e}, beta* = "
              f"{bstar}, U_add/U = {row['U_add_frac_at_bstar']}", flush=True)
    with open(os.path.join(DATA, "m5_20_4_c_census.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- statics anchors ----------------
def phase_statics(beta, a=A_STAR):
    """re-relax the recipe seed under E_old + U_C(beta, a), frozen time
    row (the B3 recipe), and compare the anchors."""
    M0 = load_seed("recipe")
    rd0 = ring_by_m13(M0, NR, NZ, H)
    q0, _ = winding_measure_biax(M0, NR, NZ, H, rd0["ring13_rho"],
                                 rd0["ring13_z"])
    cs0 = core_spectrum(M0, NR, NZ, H, rd0["ring13_rho"], rd0["ring13_z"])
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = W4[..., 0, 0]
    precond = (1.0 / wfull)[..., None, None]

    def g_frozen(MM):
        G = grad_static_4(MM, WSCALE, DELTA, w4=W4, rho4=RHO4) \
            + g_u_add(MM, beta, a, w4=W4, rho4=RHO4)
        G[..., 0, :] = 0.0
        G[..., :, 0] = 0.0
        return G

    def e_tot(MM):
        return (total_energy_4(MM, WSCALE, DELTA)
                + float(e_add_static_c(MM, beta, a).real))

    egf = lambda MM: (e_tot(MM), g_frozen(MM))  # noqa: E731
    Mx = M0.copy()
    hist = []
    done = 0
    while done < 3000:
        Mx, hh = fire_relax(Mx, egf, free4, precond, max_iter=500,
                            tol_rel=1e-9, dt0=0.005, dt_max=0.05,
                            log_every=500)
        done += hh["iter"][-1]
        rd = ring_by_m13(Mx, NR, NZ, H)
        qm, _ = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                     rd["ring13_z"])
        cs = core_spectrum(Mx, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
        hist.append({"it": done, "E": hh["E"][-1],
                     "gnorm": hh["gnorm"][-1],
                     "ring_rho": rd["ring13_rho"],
                     "q": None if not np.isfinite(qm) else float(qm),
                     "core_lam": cs["lam"]})
        print(f"  statics it {done}: E {hh['E'][-1]:.4f} ring "
              f"{rd['ring13_rho']:.2f} q {hist[-1]['q']}", flush=True)
        if hh["iter"][-1] < 500:
            break
    np.savez_compressed(os.path.join(DATA, "m5_20_4_c_seed_dressed.npz"),
                        M=Mx)
    out = {"beta": beta, "a": a,
           "baseline": {"ring_rho": rd0["ring13_rho"],
                        "q": None if not np.isfinite(q0) else float(q0),
                        "core_lam": cs0["lam"]},
           "dressed": hist[-1], "hist": hist,
           "seed_file": "m5_20_4_c_seed_dressed.npz"}
    with open(os.path.join(DATA, "m5_20_4_c_statics.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[STATICS] ring {rd0['ring13_rho']:.2f} -> "
          f"{hist[-1]['ring_rho']:.2f}, q {out['baseline']['q']} -> "
          f"{hist[-1]['q']}", flush=True)
    return out


# ---------------- the fixed dynamics ----------------
def accel_fixed(Mnp, Vnp, beta, a, wscale, delta, w4, h=H, g=G_T,
                rho4=None, want_diag=False):
    """EL solve of the FULL-RANK system:
    (4 k_q + k_C)[Mddot] = (GT_tot - G_stat_tot)/w - 4 kdot_q - kdot_C."""
    nr, nz = Mnp.shape[:2]
    Mc = Mnp[: nr - 1, 1:-1]
    Vc = Vnp[: nr - 1, 1:-1]
    G_stat = grad_static_4(Mnp, wscale, delta, h=h, g=g, w4=w4, rho4=rho4) \
        + g_u_add(Mnp, beta, a, w4=w4, rho4=rho4, h=h)
    GT = grad_m_T(Mnp, Vnp, w4, h=h, rho4=rho4)
    GT[: nr - 1, 1:-1] += w4 * grad_m_t_add(Mc, Vc, beta, a)
    kd = kdot_density(Mnp, Vnp, h=h)
    rhs = (((GT - G_stat)[: nr - 1, 1:-1]) / w4) - 4.0 * kd \
        - kdot_add(Mc, Vc, beta, a)
    r10 = np.einsum("akl,...kl->...a", BASIS, rhs)
    K10 = 4.0 * build_k10(Mnp, h) + k10_add(Mc, beta, a)
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
        diag = {"mass_mineig": float(lam.min()),
                "mass_maxeig": float(lam.max()),
                "max_abs_acc": float(np.max(np.abs(acc))),
                "n_floor_cells": int((np.abs(lam) <= floor).any(-1).sum())}
    return acc, diag


def evolve_fixed(M0, V0, T, dt, beta, a, wscale, delta, h=H, g=G_T,
                 snap_every=None, snap_fn=None, log_snaps=False):
    """velocity Verlet under the fixed (full-rank) dynamics; ledger
    E = T_q + T_C + U_old + U_C."""
    nr, nz = M0.shape[:2]
    w4 = cell_weights(nr, nz, h)[..., None, None]
    rho4 = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    pin = pin_mask(nr, nz)
    free4 = (~pin)[..., None, None].astype(float)
    if not np.all(np.isfinite(M0)):
        raise ValueError("evolve_fixed: non-finite initial state")
    Mx = M0.copy()
    v = np.zeros_like(Mx) if V0 is None else V0.copy()
    v *= free4
    n_steps = int(round(T / dt))
    if snap_every is None:
        snap_every = max(1, n_steps // 40)
    recs = []
    t0 = time.time()

    def snap(it, diag):
        ke_q = float(np.sum(t_density(Mx, v, h) * w4[..., 0, 0]))
        ke_c = float(t_add_total_c(Mx, v, beta, a, h).real)
        pe_q = float(e_static_c(Mx, wscale, delta, h, g).real)
        pe_c = float(e_add_static_c(Mx, beta, a, h).real)
        r = {"it": it, "t": it * dt, "KE_q": ke_q, "KE_C": ke_c,
             "PE_q": pe_q, "PE_C": pe_c,
             "E_tot": ke_q + ke_c + pe_q + pe_c}
        if diag:
            r.update(diag)
        if snap_fn is not None:
            r.update(snap_fn(Mx, v))
        recs.append(r)
        if log_snaps:
            print(f"  it {it:7d} t {r['t']:8.2f} E {r['E_tot']:12.6f} "
                  f"KEq {ke_q:.4f} KEc {ke_c:.4f} maxv "
                  f"{float(np.max(np.abs(v))):.3e}", flush=True)

    acc, diag = accel_fixed(Mx, v, beta, a, wscale, delta, w4, h, g,
                            rho4, want_diag=True)
    snap(0, diag)
    for it in range(1, n_steps + 1):
        vh = v + 0.5 * dt * acc
        Mx += dt * vh * free4
        if (not np.all(np.isfinite(Mx))) or float(np.max(np.abs(Mx))) > 1e6:
            recs.append({"it": it, "t": it * dt, "E_tot": float("nan"),
                         "blowup": True})
            print(f"  BLOWUP at it {it} (t {it * dt:.2f})", flush=True)
            break
        want = (it % snap_every == 0) or (it == n_steps)
        acc, diag = accel_fixed(Mx, vh, beta, a, wscale, delta, w4, h, g,
                                rho4, want_diag=want)
        v = (vh + 0.5 * dt * acc) * free4
        if want:
            snap(it, diag)
    return Mx, v, recs, time.time() - t0


def phase_evolve(beta, a=A_STAR, T=50.0, dt=0.00125, seed_kind="dressed",
                 tag=None):
    if seed_kind == "dressed":
        M0 = np.load(os.path.join(DATA, "m5_20_4_c_seed_dressed.npz"))["M"]
    else:
        M0 = load_seed(seed_kind)
    tag = tag or f"ev_{seed_kind}"

    def snap_fn(Mx, v):
        rd = ring_by_m13(Mx, NR, NZ, H)
        qm, _ = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                     rd["ring13_z"])
        return {"ring_rho": float(rd["ring13_rho"]),
                "q_r4": None if not np.isfinite(qm) else float(qm),
                "max_v": float(np.max(np.abs(v)))}

    Mx, v, recs, wall = evolve_fixed(M0, None, T, dt, beta, a, WSCALE,
                                     DELTA, snap_every=max(1, int(0.25 / dt)),
                                     snap_fn=snap_fn, log_snaps=True)
    fin = [r for r in recs if np.isfinite(r.get("E_tot", np.nan))]
    drift = (abs(fin[-1]["E_tot"] - fin[0]["E_tot"])
             / max(abs(fin[0]["E_tot"]), 1e-12)) if len(fin) > 1 else None
    out = {"tag": tag, "beta": beta, "a": a, "T": T, "dt": dt,
           "seed_kind": seed_kind, "wall_s": round(wall, 1),
           "reached_T": bool(fin and fin[-1]["t"] >= T - 2 * dt),
           "E_rel_drift": drift, "trajectory": recs}
    np.savez_compressed(os.path.join(DATA, f"m5_20_4_c_{tag}_end.npz"),
                        M=Mx, V=v)
    with open(os.path.join(DATA, f"m5_20_4_c_{tag}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[EVOLVE {tag}] reached_T={out['reached_T']} drift={drift} "
          f"wall {wall:.0f}s", flush=True)
    return out


def phase_film(beta=1.306, a=A_STAR, T=10.0, dt=0.00125,
               seed_kind="recipe", n_snap=6):
    """re-run the loop-seed closed-dynamics window with frame capture
    and render the basic-template strip per research/m5_visualization.md
    (non-blowup: N_SNAP even spacing, first row t = 0)."""
    import m5_film
    M0 = load_seed(seed_kind)
    n_steps = int(round(T / dt))
    snap_every = max(1, n_steps // (n_snap - 1))
    frames = [{"it": 0, "t": 0.0, "M": M0.copy()}]

    def snap_fn(Mx, v):
        it = len(frames) * snap_every
        if len(frames) < n_snap:
            frames.append({"it": it, "t": it * dt, "M": Mx.copy()})
        return {}

    evolve_fixed(M0, None, T, dt, beta, a, WSCALE, DELTA,
                 snap_every=snap_every, snap_fn=snap_fn)
    path = os.path.join(HERE, "..", "plots",
                        f"m5_20_4_film_{seed_kind}_closed.png")
    m5_film.film_strip(
        frames[:n_snap], path, template="basic", delta=DELTA,
        suptitle=f"M5.20.4 arm C: the loop seed under the CLOSED "
                 f"dynamics (qc term, beta = {beta:g}, a = {a:g}): "
                 f"no blowup to T = {T:g}, the texture slosh")
    return path


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "gates"
    if which == "gates":
        phase_gates()
    elif which == "census":
        phase_census(float(ARGV[1]) if len(ARGV) > 1 else A_STAR)
    elif which == "statics":
        phase_statics(float(ARGV[1]), float(ARGV[2]) if len(ARGV) > 2
                      else A_STAR)
    elif which == "evolve":
        phase_evolve(float(ARGV[1]), float(ARGV[2]) if len(ARGV) > 2
                     else A_STAR,
                     T=float(ARGV[3]) if len(ARGV) > 3 else 50.0)
    elif which == "film":
        phase_film()
    else:
        raise SystemExit(f"unknown phase {which}")
