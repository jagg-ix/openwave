"""M5.20.2 INDEPENDENT ADVERSARIAL AUDIT (AI_HYGIENE.md section 1).

Tries to REFUTE the six M5.20.2 claims with own code:
  C1  L purely quartic in derivatives; K(M) = 0 on gradient-free states;
      K[eta] = 0; kin census (rank 8/10, 3 negative at the loop core)
  C2  analytic 10x10 V-Hessian at diag(-g, 1, delta, 0): 6 zero modes +
      2w J~^T J~ signed eigenvalue sector; omega ladder at delta = 0.3;
      off-diagonal flats quartic beyond quadratic order
  C3  boost-sector runaway at t ~ 21.5 (dt-robustness + J-commuting
      uniform-background control)
  C4  H(omega) = H(0) + omega^2 K_eff exact on rigid Lorentz orbits;
      sign census; exact J12/B03 zeros on vac4
  C5  protection re-probe endpoint: own plaquette defect scan; frozen
      time row legitimacy (M00 uniform, energy ledger)
  C6  GB0 reduction spot-check with own implementation

Independence policy: all algebra re-implemented from the m5_18 equations;
imports from the task scripts are limited to the OBJECTS UNDER TEST
(seed4, vac4) and the sanctioned public functions (grad_static_4,
total_energy_4 for direct evaluation; curvature_density_np = the frozen
M5.17 reference for C6). Integrator for C3 is an own velocity Verlet.

Run:  python m5_20_2_audit_check.py [c1 c2 c4 c5 c6 c3 | all]
Out:  ../data/m5_20_2_audit.json
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.linalg import expm

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

# objects under test + sanctioned public functions ONLY
from m5_20_2_a_eom import (seed4, vac4, grad_static_4,            # noqa: E402
                           total_energy_4)
from m5_17_energy import curvature_density_np                     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# ---- own constants / conventions (re-declared, not imported) ----
NR, NZ, H = 128, 256, 1.0
G = 8.0
DELTA = 0.3
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
J4 = np.zeros((4, 4))
J4[1, 2] = -1.0
J4[2, 1] = 1.0
MIR = np.outer([1.0, -1.0, -1.0, 1.0], [1.0, -1.0, -1.0, 1.0])
with open(os.path.join(DATA, "m5_18_spectral_spec_n96.json")) as _f:
    WSCALE = json.load(_f)["params"]["wscale"]
RNG = np.random.default_rng(424242)
RESULT = {"task": "M5.20.2", "role": "independent adversarial audit",
          "wscale": WSCALE}


def sym(A):
    return 0.5 * (A + A.T)


# =================== own m5_18 algebra (from the equations) ===========
def comm_eta(A, B):
    return A @ ETA @ B - B @ ETA @ A


def inner_eta(F, Gm):
    return float(np.einsum("ab,cd,ac,bd->", F, Gm, ETA, ETA))


def l_curv_own(D):
    """- sum_{mu<nu} eta^mumu eta^nunu <F_munu, F_munu>_eta."""
    tot = 0.0
    for mu in range(4):
        for nu in range(mu + 1, 4):
            F = comm_eta(D[mu], D[nu])
            tot += ETA[mu, mu] * ETA[nu, nu] * inner_eta(F, F)
    return -tot


def sym_basis4():
    b = []
    for i in range(4):
        e = np.zeros((4, 4))
        e[i, i] = 1.0
        b.append(e)
    for (i, j) in ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)):
        e = np.zeros((4, 4))
        e[i, j] = e[j, i] = 1.0 / np.sqrt(2.0)
        b.append(e)
    return b


# =================== own axisym machinery ==============================
def own_grid():
    rho = (np.arange(NR) + 0.5) * H
    z = (np.arange(NZ) - NZ / 2 + 0.5) * H
    return np.meshgrid(rho, z, indexing="ij")


def own_weights():
    rho = ((np.arange(NR - 1) + 0.5) * H)[:, None]
    return np.broadcast_to(2.0 * np.pi * rho * H * H,
                           (NR - 1, NZ - 2)).copy()


def own_channels(M):
    """A_rho (central diff, mirror ghost), A_phi = [J, M]/rho, A_z; on
    included cells [0..NR-2] x [1..NZ-2]."""
    Mminus = np.empty_like(M[: NR - 1])
    Mminus[1:] = M[: NR - 2]
    Mminus[0] = MIR * M[0]
    Arho = ((M[1:] - Mminus) / (2.0 * H))[:, 1:-1]
    Az = (M[: NR - 1, 2:] - M[: NR - 1, :-2]) / (2.0 * H)
    Mc = M[: NR - 1, 1:-1]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
    Jb = np.broadcast_to(J4, Mc.shape)
    Aphi = (Jb @ Mc - Mc @ Jb) / rho4
    return Arho, Aphi, Az


def comm_eta_b(A, B):
    return A @ ETA @ B - B @ ETA @ A


def inner_eta_b(F, Gm):
    return np.einsum("...ab,...cd,ac,bd->...", F, Gm, ETA, ETA)


def own_u_eta(M):
    Arho, Aphi, Az = own_channels(M)
    tot = 0.0
    for (A, B) in ((Arho, Aphi), (Arho, Az), (Aphi, Az)):
        F = comm_eta_b(A, B)
        tot = tot + inner_eta_b(F, F)
    return 4.0 * tot


def own_v4(M, delta=DELTA, wscale=WSCALE, pmax=4):
    Mc = M[: NR - 1, 1:-1]
    EM = np.broadcast_to(ETA, Mc.shape) @ Mc
    v = 0.0
    P = np.broadcast_to(np.eye(4), Mc.shape)
    for p in range(1, pmax + 1):
        P = P @ EM
        cp = G ** p + 1.0 + delta ** p
        v = v + (np.einsum("...aa->...", P) - cp) ** 2
    return wscale * v


def own_energy(M, delta=DELTA, wscale=WSCALE):
    return float(np.sum((own_u_eta(M) + own_v4(M, delta, wscale))
                        * own_weights()))


def own_kin_dens(M, Md):
    """4 sum_i <[Md, A_i]_eta, [Md, A_i]_eta>_eta per included cell
    (the H-normalization matching u_eta's factor 4)."""
    Arho, Aphi, Az = own_channels(M)
    Mdc = Md[: NR - 1, 1:-1] if Md.shape[:2] == (NR, NZ) else Md
    tot = 0.0
    for A in (Arho, Aphi, Az):
        F = comm_eta_b(Mdc, A)
        tot = tot + inner_eta_b(F, F)
    return 4.0 * tot


# ============================ C1 =======================================
def c1():
    out = {}
    # (a) purely quartic: l_curv(c D) = c^4 l_curv(D)
    D = [sym(RNG.normal(size=(4, 4))) for _ in range(4)]
    c = 1.7
    l1 = l_curv_own(D)
    l2 = l_curv_own([c * d for d in D])
    out["quartic_scaling_rel"] = abs(l2 - c ** 4 * l1) / abs(l1)
    # (b) gradient-free states: T(Mdot) = L(Mdot) - L(0) == 0 exactly
    worst = 0.0
    for _ in range(10):
        Md = sym(RNG.normal(size=(4, 4))) * RNG.uniform(0.1, 20.0)
        worst = max(worst, abs(l_curv_own([Md] + [np.zeros((4, 4))] * 3)))
    out["T_on_gradient_free_maxabs"] = worst
    # (c) eta null direction on random states with gradients
    worst = 0.0
    for _ in range(6):
        Ds = [sym(RNG.normal(size=(4, 4))) for _ in range(4)]
        Md = Ds[0]
        base = l_curv_own(Ds)
        shifted = l_curv_own([Md + 0.37 * ETA, Ds[1], Ds[2], Ds[3]])
        worst = max(worst, abs(shifted - base) / max(1.0, abs(base)))
    out["eta_null_shift_rel"] = worst
    # (d) no standalone quadratic term: T quadratic in Mdot with
    # M-DEPENDENT coefficient that -> 0 with the gradients
    Ds = [sym(RNG.normal(size=(4, 4))) for _ in range(4)]
    Md = sym(RNG.normal(size=(4, 4)))
    T = lambda m, s: (l_curv_own([m, s * Ds[1], s * Ds[2], s * Ds[3]])
                      - l_curv_own([np.zeros((4, 4)), s * Ds[1],
                                    s * Ds[2], s * Ds[3]]))
    out["T_quadratic_in_Mdot_rel"] = abs(T(2.0 * Md, 1.0)
                                         - 4.0 * T(Md, 1.0)) / abs(T(Md, 1.0))
    out["K_scales_as_grad_sq_rel"] = abs(T(Md, 0.5)
                                         - 0.25 * T(Md, 1.0)) / abs(T(Md, 1.0))
    # (e) own 10x10 kinetic assembly at loop cells; their normalization
    # (kin_form_apply) is T = sum_i <F,F> (factor-2 adjoint), so K_theirs
    # = 2 sum_i <[Ba,A_i],[Bb,A_i]>; census (rank/neg) is scale-free.
    M = seed4(DELTA, "pair_1d")
    basis = sym_basis4()
    census = []
    for (ci, cj) in ((17, 128), (80, 128)):
        # own channel values AT the cell, from raw M
        rho = (ci + 0.5) * H
        Am = M[ci - 1, cj] if ci >= 1 else MIR * M[0, cj]
        Ar = (M[ci + 1, cj] - Am) / (2.0 * H)
        Azl = (M[ci, cj + 1] - M[ci, cj - 1]) / (2.0 * H)
        Ap = (J4 @ M[ci, cj] - M[ci, cj] @ J4) / rho
        K = np.zeros((10, 10))
        for a in range(10):
            for b in range(a, 10):
                v = 0.0
                for A in (Ar, Ap, Azl):
                    v += inner_eta(comm_eta(basis[a], A),
                                   comm_eta(basis[b], A))
                K[a, b] = K[b, a] = 2.0 * v
        ev = np.linalg.eigvalsh(K)
        scale = max(np.abs(ev).max(), 1e-300)
        census.append({"cell": [ci, cj], "eigs": ev.tolist(),
                       "rank": int(np.sum(np.abs(ev) > 1e-10 * scale)),
                       "n_negative": int(np.sum(ev < -1e-10 * scale))})
    out["own_kin_census"] = census
    with open(os.path.join(DATA, "m5_20_2_a_eom.json")) as f:
        theirs = json.load(f)["kin_census_seed_d0p3_pair_1d"]
    cmp = []
    for mine in census:
        th = next(t for t in theirs if t["cell"] == mine["cell"])
        cmp.append({"cell": mine["cell"],
                    "rank_match": mine["rank"] == th["rank"],
                    "neg_match": mine["n_negative"] == th["n_negative"],
                    "eig_maxreldiff": float(np.max(np.abs(
                        np.array(mine["eigs"]) - np.array(th["eigs"])))
                        / max(abs(np.array(th["eigs"])).max(), 1e-300))})
    out["census_vs_theirs"] = cmp
    ok = (out["quartic_scaling_rel"] < 1e-12
          and out["T_on_gradient_free_maxabs"] < 1e-12
          and out["eta_null_shift_rel"] < 1e-12
          and out["T_quadratic_in_Mdot_rel"] < 1e-10
          and abs(out["K_scales_as_grad_sq_rel"]) < 1e-10
          and all(c["rank_match"] and c["neg_match"]
                  and c["eig_maxreldiff"] < 1e-9 for c in cmp))
    out["verdict"] = "CONFIRMED" if ok else "REFUTED"
    RESULT["C1"] = out
    print("[C1]", out["verdict"], json.dumps(
        {k: v for k, v in out.items()
         if not isinstance(v, list)}, default=str)[:300], flush=True)


# ============================ C2 =======================================
def c2():
    out = {}
    lam = np.array([G, 1.0, DELTA, 0.0])
    M0 = np.diag([-G, 1.0, DELTA, 0.0])
    basis = sym_basis4()

    def vp(M):
        v = 0.0
        P = np.eye(4)
        for p in range(1, 5):
            P = P @ (ETA @ M)
            v += (np.trace(P) - (G ** p + 1.0 + DELTA ** p)) ** 2
        return WSCALE * v

    # own analytic derivation: at the minimum, Hess = 2w sum_p g_p g_p^T,
    # g_p[dM = B] = p tr((eta M0)^{p-1} eta B); diagonal directions give
    # p lam_i^{p-1} eta_ii; off-diagonal directions give ZERO overlap
    Jt = np.array([[p * lam[i] ** (p - 1) * ETA[i, i] for i in range(4)]
                   for p in range(1, 5)])
    Ha = np.zeros((10, 10))
    Ha[:4, :4] = 2.0 * WSCALE * (Jt.T @ Jt)
    # own overlap check for off-diagonal directions (first-order grads)
    worst_off = 0.0
    for a in range(4, 10):
        for p in range(1, 5):
            gpa = p * np.trace(np.linalg.matrix_power(ETA @ M0, p - 1)
                               @ ETA @ basis[a])
            worst_off = max(worst_off, abs(gpa))
    out["offdiag_gradient_overlap_maxabs"] = worst_off
    # own FD Hessian (own eps, own stencil)
    eps = 2e-5
    Hn = np.zeros((10, 10))
    for a in range(10):
        for b in range(a, 10):
            val = (vp(M0 + eps * (basis[a] + basis[b]))
                   - vp(M0 + eps * (basis[a] - basis[b]))
                   - vp(M0 - eps * (basis[a] - basis[b]))
                   + vp(M0 - eps * (basis[a] + basis[b]))) / (4 * eps ** 2)
            Hn[a, b] = Hn[b, a] = val
    out["FD_vs_analytic_maxabsdiff"] = float(np.max(np.abs(Hn - Ha)))
    out["FD_vs_analytic_rel"] = out["FD_vs_analytic_maxabsdiff"] / float(
        np.max(np.abs(Ha)))
    ev = np.linalg.eigvalsh(Ha)
    out["n_zero_analytic"] = int(np.sum(np.abs(ev) < 1e-14))
    out["omegas"] = np.sqrt(np.maximum(ev, 0.0))[6:].tolist()
    claimed = [0.0093, 0.0466, 0.1349, 78.28]
    out["omega_vs_claimed_rel"] = [abs(o - c) / c for o, c in
                                   zip(out["omegas"], claimed)]
    # off-diagonal flats: quadratic-order flat, QUARTIC beyond, along
    # straight lines M0 + eps B (exponentiated orbit directions stay 0)
    quart = []
    for a in range(4, 10):
        v1, v2 = vp(M0 + 1e-2 * basis[a]), vp(M0 + 1e-3 * basis[a])
        quart.append(v1 / max(v2, 1e-300))   # expect ~1e4 (eps^4)
    out["offdiag_straightline_scaling_v(1e-2)/v(1e-3)"] = quart
    # exact orbit flats: V == 0 along finite boost + rotation orbits
    worst_orb = 0.0
    for (i, j) in ((0, 1), (0, 3), (1, 2), (2, 3)):
        W = np.zeros((4, 4))
        W[i, j], W[j, i] = 1.0, -1.0
        Lam = expm(0.8 * ETA @ W)
        Li = np.linalg.inv(Lam)
        worst_orb = max(worst_orb, vp(Li.T @ M0 @ Li))
    out["V_on_finite_orbit_maxabs"] = worst_orb
    ok = (out["offdiag_gradient_overlap_maxabs"] < 1e-14
          and out["FD_vs_analytic_rel"] < 1e-6
          and out["n_zero_analytic"] == 6
          and max(out["omega_vs_claimed_rel"]) < 5e-3
          and all(3e3 < r < 3e4 for r in quart)
          and worst_orb < 1e-18)
    out["verdict"] = "CONFIRMED" if ok else "REFUTED"
    RESULT["C2"] = out
    print("[C2]", out["verdict"],
          "omegas", np.round(out["omegas"], 4).tolist(),
          "nzero", out["n_zero_analytic"],
          "FDrel", f"{out['FD_vs_analytic_rel']:.1e}", flush=True)


# ============================ C3 =======================================
def own_evolve(M0, delta, T, dt, snap_every=0.25, abort_maxabs=50.0):
    """own velocity Verlet: w_cell Mddot = -dE/dM, precond 1/w, pinned
    boundary (outer rho + both z rows) frozen; reuses ONLY the public
    grad_static_4 / total_energy_4."""
    w = own_weights()
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = w
    wfull4 = wfull[..., None, None]
    pin = np.zeros((NR, NZ), dtype=bool)
    pin[-1, :] = True
    pin[:, 0] = True
    pin[:, -1] = True
    free4 = (~pin)[..., None, None].astype(float)
    w4 = own_weights()[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
    Mx = M0.copy()
    v = np.zeros_like(Mx)
    a = -grad_static_4(Mx, WSCALE, delta, w4=w4, rho4=rho4) / wfull4 * free4
    n = int(round(T / dt))
    se = max(1, int(round(snap_every / dt)))
    recs = []

    def snap(it):
        pe = total_energy_4(Mx, WSCALE, delta)
        ke = 0.5 * float(np.sum(wfull4 * v * v))
        ma = float(np.max(np.abs(Mx[..., 0, 1:])))
        recs.append({"t": it * dt, "PE": pe, "KE": ke, "E": pe + ke,
                     "maxabs_tm": ma})
        return recs[-1]

    snap(0)
    for it in range(1, n + 1):
        v += 0.5 * dt * a
        Mx += dt * v
        a = -grad_static_4(Mx, WSCALE, delta,
                           w4=w4, rho4=rho4) / wfull4 * free4
        v += 0.5 * dt * a
        if it % se == 0 or it == n:
            r = snap(it)
            if (not np.isfinite(r["E"])) or r["maxabs_tm"] > abort_maxabs:
                break
    return recs


def clock_inject(Mb, amp=0.02, center=(40.0, 0.0), sig=3.0):
    R, Z = own_grid()
    bump = amp * np.exp(-((R - center[0]) ** 2 + (Z - center[1]) ** 2)
                        / (2 * sig ** 2))
    out = Mb.copy()
    out[..., 0, 1] += bump
    out[..., 1, 0] += bump
    return out


def tdiv_of(recs):
    t_nan = next((r["t"] for r in recs if not np.isfinite(r["E"])),
                 None)
    t_1 = next((r["t"] for r in recs
                if np.isfinite(r["maxabs_tm"]) and r["maxabs_tm"] > 1.0),
               None)
    return t_nan, t_1


def c3():
    out = {}
    vacM = np.zeros((NR, NZ, 4, 4))
    vacM[..., :, :] = vac4(DELTA)
    for dt in (0.02, 0.005):
        t0 = time.time()
        recs = own_evolve(clock_inject(vacM), DELTA, 30.0, dt)
        t_nan, t_1 = tdiv_of(recs)
        out[f"vac4_clock_dt{dt}"] = {
            "t_maxabs_gt1": t_1, "t_nonfinite_or_abort": t_nan,
            "t_last": recs[-1]["t"], "maxabs_last": recs[-1]["maxabs_tm"],
            "wall_s": round(time.time() - t0, 1)}
        print(f"  [C3] vac4 clock dt={dt}: maxabs>1 at t={t_1}, "
              f"last t={recs[-1]['t']} maxabs={recs[-1]['maxabs_tm']:.3g} "
              f"({time.time()-t0:.0f}s)", flush=True)
    # J-commuting uniform background control (A_phi == 0 exactly)
    Mu = np.zeros((NR, NZ, 4, 4))
    Mu[..., 0, 0], Mu[..., 1, 1] = -G, 0.7
    Mu[..., 2, 2], Mu[..., 3, 3] = 0.7, 0.2
    t0 = time.time()
    recs = own_evolve(clock_inject(Mu), DELTA, 60.0, 0.01)
    t_nan, t_1 = tdiv_of(recs)
    ma = [r["maxabs_tm"] for r in recs]
    out["Jcommuting_uniform_control_dt0.01"] = {
        "background": "diag(-8, 0.7, 0.7, 0.2)",
        "t_maxabs_gt1": t_1, "t_nonfinite_or_abort": t_nan,
        "t_last": recs[-1]["t"], "maxabs_max": float(np.max(ma)),
        "maxabs_last": recs[-1]["maxabs_tm"],
        "E_drift_rel": abs(recs[-1]["E"] - recs[0]["E"])
        / max(abs(recs[0]["E"]), 1e-30),
        "wall_s": round(time.time() - t0, 1)}
    print(f"  [C3] J-commuting control: maxabs>1 at t={t_1}, last "
          f"t={recs[-1]['t']} maxabs_max={np.max(ma):.3g} "
          f"({time.time()-t0:.0f}s)", flush=True)
    # their reference divergence (dt = 0.01): finite at 21.0, nan at 21.5
    t02, t005 = (out["vac4_clock_dt0.02"]["t_maxabs_gt1"],
                 out["vac4_clock_dt0.005"]["t_maxabs_gt1"])
    div_robust = (t02 is not None and t005 is not None
                  and abs(t02 - t005) < 0.25 * 21.5)
    out["divergence_dt_robust"] = bool(div_robust)
    out["verdict"] = "CONFIRMED" if div_robust else "REFUTED"
    RESULT["C3"] = out
    print("[C3]", out["verdict"], flush=True)


# ============================ C4 =======================================
def gen(name):
    pairs = {"rot_J12": (1, 2), "rot_J13": (1, 3), "rot_J23": (2, 3),
             "boost_B01": (0, 1), "boost_B02": (0, 2),
             "boost_B03": (0, 3)}
    a, b = pairs[name]
    W = np.zeros((4, 4))
    W[a, b], W[b, a] = 1.0, -1.0
    return ETA @ W


def own_keff(M, Gm):
    Mc = M[: NR - 1, 1:-1]
    Md = -(Gm.T @ Mc + Mc @ Gm)
    dens = own_kin_dens(M, Md)
    return float(np.sum(dens * own_weights())), dens


def conj_state(M, Gm, phase):
    Lam = expm(phase * Gm)
    Li = np.linalg.inv(Lam)
    return np.einsum("ba,...bc,cd->...ad", Li, M, Li)   # Li.T M Li


def c4():
    out = {}
    with open(os.path.join(DATA, "m5_20_2_c_clock.json")) as f:
        theirs = json.load(f)["rows"]
    states = {"loop_seed_d0p3_pair_1d": seed4(DELTA, "pair_1d")}
    vacM = np.zeros((NR, NZ, 4, 4))
    vacM[..., :, :] = vac4(DELTA)
    states["vac4_background"] = vacM
    st = np.load(os.path.join(
        DATA, "m5_20_1_run_d0p3_pair_1d_closed_state.npz"))
    Mr = st["M0"].astype(np.float64)
    Mr[..., 0, 0] = -G
    states["remnant_d0p3_pair_1d"] = Mr
    Mb = np.zeros((NR, NZ, 4, 4))
    Mb[..., :, :] = vac4(DELTA, branch="one_timelike")
    states["vac4_one_timelike_branch"] = Mb

    # (a) recompute all 24 K_eff with own code; sign census
    rows = []
    sign_ok = True
    for sname, M in states.items():
        for gname in ("rot_J12", "rot_J13", "rot_J23", "boost_B01",
                      "boost_B02", "boost_B03"):
            K, dens = own_keff(M, gen(gname))
            th = next(r for r in theirs
                      if r["state"] == sname and r["generator"] == gname)
            rel = abs(K - th["K_eff"]) / max(abs(th["K_eff"]), 1e-12)
            rows.append({"state": sname, "gen": gname, "K_own": K,
                         "K_theirs": th["K_eff"], "rel": rel})
            if gname.startswith("rot") and K < -1e-9:
                sign_ok = False
            if gname.startswith("boost") and K > 1e-9:
                sign_ok = False
    out["keff_max_reldiff"] = max(r["rel"] for r in rows)
    out["sign_census_rot_ge0_boost_le0"] = bool(sign_ok)
    out["vac4_J12_zero"] = next(r["K_own"] for r in rows
                                if r["state"] == "vac4_background"
                                and r["gen"] == "rot_J12")
    out["vac4_B03_zero"] = next(r["K_own"] for r in rows
                                if r["state"] == "vac4_background"
                                and r["gen"] == "boost_B03")
    # boost 100% negative density on the loop seed
    _, dseed = own_keff(states["loop_seed_d0p3_pair_1d"], gen("boost_B01"))
    out["loopseed_B01_negfrac"] = float(np.sum(dseed < 0)
                                        / dseed.size) if np.all(
        dseed <= 1e-18) else float(-np.sum(dseed[dseed < 0])
                                   / np.sum(np.abs(dseed)))
    # (b) parabola by DIRECT evaluation at finite phase (axisym-valid
    # generators J12 / B03 only)
    para = []
    for sname in ("loop_seed_d0p3_pair_1d", "vac4_background"):
        M0 = states[sname]
        H0 = total_energy_4(M0, WSCALE, DELTA)
        for gname in ("rot_J12", "boost_B03"):
            Gm = gen(gname)
            K0, _ = own_keff(M0, Gm)
            for omega in (0.05, 0.12):
                for phase in (0.3, 0.9):
                    Mc = conj_state(M0, Gm, phase)
                    Es = total_energy_4(Mc, WSCALE, DELTA)
                    Kc, _ = own_keff(Mc, Gm)
                    Hdir = Es + omega ** 2 * Kc
                    Hpar = H0 + omega ** 2 * K0
                    den = max(abs(Hpar), abs(H0), 1.0)
                    para.append({"state": sname, "gen": gname,
                                 "omega": omega, "phase": phase,
                                 "H_direct": Hdir, "H_parabola": Hpar,
                                 "rel": abs(Hdir - Hpar) / den,
                                 "E_static_invariance_rel":
                                     abs(Es - H0) / max(abs(H0), 1.0)})
    out["parabola_max_rel"] = max(p["rel"] for p in para)
    out["static_invariance_max_rel"] = max(p["E_static_invariance_rel"]
                                           for p in para)
    out["parabola_rows"] = para
    # (c) velocity formula: FD of the conjugation orbit vs analytic
    M0 = states["loop_seed_d0p3_pair_1d"]
    Gm = gen("boost_B03")
    epss = 1e-6
    MdFD = (conj_state(M0, Gm, epss) - conj_state(M0, Gm, -epss)) / (2 * epss)
    Mdan = -(np.einsum("ba,...bc->...ac", Gm, M0)
             + np.einsum("...ab,bc->...ac", M0, Gm))
    out["velocity_formula_maxabsdiff"] = float(np.max(np.abs(MdFD - Mdan)))
    # note: the method-note quoted ranges vs the alternate branch
    alt = [r for r in rows if r["state"] == "vac4_one_timelike_branch"]
    out["alt_branch_extremes"] = {
        "max_rot": max(r["K_own"] for r in alt if r["gen"].startswith("rot")),
        "min_boost": min(r["K_own"] for r in alt
                         if r["gen"].startswith("boost"))}
    ok = (out["keff_max_reldiff"] < 1e-8 and sign_ok
          and abs(out["vac4_J12_zero"]) < 1e-9
          and abs(out["vac4_B03_zero"]) < 1e-9
          and out["parabola_max_rel"] < 1e-9
          and out["velocity_formula_maxabsdiff"] < 1e-6)
    out["verdict"] = "CONFIRMED" if ok else "REFUTED"
    RESULT["C4"] = out
    print("[C4]", out["verdict"],
          f"keff_rel {out['keff_max_reldiff']:.1e} "
          f"parab {out['parabola_max_rel']:.1e} "
          f"signs {sign_ok}", flush=True)


# ============================ C5 =======================================
def plaquette_scan(M, aniso_min=0.02):
    """own winding instrument: plaquette circulation of the (1,3)-block
    eigenframe angle 2*theta; a q = 1/2 defect carries 2*pi circulation."""
    sub = M[: NR - 1, 1:-1]
    m11, m33, m13 = sub[..., 1, 1], sub[..., 3, 3], sub[..., 1, 3]
    th2 = np.arctan2(2.0 * m13, m11 - m33)
    aniso = np.sqrt((m11 - m33) ** 2 + 4.0 * m13 ** 2)

    def wrap(d):
        return (d + np.pi) % (2.0 * np.pi) - np.pi

    circ = (wrap(th2[1:, :-1] - th2[:-1, :-1])
            + wrap(th2[1:, 1:] - th2[1:, :-1])
            + wrap(th2[:-1, 1:] - th2[1:, 1:])
            + wrap(th2[:-1, :-1] - th2[:-1, 1:]))
    amin4 = np.minimum(np.minimum(aniso[1:, :-1], aniso[:-1, :-1]),
                       np.minimum(aniso[1:, 1:], aniso[:-1, 1:]))
    guarded = np.abs(circ) * (amin4 > aniso_min)
    n_def = int(np.sum(guarded > np.pi))
    idx = np.argwhere(guarded > np.pi)
    defects = [{"rho": float((i + 0.5) * H),
                "z": float((j + 1 - NZ / 2 + 0.5) * H),
                "q": float(circ[i, j] / (4 * np.pi))}
               for i, j in idx[:10]]
    return {"n_defects": n_def, "total_abs_q":
            float(np.sum(np.abs(circ[amin4 > aniso_min])) / (4 * np.pi)),
            "defects": defects}


def c5():
    out = {}
    st = np.load(os.path.join(DATA, "m5_20_2_run_protection_state.npz"))
    Me = st["M0"].astype(np.float64)
    # frozen-row integrity of the endpoint
    out["M00_min_max"] = [float(Me[..., 0, 0].min()),
                          float(Me[..., 0, 0].max())]
    out["M0i_maxabs"] = float(np.max(np.abs(Me[..., 0, 1:])))
    # own winding read: seed (positive control) vs endpoint
    Ms = seed4(DELTA, "pair_1d")
    out["plaquette_seed"] = plaquette_scan(Ms)
    out["plaquette_endpoint"] = plaquette_scan(Me)
    # energy ledger from their trajectory + own endpoint recompute
    with open(os.path.join(DATA, "m5_20_2_run_protection.json")) as f:
        run = json.load(f)
    tr = run["trajectory"]
    E = np.array([r["E_tot"] for r in tr])
    out["ledger_maxdev_rel"] = float(np.max(np.abs(E - E[0])) / abs(E[0]))
    pe_own = own_energy(Me)
    out["PE_endpoint_own"] = pe_own
    out["PE_endpoint_ledger"] = tr[-1]["PE"]
    out["PE_recompute_rel"] = abs(pe_own - tr[-1]["PE"]) / abs(tr[-1]["PE"])
    out["E0_own_vs_ledger_rel"] = abs(own_energy(Ms) - tr[0]["PE"]) / abs(
        tr[0]["PE"])
    # positive control: the seed must carry a q = +1/2 defect at the ring
    # core (R0 = 17, z = 0). A compensating -1/2 at the blend shell is
    # topologically REQUIRED (uniform far field => zero net winding), so
    # the correct expectation is core defect present, not total = 0.5.
    seed_wound = any(abs(d["rho"] - 17.0) < 3.0 and abs(d["z"]) < 3.0
                     and abs(d["q"] - 0.5) < 0.1
                     for d in out["plaquette_seed"]["defects"])
    out["seed_core_defect_found"] = bool(seed_wound)
    ok = (seed_wound
          and out["plaquette_endpoint"]["n_defects"] == 0
          and out["plaquette_endpoint"]["total_abs_q"] < 0.1
          and abs(out["M00_min_max"][0] + G) < 1e-5
          and abs(out["M00_min_max"][1] + G) < 1e-5
          and out["M0i_maxabs"] < 1e-6
          and out["ledger_maxdev_rel"] < 1e-5
          and out["PE_recompute_rel"] < 1e-3)   # float32 state
    out["verdict"] = "CONFIRMED" if ok else "REFUTED"
    RESULT["C5"] = out
    print("[C5]", out["verdict"],
          "seed defects", out["plaquette_seed"]["n_defects"],
          "q", round(out["plaquette_seed"]["total_abs_q"], 3),
          "| endpoint defects", out["plaquette_endpoint"]["n_defects"],
          "q", round(out["plaquette_endpoint"]["total_abs_q"], 4),
          "| ledger", f"{out['ledger_maxdev_rel']:.1e}",
          "PEown rel", f"{out['PE_recompute_rel']:.1e}", flush=True)


# ============================ C6 =======================================
def c6():
    out = {}
    M = seed4(DELTA, "pair_1d")          # spatial-block field, time row -g
    # own u_eta vs the frozen M5.17 plain curvature
    ue = own_u_eta(M)
    up = curvature_density_np(M, H, 1.0)
    out["u_eta_vs_plain_rel"] = float(np.max(np.abs(ue - up))
                                      / max(np.max(np.abs(up)), 1e-300))
    # own V4 (p<=3) vs own direct 3-target on the spatial block
    v4r = own_v4(M, pmax=3)
    msp = M[: NR - 1, 1:-1, 1:4, 1:4]
    v3 = 0.0
    P = np.broadcast_to(np.eye(3), msp.shape)
    for p in range(1, 4):
        P = P @ msp
        v3 = v3 + (np.einsum("...aa->...", P) - (1.0 + DELTA ** p)) ** 2
    v3 = WSCALE * v3
    out["v4_p3_vs_3target_rel"] = float(np.max(np.abs(v4r - v3))
                                        / max(np.max(np.abs(v3)), 1e-300))
    # algebra: with block-diag time row, tr((eta M)^p) = g^p + tr(Msp^p)
    Mt = M[40, 100]
    worst = 0.0
    for p in range(1, 5):
        lhs = np.trace(np.linalg.matrix_power(ETA @ Mt, p))
        rhs = G ** p + np.trace(np.linalg.matrix_power(Mt[1:, 1:], p))
        worst = max(worst, abs(lhs - rhs))
    out["blockdiag_trace_identity_maxabs"] = worst
    ok = (out["u_eta_vs_plain_rel"] < 1e-12
          and out["v4_p3_vs_3target_rel"] < 1e-9
          and worst < 1e-9)
    out["verdict"] = "CONFIRMED" if ok else "REFUTED"
    RESULT["C6"] = out
    print("[C6]", out["verdict"], json.dumps(
        {k: v for k, v in out.items() if k != "verdict"})[:220], flush=True)


def main():
    which = ARGV if ARGV else ["c1", "c2", "c6", "c5", "c4", "c3"]
    if which == ["all"]:
        which = ["c1", "c2", "c6", "c5", "c4", "c3"]
    fns = {"c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5, "c6": c6}
    for w in which:
        fns[w]()
    path = os.path.join(DATA, "m5_20_2_audit.json")
    old = {}
    if os.path.exists(path):
        with open(path) as f:
            old = json.load(f)
    old.update(RESULT)
    with open(path, "w") as f:
        json.dump(old, f, indent=1, default=float)
    print("wrote", path, flush=True)


if __name__ == "__main__":
    main()
