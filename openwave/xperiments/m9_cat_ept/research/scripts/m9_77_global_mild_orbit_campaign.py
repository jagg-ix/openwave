from openwave.xperiments.m9_cat_ept.global_mild_orbit_campaign import (
    result_to_json,
    run_global_mild_orbit_campaign,
)

print(result_to_json(run_global_mild_orbit_campaign()), end="")