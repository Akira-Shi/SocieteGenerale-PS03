from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

from backend.services.anomalies import summarize_anomalies
from backend.services.reports import generate_pdf_report
from backend.services.scoring import calculate_compliance_score, extract_framework


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
DATE_COLUMNS = ["collected_at", "reviewed_at", "created_at", "updated_at"]

app = FastAPI(title="Compliance Evidence Analyzer", version="1.0.0")
app.state.evidence_records: list[dict[str, Any]] = []


def _parse_datetime(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def load_evidence_data() -> list[dict[str, Any]]:
    artifacts_path = DATA_DIR / "evidence_artifacts.csv"
    labels_path = DATA_DIR / "evidence_labels.csv"

    if not artifacts_path.exists() or not labels_path.exists():
        missing = [str(path.name) for path in (artifacts_path, labels_path) if not path.exists()]
        raise FileNotFoundError(f"Missing required data files: {', '.join(missing)}")

    with artifacts_path.open(newline="", encoding="utf-8") as artifacts_file:
        artifacts_rows = list(csv.DictReader(artifacts_file))
    with labels_path.open(newline="", encoding="utf-8") as labels_file:
        labels_rows = list(csv.DictReader(labels_file))

    labels_by_id = {row["evidence_id"]: row for row in labels_rows}
    merged_records: list[dict[str, Any]] = []
    today = datetime.now().date()

    for artifact in artifacts_rows:
        evidence_id = artifact.get("evidence_id")
        if evidence_id not in labels_by_id:
            continue

        merged = {**artifact, **labels_by_id[evidence_id]}
        for column in DATE_COLUMNS:
            merged[column] = _parse_datetime(str(merged.get(column, "")))

        merged["confidence_score"] = float(merged.get("confidence_score", 0.0))
        merged["framework"] = extract_framework(str(merged.get("policy_ref", "")))

        collected_at = merged.get("collected_at")
        merged["days_since_collected"] = (today - collected_at.date()).days if collected_at else 0
        merged_records.append(merged)

    return merged_records


def get_evidence_records() -> list[dict[str, Any]]:
    records = app.state.evidence_records
    if not records:
        raise HTTPException(status_code=503, detail="Evidence data is not loaded.")
    return records


def build_recommendations(
    score_summary: dict[str, Any], anomaly_summary: dict[str, Any]
) -> list[str]:
    recommendations: list[str] = []

    if anomaly_summary["stale"]["count"] > 0:
        recommendations.append("Refresh evidence artifacts older than 90 days.")
    if anomaly_summary["low_confidence"]["count"] > 0:
        recommendations.append("Review low-confidence evidence and improve source quality.")
    if anomaly_summary["rejected"]["count"] > 0:
        recommendations.append("Rework rejected submissions before the next compliance review.")
    if score_summary["overall_score"] < 80:
        recommendations.append("Prioritize framework gaps with the lowest pass percentages.")

    return recommendations


def build_dashboard_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    score_summary = calculate_compliance_score(records)
    anomaly_summary = summarize_anomalies(records)

    updated_values = [record.get("updated_at") for record in records if record.get("updated_at")]
    last_updated = max(updated_values).isoformat() if updated_values else ""

    return {
        "compliance_score": score_summary["overall_score"],
        "evidence_coverage": score_summary["overall_score"],
        "total_evidence": score_summary["total"],
        "anomalies": anomaly_summary["total_anomalies"],
        "recommendations": build_recommendations(score_summary, anomaly_summary),
        "last_updated": last_updated,
    }


@app.on_event("startup")
def startup_event() -> None:
    app.state.evidence_records = load_evidence_data()


@app.get("/api/compliance-score")
def get_compliance_score() -> dict[str, Any]:
    records = get_evidence_records()
    return calculate_compliance_score(records)


@app.get("/api/anomalies")
def get_anomalies() -> dict[str, Any]:
    records = get_evidence_records()
    return summarize_anomalies(records)


@app.get("/api/dashboard-summary")
def get_dashboard_summary() -> dict[str, Any]:
    records = get_evidence_records()
    return build_dashboard_summary(records)


@app.get("/api/evidence")
def get_evidence(
    policy: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
) -> dict[str, Any]:
    records = get_evidence_records()
    filtered = records

    if policy:
        filtered = [record for record in filtered if record.get("framework", "").upper() == policy.upper()]
    if status:
        filtered = [
            record
            for record in filtered
            if str(record.get("review_status", "")).lower() == status.lower()
        ]

    limited = []
    for record in filtered[:limit]:
        normalized = dict(record)
        for column in DATE_COLUMNS:
            value = normalized.get(column)
            normalized[column] = value.isoformat() if isinstance(value, datetime) else ""
        limited.append(normalized)

    return {
        "count": len(filtered),
        "limit": limit,
        "records": limited,
    }


@app.get("/api/generate-report")
def get_generate_report() -> FileResponse:
    records = get_evidence_records()
    score_summary = calculate_compliance_score(records)
    anomaly_summary = summarize_anomalies(records)
    dashboard_summary = build_dashboard_summary(records)
    report_path = generate_pdf_report(REPORTS_DIR, score_summary, anomaly_summary, dashboard_summary)
    return FileResponse(path=report_path, media_type="application/pdf", filename=report_path.name)
