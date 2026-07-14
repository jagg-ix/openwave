"""M5 film-strip standard (the single documentation source is
research/m5_visualization.md; this module is the implementation).

TEMPLATES (columns per row; one row per snapshot):
    basic    |M13| (magma) + max spatial eigenvalue s (viridis) +
             log10 |energy density| (inferno): the M5.20-series
             cross-section lineage (m5_20_1_endpoints.png), now the
             cross-series default
    thermal  the M5.21 panel set (glyphs / A / clock / energy / charge /
             curl): directed at thermal / energy-flow analysis; delegates
             to the m5_21_a_snap instrument

STANDARD (2026-07-14):
    - the FIRST row is always t = 0 (the seed used)
    - every panel title prints the time as
          t = <steps> steps [| <t * time_unit_s> s]
      (steps only until a tu -> s calibration is anchored; the seconds
      field appears when time_unit_s is supplied, in scientific
      notation: see m5_visualization.md)
    - the number of snapshots is a parameter, default N_SNAP = 6
      (the seed + 5 shots)

API:
    pick_frame_ts(T, n)     evenly spaced capture times incl. 0
    frame_title(it, t, ...) the standard title string
    film_strip(states, path, template="basic", ...)
        states = [{"it": int, "t": float, "M": (nr, nz, 4, 4)},
                  optional "V"], states[0]["t"] MUST be 0
"""
from __future__ import annotations

import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
N_SNAP = 6


def pick_frame_ts(T, n=N_SNAP):
    """evenly spaced capture times, first = 0 (the seed row)."""
    return [float(x) for x in np.linspace(0.0, T, n)]


def frame_title(it, t, time_unit_s=None):
    """steps only: the model time unit has no anchored conversion to
    seconds yet (user call 2026-07-14); the seconds field switches on
    when a tu -> s calibration is supplied."""
    s = f"t = {int(it)} steps"
    if time_unit_s is not None:
        s += f" | {t * time_unit_s:.2e} s"
    return s


def _basic_row(axes_row, M, title, delta, h, wscale, g, density_fn):
    from m5_20_2_a_eom import u_eta_density, v4_density
    nr, nz = M.shape[:2]
    m13 = M[: nr - 1, 1:-1, 1, 3]
    msp = M[: nr - 1, 1:-1, 1:4, 1:4]
    s = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
    if density_fn is None:
        dens = u_eta_density(M, h) + v4_density(M, wscale, delta, g)
    else:
        dens = density_fn(M)
    ext = [0.5 * h, (nr - 1.5) * h, -(nz / 2 - 1.5) * h, (nz / 2 - 1.5) * h]
    for ax, arr, ttl, cm in (
            (axes_row[0], np.abs(m13).T, f"{title}\n|M13|", "magma"),
            (axes_row[1], s.T, f"{title}\nmax eigenvalue s", "viridis"),
            (axes_row[2], np.log10(np.maximum(np.abs(dens), 1e-12)).T,
             f"{title}\nlog10 |energy density|", "inferno")):
        im = ax.imshow(arr, origin="lower", aspect="auto", extent=ext,
                       cmap=cm)
        ax.set_title(ttl, fontsize=8)
        plt.colorbar(im, ax=ax, shrink=0.8)


def film_strip(states, path, template="basic", delta=0.3, h=1.0, g=8.0,
               wscale=None, time_unit_s=None, suptitle="",
               density_fn=None, **thermal_kw):
    """render a film strip per the standard. states[0] must be t = 0."""
    if abs(states[0]["t"]) > 1e-12:
        raise ValueError("film standard: the first row must be t = 0 "
                         "(the seed)")
    if template == "basic":
        if wscale is None:
            from m5_12_core_pin import load_wscale
            wscale = load_wscale()
        nrow = len(states)
        fig, axes = plt.subplots(nrow, 3, figsize=(15, 3.2 * nrow),
                                 squeeze=False)
        for i, st in enumerate(states):
            _basic_row(axes[i], st["M"],
                       frame_title(st["it"], st["t"], time_unit_s),
                       delta, h, wscale, g, density_fn)
        if suptitle:
            fig.suptitle(suptitle, fontsize=15)
            fig.tight_layout(rect=(0, 0, 1, 1 - 0.35 / nrow))
        else:
            fig.tight_layout()
        fig.savefig(path, dpi=110)
        plt.close(fig)
        print("wrote", os.path.relpath(path, HERE))
        return path
    if template == "thermal":
        from m5_17_energy import grid_coords
        from m5_21_a_snap import film_strip as thermal_strip
        nr, nz = states[0]["M"].shape[:2]
        R, Z = grid_coords(nr, nz, h)
        return thermal_strip(
            states, R, Z, h, delta, path, g=g, suptitle=suptitle,
            title_fn=lambda st: frame_title(st["it"], st["t"],
                                            time_unit_s),
            **thermal_kw)
    raise ValueError(f"unknown template {template!r}")
