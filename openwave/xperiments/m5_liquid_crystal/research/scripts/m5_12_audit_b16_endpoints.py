"""M5.12 block 16 ADVERSARIAL AUDIT, leg 1: C1 (chain endpoints) + C5
(probe integrity).

Independent recomputation, own code for the channel split, a2, phase row,
J^T F and a Cauchy descent trial; the shat/residual instrument itself is
block-11-audit verified and is the shared meter.

Run:  python m5_12_audit_b16_endpoints.py
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                      # noqa: E402
from m5_16_axisym import hedgehog_field, pin_mask                          # noqa: E402
from m5_12_dressed import to_covariant                                     # noqa: E402
from m5_12_d3a_bvp import shat, residual, x_pack                           # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402
from m5_12_gauntlet import bg5_noether                                     # noqa: E402


def load_state(path):
    d = np.load(path)
    return x_pack(d["M0"].astype(np.float64),
                  [d["A1"].astype(np.float64), d["A2"].astype(np.float64)],
                  [d["B1"].astype(np.float64), d["B2"].astype(np.float64)])


def my_a2_free(X, pin):
    """own reimplementation: first-harmonic free-cell amplitude square."""
    keep = ~pin
    return float(np.sum(X["A"][0][keep] ** 2) + np.sum(X["B"][0][keep] ** 2))


def my_channels(X, h, wscale):
    """own channel split: zero the spatial block (keep mix) or the 0-row/col
    (keep pos) of every harmonic; Q2 = Shat(0) - Shat(1) each time."""
    out = {}
    for tag, keep_mix in (("mix", True), ("pos", False)):
        Xc = {"M0": X["M0"].copy(), "A": [a.copy() for a in X["A"]],
              "B": [b.copy() for b in X["B"]]}
        for arr in Xc["A"] + Xc["B"]:
            if keep_mix:
                arr[..., 1:, 1:] = 0.0
            else:
                arr[..., 0, :] = 0.0
                arr[..., :, 0] = 0.0
        out[tag] = shat(Xc, 0.0, h, wscale) - shat(Xc, 1.0, h, wscale)
    return out


def flat_free(X, free):
    parts = [X["M0"][free]]
    for k in range(len(X["A"])):
        parts.append(X["A"][k][free])
        parts.append(X["B"][k][free])
    return np.concatenate(parts)


def unflat(v, X0, free):
    X = {"M0": X0["M0"].copy(), "A": [a.copy() for a in X0["A"]],
         "B": [b.copy() for b in X0["B"]]}
    n = int(np.sum(free))
    o = 0
    X["M0"][free] = v[o:o + n]; o += n
    for k in range(len(X["A"])):
        X["A"][k][free] = v[o:o + n]; o += n
        X["B"][k][free] = v[o:o + n]; o += n
    return X


def r_free(Rd, free):
    parts = [Rd["M0"][free]]
    for k in range(len(Rd["A"])):
        parts.append(Rd["A"][k][free])
        parts.append(Rd["B"][k][free])
    return np.concatenate(parts)


def endpoint_audit(tag, state, seed_state, ladder, h, wscale, out):
    pub = json.load(open(os.path.join(DATA, ladder)))["rungs"][-1]
    X = load_state(os.path.join(DATA, state))
    nr, nz = X["M0"].shape[:2]
    pin = pin_mask(nr, nz)
    s0 = shat(X, 0.0, h, wscale)
    q2 = s0 - shat(X, 1.0, h, wscale)
    w = float(np.sqrt(s0 / -q2))
    ch = my_channels(X, h, wscale)
    a2 = my_a2_free(X, pin)
    bg5 = bg5_noether(X, w, h, wscale)
    swing = bg5["H_max"] - bg5["H_min"]
    # |F| with the chain's phase row (U = normalized SEED A1 on free DOF)
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), X["M0"].shape)
    Xs = load_state(os.path.join(DATA, seed_state))
    U = Xs["A"][0][free]
    U = U / (np.linalg.norm(U) + 1e-300)
    Rd, _ = residual(X, w, h, wscale)
    c_ph = float(np.sum(X["B"][0][free] * U))
    Fv = np.concatenate([r_free(Rd, free), [c_ph]])
    Fn = float(np.linalg.norm(Fv))
    # J^T F via own rmatvec (fixed-w Hessian FD + rank-one + phase row)
    z = flat_free(X, free)
    R0d, _ = residual(X, 0.0, h, wscale)
    R1d, _ = residual(X, 1.0, h, wscale)
    R0v = r_free(R0d, free)
    RQv = R0v - r_free(R1d, free)
    P = -q2
    gvec = (R0v / P + (s0 / P ** 2) * RQv) / (2.0 * w)
    eps_g = 1e-6 * max(1.0, float(np.linalg.norm(z))) / np.sqrt(z.size)
    w_R, w_ph = Fv[:-1], Fv[-1]
    Rp, _ = residual(unflat(z + eps_g * w_R, X, free), w, h, wscale)
    Rm, _ = residual(unflat(z - eps_g * w_R, X, free), w, h, wscale)
    Hw = (r_free(Rp, free) - r_free(Rm, free)) / (2 * eps_g)
    JtF = Hw + gvec * float(np.dot(-2.0 * w * RQv, w_R))
    n = int(np.sum(free))
    JtF_full = JtF.copy()
    JtF_full[2 * n:3 * n] += w_ph * U     # dc_ph/dB1 = U (B1 block)
    jtf = float(np.linalg.norm(JtF_full))

    def F_of(v):
        Xv = unflat(v, X, free)
        s0v = shat(Xv, 0.0, h, wscale)
        q2v = s0v - shat(Xv, 1.0, h, wscale)
        if q2v >= 0 or s0v <= 0:
            return None
        wv = float(np.sqrt(s0v / -q2v))
        Rdv, _ = residual(Xv, wv, h, wscale)
        return np.concatenate(
            [r_free(Rdv, free), [float(np.sum(Xv["B"][0][free] * U))]])

    def retract(v):
        vv = v.copy()
        a2v = float(np.sum(vv[n:3 * n] ** 2))
        vv[n:3 * n] *= np.sqrt(a2 / a2v)
        return vv

    # Cauchy step on phi = |F|^2/2: d = -J^T F, t* = |g|^2 / |J d|^2
    d = -JtF_full
    Fp = F_of(z + eps_g * d / np.linalg.norm(d))
    Jd = (Fp - Fv) / eps_g * np.linalg.norm(d) if Fp is not None else None
    trials = []
    if Jd is not None:
        t_star = float(np.dot(JtF_full, JtF_full) / np.dot(Jd, Jd))
        for t in (t_star, 4.0 * t_star, 16.0 * t_star):
            Ft = F_of(retract(z + t * d))
            trials.append({"t": t, "F_norm": (float(np.linalg.norm(Ft))
                                              if Ft is not None else None)})
    rec = {
        "tag": tag, "state": state,
        "published": {"omega_bal": pub["omega_bal_end"], "S0": pub["S0_end"],
                      "Q2": pub["Q2_end"], "Q2_mix": pub["Q2_mix"],
                      "Q2_pos": pub["Q2_pos"], "a2_star": pub["a2_star"],
                      "F_norm": pub["hist"][-1]["F_norm"],
                      "F_rel": pub["hist"][-1]["F_rel"],
                      "H_swing_over_S0": pub["H_swing_over_S0"],
                      "H_mean": pub["BG5"]["H_mean"]},
        "recomputed": {"omega_bal": w, "S0": s0, "Q2": q2,
                       "Q2_mix": ch["mix"], "Q2_pos": ch["pos"],
                       "Q2_cross": q2 - ch["mix"] - ch["pos"],
                       "a2_free": a2, "F_norm": Fn,
                       "H_mean": bg5["H_mean"], "H_swing": swing,
                       "H_swing_over_S0": swing / s0,
                       "JtF_norm": jtf, "JtF_over_F": jtf / Fn,
                       "mix_share": ch["mix"] / q2},
        "cauchy_trials": trials,
        "a2_rel_dev": abs(a2 - pub["a2_star"]) / pub["a2_star"],
        "H_mean_over_swing": abs(bg5["H_mean"]) / swing,
    }
    out["endpoints"].append(rec)
    print(f"[{tag}] w_bal {w:.4f} (pub {pub['omega_bal_end']:.4f})  "
          f"|F| {Fn:.2f} (pub {pub['hist'][-1]['F_norm']:.2f})  "
          f"a2 rel dev {rec['a2_rel_dev']:.2e}  "
          f"H_mean/swing {rec['H_mean_over_swing']:.2e}  "
          f"|JtF| {jtf:.3e}  mix share {ch['mix']/q2:.4f}")
    for t in trials:
        print(f"        cauchy t={t['t']:.3e} -> |F| {t['F_norm']}")


def my_aniso_forge(nr, nz, h, eps, wr, wz, a2_star, pin):
    """own re-forge of the aniso seed (formula from first principles)."""
    R, Z = grid_coords(nr, nz, h)
    M4 = to_covariant(hedgehog_field(R, Z, 8.0 * nr / 96.0))
    rr = np.sqrt(R ** 2 + Z ** 2) + 1e-12
    b = np.exp(-(R / wr) ** 2 - (Z / wz) ** 2)
    A1 = np.zeros_like(M4)
    A1[..., 0, 1] = A1[..., 1, 0] = eps * b * R / rr
    A1[..., 0, 3] = A1[..., 3, 0] = eps * b * Z / rr
    A1[pin] = 0.0
    zero = np.zeros_like(M4)
    X = x_pack(M4, [A1, zero.copy()], [zero.copy(), zero.copy()])
    a2 = my_a2_free(X, pin)
    X["A"][0] *= np.sqrt(a2_star / a2)
    return X


def main():
    t0 = time.time()
    h, nr, nz = 1.0, 32, 64
    wscale = wscale_at(nr, nz, h, 8.0 * nr / 96)
    pin = pin_mask(nr, nz)
    out = {"task": "M5.12 block 16 audit leg 1 (C1 + C5)",
           "date": "2026-07-09", "wscale": wscale,
           "seeds": [], "endpoints": [], "reforge": {}}

    # ---- C5: a2_star from the reference, then seed spot-probes ----
    ref = load_state(os.path.join(
        DATA, "m5_12_d3b_breather_n32_c2seed_state.npz"))
    a2_star = my_a2_free(ref, pin)
    out["a2_star_recomputed"] = a2_star
    print(f"[a2*] {a2_star:.9f} (pub 0.303724649)")

    pub = json.load(open(os.path.join(DATA, "m5_12_b16_aniso.json")))
    pub_rows = {(r.get("kr"), r.get("kz"), r["family"]): r
                for r in pub["rows"]}
    checks = [(1.0, 1.0, "aniso_gauss"), (2.0, 2.0, "aniso_gauss"),
              (4.0, 1.0, "aniso_gauss"), (None, None, "rayleigh_opt")]
    for kr, kz, fam in checks:
        p = pub_rows[(kr, kz, fam)]
        X = load_state(os.path.join(DATA, p["state"]))
        s0 = shat(X, 0.0, h, wscale)
        q2 = s0 - shat(X, 1.0, h, wscale)
        w = float(np.sqrt(s0 / -q2)) if q2 < 0 else None
        a2 = my_a2_free(X, pin)
        rec = {"family": fam, "kr": kr, "kz": kz,
               "pub": {"S0": p["S0"], "Q2": p["Q2"],
                       "omega_bal": p["omega_bal"], "a2": p["a2"]},
               "rec": {"S0": s0, "Q2": q2, "omega_bal": w, "a2": a2},
               "w_rel_dev": abs(w - p["omega_bal"]) / p["omega_bal"]}
        out["seeds"].append(rec)
        print(f"[seed {fam} {kr}/{kz}] w {w:.4f} vs pub "
              f"{p['omega_bal']:.4f} (rel {rec['w_rel_dev']:.1e})  "
              f"a2 {a2:.6f}")

    # ---- C5b: independent re-forge of the p2 seed (r4z1) ----
    w_b = 8.0 * nr / 96.0
    Xf = my_aniso_forge(nr, nz, h, 0.16490, 4.0 * w_b, 1.0 * w_b,
                        a2_star, pin)
    s0f = shat(Xf, 0.0, h, wscale)
    q2f = s0f - shat(Xf, 1.0, h, wscale)
    wf = float(np.sqrt(s0f / -q2f))
    out["reforge"] = {"kr": 4.0, "kz": 1.0, "omega_bal": wf,
                      "pub": pub_rows[(4.0, 1.0, "aniso_gauss")]["omega_bal"],
                      "rel_dev": abs(wf - 8.057650258028477) / 8.0577}
    print(f"[reforge r4z1] own forge w_bal {wf:.4f} vs pub 8.0577")

    # ---- C1: the two chain endpoints ----
    endpoint_audit("p1", "m5_12_b12_hard_p1_1_state.npz",
                   "m5_12_b16_seed_rayleigh_opt_n32.npz",
                   "m5_12_b12_hard_ladder_p1_.json", h, wscale, out)
    endpoint_audit("p2", "m5_12_b12_hard_p2_1_state.npz",
                   "m5_12_b16_seed_aniso_r4z1_n32.npz",
                   "m5_12_b12_hard_ladder_p2_.json", h, wscale, out)

    out["wall_s"] = round(time.time() - t0, 1)
    path = os.path.join(DATA, "m5_12_audit_b16_endpoints.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(f"[done] {out['wall_s']}s -> {os.path.basename(path)}")


if __name__ == "__main__":
    main()
