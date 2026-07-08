"""M5.12 phase D3b: the first time-periodic branch attempt (Gauss-Newton on
the gated BVP residual; design m5_12_d3_bvp_design.md § 3).

FORMULATION (nonlinear eigenvalue, phase + amplitude bordered):
    unknowns  z = [ X_free ; omega ],  X = (M0, A_k, B_k) with boundary
              cells PINNED to the seed's (time-dependent) values
    equations F(z) = [ R_free(X; omega) ;          (the gated D3a residual)
                       c_ph  = <B_1free, U>/|U| ;  (phase: U = A_1seed dir)
                       c_amp = (|A_1|^2+|B_1|^2)/a*^2 - 1 ]   (branch selector:
                       prevents collapse to the static solution, which
                       trivially solves R = 0; omega is the paired unknown)
    solved by damped Gauss-Newton, matrix-free LSMR on the FD Jacobian
    (least-squares handles the phase near-null direction + indefiniteness).

SEED: the D2b dressed rotor (audit-refuted as physics, legitimate as a
seed): M(t) = R12(omega t) . dress(hedgehog, b0) . R12(omega t)^T, Fourier
content exactly band-limited at Nt = 2. Scaffolding grid n48x96 first
(w by the seed-virial protocol at this grid; profile scales rc, w_b with
nr/96), n96 confirm only if converged.

OUTCOMES (all first-class, pre-registered): converged-NONTRIVIAL branch
point (|R| down >= 4 decades, harmonics stay O(a*)) = the program's first
time-periodic candidate; stall/divergence patterns = documented negatives.
Checkpoint JSON per Newton iteration (cap survival).

Run:  python m5_12_d3b_newton.py hedgehog [--nr 48] [--newton 12]
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

from m5_17_energy import G_TIME, cell_weights, curvature_density_np, \
    grid_coords, hedgehog_field                                            # noqa: E402
from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_dressed import to_covariant, dress, v4d_density                 # noqa: E402
from m5_12_d3a_bvp import residual, shat, x_pack, sym_v                    # noqa: E402


def _flag(name, default, cast=float):
    for i, a in enumerate(ARGV):
        if a == "--" + name and i + 1 < len(ARGV):
            return cast(ARGV[i + 1])
    return default


# ---------------- seed construction ----------------
def rotor_seed(nr, nz, h, b0, w_b, rc_seed, omega, Nt=2, plane=(1, 2)):
    """plane=(1,2): the R12 clock: ⚠️ PURE GAUGE on axisymmetric fields
    (a global z-rotation == a phi-shift of the equivariant field: the
    'rotating static hedgehog' is a zero-cost symmetry orbit: the try-1/2
    diagnosis). plane=(2,3): the axis-swing clock, NOT absorbed by the
    spatial symmetry: the genuine first attempt."""
    R, Z = grid_coords(nr, nz, h)
    M4 = to_covariant(hedgehog_field(R, Z, rc_seed))
    r_def = np.sqrt(R ** 2 + Z ** 2)
    bmap = b0 * np.exp(-(r_def ** 2) / (w_b ** 2))
    Md = dress(M4, bmap)
    ns = 4 * Nt + 2
    i, j = plane

    def rot(th):
        L = np.eye(4)
        L[i, i], L[i, j], L[j, i], L[j, j] = (np.cos(th), -np.sin(th),
                                              np.sin(th), np.cos(th))
        return np.einsum("ab,...bc,dc->...ad", L, Md, L)

    samples = [rot(2.0 * np.pi * j / ns) for j in range(ns)]
    M0 = sum(samples) / ns
    As, Bs = [], []
    for k in range(1, Nt + 1):
        As.append(sum(s * np.cos(k * 2.0 * np.pi * j / ns)
                      for j, s in enumerate(samples)) * 2.0 / ns)
        Bs.append(sum(s * np.sin(k * 2.0 * np.pi * j / ns)
                      for j, s in enumerate(samples)) * 2.0 / ns)
    return x_pack(M0, As, Bs), Md


def wscale_at(nr, nz, h, rc_seed):
    """seed-virial protocol at this grid (V_4D)."""
    from m5_17_energy import ext_tail
    R, Z = grid_coords(nr, nz, h)
    M = to_covariant(hedgehog_field(R, Z, rc_seed))
    w = cell_weights(nr, nz, h)
    Ec = float(np.sum(curvature_density_np(M, h, 1.0) * w)) + ext_tail(
        (nr - 1) * h, (nz / 2 - 1) * h)
    Ep1 = float(np.sum(v4d_density(M, 1.0) * w))
    return Ec / (3.0 * Ep1)


# ---------------- flattening ----------------
class Vec:
    def __init__(self, X, free4):
        self.Nt = len(X["A"])
        self.shape = X["M0"].shape
        self.free = free4.astype(bool)
        self.nfree = int(np.sum(self.free))
        self.blocks = 1 + 2 * self.Nt

    def to_vec(self, X, omega):
        parts = [X["M0"][self.free]]
        for k in range(self.Nt):
            parts.append(X["A"][k][self.free])
            parts.append(X["B"][k][self.free])
        parts.append(np.array([omega]))
        return np.concatenate(parts)

    def from_vec(self, v, X_base):
        X = {"M0": X_base["M0"].copy(),
             "A": [a.copy() for a in X_base["A"]],
             "B": [b.copy() for b in X_base["B"]]}
        o = 0
        X["M0"][self.free] = v[o:o + self.nfree]; o += self.nfree
        for k in range(self.Nt):
            X["A"][k][self.free] = v[o:o + self.nfree]; o += self.nfree
            X["B"][k][self.free] = v[o:o + self.nfree]; o += self.nfree
        omega = float(v[o])
        return X, omega

    def r_to_vec(self, Rd, extra):
        parts = [Rd["M0"][self.free]]
        for k in range(self.Nt):
            parts.append(Rd["A"][k][self.free])
            parts.append(Rd["B"][k][self.free])
        parts.append(np.asarray(extra))
        return np.concatenate(parts)


def load_warmstart(path, nr, nz, Nt):
    """load a saved endpoint state and zoom it to the (nr, nz) grid (the
    seed convention scales the object with nr, so the physical object maps
    grid-to-grid by pure zoom; order-1, cell-centered)."""
    from scipy.ndimage import zoom as ndzoom
    d = np.load(path)
    src = d["M0"]
    fac = (nr / src.shape[0], nz / src.shape[1], 1, 1)

    def z(a):
        return ndzoom(a.astype(np.float64), fac, order=1)

    M0 = z(d["M0"])
    As = [z(d[f"A{k+1}"]) for k in range(Nt) if f"A{k+1}" in d]
    Bs = [z(d[f"B{k+1}"]) for k in range(Nt) if f"B{k+1}" in d]
    while len(As) < Nt:
        As.append(np.zeros_like(M0))
        Bs.append(np.zeros_like(M0))
    return x_pack(M0, As, Bs), float(d["omega"][0])


def run_newton(nr=48, nz=None, h=1.0, Nt=2, b0=1.6, omega0=0.34,
               max_newton=12, lsmr_iters=60, tag="hedgehog", plane=(1, 2),
               warmstart=None, w_amp=0.3, w_om=0.0, breather_eps=None,
               ascale=1.0, tag_suffix="", bmix=False):
    nz = nz or 2 * nr
    tag = f"{tag}_n{nr}"                  # grid-tagged (the block-7 collision fix)
    if tag_suffix:
        tag = f"{tag}_{tag_suffix}"       # ladder-rung-tagged (block 11)
    scale = nr / 96.0
    rc_seed, w_b = 8.0 * scale, 8.0 * scale
    wscale = wscale_at(nr, nz, h, rc_seed)
    if warmstart:
        X0, om_ws = load_warmstart(warmstart, nr, nz, Nt)
        omega0 = om_ws
        Md = None
        print(f"[warmstart] {warmstart} -> n{nr}, omega0={omega0:.4f}")
    elif breather_eps is not None:
        # 10b seed: covariant hedgehog + a pure-amplitude first harmonic
        # (A1 = eps * gaussian(core) * M0_spatial): breathing, no rotation
        R, Z = grid_coords(nr, nz, h)
        M4 = to_covariant(hedgehog_field(R, Z, rc_seed))
        r2 = R ** 2 + Z ** 2
        bump = np.exp(-r2 / (w_b ** 2))[..., None, None]
        A1 = np.zeros_like(M4)
        if bmix:
            # block-11 audit redirect (C4/T6): a mixing-free harmonic has
            # Q2_mix = 0 EXACTLY and Q2 >= 0 at ANY amplitude: no free-period
            # orbit exists in that class. The eta-negative channel is the
            # TIME-MIXING (0i) sector: seed the oscillation there (a
            # boost-amplitude breathing along the local radial direction).
            rr = np.sqrt(r2) + 1e-12
            b2 = bump[..., 0, 0]
            A1[..., 0, 1] = A1[..., 1, 0] = breather_eps * b2 * R / rr
            A1[..., 0, 3] = A1[..., 3, 0] = breather_eps * b2 * Z / rr
        else:
            A1[..., 1:4, 1:4] = breather_eps * bump * M4[..., 1:4, 1:4]
        X0 = x_pack(M4, [A1] + [np.zeros_like(M4)] * (Nt - 1),
                    [np.zeros_like(M4)] * Nt)
        Md = None
        print(f"[breather-seed] eps={breather_eps} rc={rc_seed} w_b={w_b} "
              f"bmix={bmix}")
    else:
        X0, Md = rotor_seed(nr, nz, h, b0, w_b, rc_seed, omega0, Nt,
                            plane=plane)
    pin = pin_mask(nr, nz)
    # STATIC PINNED BOUNDARY (block-11 audit fix, target T1): the vacuum
    # shell does NOT oscillate: harmonics must vanish on pinned cells.
    # Before this fix the seed's swing amplitude was FROZEN onto the
    # boundary (max |A1| = 0.5 there): the state was boundary-DRIVEN and
    # omega* was the forced-balance frequency of that driven problem.
    for kk in range(len(X0["A"])):
        X0["A"][kk][pin] = 0.0
        X0["B"][kk][pin] = 0.0
    free4 = (~pin)[..., None, None] & np.ones((1, 1, 4, 4), dtype=bool)
    V = Vec(X0, np.broadcast_to(free4, X0["M0"].shape))
    # phase reference + amplitude target from the seed
    U = X0["A"][0][V.free]
    U = U / (np.linalg.norm(U) + 1e-300)
    a2_star = float(np.sum(X0["A"][0][V.free] ** 2)
                    + np.sum(X0["B"][0][V.free] ** 2))
    # the amplitude-continuation ladder (block 11): the target is the SEED
    # amplitude times ascale; ascale > 1 pushes the branch to larger
    # amplitude than the warm-start state (c_amp measures the mismatch)
    a2_star *= ascale

    def F_of(v):
        """rows: [R_free; c_ph; w_amp*c_amp; (w_om*c_omega if w_om)].
        THE FREE-PERIOD CONDITION (block-9 correction, caught in-run): the
        total action is S = T.Lbar = -(2 pi / omega) Shat (Shat is the
        energy-signed per-period average), so dS/domega = 0 gives
            c_omega = dShat/domega - Shat/omega     (NOT dShat/domega = 0:
        the first w_om attempt drove the wrong equation).
        c_amp stays a SOFT regularizer against the trivial (static,
        omega -> 0) branch; its converged residual is the honest
        branch-amplitude mismatch to report."""
        X, om = V.from_vec(v, X0)
        Rd, dSdw = residual(X, om, h, wscale)
        c_ph = float(np.sum(X["B"][0][V.free] * U))
        c_amp = (float(np.sum(X["A"][0][V.free] ** 2)
                       + np.sum(X["B"][0][V.free] ** 2)) / a2_star - 1.0)
        Rm = {"M0": np.where(V.free, Rd["M0"], 0.0),
              "A": [np.where(V.free, a, 0.0) for a in Rd["A"]],
              "B": [np.where(V.free, b, 0.0) for b in Rd["B"]]}
        extra = [c_ph, w_amp * c_amp]
        if w_om:
            Sh = shat(X, om, h, wscale)
            extra.append(w_om * (dSdw - Sh / om))
        return V.r_to_vec(Rm, extra)

    z = V.to_vec(X0, omega0)
    F = F_of(z)
    n_in, n_out = z.size, F.size
    # diagonal column scaling (the design's preconditioner): the residual
    # rows carry the cell weight 2 pi rho h^2 (3 orders across rho), which
    # wrecks unpreconditioned LSMR (istop=7 stall, first run). Change of
    # variables z = D^{-1/2} z' with D = per-DOF weight; omega column scale 1.
    w_cells = cell_weights(*X0["M0"].shape[:2], h)
    wfull = np.ones(X0["M0"].shape[:2])
    wfull[: X0["M0"].shape[0] - 1, 1:-1] = w_cells
    w4 = np.broadcast_to(wfull[..., None, None], X0["M0"].shape)
    d_block = np.sqrt(w4[V.free])
    Dscale = np.concatenate([d_block] * V.blocks + [np.array([1.0])])
    hist = []
    t0 = time.time()
    fn0 = float(np.linalg.norm(F))
    print(f"[d3b {tag}] n{nr} Nt={Nt} wscale={wscale:.4e} b0={b0} "
          f"omega0={omega0} |F|0={fn0:.4e} DOF={n_in}")

    # J structure: rows = [R (X-block); c_ph; c_amp], cols = [X; omega].
    # R = dShat/dX  =>  dR/dX is the (symmetric) HESSIAN of Shat: the
    # X-block of J^T w equals the X-block of J w (symmetry gives rmatvec
    # almost for free); the omega column dR/domega is FD-cached once per
    # Newton iteration; constraint gradients are analytic.
    # Layout: M0 | A1 | B1 | A2 | B2 | omega  (Nt = 2).
    eps_g = 1e-6
    dRdw_cache = None

    def jv_full(vv):
        return (F_of(z + eps_g * vv) - F_of(z - eps_g * vv)) / (2 * eps_g)

    def constraint_grads():
        gph = np.zeros_like(z)
        gph[2 * V.nfree: 3 * V.nfree] = U
        gamp = np.zeros_like(z)
        Xc, _ = V.from_vec(z, X0)
        gamp[V.nfree: 2 * V.nfree] = 2.0 * Xc["A"][0][V.free] / a2_star
        gamp[2 * V.nfree: 3 * V.nfree] = 2.0 * Xc["B"][0][V.free] / a2_star
        return gph, gamp

    n_extra = 3 if w_om else 2               # [c_ph, c_amp, (c_omega)]

    def rmatvec(ww):
        w_R = ww[:-n_extra]
        w_ph, w_a = ww[-n_extra], ww[-n_extra + 1]
        v_pad = np.concatenate([w_R, [0.0]])
        Hw = jv_full(v_pad)[:-n_extra]        # Hessian . w_R (X rows)
        out = np.zeros_like(z)
        out[:-1] = Hw
        out[-1] = float(np.dot(dRdw_cache, w_R))
        gph, gamp = constraint_grads()
        # block-11 fix: the forward row is w_amp*c_amp, so the adjoint must
        # carry w_amp too (it was missing: LSMR's A and A^T disagreed on the
        # row and no w_amp value could steer the amplitude)
        out = out + w_ph * gph + w_a * (w_amp * gamp)
        if w_om:
            # grad of the c_omega row: [dR/domega (X part, symmetric cross
            # derivative = the cached column); d2Shat/domega2] times w_om
            g_com = np.concatenate([dRdw_cache, [d2Sdw2_cache]])
            out = out + ww[-1] * w_om * g_com
        return out

    d2Sdw2_cache = 0.0
    ck_path = os.path.join(DATA, f"m5_12_d3b_{tag}_progress.json")
    for it in range(1, max_newton + 1):
        eps_g = 1e-6 * max(1.0, float(np.linalg.norm(z))) / np.sqrt(n_in)
        zp = z.copy(); zp[-1] += eps_g
        zm = z.copy(); zm[-1] -= eps_g
        Fp, Fm = F_of(zp), F_of(zm)
        dRdw_cache = (Fp[:-n_extra] - Fm[:-n_extra]) / (2 * eps_g)
        if w_om:
            d2Sdw2_cache = float(Fp[-1] - Fm[-1]) / (2 * eps_g * w_om)
        A = LinearOperator(
            (n_out, n_in),
            matvec=lambda vv: jv_full(vv / Dscale),
            rmatvec=lambda ww: rmatvec(ww) / Dscale,
            dtype=float)
        sol = lsmr(A, -F, maxiter=lsmr_iters, atol=1e-8, btol=1e-8)
        s = sol[0] / Dscale
        # damped line search on |F|
        lam, ok = 1.0, False
        fn = float(np.linalg.norm(F))
        for _ in range(6):
            z_try = z + lam * s
            F_try = F_of(z_try)
            if float(np.linalg.norm(F_try)) < fn:
                z, F, ok = z_try, F_try, True
                break
            lam *= 0.5
        Xc, om = V.from_vec(z, X0)
        h1 = float(np.sqrt(np.sum(Xc["A"][0][V.free] ** 2)
                           + np.sum(Xc["B"][0][V.free] ** 2)))
        rec = {"iter": it, "F_norm": float(np.linalg.norm(F)),
               "F_rel": float(np.linalg.norm(F)) / fn0,
               "omega": om, "h1_norm": h1, "lam": lam, "accepted": ok,
               "lsmr_stop": int(sol[1]), "wall_s": round(time.time() - t0, 1)}
        if w_om:
            rec["c_omega"] = float(F[-1] / w_om)   # dShat/dw - Shat/w
            rec["c_amp"] = float(F[-2] / w_amp)
        hist.append(rec)
        extra_s = (f" c_om={rec['c_omega']:.3e} c_amp={rec['c_amp']:+.3f}"
                   if w_om else "")
        print(f"[newton {it}] |F|={rec['F_norm']:.4e} rel={rec['F_rel']:.2e} "
              f"omega={om:.4f} |h1|={h1:.3f} lam={lam:g} ok={ok}{extra_s} "
              f"wall={rec['wall_s']}s")
        with open(ck_path, "w") as f:
            json.dump({"hist": hist, "params": {
                "nr": nr, "nz": nz, "Nt": Nt, "b0": b0, "omega0": omega0,
                "wscale": wscale, "a2_star": a2_star}}, f, indent=1)
        # block-11 fix: checkpoint the FIELD state every iteration too (an
        # early-stopped run used to lose its fields: states saved only at
        # loop exit)
        Xck, omck = V.from_vec(z, X0)
        np.savez_compressed(
            os.path.join(DATA, f"m5_12_d3b_{tag}_state_ck.npz"),
            M0=Xck["M0"].astype(np.float32),
            **{f"A{k+1}": Xck["A"][k].astype(np.float32)
               for k in range(len(Xck["A"]))},
            **{f"B{k+1}": Xck["B"][k].astype(np.float32)
               for k in range(len(Xck["B"]))},
            omega=np.array([omck]))
        if not ok:
            print("[newton] line search failed: stalled")
            break
        if rec["F_rel"] < 1e-5:
            print("[newton] CONVERGED")
            break
    # endpoint classification + save
    Xc, om = V.from_vec(z, X0)
    Sh = shat(Xc, om, h, wscale)
    # persist the endpoint state (warm-start / continuation; float32)
    np.savez_compressed(
        os.path.join(DATA, f"m5_12_d3b_{tag}_state.npz"),
        M0=Xc["M0"].astype(np.float32),
        **{f"A{k+1}": Xc["A"][k].astype(np.float32) for k in range(len(Xc["A"]))},
        **{f"B{k+1}": Xc["B"][k].astype(np.float32) for k in range(len(Xc["B"]))},
        omega=np.array([om]))
    out = {"task": "M5.12", "script": "m5_12_d3b_newton.py", "tag": tag,
           "grade": "scaffolding grid n%d; rigid-rotor seed; Nt=%d" % (nr, Nt),
           "hist": hist, "omega_end": om, "Shat_end": Sh,
           "h1_norm_end": hist[-1]["h1_norm"] if hist else None,
           "verdict": ("converged_nontrivial" if hist and hist[-1]["F_rel"] < 1e-5
                       and hist[-1]["h1_norm"] > 0.1 * np.sqrt(a2_star)
                       else "stalled_or_partial")}
    path = os.path.join(DATA, f"m5_12_d3b_{tag}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[d3b] verdict={out['verdict']} Shat={Sh:.4f} json -> {path}")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "hedgehog"
    nr = int(_flag("nr", 48, int))
    mn = int(_flag("newton", 12, int))
    b0 = _flag("b0", 1.6)
    Nt = int(_flag("nt", 2, int))
    li = int(_flag("lsmr", 60, int))
    om0 = _flag("omega0", 0.34)
    ws = _flag("warmstart", None, str)
    wa = _flag("wamp", 0.3)
    wo = _flag("wom", 0.0)
    asc = _flag("ascale", 1.0)
    tx = _flag("tagx", "", str)
    if mode == "hedgehog":
        run_newton(nr=nr, max_newton=mn, b0=b0, Nt=Nt, lsmr_iters=li,
                   omega0=om0, tag="hedgehog", warmstart=ws, w_amp=wa,
                   w_om=wo, ascale=asc, tag_suffix=tx)
    elif mode == "axisswing":
        run_newton(nr=nr, max_newton=mn, b0=b0, Nt=Nt, lsmr_iters=li,
                   omega0=om0, tag="axisswing", plane=(2, 3), warmstart=ws,
                   w_amp=wa, w_om=wo, ascale=asc, tag_suffix=tx)
    elif mode == "breather":
        # 10b: the free-period class seed: pure AMPLITUDE first harmonic on
        # the (covariant) hedgehog, no rotation, no time-mixing: the class
        # where the corrected c_omega row can have a root
        run_newton(nr=nr, max_newton=mn, b0=0.0, Nt=Nt, lsmr_iters=li,
                   omega0=om0, tag="breather", plane=(2, 3), warmstart=ws,
                   w_amp=wa, w_om=wo, breather_eps=_flag("beps", 0.15),
                   ascale=asc, tag_suffix=tx,
                   bmix=bool(_flag("bmix", 0, int)))
    else:
        print(f"unknown mode {mode}")
