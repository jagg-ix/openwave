"""M5.12 block 16 leg (a): the z-anisotropic (pancake) mixing family.

The block-15 audit refuted the isotropic 23-point sweep as a class floor:
its generalized-Rayleigh minimization found a z-flattened anisotropic mix
at omega_bal 7.8955 (seed level, same matched a2 / n32 calibration), 4.1%
below the isotropic slice floor 8.2348, and the relaxed floor had dropped
with every family probed (bmix 8.64 -> wide 7.455 -> rgauss 7.376 ->
shell 6.987). This script maps the anisotropy axis the audit opened:

  probe mode: exact Q2/omega_bal readouts of the anisotropic-gaussian
      family b(R,Z) = exp(-R^2/wr^2 - Z^2/wz^2) on a (wr, wz) grid,
      matched a2 = 0.3037, n32 hedgehog-calibrated wscale. The isotropic
      diagonal (wr = wz = kappa*w_b) reproduces the b15 gauss family:
      anchor guards at (1,1) = 11.0306 and (2,2) = 8.6194 abort on drift.
      Also assembles the audit's Rayleigh-optimum seed (A1-only npz) into
      a solver-consumable state (M0 = standard covariant n32 hedgehog,
      pin-zeroed, rescaled to matched a2) and exact-probes it (the audit
      quotes 7.8955 for its unrescaled convention; the probe here is the
      definitive number under the standing convention).

All seeds saved solver-consumable for m5_12_b12_hard.py --state. The two
deepest get relax chains (tags p1_, p2_) per the pre-registered stopping
rule: two consecutive families gaining < 5% relaxed = floor saturated.

Run:  python m5_12_b16_aniso.py probe
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


def aniso_seed(nr, nz, h, eps, wr, wz, Nt=2):
    scale = nr / 96.0
    R, Z = grid_coords(nr, nz, h)
    M4 = to_covariant(hedgehog_field(R, Z, 8.0 * scale))
    rr = np.sqrt(R ** 2 + Z ** 2) + 1e-12
    b = np.exp(-(R ** 2) / wr ** 2 - (Z ** 2) / wz ** 2)
    cr, cz = R / rr, Z / rr
    A1 = np.zeros_like(M4)
    A1[..., 0, 1] = A1[..., 1, 0] = eps * b * cr
    A1[..., 0, 3] = A1[..., 3, 0] = eps * b * cz
    pin = pin_mask(nr, nz)
    A1[pin] = 0.0
    return x_pack(M4, [A1] + [np.zeros_like(M4)] * (Nt - 1),
                  [np.zeros_like(M4)] * Nt), pin


def opt_seed(nr, nz, h, Nt=2):
    """assemble the audit's Rayleigh-optimum A1 into a full state."""
    scale = nr / 96.0
    R, Z = grid_coords(nr, nz, h)
    M4 = to_covariant(hedgehog_field(R, Z, 8.0 * scale))
    d = np.load(os.path.join(DATA, "m5_12_audit_b15_rayleigh_opt.npz"))
    A1 = d["A1"].astype(np.float64)
    pin = pin_mask(nr, nz)
    A1[pin] = 0.0
    return x_pack(M4, [A1] + [np.zeros_like(M4)] * (Nt - 1),
                  [np.zeros_like(M4)] * Nt), pin


WR = (1.0, 2.0, 3.0, 4.0)
WZ = (0.25, 0.5, 1.0, 2.0)
ANCHORS = {(1.0, 1.0): 11.0306, (2.0, 2.0): 8.6194}  # b15 gauss k1/k2


def main():
    nr = int(_flag("nr", 32, int))
    eps = _flag("eps", 0.16490)
    a2ref = _flag("a2ref", os.path.join(
        DATA, "m5_12_d3b_breather_n32_c2seed_state.npz"), str)
    nz, h = 2 * nr, 1.0
    w_b = 8.0 * nr / 96.0
    wscale = wscale_at(nr, nz, h, w_b)

    d = np.load(a2ref)
    Xr = x_pack(d["M0"].astype(np.float64),
                [d["A1"].astype(np.float64), d["A2"].astype(np.float64)],
                [d["B1"].astype(np.float64), d["B2"].astype(np.float64)])
    a2_star = a2_free(Xr, pin_mask(*Xr["M0"].shape[:2]))
    print(f"[a2ref] {os.path.basename(a2ref)} a2={a2_star:.6f}")

    out = {"task": "M5.12 block 16", "mode": "probe", "nr": nr, "eps": eps,
           "a2_star": a2_star, "w_b": w_b, "rows": []}
    for kr in WR:
        for kz in WZ:
            X, pin = aniso_seed(nr, nz, h, eps, kr * w_b, kz * w_b)
            X, _ = rescale_to(X, pin, a2_star)
            rec = {"family": "aniso_gauss", "kr": kr, "kz": kz,
                   "a2": a2_free(X, pin), **probe(X, h, wscale)}
            key = (kr, kz)
            if key in ANCHORS:
                ref = ANCHORS[key]
                got = rec["omega_bal"]
                if got is None or abs(got - ref) > 5e-4 * ref:
                    raise RuntimeError(
                        f"anchor mismatch {key}: {got} vs b15 {ref}")
                rec["anchor_b15"] = ref
            name = f"aniso_r{kr:g}z{kz:g}".replace(".", "p")
            spath = os.path.join(DATA, f"m5_12_b16_seed_{name}_n{nr}.npz")
            save_state(X, spath)
            rec["state"] = os.path.basename(spath)
            out["rows"].append(rec)
            wb = rec["omega_bal"]
            print(f"[aniso] wr={kr:<4g} wz={kz:<4g} S0={rec['S0']:+9.4f}  "
                  f"Q2={rec['Q2']:+.6f}  "
                  f"w_bal={wb if wb else float('nan'):8.4f}"
                  f"{'  ANCHOR OK' if key in ANCHORS else ''}")

    X, pin = opt_seed(nr, nz, h)
    a2_raw = a2_free(X, pin)
    X, _ = rescale_to(X, pin, a2_star)
    rec = {"family": "rayleigh_opt", "a2_raw": a2_raw,
           "a2": a2_free(X, pin), **probe(X, h, wscale)}
    spath = os.path.join(DATA, f"m5_12_b16_seed_rayleigh_opt_n{nr}.npz")
    save_state(X, spath)
    rec["state"] = os.path.basename(spath)
    out["rows"].append(rec)
    print(f"[opt]   rayleigh_opt   S0={rec['S0']:+9.4f}  "
          f"Q2={rec['Q2']:+.6f}  w_bal={rec['omega_bal']:8.4f}  "
          f"(audit quoted 7.8955 pre-rescale)")

    ok = [r for r in out["rows"] if r["omega_bal"]]
    ok.sort(key=lambda r: r["omega_bal"])
    out["floor_ranked"] = ok[:6]
    path = os.path.join(DATA, "m5_12_b16_aniso.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print("[floor] " + "  ".join(
        (f"{r['family']}" if r["family"] != "aniso_gauss"
         else f"r{r['kr']:g}z{r['kz']:g}") + f"={r['omega_bal']:.4f}"
        for r in out["floor_ranked"]))
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
