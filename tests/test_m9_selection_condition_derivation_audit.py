from openwave.xperiments.m9_cat_ept.selection_condition_derivation_audit import alternative_landmark_audit,gaussian_scale_derivative,run_selection_derivation_audit,stationary_field_residual
from openwave.xperiments.m9_cat_ept.coefficient_self_consistency import selected_coefficients

def test_scale_stationarity_is_exact():
 c=selected_coefficients();assert abs(gaussian_scale_derivative(c['alpha'],c['beta']))<2e-13

def test_gaussian_fails_full_stationary_field_equation():
 c=selected_coefficients();assert stationary_field_residual(c['alpha'],c['beta'])['relative_residual']>.10

def test_alternative_landmarks_select_distinct_pairs():
 r=alternative_landmark_audit();assert r['distinct_positive_pairs']==3 and r['all_systems_nondegenerate'] and r['all_equations_close']

def test_full_derivation_audit_passes():
 r=run_selection_derivation_audit();assert r['passed'] and not r['decision']['m9_63_pair_first_principles_unique']
