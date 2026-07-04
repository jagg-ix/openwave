"""M5.17: THE M5 STATIC ENERGY FUNCTIONAL, in one auditable module.

This module IS the physics of the M5 static (electron-sector) program: every
term of the minimized energy, the potential, and the analytic anchors live
here and nowhere else. Drivers (m5_16_axisym.py, m5_17_two_charge.py) import
these functions; they never re-implement physics. The methods note
(../findings/m5_17_methods_note.md) carries the same equations with the
equation-to-code map pointing at the line numbers of THIS file.

CONVENTION (Duda index-0)
    M is the 4x4 real symmetric order-parameter field,
        M = O . D . O^T,   D = diag(g, 1, delta, 0),
    time/g axis = array index 0, spatial block = indices 1..3,
    eta = diag(-1, 1, 1, 1). The static functional below acts on the spatial
    block for the potential; statics are measured EXACTLY g-blind (M5.16 gate
    G8), so the frozen g value is a spectator here.

THE ENERGY FUNCTIONAL (the "integral of the Hamiltonian" being minimized)
    E[M] = INT d^3x  { u_curv(x) + [ V(M_sp(x)) - V_vac ] }

    curvature (kinetic/gradient) density, the tensor-commutator form:
        u_curv = c2 . 4 . SUM_{mu<nu} || [d_mu M, d_nu M] ||_F^2 ,
        mu, nu in {x, y, z},  [A,B] = AB - BA,  ||.||_F = Frobenius norm.
      -> code: curvature_density_np()

    potential, quartic trace Landau-de Gennes on the spatial block M_sp:
        V(M_sp) = a Tr(M_sp^2) - b Tr(M_sp^3) + c (Tr M_sp^2)^2 ,
      measured relative to its uniaxial-vacuum value V_vac = V(diag(1,0,0))
      = a - b + c, so the vacuum has zero energy density.
      -> code: potential_density_np(), ldg_coeffs()

VACUUM STRUCTURE (fixes a; the zero-forcing anchor)
    Requiring V stationary at the uniaxial vacuum spectrum (1, 0, 0):
        dV/ds|_{s=1} = 0  =>  a = (3b - 4c) / 2 ,
    with melt cost  V(0) - V(1) = c - b/2 > 0  =>  beta = b/c in (0, 2).
    b > 0 is required for shape selection; the one free shape ratio
    beta = b/c survives the electron sector (M5.16: r_half is beta-flat).
    The delta-axis stiffness (the cubic alone restores the delta eigenvalue):
        kappa_delta = (3/2) b .
    -> code: ldg_coeffs()

AXISYMMETRIC REDUCTION (Duda's cylindrical symmetry, exact)
    Equivariant ansatz  M(rho, phi, z) = R12(phi) . Mt(rho, z) . R12(phi)^T,
    R12 = rotation in the spatial (1,2) plane. At phi = 0 the three
    derivative channels are
        M_x = d_rho Mt,   M_y = (1/rho) [J, Mt],   M_z = d_z Mt,
    J = dR12/dphi|_0 (J[1,2] = -1, J[2,1] = +1), and the 3D integral reduces
    exactly to the (rho, z) half-plane with volume weight 2 pi rho drho dz.
    Axis handling: cell-centered rho grid (rho_i = (i + 1/2) h) + mirror
    ghost  Mt(-rho, z) = P . Mt(rho, z) . P,  P = diag(1, -1, -1, 1)
    (the phi = pi image), so the axis carries no one-sided bias.
    -> code: curvature_density_np() (the Mphi channel + the i=0 ghost row)

ANALYTIC GRADIENT (the production minimizer engine; no autodiff on the path)
    For C = [A, B] with A, B symmetric:
        d||C||_F^2 / dA = 2 [C, B],    d||C||_F^2 / dB = -2 [C, A] ;
    the azimuthal channel A_phi = [J, Mt]/rho has adjoint -[J, G]/rho
    (J antisymmetric); the i=0 ghost folds its gradient back through the
    mirror signs; the potential contributes
        dV/dM_sp = 2a M_sp - 3b M_sp^2 + 4c Tr(M_sp^2) M_sp .
    Validated against central finite differences to ~3e-7 (M5.16 gate G2).
    -> code: energy_gradient_np()

ANALYTIC ANCHORS (closed forms the gates check against)
    Pure director hedgehog M_sp = rhat rhat^T (s = 1): the curvature density
    is exactly  u_curv = 8 c2 / r^4  (gate G3), and a spherical shell
    integrates to  32 pi c2 (1/r1 - 1/r2)  (gate G4). Matching the exterior
    tail to the classical EM self-energy  alpha hbar c / (2 r)  gives the
    Coulomb lock  c2 = alpha hbar c / (64 pi)  (M5.16; the M5.17 two-charge
    run cross-checks this against Duda's interaction-energy prescription).
    -> code: ext_tail() (the exact exterior quadrature)

SEEDS
    Melted hedgehog  M_sp = s(r) n n^T,  n = rhat,
    s(r) = 1 - exp(-(r/r_c)^2)  (s ~ r^2 near 0 keeps M smooth at the
    origin);  r_c <= 0 means s = 1 (pure director, for the analytic gates).
    -> code: hedgehog_field() (axisym phi=0 slice), hedgehog_3d() (full 3D)

Provenance: extracted VERBATIM from m5_16_axisym.py (M5.16, gates G1-G8 all
green 2026-07-02) as M5.17 phase A; the M5.16 gate suite re-ran green on this
refactored stack with bit-identical energies (m5_17_task_details.md).
"""
from __future__ import annotations

import numpy as np

PI = np.pi
G_TIME = 8.0                      # frozen background; G8 proves decoupling at 1e10
MIR = np.outer([1.0, -1.0, -1.0, 1.0], [1.0, -1.0, -1.0, 1.0])  # axis mirror signs
MIR_T = tuple(tuple(float(x) for x in row) for row in MIR)

J4 = np.zeros((4, 4))
J4[1, 2] = -1.0
J4[2, 1] = 1.0


def ldg_coeffs(beta, cscale):
    """(a, b, c, vvac) from the zero-forcing vacuum conditions:
    stationary at s=1 => a = (3b-4c)/2; melt cost = c - b/2 > 0 needs beta < 2."""
    c = cscale
    b = beta * cscale
    a = 0.5 * (3.0 * b - 4.0 * c)
    vvac = a - b + c              # V at the s=1 uniaxial vacuum (negative)
    return a, b, c, vvac


def _comm_np(A, B):
    return np.einsum("...ab,...bc->...ac", A, B) - np.einsum("...ab,...bc->...ac", B, A)


def _norm2_np(A):
    return np.sum(A * A, axis=(-2, -1))


def curvature_density_np(Mnp, h, c2=1.0):
    """density on included cells (i in [0,NR-2], j in [1,NZ-2]); mirrors the kernel."""
    nr, nz = Mnp.shape[:2]
    Mminus = np.empty_like(Mnp[: nr - 1])
    Mminus[1:] = Mnp[: nr - 2]
    Mminus[0] = MIR * Mnp[0]
    Mrho = (Mnp[1:] - Mminus) / (2.0 * h)            # i = 0..nr-2, all j
    Mz = (Mnp[: nr - 1, 2:] - Mnp[: nr - 1, :-2]) / (2.0 * h)   # j = 1..nz-2
    Mc = Mnp[: nr - 1, 1:-1]
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Mphi = _comm_np(np.broadcast_to(J4, Mc.shape), Mc) / rho
    Mrho = Mrho[:, 1:-1]
    cxy = _comm_np(Mrho, Mphi)
    cxz = _comm_np(Mrho, Mz)
    cyz = _comm_np(Mphi, Mz)
    return c2 * 4.0 * (_norm2_np(cxy) + _norm2_np(cxz) + _norm2_np(cyz))


def potential_density_np(Mnp, a, b, c, vvac):
    msp = Mnp[: Mnp.shape[0] - 1, 1:-1, 1:4, 1:4]
    m2 = np.einsum("...ab,...bc->...ac", msp, msp)
    tr2 = np.einsum("...aa->...", m2)
    tr3 = np.einsum("...aa->...", np.einsum("...ab,...bc->...ac", m2, msp))
    return a * tr2 - b * tr3 + c * tr2 * tr2 - vvac


def cell_weights(nr, nz, h):
    """2 pi rho h^2 on included cells."""
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None]
    return np.broadcast_to(2.0 * PI * rho * h * h, (nr - 1, nz - 2)).copy()


def energy_gradient_np(Mnp, a, b, c, c2, h, vvac):
    """ANALYTIC gradient of total_energy_np, independent of Taichi AD (gate G2
    validates vs finite differences, G2b vs the AD gradient when available).
    Derivation (checkpoint notes): for C = [A, B] (A, B symmetric),
        d||C||^2/dA = 2 [C, B],   d||C||^2/dB = -2 [C, A],
    the azimuthal channel A_phi = [J, M]/rho has adjoint -[J, G]/rho (J
    antisymmetric), and the i=0 ghost A_rho(0) = (M[1] - MIR*M[0])/2h folds
    its gradient back through the mirror signs."""
    nr, nz = Mnp.shape[:2]
    inv2h = 1.0 / (2.0 * h)
    Mminus = np.empty_like(Mnp[: nr - 1])
    Mminus[1:] = Mnp[: nr - 2]
    Mminus[0] = MIR * Mnp[0]
    Arho = (Mnp[1:] - Mminus)[:, 1:-1] * inv2h          # (nr-1, nz-2, 4, 4)
    Az = (Mnp[: nr - 1, 2:] - Mnp[: nr - 1, :-2]) * inv2h
    Mc = Mnp[: nr - 1, 1:-1]
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Jb = np.broadcast_to(J4, Mc.shape)
    Aphi = _comm_np(Jb, Mc) / rho
    C1 = _comm_np(Arho, Aphi)
    C2 = _comm_np(Arho, Az)
    C3 = _comm_np(Aphi, Az)
    w = cell_weights(nr, nz, h)[..., None, None]
    k = 4.0 * c2 * w
    Grho = 2.0 * k * (_comm_np(C1, Aphi) + _comm_np(C2, Az))
    Gphi = 2.0 * k * (-_comm_np(C1, Arho) + _comm_np(C3, Az))
    Gz = 2.0 * k * (-_comm_np(C2, Arho) - _comm_np(C3, Aphi))
    G = np.zeros_like(Mnp)
    # scatter A_rho = (M[i+1] - M[i-1 or ghost])/2h
    G[1:, 1:-1] += Grho * inv2h
    G[: nr - 3 + 1, 1:-1] -= Grho[1:] * inv2h
    G[0, 1:-1] -= (MIR * Grho[0]) * inv2h               # ghost fold-back
    # scatter A_z = (M[., j+1] - M[., j-1])/2h
    G[: nr - 1, 2:] += Gz * inv2h
    G[: nr - 1, :-2] -= Gz * inv2h
    # local A_phi adjoint
    Gphi_r = Gphi / rho
    G[: nr - 1, 1:-1] += -_comm_np(np.broadcast_to(J4, Gphi_r.shape), Gphi_r)
    # potential dV/dM on the spatial block, weighted
    msp = Mc[..., 1:4, 1:4]
    m2 = np.einsum("...ab,...bc->...ac", msp, msp)
    tr2 = np.einsum("...aa->...", m2)[..., None, None]
    dsp = 2.0 * a * msp - 3.0 * b * m2 + 4.0 * c * tr2 * msp
    G[: nr - 1, 1:-1, 1:4, 1:4] += dsp * w
    return G


def total_energy_np(Mnp, a, b, c, c2, h, vvac):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return float(np.sum((curvature_density_np(Mnp, h, c2)
                         + potential_density_np(Mnp, a, b, c, vvac)) * w))


def ext_tail(Rc, Hh):
    """integral of the vacuum-hedgehog curvature density 8/r^4 OUTSIDE the
    cylinder (radius Rc, half-height Hh), exact 1D quadrature in theta:
    E_out = int dtheta 2 pi sin(theta) . 8 / r_b(theta),
    r_b = min(Rc/sin, Hh/|cos|)."""
    th = np.linspace(1e-9, PI - 1e-9, 40001)
    rb = np.minimum(Rc / np.sin(th), Hh / np.abs(np.cos(th)))
    return float(np.trapezoid(2.0 * PI * np.sin(th) * 8.0 / rb, th))


# ---------------- seeds ----------------
def grid_coords(nr, nz, h):
    rho = (np.arange(nr) + 0.5) * h
    z = (np.arange(nz) - nz / 2 + 0.5) * h
    return np.meshgrid(rho, z, indexing="ij")


def hedgehog_field(R, Z, r_c, g_time=G_TIME):
    """melted hedgehog at phi=0: M_sp = s(r) n n^T, n = (rho, 0, z)/r,
    s = 1 - exp(-(r/r_c)^2) (s ~ r^2 near 0 keeps M smooth at the origin);
    r_c <= 0 means s = 1 (pure director, for the analytic gates)."""
    r = np.sqrt(R ** 2 + Z ** 2)
    r = np.where(r < 1e-12, 1e-12, r)
    n1 = R / r
    n3 = Z / r
    s = np.ones_like(r) if r_c <= 0 else 1.0 - np.exp(-((r / r_c) ** 2))
    Mnp = np.zeros(R.shape + (4, 4))
    Mnp[..., 1, 1] = s * n1 * n1
    Mnp[..., 1, 3] = s * n1 * n3
    Mnp[..., 3, 1] = s * n1 * n3
    Mnp[..., 3, 3] = s * n3 * n3
    Mnp[..., 0, 0] = g_time
    return Mnp


def hedgehog_3d(X, Y, Z, r_c, g_time=G_TIME):
    r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)
    r = np.where(r < 1e-12, 1e-12, r)
    n = np.stack([X / r, Y / r, Z / r], axis=-1)
    s = np.ones_like(r) if r_c <= 0 else 1.0 - np.exp(-((r / r_c) ** 2))
    Mnp = np.zeros(X.shape + (4, 4))
    Mnp[..., 1:4, 1:4] = s[..., None, None] * n[..., :, None] * n[..., None, :]
    Mnp[..., 0, 0] = g_time
    return Mnp
