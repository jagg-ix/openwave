"""M7.8 - the helicity-pair 3:1 test (Fleury closure, amplitude-ratio ladder).

Task doc: research/tasks/m7_8_helicity_pair.md. Modes:

  python m7_8_helicity_pair.py seed      build the pair seed + seed-level gates
                                         (projector calibration, H_A sign, div identity)
  python m7_8_helicity_pair.py smoke     N=48 one rung (sqrt3), 500 iterations
  python m7_8_helicity_pair.py run       N=64 record: the 5-rung amplitude-ratio ladder
  python m7_8_helicity_pair.py grid      N=96 grid check of the sqrt3 rung
  python m7_8_helicity_pair.py analyze   plots + tables from the saved json

THE SEED (closure notes, Part A; lattice units lam0 = omega = 1, sigma = 2, w = 4):

  angles: phi = POLOIDAL, theta = TOROIDAL (the notes' convention);
  lattice: theta = atan2(y, x); d = sqrt((rho-R0)^2 + z^2); phi = atan2(z, rho-R0)

  LG radial profile (exact under lam0*sigma = 2, w = lam0*sigma^2):
      Psi(d) = (d/sigma) exp(-d^2/2 sigma^2)

  CK components per mode (m, n, s), F -> Psi, k = n/R0, alpha^2 = lam0^2 - k^2,
  chi = m*phi + n*theta - omega*t   (REPAIR #1: A_r != 0 kept):
      A_r     = -[ (m/d)Psi + (k/(s lam0)) Psi' ] sin chi
      A_phi   = -[ Psi' + (m k/(s lam0 d)) Psi ] cos chi
      A_theta = (s alpha^2 / lam0) Psi cos chi

  THE PAIR (REPAIR #2: the curl-eigenvalue sign s flips WITH the winding):
      mode(+): (m,n,s) = (1,+1,+1), amplitude a_plus
      mode(-): (m,n,s) = (1,-1,-1), amplitude a_minus
  ladder: a_plus/a_minus in {1.2, 1.5, sqrt3, 2.0, 2.5} at common Q_can = 13.2017.

  Harmonic doublet split of chi - omega*t:
      cos-carrying terms: a_c ~ cos chi, a_s ~ sin chi
      sin-carrying terms: a_c ~ sin chi, a_s ~ -cos chi

THE MEASUREMENT (pinned in the task doc par. 4c):

  U+/U- by the helical (Waleffe) k-space decomposition of the complex doublet
  CA = a_c + i a_s: project onto the eigenvectors of the DISCRETE curl
  (central differences diagonalize on kappa_l = sin(k_l h)/h; curl -> i kappa x),
  per-sector period-averaged quadratic energy
      U_s = (1/4) sum_k (omega^2 + |kappa|^2) |CA_s(k)|^2 h^3 / N^3
  with the curl-null bucket (kappa = 0) reported as U_0. Parseval gate:
  U_plus + U_minus + U_0 == the real-space A-sector quad energy to ~1e-10.

  The in-model spin target (Q15 directive S_z = hbar/2 under P2 U = hbar*omega):
      asym = (U+ - U-)/(U+ + U-) -> 1/2   (equivalently U+/U- -> 3)
  Near-Beltrami consistency: (U+ - U-)/(omega * H_A) ~ 1 (the constraint-pinning
  caveat of par. 4b; that identity is WHY the ladder dials H_A).

THE RELAXATION: fixed Q_can + fixed H_A (the M7.5/M7.6 frame), relax_qcan
lineage with the THROUGH-ZERO-SAFE helicity restore (task doc par. 4d step 0):
exact rescale when sign(H) == sign(H0), Newton additive step along dH otherwise
(the M7.6 blend_standing restore hole, fixed).

Headless; matplotlib PNG only. Data: research/data/m7_8_*.json.
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
    COMP_NAMES, HarmonicFields, curl_np, dot, fire_minimize, grid_xyz,
)
from m7_4_linked_vortex import (  # noqa: E402
    F_CONV, KAPPA, OMEGA, SHELL, TaichiBlend, apply_vacuum_shell,
    helicity_A, helicity_A_grad, interior_mask_flat, pack_dict, slot_mask,
)
from m7_functional import jz_per_quantum  # noqa: E402

DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
CKPT = os.path.join(HERE, "..", "checkpoints", "m7_8_progress.md")

CONV = F_CONV["repulsive"]
C1, C2 = CONV["c1"], CONV["c2"]
A_SLOTS = ("avc", "avs")
VEC_SLOTS = ("avc", "avs", "jvc", "jvs")
SCALAR_SLOTS = ("a0c", "a0s", "j0c", "j0s")

LAM0, SIGMA = 1.0, 2.0          # Case-B closure in lattice units (omega = c*lam0 = 1)
QCAN_REF = 13.2017              # the Phase 1 canonical Q_can (cross-rung comparability)
RATIOS = (1.2, 1.5, np.sqrt(3.0), 2.0, 2.5)
RTAGS = ("r1p2", "r1p5", "rsq3", "r2p0", "r2p5")


def _ti_init():
    import taichi as ti
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)


# =============================================================================
# the pair seed (closure notes Part A, lattice realization)
# =============================================================================


def _torus_frame(N, L, R0):
    """Toroidal frame per the NOTES' convention: theta toroidal, phi poloidal.
    RIGHT-HANDED (r_hat x phi_hat = +theta_hat), which requires the poloidal
    angle to wind as atan2(-z, rho-R0): with the naive atan2(z, .) the triad is
    left-handed and every curl eigenvalue flips sign (caught at the seed gate:
    the s = +1 mode measured H_A < 0)."""
    X, Y, Z = grid_xyz(N, L)
    rho = np.sqrt(X * X + Y * Y)
    rho_safe = np.maximum(rho, 1e-12)
    theta = np.arctan2(Y, X)
    d = np.sqrt((rho - R0) ** 2 + Z * Z)
    phi = np.arctan2(-Z, rho - R0)
    ct, st = X / rho_safe, Y / rho_safe
    rho_hat = np.stack([ct, st, np.zeros_like(ct)], axis=-1)
    theta_hat = np.stack([-st, ct, np.zeros_like(ct)], axis=-1)
    z_hat = np.zeros(rho_hat.shape)
    z_hat[..., 2] = 1.0
    cp, sp = np.cos(phi)[..., None], np.sin(phi)[..., None]
    r_hat = cp * rho_hat - sp * z_hat          # minor-radius direction
    phi_hat = -sp * rho_hat - cp * z_hat       # poloidal direction
    return d, phi, theta, r_hat, phi_hat, theta_hat


def _one_mode(N, L, R0, m, n, s, lam0=LAM0, sigma=SIGMA):
    """One CK/LG mode as a harmonic doublet (a_c, a_s). Regular at d = 0
    (Psi/d = (1/sigma)exp(...) is finite for m = 1)."""
    d, phi, theta, r_hat, phi_hat, theta_hat = _torus_frame(N, L, R0)
    k = n / R0
    alpha2 = lam0 ** 2 - k ** 2
    g = np.exp(-d * d / (2 * sigma ** 2))
    P = g / sigma                              # Psi/d
    Psi = d * P
    Psip = (1.0 - d * d / sigma ** 2) * g / sigma
    Cr = -(m * P + (k / (s * lam0)) * Psip)    # coefficient of sin(chi) on r_hat
    Cph = -(Psip + (m * k / (s * lam0)) * P)   # coefficient of cos(chi) on phi_hat
    Cth = (s * alpha2 / lam0) * Psi            # coefficient of cos(chi) on theta_hat
    chi = m * phi + n * theta
    cchi, schi = np.cos(chi)[..., None], np.sin(chi)[..., None]
    Cr, Cph, Cth = Cr[..., None], Cph[..., None], Cth[..., None]
    a_c = Cr * schi * r_hat + Cph * cchi * phi_hat + Cth * cchi * theta_hat
    a_s = -Cr * cchi * r_hat + Cph * schi * phi_hat + Cth * schi * theta_hat
    return a_c, a_s


def build_pair_seed(N, L, ratio, R0=None, j_prime=-0.1, qcan_ref=QCAN_REF):
    """The repaired helicity pair at amplitude ratio a+/a- = ratio, normalized
    to the common Q_can (all four vector slots rescaled), J primed at -0.1."""
    R0 = 0.25 * L if R0 is None else R0
    acp, asp = _one_mode(N, L, R0, 1, +1, +1)
    acm, asm = _one_mode(N, L, R0, 1, -1, -1)
    # per-mode L2 normalization so `ratio` is a true energy-amplitude ratio
    npn = np.sqrt(np.sum(dot(acp, acp) + dot(asp, asp)))
    nmn = np.sqrt(np.sum(dot(acm, acm) + dot(asm, asm)))
    f = HarmonicFields(N, L)
    f.avc = ratio * acp / npn + acm / nmn
    f.avs = ratio * asp / npn + asm / nmn
    f.jvc = j_prime * f.avc
    f.jvs = j_prime * f.avs
    f = apply_vacuum_shell(f)
    q = qcan(f)
    scale = np.sqrt(qcan_ref / q)
    for name in VEC_SLOTS:
        setattr(f, name, getattr(f, name) * scale)
    return f


def build_single_mode_seed(N, L, s, R0=None):
    """One mode alone (projector-calibration gate)."""
    R0 = 0.25 * L if R0 is None else R0
    ac, a_s = _one_mode(N, L, R0, 1, s, s)
    f = HarmonicFields(N, L)
    f.avc, f.avs = ac, a_s
    return apply_vacuum_shell(f)


# =============================================================================
# constraints (Q_can + through-zero-safe H_A)
# =============================================================================


def qcan(f: HarmonicFields, omega=OMEGA):
    h3 = f.h ** 3
    return 0.5 * omega * float(np.sum(
        dot(f.avc, f.avc) + dot(f.avs, f.avs)
        + dot(f.jvc, f.jvc) + dot(f.jvs, f.jvs)) * h3)


def qcan_grad(f: HarmonicFields, omega=OMEGA):
    h3 = f.h ** 3
    g = {name: np.zeros_like(getattr(f, name)) for name in COMP_NAMES}
    for name in VEC_SLOTS:
        g[name] = omega * getattr(f, name) * h3
    return g


def relax_qcan_safe(eng: TaichiBlend, f0: HarmonicFields, n_iter=1500, tag="",
                    omega=OMEGA, qcan0=None, log_every=250):
    """The M7.6 relax_qcan (fixed Q_can + H_A, Gram-Schmidt tangent projection)
    with the THROUGH-ZERO-SAFE helicity restore: exact A-rescale when
    sign(H) == sign(H0), Newton additive step along dH/dx otherwise."""
    N, L = f0.N, f0.L
    scratch = HarmonicFields(N, L)
    free = interior_mask_flat(f0) & ~slot_mask(f0, SCALAR_SLOTS)
    a_mask = slot_mask(f0, A_SLOTS)
    v_mask = slot_mask(f0, VEC_SLOTS)
    H0 = helicity_A(f0)
    Q0 = qcan0 if qcan0 is not None else qcan(f0, omega)

    def egf(x):
        scratch.unpack(x)
        E, g = eng.energy(scratch, grad=True)
        return E, pack_dict(g)

    def proj(x, g):
        g = g.copy()
        g[~free] = 0.0
        scratch.unpack(x)
        basis = []
        for gc in (pack_dict(helicity_A_grad(scratch)),
                   pack_dict(qcan_grad(scratch, omega))):
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
        x = x.copy()
        for _ in range(6):
            scratch.unpack(x)
            H = helicity_A(scratch)
            if H * H0 > 0:
                x[a_mask] *= np.sqrt(H0 / H)          # exact rescale restore
            else:
                gH = pack_dict(helicity_A_grad(scratch))   # Newton step (safe)
                gH[~free] = 0.0
                gn2 = float(np.dot(gH, gH))
                if gn2 > 1e-300:
                    x += ((H0 - H) / gn2) * gH
            scratch.unpack(x)
            Q = qcan(scratch, omega)
            if Q > 1e-300:
                x[v_mask] *= np.sqrt(Q0 / Q)
            scratch.unpack(x)
            if (abs(helicity_A(scratch) - H0) < 1e-10 * max(abs(H0), 1e-6)
                    and abs(qcan(scratch, omega) / Q0 - 1) < 1e-12):
                break
        return x

    x = corr(f0.pack())
    hist, it_done, status = [], 0, "ok"
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
                     "H_A": helicity_A(scratch),
                     "Q_can": qcan(scratch, omega),
                     "maxf": float(np.max(np.abs(x)))})
        if log_every:
            hh = hist[-1]
            print(f"  [{tag}] it={it_done:5d} E={hh['E']:+.5e} "
                  f"|g|={hh['gnorm']:.2e} H_A={hh['H_A']:+.4f} "
                  f"Q_can={hh['Q_can']:.4f} maxf={hh['maxf']:.3f}")
        if gn < 1e-9:
            break
    scratch.unpack(x)
    return scratch, {"history": hist, "status": status,
                     "E_final": hist[-1]["E"] if hist else None,
                     "gnorm_final": hist[-1]["gnorm"] if hist else None,
                     "H0": H0, "Q0": Q0}


# =============================================================================
# the helical (Waleffe) split U+/U- (discrete-curl-exact)
# =============================================================================


def helical_split(fc, fs, h, omega=OMEGA):
    """Per-helicity period-averaged quadratic energy of one sector's doublet.
    Returns dict with U_plus / U_minus (transverse helical sectors), U_long
    (the LONGITUDINAL bucket: curl-free, along khat, where the divergence /
    charge content lives; energy is omega^2-only), U_zero (curl-null lattice
    modes), U_real (real-space check). Completeness: U_plus + U_minus + U_long
    + U_zero == U_real to machine precision (the Parseval gate). Sign
    convention pinned by the projector gate (seed mode s = +1 -> U_plus)."""
    N = fc.shape[0]
    CA = fc + 1j * fs                                    # complex doublet
    Ck = np.fft.fftn(CA, axes=(0, 1, 2))
    k1 = 2 * np.pi * np.fft.fftfreq(N, d=h)
    KX, KY, KZ = np.meshgrid(k1, k1, k1, indexing="ij")
    # central differences diagonalize on kappa_l = sin(k_l h)/h
    kap = np.stack([np.sin(KX * h), np.sin(KY * h), np.sin(KZ * h)],
                   axis=-1) / h
    kmag = np.sqrt(np.sum(kap * kap, axis=-1))
    kn = np.maximum(kmag, 1e-300)
    khat = kap / kn[..., None]
    # orthonormal transverse frame (t not parallel to khat, switch where needed)
    t = np.zeros_like(khat)
    t[..., 0] = 1.0
    par = np.abs(khat[..., 0]) > 0.9
    t[par] = 0.0
    t[par, 1] = 1.0
    e1 = np.cross(t, khat)
    e1 /= np.maximum(np.linalg.norm(e1, axis=-1), 1e-300)[..., None]
    e2 = np.cross(khat, e1)
    ep = (e1 + 1j * e2) / np.sqrt(2)     # positive-helicity sector (gate-pinned:
    em = (e1 - 1j * e2) / np.sqrt(2)     # the s = +1 / H_A > 0 mode lands in U_plus)
    cp = np.sum(Ck * np.conj(ep), axis=-1)
    cm = np.sum(Ck * np.conj(em), axis=-1)
    cl = np.sum(Ck * khat, axis=-1)                      # longitudinal (real basis)
    w2 = 0.25 * (omega ** 2 + kmag ** 2) * h ** 3 / N ** 3
    w2l = 0.25 * omega ** 2 * h ** 3 / N ** 3            # curl-free: no curl energy
    null = kmag < 1e-12
    Up = float(np.sum(w2[~null] * np.abs(cp[~null]) ** 2))
    Um = float(np.sum(w2[~null] * np.abs(cm[~null]) ** 2))
    Ul = float(np.sum(w2l * np.abs(cl[~null]) ** 2))
    U0 = float(np.sum((w2l * (np.abs(Ck[null][..., 0]) ** 2
                              + np.abs(Ck[null][..., 1]) ** 2
                              + np.abs(Ck[null][..., 2]) ** 2))))
    # Parseval + completeness gate: compare to the real-space quad energy
    Bc, Bs = curl_np(fc, h), curl_np(fs, h)
    Ureal = 0.25 * float(np.sum(omega ** 2 * (dot(fc, fc) + dot(fs, fs))
                                + dot(Bc, Bc) + dot(Bs, Bs)) * h ** 3)
    return {"U_plus": Up, "U_minus": Um, "U_long": Ul, "U_zero": U0,
            "U_real": Ureal,
            "parseval_dev": abs(Up + Um + Ul + U0 - Ureal) / max(Ureal, 1e-300)}


# =============================================================================
# the observables battery
# =============================================================================


def battery(f: HarmonicFields, omega=OMEGA):
    h = f.h
    X, Y, Z = grid_xyz(f.N, f.L)
    out = {}
    out["A"] = helical_split(f.avc, f.avs, h, omega)
    out["J"] = helical_split(f.jvc, f.jvs, h, omega)
    Up, Um = out["A"]["U_plus"], out["A"]["U_minus"]
    Ureal, Urealj = out["A"]["U_real"], out["J"]["U_real"]
    HA = helicity_A(f)
    out["H_A"] = HA
    out["Q_can"] = qcan(f, omega)
    out["ratio_A"] = Up / Um if Um > 0 else np.inf
    out["asym_A"] = (Up - Um) / (Up + Um)
    out["beltrami_id"] = (Up - Um) / (omega * HA) if abs(HA) > 1e-12 else None
    # energy budget (numpy, term by term)
    AdotJ = 0.5 * float(np.sum(dot(f.avc, f.jvc) + dot(f.avs, f.jvs)) * h ** 3)
    s_cc, s_ss = dot(f.jvc, f.jvc), dot(f.jvs, f.jvs)
    s_cs = dot(f.jvc, f.jvs)
    s0, s1, s2 = 0.5 * (s_cc + s_ss), 0.5 * (s_cc - s_ss), s_cs
    favg = float(np.sum(C1 * s0 + C2 * (s0 * s0 + 0.5 * (s1 * s1 + s2 * s2)))
                 * h ** 3)
    out["budget"] = {"U_quad_A": Ureal, "U_quad_J": Urealj,
                     "coupling": -KAPPA * AdotJ, "quartic": favg,
                     "E_sum": Ureal + Urealj - KAPPA * AdotJ + favg}
    # localization + alignment + spin quantum
    u = (dot(f.avc, f.avc) + dot(f.avs, f.avs)
         + dot(f.jvc, f.jvc) + dot(f.jvs, f.jvs))
    cs = np.cumsum(np.sort(u.ravel())[::-1])
    ncell = int(np.searchsorted(cs, 0.5 * cs[-1])) + 1
    out["r50"] = float((3.0 * ncell * h ** 3 / (4 * np.pi)) ** (1 / 3))
    B = curl_np(f.avc, h)
    cB = curl_np(B, h)
    nB, ncB = np.sqrt(np.sum(dot(B, B))), np.sqrt(np.sum(dot(cB, cB)))
    out["align"] = float(np.sum(dot(B, cB)) / max(nB * ncB, 1e-300))
    out["jz_A"] = float(jz_per_quantum(f.avc, f.avs, X, Y, h))
    out["jz_J"] = float(jz_per_quantum(f.jvc, f.jvs, X, Y, h))
    return out


def seed_overlaps(f: HarmonicFields, N, L, R0=None):
    """Overlap of the state with each seeded mode (construction-specific read)."""
    R0 = 0.25 * L if R0 is None else R0
    out = {}
    for tagm, s in (("plus", +1), ("minus", -1)):
        ac, a_s = _one_mode(N, L, R0, 1, s, s)
        num = float(np.sum(dot(f.avc, ac) + dot(f.avs, a_s)))
        den = (np.sqrt(np.sum(dot(f.avc, f.avc) + dot(f.avs, f.avs)))
               * np.sqrt(np.sum(dot(ac, ac) + dot(a_s, a_s))))
        out[tagm] = num / max(den, 1e-300)
    return out


# =============================================================================
# checkpointing
# =============================================================================


def ckpt(line):
    os.makedirs(os.path.dirname(CKPT), exist_ok=True)
    stamp = time.strftime("%Y-%m-%d %H:%M")
    with open(CKPT, "a") as fh:
        fh.write(f"- {stamp} {line}\n")
    print(f"[ckpt] {line}")


# =============================================================================
# modes
# =============================================================================


def mode_seed(N=48, L=16.0):
    """Seed-level gates: projector calibration + H_A sign + divergence identity."""
    res = {"N": N, "L": L}
    # G1: projector calibration on single modes
    for tagm, s in (("plus", +1), ("minus", -1)):
        f = build_single_mode_seed(N, L, s)
        sp = helical_split(f.avc, f.avs, f.h)
        Utr = sp["U_plus"] + sp["U_minus"]
        frac = (sp["U_plus"] if s > 0 else sp["U_minus"]) / max(Utr, 1e-300)
        res[f"gate_projector_{tagm}"] = dict(
            sp, expected_sector_fraction=frac, H_A=helicity_A(f))
        print(f"single mode s={s:+d}: U+={sp['U_plus']:.4f} "
              f"U-={sp['U_minus']:.4f} U_long={sp['U_long']:.4f} "
              f"U0={sp['U_zero']:.4f} transverse-sector frac={frac:.4f} "
              f"H_A={helicity_A(f):+.4f} parseval dev={sp['parseval_dev']:.2e}")
    # G2: the pair seed at sqrt3, seed-level numbers
    f = build_pair_seed(N, L, float(np.sqrt(3.0)))
    b = battery(f)
    res["pair_sqrt3_seed"] = {
        "U_plus": b["A"]["U_plus"], "U_minus": b["A"]["U_minus"],
        "ratio": b["ratio_A"], "asym": b["asym_A"], "H_A": b["H_A"],
        "Q_can": b["Q_can"], "beltrami_id": b["beltrami_id"]}
    print(f"pair seed sqrt3: U+/U-={b['ratio_A']:.4f} asym={b['asym_A']:.4f} "
          f"H_A={b['H_A']:+.4f} Q_can={b['Q_can']:.4f} "
          f"(U+-U-)/(w H_A)={b['beltrami_id']:.4f}")
    # G3: divergence identity, qualitative: div a_c localized on the gradient
    # shell (d ~ sigma..w), near-zero at the core ring
    d, _, _, _, _, _ = _torus_frame(N, L, 0.25 * L)
    dv = np.abs((np.gradient(f.avc[..., 0], f.h, axis=0)
                 + np.gradient(f.avc[..., 1], f.h, axis=1)
                 + np.gradient(f.avc[..., 2], f.h, axis=2)))
    core = d < 0.5
    shell_band = (d > 1.0) & (d < 4.0)
    res["gate_div_identity"] = {
        "rms_div_core": float(np.sqrt(np.mean(dv[core] ** 2))),
        "rms_div_shell": float(np.sqrt(np.mean(dv[shell_band] ** 2)))}
    print(f"div identity: rms(div a) core={res['gate_div_identity']['rms_div_core']:.3e} "
          f"gradient-shell={res['gate_div_identity']['rms_div_shell']:.3e}")
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "m7_8_seed_gates.json"), "w") as fh:
        json.dump(res, fh, indent=1)
    ckpt(f"seed gates done (N={N}): projector fracs "
         f"{res['gate_projector_plus']['expected_sector_fraction']:.3f}/"
         f"{res['gate_projector_minus']['expected_sector_fraction']:.3f}, "
         f"pair asym(seed)={res['pair_sqrt3_seed']['asym']:.3f} -> m7_8_seed_gates.json")
    return res


def run_rung(eng, N, L, ratio, tag, n_iter):
    f0 = build_pair_seed(N, L, ratio)
    b0 = battery(f0)
    print(f"[{tag}] seed: E-parts U+={b0['A']['U_plus']:.3f} "
          f"U-={b0['A']['U_minus']:.3f} H_A={b0['H_A']:+.4f} "
          f"Q={b0['Q_can']:.4f}")
    fR, info = relax_qcan_safe(eng, f0, n_iter=n_iter, tag=tag)
    E, g = eng.energy(fR, grad=False)
    b = battery(fR)
    ov = seed_overlaps(fR, N, L)
    rec = {"ratio_seeded": float(ratio), "E": E,
           "gnorm": info["gnorm_final"], "status": info["status"],
           "H_A": b["H_A"], "Q_can": b["Q_can"],
           "seed": {"U_plus": b0["A"]["U_plus"], "U_minus": b0["A"]["U_minus"],
                    "ratio": b0["ratio_A"], "asym": b0["asym_A"],
                    "H_A": b0["H_A"]},
           "relaxed": b, "overlaps": ov}
    print(f"[{tag}] relaxed: E={E:+.5f} |g|={info['gnorm_final']:.2e} "
          f"U+/U-={b['ratio_A']:.4f} asym={b['asym_A']:.4f} "
          f"(U+-U-)/(wH_A)={b['beltrami_id']:.4f} r50={b['r50']:.2f} "
          f"align={b['align']:+.3f} jz_A={b['jz_A']:.3f}")
    return rec


def mode_smoke(N=48, L=16.0):
    _ti_init()
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    rec = run_rung(eng, N, L, float(np.sqrt(3.0)), "smoke rsq3", 500)
    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "m7_8_smoke.json"), "w") as fh:
        json.dump({"N": N, "L": L, "rsq3": rec}, fh, indent=1)
    ckpt(f"smoke done (N={N}): E={rec['E']:+.4f} U+/U-={rec['relaxed']['ratio_A']:.3f} "
         f"asym={rec['relaxed']['asym_A']:.3f} status={rec['status']} -> m7_8_smoke.json")
    return rec


def mode_run(N=64, L=16.0, n_iter=1500):
    _ti_init()
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    out = {"N": N, "L": L, "n_iter": n_iter, "rungs": {}}
    for ratio, tag in zip(RATIOS, RTAGS):
        t0 = time.time()
        rec = run_rung(eng, N, L, ratio, tag, n_iter)
        rec["wall_s"] = time.time() - t0
        out["rungs"][tag] = rec
        with open(os.path.join(DATA, "m7_8_ladder.json"), "w") as fh:
            json.dump(out, fh, indent=1)
        ckpt(f"rung {tag} (ratio {ratio:.3f}) done: E={rec['E']:+.4f} "
             f"U+/U-={rec['relaxed']['ratio_A']:.3f} "
             f"asym={rec['relaxed']['asym_A']:.3f} ({rec['wall_s']:.0f}s) "
             f"-> m7_8_ladder.json")
    return out


def mode_grid(N=96, L=16.0, n_iter=1500):
    _ti_init()
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    rec = run_rung(eng, N, L, float(np.sqrt(3.0)), "grid96 rsq3", n_iter)
    with open(os.path.join(DATA, "m7_8_grid96.json"), "w") as fh:
        json.dump({"N": N, "L": L, "rsq3": rec}, fh, indent=1)
    ckpt(f"grid96 done: E={rec['E']:+.4f} U+/U-={rec['relaxed']['ratio_A']:.3f} "
         f"asym={rec['relaxed']['asym_A']:.3f} -> m7_8_grid96.json")
    return rec


def mode_audit(N=48, L=16.0):
    """ADVERSARIAL AUDIT of the expulsion finding (AI_HYGIENE cardinal rule):
    try to REFUTE 'the relaxation expels the minus mode because the pair is
    not a constrained minimum'. Method: relax the sqrt3 rung, then re-insert
    minus-mode content at amplitude eps, restore BOTH constraints exactly, and
    measure E(eps). If E decreases anywhere, the expulsion was a relaxation
    artifact (refuted); if E rises monotonically, the pure-plus state is a
    genuine directional minimum against the minus mode (confirmed)."""
    _ti_init()
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    f0 = build_pair_seed(N, L, float(np.sqrt(3.0)))
    fR, info = relax_qcan_safe(eng, f0, n_iter=500, tag="audit relax")
    E0, _ = eng.energy(fR, grad=False)
    H0, Q0 = helicity_A(fR), qcan(fR)
    # the minus-mode direction, normalized to the state's own norm scale
    acm, asm = _one_mode(N, L, 0.25 * L, 1, -1, -1)
    g = HarmonicFields(N, L)
    g.avc, g.avs = acm, asm
    g = apply_vacuum_shell(g)
    nrm = np.sqrt(np.sum(dot(g.avc, g.avc) + dot(g.avs, g.avs)))
    ref = np.sqrt(np.sum(dot(fR.avc, fR.avc) + dot(fR.avs, fR.avs)))
    scale = ref / nrm

    # constraint-restoring corrector (same machinery as the relaxation)
    scratch = HarmonicFields(N, L)
    free = interior_mask_flat(fR) & ~slot_mask(fR, SCALAR_SLOTS)
    a_mask, v_mask = slot_mask(fR, A_SLOTS), slot_mask(fR, VEC_SLOTS)

    def restore(x):
        for _ in range(8):
            scratch.unpack(x)
            H = helicity_A(scratch)
            if H * H0 > 0:
                x[a_mask] *= np.sqrt(H0 / H)
            else:
                gH = pack_dict(helicity_A_grad(scratch))
                gH[~free] = 0.0
                gn2 = float(np.dot(gH, gH))
                if gn2 > 1e-300:
                    x += ((H0 - H) / gn2) * gH
            scratch.unpack(x)
            Q = qcan(scratch)
            if Q > 1e-300:
                x[v_mask] *= np.sqrt(Q0 / Q)
        return x

    rows = []
    for eps in (0.0, 0.02, 0.05, 0.10, 0.20):
        f = HarmonicFields(N, L)
        f.avc = fR.avc + eps * scale * g.avc
        f.avs = fR.avs + eps * scale * g.avs
        f.jvc, f.jvs = fR.jvc.copy(), fR.jvs.copy()
        x = restore(f.pack())
        f.unpack(x)
        E, _ = eng.energy(f, grad=False)
        b = battery(f)
        rows.append({"eps": eps, "E": E, "dE": E - E0,
                     "asym": b["asym_A"], "H_A": b["H_A"],
                     "Q_can": b["Q_can"]})
        print(f"  eps={eps:.2f}: E={E:+.6f} dE={E - E0:+.2e} "
              f"asym={b['asym_A']:.4f} H_A={b['H_A']:+.4f} Q={b['Q_can']:.4f}")
    verdict = ("CONFIRMED (E rises monotonically: the pure-plus state is a "
               "directional minimum against minus-mode re-insertion)"
               if all(r["dE"] >= -1e-9 for r in rows)
               and rows[-1]["dE"] > 0 else "REFUTED or inconclusive")
    print(f"AUDIT VERDICT: {verdict}")
    out = {"N": N, "L": L, "E0": E0, "rows": rows, "verdict": verdict}
    with open(os.path.join(DATA, "m7_8_audit.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    ckpt(f"audit done: {verdict} -> m7_8_audit.json")
    return out


def mode_analyze():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    with open(os.path.join(DATA, "m7_8_ladder.json")) as fh:
        lad = json.load(fh)
    rungs = [lad["rungs"][t] for t in RTAGS if t in lad["rungs"]]
    rat_seed = [r["ratio_seeded"] for r in rungs]
    rat_out = [r["relaxed"]["ratio_A"] for r in rungs]
    asym = [r["relaxed"]["asym_A"] for r in rungs]
    E = [r["E"] for r in rungs]
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    ax[0].semilogy(rat_seed, rat_out, "o-", label="relaxed U+/U-")
    ax[0].semilogy(rat_seed, [r ** 2 for r in rat_seed], "k:",
                   label="seed (ratio$^2$)")
    ax[0].axhline(3.0, color="r", ls="--", label="closure 3:1")
    ax[0].axvline(np.sqrt(3), color="r", ls=":", alpha=0.5)
    ax[0].set_xlabel("seeded amplitude ratio a+/a-")
    ax[0].set_ylabel("relaxed U+/U- (A sector, log)")
    ax[0].legend()
    ax[1].plot(rat_seed, asym, "o-")
    ax[1].axhline(0.5, color="r", ls="--", label="S_z = hbar/2 target")
    ax[1].set_xlabel("seeded amplitude ratio a+/a-")
    ax[1].set_ylabel("(U+ - U-)/(U+ + U-)")
    ax[1].legend()
    ax[2].plot(asym, E, "o-")
    ax[2].set_xlabel("(U+ - U-)/(U+ + U-)")
    ax[2].set_ylabel("E_omega (fixed Q_can)")
    for a in ax:
        a.grid(alpha=0.3)
    fig.suptitle("M7.8 helicity-pair ladder (N=64, fixed Q_can = 13.2017 + H_A per rung)")
    fig.tight_layout()
    os.makedirs(PLOTS, exist_ok=True)
    out = os.path.join(PLOTS, "m7_8_ladder.png")
    fig.savefig(out, dpi=130)
    print(f"wrote {out}")
    ckpt("analyze done -> plots/m7_8_ladder.png")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["seed", "smoke", "run", "grid", "audit",
                                     "analyze"])
    args = ap.parse_args()
    t0 = time.time()
    {"seed": mode_seed, "smoke": mode_smoke, "run": mode_run,
     "grid": mode_grid, "audit": mode_audit, "analyze": mode_analyze}[args.mode]()
    print(f"[{args.mode}] total {time.time() - t0:.0f}s")
