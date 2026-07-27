from openwave.xperiments.m9_cat_ept.electroweak_higgs_lattice import (
    result_to_json,
    run_electroweak_higgs_lattice,
)

print(result_to_json(run_electroweak_higgs_lattice()), end="")
