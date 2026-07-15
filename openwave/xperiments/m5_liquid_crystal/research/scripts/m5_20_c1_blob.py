"""M5.20 phase C+: the localized remnant (breather/oscillon candidate).

The corepin-release endpoints carry a coherent localized blob at the ring
site (s depressed to ~0.70, energy density >> background) AFTER the winding
is gone. This script measures it:

  1. blob locator: max of the energy density over rho < 60 (away from the
     axis debris wedge), local integral E_blob (r < 8), s_min, |M13|_max;
  2. breathing spectrum: evolve T from the saved (M, v) endpoint with dense
     blob-centered probes; FFT of s_min(t) and E_blob(t);
  3. the vacuum mass scale to compare against: eigenfrequencies of the
     linearized uniform-mode EOM  d_t^2 dM = -H_V dM  at the uniaxial
     vacuum diag(1,0,0) (numeric 6x6 Hessian of the spectral V density on
     the symmetric 3x3 block; kinetic metric = identity per unit measure).
     A blob line BELOW every vacuum eigenfrequency cannot couple to linear
     modes even if a Dirichlet term restored propagation.

Usage: python m5_20_c1_blob.py <run_name> [T]
Out:   ../data/m5_20_blob_<run_name>.json, ../plots/m5_20_blob_<run_name>.png
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

from m5_20_a1_dynamics import (NR, NZ, H, WSCALE, evolve, make_egf)  # noqa: E402
from m5_17_energy import curvature_density_np, grid_coords, cell_weights  # noqa: E402
from m5_18_spectral import potential_density_spec_np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def vacuum_mass_spectrum(wscale):
    """eigenfrequencies of d_t^2 dM = -H dM at the uniaxial vacuum
    diag(1,0,0): numeric Hessian of the spectral V DENSITY over the 6
    symmetric-component directions (basis normalized in the Frobenius
    metric, matching the kinetic term 1/2 ||dM/dt||_F^2)."""
    lam = np.diag([1.0, 0.0, 0.0])
    basis = []
    for i in range(3):
        e = np.zeros((3, 3))
        e[i, i] = 1.0
        basis.append(e)
    for (i, j) in ((0, 1), (0, 2), (1, 2)):
        e = np.zeros((3, 3))
        e[i, j] = e[j, i] = 1.0 / np.sqrt(2.0)
        basis.append(e)

    def vdens(m):
        m2 = m @ m
        t1, t2 = np.trace(m), np.trace(m2)
        t3 = np.trace(m2 @ m)
        return wscale * ((t1 - 1) ** 2 + (t2 - 1) ** 2 + (t3 - 1) ** 2)

    eps = 1e-5
    Hm = np.zeros((6, 6))
    for a in range(6):
        for b in range(6):
            Hm[a, b] = (vdens(lam + eps * (basis[a] + basis[b]))
                        - vdens(lam + eps * (basis[a] - basis[b]))
                        - vdens(lam + eps * (-basis[a] + basis[b]))
                        + vdens(lam - eps * (basis[a] + basis[b]))) / (4 * eps ** 2)
    ev = np.linalg.eigvalsh(Hm)
    return ev, np.sqrt(np.maximum(ev, 0.0))


def blob_locate(M):
    """max of the energy density over rho < 60 (the window includes the
    axis; in the measured endpoints the argmax lands off-axis at rho ~ 15
    and the axis wedge holds < 1% of the energy: audit note 2026-07-11)."""
    dens = (curvature_density_np(M, H, 1.0)
            + potential_density_spec_np(M, WSCALE))
    ri = (np.arange(NR - 1) + 0.5) * H
    zj = (np.arange(1, NZ - 1) - NZ / 2 + 0.5) * H
    sub = dens[: 60, :]
    i, j = np.unravel_index(np.argmax(sub), sub.shape)
    return float(ri[i]), float(zj[j])


def blob_probe(rho_c, z_c):
    R, Z = grid_coords(NR, NZ, H)
    Rin, Zin = R[: NR - 1, 1:-1], Z[: NR - 1, 1:-1]
    din = np.sqrt((Rin - rho_c) ** 2 + (Zin - z_c) ** 2) < 8.0
    w = cell_weights(NR, NZ, H)

    def fn(Mx, v):
        dens = (curvature_density_np(Mx, H, 1.0)
                + potential_density_spec_np(Mx, WSCALE)) * w
        msp = Mx[: NR - 1, 1:-1, 1:4, 1:4]
        sub = msp[din]
        s = np.linalg.eigvalsh(0.5 * (sub + np.swapaxes(sub, -1, -2)))[..., -1]
        return {"E_blob": float(np.sum(dens[din])),
                "s_min": float(np.min(s)),
                "m13_max_blob": float(np.max(np.abs(sub[..., 0, 2])))}
    return fn


def main(name, T=300.0, dt=0.02):
    st = np.load(os.path.join(DATA, f"m5_20_{name}_state.npz"))
    M0 = st["M0"].astype(np.float64)
    v0 = st["v0"].astype(np.float64) if "v0" in st else None
    rho_c, z_c = blob_locate(M0)
    print(f"[blob:{name}] located ({rho_c:.1f}, {z_c:.1f})")
    egf = make_egf("comm")
    snap = blob_probe(rho_c, z_c)
    Mx, v, recs, wall = evolve(M0, egf, T, dt, v0=v0,
                               snap_every=5, snap_fn=snap)
    t = np.array([r["t"] for r in recs])
    eb = np.array([r["E_blob"] for r in recs])
    sm = np.array([r["s_min"] for r in recs])
    # FFT of the detrended series
    def spec(y):
        y = y - np.mean(y)
        f = np.fft.rfftfreq(len(y), d=(t[1] - t[0]))
        a = np.abs(np.fft.rfft(y * np.hanning(len(y))))
        return f, a
    f_e, a_e = spec(eb)
    f_s, a_s = spec(sm)
    evals, freqs = vacuum_mass_spectrum(WSCALE)
    pk_e = float(f_e[1:][np.argmax(a_e[1:])] * 2 * np.pi)
    pk_s = float(f_s[1:][np.argmax(a_s[1:])] * 2 * np.pi)
    out = {"task": "M5.20", "blob_of": name, "center": [rho_c, z_c],
           "T": T, "dt": dt,
           "E_blob_first_last": [float(eb[0]), float(eb[-1])],
           "s_min_first_last": [float(sm[0]), float(sm[-1])],
           "omega_peak_E": pk_e, "omega_peak_s": pk_s,
           "vacuum_mass_omegas": freqs.tolist(),
           "trajectory": recs, "wall_s": round(wall, 1)}
    with open(os.path.join(DATA, f"m5_20_blob_{name}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    fig, axes = plt.subplots(1, 3, figsize=(15, 3.4))
    axes[0].plot(t, eb)
    axes[0].set_title(f"{name}: E_blob(t) (r<8 of ({rho_c:.0f},{z_c:.0f}))",
                      fontsize=9)
    axes[1].plot(t, sm)
    axes[1].set_title("s_min(t) in blob", fontsize=9)
    axes[2].semilogy(f_s * 2 * np.pi, a_s + 1e-12, label="s_min spectrum")
    axes[2].semilogy(f_e * 2 * np.pi, a_e + 1e-12, label="E_blob spectrum")
    for w0 in freqs:
        if w0 > 1e-6:
            axes[2].axvline(w0, color="k", ls=":", lw=0.8)
    axes[2].set_xlim(0, max(freqs) * 3 if max(freqs) > 0 else 1)
    axes[2].set_xlabel("omega")
    axes[2].legend(fontsize=7)
    axes[2].set_title("breathing spectrum vs vacuum mass lines (dotted)",
                      fontsize=9)
    fig.tight_layout()
    path = os.path.join(PLOTS, f"m5_20_blob_{name}.png")
    fig.savefig(path, dpi=110)
    print(f"[blob:{name}] E_blob {eb[0]:.3f}->{eb[-1]:.3f}, s_min "
          f"{sm[0]:.2f}->{sm[-1]:.2f}, omega_peak(s) {pk_s:.4f}, "
          f"vacuum omegas {np.round(freqs, 4)}, wall {wall:.0f}s")
    print("wrote", path)


if __name__ == "__main__":
    main(ARGV[0], float(ARGV[1]) if len(ARGV) > 1 else 300.0)
