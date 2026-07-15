"""M5.12 block-14 ADVERSARIAL AUDIT: endpoint addendum.

The three chains closed as honest stalls. This addendum:
  1. independently re-derives every endpoint number (|F|, omega_bal, Q2 +
     mix/pos split, H_swing/S0 via an audit-owned H(t))
  2. re-runs the N4 topology readout on the FINAL lp endpoint (iter 6)
  3. stationarity spot-check on wd_1: |J^T F| + one independent damped
     GN step (own LSMR)
Appends "endpoint_addendum" to ../data/m5_12_audit_b14.json.

Run:  python3 -u m5_12_audit_b14_endpoints.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.sparse.linalg import LinearOperator, lsmr

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import cell_weights, grid_coords, hedgehog_field       # noqa: E402
from m5_16_axisym import pin_mask                                        # noqa: E402
from m5_12_dressed import to_covariant                                   # noqa: E402
from m5_12_loop import ring_readout                                      # noqa: E402
from m5_12_d3a_bvp import (residual, shat, x_pack, sample_fields,        # noqa: E402
                           sample_density)
from m5_12_d3b_newton import wscale_at                                   # noqa: E402
from m5_12_audit_b14_loop import nematic_winding                         # noqa: E402

h = 1.0
Nt = 2


def load_x(path, nr, nz):
    d = np.load(path)
    X = x_pack(d["M0"].astype(np.float64),
               [d[f"A{k+1}"].astype(np.float64) for k in range(Nt)],
               [d[f"B{k+1}"].astype(np.float64) for k in range(Nt)])
    pin = pin_mask(nr, nz)
    for k in range(Nt):
        X["A"][k][pin] = 0.0
        X["B"][k][pin] = 0.0
    return X, pin


def flat_F(X, pin, wsc):
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), X["M0"].shape)
    s0 = shat(X, 0.0, h, wsc)
    q2 = s0 - shat(X, 1.0, h, wsc)
    w = float(np.sqrt(s0 / -q2))
    Rd, _ = residual(X, w, h, wsc)
    parts = [Rd["M0"][free]]
    for k in range(Nt):
        parts += [Rd["A"][k][free], Rd["B"][k][free]]
    Fv = np.concatenate(parts)
    U = X["A"][0][free]
    U = U / (np.linalg.norm(U) + 1e-300)
    c_ph = float(np.sum(X["B"][0][free] * U))
    return Fv, c_ph, w, s0, q2, free


def q2_split(X, wsc):
    out = {}
    for key, keep_mix in (("mix", True), ("pos", False)):
        Xc = {"M0": X["M0"].copy(), "A": [a.copy() for a in X["A"]],
              "B": [b.copy() for b in X["B"]]}
        for arr in Xc["A"] + Xc["B"]:
            if keep_mix:
                arr[..., 1:4, 1:4] = 0.0
            else:
                arr[..., 0, :] = 0.0
                arr[..., :, 0] = 0.0
        s0c = shat(Xc, 0.0, h, wsc)
        out[key] = s0c - shat(Xc, 1.0, h, wsc)
    return out["mix"], out["pos"]


def h_swing(X, w, wsc):
    """audit-owned H(t): per sample H_j = SUM wcell (2 d0_j - d_j)
    (d = spatial + V - TP, d0 = spatial + V, so H = spatial + V + TP)."""
    nr, nz = X["M0"].shape[:2]
    ns = 4 * Nt + 2
    wc = cell_weights(nr, nz, h)
    Ms, Mds = sample_fields(X, w, ns)
    Hs = []
    for Mt, Mdt in zip(Ms, Mds):
        d = sample_density(Mt, Mdt, h, wsc)
        d0 = sample_density(Mt, np.zeros_like(Mdt), h, wsc)
        Hs.append(float(np.sum((2.0 * d0 - d) * wc)))
    Hs = np.array(Hs)
    return float(Hs.max() - Hs.min()), float(Hs.mean())


OUT = {"date": "2026-07-09", "endpoints": {}, "loop_topology": {},
       "stationarity_wd1": {}}
t0 = time.time()

CFG = [("g48_1", "m5_12_b12_hard_g48_1_state.npz", 48,
        {"F": 100.90, "w": 5.7204, "Q2": -0.93268, "mix": -0.9159,
         "pos": 0.0037, "HswS0": 1.9961}),
       ("lp_1", "m5_12_b12_hard_lp_1_state.npz", 32,
        {"F": 522.20, "w": 10.1923, "Q2": -0.93473, "mix": -0.9327,
         "pos": 0.0001, "HswS0": 2.0358}),
       ("wd_1", "m5_12_b12_hard_wd_1_state.npz", 32,
        {"F": 193.89, "w": 7.4546, "Q2": -0.79658, "mix": -0.7941,
         "pos": 0.0021, "HswS0": 1.9906})]

print("=== 1: endpoint re-derivation ===")
keep = {}
for tag, fn, nr, pub in CFG:
    nz = 2 * nr
    wsc = wscale_at(nr, nz, h, 8.0 * nr / 96)
    X, pin = load_x(os.path.join(DATA, fn), nr, nz)
    Fv, c_ph, w, s0, q2, free = flat_F(X, pin, wsc)
    fnorm = float(np.sqrt(np.sum(Fv ** 2) + c_ph ** 2))
    mix, pos = q2_split(X, wsc)
    sw, hm = h_swing(X, w, wsc)
    rec = {"F_recomputed": fnorm, "F_pub": pub["F"],
           "omega_bal": w, "omega_pub": pub["w"],
           "S0": s0, "Q2": q2, "Q2_mix": mix, "Q2_pos": pos,
           "Q2_cross": q2 - mix - pos,
           "H_swing_over_S0": sw / s0, "H_mean_over_S0": hm / s0,
           "pub": pub}
    OUT["endpoints"][tag] = rec
    keep[tag] = (X, pin, wsc, w, s0, q2)
    print(f"  {tag}: |F|={fnorm:.2f} (pub {pub['F']}) w={w:.4f} "
          f"(pub {pub['w']}) Q2={q2:+.5f} (mix {mix:+.4f} pos {pos:+.4f})"
          f" Hsw/S0={sw/s0:.4f} (pub {pub['HswS0']}) Hmean/S0={hm/s0:.2e}")

print("=== 2: loop topology at the FINAL lp endpoint (iter 6) ===")
X, pin, wsc, w, s0, q2 = keep["lp_1"]
nr, nz = 32, 64
scale = 32 / 96.0
R0, rc = 16.0 * scale, 8.0 * scale
M0e = X["M0"]
rr_e = ring_readout(M0e, nr, nz, h)
q_seed_ring = nematic_winding(M0e, R0, 0.0, rc, nr, nz, h)
q_own_ring = nematic_winding(M0e, rr_e["ring_rho"], rr_e["ring_z"], rc,
                             nr, nz, h)
seed = np.load(os.path.join(DATA, "m5_12_b14_seed_loop_bmix_n32.npz"))
M0s = seed["M0"].astype(np.float64)
R, Z = grid_coords(nr, nz, h)
Mhed = to_covariant(hedgehog_field(R, Z, rc))
d_loop = float(np.sqrt(np.sum((M0e - M0s) ** 2)))
d_hed = float(np.sqrt(np.sum((M0e - Mhed) ** 2)))
OUT["loop_topology"] = {**rr_e, "q_at_seed_ring": q_seed_ring,
                        "q_at_own_ring": q_own_ring,
                        "dist_to_loop_seed": d_loop,
                        "dist_to_hedgehog": d_hed}
print(f"  ring=({rr_e['ring_rho']:.2f},{rr_e['ring_z']:.2f}) "
      f"min_s={rr_e['min_s']:.4f} q(seed ring)={q_seed_ring} "
      f"q(own ring)={q_own_ring} |dM0|seed={d_loop:.4f} "
      f"|dM0|hedgehog={d_hed:.3f}")

print("=== 3: stationarity spot-check on wd_1 (|J^T F| + one GN step) ===")
X, pin, wsc, w, s0, q2 = keep["wd_1"]
nr, nz = 32, 64
free = np.broadcast_to((~pin)[..., None, None]
                       & np.ones((1, 1, 4, 4), bool), X["M0"].shape)
nfree = int(np.sum(free))


def to_vec(Xv):
    p = [Xv["M0"][free]]
    for k in range(Nt):
        p += [Xv["A"][k][free], Xv["B"][k][free]]
    return np.concatenate(p)


def from_vec(v):
    Xv = {"M0": X["M0"].copy(), "A": [a.copy() for a in X["A"]],
          "B": [b.copy() for b in X["B"]]}
    o = 0
    Xv["M0"][free] = v[o:o + nfree]; o += nfree
    for k in range(Nt):
        Xv["A"][k][free] = v[o:o + nfree]; o += nfree
        Xv["B"][k][free] = v[o:o + nfree]; o += nfree
    return Xv


def r_to_vec(Rd):
    p = [Rd["M0"][free]]
    for k in range(Nt):
        p += [Rd["A"][k][free], Rd["B"][k][free]]
    return np.concatenate(p)


U = X["A"][0][free].copy()
U /= (np.linalg.norm(U) + 1e-300)
a2_star = float(np.sum(X["A"][0][free] ** 2) + np.sum(X["B"][0][free] ** 2))


def retract(v):
    a2 = float(np.sum(v[nfree:3 * nfree] ** 2))
    vv = v.copy()
    vv[nfree:3 * nfree] *= np.sqrt(a2_star / a2)
    return vv


def F_of(v):
    Xv = from_vec(v)
    s0v = shat(Xv, 0.0, h, wsc)
    q2v = s0v - shat(Xv, 1.0, h, wsc)
    if q2v >= 0 or s0v <= 0:
        return None, None
    wv = float(np.sqrt(s0v / -q2v))
    Rd, _ = residual(Xv, wv, h, wsc)
    c_ph = float(np.sum(Xv["B"][0][free] * U))
    return np.concatenate([r_to_vec(Rd), [c_ph]]), wv


z = to_vec(X)
F, _ = F_of(z)
fn = float(np.linalg.norm(F))
# rank-one caches at the endpoint
R0d, _ = residual(X, 0.0, h, wsc)
R1d, _ = residual(X, 1.0, h, wsc)
R0v = r_to_vec(R0d)
RQv = R0v - r_to_vec(R1d)
P = -q2
gvec = (R0v / P + (s0 / P ** 2) * RQv) / (2.0 * w)
dRdw = -2.0 * w * RQv
eps_g = 1e-6 * max(1.0, float(np.linalg.norm(z))) / np.sqrt(z.size)
# J^T F
Ff = F[:-1]
Xp = from_vec(z + eps_g * Ff)
Xm = from_vec(z - eps_g * Ff)
Rp, _ = residual(Xp, w, h, wsc)
Rm, _ = residual(Xm, w, h, wsc)
Hw = (r_to_vec(Rp) - r_to_vec(Rm)) / (2 * eps_g)
gph = np.zeros_like(z)
gph[2 * nfree:3 * nfree] = U
g = Hw + gvec * float(np.dot(dRdw, Ff)) + F[-1] * gph
gn = float(np.linalg.norm(g))
print(f"  wd_1: |F|={fn:.2f} |JtF|={gn:.3e} |JtF|/|F|={gn/fn:.3e}")


def jv(vv):
    Fp, _ = F_of(z + eps_g * vv)
    Fm, _ = F_of(z - eps_g * vv)
    if Fp is None or Fm is None:
        return np.full(F.size, np.nan)
    return (Fp - Fm) / (2 * eps_g)


def rmv(ww):
    w_R, w_ph = ww[:-1], ww[-1]
    Xp2 = from_vec(z + eps_g * w_R)
    Xm2 = from_vec(z - eps_g * w_R)
    Rp2, _ = residual(Xp2, w, h, wsc)
    Rm2, _ = residual(Xm2, w, h, wsc)
    Hw2 = (r_to_vec(Rp2) - r_to_vec(Rm2)) / (2 * eps_g)
    return Hw2 + gvec * float(np.dot(dRdw, w_R)) + w_ph * gph


w_cells = cell_weights(nr, nz, h)
wfull = np.ones((nr, nz))
wfull[: nr - 1, 1:-1] = w_cells
d_block = np.sqrt(np.broadcast_to(wfull[..., None, None],
                                  X["M0"].shape)[free])
Dscale = np.concatenate([d_block] * (1 + 2 * Nt))
A = LinearOperator((F.size, z.size),
                   matvec=lambda vv: jv(vv / Dscale),
                   rmatvec=lambda ww: rmv(ww) / Dscale, dtype=float)
sol = lsmr(A, -F, damp=0.0, maxiter=40, atol=1e-8, btol=1e-8)
s = sol[0] / Dscale
best = {"lam": 0.0, "F": fn}
lam = 1.0
for _ in range(7):
    zt = retract(z + lam * s)
    Ft, wt = F_of(zt)
    if Ft is not None:
        fnt = float(np.linalg.norm(Ft))
        if fnt < best["F"]:
            best = {"lam": lam, "F": fnt, "w": wt}
            break
    lam *= 0.5
OUT["stationarity_wd1"] = {"F": fn, "JtF": gn, "JtF_over_F": gn / fn,
                           "gn_step_best_lam": best["lam"],
                           "gn_step_F": best["F"],
                           "gn_step_drop_rel": 1.0 - best["F"] / fn,
                           "gn_step_omega": best.get("w"),
                           "lsmr_stop": int(sol[1])}
print(f"  GN step: lam={best['lam']:g} |F| {fn:.2f} -> {best['F']:.2f} "
      f"({(1.0 - best['F']/fn)*100:.2f}%) w={best.get('w')}")

# append to the verdict file
vpath = os.path.join(DATA, "m5_12_audit_b14.json")
V = json.load(open(vpath))
OUT["wall_s"] = round(time.time() - t0, 1)
V["endpoint_addendum"] = OUT
with open(vpath, "w") as f:
    json.dump(V, f, indent=1)
print(f"[done] wall={OUT['wall_s']}s appended endpoint_addendum -> "
      f"m5_12_audit_b14.json")
