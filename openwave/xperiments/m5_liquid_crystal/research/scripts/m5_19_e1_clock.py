"""M5.19 phase E: the clock probe on the phase-D states, floor-compared.

Phase D's outcome fixes E's role: no unconstrained static loop exists, so
stabilization (if any) must come from the author's R7 channel ("tiny boosts
of temporal axis, crucial to propel oscillations"). The M5.12 close already
delivered the exhaustive negative on free-period orbits for ITS seed corpus;
its named REOPENING CONDITION is "a seed beating the floor-producing seed in
both conventions". Phase E therefore asks exactly that question for the NEW
backgrounds this task produced:

    backgrounds (M0): the wound pre-unwinding q = 1/2 states (melt 8k, the
    exact-0.5-winding endpoint; escape 8k) + the corepin constrained
    minimizer; the e2e2^T far field throughout.
    mix seeding: the b14 loop_bmix convention on the CURRENT ring (the
    |M13|^2 centroid): A1[0r] = eps b(dd) cr, A1[0z] = eps b(dd) cz,
    b = exp(-dd^2/w_b^2), w_b = 8 nr/96, eps = 0.16490; other harmonics 0.
    probe: the audited exact instrument (S0, Q2 + channels,
    omega_bal = sqrt(S0/-Q2)) in the b17 CONTROL FRAME (common n32 grid,
    common r_target, common a2 = 0.303725, one wscale), the four-frame
    battery r_target in {4.77, 3.686} x wscale in {native n32, rc-matched}.
    floor reference: the per-frame minima of the M5.12 b17 rows
    (m5_12_b17_control.json), i.e. the floor-producing lineage.

GATE (pre-registered 2026-07-10 post-D, BEFORE this script ran)
    GE0  guards: the b17 GC1-style identity spot check (a probe of a
         forged n32-native seed zoomed at s = 1 reproduces its direct
         probe within float32 tolerance)
    E    decision rule: a background BEATS THE FLOOR only if its
         controlled omega_bal is below the M5.12 per-frame floor minimum
         in ALL FOUR frames (and Q2 < 0 in all four). If ANY background
         beats the floor -> the M5.12 reopening condition fires: STOP and
         escalate to the user (reopening is a user call). Otherwise the
         statics negative COMPOUNDS: no new-family seed undercuts the
         M5.12 floor, and M5.19 closes on the honest negative with the
         author's construction exhausted at the statics + seed level.

Outputs: ../data/m5_19_e1_clock.json
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import grid_coords                                  # noqa: E402
from m5_16_axisym import pin_mask                                     # noqa: E402
from m5_12_d3b_newton import wscale_at                                # noqa: E402
import m5_12_b17_control as b17                                       # noqa: E402
from m5_12_b14_seeds import probe, s0_q2                              # noqa: E402
from m5_19_d1_relax import ring_by_m13                                # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
H = 1.0
EPS = 0.16490
NRN, NZN = 128, 256

BACKGROUNDS = {
    "melt8k_wound": "m5_19_d1_melt_q05_R17_state.npz",
    "escape8k": "m5_19_d1_escape_q05_R18_state.npz",
    "corepin": "m5_19_d1_melt_q05_R17_corepin_state.npz",
}


def forge_fields(m0_path):
    """M0 background + the b14 loop_bmix first harmonic on the current ring."""
    M0 = np.load(os.path.join(DATA, m0_path))["M0"].astype(np.float64)
    nr, nz = M0.shape[:2]
    rd = ring_by_m13(M0, nr, nz, H)
    rho_c, z_c = rd["ring13_rho"], rd["ring13_z"]
    R, Z = grid_coords(nr, nz, H)
    dd = np.sqrt((R - rho_c) ** 2 + (Z - z_c) ** 2) + 1e-12
    w_b = 8.0 * nr / 96.0
    b2 = np.exp(-(dd ** 2) / (w_b ** 2))
    cr, cz = (R - rho_c) / dd, (Z - z_c) / dd
    A1 = np.zeros_like(M0)
    A1[..., 0, 1] = A1[..., 1, 0] = EPS * b2 * cr
    A1[..., 0, 3] = A1[..., 3, 0] = EPS * b2 * cz
    pin = pin_mask(nr, nz)
    A1[pin] = 0.0
    Zf = np.zeros_like(M0)
    return ({"M0": M0, "A1": A1, "A2": Zf.copy(),
             "B1": Zf.copy(), "B2": Zf.copy()}, nr, nz,
            {"ring": [rho_c, z_c], "m13_max": rd["m13_max"]})


def gate_ge0(ws):
    """identity spot check: an n32-native forged object probed directly ==
    probed through control_probe at r_target = its own r_mean (s = 1).
    BOTH sides at the common a2 = A2_STAR (the control probe rescales
    internally; the direct side must match, else the difference is the
    physical amplitude dependence, not interpolation error)."""
    from m5_12_b14_seeds import forge_seed, rescale_to
    X, pin = forge_seed("loop_bmix", 32, 64, H, EPS)
    X, _ = rescale_to(X, pin, b17.A2_STAR)
    direct = probe(X, H, ws)
    fields = {"M0": X["M0"], "A1": X["A"][0], "A2": X["A"][1],
              "B1": X["B"][0], "B2": X["B"][1]}
    r0 = b17.r_mean_of(fields, 32, 64)
    ctrl, _ = b17.control_probe(fields, 32, 64, r0, r0, ws)
    rel = abs((ctrl["omega_bal"] or 0) - (direct["omega_bal"] or 0)) / max(
        abs(direct["omega_bal"] or 1e-30), 1e-30)
    return {"direct_omega": direct["omega_bal"], "ctrl_omega": ctrl["omega_bal"],
            "rel_err": rel, "pass": bool(rel <= 5e-3)}


def floor_reference():
    d = json.load(open(os.path.join(DATA, "m5_12_b17_control.json")))
    floors = {}
    for r in d["rows"]:
        if r.get("omega_bal") is None:
            continue
        key = (round(r["r_target"], 3), r["wscale"])
        cur = floors.get(key)
        if cur is None or r["omega_bal"] < cur["omega_bal"]:
            floors[key] = {"omega_bal": r["omega_bal"],
                           "product": r["product"],
                           "endpoint": r.get("endpoint")}
    return floors


def main():
    ws_native = wscale_at(32, 64, H, 8.0 * 32 / 96.0)
    out = {"eps": EPS, "a2_star": b17.A2_STAR,
           "GE0": gate_ge0(ws_native)}
    print(f"GE0 (control-frame identity): rel {out['GE0']['rel_err']:.2e} "
          f"pass={out['GE0']['pass']}")
    floors = floor_reference()
    out["floor"] = {f"rt{k[0]}_ws{k[1]}": v for k, v in floors.items()}
    for k, v in floors.items():
        print(f"  M5.12 floor rt={k[0]} ws={k[1]}: omega {v['omega_bal']:.3f} "
              f"({v['endpoint']})")

    results = {}
    any_beats = False
    for name, path in BACKGROUNDS.items():
        if not os.path.exists(os.path.join(DATA, path)):
            print(f"  [skip] {name}: {path} not found")
            continue
        fields, nr, nz, meta = forge_fields(path)
        r_now = b17.r_mean_of(fields, nr, nz)
        rec = {"meta": meta, "r_mean_native": r_now, "frames": {}}
        # native-frame raw probe (convention-bound, for the record)
        from m5_12_d3a_bvp import x_pack
        pin = pin_mask(nr, nz)
        Xn = x_pack(fields["M0"], [fields["A1"], fields["A2"]],
                    [fields["B1"], fields["B2"]])
        ws_n128 = wscale_at(nr, nz, H, 8.0 * nr / 96.0)
        rec["native_probe"] = probe(Xn, H, ws_n128)
        beats_all = True
        for rt in (4.77, 3.686):
            ws_matched = wscale_at(32, 64, H, rt)
            for wtag, ws in (("native", ws_native), ("matched", ws_matched)):
                ctrl, _ = b17.control_probe(fields, nr, nz, r_now, rt, ws)
                fkey = (round(rt, 3),
                        "native" if wtag == "native" else "rc-matched")
                fl = floors.get(fkey)
                beats = bool(ctrl["Q2_negative"] and fl and
                             ctrl["omega_bal"] < fl["omega_bal"])
                beats_all = beats_all and beats
                rec["frames"][f"rt{rt}_{wtag}"] = {
                    **{k: ctrl[k] for k in ("S0", "Q2", "Q2_mix", "Q2_pos",
                                            "Q2_negative", "omega_bal",
                                            "product", "r_mean_frame")},
                    "floor_omega": fl["omega_bal"] if fl else None,
                    "beats_floor": beats}
                print(f"  {name:14s} rt={rt} ws={wtag:7s}: "
                      f"Q2neg={ctrl['Q2_negative']} "
                      f"omega={ctrl['omega_bal'] if ctrl['omega_bal'] else float('nan'):.3f} "
                      f"floor={fl['omega_bal'] if fl else float('nan'):.3f} "
                      f"beats={beats}")
        rec["beats_floor_all_frames"] = beats_all
        any_beats = any_beats or beats_all
        results[name] = rec
    out["results"] = results
    out["E_gate"] = {"any_background_beats_floor": any_beats,
                     "decision": ("REOPENING CONDITION CANDIDATE: escalate "
                                  "to the user" if any_beats else
                                  "the statics negative COMPOUNDS: no "
                                  "new-family seed undercuts the M5.12 "
                                  "floor")}
    print(f"E gate: {out['E_gate']['decision']}")
    with open(os.path.join(DATA, "m5_19_e1_clock.json"), "w") as f:
        json.dump(out, f, indent=1)
    print("wrote data/m5_19_e1_clock.json")


if __name__ == "__main__":
    main()
