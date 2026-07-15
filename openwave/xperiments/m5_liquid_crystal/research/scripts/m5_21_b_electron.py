"""M5.21 phase B: the electron statics baseline + clock-seed machinery (GS).

THE OBJECT. The charge defect in the 4-target stack (the M5.20.2 canonical
completion, verbatim: u_eta + V4, delta = 0.3, g-timelike branch, the
audited 128 x 256 axisym grid): a biaxial HEDGEHOG,
    M_sp(x) = 1 . n n^T + delta . m m^T,   n = rhat (radial director:
    the charge winding), m = phihat (the delta-axis azimuthal),
far field = the exact V4 vacuum spectrum (1, delta, 0) in a radial frame;
core blended to Duda's 3-equal charge core (a, a, a), a = (1 + delta)/3
(trace-continuous), as the INITIAL GUESS ONLY: the relax MEASURES what the
core actually does (the M5.20.1 lesson: say "the dynamics selects").

KNOWN TOPOLOGY FEATURE (reported, not hidden): the biaxial hedgehog cannot
comb the (delta, 0) frame smoothly over the sphere; in the axisym scheme
the z-axis carries an attached delta-frame line structure (x-y anisotropy
at rho -> 0 costs ~ (1 - delta)^2 / rho^2 through the A_phi channel: the
M5.20.1 axis-disclination lesson). The energy panel will show it; the GS
localization number is scope-boxed accordingly.

GS GATES (pre-registered)
    GS1  FIRE descent: E_final < E_seed, no net rise, force drop >= 2
         decades (or force tolerance reached)
    GS2  core spectrum at the centre: read (lam1, lam2, lam3) averaged over
         r < 1.5; REPORT 3-equal-ness (spread / vacuum anisotropy) and the
         measured a vs (1 + delta)/3: prediction check, not an imposition
    GS3  charge intact: meridional winding q == 1 within 5% after relax
    GS4  finite + localized: E finite; melt-region amplitude r_half
         measured (the M5.16-correspondence number, structural only:
         the lock is LdG-based, a different functional)

Run:  python m5_21_b_electron.py [relax_iters]        (default 12000)
Out:  ../data/m5_21_b_electron.json, ../data/m5_21_b_relaxed_state.npz,
      ../plots/m5_21_b_baseline.png
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
from m5_16_axisym import pin_mask                                  # noqa: E402
from m5_20_2_a_eom import G_T, NR, NZ, H, WSCALE                   # noqa: E402
from m5_20_2_b_dynamics import make_egf_4                          # noqa: E402
from m5_21_a_snap import (eig_fields, film_strip, orient,          # noqa: E402
                          spectral_amplitude)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
DELTA = 0.3
A_CORE = (1.0 + DELTA) / 3.0


# ================= seed =================
def electron_seed(delta=DELTA, r_c=4.0):
    """biaxial hedgehog + 3-equal core blend; time row M00 = -g."""
    R, Z = grid_coords(NR, NZ, H)
    r = np.sqrt(R ** 2 + Z ** 2)
    rs = np.where(r < 1e-12, 1e-12, r)
    n = np.stack([R / rs, np.zeros_like(R), Z / rs], axis=-1)
    m = np.broadcast_to(np.array([0.0, 1.0, 0.0]), n.shape)
    S = (n[..., :, None] * n[..., None, :]
         + delta * m[..., :, None] * m[..., None, :])
    a = (1.0 + delta) / 3.0
    core = a * np.eye(3)
    w = (1.0 - np.exp(-((r / r_c) ** 2)))[..., None, None]
    M = np.zeros((NR, NZ, 4, 4))
    M[..., 1:4, 1:4] = w * S + (1.0 - w) * core
    M[..., 0, 0] = -G_T
    return M


# ================= observables =================
def core_spectrum(Mnp, r_avg=1.5):
    R, Z = grid_coords(NR, NZ, H)
    r = np.sqrt(R ** 2 + Z ** 2)
    sel = r < r_avg
    lam, _ = eig_fields(Mnp)
    lam_c = lam[sel].mean(axis=0)
    spread = float(lam_c.max() - lam_c.min())
    return {"core_lams": lam_c.tolist(), "core_spread": spread,
            "core_spread_over_vacuum_aniso": spread / 1.0,
            "core_mean": float(lam_c.mean()),
            "a_predicted": A_CORE,
            "n_cells": int(np.sum(sel))}


def meridional_charge(Mnp, r_m=12.0, npts=181):
    """winding of the in-plane director angle along the half-circle from
    +z to -z at radius r_m (apolar: jumps folded into (-pi/2, pi/2]);
    q = total / pi. Hedgehog: alpha tracks the polar angle -> q = 1."""
    R, Z = grid_coords(NR, NZ, H)
    lam, V = eig_fields(Mnp)
    rr = np.sqrt(R ** 2 + Z ** 2)
    rr = np.where(rr < 1e-12, 1e-12, rr)
    n = orient(V[..., :, 0],
               np.stack([R / rr, np.zeros_like(R), Z / rr], axis=-1))
    th = np.linspace(1e-3, np.pi - 1e-3, npts)
    rho_s = r_m * np.sin(th)
    z_s = r_m * np.cos(th)
    i = np.clip(np.round(rho_s / H - 0.5).astype(int), 0, NR - 1)
    j = np.clip(np.round(z_s / H + NZ / 2 - 0.5).astype(int), 0, NZ - 1)
    alpha = np.arctan2(n[i, j, 0], n[i, j, 2])
    d = np.diff(alpha)
    d = (d + np.pi / 2) % np.pi - np.pi / 2
    return float(np.sum(d) / np.pi)


def amplitude_r_half(Mnp, delta=DELTA):
    """radius where the angle-median spectral amplitude falls to half its
    core value (the melt half-radius, the M5.16-correspondence number)."""
    R, Z = grid_coords(NR, NZ, H)
    r = np.sqrt(R ** 2 + Z ** 2)
    A = spectral_amplitude(Mnp, (G_T, 1.0, delta, 0.0))
    rb = np.arange(0.5, 40.0, 1.0)
    prof = np.array([np.median(A[(r >= x - 0.5) & (r < x + 0.5)])
                     for x in rb])
    a0 = prof[0]
    below = np.where(prof < 0.5 * a0)[0]
    return (float(rb[below[0]]) if below.size else float("nan"),
            rb.tolist(), prof.tolist())


def defect_center(Mnp, delta=DELTA):
    """amplitude^2-weighted centroid (rho, z) of the melt region."""
    R, Z = grid_coords(NR, NZ, H)
    A = spectral_amplitude(Mnp, (G_T, 1.0, delta, 0.0)) ** 2
    W = A / max(A.sum(), 1e-300)
    return float((R * W).sum()), float((Z * W).sum())


# ================= FIRE relax =================
def fire_relax(M0, e_fn, g_fn, max_iter=12000, dt0=0.02, dt_max=0.2,
               log_every=1000):
    """standard FIRE on the free DOFs (outer-boundary pin, m5_16 heritage);
    per-cell 1/w preconditioner. Returns (M, history)."""
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    w = np.ones((NR, NZ))
    w[: NR - 1, 1:-1] = cell_weights(NR, NZ, H)
    precond = (1.0 / w)[..., None, None]
    M = M0.copy()
    v = np.zeros_like(M)
    dt, alpha = dt0, 0.1
    n_up = 0
    hist = []
    E0 = e_fn(M)
    F = -g_fn(M) * precond * free4
    f0 = float(np.max(np.abs(F)))
    for it in range(1, max_iter + 1):
        P = float(np.sum(F * v))
        if P > 0.0:
            n_up += 1
            vn = np.sqrt(np.sum(v * v))
            fn = np.sqrt(np.sum(F * F))
            v = (1 - alpha) * v + alpha * (F / max(fn, 1e-300)) * vn
            if n_up > 5:
                dt = min(dt * 1.1, dt_max)
                alpha *= 0.99
        else:
            v[:] = 0.0
            dt *= 0.5
            alpha = 0.1
            n_up = 0
        v += dt * F
        M += dt * v
        F = -g_fn(M) * precond * free4
        if it % log_every == 0 or it == max_iter:
            E = e_fn(M)
            fmax = float(np.max(np.abs(F)))
            hist.append({"it": it, "E": E, "fmax": fmax, "dt": dt})
            print(f"  it {it:6d} E {E:12.5f} fmax {fmax:.3e} dt {dt:.3f}",
                  flush=True)
            if fmax < 1e-8 * max(f0, 1e-300):
                break
    return M, {"E_seed": E0, "fmax_seed": f0, "trace": hist}


def main(iters=12000):
    e_fn, g_fn = make_egf_4(DELTA)
    R, Z = grid_coords(NR, NZ, H)
    M0 = electron_seed()
    out = {"task": "M5.21", "phase": "B", "delta": DELTA, "g": G_T,
           "wscale": WSCALE, "grid": [NR, NZ, H], "a_core_seed": A_CORE}
    out["seed"] = {"E": e_fn(M0), "core": core_spectrum(M0),
                   "q_meridional": meridional_charge(M0),
                   "center": defect_center(M0)}
    print(f"[seed] E {out['seed']['E']:.4f} "
          f"q {out['seed']['q_meridional']:.4f} "
          f"core {np.round(out['seed']['core']['core_lams'], 4)}",
          flush=True)
    Mr, rel = fire_relax(M0, e_fn, g_fn, max_iter=iters)
    r_half, rb, prof = amplitude_r_half(Mr)
    out["relaxed"] = {"E": e_fn(Mr), "core": core_spectrum(Mr),
                      "q_meridional": meridional_charge(Mr),
                      "center": defect_center(Mr), "r_half": r_half,
                      "amp_profile_r": rb, "amp_profile": prof}
    out["fire"] = rel
    # gates
    tr = rel["trace"]
    fdrop = rel["fmax_seed"] / max(tr[-1]["fmax"], 1e-300)
    gs1 = (out["relaxed"]["E"] < out["seed"]["E"]
           and all(tr[k]["E"] >= tr[k + 1]["E"] - 1e-9 * abs(tr[k]["E"])
                   for k in range(len(tr) - 1))
           and fdrop >= 1e2)
    core = out["relaxed"]["core"]
    gs2_meas = {"spread_frac": core["core_spread_over_vacuum_aniso"],
                "a_measured": core["core_mean"],
                "a_predicted": A_CORE,
                "a_relerr": abs(core["core_mean"] - A_CORE) / A_CORE}
    gs3 = abs(out["relaxed"]["q_meridional"] - 1.0) < 0.05
    gs4 = bool(np.isfinite(out["relaxed"]["E"]) and np.isfinite(r_half))
    out["GS"] = {"GS1_descent": {"ok": bool(gs1), "force_drop": fdrop},
                 "GS2_core": gs2_meas,
                 "GS3_charge": {"ok": bool(gs3),
                                "q": out["relaxed"]["q_meridional"]},
                 "GS4_finite_localized": {"ok": bool(gs4),
                                          "r_half": r_half}}
    print(f"[GS1] {'PASS' if gs1 else 'FAIL'} force_drop {fdrop:.1e}")
    print(f"[GS2] core lams {np.round(core['core_lams'], 4)} "
          f"spread {core['core_spread']:.4f} a_meas "
          f"{core['core_mean']:.4f} vs pred {A_CORE:.4f}")
    print(f"[GS3] {'PASS' if gs3 else 'FAIL'} q "
          f"{out['relaxed']['q_meridional']:.4f}")
    print(f"[GS4] {'PASS' if gs4 else 'FAIL'} r_half {r_half}")
    # baseline film-strip row: seed vs relaxed (the instrument's first
    # physics customer)
    film_strip(
        [{"t": 0, "M": M0, "vac_spec": (G_T, 1.0, DELTA, 0.0)},
         {"t": 1, "M": Mr, "vac_spec": (G_T, 1.0, DELTA, 0.0)}],
        R, Z, H, DELTA, os.path.join(PLOTS, "m5_21_b_baseline.png"),
        step=8,
        suptitle="M5.21-B electron baseline: seed (top) vs FIRE-relaxed "
                 "(bottom); biaxial hedgehog, delta-axis azimuthal, "
                 "3-equal core")
    np.savez_compressed(os.path.join(DATA, "m5_21_b_relaxed_state.npz"),
                        M=Mr)
    with open(os.path.join(DATA, "m5_21_b_electron.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote data/m5_21_b_electron.json + m5_21_b_relaxed_state.npz"
          " + plots/m5_21_b_baseline.png")
    return out


if __name__ == "__main__":
    main(int(ARGV[0]) if ARGV else 12000)
