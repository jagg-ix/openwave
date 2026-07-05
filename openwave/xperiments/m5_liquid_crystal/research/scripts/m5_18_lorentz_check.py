"""M5.18 phase A: machine checks for Duda's 4D Lagrangian + Hamiltonian.

THE CLAIMS UNDER TEST (Duda 2026-07-05, m5_17_convo.md entry 2)
    eta = diag(-1, 1, 1, 1),  [A,B]_eta = A.eta.B - B.eta.A ,
    F_{mu nu alpha beta} = [d_mu M, d_nu M]_eta ,
    L = - SUM_{mu<nu} F_{mu nu alpha beta} F^{mu nu alpha beta}  -  V(M) ,
        (all four indexes raised with eta)
    V(M) = SUM_p (Tr_eta(M^p) - c_p)^2 ,  c_p = SUM_i Lambda_i^p ,
        Tr_eta(M^p) = trace((eta.M)^p)  (mixed-index trace),
    H = SUM_{mu<nu} F_{mu nu alpha beta} F_{mu nu}^{alpha beta}  +  V(M)
        (INTERNAL indexes raised with eta, spacetime indexes NOT raised)
      = 2 SUM_{mu<nu} [ SUM_{1<=a<b<=3} (F_{mu nu a b})^2
                        - SUM_{a=1..3}  (F_{mu nu a 0})^2 ]  +  V(M).

CHECKS (all pass/fail printed + JSON'd; analytic derivations in
../findings/m5_18_verification_note.md)
    1  Lorentz invariance of L (curvature + potential separately) under a
       random boost+rotation, on a random quadratic-polynomial field, to
       machine precision.  M transforms as a rank-2 covariant tensor:
       M'(x') = Lam^{-T} M(x) Lam^{-1}.
    1b NEGATIVE CONTROL: the naive version (plain commutator, plain
       Frobenius norm, no eta anywhere) is NOT boost-invariant (O(1) drift).
    2  Legendre transform: H(M, Mdot) = pi:Mdot - L equals the claimed
       formula EXACTLY, using L's exact quadratic dependence on Mdot:
       T = L(Mdot) - L(0),  pi:Mdot = 2T (Euler),  H = L(Mdot) - 2 L(0)
       ... compared against  H_claim = SUM_{mu<nu} S_mu_nu + V.
    3  Primary constraint: [eta, B]_eta = 0 for EVERY symmetric B, hence
       velocity direction Mdot ~ eta never enters L: pi has an identically
       zero component (the Legendre map is degenerate; Dirac constraints).
    4  Indefiniteness witness A (algebraic): a static derivative pair
       (spatial-block gradient x time-mixing gradient) whose curvature
       energy density is strictly NEGATIVE.
    4b Indefiniteness witness B (THE physics finding; construction
       CORRECTED by the 2026-07-05 adversarial audit): a field ON THE
       VACUUM MANIFOLD (V = 0 identically) built as the PRODUCT texture
       Lam(x) = expm(x1.eta.W_boost01) . expm(x2.eta.W_rot12), boost and
       rotation planes SHARING axis 1. Simultaneous conjugation makes the
       density x1-independent exactly, and the density is verified
       NEGATIVE over the full rotation period in x2 (the audit refuted
       the earlier expm-of-sum texture, which flips positive off-origin;
       and commuting planes, e.g. boost01 x rot23, give exactly zero).
       Total H falls linearly with occupied volume: H is UNBOUNDED BELOW
       on the vacuum manifold itself unless the boost-texture sector is
       constrained away. (Boost x boost textures give POSITIVE density:
       the sign is channel-specific; verified both ways.)
    4c Vacuum-manifold structure (audit finding): V = 0 fixes only the
       SPECTRUM of eta.M, so the vacuum manifold is a UNION of 4 disjoint
       Lorentz orbits labeled by WHICH preferred eigenvalue (g, 1, delta,
       or 0) rides the timelike eigenvector: all four diagonal branch
       representatives diag(-lam_t, rest) have V = 0 exactly. Possible
       domain walls between branches; owner-intent question.
    5  The slide's expansion: S_mu_nu = 2[SUM_{spatial a<b} F^2
       - SUM_a F_{a0}^2] exactly.
    6  Static-sector blindness: for fields with a uniform time row (zero
       time block in every dM: ALL M5.16/M5.17 fields), the eta-versions
       reduce EXACTLY to the plain versions used in m5_17_energy.py:
       no retroactive change to any published static number.

Run:  python m5_18_lorentz_check.py     (headless; writes
      ../data/m5_18_lorentz_check.json)
"""
from __future__ import annotations

import json
import os

import numpy as np
from scipy.linalg import expm

HERE = os.path.dirname(os.path.abspath(__file__))
ETA = np.diag([-1.0, 1.0, 1.0, 1.0])
RNG = np.random.default_rng(20260705)


def sym(A):
    return 0.5 * (A + A.T)


def comm_eta(A, B):
    return A @ ETA @ B - B @ ETA @ A


def comm_plain(A, B):
    return A @ B - B @ A


def inner_eta(F, G):
    """F_{ab} G^{ab} with both internal indexes raised by eta."""
    return float(np.einsum("ab,cd,ac,bd->", F, G, ETA, ETA))


def inner_plain(F, G):
    return float(np.sum(F * G))


def tr_eta_p(M, p):
    return float(np.trace(np.linalg.matrix_power(ETA @ M, p)))


def v_spec(M, targets):
    """V(M) = sum_p (Tr_eta(M^p) - c_p)^2, c_p = sum_i Lambda_i^p, p=1..4."""
    v = 0.0
    for p in range(1, 5):
        cp = float(np.sum(np.asarray(targets) ** p))
        v += (tr_eta_p(M, p) - cp) ** 2
    return v


def l_curv(D, eta_version=True):
    """- SUM_{mu<nu} F_{munu ab} F^{munu ab}; D = list of 4 derivative mats.
    eta_version: eta commutator + eta raising of ALL four indexes.
    else: plain commutator + plain Frobenius (the negative control)."""
    tot = 0.0
    for mu in range(4):
        for nu in range(mu + 1, 4):
            if eta_version:
                F = comm_eta(D[mu], D[nu])
                sgn = ETA[mu, mu] * ETA[nu, nu]      # spacetime raising
                tot += sgn * inner_eta(F, F)          # internal raising
            else:
                F = comm_plain(D[mu], D[nu])
                tot += inner_plain(F, F)
    return -tot


def s_munu(D):
    """S_{mu nu} = F_{munu ab} F_{munu}^{ab} per ordered pair (internal
    raising only), as a dict; the Hamiltonian summand."""
    out = {}
    for mu in range(4):
        for nu in range(mu + 1, 4):
            F = comm_eta(D[mu], D[nu])
            out[(mu, nu)] = inner_eta(F, F)
    return out


def h_claim(D, M, targets):
    return sum(s_munu(D).values()) + v_spec(M, targets)


def random_lorentz(scale=0.5):
    W = RNG.normal(size=(4, 4)) * scale
    W = W - W.T                       # antisymmetric
    G = ETA @ W                       # G^T eta + eta G = 0
    return expm(G)


def transform_derivs(D, M0, Lam):
    """M'(x') = Lam^{-T} M(x) Lam^{-1};  d'_mu M' = (Lam^{-1})^rho_mu
    Lam^{-T} d_rho M Lam^{-1}."""
    Li = np.linalg.inv(Lam)
    Mp = Li.T @ M0 @ Li
    Dp = [Li.T @ sum(Li[r, m] * D[r] for r in range(4)) @ Li for m in range(4)]
    return Dp, Mp


def main():
    res = {}
    g_t, delta = 8.0, 1e-3
    targets = (g_t, 1.0, delta, 0.0)

    # random quadratic field data at a point: M0 (near-generic), D[0..3]
    M0 = sym(RNG.normal(size=(4, 4)))
    D = [sym(RNG.normal(size=(4, 4))) for _ in range(4)]

    # ---- check 1: Lorentz invariance (eta version) ------------------------
    worst_c = worst_v = 0.0
    for _ in range(20):
        Lam = random_lorentz()
        Dp, Mp = transform_derivs(D, M0, Lam)
        lc0, lc1 = l_curv(D), l_curv(Dp)
        worst_c = max(worst_c, abs(lc1 - lc0) / max(1.0, abs(lc0)))
        v0, v1 = v_spec(M0, targets), v_spec(Mp, targets)
        worst_v = max(worst_v, abs(v1 - v0) / max(1.0, abs(v0)))
    res["1_curv_invariance_rel"] = worst_c
    res["1_pot_invariance_rel"] = worst_v

    # ---- check 1b: negative control (plain version NOT invariant) --------
    drift = 0.0
    for _ in range(20):
        Lam = random_lorentz()
        Dp, _ = transform_derivs(D, M0, Lam)
        l0, l1 = l_curv(D, eta_version=False), l_curv(Dp, eta_version=False)
        drift = max(drift, abs(l1 - l0) / max(1.0, abs(l0)))
    res["1b_naive_drift_rel"] = drift          # expected O(1)

    # ---- check 2: Legendre H == claimed formula (EXACT, no FD noise) -----
    # L(Mdot) = T - U with T quadratic in Mdot (F_{0i} linear in Mdot):
    #   T = L(Mdot) - L(0),  pi:Mdot = 2T,  H = pi:Mdot - L = L(Mdot) - 2L(0)
    # Residuals normalized by the LARGEST intermediate (V dominates the
    # magnitudes; the identity is exact, the only residual is fp
    # cancellation of the large-V terms).
    def L_of(Mdot):
        DD = [Mdot, D[1], D[2], D[3]]
        return l_curv(DD) - v_spec(M0, targets)
    worst_h = 0.0
    scale = max(1.0, abs(L_of(np.zeros((4, 4)))))
    for _ in range(10):
        Mdot = sym(RNG.normal(size=(4, 4)))
        Hnum = L_of(Mdot) - 2.0 * L_of(np.zeros((4, 4)))
        DD = [Mdot, D[1], D[2], D[3]]
        Hcl = h_claim(DD, M0, targets)
        worst_h = max(worst_h, abs(Hnum - Hcl) / max(scale, abs(Hcl)))
        # quadratic-in-velocity structure itself:
        lam = 1.7
        Tq = L_of(Mdot) - L_of(np.zeros((4, 4)))
        Tq_s = L_of(lam * Mdot) - L_of(np.zeros((4, 4)))
        worst_h = max(worst_h, abs(Tq_s - lam ** 2 * Tq) / scale)
    res["2_legendre_rel"] = worst_h

    # ---- check 3: primary constraint (eta-direction velocity is silent) --
    kerr = 0.0
    for _ in range(10):
        B = sym(RNG.normal(size=(4, 4)))
        kerr = max(kerr, float(np.max(np.abs(comm_eta(ETA, B)))))
    Mdot = sym(RNG.normal(size=(4, 4)))
    l_shift = abs(L_of(Mdot + 0.37 * ETA) - L_of(Mdot))
    res["3_eta_commutant_maxabs"] = kerr
    res["3_kinetic_eta_shift"] = l_shift

    # ---- check 4: indefiniteness witness A (algebraic) --------------------
    # spatial-block gradient x time-mixing gradient -> F is PURE alpha-0:
    # S = -2|v|^2 < 0. (boost x boost mixing gives a purely SPATIAL F,
    # POSITIVE: computed as the contrast case.)
    # CONVENTION FINDING: the preferred spectrum (g,1,delta,0) is the
    # spectrum of the MIXED tensor eta.M, so the COVARIANT vacuum is
    # M_vac = diag(-g, 1, delta, 0) (time-time component NEGATIVE); at
    # M = diag(+g,1,delta,0) the potential is large (~1e6 at g=8), not 0.
    Mvac = ETA @ np.diag(targets)               # diag(-g,1,delta,0): V = 0
    res["4_vacuum_V_at_mixed_form"] = v_spec(Mvac, targets)      # expect 0
    res["4_vacuum_V_at_naive_diag"] = v_spec(np.diag(targets), targets)
    E01 = sym(np.outer([1.0, 0, 0, 0], [0, 1.0, 0, 0])) * 2.0  # e0-e1 mixing
    E02 = sym(np.outer([1.0, 0, 0, 0], [0, 0, 1.0, 0])) * 2.0  # e0-e2 mixing
    Asp = np.zeros((4, 4))
    Asp[1:, 1:] = sym(RNG.normal(size=(3, 3)))                 # spatial block
    Dw = [np.zeros((4, 4)), Asp, E01, np.zeros((4, 4))]        # static
    res["4_witness_H_density"] = h_claim(Dw, Mvac, targets)    # expect < 0
    Dbb = [np.zeros((4, 4)), E01, E02, np.zeros((4, 4))]       # boost x boost
    res["4_boostboost_H_density"] = h_claim(Dbb, Mvac, targets)  # expect > 0

    # ---- check 4b: witness B, ON THE VACUUM MANIFOLD (V = 0, density < 0
    # EVERYWHERE; the audit-corrected PRODUCT texture) --------------------
    # M(x) = Lam(x)^{-T} M_vac Lam(x)^{-1},
    # Lam(x) = expm(x1 eta W_boost01) . expm(x2 eta W_rot12)  (shared axis 1).
    # x1-translations act by simultaneous conjugation (density exactly
    # x1-independent), so scanning x2 over the full rotation period covers
    # the whole texture; V = 0 everywhere on the manifold. The earlier
    # expm-of-sum texture is kept as the audit's REFUTED contrast case
    # (negative at the origin, positive off-origin).
    Wb = np.outer([1.0, 0, 0, 0], [0, 1.0, 0, 0])
    Wb = Wb - Wb.T                                             # boost gen 0-1
    Wr = np.outer([0, 1.0, 0, 0], [0, 0, 1.0, 0])
    Wr = Wr - Wr.T                                             # rot gen 1-2

    def prod_M(x1, x2):
        Lam = expm(x1 * ETA @ Wb) @ expm(x2 * ETA @ Wr)
        Li = np.linalg.inv(Lam)
        return Li.T @ Mvac @ Li

    def sum_M(x1, x2):
        Lam = expm(ETA @ (x1 * Wb + x2 * Wr))
        Li = np.linalg.inv(Lam)
        return Li.T @ Mvac @ Li

    eps = 1e-5

    def density_at(orbit, x1, x2):
        d1 = (orbit(x1 + eps, x2) - orbit(x1 - eps, x2)) / (2 * eps)
        d2 = (orbit(x1, x2 + eps) - orbit(x1, x2 - eps)) / (2 * eps)
        Dorb = [np.zeros((4, 4)), d1, d2, np.zeros((4, 4))]
        return h_claim(Dorb, orbit(x1, x2), targets) - v_spec(orbit(x1, x2), targets)

    xs2 = np.linspace(0.0, 2.0 * np.pi, 25)
    dens_scan = [density_at(prod_M, x1, x2)
                 for x2 in xs2 for x1 in (0.0, 0.8)]
    res["4b_orbit_H_density"] = float(max(dens_scan))       # expect < 0 (ALL)
    res["4b_orbit_density_min"] = float(min(dens_scan))
    res["4b_orbit_V_offpoint_max"] = max(
        v_spec(prod_M(0.4, -0.7), targets), v_spec(prod_M(-1.1, 0.3), targets))
    res["4b_x1_invariance"] = abs(density_at(prod_M, 0.0, 0.9)
                                  - density_at(prod_M, 1.3, 0.9))
    res["4b_sum_texture_origin"] = density_at(sum_M, 0.0, 0.0)   # negative
    res["4b_sum_texture_offorigin"] = density_at(sum_M, 1.5, -0.8)  # POSITIVE (refuted)
    # commuting planes (boost01 x rot23): exactly zero density
    Wr23 = np.outer([0, 0, 1.0, 0], [0, 0, 0, 1.0])
    Wr23 = Wr23 - Wr23.T

    def prod_M_comm(x1, x2):
        Lam = expm(x1 * ETA @ Wb) @ expm(x2 * ETA @ Wr23)
        Li = np.linalg.inv(Lam)
        return Li.T @ Mvac @ Li

    res["4b_commuting_planes_density"] = abs(density_at(prod_M_comm, 0.3, 0.5))

    # ---- check 4c: vacuum manifold = union of 4 disjoint orbits ----------
    # (audit finding) V = 0 for every choice of which preferred eigenvalue
    # rides the timelike direction: covariant diag(-lam_t, spatial perm).
    branch_v = []
    tl = list(targets)
    for it_ in range(4):
        rest = [tl[j] for j in range(4) if j != it_]
        branch_v.append(v_spec(np.diag([-tl[it_]] + rest), targets))
    res["4c_branch_V_max"] = float(max(branch_v))            # expect 0 all four

    # ---- check 5: the slide's +/- expansion -------------------------------
    worst_s = 0.0
    for mu in range(4):
        for nu in range(mu + 1, 4):
            F = comm_eta(D[mu], D[nu])
            full = inner_eta(F, F)
            red = sum(F[a, b] ** 2 for a in range(1, 4) for b in range(a + 1, 4))
            blue = sum(F[a, 0] ** 2 for a in range(1, 4))
            worst_s = max(worst_s, abs(full - 2.0 * (red - blue)))
    res["5_slide_expansion_maxabs"] = worst_s

    # ---- check 6: static-sector blindness ---------------------------------
    worst_b = 0.0
    for _ in range(10):
        Ds = []
        for _ in range(4):
            A = np.zeros((4, 4))
            A[1:, 1:] = sym(RNG.normal(size=(3, 3)))    # zero time block
            Ds.append(A)
        for mu in range(4):
            for nu in range(mu + 1, 4):
                Fe = comm_eta(Ds[mu], Ds[nu])
                Fp = comm_plain(Ds[mu], Ds[nu])
                worst_b = max(worst_b, float(np.max(np.abs(Fe - Fp))),
                              abs(inner_eta(Fe, Fe) - inner_plain(Fp, Fp)))
    res["6_static_blind_maxabs"] = worst_b

    # ---- verdicts ----------------------------------------------------------
    tol = 1e-10
    checks = {
        "1  L curvature Lorentz-invariant": res["1_curv_invariance_rel"] < tol,
        "1  V spectral Lorentz-invariant": res["1_pot_invariance_rel"] < tol,
        "1b naive version NOT invariant (control)": res["1b_naive_drift_rel"] > 0.01,
        "2  Legendre H == claimed formula": res["2_legendre_rel"] < tol,
        "3  eta-direction primary constraint": max(res["3_eta_commutant_maxabs"], res["3_kinetic_eta_shift"]) < tol,
        "4  covariant vacuum is diag(-g,1,d,0): V = 0": res["4_vacuum_V_at_mixed_form"] < tol,
        "4  witness A: spatial x time-mixing density < 0": res["4_witness_H_density"] < -tol,
        "4  contrast: boost x boost density > 0": res["4_boostboost_H_density"] > tol,
        "4b witness B: product texture density < 0 over FULL period, V = 0": (res["4b_orbit_H_density"] < -tol and res["4b_orbit_V_offpoint_max"] < 1e-12),
        "4b x1-translation invariance of the density": res["4b_x1_invariance"] < 1e-4,
        "4b audit contrast: sum-texture flips positive off-origin": (res["4b_sum_texture_origin"] < -tol and res["4b_sum_texture_offorigin"] > tol),
        "4b commuting planes give zero density": res["4b_commuting_planes_density"] < 1e-6,
        "4c vacuum manifold = 4 disjoint orbit branches (V = 0 each)": res["4c_branch_V_max"] < tol,
        "5  slide expansion exact": res["5_slide_expansion_maxabs"] < tol,
        "6  static sector eta-blind": res["6_static_blind_maxabs"] < tol,
    }
    for k, ok in checks.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {k}")
    for k, v in res.items():
        print(f"    {k} = {v:.3e}")
    res["all_pass"] = all(checks.values())
    out = os.path.join(HERE, "..", "data", "m5_18_lorentz_check.json")
    with open(out, "w") as f:
        json.dump(res, f, indent=1)
    print("ALL PASS" if res["all_pass"] else "SOME CHECKS FAILED", "->", out)


if __name__ == "__main__":
    main()
