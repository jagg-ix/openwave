"""m7_13_q11_window.py: Q11 micro-slice, window-dependence of the charged Q vs (omega, g).

Tests an externally reported claim (2026-07-06, unverified, no script shared):
    "at w = 0.800 the charged Q is window-divergent for g = 0 but converges
     (Q -> 1.6885...1.6889) for g in {0.25, 0.5}."

Method (all definitions ours, pinned to the repo-validated benchmark):
  - Profile: the M6 canonical charged-sector ODE (m7_1_harmonic_lattice.m6_profile,
    the port of m6_ouroboros/research/archive/sandbox_v8/ouroboros_benchmark.py):
        a'' = -a'/r + a/r^2 - w^2 a + b
        b'' = -b'/r + b/r^2 - w^2 b + a - lam*b - 4 g b^3
    slope BCs at r_inner, A0 = B0 = 0.1, lam = 1.
  - Q(W) = int_0^W b^2 r dr  (the benchmark Q_J quadrature), windows W in WINDOWS.
  - H/Q(W) with the benchmark H integrand, for reference.
  - Analytic far-field check: linearized modes a,b ~ Z_1(kappa r) satisfy
        (w^2 - kappa^2)(w^2 + lam - kappa^2) = 1     [g-INDEPENDENT]
    localization (a decaying channel) needs a kappa^2 root < 0, i.e.
    w^2 (w^2 + lam) < 1; at w = 0.8, lam = 1: 0.64*1.64 = 1.0496 > 1 -> both
    roots positive -> radiation, for ANY g.
  - Verdict per (w, g): CONVERGED if |Q(W_max)/Q(W_max/2) - 1| < 1%, else DIVERGENT.

Outputs: data/m7_13_q11_window.json + plots/m7_13_q11_window.png + stdout table.
Runtime: seconds. Rides task M7.19 (the Q11 localized-branch scan).
"""

import json
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from m7_1_harmonic_lattice import m6_profile  # noqa: E402

HERE = pathlib.Path(__file__).parent
LAM = 1.0
R_MAX = 132.0
N_GRID = 16000
WINDOWS = [8.0, 12.0, 16.0, 32.0, 64.0, 128.0]
OMEGAS = [0.8, 1.0]              # 0.8 = the claim's point; 1.0 = the M7.3 control
GS = [0.0, 0.25, 0.5, 1.0]       # 0/0.25/0.5 = the claim's sweep; 1.0 = canonical


def kappa_roots(omega, lam=LAM):
    """Roots kappa^2 of (w^2 - k2)(w^2 + lam - k2) = 1 (far-field, linear, no g)."""
    # k2^2 - (2 w^2 + lam) k2 + w^2 (w^2 + lam) - 1 = 0
    s = 2 * omega ** 2 + lam
    p = omega ** 2 * (omega ** 2 + lam) - 1.0
    disc = s * s - 4 * p
    r1 = 0.5 * (s + np.sqrt(disc))
    r2 = 0.5 * (s - np.sqrt(disc))
    return float(r1), float(r2)


def windowed(r, a, b, g, W):
    m = r <= W
    rm, am, bm = r[m], a[m], b[m]
    da = np.gradient(am, rm)
    db = np.gradient(bm, rm)
    Q = float(np.trapezoid(bm ** 2 * rm, rm))
    H = float(np.trapezoid((da ** 2 + db ** 2 + am ** 2 / rm ** 2
                            + bm ** 2 / rm ** 2 + 4 * g * bm ** 4) * rm, rm))
    return Q, H


def main():
    out = {"lam": LAM, "windows": WINDOWS, "runs": []}
    for omega in OMEGAS:
        k1, k2 = kappa_roots(omega)
        loc = "possible (one decaying root)" if min(k1, k2) < 0 else "impossible (both roots propagate)"
        print(f"\nomega = {omega}: kappa^2 roots = {k1:.4f}, {k2:.4f} -> linear localization {loc}")
        for g in GS:
            prof = m6_profile(g=g, omega=omega, lam=LAM, r_max=R_MAX, n_grid=N_GRID)
            if prof is None:
                print(f"  g = {g}: SOLVE FAILED")
                out["runs"].append({"omega": omega, "g": g, "status": "solve_failed"})
                continue
            r, a, b, _ = prof
            row = {"omega": omega, "g": g, "status": "ok", "Q": {}, "HQ": {}}
            for W in WINDOWS:
                Q, H = windowed(r, a, b, g, W)
                row["Q"][str(W)] = Q
                row["HQ"][str(W)] = H / Q if Q > 0 else float("nan")
            ratio = row["Q"][str(WINDOWS[-1])] / row["Q"][str(WINDOWS[-2])]
            row["Q_ratio_last"] = ratio
            row["verdict"] = "CONVERGED" if abs(ratio - 1.0) < 0.01 else "DIVERGENT"
            # envelope: RMS of b in the outermost decade vs mid-range
            tail = np.sqrt(np.mean(b[r > 0.9 * R_MAX] ** 2))
            mid = np.sqrt(np.mean(b[(r > 20) & (r < 30)] ** 2))
            row["b_rms_tail_over_mid"] = float(tail / mid) if mid > 0 else float("nan")
            out["runs"].append(row)
            qs = "  ".join(f"Q({W:g})={row['Q'][str(W)]:.4f}" for W in WINDOWS)
            print(f"  g = {g:<5}: {qs}  ratio(last)={ratio:.4f}  -> {row['verdict']}")

    (HERE / "../data/m7_13_q11_window.json").write_text(json.dumps(out, indent=1))

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, omega in zip(axes, OMEGAS):
        for g in GS:
            row = next(r for r in out["runs"]
                       if r["omega"] == omega and r["g"] == g and r["status"] == "ok")
            ax.plot(WINDOWS, [row["Q"][str(W)] for W in WINDOWS], "o-", label=f"g = {g}")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("window W")
        ax.set_ylabel("Q(W)")
        k1, k2 = kappa_roots(omega)
        ax.set_title(f"omega = {omega}  (kappa$^2$ = {k1:.3f}, {k2:.3f}: both > 0)")
        ax.legend()
        ax.grid(alpha=0.3)
    fig.suptitle("Q11 micro-slice: windowed charge vs W, per (omega, g); "
                 "convergence would mean a localized branch")
    fig.tight_layout()
    fig.savefig(HERE / "../plots/m7_13_q11_window.png", dpi=130)
    print("\nwrote data/m7_13_q11_window.json + plots/m7_13_q11_window.png")


if __name__ == "__main__":
    main()
