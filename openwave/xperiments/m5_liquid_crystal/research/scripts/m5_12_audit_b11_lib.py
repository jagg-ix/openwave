"""M5.12 block-11 ADVERSARIAL AUDIT library (independent auditor).

Independent re-implementations of the audited functionals, written fresh from
the documented conventions (m5_12_d3a_bvp.py docstring + the verified m5_18
Lagrangian conventions), NOT copied from the claimant's code paths:

    Shat[X; w] = (1/Ns) SUM_j SUM_cells wcell . [ 4 SUM_{i<j} inner_eta(F_ij)
                 - 4 SUM_i inner_eta(F_0i) + V_4D ]
    inner_eta(F, F) = SUM_ab sgn(eta_a eta_b) F_ab^2      (own closed form)
    V_4D = wscale SUM_{p=1..4} (Tr((eta M)^p) - (g^p + 1))^2
    H    = same with ALL pairs +.

KEY STRUCTURAL FACT the audit exploits (derived, then machine-verified):
M(t_j) does not depend on omega (samples at fixed phases) and Mdot ~ omega,
so Shat(X, w) = S0(X) - w^2 Q2(X) EXACTLY, and the claimant's residual
R(X, w) = R_sp(X) + w^2 R_t(X) EXACTLY. The least-squares-optimal omega at
fixed X is therefore closed-form:  w*^2 = -<R_sp, R_t> / |R_t|^2.

The spatial channel stencil (central diff + mirror ghost + J-fold) is the
single-source verified discretization (m5_17_energy / M5.16 gates); it is
re-typed here from the equations so no claimant module is imported by this
library.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
sys.path.insert(0, HERE)

ETA4 = np.diag([-1.0, 1.0, 1.0, 1.0])
MIR4 = np.outer([1.0, -1.0, -1.0, 1.0], [1.0, -1.0, -1.0, 1.0])
J4A = np.zeros((4, 4)); J4A[1, 2] = -1.0; J4A[2, 1] = 1.0
SGN = np.outer(np.diag(ETA4), np.diag(ETA4))      # sgn(eta_a eta_b)
# mask of the time-mixing entries (0,i)/(i,0): where SGN = -1
MIXMASK = (SGN < 0)


def cellw(nr, nz, h):
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None]
    return np.broadcast_to(2.0 * np.pi * rho * h * h, (nr - 1, nz - 2)).copy()


def channels(M, h):
    """(Mc, Arho, Aphi, Az) on included cells; the verified stencil."""
    nr = M.shape[0]
    Mm = np.empty_like(M[: nr - 1])
    Mm[1:] = M[: nr - 2]
    Mm[0] = MIR4 * M[0]
    Ar = (M[1:] - Mm)[:, 1:-1] / (2.0 * h)
    Az = (M[: nr - 1, 2:] - M[: nr - 1, :-2]) / (2.0 * h)
    Mc = M[: nr - 1, 1:-1]
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Ap = (np.einsum("ab,...bc->...ac", J4A, Mc)
          - np.einsum("...ab,bc->...ac", Mc, J4A)) / rho
    return Mc, Ar, Ap, Az


def ceta(A, B):
    return (np.einsum("...ab,bc,...cd->...ad", A, ETA4, B)
            - np.einsum("...ab,bc,...cd->...ad", B, ETA4, A))


def ieta(F):
    """inner_eta(F, F) per cell = SUM_ab sgn(eta_a eta_b) F_ab^2."""
    return np.einsum("...ab,...ab,ab->...", F, F, SGN)


def ieta_split(F):
    """(positive-sign part, negative-sign/time-mixing part) of inner_eta."""
    F2 = F * F
    pos = np.einsum("...ab,ab->...", F2, np.where(SGN > 0, 1.0, 0.0))
    neg = np.einsum("...ab,ab->...", F2, np.where(SGN < 0, 1.0, 0.0))
    return pos, -neg      # inner_eta = pos + (-neg) with neg >= 0


def v4(Mc, wscale, g=8.0):
    EM = np.einsum("ab,...bc->...ac", ETA4, Mc)
    P = EM.copy()
    v = np.zeros(Mc.shape[:-2])
    for p in range(1, 5):
        tr = np.einsum("...aa->...", P)
        v = v + (tr - (g ** p + 1.0)) ** 2
        if p < 4:
            P = np.einsum("...ab,...bc->...ac", P, EM)
    return wscale * v


def sample_X(X, ns):
    """M(theta_j) and Mdot-hat(theta_j) (= Mdot at omega = 1)."""
    Nt = len(X["A"])
    Ms, Mdh = [], []
    for j in range(ns):
        th = 2.0 * np.pi * j / ns
        M = X["M0"].copy()
        Md = np.zeros_like(M)
        for k in range(1, Nt + 1):
            c, s = np.cos(k * th), np.sin(k * th)
            M = M + X["A"][k - 1] * c + X["B"][k - 1] * s
            Md = Md + k * (-X["A"][k - 1] * s + X["B"][k - 1] * c)
        Ms.append(M)
        Mdh.append(Md)
    return Ms, Mdh


def s0_q2_maps(X, h, wscale, ns=None, g=8.0):
    """per-cell maps (included cells, x cellw applied by caller):
    s0map  = period-avg spatial-pairs + V density,
    q2map  = period-avg 4 SUM_i inner_eta(F_0i-hat) density (unit omega),
    q2mix  = its negative-sign (time-mixing entry) part,
    so Shat = SUM w (s0map - w^2 q2map), H = SUM w (s0map + w^2 q2map)."""
    Nt = len(X["A"])
    ns = ns or (4 * Nt + 2)
    Ms, Mdh = sample_X(X, ns)
    s0 = None
    q2 = None
    q2mix = None
    for M, Md in zip(Ms, Mdh):
        Mc, Ar, Ap, Az = channels(M, h)
        D0 = Md[: M.shape[0] - 1, 1:-1]
        d = np.zeros(Mc.shape[:2])
        ch = (Ar, Ap, Az)
        for a in range(3):
            for b in range(a + 1, 3):
                C = ceta(ch[a], ch[b])
                d += 4.0 * ieta(C)
        d += v4(Mc, wscale, g)
        q = np.zeros(Mc.shape[:2])
        qm = np.zeros(Mc.shape[:2])
        for a in range(3):
            C = ceta(D0, ch[a])
            q += 4.0 * ieta(C)
            _, neg = ieta_split(C)
            qm += 4.0 * neg          # (negative-signed) mixing contribution
        s0 = d if s0 is None else s0 + d
        q2 = q if q2 is None else q2 + q
        q2mix = qm if q2mix is None else q2mix + qm
    return s0 / ns, q2 / ns, q2mix / ns


def my_shat(X, omega, h, wscale, ns=None, g=8.0):
    nr, nz = X["M0"].shape[:2]
    w = cellw(nr, nz, h)
    s0, q2, _ = s0_q2_maps(X, h, wscale, ns, g)
    return float(np.sum((s0 - omega ** 2 * q2) * w))


def my_s0_q2(X, h, wscale, ns=None, g=8.0):
    nr, nz = X["M0"].shape[:2]
    w = cellw(nr, nz, h)
    s0, q2, q2m = s0_q2_maps(X, h, wscale, ns, g)
    return (float(np.sum(s0 * w)), float(np.sum(q2 * w)),
            float(np.sum(q2m * w)))


def my_H_samples(X, omega, h, wscale, ns=12, g=8.0):
    """per-sample H(t_j) (ALL pairs +) for the Noether-drift check."""
    nr, nz = X["M0"].shape[:2]
    w = cellw(nr, nz, h)
    Ms, Mdh = sample_X(X, ns)
    Hs = []
    for M, Md in zip(Ms, Mdh):
        Mc, Ar, Ap, Az = channels(M, h)
        D0 = omega * Md[: nr - 1, 1:-1]
        d = np.zeros(Mc.shape[:2])
        ch = (Ar, Ap, Az)
        for a in range(3):
            for b in range(a + 1, 3):
                C = ceta(ch[a], ch[b])
                d += 4.0 * ieta(C)
        for a in range(3):
            C = ceta(D0, ch[a])
            d += 4.0 * ieta(C)
        d += v4(Mc, wscale, g)
        Hs.append(float(np.sum(d * w)))
    return np.array(Hs)


def my_spatialV_samples(X, h, wscale, ns=12, g=8.0):
    """spatial+V energy of each time sample (isoenergy test of the orbit)."""
    nr, nz = X["M0"].shape[:2]
    w = cellw(nr, nz, h)
    Ms, _ = sample_X(X, ns)
    Es = []
    for M in Ms:
        Mc, Ar, Ap, Az = channels(M, h)
        d = np.zeros(Mc.shape[:2])
        ch = (Ar, Ap, Az)
        for a in range(3):
            for b in range(a + 1, 3):
                C = ceta(ch[a], ch[b])
                d += 4.0 * ieta(C)
        d += v4(Mc, wscale, g)
        Es.append(float(np.sum(d * w)))
    return np.array(Es)


# ---------------- state IO + masks ----------------
def load_state(path):
    d = np.load(path)
    Nt = sum(1 for k in d.files if k.startswith("A"))
    X = {"M0": d["M0"].astype(np.float64),
         "A": [d[f"A{k}"].astype(np.float64) for k in range(1, Nt + 1)],
         "B": [d[f"B{k}"].astype(np.float64) for k in range(1, Nt + 1)]}
    return X, float(d["omega"][0])


def free_mask(nr, nz, shape):
    pin = np.zeros((nr, nz), dtype=bool)
    pin[-1, :] = True
    pin[:, 0] = True
    pin[:, -1] = True
    return np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), shape), pin


def rd_flat(Rd, free):
    parts = [Rd["M0"][free]]
    for k in range(len(Rd["A"])):
        parts.append(Rd["A"][k][free])
        parts.append(Rd["B"][k][free])
    return np.concatenate(parts)


def rd_cellmap(Rd, free):
    """per-(nr,nz)-cell squared content over all blocks + components."""
    m = np.sum(np.where(free, Rd["M0"], 0.0) ** 2, axis=(-2, -1))
    for k in range(len(Rd["A"])):
        m = m + np.sum(np.where(free, Rd["A"][k], 0.0) ** 2, axis=(-2, -1))
        m = m + np.sum(np.where(free, Rd["B"][k], 0.0) ** 2, axis=(-2, -1))
    return m


def rd_dotmap(Ra, Rb, free):
    """per-cell <Ra, Rb> over all blocks + components."""
    m = np.sum(np.where(free, Ra["M0"], 0.0) * np.where(free, Rb["M0"], 0.0),
               axis=(-2, -1))
    for k in range(len(Ra["A"])):
        m = m + np.sum(np.where(free, Ra["A"][k], 0.0)
                       * np.where(free, Rb["A"][k], 0.0), axis=(-2, -1))
        m = m + np.sum(np.where(free, Ra["B"][k], 0.0)
                       * np.where(free, Rb["B"][k], 0.0), axis=(-2, -1))
    return m


def grid_r(nr, nz, h=1.0):
    rho = (np.arange(nr) + 0.5) * h
    z = (np.arange(nz) - nz / 2 + 0.5) * h
    R, Z = np.meshgrid(rho, z, indexing="ij")
    return np.sqrt(R ** 2 + Z ** 2)


def region_masks(nr, nz, rc, h=1.0):
    r = grid_r(nr, nz, h)
    return {"core_r<2rc": r < 2 * rc,
            "halo_2-6rc": (r >= 2 * rc) & (r < 6 * rc),
            "far_r>6rc": r >= 6 * rc}


def rotor_project(Md, plane=(2, 3), Nt=1, ns=None):
    """band-limited Fourier projection of L(th) Md L(th)^T (own code)."""
    ns = ns or (4 * Nt + 2)
    i, j = plane

    def rot(th):
        L = np.eye(4)
        L[i, i], L[i, j] = np.cos(th), -np.sin(th)
        L[j, i], L[j, j] = np.sin(th), np.cos(th)
        return np.einsum("ab,...bc,dc->...ad", L, Md, L)

    samples = [rot(2.0 * np.pi * jj / ns) for jj in range(ns)]
    M0 = sum(samples) / ns
    As, Bs = [], []
    for k in range(1, Nt + 1):
        As.append(sum(s * np.cos(k * 2.0 * np.pi * jj / ns)
                      for jj, s in enumerate(samples)) * 2.0 / ns)
        Bs.append(sum(s * np.sin(k * 2.0 * np.pi * jj / ns)
                      for jj, s in enumerate(samples)) * 2.0 / ns)
    return {"M0": M0, "A": As, "B": Bs}


def gen_w(i, j):
    W = np.zeros((4, 4))
    W[i, j], W[j, i] = -1.0, 1.0      # dL/dth at 0 for the rot() convention
    return W


def comm_eta_gen(W, M):
    """[W, M]_eta = W eta M - M eta W (generator tangent, eta action)."""
    return (np.einsum("ab,bc,...cd->...ad", W, ETA4, M)
            - np.einsum("...ab,bc,cd->...ad", M, ETA4, W))


def comm_plain_gen(W, M):
    return (np.einsum("ab,...bc->...ac", W, M)
            - np.einsum("...ab,bc->...ac", M, W))
