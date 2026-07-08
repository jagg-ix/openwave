"""M7.10 - pure-Maxwell sector, the no-Lagrangian test.

Task doc: research/tasks/m7_10_pure_maxwell.md. Modes:

  python m7_10_pure_maxwell.py gates     E1a exact discrete ABC eigenmode (two dt)
                                         + the M7.9 find_cycle/floquet adapter on
                                         the N=4 lattice Maxwell flow
  python m7_10_pure_maxwell.py cavity    E1b CK spheromak in the Dirichlet box,
                                         2 transient + 20 measured periods
  python m7_10_pure_maxwell.py evap      E2 free-space evaporation, L=16 + L=24
  python m7_10_pure_maxwell.py electron  E3 destruction comparison ON vs OFF
                                         (winner regen ~4 min if npz cache absent)
  python m7_10_pure_maxwell.py ladder    E4 coupling ladder (vacuum rates,
                                         harmonic rungs, destruction times)
  python m7_10_pure_maxwell.py analyze   plots from the saved json

The equations (evolution-first; no variational formalism anywhere in the task).
Temporal gauge, div-free sector, two coupling SWITCHES eps_x (bilinear) and
eps_q (quartic):

    d2A/dt2 = -curl curl A - eps_x J
    d2J/dt2 = -curl curl J - eps_x A - 2 eps_q (c1 + 2 c2 |J|^2) J

eps_x = eps_q = 1 is the canonical M7.5 theory; eps_x = eps_q = 0 is plain
Maxwell (two decoupled free copies; A-only runs drop J). Conserved energy:

    E = int [ 1/2 |dA/dt|^2 + 1/2 |dJ/dt|^2 + 1/2 |curl A|^2 + 1/2 |curl J|^2
              + eps_x A.J + eps_q (c1 |J|^2 + c2 |J|^4) ] d3x

Linearized vacuum (transverse):  M(k) = [[k^2, -eps_x], [-eps_x, k^2 + 2 eps_q c1]]
    det M(0) = -eps_x^2                (the tachyon is carried by the bilinear)
    growth rate at k = 0:  rate = sqrt( sqrt((eps_q c1)^2 + eps_x^2) - eps_q c1 )
    band edge / existence threshold (diagonal eps): k* = w* = 0.786 sqrt(eps)

Known answers used as gates:
  * E1a: the ABC field is an EXACT eigenfield of the discrete central-difference
    curl, lam_h = sin(kh)/h, so A(t) = A0 cos(w t) solves the discrete wave
    equation exactly; velocity-Verlet then oscillates at the ANALYTIC modified
    frequency  w_v = arccos(1 - (lam_h dt)^2 / 2) / dt  (exact for linear
    systems), making the measured period a closed-form known answer.
  * E1b: Theorem 2 of the 2026-07-05 closure notes (audited at receipt): a
    Trkalian field curl F = lam F solves free Maxwell at w = c lam.
  * E2: Arnold's inequality E_curl >= 1/2 lam_1 |H| (lam_1 = the box's smallest
    positive curl eigenvalue); helicity conserved until absorbed.
  * E3: the M7.5 anchors (t_A2_double = 2.6, probe FFT 0.62-0.64, the
    <E_real> = E_omega identity at 1.85e-14, E_real(0) = -0.4831066).
  * E4: the analytic rate curve above; eps = 1 endpoint = the M7.5 numbers.

Headless; matplotlib PNG only. Data: research/data/m7_10_*.json.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from m7_1_harmonic_lattice import (  # noqa: E402
    HarmonicFields, curl_np, dot, grid_xyz, lambda_eff_np,
    seed_abc, seed_ck_spheromak,
)
from m7_4_linked_vortex import (  # noqa: E402
    KAPPA, OMEGA, SHELL, TaichiBlend, apply_vacuum_shell, build_seed,
    helicity_A,
)
from m7_5_clock_stability import (  # noqa: E402
    C1, C2, STATE_NPZ, TaichiLeapfrog, _ti_init, clock_fft, get_winner_state,
)
from m7_6_observables import QCAN_REF, qcan, relax_qcan  # noqa: E402
from m7_9_orbits import find_cycle, floquet  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")

T_CANON = 2 * np.pi / OMEGA


def rate_analytic(eps_x, eps_q, c1=C1):
    """k = 0 vacuum growth rate of M(k) (module docstring); 0 if healthy."""
    w2min = eps_q * c1 - np.sqrt((eps_q * c1) ** 2 + eps_x ** 2)
    return float(np.sqrt(-w2min)) if w2min < 0 else 0.0


def omega_verlet(lam, dt):
    """Exact velocity-Verlet frequency on d2x/dt2 = -lam^2 x."""
    return float(np.arccos(1.0 - 0.5 * (lam * dt) ** 2) / dt)


# =============================================================================
# the eps-switched leapfrog (M7.5 engine with the two couplings scaled)
# =============================================================================


class EpsLeapfrog(TaichiLeapfrog):
    """TaichiLeapfrog with the coupling switches folded into the kernels.

    eps_x scales the bilinear cross force (and the A.J energy term); eps_q is
    folded once into (c1, c2) so the parent's quartic pipeline needs no edit.
    shell=0 makes the box fully periodic (E1a). eps_x=1, eps_q=1 must reproduce
    the parent bit-for-bit up to atomic-reduction rounding (E3 cross-gate).
    """

    def __init__(self, N, L, eps_x=1.0, eps_q=1.0, shell=SHELL):
        self.eps_x = float(eps_x)
        super().__init__(N, L, c1=eps_q * C1, c2=eps_q * C2, shell=shell)

    def _build(self):
        ti = self.ti
        N, h, sh = self.N, self.h, self.shell
        c1, c2, ex = self.c1, self.c2, self.eps_x
        A, J, VA, VJ = self.A, self.J, self.VA, self.VJ
        BA, BJ, FA, FJ = self.BA, self.BJ, self.FA, self.FJ
        ac, as_, gam, red = self.ac, self.as_, self.gam, self.red

        @ti.func
        def curlv(F, i, j, k):
            ip, im = (i + 1) % N, (i - 1 + N) % N
            jp, jm = (j + 1) % N, (j - 1 + N) % N
            kp, km = (k + 1) % N, (k - 1 + N) % N
            dyFz = (F[i, jp, k][2] - F[i, jm, k][2]) / (2 * h)
            dzFy = (F[i, j, kp][1] - F[i, j, km][1]) / (2 * h)
            dzFx = (F[i, j, kp][0] - F[i, j, km][0]) / (2 * h)
            dxFz = (F[ip, j, k][2] - F[im, j, k][2]) / (2 * h)
            dxFy = (F[ip, j, k][1] - F[im, j, k][1]) / (2 * h)
            dyFx = (F[i, jp, k][0] - F[i, jm, k][0]) / (2 * h)
            return ti.Vector([dyFz - dzFy, dzFx - dxFz, dxFy - dyFx])

        @ti.kernel
        def curls():
            for i, j, k in ti.ndrange(N, N, N):
                BA[i, j, k] = curlv(A, i, j, k)
                BJ[i, j, k] = curlv(J, i, j, k)

        @ti.kernel
        def forces():
            for i, j, k in ti.ndrange(N, N, N):
                inside = ((i >= sh) and (i < N - sh) and (j >= sh)
                          and (j < N - sh) and (k >= sh) and (k < N - sh))
                if inside:
                    s = J[i, j, k].dot(J[i, j, k])
                    FA[i, j, k] = -curlv(BA, i, j, k) - ex * J[i, j, k]
                    FJ[i, j, k] = (-curlv(BJ, i, j, k) - ex * A[i, j, k]
                                   - 2.0 * (c1 + 2.0 * c2 * s) * J[i, j, k])
                else:
                    FA[i, j, k] = ti.Vector([0.0, 0.0, 0.0])
                    FJ[i, j, k] = ti.Vector([0.0, 0.0, 0.0])

        @ti.kernel
        def kick(dt_half: ti.f64):
            for i, j, k in ti.ndrange(N, N, N):
                VA[i, j, k] += dt_half * FA[i, j, k]
                VJ[i, j, k] += dt_half * FJ[i, j, k]

        @ti.kernel
        def drift(dt: ti.f64):
            for i, j, k in ti.ndrange(N, N, N):
                A[i, j, k] += dt * VA[i, j, k]
                J[i, j, k] += dt * VJ[i, j, k]

        @ti.kernel
        def damp(dt: ti.f64):
            for i, j, k in ti.ndrange(N, N, N):
                f = ti.exp(-gam[i, j, k] * dt)
                VA[i, j, k] *= f
                VJ[i, j, k] *= f

        @ti.kernel
        def reductions():
            for i in range(8):
                red[i] = 0.0
            for i, j, k in ti.ndrange(N, N, N):
                s = J[i, j, k].dot(J[i, j, k])
                red[0] += 0.5 * (VA[i, j, k].dot(VA[i, j, k])
                                 + VJ[i, j, k].dot(VJ[i, j, k]))
                red[1] += 0.5 * (BA[i, j, k].dot(BA[i, j, k])
                                 + BJ[i, j, k].dot(BJ[i, j, k]))
                red[2] += ex * A[i, j, k].dot(J[i, j, k]) + c1 * s + c2 * s * s
                red[3] += A[i, j, k].dot(ac[i, j, k])
                red[4] += A[i, j, k].dot(as_[i, j, k])
                red[5] += A[i, j, k].dot(A[i, j, k])
                red[6] += s
                red[7] += A[i, j, k].dot(BA[i, j, k])
        self._curls, self._forces = curls, forces
        self._kick, self._drift, self._damp = kick, drift, damp
        self._reductions = reductions

    def zero_J(self):
        z = np.zeros((self.N, self.N, self.N, 3))
        self.J.from_numpy(z)
        self.VJ.from_numpy(z)
        self._curls()
        self._forces()


def load_A(eng, A0, V0=None):
    """Single-field initial data: A = A0, dA/dt = V0 (default 0), J = 0."""
    f = HarmonicFields(eng.N, eng.L)
    f.avc = A0
    if V0 is not None:
        f.avs = V0          # load() sets VA = omega * avs; use omega = 1
        eng.load(f, omega=1.0)
    else:
        eng.load(f, omega=0.0)


# =============================================================================
# evolution driver (eps-correct energy density; the m7_5 trace battery shape)
# =============================================================================


def evolve_tr(eng, t_end, dt, meas_every=4, pull_every=200, sponge=False,
              tag="", radii=()):
    """Run to t_end collecting the light trace (reductions) every meas_every
    steps and the heavy pull channel (r50, E_core, windowed E(<r), helicity is
    red[7] so it stays light) every pull_every steps."""
    n_steps = int(round(t_end / dt))
    tr = {"t": [], "E": [], "E_kin": [], "E_curl": [], "E_pot": [],
          "ov_c": [], "ov_s": [], "A2": [], "J2": [], "H_A_inst": [], "pA": []}
    heavy = {"t": [], "r50": [], "E_core": [],
             "E_win": {f"{r:g}": [] for r in radii}}
    i0, j0, k0 = 3 * eng.N // 4, eng.N // 2, eng.N // 2
    X, Y, Z = grid_xyz(eng.N, eng.L)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    core = r < 0.4 * eng.L
    t0 = time.time()
    for n in range(n_steps + 1):
        t = n * dt
        if n % meas_every == 0:
            m = eng.measure()
            tr["t"].append(t)
            for k in ("E", "E_kin", "E_curl", "E_pot",
                      "ov_c", "ov_s", "A2", "J2", "H_A_inst"):
                tr[k].append(m[k])
            tr["pA"].append([float(x) for x in eng.A[i0, j0, k0]])
            if not np.isfinite(m["E"]):
                print(f"  [{tag}] NON-FINITE at t={t:.2f}: abort")
                break
        if n % pull_every == 0:
            d = eng.pull()
            s = dot(d["J"], d["J"])
            u = (0.5 * (dot(d["VA"], d["VA"]) + dot(d["VJ"], d["VJ"])
                        + dot(curl_np(d["A"], eng.h), curl_np(d["A"], eng.h))
                        + dot(curl_np(d["J"], eng.h), curl_np(d["J"], eng.h)))
                 + eng.eps_x * dot(d["A"], d["J"]) + eng.c1 * s + eng.c2 * s * s)
            cs = np.cumsum(np.sort(u.ravel())[::-1])
            ncells = int(np.searchsorted(cs, 0.5 * cs[-1])) + 1
            heavy["t"].append(t)
            heavy["r50"].append(float((3.0 * ncells * eng.h ** 3
                                       / (4 * np.pi)) ** (1 / 3)))
            heavy["E_core"].append(float(np.sum(u[core]) * eng.h ** 3))
            for rr in radii:
                heavy["E_win"][f"{rr:g}"].append(
                    float(np.sum(u[r < rr]) * eng.h ** 3))
        if n_steps >= 10 and n % (n_steps // 5) == 0 and n > 0:
            m = eng.measure()
            print(f"  [{tag}] t={t:7.1f}  E={m['E']:+.6f}  A2={m['A2']:.4f}  "
                  f"({time.time() - t0:.0f}s)")
        if n < n_steps:
            eng.step(dt, sponge=sponge)
    tr["heavy"] = heavy
    tr["dt"] = dt
    return tr


def fit_cos(t, y, w0):
    """NLLS a cos(w t + phi) + c; returns (w, rel resid). w0 must be within
    ~one FFT bin of the truth (it is: the analytic prediction seeds it)."""
    from scipy.optimize import least_squares
    t, y = np.asarray(t), np.asarray(y)
    a0 = 0.5 * (y.max() - y.min())

    def res(p):
        return p[0] * np.cos(p[1] * t + p[2]) + p[3] - y

    sol = least_squares(res, [a0, w0, 0.0, float(y.mean())],
                        method="lm", xtol=1e-15, ftol=1e-15, max_nfev=20000)
    rel = float(np.linalg.norm(sol.fun) / max(np.linalg.norm(y), 1e-300))
    return float(sol.x[1]), rel


def _ckpt(name, obj):
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, name), "w") as fh:
        json.dump(obj, fh, indent=1,
                  default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(f"wrote data/{name}")


# =============================================================================
# E1a + the find_cycle adapter (mode: gates)
# =============================================================================


def mode_gates(N=64, L=16.0):
    _ti_init()
    out = {"N": N, "L": L, "gates": {}}
    Af, exact = seed_abc(N, L, kmult=1)
    lam_h = float(exact["lam_discrete"])
    h = L / N

    # gate 0: the discrete eigenrelation itself (identity to roundoff)
    C = curl_np(Af, h)
    eig_dev = float(np.max(np.abs(C - lam_h * Af)) / np.max(np.abs(Af)))
    out["lam_h"] = lam_h
    out["lam_continuum"] = float(exact["lam"])
    out["gates"]["eigenrelation"] = {"dev": eig_dev, "pass": eig_dev < 1e-12}
    print(f"E1a: lam_h = {lam_h:.9f} (continuum {exact['lam']:.9f}); "
          f"discrete-curl eigen dev = {eig_dev:.2e}")

    # E1a: 20 periods at two dt; gates vs the ANALYTIC Verlet frequency
    T_h = 2 * np.pi / lam_h
    for fac, key in ((0.2, "dt02"), (0.1, "dt01")):
        dt = fac * h
        eng = EpsLeapfrog(N, L, 0.0, 0.0, shell=0)   # periodic pure Maxwell
        load_A(eng, Af)
        tr = evolve_tr(eng, t_end=20 * T_h, dt=dt,
                       meas_every=(2 if fac == 0.1 else 1),
                       pull_every=10 ** 9, tag=f"E1a {key}")
        t = np.array(tr["t"])
        E = np.array(tr["E"])
        w_v = omega_verlet(lam_h, dt)
        w_fit, fit_rel = fit_cos(t, np.array(tr["ov_c"]), w_v)
        q = len(E) // 4
        secular = float(abs(E[-q:].mean() - E[:q].mean()) / abs(E[0]))
        row = {"dt": dt, "w_verlet": w_v, "w_fit": w_fit,
               "fit_resid_rel": fit_rel,
               "dev_vs_verlet": float(w_fit / w_v - 1.0),
               "dev_vs_lam": float(w_fit / lam_h - 1.0),
               "dev_vs_lam_pred": float((lam_h * dt) ** 2 / 24.0),
               "E_osc_rel": float((E.max() - E.min()) / abs(E[0])),
               "E_osc_bound": float((lam_h * dt) ** 2 / 4.0),
               "E_secular_rel": secular,
               "trace_t": t[::20].tolist(),
               "trace_dE": ((E[::20] - E[0]) / abs(E[0])).tolist()}
        row["pass"] = (abs(row["dev_vs_verlet"]) < 1e-8
                       and row["E_osc_rel"] < row["E_osc_bound"]
                       and secular < 1e-10)
        out["gates"][key] = row
        print(f"  {key}: w_fit = {w_fit:.10f} vs w_verlet = {w_v:.10f} "
              f"(dev {row['dev_vs_verlet']:+.2e}); vs lam_h dev "
              f"{row['dev_vs_lam']:+.3e} (pred {row['dev_vs_lam_pred']:.3e}); "
              f"E osc {row['E_osc_rel']:.2e} (bound {row['E_osc_bound']:.2e}) "
              f"secular {secular:.2e}  -> {'PASS' if row['pass'] else 'FAIL'}")
    r_dt = (out["gates"]["dt02"]["dev_vs_lam"]
            / out["gates"]["dt01"]["dev_vs_lam"])
    out["gates"]["dt2_ratio"] = {"ratio": float(r_dt),
                                 "pass": bool(abs(r_dt - 4.0) < 0.2)}
    print(f"  dt^2 convergence ratio = {r_dt:.4f} (expect 4)")

    # the M7.9 toolkit on the lattice Maxwell flow (N=4, d=384)
    out["find_cycle"] = _gate_find_cycle()
    ok = (out["gates"]["eigenrelation"]["pass"]
          and out["gates"]["dt02"]["pass"] and out["gates"]["dt01"]["pass"]
          and out["gates"]["dt2_ratio"]["pass"]
          and out["find_cycle"]["pass"])
    out["all_pass"] = bool(ok)
    _ckpt("m7_10_gates.json", out)
    print(f"GATES: {'ALL PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


def _gate_find_cycle(Nc=4, L=16.0):
    """E1 second verification route: the M7.9 cycle finder run VERBATIM on the
    lattice Maxwell flow. N=4 keeps dense Newton feasible (d = 2*4^3*3 = 384);
    the discrete ABC eigenrelation is exact at any N >= 3, so the known answer
    T = 2 pi / lam_h is exact.

    Two parts. (1) The GATE: at T0 = T_true the seed IS the orbit, so
    find_cycle must accept it at Newton entry (residual at the integrator
    floor) and floquet must put every multiplier on the unit circle (marginal:
    pure Maxwell has no attractor). (2) The DEMONSTRATION (recorded, not
    gated): seeding a 5% wrong period does NOT recover T_true; Newton lands,
    residual ~ 1e-13, on a DIFFERENT periodic solution (the min-norm lstsq
    step exits into the curl-curl kernel manifold, where any T is a period).
    For the LINEAR flow periodic orbits are non-isolated, so the period
    equation is degenerate BY PHYSICS; period recovery becomes a meaningful
    test only once the flow is nonlinear (the M7.11+ orbit hunt)."""
    h = L / Nc
    nA = Nc ** 3 * 3

    def f(x):
        A = x[:nA].reshape(Nc, Nc, Nc, 3)
        V = x[nA:].reshape(Nc, Nc, Nc, 3)
        return np.concatenate(
            [V.ravel(), (-curl_np(curl_np(A, h), h)).ravel()])

    d = 2 * nA
    M = np.zeros((d, d))
    e = np.zeros(d)
    for j in range(d):          # the flow is linear: constant Jacobian
        e[j] = 1.0
        M[:, j] = f(e)
        e[j] = 0.0

    Af, exact = seed_abc(Nc, L, kmult=1)
    lam_h = float(exact["lam_discrete"])
    T_true = 2 * np.pi / lam_h
    x0 = np.concatenate([Af.ravel(), np.zeros(nA)])
    print(f"find_cycle adapter: N={Nc} lattice flow, d={d}, "
          f"lam_h={lam_h:.6f}, T_true={T_true:.9f}")
    t0 = time.time()
    # (1) the gate: verification at the known period
    cyc = find_cycle(f, lambda x: M, x0, T_true, m=1, tol=1e-8,
                     max_iter=25, verbose=True)
    mult, _ = floquet(f, lambda x: M, cyc)
    T_dev = float(cyc["T"] / T_true - 1.0)
    mult_dev = float(np.max(np.abs(np.abs(mult) - 1.0)))
    row = {"N": Nc, "d": d, "lam_h": lam_h, "T_true": T_true,
           "T_found": float(cyc["T"]), "T_rel_dev": T_dev,
           "converged": bool(cyc["converged"]),
           "residual": float(cyc["residual"]),
           "n_newton": len(cyc["trace"]),
           "mult_max_abs_dev": mult_dev}
    row["pass"] = bool(cyc["converged"] and abs(T_dev) < 1e-10
                       and mult_dev < 1e-6)
    print(f"  verify @ T_true: residual {cyc['residual']:.2e} at Newton "
          f"entry, T unchanged (dev {T_dev:+.1e}), multipliers max ||L|-1| "
          f"= {mult_dev:.2e} -> {'PASS' if row['pass'] else 'FAIL'}")
    # (2) the demonstration: perturbed period -> the degenerate manifold
    cyc2 = find_cycle(f, lambda x: M, x0, 1.05 * T_true, m=1, tol=1e-8,
                      max_iter=25)
    xf = cyc2["points"][0]
    fmag = float(np.linalg.norm(f(xf)) / max(np.linalg.norm(f(x0)), 1e-300))
    row["nonisolation_demo"] = {
        "T_seeded": 1.05 * T_true, "T_found": float(cyc2["T"]),
        "residual": float(cyc2["residual"]),
        "converged": bool(cyc2["converged"]),
        "f_norm_rel_vs_seed": fmag,
        "dist_from_seed_rel": float(np.linalg.norm(xf - x0)
                                    / np.linalg.norm(x0))}
    row["wall_s"] = float(time.time() - t0)
    dm = row["nonisolation_demo"]
    print(f"  non-isolation demo: seeded T = 1.05 T_true -> converged "
          f"{dm['converged']} at T = {dm['T_found']:.6f} (NOT T_true), "
          f"residual {dm['residual']:.1e}; found point |f|/|f(seed)| = "
          f"{dm['f_norm_rel_vs_seed']:.2e}, moved "
          f"{dm['dist_from_seed_rel']:.2e} of |seed| "
          f"(the degenerate kernel manifold: linear Maxwell has no "
          f"isolated orbits)")
    return row


# =============================================================================
# E1b (mode: cavity)
# =============================================================================


def mode_cavity(N=64, L=16.0, n_transient=2, n_measured=20):
    """E1b. The truncated CK ball in a CUBIC Dirichlet box is NOT a pure
    eigenmode of the discrete curl (the C0 sheet + box geometry mix in the
    box's own cavity modes), so the honest known answers are:

      (1) while the launch is still COHERENT, the overlap <A(t), A_seed>
          oscillates at the INNER BALL's discrete eigenvalue lam_eff
          (Theorem 2: the Trkalian field rings at its own lambda). The
          first candidate for this gate, the seed RMS frequency
          w_rms = sqrt(int |curl_h A0|^2 / int |A0|^2), was REFUTED by the
          measurement: w_rms = 1.19 is dominated by the C0 sheet's high-k
          content, which dephases within a fraction of a period; the
          surviving coherent clock (0.916) sits on lam_eff (0.931, -1.6%),
          not on w_rms. w_rms stays recorded as the refuted candidate;
      (2) the smooth inner ball is discretely Beltrami (alignment ~ 1);
      (3) walls CONFINE: energy at the integrator floor and the core retains
          an O(1) fraction, against E2's ~0.04 with the same seed;
      (4) the LATE spectrum belongs to the box, not the ball (FFT peak,
          purity, 1T return error): REPORTED as the incompatible-walls
          finding, E1a (torus + ABC) carries the exact-eigenmode gate."""
    _ti_init()
    h = L / N
    Bf, meta = seed_ck_spheromak(N, L, a=0.30 * L)
    lam_cont = float(meta["lam"])
    X, Y, Z = grid_xyz(N, L)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    inner = r < 0.8 * meta["a"]        # the smooth region (away from the cutoff)
    C = curl_np(Bf, h)
    lam_eff = float(np.sum(dot(Bf, C)[inner]) / np.sum(dot(Bf, Bf)[inner]))
    w_rms = float(np.sqrt(np.sum(dot(C, C)) / np.sum(dot(Bf, Bf))))
    lam_map, F2 = lambda_eff_np(Bf, h)
    core_a = inner & (F2 > 0.01 * F2.max())
    align = lam_map[core_a] / lam_eff
    print(f"E1b: CK ball a={meta['a']:.3f}, lam_cont={lam_cont:.6f}, inner-"
          f"ball lam_eff={lam_eff:.6f} (dev {lam_eff / lam_cont - 1:+.2e}); "
          f"full-seed w_rms={w_rms:.6f}; alignment median {np.median(align):.4f} "
          f"[q10 {np.quantile(align, 0.1):.4f}, q90 {np.quantile(align, 0.9):.4f}]")

    dt = 0.2 * h
    T = 2 * np.pi / lam_eff
    eng = EpsLeapfrog(N, L, 0.0, 0.0, shell=SHELL)
    load_A(eng, Bf)
    tr = evolve_tr(eng, t_end=(n_transient + n_measured) * T, dt=dt,
                   meas_every=1, pull_every=int(round(2.0 / dt)),
                   tag="E1b cavity")
    t = np.array(tr["t"])
    E = np.array(tr["E"])
    oc = np.array(tr["ov_c"])
    keep = t >= n_transient * T
    # (1) the coherent-launch clock: single cosine over the first 1.5 T
    keep_e = t <= 1.5 * T
    w_early, fit_rel_e = fit_cos(t[keep_e], oc[keep_e], w_rms)
    # (4) the late box spectrum: Hann-FFT dominant peak + purity (reported)
    ck = clock_fft(t[keep], oc[keep], detrend_deg=1, omega=lam_eff)
    w_peak = ck["omega_peak"]
    z = (oc[keep] - oc[keep].mean()) * np.hanning(keep.sum())
    F = np.abs(np.fft.rfft(z)) ** 2
    ipk = int(np.argmax(F[1:])) + 1
    purity = float(F[max(0, ipk - 2):ipk + 3].sum() / F[1:].sum())
    w_fit, fit_rel = fit_cos(t[keep], oc[keep], w_peak)
    q = keep.sum() // 4
    Ek = E[keep]
    secular = float(abs(Ek[-q:].mean() - Ek[:q].mean()) / abs(E[0]))
    E_core_frac = float(tr["heavy"]["E_core"][-1]
                        / max(tr["heavy"]["E_core"][0], 1e-300))
    # one-period leapfrog return error after the transient (radiation stays
    # in the Dirichlet box, so this is bounded by the C0-corner transient)
    n_T = int(round(T / dt))
    eng2 = EpsLeapfrog(N, L, 0.0, 0.0, shell=SHELL)
    load_A(eng2, Bf)
    for _ in range(int(round(n_transient * T / dt))):
        eng2.step(dt)
    s0 = eng2.pull()
    x0n = np.sqrt(sum(np.sum(v ** 2) for v in s0.values()))
    for _ in range(n_T):
        eng2.step(dt)
    s1 = eng2.pull()
    d1 = float(np.sqrt(sum(np.sum((s1[k] - s0[k]) ** 2) for k in s0)) / x0n)

    out = {"N": N, "L": L, "a": meta["a"], "lam_cont": lam_cont,
           "lam_eff_inner": lam_eff, "w_rms_seed": w_rms,
           "align_median": float(np.median(align)),
           "align_q10": float(np.quantile(align, 0.1)),
           "align_q90": float(np.quantile(align, 0.9)),
           "dt": dt,
           "w_early": w_early, "fit_resid_early": fit_rel_e,
           "dev_early_vs_lam_eff": float(w_early / lam_eff - 1.0),
           "dev_early_vs_wrms": float(w_early / w_rms - 1.0),
           "w_peak_late": w_peak, "purity_peak_frac": purity,
           "dev_peak_vs_lam_eff": float(w_peak / lam_eff - 1.0),
           "w_fit_single_cos": w_fit, "fit_resid_rel": fit_rel,
           "E_secular_rel": secular, "E_ptp_rel":
               float((Ek.max() - Ek.min()) / abs(E[0])),
           "E_core_end_frac": E_core_frac,
           "return_err_1T": d1,
           "heavy": tr["heavy"],
           "traces": {"t": t[::8].tolist(), "E": E[::8].tolist(),
                      "ov_c": oc[::8].tolist()}}
    out["gates"] = {
        "clock_coherent": {"dev": out["dev_early_vs_lam_eff"],
                           "pass": abs(out["dev_early_vs_lam_eff"]) < 0.02},
        "alignment": {"median": out["align_median"],
                      "q10": out["align_q10"],
                      "pass": abs(out["align_median"] - 1.0) < 0.01
                      and out["align_q10"] > 0.9},
        "energy": {"secular": secular, "pass": secular < 1e-5},
        "confined": {"E_core_end_frac": E_core_frac,
                     "pass": E_core_frac > 0.2},   # E2 free space: 0.042
    }
    out["all_pass"] = all(g["pass"] for g in out["gates"].values())
    _ckpt("m7_10_cavity.json", out)
    print(f"E1b: coherent clock w_early = {w_early:.6f} vs lam_eff = "
          f"{lam_eff:.6f} (dev {out['dev_early_vs_lam_eff']:+.2e}, fit resid "
          f"{fit_rel_e:.3f}; refuted w_rms candidate {w_rms:.4f}); late box "
          f"peak {w_peak:.4f} purity {purity:.2f} (reported); E secular "
          f"{secular:.2e} ptp {out['E_ptp_rel']:.2e}; E_core end frac "
          f"{E_core_frac:.3f} (E2 free space: 0.042); 1T return err {d1:.2e}")
    print(f"E1b gates: {'ALL PASS' if out['all_pass'] else 'FAIL'}")


# =============================================================================
# E2 (mode: evap)
# =============================================================================


def _helicity_em(A, VA, h):
    """The CONSERVED free-Maxwell helicity H_em = 1/2 (int A.B + int C.E)
    with curl C = E = -dA/dt (C via the FFT inverse curl; the k = 0 mode is
    dropped, and boundary decay is assumed: approximate near the sponge).
    A standing wave's MAGNETIC helicity alone oscillates as cos^2(lam t)."""
    N = A.shape[0]
    B = curl_np(A, h)
    H_A = float(np.sum(dot(A, B)) * h ** 3)
    E = -VA
    # the DISCRETE curl's Fourier symbol i sin(kh)/h, not the continuum i k
    # (the audit's A3 dt-convergence test caught the continuum-symbol bug)
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=h)
    s1 = np.sin(k1 * h) / h
    KX, KY, KZ = np.meshgrid(s1, s1, s1, indexing="ij")
    K2 = KX ** 2 + KY ** 2 + KZ ** 2
    K2[K2 < 1e-14] = 1.0
    Eh = [np.fft.fftn(E[..., i]) for i in range(3)]
    Ch = [1j * (KY * Eh[2] - KZ * Eh[1]) / K2,
          1j * (KZ * Eh[0] - KX * Eh[2]) / K2,
          1j * (KX * Eh[1] - KY * Eh[0]) / K2]
    for a in Ch:
        a[0, 0, 0] = 0.0
    Cf = np.stack([np.real(np.fft.ifftn(a)) for a in Ch], axis=-1)
    H_C = float(np.sum(dot(Cf, E)) * h ** 3)
    return H_A, H_C, 0.5 * (H_A + H_C)


def _evap_run(N, L, t_end, tag):
    h = L / N
    Bf, meta = seed_ck_spheromak(N, L, a=4.8)      # same PHYSICAL ball, both boxes
    C = curl_np(Bf, h)
    inside = meta["inside"]
    lam_eff = float(np.sum(dot(Bf, C)[inside]) / np.sum(dot(Bf, Bf)[inside]))
    eng = EpsLeapfrog(N, L, 0.0, 0.0, shell=SHELL)
    load_A(eng, Bf)
    eng.set_sponge(width=8, gamma0=0.5)            # after load (load zeroes gam)
    dt = 0.2 * h
    n_steps = int(round(t_end / dt))
    pull_every = max(1, int(round(1.0 / dt / 4)) * 4)   # ~1 t-unit, meas-aligned
    tr = evolve_tr(eng, t_end=t_end, dt=dt, meas_every=4,
                   pull_every=pull_every, sponge=True, tag=tag,
                   radii=(3.0, 4.8, 6.0))
    del n_steps
    lam1 = float(np.sin(2 * np.pi / L * h) / h)    # smallest periodic-box curl eig
    E_curl = np.array(tr["E_curl"])
    H = np.array(tr["H_A_inst"])
    arnold_margin = E_curl - 0.5 * lam1 * np.abs(H)
    sponge_face = 0.5 * L - (SHELL + 8) * h
    t_free = max(sponge_face - 4.8, 0.0)           # light time ball edge -> sponge
    t = np.array(tr["t"])
    # the standing wave's known answer: H_A(t) = H_A(0) cos^2(lam_eff t)
    free = (t <= t_free) & (t > 0)
    cos2_dev = (float(np.max(np.abs(H[free] / H[0]
                                    - np.cos(lam_eff * t[free]) ** 2)))
                if free.sum() > 2 and abs(H[0]) > 1e-12 else None)
    # the conserved EM helicity, re-integrated at pull cadence on a fresh run
    eng2 = EpsLeapfrog(N, L, 0.0, 0.0, shell=SHELL)
    load_A(eng2, Bf)
    eng2.set_sponge(width=8, gamma0=0.5)
    tH, Hem = [0.0], []
    d0 = eng2.pull()
    Hem.append(_helicity_em(d0["A"], d0["VA"], h)[2])
    n_sub = pull_every
    for kk in range(int(round(t_end / (n_sub * dt)))):
        for _ in range(n_sub):
            eng2.step(dt, sponge=True)
        d0 = eng2.pull()
        tH.append((kk + 1) * n_sub * dt)
        Hem.append(_helicity_em(d0["A"], d0["VA"], h)[2])
    tH, Hem = np.array(tH), np.array(Hem)
    freeH = (tH <= t_free) & (tH >= 0)
    Hem_drift = (float(np.max(np.abs(Hem[freeH] / Hem[0] - 1.0)))
                 if freeH.sum() > 2 and abs(Hem[0]) > 1e-12 else None)
    return {"N": N, "L": L, "dt": dt, "lam_eff": lam_eff, "lam1": lam1,
            "sponge_face": sponge_face, "t_free": t_free,
            "t": t.tolist(), "E": tr["E"], "E_curl": tr["E_curl"],
            "H_A": H.tolist(), "t_Hem": tH.tolist(), "H_em": Hem.tolist(),
            "arnold_min": float(arnold_margin.min()),
            "arnold_min_rel": float(arnold_margin.min()
                                    / max(E_curl[0], 1e-300)),
            "H_cos2_dev_free": cos2_dev,
            "Hem_drift_free": Hem_drift,
            "Hem_final_frac": float(abs(Hem[-1] / Hem[0]))
            if abs(Hem[0]) > 1e-12 else None,
            "H_final_frac": float(abs(H[-1] / H[0]))
            if abs(H[0]) > 1e-12 else None,
            "heavy": tr["heavy"]}


def mode_evap():
    _ti_init()
    out = {}
    for (N, L, t_end, key) in ((64, 16.0, 40.0, "L16"), (96, 24.0, 40.0, "L24")):
        print(f"E2 {key}: N={N} L={L}")
        out[key] = _evap_run(N, L, t_end, f"E2 {key}")
        hv = out[key]["heavy"]
        th = np.array(hv["t"])
        r50 = np.array(hv["r50"])
        Ec = np.array(hv["E_core"])
        # r50 growth speed: fit while the core still holds > 20% and r50 < 0.35 L
        ok = (Ec > 0.2 * Ec[0]) & (r50 < 0.35 * L) & (th > 0.5)
        speed = (float(np.polyfit(th[ok], r50[ok], 1)[0]) if ok.sum() > 3
                 else None)
        out[key]["r50_speed"] = speed
        out[key]["E_core_final_frac"] = float(Ec[-1] / Ec[0])
        print(f"  r50 speed = {speed}; E_core(t_end)/E_core(0) = "
              f"{out[key]['E_core_final_frac']:.4f}; Arnold min margin "
              f"{out[key]['arnold_min']:.3e} (rel {out[key]['arnold_min_rel']:+.2e}); "
              f"H_A cos^2 dev (free) = {out[key]['H_cos2_dev_free']}; "
              f"H_em drift (free) = {out[key]['Hem_drift_free']}; "
              f"H_em final frac = {out[key]['Hem_final_frac']}")
        _ckpt("m7_10_evap.json", out)   # eager checkpoint after each box
    g = out["L24"]
    gates = {
        "evaporated": {"val": g["E_core_final_frac"],
                       "pass": g["E_core_final_frac"] < 0.05},
        "speed": {"val": g["r50_speed"],
                  "pass": g["r50_speed"] is not None
                  and 0.5 < g["r50_speed"] < 1.2},
        "arnold": {"val": g["arnold_min_rel"],
                   "pass": g["arnold_min_rel"] > -1e-10},
        "helicity_em": {"val": g["Hem_drift_free"],
                        "pass": g["Hem_drift_free"] is not None
                        and g["Hem_drift_free"] < 0.05},
    }
    # H_A vs cos^2(lam t) is REPORTED, not gated: cos^2 presumes a confined
    # standing eigenmode, but the free-space state dephases and evaporates
    # from t = 0 (which is what E2 measures); the conservation-law statement
    # is H_em, and that gate is above.
    out["H_cos2_note"] = {"L24_dev": g["H_cos2_dev_free"]}
    out["gates"] = gates
    out["all_pass"] = all(x["pass"] for x in gates.values())
    _ckpt("m7_10_evap.json", out)
    print(f"E2 gates (on L24): "
          + "  ".join(f"{k}={'PASS' if v['pass'] else 'FAIL'}"
                      for k, v in gates.items()))


# =============================================================================
# E3 (mode: electron)
# =============================================================================


def _identity_gate(f, E_w, n_quad=16):
    """<E_real(t)> over one period == E_omega (the M7.5 (a) check, eps = 1)."""
    h, w = f.h, OMEGA
    Es = []
    for q in range(n_quad):
        tq = 2 * np.pi / w * q / n_quad
        c, s_ = np.cos(w * tq), np.sin(w * tq)
        A = f.avc * c + f.avs * s_
        J = f.jvc * c + f.jvs * s_
        Ad = w * (-f.avc * s_ + f.avs * c)
        Jd = w * (-f.jvc * s_ + f.jvs * c)
        cA, cJ = curl_np(A, h), curl_np(J, h)
        s = dot(J, J)
        Es.append(float(np.sum(0.5 * dot(Ad, Ad) + 0.5 * dot(Jd, Jd)
                               + 0.5 * dot(cA, cA) + 0.5 * dot(cJ, cJ)
                               + dot(A, J) + C1 * s + C2 * s * s) * h ** 3))
    return float(np.mean(Es) / E_w - 1.0)


def mode_electron(N=64, L=16.0, n_periods=8):
    _ti_init()
    f, E_w = get_winner_state(N=N, L=L)
    out = {"N": N, "L": L, "E_w": E_w,
           "E_w_anchor": 6.358028005623311,
           "E_w_anchor_dev": float(E_w / 6.358028005623311 - 1.0),
           "identity_dev": _identity_gate(f, E_w)}
    print(f"E3: E_w = {E_w:.6f} (anchor dev {out['E_w_anchor_dev']:+.2e}); "
          f"<E_real> identity dev = {out['identity_dev']:+.2e}")
    dt = 0.2 * (L / N)
    runs = {}
    # closed-box OFF runs = the controlled no-growth comparison vs ON (they
    # saturate by reflection: r50 plateaus ~1.7x, E_core re-focuses to ~0.5);
    # the DISPERSAL statement itself is measured free-space, on the same
    # state with the E2-validated sponge (off_sponge)
    for key, (ex, eq, drop_J, npd, sponge) in (
            ("on", (1.0, 1.0, False, n_periods, False)),
            ("off_pair", (0.0, 0.0, False, 2 * n_periods, False)),
            ("off_Aonly", (0.0, 0.0, True, 2 * n_periods, False)),
            ("off_sponge", (0.0, 0.0, False, 2 * n_periods, True))):
        eng = EpsLeapfrog(N, L, ex, eq, shell=SHELL)
        eng.load(f, omega=OMEGA)
        if drop_J:
            eng.zero_J()
        if sponge:
            eng.set_sponge(width=8, gamma0=0.5)
        m0 = eng.measure()
        print(f"E3 {key}: eps=({ex},{eq}) J {'dropped' if drop_J else 'kept'}"
              f"{' sponge' if sponge else ''}; E(0) = {m0['E']:+.6f}")
        tr = evolve_tr(eng, t_end=npd * T_CANON, dt=dt, meas_every=2,
                       pull_every=50, sponge=sponge, tag=f"E3 {key}")
        t = np.array(tr["t"])
        A2 = np.array(tr["A2"])
        i_a = np.argmax(A2 > 2 * A2[0]) if np.any(A2 > 2 * A2[0]) else -1
        row = {"eps": [ex, eq], "drop_J": drop_J, "E0": m0["E"],
               "t_A2_double": float(t[i_a]) if i_a >= 0 else None,
               "A2_max_ratio": float(A2.max() / A2[0]),
               "fft_probe_Az": clock_fft(t, np.array(tr["pA"])[:, 2],
                                         t_max=3 * T_CANON),
               "traces": {"t": t[::4].tolist(), "A2": A2[::4].tolist(),
                          "E": np.array(tr["E"])[::4].tolist()},
               "heavy": tr["heavy"]}
        if i_a >= 0:  # tachyon growth rate of A2 (power rate = 2 x amplitude)
            w = (t > t[i_a]) & (A2 < 1e6 * A2[0]) & np.isfinite(A2)
            if w.sum() > 4:
                row["A2_log_rate"] = float(
                    np.polyfit(t[w], np.log(A2[w]), 1)[0])
        hv = tr["heavy"]
        row["r50_0"] = hv["r50"][0]
        row["r50_end"] = hv["r50"][-1]
        # the coupled (eps_x = 1) energy DENSITY is signed (A.J < 0), so the
        # ON run's core integral starts near zero and its ratio (and the
        # sorted-density r50) is meaningless there: report None
        if abs(hv["E_core"][0]) > 1e-3 * abs(m0["E"]) and hv["E_core"][0] > 0:
            row["E_core_end_frac"] = float(hv["E_core"][-1]
                                           / hv["E_core"][0])
            ec = np.array(hv["E_core"]) / hv["E_core"][0]
            th = np.array(hv["t"])
            row["t_core_half"] = (float(th[np.argmax(ec < 0.5)])
                                  if np.any(ec < 0.5) else None)
        else:
            row["E_core_end_frac"] = None
            row["t_core_half"] = None
        runs[key] = row
        print(f"  t_A2_double = {row['t_A2_double']}  A2 max ratio = "
              f"{row['A2_max_ratio']:.3f}  r50 {row['r50_0']:.2f} -> "
              f"{row['r50_end']:.2f}  E_core end frac "
              f"{row['E_core_end_frac']}  fft peak "
              f"{row['fft_probe_Az'].get('omega_peak')}")
        out["runs"] = runs
        _ckpt("m7_10_electron.json", out)   # eager checkpoint per run
    on, op, oa = runs["on"], runs["off_pair"], runs["off_Aonly"]
    gates = {
        "E_w_regen": {"val": out["E_w_anchor_dev"],
                      "pass": abs(out["E_w_anchor_dev"]) < 1e-6},
        "identity": {"val": out["identity_dev"],
                     "pass": abs(out["identity_dev"]) < 1e-12},
        "on_E0_anchor": {"val": on["E0"],
                         "pass": abs(on["E0"] - (-0.48310656075531))
                         < 1e-6 * abs(E_w)},
        "on_double": {"val": on["t_A2_double"],
                      "pass": on["t_A2_double"] is not None
                      and 2.0 <= on["t_A2_double"] <= 3.2},
        "on_fft_band_edge": {"val": on["fft_probe_Az"].get("omega_peak"),
                             "pass": on["fft_probe_Az"].get("omega_peak")
                             is not None
                             and 0.60 <= on["fft_probe_Az"]["omega_peak"] <= 0.67},
        "off_no_growth": {"val": [op["A2_max_ratio"], oa["A2_max_ratio"]],
                          "pass": op["A2_max_ratio"] < 1.5
                          and oa["A2_max_ratio"] < 1.5},
        "off_disperses": {"val": [runs["off_sponge"]["t_core_half"],
                                  runs["off_sponge"]["E_core_end_frac"]],
                          "pass": runs["off_sponge"]["t_core_half"]
                          is not None
                          and runs["off_sponge"]["t_core_half"] < 12.0
                          and runs["off_sponge"]["E_core_end_frac"] < 0.1},
        "off_box_plateau": {"val": [op["r50_end"] / op["r50_0"],
                                    op["E_core_end_frac"]],
                            "pass": True,   # reported: reflection saturation
                            "note": "closed-box r50/E_core saturate by "
                                    "reflection; the dispersal gate is the "
                                    "sponge run above"},
    }
    out["gates"] = gates
    out["all_pass"] = all(x["pass"] for x in gates.values())
    _ckpt("m7_10_electron.json", out)
    print("E3 gates: " + "  ".join(f"{k}={'PASS' if v['pass'] else 'FAIL'}"
                                   for k, v in gates.items()))


# =============================================================================
# E4 (mode: ladder)
# =============================================================================

EPS_DIAG = (1.0, 0.5, 0.25, 0.1, 0.05, 0.025, 0.0)
EPS_ATTR = ((0.0, 1.0), (1.0, 0.0))


def _vacuum_rate(eng, amp, t_end, rng_seed=75):
    """The M7.5 vacuum-probe pattern: smoothed noise, global amplitude rate."""
    from scipy.ndimage import gaussian_filter
    N = eng.N
    rng = np.random.default_rng(rng_seed)
    g = HarmonicFields(N, eng.L)
    for name in ("avc", "jvc"):
        v = rng.standard_normal((N, N, N, 3))
        for i in range(3):
            v[..., i] = gaussian_filter(v[..., i], sigma=1.5)
        setattr(g, name, amp * v / np.sqrt(np.mean(v ** 2)))
    apply_vacuum_shell(g)
    eng.load(g, omega=0.0)
    dt = 0.2 * eng.h
    n_steps = int(t_end / dt)
    ts, a2s = [], []
    for n in range(n_steps + 1):
        if n % 15 == 0:
            m = eng.measure()
            ts.append(n * dt)
            a2s.append(m["A2"])
            if not np.isfinite(m["A2"]):
                break
        if n < n_steps:
            eng.step(dt)
    ts, a2s = np.array(ts), np.array(a2s)
    ok = np.isfinite(a2s) & (a2s > 10 * a2s[0]) & (a2s < 1e10 * a2s[0])
    rate = (float(np.polyfit(ts[ok], np.log(a2s[ok]), 1)[0] / 2)
            if ok.sum() > 3 else None)
    return rate, float(a2s[np.isfinite(a2s)][-1] / a2s[0])


def _r50_state(f):
    u = 0.25 * OMEGA ** 2 * (dot(f.avc, f.avc) + dot(f.avs, f.avs)
                             + dot(f.jvc, f.jvc) + dot(f.jvs, f.jvs))
    X, Y, Z = grid_xyz(f.N, f.L)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    order = np.argsort(r.ravel())
    cu = np.cumsum(u.ravel()[order])
    return float(r.ravel()[order][np.searchsorted(cu, 0.5 * cu[-1])])


def mode_ladder(N=48, L=16.0, n_iter=800, n_periods=15):
    """The eps ladder at 48^3 (grid choice documented: the 64^3 eps=1 anchors
    are the M7.5 scan/vacuum rows; the ladder TREND is the target here)."""
    _ti_init()
    out = {"N": N, "L": L, "n_iter": n_iter, "rungs": []}
    blend = TaichiBlend(N, L)
    points = [(e, e) for e in EPS_DIAG] + list(EPS_ATTR)
    for (ex, eq) in points:
        tag = f"eps=({ex:g},{eq:g})"
        print("=" * 70)
        rp = rate_analytic(ex, eq)
        row = {"eps_x": ex, "eps_q": eq, "rate_pred": rp,
               "diagonal": bool(ex == eq)}
        # (a) vacuum growth rate
        eng = EpsLeapfrog(N, L, ex, eq, shell=SHELL)
        t_end = 30.0 if rp == 0.0 else float(min(100.0, max(20.0, 14.0 / rp)))
        rate, a2_ratio = _vacuum_rate(eng, 1e-6, t_end)
        row["rate_meas"] = rate
        row["A2_end_ratio"] = a2_ratio
        row["rate_ok"] = bool(
            (rp == 0.0 and (rate is None or a2_ratio < 2.0))
            or (rp > 0.0 and rate is not None and abs(rate / rp - 1.0) < 0.05))
        print(f"[{tag}] vacuum: rate = {rate} (pred {rp:.4f})  "
              f"A2 end ratio {a2_ratio:.2e}  -> "
              f"{'OK' if row['rate_ok'] else 'MISS'}")
        # (b) harmonic relaxation at omega = 1, fixed Q_can + H_A
        blend.set_params(OMEGA, ex * KAPPA, eq * C1, eq * C2)
        f0 = apply_vacuum_shell(build_seed("blend", N, L))
        fR, info = relax_qcan(blend, f0, n_iter=n_iter, tag=tag,
                              qcan0=QCAN_REF, log_every=0)
        row["relax"] = {"E": info["E_final"], "gnorm": info["gnorm_final"],
                        "status": info["status"],
                        "H_A": helicity_A(fR), "Q_can": qcan(fR),
                        "maxf": float(np.max(np.abs(fR.pack())))}
        row["r50"] = _r50_state(fR)
        print(f"[{tag}] relax: E = {info['E_final']}  r50 = {row['r50']:.3f}  "
              f"|g| = {info['gnorm_final']}  status = {info['status']}")
        # (c) real-time destruction from the relaxed state (diagonal rungs)
        if row["diagonal"] and info["status"] == "ok":
            eng.load(fR, omega=OMEGA)
            tr = evolve_tr(eng, t_end=n_periods * T_CANON, dt=0.2 * (L / N),
                           meas_every=4, pull_every=60, tag=tag)
            t = np.array(tr["t"])
            A2 = np.array(tr["A2"])
            i_a = np.argmax(A2 > 2 * A2[0]) if np.any(A2 > 2 * A2[0]) else -1
            row["t_A2_double"] = float(t[i_a]) if i_a >= 0 else None
            th = np.array(tr["heavy"]["t"])
            r50t = np.array(tr["heavy"]["r50"])
            i_r = (np.argmax(r50t > 2 * r50t[0])
                   if np.any(r50t > 2 * r50t[0]) else -1)
            row["t_r50_double"] = float(th[i_r]) if i_r >= 0 else None
            row["E_core_end_frac"] = float(
                tr["heavy"]["E_core"][-1] / max(tr["heavy"]["E_core"][0],
                                                1e-300))
            print(f"[{tag}] destroy: t_A2x2 = {row['t_A2_double']}  "
                  f"t_r50x2 = {row['t_r50_double']}  E_core end "
                  f"{row['E_core_end_frac']:.3f}")
        out["rungs"].append(row)
        _ckpt("m7_10_ladder.json", out)     # eager checkpoint per rung
    diag = [r for r in out["rungs"] if r["diagonal"] and r["rate_pred"] > 0]
    out["gates"] = {
        "rates": {"pass": all(r["rate_ok"] for r in out["rungs"])},
        "eps0_healthy": {"pass": all(
            r["rate_ok"] for r in out["rungs"] if r["rate_pred"] == 0.0)},
        "curve": {"vals": [(r["eps_x"], r["rate_meas"], r["rate_pred"])
                           for r in diag]},
    }
    out["all_pass"] = out["gates"]["rates"]["pass"]
    _ckpt("m7_10_ladder.json", out)
    print(f"E4 gates: rates {'ALL PASS' if out['all_pass'] else 'FAIL'}")


# =============================================================================
# plots (mode: analyze)
# =============================================================================


def mode_analyze():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(PLOTS, exist_ok=True)

    def _load(name):
        p = os.path.join(DATA, name)
        if os.path.exists(p):
            with open(p) as fh:
                return json.load(fh)
        return None

    ga, cv = _load("m7_10_gates.json"), _load("m7_10_cavity.json")
    if ga and cv:
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
        ax = axes[0]
        for key, c in (("dt02", "C0"), ("dt01", "C1")):
            g = ga["gates"][key]
            ax.plot(np.array(g["trace_t"]) / (2 * np.pi / ga["lam_h"]),
                    g["trace_dE"], c, lw=0.8,
                    label=f"dt={g['dt']:.4f}: osc {g['E_osc_rel']:.1e}, "
                          f"secular {g['E_secular_rel']:.1e}")
        ax.set_title("E1a exact ABC eigenmode: energy error, 20 periods")
        ax.set_xlabel("t / T")
        ax.set_ylabel("(E - E0)/|E0|")
        ax.legend(fontsize=7)
        ax = axes[1]
        devs = [abs(ga["gates"][k]["dev_vs_lam"]) for k in ("dt01", "dt02")]
        preds = [ga["gates"][k]["dev_vs_lam_pred"] for k in ("dt01", "dt02")]
        dts = [ga["gates"][k]["dt"] for k in ("dt01", "dt02")]
        ax.loglog(dts, devs, "o-", label="measured |w - lam_h|/lam_h")
        ax.loglog(dts, preds, "k--", label="analytic (lam dt)^2/24")
        ax.set_title("E1a clock error = the Verlet dispersion, exactly")
        ax.set_xlabel("dt")
        ax.legend(fontsize=8)
        ax = axes[2]
        t = np.array(cv["traces"]["t"])
        oc = np.array(cv["traces"]["ov_c"])
        T = 2 * np.pi / cv["lam_eff_inner"]
        ax.plot(t / T, oc / np.abs(oc).max(), lw=0.7)
        ax.set_title(f"E1b CK cavity: coherent clock dev "
                     f"{cv['dev_early_vs_wrms']:+.1e} vs w_rms; late box "
                     f"peak {cv['w_peak_late']:.3f} (purity "
                     f"{cv['purity_peak_frac']:.2f})")
        ax.set_xlabel("t / T")
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "m7_10_e1_cavity.png"), dpi=130)
        print("wrote plots/m7_10_e1_cavity.png")

    ev = _load("m7_10_evap.json")
    if ev:
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
        ax = axes[0]
        for key, c in (("L16", "C3"), ("L24", "C0")):
            hv = ev[key]["heavy"]
            ax.plot(hv["t"], np.array(hv["E_core"]) / hv["E_core"][0],
                    c, label=f"{key}: end {ev[key]['E_core_final_frac']:.3f}")
        ax.set_title("E2 free space: core energy drains (evaporation)")
        ax.set_xlabel("t")
        ax.set_ylabel("E_core / E_core(0)")
        ax.legend(fontsize=8)
        ax = axes[1]
        for key, c in (("L16", "C3"), ("L24", "C0")):
            hv = ev[key]["heavy"]
            ax.plot(hv["t"], hv["r50"], c,
                    label=f"{key} (speed {ev[key]['r50_speed'] or 0:.2f})")
        ax.plot([0, 10], [ev["L24"]["heavy"]["r50"][0],
                          ev["L24"]["heavy"]["r50"][0] + 10], "k--", lw=0.8,
                label="speed 1 (w = k)")
        ax.set_title("E2: r50(t) grows at the light speed")
        ax.set_xlabel("t")
        ax.set_ylabel("r50")
        ax.legend(fontsize=8)
        ax = axes[2]
        g = ev["L24"]
        tt = np.array(g["t"])
        ax.plot(tt, np.array(g["H_A"]) / g["H_A"][0], "C0", lw=0.8,
                label="H_A(t)/H_A(0)")
        ax.plot(tt, np.cos(g["lam_eff"] * tt) ** 2, "k--", lw=0.7,
                label="cos^2(lam_eff t) (standing-wave known answer)")
        if "H_em" in g:
            ax.plot(g["t_Hem"], np.array(g["H_em"]) / g["H_em"][0], "C3",
                    lw=1.4, label="H_em (conserved) / H_em(0)")
        ax.axvline(g["t_free"], color="k", ls=":", lw=0.8,
                   label=f"sponge reach t = {g['t_free']:.1f}")
        ax.set_title(f"E2 L24: helicity, standing-wave cos^2 vs conserved "
                     f"H_em; Arnold margin min {g['arnold_min_rel']:+.1e}")
        ax.set_xlabel("t")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "m7_10_e2_evap.png"), dpi=130)
        print("wrote plots/m7_10_e2_evap.png")

    el = _load("m7_10_electron.json")
    if el and "runs" in el:
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
        ax = axes[0]
        for key, c in (("on", "C3"), ("off_pair", "C0"), ("off_Aonly", "C2"),
                       ("off_sponge", "C4")):
            r = el["runs"].get(key)
            if r:
                tr = r["traces"]
                ax.semilogy(np.array(tr["t"]) / T_CANON,
                            np.array(tr["A2"]) / tr["A2"][0], c, label=key)
        ax.axhline(2, color="k", lw=0.6, ls="--")
        ax.set_title("E3 one state, two deaths: |A|^2 (ON grows, OFF does not)")
        ax.set_xlabel("t / T")
        ax.set_ylabel("A2 / A2(0)")
        ax.legend(fontsize=8)
        ax = axes[1]
        for key, c in (("off_pair", "C0"), ("off_Aonly", "C2"),
                       ("off_sponge", "C4")):
            r = el["runs"].get(key)
            if r:
                ax.plot(np.array(r["heavy"]["t"]) / T_CANON,
                        r["heavy"]["r50"], c, label=key)
        ax.set_title("E3: r50(t), the OFF death is dispersion")
        ax.set_xlabel("t / T")
        ax.set_ylabel("r50")
        ax.legend(fontsize=8)
        ax = axes[2]
        r = el["runs"].get("on")
        if r:
            tr = r["traces"]
            ax.plot(np.array(tr["t"]) / T_CANON,
                    np.array(tr["E"]) - tr["E"][0], "C3")
            pk = r["fft_probe_Az"].get("omega_peak")
            ax.set_title(f"E3 ON energy error (tachyon runaway); "
                         f"probe FFT peak {pk:.3f} (band edge)")
            ax.set_xlabel("t / T")
            ax.set_yscale("symlog", linthresh=1e-3)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "m7_10_e3_electron.png"), dpi=130)
        print("wrote plots/m7_10_e3_electron.png")

    la = _load("m7_10_ladder.json")
    if la:
        fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
        diag = [r for r in la["rungs"] if r["diagonal"]]
        attr = [r for r in la["rungs"] if not r["diagonal"]]
        ax = axes[0]
        es = np.array([r["eps_x"] for r in diag if r["rate_pred"] > 0])
        rm = np.array([r["rate_meas"] or np.nan for r in diag
                       if r["rate_pred"] > 0])
        ax.loglog(es, rm, "o", label="measured")
        ee = np.geomspace(0.02, 1.2, 50)
        ax.loglog(ee, 0.7861513778 * np.sqrt(ee), "k--",
                  label="0.786 sqrt(eps)")
        for r in attr:
            ax.plot(max(r["eps_x"], 0.02), r["rate_meas"] or 1e-3, "s",
                    label=f"attr ({r['eps_x']:g},{r['eps_q']:g}): "
                          f"{r['rate_meas'] or 0:.3f}")
        ax.set_title("E4a vacuum growth rate: the pre-registered curve")
        ax.set_xlabel("eps")
        ax.set_ylabel("rate")
        ax.legend(fontsize=7)
        ax = axes[1]
        ax.semilogx(np.maximum([r["eps_x"] for r in diag], 0.005),
                    [r["r50"] for r in diag], "o-")
        ax.set_title("E4b minimizer size r50(eps) at fixed Q_can + H_A")
        ax.set_xlabel("eps (0 plotted at 0.005)")
        ax.set_ylabel("r50")
        ax = axes[2]
        dd = [r for r in diag if r.get("t_A2_double") or r.get("t_r50_double")]
        ax.loglog([max(r["eps_x"], 0.005) for r in dd],
                  [r["t_A2_double"] or np.nan for r in dd], "o-",
                  label="t A2 x2 (tachyon)")
        ax.loglog([max(r["eps_x"], 0.005) for r in dd],
                  [r["t_r50_double"] or np.nan for r in dd], "s-",
                  label="t r50 x2 (dispersion)")
        ee = np.geomspace(0.02, 1.2, 50)
        ax.loglog(ee, np.log(2) / (2 * 0.7861513778 * np.sqrt(ee)), "k--",
                  lw=0.8, label="ln2 / (2 rate(eps))")
        ax.set_title("E4c destruction times: the crossover")
        ax.set_xlabel("eps")
        ax.legend(fontsize=7)
        fig.tight_layout()
        fig.savefig(os.path.join(PLOTS, "m7_10_e4_ladder.png"), dpi=130)
        print("wrote plots/m7_10_e4_ladder.png")


# =============================================================================


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["gates", "cavity", "evap", "electron",
                                     "ladder", "analyze"])
    args = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    {"gates": mode_gates, "cavity": mode_cavity, "evap": mode_evap,
     "electron": mode_electron, "ladder": mode_ladder,
     "analyze": mode_analyze}[args.mode]()


if __name__ == "__main__":
    main()
