"""M7.4 - the charged soliton (approximately-Beltrami) + its Coulomb field.

Task doc: research/tasks/m7_4_charged_soliton.md. Modes:

  python m7_4_linked_vortex.py smoke     N=48 single-seed sanity (ck x both f)
  python m7_4_linked_vortex.py run       the full seed x f-convention matrix (N=64)
  python m7_4_linked_vortex.py winner    re-relax the best state at N=96 + full plots

Design carried in from M7.3 (tasks/m7_3_ouroboros_3d.md FINDINGS):

  * Frame: fixed-omega harmonic doublet; E_w = quad - kappa <A.J> + f_avg with
    f_avg = c1 s0 + c2 (s0^2 + (s1^2+s2^2)/2). kappa = -1 kept (pure J -> -J
    relabeling; the M6-verbatim pin).
  * The f-convention fork IS the experiment (Q6):
      "focusing"  c1 = -lam/2, c2 = -4g/3   M6-verbatim; unbounded below at fixed
                                            H_A alone -> constrain Q_J too
      "repulsive" c1 = +lam/2, c2 = +g/4    the written 0d_canonical form; J-sector
                                            self-bounded -> fixed H_A alone
  * The coupling is bilinear: J = 0 is never stationary at A != 0, so the coupling
    always switches charge on; whether it SURVIVES as a finite-size minimum is the
    experiment.
  * Constraints are sector-separable and exactly restorable: H_A by A-rescale,
    Q_J (J-norm) by J-rescale; tangent projection via Gram-Schmidt on both grads.
  * Vacuum-fixed BCs (Dirichlet-0 shell); the box regulates the massless-A tail
    (a MINIMIZER suppresses radiation content, unlike the EOM).
  * Q_div: volume integral of div E_A within radius r, cos/sin pair, RMS-combined
    (the Fleury convention); near-zone caveat stated (omega = 1 ~ soliton scale).

Headless; matplotlib PNG only. Data: research/data/m7_4_*.json.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from m7_1_harmonic_lattice import (  # noqa: E402
    COMP_NAMES, COMP_VEC, HarmonicFields, curl_np, d_axis, div_np, dot,
    fire_minimize, grid_xyz, m6_profile, seed_bateman_hopfion,
    seed_ck_spheromak, seed_fleury_torus,
)

DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")

OMEGA, LAM, G = 1.0, 1.0, 1.0
KAPPA = -1.0
F_CONV = {
    "focusing": {"c1": -LAM / 2.0, "c2": -4.0 * G / 3.0, "constrain_QJ": True},
    "repulsive": {"c1": +LAM / 2.0, "c2": +G / 4.0, "constrain_QJ": False},
}
SHELL = 3          # vacuum Dirichlet boundary shell (cells)


# =============================================================================
# energy engine (Taichi, cubic N, parametrized kappa/c1/c2)
# =============================================================================


class TaichiBlend:
    def __init__(self, N, L):
        import taichi as ti
        self.ti = ti
        self.N, self.L, self.h = N, L, L / N
        self.f = {}
        for name in COMP_NAMES:
            if COMP_VEC[name]:
                self.f[name] = ti.Vector.field(3, dtype=ti.f64, shape=(N, N, N),
                                               needs_grad=True)
            else:
                self.f[name] = ti.field(dtype=ti.f64, shape=(N, N, N),
                                        needs_grad=True)
        self.loss = ti.field(dtype=ti.f64, shape=(), needs_grad=True)
        self.omega = ti.field(dtype=ti.f64, shape=())
        self.kappa = ti.field(dtype=ti.f64, shape=())
        self.c1 = ti.field(dtype=ti.f64, shape=())
        self.c2 = ti.field(dtype=ti.f64, shape=())
        self._build()

    def set_params(self, omega, kappa, c1, c2):
        self.omega[None], self.kappa[None] = omega, kappa
        self.c1[None], self.c2[None] = c1, c2

    def set_fields(self, hf: HarmonicFields):
        for name in COMP_NAMES:
            self.f[name].from_numpy(np.ascontiguousarray(getattr(hf, name)))

    def _build(self):
        ti = self.ti
        N, h = self.N, self.h
        a0c, a0s = self.f["a0c"], self.f["a0s"]
        avc, avs = self.f["avc"], self.f["avs"]
        j0c, j0s = self.f["j0c"], self.f["j0s"]
        jvc, jvs = self.f["jvc"], self.f["jvs"]
        loss, omega, kappa, c1, c2 = self.loss, self.omega, self.kappa, self.c1, self.c2

        @ti.func
        def grads(F, i, j, k):
            ip, im = (i + 1) % N, (i - 1 + N) % N
            jp, jm = (j + 1) % N, (j - 1 + N) % N
            kp, km = (k + 1) % N, (k - 1 + N) % N
            return ti.Vector([(F[ip, j, k] - F[im, j, k]) / (2 * h),
                              (F[i, jp, k] - F[i, jm, k]) / (2 * h),
                              (F[i, j, kp] - F[i, j, km]) / (2 * h)])

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
        def e_kernel():
            for i, j, k in ti.ndrange(N, N, N):
                w = omega[None]
                EAc = -grads(a0c, i, j, k) - w * avs[i, j, k]
                EAs = -grads(a0s, i, j, k) + w * avc[i, j, k]
                EJc = -grads(j0c, i, j, k) - w * jvs[i, j, k]
                EJs = -grads(j0s, i, j, k) + w * jvc[i, j, k]
                BAc = curlv(avc, i, j, k)
                BAs = curlv(avs, i, j, k)
                BJc = curlv(jvc, i, j, k)
                BJs = curlv(jvs, i, j, k)
                quad = 0.25 * (EAc.dot(EAc) + EAs.dot(EAs) + EJc.dot(EJc)
                               + EJs.dot(EJs) + BAc.dot(BAc) + BAs.dot(BAs)
                               + BJc.dot(BJc) + BJs.dot(BJs))
                AdotJ = 0.5 * (-(a0c[i, j, k] * j0c[i, j, k])
                               - (a0s[i, j, k] * j0s[i, j, k])
                               + avc[i, j, k].dot(jvc[i, j, k])
                               + avs[i, j, k].dot(jvs[i, j, k]))
                s_cc = -(j0c[i, j, k] ** 2) + jvc[i, j, k].dot(jvc[i, j, k])
                s_ss = -(j0s[i, j, k] ** 2) + jvs[i, j, k].dot(jvs[i, j, k])
                s_cs = -(j0c[i, j, k] * j0s[i, j, k]) + jvc[i, j, k].dot(jvs[i, j, k])
                s0 = 0.5 * (s_cc + s_ss)
                s1 = 0.5 * (s_cc - s_ss)
                s2 = s_cs
                favg = c1[None] * s0 + c2[None] * (s0 * s0 + 0.5 * (s1 * s1 + s2 * s2))
                loss[None] += (quad - kappa[None] * AdotJ + favg) * h ** 3

        self._e_kernel = e_kernel

    def energy(self, hf=None, grad=False):
        ti = self.ti
        if hf is not None:
            self.set_fields(hf)
        self.loss[None] = 0.0
        if grad:
            with ti.ad.Tape(loss=self.loss):
                self._e_kernel()
            g = {name: self.f[name].grad.to_numpy() for name in COMP_NAMES}
            return float(self.loss[None]), g
        self._e_kernel()
        return float(self.loss[None]), None


# =============================================================================
# constraints (numpy, analytic gradients, sector-separable exact restores)
# =============================================================================

A_SLOTS = ("avc", "avs")
J_SLOTS = ("j0c", "j0s", "jvc", "jvs")
SCALAR_SLOTS = ("a0c", "a0s", "j0c", "j0s")
# The scalar (timelike) components are FROZEN at zero in this task: the smoke run
# exposed a null-J runaway (s = -j0^2 + |jv|^2 = 0 directions are quartic-flat and
# gain unbounded bilinear a0*j0 coupling energy), i.e. the naive averaged Hamiltonian
# is unstable in the scalar sector. Since on-shell Gauss slaves the divergence charge
# to J0 (div E_A = -mJ^2 J0), freezing scalars means the charge experiment here reads:
# does SEEDED geometric divergence (Fleury-style, div av != 0) survive relaxation?
# The constraint-level scalar treatment is documented as a finding and deferred.


def helicity_A(f: HarmonicFields):
    h = f.h
    return 0.5 * float(np.sum(dot(f.avc, curl_np(f.avc, h))
                              + dot(f.avs, curl_np(f.avs, h))) * h ** 3)


def helicity_A_grad(f: HarmonicFields):
    """dH_A/d(component) arrays (zero except avc/avs)."""
    h = f.h
    g = {name: np.zeros_like(getattr(f, name)) for name in COMP_NAMES}
    g["avc"] = curl_np(f.avc, h) * h ** 3      # 0.5 * 2 * curl
    g["avs"] = curl_np(f.avs, h) * h ** 3
    return g


def qnorm_J(f: HarmonicFields):
    h = f.h
    return float(np.sum(f.j0c ** 2 + f.j0s ** 2
                        + dot(f.jvc, f.jvc) + dot(f.jvs, f.jvs)) * h ** 3)


def qnorm_J_grad(f: HarmonicFields):
    h = f.h
    g = {name: np.zeros_like(getattr(f, name)) for name in COMP_NAMES}
    for name in J_SLOTS:
        g[name] = 2.0 * getattr(f, name) * h ** 3
    return g


def pack_dict(gd):
    return np.concatenate([gd[n].ravel() for n in COMP_NAMES])


def slot_mask(f: HarmonicFields, names):
    return np.concatenate([
        (np.ones if n in names else np.zeros)(getattr(f, n).size, dtype=bool)
        for n in COMP_NAMES])


def interior_mask_flat(f: HarmonicFields, shell=SHELL):
    N = f.N
    m = np.zeros((N, N, N), dtype=bool)
    m[shell:N - shell, shell:N - shell, shell:N - shell] = True
    return np.concatenate([
        (np.broadcast_to(m[..., None], getattr(f, n).shape)
         if COMP_VEC[n] else m).ravel()
        for n in COMP_NAMES])


# =============================================================================
# seeds
# =============================================================================


def inv_curl_fft(B, L):
    """Coulomb-gauge A with curl A = B (periodic, div-free B)."""
    N = B.shape[0]
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=L / N)
    KX, KY, KZ = np.meshgrid(k1, k1, k1, indexing="ij")
    K2 = KX ** 2 + KY ** 2 + KZ ** 2
    K2[0, 0, 0] = 1.0
    Bh = [np.fft.fftn(B[..., i]) for i in range(3)]
    Ah = [1j * (KY * Bh[2] - KZ * Bh[1]) / K2,
          1j * (KZ * Bh[0] - KX * Bh[2]) / K2,
          1j * (KX * Bh[1] - KY * Bh[0]) / K2]
    for a in Ah:
        a[0, 0, 0] = 0.0
    return np.stack([np.real(np.fft.ifftn(a)) for a in Ah], axis=-1)


def _normalize(V, amp=0.3):
    m = float(np.max(np.linalg.norm(V, axis=-1)))
    return V * (amp / m) if m > 0 else V


def _ring_frame(N, L, R0):
    """Distance d from the ring of radius R0 in the z=0 plane + unit vectors:
    phi_hat (toroidal) and theta_hat (poloidal, around the tube)."""
    X, Y, Z = grid_xyz(N, L)
    rho = np.sqrt(X * X + Y * Y)
    rho_safe = np.maximum(rho, 1e-12)
    d = np.sqrt((rho - R0) ** 2 + Z * Z)
    d_safe = np.maximum(d, 1e-12)
    phix, phiy = -Y / rho_safe, X / rho_safe
    phih = np.stack([phix, phiy, np.zeros_like(X)], axis=-1)
    # theta_hat = -(z/d) rho_hat + ((rho-R0)/d) z_hat
    rhx, rhy = X / rho_safe, Y / rho_safe
    th = np.stack([-(Z / d_safe) * rhx, -(Z / d_safe) * rhy,
                   (rho - R0) / d_safe], axis=-1)
    return d, phih, th


def build_seed(name, N, L, j_prime=-0.1):
    """Returns HarmonicFields. J primed anti-parallel (kappa = -1 basin)."""
    f = HarmonicFields(N, L)
    if name == "ck":
        B, meta = seed_ck_spheromak(N, L, a=0.30 * L)
        A = _normalize(B / meta["lam"])
        f.avc = A
    elif name == "hopfion":
        s = 3.0        # stretch the unit-scale hopfion to lattice-resolvable size
        Nn = N
        _, Bh = seed_bateman_hopfion(Nn, L / s)
        A = _normalize(inv_curl_fft(Bh, L))    # curl on the TRUE box scale
        f.avc = A
    elif name == "m6taper":
        r1d, a1d, b1d, _ = m6_profile(r_max=12.0, n_grid=1200)
        d, phih, _ = _ring_frame(N, L, R0=0.25 * L)
        a3 = np.interp(d.ravel(), r1d, a1d, right=0.0).reshape(d.shape)
        b3 = np.interp(d.ravel(), r1d, b1d, right=0.0).reshape(d.shape)
        tap = np.exp(-(d / (0.22 * L)) ** 2)
        f.avc = _normalize((a3 * tap)[..., None] * phih)
        f.jvc = ((b3 * tap)[..., None] * phih)
        f.jvc *= 0.3 / max(float(np.max(np.abs(a3 * tap))), 1e-12)
        return f       # J already set by the M6 profile itself
    elif name == "blend":
        # the M6 torus with a POLOIDAL A-twist: linked toroidal+poloidal flux
        # = nonzero helicity = the anti-collapse guard the pure M6 seed lacks
        r1d, a1d, b1d, _ = m6_profile(r_max=12.0, n_grid=1200)
        d, phih, th = _ring_frame(N, L, R0=0.25 * L)
        a3 = np.interp(d.ravel(), r1d, a1d, right=0.0).reshape(d.shape)
        b3 = np.interp(d.ravel(), r1d, b1d, right=0.0).reshape(d.shape)
        tap = np.exp(-(d / (0.22 * L)) ** 2)
        f.avc = _normalize((a3 * tap)[..., None] * (phih + th))
        f.jvc = ((b3 * tap)[..., None] * phih)
        f.jvc *= 0.3 / max(float(np.max(np.abs(a3 * tap))), 1e-12)
        return f
    elif name == "fleury":
        d = seed_fleury_torus(N, L, R0=0.25 * L, r0=0.09 * L)
        f.avc = _normalize(d["Es"])
        f.avs = _normalize(-d["Ec"])
    else:
        raise ValueError(name)
    f.jvc = j_prime * f.avc
    f.jvs = j_prime * f.avs
    return f


def apply_vacuum_shell(f: HarmonicFields, shell=SHELL):
    N = f.N
    m = np.ones((N, N, N), dtype=bool)
    m[shell:N - shell, shell:N - shell, shell:N - shell] = False
    for name in COMP_NAMES:
        arr = getattr(f, name)
        arr[m] = 0.0
    return f


# =============================================================================
# relaxation (fixed H_A [+ fixed Q_J for the focusing convention])
# =============================================================================


def relax_state(eng: TaichiBlend, f0: HarmonicFields, conv, n_iter=1500,
                tag="", log_every=250):
    N, L, h = f0.N, f0.L, f0.h
    scratch = HarmonicFields(N, L)
    free = interior_mask_flat(f0) & ~slot_mask(f0, SCALAR_SLOTS)
    H0 = helicity_A(f0)
    QJ0 = qnorm_J(f0)
    constrain_QJ = conv["constrain_QJ"]
    a_mask = slot_mask(f0, A_SLOTS)
    j_mask = slot_mask(f0, J_SLOTS)

    def egf(x):
        scratch.unpack(x)
        E, g = eng.energy(scratch, grad=True)
        return E, pack_dict(g)

    def cons_grads(x):
        scratch.unpack(x)
        gs = [pack_dict(helicity_A_grad(scratch))]
        if constrain_QJ:
            gs.append(pack_dict(qnorm_J_grad(scratch)))
        return gs

    def proj(x, g):
        g = g.copy()
        g[~free] = 0.0
        basis = []
        for gc in cons_grads(x):
            gc[~free] = 0.0
            for b in basis:
                gc = gc - np.dot(gc, b) * b
            n = np.linalg.norm(gc)
            if n > 1e-300:
                basis.append(gc / n)
        for b in basis:
            g = g - np.dot(g, b) * b
        return g

    def corr(x):
        scratch.unpack(x)
        H = helicity_A(scratch)
        if H * H0 > 0:
            x = x.copy()
            x[a_mask] *= np.sqrt(H0 / H)
        if constrain_QJ:
            scratch.unpack(x)
            QJ = qnorm_J(scratch)
            if QJ > 1e-300:
                x = x.copy()
                x[j_mask] *= np.sqrt(QJ0 / QJ)
        return x

    x = corr(f0.pack())
    hist = []
    it_done = 0
    status = "ok"
    x_last = x.copy()
    while it_done < n_iter:
        x, E, gn, _ = fire_minimize(x, egf, project_fn=proj, correct_fn=corr,
                                    n_iter=min(250, n_iter - it_done),
                                    gtol=1e-9, log_every=0)
        it_done += 250
        if not np.all(np.isfinite(x)):
            status = f"BLOW-UP at iter {it_done}"
            x = x_last
            break
        x_last = x.copy()
        scratch.unpack(x)
        hist.append({"iter": it_done, "E": E, "gnorm": gn,
                     "H_A": helicity_A(scratch), "Q_J": qnorm_J(scratch),
                     "maxf": float(np.max(np.abs(x))),
                     "Q_rms": qdiv_rms_at(scratch, 0.3 * L)})
        if log_every:
            hh = hist[-1]
            print(f"  [{tag}] it={it_done:5d} E={hh['E']:+.5e} |g|={hh['gnorm']:.2e} "
                  f"H_A={hh['H_A']:+.4f} Q_J={hh['Q_J']:.4f} maxf={hh['maxf']:.3f} "
                  f"Q_rms={hh['Q_rms']:.4e}")
        if gn < 1e-9:
            break
    scratch.unpack(x)
    return scratch, {"history": hist, "status": status,
                     "E_final": hist[-1]["E"] if hist else None,
                     "gnorm_final": hist[-1]["gnorm"] if hist else None,
                     "H0": H0, "QJ0": QJ0}


# =============================================================================
# measurements (the Q3 battery + dilation + far field)
# =============================================================================


def charge_observables(f: HarmonicFields):
    """The two charge readings of the harmonic pair (rho_c, rho_s) = div(EAc, EAs):
    net monopole (Gauss flux; ZERO for m=1 rotating distributions) and the Fleury
    RMS-density volume integral (the arXiv:2510.22384 convention, M7.2)."""
    h = f.h
    EAc = -np.stack([d_axis(f.a0c, i, h) for i in range(3)], axis=-1) - OMEGA * f.avs
    EAs = -np.stack([d_axis(f.a0s, i, h) for i in range(3)], axis=-1) + OMEGA * f.avc
    rc, rs = div_np(EAc, h), div_np(EAs, h)
    return rc, rs, EAc, EAs


def qdiv_rms_at(f: HarmonicFields, rr, _cache={}):
    """Fleury RMS-density charge within radius rr: int sqrt((rc^2+rs^2)/2) dV."""
    h, N, L = f.h, f.N, f.L
    key = (N, L)
    if key not in _cache:
        X, Y, Z = grid_xyz(N, L)
        _cache[key] = np.sqrt(X * X + Y * Y + Z * Z)
    r = _cache[key]
    rc, rs, _, _ = charge_observables(f)
    m = r < rr
    return float(np.sum(np.sqrt(0.5 * (rc[m] ** 2 + rs[m] ** 2))) * h ** 3)


def measure_state(f: HarmonicFields, eng: TaichiBlend, conv):
    h, N, L = f.h, f.N, f.L
    X, Y, Z = grid_xyz(N, L)
    r = np.sqrt(X * X + Y * Y + Z * Z)

    dEc, dEs, EAc, EAs = charge_observables(f)

    radii = np.linspace(1.0, 0.47 * L, 24)
    Qc = [float(np.sum(dEc[r < rr]) * h ** 3) for rr in radii]      # net monopole
    Qs = [float(np.sum(dEs[r < rr]) * h ** 3) for rr in radii]
    Q_rms = np.sqrt((np.array(Qc) ** 2 + np.array(Qs) ** 2) / 2.0)
    rho_rms = np.sqrt(0.5 * (dEc ** 2 + dEs ** 2))
    Q_rho = [float(np.sum(rho_rms[r < rr]) * h ** 3) for rr in radii]  # Fleury conv.

    # helicities + cross-helicity
    H_A = helicity_A(f)
    H_J = 0.5 * float(np.sum(dot(f.jvc, curl_np(f.jvc, h))
                             + dot(f.jvs, curl_np(f.jvs, h))) * h ** 3)
    H_x = 0.5 * float(np.sum(dot(f.avc, curl_np(f.jvc, h))
                             + dot(f.avs, curl_np(f.jvs, h))) * h ** 3)

    # Beltrami alignment of B_A = curl avc (cos comp carries the structure)
    B = curl_np(f.avc, h)
    C = curl_np(B, h)
    num = float(np.sum(dot(B, C)))
    den = np.sqrt(float(np.sum(dot(B, B))) * float(np.sum(dot(C, C))))
    align = num / den if den > 0 else 0.0

    # energy localization radii (quad-only positive density)
    uq = _energy_density(f)
    csum = np.array([float(np.sum(uq[r < rr])) for rr in radii])
    csum = csum / max(csum[-1], 1e-300)
    r50 = float(np.interp(0.5, csum, radii))
    r90 = float(np.interp(0.9, csum, radii))

    # far-field envelope: shell-averaged |E_A| log-log slope on [r50*2, 0.45L]
    Emag = np.sqrt(dot(EAc, EAc) + dot(EAs, EAs))
    shell_r, shell_v = [], []
    for i in range(len(radii) - 1):
        m = (r >= radii[i]) & (r < radii[i + 1])
        if np.any(m):
            shell_r.append(0.5 * (radii[i] + radii[i + 1]))
            shell_v.append(float(np.mean(Emag[m])))
    shell_r, shell_v = np.array(shell_r), np.array(shell_v)
    band = (shell_r > min(2 * r50, 0.35 * L)) & (shell_r < 0.45 * L) & (shell_v > 0)
    slope = float(np.polyfit(np.log(shell_r[band]), np.log(shell_v[band]), 1)[0]) \
        if np.sum(band) >= 3 else np.nan

    return {"radii": radii.tolist(), "Q_rms_r": Q_rms.tolist(),
            "Qc_r": Qc, "Qs_r": Qs, "Q_rho_r": Q_rho,
            "Q_rho_r50x2": float(np.interp(min(2 * r50, radii[-1]), radii, Q_rho)),
            "Q_rms_r50x2": float(np.interp(min(2 * r50, radii[-1]), radii, Q_rms)),
            "H_A": H_A, "H_J": H_J, "H_cross": H_x,
            "beltrami_align": align, "r50": r50, "r90": r90,
            "farfield_slope": slope,
            "shell_r": shell_r.tolist(), "shell_E": shell_v.tolist()}


def _energy_density(f: HarmonicFields, conv=None):
    """quad-only positive density for localization radii (convention-free)."""
    h = f.h
    EAc = -np.stack([d_axis(f.a0c, i, h) for i in range(3)], axis=-1) - OMEGA * f.avs
    EAs = -np.stack([d_axis(f.a0s, i, h) for i in range(3)], axis=-1) + OMEGA * f.avc
    EJc = -np.stack([d_axis(f.j0c, i, h) for i in range(3)], axis=-1) - OMEGA * f.jvs
    EJs = -np.stack([d_axis(f.j0s, i, h) for i in range(3)], axis=-1) + OMEGA * f.jvc
    out = 0.25 * (dot(EAc, EAc) + dot(EAs, EAs) + dot(EJc, EJc) + dot(EJs, EJs))
    for V in (f.avc, f.avs, f.jvc, f.jvs):
        B = curl_np(V, h)
        out = out + 0.25 * dot(B, B)
    return out


def dilation_probe(f: HarmonicFields, eng: TaichiBlend, conv,
                   mus=(0.7, 0.8, 0.9, 1.0, 1.1, 1.25, 1.4)):
    """E(mu) along lattice rescalings x -> x/mu, constraints restored per point
    (the constrained Derrick curve) + the raw curve."""
    from scipy.ndimage import map_coordinates
    N, L = f.N, f.L
    c = (N - 1) / 2.0
    idx = np.arange(N, dtype=np.float64)
    H0 = helicity_A(f)
    QJ0 = qnorm_J(f)
    raw, restored = [], []
    for mu in mus:
        co = (idx - c) / mu + c
        CI, CJ, CK = np.meshgrid(co, co, co, indexing="ij")
        g = HarmonicFields(N, L)
        for name in COMP_NAMES:
            src = getattr(f, name)
            if COMP_VEC[name]:
                out = np.stack([map_coordinates(src[..., i], [CI, CJ, CK],
                                                order=3, mode="constant")
                                for i in range(3)], axis=-1)
            else:
                out = map_coordinates(src, [CI, CJ, CK], order=3, mode="constant")
            setattr(g, name, out)
        apply_vacuum_shell(g)
        E_raw, _ = eng.energy(g)
        raw.append(E_raw)
        H = helicity_A(g)
        if H * H0 > 0:
            for nm in A_SLOTS:
                setattr(g, nm, getattr(g, nm) * np.sqrt(H0 / H))
        if conv["constrain_QJ"]:
            QJ = qnorm_J(g)
            if QJ > 1e-300:
                for nm in J_SLOTS:
                    setattr(g, nm, getattr(g, nm) * np.sqrt(QJ0 / QJ))
        E_res, _ = eng.energy(g)
        restored.append(E_res)
    return {"mus": list(mus), "E_raw": raw, "E_restored": restored,
            "interior_min_restored": bool(
                np.argmin(restored) not in (0, len(mus) - 1)),
            "interior_min_raw": bool(np.argmin(raw) not in (0, len(mus) - 1))}


# =============================================================================
# drivers
# =============================================================================


def run_matrix(N=64, L=16.0, n_iter=1500, seeds=("ck", "hopfion", "m6taper",
                                                 "blend", "fleury"),
               convs=("repulsive", "focusing"), out_name="m7_4_states.json"):
    import taichi as ti
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)
    eng = TaichiBlend(N, L)
    results = {"N": N, "L": L, "n_iter": n_iter, "runs": {}}
    for sname in seeds:
        for cname in convs:
            conv = F_CONV[cname]
            tag = f"{sname}/{cname}"
            print("=" * 70)
            print(f"M7.4 RUN {tag}  (N={N}, L={L})")
            eng.set_params(OMEGA, KAPPA, conv["c1"], conv["c2"])
            f0 = apply_vacuum_shell(build_seed(sname, N, L))
            E0, _ = eng.energy(f0)
            H0 = helicity_A(f0)
            print(f"  seed: E={E0:+.5e}  H_A={H0:+.5f}  Q_J={qnorm_J(f0):.5f}")
            fR, info = relax_state(eng, f0, conv, n_iter=n_iter, tag=tag)
            meas = measure_state(fR, eng, conv)
            dil = dilation_probe(fR, eng, conv)
            results["runs"][tag] = {
                "seed": {"E": E0, "H_A": H0, "Q_J": qnorm_J(f0)},
                "relax": {k: v for k, v in info.items() if k != "history"},
                "history": info["history"],
                "measure": meas, "dilation": dil}
            print(f"  final: E={info['E_final']}  status={info['status']}  "
                  f"align={meas['beltrami_align']:+.3f}  r50={meas['r50']:.2f}  "
                  f"Q_rms(2r50)={meas['Q_rms_r50x2']:.4e}  "
                  f"ff_slope={meas['farfield_slope']:.2f}  "
                  f"dilation_min={dil['interior_min_restored']}")
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, out_name)
    with open(out, "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"wrote {out}")
    return results


def analyze(states_json="m7_4_states.json"):
    """Plots from the saved matrix results."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with open(os.path.join(DATA, states_json)) as fh:
        res = json.load(fh)
    runs = res["runs"]
    os.makedirs(PLOTS, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    for tag, r in runs.items():
        hh = r["history"]
        its = [x["iter"] for x in hh]
        ls = "-" if tag.endswith("repulsive") else "--"
        axes[0].plot(its, [x["E"] for x in hh], ls, label=tag)
        axes[1].semilogy(its, [max(x["Q_rms"], 1e-18) for x in hh], ls, label=tag)
        axes[2].semilogy(its, [max(x["Q_J"], 1e-18) for x in hh], ls, label=tag)
    axes[0].set_title("E_omega (fixed H_A [+Q_J])")
    axes[0].set_yscale("symlog")
    axes[1].set_title("RMS divergence charge Q_rho(0.3L) trace")
    axes[2].set_title("J-sector norm Q_J trace")
    for ax in axes:
        ax.set_xlabel("iteration")
        ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m7_4_traces.png"), dpi=130)
    print("wrote plots/m7_4_traces.png")

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    for tag, r in runs.items():
        d = r["dilation"]
        ls = "-" if tag.endswith("repulsive") else "--"
        E1 = d["E_restored"][d["mus"].index(1.0)]
        axes[0].plot(d["mus"], [e - E1 for e in d["E_restored"]], ls + "o",
                     label=f"{tag} ({'min' if d['interior_min_restored'] else 'NO min'})")
        m = r["measure"]
        axes[1].plot(m["radii"], m["Q_rho_r"], ls, label=tag)
        axes[2].loglog(m["shell_r"], m["shell_E"], ls,
                       label=f"{tag} (slope {m['farfield_slope']:.1f})")
    axes[0].set_title("constrained Derrick curve  E(mu) - E(1)")
    axes[0].set_xlabel("dilation mu")
    axes[0].set_yscale("symlog")
    axes[1].set_title("Fleury RMS charge Q_rho(< r), final states")
    axes[1].set_xlabel("r")
    axes[2].set_title("far-field shell-avg |E_A|(r)")
    axes[2].set_xlabel("r")
    for ax in axes:
        ax.legend(fontsize=6)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m7_4_dilation_charge.png"), dpi=130)
    print("wrote plots/m7_4_dilation_charge.png")


def winner(seed="ck", conv_name="repulsive", N=96, L=16.0, n_iter=2000):
    """Re-relax the winning cell at higher N; save section + lambda_eff plots."""
    import taichi as ti
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from m7_1_harmonic_lattice import lambda_eff_np
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)
    conv = F_CONV[conv_name]
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, conv["c1"], conv["c2"])
    f0 = apply_vacuum_shell(build_seed(seed, N, L))
    fR, info = relax_state(eng, f0, conv, n_iter=n_iter, tag=f"win:{seed}/{conv_name}")
    meas = measure_state(fR, eng, conv)
    dil = dilation_probe(fR, eng, conv)
    out = {"seed": seed, "conv": conv_name, "N": N,
           "relax": {k: v for k, v in info.items() if k != "history"},
           "history": info["history"], "measure": meas, "dilation": dil}
    with open(os.path.join(DATA, "m7_4_winner.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote data/m7_4_winner.json")

    h = fR.h
    k0 = N // 2
    B = curl_np(fR.avc, h)
    lam_eff, F2 = lambda_eff_np(B, h)
    rc, rs, EAc, EAs = charge_observables(fR)
    rho_rms = np.sqrt(0.5 * (rc ** 2 + rs ** 2))
    fig, axes = plt.subplots(1, 4, figsize=(19, 4.4))
    ext = (-L / 2, L / 2, -L / 2, L / 2)
    im0 = axes[0].imshow(np.linalg.norm(B[:, :, k0], axis=-1).T, origin="lower",
                         extent=ext)
    axes[0].set_title(f"|B_A| midplane ({seed}/{conv_name}, N={N})")
    wmask = np.linalg.norm(B[:, :, k0], axis=-1) > 0.05 * np.max(np.linalg.norm(B, axis=-1))
    lam_slice = np.where(wmask, lam_eff[:, :, k0], np.nan)
    im1 = axes[1].imshow(lam_slice.T, origin="lower", extent=ext, cmap="coolwarm")
    axes[1].set_title("lambda_eff = B.(curlB)/|B|^2 (core)")
    im2 = axes[2].imshow(rho_rms[:, :, k0].T, origin="lower", extent=ext)
    axes[2].set_title("RMS charge density rho_rms")
    axes[3].imshow(np.linalg.norm(fR.jvc[:, :, k0], axis=-1).T, origin="lower",
                   extent=ext)
    axes[3].set_title("|J_c| (the coupling-driven condensate)")
    for im, ax in ((im0, axes[0]), (im1, axes[1]), (im2, axes[2])):
        fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m7_4_winner_sections.png"), dpi=130)
    print("wrote plots/m7_4_winner_sections.png")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["smoke", "run", "winner", "analyze"])
    ap.add_argument("--n-iter", type=int, default=1500)
    ap.add_argument("--seed", type=str, default="ck")
    ap.add_argument("--conv", type=str, default="repulsive")
    args = ap.parse_args()
    t0 = time.time()
    if args.mode == "smoke":
        run_matrix(N=48, L=16.0, n_iter=500, seeds=("ck",),
                   out_name="m7_4_smoke.json")
    elif args.mode == "run":
        run_matrix(N=64, L=16.0, n_iter=args.n_iter)
    elif args.mode == "analyze":
        analyze()
    elif args.mode == "winner":
        winner(seed=args.seed, conv_name=args.conv, n_iter=args.n_iter)
    print(f"\ntotal {time.time() - t0:.1f}s")
