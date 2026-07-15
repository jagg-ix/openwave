"""M5.12 block 15: the (profile, width) shape-family omega_bal floor map.

Block 14 closed with the class-negative REWORDED over the shape family: the
audit's N2 kill showed the block-14 class battery froze the radial SHAPE of
the 0i mix bump, and one shape variation (wide_rz, doubled width) undercut
the bmix control ~20% at seed level AND survived relaxation below the bmix
stall band (7.455 vs 8.64-8.83 at the same a2 and grid). The shape-family
floor is UNMAPPED. This script maps it at seed level: a systematic
(profile, width) sweep at FIXED calibration (n32, hedgehog-calibrated
wscale) and MATCHED a2 (the standing 0.3037 battery convention), exact
Q2/omega_bal readouts on the audit-verified identity (no solver). The
deepest undercutters then get bounded LM relax chains (m5_12_b12_hard.py)
to test whether the seed-level floor survives relaxation.

Profile family (b(r) multiplies eps and the radial direction cosines
cr = R/r, cz = Z/r on the A1 0r/0z components, exactly the bmix template;
w = kappa * w_b, w_b = 8*nr/96 the standing convention):
    gauss    exp(-r^2/w^2)                 kappa 1 = bmix_rz control,
                                           kappa 2 = wide_rz (b14 anchors)
    lag1     gauss * (1 - 2r^2/w^2)        kappa 1 = node_rz (b14 anchor)
    lag2     gauss * L2(2r^2/w^2),         L2(x) = 1 - 2x + x^2/2
    shell    exp(-(r-r0)^2/w_b^2)          displaced bump, peak off origin
    lorentz  (1 + r^2/w^2)^(-p)            fat power-law tail
    rgauss   (r/w) * exp(-r^2/w^2)         weight pushed off the origin

All seeds saved solver-consumable (m5_12_b12_hard.py --state). Anchors are
cross-validated against m5_12_b14_seeds_n32.json at run time (gauss k1 =
11.0306, gauss k2 = 8.6194, lag1 k1 = 8.9475): any mismatch aborts.

Run:  python m5_12_b15_shapes.py sweep \
             --a2ref ../data/m5_12_d3b_breather_n32_c2seed_state.npz
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import hedgehog_field, pin_mask                          # noqa: E402
from m5_12_dressed import to_covariant                                     # noqa: E402
from m5_12_d3a_bvp import x_pack                                           # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_b14_seeds import (a2_free, probe, rescale_to,                   # noqa: E402
                             save_state)


def _flag(name, default, cast=float):
    for i, a in enumerate(ARGV):
        if a == "--" + name and i + 1 < len(ARGV):
            return cast(ARGV[i + 1])
    return default


def profile(prof, r2, w, w_b):
    """the radial bump b(r) per profile family; r2 = r^2 on the grid."""
    if prof == "gauss":
        return np.exp(-r2 / w ** 2)
    if prof == "lag1":
        return np.exp(-r2 / w ** 2) * (1.0 - 2.0 * r2 / w ** 2)
    if prof == "lag2":
        x = 2.0 * r2 / w ** 2
        return np.exp(-r2 / w ** 2) * (1.0 - 2.0 * x + 0.5 * x ** 2)
    if prof == "shell":
        # w plays the DISPLACEMENT r0 here; width stays w_b
        return np.exp(-((np.sqrt(r2) - w) ** 2) / w_b ** 2)
    if prof == "lorentz1":
        return (1.0 + r2 / w ** 2) ** -1.0
    if prof == "lorentz2":
        return (1.0 + r2 / w ** 2) ** -2.0
    if prof == "rgauss":
        return (np.sqrt(r2) / w) * np.exp(-r2 / w ** 2)
    raise ValueError(prof)


def shape_seed(nr, nz, h, eps, prof, w, Nt=2):
    scale = nr / 96.0
    rc_h, w_b = 8.0 * scale, 8.0 * scale
    R, Z = grid_coords(nr, nz, h)
    M4 = to_covariant(hedgehog_field(R, Z, rc_h))
    r2 = R ** 2 + Z ** 2
    rr = np.sqrt(r2) + 1e-12
    b = profile(prof, r2, w, w_b)
    cr, cz = R / rr, Z / rr
    A1 = np.zeros_like(M4)
    B1 = np.zeros_like(M4)
    A1[..., 0, 1] = A1[..., 1, 0] = eps * b * cr
    A1[..., 0, 3] = A1[..., 3, 0] = eps * b * cz
    pin = pin_mask(nr, nz)
    A1[pin] = 0.0
    return x_pack(M4, [A1] + [np.zeros_like(M4)] * (Nt - 1),
                  [B1] + [np.zeros_like(M4)] * (Nt - 1)), pin


# (profile, kappa list); shell's kappa = displacement r0 in w_b units
SWEEP = (
    ("gauss",    (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0)),
    ("lag1",     (1.0, 2.0, 3.0)),
    ("lag2",     (1.0, 2.0)),
    ("shell",    (1.0, 2.0, 3.0)),
    ("lorentz1", (1.0, 2.0)),
    ("lorentz2", (1.0, 2.0)),
    ("rgauss",   (1.0, 2.0, 3.0)),
)

ANCHORS = {("gauss", 1.0): 11.0306, ("gauss", 2.0): 8.6194,
           ("lag1", 1.0): 8.9475}   # m5_12_b14_seeds_n32.json


def main():
    nr = int(_flag("nr", 32, int))
    eps = _flag("eps", 0.16490)
    a2ref = _flag("a2ref", os.path.join(
        DATA, "m5_12_d3b_breather_n32_c2seed_state.npz"), str)
    nz, h = 2 * nr, 1.0
    scale = nr / 96.0
    w_b = 8.0 * scale
    wscale = wscale_at(nr, nz, h, 8.0 * scale)

    d = np.load(a2ref)
    Xr = x_pack(d["M0"].astype(np.float64),
                [d["A1"].astype(np.float64), d["A2"].astype(np.float64)],
                [d["B1"].astype(np.float64), d["B2"].astype(np.float64)])
    a2_star = a2_free(Xr, pin_mask(*Xr["M0"].shape[:2]))
    print(f"[a2ref] {os.path.basename(a2ref)} a2={a2_star:.6f}")

    out = {"task": "M5.12 block 15", "mode": "sweep", "nr": nr, "eps": eps,
           "a2ref": os.path.basename(a2ref), "a2_star": a2_star,
           "w_b": w_b, "rows": []}
    for prof, kappas in SWEEP:
        for k in kappas:
            w = k * w_b
            X, pin = shape_seed(nr, nz, h, eps, prof, w)
            a2_raw = a2_free(X, pin)
            X, _ = rescale_to(X, pin, a2_star)
            rec = {"profile": prof, "kappa": k, "w": w, "a2_raw": a2_raw,
                   "a2": a2_free(X, pin), **probe(X, h, wscale)}
            key = (prof, k)
            if key in ANCHORS:
                ref = ANCHORS[key]
                got = rec["omega_bal"]
                if got is None or abs(got - ref) > 5e-4 * ref:
                    raise RuntimeError(
                        f"anchor mismatch {key}: {got} vs b14 {ref}")
                rec["anchor_b14"] = ref
            name = f"{prof}_k{k:g}".replace(".", "p")
            spath = os.path.join(DATA, f"m5_12_b15_seed_{name}_n{nr}.npz")
            save_state(X, spath)
            rec["state"] = os.path.basename(spath)
            out["rows"].append(rec)
            wb = rec["omega_bal"]
            print(f"[sweep] {prof:>8} k={k:<4g} S0={rec['S0']:+9.4f}  "
                  f"Q2={rec['Q2']:+.6f} (mix {rec['Q2_mix']:+.5f} "
                  f"pos {rec['Q2_pos']:+.5f})  "
                  f"w_bal={wb if wb else float('nan'):8.4f}"
                  f"{'  ANCHOR OK' if key in ANCHORS else ''}")
    ok = [r for r in out["rows"] if r["omega_bal"]]
    ok.sort(key=lambda r: r["omega_bal"])
    out["floor_ranked"] = [{k: r[k] for k in
                            ("profile", "kappa", "omega_bal", "S0", "Q2")}
                           for r in ok[:6]]
    path = os.path.join(DATA, "m5_12_b15_shapes.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("[floor] " + "  ".join(
        f"{r['profile']}_k{r['kappa']:g}={r['omega_bal']:.4f}"
        for r in out["floor_ranked"]))
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
