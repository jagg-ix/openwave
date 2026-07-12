"""M5.20.1 phase E: the remnant re-probe in the gapped theory (DoD 6).

m5_20_c1_blob generalized to delta != 0: is the M5.20 breather-candidate
oscillation present / absent / sharper at (1, delta, 0)? The comparison
lines are now the DELTA-DEPENDENT vacuum mass ladder (the phase-A gap map:
the formerly-flat splitting mode sits at omega_split(delta), so a remnant
line can hide below it only in the delta -> 0 limit).

Usage: python m5_20_1_f_blob.py <run_tag> [T]
Out:   ../data/m5_20_1_blob_<tag>.json, ../plots/m5_20_1_blob_<tag>.png
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

from m5_17_energy import curvature_density_np, grid_coords, cell_weights  # noqa: E402
from m5_18_spectral import potential_density_spec_np                # noqa: E402
from m5_20_a1_dynamics import evolve                                # noqa: E402
from m5_20_1_a_theory import vacuum_hessian_delta                   # noqa: E402
from m5_20_1_b_seeds import cps_of                                  # noqa: E402
from m5_20_1_d_dynamics import NR, NZ, H, make_egf_biax             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


def blob_locate(M, wscale, cps):
    dens = (curvature_density_np(M, H, 1.0)
            + potential_density_spec_np(M, wscale, cps))
    ri = (np.arange(NR - 1) + 0.5) * H
    zj = (np.arange(1, NZ - 1) - NZ / 2 + 0.5) * H
    sub = dens[:60, :]
    i, j = np.unravel_index(np.argmax(sub), sub.shape)
    return float(ri[i]), float(zj[j])


def main(tag, T=300.0, dt=0.02):
    with open(os.path.join(DATA, f"m5_20_1_run_{tag}.json")) as f:
        d = json.load(f)
    delta, wscale = d["delta"], d["wscale"]
    cps = cps_of(delta)
    st = np.load(os.path.join(DATA, f"m5_20_1_run_{tag}_state.npz"))
    M0 = st["M0"].astype(np.float64)
    v0 = st["v0"].astype(np.float64) if "v0" in st else None
    rho_c, z_c = blob_locate(M0, wscale, cps)
    print(f"[blob:{tag}] delta={delta} located ({rho_c:.1f}, {z_c:.1f})")
    R, Z = grid_coords(NR, NZ, H)
    Rin, Zin = R[: NR - 1, 1:-1], Z[: NR - 1, 1:-1]
    din = np.sqrt((Rin - rho_c) ** 2 + (Zin - z_c) ** 2) < 8.0
    w = cell_weights(NR, NZ, H)

    def snap(Mx, v):
        dens = (curvature_density_np(Mx, H, 1.0)
                + potential_density_spec_np(Mx, wscale, cps)) * w
        msp = Mx[: NR - 1, 1:-1, 1:4, 1:4][din]
        s = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
        return {"E_blob": float(np.sum(dens[din])),
                "s_min": float(np.min(s))}

    egf = make_egf_biax(delta, wscale)
    Mx, v, recs, wall = evolve(M0, egf, T, dt, v0=v0, snap_every=5,
                               snap_fn=snap)
    t = np.array([r["t"] for r in recs])
    eb = np.array([r["E_blob"] for r in recs])
    sm = np.array([r["s_min"] for r in recs])

    def spec(y):
        y = y - np.mean(y)
        f = np.fft.rfftfreq(len(y), d=(t[1] - t[0]))
        a = np.abs(np.fft.rfft(y * np.hanning(len(y))))
        return f, a
    f_e, a_e = spec(eb)
    f_s, a_s = spec(sm)
    ev = np.linalg.eigvalsh(vacuum_hessian_delta(delta, wscale))
    freqs = np.sqrt(np.maximum(ev, 0.0))
    pk_e = float(f_e[1:][np.argmax(a_e[1:])] * 2 * np.pi)
    pk_s = float(f_s[1:][np.argmax(a_s[1:])] * 2 * np.pi)
    out = {"task": "M5.20.1", "blob_of": tag, "delta": delta,
           "center": [rho_c, z_c], "T": T, "dt": dt,
           "E_blob_first_last": [float(eb[0]), float(eb[-1])],
           "s_min_first_last": [float(sm[0]), float(sm[-1])],
           "omega_peak_E": pk_e, "omega_peak_s": pk_s,
           "vacuum_mass_omegas": freqs.tolist(),
           "trajectory": recs, "wall_s": round(wall, 1)}
    with open(os.path.join(DATA, f"m5_20_1_blob_{tag}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    fig, axes = plt.subplots(1, 3, figsize=(15, 3.4))
    axes[0].plot(t, eb)
    axes[0].set_title(f"{tag}: E_blob(t) (r<8 of ({rho_c:.0f},{z_c:.0f}))",
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
    axes[2].set_title(f"breathing spectrum vs (1,{delta},0) mass lines",
                      fontsize=9)
    fig.tight_layout()
    path = os.path.join(PLOTS, f"m5_20_1_blob_{tag}.png")
    fig.savefig(path, dpi=110)
    print(f"[blob:{tag}] E_blob {eb[0]:.3f}->{eb[-1]:.3f}, s_min "
          f"{sm[0]:.2f}->{sm[-1]:.2f}, omega_peak(s) {pk_s:.4f}, "
          f"vacuum omegas {np.round(freqs, 4)}, wall {wall:.0f}s")
    print("wrote", path)


if __name__ == "__main__":
    main(ARGV[0], float(ARGV[1]) if len(ARGV) > 1 else 300.0)
