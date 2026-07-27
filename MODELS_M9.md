# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.124**.

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v27
openwave.m9.platform-integration-contract.v7
```

## The three clock roles

The entropic-physlib theorem graph does not contain one theorem saying that Page-Wootters, modular, and entropic time are the same number. It contains three distinct physical roles and pairwise bridges.

| Clock | Physical question | Generator/evolution | Reversibility |
| --- | --- | --- | --- |
| Page-Wootters relational clock | Relative to which clock reading is the system state described? | condition a stationary system-clock history state; conditional Hamiltonian or Hamiltonian+GKSL generator | neutral: reversible or dissipative depending on the conditioned generator |
| modular / thermal clock | Which intrinsic reversible flow is selected by the state? | `K = -log rho`, `U(s)=exp(-iKs)`, isospectral conjugation | reversible; von Neumann entropy preserved |
| entropic / irreversible clock | How much irreversible change has accumulated? | relative-entropy contraction or nonnegative GKSL jump rate | irreversible; freezes at vanishing dissipation |

### Page-Wootters

Page-Wootters supplies **relational ordering**. The global state may satisfy a stationary Hamiltonian constraint while conditional system states change with the clock subsystem's reading. The formal source also permits a dissipative conditional generator

```text
d rho_S / d tau = -(i/hbar)[H_S,rho_S] + L_S(rho_S),
```

whose unitary limit is recovered when `L_S = 0`.

### Modular flow

Modular time supplies a **state-dependent reversible thermal flow**. For a faithful state or Gibbs reference,

```text
K = -log rho,
U(s) = exp(-i K s).
```

The flow is isospectral and entropy preserving. At a Gibbs state, `K = beta H + log(Z) I`, so modular flow agrees with Hamiltonian evolution after the explicit rescaling `t = beta s`.

### Entropic time

Entropic time supplies the **irreversible arrow**. Negative real spectral rates contract amplitudes, GKSL jump operators give a nonnegative dissipation rate, and relative entropy to equilibrium decreases while accumulated entropy production increases. At equilibrium the dissipative rate vanishes and the entropic clock freezes.

## Pairwise bridges

```text
Page-Wootters <-> entropic:
  conditioned GKSL evolution and nonnegative conditional entropic rate

modular <-> entropic:
  static entropy/modular bridge plus dynamical orthogonality and complementarity

Page-Wootters <-> modular:
  possible when the conditioned system generator is explicitly identified with K
```

None of these bridges makes the three parameters transitively identical.

## M9.124 numerical controls

The benchmark checks:

```text
Page-Wootters  normalized history state, exact conditioning, equal marginal entropies
modular         Gibbs identity K = beta H + log(Z)I, isospectral flow, entropy preservation
entropic        monotone accumulated relative-entropy clock, semigroup composition, population change
```

These are deterministic reduced controls, not clock experiments or independent calibration.

## Formal authority

```text
merged Physlib baseline   master@80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef
development clock source  entropic-physlib-linear-full@af78ea63ee0b39456d8dab023761482196b8c172
public zil-lean            c671f02d8b6dcf7ba689afc86477ff7e35465c35
```

The three clock files are recorded as development-branch sources. OpenWave does not relabel them as merged `master` authority and claims no new Lean proof.

## Current decision

```text
three distinct clock roles                    established internally
three pairwise bridge surfaces                registered
Page-Wootters conditioning control            passed
modular Gibbs-flow control                     passed
entropic relaxation control                    passed
single common clock carrier                    missing
constraint-to-conditioned dynamics theorem    incomplete
PW/modular/entropic parameter calibration      missing
proper-time calibration across all clocks      missing
held-out three-clock validation                missing
single unified physical clock                  not established
```

A three-aspect time framework is not the same as one universal clock theorem.
