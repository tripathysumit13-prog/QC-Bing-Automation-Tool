"""High-level orchestration for running QC checks."""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List

from .evaluator import RuleEvaluator
from .loader import load_account_snapshot, load_rules
from .models import QCResult, Rule, RuleSeverity, SEVERITY_WEIGHTS


def compute_score(findings: Iterable[RuleSeverity]) -> int:
    """Compute the QC score based on findings."""

    deductions = sum(SEVERITY_WEIGHTS[severity] for severity in findings)
    return max(0, 100 - deductions)


def run_qc(snapshot_path: str, rules_path: str) -> QCResult:
    """Run QC for the provided account snapshot and ruleset."""

    data = load_account_snapshot(snapshot_path)
    rules: List[Rule] = load_rules(rules_path)
    evaluator = RuleEvaluator(rules)
    findings = evaluator.evaluate(data)
    breakdown: Dict[RuleSeverity, int] = Counter(f.severity for f in findings)
    score = compute_score(breakdown.elements())
    return QCResult(findings=findings, score=score, breakdown=dict(breakdown))
