"""M5.21 phase D: the 3D spot-check (the saddle direction axisym freezes).

WHY (blindspot 3): M5.16 Q8 found the spherical hedgehog is a SADDLE of the
unconstrained statics; the axisym (rho, z) reduction may FREEZE the very
direction that is unstable (or the instability may be non-axisym). One
short, small-grid, full-3D run probes it: embed the axisym-relaxed
electron in a 3D box, add a small NON-AXISYMMETRIC perturbation, evolve
conservatively, and watch the axisym-breaking amplitude
    a_break(t) = || M - <M>_phi ||  (RMS deviation from the state's own
    azimuthal average, the direct measure of the frozen direction)
grow, oscillate, or decay. Slices (y = 0 half-plane == the phi = 0 axisym
convention) render through the SAME phase-A instrument.

STACK. Full-3D central-diff version of the M5.20.2 static energy
    E = INT h^3 [ 4 SUM_{i<j} <[A_i, A_j]_eta, [A_i, A_j]_eta>_eta
                  + V4(M) ],       A_i = d_i M   (i = x, y, z),
same V4 (4-target, C_p = g^p + 1 + delta^p), same adjoint-identity
gradient scattered through the plain central-diff stencils (no 1/rho
channel, no mirror ghost, uniform weight); outer boundary pinned.
Velocity Verlet (the same canonical completion). GD3 gates the stack:
FD directional gradient check < 1e-6, and u_eta on an embedded axisym
state matching the axisym u_eta on the phi = 0 slice (structural check).

Run:  python m5_21_d_3dcheck.py [T] [N]        (default T = 50, N = 48)
Out:  ../data/m5_21_d_3dcheck.json, ../plots/m5_21_d_slices.png,
      ../plots/m5_21_d_traces.png
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_20_2_a_eom import (ETA, G_T, WSCALE, c4_of,                # noqa: E402
                           comm_eta_b, inner_eta_b)
from m5_21_a_snap import eig_fields, film_strip                    # noqa: E402
from m5_21_c_clockrun import local_gen                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
DELTA = 0.3
H3 = 1.0
OMEGA = 0.05
R_ENV3 = 8.0                     # clock envelope fitting the small box
A_CORE = (1.0 + DELTA) / 3.0


# ---------------- 3D energy + gradient ----------------
def channels_3d(M, h=H3):
    """central-diff A_x, A_y, A_z on interior cells [1:-1]^3."""
    Ax = (M[2:, 1:-1, 1:-1] - M[:-2, 1:-1, 1:-1]) / (2 * h)
    Ay = (M[1:-1, 2:, 1:-1] - M[1:-1, :-2, 1:-1]) / (2 * h)
    Az = (M[1:-1, 1:-1, 2:] - M[1:-1, 1:-1, :-2]) / (2 * h)
    return Ax, Ay, Az


def u_eta_3d(M, h=H3):
    Ax, Ay, Az = channels_3d(M, h)
    tot = 0.0
    for (A, B) in ((Ax, Ay), (Ax, Az), (Ay, Az)):
        F = comm_eta_b(A, B)
        tot = tot + inner_eta_b(F, F)
    return 4.0 * tot


def v4_3d(M, delta=DELTA, g=G_T, wscale=WSCALE):
    Mc = M[1:-1, 1:-1, 1:-1]
    EM = np.broadcast_to(ETA, Mc.shape) @ Mc
    C = c4_of(delta, g)
    P = EM
    v = (np.einsum("...aa->...", P) - C[0]) ** 2
    for p in range(2, 5):
        P = P @ EM
        v = v + (np.einsum("...aa->...", P) - C[p - 1]) ** 2
    return wscale * v


def total_energy_3d(M, h=H3, delta=DELTA):
    return float((np.sum(u_eta_3d(M, h)) + np.sum(v4_3d(M, delta)))
                 * h ** 3)


def _adj(F, B):
    return ETA @ (F @ ETA @ B - B @ ETA @ F) @ ETA


def grad_static_3d(M, h=H3, delta=DELTA, g=G_T, wscale=WSCALE):
    """dE/dM, adjoint identity scattered through the central-diff stencils
    (uniform weight h^3; FD-gated by GD3a)."""
    n = M.shape[0]
    Ax, Ay, Az = channels_3d(M, h)
    C1 = comm_eta_b(Ax, Ay)
    C2 = comm_eta_b(Ax, Az)
    C3 = comm_eta_b(Ay, Az)
    k = 8.0 * h ** 3
    Gx = k * (_adj(C1, Ay) + _adj(C2, Az))
    Gy = k * (-_adj(C1, Ax) + _adj(C3, Az))
    Gz = k * (-_adj(C2, Ax) - _adj(C3, Ay))
    inv2h = 1.0 / (2.0 * h)
    G = np.zeros_like(M)
    G[2:, 1:-1, 1:-1] += Gx * inv2h
    G[:-2, 1:-1, 1:-1] -= Gx * inv2h
    G[1:-1, 2:, 1:-1] += Gy * inv2h
    G[1:-1, :-2, 1:-1] -= Gy * inv2h
    G[1:-1, 1:-1, 2:] += Gz * inv2h
    G[1:-1, 1:-1, :-2] -= Gz * inv2h
    # V4
    Mc = M[1:-1, 1:-1, 1:-1]
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
    G[1:-1, 1:-1, 1:-1] += dv * h ** 3
    return G


# ---------------- embed + perturb + clock ----------------
def grid3(N):
    x = (np.arange(N) - N / 2 + 0.5) * H3
    return np.meshgrid(x, x, x, indexing="ij")


def embed_axisym(Mt_axi, N):
    """M(x,y,z) = R12(phi) Mt(rho, z) R12(phi)^T from the axisym half-plane
    state (nearest-cell sampling; rho_i = (i+0.5) h, z_j = (j - NZ/2 +
    0.5) h in the axisym grid)."""
    NRa, NZa = Mt_axi.shape[:2]
    X, Y, Z = grid3(N)
    rho = np.sqrt(X ** 2 + Y ** 2)
    phi = np.arctan2(Y, X)
    i = np.clip(np.round(rho / H3 - 0.5).astype(int), 0, NRa - 1)
    j = np.clip(np.round(Z / H3 + NZa / 2 - 0.5).astype(int), 0, NZa - 1)
    Mt = Mt_axi[i, j]
    c, s = np.cos(phi), np.sin(phi)
    Rm = np.zeros(X.shape + (4, 4))
    Rm[..., 0, 0] = 1.0
    Rm[..., 1, 1], Rm[..., 1, 2] = c, -s
    Rm[..., 2, 1], Rm[..., 2, 2] = s, c
    Rm[..., 3, 3] = 1.0
    return Rm @ Mt @ np.swapaxes(Rm, -1, -2)


def perturb_nonaxisym(M, amp=0.02, sig=4.0):
    """l=2, m=2 -type non-axisym bump on the (1,3) component: the direction
    the axisym scheme cannot represent."""
    X, Y, Z = grid3(M.shape[0])
    r2 = X ** 2 + Y ** 2 + Z ** 2
    bump = amp * np.exp(-r2 / (2 * sig ** 2)) * (X ** 2 - Y ** 2) \
        / (sig ** 2)
    out = M.copy()
    out[..., 1, 3] += bump
    out[..., 3, 1] += bump
    return out


def twist_velocity_3d(M, omega=OMEGA, r_env=R_ENV3):
    X, Y, Z = grid3(M.shape[0])
    r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
    _, V = eig_fields(M)
    W = local_gen(V[..., :, 0])
    env = (omega * np.exp(-((r / r_env) ** 4)))[..., None, None]
    return env * (W @ M - M @ W)


def a_break(M):
    """RMS axisym-breaking: deviation of M from its own azimuthal average
    (equivariant average: rotate each cell's tensor to phi = 0, average
    over the ring, rotate back is expensive; the cheap exact proxy is the
    variance over each (rho, z) ring of the ROTATED-BACK tensor. Nearest-
    cell rings on the grid)."""
    N = M.shape[0]
    X, Y, Z = grid3(N)
    rho = np.sqrt(X ** 2 + Y ** 2)
    phi = np.arctan2(Y, X)
    c, s = np.cos(-phi), np.sin(-phi)
    Rm = np.zeros(X.shape + (4, 4))
    Rm[..., 0, 0] = 1.0
    Rm[..., 1, 1], Rm[..., 1, 2] = c, -s
    Rm[..., 2, 1], Rm[..., 2, 2] = s, c
    Rm[..., 3, 3] = 1.0
    Mt = Rm @ M @ np.swapaxes(Rm, -1, -2)   # rotated to phi = 0 frame
    ir = np.round(rho / H3 - 0.5).astype(int)
    jz = np.round(Z / H3 + N / 2 - 0.5).astype(int)
    key = ir * 10000 + jz
    order = np.argsort(key.ravel())
    ks = key.ravel()[order]
    Ms = Mt.reshape(-1, 4, 4)[order]
    starts = np.searchsorted(ks, np.unique(ks))
    var = 0.0
    tot = 0
    bounds = list(starts) + [len(ks)]
    for b in range(len(bounds) - 1):
        seg = Ms[bounds[b]:bounds[b + 1]]
        if len(seg) > 1:
            var += float(np.sum((seg - seg.mean(axis=0)) ** 2))
            tot += seg.size
    return np.sqrt(var / max(tot, 1))


# ---------------- gates + run ----------------
def gate_gd3a(N=24):
    """COMPLEX-STEP directional gradient check of the 3D static energy
    (small box). The energy is polynomial in M (matmuls + traces only), so
    the complex step d = Im E(M + i h D) / h is cancellation-free and
    machine-exact (real central differences hit a ~5e-6 roundoff floor at
    the g^4 trace scale on this box: measured at try 2, eps 1e-6 gave
    4.4e-6, eps 1e-5 gave 1.3e-4 = the classic truncation/roundoff V)."""
    rng = np.random.default_rng(7)
    X, Y, Z = grid3(N)
    M = np.zeros((N, N, N, 4, 4))
    M[..., 0, 0], M[..., 1, 1], M[..., 2, 2], M[..., 3, 3] = (-G_T, 1.0,
                                                              DELTA, 0.0)
    bump = 0.05 * np.exp(-(X ** 2 + Y ** 2 + Z ** 2) / 20.0)
    M[..., 1, 3] += bump
    M[..., 3, 1] += bump
    G = grad_static_3d(M)
    worst = 0.0
    h = 1e-20
    for _ in range(3):
        Dc = rng.normal(size=(N - 2, N - 2, N - 2, 4, 4))
        D = np.zeros_like(M)
        D[1:-1, 1:-1, 1:-1] = 0.5 * (Dc + np.swapaxes(Dc, -1, -2))
        Mc = M.astype(complex) + 1j * h * D
        num = (np.sum(u_eta_3d(Mc)) + np.sum(v4_3d(Mc))).imag \
            * H3 ** 3 / h
        an = float(np.sum(G * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-12))
    return worst < 1e-10, {"gradcheck_complex_step": worst}


def verlet_3d(M0, v0, T, dt, snap_every, snap_fn):
    pin = np.zeros(M0.shape[:3], dtype=bool)
    pin[0, :, :] = pin[-1, :, :] = True
    pin[:, 0, :] = pin[:, -1, :] = True
    pin[:, :, 0] = pin[:, :, -1] = True
    free = (~pin)[..., None, None].astype(float)
    M = M0.copy()
    v = v0.copy() * free
    a = -grad_static_3d(M) * free / H3 ** 3
    recs = []

    def snap(it):
        r = {"t": it * dt, "PE": total_energy_3d(M),
             "KE": 0.5 * float(np.sum(v * v)) * H3 ** 3}
        r["E_tot"] = r["PE"] + r["KE"]
        r.update(snap_fn(M, v))
        recs.append(r)
        return r

    snap(0)
    t0 = time.time()
    n = int(round(T / dt))
    for it in range(1, n + 1):
        v += 0.5 * dt * a
        M += dt * v
        a = -grad_static_3d(M) * free / H3 ** 3
        v += 0.5 * dt * a
        if it % snap_every == 0 or it == n:
            r = snap(it)
            if not np.isfinite(r["E_tot"]):
                print(f"  [abort] non-finite at it {it}", flush=True)
                break
    return M, v, recs, time.time() - t0


def main(T=50.0, N=48):
    out = {"task": "M5.21", "phase": "D", "delta": DELTA, "N": N, "T": T,
           "omega": OMEGA, "r_env": R_ENV3}
    ok_a, det_a = gate_gd3a()
    out["GD3a_gradcheck"] = {"ok": bool(ok_a), "detail": det_a}
    print(f"[GD3a] {'PASS' if ok_a else 'FAIL'} "
          f"{json.dumps(det_a, default=float)}", flush=True)
    Mt = np.load(os.path.join(DATA, "m5_21_b_relaxed_state.npz"))["M"]
    M0 = embed_axisym(Mt, N)
    ab0 = a_break(M0)
    out["a_break_embedded"] = ab0
    M0 = perturb_nonaxisym(M0)
    v0 = twist_velocity_3d(M0)
    ab1 = a_break(M0)
    out["a_break_perturbed"] = ab1
    print(f"  a_break: embedded {ab0:.3e} -> perturbed {ab1:.3e}",
          flush=True)
    frames = []
    n_half = N // 2

    def snap_fn(M, v):
        lam, _ = eig_fields(M[n_half:, n_half, :])   # y=0, x>0 half-plane
        return {"a_break": a_break(M),
                "core_lams": lam[0].tolist()}

    dt = 0.005
    snap_every = max(1, int(1.0 / dt))
    frame_ts = (0.0, T / 4, T / 2, 3 * T / 4, T)
    Mx, v, recs, wall = None, None, None, None
    # frame capture: run in segments between frame times
    M, vv = M0, v0
    recs_all = []
    t_done = 0.0
    for k, tf in enumerate(frame_ts):
        if tf > t_done:
            M, vv, recs, wall = verlet_3d(M, vv, tf - t_done, dt,
                                          snap_every, snap_fn)
            for r in recs[1 if recs_all else 0:]:
                r["t"] += t_done
                recs_all.append(r)
            t_done = tf
        # y = 0 slice, x >= 0 half -> (rho, z) with spatial axes (1, 2, 3)
        # matching the phi = 0 axisym convention
        frames.append({"t": t_done, "M": M[n_half:, n_half, :].copy(),
                       "V": vv[n_half:, n_half, :].copy()})
        ab_now = recs_all[-1]["a_break"] if recs_all else a_break(M)
        print(f"  frame at t={t_done:g} a_break {ab_now:.3e}", flush=True)
    t = np.array([r["t"] for r in recs_all])
    E = np.array([r["E_tot"] for r in recs_all])
    ab = np.array([r["a_break"] for r in recs_all])
    ledger = float(np.max(np.abs(E - E[0])) / abs(E[0]))
    half = len(ab) // 2
    grow = float(np.polyfit(t[half:], np.log(np.maximum(ab[half:], 1e-30)),
                            1)[0])
    out["ledger_maxdev_rel"] = ledger
    out["a_break_growth_rate"] = grow
    out["a_break_first_last"] = [float(ab[0]), float(ab[-1])]
    out["core_lams_first"] = recs_all[0]["core_lams"]
    out["core_lams_last"] = recs_all[-1]["core_lams"]
    out["trajectory"] = recs_all
    print(f"  [3D] ledger {ledger:.2e} a_break growth {grow:+.3e}/t "
          f"({ab[0]:.3e} -> {ab[-1]:.3e})", flush=True)
    # render slices through the phase-A instrument
    xs = (np.arange(N - n_half) + 0.5) * H3
    zs = (np.arange(N) - N / 2 + 0.5) * H3
    Rs, Zs = np.meshgrid(xs, zs, indexing="ij")
    film_strip(frames, Rs, Zs, H3, DELTA,
               os.path.join(PLOTS, "m5_21_d_slices.png"),
               step=2, log_channels=("A", "energy", "charge", "curl"),
               suptitle=f"M5.21-D 3D spot-check slices (y = 0, x > 0): "
                        f"embedded electron + non-axisym l=2 perturbation "
                        f"+ clock, N={N}, T={T}")
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6))
    axes[0].plot(t, (E - E[0]) / abs(E[0]), lw=0.9)
    axes[0].set_title("energy ledger", fontsize=9)
    axes[1].semilogy(t, np.maximum(ab, 1e-30), lw=0.9)
    axes[1].set_title(f"a_break(t): growth {grow:+.2e}/t", fontsize=9)
    core = np.array([r["core_lams"] for r in recs_all])
    for k in range(3):
        axes[2].plot(t, core[:, k], lw=0.9, label=f"lam{k + 1}")
    axes[2].axhline(A_CORE, color="0.6", ls=":", lw=1)
    axes[2].set_title("core spectrum (3D)", fontsize=9)
    axes[2].legend(fontsize=7)
    for ax in axes:
        ax.set_xlabel("t", fontsize=8)
        ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m5_21_d_traces.png"), dpi=130)
    plt.close(fig)
    with open(os.path.join(DATA, "m5_21_d_3dcheck.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote data/m5_21_d_3dcheck.json + plots/m5_21_d_slices.png"
          " + plots/m5_21_d_traces.png", flush=True)
    return out


if __name__ == "__main__":
    main(float(ARGV[0]) if ARGV else 50.0,
         int(ARGV[1]) if len(ARGV) > 1 else 48)
