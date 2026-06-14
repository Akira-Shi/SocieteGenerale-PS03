# Compliance Evidence Analyzer

## Problem Statement

Modern organizations must continuously demonstrate compliance with regulatory and security frameworks such as GDPR, SOX, NIST, PCI-DSS, ISO-27001, and HIPAA.

Compliance teams often face challenges including:

* Large volumes of compliance evidence
* Outdated or stale documentation
* Low-confidence evidence submissions
* Rejected compliance artifacts
* Lack of centralized compliance visibility
* Time-consuming audit preparation

The objective of this project is to provide a centralized compliance evidence analysis platform that automatically evaluates evidence quality, identifies anomalies, calculates compliance scores, and generates audit-ready reports.

---

# Solution Overview

Compliance Evidence Analyzer is a full-stack compliance monitoring dashboard that:

* Ingests compliance evidence datasets
* Calculates framework-wise compliance scores
* Detects stale, rejected, and low-confidence evidence
* Provides actionable recommendations
* Enables evidence exploration and filtering
* Generates professional audit reports in PDF format

The platform transforms raw compliance evidence into meaningful compliance insights that can assist auditors, compliance officers, and governance teams.

---

# Key Features

## Compliance Scoring

Automatically evaluates evidence quality and calculates:

* Overall compliance score
* Framework-specific compliance percentages
* Evidence coverage statistics

Supported Frameworks:

* GDPR
* SOX
* NIST
* PCI-DSS
* ISO-27001
* HIPAA

---

## Anomaly Detection

Detects critical compliance issues:

### Stale Evidence

Evidence older than the acceptable review period.

### Low Confidence Evidence

Evidence with confidence scores below threshold.

### Rejected Evidence

Evidence that failed compliance review.

Severity levels are visually highlighted within the dashboard.

---

## Evidence Explorer

Allows users to:

* Filter evidence by framework
* Filter evidence by review status
* Inspect compliance records
* Analyze evidence quality metrics

---

## Actionable Recommendations

The system generates recommendations based on detected risks, such as:

* Reviewing stale evidence
* Revalidating low-confidence submissions
* Investigating rejected compliance artifacts
* Prioritizing high-risk frameworks

---

## Audit Report Generation

Generate professional PDF reports containing:

* Executive Summary
* Compliance Overview
* Framework Breakdown
* Anomaly Analysis
* Recommendations
* Report Timestamp

---

# System Architecture

```text
Frontend (HTML/CSS/JavaScript)
            |
            v
      FastAPI Backend
            |
            v
   Compliance Services
   ├── Scoring Engine
   ├── Anomaly Detection
   └── Report Generator
            |
            v
       CSV Datasets
```

---

# Technology Stack

## Backend

* FastAPI
* Pandas
* ReportLab
* Uvicorn

## Frontend

* HTML
* CSS
* JavaScript

## Data Processing

* Pandas DataFrames
* CSV-based evidence ingestion

---

# Project Structure

```text
ComplianceEvidenceAnalyzer/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── services/
│   │   ├── scoring.py
│   │   ├── anomalies.py
│   │   └── reports.py
│   └── data/
│       ├── evidence_artifacts.csv
│       └── evidence_labels.csv
│
├── frontend/
│   └── frontend.html
│
└── README.md
```

---

# Compliance Evaluation Logic

Evidence is considered valid when:

```text
review_status == "approved"
AND
confidence_score >= 0.7
AND
freshness_status != "stale"
```

Compliance scores are calculated using valid evidence records across all supported frameworks.

---

# Setup Instructions

## 1. Clone Repository

```powershell
git clone <repository-url>
cd <repository-folder>
```

## 2. Create Virtual Environment

```powershell
python -m venv .venv
```

## 3. Activate Virtual Environment

```powershell
.venv\Scripts\Activate.ps1
```

## 4. Install Dependencies

```powershell
pip install -r backend\requirements.txt
```

## 5. Start Backend Server

```powershell
uvicorn backend.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

---

# Running the Frontend

The frontend is a static application.

Open:

```text
frontend/frontend.html
```

directly in a browser

OR

serve the frontend folder using any lightweight HTTP server.

Example:

```powershell
cd frontend
python -m http.server 5500
```

Then open:

```text
http://localhost:5500
```

---

# API Endpoints

## Compliance Score

```http
GET /api/compliance-score
```

Returns:

* Overall compliance score
* Framework-wise breakdown

---

## Anomalies

```http
GET /api/anomalies
```

Returns:

* Stale evidence
* Low confidence evidence
* Rejected evidence

---

## Dashboard Summary

```http
GET /api/dashboard-summary
```

Returns:

* Compliance metrics
* Evidence statistics
* Recommendations
* Dashboard metadata

---

## Evidence Explorer

```http
GET /api/evidence
```

Query Parameters:

```text
policy
status
limit
```

Example:

```http
GET /api/evidence?policy=GDPR&status=approved&limit=50
```

---

## Generate Report

```http
GET /api/generate-report
```

Returns:

* PDF compliance report

---

# Quick API Test

```powershell
curl.exe http://localhost:8000/api/compliance-score

curl.exe http://localhost:8000/api/anomalies

curl.exe http://localhost:8000/api/dashboard-summary

curl.exe http://localhost:8000/api/generate-report > report.pdf
```

---

# Dataset Notes

Data is loaded automatically at application startup.

Sources:

* evidence_artifacts.csv
* evidence_labels.csv

Datasets are merged using:

```text
evidence_id
```

Expected seeded results:

| Metric                  | Value  |
| ----------------------- | ------ |
| Overall Compliance      | ~72.5% |
| Total Anomalies         | ~47    |
| Stale Evidence          | ~34    |
| Low Confidence Evidence | ~8     |
| Rejected Evidence       | ~5     |

Actual values are calculated dynamically from the dataset.

---

# Future Enhancements

* Database integration
* Authentication and role-based access
* Historical compliance trends
* Real-time compliance monitoring
* Cloud deployment
* Multi-tenant support
* Automated evidence ingestion

---

# Team

Developed as part of the Societe Generale Compliance Evidence Analysis Hackathon.

Built using FastAPI, Pandas, ReportLab, HTML, CSS, and JavaScript.
