"""M5.20 phase A: conservative dynamics on the M5.19 axisym statics stack.

Duda's 2026-07-10 directive (reply to the M5.19 batch): "instead of just
energy minimization, there is required real evolution e.g. with
Euler-Lagrange equations for the assumed Lagrangian, searching if there is
a way to radiate this energy as some different field excitations".

THE ASSUMED LAGRANGIAN (the flagged Q23 assumption)
    L = INT 2 pi rho drho dz [ (1/2) ||d_t M||_F^2 - u_curv - V_spec ]
    kinetic: the canonical sigma-model choice (Q23: his Gamma-variable
    Hamiltonian structure is NOT derived here; this is the minimal
    completion of the sanctioned static functional).
    Discrete EOM (variational, mass matrix = the cell weights w):
        w d_t^2 M = -dE/dM        =>   d_t^2 M = -(1/w) G,
    the SAME preconditioned gradient FIRE uses (statics comparability).

INTEGRATOR
    velocity Verlet (symplectic, time-reversible), pinned cells frozen.
    Sponge (radiation absorber): operator splitting; after each
    conservative step, v *= exp(-gamma dt) inside the absorbing layer and
    the KE removed is accumulated EXACTLY into E_abs, so
        KE + PE + E_abs = const   up to the conservative-step drift (GA1).

VARIANTS (the Q20 control)
    comm : the sanctioned functional (commutator curvature + spectral V).
           Linearization around a uniform vacuum M0 (AUDIT-CORRECTED
           2026-07-11): the Cartesian channels give [du, du] = O(u^2), but
           the equivariant azimuthal channel carries the BACKGROUND gradient
           A_phi = [J, M0]/rho, so [A_pert, A_phi_bg] is LINEAR in u.
           => on J-COMMUTING vacua ([J, M0] = 0, e.g. e3e3^T): no spatial
           coupling at quadratic order, flat dispersion, no linear radiation
           (measured: e3 pulse spread 1.3e-6 cells over T = 60);
           => on e2e2^T (the M5.19 escaped far field): a linear channel
           EXISTS with stiffness ~ 1/rho^2 (measured eps^2 scaling; e2
           pulse spread +0.49 cells: weak, decaying, but nonzero).
    dir  : + c1 * ( ||M_rho||^2 + ||M_phi||^2 + ||M_z||^2 ), c1 = 0.5
           => linear waves at speed sqrt(2 c1) = 1 (+ the V mass gap):
           restores a propagating channel; the Q20-insensitive control.

Run:  python m5_20_a1_dynamics.py gates
      python m5_20_a1_dynamics.py pulse
      python m5_20_a1_dynamics.py run <case> <variant> <T> <closed|sponge> [tag]
Cases: melt_q10_R13 (his physical class), melt_q05_R17, escape_q05_R18.

Outputs: ../data/m5_20_*.json / _state.npz, plots by the driver.
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

from m5_17_energy import cell_weights, grid_coords, J4                # noqa: E402
from m5_16_axisym import pin_mask                                     # noqa: E402
from m5_18_spectral import (energy_gradient_spec_np,                  # noqa: E402
                            total_energy_spec_np,
                            potential_density_spec_np)
from m5_17_energy import curvature_density_np, _comm_np               # noqa: E402
from m5_12_core_pin import load_wscale                                # noqa: E402
from m5_19_c1_loop import CLASSES, NARROW, loop_field_escaped         # noqa: E402
from m5_19_d1_relax import ring_by_m13, winding_measure               # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
WSCALE = load_wscale()
NR, NZ, H = 128, 256, 1.0
C1_DIR = 0.5                       # Dirichlet stiffness: linear speed sqrt(2 c1) = 1

CASES = {
    "melt_q10_R13": {"cls": "melt", "q": 1.0, "R0": 13.0},   # audit-corrected R*
    "melt_q05_R17": {"cls": "melt", "q": 0.5, "R0": 17.0},
    "escape_q05_R18": {"cls": "escape", "q": 0.5, "R0": 18.0},
}


# ---------------- fast gradient (batched matmul; gate GF pins it to the
# audited energy_gradient_spec_np at < 1e-12 rel) ----------------
def _comm_f(A, B):
    return A @ B - B @ A


def grad_fast(Mnp, wscale, h, w4, rho4):
    """energy_gradient_spec_np, matmul fast path. w4 = cell_weights[...,None,
    None], rho4 = included-cell rho column; both precomputed by the caller."""
    from m5_17_energy import MIR
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
    # spectral potential dV (cps = delta-0 targets (1,1,1))
    msp = Mc[..., 1:4, 1:4]
    m2 = msp @ msp
    tr1 = np.einsum("...aa->...", msp)[..., None, None]
    tr2 = np.einsum("...aa->...", m2)[..., None, None]
    tr3 = np.einsum("...aa->...", m2 @ msp)[..., None, None]
    eye = np.broadcast_to(np.eye(3), msp.shape)
    dsp = wscale * (2.0 * (tr1 - 1.0) * eye + 4.0 * (tr2 - 1.0) * msp
                    + 6.0 * (tr3 - 1.0) * m2)
    G[: nr - 1, 1:-1, 1:4, 1:4] += dsp * w4
    return G


def gate_gf():
    """the fast gradient IS the audited gradient: rel Frobenius diff < 1e-12
    on the loop seed AND on a random symmetric field."""
    w4 = cell_weights(NR, NZ, H)[..., None, None]
    rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]
    out = {}
    rng = np.random.default_rng(7)
    Mr = rng.normal(size=(NR, NZ, 4, 4))
    Mr = 0.5 * (Mr + np.swapaxes(Mr, -1, -2))
    for name, MM in [("seed", seed_of("melt_q05_R17")), ("random", Mr)]:
        Ga = energy_gradient_spec_np(MM, WSCALE, H)
        Gf = grad_fast(MM, WSCALE, H, w4, rho4)
        rel = float(np.sqrt(np.sum((Ga - Gf) ** 2) / max(np.sum(Ga ** 2), 1e-300)))
        out[name] = rel
    return all(v < 1e-12 for v in out.values()), out


# ---------------- Dirichlet control term (variant "dir") ----------------
def _channels(Mnp, h):
    """the three axisym derivative channels on included cells (the
    curvature_density_np stencils, verbatim)."""
    nr = Mnp.shape[0]
    Mminus = np.empty_like(Mnp[: nr - 1])
    Mminus[1:] = Mnp[: nr - 2]
    from m5_17_energy import MIR
    Mminus[0] = MIR * Mnp[0]
    Mrho = ((Mnp[1:] - Mminus) / (2.0 * h))[:, 1:-1]
    Mz = (Mnp[: nr - 1, 2:] - Mnp[: nr - 1, :-2]) / (2.0 * h)
    Mc = Mnp[: nr - 1, 1:-1]
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Mphi = _comm_np(np.broadcast_to(J4, Mc.shape), Mc) / rho
    return Mrho, Mphi, Mz, rho


def dir_density_np(Mnp, h, c1=C1_DIR):
    Mrho, Mphi, Mz, _ = _channels(Mnp, h)
    return c1 * (np.sum(Mrho * Mrho, axis=(-2, -1))
                 + np.sum(Mphi * Mphi, axis=(-2, -1))
                 + np.sum(Mz * Mz, axis=(-2, -1)))


def dir_gradient_np(Mnp, h, c1=C1_DIR):
    """adjoints of the Dirichlet term through the same stencils as
    energy_gradient_np (scatter pattern mirrored verbatim)."""
    from m5_17_energy import MIR
    nr, nz = Mnp.shape[:2]
    inv2h = 1.0 / (2.0 * h)
    Mrho, Mphi, Mz, rho = _channels(Mnp, h)
    w = cell_weights(nr, nz, h)[..., None, None]
    Grho = 2.0 * c1 * w * Mrho
    Gphi = 2.0 * c1 * w * Mphi
    Gz = 2.0 * c1 * w * Mz
    G = np.zeros_like(Mnp)
    G[1:, 1:-1] += Grho * inv2h
    G[: nr - 2, 1:-1] -= Grho[1:] * inv2h
    G[0, 1:-1] -= (MIR * Grho[0]) * inv2h
    G[: nr - 1, 2:] += Gz * inv2h
    G[: nr - 1, :-2] -= Gz * inv2h
    Gphi_r = Gphi / rho
    G[: nr - 1, 1:-1] += -_comm_np(np.broadcast_to(J4, Gphi_r.shape), Gphi_r)
    return G


def make_egf(variant):
    """returns (e_fn, g_fn): energy and gradient SEPARATELY (the integrator
    needs only g_fn per step; e_fn runs at snapshots)."""
    if variant == "comm":
        w4 = cell_weights(NR, NZ, H)[..., None, None]
        rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]

        def e_fn(MM):
            return total_energy_spec_np(MM, WSCALE, H)

        def g_fn(MM):
            return grad_fast(MM, WSCALE, H, w4, rho4)
    elif variant == "dir":
        w = cell_weights(NR, NZ, H)
        w4 = w[..., None, None]
        rho4 = ((np.arange(NR - 1) + 0.5) * H)[:, None, None, None]

        def e_fn(MM):
            return total_energy_spec_np(MM, WSCALE, H) + float(
                np.sum(dir_density_np(MM, H) * w))

        def g_fn(MM):
            return grad_fast(MM, WSCALE, H, w4, rho4) + dir_gradient_np(MM, H)
    else:
        raise ValueError(variant)
    return e_fn, g_fn


# ---------------- sponge ----------------
def sponge_gamma(nr, nz, h, width=16.0, gmax=0.5):
    """damping profile: quadratic ramp inside `width` of the outer rho face
    and both z faces (zero elsewhere; the pinned faces sit at its far edge)."""
    R, Z = grid_coords(nr, nz, h)
    rho_max = (nr - 1) * h
    z_max = (nz / 2 - 1) * h
    d_rho = np.clip((R - (rho_max - width)) / width, 0.0, 1.0)
    d_z = np.clip((np.abs(Z) - (z_max - width)) / width, 0.0, 1.0)
    return gmax * np.maximum(d_rho, d_z) ** 2


# ---------------- the integrator ----------------
def evolve(M0, efg, T, dt, gamma=None, snap_every=None, snap_fn=None,
           v0=None, nan_abort=True, log_snaps=False, extra_pin=None):
    """velocity Verlet with optional split-step sponge. efg = (e_fn, g_fn);
    only g_fn runs per step, e_fn at snapshots. Returns (M, v, recs, wall).
    Energy ledger per snapshot: PE (e_fn), KE = 1/2 sum wfull ||v||^2,
    E_abs = cumulative KE removed by the sponge (exact bookkeeping)."""
    e_fn, g_fn = efg
    pin = pin_mask(NR, NZ)
    if extra_pin is not None:
        pin = pin | extra_pin
    free4 = (~pin)[..., None, None].astype(float)
    w = cell_weights(NR, NZ, H)
    wfull = np.ones((NR, NZ))
    wfull[: NR - 1, 1:-1] = w
    wfull4 = wfull[..., None, None]
    precond = 1.0 / wfull4
    damp = None
    if gamma is not None:
        damp = np.exp(-gamma * dt)[..., None, None]
    Mx = M0.copy()
    v = np.zeros_like(Mx) if v0 is None else v0.copy()
    a = -g_fn(Mx) * precond * free4
    E_abs = 0.0
    n_steps = int(round(T / dt))
    if snap_every is None:
        snap_every = max(1, n_steps // 40)
    recs = []

    def ke_of(vv):
        return 0.5 * float(np.sum(wfull4 * vv * vv))

    def snap(it):
        r = {"it": it, "t": it * dt, "PE": e_fn(Mx), "KE": ke_of(v),
             "E_abs": E_abs}
        r["E_tot"] = r["PE"] + r["KE"] + r["E_abs"]
        if snap_fn is not None:
            r.update(snap_fn(Mx, v))
        recs.append(r)
        if log_snaps:
            print(f"  it {it:7d} t {r['t']:8.1f} PE {r['PE']:9.3f} "
                  f"KE {r['KE']:9.3f} abs {r['E_abs']:8.3f} "
                  f"tot {r['E_tot']:9.3f}"
                  + (f" q {r.get('q_meas', float('nan')):.3f}"
                     f" rho {r.get('ring13_rho', float('nan')):.1f}"
                     if snap_fn else ""), flush=True)
        return r

    snap(0)
    t0 = time.time()
    for it in range(1, n_steps + 1):
        v += 0.5 * dt * a
        Mx += dt * v
        a = -g_fn(Mx) * precond * free4
        v += 0.5 * dt * a
        if damp is not None:
            ke_b = ke_of(v)
            v *= damp
            E_abs += ke_b - ke_of(v)
        if it % snap_every == 0 or it == n_steps:
            r = snap(it)
            if nan_abort and not np.isfinite(r["E_tot"]):
                print(f"  [abort] non-finite at it {it}", flush=True)
                break
    wall = time.time() - t0
    return Mx, v, recs, wall


# ---------------- diagnostics ----------------
def loop_snap_fn(Mx, v):
    rd = ring_by_m13(Mx, NR, NZ, H)
    out = {"ring13_rho": rd["ring13_rho"], "ring13_z": rd["ring13_z"],
           "m13_max": rd["m13_max"]}
    out["q_meas"] = winding_measure(Mx, NR, NZ, H, rd["ring13_rho"],
                                    rd["ring13_z"])
    # energy split: disk r<8 around the ring centroid vs the rest
    w = cell_weights(NR, NZ, H)
    dens = (curvature_density_np(Mx, H, 1.0)
            + potential_density_spec_np(Mx, WSCALE)) * w
    R, Z = grid_coords(NR, NZ, H)
    Rin, Zin = R[: NR - 1, 1:-1], Z[: NR - 1, 1:-1]
    if np.isfinite(rd["ring13_rho"]):
        din = np.sqrt((Rin - rd["ring13_rho"]) ** 2
                      + (Zin - rd["ring13_z"]) ** 2) < 8.0
        out["PE_in8"] = float(np.sum(dens[din]))
    else:
        out["PE_in8"] = float("nan")
    return out


def loop_field_escaped_z(R, Z, R0, q, mu0, nu0, ws, wm, w3, shape,
                         dcut_fac=2.5, wcut_fac=1.0):
    """the Z-ESCAPED loop: as m5_19_c1_loop.loop_field_escaped but blended to
    e3 e3^T (director escaped to the z axis). e3 e3^T is an exact vacuum of
    BOTH variants: spectrum (1, 0, 0) so V = 0, all comm channels vanish, AND
    [J, e3 e3^T] = 0 so the Dirichlet azimuthal channel is zero too (e2 e2^T
    is NOT a dir vacuum: the equivariant azimuthal texture carries real 3D
    Frank energy 2 c1/rho^2 the commutator never charges). The dir-arm seed."""
    from m5_19_c1_loop import loop_field_tensor
    M = loop_field_tensor(R, Z, R0, q, mu0, nu0, ws, wm, w3, shape)
    dd = np.sqrt((R - R0) ** 2 + Z ** 2)
    dcut, wcut = dcut_fac * ws, wcut_fac * ws
    x = np.clip((dd - dcut) / wcut, 0.0, 1.0)
    beta = (x * x * (3 - 2 * x))[..., None, None]
    Me = np.zeros_like(M)
    Me[..., 3, 3] = 1.0
    out = (1 - beta) * M + beta * Me
    out[..., 0, 0] = M[..., 0, 0]
    return out


def seed_of(case):
    zfar = case.endswith("_z")
    spec = CASES[case[:-2]] if zfar else CASES[case]
    ctr = CLASSES[spec["cls"]]
    R, Z = grid_coords(NR, NZ, H)
    fn = loop_field_escaped_z if zfar else loop_field_escaped
    return fn(R, Z, spec["R0"], spec["q"], ctr["mu0"],
              ctr["nu0"], NARROW["ws"], NARROW["wm"],
              NARROW["w3"], ctr["shape"])


# ---------------- gates ----------------
def gate_ga0():
    """seed energies reproduce the M5.19 phase-D t=0 values (same stack)."""
    out = {}
    ref = {"melt_q05_R17": "m5_19_d1_melt_q05_R17.json",
           "escape_q05_R18": "m5_19_d1_escape_q05_R18.json"}
    for case, fn in ref.items():
        path = os.path.join(DATA, fn)
        with open(path) as f:
            E_ref = json.load(f)["trajectory"][0]["E"]
        E_now = total_energy_spec_np(seed_of(case), WSCALE, H)
        out[case] = {"E_ref": E_ref, "E_now": E_now,
                     "rel": abs(E_now - E_ref) / abs(E_ref)}
    ok = all(v["rel"] < 1e-12 for v in out.values())
    return ok, out


def gate_ga1(case="melt_q05_R17", T=20.0, dts=(0.04, 0.02, 0.01)):
    """closed-box energy conservation + dt^2 drift scaling."""
    M0 = seed_of(case)
    egf = make_egf("comm")
    res = {}
    for dt in dts:
        _, _, recs, wall = evolve(M0, egf, T, dt, snap_every=10 ** 9)
        E0, E1 = recs[0]["E_tot"], recs[-1]["E_tot"]
        res[str(dt)] = {"drift_rel": abs(E1 - E0) / abs(E0), "wall_s": wall,
                        "finite": bool(np.isfinite(E1))}
    ds = [res[str(d)]["drift_rel"] for d in dts]
    ratios = [ds[i] / max(ds[i + 1], 1e-300) for i in range(len(ds) - 1)]
    ok = (res[str(dts[1])]["drift_rel"] < 1e-4
          and all(np.isfinite(list(r["drift_rel"] for r in res.values())))
          and all(2.0 < r < 8.0 for r in ratios))
    return ok, {"per_dt": res, "ratios": ratios}


def gate_ga2(case="melt_q05_R17", T=20.0, dt=0.02):
    """sponge budget closure: KE+PE+E_abs conserved to the GA1 drift level."""
    M0 = seed_of(case)
    egf = make_egf("comm")
    gam = sponge_gamma(NR, NZ, H)
    _, _, recs, _ = evolve(M0, egf, T, dt, gamma=gam, snap_every=10 ** 9)
    E0, E1 = recs[0]["E_tot"], recs[-1]["E_tot"]
    drift = abs(E1 - E0) / abs(E0)
    return drift < 1e-3, {"budget_drift_rel": drift,
                          "E_abs_final": recs[-1]["E_abs"]}


def gate_ga3(T=60.0, dt=0.02, amp=0.02, sig=3.0, vac_axis=2):
    """A2 pulse test: a small M11 bump on a uniform uniaxial vacuum. comm:
    the energy cloud must NOT spread ballistically (flat linear dispersion);
    dir: it must (speed ~ sqrt(2 c1) = 1). Metric: energy-weighted radial
    second moment about the bump center vs t. vac_axis 2 = e2e2^T (a comm
    vacuum but NOT a dir vacuum: background azimuthal Frank energy);
    vac_axis 3 = e3e3^T (an exact vacuum of BOTH variants: the clean run)."""
    R, Z = grid_coords(NR, NZ, H)
    Mv = np.zeros(R.shape + (4, 4))
    Mv[..., vac_axis, vac_axis] = 1.0
    bump = amp * np.exp(-((R - 40.0) ** 2 + Z ** 2) / (2 * sig ** 2))
    M0 = Mv.copy()
    M0[..., 1, 1] += bump
    w = cell_weights(NR, NZ, H)
    Rin, Zin = R[: NR - 1, 1:-1], Z[: NR - 1, 1:-1]

    def spread_fn(Mx, v):
        wfull4 = np.ones((NR, NZ, 1, 1))
        wfull4[: NR - 1, 1:-1, 0, 0] = w
        dens = (curvature_density_np(Mx, H, 1.0)
                + potential_density_spec_np(Mx, WSCALE)) * w
        dens = dens + 0.5 * np.sum(v[: NR - 1, 1:-1] ** 2, axis=(-2, -1)) * w
        tot = float(np.sum(dens))
        if tot <= 0:
            return {"r2": float("nan")}
        r2 = float(np.sum(dens * ((Rin - 40.0) ** 2 + Zin ** 2)) / tot)
        return {"r2": r2, "Edens_tot": tot}

    out = {}
    for variant in ("comm", "dir"):
        egf = make_egf(variant)
        _, _, recs, wall = evolve(M0, egf, T, dt, snap_every=int(10 / dt),
                                  snap_fn=spread_fn)
        out[variant] = {"t": [r["t"] for r in recs],
                        "r2": [r["r2"] for r in recs],
                        "drift_rel": abs(recs[-1]["E_tot"] - recs[0]["E_tot"])
                        / abs(recs[0]["E_tot"]), "wall_s": wall}
    # verdicts: rms spread growth over the window
    def growth(v):
        r2 = out[v]["r2"]
        return np.sqrt(max(r2[-1], 0.0)) - np.sqrt(max(r2[0], 0.0))
    g_comm, g_dir = growth("comm"), growth("dir")
    # dir should spread by ~T * speed-ish (ballistic, order tens); comm should
    # stay put (< a few cells over the whole window)
    ok = (g_comm < 5.0) and (g_dir > 3.0 * max(g_comm, 1.0))
    return ok, {"spread_growth_comm": g_comm, "spread_growth_dir": g_dir,
                "detail": out}


def run_gates():
    t0 = time.time()
    results = {}
    for name, fn in [("GF", gate_gf), ("GA0", gate_ga0), ("GA1", gate_ga1),
                     ("GA2", gate_ga2), ("GA3", gate_ga3)]:
        ok, detail = fn()
        results[name] = {"ok": bool(ok), "detail": detail}
        print(f"[{name}] {'PASS' if ok else 'FAIL'}")
    results["wall_s"] = round(time.time() - t0, 1)
    with open(os.path.join(DATA, "m5_20_a1_gates.json"), "w") as f:
        json.dump(results, f, indent=1, default=float)
    print(json.dumps({k: v["ok"] for k, v in results.items()
                      if isinstance(v, dict)}, indent=1))
    return results


# ---------------- production runs ----------------
def run_case(case, variant, T, mode, dt=0.02, tag=None, state_file=None):
    """case: a CASES key, or (with state_file) a label; state_file: seed from
    a saved _state.npz (M0 key; e.g. the M5.19 corepin quasi-minimizer,
    released here under conservative dynamics: the gentle-start protection
    control) instead of the analytic ansatz."""
    name = tag or f"{case}_{variant}_{mode}"
    if state_file:
        M0 = np.load(os.path.join(DATA, state_file))["M0"].astype(np.float64)
    else:
        M0 = seed_of(case)
    egf = make_egf(variant)
    gam = sponge_gamma(NR, NZ, H) if mode == "sponge" else None
    print(f"[{name}] T={T} dt={dt} E0={total_energy_spec_np(M0, WSCALE, H):.3f}")
    Mx, v, recs, wall = evolve(M0, egf, T, dt, gamma=gam,
                               snap_every=int(round(max(T / 80, dt) / dt)),
                               snap_fn=loop_snap_fn, log_snaps=True)
    out = {"task": "M5.20", "case": case, "variant": variant, "mode": mode,
           "T": T, "dt": dt, "grid": {"NR": NR, "NZ": NZ, "h": H},
           "wscale": WSCALE, "c1_dir": C1_DIR if variant == "dir" else 0.0,
           "trajectory": recs, "wall_s": round(wall, 1)}
    with open(os.path.join(DATA, f"m5_20_{name}.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    np.savez_compressed(os.path.join(DATA, f"m5_20_{name}_state.npz"),
                        M0=Mx.astype(np.float32), v0=v.astype(np.float32))
    r0, r1 = recs[0], recs[-1]
    print(f"[{name}] done t={r1['t']:.0f}: PE {r0['PE']:.2f}->{r1['PE']:.2f} "
          f"KE {r1['KE']:.2f} E_abs {r1['E_abs']:.3f} "
          f"E_tot drift {(r1['E_tot'] - r0['E_tot']) / r0['E_tot']:.2e} "
          f"q {r0['q_meas']:.2f}->{r1['q_meas']:.2f} wall {wall:.0f}s")
    return out


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gates"
    if mode == "gates":
        run_gates()
    elif mode == "pulse":
        ok, detail = gate_ga3()
        print(json.dumps({"ok": ok, "spread_comm": detail["spread_growth_comm"],
                          "spread_dir": detail["spread_growth_dir"]}, indent=1))
    elif mode == "pulse3":
        ok, detail = gate_ga3(vac_axis=3)
        with open(os.path.join(DATA, "m5_20_pulse_e3.json"), "w") as f:
            json.dump(detail, f, indent=1, default=str)
        print(json.dumps({"ok": ok, "spread_comm": detail["spread_growth_comm"],
                          "spread_dir": detail["spread_growth_dir"]}, indent=1))
    elif mode == "run":
        case, variant, T, boxmode = ARGV[1], ARGV[2], float(ARGV[3]), ARGV[4]
        tag = ARGV[5] if len(ARGV) > 5 else None
        run_case(case, variant, T, boxmode, tag=tag)
    elif mode == "runstate":
        sf, variant, T, boxmode, tag = (ARGV[1], ARGV[2], float(ARGV[3]),
                                        ARGV[4], ARGV[5])
        run_case(tag, variant, T, boxmode, tag=tag, state_file=sf)
    elif mode == "pincontrol":
        # POSITIVE CONTROL: the corepin state evolved WITH the core kept
        # frozen (the M5.12/M5.19 corepin convention, r_pin 2.5 at the seed
        # ring): the instrument must read a SURVIVING winding q = 1/2
        T = float(ARGV[1]) if len(ARGV) > 1 else 500.0
        M0 = np.load(os.path.join(
            DATA, "m5_19_d1_melt_q05_R17_corepin_state.npz"))["M0"].astype(
            np.float64)
        R, Z = grid_coords(NR, NZ, H)
        cmask = np.sqrt((R - 17.0) ** 2 + Z ** 2) < 2.5
        egf = make_egf("comm")
        Mx, v, recs, wall = evolve(M0, egf, T, 0.02,
                                   snap_every=int(round(T / 40 / 0.02)),
                                   snap_fn=loop_snap_fn, log_snaps=True,
                                   extra_pin=cmask)
        out = {"task": "M5.20", "case": "pincontrol", "T": T, "dt": 0.02,
               "trajectory": recs, "wall_s": round(wall, 1)}
        with open(os.path.join(DATA, "m5_20_pincontrol.json"), "w") as f:
            json.dump(out, f, indent=1, default=float)
        np.savez_compressed(os.path.join(DATA, "m5_20_pincontrol_state.npz"),
                            M0=Mx.astype(np.float32))
    else:
        raise SystemExit(f"unknown mode {mode}")
