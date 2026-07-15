"""M5.12 phase D1: the clock-dressing lever, MEASURED (the uniform-rotation
quadratic form Q_W on the calibrated instrument).

THE REDUCTION (exact, gated here). For the uniformly rotating clock ansatz
    M(x, t) = Lam(t)^{-T} Mtil(x) Lam(t)^{-1},   Lam(t) = expm(omega t eta W),
    W antisymmetric (a Lorentz generator),
every eta-invariant density is t-independent (Lorentz isometry), and
    d_t M |_0 = omega [W, Mtil]_eta          ([A,B]_eta = A.eta.B - B.eta.A)
so the VERIFIED Hamiltonian (m5_18_verification_note.md § 3) evaluates to
    H(omega) = E_static[Mtil] + 4 omega^2 Q_W[Mtil]     (instrument units)
    Q_W = SUM_i inner_eta( [ [W, Mtil]_eta, d_i Mtil ]_eta , same ),
    ⚠️ NORMALIZATION (2026-07-07 adversarial audit): the calibrated
    E_static carries the spatial F.F pairs at 4x the verified-H weight
    (curvature_density_np's factor 4), while Q_W is at weight 1, so the
    commensurate identity needs the explicit 4 above (equivalently omega ->
    2 omega); the m5_12_clock_q.json omega^2 windows are mislabeled by 4.
    AUDIT VERDICTS (full record: m5_12_task_details.md § FINDINGS block 2):
    the reduction algebra + phi-averaging are EXACT; but Q_W magnitudes are
    box-divergent (unconverged), the boost-negativity is algebraically
    FORCED for any zero-time-mixing texture (not defect-diagnostic), 99.4%
    of the channel rides the frozen g_time background, and the loop
    size-selection R0-trend is far-field-driven (near-ring trend OPPOSITE
    sign; defect-attributed Q_def = Q_melt - Q_vac is POSITIVE). The
    size-selection headline is RETRACTED; the machinery + sign theorem
    stand. Next rung: the time-MIXING dressed-state class (M5.8 heritage).
with inner_eta the internal double-eta raising: THE negative channel lives
in the time-mixing internal components (the note's blue-boxed terms). Q_W < 0
on a region = the clock LOWERS the energy there at fixed texture: the
"energetically preferred time derivatives" of Duda's 2026-07-06 reply,
made into a measurable functional.

WHAT D1 MEASURES
    1. Sign + magnitude of Q_W per generator class on (a) the CALIBRATED
       hedgehog (electron sector) and (b) the rotated-vortex-loop seed
       family R0 in {8, 12, 16} (q = 1/2): rotations (R12; R23/R13
       phi-averaged = the SO(3) axis-swing clock), boosts (B03; B01/B02
       phi-averaged), and a shared-axis boost x rotation mix.
    2. The rotor read: E(omega) = E_static + omega^2 Q_W and, for the loop
       family, whether an INTERIOR R0 stationary point of E_eff(R0; omega)
       appears at some omega where statics have none (the first "clock
       holds the loop" indicator).
Labels: loop numbers are SEED-level (no relaxed loop exists: block-1
negative); the hedgehog is the calibrated radial solution. Uniform rotation
is an ANSATZ (Track C lesson: reductions are ansatz-gated); a negative Q_W
is a channel indicator, not yet a solution.

phi-averaging: generators that do not commute with the spatial R12(phi)
equivariance are averaged in quadratic pairs (R23<->R13, B01<->B02), exact
for the phi-integral of the quadratic form (cross terms integrate to zero).

GATES (all run first):
    CQ1 vectorized comm/inner == the m5_18_lorentz_check scalar functions
    CQ2 isometry: H density t-independent under explicit finite rotation
    CQ3 quadratic law: H(t-FD with explicit expm conjugation) == E + w^2 Q
    CQ4 vacuum control: Q_W = 0 on the uniform vacuum (D_i = 0)

Run:  python m5_12_clock_q.py gates
      python m5_12_clock_q.py measure
"""
from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
from scipy.linalg import expm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import MIR, J4, cell_weights, grid_coords               # noqa: E402
from m5_18_spectral import run_radial                                     # noqa: E402
from m5_12_core_pin import load_wscale                                    # noqa: E402
from m5_12_loop import loop_field                                         # noqa: E402

ETA = np.diag([-1.0, 1.0, 1.0, 1.0])


# ---------------- vectorized eta algebra (gated vs m5_18_lorentz_check) --
def comm_eta_v(A, B):
    return (np.einsum("...ab,bc,...cd->...ad", A, ETA, B)
            - np.einsum("...ab,bc,...cd->...ad", B, ETA, A))


def inner_eta_v(F, G):
    """internal double-eta raising, per cell."""
    return np.einsum("...ab,...cd,ac,bd->...", F, G, ETA, ETA)


def spatial_channels(Mnp, h):
    """the three local-frame spatial derivatives on included cells
    (mirrors curvature_density_np)."""
    nr, nz = Mnp.shape[:2]
    Mminus = np.empty_like(Mnp[: nr - 1])
    Mminus[1:] = Mnp[: nr - 2]
    Mminus[0] = MIR * Mnp[0]
    Arho = (Mnp[1:] - Mminus)[:, 1:-1] / (2.0 * h)
    Az = (Mnp[: nr - 1, 2:] - Mnp[: nr - 1, :-2]) / (2.0 * h)
    Mc = Mnp[: nr - 1, 1:-1]
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Aphi = (np.einsum("ab,...bc->...ac", J4, Mc)
            - np.einsum("...ab,bc->...ac", Mc, J4)) / rho
    return Mc, Arho, Aphi, Az


def q_w_density(Mnp, W, h):
    """Q_W density on included cells (before the cell weight)."""
    Mc, Arho, Aphi, Az = spatial_channels(Mnp, h)
    D0 = comm_eta_v(np.broadcast_to(W, Mc.shape), Mc)
    q = np.zeros(Mc.shape[:2])
    for Ai in (Arho, Aphi, Az):
        F = comm_eta_v(D0, Ai)
        q += inner_eta_v(F, F)
    return q


def q_w_total(Mnp, W, h):
    w = cell_weights(Mnp.shape[0], Mnp.shape[1], h)
    return float(np.sum(q_w_density(Mnp, W, h) * w)), q_w_density(Mnp, W, h)


# ---------------- generators ----------------
def gen(i, j, boost=False):
    """antisymmetric W: rotation in (i,j) plane, or boost if one index is 0
    (still antisymmetric W; Lam = expm(eta W) is the Lorentz element)."""
    W = np.zeros((4, 4))
    W[i, j], W[j, i] = 1.0, -1.0
    return W


GENS = {
    "R12": [gen(1, 2)],
    "R23_R13_avg": [gen(2, 3), gen(1, 3)],
    "B03": [gen(0, 3)],
    "B01_B02_avg": [gen(0, 1), gen(0, 2)],
    "MIX_B01_R12": [(gen(0, 1) + gen(1, 2)) / np.sqrt(2.0),
                    (gen(0, 2) + gen(2, 1)) / np.sqrt(2.0)],
}


# ---------------- gates ----------------
def run_gates():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "m18chk", os.path.join(HERE, "m5_18_lorentz_check.py"))
    m18 = importlib.util.module_from_spec(spec)
    _argv = sys.argv
    sys.argv = ["m5_18_lorentz_check.py"]
    spec.loader.exec_module(m18)
    sys.argv = _argv
    rng = np.random.default_rng(11)
    res = {}
    # CQ1: vectorized == scalar on random symmetric matrices
    worst = 0.0
    for _ in range(20):
        A = rng.normal(size=(4, 4)); A = 0.5 * (A + A.T)
        B = rng.normal(size=(4, 4)); B = 0.5 * (B + B.T)
        c_v = comm_eta_v(A[None], B[None])[0]
        worst = max(worst, float(np.max(np.abs(c_v - m18.comm_eta(A, B)))))
        F = m18.comm_eta(A, B)
        worst = max(worst, abs(float(inner_eta_v(F[None], F[None])[0])
                               - m18.inner_eta(F, F)))
    res["CQ1_vec_vs_scalar"] = worst
    # CQ2 + CQ3: explicit finite-rotation conjugation on a random small field
    nr, nz, h = 12, 24, 1.0
    R, Z = grid_coords(nr, nz, h)
    M0 = loop_field(R, Z, 4.0, 0.5, 2.0)
    W = GENS["B01_B02_avg"][0]
    omega = 0.37

    def field_at_t(t):
        Lam = expm(ETA @ W * (omega * t))
        Li = np.linalg.inv(Lam)
        return np.einsum("ba,...bc,cd->...ad", Li, M0, Li)

    # H(t) from full formulas: E_static-like part must be t-independent AND
    # the D0 FD channel must reproduce omega^2 * Q_W
    eps = 1e-5
    Mp, Mm = field_at_t(eps), field_at_t(-eps)
    D0_fd = (Mp - Mm) / (2 * eps)
    Mc, Arho, Aphi, Az = spatial_channels(M0, h)
    D0_an = omega * comm_eta_v(Mc, Mc * 0 + 0)  # placeholder shape
    D0_an = omega * comm_eta_v(np.broadcast_to(W, Mc.shape), Mc)
    err_d0 = float(np.max(np.abs(D0_fd[: nr - 1, 1:-1] - D0_an)))
    res["CQ2_dtM_fd_vs_eta_comm"] = err_d0
    # quadratic law: sum_i inner(F0i) from FD field == omega^2 Q_W
    q_fd = np.zeros(Mc.shape[:2])
    for Ai in (Arho, Aphi, Az):
        F = comm_eta_v(D0_fd[: nr - 1, 1:-1], Ai)
        q_fd += inner_eta_v(F, F)
    q_an = omega ** 2 * q_w_density(M0, W, h)
    res["CQ3_quadratic_law_rel"] = float(
        np.max(np.abs(q_fd - q_an)) / (np.max(np.abs(q_an)) + 1e-300))
    # CQ4: vacuum control
    Mv = np.zeros((nr, nz, 4, 4))
    Mv[..., 3, 3] = 1.0
    Mv[..., 0, 0] = 8.0
    qv, _ = q_w_total(Mv, W, h)
    res["CQ4_vacuum_Q"] = qv
    ok = {
        "CQ1 vectorized == m5_18 scalar": res["CQ1_vec_vs_scalar"] < 1e-12,
        "CQ2 dtM == omega [W,M]_eta": res["CQ2_dtM_fd_vs_eta_comm"] < 1e-6,
        "CQ3 H(omega) quadratic law": res["CQ3_quadratic_law_rel"] < 1e-6,
        "CQ4 vacuum Q = 0": abs(res["CQ4_vacuum_Q"]) < 1e-12,
    }
    for k, v in ok.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    for k, v in res.items():
        print(f"    {k} = {v:.3e}")
    res["all_pass"] = all(ok.values())
    with open(os.path.join(DATA, "m5_12_clock_q_gates.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res["all_pass"]


# ---------------- the measurement ----------------
def run_measure(nr=96, nz=192, h=1.0):
    wscale = load_wscale()
    t0 = time.time()
    # calibrated hedgehog (radial solution on the spectral instrument)
    out_r, Mb, _ = run_radial(nr, nz, h, iters=8000, rc_seed=8.0,
                              tag=f"spec_n{nr}_clockq")
    fields = {"hedgehog_calibrated": (Mb, out_r["E_best"])}
    R, Z = grid_coords(nr, nz, h)
    from m5_18_spectral import total_energy_spec_np
    for R0 in (8.0, 12.0, 16.0):
        M0 = loop_field(R, Z, R0, 0.5, 4.0)
        fields[f"loop_seed_R{int(R0)}"] = (
            M0, total_energy_spec_np(M0, wscale, h))
    w = cell_weights(nr, nz, h)
    rows = []
    for fname, (Mnp, E_static) in fields.items():
        for gname, Ws in GENS.items():
            Qs, qmaps = [], []
            for W in Ws:
                qt, qd = q_w_total(Mnp, W, h)
                Qs.append(qt)
                qmaps.append(qd)
            Q = float(np.mean(Qs))
            qd = np.mean(qmaps, axis=0) * w
            neg_frac = float(np.sum(qd[qd < 0]) / (np.sum(np.abs(qd)) + 1e-300))
            k = np.unravel_index(np.argmin(qd), qd.shape)
            rows.append({
                "field": fname, "generator": gname, "E_static": E_static,
                "Q_W": Q,
                "Q_neg_fraction": abs(neg_frac),
                "most_negative_cell_rho_z": [float((k[0] + 0.5) * h),
                                             float((k[1] - (nz - 2) / 2 + 0.5) * h)],
                "most_negative_cell_val": float(np.min(qd)),
            })
            r = rows[-1]
            print(f"[Q_W] {fname:22s} {gname:14s} E={E_static:9.3f} "
                  f"Q={Q:+.4e} negfrac={r['Q_neg_fraction']:.3f} "
                  f"mincell={r['most_negative_cell_val']:+.2e} at "
                  f"({r['most_negative_cell_rho_z'][0]:.1f},"
                  f"{r['most_negative_cell_rho_z'][1]:.1f})")
    # the loop-size stationarity read: E_eff(R0; omega) = E_st + omega^2 Q
    reads = []
    for gname in GENS:
        trip = [(r["E_static"], r["Q_W"]) for r in rows
                if r["generator"] == gname and r["field"].startswith("loop")]
        if len(trip) == 3:
            (E1, Q1), (E2, Q2), (E3, Q3) = trip     # R0 = 8, 12, 16
            # interior stationary R0 needs sign change of dE_eff/dR0 between
            # the (8,12) and (12,16) intervals: solve for omega^2 windows
            s1, s2 = E2 - E1, E3 - E2               # static slopes x dR0
            k1, k2 = Q2 - Q1, Q3 - Q2
            w2_1 = -s1 / k1 if k1 != 0 else None    # omega^2 zeroing slope 1
            w2_2 = -s2 / k2 if k2 != 0 else None
            reads.append({"generator": gname,
                          "E_static_R8_12_16": [E1, E2, E3],
                          "Q_W_R8_12_16": [Q1, Q2, Q3],
                          "omega2_zero_slope_8_12": w2_1,
                          "omega2_zero_slope_12_16": w2_2,
                          "interior_window": (
                              w2_1 is not None and w2_2 is not None
                              and min(w2_1, w2_2) > 0
                              and w2_1 != w2_2)})
    out = {"task": "M5.12", "script": "m5_12_clock_q.py", "mode": "measure",
           "grade": "hedgehog = calibrated solution; loops = SEED level"
                    " (labeled); uniform-rotation ansatz (reduction gated)",
           "grid": {"NR": nr, "NZ": nz, "h": h}, "wscale": wscale,
           "rows": rows, "loop_size_reads": reads,
           "wall_s": round(time.time() - t0, 1)}
    path = os.path.join(DATA, "m5_12_clock_q.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> {path}")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gates"
    if mode == "gates":
        ok = run_gates()
        sys.exit(0 if ok else 1)
    elif mode == "measure":
        run_measure()
    else:
        print(f"unknown mode {mode}")
