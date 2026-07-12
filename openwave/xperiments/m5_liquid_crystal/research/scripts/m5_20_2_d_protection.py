"""M5.20.2 phase D: the protection re-probe under the FULL 4-target
potential (DoD 5, scoped to the stable sector).

The dynamical time block is obstructed (phase-B: boost runaway), so the
honest 4x4 protection question that CAN be run is: does adding the p = 4
spectral target (his full V, which the 3-target M5.20.1 run did not
carry; the frozen-time-row reduction adds +1.70 to the delta = 0.3 seed
energy) change the UNWOUND verdict of the spatial sector? Time row FROZEN
at the branch value (force projected off the 0-row/col): the M5.20.1
conservative instrument otherwise verbatim.

Run:  python m5_20_2_d_protection.py [T] [dt]
Out:  ../data/m5_20_2_run_protection.json / _state.npz
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import cell_weights                              # noqa: E402
from m5_20_a1_dynamics import evolve                               # noqa: E402
from m5_20_2_a_eom import (NR, NZ, H, WSCALE, grad_static_4,       # noqa: E402
                           total_energy_4, seed4)
from m5_20_1_d_dynamics import make_snap_biax                      # noqa: E402
from m5_20_1_e_verdicts import winding_measure_bilin, core_hunt    # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
DELTA = 0.3


def main(T=2000.0, dt=0.02):
    M0 = seed4(DELTA, "pair_1d")
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]

    def e_fn(MM):
        return total_energy_4(MM, WSCALE, DELTA)

    def g_fn(MM):
        G = grad_static_4(MM, WSCALE, DELTA, w4=w4, rho4=rho4)
        G[..., 0, :] = 0.0                  # time row frozen
        G[..., :, 0] = 0.0
        return G

    snap = make_snap_biax(DELTA)            # diagnostics (3-target PE_in8)
    E0 = e_fn(M0)
    print(f"[protection4] T={T} dt={dt} E0={E0:.3f} (4-target V)",
          flush=True)
    Mx, v, recs, wall = evolve(M0, (e_fn, g_fn), T, dt,
                               snap_every=int(round(max(T / 80, dt) / dt)),
                               snap_fn=snap, log_snaps=True)
    rd = ring_by_m13(Mx, NR, NZ, H)
    reads = {}
    for rw in (3.0, 4.0, 5.0, 6.0, 8.0):
        q, amin, mix = winding_measure_bilin(Mx, rd["ring13_rho"],
                                             rd["ring13_z"], r_w=rw)
        reads[str(rw)] = None if not np.isfinite(q) else round(float(q), 4)
    hunt = core_hunt(Mx)
    qs = [v for v in reads.values() if v is not None]
    unwound = (len(qs) >= 3 and max(abs(q) for q in qs) < 0.1
               and not any(any(x is not None and abs(x) > 0.35
                               for x in p["q"].values()) for p in hunt))
    out = {"task": "M5.20.2", "phase": "D", "delta": DELTA,
           "pairing": "pair_1d", "potential": "4-target (p = 1..4)",
           "time_row": "frozen (-g)", "T": T, "dt": dt,
           "wscale": WSCALE, "E0": E0,
           "endpoint_q_reads": reads, "core_hunt_top3": hunt[:3],
           "verdict": "UNWOUND" if unwound else "INSPECT",
           "trajectory": recs, "wall_s": round(wall, 1)}
    with open(os.path.join(DATA, "m5_20_2_run_protection.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    np.savez_compressed(os.path.join(DATA,
                                     "m5_20_2_run_protection_state.npz"),
                        M0=Mx.astype(np.float32))
    print(f"[protection4] done: verdict {out['verdict']}, q_reads {reads}, "
          f"drift {(recs[-1]['E_tot'] - recs[0]['E_tot']) / recs[0]['E_tot']:.2e}, "
          f"wall {wall:.0f}s", flush=True)
    return out


if __name__ == "__main__":
    T = float(ARGV[0]) if ARGV else 2000.0
    dt = float(ARGV[1]) if len(ARGV) > 1 else 0.02
    main(T, dt)
