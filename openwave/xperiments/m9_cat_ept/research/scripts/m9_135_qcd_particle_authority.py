from openwave.xperiments.m9_cat_ept.m135_qcd_particle_authority import (
    result_to_json,
    run_m135_qcd_particle_authority,
)


if __name__ == "__main__":
    print(result_to_json(run_m135_qcd_particle_authority()), end="")
