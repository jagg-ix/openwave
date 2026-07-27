from openwave.xperiments.m9_cat_ept.gaussian_covariance_scale_flow import (
    result_to_json,
    run_gaussian_covariance_scale_flow,
)

print(result_to_json(run_gaussian_covariance_scale_flow()), end="")
