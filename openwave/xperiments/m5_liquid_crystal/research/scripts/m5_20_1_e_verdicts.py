"""M5.20.1 phase E: endpoint verdicts, maps, core hunt (classifier v2).

The M5.20 verdict stack (m5_20_b1_verdicts + m5_20_b2_maps) with the two
DOCUMENTED M5.20 instrument bugs fixed BEFORE re-use (the precondition row
in m5_20_1_task_details.md):

  FIX 1 (guard evasion, m5_19_d1_relax.py:103-105 lesson): the winding read
        samples the circle by BILINEAR interpolation and the degeneracy
        guard tests the interpolated anisotropy (the M5.20 audit traced
        every spurious +-0.5/1.0 read to nearest-cell guard evasion).
  FIX 2 (pre-registration drift): RADIATES now requires the full
        pre-registered conjunction: sponge-absorbed fraction > 5% of
        E_seed post-transient AND still growing AND the ring radius
        DECLINING in concert.

Verdicts (pre-registered, m5_20_1_task_details.md DoD 5)
    HELD     endpoint bilinear reads (>= 3 valid r_w) all within 0.1 of
             the seed |q|, AND the core hunt's top peak is wound, AND
             m13_max in the last quarter stays >= half seed amplitude
    UNWOUND  endpoint reads < 0.1 (or guarded-nan with the m13 cloud at
             debris level) AND no wound peak in the core hunt
    RADIATES sponge runs: the FIX-2 conjunction
    MIXED    anything else (adjudicated by the maps + audit)

Also per run: the CORE-EQUALIZATION payload (DoD 3b): which pair the run
holds equalized (last-quarter majority + final core spectrum).

Usage: python m5_20_1_e_verdicts.py <run_tag> [...]   (verdicts + JSON)
       python m5_20_1_e_verdicts.py --maps <run_tag> [...]  (+ endpoint maps)
Out:   ../data/m5_20_1_verdicts.json, ../plots/m5_20_1_endpoints_<set>.png
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

from m5_17_energy import curvature_density_np                       # noqa: E402
from m5_18_spectral import potential_density_spec_np                # noqa: E402
from m5_20_1_b_seeds import cps_of, core_spectrum                   # noqa: E402
from m5_20_1_d_dynamics import NR, NZ, H, WSCALE                    # noqa: E402
from m5_19_d1_relax import ring_by_m13                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
RWS = (3.0, 4.0, 5.0, 6.0, 8.0)


def _bilin(F, rr, zz, h=H):
    """bilinear sample of a cell-centered included-cell field F[nr-1, nz-2]
    at physical (rho, z) points."""
    x = rr / h - 0.5
    y = zz / h + (NZ - 2) / 2 - 0.5
    i0 = np.clip(np.floor(x).astype(int), 0, NR - 3)
    j0 = np.clip(np.floor(y).astype(int), 0, NZ - 4)
    fx = np.clip(x - i0, 0.0, 1.0)
    fy = np.clip(y - j0, 0.0, 1.0)
    return ((1 - fx) * (1 - fy) * F[i0, j0] + fx * (1 - fy) * F[i0 + 1, j0]
            + (1 - fx) * fy * F[i0, j0 + 1] + fx * fy * F[i0 + 1, j0 + 1])


def winding_measure_bilin(Mnp, rho_c, z_c, r_w=4.0, npts=720,
                          aniso_min=0.02):
    """FIX 1: bilinear-interpolated eigenframe winding read; the guard
    tests the INTERPOLATED anisotropy minimum (no cell-sample evasion).
    Returns (q_meas, aniso_min_on_circle, mix_ratio)."""
    if not (np.all(np.isfinite(Mnp)) and np.isfinite(rho_c)
            and np.isfinite(z_c)):
        return float("nan"), float("nan"), float("nan")
    ang = np.linspace(0.0, 2.0 * np.pi, npts, endpoint=True)
    rr = rho_c + r_w * np.cos(ang)
    zz = z_c + r_w * np.sin(ang)
    if rr.min() < 0.5 * H:
        return float("nan"), float("nan"), float("nan")
    sub = Mnp[: NR - 1, 1:-1]
    m11 = _bilin(sub[..., 1, 1], rr, zz)
    m33 = _bilin(sub[..., 3, 3], rr, zz)
    m13 = _bilin(sub[..., 1, 3], rr, zz)
    m12 = _bilin(sub[..., 1, 2], rr, zz)
    m23 = _bilin(sub[..., 2, 3], rr, zz)
    aniso = np.sqrt((m11 - m33) ** 2 + 4.0 * m13 ** 2)
    amin = float(np.min(aniso))
    mix = float(np.max(np.sqrt(m12 ** 2 + m23 ** 2))
                / max(float(np.mean(aniso)), 1e-30))
    if amin < aniso_min or mix > 0.5:
        return float("nan"), amin, mix
    two_theta = np.arctan2(2.0 * m13, m11 - m33)
    dth = np.diff(two_theta)
    dth = (dth + np.pi) % (2.0 * np.pi) - np.pi
    return float(np.sum(dth) / (4.0 * np.pi)), amin, mix


def core_hunt(M, n_peaks=6, min_sep=6.0):
    """local maxima of |M13| + guarded bilinear winding reads (the
    load-bearing endpoint instrument per the M5.20 adjudication)."""
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
        p = {"rho": float(rho), "z": float(z), "m13": float(m13[i, j]),
             "q": {}}
        for rw in (3.0, 4.0, 5.0):
            q, amin, mix = winding_measure_bilin(M, rho, z, r_w=rw)
            p["q"][str(rw)] = (None if not np.isfinite(q)
                               else round(float(q), 3))
        peaks.append(p)
        if len(peaks) >= n_peaks:
            break
    return peaks


def classify(tag):
    with open(os.path.join(DATA, f"m5_20_1_run_{tag}.json")) as f:
        d = json.load(f)
    tr = d["trajectory"]
    t = np.array([r["t"] for r in tr])
    ke = np.array([r["KE"] for r in tr])
    ab = np.array([r["E_abs"] for r in tr])
    rho = np.array([r["ring13_rho"] if r["ring13_rho"] == r["ring13_rho"]
                    else np.nan for r in tr])
    m13 = np.array([r["m13_max"] for r in tr])
    E0 = tr[0]["PE"]
    # transient window: first local max of KE, doubled
    imax = 1
    for i in range(1, len(ke) - 1):
        if ke[i] >= ke[i - 1] and ke[i] >= ke[i + 1]:
            imax = i
            break
    t_w = 2.0 * t[imax]
    post = t >= t_w
    lastq = t >= t[-1] - 0.25 * (t[-1] - t[0])
    # endpoint reads (bilinear, FIX 1)
    st = np.load(os.path.join(DATA, f"m5_20_1_run_{tag}_state.npz"))
    M = st["M0"].astype(np.float64)
    rd = ring_by_m13(M, NR, NZ, H)
    reads = {}
    for rw in RWS:
        q, amin, mix = winding_measure_bilin(M, rd["ring13_rho"],
                                             rd["ring13_z"], r_w=rw)
        reads[str(rw)] = {"q": None if not np.isfinite(q)
                          else round(float(q), 4),
                          "aniso_min": (None if not np.isfinite(amin)
                                        else round(amin, 4)),
                          "mix": (None if not np.isfinite(mix)
                                  else round(mix, 4))}
    hunt = core_hunt(M)
    cs_end = core_spectrum(M, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
    # core-equalization payload: last-quarter majority
    eqs = [r.get("core_equalized") for r, m in zip(tr, lastq) if m]
    eq_counts = {k: eqs.count(k) for k in set(eqs)}
    # verdict
    qs = [v["q"] for v in reads.values() if v["q"] is not None]
    q_seed = abs(tr[0].get("q_meas") or 0.0)
    m13_seed = m13[0]
    held_wind = (len(qs) >= 3
                 and all(abs(abs(q) - q_seed) < 0.1 for q in qs))
    top_wound = bool(hunt and any(v is not None and abs(v) > 0.35
                                  for v in hunt[0]["q"].values()))
    m13_last_ok = bool(np.median(m13[lastq]) >= 0.5 * m13_seed)
    unwound_reads = ((len(qs) >= 3 and max(abs(q) for q in qs) < 0.1)
                     or (len(qs) == 0
                         and float(np.median(m13[lastq])) < 0.1 * m13_seed))
    no_wound_peak = not any(
        any(v is not None and abs(v) > 0.35 for v in p["q"].values())
        for p in hunt)
    ab_frac = float(ab[-1] / E0) if E0 else 0.0
    ab_post = ab[post]
    growing = (len(ab_post) > 4
               and (ab_post[-1] - ab_post[-len(ab_post) // 4])
               > 0.05 * max(ab_post[-1], 1e-30) and ab_frac > 0.0)
    rho_post = rho[post]
    rho_ok = rho_post[np.isfinite(rho_post)]
    ring_declining = bool(len(rho_ok) > 4
                          and (rho_ok[-1] - rho_ok[0]) < -1.0)
    if (d["mode"] == "sponge" and ab_frac > 0.05 and growing
            and ring_declining):
        verdict = "RADIATES"                       # FIX 2: full conjunction
    elif held_wind and top_wound and m13_last_ok \
            and (d["mode"] != "sponge" or ab_frac < 0.01):
        verdict = "HELD"
    elif unwound_reads and no_wound_peak:
        verdict = "UNWOUND"
    else:
        verdict = "MIXED"
    return {"tag": tag, "delta": d["delta"], "pairing": d["pairing"],
            "mode": d["mode"], "recal": d.get("recal", False),
            "T": d["T"], "E0": E0, "t_window": t_w,
            "q_seed": q_seed, "q_reads_endpoint": reads,
            "core_hunt_top3": hunt[:3],
            "m13_seed": float(m13_seed),
            "m13_lastq_median": float(np.median(m13[lastq])),
            "abs_frac": round(ab_frac, 5),
            "abs_growing": bool(growing),
            "ring_declining": ring_declining,
            "core_eq_lastq_counts": eq_counts,
            "core_spectrum_end": cs_end,
            "verdict": verdict}


def maps(tags, out="m5_20_1_endpoints.png"):
    fig, axes = plt.subplots(len(tags), 3,
                             figsize=(15, 3.6 * len(tags)), squeeze=False)
    for k, tag in enumerate(tags):
        with open(os.path.join(DATA, f"m5_20_1_run_{tag}.json")) as f:
            d = json.load(f)
        cps = cps_of(d["delta"])
        M = np.load(os.path.join(DATA, f"m5_20_1_run_{tag}_state.npz"))[
            "M0"].astype(np.float64)
        m13 = M[: NR - 1, 1:-1, 1, 3]
        msp = M[: NR - 1, 1:-1, 1:4, 1:4]
        s = np.linalg.eigvalsh(0.5 * (msp + np.swapaxes(msp, -1, -2)))[..., -1]
        dens = (curvature_density_np(M, H, 1.0)
                + potential_density_spec_np(M, d["wscale"], cps))
        ext = [0.5, NR - 1.5, -(NZ / 2 - 1.5), NZ / 2 - 1.5]
        for ax, arr, ttl, cm in (
                (axes[k, 0], np.abs(m13).T, f"{tag}: |M13|", "magma"),
                (axes[k, 1], s.T, "max eigenvalue s", "viridis"),
                (axes[k, 2], np.log10(np.maximum(dens, 1e-12)).T,
                 "log10 energy density", "inferno")):
            im = ax.imshow(arr, origin="lower", aspect="auto", extent=ext,
                           cmap=cm)
            ax.set_title(ttl, fontsize=9)
            plt.colorbar(im, ax=ax, shrink=0.8)
        for p in core_hunt(M):
            axes[k, 0].plot(p["rho"], p["z"], "c+", ms=8)
    fig.tight_layout()
    path = os.path.join(PLOTS, out)
    fig.savefig(path, dpi=110)
    print("wrote", path)


if __name__ == "__main__":
    args = ARGV
    do_maps = False
    if args and args[0] == "--maps":
        do_maps = True
        args = args[1:]
    out = {}
    for tag in args:
        try:
            out[tag] = classify(tag)
            e = out[tag]
            print(f"[{tag}] {e['verdict']}: q_reads "
                  f"{ {k: v['q'] for k, v in e['q_reads_endpoint'].items()} } "
                  f"core_eq {e['core_eq_lastq_counts']} "
                  f"abs {e['abs_frac']}")
        except FileNotFoundError as ex:
            print(f"[{tag}] SKIP ({ex})")
    path = os.path.join(DATA, "m5_20_1_verdicts.json")
    old = {}
    if os.path.exists(path):
        with open(path) as f:
            old = json.load(f)
    old.update(out)
    with open(path, "w") as f:
        json.dump(old, f, indent=1, default=float)
    print("wrote m5_20_1_verdicts.json")
    if do_maps and out:
        maps(list(out), out="m5_20_1_endpoints.png")
