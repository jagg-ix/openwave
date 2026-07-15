"""M5.20.2 phase A: the 4x4 (g, 1, delta, 0) sector, derived from the
M5.18-VERIFIED Lagrangian, in the axisym reduction.

SOURCE OF TRUTH: m5_18_lorentz_check.py (Duda's 4D Lagrangian, machine-
verified 2026-07-05: Lorentz invariance ~1e-11, Legendre exact, primary
constraint, indefiniteness witnesses, vacuum branches):

    eta = diag(-1, 1, 1, 1),   [A, B]_eta = A.eta.B - B.eta.A,
    F_{mu nu} = [d_mu M, d_nu M]_eta,
    L = - SUM_{mu<nu} eta^mumu eta^nunu <F, F>_eta  -  V,
    <F, G>_eta = F_ab G_cd eta^ac eta^bd,
    V = w SUM_{p=1..4} (Tr_eta(M^p) - C_p)^2,  Tr_eta(M^p) = tr((eta M)^p),
    C_p = g^p + 1 + delta^p + 0^p  (targets (g, 1, delta, 0));
    the g-timelike branch representative:  M_vac = diag(-g, 1, delta, 0)
    (then eta.M_vac = diag(g, 1, delta, 0): the preferred spectrum).

THE Q23 DERIVATION FINDING (stated up front, the honest structure):
    L is PURELY QUARTIC in derivatives: the kinetic sector is
        T = SUM_{i in rho,phi,z} <[Mdot, A_i]_eta, [Mdot, A_i]_eta>_eta ,
    quadratic in Mdot but with an M-DEPENDENT mass form K(M) that
    VANISHES on uniform states (all A_i = 0 => K = 0) and is degenerate
    everywhere (Mdot ~ eta is a global null direction: the verified
    primary constraint). There is NO canonical quadratic kinetic term in
    his verified L. Consequences measured here:
      - kin_census: the spectrum of K(M) on the loop states (rank,
        negative directions, magnitude vs the canonical norm);
    and the RUNNABLE regularization used for the M5.20.2 dynamics runs
    (documented as such, the M5.20 minimal-completion pattern):
      - canonical kinetic term (1/2)||Mdot||_F^2 + HIS static sector
        (eta-curvature + 4-target V), so the negative Gamma.Gamma-tilde
        structure enters through the STATIC energy (which is indefinite:
        the M5.18 witnesses), while time integration stays well-posed.

AXISYM REDUCTION (the M5.17 scheme, eta-extended)
    channels A_rho = d_rho M, A_z = d_z M (central diff, mirror ghost),
    A_phi = [J, M]/rho (plain commutator: the equivariant derivative;
    the rotation is eta-orthogonal so the reduction respects eta),
    static density  u_eta = 4 SUM_{(i<j)} <F_ij, F_ij>_eta ,
    F_ij = [A_i, A_j]_eta   (normalization pinned by gate GB0: for
    spatial-block-only fields u_eta == the audited M5.17/M5.20.1 plain
    u_curv EXACTLY, check-6 reduction).

GRADIENTS (adjoint identity, derived + FD-gated)
    d<F, [X, B]_eta>_eta / dX = eta (F eta B - B eta F) eta   (symmetric),
    scattered through the channel stencils exactly as grad_fast;
    dV/dM = w SUM_p 2 (Tr_eta(M^p) - C_p) * p * (eta M)^(p-1) eta.

GATES
    GB0  frozen time row (M00 = -g, M0i = 0) + any spatial-block field:
         u_eta == plain u_curv (<= 1e-12 rel) and V4 == the M5.20.1
         spatial V (exact), total energies equal
    GB1  FD directional gradient of the FULL 4x4 static energy
         (time-mixing directions included)                    (<= 1e-6)
    GB2  V4 = 0 exactly on every branch representative
    GB3  10x10 V-Hessian at M_vac: numeric == analytic eigenvalue-sector
         (2w J^T J on the eta-spectrum), zero/negative/positive census
    GB4  kinetic form: K(M)[eta] = 0 exactly (the primary constraint) on
         random states; K == 0 on uniform states

Run:  python m5_20_2_a_eom.py            (gates + gap map + censuses)
Out:  ../data/m5_20_2_a_eom.json, ../plots/m5_20_2_gapmap4.png
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

from m5_17_energy import cell_weights, grid_coords, J4, MIR        # noqa: E402
from m5_18_spectral import (potential_density_spec_np,             # noqa: E402
                            total_energy_spec_np)
from m5_17_energy import curvature_density_np                      # noqa: E402
from m5_20_1_b_seeds import cps_of, loop_field_biax                # noqa: E402
from m5_12_core_pin import load_wscale                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
WSCALE = load_wscale()
NR, NZ, H = 128, 256, 1.0
G_T = 8.0                                   # the engine LC_G
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


def c4_of(delta, g=G_T):
    return tuple(g ** p + 1.0 + delta ** p for p in range(1, 5))


def vac4(delta, g=G_T, branch="g_timelike"):
    """branch representatives diag(-lam_t, rest): eta.M has the preferred
    spectrum. g_timelike = his stated convention (primary)."""
    reps = {
        "g_timelike": (-g, 1.0, delta, 0.0),
        "one_timelike": (-1.0, g, delta, 0.0),
        "delta_timelike": (-delta, g, 1.0, 0.0),
        "zero_timelike": (0.0, g, 1.0, delta),
    }
    return np.diag(reps[branch])


# ---------------- channels (batched, 4x4 full) ----------------
def channels(Mnp, h=H):
    nr = Mnp.shape[0]
    Mminus = np.empty_like(Mnp[: nr - 1])
    Mminus[1:] = Mnp[: nr - 2]
    Mminus[0] = MIR * Mnp[0]
    Arho = ((Mnp[1:] - Mminus) / (2.0 * h))[:, 1:-1]
    Az = (Mnp[: nr - 1, 2:] - Mnp[: nr - 1, :-2]) / (2.0 * h)
    Mc = Mnp[: nr - 1, 1:-1]
    rho4 = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Aphi = (np.broadcast_to(J4, Mc.shape) @ Mc
            - Mc @ np.broadcast_to(J4, Mc.shape)) / rho4
    return Arho, Aphi, Az, rho4


def comm_eta_b(A, B):
    return A @ ETA @ B - B @ ETA @ A


def inner_eta_b(F, G):
    """<F,G>_eta per cell = tr(eta F eta G^T) (batched)."""
    return np.einsum("...ab,...cd,ac,bd->...", F, G, ETA, ETA)


def u_eta_density(Mnp, h=H):
    """4 SUM_{i<j} <F_ij, F_ij>_eta on included cells."""
    Arho, Aphi, Az, _ = channels(Mnp, h)
    tot = 0.0
    for (A, B) in ((Arho, Aphi), (Arho, Az), (Aphi, Az)):
        F = comm_eta_b(A, B)
        tot = tot + inner_eta_b(F, F)
    return 4.0 * tot


def v4_density(Mnp, wscale, delta, g=G_T):
    Mc = Mnp[: Mnp.shape[0] - 1, 1:-1]
    EM = np.broadcast_to(ETA, Mc.shape) @ Mc
    C = c4_of(delta, g)
    P = EM
    v = (np.einsum("...aa->...", P) - C[0]) ** 2
    for p in range(2, 5):
        P = P @ EM
        v = v + (np.einsum("...aa->...", P) - C[p - 1]) ** 2
    return wscale * v


def total_energy_4(Mnp, wscale, delta, h=H, g=G_T):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return float(np.sum((u_eta_density(Mnp, h)
                         + v4_density(Mnp, wscale, delta, g)) * w))


# ---------------- gradients ----------------
def _adj(F, B):
    """d<F,[X,B]_eta>/dX = eta (F eta B - B eta F) eta (symmetric)."""
    return ETA @ (F @ ETA @ B - B @ ETA @ F) @ ETA


def grad_static_4(Mnp, wscale, delta, h=H, g=G_T, w4=None, rho4=None):
    """dE/dM of the full 4x4 static energy (eta-curvature + V4), scattered
    with cell weights (the grad_fast conventions)."""
    nr = Mnp.shape[0]
    if w4 is None:
        w4 = cell_weights(NR, NZ, H)[..., None, None]
    Arho, Aphi, Az, r4 = channels(Mnp, h)
    if rho4 is None:
        rho4 = r4
    C1 = comm_eta_b(Arho, Aphi)
    C2 = comm_eta_b(Arho, Az)
    C3 = comm_eta_b(Aphi, Az)
    k = 8.0 * w4                                # 2 * 4 (density prefactor)
    Grho = k * (_adj(C1, Aphi) + _adj(C2, Az))
    Gphi = k * (-_adj(C1, Arho) + _adj(C3, Az))
    Gz = k * (-_adj(C2, Arho) - _adj(C3, Aphi))
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
    # V4: dV/dM = w sum_p 2 (tr_p - C_p) p (eta M)^(p-1) eta
    Mc = Mnp[: nr - 1, 1:-1]
    EM = np.broadcast_to(ETA, Mc.shape) @ Mc
    C = c4_of(delta, g)
    powers = [np.broadcast_to(np.eye(4), Mc.shape), EM, EM @ EM,
              EM @ EM @ EM]
    trs = [np.einsum("...aa->...", powers[1]),
           np.einsum("...aa->...", powers[2]),
           np.einsum("...aa->...", powers[3]),
           np.einsum("...aa->...", powers[3] @ EM)]
    dv = np.zeros_like(Mc)
    for p in range(1, 5):
        coef = (2.0 * wscale * (trs[p - 1] - C[p - 1]) * p)[..., None, None]
        dv = dv + coef * (powers[p - 1] @ ETA)
    dv = 0.5 * (dv + np.swapaxes(dv, -1, -2))
    G[: nr - 1, 1:-1] += dv * w4
    return G


# ---------------- the pure-L kinetic form (diagnostic) ----------------
def kin_form_apply(Mnp, Vdot, h=H):
    """pi = K(M)[Vdot] = SUM_i 2 eta (F_i eta A_i - A_i eta F_i) eta,
    F_i = [Vdot, A_i]_eta (per included cell; the pure-L momentum
    BEFORE any cell-weight measure)."""
    Arho, Aphi, Az, _ = channels(Mnp, h)
    Vc = Vdot[: Mnp.shape[0] - 1, 1:-1]
    pi = np.zeros_like(Vc)
    for A in (Arho, Aphi, Az):
        F = comm_eta_b(Vc, A)
        pi = pi + 2.0 * _adj(F, A)
    return pi


def kin_census(Mnp, cells, h=H):
    """spectrum of the 10x10 kinetic form K at sample cells: rank,
    negative count, extreme eigenvalues (vs the canonical form = I)."""
    basis = []
    for i in range(4):
        e = np.zeros((4, 4))
        e[i, i] = 1.0
        basis.append(e)
    for (i, j) in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        e = np.zeros((4, 4))
        e[i, j] = e[j, i] = 1.0 / np.sqrt(2.0)
        basis.append(e)
    out = []
    for (ci, cj) in cells:
        K = np.zeros((10, 10))
        for a in range(10):
            V = np.zeros_like(Mnp)
            V[ci, cj] = basis[a]
            # localized probe: K is cell-local (A_i at the cell)
            pi = kin_form_apply(Mnp, V, h)[ci, cj - 1]
            for b in range(10):
                K[a, b] = float(np.sum(pi * basis[b]))
        ev = np.linalg.eigvalsh(0.5 * (K + K.T))
        scale = max(np.abs(ev).max(), 1e-300)
        out.append({"cell": [int(ci), int(cj)],
                    "eigs": ev.tolist(),
                    "rank": int(np.sum(np.abs(ev) > 1e-10 * scale)),
                    "n_negative": int(np.sum(ev < -1e-10 * scale)),
                    "max_abs": float(np.abs(ev).max())})
    return out


# ---------------- gap map (10x10 V-Hessian per branch) ----------------
def sym_basis4():
    basis = []
    for i in range(4):
        e = np.zeros((4, 4))
        e[i, i] = 1.0
        basis.append(e)
    for (i, j) in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        e = np.zeros((4, 4))
        e[i, j] = e[j, i] = 1.0 / np.sqrt(2.0)
        basis.append(e)
    return basis


def vdens4_point(M, delta, wscale=WSCALE, g=G_T):
    EM = ETA @ M
    C = c4_of(delta, g)
    v = 0.0
    P = np.eye(4)
    for p in range(1, 5):
        P = P @ EM
        v += (np.trace(P) - C[p - 1]) ** 2
    return wscale * v


def hessian4(delta, branch="g_timelike", wscale=WSCALE, eps=1e-5):
    M0 = vac4(delta, branch=branch)
    basis = sym_basis4()
    Hm = np.zeros((10, 10))
    for a in range(10):
        for b in range(10):
            Hm[a, b] = (vdens4_point(M0 + eps * (basis[a] + basis[b]), delta, wscale)
                        - vdens4_point(M0 + eps * (basis[a] - basis[b]), delta, wscale)
                        - vdens4_point(M0 + eps * (-basis[a] + basis[b]), delta, wscale)
                        + vdens4_point(M0 - eps * (basis[a] + basis[b]), delta, wscale)
                        ) / (4 * eps ** 2)
    return 0.5 * (Hm + Hm.T)


def analytic_eig_sector(delta, wscale=WSCALE, g=G_T):
    """diagonal (eigenvalue) sector: 2w J~^T J~ with the SIGNED Jacobian
    J~_pi = p lam_i^{p-1} eta_ii on the eta-spectrum (g, 1, delta, 0):
    for dM = e_ii, d Tr_eta(M^p) = p [(eta M0)^{p-1} eta]_{ii}
    = p lam_i^{p-1} eta_ii (the timelike column is NEGATED; the first
    numeric run measured exactly this as a 4.2e-3 residual)."""
    lam = np.array([g, 1.0, delta, 0.0])
    sgn = np.array([-1.0, 1.0, 1.0, 1.0])
    J = np.array([[p * lam[i] ** (p - 1) * sgn[i] for i in range(4)]
                  for p in range(1, 5)])
    return 2.0 * wscale * (J.T @ J)


def hessian4_analytic(delta, wscale=WSCALE, g=G_T):
    """EXACT 10x10 V-Hessian at the g-timelike representative: at the
    minimum H = 2w SUM_p grad(t_p) grad(t_p)^T; grad(t_p) = p (eta M0)^{p-1}
    eta is DIAGONAL, so all 6 off-diagonal (boost + rotation) directions
    are EXACT zero modes at quadratic order and the diagonal sector is the
    signed 2w J~^T J~ (rank 4 for distinct (g, 1, delta, 0))."""
    Hm = np.zeros((10, 10))
    Hm[:4, :4] = analytic_eig_sector(delta, wscale, g)
    return Hm


# ---------------- seeds ----------------
def seed4(delta, pairing, branch="g_timelike", R0=17.0, q=0.5):
    """the M5.20.1 biax loop seed with the 4x4 branch time block:
    M00 = -g (the g-timelike representative), M0i = 0."""
    R, Z = grid_coords(NR, NZ, H)
    M = loop_field_biax(R, Z, R0, q, delta, pairing)
    M[..., 0, 0] = vac4(delta, branch=branch)[0, 0]
    return M


# ---------------- gates ----------------
def v4_density_pmax(Mnp, wscale, delta, g=G_T, pmax=4):
    Mc = Mnp[: Mnp.shape[0] - 1, 1:-1]
    EM = np.broadcast_to(ETA, Mc.shape) @ Mc
    C = c4_of(delta, g)
    P = EM
    v = (np.einsum("...aa->...", P) - C[0]) ** 2
    for p in range(2, pmax + 1):
        P = P @ EM
        v = v + (np.einsum("...aa->...", P) - C[p - 1]) ** 2
    return wscale * v


def gate_gb0(delta=0.3):
    """frozen-time-row reduction: u_eta == plain u_curv EXACTLY, and V4
    restricted to p <= 3 == the M5.20.1 spatial V EXACTLY (with the block-
    diagonal time row, Tr_eta(M^p) = g^p + tr(Msp^p), so the g^p cancels
    against C_p). The p = 4 target is the GENUINE 4D addition (reported,
    not a reduction error)."""
    M = seed4(delta, "pair_1d")
    u_e = u_eta_density(M)
    u_p = curvature_density_np(M, H, 1.0)
    rel_u = float(np.max(np.abs(u_e - u_p))
                  / max(float(np.max(np.abs(u_p))), 1e-300))
    v4r = v4_density_pmax(M, WSCALE, delta, pmax=3)
    v3 = potential_density_spec_np(M, WSCALE, cps_of(delta))
    rel_v = float(np.max(np.abs(v4r - v3))
                  / max(float(np.max(np.abs(v3))), 1e-300))
    w = cell_weights(NR, NZ, H)
    E4 = total_energy_4(M, WSCALE, delta)
    E3 = total_energy_spec_np(M, WSCALE, H, cps_of(delta))
    E_p4 = float(np.sum((v4_density(M, WSCALE, delta)
                         - v4_density_pmax(M, WSCALE, delta, pmax=3)) * w))
    ok = rel_u < 1e-12 and rel_v < 1e-10 and abs(E4 - (E3 + E_p4)) < 1e-9
    return ok, {"rel_u": rel_u, "rel_v4_p3_vs_v3": rel_v,
                "E4": E4, "E3": E3, "E_p4_addition": E_p4}


def gate_gb1(delta=0.3):
    """FD directional gradient of the FULL 4x4 static energy, time-mixing
    directions included."""
    M0 = seed4(delta, "pair_1d")
    rng = np.random.default_rng(13)
    # add a time-mixing texture so the eta sector is genuinely exercised
    R, Z = grid_coords(NR, NZ, H)
    bump = 0.05 * np.exp(-((R - 17.0) ** 2 + Z ** 2) / 30.0)
    M0[..., 0, 1] += bump
    M0[..., 1, 0] += bump
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
    G = grad_static_4(M0, WSCALE, delta, w4=w4, rho4=rho4)
    worst = 0.0
    eps = 1e-6
    for _ in range(4):
        Dc = rng.normal(size=(NR - 1, NZ - 2, 4, 4))
        D = np.zeros_like(M0)
        D[: NR - 1, 1:-1] = 0.5 * (Dc + np.swapaxes(Dc, -1, -2))
        num = (total_energy_4(M0 + eps * D, WSCALE, delta)
               - total_energy_4(M0 - eps * D, WSCALE, delta)) / (2 * eps)
        an = float(np.sum(G * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-12))
    return worst < 1e-6, {"gradcheck": worst}


def gate_gb2():
    out = {}
    for delta in (0.1, 0.3, 0.5):
        for branch in ("g_timelike", "one_timelike", "delta_timelike",
                       "zero_timelike"):
            out[f"d{delta}_{branch}"] = vdens4_point(vac4(delta,
                                                          branch=branch),
                                                     delta, 1.0)
    ok = all(abs(v) < 1e-18 for v in out.values())
    return ok, out


def gate_gb3_and_map():
    """the gap map is ANALYTIC (exact at the minimum: 6 boost/rotation
    flats + the signed 2w J~^T J~ diagonal sector); the FD Hessian is the
    cross-check (its noise floor ~1e-8 abs at eps 1e-5 with g = 8 traces)."""
    rows = []
    worst = 0.0
    for delta in (0.0, 0.1, 0.3, 0.5):
        Ha10 = hessian4_analytic(delta)
        ev = np.linalg.eigvalsh(Ha10)
        nzero = int(np.sum(np.abs(ev) < 1e-12))
        nneg = int(np.sum(ev < -1e-12))
        Hn = hessian4(delta)
        rel = float(np.max(np.abs(Hn - Ha10))
                    / max(np.max(np.abs(Ha10)), 1e-300))
        worst = max(worst, rel)
        omegas = np.sqrt(np.maximum(ev, 0.0))
        rows.append({"delta": delta, "eigs": ev.tolist(),
                     "omegas": omegas.tolist(), "n_zero": nzero,
                     "n_negative": nneg, "FD_crosscheck_rel": rel})
    return worst < 1e-6, rows, worst


def gate_gb4(delta=0.3):
    M = seed4(delta, "pair_1d")
    rng = np.random.default_rng(5)
    # K[eta] = 0 (global null), K == 0 on uniform states
    Veta = np.zeros_like(M)
    Veta[: NR - 1, 1:-1] = ETA
    pi_eta = kin_form_apply(M, Veta)
    # gradient-free state in the axisym scheme = uniform AND J-commuting
    # (in-plane equal); vac4 is NOT J-commuting (A_phi background: the
    # M5.20.1 axis-disclination lesson), so use diag(-g, a, a, b)
    Mu = np.zeros_like(M)
    Mu[..., 0, 0], Mu[..., 1, 1], Mu[..., 2, 2], Mu[..., 3, 3] = (
        -G_T, 0.7, 0.7, 0.2)
    Vr = rng.normal(size=M.shape)
    Vr = 0.5 * (Vr + np.swapaxes(Vr, -1, -2))
    pi_u = kin_form_apply(Mu, Vr)
    # and the vac4 background DOES carry a kinetic form (A_phi != 0):
    pi_v = kin_form_apply(np.broadcast_to(vac4(delta),
                                          M.shape).copy(), Vr)
    return (float(np.max(np.abs(pi_eta))) < 1e-12
            and float(np.max(np.abs(pi_u))) < 1e-12), {
        "max_pi_of_eta": float(np.max(np.abs(pi_eta))),
        "max_pi_on_Jcommuting_uniform": float(np.max(np.abs(pi_u))),
        "max_pi_on_vac4_equivariant_bg": float(np.max(np.abs(pi_v)))}


def main():
    os.makedirs(DATA, exist_ok=True)
    out = {"task": "M5.20.2", "phase": "A", "wscale": WSCALE, "g": G_T,
           "branch_primary": "g_timelike (M_vac = diag(-g, 1, delta, 0))"}
    for name, fn in [("GB0", gate_gb0), ("GB1", gate_gb1),
                     ("GB2", gate_gb2), ("GB4", gate_gb4)]:
        ok, detail = fn()
        out[name] = {"ok": bool(ok), "detail": detail}
        print(f"[{name}] {'PASS' if ok else 'FAIL'} "
              + json.dumps(detail, default=float)[:240])
    ok3, rows, worst3 = gate_gb3_and_map()
    out["GB3"] = {"ok": bool(ok3), "rel_worst": worst3}
    out["gap_map_4x4"] = rows
    print(f"[GB3] {'PASS' if ok3 else 'FAIL'} rel_worst={worst3:.2e}")
    for r in rows:
        print(f"  delta={r['delta']:.1f} zero={r['n_zero']} "
              f"neg={r['n_negative']} "
              f"omegas={np.round([o for o in r['omegas'] if o > 1e-9], 5)}")
    # kinetic census on the loop seed: core cell, shoulder, far field
    M = seed4(0.3, "pair_1d")
    cells = [(17, 128), (22, 128), (80, 128)]
    out["kin_census_seed_d0p3_pair_1d"] = kin_census(M, cells)
    for c in out["kin_census_seed_d0p3_pair_1d"]:
        print(f"  K at cell {c['cell']}: rank {c['rank']}/10, "
              f"neg {c['n_negative']}, max|eig| {c['max_abs']:.3e}")
    # plot
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    ds = [r["delta"] for r in rows]
    om = np.array([[o for o in r["omegas"]] for r in rows])
    for k in range(10):
        axes[0].plot(ds, om[:, k], "o-", ms=3, lw=1)
    axes[0].set_xlabel("delta")
    axes[0].set_ylabel("omega (canonical-kinetic normalization)")
    axes[0].set_title("4x4 vacuum mass ladder at diag(-g, 1, delta, 0)")
    axes[1].plot(ds, [r["n_zero"] for r in rows], "s-", label="zero modes")
    axes[1].plot(ds, [r["n_negative"] for r in rows], "v-",
                 label="negative modes")
    axes[1].set_xlabel("delta")
    axes[1].legend(fontsize=8)
    axes[1].set_title("10x10 V-Hessian census per delta (g-timelike branch)")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m5_20_2_gapmap4.png"), dpi=130)
    with open(os.path.join(DATA, "m5_20_2_a_eom.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote data/m5_20_2_a_eom.json + plots/m5_20_2_gapmap4.png")
    return out


if __name__ == "__main__":
    main()
