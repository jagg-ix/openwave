# OpenWave Models: canonical comparison registry

OpenWave hosts multiple candidate field-theoretic models. Historical M4--M8 results remain in [`MODELS_LEGACY.md`](MODELS_LEGACY.md).

| ID | Model | Current profile | Status authority |
| --- | --- | --- | --- |
| M4--M8 | historical OpenWave models | [`MODELS_LEGACY.md`](MODELS_LEGACY.md) | legacy matrix |
| **M9** | **CAT/EPT entropic particle and field dynamics** | **[`MODELS_M9.md`](MODELS_M9.md)** | **current registration + conformance aliases** |

## M9 current state

Current integrated milestone: **M9.125**.

| Layer | Current result | Boundary retained |
| --- | --- | --- |
| three clock roles | Page-Wootters relational ordering, modular reversible flow, and entropic irreversible accumulation | roles are not one universal clock |
| shared finite carrier | one full-rank thermal qubit branch carries conditioned states, modular generator, and relative-entropy arrow | finite reduced carrier is not the full constraint theorem |
| clock maps | invertible Page-Wootters/modular/nominal-proper maps and branch-invertible entropic map | model-internal maps are not measured calibration |
| blinded test path | prediction commitment, package validation, and blocked live evaluator | no real three-clock data are ingested |
| promotion | reduced common-carrier gate passes; universal clock gate fails closed | proper-time calibration and held-out evidence remain missing |

Stable entry points:

```bash
python -m openwave.xperiments.m9_cat_ept._launcher --current-conformance
python -m openwave.xperiments.m9_cat_ept._launcher --current-registration
python -m openwave.xperiments.m9_cat_ept._launcher --platform-contract
```

A shared finite carrier is stronger than a role taxonomy, but it is not a universal physical-time theorem.
