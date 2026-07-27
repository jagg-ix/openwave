# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.123**. Stable callers should use:

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
launcher      openwave/xperiments/m9_cat_ept/_launcher.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v26
openwave.m9.platform-integration-contract.v6
```

The historical 21-criterion particle-oriented maturity headlines remain those of M9.109. M9.123 adds a separate non-particle scope profile and does not rewrite those rows.

## Authorities

```text
Physlib repository    jagg-ix/entropic-physlib-private
merged branch         master
development branch    private/entropic-physlib-linear-full
merged Physlib head   80c2b0bb25ba0b28d2c3dd8b038071e0f49261ef
Physlib root blob     f953c09c428eb83d9894c1944e1fd44a7ffe95a1
public zil-lean head  c671f02d8b6dcf7ba689afc86477ff7e35465c35
```

M9.123 pins eleven theorem/runtime surfaces spanning entropic clocks, Born reconstruction, Schrödinger/Ehrenfest interfaces, local-time Fokker--Planck and kinetic control, complex-Einstein proper time, metric-built electrogravity, Stokes dissipation, open-system spectral limits, and stratified ZIL auditing.

## Why the scorecard changed

CAT/EPT has not primarily focused on particle masses and hadron spectroscopy. The audit therefore targets entropic time, quantum reconstruction, open systems, stochastic/kinetic dynamics, gravity, electromagnetism/AQFT, thermodynamics, and fluid dissipation.

particle spectroscopy is not the primary scorecard. Particle incompleteness still limits universal-unification claims, but it no longer obscures non-particle theorem and dynamics coverage.

## M9.123a scope profile

```text
strong internal       3
conditional internal  1
reduced internal      2
interface internal    1
structural internal   1
```

These counts summarize the declared eight-domain profile. They are not a universal scientific score.

## M9.123b executable controls

```text
dissipative relative-entropy clock versus unitary frozen clock
positive-imaginary-energy proper-time clock
local-time Fokker--Planck current/drift-diffusion equivalence
free kinetic Kolmogorov bracket and covariance positivity
finite Fourier Stokes energy/enstrophy balance
one-screen weak-gravity scale, flux, and test-mass consistency
```

## M9.123c explanatory scope

The broad internal modeling gate passes. The predictive fundamental theory gate remains blocked on:

```text
single universal action or generator
independent parameter fixing
end-to-end continuum dynamics
cross-domain held-out prediction
```

Current decisions:

```text
broad non-particle formal coverage                 constructed
six non-particle executable controls               passed
particle spectroscopy primary scorecard            false
broad internal physics modeling                    ready
single-mechanism explanatory compression           not established
independent physical calibration                    open
held-out external validation                        open
predictive fundamental theory                       not ready
external physical promotion                         blocked
```

## Reproduction

```bash
python openwave/xperiments/m9_cat_ept/research/scripts/m9_123a_physics_scope.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_123b_nonparticle_benchmark.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_123c_explanatory_scope.py
python openwave/xperiments/m9_cat_ept/research/scripts/m9_123_current_registration.py
```

A formal theorem map is not a unique physical explanation. A deterministic control case is not an independently calibrated prediction. Broad internal modeling does not establish a predictive fundamental theory.
