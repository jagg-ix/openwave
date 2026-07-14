"""M5.20.3 phase B: well-posedness triage of the free-EL (true-L) dynamics.

The phase-A instrument (m5_20_3_a_constraint.py, GC0a-e green) integrates
    4 w k_apply(M)[Mddot] = gradM_T - G_static - 4 w kdot
per cell with the spectral-cutoff null projection and the bookkept leak.

THE TRIAGE IS THE FINDING (first probes 2026-07-14): the loop background
diverges in FINITE TIME under the free EL, dt-robustly, at every null
regularization strength. (An early 4D-statics-dive reading was RETRACTED
at audit C8: FIRE step-size instability, see dive_4d_record.) This script
runs those discriminators as pre-registered gates:

    B1  dt-robustness of the blowup time t* at fixed cutoffs (1e-8, 1e-2):
        t*(dt) converged => genuine ODE blowup, not CFL
    B2  cutoff ladder t*(rel_cut) on the raw AND the recipe seed:
        plateau => a physical t*; monotone-no-plateau => no
        cutoff-independent free-EL evolution exists on this background
    B3  the recipe seed (HIS prescription): FIRE-relax the 3D spatial
        sector (time row FROZEN: the bounded sector), then add the g time
        row; also RECORD the 4D free-relax dive (controlled, chunked)
    B4  blowup channel identification: state at the last finite snapshot
        before t*: which component sector carries the divergence
        (time-mixing 0i vs spatial vs diagonal) and where (rho, z)
    B5  vacuum + texture injections (rotation / clock / boost4b): bounded
        over T = 400 or t* recorded (the M5.20.2 baseline comparison)

GO/NO-GO: GO for the pre-registered oscillation production requires the
loop background to integrate stably to T >> gap-ladder periods; a
finite-time blowup at every regularization = NO-GO, and the honest
deliverables become the ill-posedness card + the recipe-seed statics +
the vacuum-sector ladder, with his least-action BVP named as the successor.

Run:  python m5_20_3_b_triage.py b1|b2|b3|b4|verdict
      python m5_20_3_b_triage.py b5 rotation|clock|boost4b
Out:  ../data/m5_20_3_b_<gate>.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import fire_relax, pin_mask                      # noqa: E402
from m5_17_energy import cell_weights, grid_coords                 # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_20_1_b_seeds import core_spectrum, winding_measure_biax    # noqa: E402
from m5_20_2_a_eom import (G_T, WSCALE, grad_static_4,             # noqa: E402
                           hessian4_analytic, total_energy_4, vac4)
from m5_20_3_a_constraint import (build_k10, evolve_true,          # noqa: E402
                                  seed4_grid)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NR, NZ, H = 64, 128, 1.0
DELTA = 0.3
R0 = 17.0
W4 = cell_weights(NR, NZ, H)[..., None, None]
RHO4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]


def tstar_of(recs):
    blow = [r for r in recs if r.get("blowup")]
    return blow[0]["t"] if blow else None


def run_tstar(seed, T, dt, rel_cut, v0=None):
    _, _, recs, wall = evolve_true(seed, v0, T, dt, WSCALE, DELTA,
                                   rel_cut=rel_cut,
                                   snap_every=max(1, int(0.1 / dt)))
    return tstar_of(recs), recs, wall


# ---------------- B3: the recipe seed ----------------
def relax_spatial_frozen_time(M0, iters=3000, chunk=500):
    """FIRE on the static energy with the time row FROZEN (the bounded
    spatial sector; GB0: this is the audited 3-target problem + the p = 4
    addition). Returns (Mrel, history)."""
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = W4[..., 0, 0]
    precond = (1.0 / wfull)[..., None, None]

    def g_frozen(MM):
        G = grad_static_4(MM, WSCALE, DELTA, w4=W4, rho4=RHO4)
        G[..., 0, :] = 0.0
        G[..., :, 0] = 0.0
        return G

    egf = lambda MM: (total_energy_4(MM, WSCALE, DELTA), g_frozen(MM))  # noqa: E731
    Mx = M0.copy()
    hist = []
    done = 0
    while done < iters:
        Mx, h = fire_relax(Mx, egf, free4, precond, max_iter=chunk,
                           tol_rel=1e-9, dt0=0.005, dt_max=0.05,
                           log_every=chunk)
        done += h["iter"][-1]
        rd = ring_by_m13(Mx, NR, NZ, H)
        qm, mix = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                       rd["ring13_z"])
        cs = core_spectrum(Mx, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
        hist.append({"it": done, "E": h["E"][-1], "gnorm": h["gnorm"][-1],
                     "ring_rho": rd["ring13_rho"], "q": None
                     if not np.isfinite(qm) else float(qm),
                     "core_lam": cs["lam"]})
        print(f"  relax it {done}: E {h['E'][-1]:.4f} gnorm "
              f"{h['gnorm'][-1]:.2e} ring_rho {rd['ring13_rho']:.1f} "
              f"q {hist[-1]['q']}", flush=True)
        if h["iter"][-1] < chunk:
            break
    return Mx, hist


def dive_4d_record(M0, chunk=50, max_chunks=12, bar=-100.0):
    """controlled record of the 4D free-relax FIRE run (free time row).
    AUDIT C8 (2026-07-14): the dive this records is a FIRE STEP-SIZE
    INSTABILITY (adaptive dt crosses 2/sqrt(lam_max) ~ 0.0256 < dt_max
    0.05); monotone GD / L-BFGS / dt-capped FIRE stay BOUNDED from this
    seed: the indefiniteness-in-statics interpretation is RETRACTED."""
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = W4[..., 0, 0]
    precond = (1.0 / wfull)[..., None, None]
    g_fn = lambda MM: grad_static_4(MM, WSCALE, DELTA, w4=W4, rho4=RHO4)  # noqa: E731
    egf = lambda MM: (total_energy_4(MM, WSCALE, DELTA), g_fn(MM))       # noqa: E731
    Mx = M0.copy()
    Es = [float(total_energy_4(Mx, WSCALE, DELTA))]
    maxm = [float(np.max(np.abs(Mx)))]
    with np.errstate(all="ignore"):
        for k in range(max_chunks):
            Mx, h = fire_relax(Mx, egf, free4, precond, max_iter=chunk,
                               tol_rel=1e-12, dt0=0.005, dt_max=0.05,
                               log_every=chunk)
            E = h["E"][-1]
            Es.append(float(E))
            maxm.append(float(np.max(np.abs(Mx))))
            print(f"  dive it {(k + 1) * chunk}: E {E:.4e} "
                  f"max|M| {maxm[-1]:.3e}", flush=True)
            if not np.isfinite(E) or E < bar:
                break
    dived = bool((not np.isfinite(Es[-1])) or Es[-1] < bar)
    return {"dived": dived, "E_per_chunk": Es, "maxM_per_chunk": maxm,
            "chunk": chunk}


def b3():
    M0 = seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    print(" [B3] recipe seed: frozen-time-row FIRE relax", flush=True)
    Mrec, hist_r = relax_spatial_frozen_time(M0, iters=500, chunk=500)
    np.savez_compressed(os.path.join(DATA, "m5_20_3_b_seed_recipe.npz"),
                        M=Mrec)
    Mrel, hist = relax_spatial_frozen_time(Mrec, iters=2500, chunk=500)
    hist = hist_r + hist
    np.savez_compressed(os.path.join(DATA, "m5_20_3_b_seed_remnant.npz"),
                        M=Mrel)
    print(" [B3] 4D free-relax dive record (controlled)", flush=True)
    dive = dive_4d_record(M0)
    out = {"relax_hist": hist, "dive_4d": dive,
           "seed_file": "m5_20_3_b_seed_recipe.npz",
           "E_raw": float(total_energy_4(M0, WSCALE, DELTA)),
           "E_recipe": float(total_energy_4(Mrel, WSCALE, DELTA))}
    print(f"[B3] recipe seed E {out['E_raw']:.4f} -> {out['E_recipe']:.4f}; "
          f"4D dive: {'DIVES' if dive['dived'] else 'bounded'}", flush=True)
    return out


def load_recipe_seed():
    p = os.path.join(DATA, "m5_20_3_b_seed_recipe.npz")
    if not os.path.exists(p):
        raise SystemExit("run b3 first (builds the recipe seed)")
    return np.load(p)["M"]


# ---------------- B1 / B2 ----------------
def b1():
    M0 = seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    out = {}
    for rc in (1e-8, 1e-2):
        row = {}
        for dt in (0.005, 0.0025, 0.00125):
            ts, _, wall = run_tstar(M0, 6.0, dt, rc)
            row[str(dt)] = ts
            print(f"  rc={rc:.0e} dt={dt}: t*={ts} ({wall:.0f}s)",
                  flush=True)
        vals = [v for v in row.values() if v is not None]
        conv = (len(vals) == 3
                and abs(vals[-1] - vals[-2]) < 0.25 * max(vals[-1], 1e-9))
        out[f"{rc:.0e}"] = {"tstar_per_dt": row,
                            "dt_robust": bool(conv)}
    ok = all(v["dt_robust"] for v in out.values())
    print(f"[B1] {'PASS' if ok else 'FAIL'} (dt-robust blowup at both "
          "cutoffs = genuine ODE property)", flush=True)
    return {"ok": bool(ok), "detail": out}


def b2():
    raw = seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    seeds = {"raw": raw, "recipe": load_recipe_seed()}
    p_rem = os.path.join(DATA, "m5_20_3_b_seed_remnant.npz")
    if os.path.exists(p_rem):
        seeds["remnant_unwound"] = np.load(p_rem)["M"]
    out = {}
    for stag, seed in seeds.items():
        row = {}
        for rc in (1e-8, 1e-3, 1e-2, 3e-2, 1e-1):
            ts, recs, wall = run_tstar(seed, 8.0, 0.0025, rc)
            fin = [r for r in recs if np.isfinite(r.get("E_tot", np.nan))]
            row[f"{rc:.0e}"] = {
                "tstar": ts,
                "n_active0": fin[0].get("n_active_mean") if fin else None,
                "nff0": fin[0].get("null_force_frac") if fin else None}
            print(f"  {stag} rc={rc:.0e}: t*={ts} ({wall:.0f}s)", flush=True)
        ts_seq = [v["tstar"] for v in row.values()]
        finite_all = all(t is not None for t in ts_seq)
        plateau = (finite_all
                   and abs(ts_seq[-1] - ts_seq[-2])
                   < 0.15 * max(ts_seq[-1], 1e-9))
        out[stag] = {"ladder": row, "all_blow_up": finite_all,
                     "plateau": bool(plateau)}
    for stag in out:
        print(f"[B2] {stag}: all_blow={out[stag]['all_blow_up']} "
              f"plateau={out[stag]['plateau']}", flush=True)
    return out


# ---------------- B4: channel identification ----------------
def b4(rel_cut=1e-2, dt=0.0025):
    M0 = seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    ts, _, _ = run_tstar(M0, 8.0, dt, rel_cut)
    T_pre = max(ts - 0.15, 0.05)
    Mx, v, recs, _ = evolve_true(M0, None, T_pre, dt, WSCALE, DELTA,
                                 rel_cut=rel_cut,
                                 snap_every=max(1, int(0.05 / dt)))
    dM = Mx - M0
    sect = {
        "time_diag_00": float(np.max(np.abs(dM[..., 0, 0]))),
        "time_mix_0i": float(np.max(np.abs(dM[..., 0, 1:]))),
        "spatial_diag": float(max(np.max(np.abs(dM[..., i, i]))
                                  for i in (1, 2, 3))),
        "spatial_offdiag": float(max(np.max(np.abs(dM[..., i, j]))
                                     for (i, j) in ((1, 2), (1, 3), (2, 3))))}
    amp = np.max(np.abs(dM), axis=(-2, -1))
    ij = np.unravel_index(np.argmax(amp), amp.shape)
    rho_b = (ij[0] + 0.5) * H
    z_b = (ij[1] - NZ / 2 + 0.5) * H
    dd_ring = float(np.hypot(rho_b - R0, z_b))
    vamp = np.max(np.abs(v), axis=(-2, -1))
    ijv = np.unravel_index(np.argmax(vamp), vamp.shape)
    out = {"rel_cut": rel_cut, "tstar": ts, "T_probe": T_pre,
           "sector_max_dM": sect,
           "blow_cell_rho_z": [float(rho_b), float(z_b)],
           "blow_cell_dist_to_ring": dd_ring,
           "v_max_cell": [int(ijv[0]), int(ijv[1])],
           "max_dM": float(amp.max()), "max_v": float(vamp.max())}
    print(f"[B4] t*={ts}; at t*-0.15: sector max|dM| {sect}; "
          f"hotspot (rho, z) = ({rho_b:.1f}, {z_b:.1f}), "
          f"{dd_ring:.1f} from the ring", flush=True)
    return out


# ---------------- B5: vacuum textures ----------------
def vac_field(delta=DELTA):
    M = np.zeros((NR, NZ, 4, 4))
    M[..., :, :] = vac4(delta)
    return M


def inject(M, sector, amp=0.02, center=(20.0, 0.0), sig=3.0):
    R, Z = grid_coords(NR, NZ, H)
    bump = amp * np.exp(-((R - center[0]) ** 2 + (Z - center[1]) ** 2)
                        / (2 * sig ** 2))
    out = M.copy()
    if sector == "rotation":
        out[..., 1, 2] += bump
        out[..., 2, 1] += bump
    elif sector == "clock":
        out[..., 0, 1] += bump
        out[..., 1, 0] += bump
    elif sector == "boost4b":
        out[..., 0, 1] += bump
        out[..., 1, 0] += bump
        out[..., 1, 2] += bump
        out[..., 2, 1] += bump
    else:
        raise ValueError(sector)
    return out


def probe_cell(center=(20.0, 0.0)):
    ci = int(round(center[0] / H - 0.5))
    cj = int(round(center[1] / H + (NZ - 2) / 2 - 0.5)) + 1
    return ci, cj


def b5(sector, T=400.0, dt=0.02, amp=0.02):
    ci, cj = probe_cell()

    def snap_fn(Mx, v):
        return {"a01": float(Mx[ci, cj, 0, 1]),
                "a12": float(Mx[ci, cj, 1, 2]),
                "maxabs_mix": float(np.max(np.abs(Mx[..., 0, 1:])))}

    M0 = inject(vac_field(), sector, amp=amp)
    Mx, v, recs, wall = evolve_true(M0, None, T, dt, WSCALE, DELTA,
                                    snap_every=max(1, int(0.5 / dt)),
                                    snap_fn=snap_fn)
    ts = tstar_of(recs)
    fin = [r for r in recs if np.isfinite(r.get("E_tot", np.nan))]
    out = {"sector": sector, "T": T, "dt": dt, "amp": amp, "tstar": ts,
           "wall_s": round(wall, 1)}
    if ts is None and len(fin) > 8:
        t = np.array([r["t"] for r in fin])
        ma = np.array([r["maxabs_mix"] for r in fin])
        a01 = np.array([r["a01"] for r in fin])
        half = len(ma) // 2
        out["envelope_growth_rate"] = float(
            np.polyfit(t[half:], np.log(np.maximum(ma[half:], 1e-30)), 1)[0])
        y = a01 - np.mean(a01)
        f = np.fft.rfftfreq(len(y), d=(t[1] - t[0]))
        aa = np.abs(np.fft.rfft(y * np.hanning(len(y))))
        out["omega_peak"] = float(f[1:][np.argmax(aa[1:])] * 2 * np.pi)
        out["omega_bin_width"] = float(2 * np.pi * (f[1] - f[0]))
        out["E_dev"] = float(np.max(np.abs(
            np.array([r["E_tot"] for r in fin]) - fin[0]["E_tot"]))
            / max(abs(fin[0]["E_tot"]), 1e-30))
        out["trajectory"] = fin
    print(f"  [B5 {sector}] t*={ts} " + (
        f"growth {out.get('envelope_growth_rate', 0):+.2e}/t omega_peak "
        f"{out.get('omega_peak', -1):.4f}" if ts is None else "(blowup)"),
        flush=True)
    with open(os.path.join(DATA, f"m5_20_3_b_b5_{sector}.json"), "w") as f2:
        json.dump(out, f2, indent=1, default=float)
    return out


def true_ladder_at_probe(delta=DELTA):
    """generalized eig(Hess_V, K10(rho)) at the probe cell (indicative)."""
    M = vac_field(delta)
    K10 = build_k10(M)
    ci, cj = probe_cell()
    Kc = K10[ci, cj - 1]
    Hv = hessian4_analytic(delta)
    lam, U = np.linalg.eigh(Kc)
    keep = np.abs(lam) > 1e-10 * np.abs(lam).max()
    Ur = U[:, keep]
    from scipy.linalg import eig
    w2 = np.real(eig(Ur.T @ Hv @ Ur, np.diag(lam[keep]))[0])
    return {"omega2_all": sorted(float(x) for x in w2),
            "omega_pos": sorted(float(np.sqrt(x)) for x in w2 if x > 1e-12),
            "n_neg_omega2": int(np.sum(w2 < -1e-12)),
            "K_eigs_kept": lam[keep].tolist()}


def main(which, arg=None):
    os.makedirs(DATA, exist_ok=True)
    if which == "b1":
        out = b1()
    elif which == "b2":
        out = b2()
    elif which == "b3":
        out = b3()
    elif which == "b4":
        out = b4()
    elif which == "b5":
        return b5(arg or "rotation")
    elif which == "verdict":
        v = {}
        for name in ("b1", "b2", "b3", "b4"):
            p = os.path.join(DATA, f"m5_20_3_b_{name}.json")
            if os.path.exists(p):
                with open(p) as f:
                    v[name] = json.load(f)
        for s in ("rotation", "clock", "boost4b"):
            p = os.path.join(DATA, f"m5_20_3_b_b5_{s}.json")
            if os.path.exists(p):
                with open(p) as f:
                    v[f"b5_{s}"] = json.load(f)
        loop_blows = (v.get("b2", {}).get("raw", {}).get("all_blow_up")
                      and v.get("b2", {}).get("recipe", {}).get("all_blow_up"))
        no_plateau = not (v.get("b2", {}).get("raw", {}).get("plateau")
                          or v.get("b2", {}).get("recipe", {}).get("plateau"))
        out = {
            "GO_production": bool(not loop_blows),
            "loop_blowup_all_cutoffs": bool(loop_blows),
            "no_cutoff_plateau": bool(no_plateau),
            "dt_robust": v.get("b1", {}).get("ok"),
            "dive_4d": v.get("b3", {}).get("dive_4d", {}).get("dived"),
            "vacuum_ladder_at_probe": true_ladder_at_probe(),
            "b5_tstars": {s: v.get(f"b5_{s}", {}).get("tstar", "n/a")
                          for s in ("rotation", "clock", "boost4b")}}
        print("[VERDICT] " + json.dumps(out, default=float)[:600],
              flush=True)
        with open(os.path.join(DATA, "m5_20_3_b_verdict.json"), "w") as f:
            json.dump(out, f, indent=1, default=float)
        return out
    else:
        raise ValueError(which)
    with open(os.path.join(DATA, f"m5_20_3_b_{which}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"wrote data/m5_20_3_b_{which}.json", flush=True)
    return out


if __name__ == "__main__":
    main(ARGV[0] if ARGV else "b1", ARGV[1] if len(ARGV) > 1 else None)
