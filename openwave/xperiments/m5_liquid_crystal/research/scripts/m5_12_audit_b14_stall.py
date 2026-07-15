"""M5.12 block-14 ADVERSARIAL AUDIT, part 3: the stall floors (claim N1).

  (1) recompute |F| at the c1/c2/s deep-stall endpoints (independent
      flattening), including the phase-row share
  (2) first-order optimality: g = J^T F via the rank-one structure;
      steepest-descent line search (with retraction) in three phase-row
      variants (state U, random U, no phase row): does ANY simple descent
      break the floor?
  (3) one independent damped Gauss-Newton step (own LSMR) at the c2 stall:
      is the floor solver-limited against a modest re-solve?
  (4) grid-transfer residual scale: c2 (n32) prolonged to n48, and the
      live g48 checkpoint restricted to n32: what |F| do good states from
      ANOTHER grid show? (context for the 1e-5 rel bar)

Run:  python3 -u m5_12_audit_b14_stall.py
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
from m5_12_d3b_newton import wscale_at, load_warmstart                   # noqa: E402

h = 1.0
Nt = 2


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


def make_ctx(X, pin, wsc, a2_star, U_mode="state"):
    V = Flat(X, pin)
    n = V.n
    if U_mode == "state":
        U = X["A"][0][V.free].copy()
    elif U_mode == "random":
        U = np.random.default_rng(3).standard_normal(n)
    else:
        U = None
    if U is not None:
        U = U / (np.linalg.norm(U) + 1e-300)

    def retract(v):
        a2 = float(np.sum(v[n:3 * n] ** 2))
        vv = v.copy()
        vv[n:3 * n] *= np.sqrt(a2_star / a2)
        return vv

    def F_of(v, X0):
        Xv = V.from_vec(v, X0)
        s0 = shat(Xv, 0.0, h, wsc)
        q2 = s0 - shat(Xv, 1.0, h, wsc)
        if q2 >= 0 or s0 <= 0:
            return None, None
        w = float(np.sqrt(s0 / -q2))
        Rd, _ = residual(Xv, w, h, wsc)
        Fv = V.r_to_vec(Rd)
        if U is not None:
            c_ph = float(np.sum(Xv["B"][0][V.free] * U))
            Fv = np.concatenate([Fv, [c_ph]])
        return Fv, {"w": w, "S0": s0, "Q2": q2}

    return V, U, retract, F_of


def jtf(V, U, F, z, X0, wsc, meta):
    """J^T F via the b12_hard rank-one structure (audit reimplementation)."""
    Xv = V.from_vec(z, X0)
    w, s0, q2 = meta["w"], meta["S0"], meta["Q2"]
    R0d, _ = residual(Xv, 0.0, h, wsc)
    R1d, _ = residual(Xv, 1.0, h, wsc)
    R0v = V.r_to_vec(R0d)
    RQv = R0v - V.r_to_vec(R1d)
    P = -q2
    gvec = (R0v / P + (s0 / P ** 2) * RQv) / (2.0 * w)
    dRdw = -2.0 * w * RQv
    nfree = V.n
    F_fields = F[:len(R0v)] if U is not None else F
    eps_g = 1e-6 * max(1.0, float(np.linalg.norm(z))) / np.sqrt(z.size)
    Xp = V.from_vec(z + eps_g * F_fields_pad(F_fields, z), X0)
    Xm = V.from_vec(z - eps_g * F_fields_pad(F_fields, z), X0)
    Rp, _ = residual(Xp, w, h, wsc)
    Rm, _ = residual(Xm, w, h, wsc)
    Hw = (V.r_to_vec(Rp) - V.r_to_vec(Rm)) / (2 * eps_g)
    g = Hw + gvec * float(np.dot(dRdw, F_fields))
    if U is not None:
        gph = np.zeros_like(z)
        gph[2 * nfree:3 * nfree] = U
        g = g + F[-1] * gph
    return g


def F_fields_pad(Ff, z):
    v = np.zeros_like(z)
    v[:len(Ff)] = Ff
    return v


def descent_test(name, state_path, a2_star, F_pub, U_mode, out_rows,
                 ls_ts=(1e-2, 3e-3, 1e-3, 3e-4, 1e-4, 3e-5, 1e-5)):
    nr, nz = 32, 64
    wsc = wscale_at(nr, nz, h, 8.0 * 32 / 96)
    X, pin = load_x(os.path.join(DATA, state_path), nr, nz)
    V, U, retract, F_of = make_ctx(X, pin, wsc, a2_star, U_mode)
    z = retract(V.to_vec(X))
    F, meta = F_of(z, X)
    fn = float(np.linalg.norm(F))
    ph_share = abs(F[-1]) / fn if U is not None else 0.0
    g = jtf(V, U, F, z, X, wsc, meta)
    gn = float(np.linalg.norm(g))
    d = -g / gn
    best = {"t": 0.0, "F": fn}
    for t in ls_ts:
        zt = retract(z + t * d)
        Ft, mt = F_of(zt, X)
        if Ft is None:
            continue
        fnt = float(np.linalg.norm(Ft))
        if fnt < best["F"]:
            best = {"t": t, "F": fnt, "w": mt["w"]}
    row = {"state": state_path, "U_mode": U_mode, "F_pub": F_pub,
           "F_recomputed": fn, "phase_row_share": ph_share,
           "JtF_norm": gn, "JtF_over_F": gn / fn,
           "best_step_t": best["t"], "best_F": best["F"],
           "best_drop_rel": 1.0 - best["F"] / fn,
           "omega_bal": meta["w"]}
    out_rows.append(row)
    print(f"  {name} [{U_mode}]: |F|={fn:.2f} (pub {F_pub}) "
          f"ph_share={ph_share:.2e} |JtF|={gn:.3e} "
          f"best drop={row['best_drop_rel']*100:.2f}% at t={best['t']:g} "
          f"w_bal={meta['w']:.4f}")
    return z, F, meta, V, U, retract, F_of, X


OUT = {"script": "m5_12_audit_b14_stall.py", "sections": {}}
t0 = time.time()

# ---------- (1)+(2): floors + first-order optimality + descent ----------
print("=== (1)+(2) stall floors, J^T F, steepest descent ===")
rows = []
cfg = [("c2", "m5_12_b12_hard_c2_1_state.npz", 0.3037246498505979, 215.78),
       ("c1", "m5_12_b12_hard_c1_1_state.npz", 1.2148985873959985, 139.06),
       ("s", "m5_12_b12_hard_s_1_state.npz", 2.4297971747919974, 206.84)]
keep = {}
for name, sp, a2s, fpub in cfg:
    res = descent_test(name, sp, a2s, fpub, "state", rows)
    if name == "c2":
        keep["c2"] = res
# phase-row variants on c2 only (cost control)
for um in ("random", "none"):
    descent_test("c2", cfg[0][1], cfg[0][2], cfg[0][3], um, rows)
OUT["sections"]["floors_and_descent"] = rows

# ---------- (3) one independent damped GN step at the c2 stall ----------
print("=== (3) independent damped Gauss-Newton step (c2, own LSMR) ===")
z, F, meta, V, U, retract, F_of, X0 = keep["c2"]
nr, nz = 32, 64
wsc = wscale_at(nr, nz, h, 8.0 * 32 / 96)
n = V.n
w_cells = cell_weights(nr, nz, h)
wfull = np.ones((nr, nz))
wfull[: nr - 1, 1:-1] = w_cells
d_block = np.sqrt(np.broadcast_to(wfull[..., None, None],
                                  X0["M0"].shape)[V.free])
Dscale = np.concatenate([d_block] * (1 + 2 * Nt))
eps_g = 1e-6 * max(1.0, float(np.linalg.norm(z))) / np.sqrt(z.size)


def jv(vv):
    Fp, _ = F_of(z + eps_g * vv, X0)
    Fm, _ = F_of(z - eps_g * vv, X0)
    if Fp is None or Fm is None:
        return np.full(F.size, np.nan)
    return (Fp - Fm) / (2 * eps_g)


# linearization-point caches (z is FIXED for this one GN step)
_Xv = V.from_vec(z, X0)
_w = meta["w"]
_R0d, _ = residual(_Xv, 0.0, h, wsc)
_R1d, _ = residual(_Xv, 1.0, h, wsc)
_R0v = V.r_to_vec(_R0d)
_RQv = _R0v - V.r_to_vec(_R1d)
_P = -meta["Q2"]
_gvec = (_R0v / _P + (meta["S0"] / _P ** 2) * _RQv) / (2.0 * _w)
_dRdw = -2.0 * _w * _RQv


def rmv(ww):
    w = _w
    gvec, dRdw = _gvec, _dRdw
    w_R, w_ph = ww[:-1], ww[-1]
    Xp = V.from_vec(z + eps_g * w_R, X0)
    Xm = V.from_vec(z - eps_g * w_R, X0)
    Rp, _ = residual(Xp, w, h, wsc)
    Rm, _ = residual(Xm, w, h, wsc)
    Hw = (V.r_to_vec(Rp) - V.r_to_vec(Rm)) / (2 * eps_g)
    g = Hw + gvec * float(np.dot(dRdw, w_R))
    gph = np.zeros_like(z)
    gph[2 * n:3 * n] = U
    return g + w_ph * gph


A = LinearOperator((F.size, z.size),
                   matvec=lambda vv: jv(vv / Dscale),
                   rmatvec=lambda ww: rmv(ww) / Dscale, dtype=float)
fn = float(np.linalg.norm(F))
gn_rows = []
for damp_frac, li in ((0.0, 50), (1e-2, 40)):
    sol = lsmr(A, -F, damp=damp_frac * 0.0 if damp_frac == 0.0 else None,
               maxiter=li, atol=1e-8, btol=1e-8) \
        if damp_frac == 0.0 else None
    if sol is None:
        # need ||A|| estimate from an undamped probe first
        sol0 = lsmr(A, -F, damp=0.0, maxiter=10, atol=1e-8, btol=1e-8)
        norma = float(sol0[5])
        sol = lsmr(A, -F, damp=damp_frac * norma, maxiter=li,
                   atol=1e-8, btol=1e-8)
    s = sol[0] / Dscale
    best = {"lam": 0.0, "F": fn}
    lam = 1.0
    for _ in range(7):
        zt = retract(z + lam * s)
        Ft, mt = F_of(zt, X0)
        if Ft is not None:
            fnt = float(np.linalg.norm(Ft))
            if fnt < best["F"]:
                best = {"lam": lam, "F": fnt, "w": mt["w"]}
                break
        lam *= 0.5
    rec = {"damp_frac": damp_frac, "lsmr_iters": li,
           "lsmr_stop": int(sol[1]), "best_lam": best["lam"],
           "best_F": best["F"], "drop_rel": 1.0 - best["F"] / fn}
    gn_rows.append(rec)
    print(f"  damp={damp_frac:g}: stop={rec['lsmr_stop']} "
          f"lam={best['lam']:g} |F| {fn:.2f} -> {best['F']:.2f} "
          f"({rec['drop_rel']*100:.2f}%)")
OUT["sections"]["independent_GN_step_c2"] = gn_rows

# ---------- (4) grid-transfer residual scale ----------
print("=== (4) grid-transfer |F| scale ===")
tr = []
# c2 stall (n32, |F| 216) prolonged to n48
X48, _ = load_warmstart(os.path.join(DATA, "m5_12_b12_hard_c2_1_state.npz"),
                        48, 96, Nt)
pin48 = pin_mask(48, 96)
for k in range(Nt):
    X48["A"][k][pin48] = 0.0
    X48["B"][k][pin48] = 0.0
wsc48 = wscale_at(48, 96, h, 8.0 * 48 / 96)
V48 = Flat(X48, pin48)
s0 = shat(X48, 0.0, h, wsc48)
q2 = s0 - shat(X48, 1.0, h, wsc48)
w48 = float(np.sqrt(s0 / -q2)) if q2 < 0 else None
Rd, _ = residual(X48, w48, h, wsc48)
f48 = float(np.linalg.norm(V48.r_to_vec(Rd)))
tr.append({"transfer": "c2 n32 -> n48", "F": f48, "omega_bal": w48,
           "S0": s0, "Q2": q2})
print(f"  c2 n32->n48: |F|={f48:.1f} w_bal={w48:.4f}")
# g48 chain checkpoint (n48) restricted to n32
g48p = os.path.join(DATA, "m5_12_b12_hard_g48_1_state_ck.npz")
if os.path.exists(g48p):
    X32, _ = load_warmstart(g48p, 32, 64, Nt)
    pin32 = pin_mask(32, 64)
    for k in range(Nt):
        X32["A"][k][pin32] = 0.0
        X32["B"][k][pin32] = 0.0
    wsc32 = wscale_at(32, 64, h, 8.0 * 32 / 96)
    V32 = Flat(X32, pin32)
    s0 = shat(X32, 0.0, h, wsc32)
    q2 = s0 - shat(X32, 1.0, h, wsc32)
    w32 = float(np.sqrt(s0 / -q2)) if q2 < 0 else None
    Rd, _ = residual(X32, w32, h, wsc32)
    f32 = float(np.linalg.norm(V32.r_to_vec(Rd)))
    tr.append({"transfer": "g48 ck n48 -> n32", "F": f32,
               "omega_bal": w32, "S0": s0, "Q2": q2})
    print(f"  g48 ck n48->n32: |F|={f32:.1f} w_bal={w32:.4f}")
OUT["sections"]["grid_transfer"] = tr

OUT["wall_s"] = round(time.time() - t0, 1)
path = os.path.join(DATA, "m5_12_audit_b14_stall.json")
with open(path, "w") as f:
    json.dump(OUT, f, indent=1)
print(f"[done] wall={OUT['wall_s']}s json -> {os.path.basename(path)}")
