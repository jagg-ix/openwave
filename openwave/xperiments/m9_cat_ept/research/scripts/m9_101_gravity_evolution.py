from openwave.xperiments.m9_cat_ept.electrogravitic_weak_field_evolution import (
    result_to_json,
    run_electrogravitic_weak_field_evolution,
)

if __name__ == "__main__":
    print(result_to_json(run_electrogravitic_weak_field_evolution()), end="")
