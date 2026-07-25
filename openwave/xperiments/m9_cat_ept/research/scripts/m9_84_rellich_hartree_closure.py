from openwave.xperiments.m9_cat_ept.rellich_hartree_closure import result_to_json, run_rellich_hartree_closure

if __name__ == "__main__":
    print(result_to_json(run_rellich_hartree_closure()), end="")
