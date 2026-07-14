"""M5.20.3 phase A: free Euler-Lagrange evolution of the purely-quartic
verified L (THE ANSWER, 2026-07-13/14): no artificial restrictions; the
degenerate Legendre map handled as the theory's OWN structure.

SOURCE OF TRUTH: m5_18_lorentz_check.py / m5_20_2_a_eom.py (the verified L):

    L = SUM_i <F_0i, F_0i>_eta - SUM_{i<j} <F_ij, F_ij>_eta - V,
    F_mu nu = [d_mu M, d_nu M]_eta,   [A, B]_eta = A.eta.B - B.eta.A,
    (normalization pinned by GB0: the spatial sector carries the audited
     prefactor 4, so the kinetic density is T = 4 SUM_i <F_0i, F_0i>_eta,
     F_0i = [Mdot, A_i]_eta, i in {rho, phi, z}).

THE EOM (semi-discrete, per included cell c with measure w_c):
    T_tot = SUM_c w_c T_c = (1/2) Mdot . KK(M) Mdot,   KK = 4 w k_apply,
    k_apply(M)[X] = 2 SUM_i eta([X,A_i]_eta eta A_i - A_i eta [X,A_i]_eta) eta
                  = 2 SUM_i (eta X W_i + W_i X eta - 2 Y_i X Y_i),
        W_i = eta A_i eta A_i eta,   Y_i = eta A_i eta   (closed form),
    EL:  4 w_c k_apply(M)[Mddot]_c = gradM_T_c - G_static_c - 4 w_c kdot_c,
        gradM_T = d T_tot / dM at fixed Mdot (dT/dA_i = -8 adj(F_i, Mdot),
                  scattered through the channel stencils),
        kdot    = 2 SUM_i (adj([Mdot, Adot_i], A_i) + adj([Mdot, A_i], Adot_i)),
                  Adot_i = D_i Mdot,
    solved per cell in the 10-dim symmetric basis by spectral pseudo-inverse:
    K10 = U diag(lam) U^T; directions with |lam| below the cutoff are the
    theory's own null/frozen directions (Mdot ~ eta is the EXACT global
    null: the verified primary constraint); Mddot_null = 0 and the force
    component in the null space is RECORDED (the constraint ledger).
    Energy E = T + U is conserved by the exact EL (machine identity GC0e);
    the projection is the only bookkept leak.

GATES (complex-step: the energy is polynomial in M and Mdot)
    GC0a  pi = dT/dMdot == 4 w k_apply(Mdot)         (rel <= 1e-12)
    GC0b  gradM_T == complex-step dT/dM              (rel <= 1e-10)
    GC0c  grad_static_4 == complex-step dE_static/dM (rel <= 1e-10)
    GC0d  einsum-built K10 == 10-pass kin_form_apply build (rel <= 1e-12),
          K10 symmetric, K10 . eta10 == 0 (the exact null)
    GC0e  energy identity: SUM gradM_T . V == 2 SUM w kdot . V (rel <= 1e-10)
    GC1   census on the 4D loop seed: per-cell K10 rank / negative /
          max|eig| maps + the t = 0 constraint ledger (recorded, not
          pass/fail: his answer makes the degeneracy structure physics)

Run:  python m5_20_3_a_constraint.py           (gates + census + benchmark)
Out:  ../data/m5_20_3_a_gates.json
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import cell_weights, grid_coords                 # noqa: E402
from m5_16_axisym import pin_mask                                  # noqa: E402
from m5_20_1_b_seeds import loop_field_biax                        # noqa: E402
from m5_20_2_a_eom import (ETA, G_T, H, NR, NZ, WSCALE, MIR,       # noqa: E402
                           channels, comm_eta_b, grad_static_4,
                           inner_eta_b, kin_form_apply, sym_basis4,
                           u_eta_density, v4_density, vac4)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

REL_CUT = 1e-8          # per-cell relative eigenvalue cutoff (null threshold)
ABS_CUT_FRAC = 1e-10    # absolute cutoff as a fraction of the global max|eig|
BASIS = np.stack(sym_basis4())          # (10, 4, 4), Frobenius-orthonormal
ETA10 = np.array([-1.0, 1.0, 1.0, 1.0] + [0.0] * 6)   # eta in the 10-basis


# ---------------- kinetic sector ----------------
def t_density(Mnp, Vnp, h=H):
    """T = 4 SUM_i <[V, A_i]_eta, [V, A_i]_eta>_eta per included cell
    (complex-safe)."""
    Arho, Aphi, Az, _ = channels(Mnp, h)
    Vc = Vnp[: Mnp.shape[0] - 1, 1:-1]
    tot = 0.0
    for A in (Arho, Aphi, Az):
        F = comm_eta_b(Vc, A)
        tot = tot + inner_eta_b(F, F)
    return 4.0 * tot


def e_static_c(Mnp, wscale, delta, h=H, g=G_T):
    """complex-safe static energy (no float cast)."""
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return np.sum((u_eta_density(Mnp, h) + v4_density(Mnp, wscale, delta, g)) * w)


def t_total_c(Mnp, Vnp, h=H):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return np.sum(t_density(Mnp, Vnp, h) * w)


def energy_dyn(Mnp, Vnp, wscale, delta, h=H, g=G_T):
    """E = T + U (the conserved Hamiltonian of the quartic L)."""
    return float(t_total_c(Mnp, Vnp, h) + e_static_c(Mnp, wscale, delta, h, g))


def _adj(F, B):
    return ETA @ (F @ ETA @ B - B @ ETA @ F) @ ETA


def grad_m_T(Mnp, Vnp, w4, h=H, rho4=None):
    """d T_tot / dM at fixed Mdot: dT/dA_i = -8 adj(F_i, V), scattered
    through the channel stencils (the grad_static_4 conventions)."""
    nr = Mnp.shape[0]
    Arho, Aphi, Az, r4 = channels(Mnp, h)
    if rho4 is None:
        rho4 = r4
    Vc = Vnp[: nr - 1, 1:-1]
    k = -8.0 * w4
    Grho = k * _adj(comm_eta_b(Vc, Arho), Vc)
    Gphi = k * _adj(comm_eta_b(Vc, Aphi), Vc)
    Gz = k * _adj(comm_eta_b(Vc, Az), Vc)
    inv2h = 1.0 / (2.0 * h)
    G = np.zeros_like(Mnp)
    G[1:, 1:-1] += Grho * inv2h
    G[: nr - 2, 1:-1] -= Grho[1:] * inv2h
    G[0, 1:-1] -= (MIR * Grho[0]) * inv2h
    G[: nr - 1, 2:] += Gz * inv2h
    G[: nr - 1, :-2] -= Gz * inv2h
    Gphi_r = Gphi / rho4
    Jb = np.broadcast_to(_J4(), Gphi_r.shape)
    G[: nr - 1, 1:-1] += -(Jb @ Gphi_r - Gphi_r @ Jb)
    return G


def _J4():
    from m5_17_energy import J4
    return J4


def kdot_density(Mnp, Vnp, h=H):
    """d/dt k_apply(M)[V] at fixed V: Adot_i = D_i V."""
    nr = Mnp.shape[0]
    Arho, Aphi, Az, _ = channels(Mnp, h)
    Brho, Bphi, Bz, _ = channels(Vnp, h)
    Vc = Vnp[: nr - 1, 1:-1]
    out = np.zeros_like(Vc)
    for A, B in ((Arho, Brho), (Aphi, Bphi), (Az, Bz)):
        out = out + 2.0 * (_adj(comm_eta_b(Vc, B), A) + _adj(comm_eta_b(Vc, A), B))
    return out


BMAT = BASIS.reshape(10, 16)                    # basis as (10, 16) row matrix


def build_k10(Mnp, h=H):
    """per-cell 10x10 kinetic form (closed form):
    k_apply[X] = 2 SUM_i (eta X W_i + W_i X eta - 2 Y_i X Y_i);
    assembled as the (16, 16) operator K_(ij)(kl) = 2 (eta_ik Wsum_lj
    + Wsum_ik eta_lj - 2 SUM_i Y_ik Y_lj) then projected to the 10-basis
    with two small matmuls (the GC0d gate pins this against the 10-pass
    kin_form_apply build)."""
    Arho, Aphi, Az, _ = channels(Mnp, h)
    A3 = np.stack([Arho, Aphi, Az])                       # (3, nr-1, nz-2, 4, 4)
    Y = ETA @ A3 @ ETA                                    # eta A eta
    W = Y @ A3 @ ETA                                      # eta A eta A eta
    Wsum = W.sum(axis=0)
    sh = Wsum.shape[:-2]
    Kop = (2.0 * np.einsum("ik,...lj->...ijkl", ETA, Wsum)
           + 2.0 * np.einsum("...ik,lj->...ijkl", Wsum, ETA)
           - 4.0 * np.einsum("c...ik,c...lj->...ijkl", Y, Y))
    Kop = Kop.reshape(sh + (16, 16))
    K10 = np.einsum("ai,...ij,bj->...ab", BMAT, Kop, BMAT, optimize=True)
    return 0.5 * (K10 + np.swapaxes(K10, -1, -2))


def build_k10_slow(Mnp, h=H):
    """10-pass cross-check build through kin_form_apply (gate GC0d)."""
    nr, nz = Mnp.shape[:2]
    K10 = np.zeros((nr - 1, nz - 2, 10, 10))
    for b in range(10):
        Vb = np.zeros_like(Mnp)
        Vb[: nr - 1, 1:-1] = BASIS[b]
        pib = kin_form_apply(Mnp, Vb, h)
        K10[..., :, b] = np.einsum("akl,...kl->...a", BASIS, pib)
    return K10


def accel(Mnp, Vnp, wscale, delta, w4, h=H, g=G_T, rel_cut=REL_CUT,
          abs_cut_frac=ABS_CUT_FRAC, rho4=None, want_diag=False):
    """Mddot from the EL solve, per cell, spectral pseudo-inverse.
    Returns (acc_fullgrid, diag)."""
    nr, nz = Mnp.shape[:2]
    G_stat = grad_static_4(Mnp, wscale, delta, h=h, g=g, w4=w4, rho4=rho4)
    GT = grad_m_T(Mnp, Vnp, w4, h=h, rho4=rho4)
    kd = kdot_density(Mnp, Vnp, h=h)
    rhs = ((GT - G_stat)[: nr - 1, 1:-1] / (4.0 * w4)) - kd
    r10 = np.einsum("akl,...kl->...a", BASIS, rhs)
    K10 = build_k10(Mnp, h)
    lam, U = np.linalg.eigh(K10)
    alam = np.abs(lam)
    cut = np.maximum(rel_cut * alam.max(axis=-1, keepdims=True),
                     abs_cut_frac * alam.max())
    active = alam > cut
    rU = np.einsum("...ka,...k->...a", U, r10)
    x = np.where(active, rU / np.where(active, lam, 1.0), 0.0)
    a10 = np.einsum("...ka,...a->...k", U, x)
    acc = np.zeros_like(Mnp)
    acc[: nr - 1, 1:-1] = np.einsum("...a,akl->...kl", a10, BASIS)
    pin = pin_mask(nr, nz)
    acc[pin] = 0.0
    diag = None
    if want_diag:
        r_null = np.where(~active, rU, 0.0)
        nrm = float(np.sqrt(np.sum(rU ** 2)))
        # exact projection-leak rate: dE/dt = - SUM 4 w (V_null . RHS_null)
        v10 = np.einsum("akl,...kl->...a", BASIS, Vnp[: nr - 1, 1:-1])
        vU = np.einsum("...ka,...k->...a", U, v10)
        leak = -float(np.sum(4.0 * w4[..., 0]
                             * np.where(~active, vU, 0.0) * r_null))
        diag = {"null_force_frac": float(np.sqrt(np.sum(r_null ** 2)) / max(nrm, 1e-300)),
                "n_active_mean": float(active.sum(axis=-1).mean()),
                "max_abs_acc": float(np.max(np.abs(acc))),
                "lam_absmax_global": float(alam.max()),
                "lam_min_active": float(np.min(np.where(active, alam, np.inf))),
                "leak_rate": leak}
    return acc, diag


# ---------------- integrator ----------------
def evolve_true(M0, V0, T, dt, wscale, delta, h=H, g=G_T, rel_cut=REL_CUT,
                abs_cut_frac=ABS_CUT_FRAC, snap_every=None, snap_fn=None,
                nan_abort=True, log_snaps=False):
    """velocity Verlet with the velocity-dependent EL force evaluated at the
    half-step velocity (O(dt^2)); ledger E = T + U per snapshot."""
    nr, nz = M0.shape[:2]
    w4 = cell_weights(nr, nz, h)[..., None, None]
    rho4 = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    pin = pin_mask(nr, nz)
    free4 = (~pin)[..., None, None].astype(float)
    if not np.all(np.isfinite(M0)):
        raise ValueError("evolve_true: non-finite initial state")
    Mx = M0.copy()
    v = np.zeros_like(Mx) if V0 is None else V0.copy()
    v *= free4
    n_steps = int(round(T / dt))
    if snap_every is None:
        snap_every = max(1, n_steps // 40)
    recs = []
    t0 = time.time()

    def snap(it, diag):
        ke = float(np.sum(t_density(Mx, v, h) * w4[..., 0, 0]))
        pe = float(e_static_c(Mx, wscale, delta, h, g).real)
        r = {"it": it, "t": it * dt, "KE": ke, "PE": pe, "E_tot": ke + pe}
        if diag:
            r.update(diag)
        if snap_fn is not None:
            r.update(snap_fn(Mx, v))
        recs.append(r)
        if log_snaps:
            print(f"  it {it:7d} t {r['t']:8.2f} KE {ke:10.4f} PE {pe:10.4f} "
                  f"E {r['E_tot']:10.4f} nff {r.get('null_force_frac', -1):.2e}",
                  flush=True)

    a, diag = accel(Mx, v, wscale, delta, w4, h, g, rel_cut, abs_cut_frac,
                    rho4, want_diag=True)
    snap(0, diag)
    for it in range(1, n_steps + 1):
        vh = v + 0.5 * dt * a
        Mx += dt * vh * free4
        if (not np.all(np.isfinite(Mx))) or float(np.max(np.abs(Mx))) > 1e6:
            recs.append({"it": it, "t": it * dt, "KE": float("nan"),
                         "PE": float("nan"), "E_tot": float("nan"),
                         "blowup": True})
            print(f"  BLOWUP at it {it} (t {it * dt:.2f})", flush=True)
            break
        want = (it % snap_every == 0) or (it == n_steps)
        a, diag = accel(Mx, vh, wscale, delta, w4, h, g, rel_cut,
                        abs_cut_frac, rho4, want_diag=want)
        v = (vh + 0.5 * dt * a) * free4
        if want:
            snap(it, diag)
            if nan_abort and not np.all(np.isfinite(Mx)):
                print(f"  NAN ABORT at it {it}", flush=True)
                break
    return Mx, v, recs, time.time() - t0


# ---------------- seeds ----------------
def seed4_grid(nr, nz, delta, pairing, R0=17.0, q=0.5, h=H, g=G_T,
               branch="g_timelike"):
    R, Z = grid_coords(nr, nz, h)
    M = loop_field_biax(R, Z, R0, q, delta, pairing)
    M[..., 0, 0] = vac4(delta, g=g, branch=branch)[0, 0]
    return M


# ---------------- gates ----------------
def _rand_sym_field(shape, rng, mask_included=True):
    D = rng.normal(size=shape)
    D = 0.5 * (D + np.swapaxes(D, -1, -2))
    if mask_included:
        out = np.zeros(shape)
        out[: shape[0] - 1, 1:-1] = D[: shape[0] - 1, 1:-1]
        return out
    return D


def _cs_dir(e_fn, X, D, hstep=1e-30):
    """complex-step directional derivative of a polynomial functional."""
    return float(np.imag(e_fn(X.astype(complex) + 1j * hstep * D)) / hstep)


def gate_gc0a(delta=0.3):
    M = seed4_grid(NR, NZ, delta, "pair_d0")
    rng = np.random.default_rng(7)
    V = _rand_sym_field(M.shape, rng)
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    pi = 4.0 * kin_form_apply(M, V) * w4
    worst = 0.0
    for _ in range(3):
        D = _rand_sym_field(M.shape, rng)
        num = _cs_dir(lambda VV: t_total_c(M, VV), V, D)
        an = float(np.sum(pi * D[: NR - 1, 1:-1]))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-30))
    return worst < 1e-12, {"rel": worst}


def gate_gc0b(delta=0.3):
    M = seed4_grid(NR, NZ, delta, "pair_d0")
    rng = np.random.default_rng(11)
    V = _rand_sym_field(M.shape, rng)
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    GT = grad_m_T(M, V, w4)
    worst = 0.0
    for _ in range(3):
        D = _rand_sym_field(M.shape, rng)
        num = _cs_dir(lambda MM: t_total_c(MM, V), M, D)
        an = float(np.sum(GT * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-30))
    return worst < 1e-10, {"rel": worst}


def gate_gc0c(delta=0.3):
    M = seed4_grid(NR, NZ, delta, "pair_d0")
    rng = np.random.default_rng(13)
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
    G = grad_static_4(M, WSCALE, delta, w4=w4, rho4=rho4)
    worst = 0.0
    for _ in range(3):
        D = _rand_sym_field(M.shape, rng)
        num = _cs_dir(lambda MM: e_static_c(MM, WSCALE, delta), M, D)
        an = float(np.sum(G * D))
        worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-30))
    return worst < 1e-10, {"rel": worst}


def gate_gc0d(delta=0.3):
    M = seed4_grid(NR, NZ, delta, "pair_d0")
    Kf = build_k10(M)
    Ks = build_k10_slow(M)
    scale = max(float(np.max(np.abs(Ks))), 1e-300)
    rel = float(np.max(np.abs(Kf - Ks)) / scale)
    sym = float(np.max(np.abs(Kf - np.swapaxes(Kf, -1, -2))) / scale)
    null = float(np.max(np.abs(np.einsum("...ab,b->...a", Kf, ETA10))) / scale)
    ok = rel < 1e-12 and sym < 1e-12 and null < 1e-12
    return ok, {"rel_fast_vs_slow": rel, "asym": sym, "eta_null_resid": null}


def gate_gc0e(delta=0.3):
    M = seed4_grid(NR, NZ, delta, "pair_d0")
    rng = np.random.default_rng(17)
    V = _rand_sym_field(M.shape, rng)
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    lhs = float(np.sum(grad_m_T(M, V, w4) * V))
    rhs = 2.0 * float(np.sum(w4 * kdot_density(M, V) * V[: NR - 1, 1:-1]))
    rel = abs(lhs - rhs) / (abs(lhs) + abs(rhs) + 1e-30)
    return rel < 1e-10, {"lhs": lhs, "rhs": rhs, "rel": rel}


def gc1_census(delta=0.3):
    """per-cell K10 spectrum maps on the 4D loop seeds + the t = 0
    constraint ledger (recorded physics, not pass/fail)."""
    out = {}
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    for pairing in ("pair_d0", "pair_1d"):
        M = seed4_grid(NR, NZ, delta, pairing)
        K10 = build_k10(M)
        lam = np.linalg.eigvalsh(K10)
        alam = np.abs(lam)
        mx = alam.max(axis=-1)
        cut = np.maximum(REL_CUT * mx[..., None], ABS_CUT_FRAC * alam.max())
        rank = (alam > cut).sum(axis=-1)
        nneg = (lam < -cut).sum(axis=-1)
        _, diag = accel(M, np.zeros_like(M), WSCALE, delta, w4,
                        want_diag=True)
        out[pairing] = {
            "rank_hist": {str(k): int(np.sum(rank == k)) for k in range(11)
                          if np.any(rank == k)},
            "nneg_hist": {str(k): int(np.sum(nneg == k)) for k in range(11)
                          if np.any(nneg == k)},
            "lam_absmax_global": float(alam.max()),
            "lam_absmax_core": float(mx[15:20, 126:130].max()),
            "lam_absmax_far": float(mx[80, 128]),
            "t0_ledger": diag}
        print(f"  [{pairing}] rank_hist {out[pairing]['rank_hist']} "
              f"nneg_hist {out[pairing]['nneg_hist']} "
              f"nff(t=0) {diag['null_force_frac']:.3e}", flush=True)
    return out


def benchmark(delta=0.3):
    out = {}
    for (nr, nz) in ((128, 256), (64, 128)):
        M = seed4_grid(nr, nz, delta, "pair_d0")
        V = np.zeros_like(M)
        w4 = cell_weights(nr, nz, H)[..., None, None]
        accel(M, V, WSCALE, delta, w4)          # warm-up
        t0 = time.time()
        n = 5
        for _ in range(n):
            accel(M, V, WSCALE, delta, w4)
        dtm = (time.time() - t0) / n
        out[f"{nr}x{nz}"] = {"accel_s": dtm}
        print(f"  accel at {nr}x{nz}: {dtm:.3f} s", flush=True)
    return out


def main():
    os.makedirs(DATA, exist_ok=True)
    out = {"task": "M5.20.3", "phase": "A", "wscale": WSCALE, "g": G_T,
           "rel_cut": REL_CUT, "abs_cut_frac": ABS_CUT_FRAC,
           "eom": "free EL of the purely-quartic verified L; null projected"}
    allok = True
    for name, fn in [("GC0a", gate_gc0a), ("GC0b", gate_gc0b),
                     ("GC0c", gate_gc0c), ("GC0d", gate_gc0d),
                     ("GC0e", gate_gc0e)]:
        ok, detail = fn()
        allok = allok and ok
        out[name] = {"ok": bool(ok), "detail": detail}
        print(f"[{name}] {'PASS' if ok else 'FAIL'} "
              + json.dumps(detail, default=float)[:200], flush=True)
    print("[GC1] census (recorded)", flush=True)
    out["GC1_census"] = gc1_census()
    print("[BENCH]", flush=True)
    out["benchmark"] = benchmark()
    out["all_gc0_pass"] = bool(allok)
    with open(os.path.join(DATA, "m5_20_3_a_gates.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"ALL GC0 {'PASS' if allok else 'FAIL'}; "
          "wrote data/m5_20_3_a_gates.json", flush=True)
    return out


if __name__ == "__main__":
    main()
