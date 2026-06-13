# Compliance Evidence Analyzer Backend

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload
```

## API Endpoints

- `GET /api/compliance-score`
- `GET /api/anomalies`
- `GET /api/dashboard-summary`
- `GET /api/evidence?policy=GDPR&status=approved&limit=50`
- `GET /api/generate-report`

The application loads CSV data from `backend/data` at startup, merges records on `evidence_id`, and converts date columns to datetime for scoring and anomaly analysis.

## Note

This workspace's available Python package index does not currently provide `pandas` or `reportlab` for the installed Python `3.13` runtime, so the backend uses standard-library CSV processing and a lightweight built-in PDF writer to remain runnable in this environment while preserving the same API behavior.
