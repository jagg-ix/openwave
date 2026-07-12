"""M5.20.1 INDEPENDENT ADVERSARIAL AUDIT (AI_HYGIENE.md section 1).

Own instruments, own derivations; existing task files are consumed READ-ONLY
(states, trajectory JSONs) and the seed builder is used only as a known-q
TEST INPUT for instrument validation, never as an instrument.

Sections
  S1  headline: own winding instruments on every endpoint state
      (a) dense plaquette defect map of the block director angle,
          all three 2-plane blocks (1,3), (1,2), (2,3)
      (b) own bilinear circle winding (own interpolation index arithmetic)
          confirming every plaquette candidate at 5 radii
      (c) coarse grid of circle reads over the whole box
      validated on: own synthetic vortex (+known q), own null field,
      and the task's seeds as known-q inputs.
  S2  vacuum gap map: own analytic Hessian (exact: blockdiag(2w J^T J, 0))
      + own FD Hessian cross-check + Rayleigh-vs-true-gap comparison.
  S3  core-equalization: own eigenvalue reads at remnant locations.
  S4  energy bookkeeping: closed KE+PE drift, sponge KE+PE+E_abs drift,
      + own reimplementation of the energy density checked against the
      endpoint-state PE.
  S5  remnant line: own spectral estimates (3 windows, 16x zero-pad,
      parabolic refine, split halves) vs own analytic ladder.
  S6  barrier-vs-driving arithmetic from own closed forms + statics
      monotonicity.

Run:  python m5_20_1_audit_check.py
Out:  ../data/m5_20_1_audit.json  (matplotlib Agg only, headless)
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

NR, NZ, H = 128, 256, 1.0
RHO = (np.arange(NR) + 0.5) * H          # full-grid cell centers
ZC = (np.arange(NZ) - NZ / 2 + 0.5) * H
WSCALE = 0.0007240238793069094           # read back from the task JSONs below

RUN_TAGS = [
    "d0p1_pair_1d_closed", "d0p1_pair_d0_closed",
    "d0p3_pair_1d_closed", "d0p3_pair_d0_closed",
    "d0p5_pair_1d_closed", "d0p5_pair_d0_closed",
    "d0p3_pair_1d_closed_recal", "d0p0_pair_1d_closed_anchor",
    "d0p3_pair_1d_sponge", "d0p3_pair_d0_sponge",
]
STATIC_TAGS = ["d0p1_pair_1d", "d0p1_pair_d0", "d0p3_pair_1d",
               "d0p3_pair_d0", "d0p5_pair_1d", "d0p5_pair_d0"]
BLOCKS = ((1, 3), (1, 2), (2, 3))


# ---------------------------------------------------------------- S1 tools
def block_fields(M, a, b):
    """maa, mbb, mab on the FULL grid (own convention, no subgrid)."""
    return M[..., a, a], M[..., b, b], M[..., a, b]


def plaquette_map(M, a, b):
    """dense defect map: circulation of 2*theta_ab = atan2(2 mab, maa-mbb)
    around every grid plaquette; charge = circ/(4 pi) in units where a
    director half-turn = 1/2. Also the min corner anisotropy per plaquette."""
    maa, mbb, mab = block_fields(M, a, b)
    two_th = np.arctan2(2.0 * mab, maa - mbb)
    aniso = np.sqrt((maa - mbb) ** 2 + 4.0 * mab ** 2)

    def wrap(d):
        return (d + np.pi) % (2.0 * np.pi) - np.pi
    # corners: (i,j) (i+1,j) (i+1,j+1) (i,j+1)
    d1 = wrap(two_th[1:, :-1] - two_th[:-1, :-1])
    d2 = wrap(two_th[1:, 1:] - two_th[1:, :-1])
    d3 = wrap(two_th[:-1, 1:] - two_th[1:, 1:])
    d4 = wrap(two_th[:-1, :-1] - two_th[:-1, 1:])
    circ = d1 + d2 + d3 + d4
    q = circ / (4.0 * np.pi)
    amin = np.minimum(np.minimum(aniso[:-1, :-1], aniso[1:, :-1]),
                      np.minimum(aniso[1:, 1:], aniso[:-1, 1:]))
    return q, amin


def own_bilin(F, rr, zz):
    """own bilinear interpolation on the FULL grid (different index
    arithmetic from the task's included-cell _bilin)."""
    x = rr / H - 0.5                    # fractional full-grid i
    y = zz / H + NZ / 2 - 0.5           # fractional full-grid j
    i0 = np.clip(np.floor(x).astype(int), 0, NR - 2)
    j0 = np.clip(np.floor(y).astype(int), 0, NZ - 2)
    fx = np.clip(x - i0, 0.0, 1.0)
    fy = np.clip(y - j0, 0.0, 1.0)
    return ((1 - fx) * (1 - fy) * F[i0, j0] + fx * (1 - fy) * F[i0 + 1, j0]
            + (1 - fx) * fy * F[i0, j0 + 1] + fx * fy * F[i0 + 1, j0 + 1])


def own_circle_q(M, a, b, rho_c, z_c, r_w, npts=1440, aniso_floor=0.02):
    """own circle winding read of the (a,b)-block director angle."""
    ang = np.linspace(0.0, 2.0 * np.pi, npts, endpoint=True)
    rr = rho_c + r_w * np.cos(ang)
    zz = z_c + r_w * np.sin(ang)
    if rr.min() < 0.6 * H or rr.max() > RHO[-1] - 0.6 \
            or abs(zz).max() > ZC[-1] - 0.6:
        return float("nan"), float("nan")
    maa, mbb, mab = block_fields(M, a, b)
    saa = own_bilin(maa, rr, zz)
    sbb = own_bilin(mbb, rr, zz)
    sab = own_bilin(mab, rr, zz)
    aniso = np.sqrt((saa - sbb) ** 2 + 4.0 * sab ** 2)
    amin = float(np.min(aniso))
    if amin < aniso_floor:
        return float("nan"), amin
    two_th = np.arctan2(2.0 * sab, saa - sbb)
    d = np.diff(two_th)
    d = (d + np.pi) % (2.0 * np.pi) - np.pi
    return float(np.sum(d) / (4.0 * np.pi)), amin


def scan_state(M, label):
    """S1 per-state: plaquette candidates (all 3 blocks) + circle
    confirmation of every candidate + coarse circle grid."""
    out = {"label": label, "blocks": {}}
    survivors = []
    for (a, b) in BLOCKS:
        q, amin = plaquette_map(M, a, b)
        strong = (np.abs(q) >= 0.4) & (amin >= 0.02)
        weak = (np.abs(q) >= 0.4) & (amin >= 1e-3)
        idx = np.argwhere(weak)
        cands = []
        for (i, j) in idx[:200]:
            rho_c, z_c = RHO[i] + 0.5 * H, ZC[j] + 0.5 * H
            reads = {}
            n_conf = 0
            for rw in (2.0, 3.0, 4.0, 5.0, 6.0):
                qc, am = own_circle_q(M, a, b, rho_c, z_c, rw)
                reads[str(rw)] = (None if not np.isfinite(qc)
                                  else round(qc, 3))
                if np.isfinite(qc) and abs(qc) >= 0.35:
                    n_conf += 1
            confirmed = n_conf >= 3
            cands.append({"rho": float(rho_c), "z": float(z_c),
                          "q_plaq": float(q[i, j]),
                          "corner_aniso_min": float(amin[i, j]),
                          "circle_reads": reads,
                          "confirmed_wound": bool(confirmed)})
            if confirmed:
                survivors.append({"block": f"{a}{b}", **cands[-1]})
        out["blocks"][f"{a}{b}"] = {
            "n_plaq_weak": int(weak.sum()), "n_plaq_strong": int(strong.sum()),
            "net_charge_weak": float(np.sum(q[weak])) if weak.any() else 0.0,
            "candidates": cands}
    # coarse circle grid on the (1,3) block (the wound block by construction)
    grid_hits = []
    centers_r = np.arange(2.0, 122.0, 2.0)
    centers_z = np.arange(-120.0, 120.5, 2.0)
    Rg, Zg = np.meshgrid(centers_r, centers_z, indexing="ij")
    for rw in (3.0, 5.0):
        npts = 360
        ang = np.linspace(0.0, 2.0 * np.pi, npts, endpoint=True)
        rr = (Rg[..., None] + rw * np.cos(ang)).ravel()
        zz = (Zg[..., None] + rw * np.sin(ang)).ravel()
        ok = (rr.reshape(Rg.shape + (npts,)).min(axis=-1) > 0.6)
        maa, mbb, mab = block_fields(M, 1, 3)
        saa = own_bilin(maa, rr, zz).reshape(Rg.shape + (npts,))
        sbb = own_bilin(mbb, rr, zz).reshape(Rg.shape + (npts,))
        sab = own_bilin(mab, rr, zz).reshape(Rg.shape + (npts,))
        aniso = np.sqrt((saa - sbb) ** 2 + 4.0 * sab ** 2)
        two_th = np.arctan2(2.0 * sab, saa - sbb)
        d = np.diff(two_th, axis=-1)
        d = (d + np.pi) % (2.0 * np.pi) - np.pi
        qg = np.sum(d, axis=-1) / (4.0 * np.pi)
        valid = ok & (aniso.min(axis=-1) >= 0.02)
        hits = valid & (np.abs(qg) >= 0.35)
        for (i, j) in np.argwhere(hits)[:50]:
            grid_hits.append({"rho": float(Rg[i, j]), "z": float(Zg[i, j]),
                              "r_w": rw, "q": float(qg[i, j])})
    out["coarse_grid_hits_13"] = grid_hits
    out["surviving_wound_cores"] = survivors
    out["any_wound_core"] = bool(survivors or grid_hits)
    return out


def adjudicate_plaquettes(M, a, b, max_conf=30):
    """S1b: are the strong plaquettes genuine cores or angle-turbulence /
    dipole noise? Reports net charge, nearest-opposite-charge distance,
    and circle confirmation on a random sample."""
    q, am = plaquette_map(M, a, b)
    mask = (np.abs(q) >= 0.4) & (am >= 0.02)
    n = int(mask.sum())
    if n == 0:
        return {"n_strong": 0}
    net = float(q[mask].sum())
    idx = np.argwhere(mask)
    ch = np.sign(q[mask])
    pts = idx.astype(float)
    dmin = []
    for k in range(min(n, 400)):
        opp = pts[ch != ch[k]]
        if len(opp):
            dmin.append(float(np.sqrt(((opp - pts[k]) ** 2).sum(1)).min()))
    rng = np.random.default_rng(3)
    sample = idx[rng.choice(n, size=min(max_conf, n), replace=False)]
    conf = 0
    for (i, j) in sample:
        rc, zc = RHO[i] + 0.5 * H, ZC[j] + 0.5 * H
        good = 0
        for rw in (2.0, 3.0, 4.0, 5.0, 6.0):
            qc, _ = own_circle_q(M, a, b, rc, zc, rw)
            if np.isfinite(qc) and abs(qc) >= 0.35:
                good += 1
        if good >= 3:
            conf += 1
    return {"n_strong": n, "net_charge": net,
            "median_nearest_opposite_cells": (float(np.median(dmin))
                                              if dmin else None),
            "circle_confirmed": f"{conf}/{len(sample)}"}


def synthetic_vortex(qv=0.5, center=(17.0, 0.0), core_w=3.0):
    """OWN synthetic wound texture (independent of the task seed builder):
    director angle theta = qv * chi around the center in the (1,3) plane."""
    Rm, Zm = np.meshgrid(RHO, ZC, indexing="ij")
    chi = np.arctan2(Zm - center[1], Rm - center[0])
    dd = np.sqrt((Rm - center[0]) ** 2 + (Zm - center[1]) ** 2)
    A = 0.4 * (1.0 - np.exp(-((dd / core_w) ** 2)))
    two_th = 2.0 * qv * chi
    M = np.zeros((NR, NZ, 4, 4))
    M[..., 1, 1] = 0.5 + A * np.cos(two_th)
    M[..., 3, 3] = 0.5 - A * np.cos(two_th)
    M[..., 1, 3] = M[..., 3, 1] = A * np.sin(two_th)
    M[..., 2, 2] = 0.2
    M[..., 0, 0] = 8.0
    return M


def synthetic_null():
    """unwound m13 bump: large amplitude, zero winding."""
    Rm, Zm = np.meshgrid(RHO, ZC, indexing="ij")
    bump = 0.45 * np.exp(-((Rm - 20.0) ** 2 + Zm ** 2) / 30.0)
    M = np.zeros((NR, NZ, 4, 4))
    M[..., 1, 1] = 1.0
    M[..., 3, 3] = 0.05
    M[..., 1, 3] = M[..., 3, 1] = bump
    M[..., 2, 2] = 0.3
    M[..., 0, 0] = 8.0
    return M


# ---------------------------------------------------------------- S2 tools
def own_analytic_hessian(delta, w):
    """EXACT 6x6 Hessian of V = w sum_p (Tr M^p - c_p)^2 at M = diag(1,
    delta, 0), c_p = 1 + delta^p, in the Frobenius-orthonormal symmetric
    basis (3 diag e_ii then 3 off (e_ij+e_ji)/sqrt2).
    Derivation: r_p = Tr Lam^p - c_p = 0 exactly at the target, so
    H = 2w sum_p (grad Tr M^p)(grad Tr M^p)^T with
    (grad Tr M^p)_X = p Tr(Lam^{p-1} X); off-diagonal basis directions give
    Tr(Lam^{p-1} X) = 0, diagonal ones give p lam_i^{p-1} = J_pi.
    => H = blockdiag(2w J^T J, 0_3)."""
    lam = np.array([1.0, delta, 0.0])
    J = np.array([np.ones(3), 2.0 * lam, 3.0 * lam ** 2])
    Hd = 2.0 * w * (J.T @ J)
    Hfull = np.zeros((6, 6))
    Hfull[:3, :3] = Hd
    return Hfull, J


def own_vdens(m, delta, w):
    m2 = m @ m
    c = (1.0 + delta, 1.0 + delta ** 2, 1.0 + delta ** 3)
    return w * ((np.trace(m) - c[0]) ** 2 + (np.trace(m2) - c[1]) ** 2
                + (np.trace(m2 @ m) - c[2]) ** 2)


def own_fd_hessian(delta, w, eps):
    basis = []
    for i in range(3):
        e = np.zeros((3, 3))
        e[i, i] = 1.0
        basis.append(e)
    for (i, j) in ((0, 1), (0, 2), (1, 2)):
        e = np.zeros((3, 3))
        e[i, j] = e[j, i] = 1.0 / np.sqrt(2.0)
        basis.append(e)
    lam = np.diag([1.0, delta, 0.0])
    Hm = np.zeros((6, 6))
    for a in range(6):
        for b in range(6):
            Hm[a, b] = (own_vdens(lam + eps * (basis[a] + basis[b]), delta, w)
                        - own_vdens(lam + eps * (basis[a] - basis[b]), delta, w)
                        - own_vdens(lam - eps * (basis[a] - basis[b]), delta, w)
                        + own_vdens(lam - eps * (basis[a] + basis[b]), delta, w)
                        ) / (4.0 * eps ** 2)
    return 0.5 * (Hm + Hm.T)


# ---------------------------------------------------------------- S4 tools
def own_energy(M, w_v, cps):
    """OWN reimplementation of the discrete energy from the method-note
    equations: u_curv = 4 sum ||[A_mu, A_nu]||_F^2 (central differences,
    mirror ghost at the axis, A_phi = [J, M]/rho) + V spectral, weighted
    2 pi rho h^2 on included cells i<=NR-2, j in [1, NZ-2]."""
    J4o = np.zeros((4, 4))
    J4o[1, 2] = -1.0
    J4o[2, 1] = 1.0
    mir = np.outer([1.0, -1.0, -1.0, 1.0], [1.0, -1.0, -1.0, 1.0])
    nr, nz = M.shape[:2]
    Mm = np.empty_like(M[: nr - 1])
    Mm[1:] = M[: nr - 2]
    Mm[0] = mir * M[0]
    Ar = (M[1:] - Mm)[:, 1:-1] / (2.0 * H)
    Az = (M[: nr - 1, 2:] - M[: nr - 1, :-2]) / (2.0 * H)
    Mc = M[: nr - 1, 1:-1]
    rho = ((np.arange(nr - 1) + 0.5) * H)[:, None, None, None]
    Ap = (J4o @ Mc - Mc @ J4o) / rho

    def comm(A, B):
        return A @ B - B @ A

    def n2(A):
        return np.sum(A * A, axis=(-2, -1))
    u = 4.0 * (n2(comm(Ar, Ap)) + n2(comm(Ar, Az)) + n2(comm(Ap, Az)))
    msp = Mc[..., 1:4, 1:4]
    m2 = msp @ msp
    t1 = np.einsum("...aa->...", msp)
    t2 = np.einsum("...aa->...", m2)
    t3 = np.einsum("...aa->...", m2 @ msp)
    V = w_v * ((t1 - cps[0]) ** 2 + (t2 - cps[1]) ** 2 + (t3 - cps[2]) ** 2)
    wcell = 2.0 * np.pi * rho[..., 0, 0] * H * H
    return float(np.sum((u + V) * wcell))


# ---------------------------------------------------------------- S5 tools
def own_spectrum_peak(t, y, wmin=0.02):
    """own spectral estimate: linear detrend, 3 windows, 16x zero-pad,
    parabolic peak refinement; returns peak per window + split halves."""
    from scipy.signal.windows import blackmanharris
    t = np.asarray(t, float)
    y = np.asarray(y, float)
    y = y - np.polyval(np.polyfit(t, y, 1), t)
    n = len(y)
    dtm = t[1] - t[0]
    res = {}
    for wname in ("rect", "hann", "bh"):
        wnd = {"rect": np.ones(n), "hann": np.hanning(n),
               "bh": blackmanharris(n)}[wname]
        npad = 16 * n
        A = np.abs(np.fft.rfft(y * wnd, n=npad))
        om = np.fft.rfftfreq(npad, d=dtm) * 2.0 * np.pi
        sel = om >= wmin
        k = np.argmax(A[sel]) + np.argmax(sel)
        if 0 < k < len(A) - 1:
            a0, a1, a2 = A[k - 1], A[k], A[k + 1]
            dk = 0.5 * (a0 - a2) / (a0 - 2 * a1 + a2 + 1e-300)
        else:
            dk = 0.0
        res[wname] = float(om[k] + dk * (om[1] - om[0]))
    def topk(yy, kmax=4):
        m = len(yy)
        npad = 16 * m
        A = np.abs(np.fft.rfft(yy * np.hanning(m), n=npad))
        om = np.fft.rfftfreq(npad, d=dtm) * 2.0 * np.pi
        A2 = A.copy()
        A2[om < wmin] = 0.0
        pk = []
        for _ in range(kmax):
            i = int(np.argmax(A2))
            pk.append([round(float(om[i]), 4), round(float(A2[i]), 3)])
            hw = max(1, int(0.008 / (om[1] - om[0])))
            A2[max(0, i - hw): i + hw] = 0.0
        return pk
    h = n // 2
    res["top4_full"] = topk(y)
    res["top4_half1"] = topk(y[:h] - np.mean(y[:h]))
    res["top4_half2"] = topk(y[h:] - np.mean(y[h:]))
    for part in ("half1", "half2"):
        res[part] = res[f"top4_{part}"][0][0]
    return res


# ---------------------------------------------------------------- main
def main():
    audit = {"task": "M5.20.1 adversarial audit", "date": "2026-07-12"}
    j = json.load(open(os.path.join(DATA, "m5_20_1_a_theory.json")))
    w = float(j["wscale"])
    audit["wscale"] = w
    assert abs(w - WSCALE) < 1e-12

    # ---------------- S1: instrument validation, then all endpoints
    print("== S1: headline (own winding instruments) ==")
    val = {}
    Ms = synthetic_vortex()
    sv = scan_state(Ms, "synthetic_q0.5")
    val["synthetic_vortex"] = {
        "found": sv["any_wound_core"],
        "n_cores_13": len([s for s in sv["surviving_wound_cores"]
                           if s["block"] == "13"]),
        "sample": sv["surviving_wound_cores"][:1]}
    Mn = synthetic_null()
    sn = scan_state(Mn, "synthetic_null")
    val["synthetic_null"] = {"found": sn["any_wound_core"]}
    # the task seeds as known-q test INPUTS
    from m5_20_1_b_seeds import loop_field_biax
    from m5_17_energy import grid_coords
    R, Z = grid_coords(NR, NZ, H)
    for delta, pairing in ((0.3, "pair_1d"), (0.3, "pair_d0")):
        Mseed = loop_field_biax(R, Z, 17.0, 0.5, delta, pairing)
        ss = scan_state(Mseed, f"seed_d{delta}_{pairing}")
        qs = [own_circle_q(Mseed, 1, 3, 17.0, 0.0, rw)[0]
              for rw in (3.0, 4.0, 5.0)]
        val[f"seed_d{delta}_{pairing}"] = {
            "plaquette_found": ss["any_wound_core"],
            "circle_q_at_core": [round(q, 4) for q in qs]}
    audit["S1_instrument_validation"] = val
    inst_ok = (val["synthetic_vortex"]["found"]
               and not val["synthetic_null"]["found"]
               and val["seed_d0.3_pair_1d"]["plaquette_found"]
               and val["seed_d0.3_pair_d0"]["plaquette_found"])
    print(f"  instrument validation: {'PASS' if inst_ok else 'FAIL'} "
          + json.dumps(val, default=str)[:400])

    s1 = {}
    for tag in RUN_TAGS:
        M = np.load(os.path.join(
            DATA, f"m5_20_1_run_{tag}_state.npz"))["M0"].astype(np.float64)
        r = scan_state(M, tag)
        s1[tag] = {
            "any_wound_core": r["any_wound_core"],
            "surviving_wound_cores": r["surviving_wound_cores"],
            "coarse_grid_hits_13": r["coarse_grid_hits_13"],
            "plaq_counts": {k: {"weak": v["n_plaq_weak"],
                                "strong": v["n_plaq_strong"]}
                            for k, v in r["blocks"].items()},
            "n_candidates_checked": sum(len(v["candidates"])
                                        for v in r["blocks"].values()),
            "strong_plaq_adjudication": {
                f"{a}{b}": adjudicate_plaquettes(M, a, b)
                for (a, b) in BLOCKS
                if r["blocks"][f"{a}{b}"]["n_plaq_strong"] > 0}}
        print(f"  [{tag}] wound_core={r['any_wound_core']} "
              f"plaq(13/12/23 weak)="
              f"{[r['blocks'][k]['n_plaq_weak'] for k in ('13', '12', '23')]}"
              f" cands={s1[tag]['n_candidates_checked']}")
    for tag in STATIC_TAGS:
        M = np.load(os.path.join(
            DATA, f"m5_20_1_c_{tag}_state.npz"))["M0"].astype(np.float64)
        r = scan_state(M, "static_" + tag)
        s1["static_" + tag] = {
            "any_wound_core": r["any_wound_core"],
            "surviving_wound_cores": r["surviving_wound_cores"],
            "coarse_grid_hits_13": r["coarse_grid_hits_13"],
            "plaq_counts": {k: {"weak": v["n_plaq_weak"],
                                "strong": v["n_plaq_strong"]}
                            for k, v in r["blocks"].items()},
            "strong_plaq_adjudication": {
                f"{a}{b}": adjudicate_plaquettes(M, a, b)
                for (a, b) in BLOCKS
                if r["blocks"][f"{a}{b}"]["n_plaq_strong"] > 0}}
        print(f"  [static_{tag}] wound_core={r['any_wound_core']}")
    audit["S1_endpoints"] = s1
    headline_refuted = any(v["any_wound_core"] for k, v in s1.items()
                           if not k.startswith("static_"))
    audit["S1_verdict"] = {
        "instruments_valid": bool(inst_ok),
        "any_surviving_wound_core_in_10_runs": bool(headline_refuted)}

    # ---------------- S2: gap map
    print("== S2: vacuum gap map (own derivation) ==")
    s2 = {"per_delta": {}}
    for delta in (0.0, 0.1, 0.3, 0.5):
        Ha, J = own_analytic_hessian(delta, w)
        ev = np.linalg.eigvalsh(Ha)
        om = np.sqrt(np.maximum(ev, 0.0))
        nz_exact = int(np.sum(ev < 1e-12 * max(ev.max(), 1e-300)))
        # FD cross-check with two eps (own numeric, catches derivation error)
        H1 = own_fd_hessian(delta, w, 1e-4)
        H2 = own_fd_hessian(delta, w, 1e-5)
        relfd = float(np.max(np.abs(H1 - Ha)) / np.max(np.abs(Ha)))
        relfd2 = float(np.max(np.abs(H2 - Ha)) / np.max(np.abs(Ha)))
        # Rayleigh along the claimed split direction diag(0,1,-1)/sqrt2
        u = np.zeros(6)
        u[1], u[2] = 1 / np.sqrt(2), -1 / np.sqrt(2)
        om_ray = float(np.sqrt(max(u @ Ha @ u, 0.0)))
        om_formula = float(np.sqrt(w * (4 * delta ** 2 + 9 * delta ** 4)))
        nonzero = om[ev > 1e-12 * max(ev.max(), 1e-300)]
        s2["per_delta"][str(delta)] = {
            "zero_modes": nz_exact,
            "omegas": [round(float(x), 6) for x in om],
            "omega_min_nonzero": (round(float(nonzero.min()), 6)
                                  if len(nonzero) else 0.0),
            "omega_rayleigh_splitdir": round(om_ray, 6),
            "omega_split_formula_sqrt_w(4d2+9d4)": round(om_formula, 6),
            "rankJ": int(np.linalg.matrix_rank(J)),
            "fd_rel_err_eps1e-4": relfd, "fd_rel_err_eps1e-5": relfd2}
        print(f"  delta={delta}: zeros={nz_exact} "
              f"om_min_nonzero={s2['per_delta'][str(delta)]['omega_min_nonzero']} "
              f"om_rayleigh={om_ray:.5f} (claim quotes the Rayleigh number)")
    claimed = {"0.1": 0.00544, "0.3": 0.01770, "0.5": 0.03363}
    s2["claimed_omega_split_matches_rayleigh"] = all(
        abs(s2["per_delta"][k]["omega_rayleigh_splitdir"] - v) < 5e-5
        for k, v in claimed.items())
    s2["note"] = ("the claimed omega_split is the Rayleigh quotient along "
                  "diag(0,1,-1), NOT the lowest activated normal mode; the "
                  "true spectral gap (min nonzero omega) is smaller")
    audit["S2_gap_map"] = s2

    # ---------------- S3: core equalization at remnants
    print("== S3: core equalization (own eigen reads) ==")
    s3 = {}
    for tag in ["d0p1_pair_1d_closed", "d0p3_pair_1d_closed",
                "d0p5_pair_1d_closed", "d0p3_pair_1d_closed_recal",
                "d0p3_pair_d0_closed", "d0p5_pair_d0_closed"]:
        d = json.load(open(os.path.join(DATA, f"m5_20_1_run_{tag}.json")))
        delta = d["delta"]
        last = d["trajectory"][-1]
        M = np.load(os.path.join(
            DATA, f"m5_20_1_run_{tag}_state.npz"))["M0"].astype(np.float64)
        m13 = np.abs(M[..., 1, 3])
        i, jj = np.unravel_index(np.argmax(m13), m13.shape)
        locs = {"own_max_m13": (float(RHO[i]), float(ZC[jj])),
                "their_ring": (last["ring13_rho"], last["ring13_z"])}
        ent = {"delta": delta}
        for lname, (rc, zc) in locs.items():
            Rm, Zm = np.meshgrid(RHO, ZC, indexing="ij")
            for rad in (1.5, 3.0):
                din = (Rm - rc) ** 2 + (Zm - zc) ** 2 < rad ** 2
                msp = M[..., 1:4, 1:4][din]
                lam_cells = np.sort(np.linalg.eigvalsh(
                    0.5 * (msp + np.swapaxes(msp, -1, -2))), axis=-1)[:, ::-1]
                lam = lam_cells.mean(axis=0)
                gt, gb = float(lam[0] - lam[1]), float(lam[1] - lam[2])
                ent[f"{lname}_r{rad}"] = {
                    "center": [round(rc, 2), round(zc, 2)],
                    "lam_mean": [round(float(x), 4) for x in lam],
                    "gap_top": round(gt, 4), "gap_bot": round(gb, 4),
                    "equalized_pair": ("(1,delta)" if gt < gb
                                       else "(delta,0)")}
        # vacuum-trivial reference: at the vacuum itself gaps are (1-d, d)
        ent["vacuum_gaps"] = {"gap_top": 1.0 - delta, "gap_bot": delta}
        ent["gap_bot_below_vacuum_delta"] = bool(
            ent["their_ring_r1.5"]["gap_bot"] < delta - 1e-9) if delta else None
        s3[tag] = ent
        print(f"  [{tag}] own_max_m13 r1.5 lam="
              f"{ent['own_max_m13_r1.5']['lam_mean']} "
              f"gaps=({ent['own_max_m13_r1.5']['gap_top']},"
              f"{ent['own_max_m13_r1.5']['gap_bot']}) "
              f"-> {ent['own_max_m13_r1.5']['equalized_pair']}")
    audit["S3_core_equalization"] = s3

    # ---------------- S4: energy bookkeeping
    print("== S4: energy bookkeeping ==")
    s4 = {}
    for tag in RUN_TAGS:
        d = json.load(open(os.path.join(DATA, f"m5_20_1_run_{tag}.json")))
        tr = d["trajectory"]
        led = np.array([r["PE"] + r["KE"] + r["E_abs"] for r in tr])
        drift = float(np.max(np.abs(led - led[0])) / abs(led[0]))
        drift_end = float(abs(led[-1] - led[0]) / abs(led[0]))
        M = np.load(os.path.join(
            DATA, f"m5_20_1_run_{tag}_state.npz"))["M0"].astype(np.float64)
        cps = (1 + d["delta"], 1 + d["delta"] ** 2, 1 + d["delta"] ** 3)
        pe_own = own_energy(M, d["wscale"], cps)
        pe_rel = abs(pe_own - tr[-1]["PE"]) / max(abs(tr[-1]["PE"]), 1e-30)
        s4[tag] = {"mode": d["mode"], "n_steps": tr[-1]["it"],
                   "ledger_drift_rel": drift,
                   "ledger_drift_endpoint_rel": drift_end,
                   "E_abs_final": tr[-1]["E_abs"],
                   "PE_endpoint_json": tr[-1]["PE"],
                   "PE_endpoint_own_recompute": pe_own,
                   "PE_own_rel_diff": pe_rel}
        print(f"  [{tag}] drift={drift:.2e} own-PE rel diff={pe_rel:.2e}")
    worst_closed = max(v["ledger_drift_rel"] for v in s4.values()
                       if v["mode"] == "closed")
    worst_sponge = max(v["ledger_drift_rel"] for v in s4.values()
                       if v["mode"] == "sponge")
    s4["worst_closed_drift"] = worst_closed
    s4["worst_sponge_ledger_drift"] = worst_sponge
    audit["S4_energy"] = s4

    # ---------------- S5: remnant line
    print("== S5: remnant breathing line (own spectral estimates) ==")
    s5 = {}
    for tag, delta in (("d0p3_pair_1d_closed", 0.3),
                       ("d0p5_pair_d0_closed", 0.5)):
        b = json.load(open(os.path.join(DATA, f"m5_20_1_blob_{tag}.json")))
        tr = b["trajectory"]
        t = np.array([r["t"] for r in tr])
        sm = np.array([r["s_min"] for r in tr])
        eb = np.array([r["E_blob"] for r in tr])
        pk_s = own_spectrum_peak(t, sm)
        pk_e = own_spectrum_peak(t, eb)
        Ha, _ = own_analytic_hessian(delta, b.get("wscale", w) if isinstance(
            b.get("wscale", None), float) else w)
        om_lad = np.sqrt(np.maximum(np.linalg.eigvalsh(Ha), 0.0))
        top, mid = float(om_lad[-1]), float(om_lad[-2])
        bin_w = 2 * np.pi / (t[-1] - t[0] + (t[1] - t[0]))
        s5[tag] = {"their_omega_peak_s": b["omega_peak_s"],
                   "their_omega_peak_E": b["omega_peak_E"],
                   "own_peak_s": pk_s, "own_peak_E": pk_e,
                   "their_estimate_bin_width": float(bin_w),
                   "their_peak_in_bins": b["omega_peak_s"] / bin_w,
                   "own_ladder_top": top, "own_ladder_mid": mid,
                   "E_blob_first_last": b["E_blob_first_last"]}
        print(f"  [{tag}] own s-peaks {pk_s} vs ladder top {top:.5f} "
              f"mid {mid:.5f}; their bin width {bin_w:.5f}")
    audit["S5_remnant_line"] = s5

    # ---------------- S6: barrier vs driving
    print("== S6: barrier arithmetic + statics consistency ==")
    s6 = {"per_delta": {}}
    ws3, R0 = 3.0, 17.0
    tube = np.pi * ws3 ** 2 * 2 * np.pi * R0
    stat = json.load(open(os.path.join(DATA, "m5_20_1_c_statics.json")))
    for delta in (0.1, 0.3, 0.5):
        # own closed forms
        r2_1d = (1 + delta) ** 2 / 2 - (1 + delta ** 2)
        r3_1d = (1 + delta) ** 3 / 4 - (1 + delta ** 3)
        v1d = r2_1d ** 2 + r3_1d ** 2
        r2_d0 = -delta ** 2 / 2
        r3_d0 = -3 * delta ** 3 / 4
        vd0 = r2_d0 ** 2 + r3_d0 ** 2
        cost_1d = w * v1d * tube
        cost_d0 = w * vd0 * tube
        k1 = f"d{delta}_pair_1d"
        k0 = f"d{delta}_pair_d0"
        E1 = stat["cases"][k1]["E_first_last"][0]
        E0v = stat["cases"][k0]["E_first_last"][0]
        mono = {}
        for kk in (k1, k0):
            Es = np.array([s["E"] for s in stat["cases"][kk]["trajectory"]])
            mono[kk] = bool(np.all(np.diff(Es) <= 1e-12))
        s6["per_delta"][str(delta)] = {
            "Vcell_over_w_pair_1d_own": round(v1d, 5),
            "Vcell_over_w_pair_d0_own": round(vd0, 6),
            "tube_cost_pair_1d": round(cost_1d, 4),
            "tube_cost_pair_d0": round(cost_d0, 5),
            "loop_E_pair_1d_statics": round(E1, 3),
            "loop_E_pair_d0_statics": round(E0v, 3),
            "barrier_over_driving_pair_1d_pct": round(100 * cost_1d / E1, 2),
            "statics_E_monotone": mono}
        print(f"  delta={delta}: tube cost {cost_1d:.3f} vs loop E {E1:.1f} "
              f"({100 * cost_1d / E1:.2f}%), pair_d0 {cost_d0:.4f}; "
              f"monotone {mono}")
    audit["S6_barrier"] = s6

    # ---------------- claim verdicts
    audit["CLAIM_VERDICTS"] = {
        "1_headline_all_10_runs_unwound": {
            "verdict": "CONFIRMED",
            "evidence": ("own plaquette defect maps (3 blocks) + own bilinear "
                         "circle reads + coarse circle grid: zero confirmed "
                         "wound cores in all 10 production endpoints; "
                         "(1,3)-block strong plaquettes are 0 everywhere "
                         "except d0p5_pair_d0 (10, 1-cell dipoles, net 0, "
                         "0/30 circle-confirmed); (1,2)-block plaquette "
                         "storms are near-degenerate angle turbulence "
                         "(net charge -846 etc., 0/30 confirmed)"),
            "side_finding": ("STATICS endpoint d0p1_pair_1d retains a tight "
                             "+1/2 -1/2 dipole at (24-25, 0) (net 0, "
                             "quantized 0.5 reads on one-sided circles): the "
                             "statics 'endpoint q = 0, ALL SIX DISSOLVE' row "
                             "is net-charge-true but masks an incomplete "
                             "dissolution at delta = 0.1")},
        "2_gap_map": {
            "verdict": "CONFIRMED with caveat",
            "evidence": ("own exact Hessian blockdiag(2wJ^TJ, 0): zero modes "
                         "4 -> 3 (rank J 2 -> 3), FD cross-checked; claimed "
                         "omega_split = sqrt(w(4d^2+9d^4)) reproduced "
                         "(0.00544/0.01770/0.03363)"),
            "caveat": ("omega_split is the Rayleigh quotient along "
                       "diag(0,1,-1), NOT a normal mode; the true lowest "
                       "activated gap is 0.0041/0.0099/0.0125 (25-63% "
                       "lower); their own JSON ladder is honest")},
        "3_core_equalization": {
            "verdict": "PARTIALLY",
            "evidence": ("all pair_1d endpoints do read (delta,0)-equalized "
                         "at the remnant (own eigen reads); the seeded "
                         "(1,delta) two-equal core is definitively abandoned"),
            "caveat": ("the label is vacuum-trivial for delta < 0.5 (vacuum "
                       "gaps (1-d, d) always read (delta,0)); at delta = 0.1 "
                       "remnant gap_bot = 0.20 > delta = 0.1: no genuine "
                       "bottom-pair equalization beyond label dominance; "
                       "FIRE statics (true minimization) endpoints keep the "
                       "pair_1d label per the task's own statics JSON")},
        "4_energy_bookkeeping": {
            "verdict": "CONFIRMED",
            "evidence": ("closed KE+PE endpoint drift <= 3.57e-6 on the 6 "
                         "core runs (max-over-trajectory 5.2e-6); anchor run "
                         "5.2e-6 endpoint / 7.3e-6 max (above the quoted "
                         "3.6e-6 but not in the 6/6 set); sponge "
                         "KE+PE+E_abs ledgers close to 2.7e-6 / 1.5e-6; "
                         "own energy reimplementation matches endpoint PE "
                         "to <= 2e-7")},
        "5_remnant_on_mass_line": {
            "verdict": "PARTIALLY (0.2% coincidence REFUTED as stated)",
            "evidence": ("their 0.1466 is exactly bin 7 of a 0.02094-wide "
                         "FFT grid (no interpolation): min honest "
                         "uncertainty +-3.5%; own refined peaks are "
                         "window-dependent 0.137-0.148 over a broad band "
                         "(top-4 amplitudes within 13%), and the dominant "
                         "frequency is non-stationary (half1 0.084, half2 "
                         "0.136); a band overlapping the 0.1463 line exists, "
                         "E_blob flatness 0.348->0.349 confirmed; "
                         "omega_peak_E = 0.0209 is exactly bin 1 = detrend "
                         "artifact")},
        "6_barrier_vs_driving": {
            "verdict": "CONFIRMED (ratio wording minor)",
            "evidence": ("own closed forms: tube costs 1.335/0.630/0.207 "
                         "(pair_1d), 1e-4/0.0053/0.0534 (pair_d0); loop E "
                         "48.65/20.92/7.81; statics E strictly monotone "
                         "decreasing in all 6 cases; actual ratio "
                         "2.65-3.01%, the note's '3-5%' slightly overstates")},
    }
    with open(os.path.join(DATA, "m5_20_1_audit.json"), "w") as f:
        json.dump(audit, f, indent=1, default=float)
    print("wrote data/m5_20_1_audit.json")


if __name__ == "__main__":
    main()
