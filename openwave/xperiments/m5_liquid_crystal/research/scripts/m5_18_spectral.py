"""M5.18 phase B: Duda's universal spectral potential, swapped into the
calibrated static instrument.

THE POTENTIAL (Duda 2026-07-05, m5_17_convo.md entry 2)
    V(M) = w . SUM_p ( Tr(M_sp^p) - c_p )^2 ,   c_p = SUM_i Lambda_i^p ,
    3D statics on the spatial block, preferred eigenvalues
    Lambda = (1, delta, 0);  electron sector delta = 0  =>  c_p = 1, p = 1..3.
    Sum-of-squares: V = 0 EXACTLY at the target spectrum, dV/ds = 0 there
    term by term (no zero-forcing tuning; the LdG a = (3b-4c)/2 condition
    is automatic), and NO shape ratio survives: the quartic-LdG beta = b/c
    slot dissolves. One overall scale w remains; like the LdG cscale it is
    a LENGTH-SCALE choice (Derrick), fixed by the seed virial balance
    (identical protocol to M5.16 autochi), and the physical prediction is
    the scale-invariant J_half = E_sim . r_half_sim.

    On the uniaxial profile M_sp = s(r) n n^T (delta = 0):
        V(s)/w = (s-1)^2 + (s^2-1)^2 + (s^3-1)^2 ,    V(0)/w = 3
    vs the quartic LdG melt cost (c - b/2)/cscale = 1 - beta/2 (= 1/2 at
    beta = 1): the melt-channel economics change by construction; whether
    the channel CLOSES is measured here (mode stability), the empirical
    Q14 test.

    dV/dM_sp = w [ 2(Tr M - c1) I + 4(Tr M^2 - c2) M + 6(Tr M^3 - c3) M^2 ]

CURVATURE, SEEDS, MINIMIZERS: imported UNCHANGED from m5_17_energy.py /
m5_16_axisym.py (the M5.16-gated stack; curvature is potential-independent,
so gates G1/G3/G4/G6/G8 are inherited verbatim). The gradient assembly
reuses energy_gradient_np with (a,b,c) = 0 (pure curvature adjoints) plus
the spectral dV scattered into the spatial block, and is FD-gated here
(gate S1).

ANCHOR CHAIN (identical to m5_16_calibrate.py, minus the beta sweep):
    c2 = alpha hbar c / 64 pi (Coulomb, analytic, potential-independent)
    ell = c2 E_sim / m_e   [fm/grid unit]
    r_half_phys = c2 J_half / m_e   -> compare Faber 3.075 fm and the
    quartic-LdG 2.926 fm. With beta gone this number is PARAMETER-FREE
    given the equal-weight potential (the remaining freedom Duda flags:
    per-p weights).

Run:  python m5_18_spectral.py gates
      python m5_18_spectral.py radial [NR NZ] [--iters N] [--tag T]
      python m5_18_spectral.py stability [NR NZ]
      python m5_18_spectral.py calibrate      (radial at 64/96/128 + lock)
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
os.makedirs(DATA, exist_ok=True)

from m5_17_energy import (G_TIME, cell_weights, curvature_density_np,     # noqa: E402
                          energy_gradient_np, ext_tail, grid_coords)
from m5_16_axisym import (_field_from_profile, _radial_basis, fire_relax,  # noqa: E402
                          golden_line, pin_mask)

# ---- physical constants (CODATA 2018, as m5_16_calibrate.py) ----
HBAR_C = 197.3269804
ALPHA_F = 1.0 / 137.035999084
M_E_C2 = 0.51099895
R0_FABER = 2.21320516
C2_PHYS = ALPHA_F * HBAR_C / (64.0 * np.pi)
R_HALF_FABER_FM = 3.0754            # m5_16_calibrate.py faber_r_half()
R_HALF_LDG_FM = 2.926               # M5.16 lock headline (beta-flat)

CPS_D0 = (1.0, 1.0, 1.0)            # c_p at delta = 0, p = 1..3


# ---------------- THE SPECTRAL POTENTIAL (the physics of this task) ----
def potential_density_spec_np(Mnp, wscale, cps=CPS_D0):
    """V = w SUM_p (Tr(M_sp^p) - c_p)^2 on included cells (mirrors the
    m5_17_energy potential_density_np cell block)."""
    msp = Mnp[: Mnp.shape[0] - 1, 1:-1, 1:4, 1:4]
    m2 = np.einsum("...ab,...bc->...ac", msp, msp)
    tr1 = np.einsum("...aa->...", msp)
    tr2 = np.einsum("...aa->...", m2)
    tr3 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, msp))
    return wscale * ((tr1 - cps[0]) ** 2 + (tr2 - cps[1]) ** 2
                     + (tr3 - cps[2]) ** 2)


def dv_spec(msp, wscale, cps=CPS_D0):
    """dV/dM_sp = w [2(t1-c1) I + 4(t2-c2) M + 6(t3-c3) M^2]."""
    m2 = np.einsum("...ab,...bc->...ac", msp, msp)
    tr1 = np.einsum("...aa->...", msp)[..., None, None]
    tr2 = np.einsum("...aa->...", m2)[..., None, None]
    tr3 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, msp))[..., None, None]
    eye = np.broadcast_to(np.eye(3), msp.shape)
    return wscale * (2.0 * (tr1 - cps[0]) * eye + 4.0 * (tr2 - cps[1]) * msp
                     + 6.0 * (tr3 - cps[2]) * m2)


def total_energy_spec_np(Mnp, wscale, h, cps=CPS_D0):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return float(np.sum((curvature_density_np(Mnp, h, 1.0)
                         + potential_density_spec_np(Mnp, wscale, cps)) * w))


def energy_gradient_spec_np(Mnp, wscale, h, cps=CPS_D0):
    """curvature adjoints via energy_gradient_np with (a,b,c)=0 (they are
    the m5_17_energy gated adjoints, unchanged), plus the spectral dV."""
    nr, nz = Mnp.shape[:2]
    G = energy_gradient_np(Mnp, 0.0, 0.0, 0.0, 1.0, h, 0.0)
    w = cell_weights(nr, nz, h)[..., None, None]
    msp = Mnp[: nr - 1, 1:-1, 1:4, 1:4]
    G[: nr - 1, 1:-1, 1:4, 1:4] += dv_spec(msp, wscale, cps) * w
    return G


# ---------------- observables (mirrors m5_16_axisym.observables verbatim,
# potential line swapped to the spectral form) ----------------
def observables_spec(Mnp, wscale, h, cps=CPS_D0):
    nr, nz = Mnp.shape[:2]
    w = cell_weights(nr, nz, h)
    dcurv = curvature_density_np(Mnp, h, 1.0)
    dpot = potential_density_spec_np(Mnp, wscale, cps)
    E_curv_num = float(np.sum(dcurv * w))
    E_pot_num = float(np.sum(dpot * w))
    Rc = (nr - 1) * h
    Hh = (nz / 2 - 1) * h
    E_ext = ext_tail(Rc, Hh)          # vacuum tail: V_spec(vac) = 0 exactly
    E_tot = E_curv_num + E_pot_num + E_ext
    RHO, ZZ = grid_coords(nr, nz, h)
    Rin = np.sqrt(RHO[: nr - 1, 1:-1] ** 2 + ZZ[: nr - 1, 1:-1] ** 2)
    dens = (dcurv + dpot) * w
    rmax = min(Rc, Hh)
    nbins = int(rmax / (0.5 * h))
    edges = np.linspace(0.0, rmax, nbins + 1)
    idx = np.clip(np.digitize(Rin.ravel(), edges) - 1, 0, nbins - 1)
    inside = (Rin < rmax).ravel()
    e_r_in = np.bincount(idx[inside], weights=dens.ravel()[inside], minlength=nbins)
    cum = np.cumsum(e_r_in)
    target = 0.5 * E_tot
    k = int(np.searchsorted(cum, target))
    if 0 < k < nbins:
        r_lo, r_hi = edges[k], edges[k + 1]
        c_lo = cum[k - 1]
        frac = (target - c_lo) / max(cum[k] - c_lo, 1e-300)
        r_half = r_lo + frac * (r_hi - r_lo)
    else:
        r_half = float("nan")
    msp = Mnp[: nr - 1, 1:-1, 1:4, 1:4]
    s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    cnt = np.bincount(idx, minlength=nbins).astype(float)
    s_r = np.bincount(idx, weights=s_cell.ravel(), minlength=nbins) / np.maximum(cnt, 1)
    virial = E_curv_num + E_ext
    return {
        "E_curv_num": E_curv_num, "E_pot_num": E_pot_num, "E_ext_tail": E_ext,
        "E_tot": E_tot,
        "virial_ratio_curv_over_3pot": virial / (3.0 * E_pot_num) if E_pot_num != 0 else float("inf"),
        "r_half": float(r_half),
        "r_bins": (0.5 * (edges[:-1] + edges[1:])).tolist(),
        "s_profile": s_r.tolist(),
    }


# ---------------- gates ----------------
def run_gates(nr=48, nz=96, h=1.0):
    from m5_17_energy import hedgehog_field
    R, Z = grid_coords(nr, nz, h)
    M0 = hedgehog_field(R, Z, 6.0)
    res = {}
    # S1: analytic gradient vs central FD, DIRECTIONAL (random symmetric
    # interior spatial-block directions: per-entry FD is conditioning-limited
    # at ~5e-5 because single-entry gradients are tiny; the directional
    # aggregate resolves to ~1e-8)
    wsc = 0.37
    G = energy_gradient_spec_np(M0, wsc, h)
    rng = np.random.default_rng(3)
    eps, worst = 1e-6, 0.0
    for _ in range(6):
        Dc = rng.normal(size=(nr - 1, nz - 2, 4, 4))
        D = np.zeros_like(M0)
        D[: nr - 1, 1:-1] = 0.5 * (Dc + np.swapaxes(Dc, -1, -2))
        D[..., 0, :] = 0.0
        D[..., :, 0] = 0.0
        num = (total_energy_spec_np(M0 + eps * D, wsc, h)
               - total_energy_spec_np(M0 - eps * D, wsc, h)) / (2 * eps)
        an = float(np.sum(G * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-12))
    res["S1_gradcheck_max_rel"] = worst
    # S2: vacuum structure: V(s=1) = 0, dV/ds(1) = 0, V(0) = 3w, all exact
    def v_of_s(s):
        Mn = np.zeros((2, 3, 4, 4))
        Mn[0, 1, 1, 1] = s              # spectrum (s, 0, 0)
        return float(potential_density_spec_np(Mn, 1.0)[0, 0])
    res["S2_V_at_1"] = v_of_s(1.0)
    res["S2_dVds_at_1"] = (v_of_s(1.0 + 1e-7) - v_of_s(1.0 - 1e-7)) / 2e-7
    res["S2_V_at_0_minus_3"] = v_of_s(0.0) - 3.0
    # S3: exact biaxial pinning: V = 0 at spectrum (1, delta, 0), delta != 0
    delta = 0.3
    cps = (1.0 + delta, 1.0 + delta ** 2, 1.0 + delta ** 3)
    Mn = np.zeros((2, 3, 4, 4))
    Mn[0, 1, 1, 1], Mn[0, 1, 2, 2] = 1.0, delta
    res["S3_V_biaxial_pinned"] = float(potential_density_spec_np(Mn, 1.0, cps)[0, 0])
    ok = {
        "S1 gradient (analytic == FD)": res["S1_gradcheck_max_rel"] < 1e-5,
        "S2 vacuum: V(1)=0, V'(1)=0, V(0)=3w": max(abs(res["S2_V_at_1"]), abs(res["S2_dVds_at_1"]), abs(res["S2_V_at_0_minus_3"])) < 1e-6,
        "S3 biaxial (1,delta,0) EXACTLY pinned": abs(res["S3_V_biaxial_pinned"]) < 1e-15,
    }
    for k, v in ok.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    for k, v in res.items():
        print(f"    {k} = {v:.3e}")
    res["all_pass"] = all(ok.values())
    with open(os.path.join(DATA, "m5_18_spectral_gates.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res


# ---------------- constrained radial solve (mirrors m5_16 run_radial) ----
def run_radial(nr=96, nz=192, h=1.0, iters=8000, rc_seed=8.0, tag=None):
    dr = 0.5 * h
    r_cell, lo, frac, n_knots, nn = _radial_basis(nr, nz, h, dr)
    rk = np.arange(n_knots) * dr
    s0 = 1.0 - np.exp(-((rk / rc_seed) ** 2))
    # w from the seed virial balance (the M5.16 autochi protocol)
    M0 = _field_from_profile(s0, lo, frac, nn, nr, nz)
    w = cell_weights(nr, nz, h)
    Ecurv = float(np.sum(curvature_density_np(M0, h, 1.0) * w)) + ext_tail(
        (nr - 1) * h, (nz / 2 - 1) * h)
    Epot1 = float(np.sum(potential_density_spec_np(M0, 1.0) * w))
    wscale = Ecurv / (3.0 * Epot1) if Epot1 > 0 else 1.0
    r_pin = min((nr - 4) * h, (nz / 2 - 4) * h)
    freek = (rk <= r_pin).astype(float)

    def E_of(s):
        return total_energy_spec_np(_field_from_profile(s, lo, frac, nn, nr, nz), wscale, h)

    def g_of(s):
        Mnp = _field_from_profile(s, lo, frac, nn, nr, nz)
        G = energy_gradient_spec_np(Mnp, wscale, h)
        proj = np.sum(G[: nr - 1, 1:-1] * nn, axis=(-2, -1))
        g = np.zeros(n_knots)
        np.add.at(g, lo, proj * (1.0 - frac))
        np.add.at(g, lo + 1, proj * frac)
        return g * freek

    mass = np.zeros(n_knots)
    np.add.at(mass, lo, (1.0 - frac) * w)
    np.add.at(mass, lo + 1, frac * w)
    mass = np.maximum(mass, np.max(mass) * 1e-6)
    # chain gradcheck
    eps, errs = 1e-7, []
    g_an = g_of(s0)
    for k in (2, 8, 16, 30, 60):
        if k >= n_knots or not freek[k]:
            continue
        sp, sm = s0.copy(), s0.copy()
        sp[k] += eps
        sm[k] -= eps
        num = (E_of(sp) - E_of(sm)) / (2 * eps)
        errs.append(abs(num - g_an[k]) / (abs(num) + abs(g_an[k]) + 1e-12))
    gc = float(np.max(errs))
    # FIRE on the profile
    t0 = time.time()
    s, v = s0.copy(), np.zeros_like(s0)
    dt, dt_max, alpha, n_pos = 0.02, 0.5, 0.1, 0
    g = g_of(s)
    g0n = float(np.sqrt(np.sum(g * g)))
    Es = [E_of(s)]
    for it in range(1, iters + 1):
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
            n_pos, dt, alpha = 0, dt * 0.5, 0.1
            v[:] = 0.0
        s = s + dt * v
        g = g_of(s)
        gn = float(np.sqrt(np.sum(g * g)))
        if it % 500 == 0:
            Es.append(E_of(s))
        if gn < 1e-5 * g0n or gn < 1e-9:
            break
    t_fire = time.time() - t0
    # CG polish
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
    Mb = _field_from_profile(sc, lo, frac, nn, nr, nz)
    obs = observables_spec(Mb, wscale, h)
    mono = all(Es[i + 1] <= Es[i] + 1e-9 for i in range(len(Es) - 1))
    tag = tag or f"spec_n{nr}"
    out = {
        "task": "M5.18", "script": "m5_18_spectral.py", "mode": "radial",
        "potential": "V = w sum_p (Tr(Msp^p) - 1)^2, p=1..3 (delta=0)",
        "grid": {"NR": nr, "NZ": nz, "h": h, "n_knots": int(n_knots)},
        "params": {"wscale": wscale, "rc_seed": rc_seed, "iters": iters,
                   "melt_cost_per_cell": 3.0 * wscale},
        "chain_gradcheck_max_rel": gc,
        "E_best": E_best, "monotone_fire": bool(mono),
        "wall_s": round(t_fire, 1), "obs": obs,
        "s_knots_r": rk[:: max(1, n_knots // 200)].tolist(),
        "s_knots": sc[:: max(1, n_knots // 200)].tolist(),
    }
    path = os.path.join(DATA, f"m5_18_spectral_{tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[radial-spec] n{nr} w={wscale:.4e} E_best={E_best:.4f} "
          f"r_half={obs['r_half']:.3f} virial={obs['virial_ratio_curv_over_3pot']:.4f} "
          f"gradcheck={gc:.2e} mono={mono} wall={t_fire:.0f}s")
    return out, Mb, wscale


# ---------------- stability probe (mirrors m5_16 run_stability) ----------
def run_stability(nr=96, nz=192, h=1.0, iters=8000, rc_seed=8.0):
    out_r, Mb, wscale = run_radial(nr, nz, h, iters, rc_seed,
                                   tag=f"spec_n{nr}_pre_stability")
    E_radial = out_r["E_best"]
    R, Z = grid_coords(nr, nz, h)
    bump = 0.03 * np.exp(-(((R - 0.8 * rc_seed) ** 2) + (Z - 0.5 * rc_seed) ** 2)
                         / (rc_seed ** 2))
    Mp = Mb.copy()
    Mp[..., 1, 3] += bump
    Mp[..., 3, 1] += bump
    Mp[..., 2, 2] += 0.5 * bump
    pin = pin_mask(nr, nz)
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(nr, nz, h)
    wfull = np.ones((nr, nz))
    wfull[: nr - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    def egf(MM):
        return (total_energy_spec_np(MM, wscale, h),
                energy_gradient_spec_np(MM, wscale, h))

    Mf, hist = fire_relax(Mp, egf, free4, precond, max_iter=iters)
    E_end = hist["E"][-1]
    msp = Mf[: nr - 1, 1:-1, 1:4, 1:4]
    s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    k = np.unravel_index(np.argmin(s_cell), s_cell.shape)
    escaped = bool(E_end < E_radial - 0.05 * abs(E_radial))
    out = {
        "task": "M5.18", "mode": "stability",
        "potential": "spectral (delta=0)", "wscale": wscale,
        "melt_cost_per_cell": 3.0 * wscale,
        "E_radial": E_radial, "E_after_perturbed_2d_relax": E_end,
        "drop_rel": (E_radial - E_end) / abs(E_radial),
        "escaped_hedgehog": escaped,
        "melt_min_s": float(np.min(s_cell)),
        "melt_min_location_rho_z": [float((k[0] + 0.5) * h),
                                    float((k[1] - (nz - 2) / 2 + 0.5) * h)],
        "gnorm_first_last": [hist["gnorm"][0], hist["gnorm"][-1]],
        "iters": iters,
        "note": "escaped=False would mean the spectral potential CLOSES the"
                " point-vs-ring melt channel (the Q14 empirical test);"
                " escaped=True means the channel survives the swap",
    }
    path = os.path.join(DATA, f"m5_18_spectral_n{nr}_stability.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[stability-spec] E_radial={E_radial:.4f} -> E_2d={E_end:.4f} "
          f"escaped={escaped} min_s={out['melt_min_s']:.3f} at "
          f"(rho,z)=({out['melt_min_location_rho_z'][0]:.1f},"
          f"{out['melt_min_location_rho_z'][1]:.1f})")
    return out


# ---------------- calibrate: anchor chain, no beta sweep -----------------
def run_calibrate():
    rows = []
    for (nr, nz) in [(64, 128), (96, 192), (128, 256)]:
        rc = 8.0 * nr / 96
        out, _, wsc = run_radial(nr, nz, iters=8000, rc_seed=rc,
                                 tag=f"spec_n{nr}")
        E_sim = out["obs"]["E_tot"]
        r_half = out["obs"]["r_half"]
        J = E_sim * r_half
        rows.append({"NR": nr, "NZ": nz, "E_sim": E_sim, "r_half_sim": r_half,
                     "J_half": J, "wscale": wsc,
                     "ell_fm": C2_PHYS * E_sim / M_E_C2,
                     "r_half_phys_fm": C2_PHYS * J / M_E_C2,
                     "virial": out["obs"]["virial_ratio_curv_over_3pot"]})
    main = rows[1]
    lock = {
        "task": "M5.18", "date": "2026-07-05",
        "potential": "V = w sum_{p=1..3} (Tr(Msp^p) - 1)^2 (Duda universal"
                     " spectral form, delta = 0 electron sector, equal weights)",
        "anchors": {"coulomb_c2_MeV_fm": C2_PHYS, "mass_m_e_MeV": M_E_C2,
                    "faber_r_half_fm": R_HALF_FABER_FM,
                    "ldg_beta1_r_half_fm": R_HALF_LDG_FM},
        "rows": rows,
        "headline_r_half_phys_fm": main["r_half_phys_fm"],
        "vs_faber_rel": main["r_half_phys_fm"] / R_HALF_FABER_FM - 1.0,
        "vs_ldg_rel": main["r_half_phys_fm"] / R_HALF_LDG_FM - 1.0,
        "melt_cost_per_cell_3w": 3.0 * main["wscale"],
        "note": "no beta slot: the equal-weight spectral potential makes"
                " r_half parameter-free (remaining freedom: per-p weights)",
    }
    path = os.path.join(DATA, "m5_18_spectral_lock.json")
    with open(path, "w") as f:
        json.dump(lock, f, indent=2)
    print("=" * 72)
    for r in rows:
        print(f"NR={r['NR']:>4}  E_sim={r['E_sim']:8.3f}  r_half={r['r_half_sim']:6.2f}"
              f"  J={r['J_half']:8.2f}  ell={r['ell_fm']:.4f} fm"
              f"  r_half_phys={r['r_half_phys_fm']:.4f} fm  vir={r['virial']:.4f}")
    print(f"HEADLINE r_half = {main['r_half_phys_fm']:.4f} fm"
          f"  (Faber {R_HALF_FABER_FM}, LdG-beta1 {R_HALF_LDG_FM})")
    print(f"json -> {path}")
    return lock


# ---------------- antipair relax (mirrors m5_17_two_charge run_relax) ----
def run_pair(sign=-1, ds=(16.0, 24.0), nr=96, nz=192, h=1.0, iters=3000,
             rc_core=8.0):
    """the M5.17 annihilation-channel test on the spectral potential: pinned
    cores (2.5h disks), antipair seed, watch the near-axis melt strip. The
    potential scale w comes from the CALIBRATED hedgehog run (the instrument),
    not from the pair seed."""
    from m5_17_two_charge import pair_field
    with open(os.path.join(DATA, "m5_18_spectral_spec_n96.json")) as f:
        wscale = json.load(f)["params"]["wscale"]
    R, Z = grid_coords(nr, nz, h)
    r_pin = 2.5 * h
    rows = []
    for d in ds:
        M0 = pair_field(R, Z, d, rc_core, sign)
        r1 = np.sqrt(R ** 2 + (Z + 0.5 * d) ** 2)
        r2 = np.sqrt(R ** 2 + (Z - 0.5 * d) ** 2)
        pin = pin_mask(nr, nz) | (r1 < r_pin) | (r2 < r_pin)
        free4 = (~pin)[..., None, None].astype(float)
        w = cell_weights(nr, nz, h)
        wfull = np.ones((nr, nz))
        wfull[: nr - 1, 1:-1] = w
        precond = (1.0 / wfull)[..., None, None]

        def egf(MM):
            return (total_energy_spec_np(MM, wscale, h),
                    energy_gradient_spec_np(MM, wscale, h))

        t0 = time.time()
        Mf, hist = fire_relax(M0, egf, free4, precond, max_iter=iters,
                              tol_rel=1e-4)
        msp = Mf[: nr - 1, 1:-1, 1:4, 1:4]
        s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
        mid = s_cell[: int(4 / h), :]
        rows.append({"d": d, "E_seed": hist["E"][0], "E_relaxed": hist["E"][-1],
                     "drop": hist["E"][0] - hist["E"][-1],
                     "gnorm_decades": float(np.log10(
                         hist["gnorm"][0] / (hist["gnorm"][-1] + 1e-300))),
                     "melt_min_axis_strip": float(np.min(mid)),
                     "wall_s": round(time.time() - t0, 1)})
        print(f"[pair-spec q2={sign} d={d:g}] E {rows[-1]['E_seed']:.3f} -> "
              f"{rows[-1]['E_relaxed']:.3f} melt_min={rows[-1]['melt_min_axis_strip']:.3f} "
              f"decades={rows[-1]['gnorm_decades']:.1f} wall={rows[-1]['wall_s']}s")
    tag = "anti" if sign < 0 else "like"
    out = {"task": "M5.18", "mode": "pair_relax", "sign": sign,
           "potential": "spectral (delta=0)", "wscale": wscale,
           "grid": {"NR": nr, "NZ": nz, "h": h},
           "params": {"rc_core": rc_core, "r_pin": r_pin, "iters": iters},
           "rows": rows,
           "note": "M5.17 LdG reference: antipair ANNIHILATED at all d"
                   " (E_relaxed 0.30-0.59 vacuum residual, melt_min ~ 0.008"
                   " bridge along the axis strip). melt_min staying O(1)"
                   " here = the spectral potential closes the annihilation"
                   " melt bridge; melt_min -> 0 = channel survives"}
    path = os.path.join(DATA, f"m5_18_spectral_pair_{tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {path}")
    return out


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "gates"
    if mode == "gates":
        run_gates()
    elif mode == "radial":
        nr = int(sys.argv[2]) if len(sys.argv) > 2 else 96
        nz = int(sys.argv[3]) if len(sys.argv) > 3 else 2 * nr
        run_radial(nr, nz)
    elif mode == "stability":
        nr = int(sys.argv[2]) if len(sys.argv) > 2 else 96
        nz = int(sys.argv[3]) if len(sys.argv) > 3 else 2 * nr
        run_stability(nr, nz)
    elif mode == "calibrate":
        run_calibrate()
    elif mode == "pair":
        sign = int(sys.argv[2]) if len(sys.argv) > 2 else -1
        run_pair(sign=sign)
    else:
        print(f"unknown mode {mode}")
