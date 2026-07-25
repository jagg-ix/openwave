"""Run the M9.93b reusable CAT/EPT particle-kernel controls."""
from openwave.xperiments.m9_cat_ept.particle_model import (
    result_to_json,
    run_particle_kernel_study,
)


if __name__ == "__main__":
    print(result_to_json(run_particle_kernel_study()), end="")
