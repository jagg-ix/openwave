from openwave.xperiments.m9_cat_ept.duhamel_fixed_point_campaign import (
    result_to_json,
    run_duhamel_fixed_point_campaign,
)

print(result_to_json(run_duhamel_fixed_point_campaign()), end="")
