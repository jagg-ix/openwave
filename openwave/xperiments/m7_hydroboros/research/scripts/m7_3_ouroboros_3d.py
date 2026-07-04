"""M7.3 - reproduce M6's electron in full 3D (verbatim-ODE pre-gate + 3D chaoiton).

Task doc: research/tasks/m7_3_ouroboros_3d.md. Modes:

  python m7_3_ouroboros_3d.py pregate   sympy reduction scan: which ansatz makes the
                                        benchmark ODE the verbatim reduction of the M6
                                        Lagrangian, and which reduced functional
                                        (averaged Lagrangian vs averaged Hamiltonian)
                                        has it as Euler-Lagrange equations
  python m7_3_ouroboros_3d.py embed     numeric pre-gate: embed the converged 1D profile
                                        on the 3D lattice, compare every functional
                                        against its 1D quadrature, gradient residual
  python m7_3_ouroboros_3d.py relax     stage-2 (symmetry-constrained) + stage-3 (free
                                        3D) fixed-Q relaxation; H/Q vs the 1.6890 ledger
  python m7_3_ouroboros_3d.py all       everything in sequence

The three circulating ODE forms this pre-gate adjudicates (research/checkpoints and
m6_ouroboros/research/0c_sandbox_v8.md step 3):

  benchmark (H/Q = 1.6890 producer, sandbox_v8/ouroboros_benchmark.py):
      a'' + a'/r - a/r^2 + w^2 a = b
      b'' + b'/r - b/r^2 + w^2 b = a - lam b - 4 g b^3
  canonical 0d_canonical.md section 2.2 (the "2 w a" chiral form):
      a'' + a'/r - a/r^2 + (w^2 - mJ^2) a + 4 g a (a^2+b^2) = 0
      b'' + b'/r - b/r^2 + 2 w a - mJ^2 b + 4 g b (a^2+b^2) = 0
  LoE 9b section 5.1 ansatz (no explicit ODE): A = z_hat x grad(phi) cos wt,
      J = z_hat x grad(psi) sin wt  (azimuthal vectors, quadrature phases)

Geometry contract for the 3D run: the 1D ODE lives on the STRAIGHT CYLINDER
(r = cylindrical radius, fields z-independent), so the lattice is a periodic box with
a thin/periodic z-axis; H/Q per unit length is invariant to the 2 pi L_z measure
factor. The torus compactification (where the Q_CS = 1 linking lives) is out of scope
here and deferred to M7.4; documented honestly at the gate.

Headless module (matplotlib PNG only). Data: research/data/m7_3_*.json.
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
    m6_profile,
)

DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")


# =============================================================================
# PART 1 - sympy pre-gate
# =============================================================================

def _cyl_EB(X0, Xr, Xp, Xz, r, phi, t):
    """E and B of a 4-potential (X0, Xvec) in cylindrical coords, z-independent.
    E = -grad X0 - dt Xvec ; B = curl Xvec."""
    import sympy as sp
    Er = -sp.diff(X0, r) - sp.diff(Xr, t)
    Ep = -sp.diff(X0, phi) / r - sp.diff(Xp, t)
    Ez = -sp.diff(Xz, t)
    Br = sp.diff(Xz, phi) / r
    Bp = -sp.diff(Xz, r)
    Bz = (sp.diff(r * Xp, r) - sp.diff(Xr, phi)) / r
    return (Er, Ep, Ez), (Br, Bp, Bz)


def _avg(expr, t, w, phi=None):
    """Average over one time period (and over phi if given)."""
    import sympy as sp
    T = 2 * sp.pi / w
    out = sp.integrate(expr, (t, 0, T)) / T
    if phi is not None:
        out = sp.integrate(out, (phi, 0, 2 * sp.pi)) / (2 * sp.pi)
    return sp.simplify(sp.expand_trig(sp.expand(out)))


def _dot3(u, v):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def pregate():
    """Sympy scan: candidate ansaetze -> reduced averaged Lagrangian / Hamiltonian ->
    Euler-Lagrange equations -> verbatim comparison against the benchmark and the
    canonical-2.2 ODE forms. Prints the adjudication table, writes the JSON."""
    import sympy as sp

    r, phi, t = sp.symbols("r phi t", positive=True)
    w = sp.Symbol("omega", positive=True)
    kap = sp.Symbol("kappa")          # coupling coefficient (the mJ^2 A.J strength)
    c1 = sp.Symbol("c1")              # linear f-term coefficient, f = c1 s + c2 s^2
    c2 = sp.Symbol("c2")              # quartic f-term coefficient
    lam = sp.Symbol("lambda")         # the benchmark's lambda
    g = sp.Symbol("g", positive=True)
    mJ2 = sp.Symbol("mJ2")
    a = sp.Function("a")(r)
    b = sp.Function("b")(r)

    ct, st = sp.cos(w * t), sp.sin(w * t)
    zero = sp.Integer(0)

    # each candidate: name -> (A0, Ar, Ap, Az, J0, Jr, Jp, Jz), quartic mode
    # quartic mode "exact": <f(s(t))> with s = -J0^2+|Jvec|^2 integrated exactly;
    # "rwa": f evaluated at s0 = <s(t)> (the rotating-wave / first-harmonic
    # truncation the benchmark's 4 g b^3 suggests).
    candidates = {
        # canonical section 2.1 text: A0 scalar cos, J azimuthal sin
        "C1_text_A0cos_Jphi_sin": (a * ct, zero, zero, zero,
                                   zero, zero, b * st, zero),
        # same-phase azimuthal doublet
        "C2_Aphi_cos_Jphi_cos": (zero, zero, a * ct, zero,
                                 zero, zero, b * ct, zero),
        # quadrature azimuthal doublet (LoE 9b section 5.1 phases)
        "C3_Aphi_cos_Jphi_sin": (zero, zero, a * ct, zero,
                                 zero, zero, b * st, zero),
        # co-rotating in the (phi, z) plane, same phase
        "C4_rot_inphase": (zero, zero, a * ct, a * st,
                           zero, zero, b * ct, b * st),
        # rotating, J a quarter turn behind A (ouroboros chase)
        "C5_rot_quarter": (zero, zero, a * ct, a * st,
                           zero, zero, b * st, -b * ct),
        # counter-rotating
        "C6_rot_counter": (zero, zero, a * ct, a * st,
                           zero, zero, b * ct, -b * st),
    }

    # target ODE forms, written as residual == 0 with the a'' coefficient +1
    ap, bp = sp.diff(a, r), sp.diff(b, r)
    app, bpp = sp.diff(a, r, 2), sp.diff(b, r, 2)
    veclap_a = app + ap / r - a / r**2
    veclap_b = bpp + bp / r - b / r**2
    bench_a = veclap_a + w**2 * a - b
    bench_b = veclap_b + w**2 * b - a + lam * b + 4 * g * b**3
    canon_a = veclap_a + (w**2 - mJ2) * a + 4 * g * a * (a**2 + b**2)
    canon_b = veclap_b + 2 * w * a - mJ2 * b + 4 * g * b * (a**2 + b**2)

    def reduce_candidate(fields, quartic):
        A0, Ar, Ap_, Az, J0, Jr, Jp, Jz = fields
        EA, BA = _cyl_EB(A0, Ar, Ap_, Az, r, phi, t)
        EJ, BJ = _cyl_EB(J0, Jr, Jp, Jz, r, phi, t)
        AJ = -A0 * J0 + Ar * Jr + Ap_ * Jp + Az * Jz
        s = -J0**2 + Jr**2 + Jp**2 + Jz**2
        quadL = (_dot3(EA, EA) - _dot3(BA, BA)) / 2 + (_dot3(EJ, EJ) - _dot3(BJ, BJ)) / 2
        quadH = (_dot3(EA, EA) + _dot3(BA, BA)) / 2 + (_dot3(EJ, EJ) + _dot3(BJ, BJ)) / 2
        if quartic == "exact":
            f_avg = _avg(c1 * s + c2 * s**2, t, w)
        else:  # rwa: f at s0 = <s>
            s0 = _avg(s, t, w)
            f_avg = c1 * s0 + c2 * s0**2
        L_avg = _avg(quadL, t, w) + kap * _avg(AJ, t, w) - f_avg
        H_avg = _avg(quadH, t, w) - kap * _avg(AJ, t, w) + f_avg
        # canonical charge Q_can = (1/w) <p_A . dt(Avec) + p_J . dt(Jvec)>,
        # p_X = dL/d(dt Xvec) = E_X  (from  L ~ 1/2 |E_X|^2, E_X = -grad X0 - dt Xvec
        # => dL/d(dtXvec) = -E_X ... sign fixed by the oscillator identity below)
        pdotA = -(EA[0] * sp.diff(Ar, t) + EA[1] * sp.diff(Ap_, t) + EA[2] * sp.diff(Az, t))
        pdotJ = -(EJ[0] * sp.diff(Jr, t) + EJ[1] * sp.diff(Jp, t) + EJ[2] * sp.diff(Jz, t))
        Q_can = sp.simplify(_avg(pdotA + pdotJ, t, w) / w)
        return sp.simplify(L_avg), sp.simplify(H_avg), Q_can

    def el_equations(density):
        """EL equations of  integral density * r dr  for the profiles a, b."""
        Ld = sp.expand(density * r)
        eqs = []
        for fun in (a, b):
            expr = (sp.diff(Ld, fun)
                    - sp.diff(sp.diff(Ld, sp.diff(fun, r)), r))
            eqs.append(sp.expand(sp.simplify(sp.expand(expr))))
        return eqs

    def match(eq, target, solve_syms):
        """Does eq == c * target (nonzero constant c) for some values of the
        convention symbols in solve_syms? Returns (verdict, solved dict)."""
        eq = sp.expand(eq)
        target = sp.expand(target)
        for lead in (app, bpp):
            ce = eq.coeff(lead)
            ctg = target.coeff(lead)
            if ce != 0 and ctg != 0:
                diff = sp.expand(sp.cancel(eq / ce - target / ctg))
                if diff == 0:
                    return True, {}
                sols = sp.solve(diff, solve_syms, dict=True)
                for so in sols:
                    if all(v.free_symbols <= {w, lam, g, mJ2} for v in so.values()):
                        if sp.simplify(diff.subs(so)) == 0:
                            return True, {str(k): sp.simplify(v) for k, v in so.items()}
                return False, {"residual": str(sp.simplify(diff))}
        return False, {"residual": "no second-derivative term"}

    def joint_match(eqs, targets, solve_syms):
        """Match the pair of EL equations against the pair of target ODEs with ONE
        consistent set of convention values (kappa, c1, c2, [mJ2])."""
        for pair in ((0, 1), (1, 0)):
            okA, solA = match(eqs[pair[0]], targets[0], solve_syms)
            okB, solB = match(eqs[pair[1]], targets[1], solve_syms)
            if okA and okB:
                merged = dict(solA)
                consistent = True
                for k, v in solB.items():
                    if k in merged and sp.simplify(sp.sympify(merged[k]) - sp.sympify(v)) != 0:
                        consistent = False
                    merged[k] = v
                if consistent:
                    return True, merged
        return False, {"a_eq": str(solA), "b_eq": str(solB)}

    results = {}
    print("=" * 78)
    print("M7.3 PRE-GATE: sympy reduction scan")
    print("  L = -1/4 F^2 - 1/4 G^2 + kappa A.J - f(J.J),  f(s) = c1 s + c2 s^2")
    print("  solving (kappa, c1, c2) so EL(<L>) == benchmark ODE verbatim")
    print("=" * 78)
    for name, fields in candidates.items():
        for quartic in ("rwa", "exact"):
            L_avg, H_avg, Q_can = reduce_candidate(fields, quartic)
            if L_avg == 0:
                results[f"{name}[{quartic}]"] = {"verdict": "L_avg == 0 (degenerate)"}
                continue
            elL = el_equations(L_avg)
            elH = el_equations(H_avg)
            entry = {"L_avg": str(L_avg), "H_avg": str(H_avg),
                     "Q_can": str(Q_can), "quartic": quartic}
            okL, solL = joint_match(elL, (bench_a, bench_b), [kap, c1, c2])
            entry["benchmark_match"] = bool(okL)
            entry["conventions" if okL else "benchmark_residuals"] = \
                {k: str(v) for k, v in solL.items()}
            okC, solC = joint_match(elL, (canon_a, canon_b), [kap, c1, c2, mJ2])
            entry["canonical22_match"] = bool(okC)
            if okC:
                entry["canonical22_conventions"] = {k: str(v) for k, v in solC.items()}
            okH, solH = joint_match(elH, (bench_a, bench_b), [kap, c1, c2])
            entry["H_avg_EL_matches_benchmark"] = bool(okH)
            if not okH:
                entry["H_avg_EL_residuals"] = {k: str(v) for k, v in solH.items()}
            # the reduced-action identity <L> = w Q_can - <H> (oscillator structure)
            ident = sp.simplify(L_avg - (w * Q_can - H_avg))
            entry["L_eq_wQ_minus_H"] = str(ident)
            entry["EL_of_L_avg"] = [str(e) for e in elL]
            entry["EL_of_H_avg"] = [str(e) for e in elH]
            results[f"{name}[{quartic}]"] = entry
            print(f"{name:24s} [{quartic:5s}]  bench: "
                  f"{'MATCH' if okL else 'no':5s}  canon2.2: "
                  f"{'MATCH' if okC else 'no':5s}  E_omega-EL: "
                  f"{'MATCH' if okH else 'no':5s}  <L>=wQ-<H>: "
                  f"{'OK' if ident == 0 else str(ident)}")
            if okL:
                print(f"    conventions: {entry['conventions']}")
                print(f"    Q_can = {entry['Q_can']}")

    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "m7_3_pregate_sympy.json")
    with open(out, "w") as fh:
        json.dump(results, fh, indent=1, default=str)
    print(f"\nwrote {out}")
    return results


# =============================================================================
# PART 2 - numeric pre-gate: embed the 1D profile, windowed quadratures,
# gradient residual of the pinned functional
# =============================================================================
#
# Pinned conventions (from the sympy pre-gate, data/m7_3_pregate_sympy.json):
#   reduced action  S_w = <L> ,  EL(S_w) == benchmark ODE verbatim on
#   avc = a(rho) phi_hat, jvc = b(rho) phi_hat  (same-phase azimuthal doublet)
#   with kappa = -1 (coupling term -<A.J>) and f_avg = c1 s0 + c2 (s0^2 +
#   (s1^2+s2^2)/2), c1 = -lam/2, c2 = -4g/3 (exact harmonic bookkeeping).
#   E_w = <H> = quad(+) + <A.J> + f_avg ;  S_w = omega Q_can - E_w ;
#   Q_can = -1/2 int [EAc.avs - EAs.avc + EJc.jvs - EJs.jvc]  (identity checked).
#
# The benchmark ledger quadratures as 3D lattice integrals (per unit length,
# windowed at rho <= W with the M7.2 interface weight):
#   Q_J  = (1/2 pi Lz) int w (|jvc|^2 + |jvs|^2)
#   H_bh = (1/2 pi Lz) int w (|grad avc|_F^2 + |grad avs|_F^2 + |grad jvc|_F^2
#                             + |grad jvs|_F^2 + 4 g (|jvc|^2+|jvs|^2)^2)
#   (Frobenius gradient norm: on the ansatz |grad(a phi_hat)|_F^2 = a'^2 + a^2/rho^2,
#    the exact benchmark integrand; |curl|^2 differs by the boundary term a(W)^2,
#    NOT negligible for a delocalized profile.)

from m7_1_harmonic_lattice import COMP_NAMES, COMP_VEC, d_axis, grad_np, curl_np, dot  # noqa: E402

W_WINDOW = 12.0     # the benchmark R_MAX: H/Q = 1.6890 lives on this window
OMEGA, LAM, G = 1.0, 1.0, 1.0
R_SOLVE = 22.0      # solve the 1D profile out to the box corner


class HF3:
    """Anisotropic harmonic-field container (Nx, Ny, Nz), cubic cells h."""

    def __init__(self, Nx, Ny, Nz, h, dtype=np.float64):
        self.Nx, self.Ny, self.Nz, self.h = Nx, Ny, Nz, h
        for name in COMP_NAMES:
            shape = (Nx, Ny, Nz, 3) if COMP_VEC[name] else (Nx, Ny, Nz)
            setattr(self, name, np.zeros(shape, dtype=dtype))

    def pack(self):
        return np.concatenate([getattr(self, n).ravel() for n in COMP_NAMES])

    def unpack(self, x):
        off = 0
        for name in COMP_NAMES:
            arr = getattr(self, name)
            n = arr.size
            setattr(self, name, x[off:off + n].reshape(arr.shape))
            off += n
        return self


def grid_rho_phi(Nx, Ny, Nz, h):
    """Cell-centered grid; x, y centered on the axis, z from 0."""
    xs = (np.arange(Nx) + 0.5) * h - Nx * h / 2
    ys = (np.arange(Ny) + 0.5) * h - Ny * h / 2
    zs = (np.arange(Nz) + 0.5) * h
    X, Y, Z = np.meshgrid(xs, ys, zs, indexing="ij")
    rho = np.sqrt(X * X + Y * Y)
    return X, Y, Z, rho


def solve_profile(r_max=R_SOLVE, n_grid=2200):
    out = m6_profile(g=G, omega=OMEGA, lam=LAM, r_max=r_max, n_grid=n_grid)
    if out is None:
        raise RuntimeError("1D profile solve failed")
    return out


def embed_profile(Nx, Ny, Nz, h, r1d, a1d, b1d):
    """avc = a(rho) phi_hat, jvc = b(rho) phi_hat (the C2 winner)."""
    X, Y, Z, rho = grid_rho_phi(Nx, Ny, Nz, h)
    rho_safe = np.maximum(rho, 1e-12)
    a3 = np.interp(rho.ravel(), r1d, a1d, left=a1d[0] * 0, right=0.0).reshape(rho.shape)
    b3 = np.interp(rho.ravel(), r1d, b1d, left=b1d[0] * 0, right=0.0).reshape(rho.shape)
    # linear regularity at the axis: a ~ A0 rho, so a/rho is finite; interp handles
    phix, phiy = -Y / rho_safe, X / rho_safe
    f = HF3(Nx, Ny, Nz, h)
    f.avc = np.stack([a3 * phix, a3 * phiy, np.zeros_like(a3)], axis=-1)
    f.jvc = np.stack([b3 * phix, b3 * phiy, np.zeros_like(b3)], axis=-1)
    return f, rho


def window_weight(rho, h, W=W_WINDOW):
    """M7.2 interface weight: O(h^2) quadrature of a windowed integrand."""
    return np.clip((W - rho) / h + 0.5, 0.0, 1.0)


def fields_EB(f: HF3, omega):
    h = f.h
    EAc = -grad_np(f.a0c, h) - omega * f.avs
    EAs = -grad_np(f.a0s, h) + omega * f.avc
    EJc = -grad_np(f.j0c, h) - omega * f.jvs
    EJs = -grad_np(f.j0s, h) + omega * f.jvc
    BAc, BAs = curl_np(f.avc, h), curl_np(f.avs, h)
    BJc, BJs = curl_np(f.jvc, h), curl_np(f.jvs, h)
    return EAc, EAs, EJc, EJs, BAc, BAs, BJc, BJs


def densities_pinned(f: HF3, omega, lam, g):
    """Pointwise densities of the pinned functionals. Returns dict of (N,N,Nz)."""
    EAc, EAs, EJc, EJs, BAc, BAs, BJc, BJs = fields_EB(f, omega)
    quadE = 0.25 * (dot(EAc, EAc) + dot(EAs, EAs) + dot(EJc, EJc) + dot(EJs, EJs))
    quadB = 0.25 * (dot(BAc, BAc) + dot(BAs, BAs) + dot(BJc, BJc) + dot(BJs, BJs))
    AdotJ = 0.5 * (-(f.a0c * f.j0c) - (f.a0s * f.j0s)
                   + dot(f.avc, f.jvc) + dot(f.avs, f.jvs))
    s_cc = -(f.j0c ** 2) + dot(f.jvc, f.jvc)
    s_ss = -(f.j0s ** 2) + dot(f.jvs, f.jvs)
    s_cs = -(f.j0c * f.j0s) + dot(f.jvc, f.jvs)
    s0, s1, s2 = 0.5 * (s_cc + s_ss), 0.5 * (s_cc - s_ss), s_cs
    c1, c2 = -lam / 2.0, -4.0 * g / 3.0
    favg = c1 * s0 + c2 * (s0 * s0 + 0.5 * (s1 * s1 + s2 * s2))
    u_E = quadE + quadB + AdotJ + favg            # <H>, pinned conventions
    u_S = quadE - quadB - AdotJ - favg            # <L>
    q_can = -0.5 * (dot(EAc, f.avs) - dot(EAs, f.avc)
                    + dot(EJc, f.jvs) - dot(EJs, f.jvc))
    return {"u_E": u_E, "u_S": u_S, "q_can": q_can}


def frobenius_grad2(V, h):
    """|grad V|_F^2 for a vector field (..., 3): sum of all 9 partials squared."""
    out = 0.0
    for j in range(3):
        for i in range(3):
            out = out + d_axis(V[..., j], i, h) ** 2
    return out


def ledger_quadratures(f: HF3, rho, g, W=W_WINDOW):
    """The benchmark H and Q_J as windowed per-unit-length 3D integrals."""
    h = f.h
    w = window_weight(rho, h, W)
    Lz = f.Nz * h
    norm = h ** 3 / (2.0 * np.pi * Lz)
    amp2 = dot(f.jvc, f.jvc) + dot(f.jvs, f.jvs)
    Q_J = float(np.sum(w * amp2) * norm)
    Hd = (frobenius_grad2(f.avc, h) + frobenius_grad2(f.avs, h)
          + frobenius_grad2(f.jvc, h) + frobenius_grad2(f.jvs, h)
          + 4.0 * g * amp2 * amp2)
    H_bh = float(np.sum(w * Hd) * norm)
    return {"Q_J": Q_J, "H_bench": H_bh, "HQ": H_bh / Q_J if Q_J else np.nan}


def ref_quadratures_1d(r, a, b, g, W=W_WINDOW):
    """Continuum reference: trapz of the benchmark integrands on the fine 1D grid."""
    m = r <= W
    rm, am, bm = r[m], a[m], b[m]
    da = np.gradient(am, rm)
    db = np.gradient(bm, rm)
    Q = np.trapezoid(bm ** 2 * rm, rm)
    H = np.trapezoid((da ** 2 + db ** 2 + am ** 2 / rm ** 2 + bm ** 2 / rm ** 2
                      + 4 * g * bm ** 4) * rm, rm)
    uE = (0.25 * OMEGA ** 2 * (am ** 2 + bm ** 2)
          + 0.25 * ((da + am / rm) ** 2 + (db + bm / rm) ** 2)
          - 0.5 * am * bm                       # kappa = -1 coupling, <A.J> = ab/2
          - LAM / 2 * (bm ** 2 / 2.0)           # c1 s0, s0 = b^2/2
          - (4 * g / 3.0) * (3.0 / 8.0) * bm ** 4)  # c2 (s0^2 + s1^2/2) = c2 3b^4/8
    E_w = np.trapezoid(uE * rm, rm)
    q = 0.5 * OMEGA * (am ** 2 + bm ** 2)
    Q_can = np.trapezoid(q * rm, rm)
    return {"Q_J": float(Q), "H_bench": float(H), "HQ": float(H / Q),
            "E_omega": float(E_w), "Q_can": float(Q_can)}


# ---- Taichi kernels for the pinned functionals (anisotropic shape) ----------


class TaichiPinned:
    """E_omega (pinned) and Q_can with reverse-mode AD on an (Nx, Ny, Nz) grid."""

    def __init__(self, Nx, Ny, Nz, h):
        import taichi as ti
        self.ti = ti
        self.Nx, self.Ny, self.Nz, self.h = Nx, Ny, Nz, h
        self.f = {}
        for name in COMP_NAMES:
            if COMP_VEC[name]:
                self.f[name] = ti.Vector.field(3, dtype=ti.f64, shape=(Nx, Ny, Nz),
                                               needs_grad=True)
            else:
                self.f[name] = ti.field(dtype=ti.f64, shape=(Nx, Ny, Nz),
                                        needs_grad=True)
        self.loss = ti.field(dtype=ti.f64, shape=(), needs_grad=True)
        self.omega = ti.field(dtype=ti.f64, shape=())
        self.lam = ti.field(dtype=ti.f64, shape=())
        self.g = ti.field(dtype=ti.f64, shape=())
        self._build()

    def set_params(self, omega, lam, g):
        self.omega[None], self.lam[None], self.g[None] = omega, lam, g

    def set_fields(self, hf: HF3):
        for name in COMP_NAMES:
            self.f[name].from_numpy(np.ascontiguousarray(getattr(hf, name)))

    def _build(self):
        ti = self.ti
        Nx, Ny, Nz, h = self.Nx, self.Ny, self.Nz, self.h
        a0c, a0s = self.f["a0c"], self.f["a0s"]
        avc, avs = self.f["avc"], self.f["avs"]
        j0c, j0s = self.f["j0c"], self.f["j0s"]
        jvc, jvs = self.f["jvc"], self.f["jvs"]
        loss, omega, lam, g = self.loss, self.omega, self.lam, self.g

        @ti.func
        def grads(F, i, j, k):
            ip, im = (i + 1) % Nx, (i - 1 + Nx) % Nx
            jp, jm = (j + 1) % Ny, (j - 1 + Ny) % Ny
            kp, km = (k + 1) % Nz, (k - 1 + Nz) % Nz
            return ti.Vector([(F[ip, j, k] - F[im, j, k]) / (2 * h),
                              (F[i, jp, k] - F[i, jm, k]) / (2 * h),
                              (F[i, j, kp] - F[i, j, km]) / (2 * h)])

        @ti.func
        def curlv(F, i, j, k):
            ip, im = (i + 1) % Nx, (i - 1 + Nx) % Nx
            jp, jm = (j + 1) % Ny, (j - 1 + Ny) % Ny
            kp, km = (k + 1) % Nz, (k - 1 + Nz) % Nz
            dyFz = (F[i, jp, k][2] - F[i, jm, k][2]) / (2 * h)
            dzFy = (F[i, j, kp][1] - F[i, j, km][1]) / (2 * h)
            dzFx = (F[i, j, kp][0] - F[i, j, km][0]) / (2 * h)
            dxFz = (F[ip, j, k][2] - F[im, j, k][2]) / (2 * h)
            dxFy = (F[ip, j, k][1] - F[im, j, k][1]) / (2 * h)
            dyFx = (F[i, jp, k][0] - F[i, jm, k][0]) / (2 * h)
            return ti.Vector([dyFz - dzFy, dzFx - dxFz, dxFy - dyFx])

        @ti.kernel
        def e_kernel():
            for i, j, k in ti.ndrange(Nx, Ny, Nz):
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
                favg = (-lam[None] / 2.0) * s0 \
                    + (-4.0 * g[None] / 3.0) * (s0 * s0 + 0.5 * (s1 * s1 + s2 * s2))
                loss[None] += (quad + AdotJ + favg) * h ** 3

        @ti.kernel
        def q_kernel():
            for i, j, k in ti.ndrange(Nx, Ny, Nz):
                w = omega[None]
                EAc = -grads(a0c, i, j, k) - w * avs[i, j, k]
                EAs = -grads(a0s, i, j, k) + w * avc[i, j, k]
                EJc = -grads(j0c, i, j, k) - w * jvs[i, j, k]
                EJs = -grads(j0s, i, j, k) + w * jvc[i, j, k]
                q = -0.5 * (EAc.dot(avs[i, j, k]) - EAs.dot(avc[i, j, k])
                            + EJc.dot(jvs[i, j, k]) - EJs.dot(jvc[i, j, k]))
                loss[None] += q * h ** 3

        self._e_kernel, self._q_kernel = e_kernel, q_kernel

    def _run(self, kernel, want_grad):
        ti = self.ti
        self.loss[None] = 0.0
        if want_grad:
            with ti.ad.Tape(loss=self.loss):
                kernel()
            grads = {name: self.f[name].grad.to_numpy() for name in COMP_NAMES}
            return float(self.loss[None]), grads
        kernel()
        return float(self.loss[None]), None

    def energy(self, hf=None, grad=False):
        if hf is not None:
            self.set_fields(hf)
        return self._run(self._e_kernel, grad)

    def qcan(self, hf=None, grad=False):
        if hf is not None:
            self.set_fields(hf)
        return self._run(self._q_kernel, grad)


def pack_grads(gdict):
    return np.concatenate([gdict[n].ravel() for n in COMP_NAMES])


def embed(n_list=(96, 144, 192), L=28.8, Nz=8, make_plots=True):
    """Stage-1 numeric pre-gate."""
    import taichi as ti
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)

    r1d, a1d, b1d, obs_native = solve_profile()
    ref = ref_quadratures_1d(r1d, a1d, b1d, G)
    ledger_native = m6_profile(g=G, omega=OMEGA, lam=LAM, r_max=12.0, n_grid=800)[3]
    print("=" * 78)
    print("M7.3 EMBED (numeric pre-gate)")
    print(f"1D ledger (benchmark native, r_max=12): H/Q = {ledger_native['HQ']:.5f}")
    print(f"1D continuum reference (windowed trapz): H/Q = {ref['HQ']:.5f}  "
          f"Q_J = {ref['Q_J']:.5f}  H = {ref['H_bench']:.5f}")
    print(f"1D E_omega(win) = {ref['E_omega']:.6f}   Q_can(win) = {ref['Q_can']:.6f}")

    results = {"ledger_native": ledger_native, "ref_1d": ref, "runs": []}
    for N in n_list:
        h = L / N
        f, rho = embed_profile(N, N, Nz, h, r1d, a1d, b1d)
        led = ledger_quadratures(f, rho, G)
        dens = densities_pinned(f, OMEGA, LAM, G)
        w = window_weight(rho, h)
        Lz = Nz * h
        norm = h ** 3 / (2 * np.pi * Lz)
        E_w = float(np.sum(w * dens["u_E"]) * norm)
        Q_w = float(np.sum(w * dens["q_can"]) * norm)
        # identity S = w Qcan - E on the full box (numpy densities)
        S_full = float(np.sum(dens["u_S"])) * h ** 3
        E_full = float(np.sum(dens["u_E"])) * h ** 3
        Qc_full = float(np.sum(dens["q_can"])) * h ** 3
        ident = abs(S_full - (OMEGA * Qc_full - E_full)) / max(abs(S_full), 1e-30)

        # Taichi twin + gradient residual  gE - omega gQ  (window interior)
        eng = TaichiPinned(N, N, Nz, h)
        eng.set_params(OMEGA, LAM, G)
        eng.set_fields(f)
        E_ti, gE = eng.energy(grad=True)
        Q_ti, gQ = eng.qcan(grad=True)
        twin = abs(E_ti - E_full) / max(abs(E_full), 1e-30)
        interior = rho < (W_WINDOW - 2 * h)
        sup_r, sup_g = 0.0, 0.0
        for name in COMP_NAMES:
            rcomp = gE[name] - OMEGA * gQ[name]
            sup_r = max(sup_r, float(np.max(np.abs(rcomp[interior]))))
            sup_g = max(sup_g, float(np.max(np.abs(gE[name]))))
        rel_res = sup_r / max(sup_g, 1e-30)

        run = {"N": N, "h": h,
               "Q_J": led["Q_J"], "H_bench": led["H_bench"], "HQ": led["HQ"],
               "E_omega_win": E_w, "Q_can_win": Q_w,
               "identity_S_wQ_E": ident, "taichi_twin_rel": twin,
               "residual_sup": sup_r, "residual_rel": rel_res}
        results["runs"].append(run)
        print(f"N={N:4d} h={h:.4f}  H/Q={led['HQ']:.5f} "
              f"(vs ref {ref['HQ']:.5f}, dev {abs(led['HQ']/ref['HQ']-1):.2e})  "
              f"ident={ident:.2e}  twin={twin:.2e}  resid_rel={rel_res:.3e}")

    # Richardson on H/Q with the two finest grids (h^2 expected)
    if len(results["runs"]) >= 2:
        r2, r1 = results["runs"][-2], results["runs"][-1]
        p = 2.0
        hq_extrap = r1["HQ"] + (r1["HQ"] - r2["HQ"]) / ((r2["h"] / r1["h"]) ** p - 1)
        results["HQ_extrap_h2"] = hq_extrap
        results["HQ_extrap_dev_vs_ref"] = abs(hq_extrap / ref["HQ"] - 1)
        results["HQ_extrap_dev_vs_ledger"] = abs(hq_extrap / ledger_native["HQ"] - 1)
        print(f"H/Q Richardson (h^2): {hq_extrap:.5f}  "
              f"dev vs continuum ref {results['HQ_extrap_dev_vs_ref']:.2e}, "
              f"vs native ledger {results['HQ_extrap_dev_vs_ledger']:.2e}")

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "m7_3_embed.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    print(f"wrote {os.path.join(DATA, 'm7_3_embed.json')}")

    if make_plots:
        _plot_profile_and_convergence(r1d, a1d, b1d, results)
    return results


def _plot_profile_and_convergence(r1d, a1d, b1d, emb):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    ax = axes[0]
    ax.plot(r1d, a1d, label="alpha (A_phi)")
    ax.plot(r1d, b1d, label="beta (J_phi)")
    ax.axvline(W_WINDOW, color="k", ls=":", lw=1, label="window r = 12")
    ax.set_xlabel("rho")
    ax.set_title("M6 benchmark profile (g=1, omega=1, lam=1)\nnon-decaying tail")
    ax.legend()

    ax = axes[1]
    rmaxs = np.linspace(3, R_SOLVE - 0.2, 120)
    hqs = []
    for rc in rmaxs:
        m = r1d <= rc
        rm = r1d[m]
        am, bm = a1d[m], b1d[m]
        da, db = np.gradient(am, rm), np.gradient(bm, rm)
        Q = np.trapezoid(bm ** 2 * rm, rm)
        H = np.trapezoid((da ** 2 + db ** 2 + am ** 2 / rm ** 2 + bm ** 2 / rm ** 2
                          + 4 * G * bm ** 4) * rm, rm)
        hqs.append(H / Q if Q > 0 else np.nan)
    ax.plot(rmaxs, hqs)
    ax.axvline(12.0, color="k", ls=":", lw=1)
    ax.axhline(1.6890, color="r", ls="--", lw=1, label="ledger 1.6890")
    ax.set_xlabel("integration window r_max")
    ax.set_ylabel("H/Q")
    ax.set_title("H/Q is WINDOWED (ledger = r_max 12)")
    ax.legend()

    ax = axes[2]
    hs = [r["h"] for r in emb["runs"]]
    devs = [abs(r["HQ"] / emb["ref_1d"]["HQ"] - 1) for r in emb["runs"]]
    rres = [r["residual_rel"] for r in emb["runs"]]
    ax.loglog(hs, devs, "o-", label="|H/Q dev| vs 1D ref")
    ax.loglog(hs, rres, "s-", label="rel EL residual |gE - w gQ|")
    ax.loglog(hs, [devs[-1] * (x / hs[-1]) ** 2 for x in hs], "k:", label="h^2")
    ax.set_xlabel("h")
    ax.set_title("3D lattice convergence")
    ax.legend()
    fig.tight_layout()
    os.makedirs(PLOTS, exist_ok=True)
    out = os.path.join(PLOTS, "m7_3_embed_convergence.png")
    fig.savefig(out, dpi=130)
    print(f"wrote {out}")


# =============================================================================
# PART 3 - relaxation: stage 2 (symmetry-constrained) + stage 3 (free 3D)
# =============================================================================


def cyl_project(gdict, rho2d, cph, sph, nbins):
    """Project a gradient dict onto the axisymmetric z-independent subspace:
    z-average, convert vectors to the cylindrical basis, annular bin-average,
    broadcast back. Linear and (up to binning) idempotent. rho2d, cph, sph
    are (Nx, Ny) slices (the grid is z-independent)."""
    rb = rho2d.ravel()
    edges = np.linspace(0.0, rb.max() + 1e-9, nbins + 1)
    idx = np.clip(np.digitize(rb, edges) - 1, 0, nbins - 1)
    cnt = np.maximum(np.bincount(idx, minlength=nbins), 1)

    def radial_avg(F2):        # F2: (Nx, Ny) -> binned profile broadcast back
        s = np.bincount(idx, weights=F2.ravel(), minlength=nbins)
        return (s / cnt)[idx].reshape(F2.shape)

    out = {}
    for name, arr in gdict.items():
        Nz = arr.shape[2]
        zavg = arr.mean(axis=2)                    # (Nx, Ny[,3])
        if not COMP_VEC[name]:
            prof = radial_avg(zavg)
            out[name] = np.repeat(prof[:, :, None], Nz, axis=2)
        else:
            vx, vy, vz = zavg[..., 0], zavg[..., 1], zavg[..., 2]
            vr = vx * cph + vy * sph
            vp = -vx * sph + vy * cph
            vr_p, vp_p, vz_p = radial_avg(vr), radial_avg(vp), radial_avg(vz)
            wx = vr_p * cph - vp_p * sph
            wy = vr_p * sph + vp_p * cph
            v3 = np.stack([wx, wy, vz_p], axis=-1)
            out[name] = np.repeat(v3[:, :, None, :], Nz, axis=2)
    return out


def relax(N=96, L=28.8, Nz=8, Nz_free=32, n_iter=3000, seed_amp=1e-3,
          freeze_rho=13.0, log_every=100):
    """Stage 2 (symmetric) + stage 3 (free 3D) fixed-Q_can relaxation."""
    import taichi as ti
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)
    rng = np.random.default_rng(7)
    r1d, a1d, b1d, _ = solve_profile()
    ref = ref_quadratures_1d(r1d, a1d, b1d, G)
    out_all = {"ref_1d": ref, "stages": {}}

    def run_stage(tag, Nzs, symmetric, perturb):
        h = L / N
        f, rho = embed_profile(N, N, Nzs, h, r1d, a1d, b1d)
        rho3 = rho
        rho2d = rho3[:, :, 0]
        X, Y, _, _ = grid_rho_phi(N, N, Nzs, h)
        rho_safe2d = np.maximum(rho2d, 1e-12)
        cph2d = X[:, :, 0] / rho_safe2d
        sph2d = Y[:, :, 0] / rho_safe2d
        eng = TaichiPinned(N, N, Nzs, h)
        eng.set_params(OMEGA, LAM, G)

        led0 = ledger_quadratures(f, rho3, G)
        frozen = rho3 >= freeze_rho          # Dirichlet: pinned to profile values
        fro_flat = np.concatenate([
            (np.broadcast_to(frozen[..., None], getattr(f, name).shape)
             if COMP_VEC[name] else frozen).ravel()
            for name in COMP_NAMES])

        x0 = f.pack()
        if perturb:
            pert = rng.standard_normal(x0.shape) * seed_amp * np.max(np.abs(x0))
            for _ in range(3):      # smooth the noise
                tmp = HF3(N, N, Nzs, h).unpack(pert)
                for name in COMP_NAMES:
                    arr = getattr(tmp, name)
                    for ax in range(3):
                        arr = (np.roll(arr, 1, axis=ax) + 2 * arr
                               + np.roll(arr, -1, axis=ax)) / 4.0
                    setattr(tmp, name, arr)
                pert = tmp.pack()
            pert[fro_flat] = 0.0
            x0 = x0 + pert
        x_frozen_vals = x0.copy()

        scratch = HF3(N, N, Nzs, h)

        def apply_masks(gflat):
            if symmetric:
                gd = {}
                off = 0
                for name in COMP_NAMES:
                    arr = getattr(scratch, name)
                    n = arr.size
                    gd[name] = gflat[off:off + n].reshape(arr.shape)
                    off += n
                gd = cyl_project(gd, rho2d, cph2d, sph2d, nbins=int(N * 0.75))
                gflat = np.concatenate([gd[n].ravel() for n in COMP_NAMES])
            else:
                gflat = gflat.copy()
            gflat[fro_flat] = 0.0
            return gflat

        def egf(x):
            scratch.unpack(x)
            E, gE = eng.energy(scratch, grad=True)
            return E, pack_grads(gE)

        def qgrad(x):
            scratch.unpack(x)
            Q, gQ = eng.qcan(scratch, grad=True)
            return Q, pack_grads(gQ)

        def qval(x):
            scratch.unpack(x)
            Q, _ = eng.qcan(scratch, grad=False)
            return Q

        Q0 = qval(x0)

        def proj(x, g):
            g = apply_masks(g)
            _, gQ = qgrad(x)
            gQ = apply_masks(gQ)
            d = float(np.dot(gQ, gQ))
            if d > 1e-300:
                g = g - (np.dot(g, gQ) / d) * gQ
            return g

        def corr(x):
            # restore Q_can = Q0 exactly by scaling the FREE dofs:
            # q(alpha) = A alpha^2 + B alpha + C  from three evaluations
            xf = x.copy()
            free = ~fro_flat
            q1 = qval(xf)
            x_zero = xf.copy()
            x_zero[free] = 0.0
            qC = qval(x_zero)
            x_neg = xf.copy()
            x_neg[free] = -x_neg[free]
            qm = qval(x_neg)
            A = 0.5 * (q1 + qm) - qC
            B = 0.5 * (q1 - qm)
            C = qC - Q0
            if abs(A) < 1e-300:
                return x
            disc = B * B - 4 * A * C
            if disc < 0:
                return x
            roots = [(-B + np.sqrt(disc)) / (2 * A), (-B - np.sqrt(disc)) / (2 * A)]
            al = min(roots, key=lambda z: abs(z - 1.0))
            xf[free] = al * xf[free]
            return xf

        from m7_1_harmonic_lattice import fire_minimize
        hist_led = []

        def helicity_A(hf):
            hA = 0.0
            for name in ("avc", "avs"):
                V = getattr(hf, name)
                hA += 0.5 * float(np.sum(dot(V, curl_np(V, h))) * h ** 3)
            return hA

        x, E, gn = corr(x0), None, None
        x_last_ok = x.copy()
        # instrumented FIRE: run in chunks so we can log ledger quantities
        chunk = max(log_every, 50)
        it_done = 0
        status = "converged/ran to n_iter"
        while it_done < n_iter:
            x, E, gn, hh = fire_minimize(
                x, egf, project_fn=proj, correct_fn=corr,
                n_iter=chunk, gtol=1e-12, log_every=0)
            it_done += chunk
            if not np.all(np.isfinite(x)):
                status = f"BLOW-UP (non-finite at iter {it_done}): focusing collapse"
                x = x_last_ok
                scratch.unpack(x)
                break
            x_last_ok = x.copy()
            scratch.unpack(x)
            led = ledger_quadratures(scratch, rho3, G)
            Qn = qval(x)
            drift = float(np.linalg.norm(x - x_frozen_vals)
                          / max(np.linalg.norm(x_frozen_vals), 1e-30))
            zvar = 0.0
            if Nzs > 1:
                num, den = 0.0, 0.0
                for name in COMP_NAMES:
                    arr = getattr(scratch, name)
                    num += float(np.sum(np.var(arr, axis=2)))
                    den += float(np.sum(arr ** 2)) / Nzs
                zvar = num / max(den, 1e-30)
            amp2 = dot(scratch.jvc, scratch.jvc) + dot(scratch.jvs, scratch.jvs)
            pk = np.unravel_index(int(np.argmax(amp2)), amp2.shape)
            hist_led.append({"iter": it_done, "E": E, "gnorm": gn,
                             "Q_can": Qn, "HQ": led["HQ"], "Q_J": led["Q_J"],
                             "drift": drift, "zvar": zvar,
                             "maxfield": float(np.max(np.abs(x))),
                             "peak_rho": float(rho3[pk]),
                             "helicity_A": helicity_A(scratch)})
            print(f"[{tag}] it={it_done:5d}  E={E:+.6e}  |g|={gn:.2e}  "
                  f"H/Q={led['HQ']:.5f}  drift={drift:.3e}  zvar={zvar:.2e}  "
                  f"max|f|={hist_led[-1]['maxfield']:.3f}  "
                  f"peak_rho={hist_led[-1]['peak_rho']:.2f}  "
                  f"H_A={hist_led[-1]['helicity_A']:.2e}")
            if gn < 1e-10:
                break

        led1 = ledger_quadratures(scratch, rho3, G)
        # axisymmetric radial sections of the final state (phi components)
        vp_prof = {}
        rb = rho2d.ravel()
        nb = int(N * 0.75)
        edges = np.linspace(0.0, rb.max() + 1e-9, nb + 1)
        idx = np.clip(np.digitize(rb, edges) - 1, 0, nb - 1)
        cnt = np.maximum(np.bincount(idx, minlength=nb), 1)
        for name in ("avc", "jvc", "avs", "jvs"):
            V = getattr(scratch, name).mean(axis=2)
            vp = -V[..., 0] * sph2d + V[..., 1] * cph2d
            vp_prof[name] = (np.bincount(idx, weights=vp.ravel(), minlength=nb)
                             / cnt).tolist()
        vp_prof["rho_bins"] = (0.5 * (edges[:-1] + edges[1:])).tolist()
        return {"led_seed": led0, "led_final": led1, "history": hist_led,
                "E_final": E, "gnorm_final": gn, "Nz": Nzs, "status": status,
                "HQ_drift_vs_seed": abs(led1["HQ"] / led0["HQ"] - 1),
                "final_profiles": vp_prof}

    print("=" * 78)
    print("M7.3 RELAX stage 2 (symmetry-constrained, thin z)")
    out_all["stages"]["stage2_symmetric"] = run_stage("S2", Nz, True, False)
    print("=" * 78)
    print("M7.3 RELAX stage 3 (free 3D, tall z, perturbed seed)")
    out_all["stages"]["stage3_free"] = run_stage("S3", Nz_free, False, True)

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "m7_3_relax.json"), "w") as fh:
        json.dump(out_all, fh, indent=1)
    print(f"wrote {os.path.join(DATA, 'm7_3_relax.json')}")
    plot_relax(out_all)
    return out_all


def plot_relax(out_all):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 4, figsize=(19, 4.2))
    for tag, st in out_all["stages"].items():
        hh = st["history"]
        its = [x["iter"] for x in hh]
        axes[0].plot(its, [x["E"] for x in hh], "o-", label=tag)
        axes[1].plot(its, [x["HQ"] for x in hh], "o-", label=tag)
        axes[2].semilogy(its, [max(x["drift"], 1e-16) for x in hh], "o-",
                         label=f"{tag} drift")
        axes[2].semilogy(its, [max(x["maxfield"], 1e-16) for x in hh], "s--",
                         label=f"{tag} max|field|")
    axes[0].set_yscale("symlog")
    axes[0].set_title("E_omega (fixed Q_can); blow-up = collapse")
    axes[1].set_yscale("symlog")
    axes[1].set_title("windowed H/Q (seed 1.671 at N=96)")
    axes[1].axhline(1.6890, color="r", ls="--", lw=1)
    axes[2].set_title("drift from seed / max|field| (collapse)")
    # final radial sections vs the seed profile
    ax = axes[3]
    r1d, a1d, b1d, _ = solve_profile()
    ax.plot(r1d, a1d, "k-", lw=1, label="seed alpha")
    ax.plot(r1d, b1d, "k--", lw=1, label="seed beta")
    for tag, st in out_all["stages"].items():
        fp = st.get("final_profiles", {})
        if fp:
            ax.plot(fp["rho_bins"], fp["avc"], label=f"{tag} avc_phi (last finite)")
            ax.plot(fp["rho_bins"], fp["jvc"], "--", label=f"{tag} jvc_phi")
    ax.set_xlim(0, 16)
    ax.set_xlabel("rho")
    ax.set_title("final axisym sections vs seed")
    for ax in axes[:3]:
        ax.set_xlabel("iteration")
    for ax in axes:
        ax.legend(fontsize=7)
    fig.tight_layout()
    out = os.path.join(PLOTS, "m7_3_relax_traces.png")
    fig.savefig(out, dpi=130)
    print(f"wrote {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["pregate", "embed", "relax", "all"])
    ap.add_argument("--n-iter", type=int, default=3000)
    args = ap.parse_args()
    t0 = time.time()
    if args.mode in ("pregate", "all"):
        pregate()
    if args.mode in ("embed", "all"):
        embed()
    if args.mode in ("relax", "all"):
        relax(n_iter=args.n_iter)
    print(f"\ntotal {time.time() - t0:.1f}s")
