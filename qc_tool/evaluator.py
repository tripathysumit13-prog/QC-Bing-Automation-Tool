"""Rule evaluation logic for the QC MVP."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Iterator, List

from .models import Finding, Rule, RuleSeverity


@dataclass(slots=True)
class EvaluationContext:
    """Context for evaluating a rule."""

    rule: Rule
    data: Dict[str, Any]


class RuleEvaluator:
    """Evaluate configured rules against account snapshots."""

    def __init__(self, rules: Iterable[Rule]):
        self.rules = list(rules)

    def evaluate(self, data: Dict[str, Any]) -> List[Finding]:
        findings: List[Finding] = []
        for rule in self.rules:
            ctx = EvaluationContext(rule=rule, data=data)
            findings.extend(_EVALUATORS.get(rule.type, evaluate_boolean_true)(ctx))
        return findings


# --- Helper utilities -----------------------------------------------------


def get_value(data: Dict[str, Any], path: str) -> Any:
    """Retrieve a nested value from a dictionary using dot notation."""

    if not path:
        return data

    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        elif isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                raise KeyError(f"Cannot use key '{part}' on list in path '{path}'")
            current = current[index]
        else:
            raise KeyError(f"Cannot traverse '{part}' in path '{path}'")
    return current


def ensure_iterable(value: Any) -> Iterator[Any]:
    if value is None:
        return iter(())
    if isinstance(value, list):
        return iter(value)
    return iter([value])


# --- Rule evaluators ------------------------------------------------------


def evaluate_boolean_true(ctx: EvaluationContext) -> List[Finding]:
    value = bool(get_value(ctx.data, ctx.rule.target))
    if value:
        return []
    return [
        Finding(
            rule_id=ctx.rule.id,
            severity=ctx.rule.severity,
            entity_type="ACCOUNT",
            entity_id=str(ctx.data.get("accountId", "unknown")),
            message=f"Expected truthy value at '{ctx.rule.target}' but found {value}.",
            remediation=ctx.rule.remediation,
            evidence={"value": value},
        )
    ]


def evaluate_non_empty(ctx: EvaluationContext) -> List[Finding]:
    value = get_value(ctx.data, ctx.rule.target)
    if value:
        return []
    return [
        Finding(
            rule_id=ctx.rule.id,
            severity=ctx.rule.severity,
            entity_type="ACCOUNT",
            entity_id=str(ctx.data.get("accountId", "unknown")),
            message=f"Expected non-empty value at '{ctx.rule.target}'.",
            remediation=ctx.rule.remediation,
            evidence={"value": value},
        )
    ]


def evaluate_min_count(ctx: EvaluationContext) -> List[Finding]:
    value = ensure_iterable(get_value(ctx.data, ctx.rule.target))
    items = list(value)
    min_required = int(ctx.rule.params.get("min", 1))
    if len(items) >= min_required:
        return []
    return [
        Finding(
            rule_id=ctx.rule.id,
            severity=ctx.rule.severity,
            entity_type="ACCOUNT",
            entity_id=str(ctx.data.get("accountId", "unknown")),
            message=f"Expected at least {min_required} items at '{ctx.rule.target}' but found {len(items)}.",
            remediation=ctx.rule.remediation,
            evidence={"count": len(items)},
        )
    ]


def evaluate_regex(ctx: EvaluationContext) -> List[Finding]:
    pattern = ctx.rule.params.get("pattern")
    if not pattern:
        raise ValueError(f"Rule {ctx.rule.id} missing regex pattern")
    value = get_value(ctx.data, ctx.rule.target)
    if isinstance(value, str) and re.match(pattern, value):
        return []
    return [
        Finding(
            rule_id=ctx.rule.id,
            severity=ctx.rule.severity,
            entity_type="ACCOUNT",
            entity_id=str(ctx.data.get("accountId", "unknown")),
            message=f"Value '{value}' does not match pattern '{pattern}'.",
            remediation=ctx.rule.remediation,
            evidence={"value": value, "pattern": pattern},
        )
    ]


def evaluate_collection_field(ctx: EvaluationContext) -> List[Finding]:
    collection_path = ctx.rule.target
    field = ctx.rule.params.get("field")
    if not field:
        raise ValueError(f"Rule {ctx.rule.id} missing 'field' parameter")
    minimum = int(ctx.rule.params.get("min", 1))

    findings: List[Finding] = []
    collection = ensure_iterable(get_value(ctx.data, collection_path))
    for item in collection:
        if not isinstance(item, dict):
            continue
        entity_id = str(item.get("id", item.get("name", "unknown")))
        values = ensure_iterable(item.get(field))
        if sum(1 for _ in values) >= minimum:
            continue
        findings.append(
            Finding(
                rule_id=ctx.rule.id,
                severity=ctx.rule.severity,
                entity_type=ctx.rule.params.get("entity_type", "ENTITY"),
                entity_id=entity_id,
                message=f"Expected at least {minimum} value(s) in field '{field}' for entity {entity_id}.",
                remediation=ctx.rule.remediation,
                evidence={"field": field},
            )
        )
    return findings


_EVALUATORS = {
    "boolean_true": evaluate_boolean_true,
    "non_empty": evaluate_non_empty,
    "min_count": evaluate_min_count,
    "regex": evaluate_regex,
    "collection_field_min": evaluate_collection_field,
}
