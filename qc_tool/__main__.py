"""Command line interface for the QC MVP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .runner import run_qc


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Bing Ads QC automation MVP")
    parser.add_argument("snapshot", help="Path to account snapshot JSON")
    parser.add_argument("rules", help="Path to rules YAML file")
    parser.add_argument("--output", "-o", help="Optional path to write JSON results")
    args = parser.parse_args()

    result = run_qc(args.snapshot, args.rules)

    print("QC score:", result.score)
    print("Severity breakdown:")
    for severity, count in sorted(result.breakdown.items(), key=lambda item: item[0].value):
        print(f"  {severity.value.title()}: {count}")

    if not result.findings:
        print("No findings! Account is launch ready.")
    else:
        print("Findings:")
        for finding in result.findings:
            print(f"- [{finding.severity}] {finding.rule_id} ({finding.entity_type} {finding.entity_id})")
            print(f"    {finding.message}")
            if finding.evidence:
                print(f"    Evidence: {finding.evidence}")
            print(f"    Remediation: {finding.remediation}")

    if args.output:
        payload: dict[str, Any] = {
            "score": result.score,
            "breakdown": {severity.value: count for severity, count in result.breakdown.items()},
            "findings": [
                {
                    "ruleId": finding.rule_id,
                    "severity": finding.severity.value,
                    "entityType": finding.entity_type,
                    "entityId": finding.entity_id,
                    "message": finding.message,
                    "remediation": finding.remediation,
                    "evidence": finding.evidence,
                }
                for finding in result.findings
            ],
        }
        Path(args.output).write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"Results saved to {args.output}")


if __name__ == "__main__":  # pragma: no cover
    main()
