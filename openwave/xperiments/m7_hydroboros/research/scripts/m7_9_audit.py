"""M7.9 adversarial audit: refute the benchmark claims by independent methods.

The audit deliberately shares NO machinery with the benchmark pipeline
(m7_9_orbits.py find_cycle / variational monodromy / RK45 / Mobius formula):

    A1 Rossler cycle table: seed EXACTLY the published section point
       (0, y_p, z_p) from exercise 16.9, integrate with LSODA (different
       stepper family), refine the periodic point by a plain 2D secant Newton
       on the n-th return map in section coordinates (no variational flow),
       and get Lambda_e as the expanding eigenvalue of the FINITE-DIFFERENCE
       return-map Jacobian. Refuted if closure fails or Lambda disagrees.
    A2 exercise 5.1 multiplier: no linearization at all: kick the orbit off
       the r = 1 cycle by eps and measure the actual radial contraction over
       one period; must reproduce e^{-4 pi} as eps -> 0.
    A3 counting: brute-force enumeration of all binary/ternary/quaternary
       strings up to n = 10, prime cycles found by rotation classes; must
       reproduce the Mobius counts of tables 18.2/18.3 exactly.

Run: python3 m7_9_audit.py    writes ../data/m7_9_audit.json
"""

import json

import numpy as np
from scipy.integrate import solve_ivp

A_R, B_R, C_R = 0.2, 0.2, 5.7  # (2.28)


def rossler(t, x):
    return [-x[1] - x[2], x[0] + A_R * x[1], B_R + x[2] * (x[0] - C_R)]


def nth_return(y, z, n):
    """n-th return to the section x = 0, dx/dt < 0, via LSODA. Returns (y', z', T)."""

    def event(t, x):
        return x[0]

    event.terminal = False
    event.direction = -1.0
    sol = solve_ivp(rossler, (0.0, 500.0), [0.0, y, z], events=event,
                    method="LSODA", rtol=1e-12, atol=1e-12)
    ts, xs = sol.t_events[0], sol.y_events[0]
    keep = ts > 1e-10
    ts, xs = ts[keep], xs[keep]
    return xs[n - 1][1], xs[n - 1][2], ts[n - 1]


PUB_CYCLES = [  # exercise 16.9 table, cycles.pdf p. 12
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

results = {"A1_rows": []}
print("A1: published-point closure + finite-difference Lambda (LSODA)")
a1_ok = True
for it, yp, zp, lam_p in PUB_CYCLES:
    n = len(it)
    u = np.array([yp, zp])
    # plain Newton on the return map with FD Jacobian (no variational flow)
    for _ in range(20):
        y1, z1, T = nth_return(u[0], u[1], n)
        F = np.array([y1 - u[0], z1 - u[1]])
        if np.linalg.norm(F) < 1e-11:
            break
        eps = 1e-7
        Jr = np.empty((2, 2))
        for j in range(2):
            du = np.zeros(2)
            du[j] = eps
            ya, za, _ = nth_return(*(u + du), n)
            yb, zb, _ = nth_return(*(u - du), n)
            Jr[:, j] = [(ya - yb) / (2 * eps), (za - zb) / (2 * eps)]
        u = u + np.linalg.solve(Jr - np.eye(2), -F)
    seed_dev = float(np.hypot(u[0] - yp, u[1] - zp))
    closure = float(np.linalg.norm(F))
    lam_fd = float(np.linalg.eigvals(Jr)[np.argmax(np.abs(np.linalg.eigvals(Jr)))].real)
    rel = abs(lam_fd - lam_p) / abs(lam_p)
    # A1 gate = this method's noise floor, NOT the benchmark's: the return
    # endpoint carries integration noise amplified by |Lambda| (~|Lambda|*1e-11),
    # divided by 2*eps = 2e-7 in the central difference -> Lambda noise up to
    # ~1e-3 relative on the stiffest cycles. A wrong table value would be O(1).
    ok = closure < 1e-8 and seed_dev < 1e-4 and rel < 1e-3
    a1_ok &= ok
    results["A1_rows"].append(
        {"itinerary": it, "closure": closure, "moved_from_published": seed_dev,
         "Lambda_fd": lam_fd, "Lambda_published": lam_p, "rel_dev": rel,
         "T": float(T), "verdict": "CONFIRMED" if ok else "REFUTED"})
    print(f"  {it:9s} closure {closure:.1e}  Lambda_fd {lam_fd:+.6g} "
          f"vs {lam_p:+.6g}  rel {rel:.1e}  {'ok' if ok else 'REFUTED'}")
results["A1_pass"] = bool(a1_ok)

print("A2: exercise 5.1 multiplier by direct perturbation (no linearization)")


def erm(t, x):
    s = 1.0 - x[0] ** 2 - x[1] ** 2
    return [x[1] + x[0] * s, -x[0] + x[1] * s]


rows = []
for eps in (1e-3, 1e-4, 1e-5):
    sol = solve_ivp(erm, (0.0, 2.0 * np.pi), [1.0 + eps, 0.0],
                    method="LSODA", rtol=1e-13, atol=1e-13)
    r_end = np.linalg.norm(sol.y[:, -1])
    rows.append({"eps": eps, "contraction": (r_end - 1.0) / eps})
dev = abs(rows[-1]["contraction"] - np.exp(-4.0 * np.pi))
results["A2"] = {"rows": rows, "analytic": float(np.exp(-4.0 * np.pi)),
                 "dev_at_smallest_eps": float(dev), "pass": bool(dev < 1e-6)}
print(f"  contraction -> {rows[-1]['contraction']:.4e} vs e^-4pi "
      f"{np.exp(-4.0 * np.pi):.4e}  dev {dev:.1e}")

print("A3: counting by brute-force rotation classes")
PUB_18_3 = {2: [2, 1, 2, 3, 6, 9, 18, 30, 56, 99],
            3: [3, 3, 8, 18, 48, 116, 312, 810, 2184, 5880],
            4: [4, 6, 20, 60, 204, 670, 2340, 8160, 29120, 104754]}


def brute_prime_count(n, N):
    seen, count = set(), 0
    for code in range(N ** n):
        s = np.base_repr(code, N).zfill(n)
        if s in seen:
            continue
        rots = {s[i:] + s[:i] for i in range(n)}
        seen |= rots
        if len(rots) == n:  # not a repeat of a shorter string
            count += 1
    return count


a3_ok = True
for N in (2, 3, 4):
    ours = [brute_prime_count(n, N) for n in range(1, 11)]
    a3_ok &= ours == PUB_18_3[N]
    print(f"  N={N}: {'match' if ours == PUB_18_3[N] else 'MISMATCH'} {ours}")
results["A3"] = {"pass": bool(a3_ok)}

results["verdict"] = ("CONFIRMED" if a1_ok and results["A2"]["pass"] and a3_ok
                      else "REFUTED")
with open("../data/m7_9_audit.json", "w") as fh:
    json.dump(results, fh, indent=1)
print(f"\naudit verdict: {results['verdict']} -> ../data/m7_9_audit.json")
raise SystemExit(0 if results["verdict"] == "CONFIRMED" else 1)
