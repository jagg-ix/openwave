# M9.56 task: unified nonlinear continuum-to-grid convergence

Evolve the same coupled CAT/EPT initial state on nested 32, 64, 128, and 256 point spectral grids with a common time step. Lift each final state to the finest grid and require decreasing aggregate errors across matter, density, gauge, geometry, temperature, and reservoir fields. Preserve matter/reservoir, thermal/loss, and gauge/work ledgers, positive temperature, and monotone entropy. Report finite-grid convergence only; do not claim construction of or convergence to a continuum solution.
