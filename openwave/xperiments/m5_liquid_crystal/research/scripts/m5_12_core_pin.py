"""M5.12 phase D0: Duda's core prescription vs the melt channel.

THE PRESCRIPTION (Duda 2026-07-06, m5_18_convo.md reply 1)
    "I suspect this melt problem comes from here - assuming center of charge
    not in lattice. Should be better if constraining centers in lattice
    points, replacing central value with 'M = a I' (identity matrix) in 3D,
    or in 4D (g', a,a,a) eigenspectrum."  For static Coulomb: "centers of
    charges need e.g. to be fixed in lattice points - central eigenspectrum
    needs to be spherically symmetric: (g', a,a,a) with g', a to be
    optimized."

WHAT THIS SCRIPT MEASURES (the first M5.12 measurement, pre-registered in
m5_12_task_details.md Card 6): does the core prescription CLOSE the melt
channel that survived both potentials (M5.17 quartic LdG, M5.18 spectral)?

    mode hedgehog: the point-defect leg. Seed = melted hedgehog with the
        core disk (r < r_pin) REPLACED by the isotropic value a*I (spatial
        block a*I3; time entry G_TIME, the statics-blind g' slot, gate G8).
        The scalar a is OPTIMIZED (golden section) in coordinate descent
        with the surrounding field (FIRE, core cells frozen). Then the
        M5.16/18 stability protocol: 3% symmetry-breaking bump + long 2D
        relax, core held. escaped=False => the prescription holds the
        point defect; escaped=True => the orientation escape survives.

    mode pair: the annihilation leg. Antipair seed (pair_field), BOTH core
        disks replaced by a*I (a from the hedgehog leg, re-golden-ed per
        run), FIRE 3000 iters (the frozen M5.17/18 design). d in
        {16, 24} = the baseline distances (centers BETWEEN z-cells) and
        {17, 25} = centers ON z-cell centers (the lattice-point aspect of
        the prescription; the cell-centered rho grid never samples rho=0,
        so exact 3D lattice-centering is approximated by the z axis).
        melt_min staying O(1) on the axis strip = the melt bridge is
        CLOSED; melt_min -> 0.008-class = the channel survives.

NOTE a = 0 reduces the core to the old melt core (s=0): the prescription
GENERALIZES the melt regularization; the optimized a* is itself a result.
V(a*I) per cell = w[(3a-1)^2 + (3a^2-1)^2 + (3a^3-1)^2] at delta = 0.

Instrument: UNCHANGED M5.18 spectral stack (calibrated wscale loaded from
m5_18_spectral_spec_n96.json; curvature + gradient + FIRE imported). No
functional change => the M5.16/18 gate suite applies as passed.

Run:  python m5_12_core_pin.py hedgehog [NR NZ]
      python m5_12_core_pin.py pair [a_star]
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

from m5_17_energy import (G_TIME, cell_weights, curvature_density_np,     # noqa: E402
                          grid_coords, hedgehog_field)
from m5_16_axisym import fire_relax, pin_mask                             # noqa: E402
from m5_18_spectral import (energy_gradient_spec_np,                     # noqa: E402
                            potential_density_spec_np, total_energy_spec_np)
from m5_17_two_charge import pair_field                                   # noqa: E402


def load_wscale():
    with open(os.path.join(DATA, "m5_18_spectral_spec_n96.json")) as f:
        return json.load(f)["params"]["wscale"]


def core_masks(R, Z, centers, r_pin):
    """boolean (nr, nz) mask of core cells: union of disks around on-axis
    centers (rho = 0, z = zc)."""
    m = np.zeros(R.shape, dtype=bool)
    for zc in centers:
        m |= np.sqrt(R ** 2 + (Z - zc) ** 2) < r_pin
    return m


def core_masks_rz(R, Z, centers, r_pin):
    """general (rho, z) centers, e.g. a loop's ring core at (R0, 0)."""
    m = np.zeros(R.shape, dtype=bool)
    for (rc_, zc) in centers:
        m |= np.sqrt((R - rc_) ** 2 + (Z - zc) ** 2) < r_pin
    return m


def apply_core(Mnp, core, a):
    """set core cells to the prescription value: spatial block a*I3, time
    entry G_TIME (statics-blind g' slot), zero mixing."""
    Mx = Mnp.copy()
    blk = np.zeros((4, 4))
    blk[0, 0] = G_TIME
    blk[1, 1] = blk[2, 2] = blk[3, 3] = a
    Mx[core] = blk
    return Mx


def golden_a(e_of_a, lo=0.0, hi=1.2, iters=60):
    invphi = (np.sqrt(5.0) - 1.0) / 2.0
    a_, b_ = hi - invphi * (hi - lo), lo + invphi * (hi - lo)
    fa, fb = e_of_a(a_), e_of_a(b_)
    for _ in range(iters):
        if fa < fb:
            hi, b_, fb = b_, a_, fa
            a_ = hi - invphi * (hi - lo)
            fa = e_of_a(a_)
        else:
            lo, a_, fa = a_, b_, fb
            b_ = lo + invphi * (hi - lo)
            fb = e_of_a(b_)
        if (hi - lo) < 1e-8:
            break
    return 0.5 * (lo + hi)


def v_core_per_cell(a, wscale):
    return wscale * ((3 * a - 1) ** 2 + (3 * a ** 2 - 1) ** 2
                     + (3 * a ** 3 - 1) ** 2)


def melt_min(Mnp, nr, nz, strip=None):
    """min of the largest spatial eigenvalue; strip=k limits to rho < k
    cells (the near-axis melt-bridge readout of m5_18_spectral.run_pair)."""
    msp = Mnp[: nr - 1, 1:-1, 1:4, 1:4]
    s_cell = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    if strip is not None:
        s_cell = s_cell[:strip, :]
    return float(np.min(s_cell)), s_cell


def relax_with_core(M0, core, a, wscale, h, iters, tol_rel=1e-5):
    nr, nz = M0.shape[:2]
    Mx = apply_core(M0, core, a)
    pin = pin_mask(nr, nz) | core
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(nr, nz, h)
    wfull = np.ones((nr, nz))
    wfull[: nr - 1, 1:-1] = w
    precond = (1.0 / wfull)[..., None, None]

    def egf(MM):
        return (total_energy_spec_np(MM, wscale, h),
                energy_gradient_spec_np(MM, wscale, h))

    return fire_relax(Mx, egf, free4, precond, max_iter=iters, tol_rel=tol_rel)


def run_hedgehog(nr=96, nz=192, h=1.0, r_pin=2.5, rc_seed=8.0,
                 rounds=3, iters_cd=4000, iters_stab=8000):
    wscale = load_wscale()
    R, Z = grid_coords(nr, nz, h)
    core = core_masks(R, Z, [0.0], r_pin)
    n_core = int(np.sum(core))
    M0 = hedgehog_field(R, Z, rc_seed)
    t0 = time.time()
    # coordinate descent: golden(a) with field fixed, then FIRE with core held
    a = 0.3
    Mx = M0
    cd_log = []
    for rd in range(rounds):
        a = golden_a(lambda aa: total_energy_spec_np(
            apply_core(Mx, core, aa), wscale, h))
        Mx, hist = relax_with_core(Mx, core, a, wscale, h, iters_cd)
        cd_log.append({"round": rd + 1, "a": a, "E": hist["E"][-1],
                       "gnorm_last": hist["gnorm"][-1]})
        print(f"[cd {rd+1}] a*={a:.4f} E={hist['E'][-1]:.4f} "
              f"gn={hist['gnorm'][-1]:.2e}")
    E_base = cd_log[-1]["E"]
    mmin_base, _ = melt_min(Mx, nr, nz)
    # the M5.16/18 stability protocol: 3% bump, long relax, core held at a*
    bump = 0.03 * np.exp(-(((R - 0.8 * rc_seed) ** 2)
                           + (Z - 0.5 * rc_seed) ** 2) / (rc_seed ** 2))
    Mp = Mx.copy()
    Mp[..., 1, 3] += bump
    Mp[..., 3, 1] += bump
    Mp[..., 2, 2] += 0.5 * bump
    Mp = apply_core(Mp, core, a)          # bump never touches the core
    Mf, hist = relax_with_core(Mp, core, a, wscale, h, iters_stab)
    E_end = hist["E"][-1]
    mmin, s_cell = melt_min(Mf, nr, nz)
    k = np.unravel_index(np.argmin(s_cell), s_cell.shape)
    escaped = bool(E_end < E_base - 0.05 * abs(E_base))
    out = {
        "task": "M5.12", "script": "m5_12_core_pin.py", "mode": "hedgehog",
        "prescription": "core disk r<r_pin replaced by a*I (Duda 2026-07-06),"
                        " a golden-optimized, field FIRE-relaxed, core frozen",
        "grid": {"NR": nr, "NZ": nz, "h": h},
        "params": {"wscale": wscale, "r_pin": r_pin, "rc_seed": rc_seed,
                   "n_core_cells": n_core, "rounds": rounds,
                   "iters_cd": iters_cd, "iters_stab": iters_stab},
        "coordinate_descent": cd_log,
        "a_star": a,
        "V_core_per_cell_at_a_star": v_core_per_cell(a, wscale),
        "E_base_corepinned": E_base,
        "melt_min_s_base": mmin_base,
        "E_after_bump_relax": E_end,
        "drop_rel": (E_base - E_end) / abs(E_base),
        "escaped_hedgehog": escaped,
        "melt_min_s": mmin,
        "melt_min_location_rho_z": [float((k[0] + 0.5) * h),
                                    float((k[1] - (nz - 2) / 2 + 0.5) * h)],
        "gnorm_first_last": [hist["gnorm"][0], hist["gnorm"][-1]],
        "wall_s": round(time.time() - t0, 1),
        "baselines": {"m5_18_spectral_no_prescription":
                      {"drop_rel": 0.548, "melt_min_s": 0.508},
                      "m5_16_ldg_n64": {"drop_rel": 0.35}},
        "note": "escaped=False => the core prescription holds the point"
                " defect (channel CLOSED on this leg); escaped=True =>"
                " the orientation escape survives the prescription",
    }
    # compact structure diagnostic: s map + energy densities (float32)
    msp = Mf[: nr - 1, 1:-1, 1:4, 1:4]
    s_map = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    np.savez_compressed(
        os.path.join(DATA, "m5_12_d0_hedgehog_state.npz"),
        s_map=s_map.astype(np.float32),
        dcurv=curvature_density_np(Mf, h, 1.0).astype(np.float32),
        dpot=potential_density_spec_np(Mf, wscale).astype(np.float32),
        Msp_final=msp.astype(np.float32),
        Msp_base=Mx[: nr - 1, 1:-1, 1:4, 1:4].astype(np.float32))
    path = os.path.join(DATA, "m5_12_d0_hedgehog.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[d0-hedgehog] a*={a:.4f} E_base={E_base:.4f} -> E={E_end:.4f} "
          f"escaped={escaped} melt_min={mmin:.3f} at "
          f"(rho,z)=({out['melt_min_location_rho_z'][0]:.1f},"
          f"{out['melt_min_location_rho_z'][1]:.1f}) wall={out['wall_s']}s")
    print(f"json -> {path}")
    return out


def run_pair(a_star=None, ds=(16.0, 17.0, 24.0, 25.0), nr=96, nz=192, h=1.0,
             iters=3000, rc_core=8.0, r_pin=2.5):
    wscale = load_wscale()
    R, Z = grid_coords(nr, nz, h)
    rows = []
    t00 = time.time()
    for d in ds:
        centers = [-0.5 * d, +0.5 * d]
        core = core_masks(R, Z, centers, r_pin)
        M0 = pair_field(R, Z, d, rc_core, -1)
        # per-run golden on a (field = seed), seeded by the hedgehog a*
        a = golden_a(lambda aa: total_energy_spec_np(
            apply_core(M0, core, aa), wscale, h)) if a_star is None else a_star
        t0 = time.time()
        Mf, hist = relax_with_core(M0, core, a, wscale, h, iters, tol_rel=1e-4)
        mmin, _ = melt_min(Mf, nr, nz, strip=int(4 / h))
        on_lattice = bool(abs((0.5 * d) % h - 0.5 * h) < 1e-9)
        rows.append({"d": d, "z_centers_on_cell_centers": on_lattice,
                     "a": a,
                     "E_seed": hist["E"][0], "E_relaxed": hist["E"][-1],
                     "drop": hist["E"][0] - hist["E"][-1],
                     "gnorm_decades": float(np.log10(
                         hist["gnorm"][0] / (hist["gnorm"][-1] + 1e-300))),
                     "melt_min_axis_strip": mmin,
                     "wall_s": round(time.time() - t0, 1)})
        r = rows[-1]
        print(f"[d0-pair d={d:g} lat={on_lattice}] a={a:.4f} "
              f"E {r['E_seed']:.3f} -> {r['E_relaxed']:.3f} "
              f"melt_min={r['melt_min_axis_strip']:.3f} "
              f"decades={r['gnorm_decades']:.1f} wall={r['wall_s']}s")
    out = {"task": "M5.12", "script": "m5_12_core_pin.py", "mode": "pair",
           "prescription": "both core disks r<r_pin replaced by a*I, a"
                           " golden-optimized per run; centers at z=+-d/2"
                           " (d odd => ON z-cell centers)",
           "grid": {"NR": nr, "NZ": nz, "h": h},
           "params": {"wscale": wscale, "rc_core": rc_core, "r_pin": r_pin,
                      "iters": iters},
           "rows": rows,
           "baseline_m5_18": {"d16": {"E_relaxed": 0.345, "melt_min": 0.0076},
                              "d24": {"E_relaxed": 0.409, "melt_min": 0.0078}},
           "wall_s_total": round(time.time() - t00, 1),
           "note": "melt_min O(1) = the annihilation melt bridge is CLOSED"
                   " by the core prescription; melt_min ~ 0.008 = the"
                   " channel survives (M5.18 baseline)"}
    path = os.path.join(DATA, "m5_12_d0_pair_anti.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {path}")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "hedgehog"
    if mode == "hedgehog":
        nr = int(ARGV[1]) if len(ARGV) > 1 else 96
        nz = int(ARGV[2]) if len(ARGV) > 2 else 2 * nr
        run_hedgehog(nr, nz)
    elif mode == "pair":
        a_star = float(ARGV[1]) if len(ARGV) > 1 else None
        run_pair(a_star)
    else:
        print(f"unknown mode {mode}")
