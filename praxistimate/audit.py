from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from praxistimate import __version__


@dataclass
class Violation:
    code: str
    severity: str
    rule_id: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "code": self.code,
            "severity": self.severity,
            "rule_id": self.rule_id,
            "message": self.message,
        }


def _parse_semver(value: str) -> tuple[int, ...]:
    parts = []
    for chunk in str(value).strip().split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 2:
        parts.append(0)
    return tuple(parts)


def _semver_gte(left: str, right: str) -> bool:
    return _parse_semver(left) >= _parse_semver(right)


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest must be a JSON object")
    return data


def load_rules(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def evaluate_rule(rule: dict[str, Any], manifest: dict[str, Any]) -> Violation | None:
    check = rule.get("check") or {}
    field = check.get("field")
    if not field:
        return None
    value = manifest.get(field)
    if "equals" in check and value != check["equals"]:
        return Violation(
            code=rule["code"],
            severity=rule.get("severity", "error"),
            rule_id=rule["id"],
            message=rule.get("message", rule["code"]),
        )
    if "semver_gte" in check:
        if value is None or not _semver_gte(str(value), str(check["semver_gte"])):
            return Violation(
                code=rule["code"],
                severity=rule.get("severity", "error"),
                rule_id=rule["id"],
                message=rule.get("message", rule["code"]),
            )
    if "in" in check:
        allowed = check["in"]
        if value not in allowed:
            return Violation(
                code=rule["code"],
                severity=rule.get("severity", "warning"),
                rule_id=rule["id"],
                message=rule.get("message", rule["code"]),
            )
    return None


def audit_manifest(manifest: dict[str, Any], rules_doc: dict[str, Any]) -> list[Violation]:
    violations: list[Violation] = []
    for rule in rules_doc.get("rules", []):
        v = evaluate_rule(rule, manifest)
        if v:
            violations.append(v)
    return violations


def bundled_rules_path() -> Path:
    return Path(__file__).resolve().parent / "rules" / "default.yaml"


def build_report(
    manifest_path: Path,
    manifest: dict[str, Any],
    rules_doc: dict[str, Any],
    violations: list[Violation],
) -> dict[str, Any]:
    return {
        "tool": "praxistimate",
        "version": __version__,
        "ruleset": rules_doc.get("ruleset_id", "unknown"),
        "manifest_path": str(manifest_path),
        "practice_id": manifest.get("practice_id"),
        "violations": [v.to_dict() for v in violations],
        "policy_violations": [v.to_dict() for v in violations if v.severity == "error"],
    }


def format_text(report: dict[str, Any]) -> str:
    lines = [
        f"praxistimate {report['version']} ruleset={report['ruleset']}",
        f"practice_id={report.get('practice_id')}",
    ]
    if not report["violations"]:
        lines.append("OK — no violations")
    else:
        for v in report["violations"]:
            lines.append(f"[{v['severity']}] {v['code']} ({v['rule_id']}): {v['message']}")
    return "\n".join(lines) + "\n"


def format_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# PraxisTiMate audit report",
        "",
        f"- ruleset: `{report['ruleset']}`",
        f"- practice_id: `{report.get('practice_id')}`",
        "",
    ]
    if not report["violations"]:
        lines.append("**Status:** OK")
    else:
        lines.append("## Violations")
        lines.append("")
        for v in report["violations"]:
            lines.append(f"- **{v['code']}** ({v['rule_id']}): {v['message']}")
    return "\n".join(lines) + "\n"


def exit_code_for(violations: list[Violation]) -> int:
    if any(v.severity == "error" for v in violations):
        return 2
    return 0
