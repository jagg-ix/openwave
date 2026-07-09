"""M5.12 block 14: seed forge + Q2/omega_bal probe (class robustness +
the loop transplant; option B = harden the class-negative, then transplant).

The block-13 state of knowledge: the bmix (radial 0i boost) breather class
at n32 carries Q2 < 0 but no chain converged (floors 139-216, H_swing ~
2-2.7 S0) and omega_bal sits ~5.8-8.6 at deep stalls vs the M5.8 band ~1.1.
Before that class-negative is trusted it needs (a) GRID robustness (is the
Q2/S0/omega_bal structure an n32 artifact?) and (b) CLASS coverage (is the
rz-radial bump the only time-mixing structure, or do neighbours carry a
lower balance root?). This script forges the seed classes, probes each one
exactly (Q2 is read off the audit-verified identity Q2 = Shat(0) - Shat(1),
no solver in the loop), and saves every seed as a solver-consumable state
npz for `m5_12_b12_hard.py --state`.

Classes forged (first harmonic only, A2 = B1 = B2 = 0 unless noted):
    bmix_rz    the block-11 class (control, = the c2 chain's seed):
               A1[0r] = eps b(r) R/r, A1[0z] = eps b(r) Z/r
    mix_0r     the 0r component alone
    mix_0z     the 0z component alone
    mix_0phi   azimuthal boost, A1[0,2] = eps b(r) R/r (the R/r factor
               regularizes the undefined phi direction on the axis)
    bmix_B1    the rz mix seeded in the SIN phase (B1) instead of A1
    loop_bmix  covariant vortex-loop (loop_field, q = 1/2, ring at R0) +
               ring-localized 0i mix along the local ring-normal:
               A1[0r] = eps b(d) (R-R0)/d, A1[0z] = eps b(d) Z/d,
               b(d) = exp(-d^2/w_b^2), d = dist to the ring core

Geometry follows the d3b seed convention (object scales with nr):
hedgehog rc = w_b = 8 * nr/96; loop R0 = 16 * nr/96, rc = 8 * nr/96 (same
core resolution as the hedgehog at equal nr), mix width w_b = 8 * nr/96.

Amplitude matching: --a2ref <npz> rescales each forged seed's first
harmonic (free cells) to the reference state's a2, so classes are compared
at MATCHED constraint amplitude (the c2 seed is the natural reference).

Probe per seed: S0, Q2 total + mix/pos channel split + cross (the block-13
honest-metrics ruleset), omega_bal = sqrt(S0/-Q2) where Q2 < 0.

Run:  python m5_12_b14_seeds.py forge --nr 32 --eps 0.16490 \
             [--a2ref ../data/m5_12_d3b_breather_n32_c2seed_state.npz]
      python m5_12_b14_seeds.py grid --eps 0.16490    # bmix_rz, nr scan
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
from m5_12_loop import loop_field                                          # noqa: E402
from m5_12_d3a_bvp import shat, x_pack                                     # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402


def _flag(name, default, cast=float):
    for i, a in enumerate(ARGV):
        if a == "--" + name and i + 1 < len(ARGV):
            return cast(ARGV[i + 1])
    return default


def s0_q2(X, h, wscale):
    s0 = shat(X, 0.0, h, wscale)
    return s0, s0 - shat(X, 1.0, h, wscale)


def q2_channels(X, h, wscale):
    """the b12_hard q2_channel split: mix (0-row/col only) vs pos
    (spatial block only), cross = total - mix - pos."""
    out = {}
    for key, keep_mix in (("mix", True), ("pos", False)):
        Xc = {"M0": X["M0"].copy(),
              "A": [a.copy() for a in X["A"]],
              "B": [b.copy() for b in X["B"]]}
        for arr in Xc["A"] + Xc["B"]:
            if keep_mix:
                arr[..., 1:4, 1:4] = 0.0
            else:
                arr[..., 0, :] = 0.0
                arr[..., :, 0] = 0.0
        _, out[key] = s0_q2(Xc, h, wscale)
    return out["mix"], out["pos"]


def forge_seed(cls, nr, nz, h, eps, Nt=2, rc_fix=None, wb_fix=None):
    scale = nr / 96.0
    rc_h, w_b = rc_fix or 8.0 * scale, wb_fix or 8.0 * scale
    R, Z = grid_coords(nr, nz, h)
    if cls == "loop_bmix":
        R0, rc_l = 16.0 * scale, rc_fix or 8.0 * scale
        M4 = to_covariant(loop_field(R, Z, R0, 0.5, rc_l))
        d = np.sqrt((R - R0) ** 2 + Z ** 2) + 1e-12
        b2 = np.exp(-(d ** 2) / (w_b ** 2))
        cr, cz = (R - R0) / d, Z / d
    else:
        M4 = to_covariant(hedgehog_field(R, Z, rc_h))
        r2 = R ** 2 + Z ** 2
        rr = np.sqrt(r2) + 1e-12
        b2 = np.exp(-r2 / (w_b ** 2))
        cr, cz = R / rr, Z / rr
    A1 = np.zeros_like(M4)
    B1 = np.zeros_like(M4)
    tgt = B1 if cls == "bmix_B1" else A1
    if cls in ("bmix_rz", "bmix_B1", "loop_bmix"):
        tgt[..., 0, 1] = tgt[..., 1, 0] = eps * b2 * cr
        tgt[..., 0, 3] = tgt[..., 3, 0] = eps * b2 * cz
    elif cls == "wide_rz":
        # the b14 audit's N2c kill: doubled mix width undercuts the control
        b2w = np.exp(-r2 / ((2.0 * w_b) ** 2))
        tgt[..., 0, 1] = tgt[..., 1, 0] = eps * b2w * cr
        tgt[..., 0, 3] = tgt[..., 3, 0] = eps * b2w * cz
    elif cls == "node_rz":
        # audit N2c: radial-node profile (shape, not component, coverage)
        b2n = b2 * (1.0 - 2.0 * r2 / (w_b ** 2))
        tgt[..., 0, 1] = tgt[..., 1, 0] = eps * b2n * cr
        tgt[..., 0, 3] = tgt[..., 3, 0] = eps * b2n * cz
    elif cls == "mix_0r":
        tgt[..., 0, 1] = tgt[..., 1, 0] = eps * b2 * cr
    elif cls == "mix_0z":
        tgt[..., 0, 3] = tgt[..., 3, 0] = eps * b2 * cz
    elif cls == "mix_0phi":
        tgt[..., 0, 2] = tgt[..., 2, 0] = eps * b2 * cr
    else:
        raise ValueError(cls)
    pin = pin_mask(nr, nz)
    A1[pin] = 0.0
    B1[pin] = 0.0
    return x_pack(M4, [A1] + [np.zeros_like(M4)] * (Nt - 1),
                  [B1] + [np.zeros_like(M4)] * (Nt - 1)), pin


def a2_free(X, pin):
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), X["M0"].shape)
    return float(np.sum(X["A"][0][free] ** 2) + np.sum(X["B"][0][free] ** 2))


def rescale_to(X, pin, a2_star):
    a2 = a2_free(X, pin)
    if a2 <= 0:
        return X, a2
    fac = np.sqrt(a2_star / a2)
    X["A"][0] = X["A"][0] * fac
    X["B"][0] = X["B"][0] * fac
    return X, a2_free(X, pin)


def probe(X, h, wscale):
    s0, q2 = s0_q2(X, h, wscale)
    q2m, q2p = q2_channels(X, h, wscale)
    rec = {"S0": s0, "Q2": q2, "Q2_mix": q2m, "Q2_pos": q2p,
           "Q2_cross": q2 - q2m - q2p, "Q2_negative": bool(q2 < 0),
           "omega_bal": (float(np.sqrt(s0 / -q2))
                         if (q2 < 0 and s0 > 0) else None)}
    return rec


def save_state(X, path, Nt=2):
    np.savez_compressed(
        path, M0=X["M0"].astype(np.float32),
        **{f"A{k+1}": X["A"][k].astype(np.float32) for k in range(Nt)},
        **{f"B{k+1}": X["B"][k].astype(np.float32) for k in range(Nt)},
        omega=np.array([0.0]))


CLASSES = ("bmix_rz", "mix_0r", "mix_0z", "mix_0phi", "bmix_B1",
           "wide_rz", "node_rz", "loop_bmix")


def main():
    mode = ARGV[0] if ARGV else "forge"
    nr = int(_flag("nr", 32, int))
    eps = _flag("eps", 0.16490)
    a2ref = _flag("a2ref", None, str)
    h = 1.0

    if mode in ("grid", "fixobj"):
        # grid:   the d3b scale-family convention (object scales with nr)
        # fixobj: the SAME physical object (rc = w_b = 8*32/96) refined:
        #         pure resolution, disentangled from the scale family
        rc_fix = 8.0 * 32 / 96 if mode == "fixobj" else None
        out = {"task": "M5.12 block 14", "mode": mode, "eps": eps,
               "class": "bmix_rz", "rc_fix": rc_fix, "series": []}
        for n in (24, 32, 48, 64) if mode == "grid" else (32, 48, 64):
            nz = 2 * n
            wsc = wscale_at(n, nz, h, rc_fix or 8.0 * n / 96)
            X, pin = forge_seed("bmix_rz", n, nz, h, eps,
                                rc_fix=rc_fix, wb_fix=rc_fix)
            rec = {"nr": n, "a2": a2_free(X, pin), **probe(X, h, wsc)}
            out["series"].append(rec)
            print(f"[grid] nr={n:3d}  S0={rec['S0']:+.4f}  "
                  f"Q2={rec['Q2']:+.6f}  mix={rec['Q2_mix']:+.6f}  "
                  f"pos={rec['Q2_pos']:+.6f}  "
                  f"w_bal={rec['omega_bal'] or float('nan'):.4f}  "
                  f"a2={rec['a2']:.4f}")
        path = os.path.join(DATA, f"m5_12_b14_{mode}.json")
        with open(path, "w") as f:
            json.dump(out, f, indent=2)
        print(f"json -> {os.path.basename(path)}")
        return

    nz = 2 * nr
    wscale = wscale_at(nr, nz, h, 8.0 * nr / 96)
    a2_star = None
    if a2ref:
        d = np.load(a2ref)
        Xr = x_pack(d["M0"].astype(np.float64),
                    [d["A1"].astype(np.float64),
                     d["A2"].astype(np.float64)],
                    [d["B1"].astype(np.float64),
                     d["B2"].astype(np.float64)])
        a2_star = a2_free(Xr, pin_mask(*Xr["M0"].shape[:2]))
        print(f"[a2ref] {os.path.basename(a2ref)} a2={a2_star:.6f}")
    out = {"task": "M5.12 block 14", "mode": "forge", "nr": nr, "eps": eps,
           "a2ref": (os.path.basename(a2ref) if a2ref else None),
           "a2_star": a2_star, "seeds": []}
    for cls in CLASSES:
        X, pin = forge_seed(cls, nr, nz, h, eps)
        a2_raw = a2_free(X, pin)
        if a2_star:
            X, _ = rescale_to(X, pin, a2_star)
        rec = {"class": cls, "eps": eps, "a2_raw": a2_raw,
               "a2": a2_free(X, pin), **probe(X, h, wscale)}
        out["seeds"].append(rec)
        spath = os.path.join(DATA, f"m5_12_b14_seed_{cls}_n{nr}.npz")
        save_state(X, spath)
        rec["state"] = os.path.basename(spath)
        print(f"[forge] {cls:>10} n{nr}  S0={rec['S0']:+.4f}  "
              f"Q2={rec['Q2']:+.6f} (mix {rec['Q2_mix']:+.5f} "
              f"pos {rec['Q2_pos']:+.5f})  "
              f"w_bal={rec['omega_bal'] or float('nan'):.4f}  "
              f"a2={rec['a2']:.4f}")
    path = os.path.join(DATA, f"m5_12_b14_seeds_n{nr}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
