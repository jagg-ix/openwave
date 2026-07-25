# CAT/EPT formal interface status

Live PhysLib authority: `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`, base commit `e10af9a3b47bf90afc0a88167a5d495b6935f4dc`, exact current tree `239a663a3192a3144fb998e7bb200e09689a3bb9`.

Current ZIL runtime authority: `jagg-ix/zil-lean`, branch `main`, commit `3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc`.

OpenWave imports:

- current `Physlib.lean` blob `182a06e0f50314ec54436da602b4ac86eba4ee08`;
- 24 exact Lean aggregate/source blobs in the branch-wide inventory;
- 11 formalization/status ZIL graphs with 422 entity identifiers;
- 12 explicit open, constructive-QFT, or external-analytic boundaries;
- two M9.96 sources for Pauli--Maxwell and conserved-current/Maxwell closure;
- three M9.97 dynamics sources for rest-frame spin precession, electromagnetic particle dynamics, and distributional point-charge fields;
- six exact upstream ZIL runtime/build/example blobs;
- four exact OpenWave native `.zc` graph blobs.

Lean remains proof authority. The ZIL runtime is orchestration, dependency, source, status, query, provenance, and formalization-contract authority. Runtime availability never promotes a Lean theorem or a physical criterion.

## ZIL dual-root authority

| Root | Current role | Boundary |
| --- | --- | --- |
| `Zil` | PhysLib-facing `Zil.Datalog` compatibility root: attachments, attributes, embedded validation, `Holds`, tactics, theorem intents, file contracts | not the native standalone graph engine |
| `Zil.Native` | facts, theorem-shaped rules, native parser/query/provenance/workflow/authorization/audits for OpenWave `.zc` graphs | not Lean proof authority |

The current `lakefile.lean` builds both roots as default library roots. The historical revisions `f39758f85ee6300b8060e4f8ea1ecf344ed32c96` and `64462a3c5e2ffb51a7b226675491cc3a9b156a8d` remain recorded only as historical M9.63 and M9.62 evidence pins.

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
| Radiation-gauge Helmholtz decomposition | directly proved | decomposition is not a complete nonlinear evolution theorem |
| Distributional 3D point-charge electric field and Gauss source | directly proved | distributional point source, not a calibrated extended particle |
| Global electrogravitic action and metric-built equations | directly proved with explicit scope | full nonlinear global coupled certificate remains open |
| Eddington affine first integral and Einstein-Λ recovery | directly proved algebraically | finite-index first integral assumes the connection equation |
| Maxwell Green solutions | conditional on analytic data | concrete well-posed Cauchy data not constructed end to end |
| LDDL and Cauchy/status graphs | mixed implementation, checked, pending, and conditional states | ZIL status is not kernel proof promotion |
| Rivers/Lovelock--Rund/Veliev corpus graphs | source/declaration/status inventory | graph presence is not an independent kernel audit |
| M9.96 field-source and force evidence | OpenWave executable | no stable charged stationary branch or PDE center response |
| M9.97 gauge-spinor stationary audit | OpenWave negative model subresult | residual ends at `0.519` |
| M9.97 four-spinor momentum response | OpenWave executable | momentum/Lorentz error `2.61%`; no stable pair |
| M9.97 center response | OpenWave failed reduction | wrong sign and `114.74%` relative mismatch |
| M9.97 exact-generator spin response | OpenWave executable | finite-time/generator error `2.57%` |
| M9.97 rest-frame T-BMT shadow | OpenWave failed reduction | `266.90%` mismatch and opposite transverse sign |
| M9.98 current ZIL runtime | OpenWave executable authority | exact commit/blobs and dual-root roles; promotes no claim |

## Imported formalization/status ZIL corpus

Operational graphs:

1. electrogravitic action closure;
2. Lindblad-driven leads;
3. Liouville second quantization;
4. Cauchy weak limit;
5. Lindblad trace preservation.

Formalization-family graphs:

6. Rivers scalar Green functions;
7. Rivers scalar Green functions -- continuum extension;
8. Lovelock--Rund continuum variational structure;
9. Lovelock--Rund pointwise operators;
10. Lovelock--Rund invariant geometry;
11. Veliev periodic Schrödinger perturbation theory.

These are PhysLib declaration/status graphs and remain separate from the four OpenWave native M9 `.zc` graphs assigned to `Zil.Native`. The M9.98 graph declares its own native-root role, while its exact blob is pinned externally by the current runtime overlay.

## M9.98 runtime boundary

The runtime upgrade closes:

- exact current ZIL commit identity;
- separate PhysLib Datalog and OpenWave native root roles;
- exact upstream root, compatibility, contract, build, and example blobs;
- exact OpenWave M9.94--M9.98 graph blobs;
- historical-pin classification;
- deterministic runtime fingerprint and fail-closed drift checks.

It does not close:

- any Lean theorem proof obligation;
- charged spinorial stationarity;
- center-response convergence;
- covariant moving-packet spin dynamics;
- anomalous-moment derivation;
- common physical calibration or withheld predictions.

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

The platform matrix remains `7 validated / 13 partial / 1 negative`. M9.98 upgrades ZIL runtime authority and contract validation without changing M9.97 physics evidence. Magnetic moment/spin, electric force, magnetic force, calibration, and physical particle identity remain unpromoted.
