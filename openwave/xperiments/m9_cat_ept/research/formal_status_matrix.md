# CAT/EPT formal interface status

Live PhysLib authority: `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, base commit `e10af9a3b47bf90afc0a88167a5d495b6935f4dc`, exact current tree `239a663a3192a3144fb998e7bb200e09689a3bb9`.

OpenWave imports:

- current `Physlib.lean` blob `182a06e0f50314ec54436da602b4ac86eba4ee08`;
- 24 exact Lean aggregate/source blobs in the branch-wide inventory;
- 11 ZIL graphs with 422 entity identifiers;
- 12 explicit open, constructive-QFT, or external-analytic boundaries;
- two current-tree M9.96 sources for Pauli--Maxwell and conserved-current/Maxwell closure;
- three current-tree M9.97 dynamics sources for rest-frame spin precession, electromagnetic particle dynamics, and distributional point-charge fields.

Lean remains proof authority. ZIL remains the dependency, source, status, rule, and query graph. Criterion-specific overlays add exact witnesses without changing the 11-graph corpus count.

| Interface | Status | Boundary |
| --- | --- | --- |
| Complete continuum `H¹(ℝ³)` carrier and free Schrödinger group | directly proved | genuine infinite-dimensional carrier |
| Global conservative certificate, compact minimizing orbit, and identified branch | directly present / adapted | neutral scalar branch; physical identity remains separate |
| Winding charge additivity and conjugation | directly proved | charge-unit interpretation is separate |
| Integer winding-charge sector iff `3 | n` | directly proved | spontaneous sector selection is not derived |
| Fock-space scalar charge grading | directly proved | operator grading does not calibrate electric charge |
| Free massive Klein--Gordon mode group | directly proved | free mode, not interacting QFT |
| Coulomb endpoint and `O(4)/S³` Gegenbauer harmonics | directly proved | formal angular sector, not calibrated atoms |
| Pauli spin tensor and Dirac/FW structure | directly proved | operator structure does not identify a particle |
| Tree-level `g=2` and Schwinger structural identity | directly proved structurally | the loop computation of `F₂(0)` is not inherited |
| Spin-projector/magnetic-moment link | directly proved in M9.96 overlay | operator equality, not a stationary-state theorem |
| Gauge-invariant Pauli coupling `σF` and Dirac/anomalous split | directly proved in M9.96 overlay | anomaly coefficient remains structural input |
| Maxwell implies continuity | directly proved | momentum/coordinate carrier, not a solved finite packet by itself |
| Conserved-current-to-Maxwell construction | conditional on Green inversion | analytic Green input remains explicit |
| Maxwell stress source gauge invariance | directly proved | does not independently prove packet acceleration |
| Rest-frame Dirac--Pauli precession | directly proved in M9.97 overlay | rest-frame dipole Hamiltonian |
| Rest-frame T-BMT rate equals Dirac--Pauli rate | directly proved in M9.97 overlay | covariant boost, Thomas term, and moving-packet reduction remain open |
| QED coupling and force-law chain | structurally proved | Schwinger value is supplied; loop derivation remains open |
| Exact Coulomb potential and symmetry | directly proved | ideal point-particle carrier, not a finite winding-state identity |
| Radiation-gauge Helmholtz decomposition | directly proved | longitudinal/transverse decomposition is not a complete nonlinear evolution theorem |
| Distributional 3D point-charge electric field and Gauss source | directly proved | distributional point source, not a calibrated extended particle |
| Lorentz-EM superoperator decomposition and covariance | directly proved | does not supply a calibrated dipole force law |
| Yukawa screening and Coulomb upper bound | directly proved | potential identity, not physical charge calibration |
| Global electrogravitic action and metric-built equations | directly proved with explicit scope | full nonlinear global coupled certificate remains open |
| Eddington affine first integral and Einstein-Λ recovery | directly proved algebraically | finite-index first integral assumes the connection equation |
| Torsion-vacuum and Lovelock first-integral bridges | directly proved with scope | full variational/Cauchy theory is not reconstructed |
| Maxwell Green solutions | conditional on analytic data | concrete well-posed Cauchy data not constructed end to end |
| Local nonlinear complex-Einstein evolution/uniqueness | conditional on analytic data | local fixed-gauge result, not maximal global development |
| Liouville continuum carrier | provided by existing API | continuum generator and semigroup remain open |
| LDDL finite generator/evolution and transport declarations | implementation declared / pending CI in ZIL | ZIL status is not kernel proof promotion |
| Cauchy weak zero-width limit declarations | pending CI in ZIL | distributional limit tokens are not promoted by import |
| LDDL trace preservation | pending CI in ZIL | trace-zero tokens remain pending until kernel/CI confirmation |
| Rivers finite and continuum Green-function graphs | mixed checked, pending, and constructive-QFT boundaries | coincident products and interacting continuum measure remain open |
| Lovelock--Rund graphs | source and declaration inventory | graph presence is not an independent kernel audit |
| Veliev periodic-Schrödinger graph | formal declarations plus external analytic requirement | arbitrary-order error estimates remain external |
| M9.94 branch-wide formal import | OpenWave executable | faithful status import; no criterion promotion |
| M9.94 spin-magnetic bridge | OpenWave executable | tree `g=2`; Gaussian control, anomaly, and identity remain open |
| M9.95 electric/magnetic bridge | OpenWave executable | declared winding pair and supplied kernels |
| M9.96 charged stationary feasibility | OpenWave negative model subresult | zero passing scalar charged stationary candidates |
| M9.96 charged Maxwell source | OpenWave executable | static Maxwell constraints and moment response close; no backreacted stationary branch |
| M9.96 field-force triangle | OpenWave executable | Lorentz, energy-gradient, and stress-flux agree within `2.6%`; no PDE center response |
| M9.97 gauge-spinor stationary audit | OpenWave executable negative model subresult | winding, spin, localization, and Maxwell constraints close; residual ends at `0.519` |
| M9.97 four-spinor momentum response | OpenWave executable | momentum/Lorentz error `2.61%`; no stable pair |
| M9.97 four-spinor center response | OpenWave failed reduction | center response has the wrong sign and `114.74%` relative mismatch |
| M9.97 exact-generator spin response | OpenWave executable | finite-time/generator error `2.57%` |
| M9.97 rest-frame T-BMT shadow | OpenWave failed reduction | moving winding packet differs by `266.90%` and opposite transverse sign |
| M9.97 dynamics authority | OpenWave executable | preserves all three partial statuses and blocks physical identity |

## Imported operational/status ZIL graphs

1. electrogravitic action closure;
2. Lindblad-driven leads;
3. Liouville second quantization;
4. Cauchy weak limit;
5. Lindblad trace preservation.

## Imported formalization-corpus ZIL graphs

6. Rivers scalar Green functions;
7. Rivers scalar Green functions -- continuum extension;
8. Lovelock--Rund continuum variational structure;
9. Lovelock--Rund pointwise operators;
10. Lovelock--Rund invariant geometry;
11. Veliev periodic Schrödinger perturbation theory.

## M9.97 evidence boundary

Closed dimensionless subreductions:

- field-derived winding-three and exact-third charge;
- self-consistent periodic Maxwell constraints;
- current-integral versus weak-field-response magnetic moment;
- M9.96 Lorentz/energy/stress force triangle;
- four-spinor kinetic-momentum transfer versus Lorentz force within `2.61%`;
- finite-time spin evolution versus the exact numerical Dirac generator within `2.57%`.

Open or rejected reductions:

- charged spinorial stationary residual (`0.519` versus `0.10` gate);
- center response sign and magnitude;
- rest-frame T-BMT reduction for the moving extended winding packet;
- full covariant Thomas/BMT dynamics;
- anomalous-moment derivation;
- common physical calibration and withheld predictions.

## Explicit retained boundaries

- independently varied coupled gauge-spinor action;
- stable charged spinorial stationary branch;
- converged momentum/center relation;
- covariant moving-packet spin and torque law;
- physical charge, moment, force, mass, length, and time calibration;
- concrete Maxwell Cauchy construction;
- concrete ADM constraint propagation;
- maximal globally hyperbolic coupled development;
- global nonlinear coupled-action certificate;
- continuum hybridization and LDDL-current convergence;
- genuinely infinite-particle representation;
- continuum Lindblad generator and Fokker--Planck bridge;
- continuum coincident-product regularization;
- interacting continuum scalar measure;
- arbitrary-order periodic-Schrödinger error estimates;
- out-of-sample physical predictions.

The platform matrix remains `7 validated / 13 partial / 1 negative`. M9.97 closes momentum transfer and exact-generator spin integration, but rejects stationary, center-response, and rest-frame T-BMT reductions for the current model. Magnetic moment/spin, electric force, magnetic force, calibration, and physical particle identity remain unpromoted.
