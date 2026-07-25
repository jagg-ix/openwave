from openwave.xperiments.m9_cat_ept.klein_gordon_closure import result_to_json, run_klein_gordon_closure


if __name__ == "__main__":
    print(result_to_json(run_klein_gordon_closure()), end="")
