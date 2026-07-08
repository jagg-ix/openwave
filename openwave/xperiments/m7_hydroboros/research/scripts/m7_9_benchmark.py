"""M7.9 E3: the ChaosBook canonical-exercise benchmark.

Every published value below is transcribed from the ChaosBook chapter PDFs in
theory/chaosbook/ (version17 stable download, edition16.0 text), cited per
value; NOTHING is supplied from model memory (M7.9 hygiene rule, task doc § 4
E1). Implement-first-check-after: the toolkit (m7_9_orbits.py) was written and
gated on closed-form problems (m7_9_gates.py) before these comparisons run.

Benchmarks:
    B1 Rossler equilibria           (2.29), flows.pdf p. 24, example 2.3
    B2 Rossler equilibrium exponents (4.36), stability.pdf p. 17, example 4.5
    B3 analytic limit-cycle Floquet  exercise 5.1, invariants.pdf p. 14
       (system from the exercise; the answer {1, e^{-4 pi}}, T = 2 pi is our
       hand derivation, checked here numerically, not a printed book value)
    B4 Rossler cycles to length 7    exercise 16.9 table, cycles.pdf p. 12
       (close-return seeding -> multiple shooting -> Floquet; the section is
       x = 0 with dx/dt < 0, inferred from the table's positive y_p)
    B5 binary cycle counts           tables 18.2 + 18.3, count.pdf pp. 5, 14
       (transition-matrix trace vs Mobius / necklace counting, exact integers)

Run: python3 m7_9_benchmark.py    writes ../data/m7_9_benchmark.json
                                  + ../plots/m7_9_rossler_cycles.png
"""

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sympy import divisors, mobius

from m7_9_orbits import (close_returns, find_cycle, floquet, poincare_section,
                         return_map)

results = {}


def gate(name, ok, detail):
    results[name] = {"pass": bool(ok), **detail}
    print(f"{'PASS' if ok else 'FAIL'}  {name}")


# ------------------------------------------------------------- Rossler system

A_R, B_R, C_R = 0.2, 0.2, 5.7  # (2.28), flows.pdf p. 24


def rossler(x):
    return np.array([-x[1] - x[2],
                     x[0] + A_R * x[1],
                     B_R + x[2] * (x[0] - C_R)])


def rossler_jac(x):
    return np.array([[0.0, -1.0, -1.0],
                     [1.0, A_R, 0.0],
                     [x[2], 0.0, x[0] - C_R]])


# ---- B1: equilibria, published (2.29) flows.pdf p. 24 (printed to 4 dp / 3 dp)

PUB_EQ = {"minus": [0.0070, -0.0351, 0.0351], "plus": [5.6929, -28.464, 28.464]}
# the book TRUNCATES its printed decimals (e.g. our 5.6929738 prints as 5.6929,
# our -28.4648690 as -28.464), so the gate is 1 ULP of the printed last digit
TOL_EQ = {"minus": 1e-4, "plus": 1e-3}

D = np.sqrt(1.0 - 4.0 * A_R * B_R / C_R ** 2)
eq = {"minus": 0.5 * (1 - D) * np.array([C_R, -C_R / A_R, C_R / A_R]),
      "plus": 0.5 * (1 + D) * np.array([C_R, -C_R / A_R, C_R / A_R])}
ok1, det1 = True, {}
for k, x_eq in eq.items():
    res = float(np.linalg.norm(rossler(x_eq)))
    dev = float(np.max(np.abs(x_eq - PUB_EQ[k])))
    ok1 &= res < 1e-12 and dev < TOL_EQ[k]
    det1[k] = {"computed": x_eq.tolist(), "published": PUB_EQ[k],
               "f_residual": res, "dev_vs_printed": dev}
gate("B1_rossler_equilibria", ok1, det1)

# ---- B2: equilibrium exponents, published (4.36) stability.pdf p. 17

PUB_EIG = {"minus": {"mu1": -5.686, "mu2": 0.0970, "om2": 0.9951},
           "plus": {"mu1": 0.1929, "mu2": -4.596e-6, "om2": 5.428}}
TOL_EIG = {"minus": {"mu1": 1e-3, "mu2": 1e-4, "om2": 1e-4},  # 1 ULP printed
           "plus": {"mu1": 1e-4, "mu2": 1e-9, "om2": 1e-3}}

ok2, det2 = True, {}
for k, x_eq in eq.items():
    lam = np.linalg.eigvals(rossler_jac(x_eq))
    real_i = int(np.argmin(np.abs(lam.imag)))
    pair = lam[[i for i in range(3) if i != real_i]]
    got = {"mu1": float(lam[real_i].real), "mu2": float(pair[0].real),
           "om2": float(np.abs(pair[0].imag))}
    devs = {q: abs(got[q] - PUB_EIG[k][q]) for q in got}
    ok2 &= all(devs[q] < TOL_EIG[k][q] for q in devs)
    det2[k] = {"computed": got, "published": PUB_EIG[k], "dev": devs}
gate("B2_rossler_eigenvalues", ok2, det2)

# ---- B3: exercise 5.1 (invariants.pdf p. 14): the one flow with an analytic
# Floquet exponent. dq/dt = p + q(1-q^2-p^2), dp/dt = -q + p(1-q^2-p^2).
# In polar form dr/dt = r(1-r^2), dtheta/dt = -1: limit cycle r = 1, T = 2 pi;
# linearizing d(dr)/dt = (1-3r^2) dr = -2 dr on the cycle gives multipliers
# {1, e^{-4 pi}} (our derivation, machine-checked here).


def ermentrout(x):
    s = 1.0 - x[0] ** 2 - x[1] ** 2
    return np.array([x[1] + x[0] * s, -x[0] + x[1] * s])


def ermentrout_jac(x):
    q, p = x
    s = 1.0 - q ** 2 - p ** 2
    return np.array([[s - 2 * q * q, 1.0 - 2 * q * p],
                     [-1.0 - 2 * q * p, s - 2 * p * p]])


cyc = find_cycle(ermentrout, ermentrout_jac, [1.3, 0.0], 6.0, m=2)
mult, _ = floquet(ermentrout, ermentrout_jac, cyc)
r_dev = float(abs(np.linalg.norm(cyc["points"][0]) - 1.0))
T_dev = float(abs(cyc["T"] - 2.0 * np.pi))
m_dev = float(np.max(np.abs(np.sort(mult.real) -
                            np.sort([1.0, np.exp(-4.0 * np.pi)]))))
ok3 = cyc["converged"] and r_dev < 1e-9 and T_dev < 1e-9 and m_dev < 1e-8
gate("B3_analytic_floquet_ex5p1", ok3,
     {"T": cyc["T"], "T_dev": T_dev, "r_dev": r_dev,
      "multipliers": sorted(mult.real.tolist()),
      "analytic": [float(np.exp(-4.0 * np.pi)), 1.0], "mult_dev": m_dev})

# ---- B4: exercise 16.9 table (cycles.pdf p. 12): all Rossler cycles to
# topological length 7: itinerary, section point (0, y_p, z_p), expanding
# eigenvalue Lambda_e.

PUB_CYCLES = [  # (itinerary, y_p, z_p, Lambda_e) transcribed from the table
    ("1", 6.091768, 1.299732, -2.403953),
    ("01", 3.915804, 3.692833, -3.512007),
    ("001", 2.278281, 7.416481, -2.341923),
    ("011", 2.932877, 5.670806, 5.344908),
    ("0111", 3.466759, 4.506218, -16.69674),
    ("01011", 4.162799, 3.303903, -23.19958),
    ("01111", 3.278914, 4.890452, 36.88633),
    ("001011", 2.122094, 7.886173, -6.857665),
    ("010111", 4.059211, 3.462266, 61.64909),
    ("011111", 3.361494, 4.718206, -92.08255),
    ("0101011", 3.842769, 3.815494, 77.76110),
    ("0110111", 3.025957, 5.451444, -95.18388),
    ("0101111", 4.102256, 3.395644, -142.2380),
    ("0111111", 3.327986, 4.787463, 218.0284),
]

PLANE = (np.array([1.0, 0.0, 0.0]), 0.0)  # x = 0, crossings with dx/dt < 0
pts, ts = poincare_section(rossler, [1.0, 5.0, 0.0], PLANE, direction=-1,
                           n_cross=2500, t_transient=300.0, t_max=2.0e4,
                           rtol=1e-11, atol=1e-11)
print(f"  section: {len(pts)} crossings harvested")

found = {}  # canonical crossing-set key -> cycle record
for n in range(1, 8):
    top, sep = (14, 0.05) if n < 5 else (40, 0.008)
    for k in close_returns(pts, n, top=top, min_sep=sep):
        xs0 = pts[k:k + n]
        T0 = ts[k + n] - ts[k]
        cyc = find_cycle(rossler, rossler_jac, xs0, T0, tol=1e-10)
        if not cyc["converged"]:
            continue
        # crossings of the converged cycle on the section
        cpts, cts = poincare_section(rossler, cyc["points"][0], PLANE,
                                     direction=-1, n_cross=n + 1,
                                     t_max=1.2 * cyc["T"])
        cpts = cpts[:n]
        # repeat of a shorter cycle: fewer distinct crossings than n
        dmat = np.linalg.norm(cpts[:, None] - cpts[None, :], axis=2)
        n_distinct = int((dmat[0] > 1e-4).sum()) + 1
        if n_distinct < n:
            continue
        key = tuple(np.round(np.sort(cpts[:, 1]), 5))
        if key in found:
            continue
        mult, _ = floquet(rossler, rossler_jac, cyc)
        lam_e = float(mult[0].real)  # expanding multiplier (real for Rossler)
        found[key] = {"n": n, "T": cyc["T"], "crossings": cpts.tolist(),
                      "Lambda_e": lam_e, "residual": cyc["residual"]}
print(f"  cycles: {len(found)} distinct converged")

# match found cycles to the published rows
rows, n_match = [], 0
for it, yp, zp, lam_p in PUB_CYCLES:
    n = len(it)
    best = None
    for key, c in found.items():
        if c["n"] != n:
            continue
        dev = min(np.hypot(cy - yp, cz - zp) for _, cy, cz in c["crossings"])
        if best is None or dev < best[0]:
            best = (dev, c)
    if best is None:
        rows.append({"itinerary": it, "published": [yp, zp, lam_p],
                     "status": "NOT FOUND"})
        continue
    dev, c = best
    lam_rel = abs(c["Lambda_e"] - lam_p) / abs(lam_p)
    ok = dev < 2e-5 and lam_rel < 2e-5
    n_match += ok
    rows.append({"itinerary": it, "published": [yp, zp, lam_p],
                 "point_dev": float(dev), "Lambda_ours": c["Lambda_e"],
                 "Lambda_rel_dev": float(lam_rel), "T": c["T"],
                 "status": "ok" if ok else "DEVIATES"})
gate("B4_rossler_cycle_table", n_match == len(PUB_CYCLES),
     {"matched": n_match, "of": len(PUB_CYCLES), "rows": rows})

# ---- B5: tables 18.2 + 18.3 (count.pdf pp. 5, 14): binary periodic points
# N_n = tr T^n and prime-cycle counts M_n by Mobius inversion (necklaces).

PUB_18_2_Nn = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
PUB_18_2_Mn_diag = [2, 1, 2, 3, 6, 9, 18, 30, 56, 99]  # M_n at n_p = n column
PUB_18_3 = {2: [2, 1, 2, 3, 6, 9, 18, 30, 56, 99],
            3: [3, 3, 8, 18, 48, 116, 312, 810, 2184, 5880],
            4: [4, 6, 20, 60, 204, 670, 2340, 8160, 29120, 104754]}


def M_prime(n, N):
    return sum(int(mobius(d)) * N ** (n // d) for d in divisors(n)) // n


T2 = np.ones((2, 2), int)
ok5, det5 = True, {}
Nn_ours = [int(np.trace(np.linalg.matrix_power(T2, n))) for n in range(1, 11)]
ok5 &= Nn_ours == PUB_18_2_Nn
det5["Nn_trace_vs_18_2"] = Nn_ours
Mn_ours = {N: [M_prime(n, N) for n in range(1, 11)] for N in (2, 3, 4)}
for N in (2, 3, 4):
    ok5 &= Mn_ours[N] == PUB_18_3[N]
ok5 &= Mn_ours[2] == PUB_18_2_Mn_diag
# consistency (18.6): sum over n_p | n of n_p M_{n_p} = N_n
ok5 &= all(sum(d * M_prime(d, 2) for d in divisors(n)) == 2 ** n
           for n in range(1, 11))
det5["Mn_mobius"] = Mn_ours
gate("B5_counting_tables", ok5, det5)

# --------------------------------------------------------------------- plot

fig, ax = plt.subplots(1, 3, figsize=(15, 4.6))
traj = np.array([pts[i] for i in range(len(pts))])
u, v = return_map(pts, coord=1)
ax[0].plot(u, v, ".", ms=2, color="tab:blue")
ax[0].plot([u.min(), u.max()], [u.min(), u.max()], "k--", lw=0.7)
for it, yp, zp, _ in PUB_CYCLES:
    ax[0].axvline(yp, color="tab:red", lw=0.4, alpha=0.5)
ax[0].set(xlabel="$y_k$", ylabel="$y_{k+1}$",
          title="Rössler return map on $x{=}0$, $\\dot{x}<0$\n(red: published cycle points, ex. 16.9)")
ax[1].plot(pts[:, 1], pts[:, 2], ".", ms=2, color="tab:blue", label="crossings")
for it, yp, zp, _ in PUB_CYCLES:
    ax[1].plot(yp, zp, "x", color="tab:red", ms=7)
for c in found.values():
    arr = np.array(c["crossings"])
    ax[1].plot(arr[:, 1], arr[:, 2], "o", mfc="none", mec="k", ms=9, mew=0.8)
ax[1].set(xlabel="$y$", ylabel="$z$",
          title="section points: found cycles (black circles)\nvs published (red x)")
devs = [r.get("point_dev", np.nan) for r in rows]
lrel = [r.get("Lambda_rel_dev", np.nan) for r in rows]
xi = np.arange(len(rows))
ax[2].semilogy(xi, devs, "o-", label="section-point dev")
ax[2].semilogy(xi, lrel, "s-", label="$\\Lambda_e$ rel. dev")
ax[2].axhline(2e-5, color="k", lw=0.6, ls="--", label="gate 2e-5")
ax[2].set_xticks(xi, [r["itinerary"] for r in rows], rotation=60, fontsize=7)
ax[2].set(title="deviation vs the published table, per cycle")
ax[2].legend(fontsize=8)
fig.tight_layout()
fig.savefig("../plots/m7_9_rossler_cycles.png", dpi=140)
print("  plot -> ../plots/m7_9_rossler_cycles.png")

with open("../data/m7_9_benchmark.json", "w") as fh:
    json.dump(results, fh, indent=1,
              default=lambda o: o.item() if hasattr(o, "item") else str(o))
n_fail = sum(not r["pass"] for r in results.values())
print(f"\n{len(results) - n_fail}/{len(results)} benchmarks green -> ../data/m7_9_benchmark.json")
raise SystemExit(1 if n_fail else 0)
