"""M5.20.3 phase C: production = the ANATOMY of the true-L blowup.

DEVIATION FROM THE PRE-REGISTERED PLAN (logged in the task_details): the
pre-registered oscillation production (T = 2000, radius breathing, gap
ladder) is NO-GO: phase B measured a finite-time blowup of the free-EL
dynamics on EVERY background at EVERY null-regularization strength
(dt-robust at fixed cutoff, monotone in cutoff, no plateau; the
unregularized system blows in a fixed STEP COUNT = unbounded RHS =
ill-posed IVP). What production means here: fully-instrumented,
documented runs of the regularized dynamics up to t*, delivering the
trajectory anatomy (E/KE/PE, the projection leak, sector amplitudes,
winding + ring + core reads) and the seed/last-finite-endpoint states
for the M5.20-series cross-section maps.

Runs (64x128, dt = 0.00125 converged per B1, snapshots every 0.02):
    recipe_rc1e-2    the his-recipe seed (3D-minimized-while-loop-intact,
                     q = 0.500, + g time row), rel_cut 1e-2   [PRIMARY]
    recipe_rc1e-1    same seed, heaviest regularization (longest-lived,
                     t* ~ 7.2: the most evolution visible)
    raw_rc1e-2       the bare ansatz loop seed
    remnant_rc1e-2   the unwound remnant (NO winding: control: the blowup
                     does not need the defect)

Run:  python m5_20_3_c_production.py <tag>      (one run)
      python m5_20_3_c_production.py all
Out:  ../data/m5_20_3_c_<tag>.json + _seed/_end .npz
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_20_1_b_seeds import core_spectrum, winding_measure_biax    # noqa: E402
from m5_20_2_a_eom import WSCALE                                   # noqa: E402
from m5_20_3_a_constraint import evolve_true, seed4_grid           # noqa: E402
from m5_20_3_b_triage import DELTA, NR, NZ, H, R0, tstar_of        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

RUNS = {
    "recipe_rc1e-2": {"seed": "recipe", "rel_cut": 1e-2, "T": 3.0},
    "recipe_rc1e-1": {"seed": "recipe", "rel_cut": 1e-1, "T": 10.0},
    "raw_rc1e-2": {"seed": "raw", "rel_cut": 1e-2, "T": 4.0},
    "remnant_rc1e-2": {"seed": "remnant", "rel_cut": 1e-2, "T": 3.0},
}
DT = 0.00125


def get_seed(kind):
    if kind == "raw":
        return seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    fn = {"recipe": "m5_20_3_b_seed_recipe.npz",
          "remnant": "m5_20_3_b_seed_remnant.npz"}[kind]
    return np.load(os.path.join(DATA, fn))["M"]


def snap_fn_of(M0):
    def fn(Mx, v):
        dM = Mx - M0
        rd = ring_by_m13(Mx, NR, NZ, H)
        rho_c, z_c = rd["ring13_rho"], rd["ring13_z"]
        qs = {}
        for rw in (3.0, 4.0, 5.0):
            qm, mix = winding_measure_biax(Mx, NR, NZ, H, rho_c, z_c,
                                           r_w=rw)
            qs[f"q_r{rw:.0f}"] = None if not np.isfinite(qm) else float(qm)
        cs = core_spectrum(Mx, NR, NZ, H, rho_c, z_c)
        return {"ring_rho": float(rho_c), "ring_z": float(z_c), **qs,
                "core_lam": cs["lam"],
                "sec_time_diag": float(np.max(np.abs(dM[..., 0, 0]))),
                "sec_time_mix": float(np.max(np.abs(dM[..., 0, 1:]))),
                "sec_sp_diag": float(max(np.max(np.abs(dM[..., i, i]))
                                         for i in (1, 2, 3))),
                "sec_sp_off": float(max(np.max(np.abs(dM[..., i, j])) for
                                        (i, j) in ((1, 2), (1, 3), (2, 3)))),
                "max_v": float(np.max(np.abs(v)))}
    return fn


def run_one(tag):
    cfg = RUNS[tag]
    M0 = get_seed(cfg["seed"])
    np.savez_compressed(os.path.join(DATA, f"m5_20_3_c_{tag}_seed.npz"),
                        M=M0)
    last_fin = {"M": M0.copy()}

    base_snap = snap_fn_of(M0)

    def snap_fn(Mx, v):
        if np.all(np.isfinite(Mx)) and float(np.max(np.abs(Mx))) < 1e6:
            last_fin["M"] = Mx.copy()
        return base_snap(Mx, v)

    Mx, v, recs, wall = evolve_true(M0, None, cfg["T"], DT, WSCALE, DELTA,
                                    rel_cut=cfg["rel_cut"],
                                    snap_every=max(1, int(0.02 / DT)),
                                    snap_fn=snap_fn)
    ts = tstar_of(recs)
    np.savez_compressed(os.path.join(DATA, f"m5_20_3_c_{tag}_end.npz"),
                        M=last_fin["M"])
    out = {"tag": tag, **cfg, "dt": DT, "tstar": ts,
           "wall_s": round(wall, 1), "trajectory": recs}
    with open(os.path.join(DATA, f"m5_20_3_c_{tag}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    fin = [r for r in recs if np.isfinite(r.get("E_tot", np.nan))]
    print(f"[{tag}] t*={ts} snaps={len(fin)} "
          f"q_r4 {fin[0].get('q_r4')}->{fin[-1].get('q_r4')} "
          f"E {fin[0]['E_tot']:.4f}->{fin[-1]['E_tot']:.4f} "
          f"wall {wall:.0f}s", flush=True)
    return out


def film_one(tag, n_snap=None):
    """re-run the pre-singular window with frame capture and render the
    basic-template film strip per the 2026-07-14 standard
    (research/m5_visualization.md): first row t = 0, N_SNAP frames,
    steps + tu titles."""
    import m5_film
    from collections import deque
    n_snap = n_snap or 7
    n_takeoff = 3
    n_quiet = n_snap - 1 - n_takeoff
    cfg = RUNS[tag]
    with open(os.path.join(DATA, f"m5_20_3_c_{tag}.json")) as f:
        ts_known = json.load(f)["tstar"]
    # BLOWUP SPACING (m5_visualization.md): row 0 = seed; n_quiet rows
    # evenly over the quiet window; n_takeoff rows log-spaced in time-to-
    # singularity (dyadic offsets {4, 2, 0} fine intervals before the
    # last finite state): the takeoff is a measured exponential, so equal
    # log(t* - t) steps = equal amplitude-growth ratios per row
    t_quiet = max(ts_known - 0.08, 5 * DT)
    frame_dt = t_quiet / n_quiet
    snap_every = max(1, int(round(frame_dt / DT)))
    M0 = get_seed(cfg["seed"])
    frames = [{"it": 0, "t": 0.0, "M": M0.copy()}]

    def snap_fn(Mx, v):
        it = len(frames) * snap_every
        if len(frames) < 1 + n_quiet:
            frames.append({"it": it, "t": it * DT, "M": Mx.copy()})
        return {}

    from m5_20_3_a_constraint import evolve_true as ev
    ev(M0, None, snap_every * n_quiet * DT, DT, WSCALE, DELTA,
       rel_cut=cfg["rel_cut"], snap_every=snap_every, snap_fn=snap_fn)

    # one fine-grid pass from t = 0 to the blowup (restarting mid-way
    # with V = 0 would change the trajectory); keep a ring buffer of
    # recent finite states and pick the dyadic tail from it
    fine_every = max(1, int(round(0.005 / DT)))
    ring = deque(maxlen=8)
    step = {"k": 0}

    def snap_takeoff(Mx, v):
        step["k"] += 1
        if np.all(np.isfinite(Mx)) and float(np.max(np.abs(Mx))) < 1e6:
            ring.append((step["k"] * fine_every, Mx.copy()))
        return {}

    ev(M0, None, ts_known + 0.1, DT, WSCALE, DELTA,
       rel_cut=cfg["rel_cut"], snap_every=fine_every,
       snap_fn=snap_takeoff)
    picks = [max(len(ring) - 1 - off, 0) for off in (2, 1, 0)]
    seen = set()
    for idx in picks:
        if idx in seen:
            continue
        seen.add(idx)
        it_f, Mf = ring[idx]
        frames.append({"it": it_f, "t": it_f * DT, "M": Mf})
    short = tag.split("_")[0]
    path = os.path.join(HERE, "..", "plots", f"m5_20_3_film_{short}.png")
    m5_film.film_strip(
        frames[:n_snap], path, template="basic", delta=DELTA,
        suptitle=f"M5.20.3 {tag}: the pre-singular window "
                 f"(t* = {ts_known:g}), basic template")
    return path


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "all"
    if which == "film":
        for tg in (ARGV[1:] or ["recipe_rc1e-2", "raw_rc1e-2"]):
            film_one(tg)
    else:
        tags = list(RUNS) if which == "all" else [which]
        for tg in tags:
            run_one(tg)
