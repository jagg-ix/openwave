"""M5.21 phase C: the electron rotation-clock production runs + film-strips.

THE RUN. The FIRE-relaxed biaxial hedgehog (phase B) with a ROTATION-sector
clock seeded as an initial VELOCITY: the local ZBW twist about the
director,
    Mdot(x, 0) = omega env(r) [W(nhat(x)), M(x)],
    W(n) = the antisymmetric generator of rotations about the LOCAL
    director (so the (delta, 0) eigenframe sweeps around the axle: the
    m5_4b 4.1.1 clock), env = exp(-(r / r_env)^4) a plateau envelope
    localizing the clock to the particle.
Evolved under the M5.20.2 canonical completion verbatim (velocity Verlet,
u_eta + V4, delta = 0.3, g-timelike). The rotation sector is the MEASURED-
STABLE sector (M5.20.2 census: all rotation K_eff > 0); the boost sector is
watched, not trusted (GB).

RUNS
    noclock   the relaxed baseline evolved with zero velocity (T = 100):
              the quiet-baseline control (any activity in the clock run is
              then the clock, not the statics residual)
    prod      the twist clock, T = 400 (~3 sweeps of the apolar period
              pi/omega at omega = 0.05), film frames at quarter-sweep times
    control   the alternate-axis run (blindspot 5): global-frame
              conjugation about zhat instead of the local-director twist
              (same envelope, T = 100)
    (fallback: if GB fires exponential growth, rerun with the time row
    FROZEN: gradient time-row zeroed, the documented frozen-time-row run)

GATES
    GD  dt^2 max-deviation scaling at dts (0.02, 0.01, 0.005) on the seeded
        state, T = 10; production dt = the largest with maxdev < 2e-2 and
        clean dt^2 ratios; the production ledger maxdev is REPORTED against
        the 1e-5 DoD bar (Verlet shadow oscillation labeled if it exceeds)
    GR  clock read-back: early-window (first quarter sweep) slope of the
        rendered delta-axis phase at each probe == the SEEDED local rate
        omega env(r_probe) within 5%; and omega from the Mdot channel at
        t = 0 == seeded exactly; the LONG-run rate is a physics result
        (potential-coupled twist), reported separately, not gated
    GB  boost watch: max time-mixing |M[0, 1:4]| and |M00 + g| per snap;
        envelope growth-rate fit over the last half; exponential growth =>
        fallback + report
    GQ  stability instruments: meridional charge q == 1 (5%) throughout;
        defect-centre drift < 3 cells; E-localisation fraction (r < 24)
        traced; core spectrum traced (the Q8-dynamic verdict data)

Run:  python m5_21_c_clockrun.py gd|noclock|prod|control|all [T]
Out:  ../data/m5_21_c_<mode>.json, ../plots/m5_21_c_film_<mode>.png,
      ../plots/m5_21_c_traces_<mode>.png, ../data/m5_21_c_final_<mode>.npz
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

from m5_17_energy import cell_weights, grid_coords                 # noqa: E402
from m5_20_a1_dynamics import evolve                               # noqa: E402
from m5_20_2_a_eom import G_T, NR, NZ, H, WSCALE                   # noqa: E402
from m5_20_2_b_dynamics import make_egf_4                          # noqa: E402
from m5_21_a_snap import eig_fields, film_strip                    # noqa: E402
from m5_21_b_electron import (core_spectrum, defect_center,        # noqa: E402
                              electron_seed, meridional_charge)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
DELTA = 0.3
OMEGA = 0.05
R_ENV = 20.0
SNAP_DT = 0.5
PROBES = [(8, 128), (5, 134), (2, 136)]      # (i, j): r ~ 8.5, 8.5, 9.0
FRAME_TS = (0.0, 8.0, 16.0, 24.0, 31.5, 63.0, 126.0, 200.0, 300.0, 400.0)


def load_relaxed():
    st = np.load(os.path.join(DATA, "m5_21_b_relaxed_state.npz"))
    return st["M"].astype(np.float64)


def local_gen(n):
    """W(n): spatial antisymmetric generator about the (unit) 3-vector n,
    embedded 4x4 (time row zero). (W v) = n x v."""
    W = np.zeros(n.shape[:-1] + (4, 4))
    n1, n2, n3 = n[..., 0], n[..., 1], n[..., 2]
    W[..., 1, 2], W[..., 1, 3] = -n3, n2
    W[..., 2, 1], W[..., 2, 3] = n3, -n1
    W[..., 3, 1], W[..., 3, 2] = -n2, n1
    return W


def envelope():
    R, Z = grid_coords(NR, NZ, H)
    r = np.sqrt(R ** 2 + Z ** 2)
    return np.exp(-((r / R_ENV) ** 4))


def twist_velocity(M, omega=OMEGA):
    """the ZBW clock: rotation about the LOCAL director."""
    _, V = eig_fields(M)
    W = local_gen(V[..., :, 0])
    return (omega * envelope())[..., None, None] * (W @ M - M @ W)


def conj_velocity(M, omega=OMEGA):
    """alternate-axis control: conjugation about global zhat."""
    zhat = np.zeros(M.shape[:2] + (3,))
    zhat[..., 2] = 1.0
    W = local_gen(zhat)
    return (omega * envelope())[..., None, None] * (W @ M - M @ W)


# ---------------- probes + snap_fn ----------------
def probe_refs(M):
    """per-probe orthonormal clock frame at t0: e1 = delta-axis(t0),
    e2 = nhat(t0) x e1; phase(t) = atan2(m.e2, m.e1) mod pi."""
    _, V = eig_fields(M)
    refs = []
    for (i, j) in PROBES:
        n0 = V[i, j, :, 0]
        e1 = V[i, j, :, 1]
        e2 = np.cross(n0, e1)
        refs.append((e1, e2))
    return refs


def make_snap_fn(refs, e_loc_r=24.0):
    R, Z = grid_coords(NR, NZ, H)
    r = np.sqrt(R ** 2 + Z ** 2)
    inner = r < e_loc_r
    w = cell_weights(NR, NZ, H)

    def fn(Mx, v):
        lam, V = eig_fields(Mx)
        out = {}
        for k, ((i, j), (e1, e2)) in enumerate(zip(PROBES, refs)):
            m = V[i, j, :, 1]
            out[f"phase{k}"] = float(
                np.mod(np.arctan2(np.dot(m, e2), np.dot(m, e1)), np.pi))
            dlt = max(lam[i, j, 1] - lam[i, j, 2], 1e-30)
            out[f"wmdot{k}"] = float(
                np.linalg.norm(v[i, j]) / (np.sqrt(2.0) * dlt))
        out["gb_timemix"] = float(np.max(np.abs(Mx[..., 0, 1:4])))
        out["gb_m00dev"] = float(np.max(np.abs(Mx[..., 0, 0] + G_T)))
        out["q_meas"] = meridional_charge(Mx)
        cx, cz = defect_center(Mx)
        out["center_rho"], out["center_z"] = cx, cz
        cs = core_spectrum(Mx)
        out["core_lams"] = cs["core_lams"]
        # E localisation: static-energy density fraction inside r < e_loc_r
        # (cheap proxy: cell-weighted amplitude^2 is already in
        # defect_center; use the KE + PE split only at verdict time)
        ke_d = 0.5 * np.sum(v[: NR - 1, 1:-1] ** 2, axis=(-2, -1)) \
            * w
        out["ke_inner_frac"] = float(
            ke_d[inner[: NR - 1, 1:-1]].sum() / max(ke_d.sum(), 1e-300))
        return out
    return fn


# ---------------- GD triage ----------------
def gd_triage(dts=(0.02, 0.01, 0.005), T=10.0):
    M0 = load_relaxed()
    v0 = twist_velocity(M0)
    egf = make_egf_4(DELTA)
    res = {}
    for dt in dts:
        _, _, recs, wall = evolve(M0.copy(), egf, T, dt,
                                  snap_every=max(1, int(0.5 / dt)),
                                  v0=v0.copy())
        E = np.array([r["E_tot"] for r in recs])
        dev = float(np.max(np.abs(E - E[0])) / abs(E[0]))
        res[str(dt)] = {"maxdev_rel": dev, "wall_s": round(wall, 1),
                        "finite": bool(np.all(np.isfinite(E)))}
        print(f"  dt={dt}: maxdev {dev:.2e} wall {wall:.0f}s", flush=True)
    ds = [res[str(d)]["maxdev_rel"] for d in dts]
    ratios = [ds[i] / max(ds[i + 1], 1e-300) for i in range(len(ds) - 1)]
    dt_prod = next((d for d in dts if res[str(d)]["finite"]
                    and res[str(d)]["maxdev_rel"] < 2e-2), None)
    ok = (all(r["finite"] for r in res.values()) and dt_prod is not None)
    out = {"per_dt": res, "ratios": ratios, "dt_production": dt_prod,
           "ok": bool(ok)}
    with open(os.path.join(DATA, "m5_21_c_gd.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[GD] {'PASS' if ok else 'FAIL'} dt_prod={dt_prod} "
          f"ratios={np.round(ratios, 2)}")
    return out


# ---------------- production ----------------
def run(mode="prod", T=400.0, dt=0.01, frozen_time=False, omega=OMEGA):
    M0 = load_relaxed()
    if mode in ("prod", "gentle"):
        v0 = twist_velocity(M0, omega)
    elif mode == "control":
        v0 = conj_velocity(M0, omega)
    elif mode == "noclock":
        v0 = np.zeros_like(M0)
    else:
        raise ValueError(mode)
    refs = probe_refs(M0)
    e_fn, g_fn = make_egf_4(DELTA)
    if frozen_time:
        g_inner = g_fn

        def g_fn(MM):                      # noqa: F811
            G = g_inner(MM)
            G[..., 0, :] = 0.0
            G[..., :, 0] = 0.0
            return G
    frames, frame_ts = [], []
    snap_calls = [0]
    base_fn = make_snap_fn(refs)

    def snap_fn(Mx, v):
        t_now = snap_calls[0] * SNAP_DT
        snap_calls[0] += 1
        if (len(frame_ts) < len(FRAME_TS)
                and t_now >= FRAME_TS[len(frame_ts)] - SNAP_DT / 2
                and t_now <= T + SNAP_DT):
            frames.append({"t": t_now, "M": Mx.copy(), "V": v.copy()})
            frame_ts.append(t_now)
        return base_fn(Mx, v)

    Mx, v, recs, wall = evolve(M0, (e_fn, g_fn), T, dt,
                               snap_every=max(1, int(SNAP_DT / dt)),
                               v0=v0, snap_fn=snap_fn)
    print(f"  [{mode}] T={T} dt={dt} wall {wall:.0f}s "
          f"snaps {len(recs)} frames {len(frames)}", flush=True)
    out = analyze(mode, recs, T, dt, wall, frozen_time, omega)
    render(mode, frames, recs)
    np.savez_compressed(os.path.join(DATA, f"m5_21_c_final_{mode}.npz"),
                        M=Mx, v=v)
    with open(os.path.join(DATA, f"m5_21_c_{mode}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"wrote data/m5_21_c_{mode}.json + final npz", flush=True)
    return out


def analyze(mode, recs, T, dt, wall, frozen_time, omega=OMEGA):
    t = np.array([r["t"] for r in recs])
    E = np.array([r["E_tot"] for r in recs])
    ledger = float(np.max(np.abs(E - E[0])) / abs(E[0]))
    out = {"task": "M5.21", "phase": "C", "mode": mode, "delta": DELTA,
           "omega": omega, "r_env": R_ENV, "T": T, "dt": dt,
           "frozen_time": frozen_time, "wall_s": round(wall, 1),
           "ledger_maxdev_rel": ledger,
           "E_first_last": [float(E[0]), float(E[-1])]}
    R, Z = grid_coords(NR, NZ, H)
    env = envelope()
    # GR: early-window phase slope per probe vs seeded local rate
    gr = []
    quarter = (np.pi / omega) / 4.0
    win = t <= quarter
    for k, (i, j) in enumerate(PROBES):
        ph = np.unwrap(np.array([r[f"phase{k}"] for r in recs]),
                       period=np.pi)
        seed_rate = omega * env[i, j]
        if mode == "prod":
            pass                            # local twist: rate = omega env
        slope = float(np.polyfit(t[win], ph[win], 1)[0])
        wm0 = recs[0][f"wmdot{k}"]
        gr.append({"probe": [i, j], "r": float(np.hypot(R[i, j], Z[i, j])),
                   "seeded_rate": float(seed_rate),
                   "early_slope": slope,
                   "early_relerr": abs(abs(slope) - seed_rate)
                   / max(seed_rate, 1e-30),
                   "wmdot_t0": wm0,
                   "wmdot_t0_relerr": abs(wm0 - seed_rate)
                   / max(seed_rate, 1e-30),
                   "long_slope": float(np.polyfit(t, ph, 1)[0])})
    out["GR"] = gr
    # GB: growth of the time-mixing envelope over the last half
    gbm = np.array([r["gb_timemix"] for r in recs])
    half = len(gbm) // 2
    grow = float(np.polyfit(t[half:], np.log(np.maximum(gbm[half:], 1e-30)),
                            1)[0]) if np.any(gbm[half:] > 0) else 0.0
    out["GB"] = {"timemix_first_last": [float(gbm[0]), float(gbm[-1])],
                 "m00dev_last": recs[-1]["gb_m00dev"],
                 "envelope_growth_rate": grow,
                 "exponential": bool(grow > 1e-3 and gbm[-1] > 1e-3)}
    # GQ
    q = np.array([r["q_meas"] for r in recs])
    cx = np.array([r["center_rho"] for r in recs])
    cz = np.array([r["center_z"] for r in recs])
    drift = float(np.max(np.hypot(cx - cx[0], cz - cz[0])))
    out["GQ"] = {"q_min": float(q.min()), "q_max": float(q.max()),
                 "q_ok": bool(np.all(np.abs(q - 1.0) < 0.05)),
                 "center_drift_max": drift,
                 "drift_ok": bool(drift < 3.0),
                 "core_lams_first": recs[0]["core_lams"],
                 "core_lams_last": recs[-1]["core_lams"]}
    out["trajectory"] = recs
    print(f"  [ledger] maxdev {ledger:.2e}  [GB] growth {grow:+.2e} "
          f"timemix {gbm[0]:.2e}->{gbm[-1]:.2e}  [GQ] q "
          f"{q.min():.3f}..{q.max():.3f} drift {drift:.2f}", flush=True)
    for g in gr:
        print(f"  [GR] probe {g['probe']} seeded {g['seeded_rate']:.4f} "
              f"early {g['early_slope']:+.4f} "
              f"(err {g['early_relerr']:.1%}) long {g['long_slope']:+.4f}",
              flush=True)
    return out


def render(mode, frames, recs):
    R, Z = grid_coords(NR, NZ, H)
    film_strip(frames, R, Z, H, DELTA,
               os.path.join(PLOTS, f"m5_21_c_film_{mode}.png"),
               step=4, zoom=(-40.0, 40.0, 0.0, 40.0),
               log_channels=("A", "energy", "charge", "curl"),
               suptitle=f"M5.21-C {mode}: the electron rotation clock "
                        f"(omega = {OMEGA}, local-director twist"
                        + (", FROZEN time row" if mode.endswith("frozen")
                           else "") + "); zoom rho<40 |z|<40")
    t = np.array([r["t"] for r in recs])
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    E = np.array([r["E_tot"] for r in recs])
    axes[0, 0].plot(t, (E - E[0]) / abs(E[0]), lw=0.9)
    axes[0, 0].set_title("energy ledger (E - E0)/|E0|", fontsize=9)
    for k in range(len(PROBES)):
        ph = np.unwrap(np.array([r[f"phase{k}"] for r in recs]),
                       period=np.pi)
        axes[0, 1].plot(t, ph, lw=0.9, label=f"probe {k}")
        axes[0, 2].plot(t, [r[f"wmdot{k}"] for r in recs], lw=0.9)
    axes[0, 1].set_title("delta-axis phase (unwrapped, apolar)",
                         fontsize=9)
    axes[0, 1].legend(fontsize=7)
    axes[0, 2].set_title("omega from the Mdot channel", fontsize=9)
    axes[1, 0].semilogy(t, np.maximum(
        [r["gb_timemix"] for r in recs], 1e-30), lw=0.9, label="|M[0,i]|")
    axes[1, 0].semilogy(t, np.maximum(
        [r["gb_m00dev"] for r in recs], 1e-30), lw=0.9, label="|M00+g|")
    axes[1, 0].set_title("GB boost watch (log)", fontsize=9)
    axes[1, 0].legend(fontsize=7)
    axes[1, 1].plot(t, [r["q_meas"] for r in recs], lw=0.9)
    axes[1, 1].set_title("meridional charge q", fontsize=9)
    core = np.array([r["core_lams"] for r in recs])
    for k in range(3):
        axes[1, 2].plot(t, core[:, k], lw=0.9, label=f"lam{k + 1}")
    axes[1, 2].axhline((1 + DELTA) / 3, color="0.6", ls=":", lw=1,
                       label="(1+delta)/3")
    axes[1, 2].set_title("core spectrum (Q8-dynamic data)", fontsize=9)
    axes[1, 2].legend(fontsize=7)
    for ax in axes.flat:
        ax.set_xlabel("t", fontsize=8)
        ax.tick_params(labelsize=7)
    fig.suptitle(f"M5.21-C traces: {mode}", fontsize=11)
    fig.tight_layout()
    path = os.path.join(PLOTS, f"m5_21_c_traces_{mode}.png")
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("wrote", os.path.relpath(path, HERE), flush=True)


def main():
    mode = ARGV[0] if ARGV else "all"
    T = float(ARGV[1]) if len(ARGV) > 1 else None
    if mode in ("gd", "all"):
        gd = gd_triage()
        dt = gd["dt_production"] or 0.005
    else:
        try:
            with open(os.path.join(DATA, "m5_21_c_gd.json")) as f:
                dt = json.load(f)["dt_production"] or 0.005
        except FileNotFoundError:
            dt = 0.01
    if mode in ("noclock", "all"):
        run("noclock", T=T or 100.0, dt=dt)
    if mode in ("prod", "all"):
        run("prod", T=T or 400.0, dt=dt)
    if mode in ("control", "all"):
        run("control", T=T or 100.0, dt=dt)
    if mode == "gentle":                      # kick-amplitude dependence
        run("gentle", T=T or 100.0, dt=dt, omega=0.02)


if __name__ == "__main__":
    main()
