"""M5.20.4 arm A: the time-periodic least-action BVP at the RIGID-ORBIT
level, re-derived on the CURRENT M5.20 verified-L instrument.

WHY RIGID FIRST (tasks/m5_20_4_task_details.md): the M5.12 phase-D
Fourier container carries era drift (its V_4D predates the 4-target
stack); the rigid level answers the EXISTENCE question with the current
gated instrument, and the Fourier profile relaxation only makes sense
if the rigid level signals.

THE DERIVATION (free-period least action on conjugation orbits):
    orbit ansatz   M(x, t) = Lam(w t) M0(x) Lam(w t)^T ,
                   Lam = exp(w t G),  G in so(1,3)
    Mdot = w D_G M0,  D_G M = G M + M G^T
    T(w) = w^2 Q2,   Q2 := T_true(M0, D_G M0)   (the TRUE quartic
                     kinetic form: t_total_c of m5_20_3_a_constraint)
    S(w) = (2 pi / w) (w^2 Q2 - U) ,  U = static energy
    dS/dw = 0  =>  w*^2 = -U / Q2   (the balance root)  and the exact
    identity H = w*^2 Q2 + U = 0 at the root (the M5.12 H_mean = 0,
    re-derived for the quartic Q2).
    EXISTENCE therefore needs sign(U) != sign(Q2): with Q2 > 0 the
    root demands U < 0, i.e. the M5.18 statics indefiniteness (the
    author's "negative Hamiltonian terms propel ... angular momentum").

CLOSURE LEMMA: only ROTATION generators exponentiate periodically
(boosts are non-compact: exp(w t K) never returns), so rigid PERIODIC
orbits exist only for G in span{J12, J13, J23} (+ elliptic conjugates).
Boost generators are still tabulated (Q2 sign census) but excluded
from root claims.

PHASES
    gates  AG1 gradQ2 == complex-step (both the fixed-V and the
           orbit-direction chain), AG2 T(w D) = w^2 T(D) exactness,
           AG3 vacuum: Q2(vac) = 0 for every generator (K = 0 on
           uniform states => the trivial root is the vacuum).
    a1     generator x background census: Q2, U, root w* (or NONE),
           on recipe / remnant seeds.
    a2     the U < 0 family: static time-mixing dressing scans
           (inject 'clock' bumps: amp x width grid): does U cross 0
           in the loop sector (q intact)?
    a3     the fixed-w action ladder: minimize Shat_num = U - w^2 Q2
           (the M5.12 numeric convention; bounded below by the V4
           ~ M^8 growth) over M at fixed w (FIRE, dt_max 0.02 = the
           audit-safe cap), for a w ladder; report U, Q2, H, q, ring
           per w; a sign change of H(w) with q intact = a rigid
           particle-clock bracket; collapse to vacuum = the trivial
           root (reported as such).

Run:  python m5_20_4_a_bvp.py gates|a1|a2|a3
Out:  ../data/m5_20_4_a_<phase>.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import fire_relax, pin_mask                      # noqa: E402
from m5_17_energy import cell_weights, grid_coords                 # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_20_1_b_seeds import winding_measure_biax                   # noqa: E402
from m5_20_2_a_eom import (G_T, WSCALE, grad_static_4,             # noqa: E402
                           kin_form_apply, total_energy_4, vac4)
from m5_20_3_a_constraint import (_cs_dir, e_static_c, grad_m_T,   # noqa: E402
                                  seed4_grid, t_total_c)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NR, NZ, H = 64, 128, 1.0
DELTA = 0.3
R0 = 17.0
W4 = cell_weights(NR, NZ, H)[..., None, None]
RHO4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]


def gen(name):
    """so(1,3) generators; rotations J_kl, boosts K_k (index 0 = time)."""
    G = np.zeros((4, 4))
    if name.startswith("J"):
        k, l = int(name[1]), int(name[2])
        G[k, l], G[l, k] = -1.0, 1.0
    elif name.startswith("K"):
        k = int(name[1])
        G[0, k] = G[k, 0] = 1.0
    else:
        raise ValueError(name)
    return G


ROTS = ("J12", "J13", "J23")
BOOSTS = ("K1", "K2", "K3")


def d_g(M, G):
    return G @ M + M @ G.T


def q2_of(M, G, h=H):
    """Q2 = T_true(M, D_G M) (weights + the audited factor 4 included)."""
    return float(t_total_c(M, d_g(M, G), h).real)


def u_of(M):
    return float(e_static_c(M, WSCALE, DELTA).real)


def grad_q2(M, G, h=H, w4=None, rho4=None):
    """dQ2/dM = grad_m_T(M, V)|_{V = D_G M}  (fixed-V piece, stencil-
    scattered, w-folded)  +  w [pi, G]-chain (the orbit-direction
    piece): d<pi, D_G dM> = w4 * 4 [k_apply(V) G^T-fold] placed at
    cells; for any G: contribution = 4 w (pi G + G^T pi) with
    pi = k_apply(V) (symmetric), since
    tr(pi (G dM + dM G^T)) = tr((pi G + G^T pi) dM)."""
    nr = M.shape[0]
    if w4 is None:
        w4 = cell_weights(nr, M.shape[1], h)[..., None, None]
    V = d_g(M, G)
    Gr = grad_m_T(M, V, w4, h=h, rho4=rho4)
    pi = kin_form_apply(M, V, h)              # k_apply(V), per cell
    chain = pi @ G + G.T @ pi
    Gr[: nr - 1, 1:-1] += 4.0 * w4 * chain
    return Gr


def loop_reads(M):
    rd = ring_by_m13(M, NR, NZ, H)
    qm, _ = winding_measure_biax(M, NR, NZ, H, rd["ring13_rho"],
                                 rd["ring13_z"])
    return {"ring_rho": float(rd["ring13_rho"]),
            "q_r4": None if not np.isfinite(qm) else float(qm)}


def load_seed(kind):
    if kind == "raw":
        return seed4_grid(NR, NZ, DELTA, "pair_d0", R0=R0)
    fn = {"recipe": "m5_20_3_b_seed_recipe.npz",
          "remnant": "m5_20_3_b_seed_remnant.npz"}[kind]
    return np.load(os.path.join(DATA, fn))["M"]


def inject_clock(M, amp, sig, center=(17.0, 0.0)):
    """static time-mixing dressing (the B5 'clock' sector bump)."""
    R, Z = grid_coords(NR, NZ, H)
    bump = amp * np.exp(-((R - center[0]) ** 2 + (Z - center[1]) ** 2)
                        / (2 * sig ** 2))
    out = M.copy()
    out[..., 0, 1] += bump
    out[..., 1, 0] += bump
    return out


# ---------------- gates ----------------
def phase_gates(seed=3):
    rng = np.random.default_rng(seed)
    M = load_seed("recipe")
    M = M + 0.03 * _rand_sym(M.shape, rng)
    out = {}
    # AG1: gradQ2 == complex-step (the full chain)
    worst = 0.0
    for G in (gen("J23"), gen("K1")):
        D = _rand_sym(M.shape, rng)
        lhs = float(np.sum(grad_q2(M, G, w4=W4, rho4=RHO4) * D))
        rhs = _cs_dir(lambda MM: t_total_c(MM, d_g(MM, G)), M, D)
        worst = max(worst, abs(lhs - rhs) / max(abs(rhs), 1e-12))
    out["ag1_gradq2"] = worst
    # AG2: T(w D) = w^2 T(D)
    G = gen("J23")
    t1 = float(t_total_c(M, d_g(M, G)).real)
    t3 = float(t_total_c(M, 3.0 * d_g(M, G)).real)
    out["ag2_quadratic"] = abs(t3 - 9.0 * t1) / max(abs(t1), 1e-300)
    # AG3: a genuinely gradient-free uniform state (rotation-invariant
    # transverse block, so the equivariant A_phi = [J, M]/rho vanishes
    # too) has K = 0 => Q2 = 0 for every generator. NOTE the co-rotating
    # VACUUM is not such a state: its biaxial frame texture carries
    # A_phi != 0 and real Q2 (measured ~1e6: the arm-C texture).
    Mv = np.broadcast_to(np.diag([-G_T, 1.0, 1.0, 0.0]),
                         (NR, NZ, 4, 4)).copy()
    out["ag3_uniform_q2_max"] = max(
        abs(q2_of(Mv, gen(n))) for n in ROTS + BOOSTS)
    out["ag3_corot_vacuum_q2_J23"] = q2_of(
        np.broadcast_to(vac4(DELTA), (NR, NZ, 4, 4)).copy(), gen("J23"))
    ok = out["ag1_gradq2"] < 1e-8 and out["ag2_quadratic"] < 1e-12 \
        and out["ag3_uniform_q2_max"] < 1e-20
    out["pass"] = bool(ok)
    with open(os.path.join(DATA, "m5_20_4_a_gates.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[A GATES] ag1 {out['ag1_gradq2']:.1e} ag2 "
          f"{out['ag2_quadratic']:.1e} ag3 {out['ag3_uniform_q2_max']:.1e} "
          f"(corot-vac Q2_J23 = {out['ag3_corot_vacuum_q2_J23']:.3e}) "
          f"-> {'PASS' if ok else 'FAIL'}", flush=True)
    return out


def _rand_sym(shape, rng):
    D = rng.normal(size=shape)
    D = 0.5 * (D + np.swapaxes(D, -1, -2))
    out = np.zeros(shape)
    out[: shape[0] - 1, 1:-1] = D[: shape[0] - 1, 1:-1]
    return out


# ---------------- a1: generator x background census ----------------
def phase_a1():
    out = {}
    for tag in ("recipe", "remnant"):
        M = load_seed(tag)
        U = u_of(M)
        rows = {}
        for name in ROTS + BOOSTS:
            Q2 = q2_of(M, gen(name))
            periodic = name in ROTS
            root = None
            if periodic and Q2 != 0.0 and U * Q2 < 0.0:
                root = float(np.sqrt(-U / Q2))
            rows[name] = {"Q2": Q2, "periodic_closure": periodic,
                          "root_omega": root}
        out[tag] = {"U": U, "generators": rows, **loop_reads(M)}
        print(f"[A1] {tag}: U = {U:.4f}; " + " ".join(
            f"{n}:Q2={rows[n]['Q2']:.3e}"
            f"{'*' if rows[n]['root_omega'] else ''}"
            for n in rows), flush=True)
    with open(os.path.join(DATA, "m5_20_4_a_a1.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- a1b: elliptic (boost-conjugated rotation) orbits ----
def conj_gen(rot, boost, chi):
    """G' = B J B^-1 with B = exp(chi K): EXACTLY periodic for every chi
    (conjugation preserves closure: exp(t G') = B exp(t J) B^-1), yet
    carries boost content: the clock seen from a boosted internal frame.
    Only non-commuting (rot, boost) pairs give chi-dependence."""
    from scipy.linalg import expm
    B = expm(chi * gen(boost))
    Bi = expm(-chi * gen(boost))
    return B @ gen(rot) @ Bi


PAIRS = (("J23", "K2"), ("J23", "K3"), ("J13", "K1"), ("J13", "K3"),
         ("J12", "K1"), ("J12", "K2"))


def phase_a1b(tag="recipe", chis=None):
    """Q2 along the elliptic families: a sign crossing means a PERIODIC
    orbit direction with Q2 < 0, i.e. a balance root with U > 0:
    omega* = sqrt(-U / Q2). The S-extremal chi* is where dQ2/dchi = 0
    on the negative branch (S* = -4 pi U / omega*)."""
    chis = chis if chis is not None else np.linspace(0.0, 2.5, 26)
    M = load_seed(tag)
    U = u_of(M)
    out = {"tag": tag, "U": U, "families": {}}
    for rot, boost in PAIRS:
        q2s = [q2_of(M, conj_gen(rot, boost, float(c))) for c in chis]
        roots = [float(np.sqrt(-U / q)) if U * q < 0 else None
                 for q in q2s]
        fam = {"chi": [float(c) for c in chis], "Q2": q2s,
               "root_omega": roots}
        # the S-extremal chi on the negative branch (max of Q2<0, i.e.
        # min |Q2| is the omega->inf edge; the interior dQ2/dchi = 0
        # extremum is the stationary one: take the MOST NEGATIVE Q2 as
        # the deep-branch marker and any interior extremum)
        neg = [(c, q) for c, q in zip(chis, q2s) if q < 0]
        if neg:
            fam["first_crossing_chi"] = float(neg[0][0])
            cdeep, qdeep = min(neg, key=lambda t: t[1])
            fam["deepest"] = {"chi": float(cdeep), "Q2": float(qdeep),
                              "root_omega": float(np.sqrt(-U / qdeep))
                              if U > 0 else None}
        out["families"][f"{rot}^{boost}"] = fam
        rng = (f"crossing at chi={fam.get('first_crossing_chi')}"
               if neg else "no crossing")
        print(f"[A1b {tag}] {rot}^{boost}: Q2 {q2s[0]:.3e} -> "
              f"{q2s[-1]:.3e}; {rng}", flush=True)
    with open(os.path.join(DATA, f"m5_20_4_a_a1b_{tag}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- a1c: the AUDIT-CORRECTED (phi-averaged) Q2 ----------
def q2_avg(M, G, nphi=24):
    """the 3D orbit kinetic at t = 0, computed correctly on the slice.
    AUDIT CORRECTION (2026-07-14, C7): internal conjugation breaks the
    axisym equivariance (A_phi = [J12, M]/rho is equivariant only under
    the J12-commutant), so the slice formula q2_of(M, D_G M) is NOT the
    3D integral for G outside the commutant. For the true 3D field the
    density at azimuth phi equals the slice density with the generator
    rotated, G_phi = e^{-phi J12} G e^{phi J12}; the 3D Q2 is the
    phi-average. (T and U ARE constant along the 3D conjugation orbit:
    global internal conjugation is an eta-similarity at every point, so
    only the t = 0 average is needed.)"""
    from scipy.linalg import expm
    J = gen("J12")
    vals = []
    for phi in np.linspace(0.0, 2 * np.pi, nphi, endpoint=False):
        Gp = expm(-phi * J) @ G @ expm(phi * J)
        vals.append(q2_of(M, Gp))
    return float(np.mean(vals)), float(np.std(vals))


def phase_a1c(tag="recipe", chis=None, nphi=16):
    """the a1b elliptic-family scan under the CORRECTED Q2: does the
    sign crossing (and so the balance-root family) survive?"""
    chis = chis if chis is not None else np.linspace(0.0, 2.5, 11)
    M = load_seed(tag)
    U = u_of(M)
    out = {"tag": tag, "U": U, "nphi": nphi, "families": {}}
    for rot, boost in PAIRS:
        rows = []
        for c in chis:
            q2m, q2s = q2_avg(M, conj_gen(rot, boost, float(c)), nphi)
            rows.append({"chi": float(c), "Q2_avg": q2m,
                         "Q2_std_over_phi": q2s,
                         "root_omega": float(np.sqrt(-U / q2m))
                         if U * q2m < 0 else None})
        neg = [r for r in rows if r["Q2_avg"] < 0]
        fam = {"rows": rows,
               "first_crossing_chi": neg[0]["chi"] if neg else None}
        out["families"][f"{rot}^{boost}"] = fam
        print(f"[A1c {tag}] {rot}^{boost}: Q2_avg {rows[0]['Q2_avg']:.3e}"
              f" -> {rows[-1]['Q2_avg']:.3e}; "
              + (f"crossing at chi={fam['first_crossing_chi']}"
                 if neg else "NO crossing"), flush=True)
    with open(os.path.join(DATA, f"m5_20_4_a_a1c_{tag}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- a2: the U < 0 family ----------------
def phase_a2():
    M0 = load_seed("recipe")
    out = {"base_U": u_of(M0)}
    rows = []
    for sig in (1.5, 3.0, 6.0):
        for amp in (0.05, 0.1, 0.2, 0.4, 0.8):
            M = inject_clock(M0, amp, sig)
            U = u_of(M)
            r = {"amp": amp, "sig": sig, "U": U,
                 "Q2_J23": q2_of(M, gen("J23")), **loop_reads(M)}
            r["root_omega"] = (float(np.sqrt(-U / r["Q2_J23"]))
                               if U * r["Q2_J23"] < 0 and r["Q2_J23"] != 0
                               else None)
            rows.append(r)
            print(f"[A2] amp {amp} sig {sig}: U = {U:.4f} "
                  f"Q2 = {r['Q2_J23']:.3e} q = {r['q_r4']} "
                  f"root = {r['root_omega']}", flush=True)
    out["scan"] = rows
    with open(os.path.join(DATA, "m5_20_4_a_a2.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- a4: orbit-residual + descent on |grad Shat|^2 ------
def grad_shat(M, G, omega):
    """grad of Shat = w^2 Q2 - U; a rigid orbit solves the field EL iff
    this vanishes (with the free-period root already imposing H = 0)."""
    return omega ** 2 * grad_q2(M, G, w4=W4, rho4=RHO4) \
        - grad_static_4(M, WSCALE, DELTA, w4=W4, rho4=RHO4)


def phase_a4(rot="J23", boost="K2", chi=2.5, iters=120):
    """at the deepest measured root: how far is the recipe seed from a
    TRUE extremal orbit? residual |grad Shat| / |G_static|, then
    steepest descent on Phi = 1/2 |grad Shat|^2 (Hessian-vector by
    complex step): dropping residual = an orbit solution nearby."""
    M = load_seed("recipe").astype(float)
    G = conj_gen(rot, boost, chi)
    U = u_of(M)
    Q2 = q2_of(M, G)
    if U * Q2 >= 0:
        print(f"[A4] no root at chi={chi} (U {U:.3e}, Q2 {Q2:.3e})",
              flush=True)
        return None
    omega = float(np.sqrt(-U / Q2))
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)

    def gnorm(MM):
        g = grad_shat(MM, G, omega) * free4
        return g, float(np.sqrt(np.sum(g ** 2)))

    g0, n0 = gnorm(M)
    gs, ns = gnorm(M)
    nstat = float(np.sqrt(np.sum(
        (grad_static_4(M, WSCALE, DELTA, w4=W4, rho4=RHO4) * free4) ** 2)))
    hist = [{"it": 0, "phi_gnorm": n0, "rel_to_static": n0 / nstat}]
    print(f"[A4] {rot}^{boost} chi={chi}: U {U:.4f} Q2 {Q2:.3e} "
          f"omega* {omega:.4e}; |gradShat|/|G_static| = {n0/nstat:.4f}",
          flush=True)
    Mx = M.copy()
    step = 1e-6
    eps = 1e-30
    for it in range(1, iters + 1):
        # grad Phi = Hess(Shat) . gradShat, by complex step along g
        gx, nx = gnorm(Mx)
        try:
            gc = grad_shat(Mx.astype(complex) + 1j * eps * gx, G, omega)
            hv = np.imag(gc) / eps * free4
        except Exception:                                    # noqa: BLE001
            h = 1e-6
            hv = (grad_shat(Mx + h * gx, G, omega)
                  - grad_shat(Mx - h * gx, G, omega)) / (2 * h) * free4
        dphi = hv
        ndp = float(np.sqrt(np.sum(dphi ** 2)))
        if ndp == 0:
            break
        # backtracking on Phi = 1/2 nx^2
        ok = False
        for _ in range(20):
            Mt = Mx - step * dphi
            _, nt = gnorm(Mt)
            if nt < nx:
                Mx, ok = Mt, True
                step *= 1.5
                break
            step *= 0.4
        if not ok:
            break
        if it % 20 == 0 or it == iters:
            _, ncur = gnorm(Mx)
            hist.append({"it": it, "phi_gnorm": ncur,
                         "rel_to_static": ncur / nstat})
            print(f"  [A4] it {it}: |gradShat| {ncur:.6e} "
                  f"({ncur/n0:.4f} of start)", flush=True)
    _, nf = gnorm(Mx)
    Uf, Q2f = u_of(Mx), q2_of(Mx, G)
    out = {"rot": rot, "boost": boost, "chi": chi, "omega": omega,
           "U": U, "Q2": Q2, "resid_start": n0, "resid_final": nf,
           "resid_reduction": nf / n0, "rel_to_static_start": n0 / nstat,
           "final_U": Uf, "final_Q2": Q2f,
           "final_H_at_fixed_omega": Uf + omega ** 2 * Q2f,
           "final_root_omega": float(np.sqrt(-Uf / Q2f))
           if Uf * Q2f < 0 else None,
           "hist": hist, **loop_reads(Mx)}
    np.savez_compressed(os.path.join(DATA, "m5_20_4_a_a4_state.npz"),
                        M=Mx)
    with open(os.path.join(DATA, "m5_20_4_a_a4.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[A4] residual {n0:.4e} -> {nf:.4e} "
          f"(x{nf/n0:.4f}); q = {out['q_r4']}", flush=True)
    return out


# ---------------- a3: the fixed-w action ladder ----------------
def relax_shat(M0, omega, Gname="J23", iters=2000, chunk=400):
    """FIRE-minimize Shat_num = U - w^2 Q2 at fixed w (free 4D, the
    audit-safe dt_max 0.02)."""
    G = gen(Gname)
    pin = pin_mask(NR, NZ)
    free4 = (~pin)[..., None, None].astype(float)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = W4[..., 0, 0]
    precond = (1.0 / wfull)[..., None, None]

    def egf(MM):
        E = u_of(MM) - omega ** 2 * q2_of(MM, G)
        Gr = grad_static_4(MM, WSCALE, DELTA, w4=W4, rho4=RHO4) \
            - omega ** 2 * grad_q2(MM, G, w4=W4, rho4=RHO4)
        return E, Gr

    Mx = M0.copy()
    hist = []
    done = 0
    with np.errstate(all="ignore"):
        while done < iters:
            Mx, hh = fire_relax(Mx, egf, free4, precond, max_iter=chunk,
                                tol_rel=1e-9, dt0=0.002, dt_max=0.02,
                                log_every=chunk)
            done += hh["iter"][-1]
            U = u_of(Mx)
            Q2 = q2_of(Mx, G)
            rec = {"it": done, "Shat": hh["E"][-1], "gnorm": hh["gnorm"][-1],
                   "U": U, "Q2": Q2, "H": U + omega ** 2 * Q2,
                   **loop_reads(Mx)}
            hist.append(rec)
            print(f"  [a3 w={omega}] it {done}: Shat {rec['Shat']:.4f} "
                  f"U {U:.4f} Q2 {Q2:.3e} H {rec['H']:.4f} "
                  f"q {rec['q_r4']}", flush=True)
            if not np.isfinite(hh["E"][-1]):
                rec["diverged"] = True
                break
            if hh["iter"][-1] < chunk:
                break
    return Mx, hist


def phase_a3(omegas=(0.05, 0.1, 0.2, 0.4, 0.8, 1.6), Gname="J23"):
    M0 = load_seed("recipe")
    out = {"generator": Gname, "ladder": []}
    for w in omegas:
        Mx, hist = relax_shat(M0, w, Gname)
        rec = {"omega": w, "final": hist[-1] if hist else None,
               "hist": hist}
        out["ladder"].append(rec)
        np.savez_compressed(
            os.path.join(DATA, f"m5_20_4_a_a3_w{w:g}.npz"), M=Mx)
        with open(os.path.join(DATA, "m5_20_4_a_a3.json"), "w") as f:
            json.dump(out, f, indent=1, default=float)
    hs = [(r["omega"], r["final"]["H"], r["final"]["q_r4"])
          for r in out["ladder"] if r["final"]]
    print("[A3] H(w) ladder: " + " ".join(
        f"w={w}:H={hv:.4f}(q={q})" for w, hv, q in hs), flush=True)
    return out


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "gates"
    if which == "gates":
        phase_gates()
    elif which == "a1":
        phase_a1()
    elif which == "a1b":
        phase_a1b(ARGV[1] if len(ARGV) > 1 else "recipe")
    elif which == "a1c":
        phase_a1c(ARGV[1] if len(ARGV) > 1 else "recipe")
    elif which == "a2":
        phase_a2()
    elif which == "a3":
        phase_a3()
    elif which == "a4":
        phase_a4(chi=float(ARGV[1]) if len(ARGV) > 1 else 2.5)
    else:
        raise SystemExit(f"unknown phase {which}")
