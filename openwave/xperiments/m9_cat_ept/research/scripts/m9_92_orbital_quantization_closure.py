from openwave.xperiments.m9_cat_ept.orbital_quantization_closure import result_to_json, run_orbital_quantization_closure


if __name__ == "__main__":
    print(result_to_json(run_orbital_quantization_closure()), end="")
