"""M7.9 E1b: pre-book analytic gates for the orbit toolkit.

Every gate here is closed-form and self-contained: no value is taken from
ChaosBook (or from anywhere else), so the machinery is proven independent of
the benchmark before any book content is consulted. The characteristic-cubic
coefficients in G1 are themselves machine-derived (sympy) rather than quoted.

Gates:
    G1 Lorenz equilibria C+- exist where the formula says + Jacobian eigenvalues
       match the roots of the sympy-derived characteristic cubic
    G2 Henon fixed points (quadratic formula) + analytic multipliers, and the
       map Newton (find_cycle_map) + floquet_map reproduce them from a bad guess
    G3 linear rotation flow: Poincare return time exactly 2*pi, return point
       exact (event-finder accuracy gate)
    G4 harmonic-oscillator energy drift over 100 periods (integrator floor)

Run: python3 m7_9_gates.py            writes ../data/m7_9_gates.json
"""

import json

import numpy as np
import sympy as sp

from m7_9_orbits import (find_cycle_map, floquet_map, flow_endpoint, integrate,
                         poincare_section)

results = {}


def gate(name, ok, detail):
    results[name] = {"pass": bool(ok), **detail}
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {detail}")


# ---------------------------------------------------------------- G1: Lorenz

SIG, RHO, BET = 10.0, 28.0, 8.0 / 3.0


def lorenz(x):
    return np.array([SIG * (x[1] - x[0]),
                     x[0] * (RHO - x[2]) - x[1],
                     x[0] * x[1] - BET * x[2]])


def lorenz_jac(x):
    return np.array([[-SIG, SIG, 0.0],
                     [RHO - x[2], -1.0, -x[0]],
                     [x[1], x[0], -BET]])


q = np.sqrt(BET * (RHO - 1.0))
worst_res, worst_eig = 0.0, 0.0
for s in (+1.0, -1.0):
    C = np.array([s * q, s * q, RHO - 1.0])
    worst_res = max(worst_res, float(np.linalg.norm(lorenz(C))))
    # characteristic cubic of J(C+-), coefficients derived symbolically
    lam, sig_s, rho_s, bet_s = sp.symbols("lam sigma rho beta")
    qs = sp.sqrt(bet_s * (rho_s - 1))
    Js = sp.Matrix([[-sig_s, sig_s, 0],
                    [rho_s - (rho_s - 1), -1, -s * qs],
                    [s * qs, s * qs, -bet_s]])
    poly = sp.Poly(sp.expand((lam * sp.eye(3) - Js).det()), lam)
    coeffs = [float(c.subs({sig_s: SIG, rho_s: RHO, bet_s: BET}))
              for c in poly.all_coeffs()]
    eig_num = np.sort_complex(np.linalg.eigvals(lorenz_jac(C)))
    eig_sym = np.sort_complex(np.roots(coeffs))
    worst_eig = max(worst_eig, float(np.max(np.abs(eig_num - eig_sym))))
gate("G1_lorenz_equilibria", worst_res < 1e-12 and worst_eig < 1e-10,
     {"residual": worst_res, "eig_dev_vs_sympy_cubic": worst_eig,
      "cubic_coeffs": coeffs, "eigs_Cplus": [str(e) for e in eig_num]})

# ----------------------------------------------------------------- G2: Henon

A, B = 1.4, 0.3


def henon(x):
    return np.array([1.0 - A * x[0] ** 2 + B * x[1], x[0]])


def henon_jac(x):
    return np.array([[-2.0 * A * x[0], B], [1.0, 0.0]])


ok2, det2 = True, {}
for sgn, tag in ((+1.0, "xplus"), (-1.0, "xminus")):
    xf = (-(1.0 - B) + sgn * np.sqrt((1.0 - B) ** 2 + 4.0 * A)) / (2.0 * A)
    fp = np.array([xf, xf])
    res = np.linalg.norm(henon(fp) - fp)
    lam_an = np.sort(np.array([-A * xf + sgn2 * np.sqrt(A ** 2 * xf ** 2 + B)
                               for sgn2 in (+1.0, -1.0)]))
    found = find_cycle_map(henon, henon_jac, [fp + 0.05])
    mult, _ = floquet_map(henon_jac, found["points"])
    lam_num = np.sort(mult.real)
    dev_x = float(np.linalg.norm(found["points"][0] - fp))
    dev_l = float(np.max(np.abs(lam_num - lam_an)))
    ok2 &= res < 1e-14 and found["converged"] and dev_x < 1e-11 and dev_l < 1e-9
    det2[tag] = {"x_fixed": xf, "newton_dev": dev_x,
                 "multipliers_analytic": lam_an.tolist(), "mult_dev": dev_l}
gate("G2_henon_fixed_points", ok2, det2)

# ------------------------------------------------------------- G3: rotation


def rot(x):
    return np.array([-x[1], x[0]])


pts, ts = poincare_section(rot, [1.0, 0.0], (np.array([0.0, 1.0]), 0.0),
                           direction=+1, n_cross=3, t_max=25.0)
dev_t = float(np.max(np.abs(ts - 2.0 * np.pi * np.arange(1, 4))))
dev_x = float(np.max(np.abs(pts - np.array([1.0, 0.0]))))
gate("G3_rotation_return", dev_t < 1e-9 and dev_x < 1e-9,
     {"return_time_dev": dev_t, "return_point_dev": dev_x})

# ------------------------------------------------------ G4: integrator floor

xT = flow_endpoint(rot, [1.0, 0.0], 200.0 * np.pi)
drift = float(abs(np.linalg.norm(xT) - 1.0))
gate("G4_energy_drift_100T", drift < 1e-8, {"radius_drift_100T": drift})

# ----------------------------------------------------------------- write out

with open("../data/m7_9_gates.json", "w") as fh:
    json.dump(results, fh, indent=1)
n_fail = sum(not r["pass"] for r in results.values())
print(f"\n{len(results) - n_fail}/{len(results)} gates green -> ../data/m7_9_gates.json")
raise SystemExit(1 if n_fail else 0)
