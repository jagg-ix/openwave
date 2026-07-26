from openwave.xperiments.m9_cat_ept.packet_tbmt_refinement import PacketRefinementConfig,THOMAS_EXTENSION_POSTULATE


def test_covariant_thomas_extension_is_explicit_postulate():
    assert THOMAS_EXTENSION_POSTULATE["qed_derived"] is False
    assert THOMAS_EXTENSION_POSTULATE["rest_frame_qed_grounded"] is True
    assert "beta=j/rho" in THOMAS_EXTENSION_POSTULATE["domain"]


def test_refinement_grid_and_time_contract():
    cfg=PacketRefinementConfig()
    assert cfg.points==(16,20)
    assert cfg.time_steps==(4e-3,2e-3)
    for points in cfg.points:
        for dt in cfg.time_steps:
            dynamics=cfg.dynamics(points,dt)
            assert dynamics.points==points
            assert dynamics.time_step==dt
            assert dynamics.fit_samples>=4
