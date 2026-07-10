"""M5.12 block-15 ADVERSARIAL AUDIT, part 3 (P2): stall character of the
f1 (rgauss) and f2 (shell) relaxed endpoints.

Per endpoint, with an audit-owned flattening and phase row:
  (1) recompute |F| (claimed 187.4 / 188.8) including the phase-row share
  (2) first-order optimality: g = J^T F via the rank-one structure;
      steepest-descent line search with retraction
  (3) one independent damped Gauss-Newton step (own LSMR, damp = 1e-2 of
      the ||A|| estimate, 40 iters): does the floor still descend?

Run:  python3 -u m5_12_audit_b15_stall.py
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

from m5_17_energy import cell_weights                                    # noqa: E402
from m5_16_axisym import pin_mask                                        # noqa: E402
from m5_12_d3a_bvp import residual, shat, x_pack                         # noqa: E402
from m5_12_d3b_newton import wscale_at                                   # noqa: E402

h, Nt = 1.0, 2
nr, nz = 32, 64
WSC = wscale_at(nr, nz, h, 8.0 * 32 / 96)


class Flat:
    def __init__(self, X0, pin):
        self.free = np.broadcast_to((~pin)[..., None, None]
                                    & np.ones((1, 1, 4, 4), bool),
                                    X0["M0"].shape)
        self.n = int(np.sum(self.free))

    def to_vec(self, X):
        p = [X["M0"][self.free]]
        for k in range(Nt):
            p += [X["A"][k][self.free], X["B"][k][self.free]]
        return np.concatenate(p)

    def from_vec(self, v, X0):
        X = {"M0": X0["M0"].copy(), "A": [a.copy() for a in X0["A"]],
             "B": [b.copy() for b in X0["B"]]}
        o = 0
        X["M0"][self.free] = v[o:o + self.n]; o += self.n
        for k in range(Nt):
            X["A"][k][self.free] = v[o:o + self.n]; o += self.n
            X["B"][k][self.free] = v[o:o + self.n]; o += self.n
        return X

    def r_to_vec(self, Rd):
        p = [Rd["M0"][self.free]]
        for k in range(Nt):
            p += [Rd["A"][k][self.free], Rd["B"][k][self.free]]
        return np.concatenate(p)


def load_x(path):
    d = np.load(path)
    X = x_pack(d["M0"].astype(np.float64),
               [d[f"A{k+1}"].astype(np.float64) for k in range(Nt)],
               [d[f"B{k+1}"].astype(np.float64) for k in range(Nt)])
    pin = pin_mask(nr, nz)
    for k in range(Nt):
        X["A"][k][pin] = 0.0
        X["B"][k][pin] = 0.0
    return X, pin


def audit_endpoint(tag, state, F_pub, lsmr_iters=40):
    X0, pin = load_x(os.path.join(DATA, state))
    V = Flat(X0, pin)
    n = V.n
    a2_star = float(np.sum(X0["A"][0][V.free] ** 2)
                    + np.sum(X0["B"][0][V.free] ** 2))
    U = X0["A"][0][V.free].copy()
    U /= (np.linalg.norm(U) + 1e-300)

    def retract(v):
        a2 = float(np.sum(v[n:3 * n] ** 2))
        vv = v.copy()
        vv[n:3 * n] *= np.sqrt(a2_star / a2)
        return vv

    def F_of(v):
        Xv = V.from_vec(v, X0)
        s0 = shat(Xv, 0.0, h, WSC)
        q2 = s0 - shat(Xv, 1.0, h, WSC)
        if q2 >= 0 or s0 <= 0:
            return None, None
        w = float(np.sqrt(s0 / -q2))
        Rd, _ = residual(Xv, w, h, WSC)
        c_ph = float(np.sum(Xv["B"][0][V.free] * U))
        return np.concatenate([V.r_to_vec(Rd), [c_ph]]), \
            {"w": w, "S0": s0, "Q2": q2}

    z = retract(V.to_vec(X0))
    F, meta = F_of(z)
    fn = float(np.linalg.norm(F))
    ph_share = abs(F[-1]) / fn
    print(f"[{tag}] |F| = {fn:.2f} (pub {F_pub})  ph_share {ph_share:.2e} "
          f"w_bal {meta['w']:.4f}")

    # ---- (2) J^T F + steepest descent ----
    eps_g = 1e-6 * max(1.0, float(np.linalg.norm(z))) / np.sqrt(z.size)
    Xv = V.from_vec(z, X0)
    w, s0, q2 = meta["w"], meta["S0"], meta["Q2"]
    R0d, _ = residual(Xv, 0.0, h, WSC)
    R1d, _ = residual(Xv, 1.0, h, WSC)
    R0v = V.r_to_vec(R0d)
    RQv = R0v - V.r_to_vec(R1d)
    P = -q2
    gvec = (R0v / P + (s0 / P ** 2) * RQv) / (2.0 * w)
    dRdw = -2.0 * w * RQv

    def rmv(ww):
        w_R, w_ph = ww[:-1], ww[-1]
        Xp = V.from_vec(z + eps_g * w_R, X0)
        Xm = V.from_vec(z - eps_g * w_R, X0)
        Rp, _ = residual(Xp, w, h, WSC)
        Rm, _ = residual(Xm, w, h, WSC)
        Hw = (V.r_to_vec(Rp) - V.r_to_vec(Rm)) / (2 * eps_g)
        gph = np.zeros_like(z)
        gph[2 * n:3 * n] = U
        return Hw + gvec * float(np.dot(dRdw, w_R)) + w_ph * gph

    g = rmv(F)
    gn = float(np.linalg.norm(g))
    d = -g / gn
    best_sd = {"t": 0.0, "F": fn}
    for t in (1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5):
        Ft, mt = F_of(retract(z + t * d))
        if Ft is None:
            continue
        fnt = float(np.linalg.norm(Ft))
        if fnt < best_sd["F"]:
            best_sd = {"t": t, "F": fnt}
    print(f"[{tag}] |JtF| = {gn:.3e} (|JtF|/|F| {gn/fn:.2e}); "
          f"steepest-descent best drop "
          f"{(1 - best_sd['F']/fn)*100:.3f}% at t={best_sd['t']:g}")

    # ---- (3) one independent damped GN step ----
    def jv(vv):
        Fp, _ = F_of(z + eps_g * vv)
        Fm, _ = F_of(z - eps_g * vv)
        if Fp is None or Fm is None:
            return np.full(F.size, np.nan)
        return (Fp - Fm) / (2 * eps_g)

    w_cells = cell_weights(nr, nz, h)
    wfull = np.ones((nr, nz))
    wfull[: nr - 1, 1:-1] = w_cells
    d_block = np.sqrt(np.broadcast_to(wfull[..., None, None],
                                      X0["M0"].shape)[V.free])
    Dscale = np.concatenate([d_block] * (1 + 2 * Nt))
    A = LinearOperator((F.size, z.size),
                       matvec=lambda vv: jv(vv / Dscale),
                       rmatvec=lambda ww: rmv(ww) / Dscale, dtype=float)
    sol0 = lsmr(A, -F, damp=0.0, maxiter=10, atol=1e-8, btol=1e-8)
    norma = float(sol0[5])
    sol = lsmr(A, -F, damp=1e-2 * norma, maxiter=lsmr_iters,
               atol=1e-8, btol=1e-8)
    s = sol[0] / Dscale
    best_gn = {"lam": 0.0, "F": fn, "w": meta["w"]}
    lam = 1.0
    for _ in range(7):
        Ft, mt = F_of(retract(z + lam * s))
        if Ft is not None:
            fnt = float(np.linalg.norm(Ft))
            if fnt < best_gn["F"]:
                best_gn = {"lam": lam, "F": fnt, "w": mt["w"]}
                break
        lam *= 0.5
    print(f"[{tag}] damped GN (damp 1e-2||A||, {lsmr_iters} it): "
          f"|F| {fn:.2f} -> {best_gn['F']:.2f} "
          f"({(1 - best_gn['F']/fn)*100:.2f}%) at lam={best_gn['lam']:g}, "
          f"w_bal -> {best_gn['w']:.4f}")
    return {"tag": tag, "state": state, "F_pub": F_pub,
            "F_recomputed": fn, "phase_row_share": ph_share,
            "omega_bal": meta["w"], "a2_star": a2_star,
            "JtF_norm": gn, "JtF_over_F": gn / fn,
            "sd_best_drop_rel": 1.0 - best_sd["F"] / fn,
            "sd_best_t": best_sd["t"],
            "gn_drop_rel": 1.0 - best_gn["F"] / fn,
            "gn_best_lam": best_gn["lam"], "gn_F_after": best_gn["F"],
            "gn_w_after": best_gn["w"], "lsmr_norma": norma}


OUT = {"script": "m5_12_audit_b15_stall.py", "rows": []}
t0 = time.time()
for tag, st, fp in (("f2_shell", "m5_12_b12_hard_f2_1_state.npz", 188.83),
                    ("f1_rgauss", "m5_12_b12_hard_f1_1_state.npz", 187.41)):
    OUT["rows"].append(audit_endpoint(tag, st, fp))
OUT["wall_s"] = round(time.time() - t0, 1)
path = os.path.join(DATA, "m5_12_audit_b15_stall.json")
with open(path, "w") as f:
    json.dump(OUT, f, indent=1)
print(f"[done] wall={OUT['wall_s']}s json -> {os.path.basename(path)}")
