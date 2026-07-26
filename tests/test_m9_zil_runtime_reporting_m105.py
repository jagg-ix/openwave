from openwave.xperiments.m9_cat_ept.zil_runtime_reporting_m105 import parse_examples_report


def test_zil_examples_report_accepts_pass_and_skip():
    report="""ZIL-EXAMPLES-REPORT/1
group	native
step	description	expected	exit	status	duration_seconds	log	command
one	query	0	0	pass	1	one.log	bin/zil query-ci graph.zc
two	optional	0	-	skip	0	-	lake build
"""
    result=parse_examples_report(report)
    assert result["passed"]
    assert result["counts"]=={"pass":1,"fail":0,"skip":1}


def test_zil_examples_report_rejects_failure():
    report="""ZIL-EXAMPLES-REPORT/1
group	native
step	description	expected	exit	status	duration_seconds	log	command
one	query	0	1	fail	1	one.log	bin/zil query-ci graph.zc
"""
    assert not parse_examples_report(report)["passed"]
