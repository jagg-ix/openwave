"""M5.19 phase D: statics minimization from the phase-C R* seeds.

The pre-registered gate (task_details): a stationary regularized loop (gnorm
decades + bounded second-variation probe) OR the honest negative with the
M5.12 wording rules (a progress-rate stall is NOT stationarity; verdicts per
the M5.11 classifier).

Seeds: the phase-C twist-escaped R*-bracketing configurations (box-independent
interior minima). FIRE relaxation on the M5.12 statics stack (spectral
potential delta = 0, calibrated wscale), boundary pinned at the seed's far
field = the exact e2e2^T vacuum.

Class-aware diagnostics (the M5.12 ring_readout min_s is melt-specific):
  - ring locator by argmax |M13| (the meridional off-diagonal: zero in the
    e2e2^T far field, zero at the two-equal core center, maximal on the ring
    shoulder): robust across core classes;
  - the M5.12 min_s readout kept for the melt class (comparability);
  - WINDING q_meas: the (1,3)-block eigenframe angle
        theta = 0.5 atan2(2 M13, M11 - M33)
    accumulated around a radius-r_w circle centered on the located ring
    (mod-pi unwrapping: nematic winding in units of 1/2): detects unwinding
    through the removability channel (the phase-C caveat made measurable).

Run:  python m5_19_d1_relax.py single <case> [iters]
      python m5_19_d1_relax.py all [iters]
Cases: melt_q05_R17, escape_q05_R18, melt_q10_R6.

Outputs: ../data/m5_19_d1_<case>.json + _state.npz, ../plots/m5_19_d1_relax.png
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

from m5_17_energy import cell_weights, grid_coords                # noqa: E402
from m5_16_axisym import fire_relax, pin_mask                     # noqa: E402
from m5_18_spectral import (energy_gradient_spec_np,              # noqa: E402
                            total_energy_spec_np)
from m5_12_core_pin import load_wscale                            # noqa: E402
from m5_12_loop import ring_readout                               # noqa: E402
from m5_19_c1_loop import CLASSES, NARROW, loop_field_escaped     # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
WSCALE = load_wscale()
NR, NZ, H = 128, 256, 1.0

CASES = {
    "melt_q05_R17": {"cls": "melt", "q": 0.5, "R0": 17.0},
    "escape_q05_R18": {"cls": "escape", "q": 0.5, "R0": 18.0},
    "melt_q10_R6": {"cls": "melt", "q": 1.0, "R0": 6.0},
}


def ring_by_m13(Mnp, nr, nz, h):
    """ring CORE locator: the |M13|^2-weighted centroid (the M13 cloud is a
    donut around the core, so its centroid sits ON the core; the argmax
    would sit on the donut shoulder at z != 0 and a winding circle centered
    there can miss the core entirely: the it-0 q_meas = 0 bug)."""
    m13 = Mnp[: nr - 1, 1:-1, 1, 3]
    if not np.all(np.isfinite(m13)):
        return {"ring13_rho": float("nan"), "ring13_z": float("nan"),
                "m13_max": float("nan")}
    w2 = m13 ** 2
    tot = float(np.sum(w2))
    if tot <= 1e-30:
        return {"ring13_rho": float("nan"), "ring13_z": float("nan"),
                "m13_max": 0.0}
    ri = (np.arange(nr - 1) + 0.5) * h
    zj = (np.arange(1, nz - 1) - nz / 2 + 0.5) * h
    rho_c = float(np.sum(w2 * ri[:, None]) / tot)
    z_c = float(np.sum(w2 * zj[None, :]) / tot)
    return {"ring13_rho": rho_c, "ring13_z": z_c,
            "m13_max": float(np.max(np.abs(m13)))}


def winding_measure(Mnp, nr, nz, h, rho_c, z_c, r_w=4.0, npts=720):
    """nematic winding of the (1,3)-block eigenframe angle around the circle
    of radius r_w centered at (rho_c, z_c): theta = 0.5 atan2(2 M13,
    M11 - M33) is defined mod pi/... the DIRECTOR angle mod pi; accumulate
    the unwrapped increment (each step mapped to (-pi/4, pi/4] in theta,
    i.e. mod pi/2 on 2*theta) -> q_meas = total / pi (units of 1/2)."""
    if not np.all(np.isfinite(Mnp)):
        return float("nan")
    ang = np.linspace(0.0, 2.0 * np.pi, npts, endpoint=True)
    rr = rho_c + r_w * np.cos(ang)
    zz = z_c + r_w * np.sin(ang)
    ii = np.clip(np.round(rr / h - 0.5).astype(int), 0, nr - 2)
    jj = np.clip(np.round(zz / h + (nz - 2) / 2 - 0.5).astype(int) + 1, 1,
                 nz - 2)
    m11 = Mnp[ii, jj, 1, 1]
    m33 = Mnp[ii, jj, 3, 3]
    m13 = Mnp[ii, jj, 1, 3]
    aniso = np.sqrt((m11 - m33) ** 2 + 4.0 * m13 ** 2)
    if float(np.min(aniso)) < 0.02:      # near-isotropic arc: angle undefined
        return float("nan")
    two_theta = np.arctan2(2.0 * m13, m11 - m33)
    dth = np.diff(two_theta)
    dth = (dth + np.pi) % (2.0 * np.pi) - np.pi     # director: mod pi on 2theta
    # Delta(2 theta) = 2 pi  <=>  a director half-turn  <=>  q = 1/2
    return float(np.sum(dth) / (4.0 * np.pi))


def run_case(name, iters=8000, log_every=500, resume=False, corepin=False,
             r_pin=2.5):
    """resume=True: continue from the saved endpoint state (suffix _ext).
    corepin=True: freeze cells within r_pin of the seed ring core at their
    seed values (the M5.12 corepin convention): the CONSTRAINED minimizer,
    the quasi-static background for the phase-E clock (suffix _corepin)."""
    spec = CASES[name]
    ctr = CLASSES[spec["cls"]]
    R, Z = grid_coords(NR, NZ, H)
    if resume:
        M0 = np.load(os.path.join(
            DATA, f"m5_19_d1_{name}_state.npz"))["M0"].astype(np.float64)
        name = name + "_ext"
    else:
        M0 = loop_field_escaped(R, Z, spec["R0"], spec["q"], ctr["mu0"],
                                ctr["nu0"], NARROW["ws"], NARROW["wm"],
                                NARROW["w3"], ctr["shape"])
    pin = pin_mask(NR, NZ)
    if corepin:
        cmask = np.sqrt((R - spec["R0"]) ** 2 + Z ** 2) < r_pin
        pin = pin | cmask
        name = name + "_corepin"
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(NR, NZ, H)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    def egf(MM):
        return (total_energy_spec_np(MM, WSCALE, H),
                energy_gradient_spec_np(MM, WSCALE, H))

    def snap(MM, it, Ev):
        rd = ring_by_m13(MM, NR, NZ, H)
        rd.update(ring_readout(MM, NR, NZ, H))
        rd["q_meas"] = winding_measure(MM, NR, NZ, H, rd["ring13_rho"],
                                       rd["ring13_z"])
        rd["it"] = it
        rd["E"] = Ev
        return rd

    traj = [snap(M0, 0, total_energy_spec_np(M0, WSCALE, H))]
    print(f"[{name}] E0 = {traj[0]['E']:.3f} ring13 rho {traj[0]['ring13_rho']:.1f} "
          f"q_meas {traj[0]['q_meas']:.3f}")
    t0 = time.time()
    Mx = M0
    g0n = None
    gn_last = None
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
              f"ring13 ({r['ring13_rho']:.1f},{r['ring13_z']:.1f}) "
              f"m13 {r['m13_max']:.3f} min_s {r['min_s']:.3f} "
              f"q_meas {r['q_meas']:.3f}")
        if not np.isfinite(r["E"]):
            print("  [abort] diverged")
            break
        if gn_last < 1e-6 * g0n or gn_last < 1e-9:
            break
        if hist["iter"][-1] < step:
            break
    decades = float(np.log10(g0n / (gn_last + 1e-300)))
    out = {"task": "M5.19", "phase": "D", "case": name, "seed": spec,
           "grid": {"NR": NR, "NZ": NZ, "h": H}, "wscale": WSCALE,
           "iters_run": done, "gnorm_decades": decades,
           "E_first_last": [traj[0]["E"], traj[-1]["E"]],
           "q_meas_first_last": [traj[0]["q_meas"], traj[-1]["q_meas"]],
           "trajectory": traj, "wall_s": round(time.time() - t0, 1)}
    with open(os.path.join(DATA, f"m5_19_d1_{name}.json"), "w") as f:
        json.dump(out, f, indent=1)
    np.savez_compressed(os.path.join(DATA, f"m5_19_d1_{name}_state.npz"),
                        M0=Mx.astype(np.float32))
    print(f"[{name}] done: E {traj[0]['E']:.3f} -> {traj[-1]['E']:.3f}, "
          f"{decades:.1f} gnorm decades, ring13 rho -> "
          f"{traj[-1]['ring13_rho']:.1f}, q_meas -> {traj[-1]['q_meas']:.3f}, "
          f"wall {out['wall_s']}s")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "all"
    iters = int(ARGV[-1]) if ARGV and ARGV[-1].isdigit() else 8000
    if mode == "single":
        run_case(ARGV[1], iters)
    else:
        for c in CASES:
            run_case(c, iters)
