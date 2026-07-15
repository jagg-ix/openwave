"""M5.12 block-15 ADVERSARIAL AUDIT, part 2 (P1): the Rayleigh-quotient
floor over the WHOLE first-harmonic class, not the claimant's 23 profiles.

At seed level (background hedgehog M0 + first harmonic A1 = x, B1 = A2 =
B2 = 0) both quadratic forms are exact to O(|x|^4):
    S0(x) = S_bg + s(x),   s = Hessian form of the static energy
    Q2(x) = -q(x),         q = the kinetic (omega^2) form
so at matched a2 the balance root obeys
    omega_bal^2(x) = (S_bg + s(x)) / q(x)
      = c^T P c / c^T Q c,  P = (S_bg/a2*) G + S  (on any basis, G = Gram)
a GENERALIZED RAYLEIGH QUOTIENT: its true minimum over a basis span is the
largest eigenvalue lam of eigh(Q, P), omega_min = 1/sqrt(lam). The basis
here spans the claimant's 23 profiles (direction (cr, cz) on the 0r/0z
components) PLUS directions the sweep never probed: single components,
0phi, swapped, z-odd, z-anisotropic widths, spatial-block, (0,0), random.

Also in this script:
  (b) nonlinearity: exact omega_bal vs the quadratic model at a2*/4, a2*/2,
      a2* on the claimant's floor shape (the 4x Q2 scaling check)
  (c) the a2 convention: re-rank the 23 seeds under cell-weighted a2
  (d) the harmonic-relabel hole: the same shape moved to the SECOND
      harmonic halves omega_bal exactly and is invisible to a2_free

Run:  python3 -u m5_12_audit_b15_rayleigh.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.linalg import eigh
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords, cell_weights                       # noqa: E402
from m5_16_axisym import hedgehog_field, pin_mask                        # noqa: E402
from m5_12_dressed import to_covariant                                   # noqa: E402
from m5_12_d3a_bvp import shat, x_pack                                   # noqa: E402
from m5_12_d3b_newton import wscale_at                                   # noqa: E402

h = 1.0
nr, nz = 32, 64
WSC = wscale_at(nr, nz, h, 8.0 * 32 / 96)
W_B = 8.0 * 32 / 96
A2_STAR = 0.30372464947752503        # the c2-seed reference (b15 JSON)

R, Z = grid_coords(nr, nz, h)
M0 = to_covariant(hedgehog_field(R, Z, W_B))
PIN = pin_mask(nr, nz)
FREE = np.broadcast_to((~PIN)[..., None, None]
                       & np.ones((1, 1, 4, 4), bool), M0.shape)
R2 = R ** 2 + Z ** 2
RR = np.sqrt(R2) + 1e-12
CR, CZ = R / RR, Z / RR


def x_of(A1, Nt=1, A2=None):
    As = [A1] + [np.zeros_like(M0) for _ in range(Nt - 1)]
    if A2 is not None:
        As[1] = A2
    Bs = [np.zeros_like(M0) for _ in range(Nt)]
    return x_pack(M0, As, Bs)


def a2_of(A1):
    return float(np.sum(A1[FREE] ** 2))


def probe_exact(X):
    s0 = shat(X, 0.0, h, WSC)
    q2 = s0 - shat(X, 1.0, h, WSC)
    wb = float(np.sqrt(s0 / -q2)) if (q2 < 0 and s0 > 0) else None
    return s0, q2, wb


def prof(name, k):
    w = k * W_B
    if name == "gauss":
        return np.exp(-R2 / w ** 2)
    if name == "lag1":
        return np.exp(-R2 / w ** 2) * (1.0 - 2.0 * R2 / w ** 2)
    if name == "lag2":
        x = 2.0 * R2 / w ** 2
        return np.exp(-R2 / w ** 2) * (1.0 - 2.0 * x + 0.5 * x ** 2)
    if name == "shell":
        return np.exp(-((np.sqrt(R2) - w) ** 2) / W_B ** 2)
    if name == "lorentz1":
        return (1.0 + R2 / w ** 2) ** -1.0
    if name == "lorentz2":
        return (1.0 + R2 / w ** 2) ** -2.0
    if name == "rgauss":
        return (np.sqrt(R2) / w) * np.exp(-R2 / w ** 2)
    raise ValueError(name)


def mk(compfields):
    """A1 from {(a,b): field}, symmetrized, pinned, unit a2 norm."""
    A1 = np.zeros_like(M0)
    for (a, b), f in compfields.items():
        A1[..., a, b] = A1[..., a, b] + f
        if a != b:
            A1[..., b, a] = A1[..., b, a] + f
    A1[PIN] = 0.0
    n = np.sqrt(a2_of(A1))
    return A1 / n, n


# ---------------- basis ----------------
BASIS, LABELS = [], []
P23 = [("gauss", k) for k in (0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0)] \
    + [("lag1", k) for k in (1.0, 2.0, 3.0)] \
    + [("lag2", k) for k in (1.0, 2.0)] \
    + [("shell", k) for k in (1.0, 2.0, 3.0)] \
    + [("lorentz1", k) for k in (1.0, 2.0)] \
    + [("lorentz2", k) for k in (1.0, 2.0)] \
    + [("rgauss", k) for k in (1.0, 2.0, 3.0)]
P6 = [("gauss", 1.0), ("gauss", 2.0), ("gauss", 3.0),
      ("rgauss", 2.0), ("shell", 1.0), ("shell", 2.0)]

for nm, k in P23:                                    # D1: claimant class
    b = prof(nm, k)
    v, _ = mk({(0, 1): b * CR, (0, 3): b * CZ})
    BASIS.append(v); LABELS.append(f"D1_{nm}_k{k:g}")
for nm, k in P6:                                     # D2: 0r only
    b = prof(nm, k)
    v, _ = mk({(0, 1): b * CR})
    BASIS.append(v); LABELS.append(f"D2_0r_{nm}_k{k:g}")
for nm, k in P6:                                     # D3: 0z only
    b = prof(nm, k)
    v, _ = mk({(0, 3): b * CZ})
    BASIS.append(v); LABELS.append(f"D3_0z_{nm}_k{k:g}")
for nm, k in P6:                                     # D4: 0phi
    b = prof(nm, k)
    v, _ = mk({(0, 2): b * CR})
    BASIS.append(v); LABELS.append(f"D4_0phi_{nm}_k{k:g}")
for nm, k in P6:                                     # D5: swapped
    b = prof(nm, k)
    v, _ = mk({(0, 1): b * CZ, (0, 3): b * CR})
    BASIS.append(v); LABELS.append(f"D5_swap_{nm}_k{k:g}")
for nm, k in P6:                                     # D6: z-odd
    b = prof(nm, k) * (Z / W_B)
    v, _ = mk({(0, 1): b * CR, (0, 3): b * CZ})
    BASIS.append(v); LABELS.append(f"D6_zodd_{nm}_k{k:g}")
for wr, wz in ((1, 3), (3, 1), (1, 6), (6, 1), (2, 4), (4, 2)):  # D7
    b = np.exp(-(R ** 2 / (wr * W_B) ** 2 + Z ** 2 / (wz * W_B) ** 2))
    v, _ = mk({(0, 1): b * CR, (0, 3): b * CZ})
    BASIS.append(v); LABELS.append(f"D7_aniso_{wr}x{wz}")
for nm, k in (("gauss", 1.0), ("gauss", 2.0)):       # D8: spatial block
    b = prof(nm, k)
    for comp in ((1, 1), (3, 3), (1, 3), (2, 2)):
        v, _ = mk({comp: b})
        BASIS.append(v); LABELS.append(f"D8_sp{comp[0]}{comp[1]}_{nm}_k{k:g}")
for nm, k in (("gauss", 1.0), ("gauss", 2.0)):       # D9: (0,0)
    b = prof(nm, k)
    v, _ = mk({(0, 0): b})
    BASIS.append(v); LABELS.append(f"D9_00_{nm}_k{k:g}")
rng = np.random.default_rng(7)                        # D10: random smooth
for i in range(3):
    A1 = gaussian_filter(rng.standard_normal(M0.shape), (2.0, 2.0, 0, 0))
    A1 = 0.5 * (A1 + np.swapaxes(A1, -1, -2))
    A1[PIN] = 0.0
    A1 /= np.sqrt(a2_of(A1))
    BASIS.append(A1); LABELS.append(f"D10_rand{i}")

N = len(BASIS)
print(f"[basis] N = {N} vectors")

OUT = {"script": "m5_12_audit_b15_rayleigh.py", "N_basis": N,
       "labels": LABELS, "sections": {}}
t0 = time.time()

# ---------------- background + linearity gate ----------------
S_BG = shat(x_of(np.zeros_like(M0)), 0.0, h, WSC)
print(f"[bg] S_bg = {S_BG:.6f}")
T = 3e-3


def forms_of(A1):
    """(s, k) form values of a (not necessarily unit) A1 at amplitude T."""
    Xs = x_of(T * A1)
    s0 = shat(Xs, 0.0, h, WSC)
    q2 = s0 - shat(Xs, 1.0, h, WSC)
    return (s0 - S_BG) / T ** 2, q2 / T ** 2


sA, kA = forms_of(BASIS[2])          # D1 gauss k1 (the bmix control)
sB, kB = forms_of(2.0 * BASIS[2])
gate_quad = max(abs(sB / sA - 4.0), abs(kB / kA - 4.0))
# Nt=1 vs Nt=2 equivalence
sh1 = shat(x_of(0.1 * BASIS[2]), 1.0, h, WSC)
sh2 = shat(x_of(0.1 * BASIS[2], Nt=2), 1.0, h, WSC)
gate_nt = abs(sh1 - sh2) / abs(sh1)
print(f"[gate] quadratic-scaling at T: {gate_quad:.2e}  "
      f"Nt1==Nt2: {gate_nt:.2e}")
OUT["sections"]["gates"] = {"S_bg": S_BG, "T": T,
                            "quad_scaling_dev": gate_quad,
                            "nt_equiv_rel": gate_nt}

# ---------------- Gram assembly (cached) ----------------
GRAM_PATH = os.path.join(DATA, "m5_12_audit_b15_gram.npz")
if os.path.exists(GRAM_PATH):
    d = np.load(GRAM_PATH)
    G, S, K = d["G"], d["S"], d["K"]
    print(f"[gram] loaded cache {os.path.basename(GRAM_PATH)}")
else:
    print("[gram] assembling S, K on the basis (polarization) ...")
    G = np.zeros((N, N))
    S = np.zeros((N, N))
    K = np.zeros((N, N))
    diag_s = np.zeros(N)
    diag_k = np.zeros(N)
    for i in range(N):
        G[i, i] = a2_of(BASIS[i])
        diag_s[i], diag_k[i] = forms_of(BASIS[i])
        S[i, i], K[i, i] = diag_s[i], diag_k[i]
    cnt = 0
    for i in range(N):
        for j in range(i + 1, N):
            G[i, j] = G[j, i] = float(np.sum(BASIS[i][FREE]
                                             * BASIS[j][FREE]))
            sij, kij = forms_of(BASIS[i] + BASIS[j])
            S[i, j] = S[j, i] = 0.5 * (sij - diag_s[i] - diag_s[j])
            K[i, j] = K[j, i] = 0.5 * (kij - diag_k[i] - diag_k[j])
            cnt += 1
        if i % 10 == 0:
            print(f"  row {i}/{N}  wall {time.time()-t0:.0f}s")
    print(f"[gram] {cnt} pairs, wall {time.time()-t0:.0f}s")
    np.savez_compressed(GRAM_PATH, G=G, S=S, K=K,
                        labels=np.array(LABELS))


# ---------------- the pencil ----------------
def pencil_floor(idx, tag, tau=1e-6):
    """floor of the quadratic model on span(BASIS[idx]); the Gram keep
    threshold tau guards against polarization noise blown up by 1/lam on
    near-dependent basis vectors. If P is indefinite even after truncation
    the most negative P direction is returned for EXACT adjudication."""
    idx = np.asarray(idx)
    Gs, Ss, Ks = G[np.ix_(idx, idx)], S[np.ix_(idx, idx)], K[np.ix_(idx, idx)]
    lam, V = np.linalg.eigh(Gs)
    keep = lam > tau * lam.max()
    W = V[:, keep] / np.sqrt(lam[keep])
    Sp = W.T @ Ss @ W
    Qp = -(W.T @ Ks @ W)                     # q form = -Q2
    Pp = (S_BG / A2_STAR) * np.eye(Sp.shape[0]) + Sp
    pev, PV = np.linalg.eigh(Pp)
    pmin = float(pev[0])
    res = {"tag": tag, "tau": tau, "n_span": int(keep.sum()),
           "P_min_eig": pmin}
    if pmin <= 0:
        # quadratic model predicts S0 <= 0 somewhere: hand back that
        # direction; the caller exact-evaluates it (ground truth)
        res["indefinite_P"] = True
        res["omega_quad"] = None
        c = W @ PV[:, 0]
        return res, idx, c
    ev, EV = eigh(Qp, Pp)
    lam_max = float(ev[-1])
    res["indefinite_P"] = False
    res["lam_max"] = lam_max
    res["omega_quad"] = (1.0 / np.sqrt(lam_max) if lam_max > 0 else None)
    c = W @ EV[:, -1]
    return res, idx, c


def build_from_coeffs(idx, c):
    A1 = np.zeros_like(M0)
    for i, ci in zip(idx, c):
        A1 = A1 + ci * BASIS[i]
    A1[PIN] = 0.0
    return A1 * np.sqrt(A2_STAR / a2_of(A1))


def exact_at_a2star(idx, c):
    A1 = build_from_coeffs(idx, c)
    s0, q2, wb = probe_exact(x_of(A1, Nt=2))
    return A1, s0, q2, wb


d1_idx = [i for i, l in enumerate(LABELS) if l.startswith("D1_")]
runs = {}
for tag, idx in (("D1_only", d1_idx), ("full", list(range(N)))):
    per_tau = []
    chosen = None
    for tau in (1e-4, 1e-6, 1e-8):
        res, ridx, c = pencil_floor(idx, tag, tau)
        A1x, s0x, q2x, wbx = exact_at_a2star(ridx, c)
        res.update({"S0_exact": s0x, "Q2_exact": q2x,
                    "omega_exact_at_a2star": wbx})
        mag = np.abs(c) / np.linalg.norm(c)
        topi = np.argsort(-mag)[:8]
        res["top_coeffs"] = [{"label": LABELS[ridx[i]],
                              "coeff_share": float(mag[i])} for i in topi]
        per_tau.append(res)
        oq = res["omega_quad"]
        print(f"[pencil {tag} tau={tau:g}] n_span={res['n_span']} "
              f"P_min={res['P_min_eig']:+.2f} "
              f"indef={res['indefinite_P']} "
              f"w_quad={oq if oq else float('nan'):.4f} "
              f"EXACT: S0={s0x:.4f} Q2={q2x:+.5f} "
              f"w_bal={wbx if wbx else float('nan'):.4f}")
        # choose: the direction whose EXACT omega_bal is lowest (with a
        # valid balance root); indefinite-P directions compete via their
        # exact probes too
        if wbx is not None and (chosen is None
                                or wbx < chosen["omega_exact_at_a2star"]):
            chosen = dict(res)
            chosen["A1"] = A1x
    runs[tag] = {"per_tau": per_tau,
                 "best_exact": {k: v for k, v in (chosen or {}).items()
                                if k != "A1"}}
    if tag == "full" and chosen is not None:
        np.savez_compressed(
            os.path.join(DATA, "m5_12_audit_b15_rayleigh_opt.npz"),
            A1=chosen["A1"].astype(np.float32))
OUT["sections"]["pencil"] = {"D1_only": runs["D1_only"],
                             "full": runs["full"],
                             "claimant_floor": 8.2348}

# ---------------- (b) nonlinearity on the claimant floor shape ----------------
print("=== (b) nonlinearity: exact vs quadratic on rgauss_k2 D1 shape ===")
b = prof("rgauss", 2.0)
v_rg, _ = mk({(0, 1): b * CR, (0, 3): b * CZ})
s_rg, k_rg = forms_of(v_rg)
rows_nl = []
for fac in (0.25, 0.5, 1.0):
    a2t = fac * A2_STAR
    A1t = v_rg * np.sqrt(a2t)
    s0, q2, wb = probe_exact(x_of(A1t, Nt=2))
    w_quad = float(np.sqrt((S_BG + a2t * s_rg) / (a2t * (-k_rg))))
    rows_nl.append({"a2_over_a2star": fac, "omega_exact": wb,
                    "omega_quad_model": w_quad,
                    "Q2_exact": q2, "Q2_quad": a2t * k_rg,
                    "Q2_ratio_exact_over_quad": q2 / (a2t * k_rg)})
    print(f"  a2 = {fac:>4}*a2*: exact w={wb:.4f} quad w={w_quad:.4f} "
          f"Q2 exact/quad = {q2/(a2t*k_rg):.4f}")
# the eps vs eps/2 4x check at FULL amplitude
A1f = v_rg * np.sqrt(A2_STAR)
_, q2f, _ = probe_exact(x_of(A1f, Nt=2))
_, q2h, _ = probe_exact(x_of(0.5 * A1f, Nt=2))
print(f"  Q2(eps)/Q2(eps/2) = {q2f/q2h:.4f}  (4.0 if quadratic)")
OUT["sections"]["nonlinearity"] = {"rows": rows_nl,
                                   "q2_eps_over_epshalf": q2f / q2h}

# ---------------- (c) weighted-a2 re-ranking ----------------
print("=== (c) cell-weighted a2 matching: does the ranking reorder? ===")
wc = cell_weights(nr, nz, h)
wfull = np.zeros(M0.shape[:2])
wfull[: nr - 1, 1:-1] = wc
WT = np.broadcast_to(wfull[..., None, None], M0.shape)


def a2w_of(X):
    return float(np.sum(WT[FREE] * (X["A"][0][FREE] ** 2
                                    + X["B"][0][FREE] ** 2)))


ref = np.load(os.path.join(DATA, "m5_12_d3b_breather_n32_c2seed_state.npz"))
Xref = x_pack(ref["M0"].astype(np.float64),
              [ref["A1"].astype(np.float64), ref["A2"].astype(np.float64)],
              [ref["B1"].astype(np.float64), ref["B2"].astype(np.float64)])
for k in range(2):
    Xref["A"][k][PIN] = 0.0
    Xref["B"][k][PIN] = 0.0
a2w_star = a2w_of(Xref)
print(f"  weighted a2* = {a2w_star:.6f}")
pub = json.load(open(os.path.join(DATA, "m5_12_b15_shapes.json")))
rows_w = []
for r in pub["rows"]:
    d = np.load(os.path.join(DATA, r["state"]))
    X = x_pack(d["M0"].astype(np.float64),
               [d[f"A{k+1}"].astype(np.float64) for k in range(2)],
               [d[f"B{k+1}"].astype(np.float64) for k in range(2)])
    for k in range(2):
        X["A"][k][PIN] = 0.0
        X["B"][k][PIN] = 0.0
    fac = np.sqrt(a2w_star / a2w_of(X))
    X["A"][0] *= fac
    X["B"][0] *= fac
    s0, q2, wb = probe_exact(X)
    rows_w.append({"profile": r["profile"], "kappa": r["kappa"],
                   "rescale_fac": float(fac), "omega_bal_w": wb,
                   "omega_bal_plain": r["omega_bal"]})
okw = sorted([r for r in rows_w if r["omega_bal_w"]],
             key=lambda r: r["omega_bal_w"])
for r in okw[:6]:
    print(f"  {r['profile']:>8} k={r['kappa']:<4g} "
          f"w(weighted)={r['omega_bal_w']:.4f} "
          f"(plain {r['omega_bal_plain']:.4f}, fac {r['rescale_fac']:.3f})")
OUT["sections"]["weighted_a2"] = {
    "a2w_star": a2w_star, "rows": rows_w,
    "top6_weighted": [(r["profile"], r["kappa"],
                       round(r["omega_bal_w"], 4)) for r in okw[:6]],
    "top6_plain": [(d["profile"], d["kappa"], round(d["omega_bal"], 4))
                   for d in pub["floor_ranked"]]}

# ---------------- (d) the harmonic-relabel hole ----------------
print("=== (d) second-harmonic relabel of the floor shape ===")
A2f = v_rg * np.sqrt(A2_STAR)
X2h = x_of(np.zeros_like(M0), Nt=2, A2=A2f)
s0_2, q2_2, wb_2 = probe_exact(X2h)
a2_seen = a2_of(np.zeros_like(M0))
print(f"  same shape in A2: omega_bal={wb_2:.4f} "
      f"(first-harmonic floor was 8.2348, ratio "
      f"{8.2348/(wb_2 or 1):.3f}); a2_free sees {a2_seen:.1f}")
OUT["sections"]["harmonic_relabel"] = {
    "omega_bal_A2": wb_2, "S0": s0_2, "Q2": q2_2,
    "a2_free_visible": a2_seen}

OUT["wall_s"] = round(time.time() - t0, 1)
path = os.path.join(DATA, "m5_12_audit_b15_rayleigh.json")


def _clean(o):
    if isinstance(o, dict):
        return {k: _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.floating, np.integer)):
        return float(o)
    return o


with open(path, "w") as f:
    json.dump(_clean(OUT), f, indent=1)
print(f"[done] wall={OUT['wall_s']}s json -> {os.path.basename(path)}")
