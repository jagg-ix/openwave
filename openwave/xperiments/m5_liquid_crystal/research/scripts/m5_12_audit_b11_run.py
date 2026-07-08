"""M5.12 block-11 ADVERSARIAL AUDIT runner (independent auditor).

Attacks C1-C4 / T1-T6 (see m5_12_audit_b11.json for the verdict record).
Own functional implementations live in m5_12_audit_b11_lib.py; the
claimant's residual() is used ONLY after being re-gated here against finite
differences of the auditor's own independent Shat.

Run:  python m5_12_audit_b11_run.py [all|gates|states|seeds|breather|inject]
Writes: data/m5_12_audit_b11_numbers.json (raw numbers; the verdict JSON
m5_12_audit_b11.json is assembled by m5_12_audit_b11_verdicts.py).
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
sys.argv = sys.argv[:1]          # the m5_16_axisym import-time argv trap

import m5_12_audit_b11_lib as L                                     # noqa: E402
from m5_12_d3a_bvp import residual, shat as claimant_shat, x_pack   # noqa: E402
from m5_12_d3b_newton import rotor_seed, wscale_at                  # noqa: E402
from m5_17_energy import energy_gradient_np, curvature_density_np   # noqa: E402
from m5_12_d3pre import dv4d_dm                                     # noqa: E402
from m5_12_dressed import v4d_density                               # noqa: E402

STATES = {
    "n32": ("m5_12_d3b_axisswing_state.npz", 32),
    "n48": ("m5_12_d3b_axisswing_n48_state.npz", 48),
    "n64": ("m5_12_d3b_axisswing_n64_state_b10.npz", 64),
}
HIST = {
    "n32": "m5_12_d3b_axisswing.json",
    "n48": "m5_12_d3b_axisswing_n48.json",
    "n64": "m5_12_d3b_axisswing_n64.json",
}
OUT = {}


def rc_of(nr):
    return 8.0 * nr / 96.0


def wsc_of(nr):
    return wscale_at(nr, 2 * nr, 1.0, rc_of(nr))


def r_of_state(name):
    path = os.path.join(DATA, STATES[name][0])
    X, om = L.load_state(path)
    nr = STATES[name][1]
    return X, om, nr, 2 * nr, wsc_of(nr)


# =================== stage: gates (audit-tool self-checks) ===================
def stage_gates():
    rng = np.random.default_rng(23)
    res = {}
    nr, nz, h = 16, 32, 1.0
    wsc = 0.11
    # a structured random X
    M0 = rng.normal(size=(nr, nz, 4, 4))
    M0 = 0.5 * (M0 + np.swapaxes(M0, -1, -2))
    A1 = 0.3 * rng.normal(size=M0.shape); A1 = 0.5 * (A1 + np.swapaxes(A1, -1, -2))
    B1 = 0.3 * rng.normal(size=M0.shape); B1 = 0.5 * (B1 + np.swapaxes(B1, -1, -2))
    X = x_pack(M0, [A1], [B1])
    om = 0.73
    # AG1: my Shat == claimant Shat (same functional, independent code)
    s_mine = L.my_shat(X, om, h, wsc)
    s_theirs = claimant_shat(X, om, h, wsc)
    res["AG1_shat_rel"] = abs(s_mine - s_theirs) / (abs(s_theirs) + 1e-300)
    # AG2: claimant residual == FD of MY OWN Shat (random directions)
    Rd, dSdw = residual(X, om, h, wsc)
    eps, worst = 1e-6, 0.0
    for blk in ("M0", "A", "B"):
        arr = X[blk] if blk == "M0" else X[blk][0]
        D = rng.normal(size=arr.shape); D = 0.5 * (D + np.swapaxes(D, -1, -2))
        arr += eps * D
        Sp = L.my_shat(X, om, h, wsc)
        arr -= 2 * eps * D
        Sm = L.my_shat(X, om, h, wsc)
        arr += eps * D
        num = (Sp - Sm) / (2 * eps)
        an = float(np.sum((Rd[blk] if blk == "M0" else Rd[blk][0]) * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-300))
    res["AG2_residual_vs_myFD"] = worst
    # AG3: EXACT omega-quadraticity of Shat and of the residual
    s0 = L.my_shat(X, 0.0, h, wsc)
    s1 = L.my_shat(X, 1.0, h, wsc)
    s2 = L.my_shat(X, 2.0, h, wsc)
    res["AG3_shat_quad_rel"] = abs(s2 - (4 * s1 - 3 * s0)) / (abs(s2) + 1e-300)
    R0, _ = residual(X, 0.0, h, wsc)
    R1, _ = residual(X, 1.0, h, wsc)
    R2, _ = residual(X, 2.0, h, wsc)
    free, _ = L.free_mask(nr, nz, M0.shape)
    v0, v1, v2 = (L.rd_flat(R, free) for R in (R0, R1, R2))
    res["AG3_residual_quad_rel"] = float(
        np.linalg.norm(v2 - (4 * v1 - 3 * v0)) / (np.linalg.norm(v2) + 1e-300))
    # AG4: dv4d_dm == FD of my own v4 (the static-residual ingredient)
    Mc = M0[: nr - 1, 1:-1]
    D = rng.normal(size=Mc.shape); D = 0.5 * (D + np.swapaxes(D, -1, -2))
    g_an = float(np.sum(dv4d_dm(Mc, wsc) * D))
    vp = float(np.sum(L.v4(Mc + eps * D, wsc)))
    vm = float(np.sum(L.v4(Mc - eps * D, wsc)))
    res["AG4_dv4d_vs_myFD"] = abs((vp - vm) / (2 * eps) - g_an) / (abs(g_an) + 1e-300)
    # AG5: plain == eta conjugation for the (2,3) rotation (T4)
    from scipy.linalg import expm
    W = np.zeros((4, 4)); W[2, 3], W[3, 2] = -1.0, 1.0
    th = 0.83
    Lam = expm(L.ETA4 @ W * th)
    Lp = np.eye(4)
    Lp[2, 2], Lp[2, 3], Lp[3, 2], Lp[3, 3] = (np.cos(th), -np.sin(th),
                                              np.sin(th), np.cos(th))
    res["AG5_eta_vs_plain_rot_lam"] = float(np.max(np.abs(Lam - Lp)))
    Minv = np.linalg.inv(Lam)
    act_eta = np.einsum("ba,bc,cd->ad", Minv, M0[3, 3], Minv)   # Lam^-T M Lam^-1
    act_pl = Lp @ M0[3, 3] @ Lp.T
    # Lam^-1 = rotation by -th; Lam^-T M Lam^-1 with L(-th) = L(th)^T action:
    res["AG5_eta_vs_plain_rot_action"] = float(
        np.max(np.abs(np.einsum("ba,bc,cd->ad",
                                np.linalg.inv(Lp), M0[3, 3],
                                np.linalg.inv(Lp)) - act_eta)))
    for k, v in res.items():
        print(f"[gate] {k} = {v:.3e}")
    OUT["gates"] = res


# =================== stage: histories arithmetic (T5, C1) ===================
def stage_histories():
    res = {}
    oms, fns = {}, {}
    for name, jf in HIST.items():
        d = json.load(open(os.path.join(DATA, jf)))
        h = d["hist"]
        om = [r["omega"] for r in h]
        fn = [r["F_norm"] for r in h]
        fr = [r["F_rel"] for r in h]
        oms[name], fns[name] = om, fn
        # omega oscillation + drift over the last iterations
        tail = om[-6:] if len(om) >= 6 else om
        drift = (tail[-1] - tail[0]) / (len(tail) - 1)
        osc = float(np.std(np.diff(om))) if len(om) > 2 else 0.0
        # |F| decay rate at stop (per-iteration relative slope, last 3)
        slope = (fn[-1] / fn[-3]) ** 0.5 - 1.0 if len(fn) >= 3 else None
        res[name] = {
            "iters": len(h), "F0": fn[0] / fr[0], "F_end": fn[-1],
            "F_rel_end": fr[-1], "omega_end": om[-1],
            "omega_tail_drift_per_iter": drift,
            "omega_step_osc_std": osc,
            "F_slope_per_iter_at_stop": slope,
            "lsmr_istop7_every_iter": all(r["lsmr_stop"] == 7 for r in h),
            "converged_flag_1e-5": fr[-1] < 1e-5,
        }
        print(f"[hist {name}] F_rel_end={fr[-1]:.2e} om_end={om[-1]:.4f} "
              f"drift/iter={drift:+.5f} osc={osc:.4f} slope={slope:+.4f}")
    # Richardson consistency (h ~ 1/nr; object scales with nr)
    o32, o48, o64 = oms["n32"][-1], oms["n48"][-1], oms["n64"][-1]
    h2 = {n: (1.0 / n) ** 2 for n in (32, 48, 64)}
    ratio_obs = (o48 - o32) / (o64 - o48)
    ratio_h2 = (h2[32] - h2[48]) / (h2[48] - h2[64])
    rich_3248 = o48 + (o48 - o32) / ((48 / 32) ** 2 - 1.0)
    rich_4864 = o64 + (o64 - o48) / ((64 / 48) ** 2 - 1.0)
    res["richardson"] = {
        "omega_seq": [o32, o48, o64],
        "diff_ratio_observed": ratio_obs, "diff_ratio_h2_predicted": ratio_h2,
        "h2_inconsistency_factor": ratio_obs / ratio_h2,
        "richardson_from_32_48": rich_3248,
        "richardson_from_48_64": rich_4864,
        "extrapolation_spread": abs(rich_3248 - rich_4864),
        "within_run_drift_n64_total": oms["n64"][-1] - oms["n64"][0],
        "grid_diff_48_64": o64 - o48,
    }
    r = res["richardson"]
    print(f"[richardson] obs diff ratio {r['diff_ratio_observed']:.1f} vs h2 "
          f"{r['diff_ratio_h2_predicted']:.2f} (off x{r['h2_inconsistency_factor']:.1f}); "
          f"extrap 32/48={rich_3248:.4f} vs 48/64={rich_4864:.4f}")
    OUT["histories"] = res


# =================== per-state deep audit ===================
def omega_ls(X, h, wsc, free):
    R0, _ = residual(X, 0.0, h, wsc)
    R1, _ = residual(X, 1.0, h, wsc)
    v0 = L.rd_flat(R0, free)
    v1 = L.rd_flat(R1, free)
    vt = v1 - v0
    dot = float(np.dot(v0, vt))
    nt2 = float(np.dot(vt, vt))
    w2 = -dot / nt2
    return (float(np.sqrt(w2)) if w2 > 0 else None), R0, R1, v0, vt, dot, nt2


def stage_states():
    h = 1.0
    for name in ("n32", "n48", "n64"):
        t0 = time.time()
        X, om_saved, nr, nz, wsc = r_of_state(name)
        rc = rc_of(nr)
        free, pin = L.free_mask(nr, nz, X["M0"].shape)
        regs = L.region_masks(nr, nz, rc, h)
        res = {"omega_saved": om_saved, "wscale": wsc, "rc": rc}

        # --- residual recompute at saved omega + omega_ls closed form ---
        wstar, R0, R1, v0, vt, dot, nt2 = omega_ls(X, h, wsc, free)
        v_saved = v0 + om_saved ** 2 * vt
        Fn = float(np.linalg.norm(v_saved))
        nfree_cells = int(np.sum(~pin))
        res["Rfree_at_saved_omega"] = Fn
        res["rms_per_free_cell"] = Fn / np.sqrt(nfree_cells)
        res["omega_ls_closed_form"] = wstar
        res["omega_ls_minus_saved"] = (wstar - om_saved) if wstar else None
        n_at_star = np.sqrt(max(float(np.dot(v0, v0)) - dot ** 2 / nt2, 0.0))
        res["R_at_omega_star"] = n_at_star
        res["R_at_omega0"] = float(np.linalg.norm(v0))
        res["omega_selection_depth"] = 1.0 - n_at_star ** 2 / float(np.dot(v0, v0))
        # region-restricted omega_ls
        dmap = L.rd_dotmap(R0, {"M0": R1["M0"] - R0["M0"],
                                "A": [R1["A"][0] - R0["A"][0]],
                                "B": [R1["B"][0] - R0["B"][0]]}, free)
        Rt = {"M0": R1["M0"] - R0["M0"], "A": [R1["A"][0] - R0["A"][0]],
              "B": [R1["B"][0] - R0["B"][0]]}
        tmap2 = L.rd_cellmap(Rt, free)
        reg_om = {}
        for rn, rm in regs.items():
            dsum = float(np.sum(dmap[rm]))
            tsum = float(np.sum(tmap2[rm]))
            w2r = -dsum / tsum if tsum > 0 else np.nan
            reg_om[rn] = {"omega_ls": float(np.sqrt(w2r)) if w2r > 0 else None,
                          "share_of_Rt2": tsum / nt2,
                          "share_of_cross": dsum / dot if dot != 0 else None}
        res["omega_ls_by_region"] = reg_om
        # residual-at-saved-omega region shares
        Rsaved = {"M0": R0["M0"] + om_saved ** 2 * Rt["M0"],
                  "A": [R0["A"][0] + om_saved ** 2 * Rt["A"][0]],
                  "B": [R0["B"][0] + om_saved ** 2 * Rt["B"][0]]}
        rmap = L.rd_cellmap(Rsaved, free)
        res["R2_share_by_region"] = {rn: float(np.sum(rmap[rm]) / np.sum(rmap))
                                     for rn, rm in regs.items()}

        # --- Shat structure: S0, Q2, c_omega (free-period condition) ---
        S0, Q2, Q2mix = L.my_s0_q2(X, h, wsc)
        Sh = S0 - om_saved ** 2 * Q2
        c_om = (S0 + om_saved ** 2 * Q2) / (-om_saved)
        res.update({"S0": S0, "Q2": Q2, "Q2_mixing_part": Q2mix,
                    "Shat": Sh, "H_from_quad": S0 + om_saved ** 2 * Q2,
                    "c_omega_free_period": c_om,
                    "c_omega_over_Shat": c_om / Sh if Sh else None,
                    "free_period_root_exists_Q2sign": bool(Q2 < 0)})
        # q2/amplitude/timeterm region shares (included-cell maps x weights)
        w = L.cellw(nr, nz, h)
        s0m, q2m, q2mixm = L.s0_q2_maps(X, h, wsc)
        rin = L.grid_r(nr, nz, h)[: nr - 1, 1:-1]
        regin = {"core_r<2rc": rin < 2 * rc,
                 "halo_2-6rc": (rin >= 2 * rc) & (rin < 6 * rc),
                 "far_r>6rc": rin >= 6 * rc}
        res["Q2_share_by_region"] = {rn: float(np.sum((q2m * w)[rm]) / Q2)
                                     for rn, rm in regin.items()}
        res["S0_share_by_region"] = {rn: float(np.sum((s0m * w)[rm]) / S0)
                                     for rn, rm in regin.items()}
        ampm = np.sum(X["A"][0] ** 2 + X["B"][0] ** 2, axis=(-2, -1))
        wfull = np.zeros((nr, nz)); wfull[: nr - 1, 1:-1] = w
        amp_w = ampm * wfull
        res["amp2_weighted_share_by_region"] = {
            rn: float(np.sum(amp_w[rm]) / np.sum(amp_w))
            for rn, rm in regs.items()}
        res["A1_max_on_pinned_boundary"] = float(
            max(np.max(np.abs(X["A"][0][pin])), np.max(np.abs(X["B"][0][pin]))))
        res["A1_max_overall"] = float(
            max(np.max(np.abs(X["A"][0])), np.max(np.abs(X["B"][0]))))

        # --- H drift (my own) + isoenergy of samples ---
        Hs = L.my_H_samples(X, om_saved, h, wsc, ns=12)
        res["H_drift_rel"] = float((Hs.max() - Hs.min()) / (abs(Hs.mean()) + 1e-300))
        res["H_mean"] = float(Hs.mean())
        Es = L.my_spatialV_samples(X, h, wsc, ns=12)
        res["sampleE_spatialV_min_max_mean"] = [float(Es.min()), float(Es.max()),
                                                float(Es.mean())]
        res["sampleE_variation_rel"] = float((Es.max() - Es.min())
                                             / (abs(Es.mean()) + 1e-300))

        # --- rigidity (own recompute, ns dependence) + rotor identities ---
        for ns in (12, 36):
            Ms, _ = L.sample_X(X, ns)
            Mbars = []
            for jj, Mt in enumerate(Ms):
                th = -2.0 * np.pi * jj / ns
                Lp = np.eye(4)
                Lp[2, 2], Lp[2, 3] = np.cos(th), -np.sin(th)
                Lp[3, 2], Lp[3, 3] = np.sin(th), np.cos(th)
                Mbars.append(np.einsum("ab,...bc,dc->...ad", Lp, Mt, Lp))
            Mbar = sum(Mbars) / ns
            rig = max(float(np.max(np.abs(Mb - Mbar))) for Mb in Mbars)
            res[f"rigidity_ns{ns}"] = rig
        swing = max(float(np.max(np.abs(X["A"][0]))),
                    float(np.max(np.abs(X["B"][0]))))
        res["rigidity_rel_to_swing"] = res["rigidity_ns12"] / swing
        W23 = L.gen_w(2, 3)
        t_m0 = L.comm_plain_gen(W23, X["M0"])
        res["rotor_id_WM0_rel"] = float(np.linalg.norm(t_m0[free])
                                        / (np.linalg.norm(X["M0"][free]) + 1e-300))
        tB = L.comm_plain_gen(W23, X["A"][0])
        tA = L.comm_plain_gen(W23, X["B"][0])
        res["rotor_id_B1_eq_WA1_rel"] = float(
            np.linalg.norm((X["B"][0] - tB)[free]) / (np.linalg.norm(X["B"][0][free]) + 1e-300))
        res["rotor_id_A1_eq_minusWB1_rel"] = float(
            np.linalg.norm((X["A"][0] + tA)[free]) / (np.linalg.norm(X["A"][0][free]) + 1e-300))
        # best single-generator symmetry-orbit fit A1 ~ [W, M0]_eta (T3)
        pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        cols = []
        for (i, j) in pairs:
            Wij = L.gen_w(i, j)
            cols.append(L.comm_eta_gen(Wij, X["M0"])[free])
        Amat = np.stack(cols, axis=1)
        bvec = X["A"][0][free]
        coef, res_ls, _, _ = np.linalg.lstsq(Amat, bvec, rcond=None)
        fitres = float(np.linalg.norm(Amat @ coef - bvec)
                       / (np.linalg.norm(bvec) + 1e-300))
        res["orbit_fit_A1_rel_residual"] = fitres
        res["orbit_fit_coeffs"] = {f"W{i}{j}": float(c)
                                   for (i, j), c in zip(pairs, coef)}

        # --- co-rotating-mean static residual + distribution vs plateau ---
        Ms, _ = L.sample_X(X, 12)
        Mbars = []
        for jj, Mt in enumerate(Ms):
            th = -2.0 * np.pi * jj / 12
            Lp = np.eye(4)
            Lp[2, 2], Lp[2, 3] = np.cos(th), -np.sin(th)
            Lp[3, 2], Lp[3, 3] = np.sin(th), np.cos(th)
            Mbars.append(np.einsum("ab,...bc,dc->...ad", Lp, Mt, Lp))
        Mbar = sum(Mbars) / 12
        G = energy_gradient_np(Mbar, 0.0, 0.0, 0.0, 1.0, h, 0.0)
        w4 = w[..., None, None]
        G[: nr - 1, 1:-1] += dv4d_dm(Mbar[: nr - 1, 1:-1], wsc) * w4
        gmap = np.sum(np.where(free, G, 0.0) ** 2, axis=(-2, -1))
        res["staticR_of_corot_mean"] = float(np.sqrt(np.sum(gmap)))
        res["staticR_share_by_region"] = {
            rn: float(np.sum(gmap[rm]) / np.sum(gmap)) for rn, rm in regs.items()}
        num = float(np.sum(np.sqrt(gmap) * np.sqrt(rmap)))
        res["staticR_vs_plateau_cell_cosine"] = num / (
            float(np.sqrt(np.sum(gmap) * np.sum(rmap))) + 1e-300)
        res["E_static_corot_mean"] = float(np.sum(
            (curvature_density_np(Mbar, h, 1.0)
             + v4d_density(Mbar[..., :, :], wsc)) * w))

        # --- gauge check: R12 conj == symmetry, R23 conj != symmetry ---
        if name == "n32":
            gd = {}
            for pl, tag in (((1, 2), "R12"), ((2, 3), "R23")):
                i, j = pl
                th = 0.9
                Lp = np.eye(4)
                Lp[i, i], Lp[i, j] = np.cos(th), -np.sin(th)
                Lp[j, i], Lp[j, j] = np.sin(th), np.cos(th)
                Mrot = np.einsum("ab,...bc,dc->...ad", Lp, X["M0"], Lp)
                E0 = float(np.sum((curvature_density_np(X["M0"], h, 1.0)
                                   + v4d_density(X["M0"], wsc)) * w))
                E1 = float(np.sum((curvature_density_np(Mrot, h, 1.0)
                                   + v4d_density(Mrot, wsc)) * w))
                gd[tag] = {"E0": E0, "E_rot": E1,
                           "rel_change": (E1 - E0) / (abs(E0) + 1e-300)}
            res["gauge_check_static_energy"] = gd

            # --- g = 1 repose (Shat-level; residual stack is g=8-bound) ---
            X1 = {"M0": X["M0"].copy(), "A": [X["A"][0].copy()],
                  "B": [X["B"][0].copy()]}
            for arr in [X1["M0"], X1["A"][0], X1["B"][0]]:
                arr[..., 0, 0] = arr[..., 0, 0] / 8.0
                arr[..., 0, 1:4] = arr[..., 0, 1:4] / np.sqrt(8.0)
                arr[..., 1:4, 0] = arr[..., 1:4, 0] / np.sqrt(8.0)
            S0g, Q2g, Q2mixg = L.my_s0_q2(X1, h, wsc, g=1.0)
            res["g1_repose"] = {
                "S0": S0g, "Q2": Q2g, "Q2_mixing_part": Q2mixg,
                "c_omega_at_saved": (S0g + om_saved ** 2 * Q2g) / (-om_saved),
                "free_period_root_exists_Q2sign": bool(Q2g < 0),
                "note": "m00 -> m00/8, mixing/sqrt(8); Shat-level only"}

            # --- amplitude tracking of omega_ls (T2) ---
            lam_scan = {}
            for lam in (0.7, 1.3):
                Xl = {"M0": X["M0"].copy(),
                      "A": [lam * X["A"][0]], "B": [lam * X["B"][0]]}
                wl, *_ = omega_ls(Xl, h, wsc, free)
                lam_scan[f"lam_{lam}"] = wl
            lam_scan["lam_1.0"] = wstar
            res["omega_ls_vs_amplitude"] = lam_scan

        OUT.setdefault("states", {})[name] = res
        print(f"[state {name}] |R|={Fn:.1f} rms/cell={res['rms_per_free_cell']:.2f} "
              f"om_ls={wstar} depth={res['omega_selection_depth']:.3f} "
              f"S0={S0:.1f} Q2={Q2:.1f} c_om={c_om:.1f} Hdrift={res['H_drift_rel']:.2f} "
              f"rig={res['rigidity_ns12']:.3f} ({time.time()-t0:.0f}s)")


# =================== stage: seeds + vacuum rotor (T1, T2) ===================
def stage_seeds():
    h = 1.0
    res = {}
    nr, nz = 32, 64
    wsc = wsc_of(nr)
    free, pin = L.free_mask(nr, nz, (nr, nz, 4, 4))
    # fresh rotor seeds: omega_ls BEFORE any Newton, b0 dependence
    for b0 in (0.4, 1.6, 2.4):
        X0, _ = rotor_seed(nr, nz, h, b0, 8.0 * nr / 96, rc_of(nr), 0.64,
                           Nt=1, plane=(2, 3))
        wstar, *_ = omega_ls(X0, h, wsc, free)
        res[f"seed_b0_{b0}_omega_ls"] = wstar
        print(f"[seed b0={b0}] omega_ls at RAW SEED = {wstar}")
    # rc dependence at b0 = 0.4 (the actual n32 run's b0)
    for rcs in (rc_of(nr) * 0.75, rc_of(nr) * 1.5):
        X0, _ = rotor_seed(nr, nz, h, 0.4, 8.0 * nr / 96, rcs, 0.64,
                           Nt=1, plane=(2, 3))
        wstar, *_ = omega_ls(X0, h, wsc, free)
        res[f"seed_rc_{rcs:.2f}_omega_ls"] = wstar
        print(f"[seed rc={rcs:.2f}] omega_ls at RAW SEED = {wstar}")
    # pure-vacuum rotor (NO defect): the background kill shot
    for nrv in (32, 48):
        nzv = 2 * nrv
        wsv = wsc_of(nrv)
        Mv = np.zeros((nrv, nzv, 4, 4))
        Mv[..., 3, 3] = 1.0
        Mv[..., 0, 0] = -8.0
        Xv = L.rotor_project(Mv, plane=(2, 3), Nt=1)
        fv, _ = L.free_mask(nrv, nzv, Mv.shape)
        wstar, *_ = omega_ls(Xv, h, wsv, fv)
        res[f"vacuum_rotor_n{nrv}_omega_ls"] = wstar
        # its S0/Q2 structure
        S0v, Q2v, _ = L.my_s0_q2(Xv, h, wsv)
        res[f"vacuum_rotor_n{nrv}_S0_Q2"] = [S0v, Q2v]
        print(f"[vacuum rotor n{nrv}] omega_ls = {wstar} S0={S0v:.1f} Q2={Q2v:.1f}")
    OUT["seeds"] = res


# =================== stage: state injection across grids (C3, C1) ==========
def stage_inject():
    from scipy.ndimage import zoom as ndzoom
    h = 1.0
    res = {}
    X64, om64, nr64, nz64, _ = r_of_state("n64")
    for name in ("n32", "n48"):
        nr = STATES[name][1]
        nz = 2 * nr
        wsc = wsc_of(nr)
        fac = (nr / nr64, nz / nz64, 1, 1)

        def z(a, order):
            return ndzoom(a, fac, order=order)

        row = {}
        for order in (1, 3):
            Xi = {"M0": z(X64["M0"], order), "A": [z(X64["A"][0], order)],
                  "B": [z(X64["B"][0], order)]}
            free, _ = L.free_mask(nr, nz, Xi["M0"].shape)
            R0, _ = residual(Xi, 0.0, h, wsc)
            R1, _ = residual(Xi, om64, h, wsc)
            # R(om64) directly: R0 + om^2 (R1 - R0)/1 with R1 at om64:
            v = L.rd_flat(R1, free)
            row[f"Rfree_injected_order{order}"] = float(np.linalg.norm(v))
        # warm-start forensics: n32 state -> n48, |R| at its omega
        res[name] = row
        print(f"[inject -> {name}] {row}")
    X32, om32, _, _, _ = r_of_state("n32")
    fac = (48 / 32, 96 / 64, 1, 1)
    from scipy.ndimage import zoom as ndz
    Xi = {"M0": ndz(X32["M0"], fac, order=1), "A": [ndz(X32["A"][0], fac, order=1)],
          "B": [ndz(X32["B"][0], fac, order=1)]}
    free, _ = L.free_mask(48, 96, Xi["M0"].shape)
    Ri, _ = residual(Xi, om32, h, wsc_of(48))
    res["n32_state_zoomed_to_n48_Rfree"] = float(np.linalg.norm(L.rd_flat(Ri, free)))
    print(f"[forensic] n32 state zoomed to n48: |R| = {res['n32_state_zoomed_to_n48_Rfree']:.1f}"
          f" (n48 run's logged |F|0 = 102160)")
    OUT["inject"] = res


# =================== stage: breather (C4, T6) ===================
def stage_breather():
    h = 1.0
    path = os.path.join(DATA, "m5_12_d3b_breather_n32_state.npz")
    X, om = L.load_state(path)
    nr, nz = 32, 64
    wsc = wsc_of(nr)
    res = {"omega_saved": om}
    S0, Q2, Q2mix = L.my_s0_q2(X, h, wsc)
    Sh = S0 - om ** 2 * Q2
    dSdw = -2.0 * om * Q2
    c_om = dSdw - Sh / om
    res.update({
        "S0": S0, "Q2": Q2, "Q2_mixing_part": Q2mix, "Shat": Sh,
        "dShat_domega": dSdw, "minus_Shat_over_omega": -Sh / om,
        "c_omega": c_om,
        "c_omega_over_minusShat_over_omega": c_om / (-Sh / om),
        "identity_gap_2w2Q2_over_Shat": 2 * om ** 2 * Q2 / abs(Sh),
        "free_period_root_needs": "omega^2 Q2 = -S0",
        "root_impossible_perturbative": bool(Q2 > 0 and S0 > 0),
    })
    # amplitude^2 scaling of dShat/domega: Q2(lam)/lam^2
    scal = {}
    for lam in (0.5, 2.0):
        Xl = {"M0": X["M0"].copy(), "A": [lam * X["A"][0]],
              "B": [lam * X["B"][0]]}
        _, Q2l, _ = L.my_s0_q2(Xl, h, wsc)
        scal[f"lam_{lam}"] = Q2l / (lam ** 2 * Q2)
    res["Q2_lam_over_lam2Q2"] = scal
    # FD cross-check of dShat/domega with my own Shat
    eps = 1e-4
    num = (L.my_shat(X, om + eps, h, wsc) - L.my_shat(X, om - eps, h, wsc)) / (2 * eps)
    res["dShat_domega_FD_check_rel"] = abs(num - dSdw) / (abs(dSdw) + 1e-300)
    OUT["breather"] = res
    print(f"[breather] S0={S0:.3f} Q2={Q2:+.4f} Shat={Sh:.3f} dS/dw={dSdw:+.4f} "
          f"c_om={c_om:.3f} vs -S/w={-Sh/om:.3f} gap={res['identity_gap_2w2Q2_over_Shat']:.4f}")


def main():
    mode = ARGV[0] if ARGV else "all"
    t0 = time.time()
    stages = {"gates": stage_gates, "hist": stage_histories,
              "states": stage_states, "seeds": stage_seeds,
              "inject": stage_inject, "breather": stage_breather}
    todo = list(stages) if mode == "all" else [mode]
    for s in todo:
        print(f"===== stage {s} =====")
        try:
            stages[s]()
        except Exception as e:
            import traceback
            traceback.print_exc()
            OUT[s + "_ERROR"] = str(e)
    out_path = os.path.join(DATA, "m5_12_audit_b11_numbers.json")
    existing = {}
    if os.path.exists(out_path) and mode != "all":
        existing = json.load(open(out_path))
    existing.update(OUT)
    with open(out_path, "w") as f:
        json.dump(existing, f, indent=1)
    print(f"[audit] wall {time.time()-t0:.0f}s -> {out_path}")


if __name__ == "__main__":
    main()
