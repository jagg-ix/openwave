from openwave.xperiments.m9_cat_ept.gauge_sector_spectral_refinement import (
    result_to_json,
    run_gauge_sector_spectral_refinement,
)

print(result_to_json(run_gauge_sector_spectral_refinement()), end="")
