# CAT/EPT formal interface status

Live formal equation authority: `jagg-ix/entropic-physlib-private`, branch `entropic-physlib-linear-full`.

Current ZIL runtime authority: `jagg-ix/zil-lean`, branch `main`, commit `3c9d4ce962fb9ce0b3284d700e7acaee5fb272bc`.

Lean remains proof authority. ZIL provides orchestration, source, dependency, status, query, provenance, contract, and audit authority. OpenWave provides numerical-model and discretization evidence. None of these layers promotes another automatically.

## Runtime roots

| Root | Current role | Boundary |
| --- | --- | --- |
| `Zil` | PhysLib-facing `Zil.Datalog` compatibility root | not the native standalone graph engine |
| `Zil.Native` | OpenWave facts/rules/parser/query/provenance/workflow/audit runtime | not Lean proof authority |

## Formal-to-numerical interface

| Interface | Lean status | M9.99 numerical status | Boundary |
| --- | --- | --- | --- |
| Complete continuum `H¹(ℝ³)` carrier | directly proved | legacy finite periodic grid retained as numerical carrier | finite torus is not the continuum carrier |
| Target interaction | Hartree/Newton attraction plus supplied local interaction | Hartree term executable as `G=0,0.05,0.10` sweep | no selected dimensionless `G` |
| Cubic--quintic density coercivity | directly proved for `β>0` | local density terms executable | theorem does not select `α` or `β` |
| Minimizer/orbital stability bridges | conditional on model-specific closure data | no charged stationary branch claimed | single coupled action and analytic closure remain open |
| Schrödinger/Pauli kinetic map | nonrelativistic coefficient `1/(2m)` | reconciled with `m_eff=1/(2D)` | no physical mass calibration |
| Four-spinor Clifford algebra | directly proved | exact canonical matrix overlap | interactions and observables remain separate |
| Foldy--Wouthuysen Pauli structure | matrix-level relativistic, Darwin, and spin--orbit carrier | nonlinear self-consistent Pauli PDE remains a different model | no theorem identifying the two Hamiltonians |
| Maxwell implies continuity | directly proved algebraically | shared odd-grid Fourier differential complex | periodic neutralized source differs from isolated/momentum-space carrier |
| Conserved-current-to-Maxwell | conditional on Green inversion | periodic Poisson/Helmholtz inversion executable | no continuum Green/Cauchy construction |
| Distributional point charge | directly proved on `R³` | finite extended periodic source | no point-source identity |
| Radiation-gauge decomposition | directly proved abstractly | exact Fourier Helmholtz projection | decomposition is not nonlinear evolution closure |
| Dirac velocity operator | directly proved as `α` | `d<x>/dt=<α>` measured for pair/control/interaction | no FW packet position projection |
| Momentum/Lorentz force | formal force structures available | M9.97 `2.61%` momentum/Lorentz subreduction retained | no stable pair or calibrated force |
| Direct center acceleration | no exact unprojected Dirac `F=ma` theorem imported | old wrong-sign result retained as diagnostic only | requires FW positive-energy position/nonrelativistic limit |
| Rest-frame Dirac--Pauli precession | directly proved | full Dirac generator remains integration gate | rest-frame bridge is not a moving-packet theorem |
| Rest-frame T-BMT equality | directly proved for rest vertical field | old `266.90%` packet mismatch classified out of domain | covariant local Thomas/BMT reduction open |
| Gauge-invariant Pauli coupling | directly proved structurally | current/moment observables executable | anomaly coefficient and particle identity open |
| Electrogravitic metric/action interfaces | directly proved with explicit premises | not used as the numerical M9.99 stationary equation | full coupled global action/PDE remains open |
| M9.98 ZIL runtime | exact commit/blobs and dual roots | executable authority | promotes no theorem or criterion |
| M9.99 equation contract | exact nine formal blobs and eight OpenWave blobs | fail-closed drift validation | diagnostic map, not an equation derivation |
| M9.99 Fourier geometry | discrete implementation | odd `17³` real grid, one zero mode, exact final Maxwell vector | continuum convergence not yet established |
| M9.99 canonical registration | schema v6 | executable no-promotion authority | status profile unchanged |

## M9.99 discrete reconciliation

The legacy numerical path mixed exact Fourier matter derivatives with centered `sin(kh)/h` Maxwell symbols. M9.99 uses one exact Fourier operator family for gradient, divergence, curl, Laplacian, Poisson inversion, Helmholtz projection, and the gauge-covariant Laplacian.

Real fields use an odd `17 × 17 × 17` operational grid. The historical `16³` winding seed is Fourier-resampled and normalized. Even-grid real exact-Fourier operations fail closed because the self-conjugate Nyquist coefficient would otherwise create an imaginary derivative that cannot be discarded consistently.

Representative private reconstruction:

```text
curl grad maximum             4.4e-16
div curl maximum              0
Laplacian identity error      6.1e-16
Gauss relative residual       8.3e-15
Ampere relative residual      5.9e-15
magnetic divergence maximum   7.8e-16
```

The final stationary residual uses the exact Maxwell vector potential associated with the reported constraints, not the relaxed intermediate vector.

## Retained M9.97 measurements

```text
stationary residual             0.5190695504
momentum/Lorentz error           2.61 percent
center/Lorentz mismatch          114.74 percent, diagnostic outside exact Dirac position theorem
spin/full-generator error        2.57 percent
spin/rest-frame BMT mismatch     266.90 percent, outside moving-packet theorem domain
```

The momentum and full-generator results remain dimensionless subreductions. The center and rest-frame BMT mismatches are not Lean contradictions.

## Explicit retained boundaries

- derive one coupled gauge-spinor-Hartree action;
- select the dimensionless Hartree and gauge coupling map;
- construct a stable charged stationary branch;
- prove continuum/grid convergence of the reconciled operator family;
- construct a Foldy--Wouthuysen packet position projection;
- construct a covariant local packet T-BMT law;
- derive the anomalous moment;
- calibrate physical charge, moment, force, mass, length, and time units;
- complete Maxwell Cauchy, ADM propagation, global coupled development, continuum open-system, constructive-QFT, and withheld-prediction targets.

The platform matrix remains `7 validated / 13 partial / 1 negative`. Magnetic moment/spin, electric force, magnetic force, calibration, and physical particle identity remain unpromoted.
