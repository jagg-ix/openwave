"""M7.7 - THE CANONICAL HYDROBOROS ELECTRON, one runnable script.

Task doc: research/tasks/m7_7_consolidation.md; spec: research/m7_theory_canonical.md.

  python m7_7_canonical.py            quick run   (N = 48, ~10 min CPU)
  python m7_7_canonical.py --full     record run  (N = 64, the M7.6 numbers)

Recipe (everything pinned; provenance in the spec):
  1. seed: the rotating blend, m = 1 azimuthal pair of the M6-torus +
     poloidal-twist profile (helicity = the localization guard)
  2. relax E_omega (written/repulsive f) at fixed Q_can = 13.2017 + fixed
     H_A (seed value), two-constraint FIRE (the M7.5 real-time-orbit frame)
  3. gates: energy, gradient, constraints, the j_z = 1 spin quantum, the
     localized RMS charge; PLUS the METHOD_NOTE cross-validation gate:
     the Taichi engine's energy must agree with the m7_functional.py
     reference implementation on the final state.

The physics lives in m7_functional.py (equations in its docstring); this
driver contains NO physics definitions of its own.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import m7_functional as F  # noqa: E402  (the reference physics module)
from m7_1_harmonic_lattice import HarmonicFields, grid_xyz  # noqa: E402
from m7_4_linked_vortex import (  # noqa: E402
    KAPPA, OMEGA, TaichiBlend, apply_vacuum_shell,
)
from m7_6_observables import (  # noqa: E402
    QCAN_REF, build_seed_m76, qcan, relax_qcan,
)

DATA = os.path.join(HERE, "..", "data")

GATES = {
    # gate: (quick N=48 bracket, full N=64 bracket)  [E brackets are grid-aware]
    "E":        ((6.15, 6.45), (6.30, 6.36)),
    "gnorm":    ((0, 1e-5),    (0, 1e-5)),
    "jz_A":     ((0.97, 1.03), (0.97, 1.03)),
    "jz_J":     ((0.97, 1.03), (0.97, 1.03)),
    "Q_rho":    ((0, 0.10),    (0, 0.10)),
    "xval_rel": ((0, 1e-10),   (0, 1e-10)),   # Taichi vs reference module
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="N = 64 record run")
    ap.add_argument("--n-iter", type=int, default=1500)
    args = ap.parse_args()
    N, L = (64, 16.0) if args.full else (48, 16.0)
    col = 1 if args.full else 0

    import taichi as ti
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)
    t0 = time.time()
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, F.C1, F.C2)

    f0 = apply_vacuum_shell(build_seed_m76("blend_m1", N, L))
    print(f"CANONICAL RUN N={N}: seed H_A={F.helicity_A(f0.avc, f0.avs, f0.h):+.5f}")
    fR, info = relax_qcan(eng, f0, n_iter=args.n_iter, tag="canonical",
                          qcan0=QCAN_REF)

    # observables via the reference module ONLY
    h = fR.h
    X, Y, Z = grid_xyz(N, L)
    E_ti = info["E_final"]
    E_ref = F.energy(fR.avc, fR.avs, fR.jvc, fR.jvs, h)
    res = {
        "N": N, "L": L, "n_iter": args.n_iter,
        "E": E_ti,
        "gnorm": info["gnorm_final"],
        "H_A": F.helicity_A(fR.avc, fR.avs, h),
        "H_A_seed": info["H0"],
        "Q_can": F.q_can(fR.avc, fR.avs, fR.jvc, fR.jvs, h),
        "jz_A": F.jz_per_quantum(fR.avc, fR.avs, X, Y, h),
        "jz_J": F.jz_per_quantum(fR.jvc, fR.jvs, X, Y, h),
        "L_z": F.spin_Lz(fR.avc, fR.avs, fR.jvc, fR.jvs, X, Y, Z, h),
        "Q_rho": F.charge_rms(fR.avc, fR.avs, X, Y, Z, h, 0.3 * L),
        "E_reference_module": E_ref,
        "xval_rel": abs(E_ti - E_ref) / abs(E_ref),
        "runtime_s": time.time() - t0,
    }

    print("\nGATE TABLE")
    all_pass = True
    checks = {"E": res["E"], "gnorm": res["gnorm"], "jz_A": res["jz_A"],
              "jz_J": res["jz_J"], "Q_rho": res["Q_rho"],
              "xval_rel": res["xval_rel"]}
    for k, v in checks.items():
        lo, hi = GATES[k][col]
        ok = lo <= v <= hi
        all_pass &= ok
        print(f"  {k:10s} = {v:12.6g}   in [{lo:g}, {hi:g}]  "
              f"{'PASS' if ok else 'FAIL'}")
    # constraint holds
    dH = abs(res["H_A"] / res["H_A_seed"] - 1)
    dQ = abs(res["Q_can"] / QCAN_REF - 1)
    for name, v in (("H_A hold", dH), ("Q_can hold", dQ)):
        ok = v < 1e-6
        all_pass &= ok
        print(f"  {name:10s} = {v:12.3e}   < 1e-06        "
              f"{'PASS' if ok else 'FAIL'}")
    res["all_pass"] = bool(all_pass)
    print(f"\nCANONICAL {'ALL GATES PASS' if all_pass else 'FAILED'} "
          f"({res['runtime_s']:.0f}s)")
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, f"m7_7_canonical_{'full' if args.full else 'quick'}.json")
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
