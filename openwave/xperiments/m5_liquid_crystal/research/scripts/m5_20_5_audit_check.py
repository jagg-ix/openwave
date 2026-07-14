"""M5.20.5 INDEPENDENT ADVERSARIAL AUDIT (cardinal rule: a second agent
with its own instruments tries to REFUTE every substantive claim).

Claims audited (verdicts land in ../data/m5_20_5_audit.json):
    C1  band-limit of the phi-averaged kinetic (nphi >= 5 exact)
    C2  the a1 root ladders (crossings, monotonicity, ladder-scale edge)
    C3  the 18-run kill (own residual contraction on the saved states)
    C4  the directional block (own cosines + scope probes beyond the note)
    C5  the a3 root loss (own average on the saved state)
    C6  the s2 EL algebra (own density / own complex step / own polarization)
    C7  the escape statics kill (own gradient assembly + own FIRE relaxer)
    C8  PSD margins (own per-cell Hessians by polarization + full grid)
    C9  completeness / overclaim sweep (numeric spot checks recorded here;
        the prose findings live in the audit report)

OWN constructions (never the m5_20_5 task functions, which are imported
ONLY as comparison targets):
    - the phi ladder is built from ANALYTIC rotation/boost matrices
      (cos/sin, cosh/sinh blocks; checked once against scipy expm),
    - the phi average uses nphi = 7 (any nphi >= 5 must agree with the
      task's 5 if the band-limit claim is true) and is trapezoid-by-hand,
    - gradients are cross-checked against my own complex step of my own
      complex-safe totals,
    - per-cell kinetic operators are rebuilt by polarization from my own
      pointwise densities,
    - the statics re-relax uses my own FIRE implementation.

Trusted (prior-audit) instruments consumed as-is: pin_mask, cell_weights,
ring_by_m13, winding_measure_biax, channels, grad_static_4, e_static_c,
t_total_c, t_density, comm/inner_eta_b, build_k10, BASIS, grad_q2,
density_point, kin_form_point, k10_add, t_add_density, load_seed,
loop_reads, q2_of, u_of.

Run:  python3 m5_20_5_audit_check.py c1|c2|c3|c4|c5|c6|c7|c8|c9|all
Out:  ../data/m5_20_5_audit.json
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

os.environ.setdefault("MPLBACKEND", "Agg")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_16_axisym import pin_mask                                   # noqa: E402
from m5_17_energy import cell_weights                               # noqa: E402
from m5_19_d1_relax import ring_by_m13                              # noqa: E402
from m5_20_1_b_seeds import winding_measure_biax                    # noqa: E402
from m5_20_2_a_eom import (ETA, WSCALE, channels,                   # noqa: E402
                           grad_static_4)
from m5_20_3_a_constraint import (BASIS, build_k10, comm_eta_b,     # noqa: E402
                                  e_static_c, inner_eta_b,
                                  t_total_c)
from m5_20_4_a_bvp import (DELTA, H, NR, NZ, RHO4, W4, conj_gen,    # noqa: E402
                           grad_q2, load_seed, loop_reads, q2_of,
                           u_of)
from m5_20_4_c_terms import (A_STAR, density_point,                 # noqa: E402
                             k10_add, kin_form_point, t_add_density)
# TASK-UNDER-AUDIT functions: comparison targets only ----------------
from m5_20_5_b_escape import (e_s2_static_c, g_u_s2, k10_s2,        # noqa: E402
                              u_s2_density)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
AUD = os.path.join(DATA, "m5_20_5_audit.json")
WCELL = cell_weights(NR, NZ, H)
PIN = pin_mask(NR, NZ)
FREE4 = (~PIN)[..., None, None].astype(float)
I4 = np.eye(4)
GAMMA = -1.0
NPHI_ME = 7                      # deliberately != the task's 5


# =============== own constructions ===============
def my_gen(name):
    """so(1,3) generators, same convention as the record (a definition,
    not a claim): J_kl has G[k,l] = -1, G[l,k] = +1; K_k has
    G[0,k] = G[k,0] = 1."""
    G = np.zeros((4, 4))
    if name[0] == "J":
        k, l = int(name[1]), int(name[2])
        G[k, l], G[l, k] = -1.0, 1.0
    else:
        k = int(name[1])
        G[0, k] = G[k, 0] = 1.0
    return G


def my_rot12(phi):
    """exp(phi J12) analytically (dR/dphi = J12 R checked)."""
    c, s = np.cos(phi), np.sin(phi)
    R = np.eye(4)
    R[1, 1], R[1, 2], R[2, 1], R[2, 2] = c, -s, s, c
    return R


def my_boost(k, chi):
    """exp(chi K_k) analytically."""
    B = np.eye(4)
    ch, sh = np.cosh(chi), np.sinh(chi)
    B[0, 0] = B[k, k] = ch
    B[0, k] = B[k, 0] = sh
    return B


def my_conj(rot, boost, chi):
    k = int(boost[1])
    return my_boost(k, chi) @ my_gen(rot) @ my_boost(k, -chi)


def my_dg(M, G):
    return G @ M + M @ G.T


def my_gens_phi(G, nphi):
    phis = np.arange(nphi) * (2.0 * np.pi / nphi)
    return [my_rot12(-p) @ G @ my_rot12(p) for p in phis]


def my_q2_avg_c(M, G, nphi=NPHI_ME):
    """own phi-averaged rigid kinetic (complex-safe)."""
    return sum(t_total_c(M, my_dg(M, Gp))
               for Gp in my_gens_phi(G, nphi)) / nphi


def my_q2_avg(M, G, nphi=NPHI_ME):
    return float(np.real(my_q2_avg_c(M, G, nphi)))


def my_grad_q2_avg(M, G, nphi=NPHI_ME):
    """own phi mean over the prior-audited per-generator grad_q2."""
    out = None
    for Gp in my_gens_phi(G, nphi):
        g = grad_q2(M, Gp, w4=W4, rho4=RHO4)
        out = g if out is None else out + g
    return out / nphi


def my_cs(fn, X, D, h=1e-30):
    """own complex-step directional derivative."""
    return float(np.imag(fn(X.astype(complex) + 1j * h * D)) / h)


def my_rand_sym(rng, amp=1.0):
    D = rng.normal(size=(NR, NZ, 4, 4))
    D = 0.5 * (D + np.swapaxes(D, -1, -2))
    out = np.zeros_like(D)
    out[: NR - 1, 1:-1] = D[: NR - 1, 1:-1]
    return amp * out


def my_resid(M, G, omega, nphi=NPHI_ME):
    """own contraction of |w^2 grad_q2_avg - G_static| (free-masked)."""
    gk = my_grad_q2_avg(M, G, nphi)
    gs = grad_static_4(M, WSCALE, DELTA, w4=W4, rho4=RHO4)
    g = (omega ** 2 * gk - gs) * FREE4
    n = float(np.sqrt(np.sum(g ** 2)))
    ns = float(np.sqrt(np.sum((gs * FREE4) ** 2)))
    return n, ns


def my_sectors(Gf):
    t = float(np.sqrt(np.sum(Gf[..., 0, :] ** 2)
                      + np.sum(Gf[..., 1:, 0] ** 2)))
    s = float(np.sqrt(np.sum(Gf[..., 1:, 1:] ** 2)))
    return t, s


def my_u_s2_grid(Mnp, a):
    """own s2 static density SUM_{i<j} tr(C_ij P C_ij P) per cell
    (complex-safe)."""
    nr = Mnp.shape[0]
    Ar, Ap, Az = channels(Mnp, H)[:3]
    Xs = [ETA @ Ar, ETA @ Ap, ETA @ Az]
    P = A_STAR_P(Mnp[: nr - 1, 1:-1], a)
    tot = 0.0
    for i in range(3):
        for j in range(i + 1, 3):
            C = Xs[i] @ Xs[j] - Xs[j] @ Xs[i]
            CP = C @ P
            tot = tot + np.einsum("...ij,...ji->...", CP, CP)
    return tot


def A_STAR_P(Mc, a):
    return a * I4 - ETA @ Mc


def my_e_s2_c(Mnp, a):
    return np.sum(my_u_s2_grid(Mnp, a) * WCELL)


def my_e_s2(Mnp, a):
    return float(np.real(my_e_s2_c(Mnp, a)))


def my_t_s2_pt(Mc, Alist, a, V):
    """own s2 point kinetic SUM_i tr(C_0i P C_0i P), C_0i = [eta V, eta A_i]."""
    P = A_STAR_P(Mc, a)
    X0 = ETA @ V
    tot = 0.0
    for A in Alist:
        Xi = ETA @ A
        C = X0 @ Xi - Xi @ X0
        CP = C @ P
        tot = tot + np.trace(CP @ CP)
    return float(tot)


def my_t4_pt(Alist, V):
    """own quartic point kinetic 4 SUM_i <[V,A_i]_eta, [V,A_i]_eta>_eta."""
    tot = 0.0
    for A in Alist:
        F = comm_eta_b(V, A)
        tot = tot + inner_eta_b(F, F)
    return float(4.0 * tot)


def my_polar10(f):
    """own polarization: quadratic f(V) -> 10x10 Q with f(V) = V.Q.V."""
    fB = [f(B) for B in BASIS]
    Q = np.zeros((10, 10))
    for i in range(10):
        for j in range(i, 10):
            Q[i, j] = Q[j, i] = 0.5 * (f(BASIS[i] + BASIS[j])
                                       - fB[i] - fB[j])
    return Q


def my_winding_scan(M):
    hits = []
    centers = [(float(rc), float(zc)) for rc in np.arange(5.0, 50.0, 5.0)
               for zc in np.arange(-10.0, 10.1, 5.0)]
    rd = ring_by_m13(M, NR, NZ, H)
    centers.append((float(rd["ring13_rho"]), float(rd["ring13_z"])))
    for rc, zc in centers:
        q, _ = winding_measure_biax(M, NR, NZ, H, rc, zc)
        if np.isfinite(q) and abs(q) >= 0.4:
            hits.append({"rho": rc, "z": zc, "q": float(q)})
    return hits


def save(claim, payload):
    out = {"task": "m5_20_5 adversarial audit", "date": "2026-07-14",
           "auditor": "independent agent (Fable 5), own instruments",
           "claims": {}, "wall_s": 0.0}
    if os.path.exists(AUD):
        with open(AUD) as f:
            out.update(json.load(f))
    out["claims"][claim] = payload
    out["wall_s"] = round(sum(c.get("phase_wall_s", 0.0)
                              for c in out["claims"].values()), 1)
    with open(AUD, "w") as f:
        json.dump(out, f, indent=1, default=float)


# =============== C1: band limit ===============
def phase_c1():
    t0 = time.time()
    rng = np.random.default_rng(101)
    states = {"pert_a": load_seed("recipe") + my_rand_sym(rng, 0.04),
              "pert_b": load_seed("recipe")
              + my_rand_sym(np.random.default_rng(202), 0.08)}
    gens = {"J23^K2@0.9": my_conj("J23", "K2", 0.9),
            "J12^K1@0.3": my_conj("J12", "K1", 0.3),
            "J23^K3@0.45": my_conj("J23", "K3", 0.45)}
    # own generator build vs the record's expm build (one-time cross)
    dev_gen = max(float(np.abs(my_conj(r, b, c)
                               - conj_gen(r, b, c)).max())
                  for r, b, c in (("J23", "K2", 0.9), ("J12", "K1", 0.3),
                                  ("J23", "K3", 0.45)))
    rows, worst_5_31, hmax_q2, hmax_gen = {}, 0.0, 0, 0
    for sname, M in states.items():
        for gname, G in gens.items():
            q5 = my_q2_avg(M, G, 5)
            q17 = my_q2_avg(M, G, 17)
            q31 = my_q2_avg(M, G, 31)
            r531 = abs(q5 - q31) / max(abs(q31), 1e-300)
            r1731 = abs(q17 - q31) / max(abs(q31), 1e-300)
            worst_5_31 = max(worst_5_31, r531)
            # Fourier content of the slice kinetic vs phi (64 samples)
            nf = 64
            phis = np.arange(nf) * (2 * np.pi / nf)
            f = np.array([q2_of(M, my_rot12(-p) @ G @ my_rot12(p))
                          for p in phis])
            amps = np.abs(np.fft.rfft(f)) / nf
            big = amps > 1e-9 * amps.max()
            hq = int(np.max(np.nonzero(big)[0])) if big.any() else 0
            tail = float(amps[5:].max() / max(amps.max(), 1e-300))
            hmax_q2 = max(hmax_q2, hq)
            # Fourier content of the rotated generator itself
            Gst = np.stack([my_rot12(-p) @ G @ my_rot12(p) for p in phis])
            ag = np.abs(np.fft.rfft(Gst, axis=0)) / nf
            agf = ag.reshape(ag.shape[0], -1).max(axis=1)
            bigg = agf > 1e-12 * agf.max()
            hg = int(np.max(np.nonzero(bigg)[0])) if bigg.any() else 0
            hmax_gen = max(hmax_gen, hg)
            rows[f"{sname}|{gname}"] = {
                "q2_nphi5": q5, "rel_5_vs_31": r531, "rel_17_vs_31": r1731,
                "max_harmonic_q2": hq, "tail_ge5_rel": tail,
                "max_harmonic_gen": hg}
            print(f"[C1] {sname}|{gname}: rel(5,31) {r531:.2e} "
                  f"rel(17,31) {r1731:.2e} h(q2) {hq} h(gen) {hg} "
                  f"tail>=5 {tail:.1e}", flush=True)
    ok = worst_5_31 < 1e-12 and hmax_q2 <= 4
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "own_generator_vs_record_expm": dev_gen,
           "worst_rel_nphi5_vs_31": worst_5_31,
           "max_harmonic_q2_measured": hmax_q2,
           "max_harmonic_generator_measured": hmax_gen,
           "note": ("nphi=5 exact confirmed; measured generator harmonics"
                    f" <= {hmax_gen} (note's stated bound was <= 2) and q2"
                    f" harmonics <= {hmax_q2} (note's bound <= 4): the"
                    " claim holds; the stated bounds are valid but loose"
                    if hmax_gen <= 2 else "generator harmonics EXCEED 2"),
           "rows": rows, "phase_wall_s": round(time.time() - t0, 1)}
    save("C1", out)
    print(f"[C1] verdict {out['verdict']} (wall {out['phase_wall_s']}s)",
          flush=True)


# =============== C2: ladders ===============
def _my_bisect(fn, lo, hi, tol=1e-6):
    flo, fhi = fn(lo), fn(hi)
    if flo * fhi > 0:
        return None, "no bracket"
    while hi - lo > tol:
        mid = 0.5 * (lo + hi)
        fm = fn(mid)
        if flo * fm <= 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return 0.5 * (lo + hi), "ok"


def phase_c2():
    t0 = time.time()
    M = load_seed("recipe")
    U = u_of(M)
    reads = loop_reads(M)
    w_lad = 0.0674 * reads["ring_rho"]
    claimed = {"J23^K2": 0.7039, "J23^K3": 0.0724, "J12^K1": 0.0056}
    windows = {"J23^K2": (0.4, 1.1), "J23^K3": (0.01, 0.4),
               "J12^K1": (1e-4, 0.1)}
    out = {"U": U, "ring_rho": reads["ring_rho"], "w_ladder": w_lad,
           "families": {}}
    all_ok = True
    for fam, (rot, boost) in (("J23^K2", ("J23", "K2")),
                              ("J23^K3", ("J23", "K3")),
                              ("J12^K1", ("J12", "K1"))):
        lo, hi = windows[fam]

        def q2c(chi, _r=rot, _b=boost):
            return my_q2_avg(M, my_conj(_r, _b, chi), 5)

        chi_c, s1 = _my_bisect(lambda c: q2c(c), lo, hi)
        tgt = -U / w_lad ** 2
        chi_l, s2 = _my_bisect(lambda c: q2c(c) - tgt, lo, hi)
        d_cl = abs(chi_l - chi_c) if (chi_c and chi_l) else None
        # monotonicity of omega*(chi) on the negative branch
        chis = chi_c + np.geomspace(1e-3, 2.5 - chi_c, 25)
        oms = []
        for c in chis:
            q2v = q2c(float(c))
            oms.append(float(np.sqrt(-U / q2v)) if U * q2v < 0 else None)
        oms_ok = [o for o in oms if o is not None]
        diffs = np.diff(oms_ok)
        n_up = int((diffs > 0).sum())
        n_ext = int(((diffs[:-1] * diffs[1:]) < 0).sum())
        dev = abs(chi_c - claimed[fam]) if chi_c else None
        ok = (chi_c is not None and dev < 1e-2 and n_ext == 0
              and n_up == 0 and d_cl is not None and d_cl < 1e-3)
        all_ok = all_ok and ok
        out["families"][fam] = {
            "chi_crossing_own": chi_c, "claimed": claimed[fam],
            "dev_from_claim": dev, "chi_ladder_own": chi_l,
            "delta_chi_ladder_vs_crossing": d_cl,
            "n_omega_increasing_steps": n_up, "n_interior_extrema": n_ext,
            "omega_star_range_scanned": [min(oms_ok), max(oms_ok)],
            "n_negative_branch_pts": len(oms_ok), "ok": ok}
        print(f"[C2] {fam}: chi_c(own) {chi_c:.6f} (claim "
              f"{claimed[fam]}, dev {dev:.1e}); |chi_lad-chi_c| "
              f"{d_cl:.2e}; up-steps {n_up} extrema {n_ext} -> "
              f"{'OK' if ok else 'FAIL'}", flush=True)
    out["verdict"] = "CONFIRMED" if all_ok else "REFUTED"
    out["phase_wall_s"] = round(time.time() - t0, 1)
    save("C2", out)
    print(f"[C2] verdict {out['verdict']} (wall {out['phase_wall_s']}s)",
          flush=True)


# =============== C3: the 18-run kill ===============
def phase_c3():
    t0 = time.time()
    with open(os.path.join(DATA, "m5_20_5_a_a1.json")) as f:
        wps = json.load(f)["working_points"]
    fams = {"J23^K2": ("J23", "K2"), "J12^K1": ("J12", "K1")}
    # own-instrument gate: my grad vs my complex step of my average
    rng = np.random.default_rng(303)
    Mg = load_seed("recipe") + my_rand_sym(rng, 0.03)
    Gg = my_conj("J23", "K2", 0.9)
    Dg = my_rand_sym(rng)
    lhs = float(np.sum(my_grad_q2_avg(Mg, Gg) * Dg))
    rhs = my_cs(lambda MM: my_q2_avg_c(MM, Gg), Mg, Dg)
    gate = abs(lhs - rhs) / max(abs(rhs), 1e-300)
    print(f"[C3] own grad-vs-own-CS gate: {gate:.2e}", flush=True)
    # expected values from the task's jsons
    exp = {}
    for k in range(3):
        with open(os.path.join(DATA, f"m5_20_5_a_a2_wp{k}.json")) as f:
            a2 = json.load(f)
        best = min(a2["runs"], key=lambda r: r["resid_final"])
        exp[f"wp{k}_best"] = {"resid": best["resid_final"],
                              "rel": best["rel_final"],
                              "q": best.get("q_r4"),
                              "method": best["method"],
                              "start": best["start"]}
        exp.setdefault("all_runs", []).extend(
            [{"wp": k, "m": r["method"], "s": r["start"],
              "rel": r["rel_final"], "bar": r["bar_met"]}
             for r in a2["runs"]])
    n_runs = len(exp["all_runs"])
    n_bar = sum(r["bar"] for r in exp["all_runs"])
    states = [("wp0_best", "m5_20_5_a_a2_wp0_best.npz", wps[0]),
              ("wp1_best", "m5_20_5_a_a2_wp1_best.npz", wps[1]),
              ("wp2_best", "m5_20_5_a_a2_wp2_best.npz", wps[2]),
              ("wp0_stall", "m5_20_5_a_a2_wp0_stall.npz", wps[0])]
    Mrec = load_seed("recipe")
    m13_rec = float(np.abs(Mrec[..., 1, 3]).max())
    rows = {}
    ok = gate < 1e-10 and n_bar == 0 and n_runs == 18
    for tag, fn, wp in states:
        M = np.load(os.path.join(DATA, fn))["M"]
        rot, boost = fams[wp["fam"]]
        G = my_conj(rot, boost, float(wp["chi"]))
        n, ns = my_resid(M, G, float(wp["omega"]))
        reads = loop_reads(M)
        m13 = float(np.abs(M[..., 1, 3]).max())
        hits = my_winding_scan(M)
        row = {"resid_own": n, "rel_own": n / ns, "gstat_norm": ns,
               "U": u_of(M), "q_ring": reads["q_r4"],
               "ring_rho": reads["ring_rho"], "max_abs_M13": m13,
               "m13_vs_recipe": m13 / m13_rec, "n_winding_hits": len(hits)}
        if tag in exp:
            row["resid_task"] = exp[tag]["resid"]
            row["rel_task"] = exp[tag]["rel"]
            row["rel_dev"] = abs(row["rel_own"] - exp[tag]["rel"]) / max(
                exp[tag]["rel"], 1e-300)
            ok = ok and row["rel_dev"] < 1e-6
        rows[tag] = row
        print(f"[C3] {tag}: resid(own) {n:.4e} rel(own) {n/ns:.4f} "
              f"(task {row.get('rel_task')}) q {reads['q_r4']} "
              f"|M13|max {m13:.2e} ({m13/m13_rec:.1e} x recipe) "
              f"hits {len(hits)} U {row['U']:.4f}", flush=True)
    # the "vacuum trap" sub-claim, split into its two halves:
    winding_gone = (rows["wp0_best"]["n_winding_hits"] == 0
                    and (rows["wp0_best"]["q_ring"] is None
                         or abs(rows["wp0_best"]["q_ring"]) < 1e-6))
    near_vacuum = (rows["wp0_best"]["m13_vs_recipe"] < 1e-2
                   and rows["wp0_best"]["U"] < 0.1)
    out = {"verdict": ("QUALIFIED" if (ok and winding_gone
                                       and not near_vacuum)
                       else "CONFIRMED" if (ok and winding_gone)
                       else "REFUTED"),
           "kill_18_runs_confirmed": bool(ok),
           "vacuum_trap": {
               "winding_gone": bool(winding_gone),
               "near_vacuum": bool(near_vacuum),
               "note": "wp0_best: q = 0 and 0 scan hits (winding IS"
                       " destroyed) BUT U = 18.7x the recipe loop and"
                       " |M13| keeps 30% amplitude: an unwound rough"
                       " state, NOT the vacuum; 'unwinding the loop to"
                       " the vacuum' should read 'destroying the"
                       " winding'"},
           "own_grad_cs_gate": gate, "n_runs_in_jsons": n_runs,
           "n_runs_meeting_bar": n_bar,
           "min_rel_loop_preserving": min(
               r["rel"] for r in exp["all_runs"]
               if r["m"] != "newton_krylov"),
           "min_rel_any": min(r["rel"] for r in exp["all_runs"]),
           "recipe_max_abs_M13": m13_rec,
           "states": rows, "phase_wall_s": round(time.time() - t0, 1)}
    save("C3", out)
    print(f"[C3] verdict {out['verdict']}: {n_runs} runs, {n_bar} met "
          f"bar; winding_gone {winding_gone} near_vacuum {near_vacuum}",
          flush=True)


# =============== C4: the directional block ===============
def _cos_row(M, G, tag, extra=None):
    gk = my_grad_q2_avg(M, G) * FREE4
    gs = grad_static_4(M, WSCALE, DELTA, w4=W4, rho4=RHO4) * FREE4
    nk = float(np.sqrt(np.sum(gk ** 2)))
    ns = float(np.sqrt(np.sum(gs ** 2)))
    dot = float(np.sum(gk * gs))
    cos = dot / max(nk * ns, 1e-300)
    tk, sk = my_sectors(gk)
    ts, ss = my_sectors(gs)
    # floor over REAL omega (omega^2 >= 0): 1.0 exactly when dot <= 0
    real_floor = 1.0 if dot <= 0 else float(np.sqrt(max(1 - cos ** 2, 0)))
    row = {"cos": cos, "norm_gkin": nk, "norm_gstat": ns,
           "unconstrained_floor_sqrt_1_m_cos2":
               float(np.sqrt(max(1 - cos ** 2, 0))),
           "real_omega_floor": real_floor,
           "gstat_time_frac": ts / max(np.hypot(ts, ss), 1e-300),
           "gkin_time_frac": tk / max(np.hypot(tk, sk), 1e-300)}
    if extra:
        row.update(extra)
    print(f"[C4] {tag}: cos {cos:+.4f} real-omega floor "
          f"{real_floor:.4f} unconstrained {row['unconstrained_floor_sqrt_1_m_cos2']:.4f} "
          f"gstat time-frac {row['gstat_time_frac']:.6f}", flush=True)
    return row


def phase_c4():
    t0 = time.time()
    M = load_seed("recipe")
    out = {"seed": {}, "scope_probes": {}, "perturbed_seed": {},
           "stall_state": {}}
    combos = {"wp0_J23K2_chi0.7045": ("J23", "K2", 0.704541015625),
              "wp1_J23K2_chi0.75": ("J23", "K2", 0.75),
              "wp2_J12K1_chi0.25": ("J12", "K1", 0.25)}
    for tag, (r, b, c) in combos.items():
        out["seed"][tag] = _cos_row(M, my_conj(r, b, c), f"seed {tag}")
    # scope probes: other chi values + the family the task never solved
    probes = [("J23", "K2", 0.72), ("J23", "K2", 0.9),
              ("J23", "K2", 1.2), ("J23", "K2", 2.0),
              ("J23", "K3", 0.1), ("J23", "K3", 0.3),
              ("J12", "K1", 0.1), ("J12", "K1", 0.5)]
    for r, b, c in probes:
        tag = f"{r}^{b}@chi{c}"
        out["scope_probes"][tag] = _cos_row(M, my_conj(r, b, c),
                                            f"probe {tag}")
    # perturbed seed
    rng = np.random.default_rng(33)
    Mp = M + my_rand_sym(rng, 0.02)
    for tag, (r, b, c) in (("wp0", combos["wp0_J23K2_chi0.7045"]),
                           ("wp2", combos["wp2_J12K1_chi0.25"])):
        out["perturbed_seed"][tag] = _cos_row(
            Mp, my_conj(r, b, c), f"perturbed {tag}",
            extra={"noise_amp": 0.02})
    # the wp0 stall state (post-descent background)
    Ms = np.load(os.path.join(DATA, "m5_20_5_a_a2_wp0_stall.npz"))["M"]
    r, b, c = combos["wp0_J23K2_chi0.7045"]
    out["stall_state"]["wp0"] = _cos_row(Ms, my_conj(r, b, c),
                                         "stall wp0")
    s = out["seed"]
    dev0 = abs(s["wp0_J23K2_chi0.7045"]["cos"] - (-0.328))
    dev1 = abs(s["wp1_J23K2_chi0.75"]["cos"] - (-0.328))
    dev2 = abs(s["wp2_J12K1_chi0.25"]["cos"] - 0.022)
    tfrac = s["wp0_J23K2_chi0.7045"]["gstat_time_frac"]
    claims_ok = dev0 < 5e-3 and dev1 < 5e-3 and dev2 < 5e-3 \
        and tfrac >= 0.999
    j23k2_neg = all(v["cos"] < 0 for k, v in out["scope_probes"].items()
                    if k.startswith("J23^K2"))
    j23k3_orth = all(0 < v["cos"] < 0.05
                     for k, v in out["scope_probes"].items()
                     if k.startswith("J23^K3"))
    pert_blocked = all(v["cos"] < 0.5
                       for v in out["perturbed_seed"].values())
    out["claims_ok"] = bool(claims_ok)
    out["anti_alignment_persists_J23K2_all_chi"] = bool(j23k2_neg)
    out["J23K3_family_orthogonal_not_antialigned"] = bool(j23k3_orth)
    out["block_persists_on_perturbed_seed"] = bool(pert_blocked)
    out["verdict"] = "CONFIRMED" if claims_ok else "REFUTED"
    out["scope_note"] = (
        "established: at the recipe seed the cosines match the claims;"
        " anti-alignment is stable across the whole J23^K2 chi range"
        " (0.72-2.0, cos -0.327..-0.328) and SURVIVES 0.02 random"
        " perturbation of the seed (cos moves to -0.39/-0.50, never"
        " toward +1). NOT established: anything beyond this loop"
        " background. NEW: the untested third family J23^K3 is"
        " orthogonal-type (cos +0.024..+0.028, like J12^K1), NOT"
        " anti-aligned: 'J23-family g_kin is ANTI-aligned' in the note"
        " overgeneralizes; the BLOCK still covers it (orthogonal cannot"
        " cancel: unconstrained floor 0.9996). The 0.944 'best"
        " achievable (ANY real omega)' label is wrong for cos < 0 rows:"
        " the optimum needs omega^2 < 0; over real omega the floor is"
        " exactly 1.0 (at omega = 0). At the wp0 STALL state the local"
        " geometry differs (cos +0.709): the seed-level table does not"
        " describe the stall neighborhood")
    out["phase_wall_s"] = round(time.time() - t0, 1)
    save("C4", out)
    print(f"[C4] verdict {out['verdict']}; J23^K2 all cos<0: {j23k2_neg};"
          f" J23^K3 orthogonal: {j23k3_orth}; perturbed blocked: "
          f"{pert_blocked}", flush=True)


# =============== C5: the a3 root loss ===============
def phase_c5():
    t0 = time.time()
    M = np.load(os.path.join(DATA, "m5_20_5_a_a3_wp0_state.npz"))["M"]
    omega = 0.11900147030942104          # the a3 working-point omega
    G = my_conj("J23", "K2", 0.704541015625)
    U = u_of(M)
    Q2 = my_q2_avg(M, G)
    Hval = U + omega ** 2 * Q2
    reads = loop_reads(M)
    claimed = {"U": 0.443, "Q2_avg": 1.386, "H": 0.463, "q": 0.5}
    ok = (abs(U - claimed["U"]) < 5e-3 and Q2 > 0
          and abs(Q2 - claimed["Q2_avg"]) < 5e-3
          and abs(Hval - claimed["H"]) < 5e-3
          and reads["q_r4"] is not None
          and abs(reads["q_r4"] - 0.5) < 1e-6)
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "U_own": U, "Q2_avg_own": Q2, "H_own": Hval,
           "H_rel_to_U": abs(Hval) / abs(U), "omega": omega,
           "q_ring": reads["q_r4"], "ring_rho": reads["ring_rho"],
           "root_exists": bool(U * Q2 < 0), "claimed": claimed,
           "phase_wall_s": round(time.time() - t0, 1)}
    save("C5", out)
    print(f"[C5] U {U:.4f} Q2_avg {Q2:+.4f} H {Hval:.4f} q "
          f"{reads['q_r4']} root_exists {out['root_exists']} -> "
          f"{out['verdict']}", flush=True)


# =============== C6: the s2 EL algebra ===============
def phase_c6():
    t0 = time.time()
    a = A_STAR
    rng = np.random.default_rng(11)
    M0 = load_seed("recipe") + my_rand_sym(rng, 0.05)
    Ar, Ap, Az = channels(M0, H)[:3]
    Mc = M0[: NR - 1, 1:-1]
    cells = [(int(rng.integers(0, NR - 1)), int(rng.integers(0, NZ - 2)))
             for _ in range(5)]
    # (a) own static density vs density_point static sector (and task's)
    dens_me = my_u_s2_grid(M0, a)
    dens_task = u_s2_density(M0, a)
    worst_a, worst_task = 0.0, 0.0
    for (ir, iz) in cells:
        Al = [Ar[ir, iz], Ap[ir, iz], Az[ir, iz]]
        ref = -density_point(Mc[ir, iz], [np.zeros((4, 4))] + Al, "s2", a)
        worst_a = max(worst_a, abs(float(dens_me[ir, iz]) - ref)
                      / max(abs(ref), 1e-12))
        worst_task = max(worst_task, abs(float(dens_task[ir, iz]) - ref)
                         / max(abs(ref), 1e-12))
    # random-matrix algebra check (no grid, no channels)
    worst_alg = 0.0
    for _ in range(3):
        Mr = rng.normal(size=(4, 4))
        Mr = 0.5 * (Mr + Mr.T)
        Alr = [rng.normal(size=(4, 4)) for _ in range(3)]
        P = A_STAR_P(Mr, a)
        tot = 0.0
        for i in range(3):
            for j in range(i + 1, 3):
                Xi, Xj = ETA @ Alr[i], ETA @ Alr[j]
                C = Xi @ Xj - Xj @ Xi
                tot += np.trace(C @ P @ C @ P)
        ref = -density_point(Mr, [np.zeros((4, 4))] + Alr, "s2", a)
        worst_alg = max(worst_alg, abs(tot - ref) / max(abs(ref), 1e-12))
    # (b) task g_u_s2 vs MY complex step of MY total, fresh direction
    D = my_rand_sym(np.random.default_rng(12))
    lhs = float(np.sum(g_u_s2(M0, a, w4=W4, rho4=RHO4) * D))
    rhs = my_cs(lambda MM: my_e_s2_c(MM, a), M0, D)
    rel_b = abs(lhs - rhs) / max(abs(rhs), 1e-300)
    # (c) task k10_s2 vs MY polarization of MY point kinetic (5 cells)
    K10t = k10_s2(M0, a)
    worst_c, worst_kfp = 0.0, 0.0
    for (ir, iz) in cells:
        Al = [Ar[ir, iz], Ap[ir, iz], Az[ir, iz]]
        Q_me = my_polar10(lambda V: my_t_s2_pt(Mc[ir, iz], Al, a, V))
        scale = max(np.abs(Q_me).max() * 2, 1e-12)
        worst_c = max(worst_c, float(
            np.abs(K10t[ir, iz] - 2.0 * Q_me).max()) / scale)
        Q_kfp = kin_form_point(Mc[ir, iz], Al, "s2", a)
        worst_kfp = max(worst_kfp, float(
            np.abs(2.0 * Q_kfp - 2.0 * Q_me).max()) / scale)
    ok = (worst_a < 1e-12 and worst_task < 1e-12 and worst_alg < 1e-12
          and rel_b < 1e-12 and worst_c < 1e-12 and worst_kfp < 1e-12)
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "a_static_density_own_vs_density_point": worst_a,
           "a_static_density_task_vs_density_point": worst_task,
           "a_random_matrix_algebra": worst_alg,
           "b_g_u_s2_vs_own_cs_of_own_total": rel_b,
           "c_k10_s2_vs_own_polarization": worst_c,
           "c_own_polarization_vs_kin_form_point": worst_kfp,
           "cells": cells, "phase_wall_s": round(time.time() - t0, 1)}
    save("C6", out)
    print(f"[C6] a(own/task/alg) {worst_a:.1e}/{worst_task:.1e}/"
          f"{worst_alg:.1e} b(cs) {rel_b:.1e} c(polar/kfp) "
          f"{worst_c:.1e}/{worst_kfp:.1e} -> {out['verdict']}", flush=True)


# =============== C7: the escape statics kill ===============
def my_fire(M0, e_g_fn, n_iter=1500, dt0=0.005, dt_max=0.05,
            log_every=250):
    """own minimal FIRE (frozen-time statics relax)."""
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = WCELL
    prec = (1.0 / wfull)[..., None, None]
    Mx = M0.copy()
    v = np.zeros_like(Mx)
    dt, alpha, n_pos = dt0, 0.1, 0
    hist = []
    for it in range(1, n_iter + 1):
        E, g = e_g_fn(Mx)
        F = -g * prec * FREE4
        F[..., 0, :] = 0.0
        F[..., :, 0] = 0.0
        p = float(np.sum(F * v))
        if p > 0:
            nv = float(np.sqrt(np.sum(v ** 2)))
            nf = float(np.sqrt(np.sum(F ** 2)))
            v = (1 - alpha) * v + alpha * F * (nv / max(nf, 1e-300))
            n_pos += 1
            if n_pos > 5:
                dt = min(dt * 1.1, dt_max)
                alpha *= 0.99
        else:
            v[:] = 0.0
            dt *= 0.5
            alpha, n_pos = 0.1, 0
        v = v + dt * F
        Mx = Mx + dt * v
        if it % log_every == 0 or it == n_iter:
            reads = loop_reads(Mx)
            E2, _ = e_g_fn(Mx)
            hist.append({"it": it, "E": E2, "q": reads["q_r4"],
                         "ring_rho": reads["ring_rho"]})
            print(f"    ownFIRE it {it}: E {E2:.4f} q {reads['q_r4']} "
                  f"ring {reads['ring_rho']:.2f}", flush=True)
    return Mx, hist


def phase_c7():
    t0 = time.time()
    a, gamma = A_STAR, GAMMA
    # (i) endpoint claims from the task's jsons
    ends = {}
    for b, key in ((1e-2, "0.01"), (1e-4, "0.0001"), (0.0, "0")):
        with open(os.path.join(DATA, f"m5_20_5_b_b1_b{key}.json")) as f:
            d = json.load(f)
        fin = d["relaxed"]
        ends[key] = {"E_final": fin.get("E"), "ring": fin.get("ring_rho"),
                     "q": fin.get("q"),
                     "q_at_first_checkpoint_500": d["hist"][0].get("q"),
                     "anchors_survive": d["anchors_survive"],
                     "E_qc_x_beta_recipe":
                         d["components_recipe"]["E_qc_x_beta"]}
    ring_claim_ok = (abs(ends["0.01"]["ring"] - 42.3) < 0.2
                     and abs(ends["0.0001"]["ring"] - 27.1) < 0.2
                     and abs(ends["0"]["ring"] - 27.1) < 0.2)
    q_claim_ok = all(abs(e["q_at_first_checkpoint_500"] or 0.0) < 1e-6
                     for e in ends.values())
    # (ii) E_s2 on the recipe: own vs task vs the m5_20_4 audit record
    Mrec = load_seed("recipe")
    e_own = my_e_s2(Mrec, a)
    e_task = float(np.real(e_s2_static_c(Mrec, a)))
    with open(os.path.join(DATA, "m5_20_4_audit.json")) as f:
        e_prev = json.load(f)["claims"]["C8"][
            "b_s2_static_energy_on_recipe"]
    e_ok = (abs(e_own - (-0.693)) < 1e-3
            and abs(e_own - e_task) < 1e-12
            and abs(e_own - e_prev) < 1e-12)
    print(f"[C7] E_s2(recipe): own {e_own:.10f} task {e_task:.10f} "
          f"m5_20_4-audit {e_prev:.10f}", flush=True)
    # inline gate for the reused gradient (also done in C6b)
    rng = np.random.default_rng(77)
    Mg = Mrec + my_rand_sym(rng, 0.03)
    D = my_rand_sym(rng)
    rel_g = abs(float(np.sum(g_u_s2(Mg, a, w4=W4, rho4=RHO4) * D))
                - my_cs(lambda MM: my_e_s2_c(MM, a), Mg, D))
    rel_g /= max(abs(my_cs(lambda MM: my_e_s2_c(MM, a), Mg, D)), 1e-300)
    # (iii) own short frozen-time relax at beta = 0
    def e_g(MM):
        E = float(np.real(e_static_c(MM, WSCALE, DELTA))) \
            + gamma * my_e_s2(MM, a)
        G = grad_static_4(MM, WSCALE, DELTA, w4=W4, rho4=RHO4) \
            + gamma * g_u_s2(MM, a, w4=W4, rho4=RHO4)
        return E, G

    E0, _ = e_g(Mrec)
    reads0 = loop_reads(Mrec)
    print(f"[C7] own relax start: E {E0:.4f} q {reads0['q_r4']} ring "
          f"{reads0['ring_rho']:.2f}", flush=True)
    Mend, hist = my_fire(Mrec, e_g, n_iter=1500)
    q_end = hist[-1]["q"]
    q_collapsed = (q_end is None) or abs(q_end) < 0.05
    e_dropped = hist[-1]["E"] < E0
    ring_out = hist[-1]["ring_rho"] > reads0["ring_rho"] + 2.0
    it_collapse = next((h["it"] for h in hist
                        if h["q"] is None or abs(h["q"]) < 0.05), None)
    ok = (ring_claim_ok and q_claim_ok and e_ok and rel_g < 1e-10
          and q_collapsed and e_dropped)
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "task_endpoints": ends,
           "ring_endpoints_match_claim": bool(ring_claim_ok),
           "q_zero_at_first_checkpoint_all_beta": bool(q_claim_ok),
           "e_s2_recipe_own": e_own, "e_s2_recipe_task": e_task,
           "e_s2_recipe_m5204_audit": e_prev,
           "g_u_s2_cs_gate": rel_g,
           "own_relax_beta0": {
               "E_start": E0, "E_end": hist[-1]["E"],
               "q_start": reads0["q_r4"], "q_end": q_end,
               "ring_start": reads0["ring_rho"],
               "ring_end": hist[-1]["ring_rho"],
               "own_iter_first_q_collapse": it_collapse,
               "q_collapsed": bool(q_collapsed),
               "E_decreased": bool(e_dropped),
               "ring_drifted_outward": bool(ring_out),
               "hist": hist},
           "phase_wall_s": round(time.time() - t0, 1)}
    save("C7", out)
    print(f"[C7] verdict {out['verdict']}: own beta=0 relax q "
          f"{reads0['q_r4']} -> {q_end} (collapse by it {it_collapse}), "
          f"E {E0:.3f} -> {hist[-1]['E']:.3f}, ring "
          f"{reads0['ring_rho']:.1f} -> {hist[-1]['ring_rho']:.1f}",
          flush=True)


# =============== C8: PSD margins ===============
def phase_c8(n_cells=320):
    t0 = time.time()
    a, gamma = A_STAR, GAMMA
    M = load_seed("recipe")
    Mc = M[: NR - 1, 1:-1]
    Ar, Ap, Az = channels(M, H)[:3]
    Kq4 = 4.0 * build_k10(M, H)
    Ks2 = k10_s2(M, a)
    Kc1 = k10_add(Mc, 1.0, a)
    rng = np.random.default_rng(88)
    cells = {(int(rng.integers(0, NR - 1)), int(rng.integers(0, NZ - 2)))
             for _ in range(n_cells)}
    w4, ws2, wqc = 0.0, 0.0, 0.0
    for (ir, iz) in cells:
        Al = [Ar[ir, iz], Ap[ir, iz], Az[ir, iz]]
        H4 = 2.0 * my_polar10(lambda V: my_t4_pt(Al, V))
        Hs2 = 2.0 * my_polar10(
            lambda V: my_t_s2_pt(Mc[ir, iz], Al, a, V))
        Hqc = 2.0 * my_polar10(
            lambda V: float(t_add_density(Mc[ir, iz], V, a)))
        w4 = max(w4, float(np.abs(H4 - Kq4[ir, iz]).max())
                 / max(np.abs(Kq4[ir, iz]).max(), 1e-12))
        ws2 = max(ws2, float(np.abs(Hs2 - Ks2[ir, iz]).max())
                  / max(np.abs(Ks2[ir, iz]).max(), 1e-12))
        wqc = max(wqc, float(np.abs(Hqc - Kc1[ir, iz]).max())
                  / max(np.abs(Kc1[ir, iz]).max(), 1e-12))
    print(f"[C8] per-cell Hessian checks over {len(cells)} cells: "
          f"quartic {w4:.1e} s2 {ws2:.1e} qc {wqc:.1e}", flush=True)
    claims = {"0": -1e-13, "0.0001": 2.45e-3, "0.01": 2.45e-1}
    rows = {}
    for beta in (0.0, 1e-4, 1e-2):
        lam = np.linalg.eigvalsh(Kq4 + gamma * Ks2 + beta * Kc1)
        mn = float(lam.min())
        amin = np.unravel_index(int(lam.min(axis=-1).argmin()),
                                lam.shape[:-1])
        rows[f"beta={beta:g}"] = {"mineig": mn,
                                  "argmin_cell": list(map(int, amin))}
        print(f"[C8] beta {beta:g}: full-grid mineig {mn:.3e} at cell "
              f"{amin}", flush=True)
    # pure-polarization re-check at the beta = 0 argmin cell
    ir, iz = rows["beta=0"]["argmin_cell"]
    Al = [Ar[ir, iz], Ap[ir, iz], Az[ir, iz]]
    Hcell = (2.0 * my_polar10(lambda V: my_t4_pt(Al, V))
             + gamma * 2.0 * my_polar10(
                 lambda V: my_t_s2_pt(Mc[ir, iz], Al, a, V)))
    mn_cell = float(np.linalg.eigvalsh(Hcell).min())
    m0 = rows["beta=0"]["mineig"]
    m4 = rows["beta=0.0001"]["mineig"]
    m2 = rows["beta=0.01"]["mineig"]
    ok = (w4 < 1e-12 and ws2 < 1e-12 and wqc < 1e-12
          and abs(m0) < 1e-11
          and abs(m4 - 2.45e-3) / 2.45e-3 < 1e-2
          and abs(m2 - 2.45e-1) / 2.45e-1 < 1e-2
          and abs(mn_cell) < 1e-11)
    out = {"verdict": "CONFIRMED" if ok else "REFUTED",
           "n_cells_polarized": len(cells),
           "worst_cell_rel_quartic_vs_4build_k10": w4,
           "worst_cell_rel_s2_vs_k10_s2": ws2,
           "worst_cell_rel_qc_vs_k10_add": wqc,
           "fullgrid": rows, "claimed": claims,
           "argmin_cell_pure_polarization_mineig": mn_cell,
           "phase_wall_s": round(time.time() - t0, 1)}
    save("C8", out)
    print(f"[C8] verdict {out['verdict']} (argmin-cell polarization "
          f"mineig {mn_cell:.2e})", flush=True)


# =============== C9: completeness / overclaim sweep ===============
def phase_c9():
    t0 = time.time()
    # numeric spot checks feeding the prose findings
    nk_factors = []
    for k in range(3):
        with open(os.path.join(DATA, f"m5_20_5_a_a2_wp{k}.json")) as f:
            a2 = json.load(f)
        for r in a2["runs"]:
            if r["method"] == "newton_krylov":
                nk_factors.append(round(r["resid_start"]
                                        / r["resid_final"], 1))
    with open(os.path.join(DATA, "m5_20_5_b_b1_b0.json")) as f:
        b0j = json.load(f)
    e_b0_final = b0j["relaxed"]["E"]
    e_b0_2500 = [h for h in b0j["hist"] if h["it"] == 2500][0]["E"]
    e_b0_start = (b0j["components_recipe"]["E_old"]
                  + b0j["components_recipe"]["E_s2_x_gamma"])
    with open(os.path.join(DATA, "m5_20_5_a_a2x_wp0.json")) as f:
        a2x = json.load(f)
    sec = a2x["states"]["recipe_seed"]["sectors_gstat"]
    tfrac = sec["time_row"] / np.hypot(sec["time_row"],
                                       sec["spatial_block"])
    findings = [
        {"id": "F1", "severity": "wording",
         "where": "method note section 1.4b table",
         "issue": "column 'Best achievable rel residual (ANY real omega)'"
                  ": for the anti-aligned J23 rows the 0.944 optimum"
                  " requires omega^2 < 0; over real omega the floor is"
                  " exactly 1.0 (attained at omega = 0). 0.944 is the"
                  " unconstrained (imaginary-omega) bound."},
        {"id": "F2", "severity": "wording",
         "where": "method note section 1.4 verdict + findings row 3",
         "issue": "'3 working points spanning the distinct families':"
                  " only 2 of the 3 distinct families were solved"
                  " (J23^K2 twice, J12^K1 once; J23^K3 never). The"
                  " audit's own probe fills the hole: see C4"
                  " scope_probes J23^K3."},
        {"id": "F3", "severity": "number",
         "where": "method note section 2.3 (beta = 0 row prose)",
         "issue": f"'E 1.037 -> 0.085 over 3000 iterations': the json"
                  f" 3000-iteration value is {e_b0_final:.4f}; 0.085 is"
                  f" the 2500-iteration value ({e_b0_2500:.4f}). Start"
                  f" 1.037 checks ({e_b0_start:.4f})."},
        {"id": "F4", "severity": "number",
         "where": "task_details FINDINGS row 3",
         "issue": f"'Newton-Krylov reduces the residual 15-100x': the"
                  f" measured per-run factors are {sorted(nk_factors)}"
                  f" (range ~5x to ~472x)."},
        {"id": "F5", "severity": "wording",
         "where": "method note section 2.4",
         "issue": "'the beta-margin is background-independent': true"
                  " across the measured in-band backgrounds (and the"
                  " m5_20_4 audit's five), but the m5_20_4 audit also"
                  " recorded 0.02546 (not 0.0245) per beta = 1e-3 on"
                  " recipe_perturbed and indefiniteness outside the"
                  " physical band; scope it to measured in-band"
                  " backgrounds."},
        {"id": "F6", "severity": "nit (conservative)",
         "where": "method note section 1.4b",
         "issue": f"'g_stat is 99.998% TIME ROW': measured"
                  f" {100 * tfrac:.5f}% (the note understates)."},
        {"id": "F9", "severity": "wording",
         "where": "method note section 1.4 + 1.4b ('vacuum trap')",
         "issue": "'unwinding the loop to the VACUUM (the trivial"
                  " extremal)': the NK end states destroy the winding"
                  " (q = 0, zero scan hits) but are NOT near-vacuum:"
                  " wp0_best has U = 6.44 (18.7x the loop's 0.344) and"
                  " keeps 30% of the recipe |M13| amplitude, and its"
                  " residual is rel 1.26 (no extremal reached). Say"
                  " 'destroying the winding' / 'unwinding trap', not"
                  " 'to the vacuum'."},
        {"id": "F10", "severity": "wording",
         "where": "method note section 1.4b table row 2",
         "issue": "'J23-family g_kin is ANTI-aligned (cos < 0)': only"
                  " J23^K2 was measured. The audit measured J23^K3 at"
                  " chi = 0.1 / 0.3: cos = +0.028 / +0.024 (orthogonal"
                  " type, like J12^K1), NOT anti-aligned. The block"
                  " still covers it (orthogonal cannot cancel), but the"
                  " row should read 'the J23^K2 (and mirror J13^K1)"
                  " family'."},
        {"id": "F11", "severity": "nit (conservative)",
         "where": "method note section 1.1 (band-limit reason)",
         "issue": "'the adjoint action has phi-harmonics <= 2 ...=>"
                  " harmonics <= 4': measured generator harmonics <= 1"
                  " and q2 harmonics <= 2 (so even nphi >= 3 is exact)."
                  " The stated bounds are valid but loose; the gated"
                  " claim (nphi >= 5 exact) holds."},
        {"id": "F7", "severity": "scope-check PASS",
         "where": "method note sections 1.4b / 1.5",
         "issue": "kill statements properly scoped ('on the loop"
                  " background', 'at any measured working point', 'in"
                  " the reachable basin'); no general-death claim of the"
                  " rigid-orbit BVP found."},
        {"id": "F8", "severity": "pre-registration PASS",
         "where": "a2 bar / B3 skip / A5 skip",
         "issue": "the bar (rel <= 1e-3 AND q = 0.5 intact) is coded"
                  " exactly as registered; B3 skip and A5 skip both"
                  " covered by pre-registered contingencies; the a2x"
                  " and beta-extension deviations are logged."},
    ]
    out = {"verdict": "QUALIFIED",
           "note": "content confirmed; wording/number fixes needed"
                   " (F1-F6)",
           "nk_reduction_factors": sorted(nk_factors),
           "b1_beta0_E": {"start": e_b0_start, "it2500": e_b0_2500,
                          "it3000": e_b0_final},
           "gstat_time_frac_pct": 100 * tfrac,
           "findings": findings,
           "phase_wall_s": round(time.time() - t0, 1)}
    save("C9", out)
    print(f"[C9] {len(findings)} findings recorded "
          f"({sum(1 for x in findings if 'PASS' not in x['severity'])}"
          " need action)", flush=True)


PHASES = {"c1": phase_c1, "c2": phase_c2, "c3": phase_c3,
          "c4": phase_c4, "c5": phase_c5, "c6": phase_c6,
          "c7": phase_c7, "c8": phase_c8, "c9": phase_c9}

if __name__ == "__main__":
    which = ARGV[0] if ARGV else "all"
    t00 = time.time()
    if which == "all":
        for name, fn in PHASES.items():
            fn()
    else:
        PHASES[which]()
    print(f"[AUDIT] done ({which}) wall {time.time() - t00:.0f}s",
          flush=True)
