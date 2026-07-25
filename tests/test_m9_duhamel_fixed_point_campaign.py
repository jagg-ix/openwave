from openwave.xperiments.m9_cat_ept.duhamel_fixed_point_campaign import (
    run_duhamel_fixed_point_campaign,
)


def test_picard_differences_contract_at_every_resolution():
    result = run_duhamel_fixed_point_campaign()
    for row in result["rows"]:
        differences = row["picard_differences"]
        assert all(
            differences[index + 1] < differences[index]
            for index in range(len(differences) - 1)
        )
        assert row["fixed_point_residual_h1"] < 1e-10


def test_duhamel_time_refinement_converges_to_strang_trajectory():
    rows = run_duhamel_fixed_point_campaign()["rows"]
    errors = [row["duhamel_strang_final_h1_difference"] for row in rows]
    assert errors[2] < errors[1] < errors[0]


def test_m9_78_passes_without_claiming_continuum_strichartz():
    result = run_duhamel_fixed_point_campaign()
    assert result["passed"]
    assert not result["decision"][
        "continuum_energy_critical_strichartz_flow_constructed"
    ]
