"""M5.16 P-A/P-B/P-D: the axisymmetric (rho, z) energy-minimization instrument.

Graduates the M5.11-P0 static minimizer to Duda's cylindrical-symmetry
reduction (m5_4e 2026-07-01: "for both electron and neutrino we can assume
cylindrical symmetry to reduce dimension"), the enabling step for the
physical-regime parameter lock (task m5_16_task_details.md).

CONVENTION (Duda index-0): M is 4x4, D = diag(g, 1, delta, 0), time/g axis =
array index 0, spatial block = [1:4, 1:4], eta = diag(-1, 1, 1, 1). V_M acts
on the spatial block only (the engine freezes the boost-decoupled g axis).
The static electron sector is exactly g-decoupled (gate G8 measures this).

REDUCTION (P-B). Equivariant ansatz
    M(rho, phi, z) = R12(phi) . Mt(rho, z) . R12(phi)^T
with R12 the rotation in the spatial (1,2) plane. At phi = 0:
    M_x = d_rho Mt,    M_y = (1/rho) [J, Mt],    M_z = d_z Mt,
J = dR12/dphi at 0 (J[1,2] = -1, J[2,1] = +1). The 3D functional
    U = c2 . 4 . sum_{mu<nu} ||[d_mu M, d_nu M]||_F^2  +  (V_M - V_vac),
    V_M = a Tr(Msp^2) - b Tr(Msp^3) + c (Tr Msp^2)^2
(the engine2_pde / m5_11_p0 form) reduces exactly to the (rho, z) half-plane
with volume weight 2 pi rho drho dz. The axis rho = 0 uses a cell-centered
rho grid (rho_i = (i + 1/2) h) plus the mirror ghost
    Mt(-rho, z) = P . Mt(rho, z) . P,    P = diag(1, -1, -1, 1)
(the phi = pi image), so no one-sided bias at the axis (P-D core handling).

ANALYTIC ANCHORS derived for the gates (2026-07-02 design notes,
findings/m5_16_checkpoints.md):
  - pure hedgehog M = rhat rhat^T (s = 1): the only nonzero commutator at
    rhat = zhat is [d_x M, d_y M] = e1 e2^T - e2 e1^T, norm^2 = 2, so the
    curvature density is exactly 8 c2 / r^4 (gate G3), and a spherical shell
    integrates to 32 pi c2 (1/r1 - 1/r2) (gate G4).
  - LdG with zero-forcing at the uniaxial vacuum s = 1: a = (3b - 4c)/2,
    melt cost = c - b/2 > 0, free ratio beta = b/c in (0, 2).

MINIMIZERS: preconditioned FIRE (P0 heritage) and nonlinear conjugate
gradient, Polak-Ribiere update + bracketing/golden-section line search
(the Faber-group recipe, m5_4g_convo_2026.07.02.md), run as independent
cross-checks (relax gate R5).

GATES (all must pass before any physics claim):
  G1 numpy density mirror == taichi total          (rel 1e-12)
  G2 AD gradient == central finite difference      (rel 1e-6, incl. axis i=0)
  G3 hedgehog curvature density . r^4 == 8         (2%, FD-limited)
  G4 shell energy == 32 pi (1/r1 - 1/r2)           (2%)
  G5 slab-3D energy == m5_11_p0 total_energy       (rel 1e-12, tiny box)
  G6 2D reduced energy == 3D energy, h-refinement  (<0.5% at h/2, shrinking)
  G7 global-frame invariance R12(0.3) conjugation  (rel 1e-11)
  G8 g-decoupling: E(g=8) == E(g=1e10)             (rel 1e-15)
RELAX-STAGE (pre-registered): R1 monotone descent, R2 gnorm drop > 3 decades,
  R3 sphericity < 2%, R4 virial E_curv = 3 E_pot within 10% (finite-box
  limited, reported), R5 FIRE vs CG energy agreement < 1e-6 relative.

PHYSICS SINGLE-SOURCE (M5.17 phase A, 2026-07-03): the energy functional,
potential, analytic gradient, anchors, and seeds were extracted VERBATIM into
m5_17_energy.py (equations in its docstring; the methods note maps them to
line numbers). This file is the DRIVER: CLI, Taichi cross-check engine,
minimizers, observables, gates, run modes. The gate suite re-ran green on the
refactored stack with bit-identical energies.

Run:
  python m5_16_axisym.py gates  [NR NZ]
  python m5_16_axisym.py relax  [NR NZ] --beta 1.0 --cscale 2e-3 \
         --rc 8 --iters 30000 --autochi 1 --tag b100
Outputs: ../data/m5_16_axisym_<tag>.json (small; no file > 1 MB).
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
os.makedirs(DATA, exist_ok=True)
sys.path.insert(0, HERE)

# THE PHYSICS lives in m5_17_energy.py (the auditable single-source module,
# extracted verbatim M5.17 phase A; equations in its docstring + the methods
# note). This driver adds CLI, minimizers, observables, gates, run modes.
from m5_17_energy import (  # noqa: E402
    PI, G_TIME, MIR, MIR_T, J4, ldg_coeffs, _comm_np, _norm2_np,
    curvature_density_np, potential_density_np, cell_weights,
    energy_gradient_np, total_energy_np, ext_tail,
    grid_coords, hedgehog_field, hedgehog_3d,
)

# ---------------- CLI ----------------
MODE = sys.argv[1] if len(sys.argv) > 1 else "gates"
_pos = [a for a in sys.argv[2:] if not a.startswith("--")]
NR = int(_pos[0]) if len(_pos) > 0 else 48
NZ = int(_pos[1]) if len(_pos) > 1 else 96


def _flag(name, default, cast=float):
    for i, a in enumerate(sys.argv):
        if a == "--" + name and i + 1 < len(sys.argv):
            return cast(sys.argv[i + 1])
    return default


BETA = _flag("beta", 1.0)
CSCALE = _flag("cscale", 2e-3)
RC_SEED = _flag("rc", 8.0)
ITERS = _flag("iters", 30000, int)
AUTOCHI = _flag("autochi", 1, int)
TAG = _flag("tag", "run", str)
H = 1.0                            # grid unit; physical scale enters analytically


# ---------------- taichi energy + AD gradient (OPTIONAL cross-check engine) ----
# The production engine of this script is the ANALYTIC numpy gradient below
# (gate G2 validates it against finite differences). Taichi AD is kept as an
# independent cross-check (gates G1/G2b, flag --ti 1): its kernel JIT compile
# was observed pathologically slow on this kernel shape (>15 min), so it must
# never sit on the calibration path.
_TI = {}


def _init_taichi():
    if _TI:
        return _TI
    import taichi as ti

    ti.init(arch=ti.cpu, default_fp=ti.f64, offline_cache=True, random_seed=0)
    M = ti.Matrix.field(4, 4, ti.f64, shape=(NR, NZ), needs_grad=True)
    loss = ti.field(ti.f64, shape=(), needs_grad=True)
    par = ti.field(ti.f64, shape=(8,))   # a b c c2 h vvac (2 spare)

    @ti.kernel
    def compute_energy():
        # curvature: included cells i in [0, NR-2], j in [1, NZ-2]; ghost at i=0
        for i, j in ti.ndrange((0, NR - 1), (1, NZ - 1)):
            c2 = par[3]
            h = par[4]
            inv2h = 1.0 / (2.0 * h)
            rho = (i + 0.5) * h
            w = 2.0 * PI * rho * h * h
            Mm = ti.Matrix.zero(ti.f64, 4, 4)
            if i > 0:
                Mm = M[i - 1, j]
            else:
                Mc0 = M[0, j]
                for p in ti.static(range(4)):
                    for q in ti.static(range(4)):
                        Mm[p, q] = MIR_T[p][q] * Mc0[p, q]
            Mrho = (M[i + 1, j] - Mm) * inv2h
            Mz = (M[i, j + 1] - M[i, j - 1]) * inv2h
            Mc = M[i, j]
            Jm = ti.Matrix.zero(ti.f64, 4, 4)
            Jm[1, 2] = -1.0
            Jm[2, 1] = 1.0
            Mphi = (Jm @ Mc - Mc @ Jm) * (1.0 / rho)
            cxy = Mrho @ Mphi - Mphi @ Mrho
            cxz = Mrho @ Mz - Mz @ Mrho
            cyz = Mphi @ Mz - Mz @ Mphi
            loss[None] += c2 * 4.0 * (cxy.norm_sqr() + cxz.norm_sqr()
                                      + cyz.norm_sqr()) * w
        # potential (relative to the vacuum) over the same included cells
        for i, j in ti.ndrange((0, NR - 1), (1, NZ - 1)):
            a = par[0]
            b = par[1]
            c = par[2]
            h = par[4]
            vvac = par[5]
            rho = (i + 0.5) * h
            w = 2.0 * PI * rho * h * h
            m = M[i, j]
            tr2 = 0.0
            tr3 = 0.0
            for p in ti.static(range(1, 4)):
                for q in ti.static(range(1, 4)):
                    tr2 += m[p, q] * m[q, p]
            for p in ti.static(range(1, 4)):
                for q in ti.static(range(1, 4)):
                    for r in ti.static(range(1, 4)):
                        tr3 += m[p, q] * m[q, r] * m[r, p]
            loss[None] += (a * tr2 - b * tr3 + c * tr2 * tr2 - vvac) * w

    _TI.update({"ti": ti, "M": M, "loss": loss, "par": par,
                "kernel": compute_energy})
    return _TI


def energy_and_grad_ti(M_np, a, b, c, c2, h, vvac):
    T = _init_taichi()
    T["M"].from_numpy(M_np)
    T["par"].from_numpy(np.array([a, b, c, c2, h, vvac, 0.0, 0.0]))
    T["loss"][None] = 0.0
    with T["ti"].ad.Tape(loss=T["loss"]):
        T["kernel"]()
    return float(T["loss"][None]), T["M"].grad.to_numpy()


def energy_only_ti(M_np, a, b, c, c2, h, vvac):
    T = _init_taichi()
    T["M"].from_numpy(M_np)
    T["par"].from_numpy(np.array([a, b, c, c2, h, vvac, 0.0, 0.0]))
    T["loss"][None] = 0.0
    T["kernel"]()
    return float(T["loss"][None])


def pin_mask(nr, nz):
    """True where the DOF is pinned: outer rho boundary + both z boundaries.
    The axis (i=0) is FREE (mirror ghost handles it)."""
    m = np.zeros((nr, nz), dtype=bool)
    m[-1, :] = True
    m[:, 0] = True
    m[:, -1] = True
    return m


# ---------------- minimizers ----------------
def fire_relax(M0, egf, free4, precond, max_iter=30000, tol_rel=1e-5,
               dt0=0.02, dt_max=0.2, log_every=1000):
    """preconditioned FIRE. egf(M) -> (E, grad). precond = per-cell 1/w scaling
    (positive diagonal metric); pinned DOF forced to zero force."""
    Mx = M0.copy()
    v = np.zeros_like(Mx)
    dt = dt0
    alpha = 0.1
    n_pos = 0
    E, g = egf(Mx)
    g = g * free4
    g0n = float(np.sqrt(np.sum(g * g)))
    hist = {"E": [E], "gnorm": [g0n], "iter": [0]}
    for it in range(1, max_iter + 1):
        F = -g * precond
        v = v + dt * F
        P = float(np.sum(F * v))
        fn = np.sqrt(np.sum(F * F))
        vn = np.sqrt(np.sum(v * v))
        if fn > 0:
            v = (1 - alpha) * v + alpha * (vn / (fn + 1e-30)) * F
        if P > 0:
            n_pos += 1
            if n_pos > 5:
                dt = min(dt * 1.1, dt_max)
                alpha *= 0.99
        else:
            n_pos = 0
            dt *= 0.5
            alpha = 0.1
            v[:] = 0.0
        Mx = Mx + dt * v
        E, g = egf(Mx)
        g = g * free4
        gn = float(np.sqrt(np.sum(g * g)))
        if it % log_every == 0 or it == max_iter:
            hist["E"].append(E)
            hist["gnorm"].append(gn)
            hist["iter"].append(it)
        if gn < tol_rel * g0n or gn < 1e-9:
            hist["E"].append(E)
            hist["gnorm"].append(gn)
            hist["iter"].append(it)
            break
    return Mx, hist


def golden_line(f, t_hi_guess):
    """bracket [0, t_hi] with expansion, then golden-section. f(0) known smallest
    direction-descent assumed; returns t_min."""
    f0 = f(0.0)
    t1 = t_hi_guess
    f1 = f(t1)
    # expand until rise
    t_prev, f_prev = 0.0, f0
    while f1 < f_prev and t1 < t_hi_guess * 1e6:
        t_prev, f_prev = t1, f1
        t1 *= 2.0
        f1 = f(t1)
    lo, hi = 0.0, t1
    invphi = (np.sqrt(5.0) - 1.0) / 2.0
    a_, b_ = hi - invphi * (hi - lo), lo + invphi * (hi - lo)
    fa, fb = f(a_), f(b_)
    for _ in range(48):
        if fa < fb:
            hi, b_, fb = b_, a_, fa
            a_ = hi - invphi * (hi - lo)
            fa = f(a_)
        else:
            lo, a_, fa = a_, b_, fb
            b_ = lo + invphi * (hi - lo)
            fb = f(b_)
        if (hi - lo) < 1e-10 * max(1.0, t_hi_guess):
            break
    return 0.5 * (lo + hi)


def prcg_relax(M0, egf, ef, free4, precond, iters=300, tol_rel=1e-7):
    """nonlinear CG, Polak-Ribiere + bracketing/golden-section line search
    (the Faber-group recipe, m5_4g). Preconditioned: z = precond*g."""
    Mx = M0.copy()
    E, g = egf(Mx)
    g = g * free4
    z = g * precond
    d = -z
    g0n = float(np.sqrt(np.sum(g * g)))
    hist = {"E": [E], "gnorm": [g0n], "iter": [0]}
    gz = float(np.sum(g * z))
    for it in range(1, iters + 1):
        dn = float(np.sqrt(np.sum(d * d)))
        if dn == 0.0:
            break
        t_guess = min(0.1, 1.0 / dn)

        def f(t):
            return ef(Mx + t * d)

        t = golden_line(f, t_guess)
        if t <= 0.0:
            t = t_guess * 1e-3
        Mx = Mx + t * d
        E2, g2 = egf(Mx)
        g2 = g2 * free4
        z2 = g2 * precond
        gz2 = float(np.sum(g2 * z2))
        beta_pr = max(0.0, float(np.sum(g2 * (z2 - z))) / (gz + 1e-300))
        d = -z2 + beta_pr * d
        if float(np.sum(d * g2)) > 0.0:
            d = -z2
        g, z, gz, E = g2, z2, gz2, E2
        gn = float(np.sqrt(np.sum(g * g)))
        if it % 25 == 0 or it == iters:
            hist["E"].append(E)
            hist["gnorm"].append(gn)
            hist["iter"].append(it)
        if gn < tol_rel * g0n or gn < 1e-10:
            hist["E"].append(E)
            hist["gnorm"].append(gn)
            hist["iter"].append(it)
            break
    return Mx, hist


# ---------------- observables ----------------
def observables(Mnp, a, b, c, c2, h, vvac):
    """energy split + r_half + s(r) profile + sphericity, tail-corrected."""
    nr, nz = Mnp.shape[:2]
    w = cell_weights(nr, nz, h)
    dcurv = curvature_density_np(Mnp, h, c2)
    dpot = potential_density_np(Mnp, a, b, c, vvac)
    E_curv_num = float(np.sum(dcurv * w))
    E_pot_num = float(np.sum(dpot * w))
    Rc = (nr - 1) * h                 # included-cell outer rho edge
    Hh = (nz / 2 - 1) * h
    E_ext = c2 * ext_tail(Rc, Hh)   # s=1 vacuum-hedgehog density 8 c2/r^4 outside the box
    E_tot = E_curv_num + E_pot_num + E_ext
    # radial binning on included cells
    RHO, ZZ = grid_coords(nr, nz, h)
    Rin = np.sqrt(RHO[: nr - 1, 1:-1] ** 2 + ZZ[: nr - 1, 1:-1] ** 2)
    dens = (dcurv + dpot) * w
    rmax = min(Rc, Hh)
    nbins = int(rmax / (0.5 * h))
    edges = np.linspace(0.0, rmax, nbins + 1)
    idx = np.clip(np.digitize(Rin.ravel(), edges) - 1, 0, nbins - 1)
    e_r = np.bincount(idx, weights=dens.ravel(), minlength=nbins)
    inside = (Rin < rmax).ravel()
    e_r_in = np.bincount(idx[inside], weights=dens.ravel()[inside], minlength=nbins)
    cum = np.cumsum(e_r_in)
    # energy beyond the r<rmax ball: numeric remainder + analytic exterior
    E_beyond = E_tot - float(cum[-1])
    target = 0.5 * E_tot
    k = int(np.searchsorted(cum, target))
    if 0 < k < nbins:
        r_lo, r_hi = edges[k], edges[k + 1]
        c_lo = cum[k - 1]
        frac = (target - c_lo) / max(cum[k] - c_lo, 1e-300)
        r_half = r_lo + frac * (r_hi - r_lo)
    else:
        r_half = float("nan")
    # s(r) profile: largest eigenvalue of the spatial block
    msp = Mnp[: nr - 1, 1:-1, 1:4, 1:4]
    s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    cnt = np.bincount(idx, minlength=nbins).astype(float)
    s_r = np.bincount(idx, weights=s_cell.ravel(), minlength=nbins) / np.maximum(cnt, 1)
    # sphericity: equatorial (|z| < rho/2) vs polar (|z| > 2 rho) s(r)
    eq = (np.abs(ZZ[: nr - 1, 1:-1]) < 0.5 * RHO[: nr - 1, 1:-1]).ravel()
    po = (np.abs(ZZ[: nr - 1, 1:-1]) > 2.0 * RHO[: nr - 1, 1:-1]).ravel()
    s_eq = np.bincount(idx[eq], weights=s_cell.ravel()[eq], minlength=nbins)
    n_eq = np.bincount(idx[eq], minlength=nbins).astype(float)
    s_po = np.bincount(idx[po], weights=s_cell.ravel()[po], minlength=nbins)
    n_po = np.bincount(idx[po], minlength=nbins).astype(float)
    both = (n_eq > 3) & (n_po > 3)
    if np.any(both):
        spher = float(np.max(np.abs(s_eq[both] / n_eq[both] - s_po[both] / n_po[both])))
    else:
        spher = float("nan")
    virial = E_curv_num + E_ext  # total curvature incl. analytic tail
    return {
        "E_curv_num": E_curv_num, "E_pot_num": E_pot_num, "E_ext_tail": E_ext,
        "E_tot": E_tot, "E_beyond_rmax_ball": E_beyond,
        "virial_ratio_curv_over_3pot": virial / (3.0 * E_pot_num) if E_pot_num != 0 else float("inf"),
        "r_half": float(r_half), "sphericity_max_ds": spher,
        "r_bins": (0.5 * (edges[:-1] + edges[1:])).tolist(),
        "s_profile": s_r.tolist(),
        "e_shell": e_r.tolist(),
    }


# ---------------- gates ----------------
def gate_np_vs_ti(seed=0):
    rng = np.random.default_rng(seed)
    R, Z = grid_coords(NR, NZ, H)
    Mnp = hedgehog_field(R, Z, r_c=6.0)
    pert = rng.standard_normal((NR, NZ, 3, 3)) * 0.05
    Mnp[..., 1:4, 1:4] += 0.5 * (pert + np.swapaxes(pert, -1, -2))
    a, b, c, vvac = ldg_coeffs(1.0, 2e-3)
    E_ti = energy_only_ti(Mnp, a, b, c, 1.0, H, vvac)
    E_np = total_energy_np(Mnp, a, b, c, 1.0, H, vvac)
    rel = abs(E_ti - E_np) / (abs(E_np) + 1e-300)
    _, g_ti = energy_and_grad_ti(Mnp, a, b, c, 1.0, H, vvac)
    g_np = energy_gradient_np(Mnp, a, b, c, 1.0, H, vvac)
    grel = float(np.max(np.abs(g_ti - g_np)) / (np.max(np.abs(g_np)) + 1e-300))
    return {"gate": "G1_np_vs_ti", "ok": bool(rel < 1e-12 and grel < 1e-11),
            "E_ti": E_ti, "E_np": E_np, "rel": rel, "grad_rel": grel}


def gate_gradcheck(seed=1):
    rng = np.random.default_rng(seed)
    R, Z = grid_coords(NR, NZ, H)
    Mnp = hedgehog_field(R, Z, r_c=6.0)
    pert = rng.standard_normal((NR, NZ, 3, 3)) * 0.05
    Mnp[..., 1:4, 1:4] += 0.5 * (pert + np.swapaxes(pert, -1, -2))
    a, b, c, vvac = ldg_coeffs(1.0, 2e-3)

    def E(MM):
        return total_energy_np(MM, a, b, c, 1.0, H, vvac)

    g = energy_gradient_np(Mnp, a, b, c, 1.0, H, vvac)
    eps = 1e-6
    pts = [(0, NZ // 2), (0, NZ // 3), (2, NZ // 2), (NR // 3, NZ // 2),
           (NR // 2, 2 * NZ // 3), (NR - 3, NZ // 2)]
    comps = [(1, 1), (1, 2), (2, 3), (3, 3)]
    errs = []
    for (i, j) in pts:
        for (p, q) in comps:
            Mp = Mnp.copy()
            Mm = Mnp.copy()
            Mp[i, j, p, q] += eps
            Mp[i, j, q, p] += eps if p != q else 0.0
            Mm[i, j, p, q] -= eps
            Mm[i, j, q, p] -= eps if p != q else 0.0
            num = (E(Mp) - E(Mm)) / (2 * eps)
            ana = g[i, j, p, q] + (g[i, j, q, p] if p != q else 0.0)
            errs.append(abs(num - ana) / (abs(num) + abs(ana) + 1e-12))
    mx = float(np.max(errs))
    return {"gate": "G2_gradcheck", "ok": bool(mx < 1e-6), "max_rel": mx,
            "n": len(errs)}


def gate_hh_density():
    R, Z = grid_coords(NR, NZ, H)
    Mnp = hedgehog_field(R, Z, r_c=-1.0)   # s = 1 pure director
    d = curvature_density_np(Mnp, H, 1.0)
    Rin = np.sqrt(R[: NR - 1, 1:-1] ** 2 + Z[: NR - 1, 1:-1] ** 2)
    band = (Rin > 10.0) & (Rin < 0.7 * min((NR - 1) * H, (NZ / 2 - 1) * H))
    vals = (d * Rin ** 4)[band]
    med = float(np.median(vals))
    rel = abs(med - 8.0) / 8.0
    return {"gate": "G3_hh_density", "ok": bool(rel < 0.02), "median_d_r4": med,
            "expected": 8.0, "rel": rel, "n_cells": int(np.sum(band))}


def gate_shell():
    R, Z = grid_coords(NR, NZ, H)
    Mnp = hedgehog_field(R, Z, r_c=-1.0)
    d = curvature_density_np(Mnp, H, 1.0)
    w = cell_weights(NR, NZ, H)
    Rin = np.sqrt(R[: NR - 1, 1:-1] ** 2 + Z[: NR - 1, 1:-1] ** 2)
    r1, r2 = 10.0, 0.85 * min((NR - 1) * H, (NZ / 2 - 1) * H)
    mask = (Rin >= r1) & (Rin < r2)
    E_num = float(np.sum((d * w)[mask]))
    E_an = 32.0 * PI * (1.0 / r1 - 1.0 / r2)
    rel = abs(E_num - E_an) / E_an
    return {"gate": "G4_shell", "ok": bool(rel < 0.02), "E_num": E_num,
            "E_analytic": E_an, "rel": rel, "r1": r1, "r2": r2}


def _slab_energy_3d(N3, h, r_c, a, b, c, vvac, Rmask, Zmask):
    """3D energy on cell-centered box, slab-wise in z (memory-bounded), masked to
    the cylinder rho<=Rmask, |z|<=Zmask; interior central differences."""
    xs = (np.arange(N3) + 0.5 - N3 / 2) * h
    X2, Y2 = np.meshgrid(xs, xs, indexing="ij")
    total = 0.0
    for k in range(1, N3 - 1):
        Ms = [hedgehog_3d(X2, Y2, np.full_like(X2, xs[k + dk]), r_c)
              for dk in (-1, 0, 1)]
        Mx = (Ms[1][2:, 1:-1] - Ms[1][:-2, 1:-1]) / (2 * h)
        My = (Ms[1][1:-1, 2:] - Ms[1][1:-1, :-2]) / (2 * h)
        Mz = (Ms[2][1:-1, 1:-1] - Ms[0][1:-1, 1:-1]) / (2 * h)
        dcurv = 4.0 * (_norm2_np(_comm_np(Mx, My)) + _norm2_np(_comm_np(Mx, Mz))
                       + _norm2_np(_comm_np(My, Mz)))
        msp = Ms[1][1:-1, 1:-1, 1:4, 1:4]
        m2 = np.einsum("...ab,...bc->...ac", msp, msp)
        tr2 = np.einsum("...aa->...", m2)
        tr3 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, msp))
        dpot = a * tr2 - b * tr3 + c * tr2 * tr2 - vvac
        rho2 = np.sqrt(X2[1:-1, 1:-1] ** 2 + Y2[1:-1, 1:-1] ** 2)
        mask = (rho2 <= Rmask) & (abs(xs[k]) <= Zmask)
        total += float(np.sum((dcurv + dpot) * mask)) * h ** 3
    return total


def gate_slab_vs_p0(seed=2):
    """the slab-3D evaluator == m5_11_p0.total_energy on a tiny random box
    (anchors the 3D reference in the validated P0 lineage)."""
    sys.path.insert(0, HERE)
    import m5_11_p0_minimizer as p0
    rng = np.random.default_rng(seed)
    n = 8
    h = 0.7
    a, b, c = 0.4, 0.2, 0.3
    Mnp = np.zeros((n, n, n, 4, 4))
    Rr = rng.standard_normal((n, n, n, 3, 3)) * 0.3
    Mnp[..., 1:4, 1:4] = 0.5 * (Rr + np.swapaxes(Rr, -1, -2))
    Mnp[..., 0, 0] = G_TIME
    # P0 keeps partial curvature cross-terms at axis-boundary FACE voxels (its
    # per-axis zero-filled derivative arrays), a boundary-layer counting choice
    # that vanishes in the continuum. This gate tests FORMULA equivalence, so
    # compare on the full-interior region where both conventions coincide.
    dens_p0 = p0.energy_density(Mnp, a, b, c, h, 3, 1.0)
    E_p0 = float(np.sum(dens_p0[1:-1, 1:-1, 1:-1]) * h ** 3)
    # same field through the slab evaluator's formulas (no mask, no vvac)
    total = 0.0
    for k in range(1, n - 1):
        Mx = (Mnp[2:, 1:-1, k] - Mnp[:-2, 1:-1, k]) / (2 * h)
        My = (Mnp[1:-1, 2:, k] - Mnp[1:-1, :-2, k]) / (2 * h)
        Mz = (Mnp[1:-1, 1:-1, k + 1] - Mnp[1:-1, 1:-1, k - 1]) / (2 * h)
        dcurv = 4.0 * (_norm2_np(_comm_np(Mx, My)) + _norm2_np(_comm_np(Mx, Mz))
                       + _norm2_np(_comm_np(My, Mz)))
        msp = Mnp[1:-1, 1:-1, k, 1:4, 1:4]
        m2 = np.einsum("...ab,...bc->...ac", msp, msp)
        tr2 = np.einsum("...aa->...", m2)
        tr3 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, msp))
        dpot = a * tr2 - b * tr3 + c * tr2 * tr2
        total += float(np.sum(dcurv + dpot)) * h ** 3
    rel = abs(total - E_p0) / (abs(E_p0) + 1e-300)
    return {"gate": "G5_slab_vs_p0", "ok": bool(rel < 1e-12), "E_slab": total,
            "E_p0": E_p0, "rel": rel}


def gate_equiv3d():
    """2D reduced energy == 3D energy of the reconstructed field, refining h.
    Same analytic melted hedgehog, same cylinder mask, both Riemann sums of the
    same integral: the difference must shrink ~h^2."""
    a, b, c, vvac = ldg_coeffs(1.0, 2e-3)
    r_c = 6.0
    Rmask, Zmask = 30.0, 30.0
    diffs = {}
    for h, n3, nr2, nz2 in ((1.0, 72, 40, 80), (0.5, 144, 80, 160)):
        E3 = _slab_energy_3d(n3, h, r_c, a, b, c, vvac, Rmask, Zmask)
        R, Z = grid_coords(nr2, nz2, h)
        Mnp = hedgehog_field(R, Z, r_c)
        d = (curvature_density_np(Mnp, h, 1.0)
             + potential_density_np(Mnp, a, b, c, vvac))
        w = cell_weights(nr2, nz2, h)
        RHO = R[: nr2 - 1, 1:-1]
        ZZ = Z[: nr2 - 1, 1:-1]
        mask = (RHO <= Rmask) & (np.abs(ZZ) <= Zmask)
        E2 = float(np.sum((d * w)[mask]))
        diffs[h] = {"E3": E3, "E2": E2, "rel": abs(E3 - E2) / abs(E2)}
    shrink = diffs[1.0]["rel"] / max(diffs[0.5]["rel"], 1e-300)
    ok = (diffs[0.5]["rel"] < 0.005) and (shrink > 2.5)
    return {"gate": "G6_equiv3d", "ok": bool(ok),
            "rel_h1": diffs[1.0]["rel"], "rel_h05": diffs[0.5]["rel"],
            "shrink_factor": shrink,
            "E2_h05": diffs[0.5]["E2"], "E3_h05": diffs[0.5]["E3"]}


def gate_frame():
    R, Z = grid_coords(NR, NZ, H)
    Mnp = hedgehog_field(R, Z, r_c=6.0)
    a, b, c, vvac = ldg_coeffs(1.0, 2e-3)
    E0 = total_energy_np(Mnp, a, b, c, 1.0, H, vvac)
    ang = 0.3
    Rot = np.eye(4)
    Rot[1, 1] = Rot[2, 2] = np.cos(ang)
    Rot[1, 2] = -np.sin(ang)
    Rot[2, 1] = np.sin(ang)
    Mr = np.einsum("ab,...bc,dc->...ad", Rot, Mnp, Rot)
    E1 = total_energy_np(Mr, a, b, c, 1.0, H, vvac)
    rel = abs(E1 - E0) / (abs(E0) + 1e-300)
    return {"gate": "G7_frame", "ok": bool(rel < 1e-11), "E0": E0, "E_rot": E1,
            "rel": rel}


def gate_g_decouple():
    R, Z = grid_coords(NR, NZ, H)
    a, b, c, vvac = ldg_coeffs(1.0, 2e-3)
    E8 = total_energy_np(hedgehog_field(R, Z, 6.0, g_time=8.0), a, b, c, 1.0, H, vvac)
    Eg = total_energy_np(hedgehog_field(R, Z, 6.0, g_time=1e10), a, b, c, 1.0, H, vvac)
    rel = abs(E8 - Eg) / (abs(E8) + 1e-300)
    return {"gate": "G8_g_decouple", "ok": bool(rel < 1e-15), "E_g8": E8,
            "E_g1e10": Eg, "rel": rel}


# ---------------- spherically-constrained (radial) solver ----------------
def _radial_basis(nr, nz, h, dr):
    """linear-interp basis: cell radii -> knot weights. Returns (r_cell flat,
    idx_lo, frac, n_knots, nn_cell) for the included-cell block."""
    R, Z = grid_coords(nr, nz, h)
    Rc = R[: nr - 1, 1:-1]
    Zc = Z[: nr - 1, 1:-1]
    r = np.sqrt(Rc ** 2 + Zc ** 2)
    rmax = float(np.max(r)) + 2 * dr
    n_knots = int(np.ceil(rmax / dr)) + 2
    t = r / dr
    lo = np.floor(t).astype(int)
    frac = t - lo
    # director outer product at phi = 0 (spatial indices 1..3, n2 = 0)
    rs = np.where(r < 1e-12, 1e-12, r)
    n1 = Rc / rs
    n3 = Zc / rs
    nn = np.zeros(Rc.shape + (4, 4))
    nn[..., 1, 1] = n1 * n1
    nn[..., 1, 3] = n1 * n3
    nn[..., 3, 1] = n1 * n3
    nn[..., 3, 3] = n3 * n3
    return r, lo, frac, n_knots, nn


def _field_from_profile(s_knots, lo, frac, nn, nr, nz, g_time=G_TIME):
    s_cell = s_knots[lo] * (1.0 - frac) + s_knots[lo + 1] * frac
    Mnp = np.zeros((nr, nz, 4, 4))
    Mnp[: nr - 1, 1:-1] = s_cell[..., None, None] * nn
    Mnp[..., 0, 0] = g_time
    # boundary rows/cols (excluded cells) pinned to the same profile value
    # via nearest included neighbour (they only enter through pinned BCs)
    Mnp[nr - 1] = Mnp[nr - 2]
    Mnp[:, 0] = Mnp[:, 1]
    Mnp[:, -1] = Mnp[:, -2]
    return Mnp


def run_radial():
    """P-D: the spherical-hedgehog stationary solution (Duda/Faber's electron
    ansatz), relaxed over the radial profile s(r) ONLY, using the exact chain
    rule through the 2D discrete functional: dE/ds_k = sum_cells
    <G_cell, nn_cell> phi_k(r_cell). The unconstrained 2D relax (mode relax)
    escapes the hedgehog (the LdG point-vs-ring instability); the calibration
    lock lives on THIS constrained solution, the escape is reported (Q8)."""
    a, b, c, vvac = ldg_coeffs(BETA, CSCALE)
    dr = 0.5 * H
    r_cell, lo, frac, n_knots, nn = _radial_basis(NR, NZ, H, dr)
    rk = np.arange(n_knots) * dr

    def seed_profile(r_c):
        return 1.0 - np.exp(-((rk / r_c) ** 2))

    cscale = CSCALE
    if AUTOCHI:
        s0 = seed_profile(RC_SEED)
        M0 = _field_from_profile(s0, lo, frac, nn, NR, NZ)
        w = cell_weights(NR, NZ, H)
        Ecurv = float(np.sum(curvature_density_np(M0, H, 1.0) * w)) + ext_tail(
            (NR - 1) * H, (NZ / 2 - 1) * H)
        Epot = float(np.sum(potential_density_np(M0, a, b, c, vvac) * w))
        cscale = CSCALE * Ecurv / (3.0 * Epot) if Epot > 0 else CSCALE
        a, b, c, vvac = ldg_coeffs(BETA, cscale)
    s0 = seed_profile(RC_SEED)
    # pin the far knots (r > r_pin) at the vacuum s = 1
    r_pin = min((NR - 4) * H, (NZ / 2 - 4) * H)
    pin_k = rk > r_pin
    freek = (~pin_k).astype(float)

    def E_of(s):
        return total_energy_np(_field_from_profile(s, lo, frac, nn, NR, NZ),
                               a, b, c, 1.0, H, vvac)

    def g_of(s):
        Mnp = _field_from_profile(s, lo, frac, nn, NR, NZ)
        G = energy_gradient_np(Mnp, a, b, c, 1.0, H, vvac)
        Gc = G[: NR - 1, 1:-1]
        proj = np.sum(Gc * nn, axis=(-2, -1))            # <G_cell, nn_cell>
        g = np.zeros(n_knots)
        np.add.at(g, lo, proj * (1.0 - frac))
        np.add.at(g, lo + 1, proj * frac)
        return g * freek

    # knot "mass" = accumulated volume weight (preconditioner: outer shells
    # carry ~r^2 more weight, unpreconditioned FIRE overflows)
    wc = cell_weights(NR, NZ, H)
    mass = np.zeros(n_knots)
    np.add.at(mass, lo, (1.0 - frac) * wc)
    np.add.at(mass, lo + 1, frac * wc)
    mass = np.maximum(mass, np.max(mass) * 1e-6)

    # chain-rule gradcheck (mini-gate, always run)
    eps = 1e-7
    g_an = g_of(s0)
    errs = []
    for k in (2, 8, 16, 30, 60):
        if k >= n_knots or pin_k[k]:
            continue
        sp = s0.copy()
        sm = s0.copy()
        sp[k] += eps
        sm[k] -= eps
        num = (E_of(sp) - E_of(sm)) / (2 * eps)
        errs.append(abs(num - g_an[k]) / (abs(num) + abs(g_an[k]) + 1e-12))
    gc = float(np.max(errs))

    # FIRE on the 1D profile
    t0 = time.time()
    s = s0.copy()
    v = np.zeros_like(s)
    dt, dt_max, alpha, n_pos = 0.02, 0.5, 0.1, 0
    E = E_of(s)
    g = g_of(s)
    g0n = float(np.sqrt(np.sum(g * g)))
    Es = [E]
    for it in range(1, ITERS + 1):
        F = -g / mass
        v = v + dt * F
        P = float(np.sum(F * v))
        fn = np.sqrt(np.sum(F * F))
        vn = np.sqrt(np.sum(v * v))
        if fn > 0:
            v = (1 - alpha) * v + alpha * (vn / (fn + 1e-30)) * F
        if P > 0:
            n_pos += 1
            if n_pos > 5:
                dt = min(dt * 1.1, dt_max)
                alpha *= 0.99
        else:
            n_pos = 0
            dt *= 0.5
            alpha = 0.1
            v[:] = 0.0
        s = s + dt * v
        g = g_of(s)
        gn = float(np.sqrt(np.sum(g * g)))
        if it % 500 == 0:
            Es.append(E_of(s))
        if gn < 1e-6 * g0n or gn < 1e-10:
            break
    E_fire = E_of(s)
    Es.append(E_fire)
    t_fire = time.time() - t0
    # golden-section CG polish on the profile
    sc = s.copy()
    gc2 = g_of(sc)
    d = -gc2 / mass
    for it in range(200):
        dn = float(np.sqrt(np.sum(d * d)))
        if dn < 1e-14:
            break
        t_star = golden_line(lambda t: E_of(sc + t * d), min(0.05, 1.0 / dn))
        sc = sc + t_star * d
        g2 = g_of(sc)
        z2 = g2 / mass
        bpr = max(0.0, float(np.sum(g2 * (z2 - gc2 / mass)))
                  / (float(np.sum(gc2 * gc2 / mass)) + 1e-300))
        d = -z2 + bpr * d
        if float(np.sum(d * g2)) > 0:
            d = -g2
        gc2 = g2
        if float(np.sqrt(np.sum(g2 * g2))) < 1e-10:
            break
    E_best = E_of(sc)
    gn_final = float(np.sqrt(np.sum(g_of(sc) ** 2)))
    Mb = _field_from_profile(sc, lo, frac, nn, NR, NZ)
    obs = observables(Mb, a, b, c, 1.0, H, vvac)
    mono = all(Es[i + 1] <= Es[i] + 1e-9 for i in range(len(Es) - 1))
    decades = float(np.log10(g0n / (gn_final + 1e-300)))
    out = {
        "task": "M5.16", "script": "m5_16_axisym.py", "mode": "radial",
        "convention": "Duda index-0: D=diag(g,1,delta,0), eta=diag(-1,1,1,1)",
        "grid": {"NR": NR, "NZ": NZ, "h": H, "dr": dr, "n_knots": int(n_knots)},
        "params": {"beta": BETA, "cscale_input": CSCALE, "cscale_used": cscale,
                   "a": a, "b": b, "c": c, "vvac": vvac, "rc_seed": RC_SEED,
                   "autochi": AUTOCHI, "iters": ITERS},
        "chain_gradcheck_max_rel": gc,
        "E_fire": E_fire, "E_best": E_best,
        "monotone_fire": bool(mono), "gnorm_decades": decades,
        "gnorm_final": gn_final, "wall_s": {"fire": round(t_fire, 1)},
        "s_knots_r": rk[:: max(1, n_knots // 200)].tolist(),
        "s_knots": sc[:: max(1, n_knots // 200)].tolist(),
        "obs": obs,
    }
    path = os.path.join(DATA, f"m5_16_axisym_{TAG}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[radial] beta={BETA} cscale={cscale:.3e} E_best={E_best:.6f} "
          f"r_half={obs['r_half']:.3f} virial={obs['virial_ratio_curv_over_3pot']:.4f} "
          f"gradcheck={gc:.2e} decades={decades:.1f} mono={mono}")
    print(f"json -> {path}")
    return out, Mb, (a, b, c, vvac, cscale)



def run_stability():
    """P-D honesty probe: is the spherical hedgehog STABLE in the axisym
    class? Seed the 2D unconstrained relax from the converged radial solution
    plus a small symmetry-breaking perturbation; if the energy descends well
    below the radial minimum and a melt RING forms off the origin, the
    hedgehog is a saddle in this functional (the LdG point-vs-ring escape),
    which is the M5-native content of Duda's Q8 regularization question."""
    out_r, Mb, (a, b, c, vvac, cscale) = run_radial()
    E_radial = out_r["E_best"]
    R, Z = grid_coords(NR, NZ, H)
    rng = np.random.default_rng(7)
    # smooth symmetry-breaking bump off-center (axisym class, breaks r-sphericity)
    bump = 0.03 * np.exp(-(((R - 0.8 * RC_SEED) ** 2) + (Z - 0.5 * RC_SEED) ** 2)
                         / (RC_SEED ** 2))
    Mp = Mb.copy()
    Mp[..., 1, 3] += bump
    Mp[..., 3, 1] += bump
    Mp[..., 2, 2] += 0.5 * bump
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(NR, NZ, H)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    def egf(MM):
        return (total_energy_np(MM, a, b, c, 1.0, H, vvac),
                energy_gradient_np(MM, a, b, c, 1.0, H, vvac))

    Mf, hist = fire_relax(Mp, egf, free4, precond, max_iter=ITERS)
    E_end = hist["E"][-1]
    obs = observables(Mf, a, b, c, 1.0, H, vvac)
    # melt-ring locator: cells with smallest largest-eigenvalue
    msp = Mf[: NR - 1, 1:-1, 1:4, 1:4]
    s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    k = np.unravel_index(np.argmin(s_cell), s_cell.shape)
    rho_min = (k[0] + 0.5) * H
    z_min = (k[1] - (NZ - 2) / 2 + 0.5) * H
    escaped = bool(E_end < E_radial - 0.05 * abs(E_radial))
    out = {
        "task": "M5.16", "mode": "stability",
        "E_radial": E_radial, "E_after_perturbed_2d_relax": E_end,
        "drop_rel": (E_radial - E_end) / abs(E_radial),
        "escaped_hedgehog": escaped,
        "melt_min_s": float(np.min(s_cell)),
        "melt_min_location_rho_z": [float(rho_min), float(z_min)],
        "sphericity_after": obs["sphericity_max_ds"],
        "iters": ITERS, "note": "escaped=True means the spherical hedgehog is"
        " a SADDLE of the axisym functional at this (beta, cscale): the"
        " M5-native core-regularization question (Q8)",
    }
    path = os.path.join(DATA, f"m5_16_axisym_{TAG}_stability.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[stability] E_radial={E_radial:.4f} -> E_2d={E_end:.4f} "
          f"escaped={escaped} min_s={out['melt_min_s']:.3f} at "
          f"(rho,z)=({rho_min:.1f},{z_min:.1f})")
    print(f"json -> {path}")
    return out



def run_grade():
    """P-A: exact delta-grading on a converged radial solution (--fromtag).
    The functional is an exact QUARTIC polynomial in delta, so sampling
    E(delta) at O(1) nodes and solving the 5x5 Vandermonde gives the orders
    E_0..E_4 with NO cancellation; E(delta_phys = 1e-10) then follows to
    machine precision (the N1 lesson, without re-deriving graded commutators).
    Two axisymmetric delta-textures are graded: the delta eigenaxis along
    phi-hat (out of plane) and along theta-hat (in plane, perpendicular to
    the director), both sharing the melt profile s(r):
        M(delta) = s (n n^T) + delta s (m2 m2^T),  spectrum s.(1, delta, 0).
    The vacuum reference follows the same spectrum: vvac(delta) =
    V(diag(1, delta, 0)), so E(delta) is energy above the delta-vacuum."""
    fromtag = _flag("fromtag", TAG, str)
    with open(os.path.join(DATA, f"m5_16_axisym_{fromtag}.json")) as f:
        d = json.load(f)
    beta = d["params"]["beta"]
    cscale = d["params"]["cscale_used"]
    a, b, c, _ = ldg_coeffs(beta, cscale)
    nr = d["grid"]["NR"]
    nz = d["grid"]["NZ"]
    h = d["grid"]["h"]
    dr = d["grid"]["dr"]
    rk = np.array(d["s_knots_r"])
    sk = np.array(d["s_knots"])
    if len(rk) != d["grid"]["n_knots"]:
        raise SystemExit("decimated profile in JSON; regenerate with full knots")
    r_cell, lo, frac, n_knots, nn = _radial_basis(nr, nz, h, dr)
    s_cell = sk[lo] * (1.0 - frac) + sk[lo + 1] * frac
    # director + perpendicular textures at phi = 0
    R, Z = grid_coords(nr, nz, h)
    Rc = R[: nr - 1, 1:-1]
    Zc = Z[: nr - 1, 1:-1]
    rr = np.sqrt(Rc ** 2 + Zc ** 2)
    rr = np.where(rr < 1e-12, 1e-12, rr)
    n1 = Rc / rr
    n3 = Zc / rr
    mm_phi = np.zeros(Rc.shape + (4, 4))
    mm_phi[..., 2, 2] = 1.0                       # phi-hat outer product
    mm_th = np.zeros(Rc.shape + (4, 4))
    mm_th[..., 1, 1] = n3 * n3                    # theta-hat = (n3, 0, -n1)
    mm_th[..., 1, 3] = -n3 * n1
    mm_th[..., 3, 1] = -n3 * n1
    mm_th[..., 3, 3] = n1 * n1

    def vvac_of(delta):
        tr2 = 1.0 + delta ** 2
        tr3 = 1.0 + delta ** 3
        return a * tr2 - b * tr3 + c * tr2 * tr2

    def E_of(delta, mm2):
        Mnp = np.zeros((nr, nz, 4, 4))
        Mnp[: nr - 1, 1:-1] = s_cell[..., None, None] * (nn + delta * mm2)
        Mnp[..., 0, 0] = G_TIME
        Mnp[nr - 1] = Mnp[nr - 2]
        Mnp[:, 0] = Mnp[:, 1]
        Mnp[:, -1] = Mnp[:, -2]
        return total_energy_np(Mnp, a, b, c, 1.0, h, vvac_of(delta))

    nodes = np.array([0.0, 0.5, -0.5, 1.0, -1.0])
    V = np.vander(nodes, 5, increasing=True)      # E(d) = sum_k c_k d^k
    out = {"task": "M5.16", "mode": "grade", "fromtag": fromtag,
           "beta": beta, "cscale": cscale, "nodes": nodes.tolist(),
           "delta_phys": 1e-10, "textures": {}}
    for name, mm2 in (("phi_hat", mm_phi), ("theta_hat", mm_th)):
        Es = np.array([E_of(dd, mm2) for dd in nodes])
        coef = np.linalg.solve(V, Es)
        dp = 1e-10
        dE_phys = float(coef[1] * dp + coef[2] * dp ** 2)
        out["textures"][name] = {
            "orders_E0_to_E4": coef.tolist(),
            "E1": float(coef[1]), "E2": float(coef[2]),
            "dE_at_delta_phys": dE_phys,
            "dE_rel_to_E0": dE_phys / coef[0],
        }
        print(f"[grade:{name}] E0={coef[0]:.6f} E1={coef[1]:.6e} "
              f"E2={coef[2]:.6e} E3={coef[3]:.3e} E4={coef[4]:.3e} "
              f"dE(1e-10)={dE_phys:.3e} (rel {dE_phys/coef[0]:.3e})")
    path = os.path.join(DATA, f"m5_16_grade_{fromtag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {path}")
    return out


# ---------------- relax driver ----------------
def run_relax():
    a, b, c, vvac = ldg_coeffs(BETA, CSCALE)
    R, Z = grid_coords(NR, NZ, H)
    cscale = CSCALE
    if AUTOCHI:
        # place the seed at Derrick balance for the target size RC_SEED:
        # E_pot scales linearly in cscale, so set cscale* = E_curv / (3 E_pot/cscale)
        Mseed = hedgehog_field(R, Z, RC_SEED)
        w = cell_weights(NR, NZ, H)
        Ecurv = float(np.sum(curvature_density_np(Mseed, H, 1.0) * w)) + ext_tail(
            (NR - 1) * H, (NZ / 2 - 1) * H)
        Epot = float(np.sum(potential_density_np(Mseed, a, b, c, vvac) * w))
        cscale = CSCALE * Ecurv / (3.0 * Epot) if Epot > 0 else CSCALE
        a, b, c, vvac = ldg_coeffs(BETA, cscale)
    Mseed = hedgehog_field(R, Z, RC_SEED)
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(NR, NZ, H)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    def egf(MM):
        return (total_energy_np(MM, a, b, c, 1.0, H, vvac),
                energy_gradient_np(MM, a, b, c, 1.0, H, vvac))

    def ef(MM):
        return total_energy_np(MM, a, b, c, 1.0, H, vvac)

    t0 = time.time()
    Mf, hist_f = fire_relax(Mseed, egf, free4, precond, max_iter=ITERS)
    t_fire = time.time() - t0
    # independent minimizer from the SAME seed (Golubich recipe), cross-check
    t0 = time.time()
    Mg, hist_g = prcg_relax(Mseed, egf, ef, free4, precond,
                            iters=max(300, ITERS // 50))
    t_cg = time.time() - t0
    E_fire = hist_f["E"][-1]
    E_cg = hist_g["E"][-1]
    # polish FIRE result with CG (best of both)
    Mb, hist_b = prcg_relax(Mf, egf, ef, free4, precond, iters=200)
    E_best = hist_b["E"][-1]
    obs = observables(Mb, a, b, c, 1.0, H, vvac)
    mono = all(hist_f["E"][i + 1] <= hist_f["E"][i] + 1e-9
               for i in range(len(hist_f["E"]) - 1))
    decades = float(np.log10(hist_f["gnorm"][0] / (hist_b["gnorm"][-1] + 1e-300)))
    agree = abs(E_fire - E_cg) / (abs(E_best) + 1e-300)
    out = {
        "task": "M5.16", "script": "m5_16_axisym.py", "mode": "relax",
        "convention": "Duda index-0: D=diag(g,1,delta,0), eta=diag(-1,1,1,1)",
        "grid": {"NR": NR, "NZ": NZ, "h": H},
        "params": {"beta": BETA, "cscale_input": CSCALE, "cscale_used": cscale,
                   "a": a, "b": b, "c": c, "vvac": vvac, "rc_seed": RC_SEED,
                   "autochi": AUTOCHI, "iters": ITERS},
        "E_fire": E_fire, "E_cg_from_seed": E_cg, "E_best": E_best,
        "minimizer_agreement_rel": agree,
        "monotone_fire": bool(mono), "gnorm_decades": decades,
        "gnorm_final": hist_b["gnorm"][-1],
        "wall_s": {"fire": round(t_fire, 1), "cg": round(t_cg, 1)},
        "obs": obs,
    }
    path = os.path.join(DATA, f"m5_16_axisym_{TAG}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[relax] beta={BETA} cscale={cscale:.3e} E_best={E_best:.6f} "
          f"r_half={obs['r_half']:.3f} virial={obs['virial_ratio_curv_over_3pot']:.4f} "
          f"spher={obs['sphericity_max_ds']:.4f} agree={agree:.2e} "
          f"decades={decades:.1f} mono={mono}")
    print(f"json -> {path}")
    return out


def run_gates():
    t0 = time.time()
    res = [gate_gradcheck(), gate_hh_density(), gate_shell(),
           gate_slab_vs_p0(), gate_equiv3d(), gate_frame(), gate_g_decouple()]
    if _flag("ti", 0, int):
        res.insert(0, gate_np_vs_ti())   # taichi AD cross-check (slow JIT)
    all_ok = all(r["ok"] for r in res)
    for r in res:
        flag = "PASS" if r["ok"] else "FAIL"
        print(f"[{flag}] {r['gate']:16s} "
              + " ".join(f"{k}={v}" for k, v in r.items()
                         if k not in ("gate", "ok")))
    out = {"task": "M5.16", "mode": "gates", "all_ok": bool(all_ok),
           "grid": {"NR": NR, "NZ": NZ}, "wall_s": round(time.time() - t0, 1),
           "gates": res}
    path = os.path.join(DATA, "m5_16_axisym_gates.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nGATES {'ALL PASS' if all_ok else 'FAILURES PRESENT'} "
          f"({out['wall_s']}s)  json -> {path}")
    return all_ok


if __name__ == "__main__":
    if MODE == "gates":
        ok = run_gates()
        raise SystemExit(0 if ok else 1)
    elif MODE == "relax":
        run_relax()
    elif MODE == "radial":
        run_radial()
    elif MODE == "stability":
        run_stability()
    elif MODE == "grade":
        run_grade()
    else:
        print("modes: gates [NR NZ] | relax|radial [NR NZ] --beta --cscale "
              "--rc --iters --autochi --tag [--ti 1]")
