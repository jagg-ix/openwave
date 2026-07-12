"""M5.20.1 phase C: FIRE statics triage per (delta, pairing).

The DoD-4 question: does the removability channel close ALREADY IN STATICS
at delta != 0? Per (delta, pairing) seed (the phase-B biax escaped loop,
q = 1/2, R0 = 17, NARROW cores): FIRE relax on the m5_16 stack (fast
gradient, GF-d gated), verdict from the endpoint winding + core state.

Verdicts (pre-registered)
    HOLDS     gnorm falls >= 3 decades (or below abs floor) AND the
              endpoint winding reads |q| within 0.1 of the seed
    DISSOLVES endpoint winding < 0.1 (the winding left in statics)
    STALLS    neither (progress-rate stall, the honest M5.12 wording)

Run:  python m5_20_1_c_statics.py [iters]     (all 6 cases, sequential)
Out:  ../data/m5_20_1_c_statics.json (+ per-case _state.npz)
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import cell_weights                              # noqa: E402
from m5_16_axisym import fire_relax, pin_mask                      # noqa: E402
from m5_20_1_b_seeds import winding_measure_biax, core_spectrum    # noqa: E402
from m5_20_1_d_dynamics import (NR, NZ, H, WSCALE, make_egf_biax,  # noqa: E402
                                seed_biax)
from m5_19_d1_relax import ring_by_m13                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")


def relax_case(delta, pairing, iters=4000, log_every=500):
    name = f"d{str(delta).replace('.', 'p')}_{pairing}"
    M0 = seed_biax(delta, pairing)
    e_fn, g_fn = make_egf_biax(delta)
    egf = lambda MM: (e_fn(MM), g_fn(MM))                    # noqa: E731
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(NR, NZ, H)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    def snap(MM, it, Ev):
        rd = ring_by_m13(MM, NR, NZ, H)
        qm, mix = winding_measure_biax(MM, NR, NZ, H, rd["ring13_rho"],
                                       rd["ring13_z"])
        cs = core_spectrum(MM, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
        return {"it": it, "E": Ev, "ring13_rho": rd["ring13_rho"],
                "ring13_z": rd["ring13_z"], "m13_max": rd["m13_max"],
                "q_meas": qm, "mix": mix, "core_lam": cs["lam"],
                "core_equalized": cs["equalized"]}

    traj = [snap(M0, 0, e_fn(M0))]
    print(f"[{name}] E0 = {traj[0]['E']:.3f} q0 = {traj[0]['q_meas']:.3f} "
          f"core_eq {traj[0]['core_equalized']}", flush=True)
    t0 = time.time()
    Mx = M0
    g0n = gn_last = None
    done = 0
    while done < iters:
        step = min(log_every, iters - done)
        Mx, hist = fire_relax(Mx, egf, free4, precond, max_iter=step,
                              tol_rel=1e-6, dt0=0.005, dt_max=0.05,
                              log_every=step)
        if g0n is None:
            g0n = hist["gnorm"][0]
        gn_last = hist["gnorm"][-1]
        done += hist["iter"][-1]
        traj.append(snap(Mx, done, hist["E"][-1]))
        r = traj[-1]
        print(f"  it {done:5d} E {r['E']:.3f} gnorm {gn_last:.3e} "
              f"q {r['q_meas']:.3f} core_eq {r['core_equalized']}",
              flush=True)
        if not np.isfinite(r["E"]):
            break
        if gn_last < 1e-6 * g0n or gn_last < 1e-9:
            break
        if hist["iter"][-1] < step:
            break
    decades = float(np.log10(g0n / (gn_last + 1e-300)))
    q_end = traj[-1]["q_meas"]
    q0 = abs(traj[0]["q_meas"])
    if np.isfinite(q_end) and abs(abs(q_end) - q0) < 0.1 and decades >= 3.0:
        verdict = "HOLDS"
    elif np.isfinite(q_end) and abs(q_end) < 0.1:
        verdict = "DISSOLVES"
    elif not np.isfinite(q_end) and traj[-1]["m13_max"] < 0.1:
        verdict = "DISSOLVES"
    else:
        verdict = "STALLS"
    out = {"delta": delta, "pairing": pairing, "iters_run": done,
           "gnorm_decades": decades,
           "E_first_last": [traj[0]["E"], traj[-1]["E"]],
           "q_first_last": [traj[0]["q_meas"], q_end],
           "core_eq_first_last": [traj[0]["core_equalized"],
                                  traj[-1]["core_equalized"]],
           "verdict": verdict, "trajectory": traj,
           "wall_s": round(time.time() - t0, 1)}
    np.savez_compressed(os.path.join(DATA,
                                     f"m5_20_1_c_{name}_state.npz"),
                        M0=Mx.astype(np.float32))
    print(f"[{name}] {verdict}: E {traj[0]['E']:.3f} -> {traj[-1]['E']:.3f}, "
          f"{decades:.1f} decades, q -> {q_end}, wall {out['wall_s']}s",
          flush=True)
    return out


if __name__ == "__main__":
    iters = int(ARGV[0]) if ARGV else 4000
    results = {"task": "M5.20.1", "phase": "C", "wscale": WSCALE,
               "iters": iters, "cases": {}}
    for delta in (0.1, 0.3, 0.5):
        for pairing in ("pair_1d", "pair_d0"):
            key = f"d{delta}_{pairing}"
            results["cases"][key] = relax_case(delta, pairing, iters)
            with open(os.path.join(DATA, "m5_20_1_c_statics.json"),
                      "w") as f:
                json.dump(results, f, indent=1, default=float)
    print("wrote data/m5_20_1_c_statics.json")
