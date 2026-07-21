# Local-only datasets manifest

> AUTO-GENERATED, do not hand-edit the table: `python3 ~/Documents/source_code/XRODZ/dotfiles/claude_projects/NEPTUNYA-SABER/scripts/gen_datasets_manifest.py data --write`

Heavy binary arrays in this folder are **local-only**: gitignored, never deleted (policy 2026-07-20, which supersedes the earlier "delete raw data > 1 MB" rule). They stay on the working machine so later tasks can consume them directly, and they stay OUT of the repo so clones stay light. What IS tracked in git and readable on GitHub: the summary `.json` / `.csv` / `.txt` in this same folder, the plots, and the scripts that rebuild everything here.

**Inventory**: 242 local-only files, 542.38 MB, in 34 task groups.

| Task group | Files | Size | Producing script(s) | Record (regen commands + context) |
| --- | --- | --- | --- | --- |
| `m5_12` | 105 | 17.84 MB | [`m5_12_audit_b11_lib.py`](../scripts/m5_12_audit_b11_lib.py) · [`m5_12_audit_b11_run.py`](../scripts/m5_12_audit_b11_run.py) · [`m5_12_audit_b11_verdicts.py`](../scripts/m5_12_audit_b11_verdicts.py) (+43 more) | [`m5_12_task_details.md`](../tasks/m5_12_task_details.md) |
| `m5_19` | 6 | 2.16 MB | [`m5_19_ab_vortex.py`](../scripts/m5_19_ab_vortex.py) · [`m5_19_b2_spectral.py`](../scripts/m5_19_b2_spectral.py) · [`m5_19_c1_loop.py`](../scripts/m5_19_c1_loop.py) (+2 more) | [`m5_19_task_details.md`](../tasks/m5_19_task_details.md) |
| `m5_20` | 6 | 3.41 MB | [`m5_20_1_a_theory.py`](../scripts/m5_20_1_a_theory.py) · [`m5_20_1_audit_check.py`](../scripts/m5_20_1_audit_check.py) · [`m5_20_1_b_seeds.py`](../scripts/m5_20_1_b_seeds.py) (+30 more) | [`m5_20_task_details.md`](../tasks/m5_20_task_details.md) |
| `m5_20_1` | 11 | 5.05 MB | [`m5_20_1_a_theory.py`](../scripts/m5_20_1_a_theory.py) · [`m5_20_1_audit_check.py`](../scripts/m5_20_1_audit_check.py) · [`m5_20_1_b_seeds.py`](../scripts/m5_20_1_b_seeds.py) (+5 more) | [`m5_20_1_task_details.md`](../tasks/m5_20_1_task_details.md) |
| `m5_20_2` | 1 | 0.46 MB | [`m5_20_2_a_eom.py`](../scripts/m5_20_2_a_eom.py) · [`m5_20_2_audit_check.py`](../scripts/m5_20_2_audit_check.py) · [`m5_20_2_b_dynamics.py`](../scripts/m5_20_2_b_dynamics.py) (+2 more) | [`m5_20_2_task_details.md`](../tasks/m5_20_2_task_details.md) |
| `m5_20_3` | 11 | 3.09 MB | [`m5_20_3_a_constraint.py`](../scripts/m5_20_3_a_constraint.py) · [`m5_20_3_audit_check.py`](../scripts/m5_20_3_audit_check.py) · [`m5_20_3_b_triage.py`](../scripts/m5_20_3_b_triage.py) (+3 more) | [`m5_20_3_task_details.md`](../tasks/m5_20_3_task_details.md) |
| `m5_20_4` | 3 | 1.16 MB | [`m5_20_4_a_bvp.py`](../scripts/m5_20_4_a_bvp.py) · [`m5_20_4_audit_check.py`](../scripts/m5_20_4_audit_check.py) · [`m5_20_4_b_dirac.py`](../scripts/m5_20_4_b_dirac.py) (+2 more) | [`m5_20_4_task_details.md`](../tasks/m5_20_4_task_details.md) |
| `m5_20_5` | 5 | 2.68 MB | [`m5_20_5_a_orbit.py`](../scripts/m5_20_5_a_orbit.py) · [`m5_20_5_audit_check.py`](../scripts/m5_20_5_audit_check.py) · [`m5_20_5_b_escape.py`](../scripts/m5_20_5_b_escape.py) (+1 more) | [`m5_20_5_task_details.md`](../tasks/m5_20_5_task_details.md) |
| `m5_21` | 1 | 0.79 MB | [`m5_21_10_a_decay64.py`](../scripts/m5_21_10_a_decay64.py) · [`m5_21_10_b_ring.py`](../scripts/m5_21_10_b_ring.py) · [`m5_21_10_c_panel.py`](../scripts/m5_21_10_c_panel.py) (+52 more) | [`m5_21_task_details.md`](../tasks/m5_21_task_details.md) |
| `m5_21_1` | 8 | 3.88 MB | [`m5_21_10_a_decay64.py`](../scripts/m5_21_10_a_decay64.py) · [`m5_21_10_b_ring.py`](../scripts/m5_21_10_b_ring.py) · [`m5_21_10_c_panel.py`](../scripts/m5_21_10_c_panel.py) (+9 more) | [`m5_21_1_task_details.md`](../tasks/m5_21_1_task_details.md) |
| `m5_21_10` | 3 | 293.47 MB | [`m5_21_10_a_decay64.py`](../scripts/m5_21_10_a_decay64.py) · [`m5_21_10_b_ring.py`](../scripts/m5_21_10_b_ring.py) · [`m5_21_10_c_panel.py`](../scripts/m5_21_10_c_panel.py) (+1 more) | [`m5_21_10_task_details.md`](../tasks/m5_21_10_task_details.md) |
| `m5_21_1e` | 2 | 0.37 MB | [`m5_21_1e_audit_check.py`](../scripts/m5_21_1e_audit_check.py) · [`m5_21_1e_b_constraint.py`](../scripts/m5_21_1e_b_constraint.py) · [`m5_21_1e_c_toy.py`](../scripts/m5_21_1e_c_toy.py) | [`m5_21_1e_task_details.md`](../tasks/m5_21_1e_task_details.md) |
| `m5_21_2` | 4 | 6.78 MB | [`m5_21_2_a_scan3d.py`](../scripts/m5_21_2_a_scan3d.py) · [`m5_21_2_audit_check.py`](../scripts/m5_21_2_audit_check.py) · [`m5_21_2_b_topo_illustration.py`](../scripts/m5_21_2_b_topo_illustration.py) (+8 more) | [`m5_21_2_task_details.md`](../tasks/m5_21_2_task_details.md) |
| `m5_21_2b` | 14 | 9.40 MB | [`m5_21_2b_a_instrument.py`](../scripts/m5_21_2b_a_instrument.py) · [`m5_21_2b_audit_check.py`](../scripts/m5_21_2b_audit_check.py) · [`m5_21_2b_b_split.py`](../scripts/m5_21_2b_b_split.py) (+2 more) | [`m5_21_2b_task_details.md`](../tasks/m5_21_2b_task_details.md) |
| `m5_21_3` | 5 | 4.21 MB | [`m5_21_3_a_4d.py`](../scripts/m5_21_3_a_4d.py) · [`m5_21_3_audit_check.py`](../scripts/m5_21_3_audit_check.py) · [`m5_21_3_c_films.py`](../scripts/m5_21_3_c_films.py) (+3 more) | [`m5_21_3_task_details.md`](../tasks/m5_21_3_task_details.md) |
| `m5_21_5` | 3 | 3.13 MB | [`m5_21_5_a_mu.py`](../scripts/m5_21_5_a_mu.py) · [`m5_21_5_b_ladder.py`](../scripts/m5_21_5_b_ladder.py) · [`m5_21_5_c_bridge.py`](../scripts/m5_21_5_c_bridge.py) (+2 more) | [`m5_21_5_task_details.md`](../tasks/m5_21_5_task_details.md) |
| `m5_21_6` | 20 | 176.28 MB | [`m5_21_6_a_decay.py`](../scripts/m5_21_6_a_decay.py) · [`m5_21_6_audit_check.py`](../scripts/m5_21_6_audit_check.py) · [`m5_21_6_c_films.py`](../scripts/m5_21_6_c_films.py) (+1 more) | [`m5_21_6_task_details.md`](../tasks/m5_21_6_task_details.md) |
| `m5_21_9` | 8 | 7.18 MB | [`m5_21_9_a_audit.py`](../scripts/m5_21_9_a_audit.py) · [`m5_21_9_a_negdelta.py`](../scripts/m5_21_9_a_negdelta.py) · [`m5_21_9_b_audit.py`](../scripts/m5_21_9_b_audit.py) (+6 more) | [`m5_21_9_task_details.md`](../tasks/m5_21_9_task_details.md) |
| `m5_8_2b` | 1 | 0.01 MB | [`m5_8_2b2_field_clock.py`](../scripts/m5_8_2b2_field_clock.py) · [`m5_8_2b_cc_clock.py`](../scripts/m5_8_2b_cc_clock.py) | ⚠️ not resolved |
| `m5_8_2e` | 2 | 0.05 MB | [`m5_8_2e_invariant_matrix.py`](../scripts/m5_8_2e_invariant_matrix.py) | ⚠️ not resolved |
| `m5_8_2f` | 2 | 0.00 MB | [`m5_8_2f2_localized_clock.py`](../scripts/m5_8_2f2_localized_clock.py) · [`m5_8_2f3_breather_orbit.py`](../scripts/m5_8_2f3_breather_orbit.py) · [`m5_8_2f_breathing_bvp.py`](../scripts/m5_8_2f_breathing_bvp.py) | ⚠️ not resolved |
| `m5_8_2g` | 1 | 0.03 MB | [`m5_8_2g_spontaneity.py`](../scripts/m5_8_2g_spontaneity.py) | ⚠️ not resolved |
| `m5_8_2h` | 1 | 0.01 MB | [`m5_8_2h_omega_attractor.py`](../scripts/m5_8_2h_omega_attractor.py) | ⚠️ not resolved |
| `m5_8_2i` | 2 | 0.31 MB | [`m5_8_2i_dispersal_gate.py`](../scripts/m5_8_2i_dispersal_gate.py) | ⚠️ not resolved |
| `m5_8_2m` | 6 | 0.48 MB | [`m5_8_2m_zbw_law.py`](../scripts/m5_8_2m_zbw_law.py) | ⚠️ not resolved |
| `m5_8_2o` | 3 | 0.13 MB | [`m5_8_2o_omega_of_E.py`](../scripts/m5_8_2o_omega_of_E.py) | ⚠️ not resolved |
| `m5_8_2p` | 1 | 0.00 MB | [`m5_8_2p_spin_readout.py`](../scripts/m5_8_2p_spin_readout.py) | ⚠️ not resolved |
| `m5_8_2u` | 1 | 0.00 MB | [`m5_8_2u_clock_energy_minimum.py`](../scripts/m5_8_2u_clock_energy_minimum.py) | ⚠️ not resolved |
| `m5_8_2w` | 1 | 0.00 MB | [`m5_8_2w_energy_vs_frequency.py`](../scripts/m5_8_2w_energy_vs_frequency.py) | ⚠️ not resolved |
| `m5_8_2z` | 1 | 0.00 MB | [`m5_8_2z_length_anchor.py`](../scripts/m5_8_2z_length_anchor.py) · [`m5_8_2z_settled_energy_vs_frequency.py`](../scripts/m5_8_2z_settled_energy_vs_frequency.py) · [`m5_8_2za_g_factor.py`](../scripts/m5_8_2za_g_factor.py) | [`m5_8_2z_findings.md`](../findings/m5_8_2z_findings.md) |
| `m5_8_3a` | 1 | 0.00 MB | [`m5_8_3a_constrained_energy_vs_frequency.py`](../scripts/m5_8_3a_constrained_energy_vs_frequency.py) | ⚠️ not resolved |
| `m5_9_1` | 1 | 0.00 MB | [`m5_9_1_lepton_mass_law.py`](../scripts/m5_9_1_lepton_mass_law.py) | [`m5_9_task_details.md`](../tasks/m5_9_task_details.md) |
| `m5_9_2` | 1 | 0.00 MB | [`m5_9_2_clock_scaling.py`](../scripts/m5_9_2_clock_scaling.py) | [`m5_9_task_details.md`](../tasks/m5_9_task_details.md) |
| `m5_9_3` | 1 | 0.00 MB | [`m5_9_3_confiner.py`](../scripts/m5_9_3_confiner.py) | [`m5_9_task_details.md`](../tasks/m5_9_task_details.md) |

**Regeneration**: the exact command + runtime per dataset lives in the task record linked on its row (the task_details / findings doc), which is where the run configuration is already written down. Runs in both repos are deterministic from their fixed seeds and configs, so a regenerated array reproduces the original bit-for-bit at the stored precision.
