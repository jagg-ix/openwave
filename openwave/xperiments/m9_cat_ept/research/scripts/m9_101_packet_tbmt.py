from openwave.xperiments.m9_cat_ept.covariant_packet_tbmt import (
    result_to_json,
    run_covariant_packet_tbmt,
)

if __name__ == "__main__":
    print(result_to_json(run_covariant_packet_tbmt()), end="")
