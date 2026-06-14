from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_pdf(lines: list[str]) -> bytes:
    content_lines = ["BT", "/F1 12 Tf", "50 780 Td", "14 TL"]
    first_line = True
    for line in lines:
        escaped = _escape_pdf_text(line)
        if first_line:
            content_lines.append(f"({escaped}) Tj")
            first_line = False
        else:
            content_lines.append(f"T* ({escaped}) Tj")
    content_lines.append("ET")
    content = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj",
        b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
        f"5 0 obj << /Length {len(content)} >> stream\n".encode("latin-1")
        + content
        + b"\nendstream endobj",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)
        pdf.extend(b"\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

    pdf.extend(
        (
            f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("latin-1")
    )
    return bytes(pdf)


def generate_pdf_report(
    output_directory: Path,
    score_summary: dict[str, Any],
    anomaly_summary: dict[str, Any],
    dashboard_summary: dict[str, Any],
) -> Path:
    output_directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_directory / f"compliance_report_{timestamp}.pdf"

    lines = [
        "COMPLIANCE EVIDENCE ANALYZER",
        "Executive Compliance Report",
        "=" * 72,
        f"Generated: {dashboard_summary.get('generated_at', datetime.now().isoformat())}",
        f"Last Updated: {dashboard_summary['last_updated'] or 'N/A'}",
        "",
        "1. Executive Summary",
        "-" * 72,
        f"Compliance Score    : {score_summary['overall_score']}%",
        (
            f"Evidence Coverage   : {dashboard_summary['evidence_coverage']}% "
            f"({dashboard_summary['valid_evidence']} / {dashboard_summary['total_evidence']})"
        ),
        f"Total Requirements  : {dashboard_summary.get('total_requirements', score_summary['total'])}",
        f"Anomaly Count       : {anomaly_summary['total_anomalies']}",
        "",
        "2. Framework Breakdown",
        "-" * 72,
        "Framework           Passed   Total   Compliance",
        "-" * 72,
    ]

    for framework, values in score_summary["frameworks"].items():
        lines.append(
            f"{framework:<18} {values['passed']:>6}   {values['total']:>5}   {values['percent']:>9}%"
        )

    lines.extend(
        [
            "",
            "3. Anomaly Summary",
            "-" * 72,
            "Type                Severity   Count   Definition",
            "-" * 72,
            f"Rejected Evidence   HIGH       {anomaly_summary['rejected']['count']:<5}  {anomaly_summary['rejected']['definition']}",
            f"Low Confidence      MEDIUM     {anomaly_summary['low_confidence']['count']:<5}  {anomaly_summary['low_confidence']['definition']}",
            f"Stale Evidence      LOW        {anomaly_summary['stale']['count']:<5}  {anomaly_summary['stale']['definition']}",
            "",
            "4. Recommendations",
            "-" * 72,
        ]
    )

    recommendations = dashboard_summary["recommendations"] or ["No immediate actions identified."]
    lines.extend(f"- {recommendation}" for recommendation in recommendations)

    output_path.write_bytes(_build_pdf(lines))
    return output_path
