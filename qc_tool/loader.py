"""Utilities for loading rules and input data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

try:  # optional dependency
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - environment dependent
    yaml = None

from .models import Rule, severity_from_string


def _parse_rules(text: str) -> List[dict[str, Any]]:
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)
    if not isinstance(data, list):
        raise ValueError("Rule file must contain a list of rules")
    return data


def load_rules(path: str | Path) -> List[Rule]:
    """Load rule definitions from a YAML (or JSON) file."""

    text = Path(path).read_text(encoding="utf-8")
    raw_rules = _parse_rules(text)

    rules: List[Rule] = []
    for raw in raw_rules:
        severity = raw.get("severity")
        if severity is None:
            raise ValueError(f"Rule {raw.get('id')} missing severity")
        rules.append(
            Rule(
                id=raw["id"],
                name=raw.get("name", raw["id"]),
                description=raw.get("description", ""),
                severity=severity_from_string(severity),
                type=raw.get("type", "boolean_true"),
                target=raw.get("target", ""),
                remediation=raw.get("remediation", ""),
                params=raw.get("params", {}),
            )
        )
    return rules


def load_account_snapshot(path: str | Path) -> Dict[str, Any]:
    """Load a JSON snapshot of account data."""

    return json.loads(Path(path).read_text(encoding="utf-8"))
