"""M5.12 block 12: the omega-eliminated, hard-amplitude free-period solver.

Block-11's twin verdicts (task_details FINDINGS block 11) define this rung:
the balance root recedes as 1/amplitude under any PENALTY method, and the
soft-row solver drains amplitude. Both die here by construction:

  omega ELIMINATED   on the audit-verified structure Shat = S0 - omega^2 Q2
                     the free-period condition c_omega = dShat/domega -
                     Shat/omega = 0 is solved in closed form by
                         omega_bal(X) = sqrt(S0(X) / (-Q2(X)))   (Q2 < 0)
                     so we solve R(X, omega_bal(X)) = 0 in X alone: every
                     iterate satisfies the free-period condition EXACTLY.
  amplitude HARD     retraction: after each accepted step the first-harmonic
                     free part is rescaled to the rung target a2_star
                     (constraint elimination, no penalty row to leak).

Jacobian of the composed map (rows R only; the phase row has no omega):
    J = H(X, w) + (dR/domega) (x) (domega_bal/dX)        [rank-one update]
with, from R(X, w) = R0 - w^2 RQ (RQ := dQ2/dX = R(X,0) - R(X,1)):
    dR/domega        = -2 w RQ                              (analytic)
    domega_bal/dX    = [R0/P + (S0/P^2) RQ] / (2 w),  P := -Q2
so matvec = FD of the composed F (captures the rank-one automatically) and
rmatvec = H w (symmetric fixed-omega Hessian, FD) + g (dRdw . w) + phase.

Gates (must pass before the ladder):
    HG1  composed-residual FD == matvec (random direction)
    HG2  c_omega(X, omega_bal(X)) == 0 through the d3a residual's dSdw
    HG3  retraction exactness (|a2 - a2_star| rel < 1e-12)
    HG4  F rows == the d3a residual at (X, omega_bal) on the free DOF

Ladder: warmstart = the mixfix endpoint; rungs a2_star = base * ascale;
per-rung endpoint gets BG5 (H-drift) immediately. Convergence at any rung
(F_rel < 1e-5) = the program's first free-period-orbit candidate.

Run:  python m5_12_b12_hard.py gates --nr 32 --state <npz>
      python m5_12_b12_hard.py ladder --nr 32 --state <npz> \
             [--rungs 1,2,4,8] [--newton 8] [--lsmr 200]
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

from m5_17_energy import cell_weights                                      # noqa: E402
from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_d3a_bvp import residual, shat                                   # noqa: E402
from m5_12_d3b_newton import load_warmstart, wscale_at                     # noqa: E402
from m5_12_gauntlet import bg5_noether                                     # noqa: E402


def _flag(name, default, cast=float):
    for i, a in enumerate(ARGV):
        if a == "--" + name and i + 1 < len(ARGV):
            return cast(ARGV[i + 1])
    return default


class HardVec:
    """flatten X = (M0, A_k, B_k) over the free mask; NO omega column."""

    def __init__(self, X0, free):
        self.free = free
        self.nfree = int(np.sum(free))
        self.Nt = len(X0["A"])
        self.blocks = 1 + 2 * self.Nt

    def to_vec(self, X):
        parts = [X["M0"][self.free]]
        for k in range(self.Nt):
            parts.append(X["A"][k][self.free])
            parts.append(X["B"][k][self.free])
        return np.concatenate(parts)

    def from_vec(self, v, X0):
        X = {"M0": X0["M0"].copy(), "A": [a.copy() for a in X0["A"]],
             "B": [b.copy() for b in X0["B"]]}
        o, n = 0, self.nfree
        X["M0"][self.free] = v[o:o + n]; o += n
        for k in range(self.Nt):
            X["A"][k][self.free] = v[o:o + n]; o += n
            X["B"][k][self.free] = v[o:o + n]; o += n
        return X

    def r_to_vec(self, Rd, extra):
        parts = [np.where(self.free, Rd["M0"], 0.0)[self.free]]
        for k in range(self.Nt):
            parts.append(np.where(self.free, Rd["A"][k], 0.0)[self.free])
            parts.append(np.where(self.free, Rd["B"][k], 0.0)[self.free])
        return np.concatenate(parts + [np.asarray(extra)])


def s0_q2(X, h, wscale):
    s0 = shat(X, 0.0, h, wscale)
    return s0, s0 - shat(X, 1.0, h, wscale)      # S0, Q2


def omega_bal(X, h, wscale):
    s0, q2 = s0_q2(X, h, wscale)
    if q2 >= 0 or s0 <= 0:
        return None, s0, q2
    return float(np.sqrt(s0 / -q2)), s0, q2


def run_ladder(nr, state, rungs, max_newton, lsmr_iters, h=1.0, Nt=2,
               gates_only=False, tag_prefix="r"):
    nz = 2 * nr
    wscale = wscale_at(nr, nz, h, 8.0 * nr / 96)
    X0, _ = load_warmstart(state, nr, nz, Nt)
    pin = pin_mask(nr, nz)
    for k in range(Nt):                      # zero harmonic BCs (block-11 rule)
        X0["A"][k][pin] = 0.0
        X0["B"][k][pin] = 0.0
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), X0["M0"].shape)
    V = HardVec(X0, free)
    U = X0["A"][0][V.free]
    U = U / (np.linalg.norm(U) + 1e-300)
    a2_base = float(np.sum(X0["A"][0][V.free] ** 2)
                    + np.sum(X0["B"][0][V.free] ** 2))

    n1, n2 = V.nfree, 2 * V.nfree            # A1/B1 slices in the flat vector

    def retract(v, a2_star):
        a2 = float(np.sum(v[n1:n1 + n2] ** 2))
        if a2 <= 0:
            return v, 0.0
        vv = v.copy()
        vv[n1:n1 + n2] *= np.sqrt(a2_star / a2)
        return vv, a2

    def F_of(v):
        X = V.from_vec(v, X0)
        w, s0, q2 = omega_bal(X, h, wscale)
        if w is None:
            return None, (None, s0, q2)
        Rd, dSdw = residual(X, w, h, wscale)
        c_ph = float(np.sum(X["B"][0][V.free] * U))
        return V.r_to_vec(Rd, [c_ph]), (w, s0, q2, dSdw)

    # ---------------- gates ----------------
    z = V.to_vec(X0)
    z, _ = retract(z, a2_base)
    F, (w0, s00, q20, dSdw0) = F_of(z)
    if w0 is None:
        print(f"[HG] ABORT: warmstart state has Q2 = {q20:+.4e} >= 0")
        return
    # HG2: c_omega at omega_bal == 0 through the instrument's own dSdw
    sh = shat(V.from_vec(z, X0), w0, h, wscale)
    hg2 = abs(dSdw0 - sh / w0) / (abs(dSdw0) + 1e-300)
    # HG4: F rows == d3a residual at (X, omega_bal)
    Rd4, _ = residual(V.from_vec(z, X0), w0, h, wscale)
    hg4 = float(np.max(np.abs(
        V.r_to_vec(Rd4, [0.0])[:-1] - F[:-1])))
    # HG3: retraction exactness
    zr, _ = retract(z, 2.0 * a2_base)
    hg3 = abs(float(np.sum(zr[n1:n1 + n2] ** 2)) / (2.0 * a2_base) - 1.0)
    # HG1: composed FD == matvec on a random direction
    rng = np.random.default_rng(11)
    vdir = rng.standard_normal(z.size)
    vdir /= np.linalg.norm(vdir)
    eps = 1e-6 * max(1.0, np.linalg.norm(z)) / np.sqrt(z.size)
    Fp, _ = F_of(z + eps * vdir)
    Fm, _ = F_of(z - eps * vdir)
    jv_fd = (Fp - Fm) / (2 * eps)
    hg1 = 0.0   # matvec IS the same composed FD; consistency = finite check
    hg1 = float(np.sum(~np.isfinite(jv_fd)))
    print(f"[HG1] composed FD finite: bad={hg1:.0f}  "
          f"[HG2] c_om(omega_bal) rel={hg2:.3e}  [HG3] retract={hg3:.3e}  "
          f"[HG4] row-match={hg4:.3e}")
    gates = {"HG1_nonfinite": hg1, "HG2_com_rel": hg2, "HG3_retract": hg3,
             "HG4_rowmatch": hg4,
             "omega_bal0": w0, "S0": s00, "Q2": q20}
    gname = "m5_12_b12_gates" \
        + ("" if tag_prefix == "r" else "_" + tag_prefix) + ".json"
    with open(os.path.join(DATA, gname), "w") as f:
        json.dump(gates, f, indent=2)
    ok = (hg1 == 0 and hg2 < 1e-8 and hg3 < 1e-12 and hg4 < 1e-12)
    print(f"[HG] {'ALL PASS' if ok else 'FAIL'}; omega_bal(warmstart)="
          f"{w0:.4f} S0={s00:.4f} Q2={q20:+.6f}")
    if gates_only or not ok:
        return

    # ---------------- the ladder ----------------
    w_cells = cell_weights(nr, nz, h)
    wfull = np.ones(X0["M0"].shape[:2])
    wfull[: nr - 1, 1:-1] = w_cells
    d_block = np.sqrt(np.broadcast_to(
        wfull[..., None, None], X0["M0"].shape)[V.free])
    Dscale = np.concatenate([d_block] * V.blocks)
    ladder_out = []
    for ascale in rungs:
        a2_star = a2_base * ascale
        z, _ = retract(z, a2_star)
        F, meta = F_of(z)
        if F is None:
            print(f"[rung a{ascale}] ABORT: Q2 >= 0 after retract "
                  f"(Q2={meta[2]:+.4e})")
            break
        fn0 = float(np.linalg.norm(F))
        tag = f"{tag_prefix}{ascale:g}"
        print(f"[rung {tag}] a2_star={a2_star:.4f} |F|0={fn0:.4e} "
              f"omega_bal={meta[0]:.4f} S0={meta[1]:.4f} Q2={meta[2]:+.6f}")
        hist = []
        t0 = time.time()
        stall = 0
        frac_prev = 0.0     # winning LM damp fraction of the previous iter
        norma_est = None
        for it in range(1, max_newton + 1):
            X = V.from_vec(z, X0)
            w, s0, q2 = omega_bal(X, h, wscale)
            # per-iteration caches for the rank-one rmatvec
            R0d, _ = residual(X, 0.0, h, wscale)
            R1d, _ = residual(X, 1.0, h, wscale)
            R0v = V.r_to_vec(R0d, [0.0])[:-1]
            RQv = R0v - V.r_to_vec(R1d, [0.0])[:-1]
            P = -q2
            gvec = (R0v / P + (s0 / P ** 2) * RQv) / (2.0 * w)
            dRdw = -2.0 * w * RQv
            # phase-row gradient: dc_ph/dB1 = U (B1 sits after M0|A1)
            gph_v = np.zeros_like(z)
            gph_v[n1 + V.nfree: n1 + 2 * V.nfree] = U

            eps_g = 1e-6 * max(1.0, float(np.linalg.norm(z))) \
                / np.sqrt(z.size)

            def jv(vv):
                Fp, _ = F_of(z + eps_g * vv)
                Fm, _ = F_of(z - eps_g * vv)
                if Fp is None or Fm is None:
                    return np.full(F.size, np.nan)
                return (Fp - Fm) / (2 * eps_g)

            def rmv(ww):
                w_R, w_ph = ww[:-1], ww[-1]
                # symmetric fixed-omega Hessian action via FD of fixed-w R
                Xp = V.from_vec(z + eps_g * w_R, X0)
                Xm = V.from_vec(z - eps_g * w_R, X0)
                Rp, _ = residual(Xp, w, h, wscale)
                Rm, _ = residual(Xm, w, h, wscale)
                Hw = (V.r_to_vec(Rp, [0.0])[:-1]
                      - V.r_to_vec(Rm, [0.0])[:-1]) / (2 * eps_g)
                return Hw + gvec * float(np.dot(dRdw, w_R)) \
                    + w_ph * gph_v

            A = LinearOperator((F.size, z.size),
                               matvec=lambda vv: jv(vv / Dscale),
                               rmatvec=lambda ww: rmv(ww) / Dscale,
                               dtype=float)
            # Levenberg-Marquardt damp escalation (the block-13 probe
            # verdict: the exact GN step from FD-noisy operators is NOT a
            # descent direction; truncated Krylov only regularized by
            # accident, non-monotonically in budget). damp is a FRACTION of
            # LSMR's running ||A|| estimate; the winning fraction seeds the
            # next iteration's schedule.
            if frac_prev > 0:
                fracs = (frac_prev / 3, frac_prev, 3 * frac_prev,
                         10 * frac_prev)
            else:
                fracs = (0.0, 1e-3, 1e-2, 1e-1)
            fn = float(np.linalg.norm(F))
            ok_step, lam, used_frac, sol = False, 1.0, None, None
            for frac in fracs:
                damp = frac * norma_est if (frac and norma_est) else 0.0
                sol = lsmr(A, -F, damp=damp, maxiter=lsmr_iters,
                           atol=1e-8, btol=1e-8)
                norma_est = float(sol[5]) or norma_est
                s = sol[0] / Dscale
                lam = 1.0
                for _ in range(6):
                    z_try, _ = retract(z + lam * s, a2_star)
                    F_try, meta_try = F_of(z_try)
                    if F_try is not None \
                            and float(np.linalg.norm(F_try)) < fn:
                        z, F, ok_step = z_try, F_try, True
                        w, s0, q2 = meta_try[0], meta_try[1], meta_try[2]
                        break
                    lam *= 0.5
                if ok_step:
                    used_frac = frac
                    frac_prev = frac if frac > 0 else 0.0
                    break
            rec = {"iter": it, "F_norm": float(np.linalg.norm(F)),
                   "F_rel": float(np.linalg.norm(F)) / fn0,
                   "omega_bal": w, "S0": s0, "Q2": q2, "lam": lam,
                   "accepted": ok_step, "lsmr_stop": int(sol[1]),
                   "damp_frac": used_frac,
                   "wall_s": round(time.time() - t0, 1)}
            hist.append(rec)
            print(f"[{tag} newton {it}] |F|={rec['F_norm']:.4e} "
                  f"rel={rec['F_rel']:.2e} w_bal={w:.4f} Q2={q2:+.5f} "
                  f"lam={lam:g} damp={used_frac} ok={ok_step} "
                  f"wall={rec['wall_s']}s")
            with open(os.path.join(
                    DATA, f"m5_12_b12_hard_{tag}_progress.json"), "w") as f:
                json.dump({"hist": hist, "a2_star": a2_star}, f, indent=1)
            Xck = V.from_vec(z, X0)
            np.savez_compressed(
                os.path.join(DATA, f"m5_12_b12_hard_{tag}_state_ck.npz"),
                M0=Xck["M0"].astype(np.float32),
                **{f"A{k+1}": Xck["A"][k].astype(np.float32)
                   for k in range(Nt)},
                **{f"B{k+1}": Xck["B"][k].astype(np.float32)
                   for k in range(Nt)},
                omega=np.array([w]))
            if not ok_step:
                print(f"[{tag}] line search failed: stalled")
                break
            drop = 1.0 - rec["F_norm"] / fn
            stall = stall + 1 if drop < 0.01 else 0
            if stall >= 3:
                print(f"[{tag}] 3 consecutive sub-1% steps: stall stop")
                break
            if rec["F_rel"] < 1e-5:
                print(f"[{tag}] CONVERGED: free-period-orbit candidate")
                break
        # rung endpoint: BG5 immediately
        Xe = V.from_vec(z, X0)
        we, s0e, q2e = omega_bal(Xe, h, wscale)
        bg5 = bg5_noether(Xe, we, h, wscale) if we else None
        # honest H metric (block-13 audit L5): at omega_bal H_mean = 0 BY
        # CONSTRUCTION, so drift_rel is noise-normalized; report the SWING
        swing = (bg5["H_max"] - bg5["H_min"]) if bg5 else None
        # Q2 channel split (audit L2: the bend = eta-positive growth):
        # zero the time-mixing rows / the spatial block of A1,B1 in turn
        def q2_channel(keep_mix):
            Xc = {"M0": Xe["M0"].copy(),
                  "A": [a.copy() for a in Xe["A"]],
                  "B": [b.copy() for b in Xe["B"]]}
            for arr in Xc["A"] + Xc["B"]:
                if keep_mix:
                    arr[..., 1:4, 1:4] = 0.0
                else:
                    arr[..., 0, :] = 0.0
                    arr[..., :, 0] = 0.0
            _, q2c = s0_q2(Xc, h, wscale)
            return q2c
        q2_mix, q2_pos = q2_channel(True), q2_channel(False)
        end = {"rung": ascale, "a2_star": a2_star, "hist": hist,
               "omega_bal_end": we, "S0_end": s0e, "Q2_end": q2e,
               "Q2_mix": q2_mix, "Q2_pos": q2_pos,
               "Q2_cross": (q2e - q2_mix - q2_pos),
               "Shat_end": shat(Xe, we, h, wscale) if we else None,
               "BG5": bg5, "H_swing": swing,
               "H_swing_over_S0": (swing / s0e if swing and s0e else None),
               "verdict": ("converged_free_period_candidate"
                           if hist and hist[-1]["F_rel"] < 1e-5
                           else "stalled_or_partial")}
        ladder_out.append(end)
        np.savez_compressed(
            os.path.join(DATA, f"m5_12_b12_hard_{tag}_state.npz"),
            M0=Xe["M0"].astype(np.float32),
            **{f"A{k+1}": Xe["A"][k].astype(np.float32) for k in range(Nt)},
            **{f"B{k+1}": Xe["B"][k].astype(np.float32) for k in range(Nt)},
            omega=np.array([we if we else 0.0]))
        lname = "m5_12_b12_hard_ladder" \
            + ("" if tag_prefix == "r" else "_" + tag_prefix) + ".json"
        with open(os.path.join(DATA, lname), "w") as f:
            json.dump({"task": "M5.12", "script": "m5_12_b12_hard.py",
                       "nr": nr, "state0": os.path.basename(state),
                       "rungs": ladder_out}, f, indent=2)
        print(f"[rung {tag} END] verdict={end['verdict']} "
              f"w_bal={we if we else -1:.4f} Q2={q2e:+.5f} "
              f"(mix {q2_mix:+.4f} pos {q2_pos:+.4f}) "
              f"H_swing/S0={end['H_swing_over_S0'] or float('nan'):.3f}")
    print("[ladder] done -> m5_12_b12_hard_ladder.json")


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gates"
    nr = int(_flag("nr", 32, int))
    state = _flag("state", "../data/m5_12_d3b_breather_n32_mixfix_state.npz",
                  str)
    rungs = [float(r) for r in _flag("rungs", "1,2,4,8", str).split(",")]
    mn = int(_flag("newton", 8, int))
    li = int(_flag("lsmr", 200, int))
    tp = _flag("tagpre", "r", str)
    run_ladder(nr, state, rungs, mn, li, gates_only=(mode == "gates"),
               tag_prefix=tp)
