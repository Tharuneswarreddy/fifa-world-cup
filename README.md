# FIFA World Cup Intelligence Platform

A data-rich, responsive football analytics platform covering the history of the FIFA World Cup —
every edition from 1930 to the **2026** tournament, with teams, players, matches, records,
head-to-head comparisons and interactive charts. Built on openly-licensed data (martj42 / CC0)
with API-Football for optional current-data enrichment.

> **Data integrity first.** Nothing is fabricated. Missing data is labelled "Not recorded",
> never invented. See [DATA_SOURCES.md](DATA_SOURCES.md).

---

## Highlights

- **23 World Cup editions** (1930–2026), **1,068 matches**, **3,028 goals**, **1,596 players**, **87 teams** — all from CC0 data.
- Current: the 2026 tournament is fully loaded (Spain champions, derived from match data).
- FastAPI + PostgreSQL backend, React + TypeScript + Tailwind frontend.
- Premium dark/light sports-dashboard design system, responsive to phone width.
- All-time records engine (top scorers, titles, appearances, head-to-head) correctly scoped to
  World Cup *finals* — shootouts count as draws per FIFA convention.

## Tech stack

| Layer | Tech |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2 (async), Alembic, asyncpg, Pydantic v2 |
| Database | PostgreSQL 16 (Docker) |
| Frontend | React 18, Vite 5, TypeScript (strict), Tailwind CSS, TanStack Query, React Router, Recharts, Lucide |
| Data | martj42 (CC0) historical dataset; API-Football (free tier) for enrichment |

---

## Prerequisites

- **Docker Desktop** (for PostgreSQL)
- **Python 3.12+**
- **Node.js 20+** and npm
- Windows, macOS or Linux (developed on Windows 11)

## Quick start (Windows / PowerShell)

### 1. Start PostgreSQL

```bash
docker compose up -d
```

This starts PostgreSQL 16 on host port **5544** (chosen to avoid colliding with other local
Postgres instances). Data persists in a named Docker volume.

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\python -m pip install -r requirements.txt
```

Create `backend/.env` from the example and set your values (an API-Football key is optional —
the app is fully functional on historical data without it):

```bash
copy .env.example .env
```

Run database migrations:

```bash
venv\Scripts\python -m alembic upgrade head
```

Download the historical dataset (CC0, ~7 MB) and import it:

```bash
venv\Scripts\python scripts\download_data.py
venv\Scripts\python -m app.ingestion.cli import-history
```

Start the API:

```bash
venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

- API docs (OpenAPI/Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. The dev server proxies `/api` to the backend on port 8000.

---

## Ingestion CLI

Run from `backend/` with the venv active:

```bash
python -m app.ingestion.cli sources            # list registered data sources
python -m app.ingestion.cli import-history     # import martj42 World Cup finals
python -m app.ingestion.cli import-history --include-qualifiers   # also load qualifiers
python -m app.ingestion.cli validate           # data-quality report
python -m app.ingestion.cli sync-status        # API-Football account & quota (uses 1 request)
```

Imports are **idempotent** — re-running updates existing rows (keyed by a stable `external_ref`)
rather than duplicating them.

---

## Project structure

```
fifa/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── core/              # settings, logging
│   │   ├── db/                # async engine/session, declarative base
│   │   ├── models/            # SQLAlchemy models (16 tables)
│   │   ├── schemas/           # Pydantic response models
│   │   ├── services/          # stats engine, ORM→schema mappers
│   │   ├── providers/         # API-Football client (budget-aware)
│   │   ├── ingestion/         # loader, CLI, curated reference data
│   │   └── api/v1/            # REST routers
│   ├── alembic/               # migrations
│   └── tests/                 # pytest
├── frontend/
│   └── src/
│       ├── pages/             # 14 route pages
│       ├── components/        # layout, ui primitives, charts, matches
│       ├── lib/               # api client, theme, helpers
│       └── types/             # TypeScript API types
├── data/raw/martj42/          # downloaded CSVs (gitignored)
├── docker-compose.yml
├── DATA_SOURCES.md
└── README.md
```

## API overview (`/api/v1`)

`competitions`, `tournaments` (+ `/fixtures`, `/bracket`, `/groups`, `/records`), `teams`
(+ `/matches`, `/compare`), `players`, `matches`, `records` / `leaderboards`, `search`,
`map/participation`, `data-status`. Full interactive docs at `/docs`.

## Testing

```bash
# Backend
cd backend && venv\Scripts\python -m pytest

# Frontend
cd frontend && npm test        # vitest
npm run build                  # type-check + production build
```

## Scope & limitations

See [DATA_SOURCES.md](DATA_SOURCES.md) for full provenance and known gaps. In short: group
tables and full knockout brackets are not available from the open source (surfaced honestly in
the UI); player profiles beyond goals are "Not recorded"; women's/club/qualification competitions
have schema support but are not yet populated.

## License

Application code: for the project owner's use. Historical data: CC0 (public domain) via martj42 —
see [DATA_SOURCES.md](DATA_SOURCES.md) for attribution and third-party terms.
