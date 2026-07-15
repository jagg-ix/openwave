"""M5.12 phase D2a: the DRESSED-STATE class + the GEM-dip scan on the
calibrated instrument (block 3; the audited D1's specified next rung).

WHY THIS CLASS (D1 audit, 2026-07-07): for zero-time-mixing textures the
boost channel's sign is algebraically forced and background-dominated, and
the defect-attributed part is POSITIVE: the uniform-rotation clock on
undressed fields cannot stabilize. The M5.8 heritage (the GEM dip: a
boost-DRESSED hedgehog at E* = 2.61 < bare 6.14, quartic sandbox) lives in
states whose time row/col is genuinely dressed. D2a builds that class on
the VERIFIED Lagrangian + spectral potential and asks the static question
first: does boost dressing LOWER the defect energy here (vacuum-subtracted,
per the audit's discipline)?

THE 4D STATIC ENERGY (dressed class, instrument normalization):
    E = c2 . 4 . SUM_{i<j} inner_eta(C_ij, C_ij)  +  w . V_4D
    C_ij = [d_i M, d_j M]_eta,  inner_eta = double internal eta raising
    V_4D = SUM_{p=1..4} ( Tr_eta(M^p) - c_p )^2 ,  c_p = g^p + 1  (delta=0,
    targets (g, 1, 0, 0));  the COVARIANT vacuum has m00 = -g
    (m5_18_verification_note § 5). UNDRESSED LIMIT (gate DG1): with
    m00 = -g uniform and zero mixing, inner_eta == plain Frobenius EXACTLY
    (curvature identical to the calibrated stack), and
        V_4D == V_3D + w (Tr(M_sp^4) - 1)^2
    i.e. the 4D form legitimately ADDS the p = 4 invariant (4 power sums
    are needed to pin 4 eigenvalues; p <= 3 leaves spurious vacua). The
    dressed-class statics therefore differ from the 3D-calibrated ones by
    the p4 term even at zero mixing: dip scans below are INTERNALLY
    consistent (same E_4D for dressed and undressed, defect and control);
    absolute recalibration under V_4D is deferred (labeled).
    g = G_TIME = 8 working value (labeled: in the dressed class g is no
    longer decoupled; the physical g ~ 1e10 scaling is an open axis).

THE DRESSING: pointwise boost conjugation
    M_b(x) = Lam(-b(x)) M(x) Lam(-b(x))     (boost Lam symmetric)
    Lam(b) = expm(b eta W_B03) = I + sinh(b) K + (cosh(b) - 1) K^2
    (closed form, K = eta W_B03, K^3 = K), b(x) = b0 exp(-r_def^2 / w^2).
    B03 is the axisymmetry-compatible boost. Conjugation preserves V
    pointwise on vacuum orbits; the curvature responds: the dip question.

READOUT (the audit's vacuum-subtraction discipline):
    dip_def(b0) = [E(defect, b0) - E(defect, 0)]
                - [E(control, b0) - E(control, 0)],
    control = the same boundary/far-field texture WITHOUT the defect
    (vacuum n = z interior). A dip (dip_def < 0 with an interior minimum
    in b0) = the defect-localized GEM-dip on the calibrated instrument.

GATES: DG1 undressed identity; DG2 boosted-vacuum V = 0 (orbit) +
uniform-boost curvature isometry; DG3 closed-form Lam == scipy expm;
DG4 mixing components actually enter (a deliberate eta-vs-plain contrast).

Run:  python m5_12_dressed.py gates
      python m5_12_dressed.py scan
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

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import G_TIME, MIR, J4, cell_weights, grid_coords       # noqa: E402
from m5_18_spectral import run_radial, total_energy_spec_np               # noqa: E402
from m5_12_core_pin import load_wscale                                    # noqa: E402
from m5_12_loop import loop_field                                         # noqa: E402
from m5_12_clock_q import ETA, comm_eta_v, inner_eta_v, spatial_channels  # noqa: E402


# ---------------- the 4D static energy on the dressed class ----------------
def curvature_eta_density(Mnp, h, c2=1.0):
    """c2 . 4 . SUM_{i<j} inner_eta(C_ij, C_ij) on included cells (the
    instrument normalization: reduces to curvature_density_np on
    zero-time-mixing fields)."""
    Mc, Arho, Aphi, Az = spatial_channels(Mnp, h)
    c1 = comm_eta_v(Arho, Aphi)
    c2_ = comm_eta_v(Arho, Az)
    c3 = comm_eta_v(Aphi, Az)
    return c2 * 4.0 * (inner_eta_v(c1, c1) + inner_eta_v(c2_, c2_)
                       + inner_eta_v(c3, c3))


def v4d_density(Mnp, wscale, g=G_TIME):
    """V_4D = w SUM_{p=1..4} (Tr_eta(M^p) - c_p)^2, c_p = g^p + 1 (delta=0),
    on included cells."""
    Mc = Mnp[: Mnp.shape[0] - 1, 1:-1]
    EM = np.einsum("ab,...bc->...ac", ETA, Mc)
    v = np.zeros(Mc.shape[:2])
    P = EM
    for p in range(1, 5):
        cp = g ** p + 1.0
        tr = np.einsum("...aa->...", P)
        v += (tr - cp) ** 2
        if p < 4:
            P = np.einsum("...ab,...bc->...ac", P, EM)
    return wscale * v


def e_total_4d(Mnp, wscale, h):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return float(np.sum((curvature_eta_density(Mnp, h)
                         + v4d_density(Mnp, wscale)) * w))


# ---------------- the boost dressing (closed form) ----------------
K_B03 = ETA @ np.array([[0.0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0],
                        [-1.0, 0, 0, 0]])          # K = eta W, K^3 = K
P_B03 = K_B03 @ K_B03


def lam_boost(b):
    """Lam(b) = I + sinh(b) K + (cosh(b)-1) K^2; b is (...,) array."""
    b = np.asarray(b)[..., None, None]
    return (np.eye(4) + np.sinh(b) * K_B03 + (np.cosh(b) - 1.0) * P_B03)


def dress(Mnp, bmap):
    """M_b = Lam(-b) M Lam(-b) per cell (boost Lam symmetric)."""
    L = lam_boost(-bmap)
    return np.einsum("...ab,...bc,...cd->...ad", L, Mnp, L)


def to_covariant(Mnp, g=G_TIME):
    """instrument field (m00 = +g) -> covariant 4D class (m00 = -g)."""
    Mx = Mnp.copy()
    Mx[..., 0, 0] = -g
    return Mx


# ---------------- gates ----------------
def run_gates(nr=48, nz=96, h=1.0):
    from scipy.linalg import expm
    from m5_17_energy import hedgehog_field, curvature_density_np
    from m5_18_spectral import potential_density_spec_np
    wscale = 0.31
    R, Z = grid_coords(nr, nz, h)
    M3 = hedgehog_field(R, Z, 6.0)          # instrument field, m00 = +g
    M4 = to_covariant(M3)
    w = cell_weights(nr, nz, h)
    res = {}
    # DG1: undressed identity (curvature AND potential, term by term)
    ec_eta = float(np.sum(curvature_eta_density(M4, h) * w))
    ec_std = float(np.sum(curvature_density_np(M4, h, 1.0) * w))
    ev_4d = float(np.sum(v4d_density(M4, wscale) * w))
    ev_3d = float(np.sum(potential_density_spec_np(M4, wscale) * w))
    res["DG1_curv_rel"] = abs(ec_eta - ec_std) / (abs(ec_std) + 1e-300)
    # potential decomposition: V_4D = V_3D + w (Tr(Msp^4) - 1)^2 exactly
    msp = M4[: nr - 1, 1:-1, 1:4, 1:4]
    m2 = np.einsum("...ab,...bc->...ac", msp, msp)
    tr4 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, m2))
    ev_p4 = float(np.sum(wscale * (tr4 - 1.0) ** 2 * w))
    res["DG1_pot_decomp_rel"] = abs(ev_4d - (ev_3d + ev_p4)) / (abs(ev_4d) + 1e-300)
    res["DG1_p4_term_share"] = ev_p4 / (ev_4d + 1e-300)
    # DG2: boosted vacuum: V = 0 on the orbit; uniform boost = isometry
    Mv = np.zeros((nr, nz, 4, 4))
    Mv[..., 0, 0] = -G_TIME
    Mv[..., 3, 3] = 1.0
    b_uni = np.full((nr, nz), 0.7)
    Mvb = dress(Mv, b_uni)
    res["DG2_boosted_vacuum_V"] = float(np.sum(v4d_density(Mvb, 1.0) * w))
    M4b_uni = dress(M4, b_uni)
    e_uni = e_total_4d(M4b_uni, wscale, h)
    e_0 = e_total_4d(M4, wscale, h)
    res["DG2_uniform_boost_isometry_rel"] = abs(e_uni - e_0) / (abs(e_0) + 1e-300)
    # DG3: closed-form Lam == scipy expm
    worst = 0.0
    for b in (-1.3, 0.2, 0.9, 2.0):
        W = np.zeros((4, 4)); W[0, 3], W[3, 0] = 1.0, -1.0
        worst = max(worst, float(np.max(np.abs(
            lam_boost(np.array(b))[()] - expm(ETA @ W * b)))))
    res["DG3_lam_closed_form"] = worst
    # DG4: dressing actually creates time-mixing + the eta version differs
    b_loc = 0.8 * np.exp(-((R ** 2 + Z ** 2) / 36.0))
    M4d = dress(M4, b_loc)
    mix = float(np.max(np.abs(M4d[..., 0, 1:])))
    ec_eta_d = float(np.sum(curvature_eta_density(M4d, h) * w))
    ec_std_d = float(np.sum(curvature_density_np(M4d, h, 1.0) * w))
    res["DG4_max_time_mixing"] = mix
    res["DG4_eta_vs_plain_rel"] = abs(ec_eta_d - ec_std_d) / (abs(ec_std_d) + 1e-300)
    ok = {
        "DG1 undressed identity (curv exact; pot = 3D + p4 term)": max(res["DG1_curv_rel"], res["DG1_pot_decomp_rel"]) < 1e-12,
        "DG2 boosted vacuum V = 0 + isometry": abs(res["DG2_boosted_vacuum_V"]) < 1e-9 and res["DG2_uniform_boost_isometry_rel"] < 1e-9,
        "DG3 closed-form boost == expm": res["DG3_lam_closed_form"] < 1e-12,
        "DG4 mixing enters + eta matters": mix > 0.1 and res["DG4_eta_vs_plain_rel"] > 1e-3,
    }
    for k, v in ok.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    for k, v in res.items():
        print(f"    {k} = {v:.3e}")
    res["all_pass"] = all(ok.values())
    with open(os.path.join(DATA, "m5_12_dressed_gates.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res["all_pass"]


# ---------------- the GEM-dip scan ----------------
def run_scan(nr=96, nz=192, h=1.0, b0s=(0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 1.6, 2.0),
             ws=(4.0, 8.0, 16.0)):
    wscale = load_wscale()
    t0 = time.time()
    out_r, Mb, _ = run_radial(nr, nz, h, iters=8000, rc_seed=8.0,
                              tag=f"spec_n{nr}_dressed")
    R, Z = grid_coords(nr, nz, h)
    pinb = None
    fields = {}
    # covariant class for all
    fields["hedgehog"] = (to_covariant(Mb), np.sqrt(R ** 2 + Z ** 2))
    Ml = loop_field(R, Z, 12.0, 0.5, 4.0)
    fields["loop_R12"] = (to_covariant(Ml),
                          np.sqrt((R - 12.0) ** 2 + Z ** 2))
    # controls: same far-field texture, no defect (combed interior), plus
    # the pure vacuum
    Mc_h = np.zeros_like(Mb)
    Mc_h[..., 3, 3] = 1.0
    Mc_h[..., 0, 0] = 1.0   # placeholder, covariant fix below
    Mc_h = to_covariant(Mc_h)
    from m5_16_axisym import pin_mask
    pin = pin_mask(nr, nz)
    Mctl_h = np.where(pin[..., None, None], to_covariant(Mb), Mc_h)
    fields["control_hedgehog_boundary"] = (Mctl_h, np.sqrt(R ** 2 + Z ** 2))
    Mctl_l = np.where(pin[..., None, None], to_covariant(Ml), Mc_h)
    fields["control_loop_boundary"] = (Mctl_l, np.sqrt((R - 12.0) ** 2 + Z ** 2))
    fields["vacuum"] = (Mc_h.copy(), np.sqrt(R ** 2 + Z ** 2))
    rows = []
    for fname, (M4, r_def) in fields.items():
        E0 = e_total_4d(M4, wscale, h)
        for wb in ws:
            curve = []
            for b0 in b0s:
                bmap = b0 * np.exp(-(r_def ** 2) / (wb ** 2))
                Ed = e_total_4d(dress(M4, bmap), wscale, h)
                curve.append(Ed)
            rows.append({"field": fname, "w_b": wb, "E_b0_curve": curve,
                         "E_undressed": E0,
                         "dE": [c - curve[0] for c in curve]})
            r = rows[-1]
            print(f"[dress] {fname:26s} w_b={wb:4.1f} dE(b0): "
                  + " ".join(f"{d:+9.3f}" for d in r["dE"]))
    # vacuum-subtracted dip per defect field
    reads = []
    for deff, ctlf in (("hedgehog", "control_hedgehog_boundary"),
                       ("loop_R12", "control_loop_boundary")):
        for wb in ws:
            dd = next(r for r in rows if r["field"] == deff and r["w_b"] == wb)
            cc = next(r for r in rows if r["field"] == ctlf and r["w_b"] == wb)
            dip = [d - c for d, c in zip(dd["dE"], cc["dE"])]
            has_dip = min(dip) < -1e-6 and np.argmin(dip) not in (0,)
            reads.append({"defect": deff, "w_b": wb, "b0s": list(b0s),
                          "dip_def": dip, "min_dip": float(np.min(dip)),
                          "b0_at_min": float(b0s[int(np.argmin(dip))]),
                          "interior_dip": bool(has_dip and
                                               int(np.argmin(dip)) < len(b0s) - 1)})
            rr = reads[-1]
            print(f"[dip]   {deff:12s} w_b={wb:4.1f} min_dip={rr['min_dip']:+9.3f}"
                  f" at b0={rr['b0_at_min']:.1f} interior={rr['interior_dip']}")
    out = {"task": "M5.12", "script": "m5_12_dressed.py", "mode": "scan",
           "grade": "dressed-class statics on the calibrated instrument;"
                    " g = 8 working value (labeled); B03 dressing;"
                    " vacuum-subtracted per the D1-audit discipline",
           "grid": {"NR": nr, "NZ": nz, "h": h}, "wscale": wscale,
           "g_time": G_TIME, "b0s": list(b0s),
           "rows": rows, "dip_reads": reads,
           "wall_s": round(time.time() - t0, 1)}
    path = os.path.join(DATA, "m5_12_dressed_scan.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {path}")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gates"
    if mode == "gates":
        ok = run_gates()
        sys.exit(0 if ok else 1)
    elif mode == "scan":
        run_scan()
    else:
        print(f"unknown mode {mode}")
