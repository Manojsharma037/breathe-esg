# BreatheESG — ESG Data Ingestion Platform

A full-stack prototype for ingesting, normalizing, and reviewing 
enterprise emissions data from multiple sources.

Built with Django REST Framework + React.

---

## Overview

Enterprise ESG data lives in different systems, in different shapes, 
with different gaps. This platform ingests emissions and activity data 
from three source types, normalizes it to a common unit, and surfaces 
a review dashboard where analysts can approve records before they are 
locked for audit.

---

## Features

- File-based ingestion from SAP (fuel/procurement), utility portals (electricity), and corporate travel platforms
- Automatic CO2 normalization with Scope 1, 2, and 3 categorization
- Suspicious row detection based on 3x category average threshold
- Analyst review dashboard with approve and reject workflow
- Complete audit trail for every action
- Multi-tenant data architecture

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 4.2 + Django REST Framework |
| Database | PostgreSQL |
| Frontend | React 18 + Vite + Axios |
| Deployment | Render (Backend) + Netlify (Frontend) |

---

## Architecture
File Upload (CSV/JSON)
            ↓
RawRecord — stored as-is, source of truth
            ↓
Normalization — units converted, CO2 calculated
            ↓
NormalizedRecord — Scope 1/2/3, kgCO2e
            ↓
Analyst Review — approve or reject
            ↓
AuditLog — every action tracked, locked for auditors

---

## Project Structure
breathe-esg/
├── backend/
│   ├── config/          # Django settings, urls
│   ├── ingestion/       # Upload APIs, normalization
│   ├── records/         # Data models
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/         # Axios config
│       ├── components/  # RecordsTable, UploadForm
│       └── pages/       # Dashboard
└── docs/
├── MODEL.md
├── DECISIONS.md
├── TRADEOFFS.md
└── SOURCES.md

---

## Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## Environment Variables

Create a `.env` file inside the `backend` folder:

SECRET_KEY=your-secret-key
DEBUG=True
DB_NAME=breatheesg
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/upload/sap/ | Upload SAP CSV |
| POST | /api/upload/utility/ | Upload Utility CSV |
| POST | /api/upload/travel/ | Upload Travel JSON |
| POST | /api/normalize/ | Run normalization |
| GET | /api/records/ | List all records |
| GET | /api/records/?review_status=pending | Filter by status |
| GET | /api/records/?scope=scope1 | Filter by scope |
| GET | /api/records/?source_type=sap | Filter by source |
| POST | /api/records/{id}/approve/ | Approve a record |
| POST | /api/records/{id}/reject/ | Reject a record |
| GET | /api/dashboard/stats/ | Dashboard summary |

---

## ESG Data Flow

**Step 1 — Upload**
Upload a CSV or JSON file from the dashboard.
Each row is stored as a RawRecord exactly as received.

**Step 2 — Normalize**
Click Run Normalization. The system reads each pending
RawRecord, calculates CO2 equivalent, assigns Scope,
and creates a NormalizedRecord.

**Step 3 — Review**
Analysts review records on the dashboard.
Suspicious records (value > 3x category average)
are automatically flagged for attention.

**Step 4 — Approve or Reject**
Analysts approve or reject each record.
Every action is logged in the AuditLog with timestamp.

---

## Emission Factors

| Category | Factor | Source |
|----------|--------|--------|
| Diesel | 2.65 kgCO2e/liter | GHG Protocol |
| Petrol | 2.31 kgCO2e/liter | GHG Protocol |
| Natural Gas | 2.04 kgCO2e/m3 | GHG Protocol |
| Electricity | 0.91 kgCO2e/kWh | India CEA 2023 |
| Flight Economy | 0.16 kgCO2e/km | DEFRA 2023 |
| Flight Business | 0.43 kgCO2e/km | DEFRA 2023 |
| Hotel | 31.0 kgCO2e/night | HCMI |
| Ground Transport | 0.21 kgCO2e/km | DEFRA 2023 |

---

## Admin Panel
URL:      /admin
Username: admin
Password: provided separately

---

## Deployment

| Service | URL |
|---------|-----|
| Backend API | _update after deployment_ |
| Frontend | _update after deployment_ |

---



## Known Limitations

- No authentication — admin user hardcoded for prototype
- Emission factors hardcoded — no versioning table
- Manual file upload only — no scheduled ingestion
- No duplicate upload detection

See TRADEOFFS.md for full explanation.

---

## Future Improvements

- JWT authentication with role-based access control
- EmissionFactor table with versioning and source tracking
- Scheduled ingestion via Celery + Redis
- PDF bill parsing for utility data
- Concur and Navan API integration
- Market-based vs location-based Scope 2 calculation
