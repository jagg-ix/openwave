"""M7.5 - validate the clock in real time + stability.

Task doc: research/tasks/m7_5_clock_stability.md. Modes:

  python m7_5_clock_stability.py smoke      N=48 machinery check (short relax + evolve)
  python m7_5_clock_stability.py disp       analytic dispersion bands + tachyon window
  python m7_5_clock_stability.py vacuum     vacuum-noise growth rates (the beta* probe,
                                            amplitude-independence = linear instability)
  python m7_5_clock_stability.py main       winner regen (blend/repulsive N=64) + closed-box
                                            leapfrog: short-window clock + destruction time
  python m7_5_clock_stability.py scan       E_omega(omega) scan at fixed H_A incl. the
                                            sub-omega* points + envelope gate
  python m7_5_clock_stability.py analyze    plots from the saved json

The real-time theory (pure-vector sector, temporal gauge, scalars frozen = the
M7.4 sector):

    T = 1/2 |dA/dt|^2 + 1/2 |dJ/dt|^2
    V = 1/2 |curl A|^2 + 1/2 |curl J|^2 + A.J + f(|J|^2),   f(s) = c1 s + c2 s^2

Why this V: its period-average on the doublet A = a_c cos wt + a_s sin wt
reproduces the M7.4 harmonic functional E_w = quad - kappa<A.J> + f_avg EXACTLY
(including the exact quartic average c1 s0 + c2(s0^2 + (s1^2+s2^2)/2)); i.e. the
harmonic functional IS the averaged energy of this theory.  EOM (curl is
self-adjoint on the periodic central-difference lattice, so the discrete force
is the exact gradient of the discrete V the M7.4 relaxation minimized):

    d2A/dt2 = -curl curl A - J
    d2J/dt2 = -curl curl J - A - 2 (c1 + 2 c2 |J|^2) J

Initial conditions from the relaxed doublet: A(0) = a_c, dA/dt(0) = w a_s,
J(0) = j_c, dJ/dt(0) = w j_s.  Velocity-Verlet leapfrog; Dirichlet vacuum shell
(interior-only update, = the relaxation BC).

THE M7.5 HEADLINE (found at smoke, then quantified): the linearized transverse
sector around the vacuum has the frequency matrix

    M(k) = [[k^2, -1], [-1, k^2 + 2 c1]],   det M(0) = -1  for ANY c1

so the bilinear A.J coupling with a massless A is UNCONDITIONALLY tachyonic at
long wavelength: band k^2 < k*^2 with k*^2 = (sqrt(5)-1)/2 (repulsive) or
(1+sqrt(5))/2 (focusing); max growth rate sqrt(-w2_min) at k = 0.  The harmonic
frame is immune because its quadratic form gains the omega^2 stiffness: PSD iff
omega^2 >= k*^2, i.e. omega >= omega* = 0.786 (repulsive, canonical params).
The clock rides above the tachyonic band; the scan mode tests the prediction
that harmonic solitons fail below omega*.

Headless; matplotlib PNG only. Data: research/data/m7_5_*.json.
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
    HarmonicFields, curl_np, div_np, dot, grid_xyz,
)
from m7_4_linked_vortex import (  # noqa: E402
    F_CONV, KAPPA, OMEGA, SHELL, TaichiBlend, apply_vacuum_shell, build_seed,
    helicity_A, qnorm_J, relax_state,
)

DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
STATE_NPZ = os.path.join(DATA, "m7_5_state.npz")   # cache; DELETED at FINISH (>1MB)

CONV = F_CONV["repulsive"]           # the physical branch (M7.4 Q6 verdict)
C1, C2 = CONV["c1"], CONV["c2"]
LAMHALF = 0.5                        # lambda/2 at the canonical lambda = 1


def _ti_init():
    import taichi as ti
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)


# =============================================================================
# real-time leapfrog engine (Taichi)
# =============================================================================


class TaichiLeapfrog:
    """Velocity-Verlet on (A, J) with cached accelerations, Dirichlet shell."""

    def __init__(self, N, L, c1=C1, c2=C2, shell=SHELL):
        import taichi as ti
        self.ti = ti
        self.N, self.L, self.h = N, L, L / N
        self.c1, self.c2, self.shell = c1, c2, shell
        vec = lambda: ti.Vector.field(3, dtype=ti.f64, shape=(N, N, N))  # noqa: E731
        self.A, self.J = vec(), vec()
        self.VA, self.VJ = vec(), vec()
        self.BA, self.BJ = vec(), vec()          # curls (scratch)
        self.FA, self.FJ = vec(), vec()          # accelerations
        self.ac, self.as_ = vec(), vec()         # clock reference doublet (A)
        self.gam = ti.field(dtype=ti.f64, shape=(N, N, N))   # sponge profile
        self.red = ti.field(dtype=ti.f64, shape=(8,))        # reductions
        self._build()

    def _build(self):
        ti = self.ti
        N, h, sh = self.N, self.h, self.shell
        c1, c2 = self.c1, self.c2
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
                    FA[i, j, k] = -curlv(BA, i, j, k) - J[i, j, k]
                    FJ[i, j, k] = (-curlv(BJ, i, j, k) - A[i, j, k]
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
                # 0: kinetic, 1: curl, 2: coupling+quartic  (E = 0+1+2, x h^3)
                red[0] += 0.5 * (VA[i, j, k].dot(VA[i, j, k])
                                 + VJ[i, j, k].dot(VJ[i, j, k]))
                red[1] += 0.5 * (BA[i, j, k].dot(BA[i, j, k])
                                 + BJ[i, j, k].dot(BJ[i, j, k]))
                red[2] += A[i, j, k].dot(J[i, j, k]) + c1 * s + c2 * s * s
                # clock overlaps + amplitudes
                red[3] += A[i, j, k].dot(ac[i, j, k])
                red[4] += A[i, j, k].dot(as_[i, j, k])
                red[5] += A[i, j, k].dot(A[i, j, k])
                red[6] += s
                red[7] += A[i, j, k].dot(BA[i, j, k])     # instantaneous H_A(t)

        self._curls, self._forces = curls, forces
        self._kick, self._drift, self._damp = kick, drift, damp
        self._reductions = reductions

    # ---- host-side API ----

    def load(self, f: HarmonicFields, omega=OMEGA):
        """Doublet -> real-time initial conditions."""
        self.A.from_numpy(np.ascontiguousarray(f.avc))
        self.VA.from_numpy(np.ascontiguousarray(omega * f.avs))
        self.J.from_numpy(np.ascontiguousarray(f.jvc))
        self.VJ.from_numpy(np.ascontiguousarray(omega * f.jvs))
        self.ac.from_numpy(np.ascontiguousarray(f.avc))
        self.as_.from_numpy(np.ascontiguousarray(f.avs))
        self.gam.from_numpy(np.zeros((self.N,) * 3))
        self._curls()
        self._forces()

    def set_sponge(self, width=8, gamma0=0.5):
        """Quadratic damping ramp over `width` cells inside the frozen shell."""
        N, sh = self.N, self.shell
        idx = np.arange(N)
        dmin = np.minimum(idx - sh, N - 1 - sh - idx)   # cells from inner shell face
        d3 = np.minimum.reduce(np.meshgrid(dmin, dmin, dmin, indexing="ij"))
        g = np.where(d3 < width, gamma0 * ((width - d3) / width) ** 2, 0.0)
        g[d3 < 0] = 0.0                                  # frozen shell: no damping needed
        self.gam.from_numpy(np.ascontiguousarray(g.astype(np.float64)))

    def step(self, dt, sponge=False):
        self._kick(0.5 * dt)
        if sponge:
            self._damp(dt)
        self._drift(dt)
        self._curls()
        self._forces()
        self._kick(0.5 * dt)

    def measure(self):
        self._reductions()
        r = self.red.to_numpy()
        h3 = self.h ** 3
        return {"E_kin": r[0] * h3, "E_curl": r[1] * h3, "E_pot": r[2] * h3,
                "E": (r[0] + r[1] + r[2]) * h3,
                "ov_c": r[3] * h3, "ov_s": r[4] * h3,
                "A2": r[5] * h3, "J2": r[6] * h3, "H_A_inst": r[7] * h3}

    def pull(self):
        return {k: getattr(self, k).to_numpy()
                for k in ("A", "J", "VA", "VJ")}


# =============================================================================
# state prep (winner regen, cached)
# =============================================================================


def get_winner_state(N=64, L=16.0, n_iter=1500, force=False):
    """Regen the M7.4 blend/repulsive winner (or load the npz cache).
    Caller must have run _ti_init() already."""
    if os.path.exists(STATE_NPZ) and not force:
        z = np.load(STATE_NPZ)
        if int(z["N"]) == N:
            f = HarmonicFields(N, float(z["L"]))
            for name in ("avc", "avs", "jvc", "jvs"):
                setattr(f, name, z[name])
            print(f"loaded cached winner state {STATE_NPZ} "
                  f"(E_w={float(z['E']):.5f})")
            return f, float(z["E"])
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    f0 = apply_vacuum_shell(build_seed("blend", N, L))
    print(f"regen winner: blend/repulsive N={N} "
          f"(seed H_A={helicity_A(f0):+.4f} Q_J={qnorm_J(f0):.4f})")
    fR, info = relax_state(eng, f0, CONV, n_iter=n_iter, tag="m7_5 regen")
    E = info["E_final"]
    os.makedirs(DATA, exist_ok=True)
    np.savez(STATE_NPZ, N=N, L=L, E=E, avc=fR.avc, avs=fR.avs,
             jvc=fR.jvc, jvs=fR.jvs)
    print(f"cached winner state -> {STATE_NPZ} (E_w={E:.5f})")
    return fR, E


# =============================================================================
# evolution driver + clock analysis
# =============================================================================


def evolve(eng: TaichiLeapfrog, n_periods, dt, omega=OMEGA, sponge=False,
           meas_every=8, heavy_every=250, tag="", f_ref: HarmonicFields = None):
    """Run and collect traces. Returns dict of downsampled time series."""
    T = 2 * np.pi / omega
    n_steps = int(round(n_periods * T / dt))
    tr = {"t": [], "E": [], "E_kin": [], "E_curl": [], "E_pot": [],
          "ov_c": [], "ov_s": [], "A2": [], "J2": [], "H_A_inst": [],
          "pA": [], "pJ": []}
    i0, j0, k0 = 3 * eng.N // 4, eng.N // 2, eng.N // 2   # on the R0 = L/4 ring
    heavy = {"t": [], "q_abs": [], "r50": [], "E_core": []}
    X, Y, Z = grid_xyz(eng.N, eng.L)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    core = r < 0.4 * eng.L
    m0 = eng.measure()
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
            tr["pJ"].append([float(x) for x in eng.J[i0, j0, k0]])
            if not np.isfinite(m["E"]):
                print(f"  [{tag}] NON-FINITE at t={t:.2f}: abort")
                break
        if n % heavy_every == 0:
            d = eng.pull()
            rho = -div_np(d["VA"], eng.h)          # rho(t) = div E_A = -div dA/dt
            q_abs = float(np.sum(np.abs(rho[r < 0.3 * eng.L])) * eng.h ** 3)
            u = (0.5 * (dot(d["VA"], d["VA"]) + dot(d["VJ"], d["VJ"])
                        + dot(curl_np(d["A"], eng.h), curl_np(d["A"], eng.h))
                        + dot(curl_np(d["J"], eng.h), curl_np(d["J"], eng.h)))
                 + dot(d["A"], d["J"]) + C1 * dot(d["J"], d["J"])
                 + C2 * dot(d["J"], d["J"]) ** 2)
            cs = np.cumsum(np.sort(u.ravel())[::-1])
            ncells = int(np.searchsorted(cs, 0.5 * cs[-1])) + 1
            r50 = (3.0 * ncells * eng.h ** 3 / (4 * np.pi)) ** (1 / 3)
            heavy["t"].append(t)
            heavy["q_abs"].append(q_abs)
            heavy["r50"].append(float(r50))
            heavy["E_core"].append(float(np.sum(u[core]) * eng.h ** 3))
        if n % (n_steps // 10 if n_steps >= 10 else 1) == 0 and n > 0:
            m = eng.measure()
            print(f"  [{tag}] t={t:7.1f} ({t / T:6.1f} T)  E={m['E']:+.6f}  "
                  f"A2={m['A2']:.4f}  J2={m['J2']:.4f}  "
                  f"({(time.time() - t0):.0f}s)")
        if n < n_steps:
            eng.step(dt, sponge=sponge)
    tr["heavy"] = heavy
    tr["E0"], tr["dt"], tr["n_steps"] = m0["E"], dt, n_steps
    # one-period return error vs the reference doublet (reduction quality)
    if f_ref is not None:
        n_T = int(round(T / dt))
        tr["n_per_period"] = n_T
    return tr


def clock_fit(tr, omega=OMEGA, t_max=None):
    """Emergent frequency from the overlap phase theta(t) = atan2."""
    t = np.array(tr["t"])
    c = np.array(tr["ov_c"])
    s = np.array(tr["ov_s"])
    if t_max is not None:
        keep = t <= t_max
        t, c, s = t[keep], c[keep], s[keep]
    nc = max(abs(c).max(), 1e-30)
    ns = max(abs(s).max(), 1e-30)
    th = np.unwrap(np.arctan2(s / ns, c / nc))
    # linear fit over the full run
    A = np.vstack([t, np.ones_like(t)]).T
    slope, _ = np.linalg.lstsq(A, th, rcond=None)[0]
    # windowed slopes (drift diagnostic): 10 windows
    wins = []
    for w in np.array_split(np.arange(len(t)), 10):
        if len(w) > 3:
            sl, _ = np.linalg.lstsq(A[w], th[w], rcond=None)[0]
            wins.append(sl)
    # FFT cross-check on ov_c
    dt_s = t[1] - t[0]
    cc = c - c.mean()
    freqs = np.fft.rfftfreq(len(cc), d=dt_s) * 2 * np.pi
    peak = float(freqs[np.argmax(np.abs(np.fft.rfft(cc * np.hanning(len(cc)))))])
    return {"omega_fit": float(slope), "omega_windows": [float(x) for x in wins],
            "omega_fft": peak, "omega_in": omega,
            "rel_dev": float(slope / omega - 1.0)}


def clock_fft(t, y, t_max=None, detrend_deg=4, omega=OMEGA):
    """Tachyon-robust clock: subtract a smooth polynomial trend (the growing
    mode), Hann-window, FFT, quadratic-interpolate the peak."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    if t_max is not None:
        keep = t <= t_max
        t, y = t[keep], y[keep]
    if len(t) < 16:
        return {"omega_peak": None}
    trend = np.polyval(np.polyfit(t, y, detrend_deg), t)
    z = (y - trend) * np.hanning(len(y))
    dt_s = t[1] - t[0]
    F = np.abs(np.fft.rfft(z))
    w = np.fft.rfftfreq(len(z), d=dt_s) * 2 * np.pi
    i = int(np.argmax(F[1:])) + 1
    # parabolic peak interpolation
    if 1 <= i < len(F) - 1:
        d = 0.5 * (F[i - 1] - F[i + 1]) / (F[i - 1] - 2 * F[i] + F[i + 1])
        wpk = w[i] + d * (w[1] - w[0])
    else:
        wpk = w[i]
    return {"omega_peak": float(wpk), "rel_dev": float(wpk / omega - 1.0),
            "n_samples": int(len(t))}


# =============================================================================
# modes
# =============================================================================


def mode_smoke(N=48, L=16.0):
    """Machinery check: early-window energy conservation + clock, two dt."""
    _ti_init()
    f, E_w = get_winner_state(N=N, L=L, n_iter=600, force=True)
    eng = TaichiLeapfrog(N, L)
    out = {"E_w": E_w}
    for fac, key in ((0.2, "dt02"), (0.1, "dt01")):
        eng.load(f)
        tr = evolve(eng, n_periods=4, dt=fac * eng.h, tag=f"smoke {key}",
                    meas_every=4)
        t = np.array(tr["t"])
        E = np.array(tr["E"])
        w1 = t <= 1.5 * 2 * np.pi / OMEGA        # pre-tachyon window
        out[key] = {"E_t0": float(E[0]),
                    "drift_early": float((E[w1].max() - E[w1].min()) / abs(E[0])),
                    "clock_early": clock_fit(tr, t_max=1.5 * 2 * np.pi / OMEGA)}
        print(f"  {key}: E(0)={E[0]:+.5f}  early drift "
              f"{out[key]['drift_early']:.3e}  early omega "
              f"{out[key]['clock_early']['omega_fit']:.6f}")
    with open(os.path.join(DATA, "m7_5_smoke.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote data/m7_5_smoke.json")


def _band(c1):
    """Analytic transverse dispersion for the linearized vacuum:
    M(k) = [[k^2, -1], [-1, k^2 + 2 c1]]; w2 eigenvalues; tachyon band."""
    k = np.linspace(0.0, 2.0, 401)
    k2 = k ** 2
    tr_half = k2 + c1
    disc = np.sqrt(c1 ** 2 + 1.0)
    w2m = tr_half - disc
    w2p = tr_half + disc
    kstar2 = -c1 + disc                      # root of k^4 + 2 c1 k^2 - 1 = 0
    return {"k": k.tolist(), "w2_minus": w2m.tolist(), "w2_plus": w2p.tolist(),
            "kstar2": float(kstar2), "kstar": float(np.sqrt(kstar2)),
            "rate_max": float(np.sqrt(disc - c1)),
            "detM0": -1.0}


def mode_disp():
    """The tachyon window, both conventions + the harmonic-frame PSD threshold."""
    out = {}
    for name, c1 in (("repulsive", +LAMHALF), ("focusing", -LAMHALF)):
        b = _band(c1)
        out[name] = b
        print(f"{name}: det M(0) = -1 (unconditional)  band k^2 < {b['kstar2']:.4f} "
              f"(k* = {b['kstar']:.4f})  max rate {b['rate_max']:.4f} at k=0")
    # harmonic-frame quadratic form at k=0 (repulsive): PSD threshold in omega.
    # form matrix [[w^2/4, 1/4], [1/4, w^2/4 + c1/2]] -> marginal where det = 0
    ws = np.linspace(0.3, 1.5, 601)
    lam_min = []
    for w in ws:
        a = 0.25 * w * w
        Mq = np.array([[a, 0.25], [0.25, a + 0.5 * LAMHALF]])
        lam_min.append(float(np.linalg.eigvalsh(Mq)[0]))
    idx = int(np.argmin(np.abs(np.array(lam_min))))
    out["harmonic_threshold"] = {"omega": ws.tolist(), "lam_min": lam_min,
                                 "omega_star_grid": float(ws[idx]),
                                 "omega_star_analytic":
                                     float(np.sqrt(out["repulsive"]["kstar2"]))}
    print(f"harmonic frame PSD threshold: omega* = "
          f"{out['harmonic_threshold']['omega_star_analytic']:.4f} "
          f"(grid marginal at {ws[idx]:.4f}); the soliton's omega = 1.0 rides ABOVE")
    with open(os.path.join(DATA, "m7_5_disp.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote data/m7_5_disp.json")


def mode_main(N=64, L=16.0, n_periods=12):
    """Closed-box evolution of the winner: short-window clock + destruction time."""
    _ti_init()
    f, E_w = get_winner_state(N=N, L=L)
    eng = TaichiLeapfrog(N, L)
    eng.load(f)
    m0 = eng.measure()
    T = 2 * np.pi / OMEGA
    print(f"E_w = {E_w:.6f}  E_real(0) = {m0['E']:.6f} "
          f"(instantaneous, oscillates at 2w about the E_w average)")
    tr = evolve(eng, n_periods=n_periods, dt=0.2 * eng.h,
                tag="main closed-box", meas_every=2)
    t = np.array(tr["t"])
    E = np.array(tr["E"])
    A2 = np.array(tr["A2"])
    ck_early = clock_fit(tr, t_max=1.5 * T)
    ck_full = clock_fit(tr)
    pA = np.array(tr["pA"])
    pJ = np.array(tr["pJ"])
    clocks_fft = {
        "ov_c": clock_fft(t, np.array(tr["ov_c"]), t_max=3 * T),
        "probe_Az": clock_fft(t, pA[:, 2], t_max=3 * T),
        "probe_Ax": clock_fft(t, pA[:, 0], t_max=3 * T),
        "probe_Jz": clock_fft(t, pJ[:, 2], t_max=3 * T),
    }
    for k, v in clocks_fft.items():
        print(f"  clock_fft[{k}]: omega_peak = {v.get('omega_peak')} "
              f"(dev {v.get('rel_dev')})")
    # destruction diagnostics
    i_e = np.argmax(np.abs(E - E[0]) > 0.01 * abs(E[0])) if np.any(
        np.abs(E - E[0]) > 0.01 * abs(E[0])) else -1
    i_a = np.argmax(A2 > 2 * A2[0]) if np.any(A2 > 2 * A2[0]) else -1
    out = {"N": N, "L": L, "n_periods": n_periods, "E_w": E_w,
           "E_real_t0": m0["E"], "dt": tr["dt"],
           "clock_early": ck_early, "clock_full": ck_full,
           "clocks_fft": clocks_fft,
           "pA": tr["pA"], "pJ": tr["pJ"],
           "t_energy_1pct": float(t[i_e]) if i_e >= 0 else None,
           "t_A2_double": float(t[i_a]) if i_a >= 0 else None,
           "drift_early": float((E[t <= 1.5 * T].max() - E[t <= 1.5 * T].min())
                                / abs(E[0])),
           "traces": {k: tr[k] for k in ("t", "E", "E_kin", "A2", "J2",
                                         "H_A_inst", "ov_c", "ov_s")},
           "heavy": tr["heavy"]}
    with open(os.path.join(DATA, "m7_5_evolve.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"MAIN: early clock omega {ck_early['omega_fit']:.6f} "
          f"(dev {ck_early['rel_dev']:+.2e}); early drift {out['drift_early']:.2e}; "
          f"A2 doubles at t = {out['t_A2_double']} "
          f"({(out['t_A2_double'] or 0) / T:.2f} T)")
    print("wrote data/m7_5_evolve.json")


def mode_vacuum(N=48, L=16.0, t_end=25.0):
    """The beta* probe, correctly posed: the linearized vacuum is tachyonic, so
    the probe measures (a) mode-resolved growth rates vs the analytic band and
    (b) amplitude-INdependence of the rate (linear instability = no threshold)."""
    _ti_init()
    eng = TaichiLeapfrog(N, L)
    h = L / N
    rng = np.random.default_rng(75)
    from scipy.ndimage import gaussian_filter
    noise = {}
    for name in ("avc", "jvc"):
        v = rng.standard_normal((N, N, N, 3))
        for i in range(3):
            v[..., i] = gaussian_filter(v[..., i], sigma=1.5)
        noise[name] = v / np.sqrt(np.mean(v ** 2))
    amps = [1e-6, 1e-4, 1e-2]
    out = {"N": N, "L": L, "t_end": t_end, "amps": amps, "runs": []}
    kfreq = 2 * np.pi * np.fft.fftfreq(N, d=h)
    KX, KY, KZ = np.meshgrid(kfreq, kfreq, kfreq, indexing="ij")
    kmag = np.sqrt(KX ** 2 + KY ** 2 + KZ ** 2)
    bins = np.arange(0.15, 1.35, 0.15)
    for eps in amps:
        g = HarmonicFields(N, L)
        g.avc = eps * noise["avc"]
        g.jvc = eps * noise["jvc"]
        apply_vacuum_shell(g)
        eng.load(g, omega=0.0)          # static noise, zero velocities
        dt = 0.2 * h
        n_steps = int(t_end / dt)
        ts, a2s, shells = [], [], []
        for n in range(n_steps + 1):
            if n % 15 == 0:
                m = eng.measure()
                ts.append(n * dt)
                a2s.append(m["A2"])
                A = eng.A.to_numpy()
                P = sum(np.abs(np.fft.fftn(A[..., i])) ** 2 for i in range(3))
                sh = [float(np.mean(P[(kmag >= b - 0.075) & (kmag < b + 0.075)]))
                      for b in bins]
                shells.append(sh)
                if not np.isfinite(m["A2"]):
                    break
            if n < n_steps:
                eng.step(dt)
        ts, a2s = np.array(ts), np.array(a2s)
        shells = np.array(shells)
        # global amplitude growth rate in the clean linear window
        ok = np.isfinite(a2s) & (a2s > 10 * a2s[0]) & (a2s < 1e10 * a2s[0])
        rate_glob = None
        if ok.sum() > 3:
            sl = np.polyfit(ts[ok], np.log(a2s[ok]), 1)[0]
            rate_glob = float(sl / 2)          # amplitude rate = power rate / 2
        # per-shell rates over the same window
        rates_k = []
        for ib in range(len(bins)):
            p = shells[:, ib]
            okk = ok & np.isfinite(p) & (p > 0)
            rates_k.append(float(np.polyfit(ts[okk], np.log(p[okk]), 1)[0] / 2)
                           if okk.sum() > 3 else None)
        out["runs"].append({"eps": eps, "rate_glob": rate_glob,
                            "bins": bins.tolist(), "rates_k": rates_k,
                            "t": ts.tolist(), "A2": a2s.tolist()})
        print(f"  eps={eps:.0e}  global amplitude rate = {rate_glob}")
    # analytic reference on the same bins
    disc = np.sqrt(C1 ** 2 + 1.0)
    w2m = bins ** 2 + C1 - disc
    out["analytic"] = {"bins": bins.tolist(),
                       "rate": [float(np.sqrt(-x)) if x < 0 else 0.0 for x in w2m],
                       "rate_max": float(np.sqrt(disc - C1)),
                       "kstar": float(np.sqrt(-C1 + disc))}
    with open(os.path.join(DATA, "m7_5_vacuum.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"analytic: max rate {out['analytic']['rate_max']:.4f} at k=0, "
          f"band edge k* = {out['analytic']['kstar']:.4f}")
    print("wrote data/m7_5_vacuum.json")


def mode_scan(N=64, L=16.0, n_iter=800,
              omegas=(0.70, 0.75, 0.79, 0.85, 0.90, 1.0, 1.1, 1.2)):
    """E_omega(omega) at fixed H_A + the envelope gate dE*/domega = Q_can.
    The sub-omega* points (0.70, 0.75 < 0.786) test the PREDICTION that the
    harmonic quadratic form goes indefinite below omega* = k* = 0.786."""
    _ti_init()
    eng = TaichiBlend(N, L)
    rows = []
    for w in omegas:
        eng.set_params(w, KAPPA, C1, C2)
        f0 = apply_vacuum_shell(build_seed("blend", N, L))
        fR, info = relax_state(eng, f0, CONV, n_iter=n_iter, tag=f"scan w={w}")
        h3 = fR.h ** 3
        quad2 = float(np.sum(dot(fR.avc, fR.avc) + dot(fR.avs, fR.avs)
                             + dot(fR.jvc, fR.jvc) + dot(fR.jvs, fR.jvs)) * h3)
        rows.append({"omega": w, "E": info["E_final"],
                     "gnorm": info["gnorm_final"], "status": info["status"],
                     "maxf": float(np.max(np.abs(fR.pack()))),
                     "H_A": helicity_A(fR), "Q_J": qnorm_J(fR),
                     "Q_can": 0.5 * w * quad2, "quad2": quad2})
        print(f"  w={w:.2f}  E={rows[-1]['E']:+.5f}  Q_can={rows[-1]['Q_can']:.5f}  "
              f"|g|={rows[-1]['gnorm']:.2e}  maxf={rows[-1]['maxf']:.3f}  "
              f"status={info['status']}")
    with open(os.path.join(DATA, "m7_5_scan.json"), "w") as fh:
        json.dump({"N": N, "L": L, "n_iter": n_iter, "rows": rows}, fh, indent=1)
    print("wrote data/m7_5_scan.json")


# =============================================================================
# plots
# =============================================================================


def mode_residual(N=64, L=16.0, n_quad=16):
    """Numpy-only checks on the cached winner doublet:
    (a) <E_real(t)> over one period == E_w (validates the whole translation);
    (b) the omega-projected real-time EOM residual, decomposed on the basis
        {avc, 2 curl avc}: expect res_Ac = alpha avc + beta 2curl(avc) with
        alpha ~ -2 w^2 (the fixed-H_A minimizer is NOT a fixed-Q_can orbit;
        M7.3's objective analysis) + tiny orthogonal rest;
    (c) the Rayleigh frequency of the state, w_R^2 = <a, (curlcurl a + j)>/<a,a>:
        the frequency the state's own linear dynamics prefers, to compare with
        the FFT-measured real-time oscillation;
    (d) the 3-omega leakage of the J equation (the RWA truncation error)."""
    z = np.load(STATE_NPZ)
    assert int(z["N"]) == N, f"cache is N={int(z['N'])}, want {N}: run main first"
    avc, avs = z["avc"], z["avs"]
    jvc, jvs = z["jvc"], z["jvs"]
    E_w = float(z["E"])
    h, w = L / N, OMEGA

    def cc(F):
        return curl_np(curl_np(F, h), h)

    out = {"E_w": E_w}
    # (a) period-average of the real-time energy on the doublet
    Es = []
    for q in range(n_quad):
        tq = 2 * np.pi / w * q / n_quad
        c, s_ = np.cos(w * tq), np.sin(w * tq)
        A = avc * c + avs * s_
        J = jvc * c + jvs * s_
        Ad = w * (-avc * s_ + avs * c)
        Jd = w * (-jvc * s_ + jvs * c)
        cA, cJ = curl_np(A, h), curl_np(J, h)
        s = dot(J, J)
        Es.append(float(np.sum(0.5 * dot(Ad, Ad) + 0.5 * dot(Jd, Jd)
                               + 0.5 * dot(cA, cA) + 0.5 * dot(cJ, cJ)
                               + dot(A, J) + C1 * s + C2 * s * s) * h ** 3))
    out["E_real_avg"] = float(np.mean(Es))
    out["E_avg_gate_dev"] = float(out["E_real_avg"] / E_w - 1.0)
    out["E_real_min"], out["E_real_max"] = float(np.min(Es)), float(np.max(Es))
    print(f"(a) <E_real> = {out['E_real_avg']:.6f} vs E_w = {E_w:.6f} "
          f"(dev {out['E_avg_gate_dev']:+.2e}); range on the doublet "
          f"[{out['E_real_min']:+.3f}, {out['E_real_max']:+.3f}]")

    # (b) residual decomposition (A-sector, cos component; linear equation)
    res = -w * w * avc + cc(avc) + jvc
    b1 = avc
    b2 = 2.0 * curl_np(avc, h)

    def ip(X, Y):
        return float(np.sum(dot(X, Y)) * h ** 3)

    G = np.array([[ip(b1, b1), ip(b1, b2)], [ip(b2, b1), ip(b2, b2)]])
    rhs = np.array([ip(b1, res), ip(b2, res)])
    alpha, beta = np.linalg.solve(G, rhs)
    rest = res - alpha * b1 - beta * b2
    out["residual"] = {
        "alpha": float(alpha), "beta": float(beta),
        "alpha_expected": -2 * w * w,
        "rel_norm_res": float(np.sqrt(ip(res, res) / ip(b1, b1))) / (w * w),
        "rel_norm_rest": float(np.sqrt(ip(rest, rest) / ip(b1, b1))) / (w * w)}
    print(f"(b) res_Ac = alpha avc + beta 2curl(avc) + rest: "
          f"alpha = {alpha:+.4f} (expect ~ {-2 * w * w:+.1f}), beta = {beta:+.4f}; "
          f"|res|/(w^2|a|) = {out['residual']['rel_norm_res']:.3f}, "
          f"orthogonal rest = {out['residual']['rel_norm_rest']:.3f}")

    # (c) Rayleigh frequencies (per sector; note the M7.4 winner is a
    # STANDING doublet: avs = jvs = 0, the cos-only subspace is invariant)
    out["sector_norms"] = {k: float(np.sqrt(np.sum(v ** 2)) * h ** 1.5)
                           for k, v in (("avc", avc), ("avs", avs),
                                        ("jvc", jvc), ("jvs", jvs))}
    ray = {}
    for name, a, jsrc in (("Ac", avc, jvc), ("As", avs, jvs)):
        if ip(a, a) < 1e-20:
            ray[name] = {"w2": None, "w": None, "note": "zero sector"}
            continue
        w2 = ip(a, cc(a) + jsrc) / ip(a, a)
        ray[name] = {"w2": float(w2),
                     "w": float(np.sqrt(w2)) if w2 > 0 else None}
    for name, j, asrc in (("Jc", jvc, avc), ("Js", jvs, avs)):
        if ip(j, j) < 1e-20:
            ray[name] = {"w2": None, "w": None, "note": "zero sector"}
            continue
        s = dot(j, j)
        w2 = ip(j, cc(j) + asrc + 2 * (C1 + 2 * C2 * s[..., None]) * j) / ip(j, j)
        ray[name] = {"w2": float(w2),
                     "w": float(np.sqrt(w2)) if w2 > 0 else None}
    out["rayleigh"] = ray
    print("(c) sector norms: " + "  ".join(
        f"{k}={v:.4f}" for k, v in out["sector_norms"].items()))
    print("    Rayleigh: " + "  ".join(
        f"{k}: w2 = {v['w2']:+.4f}" if v["w2"] is not None else f"{k}: zero"
        for k, v in ray.items()))

    # (d) 3-omega leakage of the J equation
    resJ_w_c = np.zeros_like(jvc)
    resJ_3w_c = np.zeros_like(jvc)
    resJ_3w_s = np.zeros_like(jvc)
    for q in range(n_quad):
        tq = 2 * np.pi / w * q / n_quad
        c, s_ = np.cos(w * tq), np.sin(w * tq)
        J = jvc * c + jvs * s_
        A = avc * c + avs * s_
        rhsJ = -cc(J) - A - 2 * (C1 + 2 * C2 * dot(J, J)[..., None]) * J
        # LHS Jdotdot on the doublet = -w^2 J(t); residual = LHS - RHS
        rJ = -w * w * J - rhsJ
        resJ_w_c += rJ * (2.0 / n_quad) * c
        resJ_3w_c += rJ * (2.0 / n_quad) * np.cos(3 * w * tq)
        resJ_3w_s += rJ * (2.0 / n_quad) * np.sin(3 * w * tq)
    nrm = np.sqrt(ip(jvc, jvc))
    out["J_leakage"] = {
        "res_w_rel": float(np.sqrt(ip(resJ_w_c, resJ_w_c))) / (w * w * nrm),
        "res_3w_rel": float(np.sqrt(ip(resJ_3w_c, resJ_3w_c)
                                    + ip(resJ_3w_s, resJ_3w_s))) / (w * w * nrm)}
    print(f"(d) J-equation residual: omega-component {out['J_leakage']['res_w_rel']:.3f}, "
          f"3-omega leakage {out['J_leakage']['res_3w_rel']:.3f} "
          f"(relative to w^2 |j|)")
    with open(os.path.join(DATA, "m7_5_residual.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote data/m7_5_residual.json")


def mode_analyze():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(PLOTS, exist_ok=True)
    T = 2 * np.pi / OMEGA

    # --- fig 1: the clock + the destruction (main run) ---
    with open(os.path.join(DATA, "m7_5_evolve.json")) as fh:
        ev = json.load(fh)
    t = np.array(ev["traces"]["t"])
    E = np.array(ev["traces"]["E"])
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    ax = axes[0, 0]
    early = t <= 1.5 * T
    ax.plot(t[early] / T, (E[early] - E[0]) / abs(E[0]))
    ax.set_title(f"energy conservation, pre-tachyon window "
                 f"(drift {ev['drift_early']:.1e})")
    ax.set_xlabel("t / T")
    ax.set_ylabel("(E - E0)/|E0|")
    ax = axes[0, 1]
    nshow = int(np.searchsorted(t, 3 * T))
    oc = np.array(ev["traces"]["ov_c"][:nshow])
    pA = np.array(ev["pA"][:nshow])
    ax.plot(t[:nshow] / T, oc / np.max(np.abs(oc)), label="<A, a_c> (norm)")
    ax.plot(t[:nshow] / T, pA[:, 2] / np.max(np.abs(pA[:, 2])),
            label="core probe A_z (norm)")
    wpk = ev["clocks_fft"]["probe_Az"]["omega_peak"]
    ax.set_title(f"released standing state: FFT peak omega = {wpk:.3f} "
                 f"(input 1.0; tachyon-contaminated)")
    ax.set_xlabel("t / T")
    ax.legend()
    ax = axes[1, 0]
    ax.semilogy(t / T, np.array(ev["traces"]["A2"]), label="|A|^2")
    ax.semilogy(t / T, np.maximum(np.array(ev["traces"]["J2"]), 1e-30),
                label="|J|^2")
    if ev["t_A2_double"]:
        ax.axvline(ev["t_A2_double"] / T, color="r", ls="--", lw=0.8,
                   label=f"A2 doubles ({ev['t_A2_double'] / T:.1f} T)")
    ax.set_title("the tachyon takes over: field norms")
    ax.set_xlabel("t / T")
    ax.legend()
    ax = axes[1, 1]
    ax.plot(t / T, (E - E[0]) / abs(E[0]))
    ax.set_yscale("symlog", linthresh=1e-3)
    ax.set_title("full-run energy error (integrator loses the runaway)")
    ax.set_xlabel("t / T")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m7_5_clock_traces.png"), dpi=130)
    print("wrote plots/m7_5_clock_traces.png")

    # --- fig 2: dispersion + vacuum rates + omega scan ---
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    d = os.path.join(DATA, "m7_5_disp.json")
    if os.path.exists(d):
        with open(d) as fh:
            di = json.load(fh)
        ax = axes[0]
        for name, c in (("repulsive", "C0"), ("focusing", "C1")):
            b = di[name]
            k = np.array(b["k"])
            ax.plot(k, b["w2_minus"], c + "-",
                    label=f"{name}: w2- (k* = {b['kstar']:.3f})")
            ax.plot(k, b["w2_plus"], c + ":", alpha=0.6)
        ax.axhline(0, color="k", lw=0.6)
        ax.axhline(OMEGA ** 2, color="g", lw=0.8, ls="--",
                   label="soliton omega^2 = 1")
        ax.set_title("linearized vacuum bands: det M(0) = -1, both conventions")
        ax.set_xlabel("k")
        ax.set_ylabel("omega^2(k)")
        ax.set_ylim(-2, 4)
        ax.legend(fontsize=7)
    v = os.path.join(DATA, "m7_5_vacuum.json")
    if os.path.exists(v):
        with open(v) as fh:
            va = json.load(fh)
        ax = axes[1]
        an = va["analytic"]
        ax.plot(an["bins"], an["rate"], "k-", label="analytic sqrt(-w2-(k))")
        for r in va["runs"]:
            if r["rates_k"]:
                ax.plot(r["bins"], [x if x is not None else np.nan
                                    for x in r["rates_k"]], "o--",
                        label=f"measured, eps = {r['eps']:.0e}")
        ax.axvline(an["kstar"], color="k", ls=":", lw=0.8,
                   label=f"band edge k* = {an['kstar']:.3f}")
        ax.set_title("vacuum growth rates: linear tachyon, NO amplitude threshold")
        ax.set_xlabel("k")
        ax.set_ylabel("amplitude growth rate")
        ax.legend(fontsize=7)
    s = os.path.join(DATA, "m7_5_scan.json")
    if os.path.exists(s):
        with open(s) as fh:
            sc = json.load(fh)
        rows = sc["rows"]
        ws = np.array([r["omega"] for r in rows])
        Es = np.array([r["E"] for r in rows])
        ok = np.array([("BLOW" not in r["status"]) and r["gnorm"] < 1e-5
                       and r["E"] > 0 for r in rows])
        ax = axes[2]
        ax.plot(ws[ok], Es[ok], "o-", color="C0", label="E* (converged)")
        if np.any(~ok):
            ax.plot(ws[~ok], np.clip(Es[~ok], -50, 50), "x", color="r",
                    ms=10, label="failed (runaway / blow-up)")
        ax.axvline(np.sqrt((np.sqrt(5) - 1) / 2), color="k", ls="--", lw=0.8,
                   label="predicted omega* = 0.786")
        ax.set_title("fixed-H_A scan: solitons only above omega*")
        ax.set_xlabel("omega")
        ax.set_ylabel("E*")
        ax.legend(fontsize=7)
        # the envelope gate, printed
        if ok.sum() >= 3:
            wso, Eso = ws[ok], Es[ok]
            Qso = np.array([r["Q_can"] for r in rows])[ok]
            dE = np.gradient(Eso, wso)
            print("envelope gate dE*/dw vs Q_can:")
            for i in range(len(wso)):
                print(f"  w={wso[i]:.2f}  dE/dw={dE[i]:+.4f}  Q_can={Qso[i]:.4f}")
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m7_5_tachyon_scan.png"), dpi=130)
    print("wrote plots/m7_5_tachyon_scan.png")


# =============================================================================


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["smoke", "disp", "vacuum", "main",
                                     "scan", "residual", "analyze"])
    args = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    {"smoke": mode_smoke, "disp": mode_disp, "vacuum": mode_vacuum,
     "main": mode_main, "scan": mode_scan, "residual": mode_residual,
     "analyze": mode_analyze}[args.mode]()


if __name__ == "__main__":
    main()
