"""M5.20.5 arm A: the extremal-orbit solve on the corrected phi-averaged
rigid functional (the particle clock on the loop).

INHERITED VERDICT (m5_20_4 + its audit): the free-period rigid-orbit BVP
    S(w) = (2 pi / w) (w^2 Q2_avg - U),  root  w*^2 = -U / Q2_avg,
    H = w*^2 Q2_avg + U = 0 exactly at the root,
with boost-conjugated rotation generators G' = e^{chi K} J e^{-chi K}
(exactly periodic for every chi). AUDIT CORRECTION C7: the slice kinetic
q2_of is wrong outside the J12-commutant; the true 3D kinetic on the
axisym stack is the phi-average with the rotated generator
    G_phi = e^{-phi J12} G' e^{phi J12},   Q2_avg = <q2_of(M, G_phi)>_phi,
and the adjoint action has harmonics <= 2 in phi, Q2 quadratic in G_phi
=> harmonics <= 4 => the trapezoid rule with nphi >= 5 is EXACT (gated
in a0, not assumed). U needs no average (eta-similarity invariance).

THIS TASK: converge an actual extremal orbit M0 of
    Shat(M0) = w^2 Q2_avg(M0, G') - U(M0)      (gradShat -> 0)
at fixed working points (G', w*), then couple in the w-root and read the
observables. Pre-registered bar (tasks/m5_20_5_task_details.md):
residual <= 1e-3 x |G_static|, q = 0.5 intact, U / Q2_avg loop-scale.

PHASES
    a0    instrument gates: grad_q2_avg == complex-step (AG0a); nphi
          exactness 5 == 8 == 16 at machine (AG0b); J12-commutant
          sanity q2_avg(J12) == q2_of(J12) (AG0c); timing card.
    a1    refined root ladders w*(chi) for the three distinct families
          (J23^K2, J23^K3, J12^K1; the other three are exact mirrors);
          crossing chi_c; the chirped-ladder read (w_lad = 0.0674 rho);
          working-point pick (moderate w*, spread across families).
    a2    the extremal solve at a working point: 3 methods (descent on
          Phi = 1/2 |gradShat|^2, Newton-Krylov on the gradient field,
          L-BFGS on Phi) x 2 starts (warm = the m5_20_4 a4 state,
          cold = the recipe seed).
    a3    coupled stationarity from the best a2 state: alternate
          M-descent / w <- root(U, Q2_avg) / chi-stationarity report;
          H = 0 certificate at close.
    a4obs observables on the best state: w* vs the chirped ladder at
          the ring, the zero-energy split T = -U, containment radii
          (r50 / r90 of the static-energy profile) vs baseline,
          winding (multi-center scan) + core spectrum.

Run:  python m5_20_5_a_orbit.py a0|a1|a2 <wp> [budget_s]|a3|a4obs
Out:  ../data/m5_20_5_a_<phase>*.json
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

from m5_16_axisym import pin_mask                                  # noqa: E402
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_20_1_b_seeds import core_spectrum, winding_measure_biax    # noqa: E402
from m5_20_2_a_eom import WSCALE, grad_static_4                    # noqa: E402
from m5_20_3_a_constraint import (_cs_dir, e_static_c, seed4_grid,  # noqa: E402
                                  t_total_c, u_eta_density,
                                  v4_density)
from m5_20_4_a_bvp import (DELTA, H, NR, NZ, R0, RHO4, W4, PAIRS,  # noqa: E402
                           conj_gen, d_g, gen, load_seed, loop_reads,
                           q2_of, grad_q2, u_of)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
NPHI = 5                       # gated EXACT in a0 (band-limit, harmonics <= 4)
W_LAD_SLOPE = 0.0674           # the chirped vacuum ladder w1 = 0.0674 rho
RESID_BAR = 1e-3               # pre-registered: |gradShat| <= 1e-3 |G_static|

FAMS = {"J23^K2": ("J23", "K2"), "J23^K3": ("J23", "K3"),
        "J12^K1": ("J12", "K1")}


def gens_phi(G, nphi=NPHI):
    """the phi-rotated generator ladder G_phi = e^{-phi J12} G e^{phi J12}."""
    from scipy.linalg import expm
    J = gen("J12")
    return [expm(-p * J) @ G @ expm(p * J)
            for p in np.linspace(0.0, 2 * np.pi, nphi, endpoint=False)]


def q2_avg_n(M, G, nphi=NPHI):
    """the corrected 3D rigid kinetic (complex-safe, no std)."""
    return sum(t_total_c(M, d_g(M, Gp)) for Gp in gens_phi(G, nphi)) / nphi


def q2_avg_f(M, G, nphi=NPHI):
    return float(q2_avg_n(M, G, nphi).real)


def grad_q2_avg(M, G, nphi=NPHI):
    """dQ2_avg/dM = phi-mean of the gated grad_q2 with the rotated
    generator (linear combination of gated pieces)."""
    out = None
    for Gp in gens_phi(G, nphi):
        g = grad_q2(M, Gp, w4=W4, rho4=RHO4)
        out = g if out is None else out + g
    return out / nphi


PIN = pin_mask(NR, NZ)
FREE4 = (~PIN)[..., None, None].astype(float)


def grad_shat_avg(M, G, omega, nphi=NPHI):
    """gradShat = w^2 grad_q2_avg - G_static (free-masked)."""
    return (omega ** 2 * grad_q2_avg(M, G, nphi)
            - grad_static_4(M, WSCALE, DELTA, w4=W4, rho4=RHO4)) * FREE4


def resid_of(M, G, omega, nphi=NPHI):
    g = grad_shat_avg(M, G, omega, nphi)
    n = float(np.sqrt(np.sum(g ** 2)))
    gs = grad_static_4(M, WSCALE, DELTA, w4=W4, rho4=RHO4) * FREE4
    ns = float(np.sqrt(np.sum(gs ** 2)))
    return g, n, ns


def _rand_sym(shape, rng):
    D = rng.normal(size=shape)
    D = 0.5 * (D + np.swapaxes(D, -1, -2))
    out = np.zeros(shape)
    out[: shape[0] - 1, 1:-1] = D[: shape[0] - 1, 1:-1]
    return out


# ---------------- a0: instrument gates ----------------
def phase_a0(seed=5):
    rng = np.random.default_rng(seed)
    M = load_seed("recipe") + 0.03 * _rand_sym((NR, NZ, 4, 4), rng)
    G = conj_gen("J23", "K2", 0.9)
    out = {}
    # AG0a: grad_q2_avg == complex step of the phi-averaged total
    worst = 0.0
    for _ in range(2):
        D = _rand_sym((NR, NZ, 4, 4), rng)
        lhs = float(np.sum(grad_q2_avg(M, G, NPHI) * D))
        rhs = _cs_dir(lambda MM: q2_avg_n(MM, G, NPHI), M, D)
        worst = max(worst, abs(lhs - rhs) / max(abs(rhs), 1e-12))
    out["ag0a_grad_cs"] = worst
    # AG0b: nphi exactness (harmonics <= 4 => nphi >= 5 exact)
    q16 = q2_avg_f(M, G, 16)
    out["ag0b_q2_rel_5_16"] = abs(q2_avg_f(M, G, 5) - q16) / abs(q16)
    out["ag0b_q2_rel_8_16"] = abs(q2_avg_f(M, G, 8) - q16) / abs(q16)
    g5 = grad_q2_avg(M, G, 5)
    g16 = grad_q2_avg(M, G, 16)
    out["ag0b_grad_rel_5_16"] = float(
        np.abs(g5 - g16).max() / max(np.abs(g16).max(), 1e-300))
    # AG0c: J12 commutes with the axisym frame: avg == slice
    out["ag0c_j12_rel"] = abs(q2_avg_f(M, gen("J12"), 5)
                              - q2_of(M, gen("J12"))) / max(
        abs(q2_of(M, gen("J12"))), 1e-12)
    # timing card (budget planning for a2)
    t0 = time.time()
    q2_avg_f(M, G, NPHI)
    out["t_q2avg_s"] = round(time.time() - t0, 3)
    t0 = time.time()
    grad_q2_avg(M, G, NPHI)
    out["t_gradq2avg_s"] = round(time.time() - t0, 3)
    ok = (out["ag0a_grad_cs"] < 1e-8 and out["ag0b_q2_rel_5_16"] < 1e-12
          and out["ag0b_grad_rel_5_16"] < 1e-10
          and out["ag0c_j12_rel"] < 1e-12)
    out["pass"] = bool(ok)
    with open(os.path.join(DATA, "m5_20_5_a_a0.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[A0] cs {out['ag0a_grad_cs']:.1e} nphi(q2) "
          f"{out['ag0b_q2_rel_5_16']:.1e} nphi(grad) "
          f"{out['ag0b_grad_rel_5_16']:.1e} j12 {out['ag0c_j12_rel']:.1e} "
          f"| t(q2avg) {out['t_q2avg_s']}s t(grad) {out['t_gradq2avg_s']}s "
          f"-> {'PASS' if ok else 'FAIL'}", flush=True)
    return out


# ---------------- a1: refined ladders + working points ----------------
def _bisect_chi(M, fam, target, lo, hi, tol=1e-3, nphi=NPHI):
    """chi with Q2_avg(chi) = target (Q2_avg decreasing in chi here)."""
    rot, boost = fam
    flo = q2_avg_f(M, conj_gen(rot, boost, lo), nphi) - target
    fhi = q2_avg_f(M, conj_gen(rot, boost, hi), nphi) - target
    if flo * fhi > 0:
        return None
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        fm = q2_avg_f(M, conj_gen(rot, boost, mid), nphi) - target
        if flo * fm <= 0:
            hi = mid
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi)


def phase_a1():
    M = load_seed("recipe")
    U = u_of(M)
    reads = loop_reads(M)
    w_lad = W_LAD_SLOPE * reads["ring_rho"]
    out = {"U": U, "ring_rho": reads["ring_rho"], "w_ladder": w_lad,
           "nphi": NPHI, "families": {}}
    # coarse windows around the known a1c crossings
    windows = {"J23^K2": (0.4, 1.1), "J23^K3": (0.0, 0.6),
               "J12^K1": (0.0, 0.6)}
    for name, fam in FAMS.items():
        rot, boost = fam
        lo, hi = windows[name]
        chis = np.concatenate([np.linspace(lo, hi, 15),
                               np.linspace(hi + 0.2, 2.5, 8)])
        rows = []
        for c in chis:
            q2 = q2_avg_f(M, conj_gen(rot, boost, float(c)))
            rows.append({"chi": float(c), "Q2_avg": q2,
                         "root_omega": float(np.sqrt(-U / q2))
                         if U * q2 < 0 else None})
        chi_c = _bisect_chi(M, fam, 0.0, lo, hi)
        chi_lad = _bisect_chi(M, fam, -U / w_lad ** 2, lo, hi)
        chi_mod = _bisect_chi(M, fam, -U / 0.1 ** 2, lo, hi)
        # interior extrema of w*(chi) on the negative branch
        roots = [(r["chi"], r["root_omega"]) for r in rows
                 if r["root_omega"] is not None]
        n_extrema = 0
        for i in range(1, len(roots) - 1):
            d1 = roots[i][1] - roots[i - 1][1]
            d2 = roots[i + 1][1] - roots[i][1]
            if d1 * d2 < 0:
                n_extrema += 1
        fam_out = {"rows": rows, "chi_crossing": chi_c,
                   "chi_ladder": chi_lad, "chi_moderate": chi_mod,
                   "interior_omega_extrema": n_extrema}
        out["families"][name] = fam_out
        print(f"[A1] {name}: chi_c = {chi_c} chi_lad(w={w_lad:.3f}) = "
              f"{chi_lad} chi(w*=0.1) = {chi_mod} extrema = {n_extrema}",
              flush=True)
    # working points: moderate w*, spread across families
    wps = []
    f1 = out["families"]["J23^K2"]
    if f1["chi_moderate"] is not None:
        wps.append({"fam": "J23^K2", "chi": f1["chi_moderate"],
                    "note": "moderate w* ~ 0.1 (near-crossing, off-edge)"})
    wps.append({"fam": "J23^K2", "chi": 0.75,
                "note": "shallow negative branch (the a1c point)"})
    wps.append({"fam": "J12^K1", "chi": 0.25,
                "note": "the conjugated symmetry-axis clock"})
    for wp in wps:
        rot, boost = FAMS[wp["fam"]]
        q2 = q2_avg_f(M, conj_gen(rot, boost, wp["chi"]))
        wp["Q2_avg"] = q2
        wp["omega"] = float(np.sqrt(-U / q2)) if U * q2 < 0 else None
    out["working_points"] = [wp for wp in wps if wp["omega"] is not None]
    print("[A1] working points: " + " | ".join(
        f"{w['fam']} chi={w['chi']:.3f} w*={w['omega']:.4f}"
        for w in out["working_points"]), flush=True)
    with open(os.path.join(DATA, "m5_20_5_a_a1.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- a2: the extremal solve ----------------
def _flat_pack():
    """free-DOF flattening helpers (symmetric 4x4 grids, pin-masked)."""
    mask = np.broadcast_to((~PIN)[..., None, None], (NR, NZ, 4, 4))
    iu = np.triu_indices(4)

    def pack(M):
        return M[..., iu[0], iu[1]][~PIN].ravel()

    def unpack(x, base):
        M = base.copy()
        block = x.reshape(-1, 10)
        full = np.zeros(((~PIN).sum(), 4, 4))
        full[:, iu[0], iu[1]] = block
        full[:, iu[1], iu[0]] = block
        M[~PIN] = full
        return M

    return pack, unpack, mask


def run_descent(M0, G, omega, nphi, budget_s, iters=400, log=print):
    """steepest descent on Phi = 1/2 |gradShat|^2 (Hessian-vector by
    complex step; the m5_20_4 a4 machinery on the corrected functional)."""
    Mx = M0.copy()
    _, n0, ns = resid_of(Mx, G, omega, nphi)
    hist = [{"it": 0, "resid": n0, "rel": n0 / ns}]
    step, eps = 1e-6, 1e-30
    t0 = time.time()
    it = 0
    while it < iters and time.time() - t0 < budget_s:
        it += 1
        gx, nx, ns = resid_of(Mx, G, omega, nphi)
        if nx <= RESID_BAR * ns:
            break
        try:
            gc = grad_shat_avg(Mx.astype(complex) + 1j * eps * gx, G,
                               omega, nphi)
            hv = np.imag(gc) / eps * FREE4
        except Exception:                                    # noqa: BLE001
            hh = 1e-6
            hv = (grad_shat_avg(Mx + hh * gx, G, omega, nphi)
                  - grad_shat_avg(Mx - hh * gx, G, omega, nphi)) / (2 * hh)
        ndp = float(np.sqrt(np.sum(hv ** 2)))
        if ndp == 0:
            break
        ok = False
        for _ in range(20):
            Mt = Mx - step * hv
            _, nt, _ = resid_of(Mt, G, omega, nphi)
            if nt < nx:
                Mx, ok = Mt, True
                step *= 1.5
                break
            step *= 0.4
        if not ok:
            break
        if it % 20 == 0:
            _, nc, ns = resid_of(Mx, G, omega, nphi)
            hist.append({"it": it, "resid": nc, "rel": nc / ns})
            log(f"    descent it {it}: resid {nc:.4e} (rel {nc/ns:.4f})")
    _, nf, ns = resid_of(Mx, G, omega, nphi)
    hist.append({"it": it, "resid": nf, "rel": nf / ns})
    return Mx, {"method": "descent", "resid_start": n0, "resid_final": nf,
                "rel_final": nf / ns, "iters": it,
                "wall_s": round(time.time() - t0, 1), "hist": hist}


def run_nk(M0, G, omega, nphi, budget_s, log=print):
    """Jacobian-free Newton-Krylov on the gradient field."""
    from scipy.optimize import newton_krylov
    from scipy.optimize._nonlin import NoConvergence
    pack, unpack, _ = _flat_pack()
    t0 = time.time()
    n_eval = [0]

    def F(x):
        if time.time() - t0 > budget_s:
            raise TimeoutError
        n_eval[0] += 1
        return pack(grad_shat_avg(unpack(x, M0), G, omega, nphi))

    x0 = pack(M0)
    _, n0, ns = resid_of(M0, G, omega, nphi)
    xf, note = x0, "no-step"
    try:
        xf = newton_krylov(F, x0, method="lgmres", maxiter=12,
                           f_tol=RESID_BAR * ns / np.sqrt(x0.size),
                           verbose=False)
        note = "converged-flag"
    except NoConvergence as e:
        xf, note = e.args[0], "no-convergence"
    except TimeoutError:
        note = "budget"
    except Exception as e:                                   # noqa: BLE001
        note = f"error: {type(e).__name__}"
    Mx = unpack(xf, M0)
    _, nf, ns = resid_of(Mx, G, omega, nphi)
    if not np.isfinite(nf) or nf > n0:
        Mx, nf = M0.copy(), n0
        note += "; rejected (worse/non-finite)"
    log(f"    nk: {note}, {n_eval[0]} F-evals")
    return Mx, {"method": "newton_krylov", "resid_start": n0,
                "resid_final": nf, "rel_final": nf / ns, "note": note,
                "n_F_evals": n_eval[0],
                "wall_s": round(time.time() - t0, 1)}


def run_lbfgs(M0, G, omega, nphi, budget_s, log=print):
    """L-BFGS on Phi = 1/2 |gradShat|^2; grad Phi = Hess . gradShat by
    complex step (symmetric Hessian)."""
    from scipy.optimize import minimize
    pack, unpack, _ = _flat_pack()
    t0 = time.time()
    eps = 1e-30

    def phi_and_grad(x):
        if time.time() - t0 > budget_s:
            raise TimeoutError
        M = unpack(x, M0)
        g, n, _ = resid_of(M, G, omega, nphi)
        try:
            gc = grad_shat_avg(M.astype(complex) + 1j * eps * g, G,
                               omega, nphi)
            hv = np.imag(gc) / eps * FREE4
        except Exception:                                    # noqa: BLE001
            hh = 1e-6
            hv = (grad_shat_avg(M + hh * g, G, omega, nphi)
                  - grad_shat_avg(M - hh * g, G, omega, nphi)) / (2 * hh)
        return 0.5 * n ** 2, pack(hv)

    _, n0, ns = resid_of(M0, G, omega, nphi)
    x0 = pack(M0)
    note = "ok"
    try:
        res = minimize(phi_and_grad, x0, jac=True, method="L-BFGS-B",
                       options={"maxiter": 80, "gtol": 0.0, "ftol": 0.0})
        xf = res.x
        note = f"status {res.status}: {str(res.message)[:60]}"
    except TimeoutError:
        xf, note = x0, "budget"
    except Exception as e:                                   # noqa: BLE001
        xf, note = x0, f"error: {type(e).__name__}"
    Mx = unpack(xf, M0)
    _, nf, ns = resid_of(Mx, G, omega, nphi)
    if not np.isfinite(nf) or nf > n0:
        Mx, nf = M0.copy(), n0
        note += "; rejected (worse/non-finite)"
    log(f"    lbfgs: {note}")
    return Mx, {"method": "lbfgs_phi", "resid_start": n0, "resid_final": nf,
                "rel_final": nf / ns, "note": note,
                "wall_s": round(time.time() - t0, 1)}


METHODS = (("descent", run_descent), ("nk", run_nk), ("lbfgs", run_lbfgs))


def load_start(kind):
    if kind == "warm":
        return np.load(os.path.join(DATA,
                                    "m5_20_4_a_a4_state.npz"))["M"].copy()
    return load_seed("recipe").astype(float)


def phase_a2(wp_index=0, budget_s=600.0):
    with open(os.path.join(DATA, "m5_20_5_a_a1.json")) as f:
        a1 = json.load(f)
    wp = a1["working_points"][wp_index]
    rot, boost = FAMS[wp["fam"]]
    G = conj_gen(rot, boost, wp["chi"])
    omega = wp["omega"]
    print(f"[A2 wp{wp_index}] {wp['fam']} chi={wp['chi']:.3f} "
          f"w*={omega:.4f} budget {budget_s:.0f}s/run", flush=True)
    out = {"wp": wp, "nphi": NPHI, "runs": [], "converged": None}
    best = (None, np.inf)
    for mname, mfn in METHODS:
        for start in ("warm", "cold"):
            M0 = load_start(start)
            # the working-point omega is defined on the recipe seed; for
            # the warm start keep the same omega (fixed-(G', w*) solve)
            Mx, rec = mfn(M0, G, omega, NPHI, budget_s)
            rec.update({"start": start})
            Uf, Q2f = u_of(Mx), q2_avg_f(Mx, G)
            rec.update({"U_final": Uf, "Q2_avg_final": Q2f,
                        "H_at_omega": Uf + omega ** 2 * Q2f,
                        "root_consistency": abs(
                            np.sqrt(max(-Uf / Q2f, 0.0)) - omega) / omega
                        if Uf * Q2f < 0 else None,
                        **loop_reads(Mx)})
            rec["bar_met"] = bool(rec["rel_final"] <= RESID_BAR
                                  and rec.get("q_r4") == 0.5
                                  and np.isfinite(Uf) and np.isfinite(Q2f))
            out["runs"].append(rec)
            print(f"  [{mname}/{start}] resid {rec['resid_start']:.3e} -> "
                  f"{rec['resid_final']:.3e} (rel {rec['rel_final']:.4f}) "
                  f"q={rec.get('q_r4')} bar={'MET' if rec['bar_met'] else 'no'}",
                  flush=True)
            if rec["resid_final"] < best[1]:
                best = ((mname, start, Mx.copy()), rec["resid_final"])
            with open(os.path.join(DATA,
                                   f"m5_20_5_a_a2_wp{wp_index}.json"),
                      "w") as f:
                json.dump(out, f, indent=1, default=float)
            if rec["bar_met"]:
                out["converged"] = {"method": mname, "start": start}
                break
        if out["converged"]:
            break
    if best[0] is not None:
        mname, start, Mx = best[0]
        out["best"] = {"method": mname, "start": start,
                       "resid": best[1]}
        np.savez_compressed(
            os.path.join(DATA, f"m5_20_5_a_a2_wp{wp_index}_best.npz"),
            M=Mx)
    with open(os.path.join(DATA, f"m5_20_5_a_a2_wp{wp_index}.json"),
              "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[A2 wp{wp_index}] converged = {out['converged']} "
          f"best = {out.get('best')}", flush=True)
    return out


# ---------------- stall: regenerate the loop-preserving stall state ------
def phase_stall(wp_index=0, budget_s=900.0):
    """the best LOOP-PRESERVING state at a working point (the a2 'best'
    can be the NK vacuum trap): a fresh warm-start descent to stall,
    saved for a3 / a4obs / the audit."""
    with open(os.path.join(DATA, "m5_20_5_a_a1.json")) as f:
        a1 = json.load(f)
    wp = a1["working_points"][wp_index]
    rot, boost = FAMS[wp["fam"]]
    G = conj_gen(rot, boost, wp["chi"])
    Mx, rec = run_descent(load_start("warm"), G, wp["omega"], NPHI,
                          budget_s, iters=400)
    np.savez_compressed(
        os.path.join(DATA, f"m5_20_5_a_a2_wp{wp_index}_stall.npz"), M=Mx)
    print(f"[STALL wp{wp_index}] saved: resid {rec['resid_final']:.4e} "
          f"rel {rec['rel_final']:.4f}", flush=True)
    return rec


# ---------------- a2x: the blocking-structure diagnostic ----------------
def _sector_norms(G):
    """norm split: time row (0mu) vs spatial block."""
    t = float(np.sqrt(np.sum(G[..., 0, :] ** 2) + np.sum(G[..., 1:, 0] ** 2)))
    s = float(np.sqrt(np.sum(G[..., 1:, 1:] ** 2)))
    return {"time_row": t, "spatial_block": s}


def phase_a2x(wp_index=0):
    """WHAT BLOCKS the extremal solve: alignment geometry between the
    kinetic gradient grad_q2_avg and G_static. For gradShat =
    w^2 g_kin - g_stat -> 0 the two fields must ALIGN (cos ~ +1) with
    matching magnitude; cos << 1 means NO omega can cancel: the block
    is DIRECTIONAL (structural), not conditioning."""
    with open(os.path.join(DATA, "m5_20_5_a_a1.json")) as f:
        a1 = json.load(f)
    wp = a1["working_points"][wp_index]
    rot, boost = FAMS[wp["fam"]]
    G = conj_gen(rot, boost, wp["chi"])
    omega = wp["omega"]
    states = {"recipe_seed": load_seed("recipe").astype(float)}
    fn = os.path.join(DATA, f"m5_20_5_a_a2_wp{wp_index}_best.npz")
    if os.path.exists(fn):
        states[f"a2_wp{wp_index}_best"] = np.load(fn)["M"]
    out = {"wp": wp, "states": {}}
    for tag, M in states.items():
        gk = grad_q2_avg(M, G, NPHI) * FREE4
        gs = grad_static_4(M, WSCALE, DELTA, w4=W4, rho4=RHO4) * FREE4
        nk = float(np.sqrt(np.sum(gk ** 2)))
        ns = float(np.sqrt(np.sum(gs ** 2)))
        dot = float(np.sum(gk * gs))
        cos = dot / max(nk * ns, 1e-300)
        # the omega that best cancels g_stat along g_kin
        w2_opt = dot / max(nk ** 2, 1e-300)
        best_rel = float(np.sqrt(max(1.0 - cos ** 2, 0.0)))
        row = {"cos_align_gkin_gstat": cos,
               "norm_gkin": nk, "norm_gstat": ns,
               "omega2_used": omega ** 2, "omega2_optimal": w2_opt,
               "omega_optimal": float(np.sqrt(w2_opt))
               if w2_opt > 0 else None,
               "best_rel_residual_any_omega": best_rel,
               "sectors_gkin": _sector_norms(gk),
               "sectors_gstat": _sector_norms(gs)}
        out["states"][tag] = row
        print(f"[A2x {tag}] cos = {cos:+.4f} -> best achievable rel "
              f"residual (ANY omega) = {best_rel:.4f}; |gkin| {nk:.3e} "
              f"|gstat| {ns:.3e}; w2_opt {w2_opt:.3e} (used "
              f"{omega**2:.3e}); gkin time/spatial "
              f"{row['sectors_gkin']['time_row']:.2e}/"
              f"{row['sectors_gkin']['spatial_block']:.2e}, gstat "
              f"{row['sectors_gstat']['time_row']:.2e}/"
              f"{row['sectors_gstat']['spatial_block']:.2e}", flush=True)
    with open(os.path.join(DATA, f"m5_20_5_a_a2x_wp{wp_index}.json"),
              "w") as f:
        json.dump(out, f, indent=1, default=float)
    return out


# ---------------- a3: coupled stationarity ----------------
def phase_a3(wp_index=0, rounds=6, budget_s=300.0):
    with open(os.path.join(DATA, f"m5_20_5_a_a2_wp{wp_index}.json")) as f:
        a2 = json.load(f)
    wp = a2["wp"]
    rot, boost = FAMS[wp["fam"]]
    chi = float(wp["chi"])
    # start from the best LOOP-PRESERVING state: the a2 "best" can be the
    # NK vacuum trap (q = 0), which is not a valid clock start
    fn_stall = os.path.join(DATA, f"m5_20_5_a_a2_wp{wp_index}_stall.npz")
    fn_best = os.path.join(DATA, f"m5_20_5_a_a2_wp{wp_index}_best.npz")
    Mx = np.load(fn_stall if os.path.exists(fn_stall) else fn_best)["M"]
    omega = float(wp["omega"])
    out = {"wp": wp, "rounds": []}
    for rd in range(1, rounds + 1):
        G = conj_gen(rot, boost, chi)
        # (i) M-descent at fixed omega
        Mx, rec = run_descent(Mx, G, omega, NPHI, budget_s, iters=120,
                              log=lambda s: None)
        # (ii) omega <- root
        U, Q2 = u_of(Mx), q2_avg_f(Mx, G)
        root_ok = U * Q2 < 0
        d_omega = None
        if root_ok:
            w_new = float(np.sqrt(-U / Q2))
            d_omega = abs(w_new - omega) / max(omega, 1e-30)
            omega = w_new
        # (iii) chi-stationarity read (finite difference of S* over chi)
        dchi = 0.02
        q2p = q2_avg_f(Mx, conj_gen(rot, boost, chi + dchi))
        q2m = q2_avg_f(Mx, conj_gen(rot, boost, chi - dchi))
        # S* = -4 pi U / w*(chi); dS*/dchi through Q2(chi) at the root
        def sstar(q2v):
            return (-4.0 * np.pi * U * np.sqrt(-q2v / U)
                    if U * q2v < 0 else None)
        sp, sm = sstar(q2p), sstar(q2m)
        ds_dchi = ((sp - sm) / (2 * dchi)
                   if sp is not None and sm is not None else None)
        H = U + omega ** 2 * Q2
        row = {"round": rd, "resid_rel": rec["rel_final"],
               "omega": omega, "d_omega_rel": d_omega, "U": U,
               "Q2_avg": Q2, "H": H, "dSstar_dchi": ds_dchi,
               **loop_reads(Mx)}
        out["rounds"].append(row)
        print(f"[A3 rd{rd}] rel {row['resid_rel']:.4f} w {omega:.4e} "
              f"(dw {d_omega}) H {H:.3e} dS*/dchi {ds_dchi} "
              f"q {row.get('q_r4')}", flush=True)
        if not root_ok:
            row["stop"] = "root lost (U*Q2 >= 0)"
            break
    U, Q2 = u_of(Mx), q2_avg_f(Mx, conj_gen(rot, boost, chi))
    out["certificate"] = {
        "H_final": U + omega ** 2 * Q2,
        "H_rel_to_U": abs(U + omega ** 2 * Q2) / max(abs(U), 1e-30),
        "resid_rel_final": out["rounds"][-1]["resid_rel"]
        if out["rounds"] else None}
    np.savez_compressed(
        os.path.join(DATA, f"m5_20_5_a_a3_wp{wp_index}_state.npz"), M=Mx)
    with open(os.path.join(DATA, f"m5_20_5_a_a3_wp{wp_index}.json"),
              "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"[A3] certificate: H = {out['certificate']['H_final']:.4e} "
          f"(rel {out['certificate']['H_rel_to_U']:.2e})", flush=True)
    return out


# ---------------- a4obs: observables ----------------
def static_profile(M):
    """z-summed static-energy radial profile + containment radii
    (self-gated against e_static_c)."""
    from m5_17_energy import cell_weights
    w = cell_weights(NR, NZ, H)
    dens = (u_eta_density(M, H) + v4_density(M, WSCALE, DELTA)) * w
    tot = float(np.sum(dens))
    gate = abs(tot - float(e_static_c(M, WSCALE, DELTA).real)) / max(
        abs(tot), 1e-30)
    prof = dens.sum(axis=1)
    rho = (np.arange(NR - 1) + 0.5) * H
    csum = np.cumsum(prof)
    def r_at(frac):
        i = int(np.searchsorted(csum, frac * csum[-1]))
        return float(rho[min(i, len(rho) - 1)])
    return {"rho": rho.tolist(), "profile": prof.tolist(),
            "E_total": tot, "gate_rel": gate,
            "r50": r_at(0.5), "r90": r_at(0.9)}


def winding_scan(M, extra_centers=()):
    """coarse center grid + the detected ring center (the grid alone can
    miss the core; the ring read is the primary detector)."""
    hits = []
    centers = [(float(rc), float(zc))
               for rc in np.arange(5.0, 50.0, 5.0)
               for zc in np.arange(-10.0, 10.1, 5.0)]
    centers += [(float(r), float(z)) for r, z in extra_centers]
    for rc, zc in centers:
        q, _ = winding_measure_biax(M, NR, NZ, H, rc, zc)
        if np.isfinite(q) and abs(q) >= 0.4:
            hits.append({"rho": rc, "z": zc, "q": float(q)})
    return hits


def phase_a4obs(wp_index=0, state="a3"):
    fn = (f"m5_20_5_a_a3_wp{wp_index}_state.npz" if state == "a3"
          else f"m5_20_5_a_a2_wp{wp_index}_best.npz")
    Mx = np.load(os.path.join(DATA, fn))["M"]
    with open(os.path.join(DATA, f"m5_20_5_a_a3_wp{wp_index}.json")) as f:
        a3 = json.load(f)
    wp = a3["wp"]
    rot, boost = FAMS[wp["fam"]]
    G = conj_gen(rot, boost, float(wp["chi"]))
    omega = a3["rounds"][-1]["omega"] if a3["rounds"] else wp["omega"]
    M_base = load_seed("recipe")
    U, Q2 = u_of(Mx), q2_avg_f(Mx, G)
    reads = loop_reads(Mx)
    rd = ring_by_m13(Mx, NR, NZ, H)
    cs = core_spectrum(Mx, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
    out = {
        "state_file": fn, "wp": wp, "omega": omega,
        "clock_vs_ladder": {
            "omega_star": omega,
            "w_ladder_at_ring": W_LAD_SLOPE * reads["ring_rho"],
            "ratio": omega / (W_LAD_SLOPE * reads["ring_rho"])},
        "energy_split": {"U": U, "T_rot": omega ** 2 * Q2,
                         "H": U + omega ** 2 * Q2,
                         "zero_energy_rel": abs(U + omega ** 2 * Q2)
                         / max(abs(U), 1e-30)},
        "containment": {"state": static_profile(Mx),
                        "baseline": static_profile(M_base)},
        "winding": {"ring_read": reads,
                    "center_scan": winding_scan(
                        Mx, extra_centers=[(rd["ring13_rho"],
                                            rd["ring13_z"])]),
                    "core_lam": cs["lam"]},
    }
    with open(os.path.join(DATA, f"m5_20_5_a_a4obs_wp{wp_index}.json"),
              "w") as f:
        json.dump(out, f, indent=1, default=float)
    c = out["containment"]
    print(f"[A4obs] w* {omega:.4e} vs ladder "
          f"{out['clock_vs_ladder']['w_ladder_at_ring']:.3f} (ratio "
          f"{out['clock_vs_ladder']['ratio']:.2e}); H rel "
          f"{out['energy_split']['zero_energy_rel']:.2e}; r50/r90 "
          f"{c['state']['r50']:.1f}/{c['state']['r90']:.1f} vs baseline "
          f"{c['baseline']['r50']:.1f}/{c['baseline']['r90']:.1f}; "
          f"hits {len(out['winding']['center_scan'])}", flush=True)
    return out


if __name__ == "__main__":
    which = ARGV[0] if ARGV else "a0"
    if which == "a0":
        phase_a0()
    elif which == "a1":
        phase_a1()
    elif which == "a2":
        phase_a2(int(ARGV[1]) if len(ARGV) > 1 else 0,
                 float(ARGV[2]) if len(ARGV) > 2 else 600.0)
    elif which == "a2x":
        phase_a2x(int(ARGV[1]) if len(ARGV) > 1 else 0)
    elif which == "stall":
        phase_stall(int(ARGV[1]) if len(ARGV) > 1 else 0)
    elif which == "a3":
        phase_a3(int(ARGV[1]) if len(ARGV) > 1 else 0)
    elif which == "a4obs":
        phase_a4obs(int(ARGV[1]) if len(ARGV) > 1 else 0)
    else:
        raise SystemExit(f"unknown phase {which}")
