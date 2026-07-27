from openwave.xperiments.m9_cat_ept.gauge_sector_linear_response import (
    result_to_json,
    run_gauge_sector_linear_response,
)

print(result_to_json(run_gauge_sector_linear_response()), end="")
