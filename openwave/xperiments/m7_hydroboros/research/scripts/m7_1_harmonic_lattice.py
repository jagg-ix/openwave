"""M7.1 core module - time-harmonic (A_mu, J_mu) doublet on a 3D lattice.

The M7 / HydroBoros substrate infra (task M7.1, research/tasks/m7_1_infra.md):

  * HarmonicFields  - the 16 real component fields of the fixed-omega ansatz
                      X(x,t) = Xc(x) cos(wt) + Xs(x) sin(wt) for every component
                      of A_mu = (A0, Avec) and J_mu = (J0, Jvec).
  * E_omega         - the period-averaged energy functional, implemented TWICE:
                      a numpy twin (dtype-agnostic, complex-step safe) and a
                      Taichi f64 kernel with reverse-mode AD for the gradient.
  * helicity        - H = int A.(curl A) (static) and the harmonic average.
  * FIRE            - minimizer, with fixed-helicity constrained descent
                      (gradient projection + exact quadratic-rescale correction).
  * seeders         - ABC/Trkalian, Chandrasekhar-Kendall spheromak (toroidal
                      constant-lambda), Bateman/Kedia hopfion, Fleury torus,
                      M6 chaoiton embedding, Ceperley rotating mode.

Conventions (documented in research/tasks/m7_1_infra.md; the final arbiter of
the functional's correctness is the M7.3 verbatim-ODE pre-gate):

  Minkowski (-,+,+,+), A-primary. With A_mu = (A0, Avec), J_mu = (J0, Jvec):
    E_A = -grad A0 - dt Avec,   B_A = curl Avec       (same for the J sector)
    A_mu J^mu  = -A0 J0 + Avec.Jvec
    s = J_mu J^mu = -J0^2 + |Jvec|^2,   f(s) = (g/4) s^2
  Lagrangian (M6 canonical, m6_ouroboros/research/0d_canonical.md section 1):
    L = -1/4 F^2 - 1/4 G^2 + mJ^2 A.J - f(J.J)
  Period-averaged energy density (Legendre transform; interaction terms carry
  no time derivative so H_int = -L_int):
    u = 1/4 (|EAc|^2 + |EAs|^2 + |BAc|^2 + |BAs|^2)          [A sector]
      + 1/4 (|EJc|^2 + |EJs|^2 + |BJc|^2 + |BJs|^2)          [J sector]
      - mJ^2 <A.J> + <f(s)>
  with the exact harmonic averages (no rotating-wave truncation):
    <X(t)Y(t)>   = 1/2 (Xc Yc + Xs Ys)                        [bilinear]
    s(t) = s0 + s1 cos 2wt + s2 sin 2wt,
      s_cc = -j0c^2 + |jvc|^2,  s_ss = -j0s^2 + |jvs|^2,
      s_cs = -j0c j0s + jvc.jvs,
      s0 = (s_cc + s_ss)/2,  s1 = (s_cc - s_ss)/2,  s2 = s_cs
    <s^2> = s0^2 + (s1^2 + s2^2)/2                            [exact quartic]

Units: M6 natural units wholesale (c = 1, electron omega = 1, m_e anchor;
conversion table m6_ouroboros/research/0d_canonical.md section 5).

Boundary conditions: 'periodic' (neutral / net-zero configs, the Woltjer gate)
or 'vacuum' (charged sectors: fields pinned to zero on an n-cell boundary
shell; a net charge on a periodic lattice is Gauss-inconsistent).

Headless module: no rendering, no GUI. Gates runner: m7_1_gates.py.
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# numpy lattice operators (periodic, central differences; dtype-agnostic so a
# complex-step derivative through E_omega_np is exact)
# ---------------------------------------------------------------------------


def d_axis(f, axis, h):
    """Central difference along axis with periodic wrap."""
    return (np.roll(f, -1, axis=axis) - np.roll(f, 1, axis=axis)) / (2.0 * h)


def grad_np(f, h):
    """Gradient of scalar field (N,N,N) -> (N,N,N,3)."""
    return np.stack([d_axis(f, 0, h), d_axis(f, 1, h), d_axis(f, 2, h)], axis=-1)


def curl_np(F, h):
    """Curl of vector field (N,N,N,3) -> (N,N,N,3)."""
    dFx = [d_axis(F[..., 0], a, h) for a in range(3)]
    dFy = [d_axis(F[..., 1], a, h) for a in range(3)]
    dFz = [d_axis(F[..., 2], a, h) for a in range(3)]
    return np.stack([dFz[1] - dFy[2], dFx[2] - dFz[0], dFy[0] - dFx[1]], axis=-1)


def div_np(F, h):
    """Divergence of vector field (N,N,N,3) -> (N,N,N)."""
    return d_axis(F[..., 0], 0, h) + d_axis(F[..., 1], 1, h) + d_axis(F[..., 2], 2, h)


def dot(a, b):
    """Pointwise dot over the trailing axis. NOTE: plain product (a*b), never a
    conjugate norm - keeps the functional holomorphic for complex-step."""
    return np.sum(a * b, axis=-1)


# ---------------------------------------------------------------------------
# Harmonic field container
# ---------------------------------------------------------------------------

COMP_NAMES = ("a0c", "a0s", "avc", "avs", "j0c", "j0s", "jvc", "jvs")
COMP_VEC = {"a0c": False, "a0s": False, "avc": True, "avs": True,
            "j0c": False, "j0s": False, "jvc": True, "jvs": True}


class HarmonicFields:
    """The 16 real components: 4 scalars (N,N,N) + 4 vectors (N,N,N,3)."""

    def __init__(self, N, L, dtype=np.float64):
        self.N, self.L, self.h = N, L, L / N
        for name in COMP_NAMES:
            shape = (N, N, N, 3) if COMP_VEC[name] else (N, N, N)
            setattr(self, name, np.zeros(shape, dtype=dtype))

    def pack(self):
        return np.concatenate([getattr(self, n).ravel() for n in COMP_NAMES])

    def unpack(self, x):
        off = 0
        for name in COMP_NAMES:
            arr = getattr(self, name)
            n = arr.size
            setattr(self, name, x[off:off + n].reshape(arr.shape).astype(arr.dtype, copy=False))
            off += n
        return self

    def astype(self, dtype):
        out = HarmonicFields(self.N, self.L, dtype=dtype)
        for name in COMP_NAMES:
            setattr(out, name, getattr(self, name).astype(dtype))
        return out

    def randomize(self, rng, amp=1.0, smooth=2):
        for name in COMP_NAMES:
            arr = rng.standard_normal(getattr(self, name).shape) * amp
            for _ in range(smooth):  # crude smoothing so fields are resolvable
                for ax in range(3):
                    arr = (np.roll(arr, 1, axis=ax) + 2 * arr + np.roll(arr, -1, axis=ax)) / 4.0
            setattr(self, name, arr)
        return self


def vacuum_mask(N, shell=2):
    """Boolean mask, True in the interior, False on the n-cell boundary shell."""
    m = np.zeros((N, N, N), dtype=bool)
    s = slice(shell, N - shell)
    m[s, s, s] = True
    return m


# ---------------------------------------------------------------------------
# E_omega - numpy twin (complex-step safe)
# ---------------------------------------------------------------------------


def E_omega_np(f: HarmonicFields, omega, mJ, g, density=False):
    """Period-averaged energy of the harmonic doublet (module docstring)."""
    h = f.h
    EAc = -grad_np(f.a0c, h) - omega * f.avs
    EAs = -grad_np(f.a0s, h) + omega * f.avc
    BAc, BAs = curl_np(f.avc, h), curl_np(f.avs, h)
    EJc = -grad_np(f.j0c, h) - omega * f.jvs
    EJs = -grad_np(f.j0s, h) + omega * f.jvc
    BJc, BJs = curl_np(f.jvc, h), curl_np(f.jvs, h)

    quad = 0.25 * (dot(EAc, EAc) + dot(EAs, EAs) + dot(BAc, BAc) + dot(BAs, BAs)
                   + dot(EJc, EJc) + dot(EJs, EJs) + dot(BJc, BJc) + dot(BJs, BJs))

    AdotJ = 0.5 * (-(f.a0c * f.j0c) - (f.a0s * f.j0s)
                   + dot(f.avc, f.jvc) + dot(f.avs, f.jvs))

    s_cc = -(f.j0c * f.j0c) + dot(f.jvc, f.jvc)
    s_ss = -(f.j0s * f.j0s) + dot(f.jvs, f.jvs)
    s_cs = -(f.j0c * f.j0s) + dot(f.jvc, f.jvs)
    s0, s1, s2 = 0.5 * (s_cc + s_ss), 0.5 * (s_cc - s_ss), s_cs
    favg = 0.25 * g * (s0 * s0 + 0.5 * (s1 * s1 + s2 * s2))

    u = quad - (mJ ** 2) * AdotJ + favg
    if density:
        return u
    return np.sum(u) * h ** 3


def E_instantaneous_np(f: HarmonicFields, omega, mJ, g, t):
    """Instantaneous (NOT averaged) energy at time t - the G1 reference."""
    h = f.h
    ct, st = np.cos(omega * t), np.sin(omega * t)
    A0 = f.a0c * ct + f.a0s * st
    Av = f.avc * ct + f.avs * st
    dAv = omega * (-f.avc * st + f.avs * ct)
    J0 = f.j0c * ct + f.j0s * st
    Jv = f.jvc * ct + f.jvs * st
    dJv = omega * (-f.jvc * st + f.jvs * ct)

    EA = -grad_np(A0, h) - dAv
    BA = curl_np(Av, h)
    EJ = -grad_np(J0, h) - dJv
    BJ = curl_np(Jv, h)

    AdotJ = -(A0 * J0) + dot(Av, Jv)
    s = -(J0 * J0) + dot(Jv, Jv)
    u = (0.5 * (dot(EA, EA) + dot(BA, BA)) + 0.5 * (dot(EJ, EJ) + dot(BJ, BJ))
         - (mJ ** 2) * AdotJ + 0.25 * g * s * s)
    return np.sum(u) * h ** 3


# ---------------------------------------------------------------------------
# Helicity
# ---------------------------------------------------------------------------


def helicity_static_np(A, h):
    """H = int A.(curl A) d3x on the periodic box (gauge-invariant there)."""
    return np.sum(dot(A, curl_np(A, h))) * h ** 3


def helicity_static_grad_np(A, h):
    """Analytic dH/dA = 2 curl A (the discrete curl is self-adjoint on the
    periodic lattice with central differences, so this is exact)."""
    return 2.0 * curl_np(A, h)


def helicity_harmonic_np(f: HarmonicFields):
    """Period-averaged A-sector helicity <H> = 1/2 (H[avc] + H[avs])."""
    return 0.5 * (helicity_static_np(f.avc, f.h) + helicity_static_np(f.avs, f.h))


def helicity_fft_np(B, L):
    """Helicity of a periodic divergence-free B given only B, via the FFT
    inverse curl (Coulomb-gauge A). Used for seeds where A is not analytic."""
    N = B.shape[0]
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=L / N)
    KX, KY, KZ = np.meshgrid(k1, k1, k1, indexing="ij")
    K2 = KX ** 2 + KY ** 2 + KZ ** 2
    K2[0, 0, 0] = 1.0
    Bh = [np.fft.fftn(B[..., i]) for i in range(3)]
    # A = i k x B / k^2  satisfies curl A = B (for div-free B, zero-mean)
    Ah = [1j * (KY * Bh[2] - KZ * Bh[1]) / K2,
          1j * (KZ * Bh[0] - KX * Bh[2]) / K2,
          1j * (KX * Bh[1] - KY * Bh[0]) / K2]
    for a in Ah:
        a[0, 0, 0] = 0.0
    A = np.stack([np.real(np.fft.ifftn(a)) for a in Ah], axis=-1)
    return float(np.sum(dot(A, B)) * (L / N) ** 3)


# ---------------------------------------------------------------------------
# Taichi twin - E_omega kernel + AD gradient, and the static curl-energy
# kernel for the Woltjer gate
# ---------------------------------------------------------------------------


class TaichiHarmonicEnergy:
    """Taichi f64 twin of E_omega_np with reverse-mode AD.

    Usage:
        eng = TaichiHarmonicEnergy(N, L)           (after ti.init(arch=ti.cpu,
                                                    default_fp=ti.f64))
        eng.set_params(omega, mJ, g)
        eng.set_fields(f)                          (HarmonicFields, numpy)
        E = eng.energy()
        grads = eng.gradient()                     (dict name -> numpy array)
    """

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
        self.mJ = ti.field(dtype=ti.f64, shape=())
        self.g = ti.field(dtype=ti.f64, shape=())
        self._build_kernel()

    def set_params(self, omega, mJ, g):
        self.omega[None], self.mJ[None], self.g[None] = omega, mJ, g

    def set_fields(self, hf: HarmonicFields):
        for name in COMP_NAMES:
            arr = getattr(hf, name)
            self.f[name].from_numpy(np.ascontiguousarray(arr))

    def _build_kernel(self):
        ti = self.ti
        N, h = self.N, self.h
        a0c, a0s = self.f["a0c"], self.f["a0s"]
        avc, avs = self.f["avc"], self.f["avs"]
        j0c, j0s = self.f["j0c"], self.f["j0s"]
        jvc, jvs = self.f["jvc"], self.f["jvs"]
        loss, omega, mJ, g = self.loss, self.omega, self.mJ, self.g

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
        def energy_kernel():
            for i, j, k in ti.ndrange(N, N, N):
                w = omega[None]
                EAc = -grads(a0c, i, j, k) - w * avs[i, j, k]
                EAs = -grads(a0s, i, j, k) + w * avc[i, j, k]
                BAc = curlv(avc, i, j, k)
                BAs = curlv(avs, i, j, k)
                EJc = -grads(j0c, i, j, k) - w * jvs[i, j, k]
                EJs = -grads(j0s, i, j, k) + w * jvc[i, j, k]
                BJc = curlv(jvc, i, j, k)
                BJs = curlv(jvs, i, j, k)
                quad = 0.25 * (EAc.dot(EAc) + EAs.dot(EAs) + BAc.dot(BAc)
                               + BAs.dot(BAs) + EJc.dot(EJc) + EJs.dot(EJs)
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
                favg = 0.25 * g[None] * (s0 * s0 + 0.5 * (s1 * s1 + s2 * s2))
                u = quad - mJ[None] ** 2 * AdotJ + favg
                loss[None] += u * (h ** 3)

        self._energy_kernel = energy_kernel

    def energy(self):
        self.loss[None] = 0.0
        self._energy_kernel()
        return float(self.loss[None])

    def gradient(self):
        ti = self.ti
        self.loss[None] = 0.0
        with ti.ad.Tape(loss=self.loss):
            self._energy_kernel()
        return {name: self.f[name].grad.to_numpy() for name in COMP_NAMES}


class TaichiCurlEnergy:
    """Static magnetic energy E_B = int |curl A|^2 with AD gradient - the
    Woltjer-Taylor gate functional (single static vector field A)."""

    def __init__(self, N, L):
        import taichi as ti
        self.ti = ti
        self.N, self.L, self.h = N, L, L / N
        self.A = ti.Vector.field(3, dtype=ti.f64, shape=(N, N, N), needs_grad=True)
        self.loss = ti.field(dtype=ti.f64, shape=(), needs_grad=True)
        self._build_kernel()

    def _build_kernel(self):
        ti = self.ti
        N, h = self.N, self.h
        A, loss = self.A, self.loss

        @ti.kernel
        def eb_kernel():
            for i, j, k in ti.ndrange(N, N, N):
                ip, im = (i + 1) % N, (i - 1 + N) % N
                jp, jm = (j + 1) % N, (j - 1 + N) % N
                kp, km = (k + 1) % N, (k - 1 + N) % N
                dyFz = (A[i, jp, k][2] - A[i, jm, k][2]) / (2 * h)
                dzFy = (A[i, j, kp][1] - A[i, j, km][1]) / (2 * h)
                dzFx = (A[i, j, kp][0] - A[i, j, km][0]) / (2 * h)
                dxFz = (A[ip, j, k][2] - A[im, j, k][2]) / (2 * h)
                dxFy = (A[ip, j, k][1] - A[im, j, k][1]) / (2 * h)
                dyFx = (A[i, jp, k][0] - A[i, jm, k][0]) / (2 * h)
                B = ti.Vector([dyFz - dzFy, dzFx - dxFz, dxFy - dyFx])
                loss[None] += B.dot(B) * (h ** 3)

        self._eb_kernel = eb_kernel

    def energy(self, A_np):
        self.A.from_numpy(np.ascontiguousarray(A_np))
        self.loss[None] = 0.0
        self._eb_kernel()
        return float(self.loss[None])

    def energy_grad(self, A_np):
        ti = self.ti
        self.A.from_numpy(np.ascontiguousarray(A_np))
        self.loss[None] = 0.0
        with ti.ad.Tape(loss=self.loss):
            self._eb_kernel()
        return float(self.loss[None]), self.A.grad.to_numpy()


# ---------------------------------------------------------------------------
# FIRE minimizer (Bitzek 2006) with optional single-constraint projection
# ---------------------------------------------------------------------------


def fire_minimize(x0, energy_grad_fn, project_fn=None, correct_fn=None,
                  n_iter=20000, dt0=0.02, dt_max=0.5, f_inc=1.1, f_dec=0.5,
                  alpha0=0.1, f_alpha=0.99, n_min=5, gtol=1e-10, log_every=0):
    """Generic FIRE on a flat array.

    energy_grad_fn(x) -> (E, g);  project_fn(x, g) -> g_projected (constraint
    tangent space);  correct_fn(x) -> x (exact constraint restoration).
    Returns (x, E, gnorm_inf, history list of (it, E, gnorm)).
    """
    x = x0.copy()
    v = np.zeros_like(x)
    dt, alpha, n_pos = dt0, alpha0, 0
    hist = []
    E, gr = energy_grad_fn(x)
    if project_fn is not None:
        gr = project_fn(x, gr)
    for it in range(n_iter):
        F = -gr
        P = float(np.dot(F, v))
        if P > 0:
            n_pos += 1
            if n_pos > n_min:
                dt = min(dt * f_inc, dt_max)
                alpha *= f_alpha
        else:
            n_pos = 0
            dt *= f_dec
            alpha = alpha0
            v[:] = 0.0
        v += dt * F
        fn = np.linalg.norm(F)
        vn = np.linalg.norm(v)
        if fn > 1e-300:
            v = (1 - alpha) * v + alpha * (F / fn) * vn
        x = x + dt * v
        if correct_fn is not None:
            x = correct_fn(x)
        E, gr = energy_grad_fn(x)
        if project_fn is not None:
            gr = project_fn(x, gr)
        gn = float(np.max(np.abs(gr)))
        if log_every and it % log_every == 0:
            hist.append((it, E, gn))
        if gn < gtol:
            hist.append((it, E, gn))
            break
    return x, E, float(np.max(np.abs(gr))), hist


def woltjer_relax(A0_np, L, eng: "TaichiCurlEnergy", H_target, n_iter=20000,
                  gtol=1e-9, log_every=200):
    """Fixed-helicity relaxation of E_B = int |curl A|^2 (the Woltjer gate).

    Constraint handling: project the gradient onto the tangent space of
    H = const, then restore H exactly each step via the quadratic rescale
    A -> A sqrt(H_target/H) (valid while sign(H) = sign(H_target))."""
    N = A0_np.shape[0]
    h = L / N
    shape = A0_np.shape

    def egf(x):
        E, g = eng.energy_grad(x.reshape(shape))
        return E, g.ravel()

    def proj(x, g):
        A = x.reshape(shape)
        gH = helicity_static_grad_np(A, h).ravel() * h ** 3
        return g - (np.dot(g, gH) / np.dot(gH, gH)) * gH

    def corr(x):
        A = x.reshape(shape)
        H = helicity_static_np(A, h)
        if H * H_target <= 0:
            return x
        return (A * np.sqrt(H_target / H)).ravel()

    x0 = corr(A0_np.ravel())
    x, E, gn, hist = fire_minimize(x0, egf, project_fn=proj, correct_fn=corr,
                                   n_iter=n_iter, gtol=gtol, log_every=log_every)
    return x.reshape(shape), E, gn, hist


def lambda_eff_np(F, h, floor=1e-12):
    """Pointwise Beltrami alignment eigenvalue F.(curl F)/|F|^2."""
    C = curl_np(F, h)
    F2 = dot(F, F)
    return dot(F, C) / np.maximum(F2, floor), F2


# ---------------------------------------------------------------------------
# Seeders
# ---------------------------------------------------------------------------


def grid_xyz(N, L, centered=True):
    xs = np.arange(N) * (L / N)
    if centered:
        xs = xs - L / 2 + 0.5 * (L / N)  # cell-centered, origin mid-box
    return np.meshgrid(xs, xs, xs, indexing="ij")


def seed_abc(N, L, kmult=1, A=1.0, B=1.0, C=1.0):
    """ABC / Trkalian curl eigenfield on the periodic box (cell-vertex grid,
    NOT centered - exact periodicity). Returns (A_field, exact) where exact
    holds the continuum invariants: lam = k, H = k V (A^2+B^2+C^2),
    E_B = k^2 V (A^2+B^2+C^2)."""
    xs = np.arange(N) * (L / N)
    X, Y, Z = np.meshgrid(xs, xs, xs, indexing="ij")
    k = 2 * np.pi * kmult / L
    Af = np.stack([A * np.sin(k * Z) + C * np.cos(k * Y),
                   B * np.sin(k * X) + A * np.cos(k * Z),
                   C * np.sin(k * Y) + B * np.cos(k * X)], axis=-1)
    V = L ** 3
    S = A * A + B * B + C * C
    exact = {"lam": k, "H": k * V * S, "E_B": k * k * V * S,
             "lam_discrete": np.sin(k * (L / N)) / (L / N)}
    return Af, exact


def seed_ck_spheromak(N, L, a=None, B0=1.0):
    """Chandrasekhar-Kendall spheromak: axisymmetric constant-lambda Beltrami
    field inside the sphere r < a (lambda a = 4.493409...), zero outside.
    This is the toroidal constant-lambda seed (the Sato-Yamada seeder role;
    the full S&Y eikonal variable-h construction is deferred to M7.4).
    Returns (B_field, exact) with exact lambda; A = B/lam inside."""
    from scipy.special import spherical_jn
    if a is None:
        a = 0.35 * L
    lam_a = 4.493409457909064  # first zero of j1
    lam = lam_a / a
    X, Y, Z = grid_xyz(N, L)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    rho = np.sqrt(X * X + Y * Y)
    r_safe = np.maximum(r, 1e-12)
    rho_safe = np.maximum(rho, 1e-12)
    ct = Z / r_safe
    st = rho / r_safe
    x = lam * r_safe
    j1 = spherical_jn(1, x)
    j1p = spherical_jn(1, x, derivative=True)
    Br = 2 * B0 * (j1 / x) * ct
    Bt = -B0 * (j1 / x + j1p) * st
    Bp = B0 * j1 * st
    inside = r < a
    Br, Bt, Bp = [np.where(inside, f, 0.0) for f in (Br, Bt, Bp)]
    cph = X / rho_safe
    sph = Y / rho_safe
    Bx = Br * st * cph + Bt * ct * cph - Bp * sph
    By = Br * st * sph + Bt * ct * sph + Bp * cph
    Bz = Br * ct - Bt * st
    Bf = np.stack([Bx, By, Bz], axis=-1)
    return Bf, {"lam": lam, "a": a, "inside": inside}


def seed_bateman_hopfion(N, L):
    """Bateman/Kedia hopfion at t = 0: F = grad(alpha) x grad(beta) with
    alpha = (r^2 - 1 + 2iz)/d, beta = 2(x - iy)/d, d = r^2 + 1.
    Returns (E, B) real fields; null EM solution, div E = div B = 0, linked
    (Hopf) field lines. Analytic gradients (rational functions)."""
    X, Y, Z = grid_xyz(N, L)
    r2 = X * X + Y * Y + Z * Z
    d = r2 + 1.0
    d2 = d * d
    # grad alpha
    dax = 4 * X * (1 - 1j * Z) / d2
    day = 4 * Y * (1 - 1j * Z) / d2
    daz = (4 * Z + 2j * (X * X + Y * Y - Z * Z + 1)) / d2
    # grad beta ; beta = 2(x - iy)/d
    dbx = (2 * d - 4 * X * (X - 1j * Y)) / d2
    dby = (-2j * d - 4 * Y * (X - 1j * Y)) / d2
    dbz = -4 * Z * (X - 1j * Y) / d2
    Fx = day * dbz - daz * dby
    Fy = daz * dbx - dax * dbz
    Fz = dax * dby - day * dbx
    E = np.stack([Fx.real, Fy.real, Fz.real], axis=-1)
    B = np.stack([Fx.imag, Fy.imag, Fz.imag], axis=-1)
    return E, B


def seed_fleury_torus(N, L, E0=1.0, R0=1.573, r0=0.152):
    """Fleury/dos Santos torus ansatz (arXiv:2510.22384) as a harmonic pair.

    Conventions contract (research/tasks/m7_2_fleury_torus.md section 2):
    the paper's Heaviside is INVERTED (fields live INSIDE the tube,
    r_local < r0); omega = 2c/R0 is forced by Faraday; the physical field is
    X(t) = Re[Xhat e^{-i omega t}], so cos-component = Re(Xhat) and
    sin-component = Im(Xhat).

    Returns dict with Ec, Es, Bc, Bs (N,N,N,3) and params. Full observable
    validation is task M7.2; here it serves as a seed."""
    X, Y, Z = grid_xyz(N, L)
    R = np.sqrt(X * X + Y * Y)
    R_safe = np.maximum(R, 1e-12)
    rloc = np.sqrt((R - R0) ** 2 + Z * Z)
    inside = rloc < r0
    phi = np.arctan2(Y, X)
    omega = 2.0 / R0  # c = 1
    eip = np.exp(1j * phi)
    # E_hat = i E0 [a_R + i (1 + R/R0) a_phi] e^{i phi} inside the tube
    ER = 1j * E0 * eip
    EP = 1j * E0 * 1j * (1 + R / R0) * eip
    BZ = 1j * E0 * eip  # B0 = E0/c, c = 1
    ER, EP, BZ = [np.where(inside, f, 0.0) for f in (ER, EP, BZ)]
    cph, sph = X / R_safe, Y / R_safe
    Ex = ER * cph - EP * sph
    Ey = ER * sph + EP * cph
    Ez = np.zeros_like(Ex)
    Ec = np.stack([Ex.real, Ey.real, Ez.real], axis=-1)
    Es = np.stack([Ex.imag, Ey.imag, Ez.imag], axis=-1)
    Bc = np.stack([np.zeros_like(BZ.real), np.zeros_like(BZ.real), BZ.real], axis=-1)
    Bs = np.stack([np.zeros_like(BZ.imag), np.zeros_like(BZ.imag), BZ.imag], axis=-1)
    return {"Ec": Ec, "Es": Es, "Bc": Bc, "Bs": Bs,
            "omega": omega, "R0": R0, "r0": r0, "inside": inside}


def m6_profile(g=1.0, omega=1.0, lam=1.0, A0=0.1, B0=0.1,
               r_max=12.0, r_inner=0.02, n_grid=800):
    """Solve the M6 canonical charged-sector ODE (benchmark form, vector
    cylindrical Laplacian, slope BCs) - port of the repo-validated
    m6_ouroboros/research/sandbox_v8/ouroboros_benchmark.py.
    Returns (r, alpha, beta, obs) with obs the H/Q ledger observables."""
    from scipy.integrate import solve_ivp

    def odes(r, y):
        a, da, b, db = y
        d2a = -da / r + a / r ** 2 - omega ** 2 * a + b
        d2b = -db / r + b / r ** 2 - omega ** 2 * b + a - lam * b - 4 * g * b ** 3
        return [da, d2a, db, d2b]

    r_eval = np.linspace(r_inner, r_max, n_grid)
    y0 = [A0 * r_inner, A0, B0 * r_inner, B0]
    sol = solve_ivp(odes, [r_inner, r_max], y0, t_eval=r_eval,
                    method="RK45", rtol=1e-9, atol=1e-11, max_step=0.02)
    if not sol.success:
        return None
    r, a, b = sol.t, sol.y[0], sol.y[2]
    dr = np.diff(r)
    rm = 0.5 * (r[:-1] + r[1:])
    am = 0.5 * (a[:-1] + a[1:])
    bm = 0.5 * (b[:-1] + b[1:])
    dam = np.diff(a) / dr
    dbm = np.diff(b) / dr
    Q_J = np.sum(bm ** 2 * rm * dr)
    H = np.sum((dam ** 2 + dbm ** 2 + am ** 2 / rm ** 2 + bm ** 2 / rm ** 2
                + 4 * g * bm ** 4) * rm * dr)
    obs = {"H": float(H), "Q_J": float(Q_J), "HQ": float(H / Q_J),
           "tail": float(abs(a[-1]) + abs(b[-1]))}
    return r, a, b, obs


def seed_m6_embedding(N, L, profile=None):
    """Embed the M6 1D (alpha, beta) profile as the literal 3D M6 ansatz on a
    straight cylinder (periodic in z):
        a0c = alpha(rho),  jvs = beta(rho) phi_hat     (all other comps 0)
    i.e. A0 = alpha cos(wt), J = beta sin(wt) phi_hat. The toroidal-vs-
    cylindrical embedding question belongs to M7.3. Returns HarmonicFields."""
    if profile is None:
        profile = m6_profile()
    r1d, a1d, b1d, obs = profile
    X, Y, Z = grid_xyz(N, L)
    rho = np.sqrt(X * X + Y * Y)
    rho_safe = np.maximum(rho, 1e-12)
    a3 = np.interp(rho.ravel(), r1d, a1d, left=a1d[0], right=0.0).reshape(rho.shape)
    b3 = np.interp(rho.ravel(), r1d, b1d, left=b1d[0], right=0.0).reshape(rho.shape)
    f = HarmonicFields(N, L)
    f.a0c = a3
    phix, phiy = -Y / rho_safe, X / rho_safe
    f.jvs = np.stack([b3 * phix, b3 * phiy, np.zeros_like(b3)], axis=-1)
    return f, obs


def seed_ceperley_mode(N, L, m=1, kc=None, amp=1.0):
    """Ceperley rotating mode (theory/ceperley_rotating_waves.md section 4):
    scalar rotating pair psi(t) = J_m(kc rho) cos(m phi - wt), delivered as the
    harmonic pair (psi_c, psi_s) = J_m(kc rho) (cos m phi, sin m phi).
    The J_m Bessel envelope is the smooth replacement for Fleury's Heaviside
    mask (the M7.2 stretch). Returns (psi_c, psi_s, meta)."""
    from scipy.special import jv, jn_zeros
    X, Y, Z = grid_xyz(N, L)
    rho = np.sqrt(X * X + Y * Y)
    phi = np.arctan2(Y, X)
    if kc is None:
        kc = jn_zeros(m, 1)[0] / (0.45 * L)  # first zero at rho = 0.45 L
    env = amp * jv(m, kc * rho)
    return env * np.cos(m * phi), env * np.sin(m * phi), {"m": m, "kc": kc}
