"""M5.12 block 10: the claim gauntlet on a converged/candidate BVP state.

Runs, on a saved state npz (the m5_12_d3b_* format):
    BG5  Noether drift: H(t_j) over the period (the verified Hamiltonian,
         ALL pairs +, m5_18 conventions); drift = (max-min)/|mean|.
         An exact solution conserves H; the drift measures solution quality.
    BG7  partial second-variation index: the k lowest eigenvalues of the
         free-block Hessian (matrix-free Lanczos on FD Hessian-vector
         products; the X-block of the residual Jacobian is symmetric by
         the variational structure); reports how many are negative and
         whether the count is h-stable (run on two states to compare).
    ROT  rotor-nontriviality: reconstruct the co-rotating profile
         Mbar(t_j) = R(-w t_j) M(t_j) R(w t_j) (axis-swing plane (2,3));
         (a) rigidity = max_j |Mbar(t_j) - Mbar_mean| (0 = rigid rotor);
         (b) the STATIC residual norm of Mbar_mean (large = the rotation is
         load-bearing: the state is NOT a trivially-rotating static
         solution); (c) energy split E(Mbar_mean) vs the rotor state's Shat.

Run:  python m5_12_gauntlet.py <state.npz> <nr> [k_eigs]
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.sparse.linalg import ArpackNoConvergence, LinearOperator, eigsh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
DATA = os.path.join(HERE, "..", "data")

ARGV = sys.argv[1:]
sys.argv = sys.argv[:1]

from m5_17_energy import cell_weights, curvature_density_np, \
    energy_gradient_np, grid_coords                                        # noqa: E402
from m5_16_axisym import pin_mask                                          # noqa: E402
from m5_12_clock_q import inner_eta_v, comm_eta_v, spatial_channels        # noqa: E402
from m5_12_dressed import v4d_density                                     # noqa: E402
from m5_12_d3pre import dv4d_dm                                            # noqa: E402
from m5_12_d3a_bvp import residual, sample_fields, x_pack                  # noqa: E402
from m5_12_d3b_newton import wscale_at                                     # noqa: E402


def load_state(path, Nt=1):
    d = np.load(path)
    M0 = d["M0"].astype(np.float64)
    As = [d[f"A{k+1}"].astype(np.float64) for k in range(Nt) if f"A{k+1}" in d]
    Bs = [d[f"B{k+1}"].astype(np.float64) for k in range(Nt) if f"B{k+1}" in d]
    return x_pack(M0, As, Bs), float(d["omega"][0])


def hamiltonian_density(Mt, Mdott, h, wscale):
    """the verified H: ALL pairs + (spatial AND time), + V."""
    Mc, Arho, Aphi, Az = spatial_channels(Mt, h)
    D0 = Mdott[: Mt.shape[0] - 1, 1:-1]
    dd = np.zeros(Mc.shape[:2])
    chans = (Arho, Aphi, Az)
    for a in range(3):
        for b in range(a + 1, 3):
            C = comm_eta_v(chans[a], chans[b])
            dd += 4.0 * inner_eta_v(C, C)
    for a in range(3):
        C = comm_eta_v(D0, chans[a])
        dd += 4.0 * inner_eta_v(C, C)
    dd += v4d_density(Mt, wscale)
    return dd


def bg5_noether(X, omega, h, wscale, ns=None):
    Nt = len(X["A"])
    ns = ns or (8 * Nt + 4)
    nr, nz = X["M0"].shape[:2]
    w = cell_weights(nr, nz, h)
    Ms, Mds = sample_fields(X, omega, ns)
    Hs = [float(np.sum(hamiltonian_density(Mt, Mdt, h, wscale) * w))
          for Mt, Mdt in zip(Ms, Mds)]
    Hs = np.array(Hs)
    return {"H_mean": float(np.mean(Hs)), "H_min": float(np.min(Hs)),
            "H_max": float(np.max(Hs)),
            "drift_rel": float((np.max(Hs) - np.min(Hs))
                               / (abs(np.mean(Hs)) + 1e-300))}


def bg7_index(X, omega, h, wscale, k=8):
    nr, nz = X["M0"].shape[:2]
    pin = pin_mask(nr, nz)
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), X["M0"].shape)
    nfree = int(np.sum(free))
    Nt = len(X["A"])
    blocks = 1 + 2 * Nt

    def to_vec(Xd):
        parts = [Xd["M0"][free]]
        for kk in range(Nt):
            parts.append(Xd["A"][kk][free])
            parts.append(Xd["B"][kk][free])
        return np.concatenate(parts)

    def from_vec(v):
        Xd = {"M0": X["M0"].copy(), "A": [a.copy() for a in X["A"]],
              "B": [b.copy() for b in X["B"]]}
        o = 0
        Xd["M0"][free] = Xd["M0"][free] + v[o:o + nfree]; o += nfree
        for kk in range(Nt):
            Xd["A"][kk][free] = Xd["A"][kk][free] + v[o:o + nfree]; o += nfree
            Xd["B"][kk][free] = Xd["B"][kk][free] + v[o:o + nfree]; o += nfree
        return Xd

    def R_of(Xd):
        Rd, _ = residual(Xd, omega, h, wscale)
        parts = [np.where(free, Rd["M0"], 0.0)[free]]
        for kk in range(Nt):
            parts.append(np.where(free, Rd["A"][kk], 0.0)[free])
            parts.append(np.where(free, Rd["B"][kk], 0.0)[free])
        return np.concatenate(parts)

    R0v = R_of(X)
    eps = 1e-6

    def hv(v):
        return (R_of(from_vec(eps * v)) - R0v) / eps

    n = nfree * blocks
    A = LinearOperator((n, n), matvec=hv, dtype=float)
    # block-11 fix (the block-10 run died uncaught at maxiter 3000 with 4/8
    # partials LOST): salvage ArpackNoConvergence partials; default k = 4;
    # 'SA' on this indefinite stiffness-spread spectrum is ARPACK-hostile,
    # so budget generously and report what converged.
    status = "converged"
    try:
        vals = eigsh(A, k=k, which="SA", return_eigenvectors=False,
                     tol=1e-3, maxiter=12000)
    except ArpackNoConvergence as e:
        vals = np.asarray(e.eigenvalues, dtype=float)
        status = f"no_convergence_salvaged_{vals.size}_of_{k}"
        if vals.size == 0:
            return {"lowest_eigs": [], "n_negative_of_k": None, "k": k,
                    "status": status}
    vals = np.sort(vals)
    return {"lowest_eigs": vals.tolist(),
            "n_negative_of_k": int(np.sum(vals < -1e-8)), "k": k,
            "status": status}


def rotor_test(X, omega, h, wscale, plane=(2, 3), ns=12):
    nr, nz = X["M0"].shape[:2]
    i, j = plane
    Ms, _ = sample_fields(X, omega, ns)
    Mbars = []
    for jj, Mt in enumerate(Ms):
        th = -(2.0 * np.pi * jj / ns)          # = -w t_j back-rotation phase
        L = np.eye(4)
        L[i, i], L[i, j], L[j, i], L[j, j] = (np.cos(th), -np.sin(th),
                                              np.sin(th), np.cos(th))
        Mbars.append(np.einsum("ab,...bc,dc->...ad", L, Mt, L))
    Mbar = sum(Mbars) / ns
    rig = max(float(np.max(np.abs(Mb - Mbar))) for Mb in Mbars)
    # static residual of the co-rotating mean profile (V_4D statics)
    w = cell_weights(nr, nz, h)
    G = energy_gradient_np(Mbar, 0.0, 0.0, 0.0, 1.0, h, 0.0)
    G[: nr - 1, 1:-1] += dv4d_dm(Mbar[: nr - 1, 1:-1], wscale) \
        * w[..., None, None]
    pin = pin_mask(nr, nz)
    free = np.broadcast_to((~pin)[..., None, None]
                           & np.ones((1, 1, 4, 4), bool), Mbar.shape)
    r_static = float(np.sqrt(np.sum(np.where(free, G, 0.0) ** 2)))
    E_static = float(np.sum((curvature_density_np(Mbar, h, 1.0)
                             + v4d_density(Mbar, wscale)) * w))
    return {"rigidity_max_dev": rig,
            "static_residual_of_corotating_mean": r_static,
            "E_static_of_corotating_mean": E_static,
            "note": "rigidity ~ 0 = rigid rotor; static residual LARGE ="
                    " the rotation is load-bearing (not a trivially-"
                    "rotating static solution)"}


def main():
    path = ARGV[0]
    nr = int(ARGV[1])
    k = int(ARGV[2]) if len(ARGV) > 2 else 4
    nz = 2 * nr
    h = 1.0
    X, om = load_state(path, Nt=1)
    wscale = wscale_at(nr, nz, h, 8.0 * nr / 96)
    out = {"state": os.path.basename(path), "nr": nr, "omega": om}
    out["BG5"] = bg5_noether(X, om, h, wscale)
    print(f"[BG5] H mean={out['BG5']['H_mean']:.4f} drift_rel={out['BG5']['drift_rel']:.3e}")
    out["ROT"] = rotor_test(X, om, h, wscale)
    print(f"[ROT] rigidity={out['ROT']['rigidity_max_dev']:.3e} "
          f"staticR={out['ROT']['static_residual_of_corotating_mean']:.3f} "
          f"E_corot={out['ROT']['E_static_of_corotating_mean']:.3f}")
    out["BG7"] = bg7_index(X, om, h, wscale, k=k)
    print(f"[BG7] lowest eigs: " + " ".join(f"{v:+.3e}" for v in out["BG7"]["lowest_eigs"])
          + f"  negatives: {out['BG7']['n_negative_of_k']}/{k}")
    tag = os.path.basename(path).replace(".npz", "")
    with open(os.path.join(DATA, f"m5_12_gauntlet_{tag}.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"json -> m5_12_gauntlet_{tag}.json")


if __name__ == "__main__":
    main()
