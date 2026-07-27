from openwave.xperiments.m9_cat_ept.gauge_sector_spectrum import (
    result_to_json,
    run_gauge_sector_spectrum,
)

print(result_to_json(run_gauge_sector_spectrum()), end="")
