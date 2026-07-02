"""M7.1 gate suite - runs the deliverable gates of task M7.1 (m7_1_infra.md).

  G1  bookkeeping     closed-form E_omega == brute-force period average
                      (uniform time sampling is EXACT for the degree-4 trig
                      polynomial u(t), so agreement must be ~1e-13)
  G2  AD gradient     Taichi reverse-mode AD == numpy complex-step directional
                      derivatives (holomorphic twin), target 1e-12; plus
                      Taichi energy == numpy energy
  G3  Woltjer-Taylor  fixed-helicity FIRE relaxation of int |curl A|^2 from a
                      RANDOM seed converges to the constant-lambda curl
                      eigenfield: lambda -> 2 pi / L (Richardson), pointwise
                      lambda_eff uniform, E -> lambda H  (Woltjer 1958)
  G4  seeders         analytic invariants of each seeder reproduced on the
                      lattice (ABC exact eigenrelation + O(h^2) invariants;
                      CK spheromak interior lambda_eff; hopfion div-free +
                      helicity convergence; Fleury support/omega; M6 profile
                      H/Q vs the 1.6890 ledger + embedding quadrature;
                      Ceperley winding)
  G5  gauge probe     harmonic gauge transform leaves E_omega invariant at
                      mJ = 0 (machine zero) and breaks it at mJ != 0 -> the
                      Q8 empirical evidence

Run:  python m7_1_gates.py          -> gate table + data/m7_1_gates.json
                                       + plots/m7_1_*.png
"""
from __future__ import annotations

import json
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import taichi as ti

from m7_1_harmonic_lattice import (
    COMP_NAMES, HarmonicFields, TaichiCurlEnergy, TaichiHarmonicEnergy,
    E_instantaneous_np, E_omega_np, curl_np, div_np, dot, grad_np, grid_xyz,
    helicity_fft_np, helicity_static_np, lambda_eff_np, m6_profile,
    seed_abc, seed_bateman_hopfion, seed_ceperley_mode, seed_ck_spheromak,
    seed_fleury_torus, seed_m6_embedding, woltjer_relax,
)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")
os.makedirs(DATA, exist_ok=True)
os.makedirs(PLOTS, exist_ok=True)

RESULTS = {}


def gate_line(name, ok, detail):
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {name}: {detail}")


# ---------------------------------------------------------------------------
# G1 - harmonic bookkeeping
# ---------------------------------------------------------------------------


def gate_g1(rng, N=16, L=2.0, omega=1.3, mJ=0.8, g=1.7, n_t=16):
    t0 = time.time()
    f = HarmonicFields(N, L).randomize(rng, amp=0.7)
    E_closed = E_omega_np(f, omega, mJ, g)
    T = 2 * np.pi / omega
    ts = np.arange(n_t) * (T / n_t)
    E_avg = np.mean([E_instantaneous_np(f, omega, mJ, g, t) for t in ts])
    rel = abs(E_closed - E_avg) / abs(E_avg)
    ok = rel < 1e-12
    RESULTS["G1_bookkeeping"] = {
        "ok": bool(ok), "E_closed": E_closed, "E_time_avg": float(E_avg),
        "rel_diff": float(rel), "n_time_samples": n_t,
        "params": {"N": N, "L": L, "omega": omega, "mJ": mJ, "g": g},
        "wall_s": round(time.time() - t0, 2)}
    gate_line("G1 bookkeeping", ok,
              f"closed-form vs {n_t}-sample period average rel diff = {rel:.2e}")
    return ok


# ---------------------------------------------------------------------------
# G2 - AD gradient vs complex step
# ---------------------------------------------------------------------------


def gate_g2(rng, eng: TaichiHarmonicEnergy, L=2.0, omega=1.3, mJ=0.8, g=1.7,
            n_dirs=10):
    t0 = time.time()
    N = eng.N
    f = HarmonicFields(N, L).randomize(rng, amp=0.7)
    eng.set_params(omega, mJ, g)
    eng.set_fields(f)
    E_ti = eng.energy()
    E_np = E_omega_np(f, omega, mJ, g)
    rel_E = abs(E_ti - E_np) / abs(E_np)

    grads = eng.gradient()
    g_flat = np.concatenate([grads[name].ravel() for name in COMP_NAMES])
    x0 = f.pack()
    h_cs = 1e-100
    rels = []
    for _ in range(n_dirs):
        v = rng.standard_normal(x0.size)
        v /= np.linalg.norm(v)
        fc = HarmonicFields(N, L, dtype=np.complex128)
        fc.unpack(x0.astype(np.complex128) + 1j * h_cs * v)
        dE_cs = np.imag(E_omega_np(fc, omega, mJ, g)) / h_cs
        dE_ad = float(np.dot(g_flat, v))
        rels.append(abs(dE_ad - dE_cs) / max(abs(dE_cs), 1e-300))
    max_rel = float(np.max(rels))
    ok = (max_rel < 1e-12) and (rel_E < 1e-12)
    RESULTS["G2_ad_gradient"] = {
        "ok": bool(ok), "energy_rel_diff_ti_vs_np": float(rel_E),
        "grad_max_rel_err_vs_complex_step": max_rel,
        "grad_rel_errs": [float(r) for r in rels], "n_dirs": n_dirs,
        "N": N, "wall_s": round(time.time() - t0, 2)}
    gate_line("G2 AD gradient", ok,
              f"E(ti) vs E(np) rel = {rel_E:.2e}; AD vs complex-step "
              f"max rel err = {max_rel:.2e} over {n_dirs} directions")
    return ok


# ---------------------------------------------------------------------------
# G3 - Woltjer-Taylor known-answer gate
# ---------------------------------------------------------------------------


def gate_g3(rng, engines, L=1.0, n_iter=12000):
    t0 = time.time()
    rows = []
    hist_finest = None
    lam_eff_finest = None
    for N, eng in engines:
        h = L / N
        # random smoothed seed (no eigenmode content injected on purpose)
        A = rng.standard_normal((N, N, N, 3))
        for _ in range(6):
            for ax in range(3):
                A = (np.roll(A, 1, axis=ax) + 2 * A + np.roll(A, -1, axis=ax)) / 4.0
        H0 = helicity_static_np(A, h)
        sigma = 1.0 if H0 >= 0 else -1.0
        A = A / np.sqrt(abs(H0))          # normalize |H| = 1 (H quadratic)
        H_target = sigma * 1.0
        A_rel, E, gn, hist = woltjer_relax(
            A, L, eng, H_target, n_iter=n_iter, gtol=1e-9, log_every=100)
        H_fin = helicity_static_np(A_rel, h)
        lam_hat = E / H_fin
        B = curl_np(A_rel, h)
        lam_eff, B2 = lambda_eff_np(B, h)
        w = B2 / B2.sum()
        lam_mean = float(np.sum(lam_eff * w))
        lam_std = float(np.sqrt(np.sum(w * (lam_eff - lam_mean) ** 2)))
        k = 2 * np.pi / L
        lam_disc = sigma * np.sin(k * h) / h
        rows.append({"N": N, "h": h, "lam_hat": float(lam_hat),
                     "lam_disc_expected": float(lam_disc),
                     "rel_err_vs_disc": float(abs(lam_hat - lam_disc) / abs(lam_disc)),
                     "lam_eff_wmean": lam_mean, "lam_eff_wstd": lam_std,
                     "E_final": float(E), "H_final": float(H_fin),
                     "E_minus_lamH_rel": float(abs(E - lam_hat * H_fin) / abs(E)),
                     "grad_inf_final": float(gn), "iters": hist[-1][0] if hist else None,
                     "sigma": sigma})
        print(f"  G3 N={N}: lam_hat={lam_hat:+.6f}  expected(disc)={lam_disc:+.6f}"
              f"  rel={rows[-1]['rel_err_vs_disc']:.2e}  lam_eff std/|lam|="
              f"{lam_std/abs(lam_mean):.2e}  grad_inf={gn:.2e}")
        hist_finest = hist
        lam_eff_finest = (lam_eff, B2, float(lam_disc))
    # Richardson h^2 extrapolation of |lam_hat| to h -> 0
    (h1, l1), (h2, l2) = ((rows[-2]["h"], abs(rows[-2]["lam_hat"])),
                          (rows[-1]["h"], abs(rows[-1]["lam_hat"])))
    lam_extrap = (l2 * h1 ** 2 - l1 * h2 ** 2) / (h1 ** 2 - h2 ** 2)
    k = 2 * np.pi / L
    rel_extrap = abs(lam_extrap - k) / k
    disc_ok = all(r["rel_err_vs_disc"] < 1e-4 for r in rows)
    ptwise_ok = all(r["lam_eff_wstd"] / abs(r["lam_eff_wmean"]) < 1e-4 for r in rows)
    ok = disc_ok and ptwise_ok and rel_extrap < 1e-3
    RESULTS["G3_woltjer"] = {
        "ok": bool(ok), "rows": rows, "lambda_richardson": float(lam_extrap),
        "two_pi_over_L": float(k), "rel_err_extrap": float(rel_extrap),
        "disc_ok": bool(disc_ok), "pointwise_ok": bool(ptwise_ok),
        "wall_s": round(time.time() - t0, 1)}
    gate_line("G3 Woltjer-Taylor", ok,
              f"lambda(h->0) = {lam_extrap:.6f} vs 2pi/L = {k:.6f} "
              f"(rel {rel_extrap:.2e}); per-N vs discrete eigenvalue all "
              f"< 1e-4: {disc_ok}; pointwise Beltrami: {ptwise_ok}")
    return ok, hist_finest, lam_eff_finest, rows


# ---------------------------------------------------------------------------
# G4 - seeder invariants
# ---------------------------------------------------------------------------


def gate_g4(rng):
    t0 = time.time()
    out = {}

    # --- ABC / Trkalian ---------------------------------------------------
    # division-free gates: (a) the DISCRETE eigenrelation curl A = lam_disc A
    # holds to machine precision (central diff of a trig field is exact up to
    # the sin(kh)/h factor); (b) the lattice H and E_B land EXACTLY on the
    # continuum values times sinc = sin(kh)/kh (resp. sinc^2), which is the
    # O(h^2) law in closed form. (A naive pointwise lambda_eff test fails at
    # the ABC flow's exact stagnation points, |F| = 0 - division artifact.)
    abc_rows = []
    L = 1.0
    for N in (24, 32, 48):
        h = L / N
        Af, exact = seed_abc(N, L)
        B = curl_np(Af, h)
        lam_d = exact["lam_discrete"]
        res = float(np.max(np.abs(B - lam_d * Af)) / np.max(np.abs(Af)))
        H_lat = helicity_static_np(Af, h)
        E_lat = float(np.sum(dot(B, B)) * h ** 3)
        sinc = np.sin(exact["lam"] * h) / (exact["lam"] * h)
        abc_rows.append({
            "N": N, "eigenrel_residual": res,
            "H_rel_err": float(abs(H_lat - exact["H"]) / exact["H"]),
            "E_rel_err": float(abs(E_lat - exact["E_B"]) / exact["E_B"]),
            "H_ratio_minus_sinc": float(abs(H_lat / exact["H"] - sinc)),
            "E_ratio_minus_sinc2": float(abs(E_lat / exact["E_B"] - sinc ** 2))})
    abc_ok = all(r["eigenrel_residual"] < 1e-12
                 and r["H_ratio_minus_sinc"] < 1e-12
                 and r["E_ratio_minus_sinc2"] < 1e-12 for r in abc_rows)
    out["abc"] = {"ok": bool(abc_ok), "rows": abc_rows,
                  "note": "discrete eigenrelation exact (machine); lattice H, "
                          "E_B equal continuum x sinc, sinc^2 exactly (the "
                          "closed-form O(h^2) law)"}

    # --- Chandrasekhar-Kendall spheromak (toroidal constant-lambda) --------
    ck_rows = []
    L = 2.0
    for N in (48, 64, 96):
        h = L / N
        Bf, ex = seed_ck_spheromak(N, L)
        lam_eff, B2 = lambda_eff_np(Bf, h)
        X, Y, Z = grid_xyz(N, L)
        r = np.sqrt(X * X + Y * Y + Z * Z)
        core = (r < 0.8 * ex["a"]) & (B2 > 1e-4 * B2.max())
        dev = np.abs(lam_eff[core] - ex["lam"]) / ex["lam"]
        ck_rows.append({"N": N, "lam_exact": ex["lam"],
                        "lam_eff_core_median_rel_dev": float(np.median(dev)),
                        "lam_eff_core_p95_rel_dev": float(np.quantile(dev, 0.95))})
    ck_conv = all(ck_rows[i + 1]["lam_eff_core_median_rel_dev"]
                  < ck_rows[i]["lam_eff_core_median_rel_dev"]
                  for i in range(len(ck_rows) - 1))
    ck_ok = ck_conv and ck_rows[-1]["lam_eff_core_median_rel_dev"] < 5e-3
    out["ck_spheromak"] = {"ok": bool(ck_ok), "rows": ck_rows,
                           "note": "interior constant-lambda Beltrami, O(h^2); "
                                   "S&Y eikonal variable-h construction deferred "
                                   "to M7.4"}

    # --- Bateman / Kedia hopfion -------------------------------------------
    hop_rows = []
    L = 8.0
    for N in (48, 64, 96):
        h = L / N
        E, B = seed_bateman_hopfion(N, L)
        # interior only: the rational 1/r^4 tail is not periodic, so the
        # rolled central difference is wrong on the boundary faces
        core = (slice(3, N - 3),) * 3
        dE = div_np(E, h)[core]
        dB = div_np(B, h)[core]
        gE = np.sqrt(np.mean(sum(dot(grad_np(E[..., i], h), grad_np(E[..., i], h))[core]
                                 for i in range(3))))
        rdivE = float(np.sqrt(np.mean(dE ** 2)) / gE)
        rdivB = float(np.sqrt(np.mean(dB ** 2)) / gE)
        Hm = helicity_fft_np(B, L)
        He = helicity_fft_np(E, L)
        U = float(0.5 * np.sum(dot(E, E) + dot(B, B)) * h ** 3)
        hop_rows.append({"N": N, "rel_rms_divE": rdivE, "rel_rms_divB": rdivB,
                         "H_magnetic": float(Hm), "H_electric": float(He),
                         "energy": U})
    div_conv = all(hop_rows[i + 1]["rel_rms_divE"] < hop_rows[i]["rel_rms_divE"]
                   for i in range(len(hop_rows) - 1))
    (h1, H1), (h2, H2) = ((L / hop_rows[-2]["N"], hop_rows[-2]["H_magnetic"]),
                          (L / hop_rows[-1]["N"], hop_rows[-1]["H_magnetic"]))
    H_extrap = (H2 * h1 ** 2 - H1 * h2 ** 2) / (h1 ** 2 - h2 ** 2)
    ee_mm = abs(hop_rows[-1]["H_electric"] - hop_rows[-1]["H_magnetic"]) / abs(H_extrap)
    hop_ok = div_conv and abs(H_extrap) > 0.1 and ee_mm < 0.05
    out["hopfion"] = {"ok": bool(hop_ok), "rows": hop_rows,
                      "H_magnetic_richardson": float(H_extrap),
                      "He_vs_Hm_rel_diff": float(ee_mm),
                      "note": "null field: div-free O(h^2), H_e = H_m "
                              "(self-dual), helicity nonzero (linked)"}

    # --- Fleury torus -------------------------------------------------------
    # thin tube (r0 = 0.152): voxelized volume converges slowly; N = 128 puts
    # ~3.2 cells across the minor radius; the M7.2 grid plan (h <= r0/8) is
    # where the tube is actually resolved. Seed-level tolerance 10%.
    N, L = 128, 6.0
    fl = seed_fleury_torus(N, L)
    h = L / N
    frac = float(fl["inside"].mean())
    frac_expect = float(2 * np.pi ** 2 * fl["R0"] * fl["r0"] ** 2 / L ** 3)
    U = float(0.25 * np.sum(dot(fl["Ec"], fl["Ec"]) + dot(fl["Es"], fl["Es"])
                            + dot(fl["Bc"], fl["Bc"]) + dot(fl["Bs"], fl["Bs"])) * h ** 3)
    fl_ok = (abs(frac - frac_expect) / frac_expect < 0.10) and U > 0 and \
        abs(fl["omega"] - 2.0 / fl["R0"]) < 1e-14
    out["fleury"] = {"ok": bool(fl_ok), "support_frac": frac,
                     "support_frac_expected": frac_expect,
                     "omega": fl["omega"], "period_avg_energy": U,
                     "note": "seed-level checks only; observable reproduction "
                             "is task M7.2"}

    # --- M6 profile + embedding ---------------------------------------------
    prof = m6_profile()
    r1d, a1d, b1d, obs = prof
    ledger = 1.6890
    hq_ok = abs(obs["HQ"] - ledger) < 0.005
    emb_rows = []
    for N in (64, 96):
        L = 26.0
        f, _ = seed_m6_embedding(N, L, profile=prof)
        h = L / N
        QJ_3d = float(np.sum(dot(f.jvs, f.jvs)) * h ** 3)
        dr = np.diff(r1d)
        rm = 0.5 * (r1d[:-1] + r1d[1:])
        bm = 0.5 * (b1d[:-1] + b1d[1:])
        QJ_1d = float(2 * np.pi * L * np.sum(bm ** 2 * rm * dr))
        emb_rows.append({"N": N, "QJ_3d": QJ_3d, "QJ_1d_x_2piLz": QJ_1d,
                         "rel_err": float(abs(QJ_3d - QJ_1d) / QJ_1d)})
    emb_ok = emb_rows[-1]["rel_err"] < 0.02 and \
        emb_rows[-1]["rel_err"] < emb_rows[0]["rel_err"]
    m6_ok = hq_ok and emb_ok
    out["m6_embedding"] = {"ok": bool(m6_ok), "HQ_1d": obs["HQ"],
                           "HQ_ledger": ledger, "HQ_ok": bool(hq_ok),
                           "tail": obs["tail"], "rows": emb_rows,
                           "note": "profile = repo-validated benchmark ODE at "
                                   "g=1.0; straight-cylinder embedding; the "
                                   "toroidal question is M7.3's"}

    # --- Ceperley rotating mode ---------------------------------------------
    N, L = 64, 4.0
    pc, ps, meta = seed_ceperley_mode(N, L, m=1)
    mid = N // 2
    n_loop = 720
    th = np.linspace(0, 2 * np.pi, n_loop, endpoint=False)
    rr = 0.25 * L
    xs = np.arange(N) * (L / N) - L / 2 + 0.5 * (L / N)
    px = np.interp(rr * np.cos(th), xs, np.arange(N))
    py = np.interp(rr * np.sin(th), xs, np.arange(N))
    vals_c = pc[np.clip(px.round().astype(int), 0, N - 1),
                np.clip(py.round().astype(int), 0, N - 1), mid]
    vals_s = ps[np.clip(px.round().astype(int), 0, N - 1),
                np.clip(py.round().astype(int), 0, N - 1), mid]
    ph = np.unwrap(np.angle(vals_c + 1j * vals_s))
    winding = float((ph[-1] - ph[0] + (ph[1] - ph[0])) / (2 * np.pi))
    cep_ok = abs(winding - meta["m"]) < 0.02
    out["ceperley"] = {"ok": bool(cep_ok), "winding_measured": winding,
                       "m": meta["m"], "kc": float(meta["kc"]),
                       "note": "J_m Bessel envelope rotating pair; the smooth "
                               "mask replacement for the M7.2 stretch"}

    ok = all(v["ok"] for v in out.values())
    out["wall_s"] = round(time.time() - t0, 1)
    RESULTS["G4_seeders"] = {"ok": bool(ok), **out}
    for name, v in out.items():
        if isinstance(v, dict) and "ok" in v:
            gate_line(f"G4 seeder {name}", v["ok"], v.get("note", ""))
    return ok, out


# ---------------------------------------------------------------------------
# G5 - gauge probe (Q8 evidence)
# ---------------------------------------------------------------------------


def gate_g5(rng, N=16, L=2.0, omega=1.3, g=1.7):
    t0 = time.time()
    f = HarmonicFields(N, L).randomize(rng, amp=0.7)
    h = f.h
    chi_c = rng.standard_normal((N, N, N))
    chi_s = rng.standard_normal((N, N, N))
    for _ in range(2):
        for ax in range(3):
            chi_c = (np.roll(chi_c, 1, ax) + 2 * chi_c + np.roll(chi_c, -1, ax)) / 4
            chi_s = (np.roll(chi_s, 1, ax) + 2 * chi_s + np.roll(chi_s, -1, ax)) / 4

    def gauge_transform(f0):
        fg = HarmonicFields(N, L)
        for name in COMP_NAMES:
            setattr(fg, name, getattr(f0, name).copy())
        # A0 -> A0 - dt(chi), Avec -> Avec + grad(chi), per harmonic component
        fg.a0c = fg.a0c - omega * chi_s
        fg.a0s = fg.a0s + omega * chi_c
        fg.avc = fg.avc + grad_np(chi_c, h)
        fg.avs = fg.avs + grad_np(chi_s, h)
        return fg

    fg = gauge_transform(f)
    E0_free = E_omega_np(f, omega, 0.0, g)
    Eg_free = E_omega_np(fg, omega, 0.0, g)
    rel_free = abs(Eg_free - E0_free) / abs(E0_free)
    mJ = 0.8
    E0_c = E_omega_np(f, omega, mJ, g)
    Eg_c = E_omega_np(fg, omega, mJ, g)
    rel_coupled = abs(Eg_c - E0_c) / abs(E0_c)
    ok = rel_free < 1e-12 and rel_coupled > 1e-6
    RESULTS["G5_gauge_probe"] = {
        "ok": bool(ok), "rel_dE_mJ0": float(rel_free),
        "rel_dE_mJ0p8": float(rel_coupled),
        "note": "E_omega gauge-invariant at mJ=0 (Maxwell structure verified); "
                "mJ^2 A.J breaks gauge invariance off-shell -> Q8 evidence",
        "wall_s": round(time.time() - t0, 2)}
    gate_line("G5 gauge probe", ok,
              f"dE/E under gauge transform: mJ=0 -> {rel_free:.2e} "
              f"(machine zero), mJ=0.8 -> {rel_coupled:.2e} (broken as expected)")
    return ok


# ---------------------------------------------------------------------------
# plots
# ---------------------------------------------------------------------------


def make_plots(g3_hist, g3_lam_eff, g3_rows, g4_out):
    # Woltjer gate figure
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    ax = axes[0]
    if g3_hist:
        its = [r[0] for r in g3_hist]
        Es = [r[1] for r in g3_hist]
        gns = [r[2] for r in g3_hist]
        ax.semilogy(its, np.abs(gns), label="|grad|_inf (projected)")
        ax2 = ax.twinx()
        ax2.semilogy(its, np.abs(Es), color="tab:orange", label="E_B")
        ax2.set_ylabel("E_B")
        ax.set_xlabel("FIRE iteration")
        ax.set_ylabel("|grad|_inf")
        ax.set_title("G3 relaxation (finest N)")
        ax.legend(loc="upper right")
    ax = axes[1]
    hs = np.array([r["h"] for r in g3_rows])
    lams = np.array([abs(r["lam_hat"]) for r in g3_rows])
    k = RESULTS["G3_woltjer"]["two_pi_over_L"]
    ax.plot(hs ** 2, lams, "o-", label="|lambda_hat|(h)")
    ax.axhline(k, color="k", ls="--", label="2 pi / L")
    ax.plot(hs ** 2, np.abs(np.sin(k * hs) / hs), "s--", alpha=0.6,
            label="discrete sin(kh)/h")
    ax.set_xlabel("h^2")
    ax.set_ylabel("lambda")
    ax.set_title("G3 lambda -> 2 pi/L as O(h^2)")
    ax.legend()
    ax = axes[2]
    lam_eff, B2, lam_disc = g3_lam_eff
    w = (B2 / B2.sum()).ravel()
    ax.hist(lam_eff.ravel(), bins=200, weights=w,
            range=(lam_disc - 0.02 * abs(lam_disc), lam_disc + 0.02 * abs(lam_disc)))
    ax.axvline(lam_disc, color="k", ls="--", label="expected (discrete)")
    ax.set_xlabel("lambda_eff = B.(curl B)/|B|^2")
    ax.set_ylabel("|B|^2-weighted")
    ax.set_title("G3 pointwise Beltrami (finest N)")
    ax.legend()
    fig.tight_layout()
    p1 = os.path.join(PLOTS, "m7_1_woltjer_gate.png")
    fig.savefig(p1, dpi=140)
    plt.close(fig)

    # seeder gallery
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    L = 1.0
    N = 48
    Af, _ = seed_abc(N, L)
    axes[0, 0].imshow(np.sqrt(dot(Af, Af))[:, :, N // 4].T, origin="lower")
    axes[0, 0].set_title("ABC/Trkalian |A| (z slice)")
    N, L = 64, 2.0
    Bf, ex = seed_ck_spheromak(N, L)
    axes[0, 1].imshow(np.sqrt(dot(Bf, Bf))[:, N // 2, :].T, origin="lower")
    axes[0, 1].set_title("CK spheromak |B| (y=0)")
    N, L = 64, 8.0
    E, B = seed_bateman_hopfion(N, L)
    axes[0, 2].imshow(np.sqrt(dot(B, B))[:, N // 2, :].T, origin="lower")
    axes[0, 2].set_title("Bateman hopfion |B| (y=0)")
    N, L = 96, 6.0
    fl = seed_fleury_torus(N, L)
    axes[1, 0].imshow(np.sqrt(dot(fl["Ec"], fl["Ec"]))[:, N // 2, :].T, origin="lower")
    axes[1, 0].set_title("Fleury torus |Ec| (y=0)")
    N, L = 96, 26.0
    f6, _ = seed_m6_embedding(N, L)
    img = f6.a0c[:, :, N // 2].T + np.sqrt(dot(f6.jvs, f6.jvs))[:, :, N // 2].T
    axes[1, 1].imshow(img, origin="lower")
    axes[1, 1].set_title("M6 embedding a0c + |J| (z slice)")
    N, L = 64, 4.0
    pc, ps, meta = seed_ceperley_mode(N, L)
    axes[1, 2].imshow(pc[:, :, N // 2].T, origin="lower")
    axes[1, 2].set_title("Ceperley J_1 rotating mode (cos comp)")
    for ax in axes.ravel():
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    p2 = os.path.join(PLOTS, "m7_1_seeder_gallery.png")
    fig.savefig(p2, dpi=140)
    plt.close(fig)
    return [p1, p2]


# ---------------------------------------------------------------------------


def main():
    t0 = time.time()
    rng = np.random.default_rng(7)
    print("M7.1 gate suite (Taichi CPU f64)")
    ti.init(arch=ti.cpu, default_fp=ti.f64, print_ir=False)

    # allocate ALL Taichi fields up front (no allocation after kernel launch)
    eng_h = TaichiHarmonicEnergy(16, 2.0)
    woltjer_Ns = (24, 32, 48)
    engines = [(N, TaichiCurlEnergy(N, 1.0)) for N in woltjer_Ns]

    ok1 = gate_g1(rng)
    ok2 = gate_g2(rng, eng_h)
    ok3, g3_hist, g3_lam_eff, g3_rows = gate_g3(rng, engines)
    ok4, g4_out = gate_g4(rng)
    ok5 = gate_g5(rng)

    plots = make_plots(g3_hist, g3_lam_eff, g3_rows, g4_out)

    all_ok = ok1 and ok2 and ok3 and ok4 and ok5
    RESULTS["summary"] = {
        "all_pass": bool(all_ok),
        "gates": {"G1": bool(ok1), "G2": bool(ok2), "G3": bool(ok3),
                  "G4": bool(ok4), "G5": bool(ok5)},
        "plots": [os.path.relpath(p, os.path.join(HERE, "..")) for p in plots],
        "wall_s_total": round(time.time() - t0, 1)}
    out_path = os.path.join(DATA, "m7_1_gates.json")
    with open(out_path, "w") as fh:
        json.dump(RESULTS, fh, indent=2)
    print(f"\nM7.1 gate suite: {'ALL PASS' if all_ok else 'FAILURES PRESENT'} "
          f"({RESULTS['summary']['wall_s_total']}s)")
    print(f"data -> {out_path}")
    for p in plots:
        print(f"plot -> {p}")


if __name__ == "__main__":
    main()
