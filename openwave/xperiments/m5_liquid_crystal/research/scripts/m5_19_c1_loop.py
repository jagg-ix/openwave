"""M5.19 phase C: the regularized vortex LOOP with R as a degree of freedom.

The author's construction R4-R5 (the reply, m5_12_convo.md): revolve the
regularized planar vortex to a closed loop of radius R, R free ("energy
conservation demands variable R"), the field optimized at the loop center
too. This script does the ANSATZ-LEVEL half of phase C: the E(R0) curve per
cross-section class, deciding whether an interior optimum R* exists
(dE/dR = 0 bracketed) or the honest boundary verdict (collapse/runaway),
which is the pre-registered phase-C gate. Full relaxation (R relaxing as a
genuine field DOF) is phase D on the same seeds.

THE SEED (the M5.12 loop geometry with the tensor cross-section)
    Meridional winding director around the ring core (R0, 0), inherited
    VERBATIM from m5_12_loop.loop_field (chi = atan2(z, rho - R0); q = 1/2
    nematic phase or q = 1; axis blend suppressing the near-axis s_hat
    component; renormalized). New here: the uniaxial melt cross-section
    s(d) n n^T is generalized to the REGULARIZED TENSOR cross-section
        M_sp = lam_p n n^T + lam_m p p^T + lam_3 e2 e2^T ,
        n = (n1, 0, n3) meridional winding director, p = (-n3, 0, n1),
        e2 = the azimuthal axis (the local vortex-line tangent),
    profiles lam_pm = m(dd) +/- s(dd)/2, lam_3 = nu(dd) of the ring
    distance dd (the phases-A/B family, far field (1, 0, 0)); the center
    spectrum (mu0, mu0, nu0) carries R1 by construction. The M5.12 melt
    seed is the EXACT special case mu0 = nu0 = 0, gauss split (gate GC0).

ENERGY: the M5.12 statics stack: spectral potential (M5.18, Duda's own,
delta = 0 sector to match the M5.12 runs) + commutator curvature, via
total_energy_spec_np(M, wscale, h), wscale = 7.24e-4 calibrated.

CLASSES (cross-section centers from B2, delta = 0)
    melt      (0, 0)        the M5.12 control (its loop_field == GC0)
    planar    (0.72, -0.33) the B2 least-squares two-equal center
    escape    (0, 1)        the exact-vacuum escaped core (V(center) = 0)
    each at q in {1/2, 1}; widths: the B2 upper-bound configs (wide,
    calibrated scale) AND a narrow w = 3 variant (the GC1 anchor + the
    core-size sensitivity axis).

GATES (pre-registered at go)
    GC0  tensor seed at (mu0, nu0) = (0,0), gauss split, ws = rc equals
         m5_12_loop.loop_field bit-level (<= 1e-12), axis blend included
    GC1  large-R0 consistency: E(R0) / (2 pi R0 E_straight/L) -> 1 for the
         narrow-core seed (same profiles + potential on the phases-A/B 1D
         instrument), trend monotone in R0
    C    the gate proper: an interior R* bracketed (sign change in the
         discrete dE/dR0) OR the honest boundary verdict per class

Outputs: ../data/m5_19_c1_loop.json, ../plots/m5_19_c1_loop.png
"""
from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

import m5_19_ab_vortex as ab                                  # noqa: E402
from m5_19_b2_spectral import pot_spec                        # noqa: E402
from m5_17_energy import G_TIME, grid_coords                  # noqa: E402
from m5_18_spectral import total_energy_spec_np               # noqa: E402
from m5_12_loop import loop_field                             # noqa: E402
from m5_12_core_pin import load_wscale                        # noqa: E402

PI = np.pi
WSCALE = load_wscale()
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")

NR, NZ, H = 128, 256, 1.0
R0S = (4.0, 6.0, 9.0, 12.0, 16.0, 20.0, 24.0, 30.0)

CLASSES = {
    "melt": {"mu0": 0.0, "nu0": 0.0, "shape": "gauss"},
    "planar": {"mu0": 0.72, "nu0": -0.33, "shape": "tanh"},
    "escape": {"mu0": 0.0, "nu0": 1.0, "shape": "tanh"},
}
WIDE = {"ws": 10.0, "wm": 11.0, "w3": 9.0}     # the B2 calibrated-scale regime
NARROW = {"ws": 3.0, "wm": 3.0, "w3": 3.0}     # GC1 anchor + sensitivity


def winding_director(R, Z, R0, q, axis_blend=3.0):
    """the m5_12_loop.loop_field director, verbatim logic."""
    chi = np.arctan2(Z, R - R0)
    if abs(q - 0.5) < 1e-12:
        n1, n3 = np.cos(0.5 * chi), np.sin(0.5 * chi)
    else:
        n1, n3 = np.sin(q * chi), np.cos(q * chi)
    blend = 1.0 - np.exp(-((R / axis_blend) ** 2))
    n1 = n1 * blend
    norm = np.sqrt(n1 ** 2 + n3 ** 2)
    norm = np.where(norm < 1e-12, 1.0, norm)
    return n1 / norm, n3 / norm


def loop_field_tensor(R, Z, R0, q, mu0, nu0, ws, wm, w3, shape,
                      far=(1.0, 0.0, 0.0), g_time=G_TIME, profiles=None):
    """regularized tensor loop: winding pair in the meridional (1,3) plane,
    out-of-plane along the azimuthal axis 2; profiles of ring distance.
    profiles(dd) -> (lam_p, lam_m, lam3) overrides the family (GC0 uses it
    to feed the melt profile through THIS assembler, audit fix 2026-07-10)."""
    n1, n3 = winding_director(R, Z, R0, q)
    dd = np.sqrt((R - R0) ** 2 + Z ** 2)
    if profiles is not None:
        lam_p, lam_m, lam3 = profiles(dd)
    else:
        lam_p, lam_m, lam3 = ab.family_profiles(dd, mu0, nu0, ws, wm, w3,
                                                shape, far=far)
    p1, p3 = -n3, n1
    Mnp = np.zeros(R.shape + (4, 4))
    Mnp[..., 1, 1] = lam_p * n1 * n1 + lam_m * p1 * p1
    Mnp[..., 3, 3] = lam_p * n3 * n3 + lam_m * p3 * p3
    m13 = lam_p * n1 * n3 + lam_m * p1 * p3
    Mnp[..., 1, 3] = Mnp[..., 3, 1] = m13
    Mnp[..., 2, 2] = lam3
    Mnp[..., 0, 0] = g_time
    return Mnp


def loop_field_escaped(R, Z, R0, q, mu0, nu0, ws, wm, w3, shape,
                       dcut_fac=2.5, wcut_fac=1.0, g_time=G_TIME):
    """the TWIST-ESCAPED loop: meridional-winding tensor near the ring,
    blended in tensor space to the exact equivariant vacuum e2 e2^T
    (director escaped to the azimuthal direction) beyond dd ~ dcut.
    e2 e2^T is an exact zero of the functional (M_rho = M_z = 0, the lone
    M_phi channel has no commutator partner; spectrum (1,0,0) so V = 0),
    so the far field costs nothing and E(R0) is box-independent (gate GC2).
    The blend shell passes through in-plane-degenerate spectra: the SAME
    two-equal mechanism as the core regularization, applied outside (the
    loop is locally wound, globally removable: honest topology of nematic
    rings). Well-defined at q = 1/2 because tensors quotient n ~ -n."""
    M = loop_field_tensor(R, Z, R0, q, mu0, nu0, ws, wm, w3, shape)
    dd = np.sqrt((R - R0) ** 2 + Z ** 2)
    dcut, wcut = dcut_fac * ws, wcut_fac * ws
    x = np.clip((dd - dcut) / wcut, 0.0, 1.0)
    beta = (x * x * (3 - 2 * x))[..., None, None]     # smoothstep
    Me = np.zeros_like(M)
    Me[..., 2, 2] = 1.0
    out = (1 - beta) * M + beta * Me
    out[..., 0, 0] = g_time
    return out


def gate_gc2(R0=16.0, q=0.5):
    """box-independence of the escaped-family energy."""
    es = []
    for (nr, nz) in ((128, 256), (192, 384), (256, 512)):
        R, Z = grid_coords(nr, nz, H)
        M = loop_field_escaped(R, Z, R0, q, 0.0, 0.0, 3.0, 3.0, 3.0, "gauss")
        es.append(float(total_energy_spec_np(M, WSCALE, H)))
    spread = (max(es) - min(es)) / max(abs(es[0]), 1e-30)
    return {"E_by_box": es, "rel_spread": spread,
            "pass": bool(spread <= 1e-9)}


def gate_gc0(R0=16.0, q=0.5, rc=4.0):
    """melt special case == m5_12_loop.loop_field bit-level.
    loop_field: M = s dd-melt * n n^T, s = 1 - exp(-(dd/rc)^2).
    tensor family at mu0 = nu0 = 0, gauss shape, ws = rc: lam_p = s,
    lam_m = 0, lam3 = 0 exactly (mfar = 1/2, m = 1/2 gaussians... NOT the
    same functional form) -> so GC0 uses a DIRECT profile override instead:
    feed family-free profiles (s, 0, 0) through the tensor assembler and
    compare against loop_field."""
    R, Z = grid_coords(NR, NZ, H)
    ref = loop_field(R, Z, R0, q, rc)
    melt = lambda dd: (1.0 - np.exp(-((dd / rc) ** 2)),
                       np.zeros_like(dd), np.zeros_like(dd))
    Mnp = loop_field_tensor(R, Z, R0, q, 0, 0, 1, 1, 1, "gauss",
                            profiles=melt)
    err = float(np.max(np.abs(Mnp - ref)))
    return {"max_abs_err": err, "pass": bool(err <= 1e-12)}


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(PLOTS, exist_ok=True)
    out = {"wscale": WSCALE, "grid": {"NR": NR, "NZ": NZ, "h": H},
           "R0s": list(R0S), "classes": CLASSES,
           "widths": {"wide": WIDE, "narrow": NARROW}}
    out["GC0"] = gate_gc0()
    print(f"GC0 (tensor melt == m5_12_loop.loop_field): max abs "
          f"{out['GC0']['max_abs_err']:.2e} pass={out['GC0']['pass']}")
    out["GC2"] = gate_gc2()
    print(f"GC2 (escaped family box-independent): rel spread "
          f"{out['GC2']['rel_spread']:.2e} pass={out['GC2']['pass']}")

    R, Z = grid_coords(NR, NZ, H)
    vfn = pot_spec(0.0)
    curves = {}
    for cname, ctr in CLASSES.items():
        for wname, wd in (("wide", WIDE), ("narrow", NARROW)):
            for q in (0.5, 1.0):
                key = f"{cname}_{wname}_q{q}"
                es = []
                for R0 in R0S:
                    M = loop_field_tensor(R, Z, R0, q, ctr["mu0"], ctr["nu0"],
                                          wd["ws"], wd["wm"], wd["w3"],
                                          ctr["shape"])
                    es.append(float(total_energy_spec_np(M, WSCALE, H)))
                # discrete dE/dR0 sign pattern -> gate verdict
                de = np.diff(es)
                if np.all(de > 0):
                    verdict = "monotone_up(collapse-driving)"
                elif np.all(de < 0):
                    verdict = "monotone_down(runaway)"
                elif np.any((de[:-1] < 0) & (de[1:] > 0)):
                    verdict = "interior_minimum_bracketed"
                else:
                    verdict = "non-monotone(inspect)"
                curves[key] = {"E": es, "verdict": verdict}
                print(f"  {key:24s} E(R0): "
                      + " ".join(f"{e:9.4f}" for e in es) + f"  {verdict}")
                # GC1 anchor on the narrow q-classes: straight-line E/L
                if wname == "narrow":
                    fn = lambda r: ab.family_profiles(
                        r, ctr["mu0"], ctr["nu0"], wd["ws"], wd["wm"],
                        wd["w3"], ctr["shape"])
                    ecl, evl, _ = ab.energy_totals(fn, 4096, q, rmax=48.0,
                                                   pot_fn=vfn)
                    epl = ecl + evl
                    ratios = [es[i] / (2 * PI * R0S[i] * epl)
                              for i in range(len(R0S))]
                    curves[key]["E_per_len_straight"] = epl
                    curves[key]["GC1_ratio"] = ratios
                    print(f"    GC1 E/(2 pi R0 E/L): "
                          + " ".join(f"{r:6.3f}" for r in ratios))
    out["curves"] = curves

    # ---- the ESCAPED family: box-independent E(R0) -> the C gate proper ----
    print("== escaped family (far field = the exact e2 e2^T vacuum) ==")
    esc = {}
    for cname, ctr in CLASSES.items():
        for wname, wd in (("wide", WIDE), ("narrow", NARROW)):
            for q in (0.5, 1.0):
                key = f"{cname}_{wname}_q{q}_esc"
                es = []
                for R0 in R0S:
                    M = loop_field_escaped(R, Z, R0, q, ctr["mu0"],
                                           ctr["nu0"], wd["ws"], wd["wm"],
                                           wd["w3"], ctr["shape"])
                    es.append(float(total_energy_spec_np(M, WSCALE, H)))
                rec = {"E": es}
                # FULL fine scan (audit fix: refining only around the coarse
                # argmin trapped q=1 melt on the pre-bump side, R*=6 vs the
                # true 13)
                rf = np.arange(R0S[0], R0S[-1] + 0.5, 1.0)
                ef = []
                for R0 in rf:
                    M = loop_field_escaped(R, Z, R0, q, ctr["mu0"],
                                           ctr["nu0"], wd["ws"],
                                           wd["wm"], wd["w3"],
                                           ctr["shape"])
                    ef.append(float(total_energy_spec_np(M, WSCALE, H)))
                jmin = int(np.argmin(ef))
                interior = 0 < jmin < len(rf) - 1
                rec.update({"fine_R0": [float(x) for x in rf], "fine_E": ef})
                if interior:
                    rec.update({"verdict": "interior_R_star",
                                "R_star": float(rf[jmin]),
                                "E_star": ef[jmin]})
                else:
                    rec["verdict"] = ("monotone_down(runaway)" if jmin ==
                                      len(rf) - 1 else
                                      "monotone_up(collapse-driving)")
                esc[key] = rec
                msg = (f"R* = {rec['R_star']} E* = {rec['E_star']:.3f}"
                       if interior else rec["verdict"])
                print(f"  {key:26s} " + " ".join(f"{e:9.3f}" for e in es)
                      + f"  {msg}")
    out["curves_escaped"] = esc

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4))
    for key, rec in curves.items():
        axx = axes[0] if "narrow" in key else axes[1]
        axx.plot(R0S, rec["E"], "o-", label=key, lw=1, alpha=0.4)
    for key, rec in esc.items():
        if "q0.5" not in key:
            continue
        axx = axes[0] if "narrow" in key else axes[1]
        axx.plot(R0S, rec["E"], "s-", label=key, lw=1.6)
    for axx, t in zip(axes, ("narrow cores (w = 3)",
                             "wide cores (B2 calibrated scale)")):
        axx.set_xlabel("R0 (ring radius)")
        axx.set_ylabel("E (spectral potential)")
        axx.set_title(f"E(R0): {t}")
        axx.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m5_19_c1_loop.png"), dpi=150)

    with open(os.path.join(DATA, "m5_19_c1_loop.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("wrote data/m5_19_c1_loop.json + plots/m5_19_c1_loop.png")


if __name__ == "__main__":
    main()
