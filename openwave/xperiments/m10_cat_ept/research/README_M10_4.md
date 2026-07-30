# M10.4 finite QCD functional and decoherence reproducer

Run the complete finite center-valued Wilson/QCD and history-decoherence campaign with:

```bash
python - <<'PY'
from openwave.xperiments.m10_cat_ept import run_qcd_functional_decoherence_study
import json
print(json.dumps(run_qcd_functional_decoherence_study(), indent=2, sort_keys=True, default=float))
PY
```

The campaign enumerates all 81 histories, evaluates source derivatives and connected correlators, constructs the normalized influence-functional decoherence matrix, and evaluates the formal one-loop QCD integral targets.
