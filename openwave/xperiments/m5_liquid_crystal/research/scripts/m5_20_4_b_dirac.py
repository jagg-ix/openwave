"""M5.20.4 arm B: Dirac consistent initial data for the true-L dynamics.

QUESTION (pre-registered, tasks/m5_20_4_task_details.md): the from-rest
EL-inconsistency (M5.20.3: 98.6% of the static force lies in the null
space of K at V = 0) says loop seeds AT REST are off the theory's
constraint surface. Find data ON the surface and measure whether the
IVP is well-posed there.

STRUCTURE. The primary constraints are automatic in velocity space:
pi = K(M) V has EXACTLY zero component along null(K) for every V, so
"pi_null = 0" never restricts V. The consistency (secondary) condition
is on the FORCE: the EL solve's right-hand side

    rhs(M, V) = (gradM_T(M, V) - G_static(M)) / (4w) - kdot(M, V)

must have vanishing null-space components, else no acceleration exists
that satisfies the null rows (the M5.20.3 ledger's leak). At V = 0 the
condition reduces to null(K)^T G_static = 0 (violated at 98.6%).

THE VELOCITY ROUTE (b2). "Rest" is ambiguous under a degenerate K:
null velocities V = U_null c carry ZERO momentum and ZERO kinetic
energy (K V = 0 => T = 1/2 V.K.V = 0), yet they DO enter rhs through
gradM_T (quadratic in V) and kdot (bilinear in V, grad V). So consistent
initial data can be sought at zero energy cost: solve

    r(c) = [rhs(M, U_null(M) c)]_null = 0

a SQUARE system (per cell: dim null(K) equations in dim null(K)
unknowns, coupled across cells through the V-gradients in kdot and the
gradM_T stencils), solved matrix-free (Newton-Krylov, residual-only).

    b1  the from-rest inconsistency card (per-sector breakdown)
    b2  the zero-energy consistent-data solve (JFNK)
    b3  evolve from (M, V*): nff(t), leak ledger, t* vs the off-surface
        baseline t* = 0.53 (recipe, rel_cut 1e-2): does the blowup
        persist ON the surface?
    b4  (only if b2 finds no solution) the config route: is the surface
        empty near loop states?

Run:  python m5_20_4_b_dirac.py b1|b2|b2b|b3
      (b2b = the range diagnostic behind the b2 stall: alignment of
       velocity-reachable null-force changes with the direction that
       must be cancelled)
Out:  ../data/m5_20_4_b_<gate>.json
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

from m5_17_energy import cell_weights                              # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_20_1_b_seeds import winding_measure_biax                   # noqa: E402
from m5_20_2_a_eom import G_T, WSCALE, grad_static_4               # noqa: E402
from m5_20_3_a_constraint import (BASIS, REL_CUT, ABS_CUT_FRAC,    # noqa: E402
                                  build_k10, evolve_true, grad_m_T,
                                  kdot_density, t_total_c)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NR, NZ, H = 64, 128, 1.0
DELTA = 0.3
W4 = cell_weights(NR, NZ, H)[..., None, None]
RHO4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]


def load_recipe():
    return np.load(os.path.join(DATA, "m5_20_3_b_seed_recipe.npz"))["M"]


def null_basis(Mnp, rel_cut=REL_CUT, abs_cut_frac=ABS_CUT_FRAC):
    """per-cell eigendecomposition of K10; returns (lam, U, null_mask)."""
    K10 = build_k10(Mnp, H)
    lam, U = np.linalg.eigh(K10)
    alam = np.abs(lam)
    cut = np.maximum(rel_cut * alam.max(axis=-1, keepdims=True),
                     abs_cut_frac * alam.max())
    return lam, U, alam <= cut


def rhs_10(Mnp, Vnp):
    """the EL right-hand side in the 10-basis (complex-safe)."""
    nr = Mnp.shape[0]
    G_stat = grad_static_4(Mnp, WSCALE, DELTA, h=H, g=G_T, w4=W4, rho4=RHO4)
    GT = grad_m_T(Mnp, Vnp, W4, h=H, rho4=RHO4)
    kd = kdot_density(Mnp, Vnp, h=H)
    rhs = ((GT - G_stat)[: nr - 1, 1:-1] / (4.0 * W4)) - kd
    return np.einsum("akl,...kl->...a", BASIS, rhs)


def v_of_c(cvec, U, nmask):
    """assemble the full-grid V field from the packed null coefficients."""
    c10 = np.zeros(nmask.shape, dtype=cvec.dtype)
    c10[nmask] = cvec
    v10 = np.einsum("...ka,...a->...k", U, c10)
    V = np.zeros((NR, NZ, 4, 4), dtype=cvec.dtype)
    V[: NR - 1, 1:-1] = np.einsum("...a,akl->...kl", v10, BASIS)
    return V


def resid_null(cvec, M, U, nmask):
    """r(c): the null components of rhs at V = U_null c (packed)."""
    V = v_of_c(cvec, U, nmask)
    r10 = rhs_10(M, V)
    rU = np.einsum("...ka,...k->...a", U, r10)
    return rU[nmask]


def b1():
    M = load_recipe()
    lam, U, nmask = null_basis(M)
    r10 = rhs_10(M, np.zeros_like(M))
    rU = np.einsum("...ka,...k->...a", U, r10)
    tot = float(np.sqrt(np.sum(rU ** 2)))
    nul = float(np.sqrt(np.sum(np.where(nmask, rU, 0.0) ** 2)))
    # sector breakdown of the null force (which 10-basis sectors feed it)
    rnull10 = np.einsum("...ka,...a->...k", U, np.where(nmask, rU, 0.0))
    sec = {f"b{k}": float(np.sqrt(np.sum(rnull10[..., k] ** 2)))
           for k in range(10)}
    out = {"null_force_frac": nul / max(tot, 1e-300),
           "null_dim_mean": float(nmask.sum(-1).mean()),
           "null_dim_hist": {str(k): int((nmask.sum(-1) == k).sum())
                             for k in range(11)},
           "sector_norms": sec}
    with open(os.path.join(DATA, "m5_20_4_b_b1.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[B1] from-rest nff = {out['null_force_frac']:.4f}, null dim "
          f"mean {out['null_dim_mean']:.2f}", flush=True)
    return out


def b2(maxiter=60, seed=0):
    """NOTE the structure: gradM_T and kdot are both exactly quadratic
    in V, so r(c) = r0 + Q(c, c) (NO linear term: the Jacobian at c = 0
    vanishes). Newton cannot start at 0; multi-start random c0 with
    scale escalation (try cap 3 scales x 2 seeds)."""
    from scipy.optimize import newton_krylov
    from scipy.optimize import NoConvergence
    M = load_recipe()
    lam, U, nmask = null_basis(M)
    n = int(nmask.sum())
    r0n = float(np.linalg.norm(resid_null(np.zeros(n), M, U, nmask)))
    print(f"[B2] unknowns {n}, |r(0)| = {r0n:.4e}", flush=True)
    t0 = time.time()
    sol, converged, hist = None, False, []

    def F(c):
        r = resid_null(c, M, U, nmask)
        hist.append(float(np.linalg.norm(r)))
        return r

    best, bestn = None, np.inf
    for scale in (0.05, 0.2, 0.5):
        for sd in (seed, seed + 1):
            rng = np.random.default_rng(sd)
            c0 = scale * rng.normal(size=n)
            try:
                sol = newton_krylov(F, c0, maxiter=maxiter, f_tol=1e-9,
                                    method="lgmres", verbose=False)
                converged = True
            except NoConvergence as e:
                sol = np.asarray(e.args[0])
            except Exception as e:                           # noqa: BLE001
                print(f"[B2] solver error (scale {scale}): {e}",
                      flush=True)
                sol = None
            if sol is not None:
                rn = float(np.linalg.norm(resid_null(sol, M, U, nmask)))
                print(f"  [B2] scale {scale} seed {sd}: |r| -> {rn:.4e} "
                      f"({'CONV' if converged else 'no-conv'})",
                      flush=True)
                if rn < bestn:
                    best, bestn = sol.copy(), rn
            if converged:
                break
        if converged:
            break
    sol = best
    r0 = resid_null(np.zeros(n), M, U, nmask)
    wall = time.time() - t0
    out = {"n_unknowns": n, "r0_norm": float(np.linalg.norm(r0)),
           "converged": bool(converged), "wall_s": round(wall, 1),
           "resid_hist_tail": hist[-20:]}
    if sol is not None:
        rfin = resid_null(sol, M, U, nmask)
        V = v_of_c(sol, U, nmask)
        ke = float(t_total_c(M, V, H).real)
        out.update({"r_final_norm": float(np.linalg.norm(rfin)),
                    "r_reduction": float(np.linalg.norm(rfin)
                                         / np.linalg.norm(r0)),
                    "V_max": float(np.max(np.abs(V))),
                    "V_rms": float(np.sqrt(np.mean(V ** 2))),
                    "KE_of_Vstar": ke})
        np.savez_compressed(os.path.join(DATA, "m5_20_4_b_vstar.npz"),
                            V=V, c=sol)
    with open(os.path.join(DATA, "m5_20_4_b_b2.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[B2] converged={converged} |r| {out['r0_norm']:.3e} -> "
          f"{out.get('r_final_norm', float('nan')):.3e} "
          f"(KE of V* = {out.get('KE_of_Vstar')}) wall {wall:.0f}s",
          flush=True)
    return out


def b2b(nsamp=24, seed=7):
    """the range diagnostic behind b2's stall: for random velocities
    (null-only AND full), how much of the induced null-force change
    dr = r(V) - r0 aligns with the direction r0 that must be cancelled?
    alignment ~ 0 for every sample = the consistency condition cannot
    be met by ANY velocity at this M (a measured obstruction, not a
    solver failure)."""
    rng = np.random.default_rng(seed)
    M = load_recipe()
    lam, U, nmask = null_basis(M)
    n = int(nmask.sum())
    r0 = resid_null(np.zeros(n), M, U, nmask)
    r0h = r0 / np.linalg.norm(r0)
    rows = {"null_only": [], "full_V": []}
    for _ in range(nsamp // 2):
        for kind in ("null_only", "full_V"):
            if kind == "null_only":
                c = 0.3 * rng.normal(size=n)
                V = v_of_c(c, U, nmask)
            else:
                V = 0.3 * rng.normal(size=(NR, NZ, 4, 4))
                V = 0.5 * (V + np.swapaxes(V, -1, -2))
                z = np.zeros_like(V)
                z[: NR - 1, 1:-1] = V[: NR - 1, 1:-1]
                V = z
            r10 = rhs_10(M, V)
            rU = np.einsum("...ka,...k->...a", U, r10)
            r = rU[nmask]
            dr = r - r0
            ndr = np.linalg.norm(dr)
            rows[kind].append({
                "dr_norm": float(ndr),
                "align_r0": float(np.dot(dr, r0h) / max(ndr, 1e-300)),
                "resid_after_bestscale": float(np.linalg.norm(
                    r0 - np.dot(dr, r0h) * r0h)) / np.linalg.norm(r0)})
    out = {"r0_norm": float(np.linalg.norm(r0)), "samples": rows}
    for kind in rows:
        al = [abs(s["align_r0"]) for s in rows[kind]]
        out[f"{kind}_align_max"] = max(al)
        out[f"{kind}_align_mean"] = float(np.mean(al))
        print(f"[B2b] {kind}: |align(dr, r0)| mean {np.mean(al):.3e} "
              f"max {max(al):.3e} over {len(al)} samples", flush=True)
    with open(os.path.join(DATA, "m5_20_4_b_b2b.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


def _bump(sector, amp=1.0, center=(17.0, 0.0), sig=3.0):
    from m5_17_energy import grid_coords
    R, Z = grid_coords(NR, NZ, H)
    b = amp * np.exp(-((R - center[0]) ** 2 + (Z - center[1]) ** 2)
                     / (2 * sig ** 2))
    V = np.zeros((NR, NZ, 4, 4))
    i, j = sector
    V[..., i, j] = b
    V[..., j, i] = b
    z = np.zeros_like(V)
    z[: NR - 1, 1:-1] = V[: NR - 1, 1:-1]
    return z


def b2c():
    """AUDIT FOLLOW-UP (2026-07-14, C6 refuted): structured velocities
    DO reach the b0 sector (the audit's (0,2) bump: align -0.479).
    Quantify the best achievable cancellation over the audit-identified
    structured directions, full-V and null-projected separately (the
    zero-energy scope), via Nelder-Mead on the 4 amplitudes."""
    from scipy.linalg import expm
    from scipy.optimize import minimize
    M = load_recipe()
    lam, U, nmask = null_basis(M)
    r0 = resid_null(np.zeros(int(nmask.sum())), M, U, nmask)
    n0 = np.linalg.norm(r0)

    def d_g(G):
        V = G @ M + M @ G.T
        z = np.zeros_like(V)
        z[: NR - 1, 1:-1] = V[: NR - 1, 1:-1]
        return z

    J23 = np.zeros((4, 4)); J23[2, 3], J23[3, 2] = -1.0, 1.0
    K2 = np.zeros((4, 4)); K2[0, 2] = K2[2, 0] = 1.0
    K3 = np.zeros((4, 4)); K3[0, 3] = K3[3, 0] = 1.0
    B = expm(2.5 * K2)
    dirs = [_bump((0, 2)), _bump((0, 3)), d_g(K3),
            d_g(B @ J23 @ np.linalg.inv(B))]
    dirs = [D / max(np.max(np.abs(D)), 1e-300) for D in dirs]

    def proj_null(V):
        v10 = np.einsum("akl,...kl->...a", BASIS, V[: NR - 1, 1:-1])
        vU = np.einsum("...ka,...k->...a", U, v10)
        vU = np.where(nmask, vU, 0.0)
        v10 = np.einsum("...ka,...a->...k", U, vU)
        out = np.zeros_like(V)
        out[: NR - 1, 1:-1] = np.einsum("...a,akl->...kl", v10, BASIS)
        return out

    out = {"r0_norm": float(n0)}
    for scope in ("full", "null_projected"):
        ds = [proj_null(D) for D in dirs] if scope == "null_projected" \
            else dirs

        def resid_frac(s):
            V = sum(float(si) * Di for si, Di in zip(s, ds))
            r10 = rhs_10(M, V)
            rU = np.einsum("...ka,...k->...a", U, r10)
            return float(np.linalg.norm(rU[nmask]) / n0)

        best = None
        for s0 in ([0.5, 0, 0, 0], [0, 0, 0.3, 0.3], [0.3, 0.3, 0.3, 0.3]):
            res = minimize(resid_frac, s0, method="Nelder-Mead",
                           options={"maxfev": 120, "xatol": 1e-3,
                                    "fatol": 1e-4})
            if best is None or res.fun < best["frac"]:
                best = {"frac": float(res.fun),
                        "amps": [float(x) for x in res.x]}
        out[scope] = best
        print(f"[B2c] {scope}: best |r|/|r0| = {best['frac']:.4f} at "
              f"amps {['%.3f' % a for a in best['amps']]}", flush=True)
    with open(os.path.join(DATA, "m5_20_4_b_b2c.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


def b3(T=10.0, dt=0.00125, rel_cut=1e-2):
    """evolve from (M_recipe, V*): does the blowup persist ON-surface?"""
    M = load_recipe()
    V0 = np.load(os.path.join(DATA, "m5_20_4_b_vstar.npz"))["V"]

    def snap_fn(Mx, v):
        rd = ring_by_m13(Mx, NR, NZ, H)
        qm, _ = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                     rd["ring13_z"])
        return {"ring_rho": float(rd["ring13_rho"]),
                "q_r4": None if not np.isfinite(qm) else float(qm),
                "max_v": float(np.max(np.abs(v)))}

    Mx, v, recs, wall = evolve_true(M, V0, T, dt, WSCALE, DELTA,
                                    rel_cut=rel_cut,
                                    snap_every=max(1, int(0.02 / dt)),
                                    snap_fn=snap_fn)
    fin = [r for r in recs if np.isfinite(r.get("E_tot", np.nan))]
    ts = None
    for r in recs:
        if r.get("blowup"):
            ts = r["t"]
    out = {"T": T, "dt": dt, "rel_cut": rel_cut, "tstar": ts,
           "wall_s": round(wall, 1),
           "nff_first": fin[0].get("null_force_frac") if fin else None,
           "nff_last": fin[-1].get("null_force_frac") if fin else None,
           "trajectory": recs}
    with open(os.path.join(DATA, "m5_20_4_b_b3.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[B3] on-surface run: t* = {ts} (baseline off-surface 0.53); "
          f"nff {out['nff_first']} -> {out['nff_last']}", flush=True)
    return out


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "b1"
    if which == "b1":
        b1()
    elif which == "b2":
        b2()
    elif which == "b2b":
        b2b()
    elif which == "b2c":
        b2c()
    elif which == "b3":
        b3(T=float(ARGV[1]) if len(ARGV) > 1 else 10.0,
           rel_cut=float(ARGV[2]) if len(ARGV) > 2 else 1e-2)
    else:
        raise SystemExit(f"unknown gate {which}")
