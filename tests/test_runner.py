from qc_tool.runner import compute_score, run_qc
from qc_tool.models import RuleSeverity


def test_compute_score_deductions():
    score = compute_score([RuleSeverity.CRITICAL, RuleSeverity.MAJOR, RuleSeverity.MINOR])
    assert score == 100 - 15 - 5 - 2


def test_run_qc_generates_findings(tmp_path):
    # use sample data shipped with repository
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    snapshot = root / "data" / "sample_account.json"
    rules = root / "rules" / "default_rules.yaml"

    result = run_qc(str(snapshot), str(rules))

    assert result.score < 100
    assert any(f.rule_id == "MSCLKID_AUTOTAG" for f in result.findings)
    assert any(f.entity_id == "cmp2" for f in result.findings)
