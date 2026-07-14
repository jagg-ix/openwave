"""M5.21 phase A: the reusable snapshot instrument + GV0 analytic placeholders.

The headless matplotlib panel renderer previewing the launcher viz features
(m5_4b_rendering_features.md Parts 3-4) on axisym (rho, z) cross-sections:
the rendering-block feeder. Validated BEFORE any physics state exists (the
m5_4b section-5.3 placeholder-sample strategy): every channel is gated
against analytic fields with known answers.

PANEL SET (one snapshot; launcher analogs in parentheses)
    glyphs   director segment (leading eigenvector of the spatial block)
             + the DELTA-AXIS TICK (middle eigenvector): the m5_4b 4.1.1
             correction: the director is the axle, only the delta-axis
             sweeping around it shows the clock; grayness = activated
             potential V4(M) (Duda's ellipse-diagram language); glyphs FADE
             where the relevant eigenvalue gap is below a floor (the
             near-degenerate frame is meaningless there)  (glyph states 0/1)
    A        amplitude: gauge-safe SPECTRAL deviation from the vacuum
             eta-spectrum, sqrt(SUM_i (lam_i - lam_i^vac)^2)      (WM2 Amp)
    clock    ||Mdot||_F per cell                              (WM3 Clock w)
    energy   u_eta + V4 density                               (WM4 Energy H)
    charge   director splay |div n| (SIGN-GAUGE-SAFE: apolar director signs
             are aligned pairwise for the derivative, and n itself is
             oriented against a reference (radial from the defect) before
             the undifferentiated 1/rho terms; the m5_4b section-3 caveat:
             the raw signed splay flips spuriously)             (WM6 EM div)
    curl     |curl n| (the B analog: ~0 for the static charge) (WM7 EM curl)

GLYPH VARIANTS (the launcher size/color toggles, one flag)
    structure  unit-length eigenvector projections, activation-gray color
               (the far-field / structure-everywhere view)
    strength   segment length scaled by its eigenvalue / lam_ref
               (the field-strength view)
    In BOTH, the drawn length carries the IN-PLANE projection fraction:
    a delta-axis rotating out of the cross-section plane shortens its tick
    and that oscillation is the rendered clock.

CYLINDRICAL OPERATORS (equivariant field, phi = 0 half-plane; component
fields are phi-independent, so d_phi terms drop):
    div n  = d_rho n1 + n1/rho + d_z n3
    curl   = (-d_z n2,  d_z n1 - d_rho n3,  d_rho n2 + n2/rho)
    analytic hedgehog anchor: div rhat = 2/r EXACTLY (the GV0 splay gate),
    curl rhat = 0.

GV0 GATES (all must pass before the instrument touches physics)
    GV0a  uniform J-commuting vacuum diag(-g, a, a, b), b > a:
          u_eta == 0 exactly; V4 uniform (< 1e-12 rel spread); amplitude
          == 0; director gap-defined everywhere; delta-tick MASKED
          everywhere (the (a, a) pair is degenerate: the mask must fire)
    GV0b  pure analytic hedgehog (s = 1): median |r * splay / 2 - 1| < 2%
          and u_eta * r^4 == 8 within 2% (both FD-limited, annulus away
          from core + boundaries); curl n is TRUNCATION-limited: h -> h/2
          shrinks max |curl| in the same physical annulus by ~4x (ratio in
          (3, 5.5): clean h^2 scaling; first run at h = 1 measured 3.3e-4,
          consistent with the h^2/r^3 estimate at the annulus inner edge)
          and curl stays < 1% of the splay signal there
    GV0c  synthetic rotator (n = yhat out-of-plane: the clock face points
          at the viewer; the (delta, 0) eigenframe swept in the (rho, z)
          cross-section at seeded theta_k = omega t_k): rendered
          delta-axis phase == seeded (< 1e-6 rad, apolar mod pi); omega
          from the Mdot channel == seeded (< 1e-12 rel); omega from the
          multi-frame phase fit == seeded (< 1e-9 rel)

Run:  python m5_21_a_snap.py gv0
Out:  ../data/m5_21_a_gates.json, ../plots/m5_21_a_placeholders.png,
      ../plots/m5_21_a_rotator_strip.png
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import LineCollection  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords, hedgehog_field               # noqa: E402
from m5_20_2_a_eom import (ETA, G_T, u_eta_density, v4_density,    # noqa: E402
                           WSCALE)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
os.makedirs(DATA, exist_ok=True)
os.makedirs(PLOTS, exist_ok=True)


# ================= eigen-frame fields =================
def eig_fields(Mnp):
    """spatial-block eigendecomposition per cell, DESCENDING eigenvalues.
    lam[..., k], evec[..., :, k]: k = 0 director, 1 delta-axis, 2 minor."""
    S = Mnp[..., 1:4, 1:4]
    lam, V = np.linalg.eigh(S)
    return lam[..., ::-1], V[..., :, ::-1]


def orient(n, ref):
    """flip apolar vectors so n . ref >= 0 (defect-relative sign gauge)."""
    s = np.sign(np.sum(n * ref, axis=-1, keepdims=True))
    s[s == 0.0] = 1.0
    return n * s


def _aligned_central(n, axis, h):
    """central difference of an APOLAR unit-vector field: each neighbour is
    sign-aligned to the centre cell before differencing (m5_4b section-3
    caveat). Outer one-cell ring is invalid (roll wrap): mask downstream."""
    npl = np.roll(n, -1, axis=axis)
    nmi = np.roll(n, 1, axis=axis)
    sp = np.sign(np.sum(npl * n, axis=-1, keepdims=True))
    sm = np.sign(np.sum(nmi * n, axis=-1, keepdims=True))
    sp[sp == 0.0] = 1.0
    sm[sm == 0.0] = 1.0
    return (sp * npl - sm * nmi) / (2.0 * h)


def splay_curl(n, R, h):
    """cylindrical |div n| and |curl n| of the equivariant director field at
    phi = 0 (components (n1, n2, n3) = (rho, phi, z)); n must already be
    orientation-fixed (orient()) for the undifferentiated 1/rho terms."""
    dr = _aligned_central(n, 0, h)
    dz = _aligned_central(n, 1, h)
    div = dr[..., 0] + n[..., 0] / R + dz[..., 2]
    c1 = -dz[..., 1]
    c2 = dz[..., 0] - dr[..., 2]
    c3 = dr[..., 1] + n[..., 1] / R
    curl = np.sqrt(c1 ** 2 + c2 ** 2 + c3 ** 2)
    valid = np.zeros(n.shape[:2], dtype=bool)
    valid[1:-1, 1:-1] = True
    return np.abs(div), curl, valid


def spectral_amplitude(Mnp, vac_eta_spectrum):
    """gauge-safe amplitude: Frobenius distance of the ORDERED eta-spectrum
    from the vacuum spectrum, sqrt(sum_i (lam_i - lam_i^vac)^2). Uses the
    full 4x4 eta-spectrum (eigvals of eta M, sorted descending)."""
    lam = np.sort(np.linalg.eigvals(ETA[None, None] @ Mnp).real,
                  axis=-1)[..., ::-1]
    ref = np.sort(np.asarray(vac_eta_spectrum))[::-1]
    return np.sqrt(np.sum((lam - ref) ** 2, axis=-1))


def clock_phase(Mnp, e1, e2):
    """delta-axis phase per cell in the (e1, e2) reference plane, apolar
    (mod pi). e1/e2: fixed orthonormal 3-vectors perpendicular to the
    director at the probe region."""
    _, V = eig_fields(Mnp)
    m = V[..., :, 1]
    return np.mod(np.arctan2(np.sum(m * e2, -1), np.sum(m * e1, -1)), np.pi)


# ================= the panel renderer =================
PANELS = ("glyphs", "A", "clock", "energy", "charge", "curl")
CMAPS = {"A": "inferno", "clock": "cividis", "energy": "magma",
         "charge": "viridis", "curl": "plasma"}


def _extent(R, Z):
    return [Z.min(), Z.max(), R.min(), R.max()]


def channel_maps(Mnp, R, Z, h, delta, g=G_T, Vdot=None, orient_ref=None,
                 vac_spec=None):
    """all heat-map channels for one state; density channels live on the
    included cells [0:nr-1, 1:nz-1] and are padded back to full shape."""
    nr, nz = Mnp.shape[:2]
    if vac_spec is None:
        vac_spec = (g, 1.0, delta, 0.0)
    lam, V = eig_fields(Mnp)
    n = V[..., :, 0]
    if orient_ref is None:
        rr = np.sqrt(R ** 2 + Z ** 2)
        rr = np.where(rr < 1e-12, 1e-12, rr)
        orient_ref = np.stack([R / rr, np.zeros_like(R), Z / rr], axis=-1)
    n = orient(n, orient_ref)
    splay, curl, valid = splay_curl(n, R, h)
    full = np.full((nr, nz), np.nan)
    ue = full.copy()
    ue[: nr - 1, 1:-1] = u_eta_density(Mnp, h)
    v4 = full.copy()
    v4[: nr - 1, 1:-1] = v4_density(Mnp, WSCALE, delta, g)
    clock = (np.linalg.norm(Vdot, axis=(-2, -1)) if Vdot is not None
             else np.zeros((nr, nz)))
    return {"lam": lam, "evec": V, "n": n,
            "A": spectral_amplitude(Mnp, vac_spec),
            "clock": clock, "energy": ue + v4, "v4": v4,
            "charge": np.where(valid, splay, np.nan),
            "curl": np.where(valid, curl, np.nan)}


def glyph_collections(ch, R, Z, h, step=6, mode="structure",
                      gap_floor_frac=0.05, vact_norm=None):
    """director segments + delta-axis ticks as LineCollections.
    In-plane projection: plot x = z-component (axis 3), plot y = rho-
    component (axis 1); out-of-plane = axis 2 (the phi direction).
    Fading: alpha -> 0.12 where the defining eigenvalue gap is below
    gap_floor_frac * global gap scale (blindspot 4)."""
    lam, V = ch["lam"], ch["evec"]
    sub = (slice(step // 2, None, step), slice(step // 2, None, step))
    lam_s = lam[sub]
    V_s = V[sub]
    Xc, Yc = Z[sub], R[sub]
    g01 = lam_s[..., 0] - lam_s[..., 1]
    g12 = lam_s[..., 1] - lam_s[..., 2]
    gscale = max(float(np.nanmax(lam[..., 0] - lam[..., 2])), 1e-30)
    vact = (vact_norm[sub] if vact_norm is not None
            else np.zeros_like(g01))
    L = 0.46 * step * h
    lam_ref = max(float(np.nanmax(np.abs(lam_s))), 1e-30)
    segs_d, segs_t, col_d, col_t = [], [], [], []
    it = np.ndindex(Xc.shape)
    for idx in it:
        d = V_s[idx][:, 0]
        m = V_s[idx][:, 1]
        sc_d = sc_t = 1.0
        if mode == "strength":
            sc_d = abs(lam_s[idx][0]) / lam_ref
            sc_t = abs(lam_s[idx][1]) / lam_ref
        dx, dy = d[2] * L * sc_d, d[0] * L * sc_d
        tx, ty = m[2] * 0.55 * L * sc_t, m[0] * 0.55 * L * sc_t
        x0, y0 = Xc[idx], Yc[idx]
        segs_d.append([(x0 - dx, y0 - dy), (x0 + dx, y0 + dy)])
        segs_t.append([(x0 - tx, y0 - ty), (x0 + tx, y0 + ty)])
        a_d = 1.0 if g01[idx] > gap_floor_frac * gscale else 0.12
        a_t = (1.0 if min(g01[idx], g12[idx]) > gap_floor_frac * gscale
               else 0.12)
        gr = 0.55 - 0.45 * min(float(vact[idx]), 1.0)
        col_d.append((gr, gr, gr, a_d))
        col_t.append((0.86, 0.08, 0.24, a_t))
    lc_d = LineCollection(segs_d, colors=col_d, linewidths=1.6)
    lc_t = LineCollection(segs_t, colors=col_t, linewidths=2.0)
    masks = {"director_defined_frac":
             float(np.mean(g01 > gap_floor_frac * gscale)),
             "tick_defined_frac":
             float(np.mean(np.minimum(g01, g12) > gap_floor_frac * gscale))}
    return lc_d, lc_t, masks


def render_panels(ax_row, Mnp, R, Z, h, delta, g=G_T, Vdot=None,
                  glyph_mode="structure", step=6, title="",
                  panels=PANELS, orient_ref=None, vac_spec=None,
                  log_channels=(), norms=None, zoom=None):
    """one snapshot -> one row of panels. Returns the channel dict (so the
    caller can gate on the same numbers that were rendered).
    log_channels: channel names drawn with a log colour scale (for 1/r^4-
    type fields a linear scale saturates); norms: {name: (vmin, vmax)}
    to share colour scales across film-strip rows; zoom: (z0, z1, r0, r1)
    plot window."""
    ch = channel_maps(Mnp, R, Z, h, delta, g, Vdot, orient_ref, vac_spec)
    vmax_v4 = max(float(np.nanmax(ch["v4"])), 1e-30)
    ext = _extent(R, Z)
    win = zoom if zoom is not None else ext
    for ax, name in zip(ax_row, panels):
        if name == "glyphs":
            lc_d, lc_t, masks = glyph_collections(
                ch, R, Z, h, step=step, mode=glyph_mode,
                vact_norm=np.nan_to_num(ch["v4"] / vmax_v4))
            ch["glyph_masks"] = masks
            ax.set_facecolor("#f4f2ee")
            ax.add_collection(lc_d)
            ax.add_collection(lc_t)
            ax.set_aspect("equal")
            ax.set_title(f"{title} glyphs ({glyph_mode}; tick = delta-axis)",
                         fontsize=7)
        else:
            data = ch[name]
            kw = {"cmap": CMAPS[name]}
            if norms and name in norms:
                kw["vmin"], kw["vmax"] = norms[name]
            if name in log_channels:
                pos = data[np.isfinite(data) & (data > 0)]
                if pos.size:
                    vmax = kw.pop("vmax", float(pos.max()))
                    vmin = kw.pop("vmin", None)
                    if not vmin or vmin <= 0:
                        vmin = max(float(np.percentile(pos, 1.0)),
                                   vmax * 1e-8)
                    kw["norm"] = matplotlib.colors.LogNorm(vmin=vmin,
                                                           vmax=vmax)
                    data = np.where(data > 0, data, np.nan)
            im = ax.imshow(data, origin="lower", aspect="equal",
                           extent=ext, **kw)
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.02)
            ax.set_title(f"{title} {name}"
                         + (" (log)" if name in log_channels else ""),
                         fontsize=7)
        ax.set_xlim(win[0], win[1])
        ax.set_ylim(win[2], win[3])
        ax.set_xlabel("z", fontsize=6)
        ax.set_ylabel("rho", fontsize=6)
        ax.tick_params(labelsize=5)
    return ch


def film_strip(states, R, Z, h, delta, path, g=G_T, panels=PANELS,
               glyph_mode="structure", step=6, suptitle="",
               log_channels=(), norms=None, zoom=None, title_fn=None):
    """rows = timesteps, columns = panels; states = [{t, M, V(optional)}].
    title_fn(st) overrides the default per-row title (the 2026-07-14 film
    standard passes the steps + tu [+ s] title through here; see
    research/m5_visualization.md)."""
    nrow, ncol = len(states), len(panels)
    fig, axes = plt.subplots(nrow, ncol,
                             figsize=(2.9 * ncol, 2.2 * nrow), squeeze=False)
    chans = []
    for i, st in enumerate(states):
        ttl = title_fn(st) if title_fn else f"t={st['t']:g}"
        chans.append(render_panels(
            axes[i], st["M"], R, Z, h, delta, g, st.get("V"),
            glyph_mode=glyph_mode, step=step,
            title=ttl, panels=panels,
            orient_ref=st.get("orient_ref"), vac_spec=st.get("vac_spec"),
            log_channels=log_channels, norms=norms, zoom=zoom))
    if suptitle:
        fig.suptitle(suptitle, fontsize=15)
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
    print("wrote", os.path.relpath(path, HERE))
    return chans


# ================= GV0 placeholders =================
NRA, NZA, HA = 96, 192, 1.0
DELTA_A = 0.3


def placeholder_vacuum():
    """uniform J-commuting state diag(-g, a, a, b), b > a: zero curvature
    exactly, uniform V4, degenerate (a, a) pair (the delta-tick mask must
    fire), well-defined director (zhat)."""
    M = np.zeros((NRA, NZA, 4, 4))
    M[..., 0, 0], M[..., 1, 1], M[..., 2, 2], M[..., 3, 3] = (
        -G_T, 0.4, 0.4, 0.9)
    return M


def gate_gv0a(R, Z):
    M = placeholder_vacuum()
    ch = channel_maps(M, R, Z, HA, DELTA_A,
                      vac_spec=(G_T, 0.9, 0.4, 0.4))
    u_max = float(np.nanmax(np.abs(
        ch["energy"] - ch["v4"])))                     # u_eta part only
    v4v = ch["v4"][np.isfinite(ch["v4"])]
    v4_spread = float((v4v.max() - v4v.min())
                      / max(abs(v4v.mean()), 1e-300))
    a_max = float(np.nanmax(ch["A"]))
    _, _, masks = glyph_collections(ch, R, Z, HA)
    ok = (u_max < 1e-12 and v4_spread < 1e-12 and a_max < 1e-9
          and masks["director_defined_frac"] == 1.0
          and masks["tick_defined_frac"] == 0.0)
    return ok, {"u_eta_max": u_max, "v4_rel_spread": v4_spread,
                "amplitude_max": a_max, **masks}, ch, M


def _hedgehog_curl_max(nr, nz, h):
    R, Z = grid_coords(nr, nz, h)
    M = hedgehog_field(R, Z, -1.0)
    M[..., 0, 0] = -G_T
    lam, V = eig_fields(M)
    rr = np.sqrt(R ** 2 + Z ** 2)
    rr = np.where(rr < 1e-12, 1e-12, rr)
    n = orient(V[..., :, 0],
               np.stack([R / rr, np.zeros_like(R), Z / rr], axis=-1))
    splay, curl, valid = splay_curl(n, R, h)
    ann = ((rr > 12.0) & (rr < 34.0) & (R > 2.0)
           & (np.abs(Z) < Z.max() - 3.0 * h) & valid)
    return float(np.nanmax(curl[ann])), float(np.nanmax(splay[ann]))


def gate_gv0b(R, Z):
    """pure hedgehog: splay * r == 2 and u_eta * r^4 == 8; curl proven
    truncation-limited by h-refinement (h^2 scaling) + << splay signal."""
    M = hedgehog_field(R, Z, -1.0)
    M[..., 0, 0] = -G_T                       # the g-timelike branch row
    ch = channel_maps(M, R, Z, HA, DELTA_A, vac_spec=(G_T, 1.0, 0.0, 0.0))
    r = np.sqrt(R ** 2 + Z ** 2)
    ann = (r > 12.0) & (r < 34.0) & (R > 2.0) & (np.abs(Z) < Z.max() - 3.0)
    splay_err = float(np.nanmedian(
        np.abs(ch["charge"][ann] * r[ann] / 2.0 - 1.0)))
    u = ch["energy"] - ch["v4"]
    u_err = float(np.nanmedian(np.abs(u[ann] * r[ann] ** 4 / 8.0 - 1.0)))
    curl_h, splay_h = _hedgehog_curl_max(NRA, NZA, HA)
    curl_h2, _ = _hedgehog_curl_max(2 * NRA, 2 * NZA, HA / 2.0)
    ratio = curl_h / max(curl_h2, 1e-300)
    ok = (splay_err < 0.02 and u_err < 0.02 and 3.0 < ratio < 5.5
          and curl_h < 0.01 * splay_h)
    return ok, {"splay_2r_medrelerr": splay_err,
                "u_8r4_medrelerr": u_err, "curl_max_annulus": curl_h,
                "curl_max_annulus_hhalf": curl_h2,
                "curl_h2_scaling_ratio": ratio,
                "curl_over_splay": curl_h / max(splay_h, 1e-300)}, ch, M


def rotator_state(theta, omega, R, Z):
    """director OUT OF PLANE (n = yhat, the phi direction: the clock face
    points at the viewer), the (delta, 0) pair swept IN the (rho, z) cross-
    section: delta-axis d = (cos th, 0, sin th), minor = (-sin th, 0,
    cos th); M_sp = n n^T + delta d d^T. Exact velocity Mdot = omega
    (W M - M W), W the rotation generator about yhat. Synthetic: rendering-
    validation only, no energetics asserted; the tick VISIBLY rotates."""
    c, s = np.cos(theta), np.sin(theta)
    d = np.array([c, 0.0, s])
    n = np.array([0.0, 1.0, 0.0])
    S = np.outer(n, n) + DELTA_A * np.outer(d, d)
    M = np.zeros((NRA, NZA, 4, 4))
    M[..., 1:4, 1:4] = S
    M[..., 0, 0] = -G_T
    W = np.zeros((4, 4))                     # rotation about spatial yhat:
    W[1, 3], W[3, 1] = -1.0, 1.0             # takes xhat -> zhat
    V = omega * (W @ M - M @ W)
    return M, V, W


def gate_gv0c(R, Z):
    omega = 0.05
    ts = np.array([0.0, 4.0, 8.0, 12.0])
    e1 = np.array([1.0, 0.0, 0.0])
    e2 = np.array([0.0, 0.0, 1.0])
    yhat = np.array([0.0, 1.0, 0.0])
    ref = np.broadcast_to(yhat, (NRA, NZA, 3))
    phases, w_mdot = [], []
    states = []
    for t in ts:
        th = omega * t
        M, V, W = rotator_state(th, omega, R, Z)
        ph = float(np.median(clock_phase(M, e1, e2)))
        phases.append(ph)
        denom = float(np.linalg.norm(W @ M[0, 0] - M[0, 0] @ W))
        w_mdot.append(float(np.linalg.norm(V[0, 0])) / max(denom, 1e-300))
        states.append({"t": t, "M": M, "V": V, "orient_ref": ref,
                       "vac_spec": (G_T, 1.0, DELTA_A, 0.0)})
    # apolar mod-pi read vs seeded: eigh descending gives lam = (1, delta,
    # 0), so the middle eigenvector IS the swept delta-axis d(theta)
    seeded = np.mod(omega * ts, np.pi)
    ph_err = float(np.max(np.abs(np.array(phases) - seeded)))
    w_err = float(np.max(np.abs(np.array(w_mdot) - omega) / omega))
    # multi-frame fit: unwrap apolar phase, slope vs t
    ph_un = np.unwrap(np.array(phases), period=np.pi)
    w_fit = float(np.polyfit(ts, ph_un, 1)[0])
    wfit_err = abs(w_fit - omega) / omega
    ok = ph_err < 1e-6 and w_err < 1e-12 and wfit_err < 1e-9
    detail = {"phase_read": phases, "phase_seeded": seeded.tolist(),
              "phase_maxerr": ph_err, "omega_mdot_relerr": w_err,
              "omega_fit": w_fit, "omega_fit_relerr": wfit_err}
    return ok, detail, states


def main_gv0():
    R, Z = grid_coords(NRA, NZA, HA)
    out = {"task": "M5.21", "phase": "A", "delta": DELTA_A, "g": G_T,
           "grid": [NRA, NZA, HA]}
    oka, deta, cha, Ma = gate_gv0a(R, Z)
    out["GV0a_vacuum"] = {"ok": bool(oka), "detail": deta}
    print(f"[GV0a] {'PASS' if oka else 'FAIL'} "
          + json.dumps(deta, default=float)[:220])
    okb, detb, chb, Mb = gate_gv0b(R, Z)
    out["GV0b_hedgehog"] = {"ok": bool(okb), "detail": detb}
    print(f"[GV0b] {'PASS' if okb else 'FAIL'} "
          + json.dumps(detb, default=float)[:220])
    okc, detc, rot_states = gate_gv0c(R, Z)
    out["GV0c_rotator"] = {"ok": bool(okc), "detail": detc}
    print(f"[GV0c] {'PASS' if okc else 'FAIL'} "
          + json.dumps(detc, default=float)[:220])
    out["GV0"] = {"ok": bool(oka and okb and okc)}
    # figures: the three placeholders (one row each: vacuum / hedgehog /
    # rotator t=0) + the rotator film-strip (the mini demo of the format)
    film_strip(
        [{"t": 0.0, "M": Ma, "vac_spec": (G_T, 0.9, 0.4, 0.4)},
         {"t": 0.0, "M": Mb, "vac_spec": (G_T, 1.0, 0.0, 0.0)},
         rot_states[0]],
        R, Z, HA, DELTA_A,
        os.path.join(PLOTS, "m5_21_a_placeholders.png"),
        suptitle="M5.21-A GV0 placeholders: vacuum / analytic hedgehog / "
                 "synthetic rotator (rows)")
    film_strip(
        rot_states, R, Z, HA, DELTA_A,
        os.path.join(PLOTS, "m5_21_a_rotator_strip.png"), step=12,
        suptitle="M5.21-A film-strip demo: synthetic rotator, director "
                 "out-of-plane (clock face toward viewer), delta-axis tick "
                 "sweeping at seeded omega = 0.05")
    with open(os.path.join(DATA, "m5_21_a_gates.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote data/m5_21_a_gates.json")
    print(f"[GV0] {'PASS' if out['GV0']['ok'] else 'FAIL'}")
    return out


if __name__ == "__main__":
    main_gv0()
