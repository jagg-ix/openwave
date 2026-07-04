"""M7.6 - electron observables (mass, charge, mu, spin, KG, two-charge E(d)).

Task doc: research/tasks/m7_6_observables.md. Modes:

  python m7_6_observables.py run       relax 3 seeds at fixed Q_can + H_A (the M7.5
                                       frame) + full observables battery per state
  python m7_6_observables.py pair      frozen-pair interaction energy E_int(d),
                                       aligned vs anti-aligned, padded box
  python m7_6_observables.py analyze   plots + the observables table

M7.5 design inputs (tasks/m7_5_clock_stability.md par. 5):

  * Frame: fixed Q_can = (w/2) int (|a_c|^2+|a_s|^2+|j_c|^2+|j_s|^2) [the real-time
    orbit frame; multiplier omega] PLUS fixed H_A (the localization guard).
    Both restores are exact rescales, interleaved to joint convergence.
  * Seeds include ROTATING (a_s != 0) pairs: the M7.4 winner was a standing
    doublet; spin/mu need the rotating sector.
  * Spin: <E x B> = (w/2)(a_c x B_s - a_s x B_c) per sector (A and J);
    L = int x cross <p> dV; standing states must give ZERO (internal check).
    Ceperley gate on rotating states: L_z = m U / w (m = 1).
  * mu: de-phased RMS dipole of the J-current (M7.2 contract analog):
    m_vec = 0.5 int x cross J dV with complex J = (j_c + i j_s)/sqrt2,
    reported componentwise modulus; plus the displacement-current reading.
  * Mass: own anchor (E_state = m_e c^2 defines the unit); ratios reported;
    the M6 charged ledger stays windowed (Q11) and is NOT used as anchor.
  * KG: analytic note from the M7.5 dispersion (propagating branch is KG-form
    w^2 = k^2 + m_eff^2 with m_eff^2 = c1 + sqrt(c1^2+1) = golden ratio at
    canonical params); no separate run needed.

Headless; matplotlib PNG only. Data: research/data/m7_6_*.json.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from m7_1_harmonic_lattice import (  # noqa: E402
    COMP_NAMES, HarmonicFields, curl_np, dot, fire_minimize, grid_xyz,
    seed_fleury_torus,
)
from m7_4_linked_vortex import (  # noqa: E402
    F_CONV, KAPPA, OMEGA, SHELL, TaichiBlend, apply_vacuum_shell, build_seed,
    helicity_A, helicity_A_grad, interior_mask_flat, pack_dict, qdiv_rms_at,
    qnorm_J, slot_mask, _normalize, _ring_frame,
)

DATA = os.path.join(HERE, "..", "data")
PLOTS = os.path.join(HERE, "..", "plots")

CONV = F_CONV["repulsive"]
C1, C2 = CONV["c1"], CONV["c2"]
A_SLOTS = ("avc", "avs")
VEC_SLOTS = ("avc", "avs", "jvc", "jvs")
SCALAR_SLOTS = ("a0c", "a0s", "j0c", "j0s")
QCAN_REF = 13.2017          # the M7.4 winner's Q_can at omega = 1 (m7_5_scan.json)


def _ti_init():
    import taichi as ti
    ti.init(arch=ti.cpu, default_fp=ti.f64, log_level=ti.WARN)


# =============================================================================
# the M7.5 frame: fixed Q_can + fixed H_A
# =============================================================================


def qcan(f: HarmonicFields, omega=OMEGA):
    h3 = f.h ** 3
    return 0.5 * omega * float(np.sum(
        dot(f.avc, f.avc) + dot(f.avs, f.avs)
        + dot(f.jvc, f.jvc) + dot(f.jvs, f.jvs)) * h3)


def qcan_grad(f: HarmonicFields, omega=OMEGA):
    h3 = f.h ** 3
    g = {name: np.zeros_like(getattr(f, name)) for name in COMP_NAMES}
    for name in VEC_SLOTS:
        g[name] = omega * getattr(f, name) * h3
    return g


def relax_qcan(eng: TaichiBlend, f0: HarmonicFields, n_iter=1500, tag="",
               omega=OMEGA, qcan0=None, log_every=250, free_scalars=()):
    """FIRE at fixed Q_can (global rescale restore) + fixed H_A (A-rescale),
    tangent projection Gram-Schmidt on both constraint gradients.
    free_scalars: scalar slots to UNFREEZE (e.g. ("a0c","a0s") for the Gauss
    experiment; j0 stays a fixed external source there)."""
    N, L = f0.N, f0.L
    scratch = HarmonicFields(N, L)
    frozen_scalars = tuple(s for s in SCALAR_SLOTS if s not in free_scalars)
    free = interior_mask_flat(f0) & ~slot_mask(f0, frozen_scalars)
    a_mask = slot_mask(f0, A_SLOTS)
    v_mask = slot_mask(f0, VEC_SLOTS)
    H0 = helicity_A(f0)
    Q0 = qcan0 if qcan0 is not None else qcan(f0, omega)

    def egf(x):
        scratch.unpack(x)
        E, g = eng.energy(scratch, grad=True)
        return E, pack_dict(g)

    def proj(x, g):
        g = g.copy()
        g[~free] = 0.0
        scratch.unpack(x)
        basis = []
        for gc in (pack_dict(helicity_A_grad(scratch)),
                   pack_dict(qcan_grad(scratch, omega))):
            gc[~free] = 0.0
            for b in basis:
                gc = gc - np.dot(gc, b) * b
            n = np.linalg.norm(gc)
            if n > 1e-300:
                basis.append(gc / n)
        for b in basis:
            g = g - np.dot(g, b) * b
        return g

    def corr(x):
        x = x.copy()
        for _ in range(4):                      # interleaved exact restores
            scratch.unpack(x)
            H = helicity_A(scratch)
            if H * H0 > 0:
                x[a_mask] *= np.sqrt(H0 / H)
            scratch.unpack(x)
            Q = qcan(scratch, omega)
            if Q > 1e-300:
                x[v_mask] *= np.sqrt(Q0 / Q)
            scratch.unpack(x)
            if (abs(helicity_A(scratch) / H0 - 1) < 1e-12
                    and abs(qcan(scratch, omega) / Q0 - 1) < 1e-12):
                break
        return x

    x = corr(f0.pack())
    hist, it_done, status = [], 0, "ok"
    x_last = x.copy()
    while it_done < n_iter:
        x, E, gn, _ = fire_minimize(x, egf, project_fn=proj, correct_fn=corr,
                                    n_iter=min(250, n_iter - it_done),
                                    gtol=1e-9, log_every=0)
        it_done += 250
        if not np.all(np.isfinite(x)):
            status = f"BLOW-UP at iter {it_done}"
            x = x_last
            break
        x_last = x.copy()
        scratch.unpack(x)
        hist.append({"iter": it_done, "E": E, "gnorm": gn,
                     "H_A": helicity_A(scratch),
                     "Q_can": qcan(scratch, omega),
                     "maxf": float(np.max(np.abs(x)))})
        if log_every:
            hh = hist[-1]
            print(f"  [{tag}] it={it_done:5d} E={hh['E']:+.5e} "
                  f"|g|={hh['gnorm']:.2e} H_A={hh['H_A']:+.4f} "
                  f"Q_can={hh['Q_can']:.4f} maxf={hh['maxf']:.3f}")
        if gn < 1e-9:
            break
    scratch.unpack(x)
    return scratch, {"history": hist, "status": status,
                     "E_final": hist[-1]["E"] if hist else None,
                     "gnorm_final": hist[-1]["gnorm"] if hist else None,
                     "H0": H0, "Q0": Q0}


# =============================================================================
# seeds (M7.6 set: standing baseline + rotating pairs)
# =============================================================================


def build_seed_m76(name, N, L):
    if name == "blend_standing":
        return build_seed("blend", N, L)
    if name == "blend_m1":
        f = build_seed("blend", N, L)
        X, Y, _ = grid_xyz(N, L)
        phi = np.arctan2(Y, X)
        c, s = np.cos(phi)[..., None], np.sin(phi)[..., None]
        g = HarmonicFields(N, L)
        g.avc, g.avs = f.avc * c, f.avc * s
        g.jvc, g.jvs = f.jvc * c, f.jvc * s
        return g
    if name == "fleury_m1":
        d = seed_fleury_torus(N, L, R0=0.25 * L, r0=0.09 * L)
        g = HarmonicFields(N, L)
        g.avc = _normalize(d["Es"])
        g.avs = _normalize(-d["Ec"])
        # poloidal twist -> nonzero H_A (the bare pair evaporated at M7.4)
        dd, _, th = _ring_frame(N, L, R0=0.25 * L)
        tap = np.exp(-(dd / (0.15 * L)) ** 2)
        g.avc = g.avc + 0.5 * tap[..., None] * th * 0.3
        g.jvc, g.jvs = -0.1 * g.avc, -0.1 * g.avs
        return g
    raise ValueError(name)


# =============================================================================
# observables battery
# =============================================================================


def momentum_avg(f: HarmonicFields, omega=OMEGA):
    """Time-averaged field momentum <E x B> per sector, summed."""
    h = f.h
    p = np.zeros(f.avc.shape)
    for (fc, fs) in ((f.avc, f.avs), (f.jvc, f.jvs)):
        Bc, Bs = curl_np(fc, h), curl_np(fs, h)
        p += 0.5 * omega * (np.cross(fc, Bs) - np.cross(fs, Bc))
    return p


def observables(f: HarmonicFields, eng: TaichiBlend, omega=OMEGA):
    h, N, L = f.h, f.N, f.L
    h3 = h ** 3
    X, Y, Z = grid_xyz(N, L)
    R = np.stack([X, Y, Z], axis=-1)
    E, _ = eng.energy(f)

    # spin: L = int x cross <p>
    p = momentum_avg(f, omega)
    Lvec = np.sum(np.cross(R, p), axis=(0, 1, 2)) * h3
    # Ceperley rotating-wave gate: L_z = m U / omega (m = 1)
    ceperley = float(Lvec[2] / (E / omega)) if E != 0 else None

    # mu: de-phased RMS dipole of the J-current (complex (jc + i js)/sqrt2)
    mc = 0.5 * np.sum(np.cross(R, f.jvc), axis=(0, 1, 2)) * h3
    ms = 0.5 * np.sum(np.cross(R, f.jvs), axis=(0, 1, 2)) * h3
    mu_J = np.sqrt((mc ** 2 + ms ** 2) / 2.0)          # componentwise RMS
    # displacement-current reading: j_disp-hat = i w E-hat, E-hat from doublet
    EAc = -omega * f.avs
    EAs = +omega * f.avc
    mdc = 0.5 * omega * np.sum(np.cross(R, EAs), axis=(0, 1, 2)) * h3
    mds = -0.5 * omega * np.sum(np.cross(R, EAc), axis=(0, 1, 2)) * h3
    mu_disp = np.sqrt((mdc ** 2 + mds ** 2) / 2.0)

    # charge (RMS/Fleury convention, M7.4 contract)
    Q_rho = qdiv_rms_at(f, 0.3 * L)

    # g-factor analog: g = 2 m mu / (Q S) in the program's own units
    g_sol = None
    if Q_rho > 0 and abs(Lvec[2]) > 1e-12:
        g_sol = float(2.0 * E * mu_J[2] / (Q_rho * Lvec[2]))

    # size
    u = (0.25 * omega ** 2 * (dot(f.avc, f.avc) + dot(f.avs, f.avs)
                              + dot(f.jvc, f.jvc) + dot(f.jvs, f.jvs)))
    r = np.sqrt(X * X + Y * Y + Z * Z)
    tot = float(np.sum(u))
    r50 = None
    if tot > 0:
        order = np.argsort(r.ravel())
        cu = np.cumsum(u.ravel()[order])
        r50 = float(r.ravel()[order][np.searchsorted(cu, 0.5 * cu[-1])])

    return {"E": E, "L_vec": [float(x) for x in Lvec],
            "L_z": float(Lvec[2]), "ceperley_ratio": ceperley,
            "mu_J": [float(x) for x in mu_J], "mu_J_z": float(mu_J[2]),
            "mu_disp_z": float(mu_disp[2]),
            "Q_rho": Q_rho, "g_sol": g_sol,
            "H_A": helicity_A(f), "Q_can": qcan(f, omega),
            "Q_J": qnorm_J(f), "r50": r50}


# =============================================================================
# modes
# =============================================================================


def mode_run(N=64, L=16.0, n_iter=1500):
    _ti_init()
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    results = {"N": N, "L": L, "n_iter": n_iter, "frame":
               f"fixed Q_can = {QCAN_REF} + fixed H_A (seed value)", "runs": {}}
    for sname in ("blend_standing", "blend_m1", "fleury_m1"):
        print("=" * 70)
        f0 = apply_vacuum_shell(build_seed_m76(sname, N, L))
        E0, _ = eng.energy(f0)
        print(f"M7.6 RUN {sname}: seed E={E0:+.5e} H_A={helicity_A(f0):+.5f} "
              f"Q_can={qcan(f0):.5f}")
        fR, info = relax_qcan(eng, f0, n_iter=n_iter, tag=sname,
                              qcan0=QCAN_REF)
        obs = observables(fR, eng)
        results["runs"][sname] = {
            "seed": {"E": E0, "H_A": helicity_A(f0)},
            "relax": {k: v for k, v in info.items() if k != "history"},
            "history": info["history"], "obs": obs}
        print(f"  final: E={info['E_final']}  status={info['status']}")
        print(f"  obs: L_z={obs['L_z']:+.5f}  ceperley={obs['ceperley_ratio']}"
              f"  mu_J_z={obs['mu_J_z']:+.5f}  Q_rho={obs['Q_rho']:.4e}"
              f"  g_sol={obs['g_sol']}")
        # eager npz checkpoint of each relaxed state (deleted at FINISH)
        np.savez(os.path.join(DATA, f"m7_6_state_{sname}.npz"), N=N, L=L,
                 E=info["E_final"], avc=fR.avc, avs=fR.avs,
                 jvc=fR.jvc, jvs=fR.jvs)
        with open(os.path.join(DATA, "m7_6_states.json"), "w") as fh:
            json.dump(results, fh, indent=1)
        print("  checkpointed -> data/m7_6_states.json + state npz")
    print("wrote data/m7_6_states.json")


def _embed_pad(arr, N_new):
    """Zero-pad a (N,N,N,3) field into the center of an (N_new,)^3 box (same h)."""
    N = arr.shape[0]
    out = np.zeros((N_new, N_new, N_new, 3))
    o = (N_new - N) // 2
    out[o:o + N, o:o + N, o:o + N] = arr
    return out


def mode_pair(winner="blend_m1", N=64, L=16.0, N_pad=96,
              ds=(5.0, 6.5, 8.0, 10.0)):
    """Frozen-pair interaction energy in a padded box (same lattice spacing)."""
    _ti_init()
    z = np.load(os.path.join(DATA, f"m7_6_state_{winner}.npz"))
    assert int(z["N"]) == N
    h = L / N
    L_pad = N_pad * h
    eng = TaichiBlend(N_pad, L_pad)
    eng.set_params(OMEGA, KAPPA, C1, C2)

    base = HarmonicFields(N_pad, L_pad)
    for name in VEC_SLOTS:
        setattr(base, name, _embed_pad(z[name], N_pad))
    E1, _ = eng.energy(base)
    print(f"padded single: E = {E1:.6f} (was {float(z['E']):.6f} in the "
          f"L={L} box)")

    out = {"winner": winner, "N_pad": N_pad, "L_pad": L_pad, "E_single": E1,
           "rows": []}
    for d in ds:
        sh = int(round(0.5 * d / h))
        for sign, tag in ((+1.0, "aligned"), (-1.0, "anti")):
            g = HarmonicFields(N_pad, L_pad)
            for name in VEC_SLOTS:
                a = getattr(base, name)
                g_arr = np.roll(a, +sh, axis=0) + sign * np.roll(a, -sh, axis=0)
                setattr(g, name, g_arr)
            apply_vacuum_shell(g)
            E2, _ = eng.energy(g)
            Eint = E2 - 2 * E1
            out["rows"].append({"d": 2 * sh * h, "sign": tag,
                                "E_pair": E2, "E_int": Eint})
            print(f"  d={2 * sh * h:5.2f} {tag:8s} E_pair={E2:+.6f} "
                  f"E_int={Eint:+.6f}")
    with open(os.path.join(DATA, "m7_6_pair.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote data/m7_6_pair.json")


def mode_moments(N=64, L=16.0):
    """Post-fix moment battery on the saved relaxed states (numpy only):
    (a) L_z decomposed per sector (A vs J) - the Ceperley factor-2 question;
    (b) the DE-PHASED magnetic moment (the M7.2 contract: weight the complex
        moment density by e^{-i phi} before integrating; the plain integral
        vanishes by m=1 symmetry, which is what mode_run measured);
    (c) same de-phased reading from the displacement current."""
    h = L / N
    h3 = h ** 3
    X, Y, Z = grid_xyz(N, L)
    R = np.stack([X, Y, Z], axis=-1)
    phi = np.arctan2(Y, X)
    eiphi = np.exp(-1j * phi)
    out = {}
    for sname in ("blend_standing", "blend_m1", "fleury_m1"):
        p = os.path.join(DATA, f"m7_6_state_{sname}.npz")
        if not os.path.exists(p):
            continue
        z = np.load(p)
        f = HarmonicFields(N, L)
        for name in VEC_SLOTS:
            setattr(f, name, z[name])
        row = {"E": float(z["E"])}
        # (a) L_z per sector
        for sec, (fc, fs) in (("A", (f.avc, f.avs)), ("J", (f.jvc, f.jvs))):
            Bc, Bs = curl_np(fc, h), curl_np(fs, h)
            psec = 0.5 * OMEGA * (np.cross(fc, Bs) - np.cross(fs, Bc))
            Lz = float(np.sum(np.cross(R, psec), axis=(0, 1, 2))[2] * h3)
            row[f"L_z_{sec}"] = Lz
        row["L_z_total"] = row["L_z_A"] + row["L_z_J"]
        row["ceperley_total"] = (row["L_z_total"] / (row["E"] / OMEGA)
                                 if row["E"] else None)
        # (b) de-phased mu from the J-current (complex J-hat = jc + i js)
        Jh = f.jvc + 1j * f.jvs
        mz = 0.5 * (np.cross(R, Jh)[..., 2])          # complex m_z density
        row["mu_J_dephased"] = float(np.abs(np.sum(eiphi * mz)) * h3 / np.sqrt(2))
        # (c) de-phased mu from the displacement current j = i w E-hat
        Eh = (-OMEGA * f.avs) + 1j * (OMEGA * f.avc)
        jd = 1j * OMEGA * Eh
        mzd = 0.5 * (np.cross(R, jd)[..., 2])
        row["mu_disp_dephased"] = float(np.abs(np.sum(eiphi * mzd)) * h3
                                        / np.sqrt(2))
        # g-factor analog with the de-phased mu and RMS charge
        Q_rho = qdiv_rms_at(f, 0.3 * L)
        row["Q_rho"] = Q_rho
        if Q_rho > 0 and abs(row["L_z_total"]) > 1e-9:
            row["g_sol"] = float(2 * row["E"] * row["mu_J_dephased"]
                                 / (Q_rho * row["L_z_total"]))
            row["g_sol_disp"] = float(2 * row["E"] * row["mu_disp_dephased"]
                                      / (Q_rho * row["L_z_total"]))
        print(f"{sname}: Lz_A={row['L_z_A']:+.4f} Lz_J={row['L_z_J']:+.4f} "
              f"cep={row['ceperley_total']}")
        print(f"  mu_J_deph={row['mu_J_dephased']:.5f} "
              f"mu_disp_deph={row['mu_disp_dephased']:.5f} "
              f"g_sol={row.get('g_sol')} g_disp={row.get('g_sol_disp')}")
        out[sname] = row
    with open(os.path.join(DATA, "m7_6_moments.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote data/m7_6_moments.json")


def mode_gauss(N=64, L=16.0, q0=0.5, w_src=2.0, n_iter=600):
    """The scalar/Gauss experiment (time-boxed; the M7.4 § 1 follow-up):
    j0c = a FIXED external charge source (a Gaussian ball; NOT free, which
    dodges the M7.4 null-J runaway), a0c/a0s UNFROZEN. The a0 EL is then
    Gauss's law with source j0: the state carries a genuine net monopole.
    Gate: Gauss flux Q_div(r) plateaus at the source charge and the far
    field goes Coulomb (|E| ~ r^-2, slope -2 vs the M7.4 measured -3.7)."""
    _ti_init()
    from m7_1_harmonic_lattice import div_np, d_axis
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    z = np.load(os.path.join(DATA, "m7_6_state_blend_m1.npz"))
    f0 = HarmonicFields(N, L)
    for name in VEC_SLOTS:
        setattr(f0, name, z[name])
    X, Y, Z = grid_xyz(N, L)
    r = np.sqrt(X * X + Y * Y + Z * Z)
    f0.j0c = q0 * np.exp(-(r / w_src) ** 2)
    src_Q = float(np.sum(f0.j0c) * (L / N) ** 3)
    apply_vacuum_shell(f0)
    print(f"gauss: source integral int j0c dV = {src_Q:.5f} (KAPPA-signed "
          f"monopole expected = {-src_Q:.5f} by on-shell Gauss)")
    fR, info = relax_qcan(eng, f0, n_iter=n_iter, tag="gauss",
                          qcan0=QCAN_REF, free_scalars=("a0c", "a0s"))
    # Gauss flux vs radius: volume integral of div E_Ac within r
    h = fR.h
    EAc = -np.stack([d_axis(fR.a0c, i, h) for i in range(3)], axis=-1) \
        - OMEGA * fR.avs
    EAs = -np.stack([d_axis(fR.a0s, i, h) for i in range(3)], axis=-1) \
        + OMEGA * fR.avc
    rc = div_np(EAc, h)
    radii = np.arange(1.0, 0.5 * L, 0.5)
    Qr = [float(np.sum(rc[r < rr]) * h ** 3) for rr in radii]
    # far-field radial profile of |E_A| (cos component)
    Emag = np.sqrt(np.maximum(dot(EAc, EAc), 1e-300))
    shell_r, shell_E = [], []
    for rr in np.arange(2.0, 0.45 * L, 0.5):
        m = (r >= rr - 0.25) & (r < rr + 0.25)
        shell_r.append(rr)
        shell_E.append(float(np.mean(Emag[m])))
    lr, le = np.log(shell_r[-6:]), np.log(shell_E[-6:])
    slope = float(np.polyfit(lr, le, 1)[0])
    out = {"q0": q0, "w_src": w_src, "src_Q": src_Q,
           "relax": {k: v for k, v in info.items() if k != "history"},
           "history": info["history"],
           "radii": radii.tolist(), "Q_div_r": Qr,
           "shell_r": shell_r, "shell_E": shell_E,
           "farfield_slope": slope,
           "a0_norm": float(np.sqrt(np.sum(fR.a0c ** 2) * h ** 3))}
    with open(os.path.join(DATA, "m7_6_gauss.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"  Q_div(r): {Qr[2]:.4f} @ r=2 ... {Qr[-1]:.4f} @ r={radii[-1]}")
    print(f"  far-field slope = {slope:.2f} (Coulomb = -2)")
    print("wrote data/m7_6_gauss.json")


def mode_gauss2(N=64, L=16.0, q0=0.5, w_src=1.6, n_iter=500,
                ds=(4.0, 6.0, 8.0)):
    """Two-charge Coulomb E(d): two FIXED Gauss sources at separation d
    (opposite and same sign), each dressed by the relaxed field; E_int(d)
    from the pair energy minus twice the single-source energy.
    Gate: E_int ~ q^2/d (attraction/repulsion bracketing, Duda's test)."""
    _ti_init()
    eng = TaichiBlend(N, L)
    eng.set_params(OMEGA, KAPPA, C1, C2)
    X, Y, Z = grid_xyz(N, L)

    def ball(x0):
        r2 = (X - x0) ** 2 + Y ** 2 + Z ** 2
        return q0 * np.exp(-r2 / w_src ** 2)

    def relax_with_source(j0c, tag):
        f0 = HarmonicFields(N, L)
        z = np.load(os.path.join(DATA, "m7_6_state_blend_m1.npz"))
        for name in VEC_SLOTS:
            setattr(f0, name, z[name])
        f0.j0c = j0c
        apply_vacuum_shell(f0)
        fR, info = relax_qcan(eng, f0, n_iter=n_iter, tag=tag,
                              qcan0=QCAN_REF, free_scalars=("a0c", "a0s"),
                              log_every=0)
        return info["E_final"], info["gnorm_final"]

    E1, g1 = relax_with_source(ball(0.0), "single")
    print(f"single source: E = {E1:.6f} (|g| = {g1:.1e})")
    out = {"q0": q0, "w_src": w_src, "E_single": E1, "rows": []}
    with open(os.path.join(DATA, "m7_6_gauss2.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    for d in ds:
        for sgn, tag in ((-1.0, "opposite"), (+1.0, "same")):
            j0 = ball(+0.5 * d) + sgn * ball(-0.5 * d)
            E2, g2 = relax_with_source(j0, f"pair d={d} {tag}")
            # E_int convention: pair minus twice single (fields re-relaxed)
            row = {"d": d, "sign": tag, "E_pair": E2, "gnorm": g2,
                   "E_int": E2 - 2 * E1}
            out["rows"].append(row)
            print(f"  d={d:4.1f} {tag:8s} E_pair={E2:+.6f} "
                  f"E_int={row['E_int']:+.6f} (|g|={g2:.1e})")
            with open(os.path.join(DATA, "m7_6_gauss2.json"), "w") as fh:
                json.dump(out, fh, indent=1)
    # 1/d fit on the opposite-minus-same splitting (cancels self-terms)
    dd = np.array(ds, dtype=float)
    split = []
    for d in ds:
        eo = [r["E_int"] for r in out["rows"] if r["d"] == d
              and r["sign"] == "opposite"][0]
        es = [r["E_int"] for r in out["rows"] if r["d"] == d
              and r["sign"] == "same"][0]
        split.append(0.5 * (es - eo))          # ~ q^2/(4 pi eps0 d)
    out["splitting"] = split
    lp = np.polyfit(np.log(dd), np.log(np.abs(split)), 1)
    out["split_power"] = float(lp[0])
    with open(os.path.join(DATA, "m7_6_gauss2.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    print(f"splitting (E_same - E_opp)/2 = {split}")
    print(f"power-law fit: splitting ~ d^{lp[0]:.2f} (Coulomb = -1)")
    print("wrote data/m7_6_gauss2.json")


def mode_analyze():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    os.makedirs(PLOTS, exist_ok=True)
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    p = os.path.join(DATA, "m7_6_states.json")
    if os.path.exists(p):
        with open(p) as fh:
            res = json.load(fh)
        ax = axes[0]
        for tag, r in res["runs"].items():
            hh = r["history"]
            ax.plot([x["iter"] for x in hh], [x["E"] for x in hh], "-o",
                    ms=3, label=f"{tag} (E={r['relax']['E_final']:.3f})")
        ax.set_title("relaxation at fixed Q_can + H_A (the M7.5 frame)")
        ax.set_xlabel("iteration")
        ax.set_ylabel("E_omega")
        ax.legend(fontsize=7)
        ax = axes[1]
        tags = list(res["runs"])
        Lzs = [res["runs"][t]["obs"]["L_z"] for t in tags]
        ceps = [res["runs"][t]["obs"]["ceperley_ratio"] or 0 for t in tags]
        xpos = np.arange(len(tags))
        ax.bar(xpos - 0.2, Lzs, 0.4, label="L_z (measured)")
        ax.bar(xpos + 0.2, [c * l if l else 0 for c, l in zip([1] * 3, [
            res["runs"][t]["obs"]["E"] / OMEGA for t in tags])], 0.4,
            alpha=0.5, label="U/omega (Ceperley m=1)")
        ax.set_xticks(xpos)
        ax.set_xticklabels(tags, fontsize=7)
        ax.set_title("spin: L_z vs the Ceperley rotating-wave law")
        ax.legend(fontsize=7)
    q = os.path.join(DATA, "m7_6_pair.json")
    if os.path.exists(q):
        with open(q) as fh:
            pr = json.load(fh)
        ax = axes[2]
        for tag, c in (("aligned", "C0"), ("anti", "C3")):
            rows = [r for r in pr["rows"] if r["sign"] == tag]
            ax.plot([r["d"] for r in rows],
                    [r["E_int"] for r in rows], c + "-o", label=tag)
        ax.axhline(0, color="k", lw=0.6)
        ax.set_title("frozen-pair interaction E_int(d)")
        ax.set_xlabel("d")
        ax.set_ylabel("E_int")
        ax.set_yscale("symlog", linthresh=1e-4)
        ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m7_6_observables.png"), dpi=130)
    print("wrote plots/m7_6_observables.png")

    # --- fig 2: the Gauss/Coulomb sector ---
    g1 = os.path.join(DATA, "m7_6_gauss.json")
    g2 = os.path.join(DATA, "m7_6_gauss2.json")
    if not os.path.exists(g1):
        return
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.4))
    with open(g1) as fh:
        ga = json.load(fh)
    ax = axes[0]
    ax.plot(ga["radii"], ga["Q_div_r"], "o-")
    ax.axhline(ga["src_Q"], color="k", ls="--", lw=0.8,
               label=f"source charge {ga['src_Q']:.2f}")
    ax.set_title("Gauss flux Q_div(< r): the monopole is real")
    ax.set_xlabel("r")
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.loglog(ga["shell_r"], ga["shell_E"], "o-",
              label=f"measured (slope {ga['farfield_slope']:.2f})")
    rr = np.array(ga["shell_r"])
    ax.loglog(rr, ga["shell_E"][-1] * (rr / rr[-1]) ** -2, "k--", lw=0.8,
              label="Coulomb r^-2")
    ax.set_title("far field |E_A|(r): Coulomb")
    ax.set_xlabel("r")
    ax.legend(fontsize=8)
    if os.path.exists(g2):
        with open(g2) as fh:
            gb = json.load(fh)
        if gb.get("splitting"):
            ax = axes[2]
            ds = sorted({r["d"] for r in gb["rows"]})
            sp = np.abs(gb["splitting"])
            ax.loglog(ds, sp, "o-",
                      label=f"|splitting| ~ d^{gb.get('split_power', 0):.2f}")
            dd = np.array(ds, dtype=float)
            ax.loglog(dd, sp[0] * (dd / dd[0]) ** -1, "k--", lw=0.8,
                      label="Coulomb d^-1")
            ax.set_title("two-charge splitting (E_same - E_opp)/2")
            ax.set_xlabel("d")
            ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(PLOTS, "m7_6_coulomb.png"), dpi=130)
    print("wrote plots/m7_6_coulomb.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["run", "pair", "moments", "gauss",
                                     "gauss2", "analyze"])
    args = ap.parse_args()
    os.makedirs(DATA, exist_ok=True)
    {"run": mode_run, "pair": mode_pair, "moments": mode_moments,
     "gauss": mode_gauss, "gauss2": mode_gauss2,
     "analyze": mode_analyze}[args.mode]()


if __name__ == "__main__":
    main()
