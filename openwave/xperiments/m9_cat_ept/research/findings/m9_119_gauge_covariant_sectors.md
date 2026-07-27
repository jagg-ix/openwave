# M9.119 gauge-covariant sector findings

## Question

Can the reduced M9.107 strong and weak carriers be replaced by finite systems with an actual local gauge transformation law while preserving honest boundaries against QCD and complete electroweak claims?

## Repository audit

The earlier strong carrier evolved color amplitudes against one real scalar flux field. The earlier weak carrier evolved flavor amplitudes against one complex mediator and a scalar reservoir. Neither model carried group-valued links, plaquettes, Wilson loops, or an exact local matter/link covariance test.

The current `entropic-physlib-linear-full` branch supplies the appropriate formal interfaces:

- finite Wilson action and partition/expectation identities;
- Wilson-loop and area-law observable formulas;
- `GaugeGroupI = SU(3) × SU(2) × U(1)`;
- unitary U(1) and fundamental SU(2) representations;
- a Higgs doublet with unitary gauge action and gauge-orbit norm characterization;
- the quartic Higgs potential and vacuum-norm identity.

Physlib also explicitly leaves complete Standard Model fermion content open. OpenWave therefore targets gauge-covariant finite bosonic/matter carriers rather than claiming QCD or the complete Standard Model.

## M9.119a — local SU(3) carrier

The numerical carrier uses complex triplet matter on a periodic 2D lattice and group-valued SU(3) links. It implements:

```text
psi(x) -> Omega(x) psi(x)
U_mu(x) -> Omega(x) U_mu(x) Omega(x+mu)^dagger
```

with a covariant lattice Laplacian, gauge-covariant matter diffusion, a covariant link response, plaquettes, and rectangular Wilson loops.

The campaign requires:

- matter kinetic action invariance;
- Wilson action and plaquette-trace invariance;
- color-Casimir invariance;
- 1x1 and 2x1 Wilson-loop invariance;
- covariance of the complete matter/link trajectory;
- special-unitary links throughout evolution;
- a nonzero non-Abelian commutator.

Representative independent reconstruction produced errors near floating-point precision:

```text
kinetic gauge relative error             1.18e-16
Wilson gauge relative error              2.58e-13
maximum matter trajectory error          4.37e-16
maximum link trajectory error            2.45e-15
maximum link unitarity error             1.09e-14
maximum determinant error                8.44e-15
non-Abelian commutator norm               4.48e-02
```

Finite Wilson loops were constructed, but no area-law fit or continuum/volume scaling was executed. Confinement remains open.

## M9.119b — local SU(2)xU(1) Higgs carrier

The electroweak carrier uses a complex Higgs doublet, SU(2) links, and U(1) phases. Its local action matches the Physlib Higgs convention:

```text
phi -> u^3 g phi
```

where `g in SU(2)` and `u in U(1)`. The carrier includes a covariant lattice Laplacian, gauge-covariant matter/link update, separate SU(2) and U(1) Wilson actions, and the quartic potential

```text
V(phi) = -mu^2 |phi|^2 + lambda |phi|^4.
```

The declared vacuum norm is

```text
|phi|^2 = mu^2/(2 lambda).
```

The campaign verifies:

- kinetic, potential, SU(2)-Wilson and U(1)-Wilson gauge invariance;
- covariance of Higgs, SU(2)-link and U(1)-link trajectories;
- preservation of SU(2) and U(1) constraints;
- monotone flat-link relaxation toward the declared quartic vacuum orbit;
- a residual U(1) stabilizer for the canonical vacuum orientation.

Representative independent reconstruction produced:

```text
kinetic gauge relative error             1.91e-16
SU(2) Wilson gauge relative error        3.06e-15
U(1) Wilson gauge relative error         7.70e-16
maximum Higgs trajectory error           2.62e-16
maximum SU(2) trajectory error           1.38e-15
maximum U(1) trajectory error            2.06e-16
vacuum relative error                    3.69e-03
residual subgroup error                  2.66e-16
```

The system has no full chiral fermion multiplets, Yukawa sector, calibrated couplings, Weinberg-angle derivation, or physical W/Z/Higgs spectrum.

## Decision

```text
local SU(3) link carrier                  constructed
covariant color-matter evolution         constructed
finite Wilson observables                constructed
QCD confinement                          not established
local SU(2)xU(1) link carrier            constructed
covariant Higgs-doublet evolution        constructed
quartic Higgs vacuum orbit               constructed
complete electroweak theory              not established
physical gauge-sector calibration        open
```

M9.119 closes the architectural gap between scalar mediator reductions and finite local gauge systems. It does not close the physics gap to QCD, the full Standard Model, calibrated spectra, decays, or experimental validation.
