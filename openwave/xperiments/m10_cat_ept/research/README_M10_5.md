# M10.5 SU(3) link backreaction

Run the deterministic non-Abelian campaign with:

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import run_su3_link_backreaction_study
import json
print(json.dumps(run_su3_link_backreaction_study(), indent=2, sort_keys=True, default=float))
PY
```

The campaign verifies Gell-Mann normalization, local gauge covariance, Wilson-action invariance, adjoint color-current transport, a covariant current-gradient link update, and source-functional response.