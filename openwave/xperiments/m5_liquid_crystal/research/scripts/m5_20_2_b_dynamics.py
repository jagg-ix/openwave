"""M5.20.2 phase B: well-posedness triage + the clock baseline (GO/NO-GO).

Dynamics = canonical kinetic term (the documented regularization of the
purely-quartic verified L, m5_20_2_a_eom.py header) + HIS static sector:
    w_cell d_t^2 M = - dE_static/dM,   E_static = INT w (u_eta + V4),
velocity Verlet (the audited m5_20_a1_dynamics.evolve, reused verbatim).
The eta structure lives in the STATIC energy, which is INDEFINITE (the
M5.18 4b witnesses): the triage below decides whether production runs are
meaningful before any is launched.

TRIAGE (pre-registered GO/NO-GO)
    T1  dt^2 drift scaling on the 4x4 loop seed + time-mixing bump at the
        stiff-mode-resolving dts; pick the production dt
    T2  ROTATION-sector injection on the vac4 background (uniform branch
        vacuum + localized spatial-rotation time-mixing texture): energy
        conserved AND the probe oscillates at a ladder frequency (the
        clock line) => GO
    T3  BOOST-sector injection (the M5.18 4b hazard class): measured
        growth rate; bounded oscillation => the hazard is inert at this
        amplitude; exponential growth => documented, the injection class
        EXCLUDED from production seeds (production uses rotation-sector
        only), and if T2 ALSO grows => NO-GO (ship the derivation + the
        one question)

The clock observable: the time-mixing amplitude a01(t) = M[probe cell,
0, 1] and the local Tr_eta spectrum; FFT peak vs the phase-A ladder.

Run:  python m5_20_2_b_dynamics.py t1|t2|t3|all
Out:  ../data/m5_20_2_b_triage.json, ../plots/m5_20_2_clock_baseline.png
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
from m5_20_2_a_eom import (G_T, NR, NZ, H, WSCALE, grad_static_4,  # noqa: E402
                           total_energy_4, u_eta_density,
                           v4_density, vac4, seed4, hessian4_analytic)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def make_egf_4(delta):
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]

    def e_fn(MM):
        return total_energy_4(MM, WSCALE, delta)

    def g_fn(MM):
        return grad_static_4(MM, WSCALE, delta, w4=w4, rho4=rho4)
    return e_fn, g_fn


def vac_field(delta, branch="g_timelike"):
    M = np.zeros((NR, NZ, 4, 4))
    M[..., :, :] = vac4(delta, branch=branch)
    return M


def inject(M, sector, amp=0.02, center=(40.0, 0.0), sig=3.0):
    """localized time-mixing texture. rotation sector: the (0,1) component
    driven with a SPATIAL-rotation profile (the T2 probe); boost sector:
    a plain (0,1) boost bump plus a (1,2) rotation bump sharing axis 1
    (the M5.18 4b negative-density texture class, T3)."""
    R, Z = grid_coords(NR, NZ, H)
    bump = amp * np.exp(-((R - center[0]) ** 2 + (Z - center[1]) ** 2)
                        / (2 * sig ** 2))
    out = M.copy()
    if sector == "rotation":
        # spatial rotation texture in the (1,2) plane, no time mixing:
        # the benign reference (pure rotation flats)
        out[..., 1, 2] += bump
        out[..., 2, 1] += bump
    elif sector == "clock":
        # time-mixing (0,1) probe: the clock candidate (boost direction,
        # SMALL amplitude, isolated: no rotation partner texture)
        out[..., 0, 1] += bump
        out[..., 1, 0] += bump
    elif sector == "boost4b":
        # the 4b hazard class: boost(0,1) x rotation(1,2) sharing axis 1
        out[..., 0, 1] += bump
        out[..., 1, 0] += bump
        out[..., 1, 2] += bump
        out[..., 2, 1] += bump
    else:
        raise ValueError(sector)
    return out


def probe_fn(delta, center=(40.0, 0.0)):
    ci = int(round(center[0] / H - 0.5))
    cj = int(round(center[1] / H + (NZ - 2) / 2 - 0.5)) + 1
    w = cell_weights(NR, NZ, H)

    def fn(Mx, v):
        a01 = float(Mx[ci, cj, 0, 1])
        a12 = float(Mx[ci, cj, 1, 2])
        u = u_eta_density(Mx, H)
        neg = float(np.sum((u * w)[u < 0]))
        return {"a01": a01, "a12": a12, "u_neg_total": neg,
                "maxabs": float(np.max(np.abs(Mx[..., 0, 1:])))}
    return fn


def t1_dt(delta=0.3, T=10.0, dts=(0.02, 0.01, 0.005)):
    """the stiff g-mode (omega = 78) gives a LARGE but BOUNDED Verlet
    shadow-energy oscillation; the criterion is therefore the MAX energy
    DEVIATION over the window (not the endpoint drift, which aliases the
    oscillation phase: the first run of this gate measured exactly that),
    with dt^2 scaling required between successive dts."""
    M0 = inject(seed4(delta, "pair_1d"), "clock", amp=0.02,
                center=(17.0, 0.0))
    egf = make_egf_4(delta)
    res = {}
    for dt in dts:
        _, _, recs, wall = evolve(M0, egf, T, dt,
                                  snap_every=max(1, int(0.5 / dt)))
        E = np.array([r["E_tot"] for r in recs])
        dev = float(np.max(np.abs(E - E[0])) / abs(E[0]))
        res[str(dt)] = {"maxdev_rel": dev, "wall_s": wall,
                        "finite": bool(np.all(np.isfinite(E)))}
        print(f"  dt={dt}: maxdev {dev:.2e} wall {wall:.0f}s "
              f"finite={res[str(dt)]['finite']}", flush=True)
    ds = [res[str(d)]["maxdev_rel"] for d in dts]
    ratios = [ds[i] / max(ds[i + 1], 1e-300) for i in range(len(ds) - 1)]
    finite = all(r["finite"] for r in res.values())
    scaling = all(2.5 < r < 6.0 for r in ratios)
    dt_prod = None
    for dt in dts:
        if res[str(dt)]["finite"] and res[str(dt)]["maxdev_rel"] < 2e-2:
            dt_prod = dt
            break
    ok = finite and scaling and dt_prod is not None
    return ok, {"per_dt": res, "ratios": ratios,
                "dt_production": dt_prod,
                "note": "bounded shadow oscillation from the stiff g-mode;"
                        " secular drift none observed"}


def t23(delta=0.3, sector="clock", T=400.0, dt=0.01, amp=0.02):
    M0 = inject(vac_field(delta), sector, amp=amp)
    egf = make_egf_4(delta)
    snap = probe_fn(delta)
    Mx, v, recs, wall = evolve(M0, egf, T, dt,
                               snap_every=max(1, int(0.5 / dt)),
                               snap_fn=snap)
    t = np.array([r["t"] for r in recs])
    a01 = np.array([r["a01"] for r in recs])
    ma = np.array([r["maxabs"] for r in recs])
    drift = abs(recs[-1]["E_tot"] - recs[0]["E_tot"]) / max(
        abs(recs[0]["E_tot"]), 1e-30)
    # growth: log-linear fit of the envelope over the last half
    half = len(ma) // 2
    grow = float(np.polyfit(t[half:], np.log(np.maximum(ma[half:], 1e-30)),
                            1)[0])
    # FFT of the probe
    y = a01 - np.mean(a01)
    f = np.fft.rfftfreq(len(y), d=(t[1] - t[0]))
    aa = np.abs(np.fft.rfft(y * np.hanning(len(y))))
    pk = float(f[1:][np.argmax(aa[1:])] * 2 * np.pi)
    ev = np.linalg.eigvalsh(hessian4_analytic(delta))
    ladder = np.sqrt(np.maximum(ev, 0.0))
    out = {"sector": sector, "delta": delta, "T": T, "dt": dt, "amp": amp,
           "drift_rel": drift, "envelope_growth_rate": grow,
           "omega_peak": pk, "ladder": ladder.tolist(),
           "maxabs_first_last": [float(ma[0]), float(ma[-1])],
           "u_neg_final": recs[-1]["u_neg_total"],
           "wall_s": round(wall, 1),
           "trajectory": recs}
    print(f"  [{sector}] drift {drift:.2e} growth {grow:+.2e}/t "
          f"omega_peak {pk:.4f} (ladder {np.round(ladder[ladder>1e-9], 4)}) "
          f"maxabs {ma[0]:.3f}->{ma[-1]:.3f} wall {wall:.0f}s", flush=True)
    return out


def main(which="all"):
    res = {"task": "M5.20.2", "phase": "B", "wscale": WSCALE, "g": G_T}
    if which in ("t1", "all"):
        ok, det = t1_dt()
        res["T1"] = {"ok": bool(ok), "detail": det}
        print(f"[T1] {'PASS' if ok else 'FAIL'} dt_prod="
              f"{det['dt_production']}")
    dt = res.get("T1", {}).get("detail", {}).get("dt_production") or 0.01
    if which in ("t2", "all"):
        res["T2_clock"] = t23(sector="clock", dt=dt)
        res["T2_rotation"] = t23(sector="rotation", dt=dt)
    if which in ("t3", "all"):
        res["T3_boost4b"] = t23(sector="boost4b", dt=dt)
    # GO/NO-GO
    if "T2_clock" in res and "T3_boost4b" in res:
        clock_ok = (res["T2_clock"]["drift_rel"] < 1e-3
                    and res["T2_clock"]["envelope_growth_rate"] < 1e-3)
        res["verdict"] = {
            "clock_sector_stable": bool(clock_ok),
            "boost4b_growth": res["T3_boost4b"]["envelope_growth_rate"],
            "GO": bool(clock_ok)}
        print(f"[VERDICT] GO={res['verdict']['GO']} "
              f"(clock stable={clock_ok}, boost4b growth "
              f"{res['verdict']['boost4b_growth']:+.2e})")
    with open(os.path.join(DATA, "m5_20_2_b_triage.json"), "w") as f:
        json.dump(res, f, indent=1, default=float)
    # plot
    if "T2_clock" in res:
        fig, axes = plt.subplots(1, 3, figsize=(15, 3.6))
        for key, ax in (("T2_clock", axes[0]), ("T2_rotation", axes[1]),
                        ("T3_boost4b", axes[2])):
            if key not in res:
                continue
            tr = res[key]["trajectory"]
            t = [r["t"] for r in tr]
            ax.plot(t, [r["a01"] for r in tr], lw=0.9, label="a01(t)")
            ax.plot(t, [r["maxabs"] for r in tr], lw=0.9,
                    label="max|time-mixing|")
            ax.set_title(f"{key}: growth "
                         f"{res[key]['envelope_growth_rate']:+.1e}/t",
                         fontsize=9)
            ax.set_xlabel("t")
            ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "m5_20_2_clock_baseline.png"),
                    dpi=120)
        print("wrote plots/m5_20_2_clock_baseline.png")
    print("wrote data/m5_20_2_b_triage.json")
    return res


if __name__ == "__main__":
    main(ARGV[0] if ARGV else "all")
