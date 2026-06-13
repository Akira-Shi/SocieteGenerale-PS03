# Compliance Evidence Analyzer Backend

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Server runs at `http://localhost:8000`

## API Endpoints

- `GET /api/compliance-score` — Compliance score by framework
- `GET /api/anomalies` — Detected anomalies (stale, low-confidence, rejected)
- `GET /api/dashboard-summary` — Summary for dashboard cards
- `GET /api/evidence?policy=GDPR&status=approved&limit=50` — Filtered evidence records
- `GET /api/generate-report` — Download PDF compliance report

## Quick Test

```powershell
curl.exe http://localhost:8000/api/compliance-score
curl.exe http://localhost:8000/api/dashboard-summary
curl.exe http://localhost:8000/api/generate-report > report.pdf
```

## Data

- CSV files loaded from `backend/data/` at startup
- Merges evidence records and labels
- Calculates compliance scores and detects anomalies

## How It Works

**Valid evidence** = approved + confidence ≥ 0.7 + freshness ≠ stale

**Anomalies detected:**
- Stale: > 90 days old
- Low confidence: score < 0.7
- Rejected: review_status = "rejected"

**Expected results:**
- Overall score: ~72.5%
- Total anomalies: ~47
- All endpoints: < 500ms response time