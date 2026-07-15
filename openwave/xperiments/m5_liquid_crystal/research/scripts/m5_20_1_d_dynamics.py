"""M5.20.1 phase D: conservative dynamics at (1, delta, 0) (the verdict runs).

The M5.20 instrument (m5_20_a1_dynamics.py: velocity Verlet, split-step
sponge, exact E_abs ledger) re-targeted to the biaxial sector: the spectral
potential targets c_p = 1 + delta^p and the fast gradient generalized
accordingly (gate GF-d re-pins it to the audited einsum path).

THE ASSUMED LAGRANGIAN: unchanged from M5.20 (canonical sigma-model kinetic
term 1/2 ||d_t M||_F^2; Q23 conditionality now SOFTENED by the author:
"in 3D (1, delta, 0) you can start with", 2026-07-12, m5_20_convo.md).

GATES (pre-registered, m5_20_1_task_details.md)
    GF-d   fast gradient == energy_gradient_spec_np(cps) on the biax loop
           seed AND a random symmetric field, delta in {0.1, 0.3, 0.5}
           (rel Frobenius < 1e-12)
    GA1-d  closed-box energy conservation + dt^2 drift scaling at the
           stiffest production point (delta = 0.5, pair_1d)
    GA2-d  sponge budget closure KE + PE + E_abs at delta = 0.5
    GA3-d  pulse test on BOTH phase-A far-field vacua at delta = 0.3: the
           linear-radiation lemma measured per vacuum (the M5.20 audit
           lesson: diag(delta,0,1) carries an A_phi ~ delta channel,
           diag(0,1,delta) an O(1) channel); recorded, drift-checked

RUN MATRIX (plan): 6 core closed-box (delta {0.1, 0.3, 0.5} x pairing
{pair_1d, pair_d0}) + sponge arms on the delta = 0.3 pair (2) + one
recalibrated-w control at delta = 0.3 + the delta = 0 pair_1d back-compat
anchor. T = 2000, dt = 0.02, q = 1/2, R0 = 17, NARROW cores (the M5.20
comparability choices; w = 7.24e-4 fixed except the recal control).

Run:  python m5_20_1_d_dynamics.py gates
      python m5_20_1_d_dynamics.py run <delta> <pairing> <T> <closed|sponge> [tag] [--recal]
Out:  ../data/m5_20_1_run_<tag>.json / _state.npz
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

from m5_17_energy import (cell_weights, curvature_density_np,      # noqa: E402
                          grid_coords, J4, MIR)
from m5_18_spectral import (energy_gradient_spec_np,               # noqa: E402
                            potential_density_spec_np,
                            total_energy_spec_np, ext_tail)
from m5_20_a1_dynamics import evolve, sponge_gamma                 # noqa: E402
from m5_20_1_b_seeds import (cps_of, loop_field_biax,              # noqa: E402
                             winding_measure_biax, core_spectrum,
                             pairing_spec, NARROW)
from m5_19_d1_relax import ring_by_m13                             # noqa: E402
from m5_12_core_pin import load_wscale                             # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
WSCALE = load_wscale()
NR, NZ, H = 128, 256, 1.0
R0, Q = 17.0, 0.5


def _comm_f(A, B):
    return A @ B - B @ A


def grad_fast_biax(Mnp, wscale, h, w4, rho4, cps):
    """m5_20_a1_dynamics.grad_fast with general spectral targets cps
    (gate GF-d pins it to the audited energy_gradient_spec_np)."""
    nr = Mnp.shape[0]
    inv2h = 1.0 / (2.0 * h)
    Mminus = np.empty_like(Mnp[: nr - 1])
    Mminus[1:] = Mnp[: nr - 2]
    Mminus[0] = MIR * Mnp[0]
    Arho = (Mnp[1:] - Mminus)[:, 1:-1] * inv2h
    Az = (Mnp[: nr - 1, 2:] - Mnp[: nr - 1, :-2]) * inv2h
    Mc = Mnp[: nr - 1, 1:-1]
    Jb = np.broadcast_to(J4, Mc.shape)
    Aphi = _comm_f(Jb, Mc) / rho4
    C1 = _comm_f(Arho, Aphi)
    C2 = _comm_f(Arho, Az)
    C3 = _comm_f(Aphi, Az)
    k = 4.0 * w4
    Grho = 2.0 * k * (_comm_f(C1, Aphi) + _comm_f(C2, Az))
    Gphi = 2.0 * k * (-_comm_f(C1, Arho) + _comm_f(C3, Az))
    Gz = 2.0 * k * (-_comm_f(C2, Arho) - _comm_f(C3, Aphi))
    G = np.zeros_like(Mnp)
    G[1:, 1:-1] += Grho * inv2h
    G[: nr - 2, 1:-1] -= Grho[1:] * inv2h
    G[0, 1:-1] -= (MIR * Grho[0]) * inv2h
    G[: nr - 1, 2:] += Gz * inv2h
    G[: nr - 1, :-2] -= Gz * inv2h
    Gphi_r = Gphi / rho4
    G[: nr - 1, 1:-1] += -_comm_f(np.broadcast_to(J4, Gphi_r.shape), Gphi_r)
    msp = Mc[..., 1:4, 1:4]
    m2 = msp @ msp
    tr1 = np.einsum("...aa->...", msp)[..., None, None]
    tr2 = np.einsum("...aa->...", m2)[..., None, None]
    tr3 = np.einsum("...aa->...", m2 @ msp)[..., None, None]
    eye = np.broadcast_to(np.eye(3), msp.shape)
    dsp = wscale * (2.0 * (tr1 - cps[0]) * eye + 4.0 * (tr2 - cps[1]) * msp
                    + 6.0 * (tr3 - cps[2]) * m2)
    G[: nr - 1, 1:-1, 1:4, 1:4] += dsp * w4
    return G


def make_egf_biax(delta, wscale=WSCALE):
    cps = cps_of(delta)
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]

    def e_fn(MM):
        return total_energy_spec_np(MM, wscale, H, cps)

    def g_fn(MM):
        return grad_fast_biax(MM, wscale, H, w4, rho4, cps)
    return e_fn, g_fn


def seed_biax(delta, pairing):
    R, Z = grid_coords(NR, NZ, H)
    return loop_field_biax(R, Z, R0, Q, delta, pairing)


def recal_wscale(delta, pairing):
    """the seed virial-balance w (M5.16 autochi protocol) on the biax loop
    seed: the ONE recalibrated control bounding the wscale-scheme
    dependence."""
    M0 = seed_biax(delta, pairing)
    w = cell_weights(NR, NZ, H)
    Ecurv = float(np.sum(curvature_density_np(M0, H, 1.0) * w)) + ext_tail(
        (NR - 1) * H, (NZ / 2 - 1) * H)
    Epot1 = float(np.sum(potential_density_spec_np(M0, 1.0, cps_of(delta))
                         * w))
    return Ecurv / (3.0 * Epot1) if Epot1 > 0 else WSCALE


def make_snap_biax(delta, wscale=WSCALE):
    cps = cps_of(delta)
    w = cell_weights(NR, NZ, H)
    R, Z = grid_coords(NR, NZ, H)
    Rin, Zin = R[: NR - 1, 1:-1], Z[: NR - 1, 1:-1]

    def snap_fn(Mx, v):
        rd = ring_by_m13(Mx, NR, NZ, H)
        out = {"ring13_rho": rd["ring13_rho"], "ring13_z": rd["ring13_z"],
               "m13_max": rd["m13_max"]}
        qm, mix = winding_measure_biax(Mx, NR, NZ, H, rd["ring13_rho"],
                                       rd["ring13_z"])
        out["q_meas"], out["mix"] = qm, mix
        cs = core_spectrum(Mx, NR, NZ, H, rd["ring13_rho"], rd["ring13_z"])
        out["core_lam"] = cs["lam"]
        out["core_gap_top"], out["core_gap_bot"] = (cs["gap_top"],
                                                    cs["gap_bot"])
        out["core_equalized"] = cs["equalized"]
        dens = (curvature_density_np(Mx, H, 1.0)
                + potential_density_spec_np(Mx, wscale, cps)) * w
        if np.isfinite(rd["ring13_rho"]):
            din = np.sqrt((Rin - rd["ring13_rho"]) ** 2
                          + (Zin - rd["ring13_z"]) ** 2) < 8.0
            out["PE_in8"] = float(np.sum(dens[din]))
        else:
            out["PE_in8"] = float("nan")
        return out
    return snap_fn


# ---------------- gates ----------------
def gate_gf():
    out = {}
    rng = np.random.default_rng(7)
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
    Mr = rng.normal(size=(NR, NZ, 4, 4))
    Mr = 0.5 * (Mr + np.swapaxes(Mr, -1, -2))
    for delta in (0.1, 0.3, 0.5):
        cps = cps_of(delta)
        for name, MM in [("seed_1d", seed_biax(delta, "pair_1d")),
                         ("seed_d0", seed_biax(delta, "pair_d0")),
                         ("random", Mr)]:
            Ga = energy_gradient_spec_np(MM, WSCALE, H, cps)
            Gf = grad_fast_biax(MM, WSCALE, H, w4, rho4, cps)
            rel = float(np.sqrt(np.sum((Ga - Gf) ** 2)
                                / max(np.sum(Ga ** 2), 1e-300)))
            out[f"d{delta}_{name}"] = rel
    ok = all(v < 1e-12 for v in out.values())
    return ok, out


def gate_ga1(delta=0.5, pairing="pair_1d", T=20.0, dts=(0.04, 0.02, 0.01)):
    M0 = seed_biax(delta, pairing)
    egf = make_egf_biax(delta)
    res = {}
    for dt in dts:
        _, _, recs, wall = evolve(M0, egf, T, dt, snap_every=10 ** 9)
        E0, E1 = recs[0]["E_tot"], recs[-1]["E_tot"]
        res[str(dt)] = {"drift_rel": abs(E1 - E0) / abs(E0),
                        "wall_s": wall, "finite": bool(np.isfinite(E1))}
    ds = [res[str(d)]["drift_rel"] for d in dts]
    ratios = [ds[i] / max(ds[i + 1], 1e-300) for i in range(len(ds) - 1)]
    ok = (res[str(dts[1])]["drift_rel"] < 1e-4
          and all(np.isfinite(list(r["drift_rel"] for r in res.values())))
          and all(2.0 < r < 8.0 for r in ratios))
    return ok, {"per_dt": res, "ratios": ratios}


def gate_ga2(delta=0.5, pairing="pair_1d", T=20.0, dt=0.02):
    M0 = seed_biax(delta, pairing)
    egf = make_egf_biax(delta)
    gam = sponge_gamma(NR, NZ, H)
    _, _, recs, _ = evolve(M0, egf, T, dt, gamma=gam, snap_every=10 ** 9)
    E0, E1 = recs[0]["E_tot"], recs[-1]["E_tot"]
    drift = abs(E1 - E0) / abs(E0)
    return drift < 1e-3, {"budget_drift_rel": drift,
                          "E_abs_final": recs[-1]["E_abs"]}


def gate_ga3(delta=0.3, T=60.0, dt=0.02, amp=0.02, sig=3.0):
    """pulse test on BOTH phase-A vacua: the per-vacuum linear-radiation
    channel measured (spread growth of a small M11 bump); pass = finite +
    drift-clean; the channel strengths are RESULTS, not pass criteria."""
    R, Z = grid_coords(NR, NZ, H)
    w = cell_weights(NR, NZ, H)
    Rin, Zin = R[: NR - 1, 1:-1], Z[: NR - 1, 1:-1]
    cps = cps_of(delta)
    egf = make_egf_biax(delta)
    out = {}
    for pairing in ("pair_1d", "pair_d0"):
        Me = pairing_spec(delta, pairing)["Me"]
        Mv = np.zeros(R.shape + (4, 4))
        Mv[..., 1, 1], Mv[..., 2, 2], Mv[..., 3, 3] = Me
        Mv[..., 0, 0] = 8.0
        M0 = Mv.copy()
        M0[..., 1, 1] += amp * np.exp(-((R - 40.0) ** 2 + Z ** 2)
                                      / (2 * sig ** 2))

        def spread_fn(Mx, v):
            dens = (curvature_density_np(Mx, H, 1.0)
                    + potential_density_spec_np(Mx, WSCALE, cps)) * w
            dens = dens + 0.5 * np.sum(v[: NR - 1, 1:-1] ** 2,
                                       axis=(-2, -1)) * w
            tot = float(np.sum(dens))
            if tot <= 0:
                return {"r2": float("nan")}
            r2 = float(np.sum(dens * ((Rin - 40.0) ** 2 + Zin ** 2)) / tot)
            return {"r2": r2}

        _, _, recs, wall = evolve(M0, egf, T, dt, snap_every=int(10 / dt),
                                  snap_fn=spread_fn)
        r2 = [r["r2"] for r in recs]
        growth = float(np.sqrt(max(r2[-1], 0.0)) - np.sqrt(max(r2[0], 0.0)))
        out[pairing] = {"vacuum_rho_phi_z": list(Me),
                        "spread_growth_cells": growth,
                        "drift_rel": abs(recs[-1]["E_tot"] - recs[0]["E_tot"])
                        / abs(recs[0]["E_tot"]), "wall_s": wall}
    ok = all(np.isfinite(v["spread_growth_cells"])
             and v["drift_rel"] < 1e-3 for v in out.values())
    return ok, out


def run_gates():
    t0 = time.time()
    results = {}
    for name, fn in [("GF", gate_gf), ("GA1", gate_ga1), ("GA2", gate_ga2),
                     ("GA3", gate_ga3)]:
        ok, detail = fn()
        results[name] = {"ok": bool(ok), "detail": detail}
        print(f"[{name}] {'PASS' if ok else 'FAIL'} "
              + json.dumps(detail, default=float)[:300])
    results["wall_s"] = round(time.time() - t0, 1)
    with open(os.path.join(DATA, "m5_20_1_d_gates.json"), "w") as f:
        json.dump(results, f, indent=1, default=float)
    print(json.dumps({k: v["ok"] for k, v in results.items()
                      if isinstance(v, dict)}, indent=1))
    return results


# ---------------- production ----------------
def run_case(delta, pairing, T, mode, dt=0.02, tag=None, recal=False):
    wsc = recal_wscale(delta, pairing) if recal else WSCALE
    name = tag or (f"d{str(delta).replace('.', 'p')}_{pairing}_{mode}"
                   + ("_recal" if recal else ""))
    M0 = seed_biax(delta, pairing)
    egf = make_egf_biax(delta, wsc)
    gam = sponge_gamma(NR, NZ, H) if mode == "sponge" else None
    snap_fn = make_snap_biax(delta, wsc)
    E0 = total_energy_spec_np(M0, wsc, H, cps_of(delta))
    print(f"[{name}] T={T} dt={dt} wscale={wsc:.4e} E0={E0:.3f}", flush=True)
    Mx, v, recs, wall = evolve(M0, egf, T, dt, gamma=gam,
                               snap_every=int(round(max(T / 80, dt) / dt)),
                               snap_fn=snap_fn, log_snaps=True)
    out = {"task": "M5.20.1", "delta": delta, "pairing": pairing,
           "mode": mode, "recal": bool(recal), "T": T, "dt": dt,
           "grid": {"NR": NR, "NZ": NZ, "h": H}, "wscale": wsc,
           "R0": R0, "q": Q, "trajectory": recs, "wall_s": round(wall, 1)}
    with open(os.path.join(DATA, f"m5_20_1_run_{name}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    np.savez_compressed(os.path.join(DATA, f"m5_20_1_run_{name}_state.npz"),
                        M0=Mx.astype(np.float32), v0=v.astype(np.float32))
    r0, r1 = recs[0], recs[-1]
    print(f"[{name}] done t={r1['t']:.0f}: PE {r0['PE']:.2f}->{r1['PE']:.2f} "
          f"q {r0['q_meas']:.2f}->{(r1['q_meas'] if r1['q_meas'] == r1['q_meas'] else float('nan')):.2f} "
          f"core_eq {r0['core_equalized']}->{r1['core_equalized']} "
          f"wall {wall:.0f}s", flush=True)
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gates"
    if mode == "gates":
        run_gates()
    elif mode == "run":
        delta, pairing, T, boxmode = (float(ARGV[1]), ARGV[2],
                                      float(ARGV[3]), ARGV[4])
        tag = None
        recal = "--recal" in ARGV
        rest = [a for a in ARGV[5:] if not a.startswith("--")]
        if rest:
            tag = rest[0]
        run_case(delta, pairing, T, boxmode, tag=tag, recal=recal)
    else:
        raise SystemExit(f"unknown mode {mode}")
