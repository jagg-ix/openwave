# OpenWave M9 maturity profile

The current assessment keeps theorem status, numerical closure, state construction, physical identity, calibration, prediction readiness, and implementation evidence separate.

## Headline summary

| Headline | Count |
| --- | ---: |
| Validated in scope | 7 |
| Conditional validated | 5 |
| Reduced-model validated | 3 |
| Calibration pending | 1 |
| Candidate | 4 |
| Negative | 1 |
| **Total** | **21** |

M9.106--M9.108 do not hardcode new headline counts. Their physical sub-gates drive only the relevant axes.

## New axis rules

| Criterion | New evidence | Axis rule | Retained boundary |
| --- | --- | --- | --- |
| Gravity | nonlinear conformal metric, trace curvature, Hamiltonian/momentum constraints, projection | state advances only if the nonlinear constraint gate passes | general 4D Einstein Cauchy development and physical calibration |
| Antimatter/annihilation | particle, antiparticle, electrostatic, and radiation fields | reduced headline retained; coupled-field gate is additional numerical evidence | physical QED annihilation and cross sections |
| Strong force | color-triplet amplitudes and a dynamical flux field | reduced headline retained | non-Abelian Yang-Mills/QCD and hadron spectrum |
| Weak force | left/right flavor fields, mediator, and reservoir | reduced headline retained | electroweak gauge theory and calibrated rates |
| Dark matter | neutral Hartree candidate and perturbation tube | state becomes `stable_constructed` only after the candidate gate | abundance, production, mass scale, phenomenology |
| Quarks/baryons/mesons | color/composite field candidates and perturbation tubes | state follows each candidate gate | QCD identity, spectrum, decays, physical calibration |

## Program-health authority

```text
Physlib head 128974a501d3d0a43108a3ab9a1bd9d4fea5d7db
edges 4528
exact identities 218
untested numerical predictions 0
loaded uncited claims 12
undisclosed loaded claims 0
physical internal-only claims 2
hidden epistemic debt 43
```

A regression in exact identities, untested numerical predictions, undisclosed claims, vocabulary validity, internal-only physical claims, or hidden debt blocks the current authority. Program-health passage is not physical evidence.

## Executed reduced-model results

The standalone NumPy kernels for M9.107 and M9.108 were executed before publication. The committed records under `research/results/` show all three M9.107 coupled-field gates and all four M9.108 candidate-state gates passing their declared tolerances.

M9.106 depends on the complete OpenWave matter/Maxwell stack and must be executed in a repository checkout. No numerical M9.106 outcome is claimed here.
