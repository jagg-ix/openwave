from openwave.xperiments.m9_cat_ept.branch_identity_certificate import result_to_json, run_branch_identity_certificate

if __name__ == "__main__":
    print(result_to_json(run_branch_identity_certificate()), end="")
