"""M5.12 phase A extension: the sigma-model quadratic kinetic term PILOT
(the Q13-redirect "Lorentz-invariant Skyrme-like" class, first candidate).

⚠️ SCAFFOLDING GRADE: this pilot tests whether the term CAN hold the
rotated vortex loop; it is NOT a calibrated-instrument result. Any headline
use of a sigma term requires the full M5.16 gate-suite re-run + Coulomb/m_e
recalibration (the calibrated-instrument rule): the term changes the
far-field economics (hedgehog density gains a sigma/r^2 tail, IR-relevant)
and the Derrick balance (the quadratic + quartic pair is EXACTLY the
classic Skyrme stabilization; M5's quartic-only statics lack it).

THE TERM (statics, spatial channels of the equivariant reduction):
    E_sigma = sigma . SUM_cells w ( ||A_rho||^2 + ||A_phi||^2 + ||A_z||^2 ),
    A_rho, A_z = central differences, A_phi = [J, M]/rho  (the same three
    channels as the quartic curvature; Lorentz completion via eta once time
    enters, trivially invariant for statics).
    Gradient: dE/dA_x = 2 sigma w A_x, scattered through the SAME adjoints
    as m5_17_energy.energy_gradient_np (central-diff scatter, mirror-ghost
    fold-back, -[J, G]/rho azimuthal adjoint). FD-gated here (gate SG1).

    sigma is set as a FRACTION of the seed's quartic curvature energy:
    sigma = frac . E_curv(seed) / E_sigma,1(seed), frac in {0.1, 0.3, 1.0}
    (placeholder scale, labeled; the physical coefficient is the actual
    Q13-residual measurement, later).

WHY (2026-07-07 D0 verdict, m5_12_d0_pair_anti.json): constraint-only core
regularization does NOT stabilize (isotropic aI cores are free unwinding
surfaces; director-pinned cores annihilate through melt bridges): the
pre-registered branch moves the Skyrme-like-term measurement up. Note the
M5.8 N-5 dynamic caution: a Skyrme-family QUARTIC damped the clock 10x;
the quadratic sigma term is a DIFFERENT member, and this pilot is statics.

Run:  python m5_12_sigma.py gate
      python m5_12_sigma.py pilot [R0] [q] [iters]
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
sys.argv = sys.argv[:1]

from m5_17_energy import (MIR, J4, _comm_np, _norm2_np, cell_weights,     # noqa: E402
                          grid_coords)
from m5_16_axisym import fire_relax, pin_mask                             # noqa: E402
from m5_18_spectral import (energy_gradient_spec_np,                      # noqa: E402
                            total_energy_spec_np)
from m5_12_core_pin import load_wscale                                    # noqa: E402
from m5_12_loop import classify, loop_field, ring_readout                 # noqa: E402


def _channels(Mnp, h):
    nr, nz = Mnp.shape[:2]
    Mminus = np.empty_like(Mnp[: nr - 1])
    Mminus[1:] = Mnp[: nr - 2]
    Mminus[0] = MIR * Mnp[0]
    Arho = (Mnp[1:] - Mminus)[:, 1:-1] / (2.0 * h)
    Az = (Mnp[: nr - 1, 2:] - Mnp[: nr - 1, :-2]) / (2.0 * h)
    Mc = Mnp[: nr - 1, 1:-1]
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Aphi = _comm_np(np.broadcast_to(J4, Mc.shape), Mc) / rho
    return Arho, Aphi, Az, rho


def sigma_density_np(Mnp, h, sigma=1.0):
    Arho, Aphi, Az, _ = _channels(Mnp, h)
    return sigma * (_norm2_np(Arho) + _norm2_np(Aphi) + _norm2_np(Az))


def sigma_gradient_np(Mnp, h, sigma):
    """analytic adjoints, mirroring energy_gradient_np's scatter exactly."""
    nr, nz = Mnp.shape[:2]
    inv2h = 1.0 / (2.0 * h)
    Arho, Aphi, Az, rho = _channels(Mnp, h)
    w = cell_weights(nr, nz, h)[..., None, None]
    Grho = 2.0 * sigma * w * Arho
    Gphi = 2.0 * sigma * w * Aphi
    Gz = 2.0 * sigma * w * Az
    G = np.zeros_like(Mnp)
    G[1:, 1:-1] += Grho * inv2h
    G[: nr - 2, 1:-1] -= Grho[1:] * inv2h
    G[0, 1:-1] -= (MIR * Grho[0]) * inv2h
    G[: nr - 1, 2:] += Gz * inv2h
    G[: nr - 1, :-2] -= Gz * inv2h
    Gphi_r = Gphi / rho
    G[: nr - 1, 1:-1] += -_comm_np(np.broadcast_to(J4, Gphi_r.shape), Gphi_r)
    return G


def e_total(Mnp, wscale, h, sigma):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return (total_energy_spec_np(Mnp, wscale, h)
            + float(np.sum(sigma_density_np(Mnp, h, sigma) * w)))


def g_total(Mnp, wscale, h, sigma):
    return (energy_gradient_spec_np(Mnp, wscale, h)
            + sigma_gradient_np(Mnp, h, sigma))


def run_gate(nr=48, nz=96, h=1.0):
    from m5_17_energy import hedgehog_field
    R, Z = grid_coords(nr, nz, h)
    M0 = hedgehog_field(R, Z, 6.0)
    sigma = 0.21
    G = sigma_gradient_np(M0, h, sigma)
    rng = np.random.default_rng(7)
    eps, worst = 1e-6, 0.0
    w = cell_weights(nr, nz, h)

    def E(MM):
        return float(np.sum(sigma_density_np(MM, h, sigma) * w))

    for _ in range(6):
        Dc = rng.normal(size=(nr - 1, nz - 2, 4, 4))
        D = np.zeros_like(M0)
        D[: nr - 1, 1:-1] = 0.5 * (Dc + np.swapaxes(Dc, -1, -2))
        num = (E(M0 + eps * D) - E(M0 - eps * D)) / (2 * eps)
        an = float(np.sum(G * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-12))
    ok = worst < 1e-6
    print(f"[{'PASS' if ok else 'FAIL'}] SG1 sigma-term gradient (analytic == FD): {worst:.3e}")
    out = {"SG1_gradcheck_max_rel": worst, "all_pass": bool(ok)}
    with open(os.path.join(DATA, "m5_12_sigma_gate.json"), "w") as f:
        json.dump(out, f, indent=1)
    return ok


def run_pilot(R0=12.0, q=0.5, nr=96, nz=192, h=1.0, iters=6000, rc=4.0,
              fracs=(0.1, 0.3, 1.0), log_every=500):
    wscale = load_wscale()
    R, Z = grid_coords(nr, nz, h)
    w = cell_weights(nr, nz, h)
    rows = []
    for frac in fracs:
        M0 = loop_field(R, Z, R0, q, rc)
        from m5_17_energy import curvature_density_np
        Ec = float(np.sum(curvature_density_np(M0, h, 1.0) * w))
        Es1 = float(np.sum(sigma_density_np(M0, h, 1.0) * w))
        sigma = frac * Ec / Es1
        pin = pin_mask(nr, nz)
        free4 = (~pin)[..., None, None].astype(float)
        wfull = np.ones((nr, nz))
        wfull[: nr - 1, 1:-1] = w
        precond = (1.0 / wfull)[..., None, None]

        def egf(MM):
            return (e_total(MM, wscale, h, sigma),
                    g_total(MM, wscale, h, sigma))

        traj = [dict(ring_readout(M0, nr, nz, h), it=0,
                     E=e_total(M0, wscale, h, sigma))]
        t0 = time.time()
        Mx, done, g0n = M0, 0, None
        gn_last = None
        while done < iters:
            step = min(log_every, iters - done)
            Mx, hist = fire_relax(Mx, egf, free4, precond, max_iter=step,
                                  tol_rel=1e-6, dt0=0.005, dt_max=0.05,
                                  log_every=step)
            if g0n is None:
                g0n = hist["gnorm"][0]
            gn_last = hist["gnorm"][-1]
            done += hist["iter"][-1]
            traj.append(dict(ring_readout(Mx, nr, nz, h), it=done,
                             E=hist["E"][-1]))
            if not np.isfinite(hist["E"][-1]) or not np.isfinite(traj[-1]["min_s"]):
                print(f"  [abort] diverged at it={done}")
                break
            if gn_last < 1e-6 * g0n or gn_last < 1e-9:
                break
            if hist["iter"][-1] < step:
                break
        verdict = classify(traj, nr, h)
        decades = float(np.log10(g0n / (gn_last + 1e-300)))
        rows.append({"frac": frac, "sigma": sigma,
                     "E_first_last": [traj[0]["E"], traj[-1]["E"]],
                     "ring_rho_first_last": [traj[0]["ring_rho"],
                                             traj[-1]["ring_rho"]],
                     "min_s_end": traj[-1]["min_s"],
                     "gnorm_decades": decades, "iters_run": done,
                     "verdict": verdict, "trajectory": traj,
                     "wall_s": round(time.time() - t0, 1)})
        r = rows[-1]
        print(f"[sigma-pilot frac={frac:g} sigma={sigma:.4g}] "
              f"E {r['E_first_last'][0]:.2f} -> {r['E_first_last'][1]:.2f} "
              f"ring {r['ring_rho_first_last'][0]:.1f} -> "
              f"{r['ring_rho_first_last'][1]:.1f} min_s={r['min_s_end']:.3f} "
              f"decades={decades:.1f} VERDICT={verdict} wall={r['wall_s']}s")
    out = {"task": "M5.12", "script": "m5_12_sigma.py", "mode": "pilot",
           "grade": "SCAFFOLDING (placeholder sigma; calibrated-instrument"
                    " rule applies before any headline)",
           "seed": {"R0": R0, "q": q, "core": "melt", "rc": rc},
           "grid": {"NR": nr, "NZ": nz, "h": h}, "wscale": wscale,
           "rows": rows}
    path = os.path.join(DATA, f"m5_12_sigma_pilot_R{int(R0)}_q{str(q).replace('.', 'p')}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {path}")
    return out


def _relax_chunked(M0, egf, free4, precond, iters, nr, nz, h, log_every=1000):
    traj = [dict(ring_readout(M0, nr, nz, h), it=0, E=egf(M0)[0])]
    Mx, done, g0n, gn_last = M0, 0, None, None
    while done < iters:
        step = min(log_every, iters - done)
        Mx, hist = fire_relax(Mx, egf, free4, precond, max_iter=step,
                              tol_rel=1e-7, dt0=0.005, dt_max=0.05,
                              log_every=step)
        if g0n is None:
            g0n = hist["gnorm"][0]
        gn_last = hist["gnorm"][-1]
        done += hist["iter"][-1]
        traj.append(dict(ring_readout(Mx, nr, nz, h), it=done,
                         E=hist["E"][-1]))
        if not np.isfinite(hist["E"][-1]) or not np.isfinite(traj[-1]["min_s"]):
            break
        if gn_last < 1e-7 * g0n or gn_last < 1e-9:
            break
        if hist["iter"][-1] < step:
            break
    decades = float(np.log10(g0n / (gn_last + 1e-300)))
    return Mx, traj, decades, done


def run_extend(frac=1.0, R0=12.0, q=0.5, nr=96, nz=192, h=1.0, iters=20000,
               rc=4.0):
    """the discriminator: long relax of one sigma arm + a matched no-loop
    CONTROL (same pinned boundary, combed n=z interior). E_localized =
    E_end(loop) - E_end(control); a stationary localized object needs
    E_localized >> 0 with gnorm decades >= 5-6 and the ring holding."""
    from m5_17_energy import curvature_density_np
    wscale = load_wscale()
    R, Z = grid_coords(nr, nz, h)
    w = cell_weights(nr, nz, h)
    M0 = loop_field(R, Z, R0, q, rc)
    Ec = float(np.sum(curvature_density_np(M0, h, 1.0) * w))
    Es1 = float(np.sum(sigma_density_np(M0, h, 1.0) * w))
    sigma = frac * Ec / Es1
    pin = pin_mask(nr, nz)
    free4 = (~pin)[..., None, None].astype(float)
    wfull = np.ones((nr, nz))
    wfull[: nr - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    def egf(MM):
        return (e_total(MM, wscale, h, sigma),
                g_total(MM, wscale, h, sigma))

    t0 = time.time()
    Mf, traj, decades, done = _relax_chunked(M0, egf, free4, precond, iters,
                                             nr, nz, h)
    # control: same boundary ring (pinned cells keep loop-seed values),
    # interior combed to the n = z vacuum
    Mc0 = np.zeros_like(M0)
    Mc0[..., 3, 3] = 1.0
    Mc0[..., 0, 0] = M0[..., 0, 0]
    Mc0 = np.where(pin[..., None, None], M0, Mc0)
    Mcf, traj_c, decades_c, done_c = _relax_chunked(Mc0, egf, free4, precond,
                                                    min(iters, 8000), nr, nz, h)
    E_end, E_ctl = traj[-1]["E"], traj_c[-1]["E"]
    # energy-localization readout: density inside the ring neighborhood
    dens = (curvature_density_np(Mf, h, 1.0)
            + sigma_density_np(Mf, h, sigma)) * w
    RHO = ((np.arange(nr - 1) + 0.5) * h)[:, None]
    ZZ = ((np.arange(1, nz - 1) - nz / 2 + 0.5) * h)[None, :]
    rr = traj[-1]["ring_rho"]
    near = np.sqrt((RHO - rr) ** 2 + ZZ ** 2) < 8.0
    E_near = float(np.sum(dens[near]))
    out = {"task": "M5.12", "script": "m5_12_sigma.py", "mode": "extend",
           "grade": "SCAFFOLDING (placeholder sigma)",
           "seed": {"R0": R0, "q": q, "rc": rc}, "frac": frac, "sigma": sigma,
           "iters": done, "gnorm_decades": decades,
           "trajectory_tail": traj[-6:],
           "E_end": E_end, "E_control": E_ctl,
           "E_localized": E_end - E_ctl,
           "E_near_ring_8cells": E_near,
           "control": {"iters": done_c, "decades": decades_c,
                       "trajectory_tail": traj_c[-3:]},
           "wall_s": round(time.time() - t0, 1)}
    np.savez_compressed(
        os.path.join(DATA, f"m5_12_sigma_extend_f{frac:g}_state.npz"),
        Msp_final=Mf[: nr - 1, 1:-1, 1:4, 1:4].astype(np.float32),
        Msp_control=Mcf[: nr - 1, 1:-1, 1:4, 1:4].astype(np.float32))
    path = os.path.join(DATA, f"m5_12_sigma_extend_f{frac:g}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[sigma-extend frac={frac:g}] E_end={E_end:.2f} E_ctl={E_ctl:.2f} "
          f"E_loc={E_end - E_ctl:.2f} E_near={E_near:.2f} "
          f"ring={traj[-1]['ring_rho']:.1f} min_s={traj[-1]['min_s']:.3f} "
          f"decades={decades:.1f}/{decades_c:.1f} wall={out['wall_s']}s")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gate"
    if mode == "gate":
        run_gate()
    elif mode == "pilot":
        R0 = float(ARGV[1]) if len(ARGV) > 1 else 12.0
        q = float(ARGV[2]) if len(ARGV) > 2 else 0.5
        iters = int(ARGV[3]) if len(ARGV) > 3 else 6000
        run_pilot(R0, q, iters=iters)
    elif mode == "extend":
        frac = float(ARGV[1]) if len(ARGV) > 1 else 1.0
        iters = int(ARGV[2]) if len(ARGV) > 2 else 20000
        run_extend(frac=frac, iters=iters)
    else:
        print(f"unknown mode {mode}")
