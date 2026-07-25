from openwave.xperiments.m9_cat_ept.field_force_triangle import (
    result_to_json,
    run_field_force_triangle,
)


if __name__ == "__main__":
    print(result_to_json(run_field_force_triangle()), end="")
