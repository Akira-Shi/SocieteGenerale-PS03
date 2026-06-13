from __future__ import annotations

from typing import Any


ANOMALY_DEFINITIONS = {
    "stale": {
        "definition": "Evidence collected more than 90 days ago.",
        "severity": "high",
    },
    "low_confidence": {
        "definition": "Evidence confidence score below 0.7.",
        "severity": "medium",
    },
    "rejected": {
        "definition": "Evidence explicitly rejected during review.",
        "severity": "high",
    },
}


def _sample_records(records: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    samples = []
    for record in records[:limit]:
        samples.append(
            {
                "evidence_id": record.get("evidence_id"),
                "policy_ref": record.get("policy_ref"),
                "artifact_name": record.get("artifact_name"),
                "review_status": record.get("review_status"),
                "confidence_score": round(float(record.get("confidence_score", 0.0)), 2),
                "freshness_status": record.get("freshness_status"),
                "days_since_collected": int(record.get("days_since_collected", 0)),
            }
        )
    return samples


def summarize_anomalies(records: list[dict[str, Any]]) -> dict[str, Any]:
    stale_records = [record for record in records if int(record.get("days_since_collected", 0)) > 90]
    low_confidence_records = [
        record for record in records if float(record.get("confidence_score", 0.0)) < 0.7
    ]
    rejected_records = [
        record for record in records if str(record.get("review_status", "")).lower() == "rejected"
    ]

    unique_anomalies = {
        record["evidence_id"]
        for record in stale_records + low_confidence_records + rejected_records
        if record.get("evidence_id")
    }

    return {
        "total_anomalies": len(unique_anomalies),
        "stale": {
            "count": len(stale_records),
            **ANOMALY_DEFINITIONS["stale"],
            "sample_records": _sample_records(stale_records),
        },
        "low_confidence": {
            "count": len(low_confidence_records),
            **ANOMALY_DEFINITIONS["low_confidence"],
            "sample_records": _sample_records(low_confidence_records),
        },
        "rejected": {
            "count": len(rejected_records),
            **ANOMALY_DEFINITIONS["rejected"],
            "sample_records": _sample_records(rejected_records),
        },
    }
