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


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _sample_records(records: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    samples = []
    for record in records[:limit]:
        samples.append(
            {
                "evidence_id": record.get("evidence_id"),
                "policy_ref": record.get("policy_ref"),
                "artifact_name": record.get("artifact_name"),
                "review_status": record.get("review_status"),
                "confidence_score": round(_safe_float(record.get("confidence_score", 0.0)), 2),
                "freshness_status": record.get("freshness_status"),
                "days_since_collected": _safe_int(record.get("days_since_collected", 0)),
            }
        )
    return samples


def summarize_anomalies(records: list[dict[str, Any]]) -> dict[str, Any]:
    stale_records = [record for record in records if _safe_int(record.get("days_since_collected", 0)) > 90]
    low_confidence_records = [
        record for record in records if _safe_float(record.get("confidence_score", 0.0)) < 0.7
    ]
    rejected_records = [
        record for record in records if str(record.get("review_status", "")).lower() == "rejected"
    ]

    unique_anomalies = {
        record["evidence_id"]
        for record in stale_records + low_confidence_records + rejected_records
        if record.get("evidence_id")
    }

    flattened_anomalies = [
        {
            "id": record.get("evidence_id"),
            "record_id": record.get("evidence_id"),
            "policy": record.get("framework") or str(record.get("policy_ref", "")).split("-", 1)[0],
            "framework": record.get("framework") or str(record.get("policy_ref", "")).split("-", 1)[0],
            "anomaly_type": "stale",
            "type": "stale",
            "review_status": record.get("review_status"),
            "confidence_score": _safe_float(record.get("confidence_score", 0.0)),
            "freshness": record.get("freshness_status"),
            "created_at": record.get("collected_at").isoformat() if record.get("collected_at") else "",
            "days_since_collected": _safe_int(record.get("days_since_collected", 0)),
        }
        for record in stale_records
    ] + [
        {
            "id": record.get("evidence_id"),
            "record_id": record.get("evidence_id"),
            "policy": record.get("framework") or str(record.get("policy_ref", "")).split("-", 1)[0],
            "framework": record.get("framework") or str(record.get("policy_ref", "")).split("-", 1)[0],
            "anomaly_type": "low_confidence",
            "type": "low_confidence",
            "review_status": record.get("review_status"),
            "confidence_score": _safe_float(record.get("confidence_score", 0.0)),
            "freshness": record.get("freshness_status"),
            "created_at": record.get("collected_at").isoformat() if record.get("collected_at") else "",
            "days_since_collected": _safe_int(record.get("days_since_collected", 0)),
        }
        for record in low_confidence_records
    ] + [
        {
            "id": record.get("evidence_id"),
            "record_id": record.get("evidence_id"),
            "policy": record.get("framework") or str(record.get("policy_ref", "")).split("-", 1)[0],
            "framework": record.get("framework") or str(record.get("policy_ref", "")).split("-", 1)[0],
            "anomaly_type": "rejected",
            "type": "rejected",
            "review_status": record.get("review_status"),
            "confidence_score": _safe_float(record.get("confidence_score", 0.0)),
            "freshness": record.get("freshness_status"),
            "created_at": record.get("collected_at").isoformat() if record.get("collected_at") else "",
            "days_since_collected": _safe_int(record.get("days_since_collected", 0)),
        }
        for record in rejected_records
    ]

    return {
        "total_anomalies": len(unique_anomalies),
        "anomaly_count": len(unique_anomalies),
        "anomalies": flattened_anomalies,
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
