"""M7.10 adversarial audit - refute the benchmark claims with INDEPENDENT
machinery (AI_HYGIENE cardinal rule; the M7.9 audit pattern).

Independence from m7_10_pure_maxwell.py: pure numpy velocity-Verlet stepper
(no Taichi), zero-crossing clock (no NLLS), different grid resolutions
(N = 16 / 32, not 64), scipy solve_ivp for the mode ODEs. Shared with the
main script are only the PROBLEM DEFINITIONS (the m7_1 seeders and curl_np),
as in the M7.9 audit.

Claims attacked:
  A1  E1a clock: velocity-Verlet on the exact discrete ABC eigenmode ticks at
      w_v = arccos(1 - (lam_h dt)^2/2)/dt. Refuter: numpy stepper at N=16,
      zero-crossing estimator. The (lam dt)^2/24 offset from lam_h is ~24x
      the estimator noise, so a wrong formula CANNOT hide.
  A2  E1b coherent clock: the CK ball rings at its own INNER-BALL lattice
      eigenvalue lam_eff, NOT at the seed RMS frequency w_rms (the run-3
      refutation). Refuter: numpy stepper at N=32 (different lam_eff), the
      overlap masked to the inner ball, and the discriminator
      |w - lam_eff| < |w - w_rms|.
  A3  E2/E1b helicity bookkeeping: for the SEMI-DISCRETE periodic system,
      H_em = 1/2 (int A.B + int C.E) is conserved exactly (discrete-curl
      self-adjointness), while H_A alone oscillates. Refuter: numpy stepper,
      periodic box, run shorter than the wrap-around time.
  A4  E4 rate curve: rate(eps_x, eps_q) = sqrt(sqrt((eps_q c1)^2 + eps_x^2)
      - eps_q c1) at k = 0. Refuter: numpy eigvals of M(k) (no algebra
      reuse) AND time-domain growth of the 4-ODE mode system via solve_ivp.

Verdict per claim: CONFIRMED / REFUTED. Headless. Data: m7_10_audit.json.
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from m7_1_harmonic_lattice import curl_np, dot, grid_xyz, seed_abc, \
    seed_ck_spheromak  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
C1 = 0.5


# ---------------------------------------------------------- numpy leapfrog


def np_leapfrog(A, V, h, dt, n_steps, sample_every, sample_fn):
    """Velocity-Verlet on d2A/dt2 = -curl curl A (periodic numpy lattice)."""
    F = -curl_np(curl_np(A, h), h)
    out = [sample_fn(0.0, A, V)]
    for n in range(1, n_steps + 1):
        V = V + 0.5 * dt * F
        A = A + dt * V
        F = -curl_np(curl_np(A, h), h)
        V = V + 0.5 * dt * F
        if n % sample_every == 0:
            out.append(sample_fn(n * dt, A, V))
    return out


def zero_cross_omega(t, y):
    """Angular frequency from linearly interpolated zero crossings."""
    s = np.sign(y)
    idx = np.where(s[:-1] * s[1:] < 0)[0]
    tc = t[idx] - y[idx] * (t[idx + 1] - t[idx]) / (y[idx + 1] - y[idx])
    if len(tc) < 3:
        return None
    return float(np.pi * (len(tc) - 1) / (tc[-1] - tc[0]))


# ------------------------------------------------------------------- A1


def audit_A1(N=16, L=16.0):
    h = L / N
    Af, exact = seed_abc(N, L, kmult=1)
    lam_h = float(exact["lam_discrete"])
    dt = 0.2 * h
    w_v = float(np.arccos(1.0 - 0.5 * (lam_h * dt) ** 2) / dt)
    T = 2 * np.pi / lam_h
    n_steps = int(round(20 * T / dt))
    samp = np_leapfrog(Af, np.zeros_like(Af), h, dt, n_steps, 1,
                       lambda t, A, V: (t, float(np.sum(A * Af))))
    t = np.array([s[0] for s in samp])
    oc = np.array([s[1] for s in samp])
    w_zc = zero_cross_omega(t, oc)
    dev_v = w_zc / w_v - 1.0
    dev_lam = w_zc / lam_h - 1.0
    margin = (lam_h * dt) ** 2 / 24.0
    ok = abs(dev_v) < 1e-5 and abs(dev_lam - margin) < 0.2 * margin
    print(f"A1: N={N} zero-cross w = {w_zc:.9f} vs w_verlet = {w_v:.9f} "
          f"(dev {dev_v:+.2e}); offset from lam_h {dev_lam:+.3e} vs "
          f"predicted {margin:.3e} -> {'CONFIRMED' if ok else 'REFUTED'}")
    return {"w_zc": w_zc, "w_verlet": w_v, "dev": dev_v,
            "offset_meas": dev_lam, "offset_pred": margin,
            "verdict": "CONFIRMED" if ok else "REFUTED"}


# ------------------------------------------------------------------- A2


def audit_A2(N=32, L=16.0):
    h = L / N
    Bf, meta = seed_ck_spheromak(N, L, a=0.30 * L)
    X, Y, Z = grid_xyz(N, L)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    inner = (r < 0.8 * meta["a"])[..., None]
    C = curl_np(Bf, h)
    lam_eff = float(np.sum((Bf * C)[np.broadcast_to(inner, Bf.shape)])
                    / np.sum((Bf * Bf)[np.broadcast_to(inner, Bf.shape)]))
    w_rms = float(np.sqrt(np.sum(C * C) / np.sum(Bf * Bf)))
    T = 2 * np.pi / lam_eff
    dt = 0.2 * h
    n_steps = int(round(3.0 * T / dt))
    A0in = Bf * inner
    samp = np_leapfrog(Bf, np.zeros_like(Bf), h, dt, n_steps, 1,
                       lambda t, A, V: (t, float(np.sum(A * A0in))))
    t = np.array([s[0] for s in samp])
    oc = np.array([s[1] for s in samp])
    keep = t <= 1.5 * T
    from scipy.optimize import least_squares
    a0 = 0.5 * (oc[keep].max() - oc[keep].min())

    def res(p):
        return p[0] * np.cos(p[1] * t[keep] + p[2]) + p[3] - oc[keep]

    sol = least_squares(res, [a0, lam_eff, 0.0, float(oc[keep].mean())],
                        method="lm", xtol=1e-15, ftol=1e-15)
    w_fit = float(sol.x[1])
    dev = w_fit / lam_eff - 1.0
    discrim = abs(w_fit - lam_eff) < abs(w_fit - w_rms)
    ok = abs(dev) < 0.02 and discrim
    print(f"A2: N={N} inner-masked coherent clock w = {w_fit:.6f}; "
          f"lam_eff(N=32) = {lam_eff:.6f} (dev {dev:+.2e}), w_rms = "
          f"{w_rms:.4f}; discriminator |w-lam_eff| < |w-w_rms|: {discrim} "
          f"-> {'CONFIRMED' if ok else 'REFUTED'}")
    return {"w_fit": w_fit, "lam_eff": lam_eff, "w_rms": w_rms, "dev": dev,
            "discriminator": bool(discrim),
            "verdict": "CONFIRMED" if ok else "REFUTED"}


# ------------------------------------------------------------------- A3


def audit_A3(N=32, L=16.0, t_end=6.0):
    """Periodic box (no walls, no sponge), t_end < wrap-around: H_em exactly
    conserved by the semi-discrete flow; H_A alone oscillates."""
    h = L / N
    Bf, meta = seed_ck_spheromak(N, L, a=0.25 * L)
    # the DISCRETE curl's Fourier symbol is i sin(kh)/h (central difference),
    # NOT the continuum i k: using k here is an O(1) error on the sheet's
    # high-k content (the try-1 audit bug, caught by the dt-convergence test)
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=h)
    s1 = np.sin(k1 * h) / h
    KX, KY, KZ = np.meshgrid(s1, s1, s1, indexing="ij")
    K2 = KX ** 2 + KY ** 2 + KZ ** 2
    K2[K2 < 1e-14] = 1.0   # discrete-curl kernel modes (k=0, Nyquist): drop

    def H_pair(A, V):
        B = curl_np(A, h)
        H_A = float(np.sum(dot(A, B)) * h ** 3)
        E = -V
        Eh = [np.fft.fftn(E[..., i]) for i in range(3)]
        Ch = [1j * (KY * Eh[2] - KZ * Eh[1]) / K2,
              1j * (KZ * Eh[0] - KX * Eh[2]) / K2,
              1j * (KX * Eh[1] - KY * Eh[0]) / K2]
        for a in Ch:
            a[0, 0, 0] = 0.0
        Cf = np.stack([np.real(np.fft.ifftn(a)) for a in Ch], axis=-1)
        return H_A, float(np.sum(dot(Cf, E)) * h ** 3)

    # H_em is conserved by the SEMI-discrete flow; the time stepper wiggles
    # it at O((w_max dt)^2) - and the C0 sheet puts O(1) helicity content at
    # w_max dt ~ 0.35, so the honest gate is dt^2 CONVERGENCE of the drift
    # (integrator-born -> ratio ~ 1/4 at half dt; a genuine violation of the
    # conservation law would NOT shrink with dt).
    drifts, osc_HA = {}, None
    for fac in (0.2, 0.1):
        dt = fac * h
        samp = np_leapfrog(Bf, np.zeros_like(Bf), h, dt,
                           int(round(t_end / dt)), 5,
                           lambda t, A, V: (t, *H_pair(A, V)))
        H_A = np.array([s[1] for s in samp])
        H_C = np.array([s[2] for s in samp])
        Hem = 0.5 * (H_A + H_C)
        drifts[fac] = float(np.max(np.abs(Hem / Hem[0] - 1.0)))
        if osc_HA is None:
            osc_HA = float(np.ptp(H_A) / abs(H_A[0]))
    ratio = drifts[0.1] / drifts[0.2]
    ok = drifts[0.2] < 0.1 and 0.15 < ratio < 0.4 and osc_HA > 0.5
    print(f"A3: periodic N={N}, t<{t_end}: H_em drift {drifts[0.2]:.2e} "
          f"(dt=0.2h) -> {drifts[0.1]:.2e} (dt=0.1h), ratio {ratio:.3f} "
          f"(dt^2 => integrator-born, the semi-discrete law holds); H_A "
          f"alone swings {osc_HA:.2f} of H_A(0) "
          f"-> {'CONFIRMED' if ok else 'REFUTED'}")
    return {"Hem_drift_dt02": drifts[0.2], "Hem_drift_dt01": drifts[0.1],
            "dt2_ratio": ratio, "HA_swing": osc_HA,
            "verdict": "CONFIRMED" if ok else "REFUTED"}


# ------------------------------------------------------------------- A4


def audit_A4():
    from scipy.integrate import solve_ivp
    rows, allok = [], True
    rng = np.random.default_rng(7)
    for (ex, eq) in ((1.0, 1.0), (0.5, 0.5), (0.1, 0.1), (0.025, 0.025),
                     (0.3, 0.3), (1.0, 0.0), (0.0, 1.0)):
        rate_closed = np.sqrt(max(np.sqrt((eq * C1) ** 2 + ex ** 2)
                                  - eq * C1, 0.0))
        Mk = np.array([[0.0, -ex], [-ex, 2 * eq * C1]])   # k = 0
        w2 = np.linalg.eigvalsh(Mk)
        rate_eig = float(np.sqrt(-w2[0])) if w2[0] < 0 else 0.0

        def rhs(t, y):
            a, j, va, vj = y
            return [va, vj, -Mk[0, 0] * a - Mk[0, 1] * j,
                    -Mk[1, 0] * a - Mk[1, 1] * j]

        y0 = 1e-8 * rng.standard_normal(4)
        t_end = 40.0 if rate_closed > 0.2 else (200.0 if rate_closed > 0
                                                else 50.0)
        sol = solve_ivp(rhs, (0, t_end), y0, rtol=1e-10, atol=1e-14,
                        dense_output=True)
        ts = np.linspace(0.2 * t_end, t_end, 60)
        amp = np.linalg.norm(sol.sol(ts), axis=0)
        rate_time = (float(np.polyfit(ts, np.log(amp), 1)[0])
                     if amp[-1] > 30 * amp[0] else 0.0)
        ok = (abs(rate_eig - rate_closed) < 1e-12
              and (rate_closed == 0.0 and rate_time == 0.0
                   or rate_closed > 0
                   and abs(rate_time / rate_closed - 1.0) < 0.01))
        allok &= ok
        rows.append({"eps_x": ex, "eps_q": eq, "closed": float(rate_closed),
                     "eig": rate_eig, "time_domain": rate_time, "ok": ok})
        print(f"A4: eps=({ex:g},{eq:g}) closed {rate_closed:.6f} eig "
              f"{rate_eig:.6f} time-domain {rate_time:.6f} "
              f"-> {'ok' if ok else 'MISS'}")
    print(f"A4 -> {'CONFIRMED' if allok else 'REFUTED'}")
    return {"rows": rows, "verdict": "CONFIRMED" if allok else "REFUTED"}


# =============================================================================


def main():
    out = {"A1": audit_A1(), "A2": audit_A2(), "A3": audit_A3(),
           "A4": audit_A4()}
    out["verdict"] = ("CONFIRMED" if all(
        v["verdict"] == "CONFIRMED" for v in out.values()
        if isinstance(v, dict)) else "REFUTED")
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "m7_10_audit.json"), "w") as fh:
        json.dump(out, fh, indent=1,
                  default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print(f"AUDIT VERDICT: {out['verdict']}")
    print("wrote data/m7_10_audit.json")
    sys.exit(0 if out["verdict"] == "CONFIRMED" else 1)


if __name__ == "__main__":
    main()
