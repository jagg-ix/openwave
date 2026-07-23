# M9 CAT/EPT roadmap

Research mode is headless first. No `_launcher.py` or visualization port is added
until a three-dimensional field dynamics passes localization and stability gates.

| Task | Deliverable | Status / gate |
| --- | --- | --- |
| M9.1 | Version-pinned formal contract and deterministic conformance suite | DONE; contract passed |
| M9.2 | One-dimensional free complex-field solver and exact Gaussian benchmark | DONE; all 11 gates passed |
| M9.3 | Fixed field-to-probability map and distinct coarse-graining clocks | DONE; all 11 gates passed |
| M9.4 | Bounded nonlinear family and complete localization decision gate | DONE; focusing candidate passed, controls dispersed |
| M9.5 | Energy, radius, phase frequency, scaling family, and Compton-clock comparison | STARTABLE; positive M9.4 |
| M9.6 | Charge/spin carrier survey; no scalar-soliton inference | STARTABLE as a no-go and carrier-selection task |
| M9.7 | Three-dimensional dynamics, then Taichi port and launcher | Gated on a validated 3D extension |

## Completed gates

### M9.1 formal contract

- exact source branch, commit, Lean version, theorem paths, and hypotheses recorded;
- deterministic identities pass at absolute error `<= 1e-12`;
- malformed probability data and negative density are rejected;
- transcription alone earns no phenomenology claim.

### M9.2 free solver

- periodic second-order finite differences and Crank--Nicolson;
- exact Gaussian comparison at `N = 128, 256, 512`;
- phase, density, and current converge at observed order `>= 1.8`;
- norm and discrete energy are conserved to roundoff;
- finest fidelity exceeds `0.9999` with no periodic wraparound.

See [`findings/m9_2_method_note.md`](findings/m9_2_method_note.md).

### M9.3 coarse-graining clock

- fixed cell map `p_i proportional to dx |psi_i|^2`;
- fixed periodic channel `(1/4, 1/2, 1/4)` for 64 depths;
- remaining KL disequilibrium contracts at every depth;
- accumulated discarded information increases at every depth;
- one-step total correlation remains nonnegative;
- the KL ledger closes for both initial and final M9.2 snapshots;
- channel depth is kept separate from physical time.

See [`findings/m9_3_method_note.md`](findings/m9_3_method_note.md).

### M9.4 localization decision

The same normalized `sech` seed is evolved in the frozen family

```text
i psi_t = -1/2 psi_xx + kappa |psi|^2 psi,
kappa in {0, +2, -2}.
```

- free and defocusing members disperse;
- the focusing member `kappa = -2` converges to the exact bright soliton;
- norm, energy, stationary residual, fidelity, tail, shape, and core gates pass;
- the result is stable across three resolutions and three box sizes;
- a fixed 5% shape modulation remains localized through `t = 5`.

Classification: localized neutral mathematical candidate in 1+1 dimensions. It
has no assigned charge, spin, particle species, mass scale, or 3D validation.

See [`findings/m9_4_method_note.md`](findings/m9_4_method_note.md).

## Next gate: M9.5

M9.5 must characterize the scaling family without turning a definition into a
prediction. It should derive and numerically confirm how norm, energy, radius,
and phase frequency scale with the soliton parameter, count every calibration
choice, and state whether any Compton-clock identification is an assumption,
consistency relation, or independent result.
