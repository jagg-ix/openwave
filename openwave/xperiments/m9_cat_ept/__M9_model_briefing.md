# M9 CAT/EPT: Entropic Particle Dynamics

M9 covers all 21 comparison criteria and now includes cross-repository evidence control, structural and numerical selection of the binding action, a coercive spatial cubic--quintic continuum bridge, and the first frozen out-of-sample physical prediction.

## Platform status

- Zero criteria are fully validated in-platform.
- Twenty criteria are partial or bounded.
- One criterion remains an honest negative: the predictive lepton-mass hierarchy.
- Particle stability remains partial. M9.63 selects a coefficient pair under two declared self-consistency conditions and confirms the branch on three grids. M9.64 adds an exact coercive energy lower bound, nested mass/energy-stable spatial flow, and bounded small scale perturbations. A kernel theorem for every `H¹` perturbation and a physical-particle identification remain open.
- M9.65 freezes one quantitative prediction before external comparison: `omega_breath / omega_Compton = 2.634371114527`, with a 5% preregistered failure threshold. The prediction is not tested or validated.

## Cross-repository sources

| Repository | Ref | Pinned revision | Authority |
| --- | --- | --- | --- |
| `jagg-ix/openwave` | `main` | `421c962fdaa4aa7359c00cd6b37f985d297f0dac` | simulation evidence |
| `jagg-ix/entropic-physlib-private` | `entropic-physlib-linear-full` | `54b4ced090b200fac7ff04ee6a7e8797f1263049` | Lean theorem authority |
| `jagg-ix/zil-lean` | `main` | `f39758f85ee6300b8060e4f8ea1ecf344ed32c96` | evidence orchestration and test/install infrastructure |

## Latest formal changes consumed

- Exact global positive-time flow and norm contraction for the unique irreversible cubic continuum sector.
- Exact fixed spatial multiplication-energy phase coupled to the cubic continuum flow.
- Maximal dissipativity and explicit contraction `C₀` semigroups for homogeneous damping and phase-plus-damping sectors.
- Stronger free kinetic Kolmogorov kernel/PDE identities.

These strengthen the cubic and homogeneous continuum sectors. They do not prove the selected spatial differential cubic--quintic PDE or arbitrary-`H¹` orbital stability.

## Latest closures

- **M9.63:** `alpha = 74.6630446265` and `beta = 415.7483217224` are uniquely selected by density-minimum/peak matching plus reference-scale stationarity. The conditions are explicit model assumptions, not derived physical axioms. The pair retains localization on 12³, 14³, and 16³ campaigns.
- **M9.64:** `V(rho) >= -(3 alpha²/(16 beta)) rho` gives a coercive `H¹` a-priori bound. Nested 16³/20³/24³ spectral evolution preserves mass and energy numerically, refines, and keeps the preregistered small scale orbit bounded. The full kernel theorem remains open.
- **M9.65:** the Gaussian collective coordinate yields the frozen prediction `omega_breath = 2.634371114527 m c² / hbar`, independent of the dispersion normalization under the M9.63 rule. No external data were used and no agreement is claimed.

ZIL records identities, receipts, scope, and evidence-state transitions. Lean remains proof authority; OpenWave remains simulation software.

## Next critical targets

1. M9.66 derive or reject the two M9.63 self-consistency conditions from the full coupled CAT/EPT action and clock sector.
2. M9.67 kernel-formalize the spatial cubic--quintic `H¹` evolution, compactness modulo phase/translation, and orbital stability.
3. M9.68 execute an independent higher-fidelity or external comparison of the frozen M9.65 prediction without changing its value or tolerance.
