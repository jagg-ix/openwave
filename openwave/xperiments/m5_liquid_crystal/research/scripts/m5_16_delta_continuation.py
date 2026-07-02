"""M5.16 P-G: the delta-continuation study (the M5.12 unlock probe).

CONVENTION (Duda index-0): M is 4x4, D = diag(g, 1, delta, 0), eta =
diag(-1, 1, 1, 1); spatial block = [1:4, 1:4].

THE HYPOTHESIS UNDER TEST (2026-07-02 roadmap review; m5_12_task_details.md
section "The standing hypothesis"): all five M5.11 P2 loop experiments ran at
the placeholder delta = 0.3, where the spatial tensor is STRONGLY BIAXIAL,
and run 3's obstruction was precisely biaxiality (the chiral term drives a
blue-phase melt texture, the Tai/Smalyukh thesis's flagged hard case, p.132).
Duda's 2026-07-01 sketch (m5_4f section 2) says the neutrino is a UNIAXIAL
nematic field, and at the physical delta ~ 1e-10 the substrate is
quasi-uniaxial, exactly where Smalyukh's chiral knots are known stable. If
the obstruction RELAXES as delta walks down, the M5.11 P2 negatives are
regime artifacts, not verdicts, and M5.12 phase A starts from the uniaxial
end with cause.

METHOD. Fork of the frozen m5_11_p2_heliknoton.py machinery (chiral Lifshitz
+ Frank partner + AD-FIRE, all validated there: AD == numpy 1e-14), with
delta promoted from a module constant to the SWEEP VARIABLE. Everything else
held at the M5.11 run-3/run-2 settings (N=32, pitch=24, K = L/2, same LdG
amplitude well b=0, vacuum Msp = delta I + (1-delta) nn, VAC_TR2 =
1 + 2 delta^2) so the delta trend is the ONLY change vs the frozen record.
NOTE the P2 sandbox potential (b = 0 amplitude well) is NOT the calibrated
M5.16 potential; P-G is a relative-trend probe, the calibrated re-run is
M5.12 phase A/B.

Per delta in {0.30, 0.20, 0.10, 0.05, 0.02}:
  a) HELIX BACKGROUND TEST (run-3 descendant): relax the bare pitch-24 helix
     under Frank + chiral at L in {1.7, 5.0}; measure the blue-phase
     indicator = melted-voxel fraction (Tr2 < 0.7 vac) + max amplitude
     deviation + energy runaway. Blue-phase melt networks = the obstruction.
  b) HELIKNOTON RETENTION TEST (run-2/sweep descendant): relax the seeded
     heliknoton at L = 1.7; measure excess-|Msp| retention over the bare
     helix + localization (peak/mean).
Readout: the trend of (a) and (b) vs delta. RELAXING obstruction + rising or
stable retention as delta -> 0 supports the unlock hypothesis; a flat or
worsening trend refutes it (and M5.12 phase A loses its cheap motivation).

Run:  python m5_16_delta_continuation.py [N] [iters]     (defaults 32, 1200)
Outputs: ../data/m5_16_delta_continuation.json, ../plots/m5_16_delta_continuation.png
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import taichi as ti

ti.init(arch=ti.cpu, default_fp=ti.f64, offline_cache=True, random_seed=0)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
os.makedirs(DATA, exist_ok=True)
os.makedirs(PLOTS, exist_ok=True)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 32
ITERS = int(sys.argv[2]) if len(sys.argv) > 2 else 1200

G_TIME = 8.0
PITCH = 24.0
Q0 = 2.0 * np.pi / PITCH
R0 = PITCH / 4.0
DX = 1.0
C2 = 1.0
LDG_C = 0.5
LDG_B = 0.0

DELTAS = [0.30, 0.20, 0.10, 0.05, 0.02]
L_HELIX = [1.7, 5.0]
L_KNOT = 1.7

PERMS = ((1, 2, 3, 1.0), (2, 3, 1, 1.0), (3, 1, 2, 1.0),
         (1, 3, 2, -1.0), (3, 2, 1, -1.0), (2, 1, 3, -1.0))

M = ti.Matrix.field(4, 4, ti.f64, shape=(N, N, N), needs_grad=True)
loss = ti.field(ti.f64, shape=(), needs_grad=True)
par = ti.field(ti.f64, shape=(8,))   # a b c c2 dx q0 Lc Kf


@ti.kernel
def compute_energy():
    # curvature (engine form), validated == P0 in m5_11_ad_energy.py
    for i, j, k in ti.ndrange((1, N - 1), (1, N - 1), (0, N)):
        c2 = par[3]
        dx = par[4]
        inv2dx = 1.0 / (2.0 * dx)
        dV = dx * dx * dx
        Mx = (M[i + 1, j, k] - M[i - 1, j, k]) * inv2dx
        My = (M[i, j + 1, k] - M[i, j - 1, k]) * inv2dx
        cxy = Mx @ My - My @ Mx
        loss[None] += c2 * 4.0 * cxy.norm_sqr() * dV
    for i, j, k in ti.ndrange((1, N - 1), (0, N), (1, N - 1)):
        c2 = par[3]
        dx = par[4]
        inv2dx = 1.0 / (2.0 * dx)
        dV = dx * dx * dx
        Mx = (M[i + 1, j, k] - M[i - 1, j, k]) * inv2dx
        Mz = (M[i, j, k + 1] - M[i, j, k - 1]) * inv2dx
        cxz = Mx @ Mz - Mz @ Mx
        loss[None] += c2 * 4.0 * cxz.norm_sqr() * dV
    for i, j, k in ti.ndrange((0, N), (1, N - 1), (1, N - 1)):
        c2 = par[3]
        dx = par[4]
        inv2dx = 1.0 / (2.0 * dx)
        dV = dx * dx * dx
        My = (M[i, j + 1, k] - M[i, j - 1, k]) * inv2dx
        Mz = (M[i, j, k + 1] - M[i, j, k - 1]) * inv2dx
        cyz = My @ Mz - Mz @ My
        loss[None] += c2 * 4.0 * cyz.norm_sqr() * dV
    # LdG amplitude well on the spatial block
    for i, j, k in M:
        a = par[0]
        b = par[1]
        c = par[2]
        dx = par[4]
        dV = dx * dx * dx
        m = M[i, j, k]
        tr2 = 0.0
        tr3 = 0.0
        for p in ti.static(range(1, 4)):
            for q in ti.static(range(1, 4)):
                tr2 += m[p, q] * m[q, p]
        for p in ti.static(range(1, 4)):
            for q in ti.static(range(1, 4)):
                for r in ti.static(range(1, 4)):
                    tr3 += m[p, q] * m[q, r] * m[r, p]
        loss[None] += (a * tr2 - b * tr3 + c * tr2 * tr2) * dV
    # Frank K |grad Msp|^2 + chiral Lifshitz 2 q0 L eps_ikl Msp_ij d_k Msp_lj
    for i, j, k in ti.ndrange((1, N - 1), (1, N - 1), (1, N - 1)):
        q0 = par[5]
        Lc = par[6]
        Kf = par[7]
        dx = par[4]
        inv2dx = 1.0 / (2.0 * dx)
        dV = dx * dx * dx
        gx = (M[i + 1, j, k] - M[i - 1, j, k]) * inv2dx
        gy = (M[i, j + 1, k] - M[i, j - 1, k]) * inv2dx
        gz = (M[i, j, k + 1] - M[i, j, k - 1]) * inv2dx
        loss[None] += Kf * (gx.norm_sqr() + gy.norm_sqr() + gz.norm_sqr()) * dV
        m = M[i, j, k]
        chi = 0.0
        for pi, pk, pl, s in ti.static(PERMS):
            gk = gx if pk == 1 else (gy if pk == 2 else gz)
            for jj in ti.static(range(1, 4)):
                chi += s * m[pi, jj] * gk[pl, jj]
        loss[None] += 2.0 * q0 * Lc * chi * dV


def energy_and_grad(M_np, a, b, c, c2, dx, q0, Lc, Kf):
    M.from_numpy(M_np)
    par.from_numpy(np.array([a, b, c, c2, dx, q0, Lc, Kf], dtype=np.float64))
    loss[None] = 0.0
    with ti.ad.Tape(loss=loss):
        compute_energy()
    return float(loss[None]), M.grad.to_numpy()


# ---------------- seeds + diagnostics (delta-parametrized P2 forms) ----------------
def grid():
    xs = (np.arange(N) - (N - 1) / 2.0) * DX
    return np.meshgrid(xs, xs, xs, indexing="ij")


def interior_mask():
    m = np.ones((N, N, N), dtype=bool)
    for ax in range(3):
        idx = [slice(None)] * 3
        idx[ax] = 0
        m[tuple(idx)] = False
        idx[ax] = -1
        m[tuple(idx)] = False
    return m


def helix_director(X, Y, Z, q0):
    c = np.cos(q0 * Z)
    s = np.sin(q0 * Z)
    nh = np.stack([c, s, 0.0 * Z], axis=-1)
    return nh / np.linalg.norm(nh, axis=-1, keepdims=True)


def hopf_director(X, Y, Z, R0v):
    r2 = X ** 2 + Y ** 2 + Z ** 2
    d = r2 + R0v ** 2
    X1 = 2 * R0v * X / d
    X2 = 2 * R0v * Y / d
    X3 = 2 * R0v * Z / d
    X4 = (r2 - R0v ** 2) / d
    n1 = 2 * (X1 * X3 + X2 * X4)
    n2 = 2 * (X2 * X3 - X1 * X4)
    n3 = X1 ** 2 + X2 ** 2 - X3 ** 2 - X4 ** 2
    nh = np.stack([n1, n2, n3], axis=-1)
    return nh / np.linalg.norm(nh, axis=-1, keepdims=True)


def heliknoton_director(X, Y, Z, R0v, q0):
    nH = hopf_director(X, Y, Z, R0v)
    a1 = nH[..., 2]
    a2 = nH[..., 1]
    a3 = -nH[..., 0]
    c = np.cos(q0 * Z)
    s = np.sin(q0 * Z)
    b1 = c * a1 - s * a2
    b2 = s * a1 + c * a2
    nh = np.stack([b1, b2, a3], axis=-1)
    return nh / np.linalg.norm(nh, axis=-1, keepdims=True)


def tensor_from_director(nhat, delta):
    nn = nhat[..., :, None] * nhat[..., None, :]
    Msp = delta * np.eye(3) + (1.0 - delta) * nn
    Mout = np.zeros(nhat.shape[:3] + (4, 4))
    Mout[..., 1:4, 1:4] = Msp
    Mout[..., 0, 0] = G_TIME
    return Mout


def vac_tr2(delta):
    return 1.0 + 2.0 * delta ** 2


def ldg_a(delta):
    return -2.0 * LDG_C * vac_tr2(delta)


def blue_phase_indicator(M_np, delta):
    """melted-voxel fraction (Tr2 < 0.7 vac) + max amplitude deviation."""
    Msp = M_np[..., 1:4, 1:4]
    tr2 = np.trace(Msp @ Msp, axis1=-2, axis2=-1)
    vt = vac_tr2(delta)
    melt_frac = float(np.mean(tr2[interior_mask()] < 0.7 * vt))
    ampdev = float(np.max(np.abs(tr2 - vt)))
    return melt_frac, ampdev


def excess(M_np, Mhelix):
    dM = M_np[..., 1:4, 1:4] - Mhelix[..., 1:4, 1:4]
    return np.sqrt(np.sum(dM ** 2, axis=(-2, -1)))


def fire_relax(M0, delta, Lc, Kf, iters, label=""):
    free = interior_mask()[..., None, None]
    M_np = M0.copy()
    v = np.zeros_like(M_np)
    dt, dt_max, alpha, n_pos = 0.02, 0.2, 0.1, 0
    a = ldg_a(delta)
    E = None
    for it in range(iters):
        E, g = energy_and_grad(M_np, a, LDG_B, LDG_C, C2, DX, Q0, Lc, Kf)
        g[..., 1:4, 1:4] = 0.5 * (g[..., 1:4, 1:4]
                                  + np.swapaxes(g[..., 1:4, 1:4], -1, -2))
        g = np.where(free, g, 0.0)
        F = -g
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
        M_np = M_np + dt * v
        M_np = np.where(free, M_np, M0)
        if not np.isfinite(E):
            break
    return M_np, float(E)


def main():
    t0 = time.time()
    X, Y, Z = grid()
    rows = []
    for delta in DELTAS:
        nh_helix = helix_director(X, Y, Z, Q0)
        Mhelix = tensor_from_director(nh_helix, delta)
        row = {"delta": delta, "vac_tr2": vac_tr2(delta), "helix": {}, "knot": {}}
        # a) helix background stability under Frank + chiral (run-3 descendant)
        for L in L_HELIX:
            Mh_r, Ef = fire_relax(Mhelix, delta, L, L / 2.0, 400,
                                  label=f"helix d{delta} L{L}")
            mf, ad = blue_phase_indicator(Mh_r, delta)
            dmax = float(np.max(np.abs(Mh_r[..., 1:4, 1:4]
                                       - Mhelix[..., 1:4, 1:4])))
            row["helix"][str(L)] = {"melt_frac": mf, "ampdev": ad,
                                    "dMsp_max": dmax, "E_final": Ef,
                                    "finite": bool(np.isfinite(Ef))}
            print(f"[helix] delta={delta:5.2f} L={L:4.1f} melt_frac={mf:.4f} "
                  f"ampdev={ad:.3f} dMsp={dmax:.3f} finite={np.isfinite(Ef)}")
        # b) heliknoton retention (run-2/sweep descendant) at L_KNOT
        nh_seed = heliknoton_director(X, Y, Z, R0, Q0)
        M_seed = tensor_from_director(nh_seed, delta)
        exc0 = float(np.sum(excess(M_seed, Mhelix)))
        Mk, Ek = fire_relax(M_seed, delta, L_KNOT, L_KNOT / 2.0, ITERS,
                            label=f"knot d{delta}")
        exc_f = excess(Mk, Mhelix)
        ret = float(np.sum(exc_f)) / max(exc0, 1e-12)
        nz = exc_f[interior_mask()]
        loc = float(np.max(nz) / (np.mean(nz) + 1e-12))
        mf_k, ad_k = blue_phase_indicator(Mk, delta)
        row["knot"] = {"retention": ret, "localization": loc,
                       "melt_frac": mf_k, "ampdev": ad_k, "E_final": Ek,
                       "seed_excess": exc0, "finite": bool(np.isfinite(Ek))}
        print(f"[knot ] delta={delta:5.2f} retention={ret:.2%} loc={loc:.1f} "
              f"melt_frac={mf_k:.4f} finite={np.isfinite(Ek)}")
        rows.append(row)
    # trend readout
    mf_trend = [r["helix"][str(L_HELIX[-1])]["melt_frac"] for r in rows]
    ret_trend = [r["knot"]["retention"] for r in rows]
    loc_trend = [r["knot"]["localization"] for r in rows]
    obstruction_relaxes = bool(mf_trend[-1] < 0.5 * mf_trend[0]) if mf_trend[0] > 0 else None
    retention_not_worse = bool(ret_trend[-1] >= 0.8 * ret_trend[0])
    out = {
        "task": "M5.16 P-G", "script": "m5_16_delta_continuation.py",
        "convention": "Duda index-0: D=diag(g,1,delta,0), eta=diag(-1,1,1,1)",
        "settings": {"N": N, "iters": ITERS, "pitch": PITCH, "q0": Q0,
                     "R0": R0, "L_helix": L_HELIX, "L_knot": L_KNOT,
                     "ldg": "P2 sandbox amplitude well (b=0), NOT the"
                            " calibrated M5.16 potential; relative trend only"},
        "deltas": DELTAS, "rows": rows,
        "trends": {"helix_melt_frac_at_Lmax": mf_trend,
                   "knot_retention": ret_trend,
                   "knot_localization": loc_trend,
                   "obstruction_relaxes_as_delta_drops": obstruction_relaxes,
                   "retention_not_worse_at_small_delta": retention_not_worse},
        "wall_s": round(time.time() - t0, 1),
    }
    path = os.path.join(DATA, "m5_16_delta_continuation.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\njson -> {path}  ({out['wall_s']}s)")
    # plot
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
    for L in L_HELIX:
        ax[0].semilogx(DELTAS, [r["helix"][str(L)]["melt_frac"] for r in rows],
                       "o-", label=f"L={L}")
    ax[0].set_xlabel("delta")
    ax[0].set_ylabel("melted-voxel fraction")
    ax[0].set_title("blue-phase obstruction vs delta (helix relax)")
    ax[0].legend()
    ax[0].invert_xaxis()
    ax[1].semilogx(DELTAS, ret_trend, "s-", color="#c0392b")
    ax[1].set_xlabel("delta")
    ax[1].set_ylabel("excess retention")
    ax[1].set_title(f"heliknoton retention vs delta (L={L_KNOT})")
    ax[1].invert_xaxis()
    ax[2].semilogx(DELTAS, loc_trend, "d-", color="#2980b9")
    ax[2].set_xlabel("delta")
    ax[2].set_ylabel("localization (peak/mean)")
    ax[2].set_title("excess localization vs delta")
    ax[2].invert_xaxis()
    fig.suptitle("M5.16 P-G: delta-continuation toward the quasi-uniaxial regime"
                 " (delta drops left to right)", fontweight="bold")
    fig.tight_layout()
    ppath = os.path.join(PLOTS, "m5_16_delta_continuation.png")
    fig.savefig(ppath, dpi=110)
    print(f"plot -> {ppath}")
    return out


if __name__ == "__main__":
    main()
