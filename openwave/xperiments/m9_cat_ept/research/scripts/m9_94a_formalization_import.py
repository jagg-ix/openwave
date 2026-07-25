"""Run the M9.94a CAT/EPT Lean and ZIL formalization import audit."""
from openwave.xperiments.m9_cat_ept.formalization_import import (
    result_to_json,
    run_formalization_import_study,
)


if __name__ == "__main__":
    print(result_to_json(run_formalization_import_study()), end="")
