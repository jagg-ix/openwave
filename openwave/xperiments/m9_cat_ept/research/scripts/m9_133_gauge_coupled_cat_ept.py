from openwave.xperiments.m9_cat_ept.m133_gauge_coupled_authority import run_m133_gauge_coupled_authority
import json

print(json.dumps(run_m133_gauge_coupled_authority(), indent=2, sort_keys=True, default=float))
