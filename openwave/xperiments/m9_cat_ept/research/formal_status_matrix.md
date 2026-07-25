# CAT/EPT formal interface status

Live PhysLib authority: `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, base commit `e10af9a3b47bf90afc0a88167a5d495b6935f4dc`, exact current tree `239a663a3192a3144fb998e7bb200e09689a3bb9`.

OpenWave imports:

- the current `Physlib.lean` module-index blob `182a06e0f50314ec54436da602b4ac86eba4ee08`;
- 24 exact Lean aggregate/source blobs in the branch-wide inventory;
- 11 ZIL graphs with 422 entity identifiers;
- 12 explicitly open, constructive-QFT, or external-analytic boundaries;
- two criterion-specific current-tree sources for Pauli--Maxwell and conserved-current/Maxwell closure;
- criterion bindings for magnetic moment/spin, electric force, magnetic force, and gravity.

Lean remains proof authority. ZIL remains the dependency, source-traceability, status, rule, and query graph. The M9.96 current-tree overlay adds exact witnesses without changing the 11-graph corpus count.

| Interface | Status | Boundary |
| --- | --- | --- |
| Complete continuum `H¹(ℝ³)` carrier and free Schrödinger group | directly proved | genuine infinite-dimensional carrier |
| Global conservative certificate, compact minimizing orbit, and identified branch | directly present / adapted | neutral scalar branch; physical identity remains separate |
| Winding charge additivity and conjugation | directly proved | charge unit interpretation is separate |
| Integer winding-charge sector iff `3 | n` | directly proved | spontaneous sector selection is not derived |
| Fock-space scalar charge grading | directly proved | operator grading does not calibrate electric charge |
| Free massive Klein-Gordon mode group | directly proved | free mode, not interacting QFT |
| Coulomb endpoint and `O(4)/S³` Gegenbauer harmonics | directly proved | formal angular sector, not calibrated atoms |
| Pauli spin tensor involution and Dirac-energy compatibility | directly proved | operator structure does not identify an electron |
| Pauli vector/spin-orbit/Foldy-Wouthuysen structure | directly proved | c-number external-field reduction, not full particle dynamics |
| Tree-level `g=2` and Schwinger structural identity | directly proved structurally | Schwinger anomaly imported, not derived from CAT/EPT particle |
| Spin-projector/magnetic-moment operator link | directly proved in current-tree overlay | operator equality, not a charged stationary-state theorem |
| Gauge-invariant Pauli coupling `σF` and Dirac/anomalous split | directly proved in current-tree overlay | anomaly coefficient remains structural input |
| Maxwell-implies-continuity | directly proved | momentum/coordinate carrier; not a solved particle source by itself |
| Conserved-current-to-Maxwell construction | conditional on Green inversion | analytic Green input remains explicit |
| Maxwell stress source gauge invariance | directly proved | does not by itself provide particle acceleration |
| Lorentz-EM superoperator decomposition and covariance | directly proved | does not supply a calibrated dipole force law |
| Yukawa screening and Coulomb upper bound | directly proved | potential identity, not physical charge calibration |
| Global electrogravitic action and metric-built field-equation interfaces | directly proved with explicit scope | full nonlinear global coupled certificate remains open |
| Eddington affine first integral and Einstein-Λ recovery | directly proved algebraically | finite-index first integral assumes the connection field equation; no calibrated global gravity evolution |
| Torsion-vacuum contorsion elimination and Lovelock first-integral bridge | directly proved with scope | does not reconstruct the full variational/Cauchy theory |
| Maxwell Green solutions | conditional on analytic data | concrete well-posed Cauchy data not constructed end to end |
| Local nonlinear complex-Einstein evolution/uniqueness | conditional on explicit analytic data | local fixed-gauge result, not maximal global development |
| Liouville continuum carrier | provided by existing API | continuum generator and semigroup remain open |
| LDDL finite generator/evolution and transport declarations | implementation declared / pending CI in ZIL | ZIL status is not kernel proof promotion |
| Cauchy weak zero-width limit declarations | pending CI in ZIL | distributional limit tokens are not promoted by import |
| LDDL trace-preservation declarations | pending CI in ZIL | trace-zero proof tokens remain pending until kernel/CI confirmation |
| Rivers scalar Green-function finite/QFT graph | mixed kernel-checked, pending-CI, and open constructive-QFT boundaries | continuum coincident products and interacting continuum measure remain open |
| Rivers continuum Green-function graph | mixed kernel-checked and pending-kernel states | pointwise/distributional/trace-log claims retain their recorded status |
| Lovelock–Rund variational and invariant-geometry graphs | source and declaration inventory | graph presence is not an independent kernel audit |
| Veliev periodic-Schrödinger graph | formal declarations plus external analytic requirement | arbitrary-order error estimates remain externally analytic |
| M9.94 formal inventory import | OpenWave executable | imports status faithfully; promotes no criterion |
| M9.94 canonical spin-magnetic bridge | OpenWave executable | tree `g=2`; Gaussian control, anomalous moment, and electron identity remain open |
| M9.95 canonical electric/magnetic force bridge | OpenWave executable | declared winding pair and supplied kernels; charged stationary branches and units remain open |
| M9.96a charged stationary feasibility | OpenWave executable negative model subresult | winding-three seeds exist; selected scalar action has zero passing charged stationary candidates |
| M9.96b charged Maxwell source bridge | OpenWave executable | projected Gauss/Ampere, `div B`, and current/response moment close; no backreacted stationary branch |
| M9.96c field-force triangle | OpenWave executable | Lorentz, energy-gradient, and stress-flux forces agree within 2.6%; no full-PDE center acceleration |
| M9.96 current evidence authority | OpenWave executable | supersedes stale SHA-only evidence for new decisions; promotes no criterion |

## Imported operational/status ZIL graphs

1. electrogravitic action closure;
2. Lindblad-driven leads;
3. Liouville second quantization;
4. Cauchy weak limit;
5. Lindblad trace preservation.

## Imported formalization-corpus ZIL graphs

6. Rivers scalar Green functions;
7. Rivers scalar Green functions — continuum extension;
8. Lovelock–Rund continuum variational structure;
9. Lovelock–Rund pointwise operators;
10. Lovelock–Rund invariant geometry;
11. Veliev periodic Schrödinger perturbation theory.

## M9.96 current-tree evidence boundary

The field-derived winding candidate closes:

- exact winding-three and third-charge arithmetic;
- integrated charge;
- periodic projected Gauss law;
- static Ampere law;
- magnetic divergence;
- current-integral versus weak-field-response magnetic moment;
- electric and magnetic contributions to a Lorentz/energy/stress force triangle.

It does not close:

- a stable charged stationary branch;
- self-consistent gauge or spinorial stationarity;
- full coupled-PDE center acceleration;
- torque or spin precession on a stable pair;
- anomalous-moment derivation;
- physical charge, moment, force, length, or time calibration.

## Explicitly retained boundaries

- self-consistent gauge/spinorial charged stationary equation;
- full coupled-PDE center acceleration;
- full coupled-PDE torque and spin precession;
- physical charge and force calibration;
- concrete Maxwell Cauchy construction from global hyperbolicity;
- concrete ADM constraint propagation;
- maximal globally hyperbolic coupled development;
- concrete global nonlinear coupled-action certificate;
- Lorentz-sum convergence to continuum hybridization;
- LDDL-current convergence to continuum current;
- genuinely infinite-particle representation;
- continuum Lindblad generator;
- phase-space Fokker-Planck bridge;
- continuum coincident field products require external regularization;
- interacting continuum scalar measure remains a constructive-QFT boundary;
- arbitrary-order periodic-Schrödinger error estimates remain externally analytic.

The platform matrix remains `7 validated / 13 partial / 1 negative`. M9.96 strengthens magnetic moment, electric force, and magnetic force from detached controls to field-derived consistency, but the missing stable charged branch and missing full-PDE acceleration/torque/precession prevent promotion.
