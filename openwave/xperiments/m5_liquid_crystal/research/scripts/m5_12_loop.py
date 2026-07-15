"""M5.12 phase A: the rotated vortex loop (Duda's directive seed) on the
calibrated axisymmetric instrument.

THE SEED (Duda 2026-07-03, m5_4h: "the starting point of energy minimization
is topological vortex rotated cylindrically to make it loop"): in the exact
equivariant (rho, z) reduction (m5_16_axisym), a vortex at the half-plane
point (rho = R0, z = 0) swept around the z axis IS that object: the loop's
cylindrical symmetry is the reduction's symmetry, so phase A runs on the
SAME calibrated stack as the electron sector (M5.16 gates inherited).

    Director in the meridional frame (s_hat, z_hat), uniaxial (delta = 0,
    Duda: "can use delta=0 for uniaxial approximation without QM"):
        chi(rho, z) = atan2(z, rho - R0)          (angle around the core)
        q = 1/2 :  n = ( cos(chi/2),  sin(chi/2) )   [nematic, n ~ -n]
        q = 1   :  n = ( sin(chi),    cos(chi)   )
    Both phases put n parallel to z_hat ON the axis (the (1/rho)[J, M]
    channel needs [J, M] -> 0 there); a rho-blend additionally suppresses
    the residual near-axis s_hat component of the q = 1/2 seed at z != 0.
    The winding class q is the Q16 residual: BOTH are run.

    Core: melt profile s(d) = 1 - exp(-(d/rc)^2) around the ring core
    (mode melt) or the D0 prescription a*I disk, a golden-optimized, core
    frozen (mode corepin) per the phase-D0 verdict.

GATE (pre-registered, m5_12_task_details.md Card 6 phase A): the loop is
STATIONARY (gnorm falls >= 5-6 decades), FINITE (ring radius off the box
edge AND off zero), retention + localization both green. The M5.11 verdict
classifier applies: collapsed / dissolved / stable / drifting.

Run:  python m5_12_loop.py scan [--q 0.5] [--core melt|corepin]
      python m5_12_loop.py single R0 [q] [core] [iters]
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

# m5_16_axisym parses sys.argv positionals as ints AT IMPORT: capture our
# args, then strip argv so the import chain sees none.
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import G_TIME, cell_weights, grid_coords               # noqa: E402
from m5_16_axisym import fire_relax, pin_mask                            # noqa: E402
from m5_18_spectral import (energy_gradient_spec_np,                     # noqa: E402
                            potential_density_spec_np, total_energy_spec_np)
from m5_12_core_pin import (apply_core, core_masks_rz, golden_a,         # noqa: E402
                            load_wscale)


def loop_field(R, Z, R0, q=0.5, rc=4.0, g_time=G_TIME, axis_blend=3.0):
    """rotated-vortex-loop seed: winding q around the ring core (R0, 0),
    melt-regularized, n -> z_hat on the axis."""
    chi = np.arctan2(Z, R - R0)
    if abs(q - 0.5) < 1e-12:
        n1, n3 = np.cos(0.5 * chi), np.sin(0.5 * chi)
    else:
        n1, n3 = np.sin(q * chi), np.cos(q * chi)
    # suppress the residual near-axis s_hat component, renormalize
    blend = 1.0 - np.exp(-((R / axis_blend) ** 2))
    n1 = n1 * blend
    norm = np.sqrt(n1 ** 2 + n3 ** 2)
    norm = np.where(norm < 1e-12, 1.0, norm)
    n1, n3 = n1 / norm, n3 / norm
    d = np.sqrt((R - R0) ** 2 + Z ** 2)
    s = 1.0 - np.exp(-((d / rc) ** 2))
    Mnp = np.zeros(R.shape + (4, 4))
    Mnp[..., 1, 1] = s * n1 * n1
    Mnp[..., 1, 3] = s * n1 * n3
    Mnp[..., 3, 1] = s * n1 * n3
    Mnp[..., 3, 3] = s * n3 * n3
    Mnp[..., 0, 0] = g_time
    return Mnp


def ring_readout(Mnp, nr, nz, h):
    """melt-ring location: (rho, z) of the min largest-eigenvalue cell,
    plus min value (the loop-size observable). NaN-guarded (a diverged
    field returns min_s = nan and the caller aborts)."""
    msp = Mnp[: nr - 1, 1:-1, 1:4, 1:4]
    if not np.all(np.isfinite(msp)):
        return {"ring_rho": float("nan"), "ring_z": float("nan"),
                "min_s": float("nan")}
    s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    k = np.unravel_index(np.argmin(s_cell), s_cell.shape)
    return {"ring_rho": float((k[0] + 0.5) * h),
            "ring_z": float((k[1] - (nz - 2) / 2 + 0.5) * h),
            "min_s": float(np.min(s_cell))}


def classify(traj, nr, h):
    """the M5.11 honest verdict classifier on the ring-radius trajectory."""
    r_end = traj[-1]["ring_rho"]
    s_end = traj[-1]["min_s"]
    if not np.isfinite(s_end):
        return "diverged"
    if s_end > 0.7:
        return "dissolved"           # melt healed, no loop left
    if r_end <= 1.5 * h:
        return "collapsed"
    if r_end >= (nr - 6) * h:
        return "expanded_to_box"
    r_mid = traj[len(traj) // 2]["ring_rho"]
    return "stable" if abs(r_end - r_mid) <= 1.0 * h else "drifting"


def run_single(R0, q=0.5, core="melt", nr=96, nz=192, h=1.0, iters=8000,
               rc=4.0, r_pin=2.5, log_every=500):
    wscale = load_wscale()
    R, Z = grid_coords(nr, nz, h)
    M0 = loop_field(R, Z, R0, q, rc)
    a_star = None
    if core == "corepin":
        cmask = core_masks_rz(R, Z, [(R0, 0.0)], r_pin)
        a_star = golden_a(lambda aa: total_energy_spec_np(
            apply_core(M0, cmask, aa), wscale, h))
        M0 = apply_core(M0, cmask, a_star)
        pin = pin_mask(nr, nz) | cmask
    else:
        pin = pin_mask(nr, nz)
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(nr, nz, h)
    wfull = np.ones((nr, nz))
    wfull[: nr - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    traj = [dict(ring_readout(M0, nr, nz, h), it=0,
                 E=total_energy_spec_np(M0, wscale, h))]

    def egf(MM):
        return (total_energy_spec_np(MM, wscale, h),
                energy_gradient_spec_np(MM, wscale, h))

    # chunked FIRE so the ring trajectory is recorded
    t0 = time.time()
    Mx = M0
    hist_all = {"E": [], "gnorm": [], "iter": []}
    done = 0
    g0n = None
    while done < iters:
        step = min(log_every, iters - done)
        Mx, hist = fire_relax(Mx, egf, free4, precond, max_iter=step,
                              tol_rel=1e-6, dt0=0.005, dt_max=0.05,
                              log_every=step)
        if g0n is None:
            g0n = hist["gnorm"][0]
        done += hist["iter"][-1]
        hist_all["E"].append(hist["E"][-1])
        hist_all["gnorm"].append(hist["gnorm"][-1])
        hist_all["iter"].append(done)
        traj.append(dict(ring_readout(Mx, nr, nz, h), it=done,
                         E=hist["E"][-1]))
        if not np.isfinite(hist["E"][-1]) or not np.isfinite(traj[-1]["min_s"]):
            print(f"  [abort] field diverged at it={done}")
            break
        if hist["gnorm"][-1] < 1e-6 * g0n or hist["gnorm"][-1] < 1e-9:
            break
        if hist["iter"][-1] < step:      # fire_relax converged internally
            break
    verdict = classify(traj, nr, h)
    decades = float(np.log10(g0n / (hist_all["gnorm"][-1] + 1e-300)))
    out = {
        "task": "M5.12", "script": "m5_12_loop.py", "mode": "single",
        "seed": {"R0": R0, "q": q, "core": core, "rc": rc,
                 "a_star": a_star, "r_pin": r_pin if core == "corepin" else None},
        "grid": {"NR": nr, "NZ": nz, "h": h}, "wscale": wscale,
        "iters_run": done, "gnorm_decades": decades,
        "E_first_last": [traj[0]["E"], traj[-1]["E"]],
        "trajectory": traj,
        "verdict": verdict,
        "wall_s": round(time.time() - t0, 1),
    }
    tag = f"R{int(R0)}_q{str(q).replace('.', 'p')}_{core}"
    path = os.path.join(DATA, f"m5_12_loop_{tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[loop {tag}] E {traj[0]['E']:.3f} -> {traj[-1]['E']:.3f} "
          f"ring rho {traj[0]['ring_rho']:.1f} -> {traj[-1]['ring_rho']:.1f} "
          f"min_s={traj[-1]['min_s']:.3f} decades={decades:.1f} "
          f"VERDICT={verdict} wall={out['wall_s']}s")
    return out


def run_scan(qs=(0.5, 1.0), R0s=(8.0, 12.0, 16.0), core="melt", iters=6000):
    rows = []
    for q in qs:
        for R0 in R0s:
            rows.append(run_single(R0, q, core, iters=iters))
    summary = [{"R0": r["seed"]["R0"], "q": r["seed"]["q"],
                "core": r["seed"]["core"], "verdict": r["verdict"],
                "ring_rho_end": r["trajectory"][-1]["ring_rho"],
                "min_s_end": r["trajectory"][-1]["min_s"],
                "gnorm_decades": r["gnorm_decades"],
                "E_end": r["E_first_last"][1]} for r in rows]
    out = {"task": "M5.12", "mode": "scan", "core": core, "rows": summary}
    path = os.path.join(DATA, f"m5_12_loop_scan_{core}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(summary, indent=1))
    print(f"json -> {path}")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "scan"
    if mode == "single":
        R0 = float(ARGV[1])
        q = float(ARGV[2]) if len(ARGV) > 2 else 0.5
        core = ARGV[3] if len(ARGV) > 3 else "melt"
        iters = int(ARGV[4]) if len(ARGV) > 4 else 8000
        run_single(R0, q, core, iters=iters)
    elif mode == "scan":
        core = "melt"
        if "--core" in ARGV:
            core = ARGV[ARGV.index("--core") + 1]
        run_scan(core=core)
    else:
        print(f"unknown mode {mode}")
