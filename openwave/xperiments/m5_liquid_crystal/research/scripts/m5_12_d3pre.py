"""M5.12 D3-pre: the V_4D recalibration of the static instrument (REQUIRED
before any BVP number, per m5_12_d3_bvp_design.md § 6).

The 4D potential (p = 1..4, covariant m00 = -g, delta = 0) shifts undressed
statics by the p4 term (39% of V on the hedgehog seed: gate DG1). This
driver reruns the M5.16/18 anchor chain under V_4D:
    - on the uniaxial radial profile M_sp = s(r) n n^T with m00 = -g:
        V_4D(s)/w = SUM_{p=1..4} (s^p - 1)^2   (the exact DG1 reduction)
    - w re-fixed by the seed virial balance (the M5.16 autochi protocol)
    - anchors: c2 = alpha hbar c / 64 pi (curvature-side, carries over);
      ell = c2 E_sim / m_e; r_half_phys = c2 J_half / m_e
    - h-family 64/96/128, virials, Richardson: the recalibrated card.
Also implements + FD-gates the FIELD-level dV_4D/dM (needed by D3a's
residual and any 2D relax in the dressed class).

Run:  python m5_12_d3pre.py gates
      python m5_12_d3pre.py calibrate
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import G_TIME, cell_weights, curvature_density_np, \
    ext_tail, grid_coords                                                  # noqa: E402
from m5_16_axisym import _field_from_profile, _radial_basis, golden_line   # noqa: E402
from m5_18_spectral import (C2_PHYS, M_E_C2, R_HALF_FABER_FM,              # noqa: E402
                            R_HALF_LDG_FM)
from m5_12_dressed import ETA, to_covariant, v4d_density                   # noqa: E402


def dv4d_dm(Mc, wscale, g=G_TIME):
    """field-level dV_4D/dM on cell values Mc (..., 4, 4), symmetrized.
    T_p = tr((eta M)^p); dT_p/dM = p * sym( eta (eta M)^{p-1} )^T-pattern,
    FD-gated below (gate P1)."""
    EM = np.einsum("ab,...bc->...ac", ETA, Mc)
    G = np.zeros_like(Mc)
    P = np.broadcast_to(np.eye(4), Mc.shape)     # (eta M)^{p-1}, p=1 -> I
    for p in range(1, 5):
        cp = g ** p + 1.0
        EMp = np.einsum("...ab,...bc->...ac", P, EM)   # (eta M)^p
        tr = np.einsum("...aa->...", EMp)[..., None, None]
        # gradient of T_p wrt M: p * ( P eta )^T with P = (eta M)^{p-1}
        Gp = p * np.swapaxes(np.einsum("...ab,bc->...ac", P, ETA), -1, -2)
        Gp = 0.5 * (Gp + np.swapaxes(Gp, -1, -2))
        G = G + 2.0 * (tr - cp) * Gp
        P = EMp
    return wscale * G


def run_gates(nr=48, nz=96, h=1.0):
    from m5_17_energy import hedgehog_field
    R, Z = grid_coords(nr, nz, h)
    M4 = to_covariant(hedgehog_field(R, Z, 6.0))
    w = cell_weights(nr, nz, h)
    wsc = 0.29
    res = {}
    # P1: field-level dV4D/dM vs FD (directional, symmetric spatial+time)
    Mc = M4[: nr - 1, 1:-1]
    G = dv4d_dm(Mc, wsc) * w[..., None, None]
    rng = np.random.default_rng(5)
    eps, worst = 1e-6, 0.0

    def E_of(MM):
        M2 = M4.copy()
        M2[: nr - 1, 1:-1] = MM
        return float(np.sum(v4d_density(M2, wsc) * w))

    for _ in range(6):
        Dc = rng.normal(size=Mc.shape)
        D = 0.5 * (Dc + np.swapaxes(Dc, -1, -2))
        num = (E_of(Mc + eps * D) - E_of(Mc - eps * D)) / (2 * eps)
        an = float(np.sum(G * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-12))
    res["P1_dV4D_gradcheck"] = worst
    # P2: the uniaxial-profile reduction V_4D(s)/w = sum_{p=1..4}(s^p - 1)^2
    s = 0.63
    Mn = np.zeros((2, 3, 4, 4))
    Mn[0, 1, 0, 0] = -G_TIME
    Mn[0, 1, 3, 3] = s
    v_field = float(v4d_density(Mn, 1.0)[0, 0])
    v_prof = sum((s ** p - 1.0) ** 2 for p in range(1, 5))
    res["P2_profile_reduction"] = abs(v_field - v_prof)
    ok = {
        "P1 dV4D/dM analytic == FD": res["P1_dV4D_gradcheck"] < 1e-6,
        "P2 uniaxial V_4D(s) reduction": res["P2_profile_reduction"] < 1e-12,
    }
    for k, v in ok.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    for k, v in res.items():
        print(f"    {k} = {v:.3e}")
    res["all_pass"] = all(ok.values())
    with open(os.path.join(DATA, "m5_12_d3pre_gates.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res["all_pass"]


def run_radial_v4(nr, nz, h=1.0, iters=8000, rc_seed=8.0):
    """the M5.18 run_radial pattern with V_4D(s) on the profile."""
    dr = 0.5 * h
    r_cell, lo, frac, n_knots, nn = _radial_basis(nr, nz, h, dr)
    rk = np.arange(n_knots) * dr
    s0 = 1.0 - np.exp(-((rk / rc_seed) ** 2))
    M0 = _field_from_profile(s0, lo, frac, nn, nr, nz)
    M0 = to_covariant(M0)
    w = cell_weights(nr, nz, h)
    Ecurv = float(np.sum(curvature_density_np(M0, h, 1.0) * w)) + ext_tail(
        (nr - 1) * h, (nz / 2 - 1) * h)
    Epot1 = float(np.sum(v4d_density(M0, 1.0) * w))
    wscale = Ecurv / (3.0 * Epot1) if Epot1 > 0 else 1.0

    def E_of(s):
        M = to_covariant(_field_from_profile(s, lo, frac, nn, nr, nz))
        return float(np.sum((curvature_density_np(M, h, 1.0)
                             + v4d_density(M, wscale)) * w)) + ext_tail(
            (nr - 1) * h, (nz / 2 - 1) * h)

    r_pin = min((nr - 4) * h, (nz / 2 - 4) * h)
    freek = (rk <= r_pin).astype(float)

    def g_of(s):
        M = to_covariant(_field_from_profile(s, lo, frac, nn, nr, nz))
        Gc = np.zeros_like(M)
        # curvature gradient: reuse the gated static adjoints with (a,b,c)=0
        from m5_17_energy import energy_gradient_np
        Gc = energy_gradient_np(M, 0.0, 0.0, 0.0, 1.0, h, 0.0)
        Gc[: nr - 1, 1:-1] += dv4d_dm(M[: nr - 1, 1:-1], wscale) \
            * w[..., None, None]
        proj = np.sum(Gc[: nr - 1, 1:-1] * nn, axis=(-2, -1))
        g = np.zeros(n_knots)
        np.add.at(g, lo, proj * (1.0 - frac))
        np.add.at(g, lo + 1, proj * frac)
        return g * freek

    # chain gradcheck
    eps, errs = 1e-7, []
    g_an = g_of(s0)
    for k in (2, 8, 16, 30, 60):
        if k >= n_knots or not freek[k]:
            continue
        sp, sm = s0.copy(), s0.copy()
        sp[k] += eps
        sm[k] -= eps
        errs.append(abs((E_of(sp) - E_of(sm)) / (2 * eps) - g_an[k])
                    / (abs(g_an[k]) + 1e-12))
    gc = float(np.max(errs))
    # FIRE + CG polish (the m5_18 pattern)
    t0 = time.time()
    mass = np.zeros(n_knots)
    np.add.at(mass, lo, (1.0 - frac) * w)
    np.add.at(mass, lo + 1, frac * w)
    mass = np.maximum(mass, np.max(mass) * 1e-6)
    s, v = s0.copy(), np.zeros(n_knots)
    dt, dt_max, alpha, n_pos = 0.02, 0.5, 0.1, 0
    g = g_of(s)
    g0n = float(np.sqrt(np.sum(g * g)))
    for it in range(1, iters + 1):
        F = -g / mass
        v = v + dt * F
        if float(np.sum(F * v)) > 0:
            n_pos += 1
            if n_pos > 5:
                dt = min(dt * 1.1, dt_max)
                alpha *= 0.99
            fn, vn = np.sqrt(np.sum(F * F)), np.sqrt(np.sum(v * v))
            v = (1 - alpha) * v + alpha * (vn / (fn + 1e-30)) * F
        else:
            n_pos, dt, alpha = 0, dt * 0.5, 0.1
            v[:] = 0.0
        s = s + dt * v
        g = g_of(s)
        gn = float(np.sqrt(np.sum(g * g)))
        if gn < 1e-5 * g0n or gn < 1e-9:
            break
    d = -g_of(s) / mass
    gc2 = g_of(s)
    for it in range(200):
        dn = float(np.sqrt(np.sum(d * d)))
        if dn < 1e-14:
            break
        t_star = golden_line(lambda tt: E_of(s + tt * d), min(0.05, 1.0 / dn))
        s = s + t_star * d
        g2 = g_of(s)
        z2 = g2 / mass
        bpr = max(0.0, float(np.sum(g2 * (z2 - gc2 / mass)))
                  / (float(np.sum(gc2 * gc2 / mass)) + 1e-300))
        d = -z2 + bpr * d
        if float(np.sum(d * g2)) > 0:
            d = -g2
        gc2 = g2
    E_best = E_of(s)
    # observables on the converged field
    Mb = to_covariant(_field_from_profile(s, lo, frac, nn, nr, nz))
    dcurv = curvature_density_np(Mb, h, 1.0)
    dpot = v4d_density(Mb, wscale)
    E_c = float(np.sum(dcurv * w)) + ext_tail((nr - 1) * h, (nz / 2 - 1) * h)
    E_p = float(np.sum(dpot * w))
    RHO, ZZ = grid_coords(nr, nz, h)
    Rin = np.sqrt(RHO[: nr - 1, 1:-1] ** 2 + ZZ[: nr - 1, 1:-1] ** 2)
    dens = (dcurv + dpot) * w
    rmax = min((nr - 1) * h, (nz / 2 - 1) * h)
    nb = int(rmax / (0.5 * h))
    edges = np.linspace(0.0, rmax, nb + 1)
    idx = np.clip(np.digitize(Rin.ravel(), edges) - 1, 0, nb - 1)
    inside = (Rin < rmax).ravel()
    cum = np.cumsum(np.bincount(idx[inside], weights=dens.ravel()[inside],
                                minlength=nb))
    E_tot = E_best
    k = int(np.searchsorted(cum, 0.5 * E_tot))
    r_half = 0.5 * (edges[k] + edges[k + 1]) if 0 < k < nb else float("nan")
    return {"NR": nr, "NZ": nz, "E_sim": E_tot, "r_half_sim": float(r_half),
            "J_half": E_tot * float(r_half), "wscale": wscale,
            "virial": E_c / (3.0 * E_p) if E_p else float("inf"),
            "gradcheck": gc, "wall_s": round(time.time() - t0, 1)}


def run_calibrate():
    rows = []
    for (nr, nz) in [(64, 128), (96, 192), (128, 256)]:
        r = run_radial_v4(nr, nz, rc_seed=8.0 * nr / 96)
        r["ell_fm"] = C2_PHYS * r["E_sim"] / M_E_C2
        r["r_half_phys_fm"] = C2_PHYS * r["J_half"] / M_E_C2
        rows.append(r)
        print(f"[v4-radial] n{nr} E={r['E_sim']:.4f} r_half={r['r_half_sim']:.2f} "
              f"J={r['J_half']:.2f} r_half_phys={r['r_half_phys_fm']:.4f} fm "
              f"vir={r['virial']:.4f} gc={r['gradcheck']:.1e} wall={r['wall_s']}s")
    main = rows[1]
    out = {"task": "M5.12", "script": "m5_12_d3pre.py", "mode": "calibrate",
           "potential": "V_4D p=1..4, covariant m00=-g, delta=0 (uniaxial"
                        " profile V(s)/w = sum_{p=1..4}(s^p-1)^2)",
           "rows": rows,
           "headline_r_half_phys_fm": main["r_half_phys_fm"],
           "vs_faber_rel": main["r_half_phys_fm"] / R_HALF_FABER_FM - 1.0,
           "vs_ldg_rel": main["r_half_phys_fm"] / R_HALF_LDG_FM - 1.0,
           "vs_spectral3d_2935": main["r_half_phys_fm"] / 2.9352 - 1.0,
           "note": "the D3-pre recalibrated card: the BVP compares against"
                   " THESE numbers, not the 3D-spectral ones"}
    with open(os.path.join(DATA, "m5_12_d3pre_lock.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"HEADLINE r_half(V_4D) = {main['r_half_phys_fm']:.4f} fm "
          f"(3D-spectral 2.9352, LdG 2.926, Faber {R_HALF_FABER_FM})")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gates"
    if mode == "gates":
        ok = run_gates()
        sys.exit(0 if ok else 1)
    elif mode == "calibrate":
        run_calibrate()
    else:
        print(f"unknown mode {mode}")
