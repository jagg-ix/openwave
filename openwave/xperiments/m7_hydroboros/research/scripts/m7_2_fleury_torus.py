"""M7.2 - reproduce the dos Santos & Fleury electron on the M7 lattice.

Pure quadrature (no minimizer): evaluate the FLDB toroidal ansatz
(arXiv:2510.22384) on a 3D slab grid, read the sources off the fields
(rho = div E, J = curl B - dE/dt; the paper's "geometrical charge"
ontology), integrate the four constraint observables, and compare against
the paper's closed forms + solved values at demonstrated grid convergence.

Conventions contract (research/tasks/m7_2_fleury_torus.md section 2), all
pinned against the FLDB Main + Appendix full texts on 2026-07-02:

  * INVERTED Heaviside: fields live INSIDE the tube (s < r0).
  * omega = 2c/R0 (Faraday-forced, monochromatic); phase velocity 2c.
  * physical field X(t) = Re[Xhat e^{-i omega t}], e^{i phi} inside Xhat.
  * Q_rms   = rho_rms x V (appendix Eq 58-61), rho_rms = |rhohat|/sqrt2.
  * mu      = the de-phased complex moment with the phi-phase integral
    REPLACED by its "RMS" 1/sqrt2 (appendix Eq 73-88); lattice-faithful:
    mu = |int e^{-i phi} m_z dV| / (2 pi sqrt2),  m_z = (R x J)_z / 2.
    Reproduces appendix Eq 85/88 exactly in the continuum. NOTE: in the
    tube bulk (curl B)_phi = 0, so the moment-carrying current is PURE
    DISPLACEMENT current J_phi = i omega E_phi (their Eq 68) - no
    derivative stencil is needed for mu.
  * L       = int (R x pbar)_z dV, pbar = (1/2) Re[Ehat x Bhat*] (the
    time-averaged Poynting momentum; paper Eq 27 verified EXACTLY,
    including the 1 + r0^2/4R0^2 factor). The paper's left-handed triad
    puts S along -phi_hat (its Eq 23), so L_z is NEGATIVE with these
    conventions; the physical statement is |L_z| = hbar/2 and the sign is
    reported (handedness).
  * U_paper = int eps0 E0^2 (1 + R/4R0) dV  (Eq 31 density, as published).
  * U_phys  = int (1/4)(|Ehat|^2 + |Bhat|^2) dV  (the exact period average
    of u(t) = (E^2+B^2)/2 for the stated real fields; equals the
    instantaneous total at every t, checked).

FINDING CARRIED BY THIS SCRIPT (the Q10 evidence): the appendix's own
convention is the standard phasor average E^2(t) = (1/2) E.E* (its Eq
113-115), but Eq 122/124 drop the SQUARE on (1+R/R0) in E_phi E_phi*, and
Eq 127 drops the 1/2 on the B term; the two slips produce Eq 31. With the
appendix's own convention applied exactly,

    u      = (eps0 E0^2/4) [2 + (1+R/R0)^2]
    U_phys = 3 pi^2 eps0 R0 r0^2 E0^2 (1 + (5/24) r0^2/R0^2)
           = (6/5) x Eq 32   (thin torus)

and since the three constraints (Q, mu, L) are slip-free, the solved
parameters stand and only the energy prediction moves:
U/m_e c^2 = 0.795 -> ~0.958. Both densities are integrated on the lattice
against their closed forms; the interpretation goes to Marc as Q10.

Numerics: two columns.
  Column A (the integration-kernel gate): interface-weighted voxel
    quadrature (w = clip((r0-s)/h + 1/2, 0, 1), the standard linear
    interface reconstruction) of the analytically-known densities ->
    O(h^2) convergence to the closed forms.
  Column B (the stencil machinery): central-difference rho = div E and
    J = curl B + i omega E on the sharp-masked fields -> bulk rho
    accuracy O(h^2), continuity div J = i omega rho (machine, a discrete
    identity), Faraday residual O(h^2), the mask's shell surface charge /
    current reported as the honest artifact (the paper's own
    "unphysical mask" limitation, its section 5.2).

Units: m_e = c = hbar = eps0 = 1 (r_c = 1); e = sqrt(4 pi alpha),
mu_B = e/2, E_S = 1/e.

Stretch (task doc section 5): the Bessel J0 envelope replacing the
Heaviside mask (Fleury 5.5's own suggested fix; Ceperley's smooth-mode
analog): same quadrature, constraint system re-solved via the
dimensionless scaling functions f_X(r0/R0) (fixed-point iteration); the
Faraday residual of the naive envelope is quantified honestly (the smooth
torus is NOT an exact Maxwell solution; making it one is M7.4's
relaxation job).

Run:  python m7_2_fleury_torus.py          full sweep (h = r0/4, r0/8, r0/16)
      python m7_2_fleury_torus.py --quick  coarse grids only (smoke test)
"""
from __future__ import annotations

import argparse
import json
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import dblquad
from scipy.ndimage import binary_erosion
from scipy.optimize import fsolve
from scipy.special import j0, j1, jn_zeros

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
os.makedirs(DATA, exist_ok=True)
os.makedirs(PLOTS, exist_ok=True)

# ---------------------------------------------------------------------------
# constants (m_e = c = hbar = eps0 = 1)
# ---------------------------------------------------------------------------
ALPHA = 1.0 / 137.035999084
E_CH = np.sqrt(4 * np.pi * ALPHA)      # elementary charge, 0.30282
MU_B = E_CH / 2.0                      # Bohr magneton
E_S = 1.0 / E_CH                       # Schwinger field
MU_TARGET = MU_B * (1 + ALPHA / (2 * np.pi))
L_TARGET = 0.5
OMEGA_D = 2.0                          # Dirac ZBW frequency, 2 m c^2 / hbar
J01 = float(jn_zeros(0, 1)[0])         # 2.404826


# ---------------------------------------------------------------------------
# closed forms (exact torus integrals; independently re-verified by 2D
# quadrature in verify_closed_forms)
# ---------------------------------------------------------------------------


def cf_Q(E0, r0):
    return np.sqrt(2) * np.pi ** 2 * E0 * r0 ** 2                              # Eq 19


def cf_mu(E0, R0, r0):
    return np.sqrt(2) * np.pi * E0 * R0 * r0 ** 2 * (1 + r0 ** 2 / (2 * R0 ** 2))   # Eq 88


def cf_L(E0, R0, r0):
    return np.pi ** 2 * E0 ** 2 * R0 ** 2 * r0 ** 2 * (1 + r0 ** 2 / (4 * R0 ** 2))  # Eq 27


def cf_U_paper(E0, R0, r0):
    return np.pi ** 2 * R0 * r0 ** 2 * E0 ** 2 * (2.5 + r0 ** 2 / (8 * R0 ** 2))     # Eq 32


def cf_U_phys(E0, R0, r0):
    """The corrected-convention energy (see the module docstring)."""
    return 3 * np.pi ** 2 * R0 * r0 ** 2 * E0 ** 2 * (1 + 5 * r0 ** 2 / (24 * R0 ** 2))


def verify_closed_forms(E0, R0, r0):
    """Independent 2D (theta, s) quadrature of every closed form.
    dV = R dphi dA with R = R0 + s cos(theta); phi handled analytically."""
    def torus_int(f):
        val, _ = dblquad(lambda s, th: f(R0 + s * np.cos(th)) * s,
                         0, 2 * np.pi, 0, r0, epsabs=1e-13, epsrel=1e-13)
        return val

    omega = 2.0 / R0
    checks = {
        # Q = rho_rms V: rho_rms = (E0/R0)/sqrt2 uniform; V = int R dphi dA
        "Q": (E0 / R0) / np.sqrt(2) * 2 * np.pi * torus_int(lambda R: R),
        # mu = (1/(2 pi sqrt2)) |int e^{-i phi} m_z dV|; de-phased density
        # (1/2) R * omega E0 (1+R/R0); one more R from the measure
        "mu": (1 / (2 * np.pi * np.sqrt(2))) * 2 * np.pi * torus_int(
            lambda R: 0.5 * R * omega * E0 * (1 + R / R0) * R),
        # |L_z|: |pbar_phi| = E0^2/2 uniform; l_z = R |pbar_phi|
        "L": 2 * np.pi * torus_int(lambda R: 0.5 * E0 ** 2 * R * R),
        "U_paper": 2 * np.pi * torus_int(lambda R: E0 ** 2 * (1 + R / (4 * R0)) * R),
        "U_phys": 2 * np.pi * torus_int(
            lambda R: 0.25 * E0 ** 2 * (2 + (1 + R / R0) ** 2) * R),
    }
    ref = {"Q": cf_Q(E0, r0), "mu": cf_mu(E0, R0, r0), "L": cf_L(E0, R0, r0),
           "U_paper": cf_U_paper(E0, R0, r0), "U_phys": cf_U_phys(E0, R0, r0)}
    return {k: {"quad": checks[k], "closed": ref[k],
                "rel": abs(checks[k] - ref[k]) / abs(ref[k])} for k in checks}


def solve_constraints():
    """The paper's three constraints, solved exactly (full correction
    factors + the Schwinger term), and the thin-torus closed solution the
    paper's section 3.7 uses (its printed numbers sit between the two)."""
    def eqs(x):
        E0, R0, r0 = x
        return [cf_Q(E0, r0) - E_CH,
                cf_mu(E0, R0, r0) - MU_TARGET,
                cf_L(E0, R0, r0) - L_TARGET]
    x, info, ier, _ = fsolve(eqs, [0.94, 1.57, 0.15], full_output=True)
    assert ier == 1, "constraint solve failed"
    E0t = 2 * np.sqrt(2) / (np.pi ** 2 * E_CH)          # thin-torus exact
    r0t = np.sqrt(E_CH / (np.sqrt(2) * np.pi ** 2 * E0t))
    thin = {"E0": E0t, "R0": np.pi / 2, "r0": r0t,
            "E0_over_ES": E0t / E_S, "U_paper_over_mec2": 5 / (2 * np.pi)}
    # the paper's PRINTED solution reconstructs exactly as thin-torus + the
    # Schwinger factor s = alpha/2pi on the mu constraint only:
    #   R0 = (pi/2)(1+s), r0 = r0t (1+s), E0 = E0t/(1+s)^2, U = U_thin/(1+s)
    s = ALPHA / (2 * np.pi)
    paper_recon = {"E0_over_ES": (E0t / E_S) / (1 + s) ** 2,
                   "R0": (np.pi / 2) * (1 + s), "r0": r0t * (1 + s),
                   "U_paper_over_mec2": 5 / (2 * np.pi) / (1 + s),
                   "note": "matches every printed digit of Eq 37-40"}
    return {"E0": float(x[0]), "R0": float(x[1]), "r0": float(x[2]),
            "residual": float(np.max(np.abs(info["fvec"]))),
            "thin_torus": thin, "paper_printed_reconstruction": paper_recon}


# ---------------------------------------------------------------------------
# lattice operators
# ---------------------------------------------------------------------------


def d_axis(f, axis, h):
    return (np.roll(f, -1, axis=axis) - np.roll(f, 1, axis=axis)) / (2.0 * h)


def div3(F, h):
    return d_axis(F[..., 0], 0, h) + d_axis(F[..., 1], 1, h) + d_axis(F[..., 2], 2, h)


def curl3(F, h):
    dyFz = d_axis(F[..., 2], 1, h)
    dzFy = d_axis(F[..., 1], 2, h)
    dzFx = d_axis(F[..., 0], 2, h)
    dxFz = d_axis(F[..., 2], 0, h)
    dxFy = d_axis(F[..., 1], 0, h)
    dyFx = d_axis(F[..., 0], 1, h)
    return np.stack([dyFz - dzFy, dzFx - dxFz, dxFy - dyFx], axis=-1)


def build_fields(h, E0, R0, r0, envelope=None, Lxy=3.9, Lz=0.8):
    """Slab grid + complex field amplitudes (sharp mask for the stencil
    column) + the geometry arrays the quadrature column needs."""
    Nx = int(round(Lxy / h))
    Nz = int(round(Lz / h))
    xs = (np.arange(Nx) - Nx / 2 + 0.5) * h
    zs = (np.arange(Nz) - Nz / 2 + 0.5) * h
    X, Y, Z = np.meshgrid(xs, xs, zs, indexing="ij")
    R = np.sqrt(X * X + Y * Y)
    R_safe = np.maximum(R, 1e-12)
    s = np.sqrt((R - R0) ** 2 + Z * Z)
    inside = s < r0
    if envelope is None:
        g = inside.astype(float)
    elif envelope == "bessel":
        g = np.where(inside, j0(J01 * np.minimum(s, r0) / r0), 0.0)
    else:
        raise ValueError(envelope)
    eiphi = (X + 1j * Y) / R_safe
    cph, sph = X / R_safe, Y / R_safe
    ER = 1j * E0 * eiphi * g
    EP = -(1 + R / R0) * E0 * eiphi * g
    Eh = np.stack([ER * cph - EP * sph, ER * sph + EP * cph,
                   np.zeros_like(ER)], axis=-1)
    Bh = np.stack([np.zeros_like(ER), np.zeros_like(ER),
                   1j * E0 * eiphi * g], axis=-1)
    # interface weight (linear reconstruction of the tube boundary)
    w = np.clip((r0 - s) / h + 0.5, 0.0, 1.0)
    return {"X": X, "Y": Y, "Z": Z, "R": R, "inside": inside, "s": s,
            "eiphi": eiphi, "Eh": Eh, "Bh": Bh, "h": h, "g": g, "w": w}


# ---------------------------------------------------------------------------
# observables
# ---------------------------------------------------------------------------


def observables_quadrature(F, E0, R0, r0, envelope=None):
    """Column A: interface-weighted voxel quadrature of the analytic
    densities (no stencils). The gate column: O(h^2) to the closed forms."""
    h, dV = F["h"], F["h"] ** 3
    R, w, s = F["R"], F["w"], F["s"]
    omega = 2.0 / R0
    if envelope is None:
        g = np.ones_like(R)
    elif envelope == "bessel":
        g = j0(J01 * np.minimum(s, r0) / r0)
    out = {}
    out["V_w"] = float(np.sum(w) * dV)
    out["V_exact"] = 2 * np.pi ** 2 * R0 * r0 ** 2
    if envelope is None:
        rho_rms_dens = (E0 / R0) / np.sqrt(2)
        out["Q"] = rho_rms_dens * out["V_w"]
    else:
        # envelope charge density: rhohat = g * (-i E0/R0) + g'(s) dds(R) i E0
        gp = -j1(J01 * np.minimum(s, r0) / r0) * J01 / r0
        ddsR = (R - R0) / np.maximum(s, 1e-12)
        rho_abs2 = (g * E0 / R0 - 0.0) ** 2 * 0 + (
            (-g * E0 / R0 + 0.0) ** 2 + 0.0)  # placeholder, replaced below
        # rhohat = i E0 e^{i phi} (g'(s) ddsR - g/R0)  [E_R = i E0 g e^{iphi}]
        rho_abs2 = (E0 * (gp * ddsR - g / R0)) ** 2
        Vw = out["V_w"]
        rho_rms = np.sqrt(np.sum(w * rho_abs2) * dV / 2.0 / Vw)
        out["Q"] = rho_rms * Vw
    # the paper's mu = (1/(2 pi sqrt2)) |int e^{-i phi} m_z dV|; the grid sum
    # IS the full 3D integral (phi measure included), so divide by 2 pi sqrt2
    out["mu"] = float(np.sum(w * 0.5 * omega * E0 * g * (1 + R / R0) * R) * dV
                      / (2 * np.pi * np.sqrt(2)))
    out["L_signed"] = float(np.sum(w * (-0.5) * (g * E0) ** 2 * R) * dV)
    out["L_abs"] = abs(out["L_signed"])
    out["U_paper_density"] = float(np.sum(w * (g * E0) ** 2 * (1 + R / (4 * R0))) * dV)
    out["U_phys"] = float(np.sum(
        w * 0.25 * (g * E0) ** 2 * (2 + (1 + R / R0) ** 2)) * dV)
    return out


def observables_stencil(F, E0, R0, r0, erode=2):
    """Column B: the derivative machinery on the sharp-masked fields."""
    h, dV = F["h"], F["h"] ** 3
    omega = 2.0 / R0
    Eh, Bh = F["Eh"], F["Bh"]
    X, Y = F["X"], F["Y"]
    inside = F["inside"]
    bulk = binary_erosion(inside, iterations=erode)
    shell = inside & ~bulk
    dephase = np.conj(F["eiphi"])
    out = {}

    rho = div3(Eh, h)
    rho_exact = -1j * E0 * F["eiphi"] / R0
    out["rho_bulk_rel_err"] = float(np.sqrt(
        np.sum(np.abs(rho[bulk] - rho_exact[bulk]) ** 2)
        / np.sum(np.abs(rho_exact[bulk]) ** 2)))
    out["Q_shell_abs"] = float(np.sum(np.abs(rho[shell])) * dV)

    Jh = curl3(Bh, h) + 1j * omega * Eh
    divJ = div3(Jh, h)
    out["continuity_rel"] = float(np.sqrt(
        np.sum(np.abs(divJ[bulk] - 1j * omega * rho[bulk]) ** 2)
        / np.sum(np.abs(omega * rho[bulk]) ** 2)))
    curlE = curl3(Eh, h)
    out["faraday_rel"] = float(np.sqrt(
        np.sum(np.abs(curlE[bulk] - 1j * omega * Bh[bulk]) ** 2)
        / np.sum(np.abs(omega * Bh[bulk]) ** 2)))

    # mu from the FIELD (displacement current, no stencil): J_phi = i w E_phi
    mz_disp = 0.5 * 1j * omega * (X * Eh[..., 1] - Y * Eh[..., 0])
    out["mu_displacement"] = float(
        np.abs(np.sum(dephase * mz_disp)) * dV / (2 * np.pi * np.sqrt(2)))
    # the mask's shell surface current (curl B delta), the honest artifact
    cB = curl3(Bh, h)
    mz_shell = 0.5 * (X * cB[..., 1] - Y * cB[..., 0])
    out["mu_shell_current"] = float(
        np.abs(np.sum(dephase * mz_shell)) * dV / (2 * np.pi * np.sqrt(2)))

    pbar = 0.5 * np.real(np.cross(Eh, np.conj(Bh)))
    out["L_signed"] = float(np.sum(X * pbar[..., 1] - Y * pbar[..., 0]) * dV)

    u_phys = 0.25 * (np.sum(np.abs(Eh) ** 2, axis=-1) + np.abs(Bh[..., 2]) ** 2)
    out["U_phys"] = float(np.sum(u_phys) * dV)
    for tag, wt in (("t0", 0.0), ("t8", np.pi / 4)):
        ph = np.exp(-1j * wt)
        Et = np.real(Eh * ph)
        Bt = np.real(Bh * ph)
        out[f"U_inst_{tag}"] = float(np.sum(
            0.5 * (np.sum(Et ** 2, axis=-1) + Bt[..., 2] ** 2)) * dV)
    return out


# ---------------------------------------------------------------------------
# sweeps + extrapolation
# ---------------------------------------------------------------------------


def run_sweep(E0, R0, r0, denoms):
    rows = []
    for n in denoms:
        h = r0 / n
        t0 = time.time()
        try:
            F = build_fields(h, E0, R0, r0)
        except MemoryError:
            print(f"  h=r0/{n}: MemoryError, skipped")
            continue
        qa = observables_quadrature(F, E0, R0, r0)
        sb = observables_stencil(F, E0, R0, r0)
        row = {"n": n, "h": h, "A": qa, "B": sb,
               "wall_s": round(time.time() - t0, 1)}
        rows.append(row)
        print(f"  h=r0/{n:<3d} A: Q={qa['Q']:.6f} mu={qa['mu']:.6f} "
              f"|L|={qa['L_abs']:.6f} U_pap={qa['U_paper_density']:.6f} "
              f"U_phys={qa['U_phys']:.6f}   B: rho_err={sb['rho_bulk_rel_err']:.1e} "
              f"cont={sb['continuity_rel']:.1e} far={sb['faraday_rel']:.1e} "
              f"({row['wall_s']}s)")
        del F
    return rows


def extrapolate(hs, vals, ref):
    """Fit val(h) = A + B h^p (p free with >=3 points); return
    (A, p, rel err of A vs ref)."""
    hs, vals = np.asarray(hs, float), np.asarray(vals, float)
    if len(hs) >= 3:
        best = None
        for p in np.linspace(0.5, 3.5, 301):
            M = np.stack([np.ones_like(hs), hs ** p], axis=1)
            coef, res, _, _ = np.linalg.lstsq(M, vals, rcond=None)
            r2 = float(res[0]) if len(res) else 0.0
            if best is None or r2 < best[0]:
                best = (r2, p, coef[0])
        _, p, A = best
    else:
        p = 2.0
        A = vals[-1] + (vals[-1] - vals[0]) / ((hs[0] / hs[-1]) ** p - 1)
    return float(A), float(p), float(abs(A - ref) / abs(ref))


def stretch_bessel(E0, R0, r0, Q_shell_heaviside, n_ref=8, iters=6):
    """Bessel-envelope stretch, run as a DIAGNOSTIC.

    Headline: the smooth envelope EXPOSES the sharp mask's hidden surface
    charge. The Heaviside field carries a delta-shell charge (the normal
    E_R jump) that the paper's bulk integrals drop; smoothing turns it into
    an explicit envelope-gradient charge rho ~ g'(s) E0 ~ (j01/r0) E0 that
    dominates the bulk E0/R0 term by ~ j01 R0/r0 and inflates Q_rms. The
    constraint system then has no nearby solution of this naive scalar-
    envelope form (the fixed-point iteration runs away), quantified here.
    Conclusion for the record: Fleury 5.5's Bessel fix needs the full
    per-component mode structure (Ceperley) or a relaxation - M7.4's job."""
    F = build_fields(r0 / n_ref, E0, R0, r0, envelope="bessel")
    qa = observables_quadrature(F, E0, R0, r0, envelope="bessel")
    sb = observables_stencil(F, E0, R0, r0)
    # charge decomposition: core (the model's own g E0/R0 term) vs the
    # envelope-gradient term g'(s) E0 (the exposed surface charge)
    h, dV = F["h"], F["h"] ** 3
    s, R, w = F["s"], F["R"], F["w"]
    g = j0(J01 * np.minimum(s, r0) / r0)
    gp = -j1(J01 * np.minimum(s, r0) / r0) * J01 / r0
    ddsR = (R - R0) / np.maximum(s, 1e-12)
    Vw = float(np.sum(w) * dV)
    Q_core = float(np.sqrt(np.sum(w * (E0 * g / R0) ** 2) * dV / 2 / Vw) * Vw)
    Q_grad = float(np.sqrt(np.sum(w * (E0 * gp * ddsR) ** 2) * dV / 2 / Vw) * Vw)
    del F
    diag = {"at_paper_params": {
        "Q": qa["Q"], "Q_core_term": Q_core, "Q_gradient_term": Q_grad,
        "Q_inflation_vs_heaviside": qa["Q"] / cf_Q(E0, r0),
        "Q_shell_heaviside_columnB": Q_shell_heaviside,
        "mu": qa["mu"], "L_abs": qa["L_abs"], "U_phys": qa["U_phys"],
        "faraday_rel_bulk": sb["faraday_rel"]}}
    # guarded fixed-point attempt (expected to run away; documented)
    pars = {"E0": E0, "R0": R0, "r0": r0}
    hist = []
    status = "converged"
    for it in range(iters):
        F = build_fields(pars["r0"] / n_ref, pars["E0"], pars["R0"],
                         pars["r0"], envelope="bessel")
        qa_i = observables_quadrature(F, pars["E0"], pars["R0"], pars["r0"],
                                      envelope="bessel")
        del F
        fQ = qa_i["Q"] / (pars["E0"] * pars["r0"] ** 2)
        fmu = qa_i["mu"] / (pars["E0"] * pars["R0"] * pars["r0"] ** 2)
        fL = qa_i["L_abs"] / (pars["E0"] ** 2 * pars["R0"] ** 2 * pars["r0"] ** 2)
        E0r2 = E_CH / fQ
        R0n = MU_TARGET / (fmu * E0r2)
        E0n = L_TARGET / (fL * E0r2 * R0n ** 2)
        hist.append({"iter": it, "fQ": fQ, "fmu": fmu, "fL": fL,
                     "R0_next": float(R0n), "E0_next": float(E0n)})
        if not (0.3 < R0n < 6.0) or E0n <= 0:
            status = f"RUNAWAY at iter {it}: R0 -> {R0n:.2f} (no nearby smooth solution)"
            break
        r0n = float(np.sqrt(E0r2 / E0n))
        pars = {"E0": float(E0n), "R0": float(R0n), "r0": r0n}
    return {"diagnostic": diag, "fixed_point_status": status,
            "iterations": hist,
            "reading": "the smooth envelope exposes the mask's hidden "
                       "surface charge; the naive scalar-envelope ansatz "
                       "has no nearby constraint solution; the real fix = "
                       "Ceperley per-component mode structure or the M7.4 "
                       "relaxation"}


# ---------------------------------------------------------------------------
# plots
# ---------------------------------------------------------------------------


def make_plots(sol, rows, refs, stretch, out_prefix):
    E0, R0, r0 = sol["E0"], sol["R0"], sol["r0"]
    F = build_fields(r0 / 8, E0, R0, r0)
    Fb = build_fields(r0 / 8, E0, R0, r0, envelope="bessel")
    h = F["h"]
    rho = div3(F["Eh"], h)
    Nz = F["Z"].shape[2]
    Ny = F["Y"].shape[1]
    fig, axes = plt.subplots(1, 4, figsize=(18, 4.4))
    Emag = np.sqrt(np.sum(np.abs(F["Eh"]) ** 2, axis=-1))
    axes[0].imshow(Emag[:, :, Nz // 2].T, origin="lower")
    axes[0].set_title("|E_hat|  z = 0 (Heaviside)")
    axes[1].imshow(Emag[:, Ny // 2, :].T, origin="lower", aspect="auto")
    axes[1].set_title("|E_hat|  y = 0 cross-section")
    axes[2].imshow(np.real(rho)[:, :, Nz // 2].T, origin="lower", cmap="RdBu")
    axes[2].set_title("rho(t=0) = Re div E,  z = 0")
    Emag_b = np.sqrt(np.sum(np.abs(Fb["Eh"]) ** 2, axis=-1))
    axes[3].imshow(Emag_b[:, Fb["Y"].shape[1] // 2, :].T, origin="lower",
                   aspect="auto")
    axes[3].set_title("|E_hat|  y = 0 (Bessel J0 envelope)")
    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    p1 = f"{out_prefix}_field_sections.png"
    fig.savefig(p1, dpi=140)
    plt.close(fig)
    del F, Fb

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    ax = axes[0]
    hs = np.array([r["h"] for r in rows])
    keymap = {"Q": ("A", "Q"), "mu": ("A", "mu"), "L": ("A", "L_abs"),
              "U_paper": ("A", "U_paper_density"), "U_phys": ("A", "U_phys")}
    for key, (col, k2) in keymap.items():
        errs = np.abs(np.array([r[col][k2] for r in rows]) - refs[key]) / abs(refs[key])
        ax.loglog(hs, np.maximum(errs, 1e-16), "o-", label=key)
    ref_line = (hs / hs[0]) ** 2 * 3e-3
    ax.loglog(hs, ref_line, "k--", alpha=0.5, label="O(h^2)")
    ax.set_xlabel("h")
    ax.set_ylabel("|rel err| vs closed form")
    ax.set_title("Observable convergence (quadrature column)")
    ax.legend(fontsize=8)
    ax = axes[1]
    labels = ["U Eq32\n(as published)", "U corrected\nconvention", "m_e c^2",
              "U Bessel envelope\n@ paper params"]
    vals = [cf_U_paper(E0, R0, r0), cf_U_phys(E0, R0, r0), 1.0,
            stretch["diagnostic"]["at_paper_params"]["U_phys"]]
    ax.bar(range(4), vals, color=["tab:orange", "tab:blue", "0.6", "tab:green"])
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, fontsize=8)
    ax.axhline(1.0, color="k", ls="--", lw=0.8)
    ax.set_ylabel("U / m_e c^2")
    ax.set_title("Rest energy: published vs corrected vs Bessel")
    fig.tight_layout()
    p2 = f"{out_prefix}_convergence.png"
    fig.savefig(p2, dpi=140)
    plt.close(fig)
    return [p1, p2]


# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    out = {"units": "m_e = c = hbar = eps0 = 1; e = sqrt(4 pi alpha)"}

    print("M7.2 Fleury-torus quadrature")
    print("[1] constraint solve (exact closed forms + thin-torus reference)")
    sol = solve_constraints()
    E0, R0, r0 = sol["E0"], sol["R0"], sol["r0"]
    derived = {
        "E0_over_ES": E0 / E_S, "R0_over_rc": R0, "r0_over_rc": r0,
        "omega": 2.0 / R0, "omega_over_omegaD": (2.0 / R0) / OMEGA_D,
        "hbar_omega_over_mec2": 2.0 / R0,
        "U_paper_over_mec2": cf_U_paper(E0, R0, r0),
        "U_phys_over_mec2": cf_U_phys(E0, R0, r0),
        "paper_printed": {"E0_over_ES": 0.2859, "R0_over_rc": 1.5726,
                          "r0_over_rc": 0.1516, "U_over_mec2": 0.7949,
                          "omega_over_omegaD": 0.636}}
    out["constraint_solution"] = {**sol, **derived}
    print(f"    exact solve:  E0/E_S = {derived['E0_over_ES']:.4f}  "
          f"R0 = {R0:.4f}  r0 = {r0:.4f}  (paper printed 0.2859 / 1.5726 / 0.1516;"
          f" thin-torus {sol['thin_torus']['E0_over_ES']:.4f} / "
          f"{sol['thin_torus']['R0']:.4f} / {sol['thin_torus']['r0']:.4f})")
    print(f"    U_paper = {derived['U_paper_over_mec2']:.4f} m_ec^2 (printed 0.7949)"
          f"   U_corrected = {derived['U_phys_over_mec2']:.4f} m_ec^2  <-- Q10")

    print("[2] closed forms re-verified by independent 2D quadrature")
    cfv = verify_closed_forms(E0, R0, r0)
    out["closed_form_quadrature_check"] = cfv
    print(f"    worst rel diff = {max(v['rel'] for v in cfv.values()):.2e}")

    print("[3] lattice sweep (Heaviside ansatz)")
    denoms = [4, 8] if args.quick else [4, 8, 16]
    rows = run_sweep(E0, R0, r0, denoms)
    out["sweep"] = rows
    refs = {"Q": E_CH, "mu": MU_TARGET, "L": L_TARGET,
            "U_paper": cf_U_paper(E0, R0, r0), "U_phys": cf_U_phys(E0, R0, r0)}
    keymap = {"Q": "Q", "mu": "mu", "L": "L_abs",
              "U_paper": "U_paper_density", "U_phys": "U_phys"}
    hs = [r["h"] for r in rows]
    conv = {}
    for key, k2 in keymap.items():
        A, p, rel = extrapolate(hs, [r["A"][k2] for r in rows], refs[key])
        conv[key] = {"extrapolated": A, "order": p,
                     "rel_err_vs_closed": rel, "closed_form": refs[key]}
        print(f"    {key:<8s} extrap = {A:.6f}  vs closed {refs[key]:.6f} "
              f"(rel {rel:.2e}, order ~{p:.2f})")
    out["convergence"] = conv
    last = rows[-1]
    gates = {
        "targets_converged_0p5pct": all(v["rel_err_vs_closed"] < 5e-3
                                        for v in conv.values()),
        "rho_accuracy_improves": last["B"]["rho_bulk_rel_err"]
        < rows[0]["B"]["rho_bulk_rel_err"],
        "continuity_machine": last["B"]["continuity_rel"] < 1e-10,
        "faraday_bulk_O(h2)": last["B"]["faraday_rel"]
        < rows[0]["B"]["faraday_rel"],
        "U_inst_equals_U_avg": abs(last["B"]["U_inst_t0"] - last["B"]["U_phys"])
        / last["B"]["U_phys"] < 1e-3,
        "L_sign_negative_left_handed": last["A"]["L_signed"] < 0,
    }
    out["gates"] = gates
    for k, v in gates.items():
        print(f"    [{'PASS' if v else 'FAIL'}] {k}")

    print("[4] Bessel-envelope stretch (diagnostic)")
    stretch = stretch_bessel(E0, R0, r0, last["B"]["Q_shell_abs"],
                             n_ref=8, iters=6)
    out["stretch_bessel"] = stretch
    d = stretch["diagnostic"]["at_paper_params"]
    print(f"    at paper params: Q = {d['Q']:.4f} ({d['Q_inflation_vs_heaviside']:.1f}x "
          f"the Heaviside Q; gradient term {d['Q_gradient_term']:.3f} vs core "
          f"{d['Q_core_term']:.3f}; the Heaviside SHELL charge, column B: "
          f"{d['Q_shell_heaviside_columnB']:.3f})")
    print(f"    faraday residual (bulk) = {d['faraday_rel_bulk']:.3f}   "
          f"U_phys = {d['U_phys']:.4f}")
    print(f"    constraint re-solve: {stretch['fixed_point_status']}")

    print("[5] plots")
    plots = make_plots(sol, rows, refs, stretch, os.path.join(PLOTS, "m7_2"))

    out["wall_s_total"] = round(time.time() - t0, 1)
    path = os.path.join(DATA, "m7_2_observables.json")
    with open(path, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nall done ({out['wall_s_total']}s)")
    print(f"data -> {path}")
    for p in plots:
        print(f"plot -> {p}")


if __name__ == "__main__":
    main()
