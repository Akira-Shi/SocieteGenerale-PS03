from __future__ import annotations

from typing import Any


VALID_REVIEW_STATUS = "approved"
VALID_CONFIDENCE_THRESHOLD = 0.7
INVALID_FRESHNESS_STATUS = "stale"


def extract_framework(policy_ref: str) -> str:
    if not isinstance(policy_ref, str) or not policy_ref.strip():
        return "Unknown"
    return policy_ref.split("-", 1)[0].strip().upper()


def is_valid_record(record: dict[str, Any]) -> bool:
    return (
        str(record.get("review_status", "")).lower() == VALID_REVIEW_STATUS
        and float(record.get("confidence_score", 0.0)) >= VALID_CONFIDENCE_THRESHOLD
        and str(record.get("freshness_status", "")).lower() != INVALID_FRESHNESS_STATUS
    )


def calculate_compliance_score(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        return {
            "overall_score": 0.0,
            "passed": 0,
            "total": 0,
            "frameworks": {},
        }

    framework_totals: dict[str, dict[str, int]] = {}
    passed_count = 0

    for record in records:
        framework = extract_framework(str(record.get("policy_ref", "")))
        is_valid = is_valid_record(record)
        framework_totals.setdefault(framework, {"passed": 0, "total": 0})
        framework_totals[framework]["total"] += 1
        if is_valid:
            framework_totals[framework]["passed"] += 1
            passed_count += 1

    frameworks = {
        framework: {
            "passed": values["passed"],
            "total": values["total"],
            "percent": round((values["passed"] / values["total"]) * 100, 2)
            if values["total"]
            else 0.0,
        }
        for framework, values in framework_totals.items()
    }

    total_count = len(records)
    return {
        "overall_score": round((passed_count / total_count) * 100, 2),
        "passed": passed_count,
        "total": total_count,
        "frameworks": frameworks,
    }
