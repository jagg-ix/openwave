from openwave.xperiments.m9_cat_ept.charged_maxwell_source_bridge import (
    result_to_json,
    run_charged_maxwell_source_bridge,
)


if __name__ == "__main__":
    print(result_to_json(run_charged_maxwell_source_bridge()), end="")
