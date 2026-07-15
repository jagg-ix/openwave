"""M5.20.2 phase C: the ansatz-level clock: H(omega) on rigid Lorentz orbits.

Phase-B verdict (m5_20_2_b_triage.json): field-level time integration of
the canonical completion is OBSTRUCTED: boost-sector injections diverge at
t ~ 21.5 (the M5.18 4b hazard is active), rotation-sector textures are
exactly stable. The pre-registered pivot (task_details blindspot 6 /
checkpoint decision tree): measure the clock sector ANSATZ-LEVEL, on the
author's VERIFIED Hamiltonian, with no unstable integration.

THE MEASUREMENT (exact, no integration)
    Rigid orbit through a state M0(x):  M(s) = Lam(s)^-T M0 Lam(s)^-1,
    Lam(s) = exp(s omega G),  G = eta W, W antisymmetric (the 6 Lorentz
    generators: rotations J12/J13/J23, boosts B01/B02/B03).
    Velocity per cell:  Mdot = -omega (G^T M0 + M0 G).
    Because global conjugation leaves V and the static eta-curvature
    invariant, the verified Hamiltonian on the orbit is EXACTLY
        H(omega) = H(0) + omega^2 K_eff(G, M0),
        K_eff = INT w_cell 4 SUM_{i in rho,phi,z} <[Mdot^, A_i]_eta,
                [Mdot^, A_i]_eta>_eta ,   Mdot^ = unit-omega velocity.
    K_eff < 0  <=>  spinning the texture LOWERS the verified H: the
    "clock propulsion with negative Hamiltonian terms" his 07-11 reply
    names, made quantitative. (It also means H is unbounded along that
    orbit: the same indefiniteness the dynamic triage measured; a
    physical clock then needs the constraint his intended dynamics
    supplies: THE question back to the author.)

    CAVEAT (axisym representation): the reduction stores the field in the
    co-rotating azimuthal frame; a GLOBAL generator G acts per cell on M0.
    For generators that do not commute with J the orbit takes the field
    out of equivariance; K_eff is still the exact quadratic H coefficient
    of the rigid orbit at s = 0 (the measurement reported), but the orbit
    is only axisym-representable for [G, J] = 0 (J12 rotations, B03
    boosts). Rows are flagged accordingly.

STATES: the delta = 0.3 biax loop seed (pair_1d), the delta = 0.3 pair_1d
UNWOUND remnant endpoint (the M5.20.1 persistent oscillation), and the
vac4 background; branches g_timelike (primary) and one_timelike (the Q19
alternate control).

Run:  python m5_20_2_c_clock.py
Out:  ../data/m5_20_2_c_clock.json, ../plots/m5_20_2_clock_homega.png
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

from m5_17_energy import cell_weights                              # noqa: E402
from m5_20_2_a_eom import (ETA, G_T, NR, NZ, H, WSCALE, channels,  # noqa: E402
                           comm_eta_b, inner_eta_b, seed4,
                           total_energy_4, vac4)
from m5_20_2_b_dynamics import vac_field                           # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")

GENS = {}
for name, (a, b) in (("rot_J12", (1, 2)), ("rot_J13", (1, 3)),
                     ("rot_J23", (2, 3)), ("boost_B01", (0, 1)),
                     ("boost_B02", (0, 2)), ("boost_B03", (0, 3))):
    W = np.zeros((4, 4))
    W[a, b], W[b, a] = 1.0, -1.0
    GENS[name] = ETA @ W
J_COMMUTING = {"rot_J12", "boost_B03"}     # axisym-representable orbits


def k_eff(M0, G):
    """the exact omega^2 coefficient of H on the rigid orbit through M0."""
    Mc = M0[: NR - 1, 1:-1]
    Md = -(G.T @ Mc + Mc @ G)
    Arho, Aphi, Az, _ = channels(M0, H)
    w = cell_weights(NR, NZ, H)
    dens = 0.0
    for A in (Arho, Aphi, Az):
        F = comm_eta_b(Md, A)
        dens = dens + inner_eta_b(F, F)
    dens = 4.0 * dens
    return float(np.sum(dens * w)), dens


def remnant_state():
    st = np.load(os.path.join(DATA,
                              "m5_20_1_run_d0p3_pair_1d_closed_state.npz"))
    M = st["M0"].astype(np.float64)
    M[..., 0, 0] = -G_T                     # the g-timelike branch time row
    return M


def main():
    delta = 0.3
    states = {
        "loop_seed_d0p3_pair_1d": seed4(delta, "pair_1d"),
        "remnant_d0p3_pair_1d": remnant_state(),
        "vac4_background": vac_field(delta),
    }
    # the Q19 alternate-branch control on the vacuum
    Mb = vac_field(delta, branch="one_timelike")
    states["vac4_one_timelike_branch"] = Mb

    out = {"task": "M5.20.2", "phase": "C", "wscale": WSCALE, "g": G_T,
           "delta": delta, "rows": []}
    for sname, M0 in states.items():
        H0 = total_energy_4(M0, WSCALE, delta)
        for gname, G in GENS.items():
            K, dens = k_eff(M0, G)
            neg_frac = float(-np.sum(dens[dens < 0])
                             / max(np.sum(np.abs(dens)), 1e-300))
            out["rows"].append({
                "state": sname, "generator": gname, "H0": H0,
                "K_eff": K, "neg_density_fraction": neg_frac,
                "axisym_representable": gname in J_COMMUTING})
            print(f"  {sname:28s} {gname:10s} H0={H0:9.3f} "
                  f"K_eff={K:+.4e} negfrac={neg_frac:.3f} "
                  f"{'(axisym orbit)' if gname in J_COMMUTING else ''}",
                  flush=True)

    # H(omega) curves for the loop seed + remnant, the two J12/B03 orbits
    omegas = np.linspace(0.0, 0.2, 41)
    curves = {}
    for sname in ("loop_seed_d0p3_pair_1d", "remnant_d0p3_pair_1d"):
        M0 = states[sname]
        H0 = total_energy_4(M0, WSCALE, delta)
        for gname in ("rot_J12", "boost_B03", "boost_B01"):
            K, _ = k_eff(M0, GENS[gname])
            curves[f"{sname}__{gname}"] = (H0 + omegas ** 2 * K).tolist()
    out["omegas"] = omegas.tolist()
    out["curves"] = curves

    with open(os.path.join(DATA, "m5_20_2_c_clock.json"), "w") as f:
        json.dump(out, f, indent=1, default=float)

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.2))
    for ax, sname in zip(axes, ("loop_seed_d0p3_pair_1d",
                                "remnant_d0p3_pair_1d")):
        for gname, ls in (("rot_J12", "-"), ("boost_B03", "--"),
                          ("boost_B01", ":")):
            ax.plot(omegas, curves[f"{sname}__{gname}"], ls, label=gname)
        ax.set_xlabel("omega (rigid orbit rate)")
        ax.set_ylabel("H(omega), verified Hamiltonian")
        ax.set_title(sname, fontsize=9)
        ax.legend(fontsize=8)
    fig.suptitle("the ansatz-level clock: H(omega) = H(0) + omega^2 K_eff"
                 " (exact on rigid Lorentz orbits)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m5_20_2_clock_homega.png"), dpi=130)
    print("wrote data/m5_20_2_c_clock.json + plots/m5_20_2_clock_homega.png")
    return out


if __name__ == "__main__":
    main()
