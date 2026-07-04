"""The HydroBoros (M7) physics functional, reference implementation.

This is the SMALL AUDITABLE MODULE required by dev_docs/METHOD_NOTE.md:
every term of the energy functional and every observable, in plain numpy,
with this docstring carrying the same equations as the canonical spec
(research/m7_theory_canonical.md). Drivers and engines import from here (or are
cross-validated against it); they never re-implement physics silently.

THE THEORY (pinned at M7.3, tasks/m7_3_ouroboros_3d.md; conventions decided
empirically at M7.4, Q6):

    L = -1/4 F_uv F^uv - 1/4 G_uv G^uv + m_J^2 A.J - f(J.J),   f(s) = c1 s + c2 s^2

Minkowski (-,+,+,+); m_J = 1 (natural units, canonical g = lambda = omega = 1);
the WRITTEN/repulsive convention c1 = +lambda/2, c2 = +g/4 (the only branch
with stable 3D solitons, M7.4; LoE v5 writes f = g s^2 with lambda separate).

THE TIME-HARMONIC FRAME (fixed omega; the de Broglie clock is IN the state):

    A(x,t) = a_c(x) cos wt + a_s(x) sin wt        (vector sector; A0 = 0)
    J(x,t) = j_c(x) cos wt + j_s(x) sin wt        (J0 frozen: M7.4 scalar finding)

E_omega = the PERIOD-AVERAGED ENERGY of the real-time theory on this doublet
(exact identity, verified to 1.85e-14 at M7.5):

    E_omega = INT d^3x [ quad - kappa <A.J> + f_avg ]

    quad  = 1/4 ( |E_Ac|^2 + |E_As|^2 + |E_Jc|^2 + |E_Js|^2
                + |B_Ac|^2 + |B_As|^2 + |B_Jc|^2 + |B_Js|^2 )
            with E_Ac = -w a_s, E_As = +w a_c (temporal gauge), B = curl(.)
    <A.J> = 1/2 ( a_c.j_c + a_s.j_s ),  kappa = -1 (a pure J -> -J relabeling)
    f_avg = c1 s0 + c2 ( s0^2 + (s1^2 + s2^2)/2 )     [EXACT quartic average]
            s_cc = |j_c|^2, s_ss = |j_s|^2, s_cs = j_c.j_s
            s0 = (s_cc + s_ss)/2, s1 = (s_cc - s_ss)/2, s2 = s_cs

THE CONSTRAINTS (the M7.5 frame; both restores are exact rescales):

    Q_can = (w/2) INT ( |a_c|^2 + |a_s|^2 + |j_c|^2 + |j_s|^2 )   [the clock's
            conjugate: dE*/dw = Q_can verified to ~1-2% at M7.5]
    H_A   = 1/2 INT ( a_c.curl a_c + a_s.curl a_s )               [helicity,
            the localization guard: zero-H states delocalize, M7.4/M7.6]

THE OBSERVABLES:

    momentum   <E x B> = (w/2) ( a_c x B_s - a_s x B_c )  per sector, summed
    spin       L = INT x cross <E x B>;  per-quantum j_z from
               <F| -i d/dphi + S_z |F> / <F|F> on F = f_c + i f_s
    charge     rho_c, rho_s = div E_Ac, div E_As; Fleury RMS charge
               Q_rho(<r) = INT sqrt((rho_c^2 + rho_s^2)/2)
    Gauss      net monopole = INT div E_Ac (nonzero only with the scalar
               sector / a fixed j0 reservoir, M7.6)

KNOWN LIMITS (honest, load-bearing): the real-time vacuum of this truncation
is unconditionally tachyonic at long wavelength (det M(0) = -1; band
k^2 < (sqrt5-1)/2; measured rate 0.785 vs 0.786) and harmonic states exist
only above omega* = k* = 0.786 (M7.5, Q14): the clock IS the stabilizer.
The M6 charged ledger H/Q is window-defined (Q11).

Discretization: uniform cubic lattice, spacing h = L/N, central differences
(curl is self-adjoint on the periodic lattice), vacuum Dirichlet shell
(SHELL = 3 cells); volume element h^3 on all integrals.
"""

import numpy as np

OMEGA, LAM, G = 1.0, 1.0, 1.0
KAPPA = -1.0
C1, C2 = +LAM / 2.0, +G / 4.0        # the written/repulsive convention (Q6)
SHELL = 3


# ---- lattice operators (central differences, periodic wrap) ----------------


def d_axis(f, axis, h):
    return (np.roll(f, -1, axis=axis) - np.roll(f, +1, axis=axis)) / (2 * h)


def curl(F, h):
    return np.stack([
        d_axis(F[..., 2], 1, h) - d_axis(F[..., 1], 2, h),
        d_axis(F[..., 0], 2, h) - d_axis(F[..., 2], 0, h),
        d_axis(F[..., 1], 0, h) - d_axis(F[..., 0], 1, h)], axis=-1)


def div(F, h):
    return (d_axis(F[..., 0], 0, h) + d_axis(F[..., 1], 1, h)
            + d_axis(F[..., 2], 2, h))


def dot(a, b):
    return np.sum(a * b, axis=-1)


# ---- the energy functional (term by term, per the docstring) ----------------


def energy_density(ac, as_, jc, js, h, omega=OMEGA, kappa=KAPPA, c1=C1, c2=C2,
                   a0c=None, a0s=None, j0c=None, j0s=None):
    """E_omega density field. Scalars default to zero (the pure-vector
    sector); pass a0/j0 arrays for the Gauss-reservoir experiments."""
    z = np.zeros(ac.shape[:-1])
    a0c = z if a0c is None else a0c
    a0s = z if a0s is None else a0s
    j0c = z if j0c is None else j0c
    j0s = z if j0s is None else j0s
    ga0c = np.stack([d_axis(a0c, i, h) for i in range(3)], axis=-1)
    ga0s = np.stack([d_axis(a0s, i, h) for i in range(3)], axis=-1)
    gj0c = np.stack([d_axis(j0c, i, h) for i in range(3)], axis=-1)
    gj0s = np.stack([d_axis(j0s, i, h) for i in range(3)], axis=-1)
    EAc = -ga0c - omega * as_
    EAs = -ga0s + omega * ac
    EJc = -gj0c - omega * js
    EJs = -gj0s + omega * jc
    quad = 0.25 * (dot(EAc, EAc) + dot(EAs, EAs) + dot(EJc, EJc)
                   + dot(EJs, EJs)
                   + dot(curl(ac, h), curl(ac, h)) + dot(curl(as_, h), curl(as_, h))
                   + dot(curl(jc, h), curl(jc, h)) + dot(curl(js, h), curl(js, h)))
    AdotJ = 0.5 * (-(a0c * j0c) - (a0s * j0s) + dot(ac, jc) + dot(as_, js))
    s_cc = -(j0c ** 2) + dot(jc, jc)
    s_ss = -(j0s ** 2) + dot(js, js)
    s_cs = -(j0c * j0s) + dot(jc, js)
    s0 = 0.5 * (s_cc + s_ss)
    s1 = 0.5 * (s_cc - s_ss)
    s2 = s_cs
    f_avg = c1 * s0 + c2 * (s0 * s0 + 0.5 * (s1 * s1 + s2 * s2))
    return quad - kappa * AdotJ + f_avg


def energy(ac, as_, jc, js, h, **kw):
    return float(np.sum(energy_density(ac, as_, jc, js, h, **kw)) * h ** 3)


# ---- the constraints ---------------------------------------------------------


def q_can(ac, as_, jc, js, h, omega=OMEGA):
    return 0.5 * omega * float(np.sum(dot(ac, ac) + dot(as_, as_)
                                      + dot(jc, jc) + dot(js, js)) * h ** 3)


def helicity_A(ac, as_, h):
    return 0.5 * float(np.sum(dot(ac, curl(ac, h))
                              + dot(as_, curl(as_, h))) * h ** 3)


# ---- the observables ---------------------------------------------------------


def momentum_avg(ac, as_, jc, js, h, omega=OMEGA):
    p = np.zeros(ac.shape)
    for fc, fs in ((ac, as_), (jc, js)):
        p += 0.5 * omega * (np.cross(fc, curl(fs, h))
                            - np.cross(fs, curl(fc, h)))
    return p


def spin_Lz(ac, as_, jc, js, X, Y, Z, h, omega=OMEGA):
    R = np.stack([X, Y, Z], axis=-1)
    p = momentum_avg(ac, as_, jc, js, h, omega)
    return float(np.sum(np.cross(R, p), axis=(0, 1, 2))[2] * h ** 3)


def jz_per_quantum(fc, fs, X, Y, h):
    """<F| -i d/dphi + S_z |F> / <F|F> on the complex doublet F = fc + i fs,
    circular components (F_x -+ iF_y)/sqrt2 carrying spin +-1, F_z spin 0."""
    Fh = fc + 1j * fs
    comps = (((Fh[..., 0] - 1j * Fh[..., 1]) / np.sqrt(2), +1),
             ((Fh[..., 0] + 1j * Fh[..., 1]) / np.sqrt(2), -1),
             (Fh[..., 2], 0))
    num, den = 0.0, 0.0
    for comp, s in comps:
        gx = np.gradient(comp, h, axis=0)
        gy = np.gradient(comp, h, axis=1)
        dphi = X * gy - Y * gx
        num += float(np.real(np.sum(np.conj(comp) * (-1j) * dphi)))
        num += s * float(np.sum(np.abs(comp) ** 2))
        den += float(np.sum(np.abs(comp) ** 2))
    return num / den


def charge_rms(ac, as_, X, Y, Z, h, r_max, omega=OMEGA, a0c=None, a0s=None):
    """Fleury RMS-density charge within r_max (rho from div E_A)."""
    z = np.zeros(ac.shape[:-1])
    a0c = z if a0c is None else a0c
    a0s = z if a0s is None else a0s
    EAc = -np.stack([d_axis(a0c, i, h) for i in range(3)], axis=-1) - omega * as_
    EAs = -np.stack([d_axis(a0s, i, h) for i in range(3)], axis=-1) + omega * ac
    rc, rs = div(EAc, h), div(EAs, h)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    m = r < r_max
    return float(np.sum(np.sqrt(0.5 * (rc[m] ** 2 + rs[m] ** 2))) * h ** 3)
