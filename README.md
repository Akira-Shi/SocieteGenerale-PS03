# Compliance Evidence Analyzer

## Setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uvicorn backend.main:app --reload
```

Server runs at `http://localhost:8000`.

The frontend is a static file at `frontend/frontend.html`. Open it directly or serve the `frontend/` folder with a simple HTTP server.

## API Endpoints

- `GET /api/compliance-score`
- `GET /api/anomalies`
- `GET /api/dashboard-summary`
- `GET /api/evidence?policy=GDPR&status=approved&limit=50`
- `GET /api/generate-report`

## Quick Test

```powershell
curl.exe http://localhost:8000/api/compliance-score
curl.exe http://localhost:8000/api/dashboard-summary
curl.exe http://localhost:8000/api/generate-report > report.pdf
```

## Data Notes

- CSV files load from `backend/data/` at startup.
- Evidence artifacts and labels are merged on `evidence_id`.
- Valid evidence means `approved` plus confidence `>= 0.7` plus freshness not `stale`.
- Expected seeded results are about `72.5%` overall compliance and `47` anomalies.
