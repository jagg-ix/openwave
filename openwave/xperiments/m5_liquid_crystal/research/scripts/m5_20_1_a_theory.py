"""M5.20.1 phase A: vacuum theory of the biaxial (1, delta, 0) sector.

Duda's directive (2026-07-11/12, m5_20_convo.md): "topological vortex
requires potential with (1, delta, 0) minimum - preferred three different,
which should regularize to two equal in center"; "the problem was indeed
assuming delta=0 everywhere"; "in 3D (1, delta, 0) you can start with".

This script is the DoD-1/DoD-2 half of the plan (m5_20_1_task_details.md):

  1. GAP MAP: eigenfrequencies of the linearized uniform-mode EOM
         d_t^2 dM = -H_V dM     at the vacuum  diag(1, delta, 0),
     numeric 6x6 Hessian of the spectral V density (the m5_20_c1_blob
     vacuum_mass_spectrum generalized to delta != 0 targets
     c_p = 1 + delta^p), over a delta grid. Prediction under test: the
     delta = 0 vacuum has FOUR zero modes (3 conjugation flats + the
     pair-splitting direction of the degenerate (0,0) pair, flat to
     quartic order = the M5.20 removability face); at delta != 0 the
     splitting mode GAPS ("activating potential") and only the 3
     conjugation flats remain. omega_split(delta) is the protection scale.

  2. VACUUM ENUMERATION (the M5.20 dir-vacuum lesson applied up front):
     the 6 uniform equivariant vacua = diagonal assignments of (1, delta,
     0) to the axisym frame (axis 1 = meridional rho, axis 2 = azimuthal,
     axis 3 = z). Per variant: V (exact-0 check), u_curv on the grid
     (the commutator scheme charges only channel PAIRS; a uniform field
     has only the A_phi = [J, M]/rho channel, so u_curv = 0 is expected
     EXACTLY, delta-independent: the scheme-blindness measured in M5.19
     phase A), the A_phi background norm sqrt(2)|a1 - a2| (the strength
     of the LINEAR radiation channel found by the M5.20 audit: on a
     non-J-commuting vacuum, [A_pert, A_phi_bg] is linear in the
     perturbation), the dir-control Frank coefficient (a1 - a2)^2, and
     the axis-regularity flag (a1 == a2; at delta != 0 NO assignment is
     axis-regular: every uniform biaxial far field carries a
     scheme-invisible axis disclination, reported honestly).
     Output: the chosen far-field per winding pair (continuity with the
     M5.20 escape conventions at delta -> 0):
         pair_1d (winds (1, delta), out-of-plane 0): Me = diag(delta,0,1)
             -> e3 e3^T as delta -> 0 (the z-escape arm), A_phi ~ delta;
         pair_d0 (winds (delta, 0), out-of-plane 1): Me = diag(0,1,delta)
             -> e2 e2^T as delta -> 0 (the azimuthal arm), A_phi ~ 1.

  3. CORE-COST BARRIER TABLE (the spec-decode row): the per-cell V of the
     two-equal regularized core, per pairing:
         pair_1d core ((1+delta)/2, (1+delta)/2, 0)
         pair_d0 core (1, delta/2, delta/2)
     plus the full melt (0,0,0) reference; all vs the c_p(delta) targets,
     in wscale units. At delta = 0 the pair_1d/pair_d0 costs -> 0 (the
     measured potential-free removability face of M5.20).

GATES
    A1  V = 0 EXACTLY at diag(1, delta, 0) with c_p = 1 + delta^p,
        every production delta (the m5_18 S3 gate, per delta)   (<=1e-15)
    A2  FD directional gradient check of energy_gradient_spec_np at
        delta != 0 (general cps)                                (<=1e-5)
    A3  numeric 6x6 Hessian eigenvalue-sector == analytic 2 J^T J,
        J_pi = p lam_i^(p-1) (per-delta, rel)                   (<=1e-4)
    A4  u_curv == 0 exactly on every uniform enumerated vacuum  (<=1e-18)

Run:  python m5_20_1_a_theory.py
Out:  ../data/m5_20_1_a_theory.json, ../plots/m5_20_1_gapmap.png
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import (G_TIME, cell_weights, curvature_density_np,  # noqa: E402
                          grid_coords, J4)
from m5_18_spectral import (energy_gradient_spec_np,                   # noqa: E402
                            potential_density_spec_np,
                            total_energy_spec_np)
from m5_20_a1_dynamics import dir_density_np                           # noqa: E402
from m5_12_core_pin import load_wscale                                 # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
WSCALE = load_wscale()
DELTAS_PROD = (0.1, 0.3, 0.5)
DELTAS_MAP = tuple(np.round(np.arange(0.0, 0.62, 0.05), 3))


def cps_of(delta):
    return (1.0 + delta, 1.0 + delta ** 2, 1.0 + delta ** 3)


def _sym_basis3():
    """orthonormal (Frobenius) basis of symmetric 3x3: 3 diagonal + 3 off."""
    basis = []
    for i in range(3):
        e = np.zeros((3, 3))
        e[i, i] = 1.0
        basis.append(e)
    for (i, j) in ((0, 1), (0, 2), (1, 2)):
        e = np.zeros((3, 3))
        e[i, j] = e[j, i] = 1.0 / np.sqrt(2.0)
        basis.append(e)
    return basis


def vdens_delta(m, delta, wscale=1.0):
    m2 = m @ m
    t1, t2, t3 = np.trace(m), np.trace(m2), np.trace(m2 @ m)
    c1, c2, c3 = cps_of(delta)
    return wscale * ((t1 - c1) ** 2 + (t2 - c2) ** 2 + (t3 - c3) ** 2)


def vacuum_hessian_delta(delta, wscale=WSCALE, eps=1e-5):
    """numeric 6x6 Hessian of the V density at diag(1, delta, 0), in the
    Frobenius-orthonormal symmetric basis (kinetic metric = identity, so
    omega_i = sqrt(max(eig_i, 0)); m5_20_c1_blob.vacuum_mass_spectrum
    generalized to delta != 0)."""
    lam = np.diag([1.0, delta, 0.0])
    basis = _sym_basis3()
    Hm = np.zeros((6, 6))
    for a in range(6):
        for b in range(6):
            Hm[a, b] = (vdens_delta(lam + eps * (basis[a] + basis[b]), delta, wscale)
                        - vdens_delta(lam + eps * (basis[a] - basis[b]), delta, wscale)
                        - vdens_delta(lam + eps * (-basis[a] + basis[b]), delta, wscale)
                        + vdens_delta(lam - eps * (basis[a] + basis[b]), delta, wscale)
                        ) / (4 * eps ** 2)
    return 0.5 * (Hm + Hm.T)


def analytic_diag_hessian(delta, wscale=WSCALE):
    """eigenvalue-sector Hessian: 2 w J^T J, J_pi = p lam_i^(p-1) at the
    exact minimum (the (Tr M^p - c_p) factors vanish, only the rank-1
    outer-product terms survive)."""
    lam = np.array([1.0, delta, 0.0])
    J = np.array([[1.0, 1.0, 1.0],
                  [2.0 * lam[0], 2.0 * lam[1], 2.0 * lam[2]],
                  [3.0 * lam[0] ** 2, 3.0 * lam[1] ** 2, 3.0 * lam[2] ** 2]])
    return 2.0 * wscale * (J.T @ J)


def uniform_field(a1, a2, a3, nr=32, nz=64, g_time=G_TIME):
    M = np.zeros((nr, nz, 4, 4))
    M[..., 0, 0] = g_time
    M[..., 1, 1] = a1
    M[..., 2, 2] = a2
    M[..., 3, 3] = a3
    return M


def gate_a1a2():
    out = {}
    nr, nz, h = 32, 64, 1.0
    rng = np.random.default_rng(11)
    for delta in DELTAS_PROD:
        cps = cps_of(delta)
        # A1: exact pinning
        Mv = uniform_field(1.0, delta, 0.0, nr, nz)
        v = float(np.max(np.abs(potential_density_spec_np(Mv, 1.0, cps))))
        # A2: directional FD on a structured field (vacuum + smooth bump)
        R, Z = grid_coords(nr, nz, h)
        bump = 0.15 * np.exp(-((R - 8.0) ** 2 + Z ** 2) / 18.0)
        M0 = Mv.copy()
        M0[..., 1, 1] += bump
        M0[..., 1, 3] += 0.5 * bump
        M0[..., 3, 1] += 0.5 * bump
        worst = 0.0
        eps = 1e-6
        for _ in range(4):
            Dc = rng.normal(size=(nr - 1, nz - 2, 4, 4))
            D = np.zeros_like(M0)
            D[: nr - 1, 1:-1] = 0.5 * (Dc + np.swapaxes(Dc, -1, -2))
            D[..., 0, :] = 0.0
            D[..., :, 0] = 0.0
            G = energy_gradient_spec_np(M0, WSCALE, h, cps)
            num = (total_energy_spec_np(M0 + eps * D, WSCALE, h, cps)
                   - total_energy_spec_np(M0 - eps * D, WSCALE, h, cps)) / (2 * eps)
            an = float(np.sum(G * D))
            worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-12))
        out[str(delta)] = {"A1_V_pinned": v, "A2_gradcheck": worst}
    ok = all(r["A1_V_pinned"] < 1e-15 and r["A2_gradcheck"] < 1e-5
             for r in out.values())
    return ok, out


def gap_map():
    """the DoD-1 payload: zero-mode count + omega ladder vs delta."""
    rows = []
    split_dir = np.zeros(6)
    split_dir[1], split_dir[2] = 1.0 / np.sqrt(2), -1.0 / np.sqrt(2)  # diag(0,1,-1)
    a3_rel_worst = 0.0
    for delta in DELTAS_MAP:
        Hm = vacuum_hessian_delta(delta)
        ev = np.linalg.eigvalsh(Hm)
        scale = max(ev.max(), 1e-300)
        nzero = int(np.sum(ev < 1e-4 * scale))
        omegas = np.sqrt(np.maximum(ev, 0.0))
        # A3: eigenvalue-sector block (basis indices 0..2) vs analytic
        Ha = analytic_diag_hessian(delta)
        rel = float(np.max(np.abs(Hm[:3, :3] - Ha)) / np.max(np.abs(Ha)))
        a3_rel_worst = max(a3_rel_worst, rel)
        # the splitting-mode gap: Rayleigh quotient along diag(0, 1, -1)
        om_split = float(np.sqrt(max(split_dir @ Hm @ split_dir, 0.0)))
        rows.append({"delta": float(delta), "eigs": ev.tolist(),
                     "omegas": omegas.tolist(), "n_zero_modes": nzero,
                     "omega_split": om_split, "A3_rel": rel})
    return rows, a3_rel_worst


def enumerate_vacua(delta):
    """the 6 diagonal assignments of (1, delta, 0) to (rho, phi, z)."""
    import itertools
    nr, nz, h = 48, 96, 1.0
    w = cell_weights(nr, nz, h)
    out = []
    for perm in itertools.permutations((1.0, delta, 0.0)):
        a1, a2, a3 = perm
        M = uniform_field(a1, a2, a3, nr, nz)
        v = float(np.max(np.abs(potential_density_spec_np(M, 1.0, cps_of(delta)))))
        u = float(np.max(np.abs(curvature_density_np(M, h, 1.0))))
        dirE = float(np.sum(dir_density_np(M, h) * w))
        aphi = float(np.sqrt(2.0) * abs(a1 - a2))
        out.append({"assign_rho_phi_z": [a1, a2, a3], "V_max": v,
                    "u_curv_max": u, "aphi_bg_norm": aphi,
                    "dir_energy_48box": dirE,
                    "axis_regular": bool(abs(a1 - a2) < 1e-14)})
    return out


def core_cost_table():
    """per-cell V of the two-equal core, per pairing and delta, in wscale
    units (the barrier scale the unwinding path must now pay)."""
    rows = []
    for delta in DELTAS_MAP:
        m_1d = np.diag([(1 + delta) / 2, (1 + delta) / 2, 0.0])
        m_d0 = np.diag([1.0, delta / 2, delta / 2])
        m_melt = np.zeros((3, 3))
        rows.append({
            "delta": float(delta),
            "V_core_pair_1d_over_w": vdens_delta(m_1d, delta),
            "V_core_pair_d0_over_w": vdens_delta(m_d0, delta),
            "V_full_melt_over_w": vdens_delta(m_melt, delta)})
    return rows


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(PLOTS, exist_ok=True)
    out = {"task": "M5.20.1", "phase": "A", "wscale": WSCALE,
           "cps": "c_p = 1 + delta^p, p = 1..3",
           "deltas_production": list(DELTAS_PROD)}

    ok12, det12 = gate_a1a2()
    out["gates_A1_A2"] = det12
    print(f"[A1/A2] {'PASS' if ok12 else 'FAIL'} "
          + json.dumps(det12, default=float))

    rows, a3 = gap_map()
    out["gap_map"] = rows
    out["gate_A3_rel_worst"] = a3
    print(f"[A3 Hessian analytic-vs-numeric] "
          f"{'PASS' if a3 < 1e-4 else 'FAIL'} rel_worst={a3:.2e}")
    for r in rows:
        if r["delta"] in (0.0,) + tuple(DELTAS_PROD):
            print(f"  delta={r['delta']:.2f} zero_modes={r['n_zero_modes']} "
                  f"omega_split={r['omega_split']:.5f} "
                  f"omegas={np.round(r['omegas'], 5)}")
    z0 = [r for r in rows if r["delta"] == 0.0][0]["n_zero_modes"]
    zd = set(r["n_zero_modes"] for r in rows if r["delta"] >= 0.1)
    out["zero_mode_verdict"] = {"delta0": z0, "delta_ge_0.1": sorted(zd),
                                "drops_4_to_3": bool(z0 == 4 and zd == {3})}
    print(f"[gap map] zero modes: delta=0 -> {z0}, delta>=0.1 -> {sorted(zd)}"
          f"  (prediction 4 -> 3: "
          f"{'CONFIRMED' if out['zero_mode_verdict']['drops_4_to_3'] else 'NOT SEEN'})")

    vac = {}
    ok4 = True
    for delta in DELTAS_PROD:
        vac[str(delta)] = enumerate_vacua(delta)
        ok4 = ok4 and all(v["u_curv_max"] < 1e-18 and v["V_max"] < 1e-14
                          for v in vac[str(delta)])
    out["vacua"] = vac
    out["gate_A4_ucurv_zero"] = ok4
    print(f"[A4 uniform-vacua u_curv == 0] {'PASS' if ok4 else 'FAIL'}")
    n_axis_reg = sum(v["axis_regular"] for v in vac[str(DELTAS_PROD[0])])
    out["no_axis_regular_vacuum"] = bool(n_axis_reg == 0)
    print(f"  axis-regular assignments at delta != 0: {n_axis_reg} of 6 "
          "(every uniform biaxial far field carries a scheme-invisible "
          "axis disclination)")
    out["chosen_far_fields"] = {
        "pair_1d": {"assign_rho_phi_z": "(delta, 0, 1)",
                    "delta0_limit": "e3e3^T (M5.20 z-escape)",
                    "aphi_bg": "sqrt(2) delta (weak linear channel)"},
        "pair_d0": {"assign_rho_phi_z": "(0, 1, delta)",
                    "delta0_limit": "e2e2^T (M5.19/M5.20 azimuthal escape)",
                    "aphi_bg": "sqrt(2) (O(1) linear channel, as at delta=0)"}}

    cc = core_cost_table()
    out["core_cost"] = cc
    print("core cost per cell / wscale (the activated barrier):")
    for r in cc:
        if r["delta"] in (0.0,) + tuple(DELTAS_PROD):
            print(f"  delta={r['delta']:.2f}  pair_1d {r['V_core_pair_1d_over_w']:.5f}"
                  f"  pair_d0 {r['V_core_pair_d0_over_w']:.5f}"
                  f"  melt {r['V_full_melt_over_w']:.5f}")

    # plot: gap map + core costs
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.0))
    ds = [r["delta"] for r in rows]
    om = np.array([r["omegas"] for r in rows])
    for k in range(6):
        axes[0].plot(ds, om[:, k], "o-", ms=3, lw=1)
    axes[0].plot(ds, [r["omega_split"] for r in rows], "k--", lw=1.8,
                 label="omega along diag(0,1,-1) split dir")
    axes[0].set_xlabel("delta")
    axes[0].set_ylabel("omega (vacuum mass ladder)")
    axes[0].set_title("gap map at diag(1, delta, 0): the split mode activates")
    axes[0].legend(fontsize=7)
    axes[1].plot(ds, [r["n_zero_modes"] for r in rows], "s-")
    axes[1].set_xlabel("delta")
    axes[1].set_ylabel("zero modes of the 6x6 V-Hessian")
    axes[1].set_yticks([0, 1, 2, 3, 4, 5])
    axes[1].set_title("removability face gaps: 4 -> 3")
    for key, lab in (("V_core_pair_1d_over_w", "pair (1,d) core"),
                     ("V_core_pair_d0_over_w", "pair (d,0) core"),
                     ("V_full_melt_over_w", "full melt")):
        axes[2].plot([r["delta"] for r in cc], [r[key] for r in cc],
                     "o-", ms=3, label=lab)
    axes[2].set_xlabel("delta")
    axes[2].set_ylabel("V(core)/wscale per cell")
    axes[2].set_title("two-equal core cost (activating potential)")
    axes[2].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m5_20_1_gapmap.png"), dpi=130)

    with open(os.path.join(DATA, "m5_20_1_a_theory.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)
    print("wrote data/m5_20_1_a_theory.json + plots/m5_20_1_gapmap.png")
    return out


if __name__ == "__main__":
    main()
