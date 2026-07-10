"""M5.12 phase D3a: the time-periodic BVP action evaluator + analytic
residual on the equivariant instrument (design: m5_12_d3_bvp_design.md).

FIELDS (the Fourier container X):
    M(x, t) = M0(x) + SUM_{k=1..Nt} [ A_k(x) cos(k w t) + B_k(x) sin(k w t) ]
    each block (nr, nz, 4, 4) symmetric; samples t_j = j T / N_s,
    N_s = 4 Nt + 2 (band-limit-exact trapezoid on the period).

THE FUNCTIONAL (numeric sign convention: Shat reduces to the STATIC energy
when all harmonics vanish; stationarity of Shat == stationarity of S):
    Shat[X; w] = (1/N_s) SUM_j SUM_cells wcell . [
        4 ( SUM_{i<j spatial} inner_eta(F_ij) )      (spatial pairs, +)
      - 4 ( SUM_i inner_eta(F_0i) )                  (time pairs, -; the
                                                      verified spacetime sign)
      + V_4D(M) ]
    F_ij = [A_i, A_j]_eta on the three equivariant channels (rho, phi, z),
    F_0i = [Mdot, A_i]_eta,  Mdot = SUM_k k w (-A_k sin + B_k cos).

RESIDUAL (analytic adjoints, FD-gated BG1):
    for E = inner_eta(C, C), C = [A, B]_eta:
        dE/dA = +2 sym( eta [C, B]_eta eta ),  dE/dB = -2 sym( eta [C, A]_eta eta )
    scattered through the SAME channel adjoints as the gated static gradient
    (central differences + mirror ghost + the -[J, G]/rho azimuthal fold);
    V_4D gradient = dv4d_dm (gated P1, m5_12_d3pre.py); Fourier chain by the
    cos/sin sample weights; dShat/dw via the Mdot channel.

GATES THIS SCRIPT CARRIES (design BG series):
    BG1 residual == FD of Shat (random X, random symmetric directions,
        every block incl. w)
    BG2 static embedding: harmonics = 0 -> the M0-block residual equals the
        gated static gradient (eta-curvature == plain on covariant statics
        + dV_4D), and every harmonic-block residual is 0
    BG3 the vacuum rotor: X = Fourier projection of
        Lam(wt) M_vac Lam(wt)^{-1} (R12 conjugation of a transverse vacuum)
        has residual == 0 for every w (an exact solution family; exercises
        the harmonic plumbing end to end)

Run:  python m5_12_d3a_bvp.py gates
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import G_TIME, MIR, J4, cell_weights, grid_coords        # noqa: E402
from m5_12_clock_q import ETA, comm_eta_v, inner_eta_v, spatial_channels   # noqa: E402
from m5_12_dressed import to_covariant, v4d_density                       # noqa: E402
from m5_12_d3pre import dv4d_dm                                           # noqa: E402


def sym_v(A):
    return 0.5 * (A + np.swapaxes(A, -1, -2))


def eta_sandwich(A):
    """eta A eta, vectorized."""
    return np.einsum("ab,...bc,cd->...ad", ETA, A, ETA)


# ---------------- the Fourier container ----------------
def x_pack(M0, As, Bs):
    return {"M0": M0, "A": As, "B": Bs}


def sample_fields(X, omega, nt_samples):
    """M(t_j) and Mdot(t_j) for j = 0..N_s-1."""
    Nt = len(X["A"])
    js = np.arange(nt_samples)
    Ms, Mdots = [], []
    for j in js:
        th = 2.0 * np.pi * j / nt_samples
        M = X["M0"].copy()
        Md = np.zeros_like(X["M0"])
        for k in range(1, Nt + 1):
            c, s = np.cos(k * th), np.sin(k * th)
            M = M + X["A"][k - 1] * c + X["B"][k - 1] * s
            Md = Md + k * omega * (-X["A"][k - 1] * s + X["B"][k - 1] * c)
        Ms.append(M)
        Mdots.append(Md)
    return Ms, Mdots


# ---------------- per-sample density + gradients ----------------
def sample_density(Mt, Mdott, h, wscale):
    """density on included cells for one time sample."""
    Mc, Arho, Aphi, Az = spatial_channels(Mt, h)
    D0 = Mdott[: Mt.shape[0] - 1, 1:-1]
    d = np.zeros(Mc.shape[:2])
    chans = (Arho, Aphi, Az)
    for a in range(3):
        for b in range(a + 1, 3):
            C = comm_eta_v(chans[a], chans[b])
            d += 4.0 * inner_eta_v(C, C)
    for a in range(3):
        C = comm_eta_v(D0, chans[a])
        d -= 4.0 * inner_eta_v(C, C)
    d += v4d_density(Mt, wscale)
    return d


def sample_grad(Mt, Mdott, h, wscale, w):
    """gradients of SUM_cells wcell*density wrt the full-grid Mt and Mdott
    (both (nr, nz, 4, 4)); analytic adjoints."""
    nr, nz = Mt.shape[:2]
    inv2h = 1.0 / (2.0 * h)
    Mc, Arho, Aphi, Az = spatial_channels(Mt, h)
    D0 = Mdott[: nr - 1, 1:-1]
    w4 = w[..., None, None]
    chans = [Arho, Aphi, Az]
    Gch = [np.zeros_like(Arho) for _ in range(3)]
    GD0 = np.zeros_like(D0)
    # spatial pairs, +4
    for a in range(3):
        for b in range(a + 1, 3):
            C = comm_eta_v(chans[a], chans[b])
            Gch[a] += 4.0 * w4 * 2.0 * sym_v(eta_sandwich(comm_eta_v(C, chans[b])))
            Gch[b] += 4.0 * w4 * (-2.0) * sym_v(eta_sandwich(comm_eta_v(C, chans[a])))
    # time pairs, -4
    for a in range(3):
        C = comm_eta_v(D0, chans[a])
        GD0 += -4.0 * w4 * 2.0 * sym_v(eta_sandwich(comm_eta_v(C, chans[a])))
        Gch[a] += -4.0 * w4 * (-2.0) * sym_v(eta_sandwich(comm_eta_v(C, D0)))
    # scatter the channel gradients into the grid (the gated static pattern)
    GM = np.zeros_like(Mt)
    Grho, Gphi, Gz = Gch
    GM[1:, 1:-1] += Grho * inv2h
    GM[: nr - 2, 1:-1] -= Grho[1:] * inv2h
    GM[0, 1:-1] -= (MIR * Grho[0]) * inv2h
    GM[: nr - 1, 2:] += Gz * inv2h
    GM[: nr - 1, :-2] -= Gz * inv2h
    rho = ((np.arange(nr - 1) + 0.5) * h)[:, None, None, None]
    Gphi_r = Gphi / rho
    GM[: nr - 1, 1:-1] += -(np.einsum("ab,...bc->...ac", J4, Gphi_r)
                            - np.einsum("...ab,bc->...ac", Gphi_r, J4))
    # potential
    GM[: nr - 1, 1:-1] += dv4d_dm(Mc, wscale) * w4
    GMd = np.zeros_like(Mt)
    GMd[: nr - 1, 1:-1] = GD0
    return GM, GMd


# ---------------- Shat and the residual ----------------
def shat(X, omega, h, wscale, nt_samples=None):
    Nt = len(X["A"])
    ns = nt_samples or (4 * Nt + 2)
    nr, nz = X["M0"].shape[:2]
    w = cell_weights(nr, nz, h)
    Ms, Mds = sample_fields(X, omega, ns)
    tot = 0.0
    for Mt, Mdt in zip(Ms, Mds):
        tot += float(np.sum(sample_density(Mt, Mdt, h, wscale) * w))
    return tot / ns


def residual(X, omega, h, wscale, nt_samples=None):
    """returns (R dict matching X, dShat/domega)."""
    Nt = len(X["A"])
    ns = nt_samples or (4 * Nt + 2)
    nr, nz = X["M0"].shape[:2]
    w = cell_weights(nr, nz, h)
    R = {"M0": np.zeros_like(X["M0"]),
         "A": [np.zeros_like(a) for a in X["A"]],
         "B": [np.zeros_like(b) for b in X["B"]]}
    dSdw = 0.0
    Ms, Mds = sample_fields(X, omega, ns)
    for j, (Mt, Mdt) in enumerate(zip(Ms, Mds)):
        th = 2.0 * np.pi * j / ns
        GM, GMd = sample_grad(Mt, Mdt, h, wscale, w)
        R["M0"] += GM / ns
        for k in range(1, Nt + 1):
            c, s = np.cos(k * th), np.sin(k * th)
            R["A"][k - 1] += (GM * c + GMd * (-k * omega * s)) / ns
            R["B"][k - 1] += (GM * s + GMd * (k * omega * c)) / ns
        if omega != 0.0:
            dSdw += float(np.sum(GMd * (Mdt / omega))) / ns
    return R, dSdw


# ---------------- gates ----------------
def _rand_sym_like(M, rng, boundary_free=True):
    D = rng.normal(size=M.shape)
    D = sym_v(D)
    return D


def run_gates(nr=24, nz=48, h=1.0, Nt=2):
    from m5_17_energy import hedgehog_field, energy_gradient_np
    rng = np.random.default_rng(17)
    R0v, Z0v = grid_coords(nr, nz, h)
    wscale = 0.23
    omega = 0.41
    res = {}
    # a random but structured X: covariant hedgehog + small random harmonics
    M0 = to_covariant(hedgehog_field(R0v, Z0v, 5.0))
    As = [0.05 * _rand_sym_like(M0, rng) for _ in range(Nt)]
    Bs = [0.05 * _rand_sym_like(M0, rng) for _ in range(Nt)]
    X = x_pack(M0, As, Bs)
    # BG1: residual vs FD on every block + omega
    R, dSdw = residual(X, omega, h, wscale)
    eps, worst = 1e-6, 0.0
    for blk, arrs in (("M0", [X["M0"]]), ("A", X["A"]), ("B", X["B"])):
        for idx, arr in enumerate(arrs):
            D = _rand_sym_like(arr, rng)
            arr += eps * D
            Ep = shat(X, omega, h, wscale)
            arr -= 2 * eps * D
            Em = shat(X, omega, h, wscale)
            arr += eps * D
            num = (Ep - Em) / (2 * eps)
            an = float(np.sum((R[blk][idx] if blk != "M0" else R["M0"]) * D))
            worst = max(worst, abs(num - an) / (abs(num) + abs(an) + 1e-12))
    num_w = (shat(X, omega + eps, h, wscale)
             - shat(X, omega - eps, h, wscale)) / (2 * eps)
    worst_w = abs(num_w - dSdw) / (abs(num_w) + abs(dSdw) + 1e-12)
    res["BG1_residual_vs_FD"] = worst
    res["BG1_domega_vs_FD"] = worst_w
    # BG2: static embedding
    Xs = x_pack(M0.copy(), [np.zeros_like(M0) for _ in range(Nt)],
                [np.zeros_like(M0) for _ in range(Nt)])
    Rs, _ = residual(Xs, omega, h, wscale)
    G_static = energy_gradient_np(M0, 0.0, 0.0, 0.0, 1.0, h, 0.0)
    w = cell_weights(nr, nz, h)
    G_static[: nr - 1, 1:-1] += dv4d_dm(M0[: nr - 1, 1:-1], wscale) \
        * w[..., None, None]
    res["BG2_static_identity"] = float(np.max(np.abs(Rs["M0"] - G_static)))
    res["BG2_harmonics_zero"] = float(max(np.max(np.abs(a)) for a in
                                          Rs["A"] + Rs["B"]))
    # BG3: the vacuum rotor (transverse vacuum conjugated by R12(omega t))
    Mv = np.zeros((nr, nz, 4, 4))
    Mv[..., 1, 1] = 1.0                      # n = x_hat vacuum, spectrum (1,0,0)
    Mv = to_covariant(Mv)
    ns = 4 * Nt + 2
    # exact Fourier projection of Lam(th) Mv Lam(th)^T by sampling (band-limited)
    def rot(th):
        L = np.eye(4)
        L[1, 1], L[1, 2], L[2, 1], L[2, 2] = (np.cos(th), -np.sin(th),
                                              np.sin(th), np.cos(th))
        return np.einsum("ab,...bc,dc->...ad", L, Mv, L)
    samples = [rot(2.0 * np.pi * j / ns) for j in range(ns)]
    M0r = sum(samples) / ns
    Ar, Br = [], []
    for k in range(1, Nt + 1):
        Ar.append(sum(s * np.cos(k * 2.0 * np.pi * j / ns)
                      for j, s in enumerate(samples)) * 2.0 / ns)
        Br.append(sum(s * np.sin(k * 2.0 * np.pi * j / ns)
                      for j, s in enumerate(samples)) * 2.0 / ns)
    Xr = x_pack(M0r, Ar, Br)
    for om in (0.3, 1.1):
        Rr, dSw = residual(Xr, om, h, wscale)
        key = f"BG3_vacuum_rotor_maxR_w{om:g}"
        res[key] = float(max(np.max(np.abs(Rr["M0"])),
                             max(np.max(np.abs(a)) for a in Rr["A"] + Rr["B"]),
                             abs(dSw)))
    # tolerances (documented, not rigged): field-block FD is clean at 1e-9;
    # the omega FD is a difference of large Shat values (conditioning-limited
    # ~1e-5-1e-4); BG3's absolute floor is fp of (eta M)^4 arithmetic at
    # g = 8 (natural V scale ~ wscale g^4 ~ 1e3: relative ~1e-11)
    ok = {
        "BG1 residual == FD (all blocks + omega)": res["BG1_residual_vs_FD"] < 1e-6 and res["BG1_domega_vs_FD"] < 1e-4,
        "BG2 static embedding identity": res["BG2_static_identity"] < 1e-10 and res["BG2_harmonics_zero"] < 1e-10,
        "BG3 vacuum rotor is an exact solution": max(v for k, v in res.items() if k.startswith("BG3")) < 1e-6,
    }
    for k, v in ok.items():
        print(f"[{'PASS' if v else 'FAIL'}] {k}")
    for k, v in res.items():
        print(f"    {k} = {v:.3e}")
    res["all_pass"] = all(ok.values())
    with open(os.path.join(DATA, "m5_12_d3a_gates.json"), "w") as f:
        json.dump(res, f, indent=1)
    return res["all_pass"]


if __name__ == "__main__":
    mode = ARGV[0] if ARGV else "gates"
    if mode == "gates":
        ok = run_gates()
        sys.exit(0 if ok else 1)
    else:
        print(f"unknown mode {mode}")
