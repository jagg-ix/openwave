from openwave.xperiments.m9_cat_ept.physical_promotion_gate import (
    run_physical_promotion_gate,
)
import json

print(json.dumps(run_physical_promotion_gate(), indent=2, sort_keys=True), end="\n")
