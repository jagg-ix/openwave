from openwave.xperiments.m9_cat_ept.recentered_compactness_audit import (
    result_to_json,
    run_recentered_compactness_audit,
)

print(result_to_json(run_recentered_compactness_audit()), end="")