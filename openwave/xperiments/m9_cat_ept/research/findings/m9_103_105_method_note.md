# M9.103--M9.105 method note

A deep source audit found three concrete rather than rhetorical blockers.

1. `coupled_gauge_spinor_hartree_action.py` projected the spinor to a fixed winding/spin sector after every imaginary-time step. M9.103 removes that projection after initialization and measures the full residual and stability directly.
2. `covariant_packet_tbmt.py` evaluated one coarse carrier. M9.104 registers the covariant Thomas equation as an explicit external postulate and performs a grid/time refinement against the exact Dirac generator.
3. `clock_action_rate_calibration.py` determined an entropy normalization from the same internal branch frequency used by the target. M9.105 represents every calibration dependency and refuses to execute physical predictions using internal, derived, absent, circular, or target-fitted anchors.

The current ZIL roots are unchanged. The new upstream commit contributes a Make-driven `ZIL-EXAMPLES-REPORT/1` harness; OpenWave pins and parses this reporting layer separately from Lean proof authority and physical evidence.

No numerical campaign was executed in the connector-only environment. Exact outcomes remain dynamic and are obtained from the repository runners. The PR establishes the full experiment and evidence contracts, not a predetermined successful result.
