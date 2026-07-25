from openwave.xperiments.m9_cat_ept.local_interaction_no_loss_closure import result_to_json, run_local_interaction_no_loss_closure

if __name__ == "__main__":
    print(result_to_json(run_local_interaction_no_loss_closure()), end="")
