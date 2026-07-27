# OpenWave M9 CAT/EPT current comparison profile

M9 is integrated through **M9.126**.

```text
conformance   openwave/xperiments/m9_cat_ept/model_conformance_current.py
registration  openwave/xperiments/m9_cat_ept/model_registration_current.py
```

Current schemas:

```text
openwave.m9.models-conformance.v22
openwave.model-registration.v29
openwave.m9.platform-integration-contract.v9
```

## Existing experimental papers recognized

The strongest ready empirical registry is Planckian dissipation:

- Bruin et al. 2013: five materials, ratios 0.3, 0.7, 0.5, 1.0, 0.4;
- Legros et al. 2019: two overdoped cuprates, ratios 1.1 and 1.0;
- Cao et al. 2020: magic-angle bilayer graphene, ratio 0.7.

The measured dimensionless observable is `R = tau_tr * k_B * T / hbar`. Physlib's preregistered broad Planckian band is `0.1 < R < 10`.

## M9.126a — evidence inventory

Eight published measurement records and three independent papers are separated from illustrative negative controls. Muon g-2, CODATA constants, cosmology, particle reactions, and alpha-decay tests are also registered with their correct epistemic status.

## M9.126b — paper-level holdout

Each paper is held out while the other papers define a fitted constant baseline. All held-out paper groups pass the broad Planckian band. The evaluator reports both the fixed central prediction `R = 1` and the training-fitted constant baseline.

This is a retrospective leave-one-paper-out analysis. It is not a prospective experiment, and the rounded values lack uncertainty and extraction metadata needed for a precision likelihood.

## M9.126c — qualification gate

Existing evidence is qualified for retrospective use. Prospective external promotion remains blocked on raw values and uncertainties, commitment before data access, independent transport-time extraction, predeclared exclusions, a discriminator stronger than dimensional scaling, and independent replication.

```text
existing experimental papers recognized      true
retrospective Planckian holdout complete      true
broad-band consistency supported              true
entropic time uniquely selected               false
prospective external validation complete      false
physical promotion allowed                    false
```
