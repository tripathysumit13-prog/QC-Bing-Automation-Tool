"""Dataclasses describing QC rules and findings."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class RuleSeverity(str, Enum):
    """Supported severity levels for findings."""

    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    MINOR = "MINOR"


SEVERITY_WEIGHTS: dict[RuleSeverity, int] = {
    RuleSeverity.CRITICAL: 15,
    RuleSeverity.MAJOR: 5,
    RuleSeverity.MINOR: 2,
}


@dataclass(slots=True)
class Rule:
    """Configuration for a single QC rule."""

    id: str
    name: str
    description: str
    severity: RuleSeverity
    type: str
    target: str
    remediation: str
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class Finding:
    """Result of executing a rule against an entity."""

    rule_id: str
    severity: RuleSeverity
    entity_type: str
    entity_id: str
    message: str
    remediation: str
    evidence: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class QCResult:
    """Aggregated QC results."""

    findings: List[Finding]
    score: int
    breakdown: Dict[RuleSeverity, int]


def severity_from_string(value: str) -> RuleSeverity:
    """Parse a string into a :class:`RuleSeverity`."""

    try:
        return RuleSeverity[value.upper()]
    except KeyError as exc:  # pragma: no cover - defensive
        allowed = ", ".join(severity.name for severity in RuleSeverity)
        raise ValueError(f"Unknown severity '{value}'. Allowed: {allowed}") from exc
