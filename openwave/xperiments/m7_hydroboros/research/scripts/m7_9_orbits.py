"""M7.9 orbit-hunting toolkit (ChaosBook methodology, dimension-agnostic).

Reusable module for the M7.10-M7.14 pure-Maxwell / Beltrami orbit track.
Small ODE systems run through scipy RK45 here; lattice field flows plug in
later through the same interfaces (state vector + callable RHS).

API (consumed by the m7_9_* drivers and by M7.10 E1):
    integrate(f, x0, T)                 trajectory of dx/dt = f(x)
    monodromy(f, jac, x0, T)            fundamental matrix along a trajectory
    poincare_section(f, x0, plane, ...) ordered section crossings + times
    return_map(crossings, coords)       (u_k, u_{k+1}) pairs on the section
    close_returns(pts, n)               n-step near-recurrences = cycle seeds
    find_cycle(f, jac, x0, T0, m)       Newton / multiple shooting on (x, T)
    floquet(f, jac, cycle)              Floquet multipliers of a flow cycle
    find_cycle_map(fmap, jmap, xs)      Newton multi-shooting for maps
    floquet_map(jmap, xs)               multipliers of a map cycle

Conventions: autonomous flows dx/dt = f(x); jac(x) is the [d,d] stability
matrix A_ij = df_i/dx_j; a flow cycle is (points[m,d], T) with points[i] on
the orbit at times i*T/m. References: ChaosBook (chaosbook.org) ch. 16
"Fixed points, and how to get them" + appendix A16 (multi-shooting), local
copies in theory/chaosbook/.
"""

from __future__ import annotations

import numpy as np
from scipy.integrate import solve_ivp

RTOL = 1e-12
ATOL = 1e-12


# ---------------------------------------------------------------- integration


def integrate(f, x0, T, t_eval=None, rtol=RTOL, atol=ATOL, dense=False):
    """Integrate dx/dt = f(x) from x0 over [0, T]. Returns the solve_ivp result."""
    sol = solve_ivp(
        lambda t, x: f(x), (0.0, T), np.asarray(x0, float),
        t_eval=t_eval, rtol=rtol, atol=atol, dense_output=dense, method="RK45",
    )
    if not sol.success:
        raise RuntimeError(f"integrate failed: {sol.message}")
    return sol


def flow_endpoint(f, x0, T, rtol=RTOL, atol=ATOL):
    """The point phi_T(x0)."""
    return integrate(f, x0, T, rtol=rtol, atol=atol).y[:, -1]


def monodromy(f, jac, x0, T, rtol=RTOL, atol=ATOL):
    """Fundamental matrix J(T): integrate dPhi/dt = A(x)Phi along the trajectory.

    Returns (x_T, Phi_T). For a full cycle period this is the monodromy matrix.
    """
    d = len(x0)

    def rhs(t, y):
        x, phi = y[:d], y[d:].reshape(d, d)
        return np.concatenate([f(x), (jac(x) @ phi).ravel()])

    y0 = np.concatenate([np.asarray(x0, float), np.eye(d).ravel()])
    sol = solve_ivp(rhs, (0.0, T), y0, rtol=rtol, atol=atol, method="RK45")
    if not sol.success:
        raise RuntimeError(f"monodromy failed: {sol.message}")
    yT = sol.y[:, -1]
    return yT[:d], yT[d:].reshape(d, d)


def numjac(f, eps=1e-7):
    """Central-difference Jacobian factory for flows/maps lacking an analytic one."""

    def jac(x):
        x = np.asarray(x, float)
        d = len(x)
        J = np.empty((d, d))
        for j in range(d):
            dx = np.zeros(d)
            dx[j] = eps * max(1.0, abs(x[j]))
            J[:, j] = (np.asarray(f(x + dx)) - np.asarray(f(x - dx))) / (2 * dx[j])
        return J

    return jac


# ----------------------------------------------------------- Poincare section


def poincare_section(f, x0, plane, direction=-1, n_cross=100, t_transient=0.0,
                     t_max=1e4, rtol=RTOL, atol=ATOL):
    """Ordered crossings of the hyperplane n.x = c.

    plane = (n, c) with n the normal vector; direction = +1 keeps crossings with
    d(n.x)/dt > 0, -1 the opposite ones, 0 both. Returns (points[k,d], times[k]).
    """
    n, c = np.asarray(plane[0], float), float(plane[1])
    x0 = np.asarray(x0, float)

    if t_transient > 0.0:
        x0 = flow_endpoint(f, x0, t_transient, rtol=rtol, atol=atol)

    def event(t, x):
        return float(n @ x - c)

    event.terminal = False
    event.direction = float(direction)

    sol = solve_ivp(
        lambda t, x: f(x), (0.0, t_max), x0,
        events=event, rtol=rtol, atol=atol, method="RK45", dense_output=True,
    )
    pts, ts = sol.y_events[0], sol.t_events[0]
    keep = ts > 1e-12  # an initial point sitting on the section is not a crossing
    pts, ts = pts[keep], ts[keep]
    return pts[:n_cross], ts[:n_cross]


def return_map(points, coord=0):
    """(u_k, u_{k+1}) pairs from ordered section crossings; coord picks the
    section coordinate (int index or callable point -> scalar)."""
    u = np.array([coord(p) for p in points]) if callable(coord) else points[:, coord]
    return u[:-1], u[1:]


def close_returns(points, n, top=8, min_sep=0.05):
    """Indices k whose n-step return |p_{k+n} - p_k| is smallest: cycle seeds.

    Greedy dedupe: a candidate within min_sep * ptp of an already accepted
    seed is skipped (distinct cycles can pass close on the section, so keep
    min_sep small when hunting longer cycles). Returns a list of indices.
    """
    m = len(points) - n
    if m <= 0:
        return []
    dist = np.linalg.norm(points[n:] - points[:-n], axis=1)
    order = np.argsort(dist)
    seeds, taken = [], []
    for k in order:
        if any(np.linalg.norm(points[k] - points[j]) < min_sep * np.ptp(points) for j in taken):
            continue
        seeds.append(int(k))
        taken.append(k)
        if len(seeds) >= top:
            break
    return seeds


# ------------------------------------------------------- cycle finding: flows


def find_cycle(f, jac, x0, T0, m=1, tol=1e-11, max_iter=60, verbose=False):
    """Newton / multiple shooting for a periodic orbit of a flow, period free.

    Unknowns: m shooting points x_1..x_m plus the period T. Residuals: the m
    cyclic matching conditions phi_{T/m}(x_i) - x_{i+1} and one phase condition
    f(x_1^(0)) . (x_1 - x_1^(0)) = 0 anchoring the orbit parametrization
    (ChaosBook ch. 16 (16.3); appendix A16.1). Square system, solved by damped
    Newton with a residual-decrease line search.

    Returns dict: points[m,d], T, converged, residual, trace (residual per step).
    """
    x0 = np.asarray(x0, float)
    if x0.ndim == 2:  # caller supplies the m shooting points directly
        xs, (m, d) = x0.copy(), x0.shape
    else:
        d = len(x0)
        xs = np.empty((m, d))
        xs[0] = x0
        for i in range(1, m):
            xs[i] = flow_endpoint(f, xs[i - 1], T0 / m)
    T = float(T0)
    anchor, f_anchor = xs[0].copy(), f(xs[0])

    def residual_and_jac(xs, T):
        h = T / m
        R = np.empty(m * d + 1)
        Jbig = np.zeros((m * d + 1, m * d + 1))
        for i in range(m):
            xi_end, Phi = monodromy(f, jac, xs[i], h)
            j = (i + 1) % m
            R[i * d:(i + 1) * d] = xi_end - xs[j]
            Jbig[i * d:(i + 1) * d, i * d:(i + 1) * d] = Phi
            Jbig[i * d:(i + 1) * d, j * d:(j + 1) * d] -= np.eye(d)
            Jbig[i * d:(i + 1) * d, -1] = f(xi_end) / m
        R[-1] = f_anchor @ (xs[0] - anchor)
        Jbig[-1, :d] = f_anchor
        return R, Jbig

    trace = []
    for _ in range(max_iter):
        try:
            R, Jbig = residual_and_jac(xs, T)
        except RuntimeError:  # trajectory blew up from a bad iterate
            return {"points": xs, "T": T, "converged": False,
                    "residual": np.inf, "trace": trace}
        rnorm = np.linalg.norm(R)
        trace.append(rnorm)
        if verbose:
            print(f"  newton |R| = {rnorm:.3e}  T = {T:.9f}")
        if rnorm < tol:
            return {"points": xs, "T": T, "converged": True,
                    "residual": rnorm, "trace": trace}
        try:
            step = np.linalg.solve(Jbig, -R)
        except np.linalg.LinAlgError:
            step, *_ = np.linalg.lstsq(Jbig, -R, rcond=None)
        lam = 1.0
        for _ in range(8):
            xs_try = xs + lam * step[:m * d].reshape(m, d)
            T_try = T + lam * step[-1]
            if T_try > 0:
                try:
                    R_try, _ = residual_and_jac(xs_try, T_try)
                except RuntimeError:  # blow-up: shrink the step and retry
                    lam *= 0.5
                    continue
                if np.linalg.norm(R_try) < rnorm:
                    xs, T = xs_try, T_try
                    break
            lam *= 0.5
        else:
            break
    return {"points": xs, "T": T, "converged": False,
            "residual": trace[-1], "trace": trace}


def floquet(f, jac, cycle, rtol=RTOL, atol=ATOL):
    """Floquet multipliers of a flow cycle: eigenvalues of the monodromy matrix
    accumulated segment by segment over the full period (ChaosBook ch. 5)."""
    xs, T = cycle["points"], cycle["T"]
    m, d = xs.shape
    M = np.eye(d)
    for i in range(m):
        _, Phi = monodromy(f, jac, xs[i], T / m, rtol=rtol, atol=atol)
        M = Phi @ M
    mult = np.linalg.eigvals(M)
    return mult[np.argsort(-np.abs(mult))], M


# -------------------------------------------------------- cycle finding: maps


def find_cycle_map(fmap, jmap, xs0, tol=1e-12, max_iter=60):
    """Newton multi-shooting for an n-cycle of a map (appendix A16 (A16.1)).

    xs0: [n,d] initial guesses for the n periodic points. Returns dict:
    points[n,d], converged, residual.
    """
    xs = np.array(xs0, float, ndmin=2)
    n, d = xs.shape
    for it in range(max_iter):
        R = np.empty(n * d)
        Jbig = np.zeros((n * d, n * d))
        for i in range(n):
            j = (i + 1) % n
            R[i * d:(i + 1) * d] = np.asarray(fmap(xs[i])) - xs[j]
            Jbig[i * d:(i + 1) * d, i * d:(i + 1) * d] = jmap(xs[i])
            Jbig[i * d:(i + 1) * d, j * d:(j + 1) * d] -= np.eye(d)
        rnorm = np.linalg.norm(R)
        if rnorm < tol:
            return {"points": xs, "converged": True, "residual": rnorm}
        xs = xs + np.linalg.solve(Jbig, -R).reshape(n, d)
    return {"points": xs, "converged": False, "residual": rnorm}


def floquet_map(jmap, xs):
    """Multipliers of a map cycle: eigenvalues of the ordered Jacobian product
    M = J(x_n)...J(x_1) (ChaosBook example 5.2)."""
    M = np.eye(xs.shape[1])
    for x in xs:
        M = jmap(x) @ M
    mult = np.linalg.eigvals(M)
    return mult[np.argsort(-np.abs(mult))], M
