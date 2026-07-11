"""M5.20: endpoint field maps + core hunting for the verdict runs.

Panels per run: |M13| map, max-eigenvalue s map, energy density (log) map;
plus a CORE HUNT: local maxima of |M13| (min separation 6 cells), each with
guarded winding reads at r_w in {3,4,5}: distinguishes a surviving moved
core from dispersal debris (the M5.19 centroid-lesson applied at endpoint).

Usage: python m5_20_b2_maps.py <run_name> [...]
Out:   ../plots/m5_20_endpoints.png + core-hunt JSON to stdout/verdicts file.
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

from m5_20_a1_dynamics import NR, NZ, H, WSCALE           # noqa: E402
from m5_17_energy import curvature_density_np             # noqa: E402
from m5_18_spectral import potential_density_spec_np      # noqa: E402
from m5_19_d1_relax import winding_measure                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def core_hunt(M, n_peaks=6, min_sep=6.0):
    """local maxima of |M13| + guarded winding reads around each."""
    m13 = np.abs(M[: NR - 1, 1:-1, 1, 3])
    ri = (np.arange(NR - 1) + 0.5) * H
    zj = (np.arange(1, NZ - 1) - NZ / 2 + 0.5) * H
    flat = m13.ravel().argsort()[::-1]
    peaks = []
    for idx in flat[:4000]:
        i, j = np.unravel_index(idx, m13.shape)
        rho, z = ri[i], zj[j]
        if any((rho - p["rho"]) ** 2 + (z - p["z"]) ** 2 < min_sep ** 2
               for p in peaks):
            continue
        p = {"rho": float(rho), "z": float(z), "m13": float(m13[i, j])}
        p["q"] = {}
        for rw in (3.0, 4.0, 5.0):
            q = winding_measure(M, NR, NZ, H, rho, z, r_w=rw)
            p["q"][str(rw)] = None if not np.isfinite(q) else round(float(q), 3)
        peaks.append(p)
        if len(peaks) >= n_peaks:
            break
    return peaks


def main(names, out="m5_20_endpoints.png"):
    fig, axes = plt.subplots(len(names), 3, figsize=(15, 3.6 * len(names)),
                             squeeze=False)
    hunts = {}
    for k, name in enumerate(names):
        M = np.load(os.path.join(DATA, f"m5_20_{name}_state.npz"))[
            "M0"].astype(np.float64)
        m13 = M[: NR - 1, 1:-1, 1, 3]
        msp = M[: NR - 1, 1:-1, 1:4, 1:4]
        s = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
        dens = (curvature_density_np(M, H, 1.0)
                + potential_density_spec_np(M, WSCALE))
        ext = [0.5, NR - 1.5, -(NZ / 2 - 1.5), NZ / 2 - 1.5]
        for ax, arr, ttl, cm in (
                (axes[k, 0], np.abs(m13).T, f"{name}: |M13|", "magma"),
                (axes[k, 1], s.T, "max eigenvalue s", "viridis"),
                (axes[k, 2], np.log10(np.maximum(dens, 1e-12)).T,
                 "log10 energy density", "inferno")):
            im = ax.imshow(arr, origin="lower", aspect="auto",
                           extent=ext, cmap=cm)
            ax.set_title(ttl, fontsize=9)
            plt.colorbar(im, ax=ax, shrink=0.8)
        hunts[name] = core_hunt(M)
        for p in hunts[name]:
            axes[k, 0].plot(p["rho"], p["z"], "c+", ms=8)
    fig.tight_layout()
    path = os.path.join(PLOTS, out)
    fig.savefig(path, dpi=110)
    print("wrote", path)
    print(json.dumps(hunts, indent=1))
    hunt_json = "m5_20_core_hunt.json" if out == "m5_20_endpoints.png" \
        else out.replace(".png", "_hunt.json")
    with open(os.path.join(DATA, hunt_json), "w") as f:
        json.dump(hunts, f, indent=1)


if __name__ == "__main__":
    args = ARGV
    out = "m5_20_endpoints.png"
    if args and args[0].startswith("--out="):
        out = args[0].split("=", 1)[1]
        args = args[1:]
    main(args, out)
